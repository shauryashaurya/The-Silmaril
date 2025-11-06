# surveillance_insider.py

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
    pre_announcement_window_days: int = 50  # was 30
    # Rule 5.1 (Pre-Announcement)
    abnormal_volume_multiplier: float = 1.1  # was 2.5
    # Rule 5.3 (Abnormal Profits)
    abnormal_return_threshold_pct: float = 0.015  # was 0.05
    # Rule 5.3 (Abnormal Profits)
    profit_threshold_pct: float = 0.005  # was 0.03
    # Rule 5.2 (Network Trading)
    network_time_window_days: int = 15  # was 5
    # Rule 5.4 (Leakage)
    leakage_cluster_window_hours: int = 72  # was 24
    # Rule 5.4 (Leakage)
    leakage_min_accounts: int = 2  # was 3
    #
    severity_high_occurrences: int = 5
    severity_medium_occurrences: int = 3
    severity_low_occurrences: int = 1
    save_intermediates: bool = True
    # General
    min_suspicious_events: int = 1  # was 2

# preserving OG config
# class InsiderConfig:
#     data_config: DataConfig = None
#     pre_announcement_window_days: int = 30
#     abnormal_volume_multiplier: float = 2.5
#     abnormal_return_threshold_pct: float = 0.05
#     profit_threshold_pct: float = 0.03
#     network_time_window_days: int = 5
#     leakage_cluster_window_hours: int = 24
#     leakage_min_accounts: int = 3
#     severity_high_occurrences: int = 5
#     severity_medium_occurrences: int = 3
#     severity_low_occurrences: int = 1
#     save_intermediates: bool = True
#     min_suspicious_events: int = 2

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


