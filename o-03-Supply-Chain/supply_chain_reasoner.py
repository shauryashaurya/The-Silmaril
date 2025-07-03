#!/usr/bin/env python3
"""
Supply Chain Ontology Reasoner
==============================

Core reasoning engine for supply chain ontology with business rule implementation.
Handles data loading, entity modeling, and intelligent automation capabilities.

Author: Advanced Supply Chain Analytics System
"""

import pandas as pd
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Union, Any
from datetime import datetime, timedelta
import re
import math
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Data location configuration
DATA_LOCATION = './data'


def normalize_id(value: Any) -> str:
    """Normalize ID values to prevent foreign key mismatches."""
    if pd.isna(value) or value is None:
        return ""
    try:
        return str(int(float(value)))
    except (ValueError, TypeError):
        return str(value).strip()


def parse_id_list(id_string: str) -> List[str]:
    """Parse comma-separated ID lists and normalize each ID."""
    if not id_string or pd.isna(id_string):
        return []
    return [normalize_id(id_val.strip()) for id_val in str(id_string).split(',') if id_val.strip()]

# ===== ENTITY DATA MODELS =====


@dataclass
class Supplier:
    """Supplier entity with performance metrics and relationships."""
    id: str
    supplier_name: str
    supplier_location: str
    rating: float
    manufacturer_ids: List[str] = field(default_factory=list)

    # Derived properties (populated by reasoning)
    is_preferred: bool = False
    is_critical: bool = False
    lead_time: int = 30  # Default lead time in days
    on_time_delivery_rate: float = 85.0  # Default percentage
    risk_level: str = "MEDIUM"


@dataclass
class Manufacturer:
    """Manufacturer entity with production capabilities."""
    id: str
    manufacturer_name: str
    manufacturer_location: str
    manufacturing_capacity: int
    product_ids: List[str] = field(default_factory=list)

    # Derived properties
    is_high_volume: bool = False
    supplier_ids: List[str] = field(
        default_factory=list)  # Inverse relationship


@dataclass
class Warehouse:
    """Warehouse entity with storage and distribution capabilities."""
    id: str
    warehouse_name: str
    warehouse_location: str
    storage_capacity: int
    product_ids: List[str] = field(default_factory=list)

    # Derived properties
    is_overcapacity: bool = False
    capacity_utilization: float = 0.0
    service_level_agreement: str = "STANDARD"


@dataclass
class Retailer:
    """Retailer entity with customer classification."""
    id: str
    retailer_name: str
    retailer_location: str
    retailer_type: str

    # Derived properties
    is_premium: bool = False
    total_order_value: float = 0.0
    average_order_size: float = 0.0


@dataclass
class Product:
    """Product entity with inventory and performance metrics."""
    id: str
    product_name: str
    sku: str
    product_type: str
    unit_price: float

    # Derived properties
    current_inventory_level: int = 100  # Default inventory
    reorder_point: int = 20  # Default reorder point
    turnover_rate: float = 2.0  # Default monthly turnover
    is_fast_moving: bool = False
    is_slow_moving: bool = False
    is_low_stock: bool = False
    requires_quality_check: bool = False
    demand_multiplier: float = 1.0

    # Relationships
    manufacturer_id: str = ""
    warehouse_ids: List[str] = field(default_factory=list)


@dataclass
class Order:
    """Order entity with processing status and financial details."""
    id: str
    order_number: str
    order_date: datetime
    order_status: str
    total_amount: float
    seller_type: str  # "warehouse" or "manufacturer"
    seller_id: str
    retailer_id: str
    product_ids: List[str] = field(default_factory=list)

    # Derived properties
    is_urgent: bool = False
    is_large: bool = False
    discount_amount: float = 0.0
    final_amount: float = 0.0
    shipping_optimization: str = "STANDARD"


@dataclass
class Shipment:
    """Shipment entity with tracking and delivery information."""
    id: str
    shipment_id: str
    ship_date: datetime
    carrier: str
    tracking_number: str
    order_id: str
    shipper_id: str

    # Derived properties
    expected_delivery_date: Optional[datetime] = None
    is_delayed: bool = False


