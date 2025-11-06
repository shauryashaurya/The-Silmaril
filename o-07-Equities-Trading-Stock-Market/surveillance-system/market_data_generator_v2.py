# market_data_generator_v2.py
# High-performance realistic market surveillance test data generator

import random
import uuid
import json
import csv
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import pandas as pd
from faker import Faker
import numpy as np
from collections import defaultdict
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import pyarrow as pa
import pyarrow.parquet as pq

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Configuration


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
    modification_rate: float = 0.1
    wash_trading_probability: float = 0.02
    layering_probability: float = 0.01
    front_running_probability: float = 0.015
    insider_trading_probability: float = 0.005
    marking_close_probability: float = 0.01
    base_price_range: Tuple[float, float] = (10.0, 500.0)
    tick_size_default: float = 0.01
    volatility_range: Tuple[float, float] = (0.01, 0.05)
    market_open_hour: int = 9
    market_close_hour: int = 16
    related_account_probability: float = 0.15
    output_format: str = 'parquet'
    output_dir: str = './generated_data'
    generate_manipulative_patterns: bool = True
    batch_size: int = 10000
    num_workers: int = 4
    write_frequency: int = 50000

# Enums


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


class TradeType(Enum):
    REGULAR = 'regular'
    CROSS = 'cross'
    BLOCK = 'block'
    AUCTION = 'auction'
    DARK = 'dark'


class SecurityType(Enum):
    EQUITY = 'equity'
    BOND = 'bond'
    DERIVATIVE = 'derivative'
    ETF = 'etf'
    OPTION = 'option'

# Optimized Data Generator


