# surveillance_collusion.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import uuid
from itertools import combinations

from data_handler import (
    DataConfig, ArrowDataLoader, ArrowDataWriter,
    DataOptimizer
)


@dataclass
class CollusionConfig:
    data_config: DataConfig = None
    sync_time_window_seconds: int = 30
    sync_min_instruments: int = 2
    sync_min_occurrences: int = 3
    quote_coordination_time_window_seconds: int = 60
    quote_min_updates: int = 5
    volume_ramp_time_window_minutes: int = 5
    volume_spike_multiplier: float = 3.0
    volume_min_accounts: int = 3
    cross_firm_time_window_seconds: int = 120
    cross_firm_min_firms: int = 2
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


class VectorizedCollusionDetector:
    def __init__(self, config: CollusionConfig, loader: ArrowDataLoader, writer: ArrowDataWriter):
        self.config = config
        self.loader = loader
        self.writer = writer
        self.category = "collusion_coordination"
        self.optimizer = DataOptimizer()

    def execute(self) -> pd.DataFrame:
        print("\n" + "="*80)
        print("CATEGORY 6: COLLUSION AND COORDINATION DETECTION (VECTORIZED)")
        print("="*80)

        print("\nLoading required data...")

        trade_cols = ['trade_id', 'timestamp', 'instrument_id', 'buy_account_id',
                      'sell_account_id', 'quantity', 'price', 'trade_value']

        order_cols = ['order_id', 'timestamp', 'account_id', 'instrument_id',
                      'side', 'quantity', 'price', 'order_type']

        account_cols = ['account_id', 'beneficial_owner_id', 'firm_id']

        trades = self.loader.load_table('trades', columns=trade_cols)
        orders = self.loader.load_table('orders', columns=order_cols)
        accounts = self.loader.load_table('accounts', columns=account_cols)

        trades = self.optimizer.optimize_dtypes(trades)
        orders = self.optimizer.optimize_dtypes(orders)
        accounts = self.optimizer.optimize_dtypes(accounts)

        trades = self.optimizer.convert_timestamps(trades, ['timestamp'])
        orders = self.optimizer.convert_timestamps(orders, ['timestamp'])

        trades = trades.dropna(subset=['timestamp'])
        orders = orders.dropna(subset=['timestamp'])

        print(
            f"Loaded {len(trades):,} trades, {len(orders):,} orders, {len(accounts):,} accounts")

        alerts = []

        print("\nExecuting Rule 6.1: Synchronized Trading...")
        alerts_6_1, intermediates_6_1 = self._rule_6_1_synchronized_trading(
            trades)
        alerts.extend(alerts_6_1)
        if self.config.save_intermediates and not intermediates_6_1.empty:
            self.writer.write_table(
                intermediates_6_1, self.category, 'intermediate', 'rule_6_1_candidates')

        print("\nExecuting Rule 6.2: Quote Coordination...")
        alerts_6_2, intermediates_6_2 = self._rule_6_2_quote_coordination(
            orders)
        alerts.extend(alerts_6_2)
        if self.config.save_intermediates and not intermediates_6_2.empty:
            self.writer.write_table(
                intermediates_6_2, self.category, 'intermediate', 'rule_6_2_candidates')

        print("\nExecuting Rule 6.3: Volume Ramping...")
        alerts_6_3, intermediates_6_3 = self._rule_6_3_volume_ramping(trades)
        alerts.extend(alerts_6_3)
        if self.config.save_intermediates and not intermediates_6_3.empty:
            self.writer.write_table(
                intermediates_6_3, self.category, 'intermediate', 'rule_6_3_candidates')

        print("\nExecuting Rule 6.4: Cross-Firm Coordination...")
        alerts_6_4, intermediates_6_4 = self._rule_6_4_cross_firm(
            trades, accounts)
        alerts.extend(alerts_6_4)
        if self.config.save_intermediates and not intermediates_6_4.empty:
            self.writer.write_table(
                intermediates_6_4, self.category, 'intermediate', 'rule_6_4_candidates')

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

    def _rule_6_1_synchronized_trading(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['sell_account_id'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # create time buckets for synchronization detection
        trades_clean['time_bucket'] = (
            trades_clean['timestamp'].astype(
                'int64') // 10**9 // self.config.sync_time_window_seconds
        )

        # identify accounts trading in same time buckets
        buy_activity = trades_clean.groupby(
            ['time_bucket', 'instrument_id', 'buy_account_id'], observed=True).size().reset_index(name='buy_count')
        sell_activity = trades_clean.groupby(
            ['time_bucket', 'instrument_id', 'sell_account_id'], observed=True).size().reset_index(name='sell_count')

        buy_activity.columns = ['time_bucket',
                                'instrument_id', 'account_id', 'trade_count']
        sell_activity.columns = ['time_bucket',
                                 'instrument_id', 'account_id', 'trade_count']

        all_activity = pd.concat(
            [buy_activity, sell_activity], ignore_index=True)
        all_activity = all_activity.groupby(['time_bucket', 'instrument_id', 'account_id'], observed=True)[
            'trade_count'].sum().reset_index()

        # find time buckets with multiple accounts
        bucket_accounts = all_activity.groupby(['time_bucket', 'instrument_id'], observed=True).agg({
            'account_id': ['count', lambda x: list(x)]
        }).reset_index()

        bucket_accounts.columns = [
            'time_bucket', 'instrument_id', 'num_accounts', 'account_list']

        # filter to synchronized activity
        synchronized = bucket_accounts[bucket_accounts['num_accounts'] >= 2].copy(
        )

        if len(synchronized) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(synchronized):,} synchronized time buckets")

        # count instruments per account pair
        sync_patterns = []

        for idx, row in synchronized.iterrows():
            accounts_list = row['account_list']
            if len(accounts_list) >= 2:
                for acc1, acc2 in combinations(sorted(accounts_list)[:5], 2):
                    sync_patterns.append({
                        'account_pair': tuple(sorted([acc1, acc2])),
                        'instrument_id': row['instrument_id'],
                        'time_bucket': row['time_bucket']
                    })

        if not sync_patterns:
            return [], pd.DataFrame()

        patterns_df = pd.DataFrame(sync_patterns)

        # aggregate by account pair
        grouped = patterns_df.groupby('account_pair', observed=True).agg({
            'instrument_id': ['nunique'],
            'time_bucket': ['count']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]

        grouped = grouped[
            (grouped['instrument_id_nunique'] >= self.config.sync_min_instruments) &
            (grouped['time_bucket_count'] >= self.config.sync_min_occurrences)
        ]

        if len(grouped) == 0:
            return [], pd.DataFrame()

        print(
            f"  Found {len(grouped):,} account pairs with synchronized patterns")

        # create alerts
        alerts = []
        for idx, row in grouped.iterrows():
            if row['time_bucket_count'] >= self.config.severity_high_occurrences:
                severity = 'high'
            elif row['time_bucket_count'] >= self.config.severity_medium_occurrences:
                severity = 'medium'
            else:
                severity = 'low'

            confidence = min(0.90, 0.6 + (row['instrument_id_nunique'] / 10))

            alert = Alert(
                alert_id=f"COLLUSION_6_1_{uuid.uuid4().hex[:8]}",
                category="collusion_coordination",
                rule_id="6.1",
                severity=severity,
                timestamp=datetime.now().isoformat(),
                account_ids=list(row['account_pair']),
                instrument_ids=[],
                description=f"Synchronized trading: {int(row['time_bucket_count'])} instances across {int(row['instrument_id_nunique'])} instruments",
                evidence={
                    'num_occurrences': int(row['time_bucket_count']),
                    'num_instruments': int(row['instrument_id_nunique'])
                },
                confidence_score=confidence
            )
            alerts.append(alert)

        return alerts, patterns_df

    def _rule_6_2_quote_coordination(self, orders: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        orders_clean = orders[
            (orders['account_id'].notna()) &
            (orders['instrument_id'].notna()) &
            (orders['price'].notna())
        ].copy()

        if len(orders_clean) == 0:
            return [], pd.DataFrame()

        # create time buckets
        orders_clean['time_bucket'] = (
            orders_clean['timestamp'].astype(
                'int64') // 10**9 // self.config.quote_coordination_time_window_seconds
        )

        # group by instrument and time bucket
        quote_activity = orders_clean.groupby(['instrument_id', 'time_bucket', 'side'], observed=True).agg({
            'account_id': ['nunique', lambda x: list(set(x))],
            'order_id': ['count'],
            'price': ['std']
        }).reset_index()

        quote_activity.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in quote_activity.columns.values]

        # identify coordinated quote updates
        coordinated = quote_activity[
            (quote_activity['account_id_nunique'] >= 2) &
            (quote_activity['order_id_count'] >= self.config.quote_min_updates) &
            (quote_activity['price_std'] < 0.01)
        ].copy()

        if len(coordinated) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(coordinated):,} coordinated quote patterns")

        # aggregate by instrument
        grouped = coordinated.groupby('instrument_id', observed=True).agg({
            'time_bucket': ['count'],
            'account_id_nunique': ['mean'],
            'order_id_count': ['sum']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['time_bucket_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} instruments with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='6.2',
            account_col='instrument_id',
            count_col='time_bucket_count',
            description_template='Quote coordination: {} suspicious periods',
            is_instrument_alert=True
        )

        return alerts, coordinated

    def _rule_6_3_volume_ramping(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # create minute buckets
        trades_clean['minute'] = trades_clean['timestamp'].dt.floor('min')

        # calculate volume per minute
        minute_volume = trades_clean.groupby(['instrument_id', 'minute'], observed=True).agg({
            'quantity': ['sum'],
            'buy_account_id': ['nunique']
        }).reset_index()

        minute_volume.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in minute_volume.columns.values]

        # calculate rolling average
        minute_volume = minute_volume.sort_values(['instrument_id', 'minute'])
        minute_volume['volume_ma'] = minute_volume.groupby('instrument_id', observed=True)['quantity_sum'].transform(
            lambda x: x.rolling(
                window=self.config.volume_ramp_time_window_minutes, min_periods=1).mean()
        )

        minute_volume['volume_ratio'] = minute_volume['quantity_sum'] / \
            (minute_volume['volume_ma'] + 1)

        # identify volume spikes with multiple accounts
        spikes = minute_volume[
            (minute_volume['volume_ratio'] >= self.config.volume_spike_multiplier) &
            (minute_volume['buy_account_id_nunique']
             >= self.config.volume_min_accounts)
        ].copy()

        if len(spikes) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(spikes):,} coordinated volume spikes")

        # get account details for spikes
        spike_trades = trades_clean.merge(
            spikes[['instrument_id', 'minute']],
            on=['instrument_id', 'minute'],
            how='inner'
        )

        # identify coordinating accounts
        account_participation = spike_trades.groupby(['instrument_id', 'minute', 'buy_account_id'], observed=True).agg({
            'quantity': ['sum']
        }).reset_index()

        account_participation.columns = [
            'instrument_id', 'minute', 'account_id', 'volume']

        # aggregate by instrument
        grouped = account_participation.groupby('instrument_id', observed=True).agg({
            'minute': ['nunique'],
            'account_id': ['nunique']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['minute_nunique']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} instruments with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='6.3',
            account_col='instrument_id',
            count_col='minute_nunique',
            description_template='Volume ramping: {} coordinated spikes',
            is_instrument_alert=True
        )

        return alerts, spikes

    def _rule_6_4_cross_firm(self, trades: pd.DataFrame,
                             accounts: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['sell_account_id'].notna())
        ].copy()

        accounts_clean = accounts[
            (accounts['account_id'].notna()) &
            (accounts['firm_id'].notna())
        ].copy()

        if len(trades_clean) == 0 or len(accounts_clean) == 0:
            return [], pd.DataFrame()

        # map accounts to firms
        account_firm_map = accounts_clean.set_index(
            'account_id')['firm_id'].to_dict()

        trades_clean['buy_firm'] = trades_clean['buy_account_id'].map(
            account_firm_map)
        trades_clean['sell_firm'] = trades_clean['sell_account_id'].map(
            account_firm_map)

        trades_clean = trades_clean.dropna(subset=['buy_firm', 'sell_firm'])

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # create time buckets
        trades_clean['time_bucket'] = (
            trades_clean['timestamp'].astype(
                'int64') // 10**9 // self.config.cross_firm_time_window_seconds
        )

        # identify coordinated activity across firms
        buy_firms = trades_clean.groupby(
            ['instrument_id', 'time_bucket', 'buy_firm'], observed=True).size().reset_index(name='buy_trades')
        sell_firms = trades_clean.groupby(
            ['instrument_id', 'time_bucket', 'sell_firm'], observed=True).size().reset_index(name='sell_trades')

        buy_firms.columns = ['instrument_id',
                             'time_bucket', 'firm_id', 'trade_count']
        sell_firms.columns = ['instrument_id',
                              'time_bucket', 'firm_id', 'trade_count']

        all_firms = pd.concat([buy_firms, sell_firms], ignore_index=True)
        all_firms = all_firms.groupby(['instrument_id', 'time_bucket', 'firm_id'], observed=True)[
            'trade_count'].sum().reset_index()

        # count firms per bucket
        firm_counts = all_firms.groupby(['instrument_id', 'time_bucket'], observed=True).agg({
            'firm_id': ['nunique', lambda x: list(set(x))]
        }).reset_index()

        firm_counts.columns = ['instrument_id',
                               'time_bucket', 'num_firms', 'firm_list']

        # filter to cross-firm coordination
        coordinated = firm_counts[
            firm_counts['num_firms'] >= self.config.cross_firm_min_firms
        ].copy()

        if len(coordinated) == 0:
            return [], pd.DataFrame()

        print(
            f"  Found {len(coordinated):,} cross-firm coordination instances")

        # aggregate by instrument
        grouped = coordinated.groupby('instrument_id', observed=True).agg({
            'time_bucket': ['count'],
            'num_firms': ['mean']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['time_bucket_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} instruments with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='6.4',
            account_col='instrument_id',
            count_col='time_bucket_count',
            description_template='Cross-firm coordination: {} instances',
            is_instrument_alert=True
        )

        return alerts, coordinated

    def _generate_alerts(self, grouped: pd.DataFrame, rule_id: str,
                         account_col: str, count_col: str,
                         description_template: str,
                         is_instrument_alert: bool = False) -> List[Alert]:

        if grouped.empty:
            return []

        grouped['severity'] = 'low'
        grouped.loc[grouped[count_col] >=
                    self.config.severity_medium_occurrences, 'severity'] = 'medium'
        grouped.loc[grouped[count_col] >=
                    self.config.severity_high_occurrences, 'severity'] = 'high'

        grouped['confidence'] = np.minimum(0.95, 0.6 + grouped[count_col] / 15)

        alerts = []
        for idx, row in grouped.iterrows():
            if is_instrument_alert:
                account_ids = []
                instrument_ids = [row[account_col]]
            else:
                account_ids = [row[account_col]] if isinstance(
                    row[account_col], str) else list(row[account_col])
                instrument_ids = []

            alert = Alert(
                alert_id=f"COLLUSION_{rule_id.replace('.', '_')}_{uuid.uuid4().hex[:8]}",
                category="collusion_coordination",
                rule_id=rule_id,
                severity=row['severity'],
                timestamp=datetime.now().isoformat(),
                account_ids=account_ids,
                instrument_ids=instrument_ids,
                description=description_template.format(int(row[count_col])),
                evidence={'num_occurrences': int(row[count_col])},
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
            'unique_accounts': len(set([acc for accs in alerts_df['account_ids'].apply(json.loads) for acc in accs if accs]))
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

    collusion_config = CollusionConfig(
        data_config=data_config,
        save_intermediates=True
    )

    print("Market Surveillance Engine - Category 6: Collusion and Coordination (VECTORIZED)")
    print("="*80)

    loader = ArrowDataLoader(data_config)
    writer = ArrowDataWriter(data_config)

    start_time = time.time()

    detector = VectorizedCollusionDetector(collusion_config, loader, writer)
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
