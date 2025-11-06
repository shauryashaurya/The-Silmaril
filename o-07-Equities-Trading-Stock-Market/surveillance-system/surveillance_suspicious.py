# surveillance_suspicious.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import uuid

from data_handler import (
    DataConfig, ArrowDataLoader, ArrowDataWriter,
    DataOptimizer
)


@dataclass
class SuspiciousConfig:
    data_config: DataConfig = None
    structuring_threshold_amount: float = 9000
    structuring_time_window_hours: int = 24
    structuring_min_trades: int = 5
    layering_min_hops: int = 3
    layering_time_window_days: int = 7
    layering_return_threshold_pct: float = 0.10
    round_trip_time_window_days: int = 30
    round_trip_return_threshold_pct: float = 0.95
    high_risk_min_occurrences: int = 3
    severity_high_occurrences: int = 10
    severity_medium_occurrences: int = 5
    severity_low_occurrences: int = 2
    save_intermediates: bool = True

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


class VectorizedSuspiciousDetector:
    def __init__(self, config: SuspiciousConfig, loader: ArrowDataLoader, writer: ArrowDataWriter):
        self.config = config
        self.loader = loader
        self.writer = writer
        self.category = "suspicious_transactions"
        self.optimizer = DataOptimizer()

    def execute(self) -> pd.DataFrame:
        print("\n" + "="*80)
        print("CATEGORY 9: SUSPICIOUS TRANSACTION MONITORING (VECTORIZED)")
        print("="*80)

        print("\nLoading required data...")

        trade_cols = ['trade_id', 'timestamp', 'instrument_id', 'buy_account_id',
                      'sell_account_id', 'quantity', 'price', 'trade_value']

        account_cols = ['account_id', 'beneficial_owner_id', 'firm_id']

        trades = self.loader.load_table('trades', columns=trade_cols)
        accounts = self.loader.load_table('accounts', columns=account_cols)

        trades = self.optimizer.optimize_dtypes(trades)
        accounts = self.optimizer.optimize_dtypes(accounts)

        trades = self.optimizer.convert_timestamps(trades, ['timestamp'])
        trades = trades.dropna(subset=['timestamp'])

        print(f"Loaded {len(trades):,} trades, {len(accounts):,} accounts")

        alerts = []

        print("\nExecuting Rule 9.1: Structuring Detection...")
        alerts_9_1, intermediates_9_1 = self._rule_9_1_structuring(trades)
        alerts.extend(alerts_9_1)
        if self.config.save_intermediates and not intermediates_9_1.empty:
            self.writer.write_table(
                intermediates_9_1, self.category, 'intermediate', 'rule_9_1_candidates')

        print("\nExecuting Rule 9.2: Layering Detection...")
        alerts_9_2, intermediates_9_2 = self._rule_9_2_layering(
            trades, accounts)
        alerts.extend(alerts_9_2)
        if self.config.save_intermediates and not intermediates_9_2.empty:
            self.writer.write_table(
                intermediates_9_2, self.category, 'intermediate', 'rule_9_2_candidates')

        print("\nExecuting Rule 9.3: Round-Tripping Detection...")
        alerts_9_3, intermediates_9_3 = self._rule_9_3_round_tripping(
            trades, accounts)
        alerts.extend(alerts_9_3)
        if self.config.save_intermediates and not intermediates_9_3.empty:
            self.writer.write_table(
                intermediates_9_3, self.category, 'intermediate', 'rule_9_3_candidates')

        print("\nExecuting Rule 9.4: Rapid Value Transfer...")
        alerts_9_4, intermediates_9_4 = self._rule_9_4_rapid_transfer(trades)
        alerts.extend(alerts_9_4)
        if self.config.save_intermediates and not intermediates_9_4.empty:
            self.writer.write_table(
                intermediates_9_4, self.category, 'intermediate', 'rule_9_4_candidates')

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

    def _rule_9_1_structuring(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['buy_account_id'].notna()) &
            (trades['instrument_id'].notna()) &
            (trades['trade_value'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # identify trades just below threshold
        trades_clean['below_threshold'] = (
            (trades_clean['trade_value'] < self.config.structuring_threshold_amount) &
            (trades_clean['trade_value'] >
             self.config.structuring_threshold_amount * 0.8)
        )

        suspicious_trades = trades_clean[trades_clean['below_threshold']].copy(
        )

        if len(suspicious_trades) == 0:
            return [], pd.DataFrame()

        # create time windows
        suspicious_trades['time_bucket'] = suspicious_trades['timestamp'].dt.floor(
            'h')

        # aggregate within time windows
        window_agg = suspicious_trades.groupby(
            ['buy_account_id', 'instrument_id', 'time_bucket'],
            observed=True
        ).agg({
            'trade_id': ['count'],
            'trade_value': ['sum', 'mean']
        }).reset_index()

        # explicit column naming
        window_agg.columns = ['account_id', 'instrument_id',
                              'time_bucket', 'num_trades', 'total_value', 'avg_value']

        # filter to suspicious patterns
        suspicious_windows = window_agg[
            window_agg['num_trades'] >= self.config.structuring_min_trades
        ].copy()

        if len(suspicious_windows) == 0:
            return [], pd.DataFrame()

        print(
            f"  Found {len(suspicious_windows):,} suspicious structuring patterns")

        # aggregate by account
        grouped = suspicious_windows.groupby(['account_id', 'instrument_id'], observed=True).agg({
            'time_bucket': ['count'],
            'num_trades': ['sum', 'mean'],
            'total_value': ['sum']
        }).reset_index()

        grouped.columns = ['account_id', 'instrument_id', 'window_count',
                           'total_trades', 'avg_trades', 'cumulative_value']
        grouped = grouped[grouped['window_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='9.1',
            account_col='account_id',
            count_col='window_count',
            description_template='Structuring detected: {} suspicious periods'
        )

        return alerts, suspicious_windows

    def _rule_9_2_layering(self, trades: pd.DataFrame,
                           accounts: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['buy_account_id'].notna()) &
            (trades['sell_account_id'].notna()) &
            (trades['instrument_id'].notna()) &
            (trades['trade_value'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # map to beneficial owners
        account_owner_map = accounts.set_index(
            'account_id')['beneficial_owner_id'].to_dict()

        trades_clean['buy_owner'] = trades_clean['buy_account_id'].map(
            account_owner_map)
        trades_clean['sell_owner'] = trades_clean['sell_account_id'].map(
            account_owner_map)

        # filter to trades between different owners
        inter_owner = trades_clean[
            (trades_clean['buy_owner'].notna()) &
            (trades_clean['sell_owner'].notna()) &
            (trades_clean['buy_owner'] != trades_clean['sell_owner'])
        ].copy()

        if len(inter_owner) == 0:
            return [], pd.DataFrame()

        # build transaction chains
        inter_owner['trade_date'] = inter_owner['timestamp'].dt.date

        # count number of hops per owner per instrument per day
        owner_activity = inter_owner.groupby(
            ['buy_owner', 'instrument_id', 'trade_date'],
            observed=True
        ).agg({
            'sell_owner': ['nunique'],
            'trade_id': ['count'],
            'trade_value': ['sum']
        }).reset_index()

        owner_activity.columns = ['owner_id', 'instrument_id',
                                  'trade_date', 'num_counterparties', 'num_trades', 'total_value']

        # identify complex layering
        layering_patterns = owner_activity[
            owner_activity['num_counterparties'] >= self.config.layering_min_hops
        ].copy()

        if len(layering_patterns) == 0:
            return [], pd.DataFrame()

        print(
            f"  Found {len(layering_patterns):,} potential layering patterns")

        # aggregate by owner
        grouped = layering_patterns.groupby(['owner_id', 'instrument_id'], observed=True).agg({
            'trade_date': ['count'],
            'num_counterparties': ['mean'],
            'num_trades': ['sum'],
            'total_value': ['sum']
        }).reset_index()

        grouped.columns = ['owner_id', 'instrument_id', 'pattern_count',
                           'avg_counterparties', 'total_trades', 'total_value']
        grouped = grouped[grouped['pattern_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} owners with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='9.2',
            account_col='owner_id',
            count_col='pattern_count',
            description_template='Layering detected: {} complex transaction chains'
        )

        return alerts, layering_patterns

    def _rule_9_3_round_tripping(self, trades: pd.DataFrame,
                                 accounts: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['buy_account_id'].notna()) &
            (trades['sell_account_id'].notna()) &
            (trades['instrument_id'].notna()) &
            (trades['trade_value'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # map to beneficial owners
        account_owner_map = accounts.set_index(
            'account_id')['beneficial_owner_id'].to_dict()

        trades_clean['buy_owner'] = trades_clean['buy_account_id'].map(
            account_owner_map)
        trades_clean['sell_owner'] = trades_clean['sell_account_id'].map(
            account_owner_map)

        trades_clean = trades_clean[
            (trades_clean['buy_owner'].notna()) &
            (trades_clean['sell_owner'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # sort by owner and time
        trades_clean = trades_clean.sort_values(
            ['buy_owner', 'instrument_id', 'timestamp'])

        # for each owner buying, look for them selling same instrument later
        buy_positions = trades_clean[[
            'timestamp', 'buy_owner', 'instrument_id', 'trade_value', 'trade_id']].copy()
        buy_positions.columns = ['buy_time', 'owner_id',
                                 'instrument_id', 'buy_value', 'buy_trade_id']

        sell_positions = trades_clean[[
            'timestamp', 'sell_owner', 'instrument_id', 'trade_value', 'trade_id']].copy()
        sell_positions.columns = ['sell_time', 'owner_id',
                                  'instrument_id', 'sell_value', 'sell_trade_id']

        # ensure proper types
        buy_positions['owner_id'] = buy_positions['owner_id'].astype(str)
        buy_positions['instrument_id'] = buy_positions['instrument_id'].astype(
            str)
        sell_positions['owner_id'] = sell_positions['owner_id'].astype(str)
        sell_positions['instrument_id'] = sell_positions['instrument_id'].astype(
            str)

        buy_positions = buy_positions.dropna(
            subset=['owner_id', 'instrument_id', 'buy_time'])
        sell_positions = sell_positions.dropna(
            subset=['owner_id', 'instrument_id', 'sell_time'])

        if len(buy_positions) == 0 or len(sell_positions) == 0:
            return [], pd.DataFrame()

        buy_positions = buy_positions.sort_values(
            ['owner_id', 'instrument_id', 'buy_time']).reset_index(drop=True)
        sell_positions = sell_positions.sort_values(
            ['owner_id', 'instrument_id', 'sell_time']).reset_index(drop=True)

        # find round trips
        try:
            round_trips = pd.merge_asof(
                buy_positions,
                sell_positions,
                by=['owner_id', 'instrument_id'],
                left_on='buy_time',
                right_on='sell_time',
                direction='forward',
                tolerance=pd.Timedelta(
                    days=self.config.round_trip_time_window_days)
            )
        except:
            return [], pd.DataFrame()

        round_trips = round_trips.dropna(subset=['sell_time'])

        if len(round_trips) == 0:
            return [], pd.DataFrame()

        # calculate return rate
        round_trips['return_pct'] = round_trips['sell_value'] / \
            round_trips['buy_value']

        # filter to near-equal value (potential round-tripping)
        suspicious = round_trips[
            np.abs(round_trips['return_pct'] - 1.0) <= (1 -
                                                        self.config.round_trip_return_threshold_pct)
        ].copy()

        if len(suspicious) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(suspicious):,} potential round-trip patterns")

        # aggregate by owner
        grouped = suspicious.groupby(['owner_id', 'instrument_id'], observed=True).agg({
            'buy_trade_id': ['count'],
            'return_pct': ['mean'],
            'buy_value': ['sum']
        }).reset_index()

        grouped.columns = ['owner_id', 'instrument_id',
                           'round_trip_count', 'avg_return', 'total_value']
        grouped = grouped[grouped['round_trip_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} owners with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='9.3',
            account_col='owner_id',
            count_col='round_trip_count',
            description_template='Round-tripping detected: {} suspicious round trips'
        )

        return alerts, suspicious

    def _rule_9_4_rapid_transfer(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['buy_account_id'].notna()) &
            (trades['sell_account_id'].notna()) &
            (trades['instrument_id'].notna()) &
            (trades['trade_value'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # identify rapid sequences of transfers
        trades_clean = trades_clean.sort_values(['instrument_id', 'timestamp'])

        # calculate time between consecutive trades per instrument
        trades_clean['prev_timestamp'] = trades_clean.groupby(
            'instrument_id', observed=True)['timestamp'].shift(1)
        trades_clean['time_diff_seconds'] = (
            trades_clean['timestamp'] - trades_clean['prev_timestamp']
        ).dt.total_seconds()

        # identify rapid transfers (within 60 seconds)
        rapid = trades_clean[
            (trades_clean['time_diff_seconds'].notna()) &
            (trades_clean['time_diff_seconds'] <= 60)
        ].copy()

        if len(rapid) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(rapid):,} rapid transfer instances")

        # create time windows
        rapid['time_bucket'] = rapid['timestamp'].dt.floor('h')

        # aggregate by account and window
        window_agg = rapid.groupby(
            ['buy_account_id', 'instrument_id', 'time_bucket'],
            observed=True
        ).agg({
            'trade_id': ['count'],
            'trade_value': ['sum'],
            'time_diff_seconds': ['mean']
        }).reset_index()

        window_agg.columns = ['account_id', 'instrument_id',
                              'time_bucket', 'num_rapid', 'total_value', 'avg_gap']

        # filter to suspicious patterns
        suspicious = window_agg[window_agg['num_rapid'] >= 3].copy()

        if len(suspicious) == 0:
            return [], pd.DataFrame()

        # aggregate by account
        grouped = suspicious.groupby(['account_id', 'instrument_id'], observed=True).agg({
            'time_bucket': ['count'],
            'num_rapid': ['sum'],
            'total_value': ['sum']
        }).reset_index()

        grouped.columns = ['account_id', 'instrument_id',
                           'pattern_count', 'total_rapid', 'cumulative_value']
        grouped = grouped[grouped['pattern_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='9.4',
            account_col='account_id',
            count_col='pattern_count',
            description_template='Rapid value transfer: {} suspicious periods'
        )

        return alerts, suspicious

    def _generate_alerts(self, grouped: pd.DataFrame, rule_id: str,
                         account_col: str, count_col: str,
                         description_template: str) -> List[Alert]:

        if grouped.empty:
            return []

        # assign severity
        grouped['severity'] = 'low'
        grouped.loc[grouped[count_col] >=
                    self.config.severity_medium_occurrences, 'severity'] = 'medium'
        grouped.loc[grouped[count_col] >=
                    self.config.severity_high_occurrences, 'severity'] = 'high'

        grouped['confidence'] = np.minimum(0.95, 0.6 + grouped[count_col] / 15)

        alerts = []
        for idx, row in grouped.iterrows():
            alert = Alert(
                alert_id=f"SUSP_{rule_id.replace('.', '_')}_{uuid.uuid4().hex[:8]}",
                category="suspicious_transactions",
                rule_id=rule_id,
                severity=row['severity'],
                timestamp=datetime.now().isoformat(),
                account_ids=[row[account_col]],
                instrument_ids=[row.get('instrument_id', 'multiple')],
                description=description_template.format(int(row[count_col])),
                evidence={'num_instances': int(row[count_col])},
                confidence_score=float(row['confidence'])
            )
            alerts.append(alert)

        return alerts

    def _generate_summary_report(self, alerts_df: pd.DataFrame):
        summary = {
            'total_alerts': len(alerts_df),
            'by_severity': alerts_df.groupby('severity', observed=True).size().to_dict(),
            'by_rule': alerts_df.groupby('rule_id', observed=True).size().to_dict(),
            'avg_confidence': float(alerts_df['confidence_score'].mean()),
            'unique_accounts': len(set([acc for accs in alerts_df['account_ids'].apply(json.loads) for acc in accs]))
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

    suspicious_config = SuspiciousConfig(
        data_config=data_config,
        save_intermediates=True
    )

    print("Market Surveillance Engine - Category 9: Suspicious Transactions (VECTORIZED)")
    print("="*80)

    loader = ArrowDataLoader(data_config)
    writer = ArrowDataWriter(data_config)

    start_time = time.time()

    detector = VectorizedSuspiciousDetector(suspicious_config, loader, writer)
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
