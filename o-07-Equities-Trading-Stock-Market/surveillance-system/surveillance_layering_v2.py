# surveillance_layering_v2.py

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
class LayeringConfig:
    data_config: DataConfig = None
    layering_min_orders: int = 3
    layering_max_orders: int = 20
    layering_order_window_seconds: int = 60
    layering_execution_window_seconds: int = 300
    layering_cancel_window_seconds: int = 120
    layering_min_price_levels: int = 2
    spoofing_anchor_size_multiplier: float = 10.0
    spoofing_cancel_time_pct: float = 0.9
    spoofing_execution_window_seconds: int = 300
    quote_stuffing_orders_per_minute: int = 50
    quote_stuffing_cancel_rate: float = 0.8
    quote_stuffing_avg_lifespan_seconds: float = 1.0
    momentum_price_change_pct: float = 0.02
    momentum_time_window_seconds: int = 300
    momentum_min_trades: int = 5
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


class VectorizedLayeringDetector:
    def __init__(self, config: LayeringConfig, loader: ArrowDataLoader, writer: ArrowDataWriter):
        self.config = config
        self.loader = loader
        self.writer = writer
        self.category = "layering_spoofing"
        self.optimizer = DataOptimizer()

    def execute(self) -> pd.DataFrame:
        print("\n" + "="*80)
        print("CATEGORY 2: LAYERING AND SPOOFING DETECTION (VECTORIZED)")
        print("="*80)

        print("\nLoading required data...")

        order_cols = ['order_id', 'timestamp', 'account_id', 'trader_id', 'firm_id',
                      'instrument_id', 'order_type', 'side', 'quantity', 'displayed_quantity',
                      'price', 'order_state', 'venue_id']

        cancel_cols = ['cancellation_id', 'timestamp', 'order_id', 'account_id',
                       'instrument_id', 'remaining_quantity', 'reason']

        trade_cols = ['trade_id', 'timestamp', 'instrument_id', 'buy_order_id',
                      'sell_order_id', 'buy_account_id', 'sell_account_id',
                      'quantity', 'price', 'aggressor_side']

        orders = self.loader.load_table('orders', columns=order_cols)
        cancellations = self.loader.load_table(
            'cancellations', columns=cancel_cols)
        trades = self.loader.load_table('trades', columns=trade_cols)

        orders = self.optimizer.optimize_dtypes(orders)
        cancellations = self.optimizer.optimize_dtypes(cancellations)
        trades = self.optimizer.optimize_dtypes(trades)

        orders = self.optimizer.convert_timestamps(orders, ['timestamp'])
        cancellations = self.optimizer.convert_timestamps(
            cancellations, ['timestamp'])
        trades = self.optimizer.convert_timestamps(trades, ['timestamp'])

        orders = orders.dropna(subset=['timestamp'])
        cancellations = cancellations.dropna(subset=['timestamp'])
        trades = trades.dropna(subset=['timestamp'])

        print(
            f"Loaded {len(orders):,} orders, {len(cancellations):,} cancellations, {len(trades):,} trades")

        alerts = []

        print("\nExecuting Rule 2.1: Classic Layering Pattern (Vectorized)...")
        alerts_2_1, intermediates_2_1 = self._rule_2_1_vectorized(
            orders, cancellations, trades)
        alerts.extend(alerts_2_1)
        if self.config.save_intermediates and not intermediates_2_1.empty:
            self.writer.write_table(
                intermediates_2_1, self.category, 'intermediate', 'rule_2_1_candidates')

        print("\nExecuting Rule 2.2: Spoofing (Vectorized)...")
        alerts_2_2, intermediates_2_2 = self._rule_2_2_vectorized(
            orders, cancellations, trades)
        alerts.extend(alerts_2_2)
        if self.config.save_intermediates and not intermediates_2_2.empty:
            self.writer.write_table(
                intermediates_2_2, self.category, 'intermediate', 'rule_2_2_candidates')

        print("\nExecuting Rule 2.3: Quote Stuffing (Vectorized)...")
        alerts_2_3, intermediates_2_3 = self._rule_2_3_vectorized(
            orders, cancellations)
        alerts.extend(alerts_2_3)
        if self.config.save_intermediates and not intermediates_2_3.empty:
            self.writer.write_table(
                intermediates_2_3, self.category, 'intermediate', 'rule_2_3_candidates')

        print("\nExecuting Rule 2.4: Momentum Ignition (Vectorized)...")
        alerts_2_4, intermediates_2_4 = self._rule_2_4_vectorized(
            orders, trades)
        alerts.extend(alerts_2_4)
        if self.config.save_intermediates and not intermediates_2_4.empty:
            self.writer.write_table(
                intermediates_2_4, self.category, 'intermediate', 'rule_2_4_candidates')

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

    def _rule_2_1_vectorized(self, orders: pd.DataFrame, cancellations: pd.DataFrame,
                             trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        limit_orders = orders[
            (orders['order_type'] == 'limit') &
            (orders['account_id'].notna()) &
            (orders['instrument_id'].notna()) &
            (orders['price'].notna())
        ].copy()

        if len(limit_orders) == 0:
            return [], pd.DataFrame()

        # merge cancellation times
        orders_with_cancel = limit_orders.merge(
            cancellations[['order_id', 'timestamp']].rename(
                columns={'timestamp': 'cancel_timestamp'}),
            on='order_id',
            how='left'
        )

        # sort for efficient window operations
        orders_with_cancel = orders_with_cancel.sort_values(
            ['account_id', 'instrument_id', 'side', 'timestamp'])

        # create time-based grouping key for clustering orders
        orders_with_cancel['time_bucket'] = (
            orders_with_cancel['timestamp'].astype(
                'int64') // 10**9 // self.config.layering_order_window_seconds
        )

        # group orders by account, instrument, side, time bucket
        order_clusters = orders_with_cancel.groupby(
            ['account_id', 'instrument_id', 'side', 'time_bucket'],
            observed=True
        ).agg({
            'order_id': ['count'],
            'price': ['nunique', 'min', 'max'],
            'quantity': ['sum'],
            'timestamp': ['min', 'max'],
            'cancel_timestamp': ['count']
        }).reset_index()

        order_clusters.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in order_clusters.columns.values]

        # filter clusters with sufficient orders and price levels
        layer_candidates = order_clusters[
            (order_clusters['order_id_count'] >= self.config.layering_min_orders) &
            (order_clusters['price_nunique'] >=
             self.config.layering_min_price_levels)
        ].copy()

        if len(layer_candidates) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(layer_candidates):,} potential layer clusters")

        # vectorized merge to find opposite side executions
        layer_candidates['execution_window_start'] = pd.to_datetime(
            layer_candidates['timestamp_min'])
        layer_candidates['execution_window_end'] = (
            layer_candidates['execution_window_start'] +
            timedelta(seconds=self.config.layering_execution_window_seconds)
        )

        # create opposite side mapping
        layer_candidates['opposite_side'] = layer_candidates['side'].map(
            {'buy': 'sell', 'sell': 'buy'})

        # prepare trades for matching
        trades['buy_or_sell'] = 'buy'
        trades_buy = trades[['timestamp', 'instrument_id',
                             'buy_account_id', 'quantity']].copy()
        trades_buy.columns = ['trade_time',
                              'instrument_id', 'account_id', 'trade_quantity']
        trades_buy['trade_side'] = 'buy'

        trades_sell = trades[['timestamp', 'instrument_id',
                              'sell_account_id', 'quantity']].copy()
        trades_sell.columns = ['trade_time',
                               'instrument_id', 'account_id', 'trade_quantity']
        trades_sell['trade_side'] = 'sell'

        all_trades = pd.concat([trades_buy, trades_sell], ignore_index=True)

        # merge to find executions for each layer cluster
        matched = layer_candidates.merge(
            all_trades,
            left_on=['account_id', 'instrument_id', 'opposite_side'],
            right_on=['account_id', 'instrument_id', 'trade_side'],
            how='inner'
        )

        # filter to execution window
        matched = matched[
            (matched['trade_time'] >= matched['execution_window_start']) &
            (matched['trade_time'] <= matched['execution_window_end'])
        ]

        if len(matched) == 0:
            return [], pd.DataFrame()

        # calculate cancellation metrics
        matched['cancel_rate'] = matched['cancel_timestamp_count'] / \
            matched['order_id_count']

        # filter by cancel rate threshold
        layer_patterns = matched[matched['cancel_rate'] >= 0.5].copy()

        if len(layer_patterns) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(layer_patterns):,} layering patterns")

        # aggregate by account and instrument
        grouped = layer_patterns.groupby(['account_id', 'instrument_id'], observed=True).agg({
            'side': ['first'],
            'order_id_count': ['sum', 'mean'],
            'trade_quantity': ['sum'],
            'cancel_rate': ['mean'],
            'time_bucket': ['count']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['time_bucket_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='2.1',
            count_col='time_bucket_count',
            description_template='Classic layering: {} patterns detected'
        )

        return alerts, layer_patterns

    def _rule_2_2_vectorized(self, orders: pd.DataFrame, cancellations: pd.DataFrame,
                             trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        orders_clean = orders[
            (orders['account_id'].notna()) &
            (orders['instrument_id'].notna()) &
            (orders['quantity'].notna())
        ].copy()

        if len(orders_clean) == 0:
            return [], pd.DataFrame()

        # calculate typical sizes vectorized
        order_size_stats = orders_clean.groupby(['account_id', 'instrument_id'], observed=True)[
            'quantity'].agg(['mean', 'std']).reset_index()
        order_size_stats.columns = ['account_id',
                                    'instrument_id', 'typical_size', 'size_std']

        orders_with_stats = orders_clean.merge(
            order_size_stats, on=['account_id', 'instrument_id'], how='left')

        # identify anchor orders vectorized
        orders_with_stats['size_multiple'] = orders_with_stats['quantity'] / \
            (orders_with_stats['typical_size'] + 1)
        anchor_orders = orders_with_stats[
            orders_with_stats['size_multiple'] >= self.config.spoofing_anchor_size_multiplier
        ].copy()

        if len(anchor_orders) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(anchor_orders):,} potential anchor orders")

        # merge cancellations vectorized
        anchors_with_cancel = anchor_orders.merge(
            cancellations[['order_id', 'timestamp']].rename(
                columns={'timestamp': 'cancel_timestamp'}),
            on='order_id',
            how='inner'
        )

        if len(anchors_with_cancel) == 0:
            return [], pd.DataFrame()

        # calculate execution window bounds vectorized
        anchors_with_cancel['execution_window_end'] = (
            anchors_with_cancel['timestamp'] +
            timedelta(seconds=self.config.spoofing_execution_window_seconds)
        )
        anchors_with_cancel['opposite_side'] = anchors_with_cancel['side'].map(
            {'buy': 'sell', 'sell': 'buy'})

        # prepare trades
        trades_buy = trades[['timestamp', 'instrument_id',
                             'buy_account_id', 'quantity']].copy()
        trades_buy.columns = ['trade_time',
                              'instrument_id', 'account_id', 'trade_quantity']
        trades_buy['trade_side'] = 'buy'

        trades_sell = trades[['timestamp', 'instrument_id',
                              'sell_account_id', 'quantity']].copy()
        trades_sell.columns = ['trade_time',
                               'instrument_id', 'account_id', 'trade_quantity']
        trades_sell['trade_side'] = 'sell'

        all_trades = pd.concat([trades_buy, trades_sell], ignore_index=True)

        # merge to find opposite executions vectorized
        matched = anchors_with_cancel.merge(
            all_trades,
            left_on=['account_id', 'instrument_id', 'opposite_side'],
            right_on=['account_id', 'instrument_id', 'trade_side'],
            how='inner'
        )

        # filter to execution window vectorized
        matched = matched[
            (matched['trade_time'] >= matched['timestamp']) &
            (matched['trade_time'] <= matched['execution_window_end'])
        ]

        if len(matched) == 0:
            return [], pd.DataFrame()

        # calculate timing metrics vectorized
        matched['time_to_cancel'] = (
            matched['cancel_timestamp'] - matched['timestamp']).dt.total_seconds()
        matched['time_to_execution'] = (
            matched['trade_time'] - matched['timestamp']).dt.total_seconds()
        matched['cancel_after_execution'] = (
            matched['cancel_timestamp'] - matched['trade_time']).dt.total_seconds()

        # apply spoofing criteria vectorized
        spoof_patterns = matched[
            (matched['time_to_cancel'] > matched['time_to_execution'] * self.config.spoofing_cancel_time_pct) &
            (matched['cancel_after_execution'] <= 60)
        ].copy()

        if len(spoof_patterns) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(spoof_patterns):,} spoofing patterns")

        # aggregate vectorized
        grouped = spoof_patterns.groupby(['account_id', 'instrument_id'], observed=True).agg({
            'side': ['first'],
            'size_multiple': ['mean'],
            'trade_quantity': ['sum'],
            'cancel_after_execution': ['mean'],
            'order_id': ['count']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['order_id_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='2.2',
            count_col='order_id_count',
            description_template='Spoofing detected: {} patterns'
        )

        return alerts, spoof_patterns

    def _rule_2_3_vectorized(self, orders: pd.DataFrame,
                             cancellations: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        orders_clean = orders[
            (orders['account_id'].notna()) &
            (orders['instrument_id'].notna())
        ].copy()

        if len(orders_clean) == 0:
            return [], pd.DataFrame()

        # create minute buckets vectorized
        orders_clean['minute'] = orders_clean['timestamp'].dt.floor('min')

        # count orders per minute vectorized
        order_rate = orders_clean.groupby(['account_id', 'instrument_id', 'minute'], observed=True).agg({
            'order_id': ['count']
        }).reset_index()
        order_rate.columns = ['account_id',
                              'instrument_id', 'minute', 'orders_per_minute']

        # filter high rate periods vectorized
        high_rate = order_rate[
            order_rate['orders_per_minute'] >= self.config.quote_stuffing_orders_per_minute
        ].copy()

        if len(high_rate) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(high_rate):,} high-rate periods")

        # merge orders with high rate periods
        period_orders = orders_clean.merge(
            high_rate[['account_id', 'instrument_id', 'minute']],
            on=['account_id', 'instrument_id', 'minute'],
            how='inner'
        )

        # merge with cancellations vectorized
        period_orders_with_cancel = period_orders.merge(
            cancellations[['order_id', 'timestamp']].rename(
                columns={'timestamp': 'cancel_timestamp'}),
            on='order_id',
            how='left'
        )

        # calculate lifespan vectorized
        period_orders_with_cancel['lifespan'] = (
            period_orders_with_cancel['cancel_timestamp'] -
            period_orders_with_cancel['timestamp']
        ).dt.total_seconds()

        # aggregate metrics per period vectorized
        period_metrics = period_orders_with_cancel.groupby(
            ['account_id', 'instrument_id', 'minute'],
            observed=True
        ).agg({
            'order_id': ['count'],
            'cancel_timestamp': ['count'],
            'lifespan': ['mean']
        }).reset_index()

        period_metrics.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in period_metrics.columns.values]

        # calculate cancel rate vectorized
        period_metrics['cancel_rate'] = period_metrics['cancel_timestamp_count'] / \
            period_metrics['order_id_count']

        # filter by criteria vectorized
        stuffing_patterns = period_metrics[
            (period_metrics['cancel_rate'] >= self.config.quote_stuffing_cancel_rate) &
            (period_metrics['lifespan_mean'] <=
             self.config.quote_stuffing_avg_lifespan_seconds)
        ].copy()

        if len(stuffing_patterns) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(stuffing_patterns):,} quote stuffing patterns")

        # aggregate by account and instrument vectorized
        grouped = stuffing_patterns.groupby(['account_id', 'instrument_id'], observed=True).agg({
            'order_id_count': ['sum', 'mean', 'max'],
            'cancel_rate': ['mean'],
            'lifespan_mean': ['mean'],
            'minute': ['count']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['minute_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='2.3',
            count_col='minute_count',
            description_template='Quote stuffing: {} high-rate periods'
        )

        return alerts, stuffing_patterns

    def _rule_2_4_vectorized(self, orders: pd.DataFrame,
                             trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['sell_account_id'].notna()) &
            (trades['price'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # sort for window operations
        trades_clean = trades_clean.sort_values(['instrument_id', 'timestamp'])

        # create time windows vectorized
        trades_clean['window_id'] = (
            trades_clean.groupby('instrument_id', observed=True)['timestamp']
            .transform(lambda x: (x.astype('int64') // 10**9 // self.config.momentum_time_window_seconds))
        )

        # calculate price changes per window vectorized
        window_stats = trades_clean.groupby(['instrument_id', 'window_id'], observed=True).agg({
            'timestamp': ['min', 'max', 'count'],
            'price': ['first', 'last'],
            'trade_id': ['count']
        }).reset_index()

        window_stats.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in window_stats.columns.values]

        # calculate price change percentage vectorized
        window_stats['price_change_pct'] = np.abs(
            window_stats['price_last'] - window_stats['price_first']
        ) / window_stats['price_first']

        # filter windows with significant price movement
        significant_windows = window_stats[
            (window_stats['price_change_pct'] >= self.config.momentum_price_change_pct) &
            (window_stats['trade_id_count'] >= self.config.momentum_min_trades)
        ].copy()

        if len(significant_windows) == 0:
            return [], pd.DataFrame()

        print(
            f"  Found {len(significant_windows):,} windows with significant price movement")

        # merge trades with significant windows
        window_trades = trades_clean.merge(
            significant_windows[['instrument_id', 'window_id']],
            on=['instrument_id', 'window_id'],
            how='inner'
        )

        # calculate account participation vectorized
        buy_participation = window_trades.groupby(
            ['instrument_id', 'window_id', 'buy_account_id'],
            observed=True
        ).size().reset_index(name='buy_count')

        sell_participation = window_trades.groupby(
            ['instrument_id', 'window_id', 'sell_account_id'],
            observed=True
        ).size().reset_index(name='sell_count')

        # combine buy and sell participation
        buy_participation.columns = [
            'instrument_id', 'window_id', 'account_id', 'participation_count']
        sell_participation.columns = [
            'instrument_id', 'window_id', 'account_id', 'participation_count']

        all_participation = pd.concat(
            [buy_participation, sell_participation], ignore_index=True)
        all_participation = all_participation.groupby(
            ['instrument_id', 'window_id', 'account_id'],
            observed=True
        )['participation_count'].sum().reset_index()

        # merge with window stats to calculate participation rate
        all_participation = all_participation.merge(
            significant_windows[['instrument_id',
                                 'window_id', 'trade_id_count']],
            on=['instrument_id', 'window_id'],
            how='left'
        )

        all_participation['participation_rate'] = (
            all_participation['participation_count'] /
            all_participation['trade_id_count']
        )

        # filter dominant accounts vectorized
        dominant_accounts = all_participation[
            all_participation['participation_rate'] >= 0.3
        ].copy()

        if len(dominant_accounts) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(dominant_accounts):,} dominant account patterns")

        # check for position reversal (simplified - checking if account both buys and sells)
        account_sides = window_trades.merge(
            dominant_accounts[['instrument_id', 'window_id', 'account_id']],
            left_on=['instrument_id', 'window_id', 'buy_account_id'],
            right_on=['instrument_id', 'window_id', 'account_id'],
            how='inner'
        )[['instrument_id', 'window_id', 'account_id', 'quantity']].copy()
        account_sides['side'] = 'buy'

        account_sides_sell = window_trades.merge(
            dominant_accounts[['instrument_id', 'window_id', 'account_id']],
            left_on=['instrument_id', 'window_id', 'sell_account_id'],
            right_on=['instrument_id', 'window_id', 'account_id'],
            how='inner'
        )[['instrument_id', 'window_id', 'account_id', 'quantity']].copy()
        account_sides_sell['side'] = 'sell'

        all_sides = pd.concat(
            [account_sides, account_sides_sell], ignore_index=True)

        # calculate net position per window vectorized
        net_positions = all_sides.groupby(
            ['instrument_id', 'window_id', 'account_id', 'side'],
            observed=True
        )['quantity'].sum().reset_index()

        net_positions_pivot = net_positions.pivot_table(
            index=['instrument_id', 'window_id', 'account_id'],
            columns='side',
            values='quantity',
            fill_value=0,
            observed=True
        ).reset_index()

        if 'buy' not in net_positions_pivot.columns:
            net_positions_pivot['buy'] = 0
        if 'sell' not in net_positions_pivot.columns:
            net_positions_pivot['sell'] = 0

        net_positions_pivot['net_position'] = net_positions_pivot['buy'] - \
            net_positions_pivot['sell']

        # merge with significant windows for price change info
        momentum_patterns = net_positions_pivot.merge(
            significant_windows[['instrument_id', 'window_id',
                                 'price_change_pct', 'trade_id_count']],
            on=['instrument_id', 'window_id'],
            how='left'
        )

        if len(momentum_patterns) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(momentum_patterns):,} momentum ignition patterns")

        # aggregate by account and instrument vectorized
        grouped = momentum_patterns.groupby(['account_id', 'instrument_id'], observed=True).agg({
            'price_change_pct': ['mean'],
            'net_position': ['mean'],
            'trade_id_count': ['sum'],
            'window_id': ['count']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['window_id_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='2.4',
            count_col='window_id_count',
            description_template='Momentum ignition: {} patterns detected'
        )

        return alerts, momentum_patterns

    def _generate_alerts(self, grouped: pd.DataFrame, rule_id: str,
                         count_col: str, description_template: str) -> List[Alert]:

        if grouped.empty:
            return []

        # assign severity vectorized
        grouped['severity'] = 'low'
        grouped.loc[grouped[count_col] >=
                    self.config.severity_medium_occurrences, 'severity'] = 'medium'
        grouped.loc[grouped[count_col] >=
                    self.config.severity_high_occurrences, 'severity'] = 'high'

        # calculate confidence vectorized
        grouped['confidence'] = np.minimum(0.95, 0.6 + grouped[count_col] / 15)

        alerts = []

        for idx, row in grouped.iterrows():
            alert = Alert(
                alert_id=f"LAYER_{rule_id.replace('.', '_')}_{uuid.uuid4().hex[:8]}",
                category="layering_spoofing",
                rule_id=rule_id,
                severity=row['severity'],
                timestamp=datetime.now().isoformat(),
                account_ids=[row['account_id']],
                instrument_ids=[row['instrument_id']],
                description=description_template.format(int(row[count_col])),
                evidence={'num_patterns': int(row[count_col])},
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

    layering_config = LayeringConfig(
        data_config=data_config,
        save_intermediates=True
    )

    print("Market Surveillance Engine - Category 2: Layering and Spoofing (VECTORIZED)")
    print("="*80)

    loader = ArrowDataLoader(data_config)
    writer = ArrowDataWriter(data_config)

    start_time = time.time()

    detector = VectorizedLayeringDetector(layering_config, loader, writer)
    alerts = detector.execute()

    elapsed = time.time() - start_time

    print("\n" + "="*80)
    print("EXECUTION COMPLETE")
    print("="*80)
    print(f"Results saved to: {data_config.output_dir}")
    print(f"Total alerts: {len(alerts)}")
    print(f"Execution time: {elapsed:.2f} seconds")
    print(
        f"Performance: {len(alerts)/elapsed:.1f} alerts/second" if elapsed > 0 else "")


if __name__ == "__main__":
    main()
