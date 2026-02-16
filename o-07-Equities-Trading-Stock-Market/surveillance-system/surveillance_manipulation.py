# surveillance_manipulation.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time as dt_time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import uuid

from data_handler import (
    DataConfig, ArrowDataLoader, ArrowDataWriter,
    DataOptimizer
)


@dataclass
class ManipulationConfig:
    # relaxed params so that we generate some more alerts...
    data_config: DataConfig = None
    closing_window_minutes: int = 15
    # for Rule 4.1 (Marking the Close)
    closing_trade_concentration_threshold: float = 0.15  # was 0.3
    closing_price_impact_pct: float = 0.005  # was 0.01
    # Rule 4.2 (Tape Painting)
    tape_painting_min_trades: int = 3  # was 5
    tape_painting_time_window_seconds: int = 60
    tape_painting_volume_threshold_pct: float = 0.05  # was 0.15
    # Rule 4.3 (HF Disruption)
    hf_disruption_orders_per_minute: int = 30  # was 100
    hf_disruption_cancel_rate: float = 0.9
    # Rule 4.4 (Pump and Dump)
    pump_accumulation_window_days: int = 3  # was 5
    pump_price_increase_pct: float = 0.03  # was 0.10
    pump_volume_increase_multiplier: float = 2.0  # was 3.0
    dump_window_hours: int = 4
    severity_high_occurrences: int = 10
    severity_medium_occurrences: int = 5
    # General thresholds
    severity_low_occurrences: int = 1  # was 2
    save_intermediates: bool = True

# OG config
# @dataclass
# class ManipulationConfig:
#     data_config: DataConfig = None
#     closing_window_minutes: int = 15
#     closing_trade_concentration_threshold: float = 0.3
#     closing_price_impact_pct: float = 0.01
#     tape_painting_min_trades: int = 5
#     tape_painting_time_window_seconds: int = 60
#     tape_painting_volume_threshold_pct: float = 0.15
#     hf_disruption_orders_per_minute: int = 100
#     hf_disruption_cancel_rate: float = 0.9
#     pump_accumulation_window_days: int = 5
#     pump_price_increase_pct: float = 0.10
#     pump_volume_increase_multiplier: float = 3.0
#     dump_window_hours: int = 4
#     severity_high_occurrences: int = 10
#     severity_medium_occurrences: int = 5
#     severity_low_occurrences: int = 2
#     save_intermediates: bool = True

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


