# surveillance_derivatives.py

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
class DerivativesConfig:
    data_config: DataConfig = None
    pin_risk_window_days: int = 3
    pin_risk_distance_pct: float = 0.02
    pin_risk_concentration: float = 0.30
    max_pain_strikes_range: int = 5
    max_pain_min_open_interest: int = 100
    volatility_spike_multiplier: float = 2.0
    volatility_window_hours: int = 4
    expiry_window_hours: int = 2
    expiry_concentration: float = 0.25
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


class VectorizedDerivativesDetector:
    def __init__(self, config: DerivativesConfig, loader: ArrowDataLoader, writer: ArrowDataWriter):
        self.config = config
        self.loader = loader
        self.writer = writer
        self.category = "derivatives_manipulation"
        self.optimizer = DataOptimizer()

    def execute(self) -> pd.DataFrame:
        print("\n" + "="*80)
        print("CATEGORY 10: OPTIONS/DERIVATIVES MANIPULATION (VECTORIZED)")
        print("="*80)

        print("\nLoading required data...")

        trade_cols = ['trade_id', 'timestamp', 'instrument_id', 'buy_account_id',
                      'sell_account_id', 'quantity', 'price', 'trade_value']

        trades = self.loader.load_table('trades', columns=trade_cols)

        trades = self.optimizer.optimize_dtypes(trades)
        trades = self.optimizer.convert_timestamps(trades, ['timestamp'])
        trades = trades.dropna(subset=['timestamp'])

        print(f"Loaded {len(trades):,} trades")

        # generate synthetic options data based on trades
        options_data = self._generate_synthetic_options(trades)

        alerts = []

        print("\nExecuting Rule 10.1: Pin Risk Manipulation...")
        alerts_10_1, intermediates_10_1 = self._rule_10_1_pin_risk(
            trades, options_data)
        alerts.extend(alerts_10_1)
        if self.config.save_intermediates and not intermediates_10_1.empty:
            self.writer.write_table(
                intermediates_10_1, self.category, 'intermediate', 'rule_10_1_candidates')

        print("\nExecuting Rule 10.2: Max Pain Manipulation...")
        alerts_10_2, intermediates_10_2 = self._rule_10_2_max_pain(
            trades, options_data)
        alerts.extend(alerts_10_2)
        if self.config.save_intermediates and not intermediates_10_2.empty:
            self.writer.write_table(
                intermediates_10_2, self.category, 'intermediate', 'rule_10_2_candidates')

        print("\nExecuting Rule 10.3: Volatility Manipulation...")
        alerts_10_3, intermediates_10_3 = self._rule_10_3_volatility(trades)
        alerts.extend(alerts_10_3)
        if self.config.save_intermediates and not intermediates_10_3.empty:
            self.writer.write_table(
                intermediates_10_3, self.category, 'intermediate', 'rule_10_3_candidates')

        print("\nExecuting Rule 10.4: Expiry Manipulation...")
        alerts_10_4, intermediates_10_4 = self._rule_10_4_expiry(
            trades, options_data)
        alerts.extend(alerts_10_4)
        if self.config.save_intermediates and not intermediates_10_4.empty:
            self.writer.write_table(
                intermediates_10_4, self.category, 'intermediate', 'rule_10_4_candidates')

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

    def _generate_synthetic_options(self, trades: pd.DataFrame) -> pd.DataFrame:
        # generate synthetic options expiries based on trade data
        instruments = trades['instrument_id'].unique()[:50]

        date_range = pd.date_range(
            start=trades['timestamp'].min(),
            end=trades['timestamp'].max(),
            freq='7d'
        )

        options = []
        for instrument in instruments:
            instrument_trades = trades[trades['instrument_id'] == instrument]
            if len(instrument_trades) == 0:
                continue

            avg_price = instrument_trades['price'].mean()

            for expiry_date in date_range:
                for offset in [-0.05, 0, 0.05]:
                    strike = avg_price * (1 + offset)
                    options.append({
                        'option_id': f"OPT_{uuid.uuid4().hex[:8]}",
                        'underlying_instrument_id': instrument,
                        'strike_price': strike,
                        'expiry_date': expiry_date,
                        'option_type': 'call' if offset >= 0 else 'put',
                        'open_interest': np.random.randint(50, 500)
                    })

        return pd.DataFrame(options)

    def _rule_10_1_pin_risk(self, trades: pd.DataFrame,
                            options: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['price'].notna())
        ].copy()

        if len(trades_clean) == 0 or len(options) == 0:
            return [], pd.DataFrame()

        # identify approaching expiries
        options['expiry_date'] = pd.to_datetime(options['expiry_date'])

        pin_patterns = []

        for _, opt in options.iterrows():
            window_start = opt['expiry_date'] - \
                timedelta(days=self.config.pin_risk_window_days)

            # get trades in expiry window for underlying
            window_trades = trades_clean[
                (trades_clean['instrument_id'] == opt['underlying_instrument_id']) &
                (trades_clean['timestamp'] >= window_start) &
                (trades_clean['timestamp'] <= opt['expiry_date'])
            ]

            if len(window_trades) == 0:
                continue

            # calculate distance from strike
            window_trades_copy = window_trades.copy()
            window_trades_copy['distance_from_strike'] = np.abs(
                window_trades_copy['price'] - opt['strike_price']
            ) / opt['strike_price']

            # filter to trades near strike
            near_strike = window_trades_copy[
                window_trades_copy['distance_from_strike'] <= self.config.pin_risk_distance_pct
            ]

            if len(near_strike) == 0:
                continue

            # calculate concentration
            concentration = len(near_strike) / len(window_trades)

            if concentration >= self.config.pin_risk_concentration:
                pin_patterns.append({
                    'option_id': opt['option_id'],
                    'instrument_id': opt['underlying_instrument_id'],
                    'strike_price': opt['strike_price'],
                    'expiry_date': opt['expiry_date'],
                    'concentration': concentration,
                    'num_near_strike': len(near_strike)
                })

        if not pin_patterns:
            return [], pd.DataFrame()

        patterns_df = pd.DataFrame(pin_patterns)

        print(f"  Found {len(patterns_df):,} pin risk patterns")

        # aggregate by instrument
        grouped = patterns_df.groupby('instrument_id', observed=True).agg({
            'option_id': ['count'],
            'concentration': ['mean'],
            'num_near_strike': ['sum']
        }).reset_index()

        grouped.columns = ['instrument_id', 'pattern_count',
                           'avg_concentration', 'total_near_strike']
        grouped = grouped[grouped['pattern_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} instruments with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='10.1',
            account_col='instrument_id',
            count_col='pattern_count',
            description_template='Pin risk manipulation: {} instances detected',
            is_instrument_alert=True
        )

        return alerts, patterns_df

    def _rule_10_2_max_pain(self, trades: pd.DataFrame,
                            options: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['price'].notna())
        ].copy()

        if len(trades_clean) == 0 or len(options) == 0:
            return [], pd.DataFrame()

        # calculate max pain per expiry
        max_pain_patterns = []

        for expiry_date in options['expiry_date'].unique():
            expiry_options = options[options['expiry_date'] == expiry_date]

            for instrument in expiry_options['underlying_instrument_id'].unique():
                instrument_options = expiry_options[
                    expiry_options['underlying_instrument_id'] == instrument
                ]

                if len(instrument_options) < self.config.max_pain_strikes_range:
                    continue

                # calculate max pain strike (simplified - strike with most OI)
                max_oi_strike = instrument_options.loc[
                    instrument_options['open_interest'].idxmax(),
                    'strike_price'
                ]

                # get trades near expiry
                window_start = pd.to_datetime(expiry_date) - timedelta(days=1)

                near_expiry_trades = trades_clean[
                    (trades_clean['instrument_id'] == instrument) &
                    (trades_clean['timestamp'] >= window_start) &
                    (trades_clean['timestamp'] <= pd.to_datetime(expiry_date))
                ]

                if len(near_expiry_trades) == 0:
                    continue

                # calculate final price
                final_price = near_expiry_trades.sort_values(
                    'timestamp').iloc[-1]['price']

                # check if pinned to max pain
                distance_pct = np.abs(
                    final_price - max_oi_strike) / max_oi_strike

                if distance_pct <= 0.01:
                    max_pain_patterns.append({
                        'instrument_id': instrument,
                        'expiry_date': expiry_date,
                        'max_pain_strike': max_oi_strike,
                        'final_price': final_price,
                        'distance_pct': distance_pct
                    })

        if not max_pain_patterns:
            return [], pd.DataFrame()

        patterns_df = pd.DataFrame(max_pain_patterns)

        print(f"  Found {len(patterns_df):,} max pain patterns")

        # aggregate by instrument
        grouped = patterns_df.groupby('instrument_id', observed=True).agg({
            'expiry_date': ['count'],
            'distance_pct': ['mean']
        }).reset_index()

        grouped.columns = ['instrument_id', 'pattern_count', 'avg_distance']
        grouped = grouped[grouped['pattern_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} instruments with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='10.2',
            account_col='instrument_id',
            count_col='pattern_count',
            description_template='Max pain manipulation: {} instances detected',
            is_instrument_alert=True
        )

        return alerts, patterns_df

    def _rule_10_3_volatility(self, trades: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['price'].notna())
        ].copy()

        if len(trades_clean) == 0:
            return [], pd.DataFrame()

        # calculate rolling volatility
        trades_clean = trades_clean.sort_values(['instrument_id', 'timestamp'])

        # calculate hourly returns
        trades_clean['hour'] = trades_clean['timestamp'].dt.floor('h')

        hourly_prices = trades_clean.groupby(['instrument_id', 'hour'], observed=True).agg({
            'price': ['last']
        }).reset_index()

        hourly_prices.columns = ['instrument_id', 'hour', 'price']

        # calculate returns
        hourly_prices = hourly_prices.sort_values(['instrument_id', 'hour'])
        hourly_prices['return'] = hourly_prices.groupby(
            'instrument_id', observed=True)['price'].pct_change()

        # calculate rolling volatility
        hourly_prices['rolling_vol'] = hourly_prices.groupby('instrument_id', observed=True)['return'].transform(
            lambda x: x.rolling(window=24, min_periods=1).std()
        )

        # identify volatility spikes
        hourly_prices['vol_spike'] = hourly_prices.groupby('instrument_id', observed=True)['rolling_vol'].transform(
            lambda x: x > x.shift(1) * self.config.volatility_spike_multiplier
        )

        spikes = hourly_prices[hourly_prices['vol_spike']].copy()

        if len(spikes) == 0:
            return [], pd.DataFrame()

        print(f"  Found {len(spikes):,} volatility spike instances")

        # match to accounts trading during spikes
        spike_trades = trades_clean.merge(
            spikes[['instrument_id', 'hour']],
            left_on=['instrument_id', trades_clean['timestamp'].dt.floor('h')],
            right_on=['instrument_id', 'hour'],
            how='inner'
        )

        if len(spike_trades) == 0:
            return [], pd.DataFrame()

        # aggregate by account
        grouped = spike_trades.groupby(['buy_account_id', 'instrument_id'], observed=True).agg({
            'hour': ['count'],
            'quantity': ['sum']
        }).reset_index()

        grouped.columns = ['account_id', 'instrument_id',
                           'spike_count', 'total_quantity']
        grouped = grouped[grouped['spike_count'] >=
                          self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} accounts with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='10.3',
            account_col='account_id',
            count_col='spike_count',
            description_template='Volatility manipulation: {} spike instances',
            is_instrument_alert=False
        )

        return alerts, spikes

    def _rule_10_4_expiry(self, trades: pd.DataFrame,
                          options: pd.DataFrame) -> Tuple[List[Alert], pd.DataFrame]:

        trades_clean = trades[
            (trades['instrument_id'].notna()) &
            (trades['buy_account_id'].notna()) &
            (trades['quantity'].notna())
        ].copy()

        if len(trades_clean) == 0 or len(options) == 0:
            return [], pd.DataFrame()

        # identify expiry manipulation
        options['expiry_date'] = pd.to_datetime(options['expiry_date'])

        expiry_patterns = []

        for expiry_date in options['expiry_date'].unique():
            window_start = expiry_date - \
                timedelta(hours=self.config.expiry_window_hours)

            expiry_instruments = options[
                options['expiry_date'] == expiry_date
            ]['underlying_instrument_id'].unique()

            for instrument in expiry_instruments:
                # get daily volume baseline
                daily_volume = trades_clean[
                    trades_clean['instrument_id'] == instrument
                ].groupby(trades_clean['timestamp'].dt.date, observed=True)['quantity'].sum().mean()

                # get expiry window volume
                expiry_trades = trades_clean[
                    (trades_clean['instrument_id'] == instrument) &
                    (trades_clean['timestamp'] >= window_start) &
                    (trades_clean['timestamp'] <= expiry_date)
                ]

                if len(expiry_trades) == 0:
                    continue

                expiry_volume = expiry_trades['quantity'].sum()

                # normalize to hourly comparison
                hourly_baseline = daily_volume / 24
                hourly_expiry = expiry_volume / self.config.expiry_window_hours

                concentration = hourly_expiry / (hourly_baseline + 1)

                if concentration >= self.config.expiry_concentration:
                    expiry_patterns.append({
                        'instrument_id': instrument,
                        'expiry_date': expiry_date,
                        'concentration': concentration,
                        'expiry_volume': expiry_volume
                    })

        if not expiry_patterns:
            return [], pd.DataFrame()

        patterns_df = pd.DataFrame(expiry_patterns)

        print(f"  Found {len(patterns_df):,} expiry manipulation patterns")

        # aggregate by instrument
        grouped = patterns_df.groupby('instrument_id', observed=True).agg({
            'expiry_date': ['count'],
            'concentration': ['mean'],
            'expiry_volume': ['sum']
        }).reset_index()

        grouped.columns = ['instrument_id', 'pattern_count',
                           'avg_concentration', 'total_volume']
        grouped = grouped[grouped['pattern_count']
                          >= self.config.severity_low_occurrences]

        print(f"  Found {len(grouped):,} instruments with repeated patterns")

        alerts = self._generate_alerts(
            grouped,
            rule_id='10.4',
            account_col='instrument_id',
            count_col='pattern_count',
            description_template='Expiry manipulation: {} instances detected',
            is_instrument_alert=True
        )

        return alerts, patterns_df

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
                account_ids = [row[account_col]]
                instrument_ids = [row.get('instrument_id', 'multiple')]

            alert = Alert(
                alert_id=f"DERIV_{rule_id.replace('.', '_')}_{uuid.uuid4().hex[:8]}",
                category="derivatives_manipulation",
                rule_id=rule_id,
                severity=row['severity'],
                timestamp=datetime.now().isoformat(),
                account_ids=account_ids,
                instrument_ids=instrument_ids,
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

    derivatives_config = DerivativesConfig(
        data_config=data_config,
        save_intermediates=True
    )

    print("Market Surveillance Engine - Category 10: Derivatives Manipulation (VECTORIZED)")
    print("="*80)

    loader = ArrowDataLoader(data_config)
    writer = ArrowDataWriter(data_config)

    start_time = time.time()

    detector = VectorizedDerivativesDetector(
        derivatives_config, loader, writer)
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
