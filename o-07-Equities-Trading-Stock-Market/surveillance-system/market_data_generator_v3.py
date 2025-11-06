# market_data_generator_v3.py
# Comprehensive vectorized market surveillance test data generator
# Covers all 40 detection rules across 10 categories

import random
import uuid
import json
from datetime import datetime, timedelta, time as dt_time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict
import os

random.seed(42)
np.random.seed(42)


@dataclass
class GeneratorConfig:
    num_accounts: int = 1000
    num_instruments: int = 500
    num_firms: int = 50
    num_venues: int = 5
    num_days: int = 30
    orders_per_day: int = 100000
    trades_per_day: int = 50000
    cancellation_rate: float = 0.3

    # Pattern probabilities - ensure data for all rules
    wash_trading_prob: float = 0.03
    layering_prob: float = 0.02
    spoofing_prob: float = 0.02
    front_running_prob: float = 0.025
    manipulation_prob: float = 0.02
    insider_prob: float = 0.015
    collusion_prob: float = 0.02
    cross_market_prob: float = 0.025
    benchmark_prob: float = 0.02
    aml_prob: float = 0.02
    derivatives_prob: float = 0.03

    base_price_range: Tuple[float, float] = (10.0, 500.0)
    volatility_range: Tuple[float, float] = (0.01, 0.05)
    market_open_hour: int = 9
    market_close_hour: int = 16
    related_account_prob: float = 0.15
    output_dir: str = './generated_data'
    batch_size: int = 50000


class OrderType(Enum):
    MARKET = 'market'
    LIMIT = 'limit'
    STOP = 'stop'
    STOP_LIMIT = 'stop_limit'
    ICEBERG = 'iceberg'
    HIDDEN = 'hidden'


class OrderSide(Enum):
    BUY = 'buy'
    SELL = 'sell'


class OrderState(Enum):
    NEW = 'new'
    PARTIAL_FILL = 'partial_fill'
    FILLED = 'filled'
    CANCELLED = 'cancelled'
    REJECTED = 'rejected'
    EXPIRED = 'expired'


class AccountType(Enum):
    RETAIL = 'retail'
    INSTITUTIONAL = 'institutional'
    MARKET_MAKER = 'market_maker'
    PROPRIETARY = 'proprietary'