class VectorizedManipulationDetector:
    def __init__(self, config: ManipulationConfig, loader: ArrowDataLoader, writer: ArrowDataWriter):
        self.config = config
        self.loader = loader
        self.writer = writer
        self.category = "market_manipulation"
        self.optimizer = DataOptimizer()

    def execute(self) -> pd.DataFrame:
        print("\n" + "="*80)
        print("CATEGORY 4: MARKET MANIPULATION DETECTION (VECTORIZED)")
        print("="*80)

        print("\nLoading required data...")

        trade_cols = ['trade_id', 'timestamp', 'instrument_id', 'buy_account_id',
                      'sell_account_id', 'quantity', 'price', 'trade_value']

        order_cols = ['order_id', 'timestamp', 'account_id', 'instrument_id',
                      'side', 'quantity', 'price', 'order_type']

        trades = self.loader.load_table('trades', columns=trade_cols)
        orders = self.loader.load_table('orders', columns=order_cols)

        trades = self.optimizer.optimize_dtypes(trades)
        orders = self.optimizer.optimize_dtypes(orders)

        trades = self.optimizer.convert_timestamps(trades, ['timestamp'])
        orders = self.optimizer.convert_timestamps(orders, ['timestamp'])

        trades = trades.dropna(subset=['timestamp'])
        orders = orders.dropna(subset=['timestamp'])

        print(f"Loaded {len(trades):,} trades, {len(orders):,} orders")

        alerts = []

        print("\nExecuting Rule 4.1: Marking the Close...")
        alerts_4_1, intermediates_4_1 = self._rule_4_1_marking_close(trades)
        alerts.extend(alerts_4_1)
        if self.config.save_intermediates and not intermediates_4_1.empty:
            self.writer.write_table(
                intermediates_4_1, self.category, 'intermediate', 'rule_4_1_candidates')

        print("\nExecuting Rule 4.2: Painting the Tape...")
        alerts_4_2, intermediates_4_2 = self._rule_4_2_tape_painting(trades)
        alerts.extend(alerts_4_2)
        if self.config.save_intermediates and not intermediates_4_2.empty:
            self.writer.write_table(
                intermediates_4_2, self.category, 'intermediate', 'rule_4_2_candidates')

        print("\nExecuting Rule 4.3: High Frequency Disruption...")
        alerts_4_3, intermediates_4_3 = self._rule_4_3_hf_disruption(orders)
        alerts.extend(alerts_4_3)
        if self.config.save_intermediates and not intermediates_4_3.empty:
            self.writer.write_table(
                intermediates_4_3, self.category, 'intermediate', 'rule_4_3_candidates')

        print("\nExecuting Rule 4.4: Pump and Dump...")
        alerts_4_4, intermediates_4_4 = self._rule_4_4_pump_dump(trades)
        alerts.extend(alerts_4_4)
        if self.config.save_intermediates and not intermediates_4_4.empty:
            self.writer.write_table(
                intermediates_4_4, self.category, 'intermediate', 'rule_4_4_candidates')

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

    def _rule_4_1_marking_close(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['sell_account_id'].notna()) &
            (trades['price'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # extract time components vectorized
        trades_clean['trade_date'] = trades_clean['timestamp'].dt.date
        trades_clean['trade_time'] = trades_clean['timestamp'].dt.time

        # identify closing window trades vectorized
        close_time = dt_time(16, 0)
        window_start = dt_time(15, 60 - self.config.closing_window_minutes)

        trades_clean['is_closing_window'] = (
            (trades_clean['trade_time'] >= window_start) &
            (trades_clean['trade_time'] <= close_time)
        )

        # calculate daily metrics per instrument
        daily_metrics = trades_clean.groupby(['instrument_id', 'trade_date'], observed=True).agg({
            'quantity': ['sum'],
            'trade_value': ['sum'],
            'price': ['first', 'last'],
            'trade_id': ['count']
        }).reset_index()

        daily_metrics.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in daily_metrics.columns.values]

        # calculate closing window metrics
        closing_trades = trades_clean[trades_clean['is_closing_window']].copy()

        if len(closing_trades) == 0:
            return [], pd.DataFrame()

        closing_metrics = closing_trades.groupby(['instrument_id', 'trade_date'], observed=True).agg({
            'quantity': ['sum'],
            'trade_value': ['sum'],
            'trade_id': ['count']
        }).reset_index()

        closing_metrics.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in closing_metrics.columns.values]

        # merge to calculate concentration
        combined = daily_metrics.merge(
            closing_metrics,
            on=['instrument_id', 'trade_date'],
            how='left',
            suffixes=('_daily', '_close')
        )

        combined = combined.dropna(subset=['quantity_sum_close'])

        if len(combined) == 0:
            return [], pd.DataFrame()

        # calculate concentration and price impact vectorized
        combined['volume_concentration'] = combined['quantity_sum_close'] / \
            combined['quantity_sum_daily']
        combined['price_change_pct'] = np.abs(
            combined['price_last'] - combined['price_first']
        ) / combined['price_first']

        # filter suspicious patterns
        suspicious = combined[
            (combined['volume_concentration'] >= self.config.closing_trade_concentration_threshold) &
            (combined['price_change_pct'] >=
             self.config.closing_price_impact_pct)
        ].copy()

        if len(suspicious) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(suspicious):,} suspicious closing patterns")

        # match back to get account details
        closing_detail = closing_trades.merge(
            suspicious[['instrument_id', 'trade_date']],
            on=['instrument_id', 'trade_date'],
            how='inner'
        )

        # identify dominant accounts per pattern vectorized
        buy_participation = closing_detail.groupby(
            ['instrument_id', 'trade_date', 'buy_account_id'],
            observed=True
        )['quantity'].sum().reset_index()
        buy_participation.columns = ['instrument_id',
                                     'trade_date', 'account_id', 'buy_volume']

        sell_participation = closing_detail.groupby(
            ['instrument_id', 'trade_date', 'sell_account_id'],
            observed=True
        )['quantity'].sum().reset_index()
        sell_participation.columns = [
            'instrument_id', 'trade_date', 'account_id', 'sell_volume']

        all_participation = buy_participation.merge(
            sell_participation,
            on=['instrument_id', 'trade_date', 'account_id'],
            how='outer'
        ).fillna({'buy_volume': 0, 'sell_volume': 0})

        all_participation['total_volume'] = all_participation['buy_volume'] + \
            all_participation['sell_volume']

        # get top account per pattern
        top_accounts = all_participation.sort_values(
            ['instrument_id', 'trade_date', 'total_volume'],
            ascending=[True, True, False]
        ).groupby(['instrument_id', 'trade_date'], observed=True).first().reset_index()

        # merge with suspicious patterns
        patterns = suspicious.merge(
            top_accounts[['instrument_id', 'trade_date',
                          'account_id', 'total_volume']],
            on=['instrument_id', 'trade_date'],
            how='left'
        )

        # aggregate by account
        grouped = patterns.groupby(['account_id', 'instrument_id'], observed=True).agg({
            'trade_date': ['count'],
            'volume_concentration': ['mean'],
            'price_change_pct': ['mean']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['trade_date_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='4.1',
            account_col='account_id',
            count_col='trade_date_count',
            description_template='Marking the close: {} instances detected'
        )

        return alerts, patterns

    def _rule_4_2_tape_painting(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['sell_account_id'].notna()) &
            (trades['price'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # create time windows vectorized
        trades_clean['time_bucket'] = (
            trades_clean['timestamp'].astype(
                'int64') // 10**9 // self.config.tape_painting_time_window_seconds
        )

        # identify coordinated trade clusters
        cluster_metrics = trades_clean.groupby(
            ['instrument_id', 'time_bucket'],
            observed=True
        ).agg({
            'trade_id': ['count'],
            'quantity': ['sum'],
            'price': ['std', 'mean'],
            'buy_account_id': ['nunique'],
            'sell_account_id': ['nunique'],
            'timestamp': ['min', 'max']
        }).reset_index()

        cluster_metrics.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in cluster_metrics.columns.values]

        # calculate daily volume for comparison
        trades_clean['trade_date'] = trades_clean['timestamp'].dt.date

        daily_volume = trades_clean.groupby(['instrument_id', 'trade_date'], observed=True).agg({
            'quantity': ['sum']
        }).reset_index()
        daily_volume.columns = ['instrument_id', 'trade_date', 'daily_volume']

        # merge cluster metrics with daily volume
        trades_clean['trade_date'] = trades_clean['timestamp'].dt.date
        cluster_with_date = cluster_metrics.merge(
            trades_clean[['instrument_id', 'time_bucket',
                          'trade_date']].drop_duplicates(),
            on=['instrument_id', 'time_bucket'],
            how='left'
        )

        cluster_with_volume = cluster_with_date.merge(
            daily_volume,
            on=['instrument_id', 'trade_date'],
            how='left'
        )

        # calculate volume concentration
        cluster_with_volume['volume_concentration'] = (
            cluster_with_volume['quantity_sum'] /
            cluster_with_volume['daily_volume']
        )

        # filter suspicious clusters
        # cluster_with_volume['price_mean'] * 0.01)  # was 0.001 - changed to generate more alerts...
        suspicious_clusters = cluster_with_volume[
            (cluster_with_volume['trade_id_count'] >= self.config.tape_painting_min_trades) &
            (cluster_with_volume['volume_concentration'] >= self.config.tape_painting_volume_threshold_pct) &
            (cluster_with_volume['price_std'] <
             cluster_with_volume['price_mean'] * 0.01)
        ].copy()

        # suspicious_clusters = cluster_with_volume[
        #     (cluster_with_volume['trade_id_count'] >= self.config.tape_painting_min_trades) &
        #     (cluster_with_volume['volume_concentration'] >= self.config.tape_painting_volume_threshold_pct) &
        #     (cluster_with_volume['price_std'] <
        #      cluster_with_volume['price_mean'] * 0.001)
        # ].copy()

        if len(suspicious_clusters) == 0:
            return [], pd.DataFrame()

        print(
            f"  Found {len(suspicious_clusters):,} suspicious trade clusters")

        # get accounts involved in suspicious clusters
        cluster_trades = trades_clean.merge(
            suspicious_clusters[['instrument_id', 'time_bucket']],
            on=['instrument_id', 'time_bucket'],
            how='inner'
        )

        # identify coordinating accounts
        buy_accounts = cluster_trades.groupby(
            ['instrument_id', 'time_bucket', 'buy_account_id'],
            observed=True
        ).size().reset_index(name='buy_trades')

        sell_accounts = cluster_trades.groupby(
            ['instrument_id', 'time_bucket', 'sell_account_id'],
            observed=True
        ).size().reset_index(name='sell_trades')

        # find accounts that appear in same clusters
        buy_accounts.columns = ['instrument_id',
                                'time_bucket', 'account_id', 'trade_count']
        sell_accounts.columns = ['instrument_id',
                                 'time_bucket', 'account_id', 'trade_count']

        all_accounts = pd.concat(
            [buy_accounts, sell_accounts], ignore_index=True)
        all_accounts = all_accounts.groupby(
            ['instrument_id', 'time_bucket', 'account_id'],
            observed=True
        )['trade_count'].sum().reset_index()

        # merge with cluster info
        patterns = all_accounts.merge(
            suspicious_clusters[['instrument_id', 'time_bucket',
                                 'volume_concentration', 'trade_id_count']],
            on=['instrument_id', 'time_bucket'],
            how='left'
        )

        # aggregate by account
        grouped = patterns.groupby(['account_id', 'instrument_id'], observed=True).agg({
            'time_bucket': ['count'],
            'volume_concentration': ['mean'],
            'trade_id_count': ['mean']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['time_bucket_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='4.2',
            account_col='account_id',
            count_col='time_bucket_count',
            description_template='Tape painting: {} suspicious clusters detected'
        )

        return alerts, patterns

    def _rule_4_3_hf_disruption(self, orders: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        orders_clean = orders[
            (orders['account_id'].notna()) &
            (orders['instrument_id'].notna())
        ].copy()

        if len(orders_clean) == 0:
            return [], pd.DataFrame()

        # create minute buckets
        orders_clean['minute'] = orders_clean['timestamp'].dt.floor('min')

        # count orders per minute
        order_rate = orders_clean.groupby(
            ['account_id', 'instrument_id', 'minute'],
            observed=True
        ).agg({
            'order_id': ['count']
        }).reset_index()

        order_rate.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in order_rate.columns.values]

        # filter high frequency periods
        high_freq = order_rate[
            order_rate['order_id_count'] >= self.config.hf_disruption_orders_per_minute
        ].copy()

        if len(high_freq) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(high_freq):,} high frequency periods")

        # check if these are critical market times (market open/close)
        high_freq['hour'] = high_freq['minute'].dt.hour
        high_freq['is_critical'] = (
            ((high_freq['hour'] >= 9) & (high_freq['hour'] < 10)) |
            ((high_freq['hour'] >= 15) & (high_freq['hour'] <= 16))
        )

        critical_hf = high_freq[high_freq['is_critical']].copy()

        if len(critical_hf) == 0:
            return [], pd.DataFrame()

        print(
            f"  Found {len(critical_hf):,} critical time high frequency periods")

        # aggregate by account
        grouped = critical_hf.groupby(['account_id', 'instrument_id'], observed=True).agg({
            'minute': ['count'],
            'order_id_count': ['mean', 'max']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['minute_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='4.3',
            account_col='account_id',
            count_col='minute_count',
            description_template='HF disruption at critical times: {} instances detected'
        )

        return alerts, critical_hf

    def _rule_4_4_pump_dump(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['sell_account_id'].notna()) &
            (trades['price'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # add date for daily aggregation
        trades_clean['trade_date'] = trades_clean['timestamp'].dt.date

        # calculate daily price and volume metrics
        daily_metrics = trades_clean.groupby(['instrument_id', 'trade_date'], observed=True).agg({
            'price': ['first', 'last', 'mean'],
            'quantity': ['sum'],
            'trade_id': ['count']
        }).reset_index()

        daily_metrics.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in daily_metrics.columns.values]

        # calculate rolling metrics
        daily_metrics = daily_metrics.sort_values(
            ['instrument_id', 'trade_date'])

        daily_metrics['price_change_pct'] = daily_metrics.groupby(
            'instrument_id', observed=True)['price_last'].pct_change()

        daily_metrics['volume_ma'] = daily_metrics.groupby('instrument_id', observed=True)['quantity_sum'].transform(
            lambda x: x.rolling(
                window=self.config.pump_accumulation_window_days, min_periods=1).mean()
        )

        daily_metrics['volume_ratio'] = daily_metrics['quantity_sum'] / \
            (daily_metrics['volume_ma'] + 1)

        # identify pump phases (price increase with volume spike)
        pump_days = daily_metrics[
            (daily_metrics['price_change_pct'] >= self.config.pump_price_increase_pct) &
            (daily_metrics['volume_ratio'] >=
             self.config.pump_volume_increase_multiplier)
        ].copy()

        if len(pump_days) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(pump_days):,} potential pump days")

        # look for dump phase (large sell-off after pump)
        pump_days['dump_window_start'] = pd.to_datetime(
            pump_days['trade_date'])
        pump_days['dump_window_end'] = pump_days['dump_window_start'] + \
            timedelta(hours=self.config.dump_window_hours)

        # match trades to pump days
        trades_clean['timestamp_date'] = pd.to_datetime(
            trades_clean['trade_date'])

        pump_trades = trades_clean.merge(
            pump_days[['instrument_id', 'trade_date']],
            on=['instrument_id', 'trade_date'],
            how='inner'
        )

        # identify accounts with significant selling after pump
        dump_window_trades = []

        for _, pump in pump_days.iterrows():
            instrument_trades = trades_clean[
                (trades_clean['instrument_id'] == pump['instrument_id']) &
                (trades_clean['timestamp'] >= pump['dump_window_start']) &
                (trades_clean['timestamp'] <= pump['dump_window_end'])
            ].copy()

            if len(instrument_trades) > 0:
                instrument_trades['pump_date'] = pump['trade_date']
                dump_window_trades.append(instrument_trades)

        if not dump_window_trades:
            return [], pd.DataFrame()

        dump_trades = pd.concat(dump_window_trades, ignore_index=True)

        # calculate net positions
        buy_positions = dump_trades.groupby(['instrument_id', 'pump_date', 'buy_account_id'], observed=True)[
            'quantity'].sum().reset_index()
        buy_positions.columns = ['instrument_id',
                                 'pump_date', 'account_id', 'buy_volume']

        sell_positions = dump_trades.groupby(['instrument_id', 'pump_date', 'sell_account_id'], observed=True)[
            'quantity'].sum().reset_index()
        sell_positions.columns = ['instrument_id',
                                  'pump_date', 'account_id', 'sell_volume']

        positions = buy_positions.merge(
            sell_positions,
            on=['instrument_id', 'pump_date', 'account_id'],
            how='outer'
        ).fillna({'buy_volume': 0, 'sell_volume': 0})

        positions['net_position'] = positions['sell_volume'] - \
            positions['buy_volume']

        # identify accounts with significant selling (dump)
        dump_patterns = positions[positions['net_position'] > 0].copy()

        if len(dump_patterns) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(dump_patterns):,} potential pump-dump patterns")

        # aggregate by account
        grouped = dump_patterns.groupby(['account_id', 'instrument_id'], observed=True).agg({
            'pump_date': ['count'],
            'net_position': ['sum', 'mean']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['pump_date_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='4.4',
            account_col='account_id',
            count_col='pump_date_count',
            description_template='Pump and dump: {} instances detected'
        )

        return alerts, dump_patterns

    def _generate_alerts(self, grouped: pd.DataFrame, rule_id: str,
                         account_col: str, count_col: str,
                         description_template: str) -> List[Alert]:

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
            alert = Alert(
                alert_id=f"MANIP_{rule_id.replace('.', '_')}_{uuid.uuid4().hex[:8]}",
                category="market_manipulation",
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

    manip_config = ManipulationConfig(
        data_config=data_config,
        save_intermediates=True
    )

    print("Market Surveillance Engine - Category 4: Market Manipulation (VECTORIZED)")
    print("="*80)

    loader = ArrowDataLoader(data_config)
    writer = ArrowDataWriter(data_config)

    start_time = time.time()

    detector = VectorizedManipulationDetector(manip_config, loader, writer)
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
