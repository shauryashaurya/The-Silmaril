# surveillance_frontrunning.py

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
class FrontRunningConfig:
    data_config: DataConfig = None
    large_order_threshold_multiplier: float = 5.0
    front_run_time_window_seconds: int = 300
    front_run_min_occurrences: int = 3
    profit_threshold_pct: float = 0.005
    cross_account_time_window_seconds: int = 60
    min_instruments_for_pattern: int = 3
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


class VectorizedFrontRunningDetector:
    def __init__(self, config: FrontRunningConfig, loader: ArrowDataLoader, writer: ArrowDataWriter):
        self.config = config
        self.loader = loader
        self.writer = writer
        self.category = "front_running"
        self.optimizer = DataOptimizer()

    def execute(self) -> pd.DataFrame:
        print("\n" + "="*80)
        print("CATEGORY 3: FRONT RUNNING DETECTION (VECTORIZED)")
        print("="*80)

        print("\nLoading required data...")

        order_cols = ['order_id', 'timestamp', 'account_id', 'instrument_id',
                      'side', 'quantity', 'price', 'order_type', 'order_state']

        trade_cols = ['trade_id', 'timestamp', 'instrument_id', 'buy_order_id',
                      'sell_order_id', 'buy_account_id', 'sell_account_id',
                      'quantity', 'price']

        account_cols = ['account_id', 'beneficial_owner_id', 'firm_id',
                        'related_accounts']

        orders = self.loader.load_table('orders', columns=order_cols)
        trades = self.loader.load_table('trades', columns=trade_cols)
        accounts = self.loader.load_table('accounts', columns=account_cols)

        orders = self.optimizer.optimize_dtypes(orders)
        trades = self.optimizer.optimize_dtypes(trades)
        accounts = self.optimizer.optimize_dtypes(accounts)

        accounts = self.optimizer.parse_json_columns(
            accounts, ['related_accounts'])

        orders = self.optimizer.convert_timestamps(orders, ['timestamp'])
        trades = self.optimizer.convert_timestamps(trades, ['timestamp'])

        orders = orders.dropna(subset=['timestamp'])
        trades = trades.dropna(subset=['timestamp'])

        print(
            f"Loaded {len(orders):,} orders, {len(trades):,} trades, {len(accounts):,} accounts")

        alerts = []

        print("\nExecuting Rule 3.1: Temporal Front Running...")
        alerts_3_1, intermediates_3_1 = self._rule_3_1_temporal_frontrun(
            orders, trades)
        alerts.extend(alerts_3_1)
        if self.config.save_intermediates and not intermediates_3_1.empty:
            self.writer.write_table(
                intermediates_3_1, self.category, 'intermediate', 'rule_3_1_candidates')

        print("\nExecuting Rule 3.2: Consistent Pattern Detection...")
        alerts_3_2, intermediates_3_2 = self._rule_3_2_consistent_pattern(
            orders, trades)
        alerts.extend(alerts_3_2)
        if self.config.save_intermediates and not intermediates_3_2.empty:
            self.writer.write_table(
                intermediates_3_2, self.category, 'intermediate', 'rule_3_2_candidates')

        print("\nExecuting Rule 3.3: Cross-Account Front Running...")
        alerts_3_3, intermediates_3_3 = self._rule_3_3_cross_account(
            orders, trades, accounts)
        alerts.extend(alerts_3_3)
        if self.config.save_intermediates and not intermediates_3_3.empty:
            self.writer.write_table(
                intermediates_3_3, self.category, 'intermediate', 'rule_3_3_candidates')

        print("\nExecuting Rule 3.4: Beneficial Front Running...")
        alerts_3_4, intermediates_3_4 = self._rule_3_4_beneficial(
            orders, trades)
        alerts.extend(alerts_3_4)
        if self.config.save_intermediates and not intermediates_3_4.empty:
            self.writer.write_table(
                intermediates_3_4, self.category, 'intermediate', 'rule_3_4_candidates')

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

    def _rule_3_1_temporal_frontrun(self, orders: pd.DataFrame,
                                    trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        # filter clean orders
        orders_clean = orders[
            (orders['account_id'].notna()) &
            (orders['instrument_id'].notna()) &
            (orders['quantity'].notna())
        ].copy()

        if len(orders_clean) == 0:
            return [], pd.DataFrame()

        # calculate typical order sizes per instrument vectorized
        instrument_stats = orders_clean.groupby('instrument_id', observed=True)[
            'quantity'].agg(['mean', 'std']).reset_index()
        instrument_stats.columns = [
            'instrument_id', 'typical_size', 'size_std']

        # merge stats with orders
        orders_with_stats = orders_clean.merge(
            instrument_stats, on='instrument_id', how='left')

        # identify large orders vectorized
        orders_with_stats['size_multiple'] = orders_with_stats['quantity'] / \
            (orders_with_stats['typical_size'] + 1)
        large_orders = orders_with_stats[
            orders_with_stats['size_multiple'] >= self.config.large_order_threshold_multiplier
        ].copy()

        if len(large_orders) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(large_orders):,} large orders")

        # prepare for temporal matching - look for orders before large orders
        large_orders['lookback_start'] = large_orders['timestamp'] - \
            timedelta(seconds=self.config.front_run_time_window_seconds)

        # self-join to find preceding orders on same side/instrument
        preceding = orders_clean[[
            'order_id', 'timestamp', 'account_id', 'instrument_id', 'side', 'quantity']].copy()
        preceding.columns = ['front_order_id', 'front_time',
                             'front_account', 'instrument_id', 'side', 'front_quantity']

        # merge to find matching orders
        matched = large_orders.merge(
            preceding,
            on=['instrument_id', 'side'],
            how='inner'
        )

        # filter to time window vectorized
        matched = matched[
            (matched['front_time'] >= matched['lookback_start']) &
            (matched['front_time'] < matched['timestamp']) &
            (matched['front_account'] != matched['account_id'])
        ]

        if len(matched) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(matched):,} potential front-running instances")

        # calculate metrics vectorized
        matched['time_gap_seconds'] = (
            matched['timestamp'] - matched['front_time']).dt.total_seconds()
        matched['size_ratio'] = matched['front_quantity'] / matched['quantity']

        # aggregate by front-running account and instrument
        grouped = matched.groupby(['front_account', 'instrument_id'], observed=True).agg({
            'front_order_id': ['count'],
            'time_gap_seconds': ['mean'],
            'size_ratio': ['mean'],
            'quantity': ['sum'],
            'front_time': ['min', 'max']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['front_order_id_count']
                          >= self.config.front_run_min_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='3.1',
            account_col='front_account',
            count_col='front_order_id_count',
            description_template='Temporal front running: {} instances detected'
        )

        return alerts, matched

    def _rule_3_2_consistent_pattern(self, orders: pd.DataFrame,
                                     trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        orders_clean = orders[
            (orders['account_id'].notna()) &
            (orders['instrument_id'].notna()) &
            (orders['quantity'].notna())
        ].copy()

        if len(orders_clean) == 0:
            return [], pd.DataFrame()

        # calculate instrument stats
        instrument_stats = orders_clean.groupby('instrument_id', observed=True)[
            'quantity'].agg(['mean']).reset_index()
        instrument_stats.columns = ['instrument_id', 'typical_size']

        orders_with_stats = orders_clean.merge(
            instrument_stats, on='instrument_id', how='left')
        orders_with_stats['size_multiple'] = orders_with_stats['quantity'] / \
            (orders_with_stats['typical_size'] + 1)

        large_orders = orders_with_stats[
            orders_with_stats['size_multiple'] >= self.config.large_order_threshold_multiplier
        ].copy()

        if len(large_orders) == 0:
            return [], pd.DataFrame()

        # add time window for matching
        large_orders['lookback_start'] = large_orders['timestamp'] - \
            timedelta(seconds=self.config.front_run_time_window_seconds)

        # find preceding orders
        preceding = orders_clean[['order_id', 'timestamp',
                                  'account_id', 'instrument_id', 'side']].copy()
        preceding.columns = ['front_order_id', 'front_time',
                             'front_account', 'instrument_id', 'side']

        matched = large_orders.merge(
            preceding,
            on=['instrument_id', 'side'],
            how='inner'
        )

        matched = matched[
            (matched['front_time'] >= matched['lookback_start']) &
            (matched['front_time'] < matched['timestamp']) &
            (matched['front_account'] != matched['account_id'])
        ]

        if len(matched) == 0:
            return [], pd.DataFrame()

        # count unique instruments per account vectorized
        instrument_counts = matched.groupby('front_account', observed=True)[
            'instrument_id'].nunique().reset_index()
        instrument_counts.columns = ['front_account', 'num_instruments']

        # filter accounts with pattern across multiple instruments
        multi_instrument = instrument_counts[
            instrument_counts['num_instruments'] >= self.config.min_instruments_for_pattern
        ]

        if len(multi_instrument) == 0:
            return [], pd.DataFrame()

        print(
            f"  Found {len(multi_instrument):,} accounts with cross-instrument patterns")

        # merge back to get full details
        patterns = matched.merge(
            multi_instrument[['front_account']],
            on='front_account',
            how='inner'
        )

        # aggregate metrics
        grouped = patterns.groupby('front_account', observed=True).agg({
            'front_order_id': ['count'],
            'instrument_id': ['nunique'],
            'timestamp': ['min', 'max']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]

        # create instrument list for alerts
        instrument_summary = patterns.groupby('front_account', observed=True)['instrument_id'].apply(
            lambda x: list(x.unique())
        ).reset_index()
        instrument_summary.columns = ['front_account', 'instruments']

        grouped = grouped.merge(
            instrument_summary, on='front_account', how='left')

        alerts = []
        for idx, row in grouped.iterrows():
            if row['front_order_id_count'] >= self.config.severity_high_occurrences:
                severity = 'high'
            elif row['front_order_id_count'] >= self.config.severity_medium_occurrences:
                severity = 'medium'
            else:
                severity = 'low'

            confidence = min(0.90, 0.6 + (row['instrument_id_nunique'] / 10))

            alert = Alert(
                alert_id=f"FRONT_3_2_{uuid.uuid4().hex[:8]}",
                category="front_running",
                rule_id="3.2",
                severity=severity,
                timestamp=datetime.now().isoformat(),
                account_ids=[row['front_account']],
                instrument_ids=row['instruments'][:10],
                description=f"Consistent front running: {int(row['front_order_id_count'])} instances across {int(row['instrument_id_nunique'])} instruments",
                evidence={
                    'num_instances': int(row['front_order_id_count']),
                    'num_instruments': int(row['instrument_id_nunique'])
                },
                confidence_score=confidence
            )
            alerts.append(alert)

        return alerts, patterns

    def _rule_3_3_cross_account(self, orders: pd.DataFrame, trades: pd.DataFrame,
                                accounts: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        orders_clean = orders[
            (orders['account_id'].notna()) &
            (orders['instrument_id'].notna()) &
            (orders['quantity'].notna())
        ].copy()

        if len(orders_clean) == 0:
            return [], pd.DataFrame()

        # build related account pairs
        related_pairs = set()
        for _, acc in accounts.iterrows():
            if 'related_accounts_list' in acc and acc['related_accounts_list']:
                for related_id in acc['related_accounts_list']:
                    pair = tuple(sorted([acc['account_id'], related_id]))
                    related_pairs.add(pair)

        if not related_pairs:
            print("  No related account pairs found")
            return [], pd.DataFrame()

        # calculate instrument stats
        instrument_stats = orders_clean.groupby('instrument_id', observed=True)[
            'quantity'].agg(['mean']).reset_index()
        instrument_stats.columns = ['instrument_id', 'typical_size']

        orders_with_stats = orders_clean.merge(
            instrument_stats, on='instrument_id', how='left')
        orders_with_stats['size_multiple'] = orders_with_stats['quantity'] / \
            (orders_with_stats['typical_size'] + 1)

        large_orders = orders_with_stats[
            orders_with_stats['size_multiple'] >= self.config.large_order_threshold_multiplier
        ].copy()

        if len(large_orders) == 0:
            return [], pd.DataFrame()

        # look for coordinated orders from related accounts
        large_orders['lookback_start'] = large_orders['timestamp'] - \
            timedelta(seconds=self.config.cross_account_time_window_seconds)

        preceding = orders_clean[['order_id', 'timestamp',
                                  'account_id', 'instrument_id', 'side']].copy()
        preceding.columns = ['coord_order_id', 'coord_time',
                             'coord_account', 'instrument_id', 'side']

        matched = large_orders.merge(
            preceding,
            on=['instrument_id', 'side'],
            how='inner'
        )

        matched = matched[
            (matched['coord_time'] >= matched['lookback_start']) &
            (matched['coord_time'] < matched['timestamp'])
        ]

        if len(matched) == 0:
            return [], pd.DataFrame()

        # filter to related account pairs only vectorized
        matched['account_pair'] = matched.apply(
            lambda x: tuple(sorted([x['account_id'], x['coord_account']])),
            axis=1
        )

        coordinated = matched[matched['account_pair'].isin(
            related_pairs)].copy()

        if len(coordinated) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(coordinated):,} coordinated instances")

        # aggregate by account pair
        grouped = coordinated.groupby('account_pair', observed=True).agg({
            'coord_order_id': ['count'],
            'instrument_id': ['nunique'],
            'timestamp': ['min', 'max']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['coord_order_id_count']
                          >= self.config.front_run_min_occurrences]

        print(f"  Found {len(grouped):,} account pairs with repeated patterns")

        alerts = []
        for idx, row in grouped.iterrows():
            if row['coord_order_id_count'] >= self.config.severity_high_occurrences:
                severity = 'high'
            elif row['coord_order_id_count'] >= self.config.severity_medium_occurrences:
                severity = 'medium'
            else:
                severity = 'low'

            confidence = min(0.95, 0.7 + (row['coord_order_id_count'] / 15))

            alert = Alert(
                alert_id=f"FRONT_3_3_{uuid.uuid4().hex[:8]}",
                category="front_running",
                rule_id="3.3",
                severity=severity,
                timestamp=datetime.now().isoformat(),
                account_ids=list(row['account_pair']),
                instrument_ids=[],
                description=f"Cross-account front running: {int(row['coord_order_id_count'])} coordinated instances",
                evidence={
                    'num_instances': int(row['coord_order_id_count']),
                    'num_instruments': int(row['instrument_id_nunique'])
                },
                confidence_score=confidence
            )
            alerts.append(alert)

        return alerts, coordinated

    def _rule_3_4_beneficial(self, orders: pd.DataFrame,
                             trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        orders_clean = orders[
            (orders['account_id'].notna()) &
            (orders['instrument_id'].notna()) &
            (orders['quantity'].notna()) &
            (orders['price'].notna())
        ].copy()

        trades_clean = trades[
            (trades['buy_account_id'].notna()) &
            (trades['sell_account_id'].notna()) &
            (trades['price'].notna())
        ].copy()

        if len(orders_clean) == 0 or len(trades_clean) == 0:
            return [], pd.DataFrame()

        # merge orders with their executions
        buy_executions = orders_clean.merge(
            trades_clean[['buy_order_id', 'timestamp', 'price', 'quantity']],
            left_on='order_id',
            right_on='buy_order_id',
            how='inner',
            suffixes=('_order', '_trade')
        )
        buy_executions['side'] = 'buy'

        sell_executions = orders_clean.merge(
            trades_clean[['sell_order_id', 'timestamp', 'price', 'quantity']],
            left_on='order_id',
            right_on='sell_order_id',
            how='inner',
            suffixes=('_order', '_trade')
        )
        sell_executions['side'] = 'sell'

        all_executions = pd.concat(
            [buy_executions, sell_executions], ignore_index=True)

        if len(all_executions) == 0:
            return [], pd.DataFrame()

        # calculate profit potential vectorized
        all_executions = all_executions.sort_values(
            ['instrument_id', 'timestamp_trade'])

        # get next trade price for profit calculation
        all_executions['next_price'] = all_executions.groupby(
            'instrument_id', observed=True)['price_trade'].shift(-1)

        # calculate profit based on side
        all_executions['profit_pct'] = np.where(
            all_executions['side'] == 'buy',
            (all_executions['next_price'] - all_executions['price_trade']
             ) / all_executions['price_trade'],
            (all_executions['price_trade'] - all_executions['next_price']
             ) / all_executions['price_trade']
        )

        # filter to profitable trades
        profitable = all_executions[
            (all_executions['profit_pct'].notna()) &
            (all_executions['profit_pct'] >= self.config.profit_threshold_pct)
        ].copy()

        if len(profitable) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(profitable):,} profitable front-run executions")

        # aggregate by account
        grouped = profitable.groupby('account_id', observed=True).agg({
            'order_id': ['count'],
            'profit_pct': ['mean', 'sum'],
            'instrument_id': ['nunique'],
            'timestamp_order': ['min', 'max']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['order_id_count']
                          >= self.config.front_run_min_occurrences]

        print(f"  Found {len(grouped):,} accounts with profitable patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='3.4',
            account_col='account_id',
            count_col='order_id_count',
            description_template='Beneficial front running: {} profitable instances'
        )

        return alerts, profitable

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
                alert_id=f"FRONT_{rule_id.replace('.', '_')}_{uuid.uuid4().hex[:8]}",
                category="front_running",
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

    frontrun_config = FrontRunningConfig(
        data_config=data_config,
        save_intermediates=True
    )

    print("Market Surveillance Engine - Category 3: Front Running (VECTORIZED)")
    print("="*80)

    loader = ArrowDataLoader(data_config)
    writer = ArrowDataWriter(data_config)

    start_time = time.time()

    detector = VectorizedFrontRunningDetector(frontrun_config, loader, writer)
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
