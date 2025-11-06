# surveillance_crossmarket.py

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
class CrossMarketConfig:
    data_config: DataConfig = None
    price_divergence_threshold_pct: float = 0.005
    arbitrage_time_window_seconds: int = 5
    arbitrage_min_profit_pct: float = 0.002
    arbitrage_min_occurrences: int = 3
    execution_quality_sample_size: int = 10
    execution_quality_threshold_pct: float = 0.003
    venue_shopping_min_venues: int = 3
    venue_shopping_min_occurrences: int = 5
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


class VectorizedCrossMarketDetector:
    def __init__(self, config: CrossMarketConfig, loader: ArrowDataLoader, writer: ArrowDataWriter):
        self.config = config
        self.loader = loader
        self.writer = writer
        self.category = "cross_market_manipulation"
        self.optimizer = DataOptimizer()

    def execute(self) -> pd.DataFrame:
        print("\n" + "="*80)
        print("CATEGORY 7: CROSS-MARKET MANIPULATION DETECTION (VECTORIZED)")
        print("="*80)

        print("\nLoading required data...")

        trade_cols = ['trade_id', 'timestamp', 'instrument_id', 'buy_account_id',
                      'sell_account_id', 'quantity', 'price', 'venue_id']

        order_cols = ['order_id', 'timestamp', 'account_id', 'instrument_id',
                      'side', 'quantity', 'price', 'venue_id']

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

        print("\nExecuting Rule 7.1: Cross-Venue Price Manipulation...")
        alerts_7_1, intermediates_7_1 = self._rule_7_1_price_manipulation(
            trades)
        alerts.extend(alerts_7_1)
        if self.config.save_intermediates and not intermediates_7_1.empty:
            self.writer.write_table(
                intermediates_7_1, self.category, 'intermediate', 'rule_7_1_candidates')

        print("\nExecuting Rule 7.2: Venue Arbitrage Abuse...")
        alerts_7_2, intermediates_7_2 = self._rule_7_2_arbitrage_abuse(trades)
        alerts.extend(alerts_7_2)
        if self.config.save_intermediates and not intermediates_7_2.empty:
            self.writer.write_table(
                intermediates_7_2, self.category, 'intermediate', 'rule_7_2_candidates')

        print("\nExecuting Rule 7.3: Best Execution Violations...")
        alerts_7_3, intermediates_7_3 = self._rule_7_3_best_execution(trades)
        alerts.extend(alerts_7_3)
        if self.config.save_intermediates and not intermediates_7_3.empty:
            self.writer.write_table(
                intermediates_7_3, self.category, 'intermediate', 'rule_7_3_candidates')

        print("\nExecuting Rule 7.4: Venue Shopping...")
        alerts_7_4, intermediates_7_4 = self._rule_7_4_venue_shopping(
            trades, orders)
        alerts.extend(alerts_7_4)
        if self.config.save_intermediates and not intermediates_7_4.empty:
            self.writer.write_table(
                intermediates_7_4, self.category, 'intermediate', 'rule_7_4_candidates')

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

    def _rule_7_1_price_manipulation(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['venue_id'].notna()) &
            (trades['price'].notna()) &
            (trades['buy_account_id'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # create time buckets for cross-venue comparison
        trades_clean['time_bucket'] = (
            trades_clean['timestamp'].astype('int64') // 10**9 // 60
        )

        # calculate average price per venue in each time bucket
        venue_prices = trades_clean.groupby(['instrument_id', 'time_bucket', 'venue_id'], observed=True).agg({
            'price': ['mean', 'count']
        }).reset_index()

        venue_prices.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in venue_prices.columns.values]

        # filter to buckets with multiple venues
        multi_venue = venue_prices.groupby(['instrument_id', 'time_bucket'], observed=True)[
            'venue_id'].count().reset_index(name='num_venues')
        multi_venue = multi_venue[multi_venue['num_venues'] >= 2]

        if len(multi_venue) == 0:
            return [], pd.DataFrame()

        # merge back to get prices
        venue_prices_filtered = venue_prices.merge(
            multi_venue[['instrument_id', 'time_bucket']],
            on=['instrument_id', 'time_bucket'],
            how='inner'
        )

        # calculate price divergence within each bucket
        price_stats = venue_prices_filtered.groupby(['instrument_id', 'time_bucket'], observed=True).agg({
            'price_mean': ['min', 'max', 'mean']
        }).reset_index()

        price_stats.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in price_stats.columns.values]

        price_stats['price_divergence_pct'] = (
            (price_stats['price_mean_max'] - price_stats['price_mean_min']) /
            price_stats['price_mean_mean']
        )

        # identify suspicious divergence
        suspicious = price_stats[
            price_stats['price_divergence_pct'] >= self.config.price_divergence_threshold_pct
        ].copy()

        if len(suspicious) == 0:
            return [], pd.DataFrame()

        print(
            f"  Found {len(suspicious):,} suspicious price divergence patterns")

        # match back to trades to find accounts
        suspicious_trades = trades_clean.merge(
            suspicious[['instrument_id', 'time_bucket']],
            on=['instrument_id', 'time_bucket'],
            how='inner'
        )

        # identify accounts trading across venues with divergent prices
        account_activity = suspicious_trades.groupby(['instrument_id', 'time_bucket', 'buy_account_id'], observed=True).agg({
            'venue_id': ['nunique']
        }).reset_index()

        account_activity.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in account_activity.columns.values]

        multi_venue_accounts = account_activity[account_activity['venue_id_nunique'] >= 2].copy(
        )

        if len(multi_venue_accounts) == 0:
            return [], pd.DataFrame()

        # aggregate by account
        grouped = multi_venue_accounts.groupby('buy_account_id', observed=True).agg({
            'time_bucket': ['count'],
            'instrument_id': ['nunique']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['time_bucket_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='7.1',
            account_col='buy_account_id',
            count_col='time_bucket_count',
            description_template='Cross-venue price manipulation: {} instances'
        )

        return alerts, suspicious

    def _rule_7_2_arbitrage_abuse(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['venue_id'].notna()) &
            (trades['price'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['sell_account_id'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # sort by instrument and time
        trades_clean = trades_clean.sort_values(['instrument_id', 'timestamp'])

        # create buy and sell views
        buy_trades = trades_clean[['timestamp', 'instrument_id',
                                   'buy_account_id', 'venue_id', 'price', 'quantity']].copy()
        buy_trades.columns = ['buy_time', 'instrument_id',
                              'account_id', 'buy_venue', 'buy_price', 'quantity']

        sell_trades = trades_clean[['timestamp', 'instrument_id',
                                    'sell_account_id', 'venue_id', 'price', 'quantity']].copy()
        sell_trades.columns = ['sell_time', 'instrument_id',
                               'account_id', 'sell_venue', 'sell_price', 'quantity']

        # ensure proper types and sort
        buy_trades['account_id'] = buy_trades['account_id'].astype(str)
        buy_trades['instrument_id'] = buy_trades['instrument_id'].astype(str)
        sell_trades['account_id'] = sell_trades['account_id'].astype(str)
        sell_trades['instrument_id'] = sell_trades['instrument_id'].astype(str)

        buy_trades = buy_trades.dropna(
            subset=['account_id', 'instrument_id', 'buy_time'])
        sell_trades = sell_trades.dropna(
            subset=['account_id', 'instrument_id', 'sell_time'])

        if len(buy_trades) == 0 or len(sell_trades) == 0:
            return [], pd.DataFrame()

        buy_trades = buy_trades.sort_values(
            ['account_id', 'instrument_id', 'buy_time']).reset_index(drop=True)
        sell_trades = sell_trades.sort_values(
            ['account_id', 'instrument_id', 'sell_time']).reset_index(drop=True)

        # use merge_asof to find quick round trips
        try:
            arbitrage_pairs = pd.merge_asof(
                buy_trades,
                sell_trades,
                by=['account_id', 'instrument_id'],
                left_on='buy_time',
                right_on='sell_time',
                direction='forward',
                tolerance=pd.Timedelta(
                    seconds=self.config.arbitrage_time_window_seconds),
                suffixes=('_buy', '_sell')
            )
        except:
            return [], pd.DataFrame()

        # filter to matched pairs
        arbitrage_pairs = arbitrage_pairs.dropna(subset=['sell_time'])

        if len(arbitrage_pairs) == 0:
            return [], pd.DataFrame()

        # filter to cross-venue arbitrage
        arbitrage_pairs = arbitrage_pairs[arbitrage_pairs['buy_venue']
                                          != arbitrage_pairs['sell_venue']]

        if len(arbitrage_pairs) == 0:
            return [], pd.DataFrame()

        # calculate profit
        arbitrage_pairs['profit_pct'] = (
            (arbitrage_pairs['sell_price'] - arbitrage_pairs['buy_price']) /
            arbitrage_pairs['buy_price']
        )

        # filter to profitable arbitrage
        profitable = arbitrage_pairs[
            arbitrage_pairs['profit_pct'] >= self.config.arbitrage_min_profit_pct
        ].copy()

        if len(profitable) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(profitable):,} arbitrage instances")

        # aggregate by account
        grouped = profitable.groupby('account_id', observed=True).agg({
            'buy_time': ['count'],
            'profit_pct': ['mean', 'sum'],
            'instrument_id': ['nunique']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['buy_time_count']
                          >= self.config.arbitrage_min_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='7.2',
            account_col='account_id',
            count_col='buy_time_count',
            description_template='Venue arbitrage abuse: {} instances'
        )

        return alerts, profitable

    def _rule_7_3_best_execution(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['venue_id'].notna()) &
            (trades['price'].notna()) &
            (trades['buy_account_id'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # create time buckets
        trades_clean['time_bucket'] = trades_clean['timestamp'].dt.floor('min')

        # calculate best available price per instrument/time
        best_prices = trades_clean.groupby(['instrument_id', 'time_bucket'], observed=True).agg({
            'price': ['min']
        }).reset_index()
        best_prices.columns = ['instrument_id', 'time_bucket', 'best_price']

        # merge back to get execution quality
        trades_with_best = trades_clean.merge(
            best_prices,
            on=['instrument_id', 'time_bucket'],
            how='left'
        )

        # calculate price slippage
        trades_with_best['slippage_pct'] = (
            (trades_with_best['price'] - trades_with_best['best_price']) /
            trades_with_best['best_price']
        )

        # identify poor executions
        poor_executions = trades_with_best[
            trades_with_best['slippage_pct'] >= self.config.execution_quality_threshold_pct
        ].copy()

        if len(poor_executions) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(poor_executions):,} poor execution instances")

        # aggregate by account
        grouped = poor_executions.groupby('buy_account_id', observed=True).agg({
            'trade_id': ['count'],
            'slippage_pct': ['mean'],
            'instrument_id': ['nunique'],
            'venue_id': ['nunique']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['trade_id_count'] >=
                          self.config.execution_quality_sample_size]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='7.3',
            account_col='buy_account_id',
            count_col='trade_id_count',
            description_template='Best execution violations: {} poor executions'
        )

        return alerts, poor_executions

    def _rule_7_4_venue_shopping(self, trades: pd.DataFrame,
                                 orders: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        orders_clean = orders[
            (orders['account_id'].notna()) &
            (orders['instrument_id'].notna()) &
            (orders['venue_id'].notna())
        ].copy()

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['venue_id'].notna()) &
            (trades['buy_account_id'].notna())
        ].copy()

        if len(orders_clean) == 0 or len(trades_clean) == 0:
            return [], pd.DataFrame()

        # analyze venue selection patterns
        order_venue_patterns = orders_clean.groupby(['account_id', 'instrument_id'], observed=True).agg({
            'venue_id': ['nunique', lambda x: list(x)]
        }).reset_index()

        order_venue_patterns.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in order_venue_patterns.columns.values]

        # filter to accounts using multiple venues
        multi_venue = order_venue_patterns[
            order_venue_patterns['venue_id_nunique'] >= self.config.venue_shopping_min_venues
        ].copy()

        if len(multi_venue) == 0:
            return [], pd.DataFrame()

        print(
            f"  Found {len(multi_venue):,} account-instrument pairs with multi-venue activity")

        # check execution outcomes across venues
        trade_outcomes = trades_clean.groupby(['buy_account_id', 'instrument_id', 'venue_id'], observed=True).agg({
            'price': ['mean'],
            'trade_id': ['count']
        }).reset_index()

        trade_outcomes.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in trade_outcomes.columns.values]

        # merge with multi-venue accounts
        shopping_patterns = multi_venue.merge(
            trade_outcomes,
            left_on=['account_id', 'instrument_id'],
            right_on=['buy_account_id', 'instrument_id'],
            how='inner'
        )

        if len(shopping_patterns) == 0:
            return [], pd.DataFrame()

        # calculate price variance across venues per account
        venue_variance = shopping_patterns.groupby(['account_id', 'instrument_id'], observed=True).agg({
            'price_mean': ['std'],
            'venue_id': ['count']
        }).reset_index()

        venue_variance.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in venue_variance.columns.values]

        # identify suspicious venue selection
        suspicious = venue_variance[
            (venue_variance['venue_id_count'] >= self.config.venue_shopping_min_venues) &
            (venue_variance['price_mean_std'] > 0)
        ].copy()

        if len(suspicious) == 0:
            return [], pd.DataFrame()

        # aggregate by account
        grouped = suspicious.groupby('account_id', observed=True).agg({
            'instrument_id': ['count'],
            'price_mean_std': ['mean']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['instrument_id_count']
                          >= self.config.venue_shopping_min_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='7.4',
            account_col='account_id',
            count_col='instrument_id_count',
            description_template='Venue shopping: {} instruments affected'
        )

        return alerts, suspicious

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
                alert_id=f"CROSS_{rule_id.replace('.', '_')}_{uuid.uuid4().hex[:8]}",
                category="cross_market_manipulation",
                rule_id=rule_id,
                severity=row['severity'],
                timestamp=datetime.now().isoformat(),
                account_ids=[row[account_col]],
                instrument_ids=[],
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

    cross_market_config = CrossMarketConfig(
        data_config=data_config,
        save_intermediates=True
    )

    print("Market Surveillance Engine - Category 7: Cross-Market Manipulation (VECTORIZED)")
    print("="*80)

    loader = ArrowDataLoader(data_config)
    writer = ArrowDataWriter(data_config)

    start_time = time.time()

    detector = VectorizedCrossMarketDetector(
        cross_market_config, loader, writer)
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
