# market_data_generator.py
# Realistic market surveillance test data generator

import random
import uuid
import json
import csv
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
import pandas as pd
from faker import Faker
import numpy as np

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

# Data Models


@dataclass
class Person:
    person_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    ssn: str
    date_of_birth: str


@dataclass
class Firm:
    firm_id: str
    firm_name: str
    lei_code: str
    address: str
    country: str
    firm_type: str


@dataclass
class Account:
    account_id: str
    beneficial_owner_id: str
    parent_account_id: Optional[str]
    firm_id: str
    account_type: str
    opening_date: str
    credit_limit: float
    ip_addresses: List[str]
    device_fingerprints: List[str]
    related_accounts: List[str]


@dataclass
class Instrument:
    instrument_id: str
    symbol: str
    isin: str
    security_type: str
    sector: str
    market_cap: float
    average_daily_volume: float
    tick_size: float
    lot_size: int
    price: float
    volatility: float
    issuer: str


@dataclass
class Order:
    order_id: str
    timestamp: str
    account_id: str
    trader_id: str
    firm_id: str
    instrument_id: str
    order_type: str
    side: str
    quantity: float
    displayed_quantity: float
    price: Optional[float]
    stop_price: Optional[float]
    time_in_force: str
    order_state: str
    venue_id: str
    algo_indicator: bool
    algo_id: Optional[str]
    parent_order_id: Optional[str]
    session_id: str


@dataclass
class Trade:
    trade_id: str
    timestamp: str
    instrument_id: str
    buy_order_id: str
    sell_order_id: str
    buy_account_id: str
    sell_account_id: str
    buy_firm_id: str
    sell_firm_id: str
    buy_trader_id: str
    sell_trader_id: str
    quantity: float
    price: float
    trade_value: float
    aggressor_side: str
    trade_type: str
    venue_id: str
    buy_capacity: str
    sell_capacity: str


@dataclass
class Cancellation:
    cancellation_id: str
    timestamp: str
    order_id: str
    account_id: str
    instrument_id: str
    remaining_quantity: float
    reason: str


@dataclass
class MarketData:
    timestamp: str
    instrument_id: str
    best_bid: float
    best_offer: float
    bid_size: float
    offer_size: float
    last_price: float
    volume: float


@dataclass
class CorporateEvent:
    event_id: str
    instrument_id: str
    event_type: str
    announcement_date: str
    effective_date: str
    materiality: str
    description: str

# Data Generator Class


