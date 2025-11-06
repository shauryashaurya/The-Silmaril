# surveillance_engine_v3.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import uuid
from collections import defaultdict

from data_handler import (
    DataConfig, ArrowDataLoader, ArrowDataWriter,
    DataOptimizer
)


@dataclass
class EngineConfig:
    data_config: DataConfig = None
    lookback_days: int = 30
    save_intermediates: bool = True
    wash_trade_time_window_seconds: int = 300
    wash_trade_price_tolerance_pct: float = 0.001
    wash_trade_min_occurrences: int = 3
    wash_trade_same_day_only: bool = True
    severity_high_trades: int = 10
    severity_medium_trades: int = 5
    severity_low_trades: int = 3

    def __post_init__(self):
        if self.data_config is None:
            self.data_config = DataConfig()


@dataclass
class Alert:
    alert_id: str
    category: str
    rule_id: str
    severity: str
    timestamp: str
    account_ids: List[str]
    instrument_ids: List[str]
    description: str
    evidence: Dict[str, Any]
    confidence_score: float

    def to_dict(self):
        return {
            'alert_id': self.alert_id,
            'category': self.category,
            'rule_id': self.rule_id,
            'severity': self.severity,
            'timestamp': self.timestamp,
            'account_ids': json.dumps(self.account_ids),
            'instrument_ids': json.dumps(self.instrument_ids),
            'description': self.description,
            'evidence': json.dumps(self.evidence),
            'confidence_score': self.confidence_score
        }