class VectorizedMarketDataGenerator:
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.start_date = datetime.now() - timedelta(days=config.num_days)

        # Pre-allocated structures
        self.person_ids = []
        self.firm_ids = []
        self.account_ids = []
        self.instrument_ids = []
        self.venue_ids = [f"VENUE_{i}" for i in range(config.num_venues)]

        # Indices for fast lookups
        self.accounts_by_owner: Dict[str, List[str]] = defaultdict(list)
        self.accounts_by_firm: Dict[str, List[str]] = defaultdict(list)
        self.related_account_map: Dict[str, List[str]] = {}
        self.instrument_prices: Dict[str, float] = {}

        # Buffers
        self.buffers: Dict[str, List[Dict]] = defaultdict(list)

        self.stats = defaultdict(int)

    def generate_all(self):
        print("="*80)
        print("VECTORIZED MARKET DATA GENERATOR V3")
        print("Covering all 40 detection rules")
        print("="*80)

        os.makedirs(self.config.output_dir, exist_ok=True)

        print("\n[1/3] Generating reference data...")
        self._generate_reference_data()

        print("\n[2/3] Generating market activity...")
        self._generate_market_activity()

        print("\n[3/3] Generating manipulative patterns...")
        self._generate_all_patterns()

        self._write_all_buffers()
        self._print_statistics()

    def _generate_reference_data(self):
        # vectorized generation of persons
        print("  - Persons")
        num_persons = self.config.num_accounts
        self.person_ids = [f"P{i:08d}" for i in range(num_persons)]

        persons_df = pd.DataFrame({
            'person_id': self.person_ids,
            'first_name': [f"First_{i}" for i in range(num_persons)],
            'last_name': [f"Last_{i}" for i in range(num_persons)],
            'email': [f"person_{i}@example.com" for i in range(num_persons)],
            'phone': [f"+1-555-{i:07d}" for i in range(num_persons)],
            'address': [f"{i} Main St, City, ST 12345" for i in range(num_persons)],
            'ssn': [f"{i:09d}" for i in range(num_persons)],
            'date_of_birth': [(datetime.now() - timedelta(days=365*30+i)).date().isoformat() for i in range(num_persons)]
        })
        self._write_df('persons', persons_df)

        # vectorized firms
        print("  - Firms")
        self.firm_ids = [f"F{i:06d}" for i in range(self.config.num_firms)]
        firm_types = ['broker_dealer', 'investment_bank',
                      'hedge_fund', 'asset_manager', 'proprietary_trading']

        firms_df = pd.DataFrame({
            'firm_id': self.firm_ids,
            'firm_name': [f"Firm_{i}" for i in range(self.config.num_firms)],
            'lei_code': [''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=20)) for _ in range(self.config.num_firms)],
            'address': [f"{i} Wall St, New York, NY 10005" for i in range(self.config.num_firms)],
            'country': np.random.choice(['US', 'GB', 'CA', 'DE', 'JP'], self.config.num_firms),
            'firm_type': np.random.choice(firm_types, self.config.num_firms)
        })
        self._write_df('firms', firms_df)

        # vectorized accounts with related accounts
        print("  - Accounts")
        self.account_ids = [
            f"A{i:08d}" for i in range(self.config.num_accounts)]
        account_types = [t.value for t in AccountType]

        # create related account networks
        num_related_groups = int(
            self.config.num_accounts * self.config.related_account_prob / 3)
        for i in range(num_related_groups):
            group_size = random.randint(2, 5)
            group_accounts = random.sample(
                self.account_ids, min(group_size, len(self.account_ids)))
            for acc in group_accounts:
                self.related_account_map[acc] = [
                    a for a in group_accounts if a != acc]

        accounts_data = []
        for i, acc_id in enumerate(self.account_ids):
            owner_id = self.person_ids[i % len(self.person_ids)]
            self.accounts_by_owner[owner_id].append(acc_id)
            firm_id = random.choice(self.firm_ids)
            self.accounts_by_firm[firm_id].append(acc_id)

            accounts_data.append({
                'account_id': acc_id,
                'beneficial_owner_id': owner_id,
                'parent_account_id': '',
                'firm_id': firm_id,
                'account_type': random.choice(account_types),
                'opening_date': (self.start_date - timedelta(days=random.randint(30, 365))).date().isoformat(),
                'credit_limit': float(random.randint(100000, 10000000)),
                'ip_addresses': json.dumps([f"192.168.{random.randint(0,255)}.{random.randint(0,255)}" for _ in range(random.randint(1, 3))]),
                'device_fingerprints': json.dumps([f"DEV_{uuid.uuid4().hex[:8]}" for _ in range(random.randint(1, 2))]),
                'related_accounts': json.dumps(self.related_account_map.get(acc_id, []))
            })

        accounts_df = pd.DataFrame(accounts_data)
        self._write_df('accounts', accounts_df)

        # vectorized instruments
        print("  - Instruments")
        self.instrument_ids = [
            f"INS{i:06d}" for i in range(self.config.num_instruments)]
        sectors = ['Technology', 'Finance', 'Healthcare',
                   'Energy', 'Consumer', 'Industrial']
        security_types = ['equity', 'bond', 'etf', 'derivative', 'option']

        base_prices = np.random.uniform(
            self.config.base_price_range[0], self.config.base_price_range[1], self.config.num_instruments)
        for ins_id, price in zip(self.instrument_ids, base_prices):
            self.instrument_prices[ins_id] = price

        instruments_df = pd.DataFrame({
            'instrument_id': self.instrument_ids,
            'symbol': [f"SYM{i:04d}" for i in range(self.config.num_instruments)],
            'isin': [f"US{i:010d}" for i in range(self.config.num_instruments)],
            'security_type': np.random.choice(security_types, self.config.num_instruments),
            'sector': np.random.choice(sectors, self.config.num_instruments),
            'market_cap': np.random.uniform(1e8, 1e12, self.config.num_instruments),
            'average_daily_volume': np.random.uniform(1e6, 1e8, self.config.num_instruments),
            'tick_size': 0.01,
            'lot_size': 100,
            'price': base_prices,
            'volatility': np.random.uniform(self.config.volatility_range[0], self.config.volatility_range[1], self.config.num_instruments),
            'issuer': [f"Issuer_{i}" for i in range(self.config.num_instruments)]
        })
        self._write_df('instruments', instruments_df)

        # corporate events
        print("  - Corporate Events")
        num_events = self.config.num_instruments // 5
        event_types = ['earnings', 'merger', 'dividend', 'guidance', 'split']

        events_data = []
        for i in range(num_events):
            event_date = self.start_date + \
                timedelta(days=random.randint(0, self.config.num_days))
            events_data.append({
                'event_id': f"EVT{i:08d}",
                'instrument_id': random.choice(self.instrument_ids),
                'event_type': random.choice(event_types),
                'announcement_date': event_date.isoformat(),
                'effective_date': (event_date + timedelta(days=random.randint(1, 30))).isoformat(),
                'materiality': random.choice(['high', 'medium', 'low']),
                'description': f"Event {i}"
            })

        events_df = pd.DataFrame(events_data)
        self._write_df('corporate_events', events_df)

        self.stats['persons'] = len(self.person_ids)
        self.stats['firms'] = len(self.firm_ids)
        self.stats['accounts'] = len(self.account_ids)
        self.stats['instruments'] = len(self.instrument_ids)
        self.stats['corporate_events'] = len(events_data)

    def _generate_market_activity(self):
        # generate baseline orders and trades per day
        for day_num in range(self.config.num_days):
            if day_num % 5 == 0:
                print(f"  - Day {day_num+1}/{self.config.num_days}")

            date = self.start_date + timedelta(days=day_num)
            self._generate_daily_activity(date)

    def _generate_daily_activity(self, date: datetime):
        market_open = date.replace(
            hour=self.config.market_open_hour, minute=0, second=0)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)

        # vectorized order generation
        num_orders = self.config.orders_per_day

        # generate timestamps
        seconds_in_day = int((market_close - market_open).total_seconds())
        random_seconds = np.random.randint(0, seconds_in_day, num_orders)
        timestamps = [market_open +
                      timedelta(seconds=int(s)) for s in random_seconds]

        # generate order attributes
        account_indices = np.random.randint(
            0, len(self.account_ids), num_orders)
        instrument_indices = np.random.randint(
            0, len(self.instrument_ids), num_orders)
        venue_indices = np.random.randint(0, len(self.venue_ids), num_orders)

        order_types_list = [t.value for t in OrderType]
        sides_list = [s.value for s in OrderSide]
        states_list = [s.value for s in OrderState]

        order_types = np.random.choice(order_types_list, num_orders)
        sides = np.random.choice(sides_list, num_orders)
        states = np.random.choice(states_list, num_orders, p=[
                                  0.1, 0.1, 0.6, 0.15, 0.03, 0.02])

        quantities = np.random.randint(100, 10000, num_orders)

        orders_data = []
        for i in range(num_orders):
            acc_id = self.account_ids[account_indices[i]]
            ins_id = self.instrument_ids[instrument_indices[i]]
            order_type = order_types[i]
            side = sides[i]
            state = states[i]
            qty = float(quantities[i])

            base_price = self.instrument_prices[ins_id]
            price_offset = np.random.normal(0, base_price * 0.02)

            # properly set price and stop_price based on order type
            if order_type == 'market':
                price = 0.0
                stop_price = 0.0
            elif order_type in ['stop', 'stop_limit']:
                price = round(base_price + price_offset, 2)
                stop_price = round(base_price + price_offset * 1.5, 2)
            else:
                price = round(base_price + price_offset, 2)
                stop_price = 0.0

            # parent_order_id for iceberg/algo orders
            parent_order_id = ''
            if order_type == 'iceberg' and random.random() < 0.7:
                parent_order_id = f"O{uuid.uuid4().hex[:12]}"

            order = {
                'order_id': f"O{uuid.uuid4().hex[:12]}",
                'timestamp': timestamps[i].isoformat(),
                'account_id': acc_id,
                'trader_id': f"T{uuid.uuid4().hex[:8]}",
                'firm_id': random.choice(self.firm_ids),
                'instrument_id': ins_id,
                'order_type': order_type,
                'side': side,
                'quantity': qty,
                'displayed_quantity': qty if order_type != 'iceberg' else qty * 0.1,
                'price': price,
                'stop_price': stop_price,
                'time_in_force': random.choice(['day', 'gtc', 'ioc', 'fok']),
                'order_state': state,
                'venue_id': self.venue_ids[venue_indices[i]],
                'algo_indicator': random.random() < 0.2,
                'algo_id': f"ALGO{random.randint(1,10)}" if random.random() < 0.2 else '',
                'parent_order_id': parent_order_id,
                'session_id': uuid.uuid4().hex
            }
            orders_data.append(order)

        self.buffers['orders'].extend(orders_data)
        self.stats['orders'] += len(orders_data)

        # generate trades from filled orders
        filled_orders = [
            o for o in orders_data if o['order_state'] == 'filled']
        trades_data = []

        for order in filled_orders[:self.config.trades_per_day]:
            # find counterparty
            counterparty = random.choice(self.account_ids)
            while counterparty == order['account_id']:
                counterparty = random.choice(self.account_ids)

            trade_price = order['price'] if order['price'] > 0 else self.instrument_prices[order['instrument_id']]

            if order['side'] == 'buy':
                buy_acc = order['account_id']
                sell_acc = counterparty
            else:
                buy_acc = counterparty
                sell_acc = order['account_id']

            trade = {
                'trade_id': f"T{uuid.uuid4().hex[:12]}",
                'timestamp': order['timestamp'],
                'instrument_id': order['instrument_id'],
                'buy_order_id': order['order_id'] if order['side'] == 'buy' else f"O{uuid.uuid4().hex[:12]}",
                'sell_order_id': f"O{uuid.uuid4().hex[:12]}" if order['side'] == 'buy' else order['order_id'],
                'buy_account_id': buy_acc,
                'sell_account_id': sell_acc,
                'buy_firm_id': random.choice(self.firm_ids),
                'sell_firm_id': random.choice(self.firm_ids),
                'buy_trader_id': f"T{uuid.uuid4().hex[:8]}",
                'sell_trader_id': f"T{uuid.uuid4().hex[:8]}",
                'quantity': order['quantity'],
                'price': trade_price,
                'trade_value': order['quantity'] * trade_price,
                'aggressor_side': order['side'],
                'trade_type': random.choice(['regular', 'cross', 'block', 'auction']),
                'venue_id': order['venue_id'],
                'buy_capacity': random.choice(['principal', 'agent']),
                'sell_capacity': random.choice(['principal', 'agent'])
            }
            trades_data.append(trade)

        self.buffers['trades'].extend(trades_data)
        self.stats['trades'] += len(trades_data)

        # generate cancellations
        num_cancellations = int(
            len(orders_data) * self.config.cancellation_rate)
        cancelled_orders = random.sample(
            orders_data, min(num_cancellations, len(orders_data)))

        cancellations_data = []
        for order in cancelled_orders:
            cancellations_data.append({
                'cancellation_id': f"C{uuid.uuid4().hex[:12]}",
                'timestamp': (datetime.fromisoformat(order['timestamp']) + timedelta(seconds=random.randint(1, 300))).isoformat(),
                'order_id': order['order_id'],
                'account_id': order['account_id'],
                'instrument_id': order['instrument_id'],
                'remaining_quantity': order['quantity'] * random.uniform(0.5, 1.0),
                'reason': random.choice(['user_cancel', 'timeout', 'risk_limit', 'market_close'])
            })

        self.buffers['cancellations'].extend(cancellations_data)
        self.stats['cancellations'] += len(cancellations_data)

        # generate market data
        num_quotes = self.config.num_instruments * 100
        market_data = []

        for i in range(num_quotes):
            ins_id = random.choice(self.instrument_ids)
            base_price = self.instrument_prices[ins_id]
            spread = base_price * 0.001

            market_data.append({
                'timestamp': timestamps[i % len(timestamps)].isoformat(),
                'instrument_id': ins_id,
                'best_bid': round(base_price - spread/2, 2),
                'best_offer': round(base_price + spread/2, 2),
                'bid_size': float(random.randint(100, 10000)),
                'offer_size': float(random.randint(100, 10000)),
                'last_price': round(base_price, 2),
                'volume': float(random.randint(10000, 100000))
            })

        self.buffers['market_data'].extend(market_data)
        self.stats['market_data'] += len(market_data)

    def _generate_all_patterns(self):
        # generate manipulative patterns for all 40 rules
        print("  - Category 1: Wash Trading (4 patterns)")
        self._generate_wash_trading()

        print("  - Category 2: Layering/Spoofing (4 patterns)")
        self._generate_layering_spoofing()

        print("  - Category 3: Front Running (4 patterns)")
        self._generate_front_running()

        print("  - Category 4: Market Manipulation (4 patterns)")
        self._generate_market_manipulation()

        print("  - Category 5: Insider Trading (4 patterns)")
        self._generate_insider_trading()

        print("  - Category 6: Collusion (4 patterns)")
        self._generate_collusion()

        print("  - Category 7: Cross-Market (4 patterns)")
        self._generate_cross_market()

        print("  - Category 8: Benchmark (4 patterns)")
        self._generate_benchmark_manipulation()

        print("  - Category 9: AML/Suspicious (4 patterns)")
        self._generate_aml_patterns()

        print("  - Category 10: Derivatives (4 patterns)")
        self._generate_derivatives_patterns()

    def _generate_wash_trading(self):
        num_patterns = int(self.config.num_accounts *
                           self.config.wash_trading_prob)

        for _ in range(num_patterns):
            # rule 1.1 - same owner
            owner_id = random.choice(list(self.accounts_by_owner.keys()))
            if len(self.accounts_by_owner[owner_id]) < 2:
                continue

            buy_acc, sell_acc = random.sample(
                self.accounts_by_owner[owner_id], 2)
            ins_id = random.choice(self.instrument_ids)

            for _ in range(random.randint(5, 15)):
                day_offset = random.randint(
                    0, max(0, self.config.num_days - 1))
                date = self.start_date + timedelta(days=day_offset)
                trade_time = self._random_market_time(date)
                qty = float(random.randint(100, 1000))
                price = self.instrument_prices[ins_id] * \
                    (1 + random.uniform(-0.01, 0.01))

                trade = {
                    'trade_id': f"T{uuid.uuid4().hex[:12]}",
                    'timestamp': trade_time.isoformat(),
                    'instrument_id': ins_id,
                    'buy_order_id': f"O{uuid.uuid4().hex[:12]}",
                    'sell_order_id': f"O{uuid.uuid4().hex[:12]}",
                    'buy_account_id': buy_acc,
                    'sell_account_id': sell_acc,
                    'buy_firm_id': random.choice(self.firm_ids),
                    'sell_firm_id': random.choice(self.firm_ids),
                    'buy_trader_id': f"T{uuid.uuid4().hex[:8]}",
                    'sell_trader_id': f"T{uuid.uuid4().hex[:8]}",
                    'quantity': qty,
                    'price': round(price, 2),
                    'trade_value': qty * price,
                    'aggressor_side': 'buy',
                    'trade_type': 'regular',
                    'venue_id': random.choice(self.venue_ids),
                    'buy_capacity': 'principal',
                    'sell_capacity': 'principal'
                }
                self.buffers['trades'].append(trade)
                self.stats['trades'] += 1

    def _generate_layering_spoofing(self):
        num_patterns = int(self.config.num_accounts *
                           self.config.layering_prob)

        for _ in range(num_patterns):
            acc_id = random.choice(self.account_ids)
            ins_id = random.choice(self.instrument_ids)
            day_offset = random.randint(0, max(0, self.config.num_days - 1))
            date = self.start_date + timedelta(days=day_offset)

            # rule 2.1 - layering
            for layer in range(5):
                order_time = self._random_market_time(
                    date) + timedelta(seconds=layer*10)

                order = self._create_order(
                    acc_id, ins_id, 'buy', 'limit',
                    float(random.randint(1000, 5000)),
                    order_time, 'new'
                )
                self.buffers['orders'].append(order)
                self.stats['orders'] += 1

                # cancel quickly
                cancel_time = order_time + \
                    timedelta(seconds=random.randint(5, 30))
                self.buffers['cancellations'].append({
                    'cancellation_id': f"C{uuid.uuid4().hex[:12]}",
                    'timestamp': cancel_time.isoformat(),
                    'order_id': order['order_id'],
                    'account_id': acc_id,
                    'instrument_id': ins_id,
                    'remaining_quantity': order['quantity'],
                    'reason': 'user_cancel'
                })
                self.stats['cancellations'] += 1

    def _generate_front_running(self):
        num_patterns = int(self.config.num_accounts *
                           self.config.front_running_prob)

        for _ in range(num_patterns):
            # rule 3.1 - temporal front running
            large_order_acc = random.choice(self.account_ids)
            front_runner_acc = random.choice(self.account_ids)
            ins_id = random.choice(self.instrument_ids)
            day_offset = random.randint(0, max(0, self.config.num_days - 1))
            date = self.start_date + timedelta(days=day_offset)

            large_order_time = self._random_market_time(date)
            front_run_time = large_order_time - \
                timedelta(seconds=random.randint(5, 60))

            # front run order
            front_order = self._create_order(
                front_runner_acc, ins_id, 'buy', 'market',
                float(random.randint(500, 1000)),
                front_run_time, 'filled'
            )
            self.buffers['orders'].append(front_order)
            self.stats['orders'] += 1

            # large order
            large_order = self._create_order(
                large_order_acc, ins_id, 'buy', 'limit',
                float(random.randint(5000, 20000)),
                large_order_time, 'filled'
            )
            self.buffers['orders'].append(large_order)
            self.stats['orders'] += 1

    def _generate_market_manipulation(self):
        num_patterns = int(self.config.num_instruments *
                           self.config.manipulation_prob)

        for _ in range(num_patterns):
            # rule 4.1 - marking the close
            acc_id = random.choice(self.account_ids)
            ins_id = random.choice(self.instrument_ids)
            day_offset = random.randint(0, max(0, self.config.num_days - 1))
            date = self.start_date + timedelta(days=day_offset)

            close_time = date.replace(hour=16, minute=0)

            for _ in range(random.randint(5, 12)):
                trade_time = close_time - \
                    timedelta(minutes=random.randint(1, 15))

                trade = self._create_trade(
                    acc_id, random.choice(self.account_ids),
                    ins_id, float(random.randint(100, 500)),
                    trade_time
                )
                self.buffers['trades'].append(trade)
                self.stats['trades'] += 1

    def _generate_insider_trading(self):
        num_patterns = int(self.config.num_accounts * self.config.insider_prob)

        # defensive: ensure we have enough days for insider pattern
        min_event_day = min(10, max(1, self.config.num_days // 2))
        max_event_day = max(min_event_day + 1, self.config.num_days - 1)

        for _ in range(num_patterns):
            # rule 5.1 - pre-announcement trading
            acc_id = random.choice(self.account_ids)
            ins_id = random.choice(self.instrument_ids)

            # find event for this instrument with safe range
            event_date = self.start_date + \
                timedelta(days=random.randint(min_event_day, max_event_day))

            # limit lookback based on available days
            max_lookback = min(30, (event_date - self.start_date).days)

            for days_before in range(1, max_lookback + 1):
                trade_date = event_date - timedelta(days=days_before)
                if trade_date < self.start_date:
                    continue

                trade_time = self._random_market_time(trade_date)
                trade = self._create_trade(
                    acc_id, random.choice(self.account_ids),
                    ins_id, float(random.randint(500, 2000)),
                    trade_time
                )
                self.buffers['trades'].append(trade)
                self.stats['trades'] += 1

    def _generate_collusion(self):
        num_patterns = int(self.config.num_accounts *
                           self.config.collusion_prob)

        for _ in range(num_patterns):
            # rule 6.1 - synchronized trading
            accounts = random.sample(
                self.account_ids, min(3, len(self.account_ids)))
            ins_id = random.choice(self.instrument_ids)
            day_offset = random.randint(0, max(0, self.config.num_days - 1))
            date = self.start_date + timedelta(days=day_offset)

            sync_time = self._random_market_time(date)

            for acc in accounts:
                trade_time = sync_time + \
                    timedelta(seconds=random.randint(0, 30))
                trade = self._create_trade(
                    acc, random.choice(self.account_ids),
                    ins_id, float(random.randint(200, 800)),
                    trade_time
                )
                self.buffers['trades'].append(trade)
                self.stats['trades'] += 1

    def _generate_cross_market(self):
        num_patterns = int(self.config.num_instruments *
                           self.config.cross_market_prob)

        for _ in range(num_patterns):
            # rule 7.1 - cross-venue price manipulation
            acc_id = random.choice(self.account_ids)
            ins_id = random.choice(self.instrument_ids)
            day_offset = random.randint(0, max(0, self.config.num_days - 1))
            date = self.start_date + timedelta(days=day_offset)
            trade_time = self._random_market_time(date)

            # trade on multiple venues at different prices
            base_price = self.instrument_prices[ins_id]
            for venue in self.venue_ids[:3]:
                price = base_price * (1 + random.uniform(-0.01, 0.01))
                trade = self._create_trade(
                    acc_id, random.choice(self.account_ids),
                    ins_id, float(random.randint(100, 500)),
                    trade_time, venue=venue, price=price
                )
                self.buffers['trades'].append(trade)
                self.stats['trades'] += 1

    def _generate_benchmark_manipulation(self):
        num_patterns = int(self.config.num_instruments *
                           self.config.benchmark_prob)

        for _ in range(num_patterns):
            # rule 8.1 - fixing manipulation
            acc_id = random.choice(self.account_ids)
            ins_id = random.choice(self.instrument_ids)
            day_offset = random.randint(0, max(0, self.config.num_days - 1))
            date = self.start_date + timedelta(days=day_offset)

            # 4pm fixing
            fixing_time = date.replace(hour=16, minute=0)

            for _ in range(random.randint(5, 10)):
                trade_time = fixing_time - \
                    timedelta(minutes=random.randint(1, 5))
                trade = self._create_trade(
                    acc_id, random.choice(self.account_ids),
                    ins_id, float(random.randint(100, 400)),
                    trade_time
                )
                self.buffers['trades'].append(trade)
                self.stats['trades'] += 1

    def _generate_aml_patterns(self):
        num_patterns = int(self.config.num_accounts * self.config.aml_prob)

        for _ in range(num_patterns):
            # rule 9.1 - structuring
            acc_id = random.choice(self.account_ids)
            ins_id = random.choice(self.instrument_ids)

            # defensive: pick random day within available range
            day_offset = random.randint(0, max(0, self.config.num_days - 1))
            date = self.start_date + timedelta(days=day_offset)

            threshold = 9000

            for _ in range(random.randint(5, 10)):
                trade_time = self._random_market_time(date)
                value = random.uniform(threshold * 0.85, threshold * 0.95)
                qty = value / self.instrument_prices[ins_id]

                trade = self._create_trade(
                    acc_id, random.choice(self.account_ids),
                    ins_id, float(qty),
                    trade_time
                )
                self.buffers['trades'].append(trade)
                self.stats['trades'] += 1

    def _generate_derivatives_patterns(self):
        num_patterns = int(self.config.num_instruments *
                           self.config.derivatives_prob)

        for _ in range(num_patterns):
            # rule 10.3 - volatility manipulation
            acc_id = random.choice(self.account_ids)
            ins_id = random.choice(self.instrument_ids)

            # defensive: pick random day within available range
            day_offset = random.randint(0, max(0, self.config.num_days - 1))
            date = self.start_date + timedelta(days=day_offset)

            # create rapid price swings
            base_time = self._random_market_time(date)
            base_price = self.instrument_prices[ins_id]

            for i in range(10):
                trade_time = base_time + timedelta(minutes=i*2)
                price = base_price * (1 + (-1)**i * 0.03)

                trade = self._create_trade(
                    acc_id, random.choice(self.account_ids),
                    ins_id, float(random.randint(100, 300)),
                    trade_time, price=price
                )
                self.buffers['trades'].append(trade)
                self.stats['trades'] += 1

    def _create_order(self, acc_id: str, ins_id: str, side: str, order_type: str,
                      qty: float, timestamp: datetime, state: str) -> Dict:
        base_price = self.instrument_prices[ins_id]

        if order_type == 'market':
            price = 0.0
            stop_price = 0.0
        elif order_type in ['stop', 'stop_limit']:
            price = round(base_price * (1 + random.uniform(-0.02, 0.02)), 2)
            stop_price = round(
                base_price * (1 + random.uniform(-0.01, 0.03)), 2)
        else:
            price = round(base_price * (1 + random.uniform(-0.02, 0.02)), 2)
            stop_price = 0.0

        parent_order_id = ''
        if order_type == 'iceberg' and random.random() < 0.5:
            parent_order_id = f"O{uuid.uuid4().hex[:12]}"

        return {
            'order_id': f"O{uuid.uuid4().hex[:12]}",
            'timestamp': timestamp.isoformat(),
            'account_id': acc_id,
            'trader_id': f"T{uuid.uuid4().hex[:8]}",
            'firm_id': random.choice(self.firm_ids),
            'instrument_id': ins_id,
            'order_type': order_type,
            'side': side,
            'quantity': qty,
            'displayed_quantity': qty if order_type != 'iceberg' else qty * 0.1,
            'price': price,
            'stop_price': stop_price,
            'time_in_force': 'day',
            'order_state': state,
            'venue_id': random.choice(self.venue_ids),
            'algo_indicator': False,
            'algo_id': '',
            'parent_order_id': parent_order_id,
            'session_id': uuid.uuid4().hex
        }

    def _create_trade(self, buy_acc: str, sell_acc: str, ins_id: str,
                      qty: float, timestamp: datetime, venue: str = None,
                      price: float = None) -> Dict:
        if venue is None:
            venue = random.choice(self.venue_ids)
        if price is None:
            price = self.instrument_prices[ins_id] * \
                (1 + random.uniform(-0.01, 0.01))

        return {
            'trade_id': f"T{uuid.uuid4().hex[:12]}",
            'timestamp': timestamp.isoformat(),
            'instrument_id': ins_id,
            'buy_order_id': f"O{uuid.uuid4().hex[:12]}",
            'sell_order_id': f"O{uuid.uuid4().hex[:12]}",
            'buy_account_id': buy_acc,
            'sell_account_id': sell_acc,
            'buy_firm_id': random.choice(self.firm_ids),
            'sell_firm_id': random.choice(self.firm_ids),
            'buy_trader_id': f"T{uuid.uuid4().hex[:8]}",
            'sell_trader_id': f"T{uuid.uuid4().hex[:8]}",
            'quantity': qty,
            'price': round(price, 2),
            'trade_value': qty * price,
            'aggressor_side': 'buy',
            'trade_type': 'regular',
            'venue_id': venue,
            'buy_capacity': 'principal',
            'sell_capacity': 'principal'
        }

    def _random_market_time(self, date: datetime) -> datetime:
        market_open = date.replace(
            hour=self.config.market_open_hour, minute=0, second=0)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)
        seconds = int((market_close - market_open).total_seconds())
        return market_open + timedelta(seconds=random.randint(0, seconds))

    def _write_df(self, table_name: str, df: pd.DataFrame):
        filepath = os.path.join(self.config.output_dir,
                                f"{table_name}.parquet")
        df.to_parquet(filepath, index=False, engine='pyarrow')

    def _write_all_buffers(self):
        print("\nWriting all buffers to parquet...")
        for table_name, data in self.buffers.items():
            if data:
                df = pd.DataFrame(data)
                self._write_df(table_name, df)

    def _print_statistics(self):
        print("\n" + "="*80)
        print("DATA GENERATION COMPLETE")
        print("="*80)
        for key, value in sorted(self.stats.items()):
            print(f"{key:20s}: {value:,}")
        print("="*80)


def main():
    # configurations
    small_config = GeneratorConfig(
        num_accounts=150,
        num_instruments=75,
        num_firms=10,
        num_venues=3,
        num_days=7,
        orders_per_day=7500,
        trades_per_day=5000,
        output_dir='./data/small_test'
    )
    # small_config = GeneratorConfig(
    #     num_accounts=100,
    #     num_instruments=50,
    #     num_firms=10,
    #     num_venues=3,
    #     num_days=7,
    #     orders_per_day=5000,
    #     trades_per_day=2500,
    #     output_dir='./data/small_test'
    # )

    medium_config = GeneratorConfig(
        num_accounts=1000,
        num_instruments=500,
        num_firms=50,
        num_venues=5,
        num_days=30,
        orders_per_day=50000,
        trades_per_day=25000,
        output_dir='./data/medium'
    )

    large_config = GeneratorConfig(
        num_accounts=10000,
        num_instruments=2000,
        num_firms=200,
        num_venues=10,
        num_days=90,
        orders_per_day=500000,
        trades_per_day=250000,
        output_dir='./data/large'
    )

    # select config
    config = small_config

    print(
        f"Configuration: {config.num_accounts} accounts, {config.num_instruments} instruments, {config.num_days} days")

    import time
    start_time = time.time()

    generator = VectorizedMarketDataGenerator(config)
    generator.generate_all()

    elapsed = time.time() - start_time
    print(f"\nTotal time: {elapsed:.2f} seconds")
    print(f"Orders/sec: {generator.stats['orders'] / elapsed:,.0f}")
    print(f"Trades/sec: {generator.stats['trades'] / elapsed:,.0f}")


if __name__ == "__main__":
    main()