class OptimizedMarketDataGenerator:
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.start_date = datetime.now() - timedelta(days=config.num_days)

        # Use dictionaries for O(1) lookups
        self.persons_dict: Dict[str, Dict] = {}
        self.firms_dict: Dict[str, Dict] = {}
        self.accounts_dict: Dict[str, Dict] = {}
        self.instruments_dict: Dict[str, Dict] = {}

        # Indices for fast lookups
        self.accounts_by_owner: Dict[str, List[str]] = defaultdict(list)
        self.accounts_by_firm: Dict[str, List[str]] = defaultdict(list)
        self.accounts_by_type: Dict[str, List[str]] = defaultdict(list)
        self.insider_connections: Dict[str, List[str]] = {}

        # Pre-generated IDs
        self.account_ids: List[str] = []
        self.instrument_ids: List[str] = []
        self.firm_ids: List[str] = []
        self.venue_ids: List[str] = []

        # Batch writers
        self.writers: Dict[str, pq.ParquetWriter] = {}
        self.buffers: Dict[str, List[Dict]] = defaultdict(list)

        # Statistics
        self.stats = {
            'persons': 0,
            'firms': 0,
            'accounts': 0,
            'instruments': 0,
            'orders': 0,
            'trades': 0,
            'cancellations': 0,
            'market_data': 0,
            'corporate_events': 0
        }

    def generate_all(self):
        print("Generating reference data...")
        self._setup_output_dir()

        # Generate reference data in batches
        self._generate_persons_batch()
        self._generate_firms_batch()
        self._generate_accounts_batch()
        self._generate_instruments_batch()
        self._generate_corporate_events_batch()

        # Build indices
        self._build_indices()

        print("Generating market activity...")
        # Generate daily activity in parallel
        self._generate_all_days_parallel()

        # Flush remaining buffers
        self._flush_all_buffers()
        self._close_all_writers()

        print("Data generation complete.")

    def _setup_output_dir(self):
        os.makedirs(self.config.output_dir, exist_ok=True)

    def _generate_persons_batch(self):
        print("Generating persons...")
        persons = []

        # Batch generate using numpy and faker
        for _ in range(self.config.num_accounts):
            person_id = f"P{uuid.uuid4().hex[:8]}"
            person = {
                'person_id': person_id,
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'email': fake.email(),
                'phone': fake.phone_number(),
                'address': fake.address().replace('\n', ', '),
                'ssn': fake.ssn(),
                'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat()
            }
            self.persons_dict[person_id] = person
            persons.append(person)

        self._write_batch('persons', persons)
        self.stats['persons'] = len(persons)

    def _generate_firms_batch(self):
        print("Generating firms...")
        firms = []
        firm_types = ['broker_dealer', 'investment_bank',
                      'hedge_fund', 'asset_manager', 'proprietary_trading']

        for _ in range(self.config.num_firms):
            firm_id = f"F{uuid.uuid4().hex[:8]}"
            firm = {
                'firm_id': firm_id,
                'firm_name': fake.company(),
                'lei_code': ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=20)),
                'address': fake.address().replace('\n', ', '),
                'country': fake.country_code(),
                'firm_type': random.choice(firm_types)
            }
            self.firms_dict[firm_id] = firm
            self.firm_ids.append(firm_id)
            firms.append(firm)

        self._write_batch('firms', firms)
        self.stats['firms'] = len(firms)

    def _generate_accounts_batch(self):
        print("Generating accounts...")
        accounts = []
        account_types = [t.value for t in AccountType]
        person_ids = list(self.persons_dict.keys())

        # Primary accounts
        for person_id in person_ids:
            firm_id = random.choice(self.firm_ids)
            account_id = f"A{uuid.uuid4().hex[:8]}"

            account = {
                'account_id': account_id,
                'beneficial_owner_id': person_id,
                'parent_account_id': None,
                'firm_id': firm_id,
                'account_type': random.choice(account_types),
                'opening_date': (self.start_date - timedelta(days=random.randint(1, 1000))).isoformat(),
                'credit_limit': random.uniform(10000, 10000000),
                'ip_addresses': json.dumps([fake.ipv4() for _ in range(random.randint(1, 3))]),
                'device_fingerprints': json.dumps([uuid.uuid4().hex for _ in range(random.randint(1, 2))]),
                'related_accounts': json.dumps([])
            }

            self.accounts_dict[account_id] = account
            self.account_ids.append(account_id)
            accounts.append(account)

        # Sub-accounts (10% of primary)
        num_sub = int(len(accounts) * 0.1)
        for _ in range(num_sub):
            parent_id = random.choice(self.account_ids)
            parent = self.accounts_dict[parent_id]
            account_id = f"A{uuid.uuid4().hex[:8]}"

            account = {
                'account_id': account_id,
                'beneficial_owner_id': parent['beneficial_owner_id'],
                'parent_account_id': parent_id,
                'firm_id': parent['firm_id'],
                'account_type': parent['account_type'],
                'opening_date': (self.start_date - timedelta(days=random.randint(1, 500))).isoformat(),
                'credit_limit': parent['credit_limit'] * 0.5,
                'ip_addresses': parent['ip_addresses'],
                'device_fingerprints': parent['device_fingerprints'],
                'related_accounts': json.dumps([])
            }

            self.accounts_dict[account_id] = account
            self.account_ids.append(account_id)
            accounts.append(account)

        # Generate relationships in batch
        num_with_relations = int(len(self.account_ids)
                                 * self.config.related_account_probability)
        accounts_with_relations = random.sample(
            self.account_ids, num_with_relations)

        for account_id in accounts_with_relations:
            num_related = random.randint(1, 3)
            related = random.sample([a for a in self.account_ids if a != account_id],
                                    min(num_related, len(self.account_ids) - 1))
            self.accounts_dict[account_id]['related_accounts'] = json.dumps(
                related)

        self._write_batch('accounts', accounts)
        self.stats['accounts'] = len(accounts)

    def _generate_instruments_batch(self):
        print("Generating instruments...")
        instruments = []
        sectors = ['Technology', 'Finance', 'Healthcare', 'Energy',
                   'Consumer', 'Industrial', 'Materials', 'Utilities']
        security_types = [t.value for t in SecurityType]

        # Vectorized generation
        num_instruments = self.config.num_instruments
        symbols = [''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(3, 5)))
                   for _ in range(num_instruments)]
        prices = np.random.uniform(
            *self.config.base_price_range, num_instruments)
        volatilities = np.random.uniform(
            *self.config.volatility_range, num_instruments)
        market_caps = np.random.uniform(100e6, 500e9, num_instruments)
        avg_volumes = np.random.uniform(100000, 50000000, num_instruments)

        for i in range(num_instruments):
            instrument_id = f"I{uuid.uuid4().hex[:8]}"
            instrument = {
                'instrument_id': instrument_id,
                'symbol': symbols[i],
                'isin': ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=12)),
                'security_type': random.choice(security_types),
                'sector': random.choice(sectors),
                'market_cap': float(market_caps[i]),
                'average_daily_volume': float(avg_volumes[i]),
                'tick_size': self.config.tick_size_default,
                'lot_size': 100,
                'price': float(prices[i]),
                'volatility': float(volatilities[i]),
                'issuer': fake.company()
            }

            self.instruments_dict[instrument_id] = instrument
            self.instrument_ids.append(instrument_id)
            instruments.append(instrument)

        # Create insider connections
        num_with_insiders = int(num_instruments * 0.3)
        instruments_with_insiders = random.sample(
            self.instrument_ids, num_with_insiders)
        person_ids = list(self.persons_dict.keys())

        for instrument_id in instruments_with_insiders:
            insiders = random.sample(person_ids, random.randint(3, 8))
            self.insider_connections[instrument_id] = insiders

        self._write_batch('instruments', instruments)
        self.stats['instruments'] = len(instruments)

    def _generate_corporate_events_batch(self):
        print("Generating corporate events...")
        events = []
        event_types = ['earnings', 'merger', 'acquisition', 'dividend', 'stock_split',
                       'IPO', 'secondary_offering', 'index_add', 'index_remove']
        materiality_levels = ['low', 'medium', 'high']

        num_events = int(self.config.num_instruments * 0.2)

        for _ in range(num_events):
            instrument_id = random.choice(self.instrument_ids)
            event_date = self.start_date + \
                timedelta(days=random.randint(0, self.config.num_days))

            event = {
                'event_id': f"E{uuid.uuid4().hex[:8]}",
                'instrument_id': instrument_id,
                'event_type': random.choice(event_types),
                'announcement_date': (event_date - timedelta(days=random.randint(1, 14))).isoformat(),
                'effective_date': event_date.isoformat(),
                'materiality': random.choice(materiality_levels),
                'description': fake.sentence()
            }
            events.append(event)

        self._write_batch('corporate_events', events)
        self.stats['corporate_events'] = len(events)

    def _build_indices(self):
        print("Building indices...")

        # Index accounts by owner
        for account_id, account in self.accounts_dict.items():
            owner_id = account['beneficial_owner_id']
            self.accounts_by_owner[owner_id].append(account_id)

            firm_id = account['firm_id']
            self.accounts_by_firm[firm_id].append(account_id)

            account_type = account['account_type']
            self.accounts_by_type[account_type].append(account_id)

        # Pre-generate venue IDs
        self.venue_ids = [f"V{i}" for i in range(
            1, self.config.num_venues + 1)]

    def _generate_all_days_parallel(self):
        # Generate each day in parallel
        dates = [self.start_date + timedelta(days=i)
                 for i in range(self.config.num_days)]

        # For now, sequential to maintain state consistency
        # Can be parallelized with proper synchronization
        for i, date in enumerate(dates):
            print(f"Day {i+1}/{self.config.num_days}: {date.date()}")
            self._generate_daily_activity(date)

    def _generate_daily_activity(self, date: datetime):
        # Generate market data first
        self._generate_market_data_vectorized(date)

        # Generate orders in large batches
        self._generate_orders_vectorized(date)

        # Generate manipulative patterns
        if self.config.generate_manipulative_patterns:
            self._generate_layering_batch(date)
            self._generate_wash_trading_batch(date)
            self._generate_front_running_batch(date)
            self._generate_insider_trading_batch(date)
            self._generate_marking_close_batch(date)

    def _generate_market_data_vectorized(self, date: datetime):
        market_open = date.replace(
            hour=self.config.market_open_hour, minute=0, second=0)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)
        minutes = int((market_close - market_open).total_seconds() / 60)

        # Sample instruments for market data
        sample_size = max(50, int(len(self.instrument_ids) * 0.1))
        sampled_instruments = random.sample(self.instrument_ids, sample_size)

        market_data_batch = []

        for minute in range(0, minutes, 5):
            current_time = market_open + timedelta(minutes=minute)

            for instrument_id in sampled_instruments:
                instrument = self.instruments_dict[instrument_id]

                # Vectorized price movement
                price_change = np.random.normal(
                    0, instrument['volatility'] * instrument['price'])
                new_price = max(
                    instrument['price'] + price_change, instrument['tick_size'])
                spread = instrument['tick_size'] * random.randint(1, 5)

                md = {
                    'timestamp': current_time.isoformat(),
                    'instrument_id': instrument_id,
                    'best_bid': round(new_price - spread/2, 2),
                    'best_offer': round(new_price + spread/2, 2),
                    'bid_size': random.uniform(100, 10000),
                    'offer_size': random.uniform(100, 10000),
                    'last_price': new_price,
                    'volume': random.uniform(1000, 100000)
                }
                market_data_batch.append(md)

                if len(market_data_batch) >= self.config.batch_size:
                    self._write_batch('market_data', market_data_batch)
                    self.stats['market_data'] += len(market_data_batch)
                    market_data_batch = []

        if market_data_batch:
            self._write_batch('market_data', market_data_batch)
            self.stats['market_data'] += len(market_data_batch)

    def _generate_orders_vectorized(self, date: datetime):
        market_open = date.replace(
            hour=self.config.market_open_hour, minute=0, second=0)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)

        orders_batch = []
        trades_batch = []
        cancellations_batch = []

        # Pre-generate random values in bulk
        num_orders = self.config.orders_per_day
        account_indices = np.random.randint(
            0, len(self.account_ids), num_orders)
        instrument_indices = np.random.randint(
            0, len(self.instrument_ids), num_orders)
        side_indices = np.random.randint(0, 2, num_orders)
        order_type_indices = np.random.randint(0, 6, num_orders)
        timestamps = self._random_timestamps(
            market_open, market_close, num_orders)
        quantities = np.random.randint(1, 100, num_orders) * 100
        execute_flags = np.random.random(num_orders) < 0.6
        cancel_flags = np.random.random(
            num_orders) < self.config.cancellation_rate

        order_types = [t.value for t in OrderType]
        sides = [OrderSide.BUY.value, OrderSide.SELL.value]

        for i in range(num_orders):
            account_id = self.account_ids[account_indices[i]]
            instrument_id = self.instrument_ids[instrument_indices[i]]
            account = self.accounts_dict[account_id]
            instrument = self.instruments_dict[instrument_id]

            order_type = order_types[order_type_indices[i]]
            side = sides[side_indices[i]]
            quantity = int(quantities[i])
            timestamp = timestamps[i]

            displayed_quantity = quantity
            if order_type == OrderType.ICEBERG.value:
                displayed_quantity = int(quantity * random.uniform(0.1, 0.3))
            elif order_type == OrderType.HIDDEN.value:
                displayed_quantity = 0

            price = None
            if order_type in [OrderType.LIMIT.value, OrderType.STOP_LIMIT.value]:
                price = round(instrument['price'] *
                              random.uniform(0.95, 1.05), 2)

            order_id = f"O{uuid.uuid4().hex[:12]}"
            order = {
                'order_id': order_id,
                'timestamp': timestamp.isoformat(),
                'account_id': account_id,
                'trader_id': f"T{uuid.uuid4().hex[:8]}",
                'firm_id': account['firm_id'],
                'instrument_id': instrument_id,
                'order_type': order_type,
                'side': side,
                'quantity': float(quantity),
                'displayed_quantity': float(displayed_quantity),
                'price': price,
                'stop_price': None,
                'time_in_force': random.choice(['day', 'gtc', 'ioc', 'fok']),
                'order_state': OrderState.NEW.value,
                'venue_id': random.choice(self.venue_ids),
                'algo_indicator': random.random() < 0.3,
                'algo_id': f"ALG{random.randint(1, 20)}" if random.random() < 0.3 else None,
                'parent_order_id': None,
                'session_id': uuid.uuid4().hex
            }
            orders_batch.append(order)

            # Generate trade
            if execute_flags[i]:
                trade = self._create_trade_fast(order, timestamp)
                if trade:
                    trades_batch.append(trade)
                    order['order_state'] = OrderState.FILLED.value

            # Generate cancellation
            if cancel_flags[i] and order['order_state'] == OrderState.NEW.value:
                cancel_time = timestamp + \
                    timedelta(milliseconds=random.randint(100, 60000))
                cancellation = {
                    'cancellation_id': f"C{uuid.uuid4().hex[:12]}",
                    'timestamp': cancel_time.isoformat(),
                    'order_id': order_id,
                    'account_id': account_id,
                    'instrument_id': instrument_id,
                    'remaining_quantity': float(quantity),
                    'reason': random.choice(['user_cancel', 'timeout', 'risk_breach', 'end_of_day'])
                }
                cancellations_batch.append(cancellation)
                order['order_state'] = OrderState.CANCELLED.value

            # Write in batches
            if len(orders_batch) >= self.config.batch_size:
                self._write_batch('orders', orders_batch)
                self.stats['orders'] += len(orders_batch)
                orders_batch = []

            if len(trades_batch) >= self.config.batch_size:
                self._write_batch('trades', trades_batch)
                self.stats['trades'] += len(trades_batch)
                trades_batch = []

            if len(cancellations_batch) >= self.config.batch_size:
                self._write_batch('cancellations', cancellations_batch)
                self.stats['cancellations'] += len(cancellations_batch)
                cancellations_batch = []

        # Flush remaining
        if orders_batch:
            self._write_batch('orders', orders_batch)
            self.stats['orders'] += len(orders_batch)
        if trades_batch:
            self._write_batch('trades', trades_batch)
            self.stats['trades'] += len(trades_batch)
        if cancellations_batch:
            self._write_batch('cancellations', cancellations_batch)
            self.stats['cancellations'] += len(cancellations_batch)

    def _create_trade_fast(self, order: Dict, timestamp: datetime) -> Optional[Dict]:
        # Fast trade creation without searching
        opposite_side = OrderSide.SELL.value if order['side'] == OrderSide.BUY.value else OrderSide.BUY.value

        # Create synthetic matching account
        matching_account_id = random.choice(self.account_ids)
        matching_account = self.accounts_dict[matching_account_id]

        quantity = order['quantity'] * random.uniform(0.5, 1.0)
        trade_price = order['price'] if order['price'] else self.instruments_dict[order['instrument_id']]['price']

        exec_timestamp = timestamp + \
            timedelta(milliseconds=random.randint(10, 5000))

        if order['side'] == OrderSide.BUY.value:
            buy_account_id = order['account_id']
            sell_account_id = matching_account_id
            buy_firm = order['firm_id']
            sell_firm = matching_account['firm_id']
        else:
            sell_account_id = order['account_id']
            buy_account_id = matching_account_id
            sell_firm = order['firm_id']
            buy_firm = matching_account['firm_id']

        trade = {
            'trade_id': f"T{uuid.uuid4().hex[:12]}",
            'timestamp': exec_timestamp.isoformat(),
            'instrument_id': order['instrument_id'],
            'buy_order_id': order['order_id'] if order['side'] == OrderSide.BUY.value else f"O{uuid.uuid4().hex[:12]}",
            'sell_order_id': order['order_id'] if order['side'] == OrderSide.SELL.value else f"O{uuid.uuid4().hex[:12]}",
            'buy_account_id': buy_account_id,
            'sell_account_id': sell_account_id,
            'buy_firm_id': buy_firm,
            'sell_firm_id': sell_firm,
            'buy_trader_id': f"T{uuid.uuid4().hex[:8]}",
            'sell_trader_id': f"T{uuid.uuid4().hex[:8]}",
            'quantity': float(quantity),
            'price': float(trade_price),
            'trade_value': float(quantity * trade_price),
            'aggressor_side': order['side'],
            'trade_type': random.choice([t.value for t in TradeType]),
            'venue_id': order['venue_id'],
            'buy_capacity': random.choice(['principal', 'agency', 'riskless_principal', 'market_maker']),
            'sell_capacity': random.choice(['principal', 'agency', 'riskless_principal', 'market_maker'])
        }

        return trade

    def _generate_layering_batch(self, date: datetime):
        num_patterns = int(self.config.orders_per_day *
                           self.config.layering_probability)
        market_open = date.replace(
            hour=self.config.market_open_hour, minute=0, second=0)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)

        orders_batch = []
        trades_batch = []
        cancellations_batch = []

        for _ in range(num_patterns):
            account_id = random.choice(self.account_ids)
            instrument_id = random.choice(self.instrument_ids)
            account = self.accounts_dict[account_id]
            instrument = self.instruments_dict[instrument_id]

            side = random.choice([OrderSide.BUY, OrderSide.SELL])
            base_time = self._random_timestamp(market_open, market_close)

            # Layer orders
            num_layers = random.randint(3, 8)
            layer_order_ids = []

            for i in range(num_layers):
                offset = (i + 2) * instrument['tick_size']
                price = instrument['price'] + \
                    offset if side == OrderSide.SELL else instrument['price'] - offset
                order_time = base_time + \
                    timedelta(milliseconds=i * random.randint(100, 500))

                order_id = f"O{uuid.uuid4().hex[:12]}"
                layer_order_ids.append(order_id)

                order = {
                    'order_id': order_id,
                    'timestamp': order_time.isoformat(),
                    'account_id': account_id,
                    'trader_id': f"T{uuid.uuid4().hex[:8]}",
                    'firm_id': account['firm_id'],
                    'instrument_id': instrument_id,
                    'order_type': OrderType.LIMIT.value,
                    'side': side.value,
                    'quantity': float(random.randint(5, 20) * 100),
                    'displayed_quantity': float(random.randint(5, 20) * 100),
                    'price': round(price, 2),
                    'stop_price': None,
                    'time_in_force': 'day',
                    'order_state': OrderState.NEW.value,
                    'venue_id': random.choice(self.venue_ids),
                    'algo_indicator': False,
                    'algo_id': None,
                    'parent_order_id': None,
                    'session_id': uuid.uuid4().hex
                }
                orders_batch.append(order)

            # Opposite execution
            exec_time = base_time + timedelta(seconds=random.randint(10, 50))
            opposite_side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY

            exec_order_id = f"O{uuid.uuid4().hex[:12]}"
            exec_order = {
                'order_id': exec_order_id,
                'timestamp': exec_time.isoformat(),
                'account_id': account_id,
                'trader_id': f"T{uuid.uuid4().hex[:8]}",
                'firm_id': account['firm_id'],
                'instrument_id': instrument_id,
                'order_type': OrderType.MARKET.value,
                'side': opposite_side.value,
                'quantity': float(random.randint(1, 5) * 100),
                'displayed_quantity': float(random.randint(1, 5) * 100),
                'price': None,
                'stop_price': None,
                'time_in_force': 'ioc',
                'order_state': OrderState.FILLED.value,
                'venue_id': orders_batch[-1]['venue_id'] if orders_batch else random.choice(self.venue_ids),
                'algo_indicator': False,
                'algo_id': None,
                'parent_order_id': None,
                'session_id': uuid.uuid4().hex
            }
            orders_batch.append(exec_order)

            # Create trade
            trade = self._create_trade_fast(exec_order, exec_time)
            if trade:
                trades_batch.append(trade)

            # Cancellations
            cancel_time = exec_time + timedelta(seconds=random.randint(5, 60))
            for layer_id in layer_order_ids:
                if random.random() < 0.9:
                    cancellation = {
                        'cancellation_id': f"C{uuid.uuid4().hex[:12]}",
                        'timestamp': cancel_time.isoformat(),
                        'order_id': layer_id,
                        'account_id': account_id,
                        'instrument_id': instrument_id,
                        'remaining_quantity': float(random.randint(5, 20) * 100),
                        'reason': 'user_cancel'
                    }
                    cancellations_batch.append(cancellation)

        # Write batches
        if orders_batch:
            self._write_batch('orders', orders_batch)
            self.stats['orders'] += len(orders_batch)
        if trades_batch:
            self._write_batch('trades', trades_batch)
            self.stats['trades'] += len(trades_batch)
        if cancellations_batch:
            self._write_batch('cancellations', cancellations_batch)
            self.stats['cancellations'] += len(cancellations_batch)

    def _generate_wash_trading_batch(self, date: datetime):
        num_patterns = int(self.config.trades_per_day *
                           self.config.wash_trading_probability)
        market_open = date.replace(
            hour=self.config.market_open_hour, minute=0, second=0)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)

        orders_batch = []
        trades_batch = []

        # Use indexed lookups for related accounts
        owners_with_multiple = [owner for owner, accounts in self.accounts_by_owner.items()
                                if len(accounts) >= 2]

        if not owners_with_multiple:
            return

        for _ in range(num_patterns):
            owner = random.choice(owners_with_multiple)
            accounts = self.accounts_by_owner[owner]

            if len(accounts) < 2:
                continue

            account1_id, account2_id = random.sample(accounts, 2)
            instrument_id = random.choice(self.instrument_ids)
            instrument = self.instruments_dict[instrument_id]

            num_trades = random.randint(3, 15)

            for _ in range(num_trades):
                trade_time = self._random_timestamp(market_open, market_close)
                quantity = random.randint(1, 10) * 100
                price = round(instrument['price'] *
                              random.uniform(0.999, 1.001), 2)

                buy_order_id = f"O{uuid.uuid4().hex[:12]}"
                sell_order_id = f"O{uuid.uuid4().hex[:12]}"

                buy_order = {
                    'order_id': buy_order_id,
                    'timestamp': trade_time.isoformat(),
                    'account_id': account1_id,
                    'trader_id': f"T{uuid.uuid4().hex[:8]}",
                    'firm_id': self.accounts_dict[account1_id]['firm_id'],
                    'instrument_id': instrument_id,
                    'order_type': OrderType.LIMIT.value,
                    'side': OrderSide.BUY.value,
                    'quantity': float(quantity),
                    'displayed_quantity': float(quantity),
                    'price': price,
                    'stop_price': None,
                    'time_in_force': 'ioc',
                    'order_state': OrderState.FILLED.value,
                    'venue_id': random.choice(self.venue_ids),
                    'algo_indicator': False,
                    'algo_id': None,
                    'parent_order_id': None,
                    'session_id': uuid.uuid4().hex
                }

                sell_order = {
                    'order_id': sell_order_id,
                    'timestamp': (trade_time + timedelta(milliseconds=random.randint(1, 100))).isoformat(),
                    'account_id': account2_id,
                    'trader_id': f"T{uuid.uuid4().hex[:8]}",
                    'firm_id': self.accounts_dict[account2_id]['firm_id'],
                    'instrument_id': instrument_id,
                    'order_type': OrderType.LIMIT.value,
                    'side': OrderSide.SELL.value,
                    'quantity': float(quantity),
                    'displayed_quantity': float(quantity),
                    'price': price,
                    'stop_price': None,
                    'time_in_force': 'ioc',
                    'order_state': OrderState.FILLED.value,
                    'venue_id': buy_order['venue_id'],
                    'algo_indicator': False,
                    'algo_id': None,
                    'parent_order_id': None,
                    'session_id': uuid.uuid4().hex
                }

                orders_batch.extend([buy_order, sell_order])

                trade = {
                    'trade_id': f"T{uuid.uuid4().hex[:12]}",
                    'timestamp': (trade_time + timedelta(milliseconds=random.randint(10, 200))).isoformat(),
                    'instrument_id': instrument_id,
                    'buy_order_id': buy_order_id,
                    'sell_order_id': sell_order_id,
                    'buy_account_id': account1_id,
                    'sell_account_id': account2_id,
                    'buy_firm_id': self.accounts_dict[account1_id]['firm_id'],
                    'sell_firm_id': self.accounts_dict[account2_id]['firm_id'],
                    'buy_trader_id': buy_order['trader_id'],
                    'sell_trader_id': sell_order['trader_id'],
                    'quantity': float(quantity),
                    'price': float(price),
                    'trade_value': float(quantity * price),
                    'aggressor_side': OrderSide.BUY.value,
                    'trade_type': TradeType.REGULAR.value,
                    'venue_id': buy_order['venue_id'],
                    'buy_capacity': 'principal',
                    'sell_capacity': 'principal'
                }
                trades_batch.append(trade)

        if orders_batch:
            self._write_batch('orders', orders_batch)
            self.stats['orders'] += len(orders_batch)
        if trades_batch:
            self._write_batch('trades', trades_batch)
            self.stats['trades'] += len(trades_batch)

    def _generate_front_running_batch(self, date: datetime):
        num_patterns = int(self.config.orders_per_day *
                           self.config.front_running_probability)
        market_open = date.replace(
            hour=self.config.market_open_hour, minute=0, second=0)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)

        orders_batch = []
        trades_batch = []

        # Use indexed lookups
        for firm_id, firm_accounts in list(self.accounts_by_firm.items())[:20]:
            if len(firm_accounts) < 2:
                continue

            prop_accounts = [a for a in firm_accounts
                             if self.accounts_dict[a]['account_type'] == AccountType.PROPRIETARY.value]
            cust_accounts = [a for a in firm_accounts
                             if self.accounts_dict[a]['account_type'] in [AccountType.RETAIL.value, AccountType.INSTITUTIONAL.value]]

            if not prop_accounts or not cust_accounts:
                continue

            for _ in range(max(1, num_patterns // 20)):
                prop_account_id = random.choice(prop_accounts)
                cust_account_id = random.choice(cust_accounts)
                instrument_id = random.choice(self.instrument_ids)
                instrument = self.instruments_dict[instrument_id]

                side = random.choice([OrderSide.BUY, OrderSide.SELL])
                base_time = self._random_timestamp(market_open, market_close)

                # Prop order
                prop_order_id = f"O{uuid.uuid4().hex[:12]}"
                prop_order = {
                    'order_id': prop_order_id,
                    'timestamp': base_time.isoformat(),
                    'account_id': prop_account_id,
                    'trader_id': f"T{uuid.uuid4().hex[:8]}",
                    'firm_id': firm_id,
                    'instrument_id': instrument_id,
                    'order_type': OrderType.LIMIT.value,
                    'side': side.value,
                    'quantity': float(random.randint(1, 5) * 100),
                    'displayed_quantity': float(random.randint(1, 5) * 100),
                    'price': round(instrument['price'] * random.uniform(0.999, 1.001), 2),
                    'stop_price': None,
                    'time_in_force': 'day',
                    'order_state': OrderState.FILLED.value,
                    'venue_id': random.choice(self.venue_ids),
                    'algo_indicator': False,
                    'algo_id': None,
                    'parent_order_id': None,
                    'session_id': uuid.uuid4().hex
                }
                orders_batch.append(prop_order)

                # Customer order
                cust_time = base_time + \
                    timedelta(seconds=random.randint(5, 45))
                cust_order_id = f"O{uuid.uuid4().hex[:12]}"
                cust_order = {
                    'order_id': cust_order_id,
                    'timestamp': cust_time.isoformat(),
                    'account_id': cust_account_id,
                    'trader_id': f"T{uuid.uuid4().hex[:8]}",
                    'firm_id': firm_id,
                    'instrument_id': instrument_id,
                    'order_type': OrderType.MARKET.value,
                    'side': side.value,
                    'quantity': float(prop_order['quantity'] * random.randint(10, 50)),
                    'displayed_quantity': float(prop_order['quantity'] * random.randint(10, 50)),
                    'price': None,
                    'stop_price': None,
                    'time_in_force': 'day',
                    'order_state': OrderState.FILLED.value,
                    'venue_id': prop_order['venue_id'],
                    'algo_indicator': False,
                    'algo_id': None,
                    'parent_order_id': None,
                    'session_id': uuid.uuid4().hex
                }
                orders_batch.append(cust_order)

                # Create trades
                prop_trade = self._create_trade_fast(prop_order, base_time)
                if prop_trade:
                    trades_batch.append(prop_trade)

                cust_trade = self._create_trade_fast(cust_order, cust_time)
                if cust_trade:
                    trades_batch.append(cust_trade)

        if orders_batch:
            self._write_batch('orders', orders_batch)
            self.stats['orders'] += len(orders_batch)
        if trades_batch:
            self._write_batch('trades', trades_batch)
            self.stats['trades'] += len(trades_batch)

    def _generate_insider_trading_batch(self, date: datetime):
        # Simplified insider trading for performance
        if not self.insider_connections:
            return

        orders_batch = []
        trades_batch = []

        num_patterns = max(1, int(self.config.orders_per_day *
                           self.config.insider_trading_probability))

        for _ in range(num_patterns):
            instrument_id = random.choice(
                list(self.insider_connections.keys()))
            insider_person_id = random.choice(
                self.insider_connections[instrument_id])

            if insider_person_id not in self.accounts_by_owner:
                continue

            insider_accounts = self.accounts_by_owner[insider_person_id]
            if not insider_accounts:
                continue

            insider_account_id = random.choice(insider_accounts)
            instrument = self.instruments_dict[instrument_id]

            market_open = date.replace(
                hour=self.config.market_open_hour, minute=0, second=0)
            market_close = date.replace(
                hour=self.config.market_close_hour, minute=0, second=0)

            side = random.choice([OrderSide.BUY, OrderSide.SELL])

            for _ in range(random.randint(5, 15)):
                trade_time = self._random_timestamp(market_open, market_close)
                quantity = random.randint(50, 200) * 100

                order_id = f"O{uuid.uuid4().hex[:12]}"
                order = {
                    'order_id': order_id,
                    'timestamp': trade_time.isoformat(),
                    'account_id': insider_account_id,
                    'trader_id': f"T{uuid.uuid4().hex[:8]}",
                    'firm_id': self.accounts_dict[insider_account_id]['firm_id'],
                    'instrument_id': instrument_id,
                    'order_type': OrderType.MARKET.value,
                    'side': side.value,
                    'quantity': float(quantity),
                    'displayed_quantity': float(quantity),
                    'price': None,
                    'stop_price': None,
                    'time_in_force': 'day',
                    'order_state': OrderState.FILLED.value,
                    'venue_id': random.choice(self.venue_ids),
                    'algo_indicator': False,
                    'algo_id': None,
                    'parent_order_id': None,
                    'session_id': uuid.uuid4().hex
                }
                orders_batch.append(order)

                trade = self._create_trade_fast(order, trade_time)
                if trade:
                    trades_batch.append(trade)

        if orders_batch:
            self._write_batch('orders', orders_batch)
            self.stats['orders'] += len(orders_batch)
        if trades_batch:
            self._write_batch('trades', trades_batch)
            self.stats['trades'] += len(trades_batch)

    def _generate_marking_close_batch(self, date: datetime):
        num_patterns = int(self.config.num_instruments *
                           self.config.marking_close_probability)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)
        close_window_start = market_close - timedelta(minutes=5)

        orders_batch = []
        trades_batch = []

        for _ in range(num_patterns):
            account_id = random.choice(self.account_ids)
            instrument_id = random.choice(self.instrument_ids)
            account = self.accounts_dict[account_id]
            side = random.choice([OrderSide.BUY, OrderSide.SELL])

            for _ in range(random.randint(5, 15)):
                trade_time = self._random_timestamp(
                    close_window_start, market_close)

                order_id = f"O{uuid.uuid4().hex[:12]}"
                order = {
                    'order_id': order_id,
                    'timestamp': trade_time.isoformat(),
                    'account_id': account_id,
                    'trader_id': f"T{uuid.uuid4().hex[:8]}",
                    'firm_id': account['firm_id'],
                    'instrument_id': instrument_id,
                    'order_type': OrderType.MARKET.value,
                    'side': side.value,
                    'quantity': float(random.randint(10, 50) * 100),
                    'displayed_quantity': float(random.randint(10, 50) * 100),
                    'price': None,
                    'stop_price': None,
                    'time_in_force': 'ioc',
                    'order_state': OrderState.FILLED.value,
                    'venue_id': random.choice(self.venue_ids),
                    'algo_indicator': False,
                    'algo_id': None,
                    'parent_order_id': None,
                    'session_id': uuid.uuid4().hex
                }
                orders_batch.append(order)

                trade = self._create_trade_fast(order, trade_time)
                if trade:
                    trades_batch.append(trade)

        if orders_batch:
            self._write_batch('orders', orders_batch)
            self.stats['orders'] += len(orders_batch)
        if trades_batch:
            self._write_batch('trades', trades_batch)
            self.stats['trades'] += len(trades_batch)

    def _random_timestamps(self, start: datetime, end: datetime, count: int) -> List[datetime]:
        # Vectorized timestamp generation
        delta_seconds = int((end - start).total_seconds())
        random_seconds = np.random.randint(0, delta_seconds, count)
        return [start + timedelta(seconds=int(s)) for s in random_seconds]

    def _random_timestamp(self, start: datetime, end: datetime) -> datetime:
        delta_seconds = int((end - start).total_seconds())
        random_seconds = random.randint(0, delta_seconds)
        return start + timedelta(seconds=random_seconds)

    def _write_batch(self, table_name: str, data: List[Dict]):
        # Buffer data and write when buffer is full
        self.buffers[table_name].extend(data)

        if len(self.buffers[table_name]) >= self.config.write_frequency:
            self._flush_buffer(table_name)

    def _flush_buffer(self, table_name: str):
        if not self.buffers[table_name]:
            return

        df = pd.DataFrame(self.buffers[table_name])

        filepath = os.path.join(self.config.output_dir,
                                f"{table_name}.parquet")

        if os.path.exists(filepath):
            # Append to existing file
            existing_df = pd.read_parquet(filepath)
            df = pd.concat([existing_df, df], ignore_index=True)

        df.to_parquet(filepath, index=False, engine='pyarrow')

        # Clear buffer
        self.buffers[table_name] = []

    def _flush_all_buffers(self):
        for table_name in list(self.buffers.keys()):
            self._flush_buffer(table_name)

    def _close_all_writers(self):
        for writer in self.writers.values():
            writer.close()
        self.writers = {}

    def print_statistics(self):
        print("\n" + "="*60)
        print("DATA GENERATION STATISTICS")
        print("="*60)
        for key, value in self.stats.items():
            print(f"{key.capitalize():20s}: {value:,}")
        print("="*60 + "\n")

# Main execution


def main():
    # Small test dataset
    small_config = GeneratorConfig(
        num_accounts=100,
        num_instruments=50,
        num_firms=10,
        num_venues=3,
        num_days=7,
        orders_per_day=5000,
        trades_per_day=10000,
        batch_size=5000,
        write_frequency=10000,
        output_format='parquet',
        output_dir='./data/small_test'
    )

    # Mid-Small test dataset
    mid_small_config = GeneratorConfig(
        num_accounts=250,
        num_instruments=100,
        num_firms=10,
        num_venues=3,
        num_days=15,
        orders_per_day=50000,
        trades_per_day=7500,
        batch_size=5000,
        write_frequency=10000,
        output_format='parquet',
        output_dir='./data/mid_small_test'
    )

    # Medium dataset
    medium_config = GeneratorConfig(
        num_accounts=1000,
        num_instruments=500,
        num_firms=50,
        num_venues=5,
        num_days=30,
        orders_per_day=100000,
        trades_per_day=50000,
        batch_size=10000,
        write_frequency=50000,
        output_format='parquet',
        output_dir='./data/medium'
    )

    # Large production dataset
    large_config = GeneratorConfig(
        num_accounts=10000,
        num_instruments=2000,
        num_firms=200,
        num_venues=10,
        num_days=90,
        orders_per_day=1000000,
        trades_per_day=500000,
        batch_size=20000,
        write_frequency=100000,
        output_format='parquet',
        output_dir='./data/large_production'
    )

    # Select configuration
    # config = medium_config
    config = small_config
    # config = mid_small_config

    print("Starting optimized market data generation...")
    print(
        f"Configuration: {config.num_accounts} accounts, {config.num_instruments} instruments, {config.num_days} days")

    import time
    start_time = time.time()

    generator = OptimizedMarketDataGenerator(config)
    generator.generate_all()
    generator.print_statistics()

    elapsed_time = time.time() - start_time
    print(f"\nTotal generation time: {elapsed_time:.2f} seconds")
    print(
        f"Orders per second: {generator.stats['orders'] / elapsed_time:,.0f}")
    print(
        f"Trades per second: {generator.stats['trades'] / elapsed_time:,.0f}")

    print("\nGeneration complete!")


if __name__ == "__main__":
    main()
