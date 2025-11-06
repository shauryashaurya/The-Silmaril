# surveillance_benchmark.py

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
class BenchmarkConfig:
    data_config: DataConfig = None
    fixing_window_seconds_before: int = 300
    fixing_window_seconds_after: int = 60
    fixing_concentration_threshold: float = 0.25
    fixing_price_impact_pct: float = 0.005
    rate_submission_window_minutes: int = 30
    rate_manipulation_threshold: float = 0.01
    index_rebalance_window_days: int = 5
    index_volume_multiplier: float = 2.5
    settlement_window_minutes: int = 15
    settlement_concentration_threshold: float = 0.20
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


class VectorizedBenchmarkDetector:
    def __init__(self, config: BenchmarkConfig, loader: ArrowDataLoader, writer: ArrowDataWriter):
        self.config = config
        self.loader = loader
        self.writer = writer
        self.category = "benchmark_manipulation"
        self.optimizer = DataOptimizer()

    def execute(self) -> pd.DataFrame:
        print("\n" + "="*80)
        print("CATEGORY 8: BENCHMARK MANIPULATION DETECTION (VECTORIZED)")
        print("="*80)

        print("\nLoading required data...")

        trade_cols = ['trade_id', 'timestamp', 'instrument_id', 'buy_account_id',
                      'sell_account_id', 'quantity', 'price', 'trade_value']

        trades = self.loader.load_table('trades', columns=trade_cols)

        trades = self.optimizer.optimize_dtypes(trades)
        trades = self.optimizer.convert_timestamps(trades, ['timestamp'])
        trades = trades.dropna(subset=['timestamp'])

        print(f"Loaded {len(trades):,} trades")

        alerts = []

        print("\nExecuting Rule 8.1: Fixing Manipulation...")
        alerts_8_1, intermediates_8_1 = self._rule_8_1_fixing_manipulation(
            trades)
        alerts.extend(alerts_8_1)
        if self.config.save_intermediates and not intermediates_8_1.empty:
            self.writer.write_table(
                intermediates_8_1, self.category, 'intermediate', 'rule_8_1_candidates')

        print("\nExecuting Rule 8.2: Reference Rate Manipulation...")
        alerts_8_2, intermediates_8_2 = self._rule_8_2_rate_manipulation(
            trades)
        alerts.extend(alerts_8_2)
        if self.config.save_intermediates and not intermediates_8_2.empty:
            self.writer.write_table(
                intermediates_8_2, self.category, 'intermediate', 'rule_8_2_candidates')

        print("\nExecuting Rule 8.3: Index Constituent Manipulation...")
        alerts_8_3, intermediates_8_3 = self._rule_8_3_index_manipulation(
            trades)
        alerts.extend(alerts_8_3)
        if self.config.save_intermediates and not intermediates_8_3.empty:
            self.writer.write_table(
                intermediates_8_3, self.category, 'intermediate', 'rule_8_3_candidates')

        print("\nExecuting Rule 8.4: Settlement Price Manipulation...")
        alerts_8_4, intermediates_8_4 = self._rule_8_4_settlement_manipulation(
            trades)
        alerts.extend(alerts_8_4)
        if self.config.save_intermediates and not intermediates_8_4.empty:
            self.writer.write_table(
                intermediates_8_4, self.category, 'intermediate', 'rule_8_4_candidates')

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

    def _rule_8_1_fixing_manipulation(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['price'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # define fixing times (common benchmark times: 4pm London)
        trades_clean['trade_time'] = trades_clean['timestamp'].dt.time
        trades_clean['trade_date'] = trades_clean['timestamp'].dt.date

        # 4pm fixing window
        fixing_time = dt_time(16, 0)
        window_start = dt_time(15, 55)
        window_end = dt_time(16, 1)

        # identify fixing window trades
        trades_clean['is_fixing_window'] = (
            (trades_clean['trade_time'] >= window_start) &
            (trades_clean['trade_time'] <= window_end)
        )

        # calculate daily metrics
        daily_metrics = trades_clean.groupby(['instrument_id', 'trade_date'], observed=True).agg({
            'quantity': ['sum'],
            'trade_value': ['sum'],
            'price': ['first', 'last'],
            'trade_id': ['count']
        }).reset_index()

        daily_metrics.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in daily_metrics.columns.values]

        # calculate fixing window metrics
        fixing_trades = trades_clean[trades_clean['is_fixing_window']].copy()

        if len(fixing_trades) == 0:
            return [], pd.DataFrame()

        fixing_metrics = fixing_trades.groupby(['instrument_id', 'trade_date'], observed=True).agg({
            'quantity': ['sum'],
            'trade_value': ['sum'],
            'trade_id': ['count']
        }).reset_index()

        fixing_metrics.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in fixing_metrics.columns.values]

        # merge and calculate concentration
        combined = daily_metrics.merge(
            fixing_metrics,
            on=['instrument_id', 'trade_date'],
            how='left',
            suffixes=('_daily', '_fixing')
        )

        combined = combined.dropna(subset=['quantity_sum_fixing'])

        if len(combined) == 0:
            return [], pd.DataFrame()

        combined['volume_concentration'] = combined['quantity_sum_fixing'] / \
            combined['quantity_sum_daily']
        combined['price_change_pct'] = np.abs(
            combined['price_last'] - combined['price_first']
        ) / combined['price_first']

        # identify suspicious patterns
        suspicious = combined[
            (combined['volume_concentration'] >= self.config.fixing_concentration_threshold) &
            (combined['price_change_pct'] >=
             self.config.fixing_price_impact_pct)
        ].copy()

        if len(suspicious) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(suspicious):,} suspicious fixing patterns")

        # match to accounts
        fixing_detail = fixing_trades.merge(
            suspicious[['instrument_id', 'trade_date']],
            on=['instrument_id', 'trade_date'],
            how='inner'
        )

        # identify dominant accounts
        account_volumes = fixing_detail.groupby(['instrument_id', 'trade_date', 'buy_account_id'], observed=True).agg({
            'quantity': ['sum']
        }).reset_index()
        account_volumes.columns = ['instrument_id',
                                   'trade_date', 'account_id', 'volume']

        # get top account per pattern
        top_accounts = account_volumes.sort_values(
            ['instrument_id', 'trade_date', 'volume'],
            ascending=[True, True, False]
        ).groupby(['instrument_id', 'trade_date'], observed=True).first().reset_index()

        # merge with suspicious patterns
        patterns = suspicious.merge(
            top_accounts[['instrument_id', 'trade_date', 'account_id']],
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
            rule_id='8.1',
            account_col='account_id',
            count_col='trade_date_count',
            description_template='Fixing manipulation: {} instances detected'
        )

        return alerts, patterns

    def _rule_8_2_rate_manipulation(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['price'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # identify submission times (e.g., 11am for rate fixings)
        trades_clean['hour'] = trades_clean['timestamp'].dt.hour
        trades_clean['minute'] = trades_clean['timestamp'].dt.minute
        trades_clean['trade_date'] = trades_clean['timestamp'].dt.date

        # rate submission window (10:30-11:00)
        submission_window = (
            ((trades_clean['hour'] == 10) & (trades_clean['minute'] >= 30)) |
            ((trades_clean['hour'] == 11) & (trades_clean['minute'] == 0))
        )

        trades_clean['is_submission_window'] = submission_window

        # calculate price movements in submission window
        submission_trades = trades_clean[trades_clean['is_submission_window']].copy(
        )

        if len(submission_trades) == 0:
            return [], pd.DataFrame()

        # calculate price changes within submission window per day
        submission_prices = submission_trades.groupby(['instrument_id', 'trade_date'], observed=True).agg({
            'price': ['first', 'last', 'std'],
            'trade_id': ['count']
        }).reset_index()

        submission_prices.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in submission_prices.columns.values]

        submission_prices['price_move_pct'] = (
            (submission_prices['price_last'] - submission_prices['price_first']) /
            submission_prices['price_first']
        )

        # identify unusual movements
        suspicious = submission_prices[
            np.abs(submission_prices['price_move_pct']
                   ) >= self.config.rate_manipulation_threshold
        ].copy()

        if len(suspicious) == 0:
            return [], pd.DataFrame()

        print(
            f"  Found {len(suspicious):,} suspicious rate submission patterns")

        # match to accounts
        submission_detail = submission_trades.merge(
            suspicious[['instrument_id', 'trade_date']],
            on=['instrument_id', 'trade_date'],
            how='inner'
        )

        # aggregate by account
        grouped = submission_detail.groupby(['buy_account_id', 'instrument_id'], observed=True).agg({
            'trade_date': ['count'],
            'quantity': ['sum']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['trade_date_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='8.2',
            account_col='buy_account_id',
            count_col='trade_date_count',
            description_template='Reference rate manipulation: {} instances'
        )

        return alerts, suspicious

    def _rule_8_3_index_manipulation(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # calculate days to month end using datetime arithmetic
        trades_clean['month_end'] = trades_clean['timestamp'] + \
            pd.offsets.MonthEnd(0)
        trades_clean['days_to_month_end'] = (
            trades_clean['month_end'] - trades_clean['timestamp']).dt.days
        trades_clean['trade_date'] = trades_clean['timestamp'].dt.date

        # identify rebalance window
        trades_clean['is_rebalance_window'] = (
            trades_clean['days_to_month_end'] <= self.config.index_rebalance_window_days
        )

        # calculate baseline volume
        baseline_volume = trades_clean[~trades_clean['is_rebalance_window']].groupby(
            ['instrument_id', 'trade_date'],
            observed=True
        )['quantity'].sum().reset_index(name='baseline_volume')

        baseline_avg = baseline_volume.groupby('instrument_id', observed=True)[
            'baseline_volume'].mean().reset_index(name='avg_baseline')

        # calculate rebalance window volume
        rebalance_trades = trades_clean[trades_clean['is_rebalance_window']].copy(
        )

        if len(rebalance_trades) == 0:
            return [], pd.DataFrame()

        rebalance_volume = rebalance_trades.groupby(['instrument_id', 'trade_date'], observed=True).agg({
            'quantity': ['sum'],
            'trade_id': ['count']
        }).reset_index()

        rebalance_volume.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in rebalance_volume.columns.values]

        # merge with baseline
        rebalance_with_baseline = rebalance_volume.merge(
            baseline_avg, on='instrument_id', how='left')

        rebalance_with_baseline['volume_ratio'] = (
            rebalance_with_baseline['quantity_sum'] /
            (rebalance_with_baseline['avg_baseline'] + 1)
        )

        # identify suspicious volume spikes
        suspicious = rebalance_with_baseline[
            rebalance_with_baseline['volume_ratio'] >= self.config.index_volume_multiplier
        ].copy()

        if len(suspicious) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(suspicious):,} suspicious rebalance patterns")

        # match to accounts
        rebalance_detail = rebalance_trades.merge(
            suspicious[['instrument_id', 'trade_date']],
            on=['instrument_id', 'trade_date'],
            how='inner'
        )

        # aggregate by account
        grouped = rebalance_detail.groupby(['buy_account_id', 'instrument_id'], observed=True).agg({
            'trade_date': ['count'],
            'quantity': ['sum']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip('_')
                           for col in grouped.columns.values]
        grouped = grouped[grouped['trade_date_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='8.3',
            account_col='buy_account_id',
            count_col='trade_date_count',
            description_template='Index constituent manipulation: {} instances'
        )

        return alerts, suspicious

    def _rule_8_4_settlement_manipulation(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['price'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # identify settlement window (last 15 minutes of trading day)
        trades_clean['trade_time'] = trades_clean['timestamp'].dt.time
        trades_clean['trade_date'] = trades_clean['timestamp'].dt.date

        settlement_start = dt_time(15, 45)
        settlement_end = dt_time(16, 0)

        trades_clean['is_settlement_window'] = (
            (trades_clean['trade_time'] >= settlement_start) &
            (trades_clean['trade_time'] <= settlement_end)
        )

        # calculate daily metrics - rename columns explicitly
        daily_metrics = trades_clean.groupby(['instrument_id', 'trade_date'], observed=True).agg({
            'quantity': ['sum'],
            'price': ['first', 'last']
        }).reset_index()

        daily_metrics.columns = ['instrument_id', 'trade_date',
                                 'daily_quantity', 'daily_first_price', 'daily_last_price']

        # calculate settlement window metrics - rename explicitly
        settlement_trades = trades_clean[trades_clean['is_settlement_window']].copy(
        )

        if len(settlement_trades) == 0:
            return [], pd.DataFrame()

        settlement_metrics = settlement_trades.groupby(['instrument_id', 'trade_date'], observed=True).agg({
            'quantity': ['sum'],
            'price': ['last'],
            'trade_id': ['count']
        }).reset_index()

        settlement_metrics.columns = ['instrument_id', 'trade_date',
                                      'settlement_quantity', 'settlement_price', 'settlement_count']

        # merge with explicit column names - no suffix confusion
        combined = daily_metrics.merge(
            settlement_metrics,
            on=['instrument_id', 'trade_date'],
            how='left'
        )

        combined = combined.dropna(subset=['settlement_quantity'])

        if len(combined) == 0:
            return [], pd.DataFrame()

        combined['volume_concentration'] = combined['settlement_quantity'] / \
            combined['daily_quantity']
        combined['price_impact_pct'] = np.abs(
            combined['settlement_price'] - combined['daily_first_price']
        ) / combined['daily_first_price']

        # identify suspicious patterns
        suspicious = combined[
            combined['volume_concentration'] >= self.config.settlement_concentration_threshold
        ].copy()

        if len(suspicious) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(suspicious):,} suspicious settlement patterns")

        # match to accounts
        settlement_detail = settlement_trades.merge(
            suspicious[['instrument_id', 'trade_date']],
            on=['instrument_id', 'trade_date'],
            how='inner'
        )

        # identify dominant accounts
        account_volumes = settlement_detail.groupby(['instrument_id', 'trade_date', 'buy_account_id'], observed=True).agg({
            'quantity': ['sum']
        }).reset_index()
        account_volumes.columns = ['instrument_id',
                                   'trade_date', 'account_id', 'volume']

        # get top account per pattern
        top_accounts = account_volumes.sort_values(
            ['instrument_id', 'trade_date', 'volume'],
            ascending=[True, True, False]
        ).groupby(['instrument_id', 'trade_date'], observed=True).first().reset_index()

        # merge with suspicious patterns
        patterns = suspicious.merge(
            top_accounts[['instrument_id', 'trade_date', 'account_id']],
            on=['instrument_id', 'trade_date'],
            how='left'
        )

        # aggregate by account
        grouped = patterns.groupby(['account_id', 'instrument_id'], observed=True).agg({
            'trade_date': ['count'],
            'volume_concentration': ['mean']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['trade_date_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='8.4',
            account_col='account_id',
            count_col='trade_date_count',
            description_template='Settlement price manipulation: {} instances'
        )

        return alerts, patterns

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
                alert_id=f"BENCH_{rule_id.replace('.', '_')}_{uuid.uuid4().hex[:8]}",
                category="benchmark_manipulation",
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

    benchmark_config = BenchmarkConfig(
        data_config=data_config,
        save_intermediates=True
    )

    print("Market Surveillance Engine - Category 8: Benchmark Manipulation (VECTORIZED)")
    print("="*80)

    loader = ArrowDataLoader(data_config)
    writer = ArrowDataWriter(data_config)

    start_time = time.time()

    detector = VectorizedBenchmarkDetector(benchmark_config, loader, writer)
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
