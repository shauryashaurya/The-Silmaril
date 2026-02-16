# surveillance_insider_v2.py
# Improved insider trading detection with better baseline calculation

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
class InsiderConfig:
    data_config: DataConfig = None
    # Rule 5.1 (Pre-Announcement)
    pre_announcement_window_days: int = 14  # Look 14 days before
    abnormal_volume_zscore: float = 2.0  # 2 std devs above normal
    # Rule 5.2 (Network Trading)
    network_time_window_hours: int = 168  # 7 days
    network_min_accounts: int = 2
    # Rule 5.3 (Abnormal Profits)
    min_return_threshold_pct: float = 0.02  # 2% profit
    # Rule 5.4 (Leakage)
    leakage_cluster_window_hours: int = 72
    leakage_min_accounts: int = 2
    # General
    severity_high_occurrences: int = 3
    severity_medium_occurrences: int = 2
    severity_low_occurrences: int = 1
    save_intermediates: bool = True
    min_suspicious_events: int = 1

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


class ImprovedInsiderDetector:
    def __init__(self, config: InsiderConfig, loader: ArrowDataLoader, writer: ArrowDataWriter):
        self.config = config
        self.loader = loader
        self.writer = writer
        self.category = "insider_trading"
        self.optimizer = DataOptimizer()

    def execute(self) -> pd.DataFrame:
        print("\n" + "="*80)
        print("CATEGORY 5: INSIDER TRADING DETECTION (IMPROVED)")
        print("="*80)

        print("\nLoading required data...")

        trade_cols = ['trade_id', 'timestamp', 'instrument_id', 'buy_account_id',
                      'sell_account_id', 'quantity', 'price', 'trade_value']

        account_cols = ['account_id', 'beneficial_owner_id',
                        'firm_id', 'related_accounts']

        trades = self.loader.load_table('trades', columns=trade_cols)
        accounts = self.loader.load_table('accounts', columns=account_cols)

        # Check for corporate events
        try:
            event_cols = ['event_id', 'instrument_id',
                          'event_type', 'announcement_date', 'effective_date']
            events = self.loader.load_table(
                'corporate_events', columns=event_cols)
            print(f"  Loaded corporate_events table with {len(events)} events")
        except Exception as e:
            print(
                f"  Warning: corporate_events table not found ({e}), generating synthetic events")
            events = self._generate_synthetic_events(trades)

        trades = self.optimizer.optimize_dtypes(trades)
        accounts = self.optimizer.optimize_dtypes(accounts)
        events = self.optimizer.optimize_dtypes(events)

        accounts = self.optimizer.parse_json_columns(
            accounts, ['related_accounts'])

        trades = self.optimizer.convert_timestamps(trades, ['timestamp'])
        events = self.optimizer.convert_timestamps(
            events, ['announcement_date'])

        trades = trades.dropna(subset=['timestamp'])
        events = events.dropna(subset=['announcement_date'])

        print(
            f"Loaded {len(trades):,} trades, {len(accounts):,} accounts, {len(events):,} events")

        alerts = []

        print("\nExecuting Rule 5.1: Pre-Announcement Trading...")
        alerts_5_1, intermediates_5_1 = self._rule_5_1_pre_announcement_improved(
            trades, events)
        alerts.extend(alerts_5_1)
        if self.config.save_intermediates and not intermediates_5_1.empty:
            self.writer.write_table(
                intermediates_5_1, self.category, 'intermediate', 'rule_5_1_candidates')

        print("\nExecuting Rule 5.2: Insider Network Trading...")
        alerts_5_2, intermediates_5_2 = self._rule_5_2_network_trading_improved(
            trades, events, accounts)
        alerts.extend(alerts_5_2)
        if self.config.save_intermediates and not intermediates_5_2.empty:
            self.writer.write_table(
                intermediates_5_2, self.category, 'intermediate', 'rule_5_2_candidates')

        print("\nExecuting Rule 5.3: Abnormal Profit Patterns...")
        alerts_5_3, intermediates_5_3 = self._rule_5_3_abnormal_profits_improved(
            trades, events)
        alerts.extend(alerts_5_3)
        if self.config.save_intermediates and not intermediates_5_3.empty:
            self.writer.write_table(
                intermediates_5_3, self.category, 'intermediate', 'rule_5_3_candidates')

        print("\nExecuting Rule 5.4: Information Leakage...")
        alerts_5_4, intermediates_5_4 = self._rule_5_4_leakage_improved(
            trades, events)
        alerts.extend(alerts_5_4)
        if self.config.save_intermediates and not intermediates_5_4.empty:
            self.writer.write_table(
                intermediates_5_4, self.category, 'intermediate', 'rule_5_4_candidates')

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

    def _generate_synthetic_events(self, trades: pd.DataFrame) -> pd.DataFrame:
        """Generate synthetic events based on trade data."""
        instruments = trades['instrument_id'].unique()

        date_range = pd.date_range(
            start=trades['timestamp'].min(),
            end=trades['timestamp'].max(),
            freq='7d'
        )

        events = []
        event_types = ['earnings', 'merger', 'dividend', 'guidance']

        for instrument in instruments[:min(len(instruments), 50)]:
            for date in date_range[::3]:
                events.append({
                    'event_id': f"EVT_{uuid.uuid4().hex[:8]}",
                    'instrument_id': instrument,
                    'event_type': np.random.choice(event_types),
                    'announcement_date': date,
                    'effective_date': date + timedelta(days=7)
                })

        return pd.DataFrame(events)

    def _rule_5_1_pre_announcement_improved(self, trades: pd.DataFrame,
                                            events: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:
        """
        Improved pre-announcement detection:
        1. Excludes pre-announcement windows from baseline
        2. Uses Z-score for statistical significance
        3. Compares daily averages properly
        """
        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0 or len(events) == 0:
            return [], pd.DataFrame()

        trades_clean['trade_date'] = trades_clean['timestamp'].dt.date

        # Add event windows
        events['window_start'] = events['announcement_date'] - \
            timedelta(days=self.config.pre_announcement_window_days)
        events['window_end'] = events['announcement_date']

        # For each instrument, calculate clean baseline (excluding ALL event windows)
        instrument_baselines = {}

        for instrument_id in trades_clean['instrument_id'].unique():
            ins_trades = trades_clean[trades_clean['instrument_id'] == instrument_id].copy(
            )

            # Get all event windows for this instrument
            ins_events = events[events['instrument_id'] == instrument_id]

            # Mark trades that are in ANY event window
            ins_trades['in_event_window'] = False

            for _, event in ins_events.iterrows():
                in_window = (
                    (ins_trades['timestamp'] >= event['window_start']) &
                    (ins_trades['timestamp'] < event['window_end'])
                )
                ins_trades.loc[in_window, 'in_event_window'] = True

            # Baseline: only trades NOT in event windows
            baseline_trades = ins_trades[~ins_trades['in_event_window']]

            if len(baseline_trades) > 0:
                # Calculate daily volume statistics
                daily_baseline = baseline_trades.groupby(
                    'trade_date', observed=True)['quantity'].sum()

                if len(daily_baseline) > 0:
                    instrument_baselines[instrument_id] = {
                        'mean': daily_baseline.mean(),
                        'std': daily_baseline.std() if len(daily_baseline) > 1 else daily_baseline.mean() * 0.3,
                        'count': len(daily_baseline)
                    }

        if not instrument_baselines:
            return [], pd.DataFrame()

        print(
            f"  Calculated clean baselines for {len(instrument_baselines)} instruments")

        # Find abnormal pre-announcement trading
        suspicious_patterns = []

        for _, event in events.iterrows():
            instrument_id = event['instrument_id']

            if instrument_id not in instrument_baselines:
                continue

            baseline = instrument_baselines[instrument_id]

            # Get pre-announcement trades
            pre_trades = trades_clean[
                (trades_clean['instrument_id'] == instrument_id) &
                (trades_clean['timestamp'] >= event['window_start']) &
                (trades_clean['timestamp'] < event['window_end'])
            ]

            if len(pre_trades) == 0:
                continue

            # Calculate account volumes in pre-announcement window
            account_volumes = pre_trades.groupby('buy_account_id', observed=True).agg({
                'quantity': 'sum',
                'trade_date': 'nunique'
            }).reset_index()
            account_volumes.columns = [
                'account_id', 'total_volume', 'num_days']

            # Calculate daily average for each account
            account_volumes['daily_avg'] = account_volumes['total_volume'] / \
                account_volumes['num_days']

            # Calculate Z-score compared to baseline
            account_volumes['z_score'] = (
                account_volumes['daily_avg'] - baseline['mean']
            ) / (baseline['std'] + 0.01)  # Add small epsilon to prevent /0

            # Flag abnormal accounts
            abnormal = account_volumes[account_volumes['z_score']
                                       >= self.config.abnormal_volume_zscore].copy()

            if len(abnormal) > 0:
                for _, acc_row in abnormal.iterrows():
                    suspicious_patterns.append({
                        'event_id': event['event_id'],
                        'instrument_id': instrument_id,
                        'account_id': acc_row['account_id'],
                        'total_volume': acc_row['total_volume'],
                        'daily_avg': acc_row['daily_avg'],
                        'baseline_mean': baseline['mean'],
                        'baseline_std': baseline['std'],
                        'z_score': acc_row['z_score'],
                        'announcement_date': event['announcement_date']
                    })

        if not suspicious_patterns:
            print("  No suspicious pre-announcement patterns found")
            return [], pd.DataFrame()

        patterns_df = pd.DataFrame(suspicious_patterns)
        print(
            f"  Found {len(patterns_df):,} suspicious pre-announcement patterns")

        # Aggregate by account to find repeat offenders
        grouped = patterns_df.groupby('account_id', observed=True).agg({
            'event_id': 'count',
            'z_score': 'mean',
            'daily_avg': 'sum',
            'instrument_id': 'nunique'
        }).reset_index()

        grouped.columns = ['account_id', 'num_events',
                           'avg_z_score', 'total_volume', 'num_instruments']
        grouped = grouped[grouped['num_events']
                          >= self.config.min_suspicious_events]

        if len(grouped) == 0:
            print("  No accounts with repeated patterns")
            return [], pd.DataFrame()

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        # Generate alerts
        alerts = []
        for _, row in grouped.iterrows():
            # Get instruments for this account
            instruments = patterns_df[patterns_df['account_id'] ==
                                      row['account_id']]['instrument_id'].unique().tolist()

            severity = 'low'
            if row['num_events'] >= self.config.severity_high_occurrences:
                severity = 'high'
            elif row['num_events'] >= self.config.severity_medium_occurrences:
                severity = 'medium'

            confidence = min(
                0.95, 0.60 + (row['num_events'] * 0.1) + (row['avg_z_score'] * 0.05))

            alert = Alert(
                alert_id=f"INSIDER_5_1_{uuid.uuid4().hex[:8]}",
                category="insider_trading",
                rule_id="5.1",
                severity=severity,
                timestamp=datetime.now().isoformat(),
                account_ids=[row['account_id']],
                instrument_ids=instruments,
                description=f"Pre-announcement trading: {int(row['num_events'])} events, avg Z-score {row['avg_z_score']:.1f}",
                evidence={
                    'num_events': int(row['num_events']),
                    'avg_z_score': float(row['avg_z_score']),
                    'num_instruments': int(row['num_instruments']),
                    'total_volume': float(row['total_volume'])
                },
                confidence_score=confidence
            )
            alerts.append(alert)

        return alerts, patterns_df

    def _rule_5_2_network_trading_improved(self, trades: pd.DataFrame, events: pd.DataFrame,
                                           accounts: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:
        """Detect coordinated trading among related accounts before events."""
        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0 or len(events) == 0:
            return [], pd.DataFrame()

        # Build account relationship map
        account_relationships = {}
        for _, acc in accounts.iterrows():
            if acc['related_accounts'] and len(acc['related_accounts']) > 0:
                account_relationships[acc['account_id']
                                      ] = acc['related_accounts']

        if not account_relationships:
            print("  No account relationships found")
            return [], pd.DataFrame()

        # Add event windows
        events['window_start'] = events['announcement_date'] - \
            timedelta(hours=self.config.network_time_window_hours)

        # Find coordinated trading
        network_patterns = []

        for _, event in events.iterrows():
            # Get pre-announcement trades
            pre_trades = trades_clean[
                (trades_clean['instrument_id'] == event['instrument_id']) &
                (trades_clean['timestamp'] >= event['window_start']) &
                (trades_clean['timestamp'] < event['announcement_date'])
            ]

            if len(pre_trades) == 0:
                continue

            trading_accounts = pre_trades['buy_account_id'].unique()

            # Check for networks
            for primary_account in trading_accounts:
                if primary_account not in account_relationships:
                    continue

                related_accounts = account_relationships[primary_account]
                related_trading = [
                    acc for acc in related_accounts if acc in trading_accounts]

                # -1 because we count primary
                if len(related_trading) >= self.config.network_min_accounts - 1:
                    all_network_accounts = [primary_account] + related_trading

                    network_patterns.append({
                        'event_id': event['event_id'],
                        'instrument_id': event['instrument_id'],
                        'primary_account': primary_account,
                        'related_accounts': json.dumps(related_trading),
                        'num_network_accounts': len(all_network_accounts),
                        'announcement_date': event['announcement_date']
                    })

        if not network_patterns:
            print("  No network trading patterns found")
            return [], pd.DataFrame()

        patterns_df = pd.DataFrame(network_patterns)
        print(f"  Found {len(patterns_df):,} network trading patterns")

        # Aggregate by primary account
        grouped = patterns_df.groupby('primary_account', observed=True).agg({
            'event_id': 'count',
            'num_network_accounts': 'mean',
            'instrument_id': 'nunique'
        }).reset_index()

        grouped.columns = ['account_id', 'num_events',
                           'avg_network_size', 'num_instruments']
        grouped = grouped[grouped['num_events']
                          >= self.config.min_suspicious_events]

        if len(grouped) == 0:
            print("  No accounts with repeated network patterns")
            return [], pd.DataFrame()

        print(
            f"  Found {len(grouped):,} accounts with repeated network patterns")

        # Generate alerts
        alerts = []
        for _, row in grouped.iterrows():
            instruments = patterns_df[patterns_df['primary_account']
                                      == row['account_id']]['instrument_id'].unique().tolist()

            severity = 'low'
            if row['num_events'] >= self.config.severity_high_occurrences:
                severity = 'high'
            elif row['num_events'] >= self.config.severity_medium_occurrences:
                severity = 'medium'

            confidence = min(0.95, 0.65 + (row['num_events'] * 0.1))

            alert = Alert(
                alert_id=f"INSIDER_5_2_{uuid.uuid4().hex[:8]}",
                category="insider_trading",
                rule_id="5.2",
                severity=severity,
                timestamp=datetime.now().isoformat(),
                account_ids=[row['account_id']],
                instrument_ids=instruments,
                description=f"Network insider trading: {int(row['num_events'])} coordinated events",
                evidence={
                    'num_events': int(row['num_events']),
                    'avg_network_size': float(row['avg_network_size']),
                    'num_instruments': int(row['num_instruments'])
                },
                confidence_score=confidence
            )
            alerts.append(alert)

        return alerts, patterns_df

    def _rule_5_3_abnormal_profits_improved(self, trades: pd.DataFrame,
                                            events: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:
        """Detect accounts with consistent profits from pre-event trading."""
        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['price'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0 or len(events) == 0:
            return [], pd.DataFrame()

        # Add event windows
        events['pre_window_start'] = events['announcement_date'] - \
            timedelta(days=self.config.pre_announcement_window_days)
        events['post_window_end'] = events['announcement_date'] + \
            timedelta(days=7)

        profitable_patterns = []

        for _, event in events.iterrows():
            # Get pre-announcement buy trades
            pre_trades = trades_clean[
                (trades_clean['instrument_id'] == event['instrument_id']) &
                (trades_clean['timestamp'] >= event['pre_window_start']) &
                (trades_clean['timestamp'] < event['announcement_date'])
            ]

            if len(pre_trades) == 0:
                continue

            # Get post-announcement prices
            post_trades = trades_clean[
                (trades_clean['instrument_id'] == event['instrument_id']) &
                (trades_clean['timestamp'] >= event['announcement_date']) &
                (trades_clean['timestamp'] <= event['post_window_end'])
            ]

            if len(post_trades) == 0:
                continue

            # Calculate average post-announcement price
            post_avg_price = post_trades['price'].mean()

            # Calculate returns for each account
            account_positions = pre_trades.groupby('buy_account_id', observed=True).agg({
                'price': 'mean',
                'quantity': 'sum'
            }).reset_index()
            account_positions.columns = [
                'account_id', 'avg_buy_price', 'total_quantity']

            # Calculate return
            account_positions['return_pct'] = (
                post_avg_price - account_positions['avg_buy_price']) / account_positions['avg_buy_price']
            account_positions['profit_value'] = account_positions['return_pct'] * \
                account_positions['avg_buy_price'] * \
                account_positions['total_quantity']

            # Filter profitable accounts
            profitable = account_positions[account_positions['return_pct']
                                           >= self.config.min_return_threshold_pct].copy()

            if len(profitable) > 0:
                profitable['event_id'] = event['event_id']
                profitable['instrument_id'] = event['instrument_id']
                profitable['post_price'] = post_avg_price
                profitable_patterns.append(profitable)

        if not profitable_patterns:
            print("  No profitable pre-announcement patterns found")
            return [], pd.DataFrame()

        patterns_df = pd.concat(profitable_patterns, ignore_index=True)
        print(
            f"  Found {len(patterns_df):,} profitable pre-announcement patterns")

        # Aggregate by account
        grouped = patterns_df.groupby('account_id', observed=True).agg({
            'event_id': 'count',
            'return_pct': 'mean',
            'profit_value': 'sum',
            'instrument_id': 'nunique'
        }).reset_index()

        grouped.columns = ['account_id', 'num_events',
                           'avg_return', 'total_profit', 'num_instruments']
        grouped = grouped[grouped['num_events']
                          >= self.config.min_suspicious_events]

        if len(grouped) == 0:
            print("  No accounts with repeated profitable patterns")
            return [], pd.DataFrame()

        print(
            f"  Found {len(grouped):,} accounts with repeated profitable patterns")

        # Generate alerts
        alerts = []
        for _, row in grouped.iterrows():
            instruments = patterns_df[patterns_df['account_id'] ==
                                      row['account_id']]['instrument_id'].unique().tolist()

            severity = 'low'
            if row['num_events'] >= self.config.severity_high_occurrences:
                severity = 'high'
            elif row['num_events'] >= self.config.severity_medium_occurrences:
                severity = 'medium'

            confidence = min(0.95, 0.70 + (row['num_events'] * 0.08))

            alert = Alert(
                alert_id=f"INSIDER_5_3_{uuid.uuid4().hex[:8]}",
                category="insider_trading",
                rule_id="5.3",
                severity=severity,
                timestamp=datetime.now().isoformat(),
                account_ids=[row['account_id']],
                instrument_ids=instruments,
                description=f"Abnormal profits: {int(row['num_events'])} profitable events, {row['avg_return']:.1%} avg return",
                evidence={
                    'num_events': int(row['num_events']),
                    'avg_return_pct': float(row['avg_return']),
                    'total_profit': float(row['total_profit']),
                    'num_instruments': int(row['num_instruments'])
                },
                confidence_score=confidence
            )
            alerts.append(alert)

        return alerts, patterns_df

    def _rule_5_4_leakage_improved(self, trades: pd.DataFrame,
                                   events: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:
        """Detect clusters of accounts trading before announcements (information leakage)."""
        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0 or len(events) == 0:
            return [], pd.DataFrame()

        # Add leakage window
        events['leakage_window_start'] = events['announcement_date'] - \
            timedelta(hours=self.config.leakage_cluster_window_hours)

        leakage_patterns = []

        for _, event in events.iterrows():
            # Get trades in leakage window
            cluster_trades = trades_clean[
                (trades_clean['instrument_id'] == event['instrument_id']) &
                (trades_clean['timestamp'] >= event['leakage_window_start']) &
                (trades_clean['timestamp'] < event['announcement_date'])
            ]

            if len(cluster_trades) == 0:
                continue

            # Count unique accounts
            unique_accounts = cluster_trades['buy_account_id'].nunique()

            if unique_accounts >= self.config.leakage_min_accounts:
                total_volume = cluster_trades['quantity'].sum()

                leakage_patterns.append({
                    'event_id': event['event_id'],
                    'instrument_id': event['instrument_id'],
                    'num_accounts': unique_accounts,
                    'total_volume': total_volume,
                    'num_trades': len(cluster_trades),
                    'announcement_date': event['announcement_date']
                })

        if not leakage_patterns:
            print("  No information leakage clusters found")
            return [], pd.DataFrame()

        patterns_df = pd.DataFrame(leakage_patterns)
        print(f"  Found {len(patterns_df):,} potential leakage clusters")

        # Aggregate by instrument
        grouped = patterns_df.groupby('instrument_id', observed=True).agg({
            'event_id': 'count',
            'num_accounts': 'mean',
            'total_volume': 'sum',
            'num_trades': 'sum'
        }).reset_index()

        grouped.columns = ['instrument_id', 'num_events',
                           'avg_accounts', 'total_volume', 'total_trades']
        grouped = grouped[grouped['num_events']
                          >= self.config.min_suspicious_events]

        if len(grouped) == 0:
            print("  No instruments with repeated leakage patterns")
            return [], pd.DataFrame()

        print(
            f"  Found {len(grouped):,} instruments with repeated leakage patterns")

        # Generate alerts
        alerts = []
        for _, row in grouped.iterrows():
            severity = 'low'
            if row['num_events'] >= self.config.severity_high_occurrences:
                severity = 'high'
            elif row['num_events'] >= self.config.severity_medium_occurrences:
                severity = 'medium'

            confidence = min(
                0.90, 0.50 + (row['num_events'] * 0.1) + (row['avg_accounts'] * 0.05))

            alert = Alert(
                alert_id=f"INSIDER_5_4_{uuid.uuid4().hex[:8]}",
                category="insider_trading",
                rule_id="5.4",
                severity=severity,
                timestamp=datetime.now().isoformat(),
                account_ids=[],
                instrument_ids=[row['instrument_id']],
                description=f"Information leakage: {int(row['num_events'])} clusters, {row['avg_accounts']:.1f} avg accounts",
                evidence={
                    'num_events': int(row['num_events']),
                    'avg_accounts': float(row['avg_accounts']),
                    'total_volume': float(row['total_volume']),
                    'total_trades': int(row['total_trades'])
                },
                confidence_score=confidence
            )
            alerts.append(alert)

        return alerts, patterns_df

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

    insider_config = InsiderConfig(
        data_config=data_config,
        save_intermediates=True
    )

    print("Market Surveillance Engine - Category 5: Insider Trading (IMPROVED)")
    print("="*80)

    loader = ArrowDataLoader(data_config)
    writer = ArrowDataWriter(data_config)

    start_time = time.time()

    detector = ImprovedInsiderDetector(insider_config, loader, writer)
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
