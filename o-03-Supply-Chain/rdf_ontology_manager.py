"""
RDF Ontology Manager for Supply Chain Reasoning


RDF graph management, URI generation, and multi-format export capabilities.
Converts reasoning results to semantic web standards with comprehensive validation.

"""

import logging
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from collections import defaultdict

try:
    from rdflib import Graph, Namespace, URIRef, Literal, BNode
    from rdflib.namespace import RDF, RDFS, OWL, XSD
    from rdflib import plugins
except ImportError:
    raise ImportError("rdflib is required. Install with: pip install rdflib")

# Import the core reasoner
from supply_chain_reasoner import SimpleSupplyChainReasoner

# Configure logging
logging.basicConfig(filename='./supply_chain_rdf_ontology_mgr.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RDFOntologyManager:
    """
    RDF graph management and multi-format export for supply chain ontology.

    Converts entity data and reasoning results to RDF triples with consistent
    URI generation and semantic web compliance.
    """

    def __init__(self, data_location: str = './data', output_location: str = './data/ontologies'):
        """Initialize the RDF ontology manager."""
        self.reasoner = SimpleSupplyChainReasoner(data_location)
        self.output_location = Path(output_location)
        self.output_location.mkdir(exist_ok=True)

        # RDF Graph and namespaces
        self.graph = Graph()
        self.ns = Namespace("http://example.org/supplychain#")
        self.graph.bind("sc", self.ns)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("xsd", XSD)

        # URI tracking and validation
        self.created_uris: Set[URIRef] = set()
        self.uri_mappings: Dict[str, URIRef] = {}
        self.validation_results: Dict[str, Any] = {}

        # RDF statistics
        self.rdf_stats: Dict[str, Any] = {}

        # Processing metadata
        self.processing_timestamp = datetime.now()

    def create_complete_rdf_graph(self) -> Graph:
        """
        Create complete RDF graph from supply chain analysis.

        Returns:
            RDF Graph with all entities, relationships, and reasoning results
        """
        logger.info("Creating complete RDF graph from supply chain analysis...")

        try:
            # Run reasoning analysis
            analysis_results = self.reasoner.run_complete_analysis()

            # Add ontology metadata
            self._add_ontology_metadata()

            # Convert entities to RDF
            self._convert_suppliers_to_rdf()
            self._convert_manufacturers_to_rdf()
            self._convert_warehouses_to_rdf()
            self._convert_retailers_to_rdf()
            self._convert_products_to_rdf()
            self._convert_orders_to_rdf()
            self._convert_shipments_to_rdf()

            # Add relationships
            self._add_object_properties()
            self._add_inverse_properties()

            # Add reasoning results
            self._add_classification_results()
            self._add_derived_properties()

            # Validate RDF graph
            self._validate_rdf_graph()

            # Generate statistics
            self._generate_rdf_statistics()

            logger.info(f"RDF graph created with {len(self.graph)} triples")
            return self.graph

        except Exception as e:
            logger.error(f"Error creating RDF graph: {e}")
            raise

    def _add_ontology_metadata(self) -> None:
        """Add ontology metadata and class definitions."""
        logger.info("Adding ontology metadata...")

        # Ontology declaration
        ontology_uri = URIRef("http://example.org/supplychain")
        self.graph.add((ontology_uri, RDF.type, OWL.Ontology))
        self.graph.add((ontology_uri, RDFS.label, Literal(
            "Supply Chain Ontology", datatype=XSD.string)))
        self.graph.add((ontology_uri, RDFS.comment, Literal(
            "Comprehensive supply chain ontology with business rules", datatype=XSD.string)))

        # Core class definitions
        core_classes = [
            ("Supplier", "An entity that provides raw materials or components"),
            ("Manufacturer", "An entity that produces finished goods"),
            ("Warehouse", "A facility for storing and distributing products"),
            ("Retailer", "An entity that sells products to end customers"),
            ("Product", "A manufactured item or good"),
            ("Order", "A request to purchase specific products"),
            ("Shipment", "A batch of products being transported"),
            ("Invoice", "A bill requesting payment for products or services")
        ]

        for class_name, description in core_classes:
            class_uri = self.ns[class_name]
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.label, Literal(
                class_name, datatype=XSD.string)))
            self.graph.add((class_uri, RDFS.comment, Literal(
                description, datatype=XSD.string)))

        # Derived class definitions
        derived_classes = [
            ("PreferredSupplier", "Supplier",
             "A supplier with high performance ratings"),
            ("CriticalSupplier", "Supplier", "A supplier with limited alternatives"),
            ("HighVolumeManufacturer", "Manufacturer",
             "A manufacturer with large production capacity"),
            ("OvercapacityWarehouse", "Warehouse",
             "A warehouse operating above optimal capacity"),
            ("PremiumCustomer", "Retailer",
             "A high-value customer with priority service"),
            ("UrgentOrder", "Order", "An order requiring expedited processing"),
            ("LargeOrder", "Order", "An order with high monetary value"),
            ("DelayedShipment", "Shipment",
             "A shipment past its expected delivery date"),
            ("FastMovingProduct", "Product",
             "A product with high demand and turnover"),
            ("SlowMovingProduct", "Product",
             "A product with low demand and turnover"),
            ("LowStockProduct", "Product",
             "A product with inventory below reorder point")
        ]

        for derived_class, parent_class, description in derived_classes:
            class_uri = self.ns[derived_class]
            parent_uri = self.ns[parent_class]
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.subClassOf, parent_uri))
            self.graph.add((class_uri, RDFS.label, Literal(
                derived_class, datatype=XSD.string)))
            self.graph.add((class_uri, RDFS.comment, Literal(
                description, datatype=XSD.string)))

    def _convert_suppliers_to_rdf(self) -> None:
        """Convert supplier entities to RDF triples."""
        logger.info("Converting suppliers to RDF...")

        for supplier in self.reasoner.suppliers.values():
            supplier_uri = self._create_safe_uri("supplier", supplier.id)

            # Core class assertion
            self.graph.add((supplier_uri, RDF.type, self.ns.Supplier))

            # Data properties
            self.graph.add((supplier_uri, self.ns.supplierName, Literal(
                supplier.supplier_name, datatype=XSD.string)))
            self.graph.add((supplier_uri, self.ns.supplierLocation, Literal(
                supplier.supplier_location, datatype=XSD.string)))
            self.graph.add((supplier_uri, self.ns.rating, Literal(
                supplier.rating, datatype=XSD.float)))
            self.graph.add((supplier_uri, self.ns.leadTime, Literal(
                supplier.lead_time, datatype=XSD.int)))
            self.graph.add((supplier_uri, self.ns.onTimeDeliveryRate, Literal(
                supplier.on_time_delivery_rate, datatype=XSD.float)))
            self.graph.add((supplier_uri, self.ns.riskLevel, Literal(
                supplier.risk_level, datatype=XSD.string)))

            # Classification results
            if supplier.is_preferred:
                self.graph.add(
                    (supplier_uri, RDF.type, self.ns.PreferredSupplier))
            if supplier.is_critical:
                self.graph.add(
                    (supplier_uri, RDF.type, self.ns.CriticalSupplier))

    def _convert_manufacturers_to_rdf(self) -> None:
        """Convert manufacturer entities to RDF triples."""
        logger.info("Converting manufacturers to RDF...")

        for manufacturer in self.reasoner.manufacturers.values():
            mfg_uri = self._create_safe_uri("manufacturer", manufacturer.id)

            # Core class assertion
            self.graph.add((mfg_uri, RDF.type, self.ns.Manufacturer))

            # Data properties
            self.graph.add((mfg_uri, self.ns.manufacturerName, Literal(
                manufacturer.manufacturer_name, datatype=XSD.string)))
            self.graph.add((mfg_uri, self.ns.manufacturerLocation, Literal(
                manufacturer.manufacturer_location, datatype=XSD.string)))
            self.graph.add((mfg_uri, self.ns.manufacturingCapacity, Literal(
                manufacturer.manufacturing_capacity, datatype=XSD.int)))

            # Classification results
            if manufacturer.is_high_volume:
                self.graph.add(
                    (mfg_uri, RDF.type, self.ns.HighVolumeManufacturer))

    def _convert_warehouses_to_rdf(self) -> None:
        """Convert warehouse entities to RDF triples."""
        logger.info("Converting warehouses to RDF...")

        for warehouse in self.reasoner.warehouses.values():
            warehouse_uri = self._create_safe_uri("warehouse", warehouse.id)

            # Core class assertion
            self.graph.add((warehouse_uri, RDF.type, self.ns.Warehouse))

            # Data properties
            self.graph.add((warehouse_uri, self.ns.warehouseName, Literal(
                warehouse.warehouse_name, datatype=XSD.string)))
            self.graph.add((warehouse_uri, self.ns.warehouseLocation, Literal(
                warehouse.warehouse_location, datatype=XSD.string)))
            self.graph.add((warehouse_uri, self.ns.storageCapacity, Literal(
                warehouse.storage_capacity, datatype=XSD.int)))
            self.graph.add((warehouse_uri, self.ns.capacityUtilization, Literal(
                warehouse.capacity_utilization, datatype=XSD.float)))
            self.graph.add((warehouse_uri, self.ns.serviceLevelAgreement, Literal(
                warehouse.service_level_agreement, datatype=XSD.string)))

            # Classification results
            if warehouse.is_overcapacity:
                self.graph.add(
                    (warehouse_uri, RDF.type, self.ns.OvercapacityWarehouse))

    def _convert_retailers_to_rdf(self) -> None:
        """Convert retailer entities to RDF triples."""
        logger.info("Converting retailers to RDF...")

        for retailer in self.reasoner.retailers.values():
            retailer_uri = self._create_safe_uri("retailer", retailer.id)

            # Core class assertion
            self.graph.add((retailer_uri, RDF.type, self.ns.Retailer))

            # Data properties
            self.graph.add((retailer_uri, self.ns.retailerName, Literal(
                retailer.retailer_name, datatype=XSD.string)))
            self.graph.add((retailer_uri, self.ns.retailerLocation, Literal(
                retailer.retailer_location, datatype=XSD.string)))
            self.graph.add((retailer_uri, self.ns.retailerType, Literal(
                retailer.retailer_type, datatype=XSD.string)))
            self.graph.add((retailer_uri, self.ns.totalOrderValue, Literal(
                retailer.total_order_value, datatype=XSD.float)))
            self.graph.add((retailer_uri, self.ns.averageOrderSize, Literal(
                retailer.average_order_size, datatype=XSD.float)))

            # Classification results
            if retailer.is_premium:
                self.graph.add(
                    (retailer_uri, RDF.type, self.ns.PremiumCustomer))

    def _convert_products_to_rdf(self) -> None:
        """Convert product entities to RDF triples."""
        logger.info("Converting products to RDF...")

        for product in self.reasoner.products.values():
            product_uri = self._create_safe_uri("product", product.id)

            # Core class assertion
            self.graph.add((product_uri, RDF.type, self.ns.Product))

            # Data properties
            self.graph.add((product_uri, self.ns.productName, Literal(
                product.product_name, datatype=XSD.string)))
            self.graph.add((product_uri, self.ns.sku, Literal(
                product.sku, datatype=XSD.string)))
            self.graph.add((product_uri, self.ns.productType, Literal(
                product.product_type, datatype=XSD.string)))
            self.graph.add((product_uri, self.ns.unitPrice, Literal(
                product.unit_price, datatype=XSD.float)))
            self.graph.add((product_uri, self.ns.currentInventoryLevel, Literal(
                product.current_inventory_level, datatype=XSD.int)))
            self.graph.add((product_uri, self.ns.reorderPoint, Literal(
                product.reorder_point, datatype=XSD.int)))
            self.graph.add((product_uri, self.ns.turnoverRate, Literal(
                product.turnover_rate, datatype=XSD.float)))
            self.graph.add((product_uri, self.ns.demandMultiplier, Literal(
                product.demand_multiplier, datatype=XSD.float)))
            self.graph.add((product_uri, self.ns.requiresQualityCheck, Literal(
                product.requires_quality_check, datatype=XSD.boolean)))

            # Classification results
            if product.is_fast_moving:
                self.graph.add(
                    (product_uri, RDF.type, self.ns.FastMovingProduct))
            if product.is_slow_moving:
                self.graph.add(
                    (product_uri, RDF.type, self.ns.SlowMovingProduct))
            if product.is_low_stock:
                self.graph.add(
                    (product_uri, RDF.type, self.ns.LowStockProduct))

    def _convert_orders_to_rdf(self) -> None:
        """Convert order entities to RDF triples."""
        logger.info("Converting orders to RDF...")

        for order in self.reasoner.orders.values():
            order_uri = self._create_safe_uri("order", order.id)

            # Core class assertion
            self.graph.add((order_uri, RDF.type, self.ns.Order))

            # Data properties
            self.graph.add((order_uri, self.ns.orderNumber, Literal(
                order.order_number, datatype=XSD.string)))
            self.graph.add((order_uri, self.ns.orderDate, Literal(
                order.order_date.isoformat(), datatype=XSD.dateTime)))
            self.graph.add((order_uri, self.ns.orderStatus, Literal(
                order.order_status, datatype=XSD.string)))
            self.graph.add((order_uri, self.ns.totalAmount, Literal(
                order.total_amount, datatype=XSD.float)))
            self.graph.add((order_uri, self.ns.discountAmount, Literal(
                order.discount_amount, datatype=XSD.float)))
            self.graph.add((order_uri, self.ns.finalAmount, Literal(
                order.final_amount, datatype=XSD.float)))
            self.graph.add((order_uri, self.ns.shippingOptimization, Literal(
                order.shipping_optimization, datatype=XSD.string)))

            # Classification results
            if order.is_urgent:
                self.graph.add((order_uri, RDF.type, self.ns.UrgentOrder))
            if order.is_large:
                self.graph.add((order_uri, RDF.type, self.ns.LargeOrder))

    def _convert_shipments_to_rdf(self) -> None:
        """Convert shipment entities to RDF triples."""
        logger.info("Converting shipments to RDF...")

        for shipment in self.reasoner.shipments.values():
            shipment_uri = self._create_safe_uri("shipment", shipment.id)

            # Core class assertion
            self.graph.add((shipment_uri, RDF.type, self.ns.Shipment))

            # Data properties
            self.graph.add((shipment_uri, self.ns.shipmentID, Literal(
                shipment.shipment_id, datatype=XSD.string)))
            self.graph.add((shipment_uri, self.ns.shipDate, Literal(
                shipment.ship_date.isoformat(), datatype=XSD.dateTime)))
            self.graph.add((shipment_uri, self.ns.carrier, Literal(
                shipment.carrier, datatype=XSD.string)))
            self.graph.add((shipment_uri, self.ns.trackingNumber, Literal(
                shipment.tracking_number, datatype=XSD.string)))

            if shipment.expected_delivery_date:
                self.graph.add((shipment_uri, self.ns.expectedDeliveryDate,
                                Literal(shipment.expected_delivery_date.isoformat(), datatype=XSD.dateTime)))

            # Classification results
            if shipment.is_delayed:
                self.graph.add(
                    (shipment_uri, RDF.type, self.ns.DelayedShipment))

    def _add_object_properties(self) -> None:
        """Add object properties between entities."""
        logger.info("Adding object properties...")

        # Supplier-Manufacturer relationships
        for supplier in self.reasoner.suppliers.values():
            supplier_uri = self._get_entity_uri("supplier", supplier.id)
            for mfg_id in supplier.manufacturer_ids:
                if mfg_id in self.reasoner.manufacturers:
                    mfg_uri = self._get_entity_uri("manufacturer", mfg_id)
                    self.graph.add((supplier_uri, self.ns.suppliesTo, mfg_uri))

        # Manufacturer-Product relationships
        for manufacturer in self.reasoner.manufacturers.values():
            mfg_uri = self._get_entity_uri("manufacturer", manufacturer.id)
            for product_id in manufacturer.product_ids:
                if product_id in self.reasoner.products:
                    product_uri = self._get_entity_uri("product", product_id)
                    self.graph.add(
                        (mfg_uri, self.ns.manufactures, product_uri))

        # Warehouse-Product relationships
        for warehouse in self.reasoner.warehouses.values():
            warehouse_uri = self._get_entity_uri("warehouse", warehouse.id)
            for product_id in warehouse.product_ids:
                if product_id in self.reasoner.products:
                    product_uri = self._get_entity_uri("product", product_id)
                    self.graph.add(
                        (warehouse_uri, self.ns.stores, product_uri))

        # Order relationships
        for order in self.reasoner.orders.values():
            order_uri = self._get_entity_uri("order", order.id)

            # Order-Retailer relationship
            if order.retailer_id in self.reasoner.retailers:
                retailer_uri = self._get_entity_uri(
                    "retailer", order.retailer_id)

                # Order from warehouse or manufacturer
                if order.seller_type == "warehouse" and order.seller_id in self.reasoner.warehouses:
                    warehouse_uri = self._get_entity_uri(
                        "warehouse", order.seller_id)
                    self.graph.add(
                        (retailer_uri, self.ns.ordersFromWarehouse, warehouse_uri))
                elif order.seller_type == "manufacturer" and order.seller_id in self.reasoner.manufacturers:
                    mfg_uri = self._get_entity_uri(
                        "manufacturer", order.seller_id)
                    self.graph.add(
                        (retailer_uri, self.ns.ordersFromManufacturer, mfg_uri))

            # Order-Product relationships
            for product_id in order.product_ids:
                if product_id in self.reasoner.products:
                    product_uri = self._get_entity_uri("product", product_id)
                    self.graph.add(
                        (order_uri, self.ns.hasOrderLine, product_uri))

        # Shipment relationships
        for shipment in self.reasoner.shipments.values():
            shipment_uri = self._get_entity_uri("shipment", shipment.id)

            # Shipment-Order relationship
            if shipment.order_id in self.reasoner.orders:
                order_uri = self._get_entity_uri("order", shipment.order_id)
                self.graph.add((shipment_uri, self.ns.shipsOrder, order_uri))

            # Shipment-Shipper relationship
            if shipment.shipper_id in self.reasoner.warehouses:
                shipper_uri = self._get_entity_uri(
                    "warehouse", shipment.shipper_id)
                self.graph.add((shipment_uri, self.ns.hasShipper, shipper_uri))
            elif shipment.shipper_id in self.reasoner.manufacturers:
                shipper_uri = self._get_entity_uri(
                    "manufacturer", shipment.shipper_id)
                self.graph.add((shipment_uri, self.ns.hasShipper, shipper_uri))

    def _add_inverse_properties(self) -> None:
        """Add inverse object properties."""
        logger.info("Adding inverse properties...")

        # Define inverse property mappings
        inverse_properties = [
            (self.ns.suppliesTo, self.ns.suppliedBy),
            (self.ns.manufactures, self.ns.manufacturedBy),
            (self.ns.stores, self.ns.storedIn),
            (self.ns.ordersFromWarehouse, self.ns.warehouseOrderedBy),
            (self.ns.ordersFromManufacturer, self.ns.manufacturerOrderedBy),
            (self.ns.hasOrderLine, self.ns.orderLineOf),
            (self.ns.shipsOrder, self.ns.shippedIn),
            (self.ns.hasShipper, self.ns.ships)
        ]

        # Add inverse triples
        for property_uri, inverse_uri in inverse_properties:
            for subj, pred, obj in self.graph.triples((None, property_uri, None)):
                self.graph.add((obj, inverse_uri, subj))

    def _add_classification_results(self) -> None:
        """Add classification results from reasoning."""
        logger.info("Adding classification results...")

        # Classifications are already added during entity conversion
        # This method can be extended for additional classification metadata

        # Add classification statistics as data properties
        stats_uri = self.ns.ClassificationStatistics
        self.graph.add((stats_uri, RDF.type, self.ns.Statistics))

        for classification_type, entity_ids in self.reasoner.classification_results.items():
            property_name = f"count_{classification_type}"
            property_uri = self.ns[property_name]
            self.graph.add((stats_uri, property_uri, Literal(
                len(entity_ids), datatype=XSD.int)))

    def _add_derived_properties(self) -> None:
        """Add derived properties from reasoning results."""
        logger.info("Adding derived properties...")

        # Derived properties are already added during entity conversion
        # Additional derived statistics can be added here

        # Add overall statistics
        stats = self.reasoner.statistics if hasattr(
            self.reasoner, 'statistics') and self.reasoner.statistics else {}

        if stats:
            stats_uri = self.ns.SupplyChainStatistics
            self.graph.add((stats_uri, RDF.type, self.ns.Statistics))

            # Financial metrics
            if 'financial_metrics' in stats:
                for metric, value in stats['financial_metrics'].items():
                    if isinstance(value, (int, float)):
                        property_uri = self.ns[f"financial_{metric}"]
                        datatype = XSD.float if isinstance(
                            value, float) else XSD.int
                        self.graph.add(
                            (stats_uri, property_uri, Literal(value, datatype=datatype)))

            # Operational metrics
            if 'operational_metrics' in stats:
                for metric, value in stats['operational_metrics'].items():
                    if isinstance(value, (int, float)):
                        property_uri = self.ns[f"operational_{metric}"]
                        datatype = XSD.float if isinstance(
                            value, float) else XSD.int
                        self.graph.add(
                            (stats_uri, property_uri, Literal(value, datatype=datatype)))

    def _create_safe_uri(self, prefix: str, identifier: str) -> URIRef:
        """Create safe URI with consistent cleaning."""
        clean_id = self._clean_identifier(identifier)
        uri = self.ns[f"{prefix}_{clean_id}"]
        self.created_uris.add(uri)
        self.uri_mappings[f"{prefix}_{identifier}"] = uri
        return uri

    def _clean_identifier(self, text: str) -> str:
        """Clean identifier for safe URI generation."""
        # Remove special characters and replace with underscores
        cleaned = re.sub(r'[^\w\-_]', '_', str(text))

        # Ensure identifier doesn't start with digit
        if cleaned and cleaned[0].isdigit():
            cleaned = f"id_{cleaned}"

        # Remove multiple consecutive underscores
        cleaned = re.sub(r'_+', '_', cleaned).strip('_')

        # Ensure minimum length
        if not cleaned:
            cleaned = "unknown"

        return cleaned

    def _get_entity_uri(self, entity_type: str, entity_id: str) -> URIRef:
        """Get existing URI for entity or create new one."""
        key = f"{entity_type}_{entity_id}"
        if key in self.uri_mappings:
            return self.uri_mappings[key]
        return self._create_safe_uri(entity_type, entity_id)

    def _validate_rdf_graph(self) -> None:
        """Validate RDF graph for consistency and completeness."""
        logger.info("Validating RDF graph...")

        validation_results = {
            'total_triples': len(self.graph),
            'unique_subjects': len(set(s for s, p, o in self.graph)),
            'unique_predicates': len(set(p for s, p, o in self.graph)),
            'unique_objects': len(set(o for s, p, o in self.graph)),
            'uri_consistency': self._validate_uri_consistency(),
            'datatype_validation': self._validate_datatypes(),
            'relationship_validation': self._validate_relationships()
        }

        self.validation_results = validation_results

        # Log validation summary
        logger.info(f"RDF validation completed - Triples: {validation_results['total_triples']}, "
                    f"Subjects: {validation_results['unique_subjects']}, "
                    f"URI consistency: {validation_results['uri_consistency']['consistent']}")

    def _validate_uri_consistency(self) -> Dict[str, Any]:
        """Validate URI consistency and patterns."""
        uri_patterns = defaultdict(int)
        invalid_uris = []

        for uri in self.created_uris:
            if not str(uri).startswith("http://example.org/supplychain#"):
                invalid_uris.append(uri)
            else:
                # Extract pattern (prefix before underscore)
                local_name = str(uri).split('#')[1]
                if '_' in local_name:
                    pattern = local_name.split('_')[0]
                    uri_patterns[pattern] += 1

        return {
            'consistent': len(invalid_uris) == 0,
            'invalid_count': len(invalid_uris),
            'pattern_distribution': dict(uri_patterns),
            'total_created_uris': len(self.created_uris)
        }

    def _validate_datatypes(self) -> Dict[str, Any]:
        """Validate literal datatypes."""
        datatype_counts = defaultdict(int)
        invalid_literals = []

        for s, p, o in self.graph:
            if isinstance(o, Literal):
                if o.datatype:
                    datatype_counts[str(o.datatype)] += 1
                else:
                    invalid_literals.append((s, p, o))

        return {
            'typed_literals': sum(datatype_counts.values()),
            'untyped_literals': len(invalid_literals),
            'datatype_distribution': dict(datatype_counts),
            'valid_typing': len(invalid_literals) == 0
        }

    def _validate_relationships(self) -> Dict[str, Any]:
        """Validate object property relationships."""
        object_properties = [
            self.ns.suppliesTo, self.ns.manufactures, self.ns.stores,
            self.ns.ordersFromWarehouse, self.ns.ordersFromManufacturer,
            self.ns.hasOrderLine, self.ns.shipsOrder, self.ns.hasShipper
        ]

        relationship_counts = {}
        dangling_references = []

        for prop in object_properties:
            count = len(list(self.graph.triples((None, prop, None))))
            relationship_counts[str(prop)] = count

            # Check for dangling references
            for s, p, o in self.graph.triples((None, prop, None)):
                if isinstance(o, URIRef) and o not in self.created_uris:
                    dangling_references.append((s, p, o))

        return {
            'relationship_counts': relationship_counts,
            'dangling_references': len(dangling_references),
            'total_relationships': sum(relationship_counts.values())
        }

    def _generate_rdf_statistics(self) -> None:
        """Generate comprehensive RDF statistics."""
        logger.info("Generating RDF statistics...")

        # Count entities by type
        entity_counts = {}
        for class_name in ['Supplier', 'Manufacturer', 'Warehouse', 'Retailer', 'Product', 'Order', 'Shipment']:
            class_uri = self.ns[class_name]
            count = len(list(self.graph.triples((None, RDF.type, class_uri))))
            entity_counts[class_name] = count

        # Count derived classifications
        classification_counts = {}
        derived_classes = ['PreferredSupplier', 'CriticalSupplier', 'HighVolumeManufacturer',
                           'OvercapacityWarehouse', 'PremiumCustomer', 'UrgentOrder', 'LargeOrder',
                           'DelayedShipment', 'FastMovingProduct', 'SlowMovingProduct', 'LowStockProduct']

        for class_name in derived_classes:
            class_uri = self.ns[class_name]
            count = len(list(self.graph.triples((None, RDF.type, class_uri))))
            classification_counts[class_name] = count

        # Property usage statistics
        property_usage = defaultdict(int)
        for s, p, o in self.graph:
            property_usage[str(p)] += 1

        self.rdf_stats = {
            'graph_metrics': {
                'total_triples': len(self.graph),
                'unique_subjects': len(set(s for s, p, o in self.graph)),
                'unique_predicates': len(set(p for s, p, o in self.graph)),
                'unique_objects': len(set(o for s, p, o in self.graph))
            },
            'entity_counts': entity_counts,
            'classification_counts': classification_counts,
            'property_usage': dict(property_usage),
            'validation_results': self.validation_results,
            'processing_metadata': {
                # 'created_timestamp': self.processing_timestamp.isoformat(),
                'rdf_formats_supported': ['turtle', 'n3', 'xml', 'json-ld', 'nt'],
                'namespace_uri': str(self.ns),
                'ontology_version': '1.0'
            }
        }

    def export_all_formats(self, base_filename: Optional[str] = None) -> Dict[str, str]:
        """
        Export RDF graph to all supported formats.

        Returns:
            Dictionary mapping format names to file paths
        """
        if not base_filename:
            base_filename = f"supply_chain_ontology"

        # Ensure graph is created
        if len(self.graph) == 0:
            self.create_complete_rdf_graph()

        exported_files = {}

        # Export formats with error handling
        formats = [
            ('turtle', 'ttl', 'Turtle'),
            ('n3', 'n3', 'N3'),
            ('xml', 'rdf', 'RDF/XML'),
            ('json-ld', 'jsonld', 'JSON-LD'),
            ('nt', 'nt', 'N-Triples')
        ]

        for format_name, extension, description in formats:
            try:
                filepath = self.output_location / \
                    f"{base_filename}.{extension}"
                self.graph.serialize(destination=str(
                    filepath), format=format_name)
                exported_files[description] = str(filepath)
                logger.info(f"Exported {description} to {filepath}")
            except Exception as e:
                logger.error(f"Failed to export {description}: {e}")
                exported_files[description] = f"ERROR: {e}"

        return exported_files

    def export_rdf_statistics(self, filename: Optional[str] = None) -> str:
        """Export RDF statistics to JSON file."""
        if not filename:
            filename = f"rdf_statistics.json"

        filepath = self.output_location / filename

        # Generate statistics if not already done
        if not self.rdf_stats:
            self._generate_rdf_statistics()

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.rdf_stats, f, indent=2, ensure_ascii=False)

        logger.info(f"RDF statistics exported to {filepath}")
        return str(filepath)

    def generate_rdf_report(self, filename: Optional[str] = None) -> str:
        """Generate comprehensive RDF report in text format."""
        if not filename:
            filename = "rdf_report.txt"

        filepath = self.output_location / filename

        # Ensure statistics are generated
        if not self.rdf_stats:
            self._generate_rdf_statistics()

        report_content = f"""RDF Ontology Report
==================

Namespace: {self.ns}

Graph Metrics
-------------
Total Triples: {self.rdf_stats['graph_metrics']['total_triples']:,}
Unique Subjects: {self.rdf_stats['graph_metrics']['unique_subjects']:,}
Unique Predicates: {self.rdf_stats['graph_metrics']['unique_predicates']:,}
Unique Objects: {self.rdf_stats['graph_metrics']['unique_objects']:,}

Entity Counts
-------------
"""

        for entity_type, count in self.rdf_stats['entity_counts'].items():
            report_content += f"{entity_type}: {count:,}\n"

        report_content += "\nClassification Counts\n"
        report_content += "--------------------\n"

        for classification, count in self.rdf_stats['classification_counts'].items():
            report_content += f"{classification}: {count:,}\n"

        report_content += f"\nValidation Results\n"
        report_content += "-------------------\n"

        if self.validation_results:
            report_content += f"URI Consistency: {'PASS' if self.validation_results['uri_consistency']['consistent'] else 'FAIL'}\n"
            report_content += f"Datatype Validation: {'PASS' if self.validation_results['datatype_validation']['valid_typing'] else 'FAIL'}\n"
            report_content += f"Dangling References: {self.validation_results['relationship_validation']['dangling_references']}\n"

        report_content += f"\nTop Property Usage\n"
        report_content += "------------------\n"

        # Sort properties by usage count
        sorted_props = sorted(
            self.rdf_stats['property_usage'].items(), key=lambda x: x[1], reverse=True)
        for prop, count in sorted_props[:20]:  # Top 20
            prop_name = prop.split('#')[-1] if '#' in prop else prop
            report_content += f"{prop_name}: {count:,}\n"

        report_content += f"\nExport Summary\n"
        report_content += "--------------\n"
        report_content += f"RDF formats supported: {', '.join(self.rdf_stats['processing_metadata']['rdf_formats_supported'])}\n"
        report_content += f"Ontology version: {self.rdf_stats['processing_metadata']['ontology_version']}\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"RDF report generated at {filepath}")
        return str(filepath)

    def run_complete_rdf_pipeline(self) -> Dict[str, Any]:
        """
        Run complete RDF processing pipeline.

        Returns:
            Complete results with file paths and statistics
        """
        logger.info("Running complete RDF processing pipeline...")

        try:
            # Create RDF graph
            graph = self.create_complete_rdf_graph()

            # Export all formats
            exported_files = self.export_all_formats()

            # Export statistics and reports
            stats_file = self.export_rdf_statistics()
            report_file = self.generate_rdf_report()

            # Compile results
            pipeline_results = {
                'rdf_graph': {
                    'total_triples': len(graph),
                    'validation_passed': self.validation_results.get('uri_consistency', {}).get('consistent', False)
                },
                'exported_files': exported_files,
                'statistics_file': stats_file,
                'report_file': report_file,
                'rdf_statistics': self.rdf_stats,
                'pipeline_metadata': {
                    # 'processing_timestamp': self.processing_timestamp.isoformat(),
                    'pipeline_version': '1.0',
                    'success': True
                }
            }

            logger.info("RDF processing pipeline completed successfully")
            return pipeline_results

        except Exception as e:
            logger.error(f"RDF pipeline failed: {e}")
            raise


