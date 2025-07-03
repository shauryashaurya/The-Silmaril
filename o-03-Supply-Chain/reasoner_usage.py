"""
Supply Chain Reasoner Usage Analyzer

Analytics, reporting, and user-facing functionality for the Supply Chain Reasoner.
Provides business intelligence, strategic insights, and comprehensive reporting capabilities.

"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import asdict

# Import the core reasoner
from supply_chain_reasoner import SimpleSupplyChainReasoner

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SupplyChainAnalyticsEngine:
    """
    Comprehensive analytics engine for supply chain business intelligence.

    Provides strategic insights, performance analytics, and actionable recommendations
    based on ontological reasoning results.
    """

    def __init__(self, data_location: str = './data', output_location: str = './output'):
        """Initialize the analytics engine."""
        self.reasoner = SimpleSupplyChainReasoner(data_location)
        self.output_location = Path(output_location)
        self.output_location.mkdir(exist_ok=True)

        # Analysis results
        self.analysis_results: Optional[Dict[str, Any]] = None
        self.business_insights: Dict[str, Any] = {}
        self.strategic_recommendations: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}

        # Report metadata
        self.report_timestamp = datetime.now()
        self.executive_summary: Dict[str, Any] = {}

    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Execute comprehensive supply chain analysis and generate insights.

        Returns:
            Complete analysis results with business intelligence
        """
        logger.info("Starting comprehensive supply chain analytics...")

        try:
            # Run core reasoning analysis
            self.analysis_results = self.reasoner.run_complete_analysis()

            # Generate business intelligence insights
            self._generate_business_insights()
            self._calculate_performance_metrics()
            self._generate_strategic_recommendations()
            self._create_executive_summary()

            # Compile comprehensive analytics results
            analytics_results = {
                'core_analysis': self.analysis_results,
                'business_insights': self.business_insights,
                'performance_metrics': self.performance_metrics,
                'strategic_recommendations': self.strategic_recommendations,
                'executive_summary': self.executive_summary,
                'analytics_metadata': {
                    'analysis_timestamp': self.report_timestamp.isoformat(),
                    'analytics_version': '1.0',
                    'recommendations_count': len(self.strategic_recommendations),
                    'insights_generated': len(self.business_insights)
                }
            }

            logger.info("Comprehensive analytics completed successfully")
            return analytics_results

        except Exception as e:
            logger.error(f"Error during comprehensive analysis: {e}")
            raise

    def _generate_business_insights(self) -> None:
        """Generate strategic business insights from reasoning results."""
        logger.info("Generating business insights...")

        stats = self.analysis_results['statistics']
        classifications = self.analysis_results['classifications']

        # Supply Chain Health Assessment
        self.business_insights['supply_chain_health'] = {
            'overall_health_score': self._calculate_health_score(),
            'critical_supplier_ratio': len(classifications['critical_suppliers']) / max(len(self.reasoner.suppliers), 1),
            'capacity_utilization_efficiency': stats['operational_metrics']['average_capacity_utilization'],
            'premium_customer_penetration': len(classifications['premium_customers']) / max(len(self.reasoner.retailers), 1),
            'risk_assessment': self._assess_supply_chain_risks()
        }

        # Financial Performance Insights
        self.business_insights['financial_performance'] = {
            'revenue_optimization': {
                'total_revenue': stats['financial_metrics']['total_order_value'],
                'discount_impact': stats['financial_metrics']['total_discount_amount'],
                'revenue_after_discounts': stats['financial_metrics']['total_final_amount'],
                'discount_efficiency': self._calculate_discount_efficiency()
            },
            'customer_value_analysis': self._analyze_customer_value(),
            'order_size_trends': self._analyze_order_trends()
        }

        # Operational Excellence Insights
        self.business_insights['operational_excellence'] = {
            'inventory_management': self._analyze_inventory_management(),
            'shipping_optimization': self._analyze_shipping_performance(),
            'supplier_performance': self._analyze_supplier_performance(),
            'manufacturing_efficiency': self._analyze_manufacturing_efficiency()
        }

        # Strategic Market Position
        self.business_insights['market_position'] = {
            'competitive_advantages': self._identify_competitive_advantages(),
            'growth_opportunities': self._identify_growth_opportunities(),
            'operational_bottlenecks': self._identify_bottlenecks(),
            'quality_metrics': self._analyze_quality_metrics()
        }

    def _calculate_performance_metrics(self) -> None:
        """Calculate comprehensive performance metrics."""
        logger.info("Calculating performance metrics...")

        stats = self.analysis_results['statistics']
        classifications = self.analysis_results['classifications']

        # Key Performance Indicators (KPIs)
        self.performance_metrics = {
            'financial_kpis': {
                'revenue_per_order': stats['financial_metrics']['average_order_value'],
                'discount_penetration_rate': (len([o for o in self.reasoner.orders.values() if o.discount_amount > 0]) /
                                              max(len(self.reasoner.orders), 1)) * 100,
                'premium_customer_revenue_share': self._calculate_premium_revenue_share(),
                'large_order_contribution': self._calculate_large_order_contribution()
            },
            'operational_kpis': {
                'supplier_diversity_index': self._calculate_supplier_diversity(),
                'warehouse_efficiency_score': self._calculate_warehouse_efficiency(),
                'inventory_turnover_health': self._calculate_inventory_health(),
                'shipment_performance_score': self._calculate_shipment_performance()
            },
            'quality_kpis': {
                'data_integrity_score': stats['data_quality']['data_integrity_score'],
                'relationship_completeness': self._calculate_relationship_completeness(),
                'classification_coverage': self._calculate_classification_coverage(),
                'processing_efficiency': self._calculate_processing_efficiency()
            },
            'strategic_kpis': {
                'supply_chain_resilience': self._calculate_resilience_score(),
                'automation_readiness': self._calculate_automation_readiness(),
                'scalability_index': self._calculate_scalability_index(),
                'innovation_potential': self._calculate_innovation_potential()
            }
        }

    def _generate_strategic_recommendations(self) -> None:
        """Generate actionable strategic recommendations."""
        logger.info("Generating strategic recommendations...")

        classifications = self.analysis_results['classifications']

        # Critical Supply Chain Issues
        if len(classifications['critical_suppliers']) > 0:
            self.strategic_recommendations.append({
                'priority': 'HIGH',
                'category': 'Supply Chain Risk',
                'title': 'Diversify Critical Supplier Base',
                'description': f"You have {len(classifications['critical_suppliers'])} critical suppliers with limited alternatives.",
                'impact': 'Reduces supply chain disruption risk',
                'action_items': [
                    'Identify and qualify alternative suppliers for critical materials',
                    'Implement supplier development programs',
                    'Consider strategic partnerships or vertical integration'
                ],
                'expected_benefit': 'Risk reduction, improved supply security',
                'timeline': '3-6 months'
            })

        # Capacity Optimization
        if len(classifications['overcapacity_warehouses']) > 0:
            self.strategic_recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Operational Efficiency',
                'title': 'Optimize Warehouse Capacity',
                'description': f"{len(classifications['overcapacity_warehouses'])} warehouses are operating above 90% capacity.",
                'impact': 'Improves operational efficiency and reduces costs',
                'action_items': [
                    'Implement dynamic inventory redistribution',
                    'Consider capacity expansion for high-utilization facilities',
                    'Optimize product placement and storage strategies'
                ],
                'expected_benefit': 'Reduced operational bottlenecks, improved service levels',
                'timeline': '2-4 months'
            })

        # Customer Value Enhancement
        premium_ratio = len(
            classifications['premium_customers']) / max(len(self.reasoner.retailers), 1)
        if premium_ratio < 0.2:
            self.strategic_recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Revenue Growth',
                'title': 'Expand Premium Customer Base',
                'description': f"Only {premium_ratio:.1%} of customers are classified as premium.",
                'impact': 'Increases revenue and improves customer lifetime value',
                'action_items': [
                    'Develop customer tier advancement programs',
                    'Implement targeted marketing for high-potential customers',
                    'Enhance service offerings for mid-tier customers'
                ],
                'expected_benefit': 'Increased revenue per customer, improved retention',
                'timeline': '6-12 months'
            })

        # Inventory Optimization
        if len(classifications['low_stock_products']) > 0:
            self.strategic_recommendations.append({
                'priority': 'HIGH',
                'category': 'Inventory Management',
                'title': 'Implement Predictive Inventory Management',
                'description': f"{len(classifications['low_stock_products'])} products are currently below reorder points.",
                'impact': 'Prevents stockouts and improves customer satisfaction',
                'action_items': [
                    'Implement automated reorder point optimization',
                    'Deploy demand forecasting algorithms',
                    'Establish safety stock buffers for critical products'
                ],
                'expected_benefit': 'Reduced stockouts, improved order fulfillment',
                'timeline': '1-3 months'
            })

        # Technology and Automation
        urgent_orders_ratio = len(
            classifications['urgent_orders']) / max(len(self.reasoner.orders), 1)
        if urgent_orders_ratio > 0.1:
            self.strategic_recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Process Automation',
                'title': 'Enhance Order Processing Automation',
                'description': f"{urgent_orders_ratio:.1%} of orders require urgent processing.",
                'impact': 'Improves processing speed and reduces manual intervention',
                'action_items': [
                    'Implement real-time inventory monitoring',
                    'Deploy automated order prioritization systems',
                    'Establish proactive customer communication workflows'
                ],
                'expected_benefit': 'Faster order processing, improved customer satisfaction',
                'timeline': '3-6 months'
            })

    def _create_executive_summary(self) -> None:
        """Create executive summary of key findings."""
        logger.info("Creating executive summary...")

        stats = self.analysis_results['statistics']
        classifications = self.analysis_results['classifications']

        # Key metrics for executive overview
        total_entities = sum(stats['entity_counts'].values())
        total_revenue = stats['financial_metrics']['total_order_value']
        avg_order_value = stats['financial_metrics']['average_order_value']

        self.executive_summary = {
            'overview': {
                'analysis_scope': f"Analyzed {total_entities} supply chain entities across 7 categories",
                'revenue_analyzed': f"${total_revenue:,.2f} in total order value",
                'average_order_size': f"${avg_order_value:,.2f} per order",
                'data_quality_score': f"{stats['data_quality']['data_integrity_score']:.1%}"
            },
            'key_findings': {
                'strengths': self._identify_key_strengths(),
                'opportunities': self._identify_key_opportunities(),
                'risks': self._identify_key_risks(),
                'quick_wins': self._identify_quick_wins()
            },
            'priority_actions': [rec for rec in self.strategic_recommendations if rec['priority'] == 'HIGH'],
            'financial_impact': {
                'potential_savings': self._calculate_potential_savings(),
                'revenue_opportunities': self._calculate_revenue_opportunities(),
                'risk_exposure': self._calculate_risk_exposure()
            }
        }

    # ===== ANALYTICAL HELPER METHODS =====

    def _calculate_health_score(self) -> float:
        """Calculate overall supply chain health score."""
        stats = self.analysis_results['statistics']

        # Weighted scoring factors
        factors = {
            'data_integrity': stats['data_quality']['data_integrity_score'] * 0.25,
            'supplier_performance': min(stats['operational_metrics']['average_supplier_rating'] / 5.0, 1.0) * 0.20,
            'capacity_efficiency': min(stats['operational_metrics']['average_capacity_utilization'] / 80.0, 1.0) * 0.20,
            'customer_satisfaction': min(len(self.analysis_results['classifications']['premium_customers']) /
                                         max(len(self.reasoner.retailers) * 0.3, 1), 1.0) * 0.20,
            'operational_stability': max(1.0 - len(self.analysis_results['classifications']['delayed_shipments']) /
                                         max(len(self.reasoner.shipments), 1), 0.0) * 0.15
        }

        return sum(factors.values()) * 100

    def _assess_supply_chain_risks(self) -> Dict[str, Any]:
        """Assess various supply chain risks."""
        classifications = self.analysis_results['classifications']

        return {
            'supplier_risk': 'HIGH' if len(classifications['critical_suppliers']) > 3 else 'MEDIUM' if len(classifications['critical_suppliers']) > 0 else 'LOW',
            'capacity_risk': 'HIGH' if len(classifications['overcapacity_warehouses']) > 2 else 'MEDIUM' if len(classifications['overcapacity_warehouses']) > 0 else 'LOW',
            'inventory_risk': 'HIGH' if len(classifications['low_stock_products']) > 5 else 'MEDIUM' if len(classifications['low_stock_products']) > 0 else 'LOW',
            'delivery_risk': 'HIGH' if len(classifications['delayed_shipments']) > 3 else 'MEDIUM' if len(classifications['delayed_shipments']) > 0 else 'LOW'
        }

    def _calculate_discount_efficiency(self) -> float:
        """Calculate the efficiency of discount programs."""
        stats = self.analysis_results['statistics']

        total_discounts = stats['financial_metrics']['total_discount_amount']
        total_revenue = stats['financial_metrics']['total_order_value']

        if total_revenue > 0:
            return (total_discounts / total_revenue) * 100
        return 0.0

    def _analyze_customer_value(self) -> Dict[str, Any]:
        """Analyze customer value distribution."""
        retailer_values = [(r.retailer_name, r.total_order_value)
                           for r in self.reasoner.retailers.values()]
        retailer_values.sort(key=lambda x: x[1], reverse=True)

        total_value = sum(
            r.total_order_value for r in self.reasoner.retailers.values())

        return {
            'top_customers': retailer_values[:5],
            'customer_concentration': retailer_values[0][1] / max(total_value, 1) if retailer_values else 0,
            'value_distribution': {
                'top_20_percent_share': sum(rv[1] for rv in retailer_values[:max(1, len(retailer_values)//5)]) / max(total_value, 1),
                'bottom_50_percent_share': sum(rv[1] for rv in retailer_values[len(retailer_values)//2:]) / max(total_value, 1)
            }
        }

    def _analyze_order_trends(self) -> Dict[str, Any]:
        """Analyze order size and frequency trends."""
        order_amounts = [o.total_amount for o in self.reasoner.orders.values()]

        return {
            'order_size_distribution': {
                'mean': np.mean(order_amounts) if order_amounts else 0,
                'median': np.median(order_amounts) if order_amounts else 0,
                'std_deviation': np.std(order_amounts) if order_amounts else 0,
                'large_order_percentage': len(self.analysis_results['classifications']['large_orders']) / max(len(order_amounts), 1) * 100
            },
            'order_patterns': {
                'urgent_order_rate': len(self.analysis_results['classifications']['urgent_orders']) / max(len(order_amounts), 1) * 100,
                'discount_utilization': len([o for o in self.reasoner.orders.values() if o.discount_amount > 0]) / max(len(order_amounts), 1) * 100
            }
        }

    def _analyze_inventory_management(self) -> Dict[str, Any]:
        """Analyze inventory management effectiveness."""
        classifications = self.analysis_results['classifications']

        return {
            'stock_health': {
                'low_stock_percentage': len(classifications['low_stock_products']) / max(len(self.reasoner.products), 1) * 100,
                'fast_moving_percentage': len(classifications['fast_moving_products']) / max(len(self.reasoner.products), 1) * 100,
                'slow_moving_percentage': len(classifications['slow_moving_products']) / max(len(self.reasoner.products), 1) * 100
            },
            'turnover_analysis': {
                'average_turnover': np.mean([p.turnover_rate for p in self.reasoner.products.values()]),
                'turnover_distribution': self._calculate_turnover_distribution()
            }
        }

    def _analyze_shipping_performance(self) -> Dict[str, Any]:
        """Analyze shipping and delivery performance."""
        classifications = self.analysis_results['classifications']

        return {
            'delivery_performance': {
                'on_time_percentage': (len(self.reasoner.shipments) - len(classifications['delayed_shipments'])) / max(len(self.reasoner.shipments), 1) * 100,
                'delayed_shipments': len(classifications['delayed_shipments']),
                'carrier_distribution': self._analyze_carrier_distribution()
            },
            'optimization_opportunities': {
                'consolidation_eligible': len([o for o in self.reasoner.orders.values() if o.shipping_optimization == "CONSOLIDATE_SHIPMENT"]),
                'priority_shipping_usage': len([o for o in self.reasoner.orders.values() if o.order_status == "PRIORITY_SHIPPING"])
            }
        }

    def _analyze_supplier_performance(self) -> Dict[str, Any]:
        """Analyze supplier performance metrics."""
        classifications = self.analysis_results['classifications']

        return {
            'supplier_quality': {
                'preferred_supplier_percentage': len(classifications['preferred_suppliers']) / max(len(self.reasoner.suppliers), 1) * 100,
                'critical_supplier_percentage': len(classifications['critical_suppliers']) / max(len(self.reasoner.suppliers), 1) * 100,
                'average_rating': np.mean([s.rating for s in self.reasoner.suppliers.values()]),
                'rating_distribution': self._calculate_rating_distribution()
            },
            'risk_factors': {
                'single_source_risk': len(classifications['critical_suppliers']),
                'geographic_concentration': self._analyze_geographic_distribution(),
                'performance_variability': np.std([s.rating for s in self.reasoner.suppliers.values()])
            }
        }

    def _analyze_manufacturing_efficiency(self) -> Dict[str, Any]:
        """Analyze manufacturing capacity and efficiency."""
        classifications = self.analysis_results['classifications']

        return {
            'capacity_metrics': {
                'high_volume_percentage': len(classifications['high_volume_manufacturers']) / max(len(self.reasoner.manufacturers), 1) * 100,
                'total_capacity': sum(m.manufacturing_capacity for m in self.reasoner.manufacturers.values()),
                'average_capacity': np.mean([m.manufacturing_capacity for m in self.reasoner.manufacturers.values()]),
                'capacity_distribution': self._calculate_capacity_distribution()
            },
            'efficiency_indicators': {
                'products_per_manufacturer': np.mean([len(m.product_ids) for m in self.reasoner.manufacturers.values()]),
                'manufacturer_utilization': self._estimate_manufacturer_utilization()
            }
        }

    def _analyze_quality_metrics(self) -> Dict[str, Any]:
        """Analyze quality metrics across the supply chain."""
        classifications = self.analysis_results['classifications']

        # Product quality requirements
        quality_required_products = [
            p for p in self.reasoner.products.values() if p.requires_quality_check]

        # Supplier quality metrics
        supplier_ratings = [s.rating for s in self.reasoner.suppliers.values()]
        delivery_rates = [
            s.on_time_delivery_rate for s in self.reasoner.suppliers.values()]

        return {
            'product_quality': {
                'quality_controlled_percentage': len(quality_required_products) / max(len(self.reasoner.products), 1) * 100,
                'pharmaceutical_products': len([p for p in self.reasoner.products.values() if "Pharmaceutical" in p.product_type]),
                'total_quality_products': len(quality_required_products)
            },
            'supplier_quality': {
                'average_rating': np.mean(supplier_ratings) if supplier_ratings else 0,
                'rating_std_deviation': np.std(supplier_ratings) if supplier_ratings else 0,
                'high_quality_suppliers': len([s for s in self.reasoner.suppliers.values() if s.rating >= 4.0]),
                'preferred_supplier_percentage': len(classifications['preferred_suppliers']) / max(len(self.reasoner.suppliers), 1) * 100
            },
            'delivery_quality': {
                'average_delivery_rate': np.mean(delivery_rates) if delivery_rates else 0,
                'on_time_performance': (len(self.reasoner.shipments) - len(classifications['delayed_shipments'])) / max(len(self.reasoner.shipments), 1) * 100,
                'delayed_shipment_count': len(classifications['delayed_shipments'])
            },
            'data_quality': {
                'integrity_score': self.analysis_results['statistics']['data_quality']['data_integrity_score'] * 100,
                'cardinality_violations': sum(len(v) for v in self.reasoner.cardinality_violations.values()),
                'relationship_completeness': self._calculate_relationship_completeness() * 100
            }
        }

    # ===== INSIGHT IDENTIFICATION METHODS =====

    def _identify_competitive_advantages(self) -> List[str]:
        """Identify competitive advantages from the analysis."""
        advantages = []

        stats = self.analysis_results['statistics']

        if stats['operational_metrics']['average_supplier_rating'] > 4.0:
            advantages.append(
                "Strong supplier relationships with high performance ratings")

        if stats['financial_metrics']['average_order_value'] > 25000:
            advantages.append(
                "High-value customer base with substantial order sizes")

        if len(self.analysis_results['classifications']['premium_customers']) > 0:
            advantages.append(
                "Established premium customer segment driving revenue")

        if stats['data_quality']['data_integrity_score'] > 0.9:
            advantages.append(
                "Excellent data quality enabling accurate analytics")

        return advantages

    def _identify_growth_opportunities(self) -> List[str]:
        """Identify growth opportunities from the analysis."""
        opportunities = []

        classifications = self.analysis_results['classifications']

        if len(classifications['fast_moving_products']) > 0:
            opportunities.append(
                "Expand production and marketing of fast-moving products")

        if len(classifications['high_volume_manufacturers']) > 0:
            opportunities.append(
                "Leverage high-volume manufacturing capabilities for scale")

        premium_ratio = len(
            classifications['premium_customers']) / max(len(self.reasoner.retailers), 1)
        if premium_ratio < 0.3:
            opportunities.append(
                "Significant potential to upgrade customers to premium tier")

        if len(classifications['preferred_suppliers']) > 2:
            opportunities.append(
                "Strong supplier base enables capacity expansion")

        return opportunities

    def _identify_bottlenecks(self) -> List[str]:
        """Identify operational bottlenecks."""
        bottlenecks = []

        classifications = self.analysis_results['classifications']

        if len(classifications['overcapacity_warehouses']) > 0:
            bottlenecks.append(
                "Warehouse capacity constraints limiting growth")

        if len(classifications['critical_suppliers']) > 0:
            bottlenecks.append(
                "Supplier dependency creating supply chain vulnerability")

        if len(classifications['low_stock_products']) > 0:
            bottlenecks.append(
                "Inventory shortages affecting order fulfillment")

        if len(classifications['delayed_shipments']) > 0:
            bottlenecks.append(
                "Shipping delays impacting customer satisfaction")

        return bottlenecks

    def _identify_key_strengths(self) -> List[str]:
        """Identify key organizational strengths."""
        return [
            "Comprehensive supply chain visibility and tracking",
            "Advanced analytics and reasoning capabilities",
            "Strong data integration across multiple entities",
            "Automated classification and optimization systems"
        ]

    def _identify_key_opportunities(self) -> List[str]:
        """Identify key improvement opportunities."""
        opportunities = []
        classifications = self.analysis_results['classifications']

        if len(classifications['critical_suppliers']) > 0:
            opportunities.append("Supplier diversification and risk reduction")

        if len(classifications['overcapacity_warehouses']) > 0:
            opportunities.append(
                "Capacity optimization and efficiency improvements")

        opportunities.append("Customer tier advancement and revenue growth")
        opportunities.append("Predictive analytics and automation enhancement")

        return opportunities

    def _identify_key_risks(self) -> List[str]:
        """Identify key business risks."""
        risks = []
        classifications = self.analysis_results['classifications']

        if len(classifications['critical_suppliers']) > 2:
            risks.append(
                "High supplier dependency and supply chain disruption risk")

        if len(classifications['delayed_shipments']) > 0:
            risks.append(
                "Delivery performance issues affecting customer satisfaction")

        if len(classifications['low_stock_products']) > 3:
            risks.append("Inventory shortages leading to potential stockouts")

        return risks

    def _identify_quick_wins(self) -> List[str]:
        """Identify quick win opportunities."""
        return [
            "Implement automated reorder points for low-stock products",
            "Optimize warehouse capacity allocation",
            "Enhance premium customer service offerings",
            "Automate urgent order processing workflows"
        ]

    # ===== CALCULATION HELPER METHODS =====

    def _calculate_premium_revenue_share(self) -> float:
        """Calculate revenue share from premium customers."""
        premium_customer_ids = set(
            self.analysis_results['classifications']['premium_customers'])
        premium_revenue = sum(o.total_amount for o in self.reasoner.orders.values()
                              if o.retailer_id in premium_customer_ids)
        total_revenue = sum(
            o.total_amount for o in self.reasoner.orders.values())
        return (premium_revenue / max(total_revenue, 1)) * 100

    def _calculate_large_order_contribution(self) -> float:
        """Calculate contribution of large orders to total revenue."""
        large_order_ids = set(
            self.analysis_results['classifications']['large_orders'])
        large_order_revenue = sum(o.total_amount for o in self.reasoner.orders.values()
                                  if o.id in large_order_ids)
        total_revenue = sum(
            o.total_amount for o in self.reasoner.orders.values())
        return (large_order_revenue / max(total_revenue, 1)) * 100

    def _calculate_supplier_diversity(self) -> float:
        """Calculate supplier diversity index."""
        manufacturer_supplier_counts = [
            len(m.supplier_ids) for m in self.reasoner.manufacturers.values()]
        if not manufacturer_supplier_counts:
            return 0.0
        return np.mean(manufacturer_supplier_counts)

    def _calculate_warehouse_efficiency(self) -> float:
        """Calculate warehouse efficiency score."""
        utilizations = [
            w.capacity_utilization for w in self.reasoner.warehouses.values()]
        if not utilizations:
            return 0.0

        # Optimal utilization is around 75-85%
        optimal_range = (75, 85)
        efficiency_scores = []

        for util in utilizations:
            if optimal_range[0] <= util <= optimal_range[1]:
                efficiency_scores.append(100)
            elif util < optimal_range[0]:
                efficiency_scores.append(util / optimal_range[0] * 100)
            else:
                efficiency_scores.append(
                    max(0, 100 - (util - optimal_range[1]) * 2))

        return np.mean(efficiency_scores)

    def _calculate_inventory_health(self) -> float:
        """Calculate inventory health score."""
        classifications = self.analysis_results['classifications']
        total_products = len(self.reasoner.products)

        if total_products == 0:
            return 0.0

        health_factors = {
            'low_stock_penalty': len(classifications['low_stock_products']) / total_products * -30,
            'fast_moving_bonus': len(classifications['fast_moving_products']) / total_products * 20,
            'slow_moving_penalty': len(classifications['slow_moving_products']) / total_products * -10
        }

        base_score = 70  # Base health score
        return max(0, base_score + sum(health_factors.values()))

    def _calculate_shipment_performance(self) -> float:
        """Calculate shipment performance score."""
        total_shipments = len(self.reasoner.shipments)
        delayed_shipments = len(
            self.analysis_results['classifications']['delayed_shipments'])

        if total_shipments == 0:
            return 100.0

        on_time_rate = (total_shipments - delayed_shipments) / total_shipments
        return on_time_rate * 100

    def _calculate_relationship_completeness(self) -> float:
        """Calculate relationship completeness score."""
        stats = self.analysis_results['statistics']['relationship_stats']

        # Count expected vs actual relationships
        expected_relationships = len(
            self.reasoner.suppliers) + len(self.reasoner.manufacturers) + len(self.reasoner.orders)
        actual_relationships = (stats['inverse_properties']['supplier_manufacturer_links'] +
                                stats['inverse_properties']['product_manufacturer_links'] +
                                stats['inverse_properties']['order_product_links'])

        return min(actual_relationships / max(expected_relationships, 1), 1.0)

    def _calculate_classification_coverage(self) -> float:
        """Calculate classification coverage score."""
        total_classifications = sum(
            len(v) for v in self.analysis_results['classifications'].values())
        total_entities = sum(
            self.analysis_results['statistics']['entity_counts'].values())

        return (total_classifications / max(total_entities, 1)) * 100

    def _calculate_processing_efficiency(self) -> float:
        """Calculate processing efficiency score."""
        violations = sum(len(v)
                         for v in self.reasoner.cardinality_violations.values())
        total_entities = sum(
            self.analysis_results['statistics']['entity_counts'].values())

        return max(0, (1 - violations / max(total_entities, 1)) * 100)

    def _calculate_resilience_score(self) -> float:
        """Calculate supply chain resilience score."""
        classifications = self.analysis_results['classifications']

        resilience_factors = {
            'supplier_diversity': min(len(self.reasoner.suppliers) / max(len(self.reasoner.manufacturers), 1), 3) / 3 * 25,
            'capacity_buffer': max(0, (100 - self.analysis_results['statistics']['operational_metrics']['average_capacity_utilization']) / 100) * 25,
            'quality_suppliers': len(classifications['preferred_suppliers']) / max(len(self.reasoner.suppliers), 1) * 25,
            'inventory_health': (1 - len(classifications['low_stock_products']) / max(len(self.reasoner.products), 1)) * 25
        }

        return sum(resilience_factors.values())

    def _calculate_automation_readiness(self) -> float:
        """Calculate automation readiness score."""
        data_quality = self.analysis_results['statistics']['data_quality']['data_integrity_score']
        classification_coverage = self._calculate_classification_coverage() / 100

        return (data_quality + classification_coverage) / 2 * 100

    def _calculate_scalability_index(self) -> float:
        """Calculate scalability index."""
        avg_capacity_util = self.analysis_results['statistics'][
            'operational_metrics']['average_capacity_utilization']
        high_volume_mfg_ratio = len(
            self.analysis_results['classifications']['high_volume_manufacturers']) / max(len(self.reasoner.manufacturers), 1)

        capacity_headroom = max(0, (100 - avg_capacity_util) / 100) * 50
        manufacturing_scale = high_volume_mfg_ratio * 50

        return capacity_headroom + manufacturing_scale

    def _calculate_innovation_potential(self) -> float:
        """Calculate innovation potential score."""
        premium_customer_ratio = len(
            self.analysis_results['classifications']['premium_customers']) / max(len(self.reasoner.retailers), 1)
        fast_moving_ratio = len(
            self.analysis_results['classifications']['fast_moving_products']) / max(len(self.reasoner.products), 1)

        return (premium_customer_ratio + fast_moving_ratio) / 2 * 100

    # ===== ADDITIONAL ANALYTICAL METHODS =====

    def _calculate_turnover_distribution(self) -> Dict[str, float]:
        """Calculate turnover rate distribution."""
        turnover_rates = [
            p.turnover_rate for p in self.reasoner.products.values()]

        return {
            'high_turnover': len([r for r in turnover_rates if r > 5.0]) / max(len(turnover_rates), 1) * 100,
            'medium_turnover': len([r for r in turnover_rates if 1.0 <= r <= 5.0]) / max(len(turnover_rates), 1) * 100,
            'low_turnover': len([r for r in turnover_rates if r < 1.0]) / max(len(turnover_rates), 1) * 100
        }

    def _analyze_carrier_distribution(self) -> Dict[str, int]:
        """Analyze carrier usage distribution."""
        carrier_counts = {}
        for shipment in self.reasoner.shipments.values():
            carrier = shipment.carrier
            carrier_counts[carrier] = carrier_counts.get(carrier, 0) + 1
        return carrier_counts

    def _calculate_rating_distribution(self) -> Dict[str, float]:
        """Calculate supplier rating distribution."""
        ratings = [s.rating for s in self.reasoner.suppliers.values()]

        return {
            'excellent': len([r for r in ratings if r >= 4.5]) / max(len(ratings), 1) * 100,
            'good': len([r for r in ratings if 3.5 <= r < 4.5]) / max(len(ratings), 1) * 100,
            'fair': len([r for r in ratings if 2.5 <= r < 3.5]) / max(len(ratings), 1) * 100,
            'poor': len([r for r in ratings if r < 2.5]) / max(len(ratings), 1) * 100
        }

    def _analyze_geographic_distribution(self) -> Dict[str, int]:
        """Analyze geographic distribution of suppliers."""
        location_counts = {}
        for supplier in self.reasoner.suppliers.values():
            location = supplier.supplier_location
            location_counts[location] = location_counts.get(location, 0) + 1
        return location_counts

    def _calculate_capacity_distribution(self) -> Dict[str, float]:
        """Calculate manufacturing capacity distribution."""
        capacities = [
            m.manufacturing_capacity for m in self.reasoner.manufacturers.values()]

        return {
            'large_capacity': len([c for c in capacities if c > 10000]) / max(len(capacities), 1) * 100,
            'medium_capacity': len([c for c in capacities if 5000 <= c <= 10000]) / max(len(capacities), 1) * 100,
            'small_capacity': len([c for c in capacities if c < 5000]) / max(len(capacities), 1) * 100
        }

    def _estimate_manufacturer_utilization(self) -> float:
        """Estimate average manufacturer utilization."""
        # Simplified estimation based on product count vs capacity
        utilizations = []
        for manufacturer in self.reasoner.manufacturers.values():
            if manufacturer.manufacturing_capacity > 0:
                product_load = len(manufacturer.product_ids)
                estimated_util = min(
                    (product_load / manufacturer.manufacturing_capacity) * 1000, 100)
                utilizations.append(estimated_util)

        return np.mean(utilizations) if utilizations else 0.0

    def _calculate_potential_savings(self) -> float:
        """Calculate potential cost savings from recommendations."""
        # Estimate savings from capacity optimization, supplier diversification, etc.
        base_revenue = self.analysis_results['statistics']['financial_metrics']['total_order_value']
        estimated_savings_percentage = 0.05  # 5% potential savings
        return base_revenue * estimated_savings_percentage

    def _calculate_revenue_opportunities(self) -> float:
        """Calculate potential revenue opportunities."""
        # Estimate revenue growth from customer tier advancement, etc.
        base_revenue = self.analysis_results['statistics']['financial_metrics']['total_order_value']
        estimated_growth_percentage = 0.15  # 15% potential growth
        return base_revenue * estimated_growth_percentage

    def _calculate_risk_exposure(self) -> float:
        """Calculate financial risk exposure."""
        # Estimate risk exposure from supply chain vulnerabilities
        base_revenue = self.analysis_results['statistics']['financial_metrics']['total_order_value']

        risk_factors = {
            'supplier_risk': len(self.analysis_results['classifications']['critical_suppliers']) * 0.02,
            'capacity_risk': len(self.analysis_results['classifications']['overcapacity_warehouses']) * 0.01,
            'inventory_risk': len(self.analysis_results['classifications']['low_stock_products']) * 0.005
        }

        total_risk_percentage = min(
            sum(risk_factors.values()), 0.20)  # Cap at 20%
        return base_revenue * total_risk_percentage

    # ===== OUTPUT GENERATION METHODS =====

    def export_json_report(self, filename: Optional[str] = None) -> str:
        """Export comprehensive analysis results to JSON."""
        if not filename:
            filename = f"supply_chain_analysis_{self.report_timestamp.strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.output_location / filename

        # Run analysis if not already done
        if not self.analysis_results:
            analytics_results = self.run_comprehensive_analysis()
        else:
            analytics_results = {
                'core_analysis': self.analysis_results,
                'business_insights': self.business_insights,
                'performance_metrics': self.performance_metrics,
                'strategic_recommendations': self.strategic_recommendations,
                'executive_summary': self.executive_summary
            }

        # Make JSON serializable
        def make_serializable(obj):
            if isinstance(obj, (set, frozenset)):
                return list(obj)
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            return obj

        # Deep convert to serializable format
        import json
        serializable_results = json.loads(json.dumps(
            analytics_results, default=make_serializable))

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)

        logger.info(f"JSON report exported to {filepath}")
        return str(filepath)

    def generate_markdown_report(self, filename: Optional[str] = None) -> str:
        """Generate comprehensive markdown report."""
        if not filename:
            filename = "supply_chain_report.md"

        filepath = self.output_location / filename

        # Run analysis if not already done
        if not self.analysis_results:
            self.run_comprehensive_analysis()

        # Generate markdown content
        stats = self.analysis_results['statistics']

        markdown = """# Supply Chain Analysis Report

    ## Executive Summary

    """

        # Add key metrics
        markdown += f"""### Key Metrics
    - **Total Entities Analyzed**: {sum(stats['entity_counts'].values()):,}
    - **Total Revenue**: ${stats['financial_metrics']['total_order_value']:,.2f}
    - **Average Order Value**: ${stats['financial_metrics']['average_order_value']:,.2f}
    - **Data Integrity Score**: {stats['data_quality']['data_integrity_score']:.1%}
    - **Supply Chain Health Score**: {self.business_insights['supply_chain_health']['overall_health_score']:.1f}/100

    ### Key Findings

    #### Strengths
    """

        # Add strengths
        for strength in self.executive_summary['key_findings']['strengths']:
            markdown += f"- {strength}\n"

        markdown += "\n#### Opportunities\n"

        # Add opportunities
        for opp in self.executive_summary['key_findings']['opportunities']:
            markdown += f"- {opp}\n"

        markdown += "\n#### Risks\n"

        # Add risks
        for risk in self.executive_summary['key_findings']['risks']:
            markdown += f"- {risk}\n"

        # Business Intelligence section
        markdown += f"""

    ## Business Intelligence Insights

    ### Supply Chain Health
    - **Overall Health Score**: {self.business_insights['supply_chain_health']['overall_health_score']:.1f}/100
    - **Critical Supplier Ratio**: {self.business_insights['supply_chain_health']['critical_supplier_ratio']:.1%}
    - **Capacity Utilization**: {self.business_insights['supply_chain_health']['capacity_utilization_efficiency']:.1f}%
    - **Premium Customer Penetration**: {self.business_insights['supply_chain_health']['premium_customer_penetration']:.1%}

    ### Financial Performance
    - **Total Revenue**: ${self.business_insights['financial_performance']['revenue_optimization']['total_revenue']:,.2f}
    - **Total Discounts**: ${self.business_insights['financial_performance']['revenue_optimization']['discount_impact']:,.2f}
    - **Net Revenue**: ${self.business_insights['financial_performance']['revenue_optimization']['revenue_after_discounts']:,.2f}
    - **Discount Efficiency**: {self.business_insights['financial_performance']['revenue_optimization']['discount_efficiency']:.2f}%

    ## Entity Analysis

    ### Suppliers ({len(self.reasoner.suppliers)})
    - **Preferred Suppliers**: {len(self.analysis_results['classifications']['preferred_suppliers'])}
    - **Critical Suppliers**: {len(self.analysis_results['classifications']['critical_suppliers'])}
    - **Average Rating**: {stats['operational_metrics']['average_supplier_rating']:.2f}/5.0

    ### Manufacturers ({len(self.reasoner.manufacturers)})
    - **High Volume Manufacturers**: {len(self.analysis_results['classifications']['high_volume_manufacturers'])}
    - **Total Capacity**: {stats['operational_metrics']['total_manufacturing_capacity']:,}
    - **Average Capacity**: {stats['operational_metrics']['total_manufacturing_capacity'] / max(len(self.reasoner.manufacturers), 1):,.0f}

    ### Warehouses ({len(self.reasoner.warehouses)})
    - **Overcapacity Warehouses**: {len(self.analysis_results['classifications']['overcapacity_warehouses'])}
    - **Average Utilization**: {stats['operational_metrics']['average_capacity_utilization']:.1f}%
    - **Total Storage Capacity**: {sum(w.storage_capacity for w in self.reasoner.warehouses.values()):,}

    ### Products ({len(self.reasoner.products)})
    - **Fast Moving Products**: {len(self.analysis_results['classifications']['fast_moving_products'])}
    - **Slow Moving Products**: {len(self.analysis_results['classifications']['slow_moving_products'])}
    - **Low Stock Products**: {len(self.analysis_results['classifications']['low_stock_products'])}

    ### Orders ({len(self.reasoner.orders)})
    - **Large Orders**: {len(self.analysis_results['classifications']['large_orders'])}
    - **Urgent Orders**: {len(self.analysis_results['classifications']['urgent_orders'])}
    - **Average Order Value**: ${stats['financial_metrics']['average_order_value']:,.2f}

    ### Customers ({len(self.reasoner.retailers)})
    - **Premium Customers**: {len(self.analysis_results['classifications']['premium_customers'])}
    - **Total Customer Value**: ${sum(r.total_order_value for r in self.reasoner.retailers.values()):,.2f}

    ## Performance Metrics

    ### Financial KPIs
    - **Revenue per Order**: ${self.performance_metrics['financial_kpis']['revenue_per_order']:,.2f}
    - **Discount Penetration**: {self.performance_metrics['financial_kpis']['discount_penetration_rate']:.1f}%
    - **Premium Revenue Share**: {self.performance_metrics['financial_kpis']['premium_customer_revenue_share']:.1f}%
    - **Large Order Contribution**: {self.performance_metrics['financial_kpis']['large_order_contribution']:.1f}%

    ### Operational KPIs
    - **Supplier Diversity Index**: {self.performance_metrics['operational_kpis']['supplier_diversity_index']:.2f}
    - **Warehouse Efficiency**: {self.performance_metrics['operational_kpis']['warehouse_efficiency_score']:.1f}%
    - **Inventory Health**: {self.performance_metrics['operational_kpis']['inventory_turnover_health']:.1f}%
    - **Shipment Performance**: {self.performance_metrics['operational_kpis']['shipment_performance_score']:.1f}%

    ### Strategic KPIs
    - **Supply Chain Resilience**: {self.performance_metrics['strategic_kpis']['supply_chain_resilience']:.1f}%
    - **Automation Readiness**: {self.performance_metrics['strategic_kpis']['automation_readiness']:.1f}%
    - **Scalability Index**: {self.performance_metrics['strategic_kpis']['scalability_index']:.1f}%
    - **Innovation Potential**: {self.performance_metrics['strategic_kpis']['innovation_potential']:.1f}%

    ## Strategic Recommendations

    """

        # Generate recommendations section separately to avoid f-string nesting issues
        for rec in self.strategic_recommendations:
            markdown += f"""### {rec['title']} (Priority: {rec['priority']})
    **Category**: {rec['category']}  
    **Description**: {rec['description']}  
    **Impact**: {rec['impact']}  
    **Timeline**: {rec['timeline']}

    **Action Items**:
    """
            for item in rec['action_items']:
                markdown += f"- {item}\n"

            markdown += f"""
    **Expected Benefit**: {rec['expected_benefit']}

    ---

    """

        # Risk Assessment section
        markdown += "## Risk Assessment\n\n### Supply Chain Risks\n"

        for risk_type, level in self.business_insights['supply_chain_health']['risk_assessment'].items():
            risk_name = risk_type.replace('_', ' ').title()
            markdown += f"- **{risk_name}**: {level}\n"

        markdown += f"""
    ### Financial Impact Projections
    - **Potential Savings**: ${self.executive_summary['financial_impact']['potential_savings']:,.2f}
    - **Revenue Opportunities**: ${self.executive_summary['financial_impact']['revenue_opportunities']:,.2f}
    - **Risk Exposure**: ${self.executive_summary['financial_impact']['risk_exposure']:,.2f}

    ## Data Quality Assessment

    - **Data Integrity Score**: {stats['data_quality']['data_integrity_score']:.1%}
    - **Relationship Completeness**: {self.performance_metrics['quality_kpis']['relationship_completeness']:.1%}
    - **Classification Coverage**: {self.performance_metrics['quality_kpis']['classification_coverage']:.1f}%
    - **Processing Efficiency**: {self.performance_metrics['quality_kpis']['processing_efficiency']:.1f}%

    ## Conclusion

    This comprehensive supply chain analysis has evaluated {sum(stats['entity_counts'].values())} entities across your supply chain network. The analysis reveals a {self.business_insights['supply_chain_health']['overall_health_score']:.0f}% health score with significant opportunities for optimization and growth.

    **Immediate Action Required**: {len([rec for rec in self.strategic_recommendations if rec['priority'] == 'HIGH'])} high-priority recommendations require immediate attention.

    **Growth Potential**: Estimated revenue growth opportunity of ${self.executive_summary['financial_impact']['revenue_opportunities']:,.2f} through strategic improvements.

    **Risk Mitigation**: Address identified risks to prevent potential exposure of ${self.executive_summary['financial_impact']['risk_exposure']:,.2f}.

    ---
    *Report generated by Advanced Supply Chain Analytics Engine v1.0*
    """

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)

        logger.info(f"Markdown report generated at {filepath}")
        return str(filepath)


def main():
    """Main execution function for  supply chain analytics."""
    try:
        # Initialize analytics engine
        analytics_engine = SupplyChainAnalyticsEngine()

        # Run  analysis
        logger.info("Starting supply chain analytics...")
        results = analytics_engine.run_comprehensive_analysis()

        # Export results
        json_file = analytics_engine.export_json_report()
        markdown_file = analytics_engine.generate_markdown_report()

        # Print summary
        print("\n=== SUPPLY CHAIN ANALYTICS SUMMARY ===")
        print(
            f"Health Score: {analytics_engine.business_insights['supply_chain_health']['overall_health_score']:.1f}/100")
        print(
            f"Total Revenue: ${results['core_analysis']['statistics']['financial_metrics']['total_order_value']:,.2f}")
        print(
            f"Strategic Recommendations: {len(analytics_engine.strategic_recommendations)}")
        print(
            f"High Priority Actions: {len([r for r in analytics_engine.strategic_recommendations if r['priority'] == 'HIGH'])}")
        print(f"\nReports Generated:")
        print(f"- JSON Report: {json_file}")
        print(f"- Markdown Report: {markdown_file}")

        return results

    except Exception as e:
        logger.error(f"Analytics failed: {e}")
        raise


if __name__ == "__main__":
    main()