class MarketDataGenerator:
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.persons: List[Person] = []
        self.firms: List[Firm] = []
        self.accounts: List[Account] = []
        self.instruments: List[Instrument] = []
        self.orders: List[Order] = []
        self.trades: List[Trade] = []
        self.cancellations: List[Cancellation] = []
        self.market_data: List[MarketData] = []
        self.corporate_events: List[CorporateEvent] = []
        self.account_relationships: Dict[str, List[str]] = {}
        self.insider_connections: Dict[str, List[str]] = {}
        self.start_date = datetime.now() - timedelta(days=config.num_days)

    def generate_all(self):
        print("Generating reference data...")
        self.generate_persons()
        self.generate_firms()
        self.generate_accounts()
        self.generate_instruments()
        self.generate_corporate_events()

        print("Generating market activity...")
        for day in range(self.config.num_days):
            current_date = self.start_date + timedelta(days=day)
            print(f"Generating data for {current_date.date()}...")
            self.generate_daily_activity(current_date)

        print("Data generation complete.")

    def generate_persons(self):
        for _ in range(self.config.num_accounts):
            person = Person(
                person_id=f"P{str(uuid.uuid4())[:8]}",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone=fake.phone_number(),
                address=fake.address().replace('\n', ', '),
                ssn=fake.ssn(),
                date_of_birth=fake.date_of_birth(
                    minimum_age=18, maximum_age=80).isoformat()
            )
            self.persons.append(person)

    def generate_firms(self):
        firm_types = ['broker_dealer', 'investment_bank',
                      'hedge_fund', 'asset_manager', 'proprietary_trading']
        for _ in range(self.config.num_firms):
            firm = Firm(
                firm_id=f"F{str(uuid.uuid4())[:8]}",
                firm_name=fake.company(),
                lei_code=''.join(random.choices(
                    '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=20)),
                address=fake.address().replace('\n', ', '),
                country=fake.country_code(),
                firm_type=random.choice(firm_types)
            )
            self.firms.append(firm)

    def generate_accounts(self):
        account_types = [t.value for t in AccountType]

        for i, person in enumerate(self.persons):
            firm = random.choice(self.firms)
            account = Account(
                account_id=f"A{str(uuid.uuid4())[:8]}",
                beneficial_owner_id=person.person_id,
                parent_account_id=None,
                firm_id=firm.firm_id,
                account_type=random.choice(account_types),
                opening_date=(
                    self.start_date - timedelta(days=random.randint(1, 1000))).isoformat(),
                credit_limit=random.uniform(10000, 10000000),
                ip_addresses=[fake.ipv4()
                              for _ in range(random.randint(1, 3))],
                device_fingerprints=[str(uuid.uuid4())
                                     for _ in range(random.randint(1, 2))],
                related_accounts=[]
            )
            self.accounts.append(account)

        # Create related accounts
        for account in self.accounts:
            if random.random() < self.config.related_account_probability:
                related_count = random.randint(1, 3)
                potential_related = [
                    a for a in self.accounts if a.account_id != account.account_id]
                related = random.sample(potential_related, min(
                    related_count, len(potential_related)))
                account.related_accounts = [a.account_id for a in related]

                # Store bidirectional relationships
                if account.account_id not in self.account_relationships:
                    self.account_relationships[account.account_id] = []
                self.account_relationships[account.account_id].extend(
                    account.related_accounts)

        # Create some sub-accounts
        num_sub_accounts = int(self.config.num_accounts * 0.1)
        for _ in range(num_sub_accounts):
            parent = random.choice(self.accounts)
            person = random.choice(self.persons)
            sub_account = Account(
                account_id=f"A{str(uuid.uuid4())[:8]}",
                beneficial_owner_id=parent.beneficial_owner_id,
                parent_account_id=parent.account_id,
                firm_id=parent.firm_id,
                account_type=parent.account_type,
                opening_date=(
                    self.start_date - timedelta(days=random.randint(1, 500))).isoformat(),
                credit_limit=parent.credit_limit * 0.5,
                ip_addresses=parent.ip_addresses,
                device_fingerprints=parent.device_fingerprints,
                related_accounts=[]
            )
            self.accounts.append(sub_account)

    def generate_instruments(self):
        sectors = ['Technology', 'Finance', 'Healthcare', 'Energy',
                   'Consumer', 'Industrial', 'Materials', 'Utilities']
        security_types = [t.value for t in SecurityType]

        for i in range(self.config.num_instruments):
            symbol = ''.join(random.choices(
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(3, 5)))
            security_type = random.choice(security_types)

            price = random.uniform(*self.config.base_price_range)
            volatility = random.uniform(*self.config.volatility_range)

            instrument = Instrument(
                instrument_id=f"I{str(uuid.uuid4())[:8]}",
                symbol=symbol,
                isin=''.join(random.choices(
                    '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=12)),
                security_type=security_type,
                sector=random.choice(sectors),
                market_cap=random.uniform(100e6, 500e9),
                average_daily_volume=random.uniform(100000, 50000000),
                tick_size=self.config.tick_size_default,
                lot_size=100,
                price=price,
                volatility=volatility,
                issuer=fake.company()
            )
            self.instruments.append(instrument)

        # Create some insider connections
        for instrument in self.instruments[:int(len(self.instruments) * 0.3)]:
            insiders = random.sample(self.persons, random.randint(3, 8))
            self.insider_connections[instrument.instrument_id] = [
                p.person_id for p in insiders]

    def generate_corporate_events(self):
        event_types = ['earnings', 'merger', 'acquisition', 'dividend',
                       'stock_split', 'IPO', 'secondary_offering', 'index_add', 'index_remove']
        materiality_levels = ['low', 'medium', 'high']

        for _ in range(int(self.config.num_instruments * 0.2)):
            instrument = random.choice(self.instruments)
            event_date = self.start_date + \
                timedelta(days=random.randint(0, self.config.num_days))

            event = CorporateEvent(
                event_id=f"E{str(uuid.uuid4())[:8]}",
                instrument_id=instrument.instrument_id,
                event_type=random.choice(event_types),
                announcement_date=(
                    event_date - timedelta(days=random.randint(1, 14))).isoformat(),
                effective_date=event_date.isoformat(),
                materiality=random.choice(materiality_levels),
                description=fake.sentence()
            )
            self.corporate_events.append(event)

    def generate_daily_activity(self, date: datetime):
        # Generate market data
        self.generate_market_data_for_day(date)

        # Generate orders and trades
        self.generate_orders_for_day(date)

        # Generate manipulative patterns if enabled
        if self.config.generate_manipulative_patterns:
            self.generate_layering_patterns(date)
            self.generate_wash_trading_patterns(date)
            self.generate_front_running_patterns(date)
            self.generate_insider_trading_patterns(date)
            self.generate_marking_close_patterns(date)
            self.generate_spoofing_patterns(date)

    def generate_market_data_for_day(self, date: datetime):
        # Generate snapshots every minute during market hours
        market_open = date.replace(
            hour=self.config.market_open_hour, minute=0, second=0)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)

        current_time = market_open
        while current_time <= market_close:
            for instrument in random.sample(self.instruments, int(len(self.instruments) * 0.1)):
                # Simulate price movement
                price_change = np.random.normal(
                    0, instrument.volatility * instrument.price)
                new_price = max(instrument.price + price_change,
                                instrument.tick_size)

                spread = instrument.tick_size * random.randint(1, 5)

                market_data = MarketData(
                    timestamp=current_time.isoformat(),
                    instrument_id=instrument.instrument_id,
                    best_bid=round(new_price - spread/2, 2),
                    best_offer=round(new_price + spread/2, 2),
                    bid_size=random.uniform(100, 10000),
                    offer_size=random.uniform(100, 10000),
                    last_price=new_price,
                    volume=random.uniform(1000, 100000)
                )
                self.market_data.append(market_data)

            current_time += timedelta(minutes=1)

    def generate_orders_for_day(self, date: datetime):
        market_open = date.replace(
            hour=self.config.market_open_hour, minute=0, second=0)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)

        for _ in range(self.config.orders_per_day):
            timestamp = self._random_market_time(market_open, market_close)
            account = random.choice(self.accounts)
            instrument = random.choice(self.instruments)
            order_type = random.choice([t.value for t in OrderType])
            side = random.choice([s.value for s in OrderSide])

            quantity = random.randint(1, 100) * 100
            displayed_quantity = quantity

            if order_type == OrderType.ICEBERG.value:
                displayed_quantity = quantity * random.uniform(0.1, 0.3)
            elif order_type == OrderType.HIDDEN.value:
                displayed_quantity = 0

            price = None
            if order_type in [OrderType.LIMIT.value, OrderType.STOP_LIMIT.value]:
                offset = random.uniform(-0.05, 0.05)
                price = round(instrument.price * (1 + offset), 2)

            stop_price = None
            if order_type in [OrderType.STOP.value, OrderType.STOP_LIMIT.value]:
                stop_price = round(instrument.price *
                                   random.uniform(0.95, 1.05), 2)

            order = Order(
                order_id=f"O{str(uuid.uuid4())[:12]}",
                timestamp=timestamp.isoformat(),
                account_id=account.account_id,
                trader_id=f"T{str(uuid.uuid4())[:8]}",
                firm_id=account.firm_id,
                instrument_id=instrument.instrument_id,
                order_type=order_type,
                side=side,
                quantity=quantity,
                displayed_quantity=displayed_quantity,
                price=price,
                stop_price=stop_price,
                time_in_force=random.choice(['day', 'gtc', 'ioc', 'fok']),
                order_state=OrderState.NEW.value,
                venue_id=f"V{random.randint(1, self.config.num_venues)}",
                algo_indicator=random.random() < 0.3,
                algo_id=f"ALG{random.randint(1, 20)}" if random.random(
                ) < 0.3 else None,
                parent_order_id=None,
                session_id=str(uuid.uuid4())
            )
            self.orders.append(order)

            # Generate potential execution
            if random.random() < 0.6:
                self.generate_trade_for_order(order, timestamp)

            # Generate potential cancellation
            if random.random() < self.config.cancellation_rate:
                self.generate_cancellation_for_order(order, timestamp)

    def generate_trade_for_order(self, order: Order, base_timestamp: datetime):
        # Find or create matching order
        opposite_side = OrderSide.SELL.value if order.side == OrderSide.BUY.value else OrderSide.BUY.value

        # Try to find existing opposite order
        matching_orders = [o for o in self.orders
                           if o.instrument_id == order.instrument_id
                           and o.side == opposite_side
                           and o.order_state == OrderState.NEW.value]

        if matching_orders and random.random() < 0.5:
            matching_order = random.choice(matching_orders)
        else:
            # Create synthetic matching order
            account = random.choice(self.accounts)
            matching_order = Order(
                order_id=f"O{str(uuid.uuid4())[:12]}",
                timestamp=(
                    base_timestamp - timedelta(milliseconds=random.randint(1, 1000))).isoformat(),
                account_id=account.account_id,
                trader_id=f"T{str(uuid.uuid4())[:8]}",
                firm_id=account.firm_id,
                instrument_id=order.instrument_id,
                order_type=order.order_type,
                side=opposite_side,
                quantity=order.quantity,
                displayed_quantity=order.displayed_quantity,
                price=order.price,
                stop_price=None,
                time_in_force='ioc',
                order_state=OrderState.NEW.value,
                venue_id=order.venue_id,
                algo_indicator=False,
                algo_id=None,
                parent_order_id=None,
                session_id=str(uuid.uuid4())
            )
            self.orders.append(matching_order)

        # Create trade
        exec_timestamp = base_timestamp + \
            timedelta(milliseconds=random.randint(10, 5000))
        quantity = min(order.quantity, matching_order.quantity) * \
            random.uniform(0.5, 1.0)

        instrument = next(
            i for i in self.instruments if i.instrument_id == order.instrument_id)
        trade_price = order.price if order.price else instrument.price

        buy_order = order if order.side == OrderSide.BUY.value else matching_order
        sell_order = matching_order if order.side == OrderSide.BUY.value else order

        trade = Trade(
            trade_id=f"T{str(uuid.uuid4())[:12]}",
            timestamp=exec_timestamp.isoformat(),
            instrument_id=order.instrument_id,
            buy_order_id=buy_order.order_id,
            sell_order_id=sell_order.order_id,
            buy_account_id=buy_order.account_id,
            sell_account_id=sell_order.account_id,
            buy_firm_id=buy_order.firm_id,
            sell_firm_id=sell_order.firm_id,
            buy_trader_id=buy_order.trader_id,
            sell_trader_id=sell_order.trader_id,
            quantity=quantity,
            price=trade_price,
            trade_value=quantity * trade_price,
            aggressor_side=order.side,
            trade_type=random.choice([t.value for t in TradeType]),
            venue_id=order.venue_id,
            buy_capacity=random.choice(
                ['principal', 'agency', 'riskless_principal', 'market_maker']),
            sell_capacity=random.choice(
                ['principal', 'agency', 'riskless_principal', 'market_maker'])
        )
        self.trades.append(trade)

        # Update order states
        if quantity >= order.quantity * 0.99:
            order.order_state = OrderState.FILLED.value
        else:
            order.order_state = OrderState.PARTIAL_FILL.value

    def generate_cancellation_for_order(self, order: Order, base_timestamp: datetime):
        if order.order_state not in [OrderState.NEW.value, OrderState.PARTIAL_FILL.value]:
            return

        cancel_timestamp = base_timestamp + \
            timedelta(milliseconds=random.randint(100, 60000))

        remaining = order.quantity
        if order.order_state == OrderState.PARTIAL_FILL.value:
            remaining *= random.uniform(0.3, 0.8)

        cancellation = Cancellation(
            cancellation_id=f"C{str(uuid.uuid4())[:12]}",
            timestamp=cancel_timestamp.isoformat(),
            order_id=order.order_id,
            account_id=order.account_id,
            instrument_id=order.instrument_id,
            remaining_quantity=remaining,
            reason=random.choice(
                ['user_cancel', 'timeout', 'risk_breach', 'end_of_day'])
        )
        self.cancellations.append(cancellation)
        order.order_state = OrderState.CANCELLED.value

    # Manipulative Pattern Generators

    def generate_layering_patterns(self, date: datetime):
        num_patterns = int(self.config.orders_per_day *
                           self.config.layering_probability)
        market_open = date.replace(
            hour=self.config.market_open_hour, minute=0, second=0)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)

        for _ in range(num_patterns):
            account = random.choice(self.accounts)
            instrument = random.choice(self.instruments)
            side = random.choice([OrderSide.BUY, OrderSide.SELL])

            base_time = self._random_market_time(market_open, market_close)

            # Create layer orders
            layer_orders = []
            for i in range(random.randint(3, 8)):
                offset = (i + 2) * instrument.tick_size
                price = instrument.price + \
                    offset if side == OrderSide.SELL else instrument.price - offset

                order_time = base_time + \
                    timedelta(milliseconds=i * random.randint(100, 500))

                layer_order = Order(
                    order_id=f"O{str(uuid.uuid4())[:12]}",
                    timestamp=order_time.isoformat(),
                    account_id=account.account_id,
                    trader_id=f"T{str(uuid.uuid4())[:8]}",
                    firm_id=account.firm_id,
                    instrument_id=instrument.instrument_id,
                    order_type=OrderType.LIMIT.value,
                    side=side.value,
                    quantity=random.randint(5, 20) * 100,
                    displayed_quantity=random.randint(5, 20) * 100,
                    price=round(price, 2),
                    stop_price=None,
                    time_in_force='day',
                    order_state=OrderState.NEW.value,
                    venue_id=f"V{random.randint(1, self.config.num_venues)}",
                    algo_indicator=False,
                    algo_id=None,
                    parent_order_id=None,
                    session_id=str(uuid.uuid4())
                )
                layer_orders.append(layer_order)
                self.orders.append(layer_order)

            # Create opposite execution
            exec_time = base_time + timedelta(seconds=random.randint(10, 50))
            opposite_side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY

            exec_order = Order(
                order_id=f"O{str(uuid.uuid4())[:12]}",
                timestamp=exec_time.isoformat(),
                account_id=account.account_id,
                trader_id=f"T{str(uuid.uuid4())[:8]}",
                firm_id=account.firm_id,
                instrument_id=instrument.instrument_id,
                order_type=OrderType.MARKET.value,
                side=opposite_side.value,
                quantity=random.randint(1, 5) * 100,
                displayed_quantity=random.randint(1, 5) * 100,
                price=None,
                stop_price=None,
                time_in_force='ioc',
                order_state=OrderState.NEW.value,
                venue_id=layer_orders[0].venue_id,
                algo_indicator=False,
                algo_id=None,
                parent_order_id=None,
                session_id=str(uuid.uuid4())
            )
            self.orders.append(exec_order)
            self.generate_trade_for_order(exec_order, exec_time)

            # Cancel layer orders
            cancel_time = exec_time + timedelta(seconds=random.randint(5, 60))
            for layer_order in layer_orders:
                if random.random() < 0.9:
                    self.generate_cancellation_for_order(
                        layer_order, cancel_time)

    def generate_wash_trading_patterns(self, date: datetime):
        num_patterns = int(self.config.trades_per_day *
                           self.config.wash_trading_probability)
        market_open = date.replace(
            hour=self.config.market_open_hour, minute=0, second=0)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)

        for _ in range(num_patterns):
            # Find related accounts
            account1 = random.choice(self.accounts)

            # Use related account or create one with same beneficial owner
            if account1.related_accounts and random.random() < 0.7:
                account2_id = random.choice(account1.related_accounts)
                account2 = next(
                    (a for a in self.accounts if a.account_id == account2_id), None)
                if not account2:
                    continue
            else:
                # Find or create account with same beneficial owner
                same_owner_accounts = [a for a in self.accounts
                                       if a.beneficial_owner_id == account1.beneficial_owner_id
                                       and a.account_id != account1.account_id]
                if same_owner_accounts:
                    account2 = random.choice(same_owner_accounts)
                else:
                    continue

            instrument = random.choice(self.instruments)

            # Generate wash trades
            for _ in range(random.randint(3, 15)):
                trade_time = self._random_market_time(
                    market_open, market_close)
                quantity = random.randint(1, 10) * 100
                price = round(instrument.price *
                              random.uniform(0.999, 1.001), 2)

                # Create buy order
                buy_order = Order(
                    order_id=f"O{str(uuid.uuid4())[:12]}",
                    timestamp=trade_time.isoformat(),
                    account_id=account1.account_id,
                    trader_id=f"T{str(uuid.uuid4())[:8]}",
                    firm_id=account1.firm_id,
                    instrument_id=instrument.instrument_id,
                    order_type=OrderType.LIMIT.value,
                    side=OrderSide.BUY.value,
                    quantity=quantity,
                    displayed_quantity=quantity,
                    price=price,
                    stop_price=None,
                    time_in_force='ioc',
                    order_state=OrderState.FILLED.value,
                    venue_id=f"V{random.randint(1, self.config.num_venues)}",
                    algo_indicator=False,
                    algo_id=None,
                    parent_order_id=None,
                    session_id=str(uuid.uuid4())
                )
                self.orders.append(buy_order)

                # Create sell order
                sell_order = Order(
                    order_id=f"O{str(uuid.uuid4())[:12]}",
                    timestamp=(
                        trade_time + timedelta(milliseconds=random.randint(1, 100))).isoformat(),
                    account_id=account2.account_id,
                    trader_id=f"T{str(uuid.uuid4())[:8]}",
                    firm_id=account2.firm_id,
                    instrument_id=instrument.instrument_id,
                    order_type=OrderType.LIMIT.value,
                    side=OrderSide.SELL.value,
                    quantity=quantity,
                    displayed_quantity=quantity,
                    price=price,
                    stop_price=None,
                    time_in_force='ioc',
                    order_state=OrderState.FILLED.value,
                    venue_id=buy_order.venue_id,
                    algo_indicator=False,
                    algo_id=None,
                    parent_order_id=None,
                    session_id=str(uuid.uuid4())
                )
                self.orders.append(sell_order)

                # Create wash trade
                wash_trade = Trade(
                    trade_id=f"T{str(uuid.uuid4())[:12]}",
                    timestamp=(
                        trade_time + timedelta(milliseconds=random.randint(10, 200))).isoformat(),
                    instrument_id=instrument.instrument_id,
                    buy_order_id=buy_order.order_id,
                    sell_order_id=sell_order.order_id,
                    buy_account_id=account1.account_id,
                    sell_account_id=account2.account_id,
                    buy_firm_id=account1.firm_id,
                    sell_firm_id=account2.firm_id,
                    buy_trader_id=buy_order.trader_id,
                    sell_trader_id=sell_order.trader_id,
                    quantity=quantity,
                    price=price,
                    trade_value=quantity * price,
                    aggressor_side=OrderSide.BUY.value,
                    trade_type=TradeType.REGULAR.value,
                    venue_id=buy_order.venue_id,
                    buy_capacity='principal',
                    sell_capacity='principal'
                )
                self.trades.append(wash_trade)

    def generate_front_running_patterns(self, date: datetime):
        num_patterns = int(self.config.orders_per_day *
                           self.config.front_running_probability)
        market_open = date.replace(
            hour=self.config.market_open_hour, minute=0, second=0)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)

        for _ in range(num_patterns):
            firm = random.choice(self.firms)

            # Find proprietary and customer accounts in same firm
            prop_accounts = [a for a in self.accounts
                             if a.firm_id == firm.firm_id
                             and a.account_type == AccountType.PROPRIETARY.value]
            cust_accounts = [a for a in self.accounts
                             if a.firm_id == firm.firm_id
                             and a.account_type in [AccountType.RETAIL.value, AccountType.INSTITUTIONAL.value]]

            if not prop_accounts or not cust_accounts:
                continue

            prop_account = random.choice(prop_accounts)
            cust_account = random.choice(cust_accounts)
            instrument = random.choice(self.instruments)
            side = random.choice([OrderSide.BUY, OrderSide.SELL])

            base_time = self._random_market_time(market_open, market_close)

            # Proprietary order first
            prop_order = Order(
                order_id=f"O{str(uuid.uuid4())[:12]}",
                timestamp=base_time.isoformat(),
                account_id=prop_account.account_id,
                trader_id=f"T{str(uuid.uuid4())[:8]}",
                firm_id=firm.firm_id,
                instrument_id=instrument.instrument_id,
                order_type=OrderType.LIMIT.value,
                side=side.value,
                quantity=random.randint(1, 5) * 100,
                displayed_quantity=random.randint(1, 5) * 100,
                price=round(instrument.price *
                            random.uniform(0.999, 1.001), 2),
                stop_price=None,
                time_in_force='day',
                order_state=OrderState.NEW.value,
                venue_id=f"V{random.randint(1, self.config.num_venues)}",
                algo_indicator=False,
                algo_id=None,
                parent_order_id=None,
                session_id=str(uuid.uuid4())
            )
            self.orders.append(prop_order)

            # Customer order follows
            cust_time = base_time + timedelta(seconds=random.randint(5, 45))
            cust_order = Order(
                order_id=f"O{str(uuid.uuid4())[:12]}",
                timestamp=cust_time.isoformat(),
                account_id=cust_account.account_id,
                trader_id=f"T{str(uuid.uuid4())[:8]}",
                firm_id=firm.firm_id,
                instrument_id=instrument.instrument_id,
                order_type=OrderType.MARKET.value,
                side=side.value,
                quantity=prop_order.quantity * random.randint(10, 50),
                displayed_quantity=prop_order.quantity *
                random.randint(10, 50),
                price=None,
                stop_price=None,
                time_in_force='day',
                order_state=OrderState.NEW.value,
                venue_id=prop_order.venue_id,
                algo_indicator=False,
                algo_id=None,
                parent_order_id=None,
                session_id=str(uuid.uuid4())
            )
            self.orders.append(cust_order)

            # Execute proprietary order first
            prop_exec_time = cust_time + \
                timedelta(seconds=random.randint(1, 10))
            self.generate_trade_for_order(prop_order, prop_exec_time)

            # Execute customer order
            cust_exec_time = prop_exec_time + \
                timedelta(seconds=random.randint(1, 30))
            self.generate_trade_for_order(cust_order, cust_exec_time)

    def generate_insider_trading_patterns(self, date: datetime):
        # Find corporate events in near future
        upcoming_events = [e for e in self.corporate_events
                           if datetime.fromisoformat(e.announcement_date) > date
                           and datetime.fromisoformat(e.announcement_date) <= date + timedelta(days=7)
                           and e.materiality in ['medium', 'high']]

        if not upcoming_events:
            return

        for event in random.sample(upcoming_events, min(len(upcoming_events),
                                                        int(self.config.orders_per_day * self.config.insider_trading_probability))):
            if event.instrument_id not in self.insider_connections:
                continue

            # Select insider
            insider_person_id = random.choice(
                self.insider_connections[event.instrument_id])
            insider_accounts = [
                a for a in self.accounts if a.beneficial_owner_id == insider_person_id]

            if not insider_accounts:
                continue

            insider_account = random.choice(insider_accounts)
            instrument = next(
                i for i in self.instruments if i.instrument_id == event.instrument_id)

            # Generate unusual trading 1-5 days before announcement
            days_before = random.randint(1, 5)
            trade_date = datetime.fromisoformat(
                event.announcement_date) - timedelta(days=days_before)

            if trade_date < date or trade_date > date + timedelta(days=1):
                continue

            market_open = trade_date.replace(
                hour=self.config.market_open_hour, minute=0, second=0)
            market_close = trade_date.replace(
                hour=self.config.market_close_hour, minute=0, second=0)

            # Determine direction based on event type
            if event.event_type in ['merger', 'acquisition', 'positive_earnings']:
                side = OrderSide.BUY
            elif event.event_type in ['negative_earnings', 'investigation']:
                side = OrderSide.SELL
            else:
                side = random.choice([OrderSide.BUY, OrderSide.SELL])

            # Generate multiple trades with unusually large volume
            num_trades = random.randint(5, 15)
            for _ in range(num_trades):
                trade_time = self._random_market_time(
                    market_open, market_close)

                # Unusually large quantity
                quantity = random.randint(50, 200) * 100

                order = Order(
                    order_id=f"O{str(uuid.uuid4())[:12]}",
                    timestamp=trade_time.isoformat(),
                    account_id=insider_account.account_id,
                    trader_id=f"T{str(uuid.uuid4())[:8]}",
                    firm_id=insider_account.firm_id,
                    instrument_id=instrument.instrument_id,
                    order_type=random.choice(
                        [OrderType.MARKET.value, OrderType.LIMIT.value]),
                    side=side.value,
                    quantity=quantity,
                    displayed_quantity=quantity,
                    price=round(instrument.price * random.uniform(0.995,
                                1.005), 2) if random.random() < 0.5 else None,
                    stop_price=None,
                    time_in_force='day',
                    order_state=OrderState.NEW.value,
                    venue_id=f"V{random.randint(1, self.config.num_venues)}",
                    algo_indicator=False,
                    algo_id=None,
                    parent_order_id=None,
                    session_id=str(uuid.uuid4())
                )
                self.orders.append(order)
                self.generate_trade_for_order(order, trade_time)

    def generate_marking_close_patterns(self, date: datetime):
        num_patterns = int(self.config.num_instruments *
                           self.config.marking_close_probability)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)

        for _ in range(num_patterns):
            account = random.choice(self.accounts)
            instrument = random.choice(self.instruments)
            side = random.choice([OrderSide.BUY, OrderSide.SELL])

            # Generate aggressive orders in last 5 minutes
            close_window_start = market_close - timedelta(minutes=5)

            for _ in range(random.randint(5, 15)):
                trade_time = self._random_market_time(
                    close_window_start, market_close)

                order = Order(
                    order_id=f"O{str(uuid.uuid4())[:12]}",
                    timestamp=trade_time.isoformat(),
                    account_id=account.account_id,
                    trader_id=f"T{str(uuid.uuid4())[:8]}",
                    firm_id=account.firm_id,
                    instrument_id=instrument.instrument_id,
                    order_type=OrderType.MARKET.value,
                    side=side.value,
                    quantity=random.randint(10, 50) * 100,
                    displayed_quantity=random.randint(10, 50) * 100,
                    price=None,
                    stop_price=None,
                    time_in_force='ioc',
                    order_state=OrderState.NEW.value,
                    venue_id=f"V{random.randint(1, self.config.num_venues)}",
                    algo_indicator=False,
                    algo_id=None,
                    parent_order_id=None,
                    session_id=str(uuid.uuid4())
                )
                self.orders.append(order)
                self.generate_trade_for_order(order, trade_time)

    def generate_spoofing_patterns(self, date: datetime):
        num_patterns = int(self.config.orders_per_day * 0.005)
        market_open = date.replace(
            hour=self.config.market_open_hour, minute=0, second=0)
        market_close = date.replace(
            hour=self.config.market_close_hour, minute=0, second=0)

        for _ in range(num_patterns):
            account = random.choice(self.accounts)
            instrument = random.choice(self.instruments)
            side = random.choice([OrderSide.BUY, OrderSide.SELL])

            base_time = self._random_market_time(market_open, market_close)

            # Large anchor order
            anchor_quantity = random.randint(100, 500) * 100
            anchor_price = instrument.price + \
                (instrument.tick_size * random.randint(1, 5)
                 * (1 if side == OrderSide.SELL else -1))

            anchor_order = Order(
                order_id=f"O{str(uuid.uuid4())[:12]}",
                timestamp=base_time.isoformat(),
                account_id=account.account_id,
                trader_id=f"T{str(uuid.uuid4())[:8]}",
                firm_id=account.firm_id,
                instrument_id=instrument.instrument_id,
                order_type=OrderType.LIMIT.value,
                side=side.value,
                quantity=anchor_quantity,
                displayed_quantity=anchor_quantity,
                price=round(anchor_price, 2),
                stop_price=None,
                time_in_force='day',
                order_state=OrderState.NEW.value,
                venue_id=f"V{random.randint(1, self.config.num_venues)}",
                algo_indicator=False,
                algo_id=None,
                parent_order_id=None,
                session_id=str(uuid.uuid4())
            )
            self.orders.append(anchor_order)

            # Small executions same side
            for _ in range(random.randint(2, 5)):
                exec_time = base_time + \
                    timedelta(seconds=random.randint(5, 20))
                small_order = Order(
                    order_id=f"O{str(uuid.uuid4())[:12]}",
                    timestamp=exec_time.isoformat(),
                    account_id=account.account_id,
                    trader_id=anchor_order.trader_id,
                    firm_id=account.firm_id,
                    instrument_id=instrument.instrument_id,
                    order_type=OrderType.MARKET.value,
                    side=side.value,
                    quantity=random.randint(1, 5) * 100,
                    displayed_quantity=random.randint(1, 5) * 100,
                    price=None,
                    stop_price=None,
                    time_in_force='ioc',
                    order_state=OrderState.NEW.value,
                    venue_id=anchor_order.venue_id,
                    algo_indicator=False,
                    algo_id=None,
                    parent_order_id=None,
                    session_id=str(uuid.uuid4())
                )
                self.orders.append(small_order)
                self.generate_trade_for_order(small_order, exec_time)

            # Cancel anchor
            cancel_time = base_time + timedelta(seconds=random.randint(30, 50))
            self.generate_cancellation_for_order(anchor_order, cancel_time)

    def _random_market_time(self, start: datetime, end: datetime) -> datetime:
        delta = end - start
        random_seconds = random.randint(0, int(delta.total_seconds()))
        return start + timedelta(seconds=random_seconds)

    # Data Export

    def save_data(self):
        import os
        os.makedirs(self.config.output_dir, exist_ok=True)

        if self.config.output_format == 'json':
            self._save_json()
        elif self.config.output_format == 'csv':
            self._save_csv()
        elif self.config.output_format == 'parquet':
            self._save_parquet()
        else:
            raise ValueError(
                f"Unsupported output format: {self.config.output_format}")

        print(f"Data saved to {self.config.output_dir}")

    def _save_json(self):
        datasets = {
            'persons': self.persons,
            'firms': self.firms,
            'accounts': self.accounts,
            'instruments': self.instruments,
            'orders': self.orders,
            'trades': self.trades,
            'cancellations': self.cancellations,
            'market_data': self.market_data,
            'corporate_events': self.corporate_events
        }

        for name, data in datasets.items():
            filepath = f"{self.config.output_dir}/{name}.json"
            with open(filepath, 'w') as f:
                json.dump([asdict(item) for item in data], f, indent=2)

    def _save_csv(self):
        datasets = {
            'persons': self.persons,
            'firms': self.firms,
            'accounts': self.accounts,
            'instruments': self.instruments,
            'orders': self.orders,
            'trades': self.trades,
            'cancellations': self.cancellations,
            'market_data': self.market_data,
            'corporate_events': self.corporate_events
        }

        for name, data in datasets.items():
            if not data:
                continue
            filepath = f"{self.config.output_dir}/{name}.csv"
            df = pd.DataFrame([asdict(item) for item in data])
            df.to_csv(filepath, index=False)

    def _save_parquet(self):
        datasets = {
            'persons': self.persons,
            'firms': self.firms,
            'accounts': self.accounts,
            'instruments': self.instruments,
            'orders': self.orders,
            'trades': self.trades,
            'cancellations': self.cancellations,
            'market_data': self.market_data,
            'corporate_events': self.corporate_events
        }

        for name, data in datasets.items():
            if not data:
                continue
            filepath = f"{self.config.output_dir}/{name}.parquet"
            df = pd.DataFrame([asdict(item) for item in data])

            # Handle list columns for parquet
            for col in df.columns:
                if isinstance(df[col].iloc[0], list):
                    df[col] = df[col].apply(
                        lambda x: json.dumps(x) if x else None)

            df.to_parquet(filepath, index=False, engine='pyarrow')

    def print_statistics(self):
        print("\n" + "="*60)
        print("DATA GENERATION STATISTICS")
        print("="*60)
        print(f"Persons:         {len(self.persons):,}")
        print(f"Firms:           {len(self.firms):,}")
        print(f"Accounts:        {len(self.accounts):,}")
        print(f"Instruments:     {len(self.instruments):,}")
        print(f"Orders:          {len(self.orders):,}")
        print(f"Trades:          {len(self.trades):,}")
        print(f"Cancellations:   {len(self.cancellations):,}")
        print(f"Market Data:     {len(self.market_data):,}")
        print(f"Corporate Events:{len(self.corporate_events):,}")
        print("="*60)

        # Calculate some statistics
        if self.trades:
            total_value = sum(t.trade_value for t in self.trades)
            print(f"\nTotal Trade Value: ${total_value:,.2f}")

        if self.orders:
            filled_orders = len(
                [o for o in self.orders if o.order_state == OrderState.FILLED.value])
            cancelled_orders = len(
                [o for o in self.orders if o.order_state == OrderState.CANCELLED.value])
            print(
                f"Fill Rate:         {filled_orders/len(self.orders)*100:.2f}%")
            print(
                f"Cancel Rate:       {cancelled_orders/len(self.orders)*100:.2f}%")

        print("="*60 + "\n")

# Main execution


def main():
    # Example configurations for different scenarios

    # Small test dataset
    small_config = GeneratorConfig(
        num_accounts=100,
        num_instruments=50,
        num_firms=10,
        num_venues=3,
        num_days=5,
        orders_per_day=10000,
        trades_per_day=5000,
        output_format='parquet',
        output_dir='./data/small_test'
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
        output_format='parquet',
        output_dir='./data/large_production'
    )

    # Select configuration
    config = medium_config

    print("Starting market data generation...")
    print(
        f"Configuration: {config.num_accounts} accounts, {config.num_instruments} instruments, {config.num_days} days")

    generator = MarketDataGenerator(config)
    generator.generate_all()
    generator.save_data()
    generator.print_statistics()

    print("Generation complete!")


if __name__ == "__main__":
    main()