class VectorizedInsiderDetector:
    def __init__(self, config: InsiderConfig, loader: ArrowDataLoader, writer: ArrowDataWriter):
        self.config = config
        self.loader = loader
        self.writer = writer
        self.category = "insider_trading"
        self.optimizer = DataOptimizer()

    def execute(self) -> pd.DataFrame:
        print("\n" + "="*80)
        print("CATEGORY 5: INSIDER TRADING DETECTION (VECTORIZED)")
        print("="*80)

        print("\nLoading required data...")

        trade_cols = ['trade_id', 'timestamp', 'instrument_id', 'buy_account_id',
                      'sell_account_id', 'quantity', 'price', 'trade_value']

        account_cols = ['account_id', 'beneficial_owner_id',
                        'firm_id', 'related_accounts']

        trades = self.loader.load_table('trades', columns=trade_cols)
        accounts = self.loader.load_table('accounts', columns=account_cols)

        # check if corporate_events table exists
        try:
            event_cols = ['event_id', 'instrument_id',
                          'event_type', 'announcement_date', 'event_date']
            events = self.loader.load_table(
                'corporate_events', columns=event_cols)
        except:
            print(
                "  Warning: corporate_events table not found, generating synthetic events")
            events = self._generate_synthetic_events(trades)

        trades = self.optimizer.optimize_dtypes(trades)
        accounts = self.optimizer.optimize_dtypes(accounts)
        events = self.optimizer.optimize_dtypes(events)

        accounts = self.optimizer.parse_json_columns(
            accounts, ['related_accounts'])

        trades = self.optimizer.convert_timestamps(trades, ['timestamp'])
        events = self.optimizer.convert_timestamps(
            events, ['announcement_date', 'event_date'])

        trades = trades.dropna(subset=['timestamp'])
        events = events.dropna(subset=['announcement_date'])

        print(
            f"Loaded {len(trades):,} trades, {len(accounts):,} accounts, {len(events):,} events")

        alerts = []

        print("\nExecuting Rule 5.1: Pre-Announcement Trading...")
        alerts_5_1, intermediates_5_1 = self._rule_5_1_pre_announcement(
            trades, events)
        alerts.extend(alerts_5_1)
        if self.config.save_intermediates and not intermediates_5_1.empty:
            self.writer.write_table(
                intermediates_5_1, self.category, 'intermediate', 'rule_5_1_candidates')

        print("\nExecuting Rule 5.2: Insider Network Trading...")
        alerts_5_2, intermediates_5_2 = self._rule_5_2_network_trading(
            trades, events, accounts)
        alerts.extend(alerts_5_2)
        if self.config.save_intermediates and not intermediates_5_2.empty:
            self.writer.write_table(
                intermediates_5_2, self.category, 'intermediate', 'rule_5_2_candidates')

        print("\nExecuting Rule 5.3: Abnormal Profit Patterns...")
        alerts_5_3, intermediates_5_3 = self._rule_5_3_abnormal_profits(
            trades, events)
        alerts.extend(alerts_5_3)
        if self.config.save_intermediates and not intermediates_5_3.empty:
            self.writer.write_table(
                intermediates_5_3, self.category, 'intermediate', 'rule_5_3_candidates')

        print("\nExecuting Rule 5.4: Information Leakage...")
        alerts_5_4, intermediates_5_4 = self._rule_5_4_leakage(trades, events)
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
        # generate synthetic corporate events based on trade data
        instruments = trades['instrument_id'].unique()

        # sample random dates from trade data
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
                    'event_date': date + timedelta(days=7)
                })

        return pd.DataFrame(events)

    def _rule_5_1_pre_announcement(self, trades: pd.DataFrame,
                                   events: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['sell_account_id'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0 or len(events) == 0:
            return [], pd.DataFrame()

        # add pre-announcement window to events
        events['window_start'] = events['announcement_date'] - \
            timedelta(days=self.config.pre_announcement_window_days)

        # calculate baseline volume per instrument
        trades_clean['trade_date'] = trades_clean['timestamp'].dt.date

        baseline_volume = trades_clean.groupby(['instrument_id', 'trade_date'], observed=True).agg({
            'quantity': ['sum']
        }).reset_index()
        baseline_volume.columns = [
            'instrument_id', 'trade_date', 'daily_volume']

        # calculate average baseline
        avg_baseline = baseline_volume.groupby('instrument_id', observed=True).agg({
            'daily_volume': ['mean', 'std']
        }).reset_index()
        avg_baseline.columns = ['instrument_id', 'avg_volume', 'std_volume']

        # find trades in pre-announcement windows
        pre_announcement_trades = []

        for _, event in events.iterrows():
            instrument_trades = trades_clean[
                (trades_clean['instrument_id'] == event['instrument_id']) &
                (trades_clean['timestamp'] >= event['window_start']) &
                (trades_clean['timestamp'] < event['announcement_date'])
            ].copy()

            if len(instrument_trades) > 0:
                instrument_trades['event_id'] = event['event_id']
                instrument_trades['announcement_date'] = event['announcement_date']
                pre_announcement_trades.append(instrument_trades)

        if not pre_announcement_trades:
            return [], pd.DataFrame()

        pre_trades = pd.concat(pre_announcement_trades, ignore_index=True)

        print(
            f"  Found {len(pre_trades):,} trades in pre-announcement windows")

        # calculate volume by account in pre-announcement period
        pre_volume = pre_trades.groupby(['instrument_id', 'event_id', 'buy_account_id'], observed=True).agg({
            'quantity': ['sum']
        }).reset_index()
        pre_volume.columns = ['instrument_id',
                              'event_id', 'account_id', 'pre_volume']

        # merge with baseline
        pre_volume = pre_volume.merge(
            avg_baseline, on='instrument_id', how='left')

        # identify abnormal volume
        pre_volume['volume_ratio'] = pre_volume['pre_volume'] / \
            (pre_volume['avg_volume'] + 1)

        suspicious = pre_volume[
            pre_volume['volume_ratio'] >= self.config.abnormal_volume_multiplier
        ].copy()

        if len(suspicious) == 0:
            return [], pd.DataFrame()

        print(
            f"  Found {len(suspicious):,} suspicious pre-announcement patterns")

        # aggregate by account
        grouped = suspicious.groupby(['account_id', 'instrument_id'], observed=True).agg({
            'event_id': ['count'],
            'volume_ratio': ['mean'],
            'pre_volume': ['sum']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['event_id_count']
                          >= self.config.min_suspicious_events]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='5.1',
            account_col='account_id',
            count_col='event_id_count',
            description_template='Pre-announcement trading: {} suspicious events'
        )

        return alerts, suspicious

    def _rule_5_2_network_trading(self, trades: pd.DataFrame, events: pd.DataFrame,
                                  accounts: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0 or len(events) == 0:
            return [], pd.DataFrame()

        # build related account network
        related_map = {}
        for _, acc in accounts.iterrows():
            if 'related_accounts_list' in acc and acc['related_accounts_list']:
                related_map[acc['account_id']] = set(
                    acc['related_accounts_list'])

        if not related_map:
            print("  No related accounts found")
            return [], pd.DataFrame()

        # add event windows
        events['window_start'] = events['announcement_date'] - \
            timedelta(days=self.config.network_time_window_days)

        # find coordinated trading
        coordinated_patterns = []

        for _, event in events.iterrows():
            window_trades = trades_clean[
                (trades_clean['instrument_id'] == event['instrument_id']) &
                (trades_clean['timestamp'] >= event['window_start']) &
                (trades_clean['timestamp'] < event['announcement_date'])
            ]

            if len(window_trades) == 0:
                continue

            # check for related accounts trading together
            active_accounts = set(window_trades['buy_account_id'].unique())

            for account, related in related_map.items():
                if account in active_accounts:
                    related_active = related.intersection(active_accounts)
                    if len(related_active) > 0:
                        coordinated_patterns.append({
                            'primary_account': account,
                            'related_accounts': list(related_active),
                            'instrument_id': event['instrument_id'],
                            'event_id': event['event_id'],
                            'num_related': len(related_active)
                        })

        if not coordinated_patterns:
            return [], pd.DataFrame()

        patterns_df = pd.DataFrame(coordinated_patterns)

        print(f"  Found {len(patterns_df):,} coordinated trading patterns")

        # aggregate by primary account
        grouped = patterns_df.groupby('primary_account', observed=True).agg({
            'event_id': ['count'],
            'num_related': ['mean'],
            'instrument_id': ['nunique']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['event_id_count']
                          >= self.config.min_suspicious_events]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='5.2',
            account_col='primary_account',
            count_col='event_id_count',
            description_template='Insider network trading: {} coordinated events'
        )

        return alerts, patterns_df

    def _rule_5_3_abnormal_profits(self, trades: pd.DataFrame,
                                   events: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['price'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0 or len(events) == 0:
            return [], pd.DataFrame()

        # add event windows
        events['pre_window_start'] = events['announcement_date'] - \
            timedelta(days=self.config.pre_announcement_window_days)
        events['post_window_end'] = events['announcement_date'] + \
            timedelta(days=7)

        # find profitable patterns
        profitable_patterns = []

        for _, event in events.iterrows():
            # get pre-announcement trades
            pre_trades = trades_clean[
                (trades_clean['instrument_id'] == event['instrument_id']) &
                (trades_clean['timestamp'] >= event['pre_window_start']) &
                (trades_clean['timestamp'] < event['announcement_date'])
            ]

            if len(pre_trades) == 0:
                continue

            # get post-announcement price
            post_trades = trades_clean[
                (trades_clean['instrument_id'] == event['instrument_id']) &
                (trades_clean['timestamp'] >= event['announcement_date']) &
                (trades_clean['timestamp'] <= event['post_window_end'])
            ]

            if len(post_trades) == 0:
                continue

            post_avg_price = post_trades['price'].mean()

            # calculate returns for buy accounts
            buy_accounts = pre_trades.groupby('buy_account_id', observed=True).agg({
                'price': ['mean'],
                'quantity': ['sum']
            }).reset_index()
            buy_accounts.columns = ['account_id',
                                    'avg_buy_price', 'total_quantity']

            buy_accounts['return_pct'] = (
                post_avg_price - buy_accounts['avg_buy_price']) / buy_accounts['avg_buy_price']

            profitable = buy_accounts[
                buy_accounts['return_pct'] >= self.config.profit_threshold_pct
            ].copy()

            if len(profitable) > 0:
                profitable['event_id'] = event['event_id']
                profitable['instrument_id'] = event['instrument_id']
                profitable_patterns.append(profitable)

        if not profitable_patterns:
            return [], pd.DataFrame()

        patterns_df = pd.concat(profitable_patterns, ignore_index=True)

        print(
            f"  Found {len(patterns_df):,} profitable pre-announcement patterns")

        # aggregate by account
        grouped = patterns_df.groupby('account_id', observed=True).agg({
            'event_id': ['count'],
            'return_pct': ['mean'],
            'total_quantity': ['sum'],
            'instrument_id': ['nunique']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['event_id_count']
                          >= self.config.min_suspicious_events]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='5.3',
            account_col='account_id',
            count_col='event_id_count',
            description_template='Abnormal profits: {} profitable events'
        )

        return alerts, patterns_df

    def _rule_5_4_leakage(self, trades: pd.DataFrame,
                          events: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0 or len(events) == 0:
            return [], pd.DataFrame()

        # add leakage detection windows
        events['leakage_window_start'] = events['announcement_date'] - \
            timedelta(hours=self.config.leakage_cluster_window_hours)

        # find clusters of trading before announcements
        leakage_patterns = []

        for _, event in events.iterrows():
            cluster_trades = trades_clean[
                (trades_clean['instrument_id'] == event['instrument_id']) &
                (trades_clean['timestamp'] >= event['leakage_window_start']) &
                (trades_clean['timestamp'] < event['announcement_date'])
            ]

            if len(cluster_trades) == 0:
                continue

            # count unique accounts
            unique_accounts = cluster_trades['buy_account_id'].nunique()

            if unique_accounts >= self.config.leakage_min_accounts:
                # calculate concentration
                total_volume = cluster_trades['quantity'].sum()
                account_volumes = cluster_trades.groupby(
                    'buy_account_id', observed=True)['quantity'].sum()

                leakage_patterns.append({
                    'event_id': event['event_id'],
                    'instrument_id': event['instrument_id'],
                    'num_accounts': unique_accounts,
                    'total_volume': total_volume,
                    'top_account': account_volumes.idxmax(),
                    'top_account_volume': account_volumes.max(),
                    'announcement_date': event['announcement_date']
                })

        if not leakage_patterns:
            return [], pd.DataFrame()

        patterns_df = pd.DataFrame(leakage_patterns)

        print(f"  Found {len(patterns_df):,} potential leakage clusters")

        # aggregate by instrument
        grouped = patterns_df.groupby('instrument_id', observed=True).agg({
            'event_id': ['count'],
            'num_accounts': ['mean'],
            'total_volume': ['sum']
        }).reset_index()

        grouped.columns = ['_'.join(str(c) for c in col).strip(
            '_') for col in grouped.columns.values]
        grouped = grouped[grouped['event_id_count']
                          >= self.config.min_suspicious_events]

        print(f"  Found {len(grouped):,} instruments with repeated patterns")

        # create alerts per instrument
        alerts = []
        for idx, row in grouped.iterrows():
            if row['event_id_count'] >= self.config.severity_high_occurrences:
                severity = 'high'
            elif row['event_id_count'] >= self.config.severity_medium_occurrences:
                severity = 'medium'
            else:
                severity = 'low'

            confidence = min(0.90, 0.5 + (row['event_id_count'] / 10))

            alert = Alert(
                alert_id=f"INSIDER_5_4_{uuid.uuid4().hex[:8]}",
                category="insider_trading",
                rule_id="5.4",
                severity=severity,
                timestamp=datetime.now().isoformat(),
                account_ids=[],
                instrument_ids=[row['instrument_id']],
                description=f"Information leakage: {int(row['event_id_count'])} suspicious clusters",
                evidence={
                    'num_events': int(row['event_id_count']),
                    'avg_accounts': float(row['num_accounts_mean'])
                },
                confidence_score=confidence
            )
            alerts.append(alert)

        return alerts, patterns_df

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

        grouped['confidence'] = np.minimum(0.95, 0.6 + grouped[count_col] / 10)

        alerts = []
        for idx, row in grouped.iterrows():
            alert = Alert(
                alert_id=f"INSIDER_{rule_id.replace('.', '_')}_{uuid.uuid4().hex[:8]}",
                category="insider_trading",
                rule_id=rule_id,
                severity=row['severity'],
                timestamp=datetime.now().isoformat(),
                account_ids=[row[account_col]],
                instrument_ids=[row.get('instrument_id', 'multiple')],
                description=description_template.format(int(row[count_col])),
                evidence={'num_events': int(row[count_col])},
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

    insider_config = InsiderConfig(
        data_config=data_config,
        save_intermediates=True
    )

    print("Market Surveillance Engine - Category 5: Insider Trading (VECTORIZED)")
    print("="*80)

    loader = ArrowDataLoader(data_config)
    writer = ArrowDataWriter(data_config)

    start_time = time.time()

    detector = VectorizedInsiderDetector(insider_config, loader, writer)
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