def main():
    """Main execution function for RDF ontology management."""
    try:
        # Initialize RDF manager
        rdf_manager = RDFOntologyManager()

        # Run complete pipeline
        logger.info("Starting RDF ontology processing...")
        results = rdf_manager.run_complete_rdf_pipeline()

        # Print summary
        print("\n=== RDF ONTOLOGY PROCESSING SUMMARY ===")
        print(
            f"Total Triples Generated: {results['rdf_graph']['total_triples']:,}")
        print(
            f"Validation Status: {'PASSED' if results['rdf_graph']['validation_passed'] else 'FAILED'}")
        print(f"\nExported Formats:")
        for format_name, filepath in results['exported_files'].items():
            status = "PASSED" if not filepath.startswith(
                "ERROR") else "FAILED"
            print(f"  {status} {format_name}: {filepath}")

        print(f"\nAdditional Files:")
        print(f"  Statistics: {results['statistics_file']}")
        print(f"  Report: {results['report_file']}")

        # Entity summary
        if 'entity_counts' in results['rdf_statistics']:
            print(f"\nEntity Summary:")
            for entity_type, count in results['rdf_statistics']['entity_counts'].items():
                print(f"  {entity_type}: {count:,}")

        return results

    except Exception as e:
        logger.error(f"RDF processing failed: {e}")
        raise


if __name__ == "__main__":
    main()