class OptimizedWashTradingDetector:
    def __init__(self, config: EngineConfig, loader: ArrowDataLoader, writer: ArrowDataWriter):
        self.config = config
        self.loader = loader
        self.writer = writer
        self.category = "wash_trading"
        self.optimizer = DataOptimizer()

    def execute(self) -> pd.DataFrame:
        print("\n" + "="*80)
        print("CATEGORY 1: WASH TRADING DETECTION")
        print("="*80)

        print("\nLoading required data...")

        trade_cols = ['trade_id', 'timestamp', 'instrument_id',
                      'buy_order_id', 'sell_order_id',
                      'buy_account_id', 'sell_account_id',
                      'buy_firm_id', 'sell_firm_id',
                      'quantity', 'price', 'trade_value']

        account_cols = ['account_id', 'beneficial_owner_id', 'firm_id',
                        'ip_addresses', 'device_fingerprints', 'related_accounts']

        trades = self.loader.load_table('trades', columns=trade_cols)
        accounts = self.loader.load_table('accounts', columns=account_cols)

        trades = self.optimizer.optimize_dtypes(trades)
        accounts = self.optimizer.optimize_dtypes(accounts)

        accounts = self.optimizer.parse_json_columns(
            accounts,
            ['ip_addresses', 'device_fingerprints', 'related_accounts']
        )
        trades = self.optimizer.convert_timestamps(trades, ['timestamp'])

        # remove rows with NaT timestamps immediately after conversion
        trades = trades.dropna(subset=['timestamp'])

        print(f"Loaded {len(trades):,} trades and {len(accounts):,} accounts")

        alerts = []

        print("\nExecuting Rule 1.1: Same Beneficial Owner...")
        alerts_1_1, intermediates_1_1 = self._rule_1_1_fixed(trades, accounts)
        alerts.extend(alerts_1_1)
        if self.config.save_intermediates and not intermediates_1_1.empty:
            self.writer.write_table(
                intermediates_1_1, self.category, 'intermediate', 'rule_1_1_candidates')

        print("\nExecuting Rule 1.2: Related Accounts...")
        alerts_1_2, intermediates_1_2 = self._rule_1_2_fixed(trades, accounts)
        alerts.extend(alerts_1_2)
        if self.config.save_intermediates and not intermediates_1_2.empty:
            self.writer.write_table(
                intermediates_1_2, self.category, 'intermediate', 'rule_1_2_candidates')

        print("\nExecuting Rule 1.3: Same IP/Device...")
        alerts_1_3, intermediates_1_3 = self._rule_1_3_fixed(trades, accounts)
        alerts.extend(alerts_1_3)
        if self.config.save_intermediates and not intermediates_1_3.empty:
            self.writer.write_table(
                intermediates_1_3, self.category, 'intermediate', 'rule_1_3_candidates')

        print("\nExecuting Rule 1.4: Rapid Round-Trip...")
        alerts_1_4, intermediates_1_4 = self._rule_1_4_fixed(trades, accounts)
        alerts.extend(alerts_1_4)
        if self.config.save_intermediates and not intermediates_1_4.empty:
            self.writer.write_table(
                intermediates_1_4, self.category, 'intermediate', 'rule_1_4_candidates')

        if alerts:
            alerts_df = pd.DataFrame([alert.to_dict() for alert in alerts])
        else:
            alerts_df = pd.DataFrame()

        print(f"\nGenerated {len(alerts)} alerts")
        if len(alerts) > 0:
            self.writer.write_table(
                alerts_df, self.category, 'results', 'alerts')
            self._generate_summary_report(alerts_df)

        return alerts_df

    def _rule_1_1_fixed(self, trades: pd.DataFrame, accounts: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        account_owner_map = accounts.set_index(
            'account_id')['beneficial_owner_id'].to_dict()

        trades['buy_owner_id'] = trades['buy_account_id'].map(
            account_owner_map)
        trades['sell_owner_id'] = trades['sell_account_id'].map(
            account_owner_map)

        wash_candidates = trades[
            (trades['buy_owner_id'] == trades['sell_owner_id']) &
            (trades['buy_account_id'] != trades['sell_account_id']) &
            (trades['buy_owner_id'].notna()) &
            (trades['sell_owner_id'].notna())
        ].copy()

        if len(wash_candidates) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(wash_candidates):,} candidate trades")

        wash_candidates['trade_date'] = wash_candidates['timestamp'].dt.date

        numeric_agg = wash_candidates.groupby(
            ['buy_owner_id', 'instrument_id', 'trade_date'],
            as_index=False,
            observed=True
        ).agg({
            'trade_id': 'count',
            'quantity': ['sum', 'mean', 'std'],
            'price': ['mean', 'std'],
            'trade_value': 'sum',
            'timestamp': ['min', 'max']
        })

        numeric_agg.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in numeric_agg.columns.values]

        account_lists = wash_candidates.groupby(
            ['buy_owner_id', 'instrument_id', 'trade_date'],
            as_index=False,
            observed=True
        ).agg({
            'buy_account_id': lambda x: list(set(x)),
            'sell_account_id': lambda x: list(set(x))
        })

        grouped = numeric_agg.merge(
            account_lists,
            on=['buy_owner_id', 'instrument_id', 'trade_date'],
            how='left'
        )

        grouped = grouped[grouped['trade_id_count']
                          >= self.config.wash_trade_min_occurrences]

        print(f"  Found {len(grouped):,} patterns meeting threshold")

        alerts = self._generate_alerts_fixed(
            grouped,
            rule_id='1.1',
            description_template='Wash trading: {} trades between accounts with same beneficial owner',
            owner_col='buy_owner_id'
        )

        return alerts, grouped

    def _rule_1_2_fixed(self, trades: pd.DataFrame, accounts: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        related_pairs = set()

        for _, acc in accounts.iterrows():
            if 'related_accounts_list' in acc and acc['related_accounts_list']:
                for related_id in acc['related_accounts_list']:
                    related_pairs.add((acc['account_id'], related_id))
                    related_pairs.add((related_id, acc['account_id']))

        if not related_pairs:
            return [], pd.DataFrame()

        trades['is_related'] = trades.apply(
            lambda x: (x['buy_account_id'],
                       x['sell_account_id']) in related_pairs,
            axis=1
        )

        wash_candidates = trades[trades['is_related']].copy()

        if len(wash_candidates) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(wash_candidates):,} candidate trades")

        wash_candidates['trade_date'] = wash_candidates['timestamp'].dt.date

        grouped = wash_candidates.groupby(
            ['buy_account_id', 'sell_account_id', 'instrument_id', 'trade_date'],
            as_index=False,
            observed=True
        ).agg({
            'trade_id': 'count',
            'quantity': ['sum', 'mean'],
            'price': ['mean', 'std'],
            'trade_value': 'sum',
            'timestamp': ['min', 'max']
        })

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['trade_id_count']
                          >= self.config.wash_trade_min_occurrences]

        print(f"  Found {len(grouped):,} patterns meeting threshold")

        alerts = self._generate_alerts_fixed(
            grouped,
            rule_id='1.2',
            description_template='Wash trading: {} trades between related accounts',
            owner_col=None
        )

        return alerts, grouped

    def _rule_1_3_fixed(self, trades: pd.DataFrame, accounts: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        ip_account_map = defaultdict(set)
        device_account_map = defaultdict(set)

        for _, acc in accounts.iterrows():
            if 'ip_addresses_list' in acc and acc['ip_addresses_list']:
                for ip in acc['ip_addresses_list']:
                    ip_account_map[ip].add(acc['account_id'])

            if 'device_fingerprints_list' in acc and acc['device_fingerprints_list']:
                for device in acc['device_fingerprints_list']:
                    device_account_map[device].add(acc['account_id'])

        shared_pairs = set()

        for accounts_set in ip_account_map.values():
            if len(accounts_set) > 1:
                accounts_list = list(accounts_set)
                for i in range(len(accounts_list)):
                    for j in range(i+1, len(accounts_list)):
                        pair = tuple(
                            sorted([accounts_list[i], accounts_list[j]]))
                        shared_pairs.add(pair)

        for accounts_set in device_account_map.values():
            if len(accounts_set) > 1:
                accounts_list = list(accounts_set)
                for i in range(len(accounts_list)):
                    for j in range(i+1, len(accounts_list)):
                        pair = tuple(
                            sorted([accounts_list[i], accounts_list[j]]))
                        shared_pairs.add(pair)

        if not shared_pairs:
            return [], pd.DataFrame()

        print(f"  Found {len(shared_pairs):,} account pairs sharing IP/device")

        trades['account_pair'] = trades.apply(
            lambda x: tuple(
                sorted([x['buy_account_id'], x['sell_account_id']])),
            axis=1
        )

        trades['is_shared'] = trades['account_pair'].isin(shared_pairs)
        wash_candidates = trades[trades['is_shared']].copy()

        if len(wash_candidates) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(wash_candidates):,} candidate trades")

        wash_candidates['trade_date'] = wash_candidates['timestamp'].dt.date

        grouped = wash_candidates.groupby(
            ['buy_account_id', 'sell_account_id', 'instrument_id', 'trade_date'],
            as_index=False,
            observed=True
        ).agg({
            'trade_id': 'count',
            'quantity': ['sum', 'mean'],
            'price': ['mean', 'std'],
            'trade_value': 'sum'
        })

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['trade_id_count']
                          >= self.config.wash_trade_min_occurrences]

        print(f"  Found {len(grouped):,} patterns meeting threshold")

        alerts = self._generate_alerts_fixed(
            grouped,
            rule_id='1.3',
            description_template='Wash trading: {} trades between accounts sharing IP/device',
            owner_col=None
        )

        return alerts, grouped

    def _rule_1_4_fixed(self, trades: pd.DataFrame, accounts: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        # create buy trades view
        buy_trades = trades[['buy_account_id', 'instrument_id',
                             'timestamp', 'price', 'quantity', 'trade_id']].copy()
        buy_trades.columns = ['account_id', 'instrument_id',
                              'buy_time', 'buy_price', 'buy_quantity', 'buy_trade_id']

        # create sell trades view
        sell_trades = trades[['sell_account_id', 'instrument_id',
                              'timestamp', 'price', 'quantity', 'trade_id']].copy()
        sell_trades.columns = ['account_id', 'instrument_id',
                               'sell_time', 'sell_price', 'sell_quantity', 'sell_trade_id']

        # remove any NaN values in key columns that would break merge_asof
        buy_trades = buy_trades.dropna(
            subset=['account_id', 'instrument_id', 'buy_time'])
        sell_trades = sell_trades.dropna(
            subset=['account_id', 'instrument_id', 'sell_time'])

        if len(buy_trades) == 0 or len(sell_trades) == 0:
            return [], pd.DataFrame()

        # ensure account_id and instrument_id are string type for consistent sorting
        buy_trades['account_id'] = buy_trades['account_id'].astype(str)
        buy_trades['instrument_id'] = buy_trades['instrument_id'].astype(str)
        sell_trades['account_id'] = sell_trades['account_id'].astype(str)
        sell_trades['instrument_id'] = sell_trades['instrument_id'].astype(str)

        # sort by grouping columns first, then by time column
        # this ensures data is grouped and sorted within each group
        buy_trades = buy_trades.sort_values(
            ['account_id', 'instrument_id', 'buy_time']).reset_index(drop=True)
        sell_trades = sell_trades.sort_values(
            ['account_id', 'instrument_id', 'sell_time']).reset_index(drop=True)

        # merge_asof to find sell trades following buy trades
        try:
            roundtrips = pd.merge_asof(
                buy_trades,
                sell_trades,
                by=['account_id', 'instrument_id'],
                left_on='buy_time',
                right_on='sell_time',
                direction='forward',
                tolerance=pd.Timedelta(
                    seconds=self.config.wash_trade_time_window_seconds)
            )
        except ValueError as e:
            print(f"  merge_asof failed: {e}")
            return [], pd.DataFrame()

        # filter to only matched pairs
        roundtrips = roundtrips.dropna(subset=['sell_time'])

        if len(roundtrips) == 0:
            return [], pd.DataFrame()

        # calculate time and price differences
        roundtrips['time_diff_seconds'] = (
            roundtrips['sell_time'] - roundtrips['buy_time']).dt.total_seconds()
        roundtrips['price_diff_pct'] = np.abs(
            roundtrips['sell_price'] - roundtrips['buy_price']) / roundtrips['buy_price']

        # filter by price tolerance
        roundtrips = roundtrips[roundtrips['price_diff_pct']
                                <= self.config.wash_trade_price_tolerance_pct]

        if len(roundtrips) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(roundtrips):,} candidate round-trips")

        roundtrips['trade_date'] = roundtrips['buy_time'].dt.date

        grouped = roundtrips.groupby(
            ['account_id', 'instrument_id', 'trade_date'],
            as_index=False,
            observed=True
        ).agg({
            'buy_trade_id': 'count',
            'time_diff_seconds': 'mean',
            'price_diff_pct': 'mean',
            'buy_quantity': 'sum',
            'buy_time': ['min', 'max']
        })

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['buy_trade_id_count']
                          >= self.config.wash_trade_min_occurrences]

        print(f"  Found {len(grouped):,} patterns meeting threshold")

        alerts = self._generate_alerts_fixed(
            grouped,
            rule_id='1.4',
            description_template='Rapid round-trip trading: {} round-trips detected',
            owner_col=None,
            roundtrip_mode=True
        )

        return alerts, grouped

    def _generate_alerts_fixed(self, grouped: pd.DataFrame, rule_id: str,
                               description_template: str, owner_col: Optional[str] = None,
                               roundtrip_mode: bool = False) -> List[Alert]:

        if grouped.empty:
            return []

        count_col = 'buy_trade_id_count' if roundtrip_mode else 'trade_id_count'

        grouped['severity'] = 'low'
        grouped.loc[grouped[count_col] >=
                    self.config.severity_medium_trades, 'severity'] = 'medium'
        grouped.loc[grouped[count_col] >=
                    self.config.severity_high_trades, 'severity'] = 'high'

        grouped['confidence'] = np.minimum(0.95, 0.5 + grouped[count_col] / 20)

        alerts = []

        for idx, row in grouped.iterrows():
            if 'buy_account_id' in row and isinstance(row['buy_account_id'], list):
                account_ids = list(
                    set(row['buy_account_id'] + row['sell_account_id']))
            elif 'buy_account_id' in row:
                account_ids = [row['buy_account_id'], row['sell_account_id']]
            else:
                account_ids = [row.get('account_id', 'unknown')]

            evidence = {
                'num_trades': int(row[count_col]),
                'date': str(row.get('trade_date', 'unknown'))
            }

            if 'trade_value_sum' in row:
                evidence['total_value'] = float(row['trade_value_sum'])
            if 'quantity_mean' in row:
                evidence['avg_quantity'] = float(row['quantity_mean'])
            if 'price_mean' in row:
                evidence['avg_price'] = float(row['price_mean'])
            if 'time_diff_seconds_mean' in row:
                evidence['avg_time_diff_seconds'] = float(
                    row['time_diff_seconds_mean'])
            if 'price_diff_pct_mean' in row:
                evidence['avg_price_diff_pct'] = float(
                    row['price_diff_pct_mean'])
            if owner_col and owner_col in row:
                evidence['beneficial_owner_id'] = str(row[owner_col])

            alert = Alert(
                alert_id=f"WASH_{rule_id.replace('.', '_')}_{uuid.uuid4().hex[:8]}",
                category="wash_trading",
                rule_id=rule_id,
                severity=row['severity'],
                timestamp=datetime.now().isoformat(),
                account_ids=account_ids,
                instrument_ids=[row['instrument_id']],
                description=description_template.format(row[count_col]),
                evidence=evidence,
                confidence_score=float(row['confidence'])
            )
            alerts.append(alert)

        return alerts

    def _generate_summary_report(self, alerts_df: pd.DataFrame):
        summary = {
            'total_alerts': len(alerts_df),
            'by_severity': alerts_df['severity'].value_counts().to_dict(),
            'by_rule': alerts_df['rule_id'].value_counts().to_dict(),
            'avg_confidence': float(alerts_df['confidence_score'].mean()),
            'unique_accounts': len(set([acc for accs in alerts_df['account_ids'].apply(json.loads) for acc in accs])),
            'unique_instruments': len(set([inst for insts in alerts_df['instrument_ids'].apply(json.loads) for inst in insts]))
        }

        summary_df = pd.DataFrame([summary])
        self.writer.write_table(
            summary_df, self.category, 'results', 'summary')

        print("\nSummary:")
        print(f"  Total Alerts: {summary['total_alerts']}")
        print(f"  By Severity: {summary['by_severity']}")
        print(f"  By Rule: {summary['by_rule']}")
        print(f"  Average Confidence: {summary['avg_confidence']:.2%}")