@dataclass
class Invoice:
    """Invoice entity - placeholder for future implementation."""
    id: str
    # Note: Invoice data not available in CSV files
    # Implementation deferred per requirements


class SupplyChainReasoner:
    """
    Core reasoning engine for supply chain ontology.

    Handles data loading, relationship validation, and business rule application.
    """

    def __init__(self, data_location: str = DATA_LOCATION):
        """Initialize the reasoner with data location."""
        self.data_location = Path(data_location)

        # Entity collections
        self.suppliers: Dict[str, Supplier] = {}
        self.manufacturers: Dict[str, Manufacturer] = {}
        self.warehouses: Dict[str, Warehouse] = {}
        self.retailers: Dict[str, Retailer] = {}
        self.products: Dict[str, Product] = {}
        self.orders: Dict[str, Order] = {}
        self.shipments: Dict[str, Shipment] = {}
        self.invoices: Dict[str, Invoice] = {}  # Placeholder

        # Reasoning results
        self.classification_results: Dict[str, Set[str]] = {
            'preferred_suppliers': set(),
            'critical_suppliers': set(),
            'high_volume_manufacturers': set(),
            'overcapacity_warehouses': set(),
            'premium_customers': set(),
            'urgent_orders': set(),
            'large_orders': set(),
            'delayed_shipments': set(),
            'fast_moving_products': set(),
            'slow_moving_products': set(),
            'low_stock_products': set()
        }

        self.relationship_mappings: Dict[str, Any] = {}
        self.statistics: Dict[str, Any] = {}

    def load_all_data(self) -> None:
        """Load all CSV data files and establish relationships."""
        logger.info("Starting data loading process...")

        try:
            self._load_suppliers()
            self._load_manufacturers()
            self._load_warehouses()
            self._load_retailers()
            self._load_products()
            self._load_orders()
            self._load_shipments()
            self._establish_relationships()
            self._validate_data_integrity()

            logger.info("Data loading completed successfully")

        except Exception as e:
            logger.error(f"Error during data loading: {e}")
            raise

    def _load_suppliers(self) -> None:
        """Load supplier data from CSV."""
        file_path = self.data_location / 'suppliers.csv'
        logger.info(f"Loading suppliers from {file_path}")

        df = pd.read_csv(file_path)
        df['id'] = df['id'].astype(int).astype(str)

        for row in df.itertuples(index=False, name=None):
            supplier_id, name, location, rating, manufacturer_ids = row

            supplier = Supplier(
                id=normalize_id(supplier_id),
                supplier_name=str(name),
                supplier_location=str(location),
                rating=float(rating),
                manufacturer_ids=parse_id_list(manufacturer_ids)
            )

            self.suppliers[supplier.id] = supplier

        logger.info(f"Loaded {len(self.suppliers)} suppliers")

    def _load_manufacturers(self) -> None:
        """Load manufacturer data from CSV."""
        file_path = self.data_location / 'manufacturers.csv'
        logger.info(f"Loading manufacturers from {file_path}")

        df = pd.read_csv(file_path)
        df['id'] = df['id'].astype(int).astype(str)

        for row in df.itertuples(index=False, name=None):
            mfg_id, name, location, capacity, product_ids = row

            manufacturer = Manufacturer(
                id=normalize_id(mfg_id),
                manufacturer_name=str(name),
                manufacturer_location=str(location),
                manufacturing_capacity=int(capacity),
                product_ids=parse_id_list(product_ids)
            )

            self.manufacturers[manufacturer.id] = manufacturer

        logger.info(f"Loaded {len(self.manufacturers)} manufacturers")

    def _load_warehouses(self) -> None:
        """Load warehouse data from CSV."""
        file_path = self.data_location / 'warehouses.csv'
        logger.info(f"Loading warehouses from {file_path}")

        df = pd.read_csv(file_path)
        df['id'] = df['id'].astype(int).astype(str)

        for row in df.itertuples(index=False, name=None):
            wh_id, name, location, capacity, product_ids = row

            warehouse = Warehouse(
                id=normalize_id(wh_id),
                warehouse_name=str(name),
                warehouse_location=str(location),
                storage_capacity=int(capacity),
                product_ids=parse_id_list(product_ids)
            )

            self.warehouses[warehouse.id] = warehouse

        logger.info(f"Loaded {len(self.warehouses)} warehouses")

    def _load_retailers(self) -> None:
        """Load retailer data from CSV."""
        file_path = self.data_location / 'retailers.csv'
        logger.info(f"Loading retailers from {file_path}")

        df = pd.read_csv(file_path)
        df['id'] = df['id'].astype(int).astype(str)

        for row in df.itertuples(index=False, name=None):
            retailer_id, name, location, retailer_type = row

            retailer = Retailer(
                id=normalize_id(retailer_id),
                retailer_name=str(name),
                retailer_location=str(location),
                retailer_type=str(retailer_type)
            )

            self.retailers[retailer.id] = retailer

        logger.info(f"Loaded {len(self.retailers)} retailers")

    def _load_products(self) -> None:
        """Load product data from CSV."""
        file_path = self.data_location / 'products.csv'
        logger.info(f"Loading products from {file_path}")

        df = pd.read_csv(file_path)
        df['id'] = df['id'].astype(int).astype(str)

        for row in df.itertuples(index=False, name=None):
            product_id, name, sku, product_type, unit_price = row

            product = Product(
                id=normalize_id(product_id),
                product_name=str(name),
                sku=str(sku),
                product_type=str(product_type),
                unit_price=float(unit_price)
            )

            self.products[product.id] = product

        logger.info(f"Loaded {len(self.products)} products")

    def _load_orders(self) -> None:
        """Load order data from CSV."""
        file_path = self.data_location / 'orders.csv'
        logger.info(f"Loading orders from {file_path}")

        df = pd.read_csv(file_path)
        df['id'] = df['id'].astype(int).astype(str)
        df['sellerID'] = df['sellerID'].astype(int).astype(str)
        df['retailerID'] = df['retailerID'].astype(int).astype(str)

        for row in df.itertuples(index=False, name=None):
            order_id, order_number, order_date, status, total_amount, seller_type, seller_id, retailer_id, product_ids = row

            # Parse order date
            try:
                parsed_date = pd.to_datetime(order_date).to_pydatetime()
            except:
                parsed_date = datetime.now()

            order = Order(
                id=normalize_id(order_id),
                order_number=str(order_number),
                order_date=parsed_date,
                order_status=str(status),
                total_amount=float(total_amount),
                seller_type=str(seller_type).lower(),
                seller_id=normalize_id(seller_id),
                retailer_id=normalize_id(retailer_id),
                product_ids=parse_id_list(product_ids)
            )

            self.orders[order.id] = order

        logger.info(f"Loaded {len(self.orders)} orders")

    def _load_shipments(self) -> None:
        """Load shipment data from CSV."""
        file_path = self.data_location / 'shipments.csv'
        logger.info(f"Loading shipments from {file_path}")

        df = pd.read_csv(file_path)
        df['id'] = df['id'].astype(int).astype(str)
        df['orderID'] = df['orderID'].astype(int).astype(str)
        df['shipperID'] = df['shipperID'].astype(int).astype(str)

        for row in df.itertuples(index=False, name=None):
            ship_id, shipment_id, ship_date, carrier, tracking_number, order_id, shipper_id = row

            # Parse ship date
            try:
                parsed_date = pd.to_datetime(ship_date).to_pydatetime()
            except:
                parsed_date = datetime.now()

            shipment = Shipment(
                id=normalize_id(ship_id),
                shipment_id=str(shipment_id),
                ship_date=parsed_date,
                carrier=str(carrier),
                tracking_number=str(tracking_number),
                order_id=normalize_id(order_id),
                shipper_id=normalize_id(shipper_id)
            )

            self.shipments[shipment.id] = shipment

        logger.info(f"Loaded {len(self.shipments)} shipments")

    def _establish_relationships(self) -> None:
        """Establish bidirectional relationships between entities."""
        logger.info("Establishing entity relationships...")

        # Supplier-Manufacturer relationships
        for supplier in self.suppliers.values():
            for mfg_id in supplier.manufacturer_ids:
                if mfg_id in self.manufacturers:
                    self.manufacturers[mfg_id].supplier_ids.append(supplier.id)

        # Product-Manufacturer relationships
        for manufacturer in self.manufacturers.values():
            for product_id in manufacturer.product_ids:
                if product_id in self.products:
                    self.products[product_id].manufacturer_id = manufacturer.id

        # Product-Warehouse relationships
        for warehouse in self.warehouses.values():
            for product_id in warehouse.product_ids:
                if product_id in self.products:
                    self.products[product_id].warehouse_ids.append(
                        warehouse.id)

        logger.info("Relationships established")

    def _validate_data_integrity(self) -> None:
        """Validate data integrity and foreign key relationships."""
        logger.info("Validating data integrity...")

        # Check supplier-manufacturer relationships
        orphaned_suppliers = 0
        for supplier in self.suppliers.values():
            valid_manufacturers = [
                mid for mid in supplier.manufacturer_ids if mid in self.manufacturers]
            if len(valid_manufacturers) != len(supplier.manufacturer_ids):
                orphaned_suppliers += 1

        # Check order-retailer relationships
        orphaned_orders = 0
        for order in self.orders.values():
            if order.retailer_id not in self.retailers:
                orphaned_orders += 1

        # Check shipment-order relationships
        orphaned_shipments = 0
        for shipment in self.shipments.values():
            if shipment.order_id not in self.orders:
                orphaned_shipments += 1

        logger.info(f"Data integrity check - Orphaned suppliers: {orphaned_suppliers}, "
                    f"orders: {orphaned_orders}, shipments: {orphaned_shipments}")

        if orphaned_orders > 0 or orphaned_shipments > 0:
            logger.warning("Critical data integrity issues detected!")

    def apply_reasoning_rules(self) -> None:
        """Apply all reasoning rules to derive new knowledge."""
        logger.info("Applying reasoning rules...")

        # Apply rules in logical sequence
        self._rule_01_supplier_performance_classification()
        self._rule_02_critical_supplier_identification()
        self._rule_03_high_volume_manufacturer_classification()
        self._rule_04_warehouse_capacity_utilization_calculation()
        self._rule_05_overcapacity_warehouse_detection()
        self._rule_06_premium_customer_recognition()
        self._rule_07_large_order_classification()
        self._rule_08_volume_discount_calculation()
        self._rule_09_final_order_amount_calculation()
        self._rule_10_urgent_order_processing()
        self._rule_11_expected_delivery_date_calculation()
        self._rule_12_delayed_shipment_detection()
        self._rule_13_overdue_invoice_detection()
        self._rule_14_low_stock_detection()
        self._rule_15_automatic_reorder_generation()
        self._rule_16_fast_moving_product_classification()
        self._rule_17_slow_moving_product_classification()
        self._rule_18_supplier_lead_time_adjustment()
        self._rule_19_priority_shipping_for_premium_customers()
        self._rule_20_carrier_selection_based_on_location()
        self._rule_21_quality_control_rules()
        self._rule_22_seasonal_demand_adjustment()
        self._rule_23_supply_chain_risk_assessment()
        self._rule_24_bulk_order_optimization()
        self._rule_25_customer_service_level_agreement()

        logger.info("Reasoning rules applied successfully")

    # ===== REASONING RULE IMPLEMENTATIONS =====

    def _rule_01_supplier_performance_classification(self) -> None:
        """Rule 1: Classify suppliers as preferred based on rating and delivery performance."""
        for supplier in self.suppliers.values():
            if supplier.rating > 4.5 and supplier.on_time_delivery_rate > 95.0:
                supplier.is_preferred = True
                self.classification_results['preferred_suppliers'].add(
                    supplier.id)

    def _rule_02_critical_supplier_identification(self) -> None:
        """Rule 2: Identify critical suppliers with limited alternatives."""
        for supplier in self.suppliers.values():
            supplier_count_for_manufacturers = 0
            for manufacturer in self.manufacturers.values():
                if supplier.id in manufacturer.supplier_ids:
                    # Count other suppliers for this manufacturer
                    other_suppliers = len(
                        [s for s in manufacturer.supplier_ids if s != supplier.id])
                    if other_suppliers < 2:  # Less than 3 total suppliers
                        supplier_count_for_manufacturers += 1

            if supplier_count_for_manufacturers > 0:
                supplier.is_critical = True
                self.classification_results['critical_suppliers'].add(
                    supplier.id)

    def _rule_03_high_volume_manufacturer_classification(self) -> None:
        """Rule 3: Classify manufacturers with high production capacity."""
        for manufacturer in self.manufacturers.values():
            if manufacturer.manufacturing_capacity > 10000:
                manufacturer.is_high_volume = True
                self.classification_results['high_volume_manufacturers'].add(
                    manufacturer.id)

    def _rule_04_warehouse_capacity_utilization_calculation(self) -> None:
        """Rule 4: Calculate warehouse capacity utilization percentage."""
        for warehouse in self.warehouses.values():
            stored_products = len(warehouse.product_ids)
            if warehouse.storage_capacity > 0:
                utilization = (stored_products /
                               warehouse.storage_capacity) * 100
                warehouse.capacity_utilization = min(utilization, 100.0)

    def _rule_05_overcapacity_warehouse_detection(self) -> None:
        """Rule 5: Detect warehouses operating above 90% capacity."""
        for warehouse in self.warehouses.values():
            if warehouse.capacity_utilization > 90.0:
                warehouse.is_overcapacity = True
                self.classification_results['overcapacity_warehouses'].add(
                    warehouse.id)

    def _rule_06_premium_customer_recognition(self) -> None:
        """Rule 6: Recognize premium customers based on total order value."""
        retailer_totals = {}

        for order in self.orders.values():
            if order.retailer_id not in retailer_totals:
                retailer_totals[order.retailer_id] = 0
            retailer_totals[order.retailer_id] += order.total_amount

        for retailer_id, total_value in retailer_totals.items():
            if total_value > 100000 and retailer_id in self.retailers:
                retailer = self.retailers[retailer_id]
                retailer.is_premium = True
                retailer.total_order_value = total_value
                self.classification_results['premium_customers'].add(
                    retailer_id)

    def _rule_07_large_order_classification(self) -> None:
        """Rule 7: Classify orders as large based on monetary value."""
        for order in self.orders.values():
            if order.total_amount > 50000:
                order.is_large = True
                self.classification_results['large_orders'].add(order.id)

    def _rule_08_volume_discount_calculation(self) -> None:
        """Rule 8: Calculate volume discounts for qualifying orders."""
        for order in self.orders.values():
            if order.total_amount > 25000:
                order.discount_amount = order.total_amount * 0.10
            elif order.total_amount > 10000:
                order.discount_amount = order.total_amount * 0.05

    def _rule_09_final_order_amount_calculation(self) -> None:
        """Rule 9: Calculate final order amount after discounts."""
        for order in self.orders.values():
            order.final_amount = order.total_amount - order.discount_amount

    def _rule_10_urgent_order_processing(self) -> None:
        """Rule 10: Mark orders as urgent if they contain low stock products."""
        current_time = datetime.now()

        for order in self.orders.values():
            # Check if order contains low stock products
            contains_low_stock = False
            for product_id in order.product_ids:
                if product_id in self.products and self.products[product_id].is_low_stock:
                    contains_low_stock = True
                    break

            # Check if order is recent (within 1 hour)
            time_diff = current_time - order.order_date
            is_recent = time_diff.total_seconds() < 3600

            if contains_low_stock and is_recent:
                order.is_urgent = True
                order.order_status = "URGENT_PROCESSING"
                self.classification_results['urgent_orders'].add(order.id)

    def _rule_11_expected_delivery_date_calculation(self) -> None:
        """Rule 11: Calculate expected delivery dates based on shipper location."""
        for shipment in self.shipments.values():
            shipper_location = ""

            # Get shipper location (warehouse or manufacturer)
            if shipment.shipper_id in self.warehouses:
                shipper_location = self.warehouses[shipment.shipper_id].warehouse_location
            elif shipment.shipper_id in self.manufacturers:
                shipper_location = self.manufacturers[shipment.shipper_id].manufacturer_location

            # Calculate delivery date based on location
            if "Local" in shipper_location:
                delivery_date = shipment.ship_date + timedelta(days=2)
            elif "International" in shipper_location:
                delivery_date = shipment.ship_date + timedelta(days=7)
            else:
                delivery_date = shipment.ship_date + \
                    timedelta(days=5)  # Default

            shipment.expected_delivery_date = delivery_date

    def _rule_12_delayed_shipment_detection(self) -> None:
        """Rule 12: Detect shipments that are past their expected delivery date."""
        current_time = datetime.now()

        for shipment in self.shipments.values():
            if (shipment.expected_delivery_date and
                    current_time > shipment.expected_delivery_date):
                shipment.is_delayed = True
                self.classification_results['delayed_shipments'].add(
                    shipment.id)

    def _rule_13_overdue_invoice_detection(self) -> None:
        """Rule 13: Detect overdue invoices (placeholder - unimplemented)."""
        # Unimplemented: Invoice data not available in CSV files
        pass

    def _rule_14_low_stock_detection(self) -> None:
        """Rule 14: Detect products with inventory below reorder point."""
        for product in self.products.values():
            if product.current_inventory_level <= product.reorder_point:
                product.is_low_stock = True
                self.classification_results['low_stock_products'].add(
                    product.id)

    def _rule_15_automatic_reorder_generation(self) -> None:
        """Rule 15: Generate automatic reorders for low stock products from preferred suppliers."""
        # Unimplemented: Would require creating new order records
        pass

    def _rule_16_fast_moving_product_classification(self) -> None:
        """Rule 16: Classify products as fast-moving based on turnover rate."""
        for product in self.products.values():
            if product.turnover_rate > 5.0:
                product.is_fast_moving = True
                self.classification_results['fast_moving_products'].add(
                    product.id)

    def _rule_17_slow_moving_product_classification(self) -> None:
        """Rule 17: Classify products as slow-moving based on turnover rate."""
        for product in self.products.values():
            if product.turnover_rate < 1.0:
                product.is_slow_moving = True
                self.classification_results['slow_moving_products'].add(
                    product.id)

    def _rule_18_supplier_lead_time_adjustment(self) -> None:
        """Rule 18: Adjust lead times for remote suppliers."""
        for supplier in self.suppliers.values():
            if "Remote" in supplier.supplier_location:
                supplier.lead_time = int(supplier.lead_time * 1.5)

    def _rule_19_priority_shipping_for_premium_customers(self) -> None:
        """Rule 19: Set priority shipping for premium customer orders."""
        for order in self.orders.values():
            if (order.retailer_id in self.retailers and
                    self.retailers[order.retailer_id].is_premium):
                order.order_status = "PRIORITY_SHIPPING"

    def _rule_20_carrier_selection_based_on_location(self) -> None:
        """Rule 20: Select carriers based on shipper location."""
        for shipment in self.shipments.values():
            shipper_location = ""

            if shipment.shipper_id in self.warehouses:
                shipper_location = self.warehouses[shipment.shipper_id].warehouse_location
            elif shipment.shipper_id in self.manufacturers:
                shipper_location = self.manufacturers[shipment.shipper_id].manufacturer_location

            if "East Coast" in shipper_location:
                shipment.carrier = "FEDEX_PRIORITY"
            elif "West Coast" in shipper_location:
                shipment.carrier = "UPS_GROUND"

    def _rule_21_quality_control_rules(self) -> None:
        """Rule 21: Set quality control requirements for pharmaceutical products."""
        for product in self.products.values():
            if "Pharmaceutical" in product.product_type:
                product.requires_quality_check = True

    def _rule_22_seasonal_demand_adjustment(self) -> None:
        """Rule 22: Adjust demand multiplier for holiday products during peak season."""
        current_month = datetime.now().month

        for product in self.products.values():
            if "Holiday" in product.product_type and current_month > 10:
                product.demand_multiplier = 2.0

    def _rule_23_supply_chain_risk_assessment(self) -> None:
        """Rule 23: Assess supply chain risk for critical suppliers in high-risk zones."""
        for supplier in self.suppliers.values():
            if supplier.is_critical and "High Risk Zone" in supplier.supplier_location:
                supplier.risk_level = "HIGH"

    def _rule_24_bulk_order_optimization(self) -> None:
        """Rule 24: Optimize shipping for bulk orders with many items."""
        for order in self.orders.values():
            if len(order.product_ids) > 10:
                order.shipping_optimization = "CONSOLIDATE_SHIPMENT"

    def _rule_25_customer_service_level_agreement(self) -> None:
        """Rule 25: Set service level agreements for premium customers."""
        for retailer in self.retailers.values():
            if retailer.is_premium:
                # Find warehouses that serve this retailer
                for order in self.orders.values():
                    if (order.retailer_id == retailer.id and
                        order.seller_type == "warehouse" and
                            order.seller_id in self.warehouses):
                        self.warehouses[order.seller_id].service_level_agreement = "24_HOUR_PROCESSING"

    def generate_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive statistics about the supply chain data."""
        stats = {
            'entity_counts': {
                'suppliers': len(self.suppliers),
                'manufacturers': len(self.manufacturers),
                'warehouses': len(self.warehouses),
                'retailers': len(self.retailers),
                'products': len(self.products),
                'orders': len(self.orders),
                'shipments': len(self.shipments)
            },
            'classification_counts': {
                'preferred_suppliers': len(self.classification_results['preferred_suppliers']),
                'critical_suppliers': len(self.classification_results['critical_suppliers']),
                'high_volume_manufacturers': len(self.classification_results['high_volume_manufacturers']),
                'overcapacity_warehouses': len(self.classification_results['overcapacity_warehouses']),
                'premium_customers': len(self.classification_results['premium_customers']),
                'urgent_orders': len(self.classification_results['urgent_orders']),
                'large_orders': len(self.classification_results['large_orders']),
                'delayed_shipments': len(self.classification_results['delayed_shipments']),
                'fast_moving_products': len(self.classification_results['fast_moving_products']),
                'slow_moving_products': len(self.classification_results['slow_moving_products']),
                'low_stock_products': len(self.classification_results['low_stock_products'])
            },
            'financial_metrics': {
                'total_order_value': sum(order.total_amount for order in self.orders.values()),
                'total_discount_amount': sum(order.discount_amount for order in self.orders.values()),
                'average_order_value': sum(order.total_amount for order in self.orders.values()) / max(len(self.orders), 1)
            },
            'operational_metrics': {
                'average_capacity_utilization': sum(wh.capacity_utilization for wh in self.warehouses.values()) / max(len(self.warehouses), 1),
                'total_manufacturing_capacity': sum(mfg.manufacturing_capacity for mfg in self.manufacturers.values()),
                'average_supplier_rating': sum(sup.rating for sup in self.suppliers.values()) / max(len(self.suppliers), 1)
            }
        }

        self.statistics = stats
        return stats

    def get_diagnostic_report(self) -> Dict[str, Any]:
        """Generate diagnostic report for data quality assessment."""
        return {
            'data_integrity': {
                'total_entities': sum([
                    len(self.suppliers), len(
                        self.manufacturers), len(self.warehouses),
                    len(self.retailers), len(self.products), len(
                        self.orders), len(self.shipments)
                ]),
                'relationship_integrity': self._check_relationship_integrity()
            },
            'classification_summary': self.classification_results,
            'processing_status': 'COMPLETED'
        }

    def _check_relationship_integrity(self) -> Dict[str, int]:
        """Check integrity of relationships between entities."""
        integrity_stats = {
            'valid_supplier_manufacturer_links': 0,
            'valid_order_retailer_links': 0,
            'valid_shipment_order_links': 0,
            'valid_product_manufacturer_links': 0
        }

        # Check supplier-manufacturer relationships
        for supplier in self.suppliers.values():
            for mfg_id in supplier.manufacturer_ids:
                if mfg_id in self.manufacturers:
                    integrity_stats['valid_supplier_manufacturer_links'] += 1

        # Check order-retailer relationships
        for order in self.orders.values():
            if order.retailer_id in self.retailers:
                integrity_stats['valid_order_retailer_links'] += 1

        # Check shipment-order relationships
        for shipment in self.shipments.values():
            if shipment.order_id in self.orders:
                integrity_stats['valid_shipment_order_links'] += 1

        # Check product-manufacturer relationships
        for product in self.products.values():
            if product.manufacturer_id and product.manufacturer_id in self.manufacturers:
                integrity_stats['valid_product_manufacturer_links'] += 1

        return integrity_stats

    def run_complete_analysis(self) -> Dict[str, Any]:
        """Run the complete supply chain analysis pipeline."""
        logger.info("Starting complete supply chain analysis...")

        try:
            # Load all data
            self.load_all_data()

            # Apply reasoning rules
            self.apply_reasoning_rules()

            # Generate statistics
            stats = self.generate_statistics()

            # Create comprehensive results
            results = {
                'entities': {
                    'suppliers': {sid: supplier.__dict__ for sid, supplier in self.suppliers.items()},
                    'manufacturers': {mid: manufacturer.__dict__ for mid, manufacturer in self.manufacturers.items()},
                    'warehouses': {wid: warehouse.__dict__ for wid, warehouse in self.warehouses.items()},
                    'retailers': {rid: retailer.__dict__ for rid, retailer in self.retailers.items()},
                    'products': {pid: product.__dict__ for pid, product in self.products.items()},
                    'orders': {oid: self._serialize_order(order) for oid, order in self.orders.items()},
                    'shipments': {sid: self._serialize_shipment(shipment) for sid, shipment in self.shipments.items()}
                },
                'classifications': self.classification_results,
                'statistics': stats,
                'diagnostics': self.get_diagnostic_report()
            }

            logger.info("Supply chain analysis completed successfully")
            return results

        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            raise

    def _serialize_order(self, order: Order) -> Dict[str, Any]:
        """Serialize order object for JSON export."""
        order_dict = order.__dict__.copy()
        order_dict['order_date'] = order.order_date.isoformat()
        return order_dict

    def _serialize_shipment(self, shipment: Shipment) -> Dict[str, Any]:
        """Serialize shipment object for JSON export."""
        shipment_dict = shipment.__dict__.copy()
        shipment_dict['ship_date'] = shipment.ship_date.isoformat()
        if shipment.expected_delivery_date:
            shipment_dict['expected_delivery_date'] = shipment.expected_delivery_date.isoformat(
            )
        return shipment_dict


def main():
    """Main execution function for standalone testing."""
    try:
        reasoner = SupplyChainReasoner()
        results = reasoner.run_complete_analysis()

        print("\n=== SUPPLY CHAIN ANALYSIS RESULTS ===")
        print(
            f"Total entities processed: {sum(results['statistics']['entity_counts'].values())}")
        print(
            f"Classifications applied: {sum(results['statistics']['classification_counts'].values())}")
        print(
            f"Total order value: ${results['statistics']['financial_metrics']['total_order_value']:,.2f}")
        print(
            f"Average capacity utilization: {results['statistics']['operational_metrics']['average_capacity_utilization']:.1f}%")

        return results

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise


if __name__ == "__main__":
    main()