def main():
    import time

    data_config = DataConfig(
        source_format='parquet',
        output_format='parquet',
        source_dir='./data/small_test',
        output_dir='./data/small_test/surveillance_output',
        use_arrow_native=True,
        compress_output=True
    )
    # data_config = DataConfig(
    #     source_format='parquet',
    #     output_format='parquet',
    #     source_dir='./data/parquet_output',
    #     output_dir='./data/surveillance_output',
    #     use_arrow_native=True,
    #     compress_output=True
    # )

    engine_config = EngineConfig(
        data_config=data_config,
        save_intermediates=True,
        wash_trade_min_occurrences=3,
        severity_high_trades=10,
        severity_medium_trades=5,
        severity_low_trades=3
    )

    print("Market Surveillance Engine - Category 1: Wash Trading")
    print("="*80)

    loader = ArrowDataLoader(data_config)
    writer = ArrowDataWriter(data_config)

    start_time = time.time()

    detector = OptimizedWashTradingDetector(engine_config, loader, writer)
    alerts = detector.execute()

    elapsed = time.time() - start_time

    print("\n" + "="*80)
    print("EXECUTION COMPLETE")
    print("="*80)
    print(f"Results saved to: {data_config.output_dir}")
    print(f"Total alerts: {len(alerts)}")
    print(f"Execution time: {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()
