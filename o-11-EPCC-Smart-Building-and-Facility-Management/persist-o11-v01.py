import pandas as pd
import numpy as np
from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef
from rdflib.namespace import XSD
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class GraphExporter:
    def __init__(self, ontology_path, data_folder):
        self.graph = Graph()
        self.ontology_path = ontology_path
        self.data_folder = Path(data_folder)
        self.namespace = Namespace("http://example.org/smartbuilding#")

    def create_schema_only_ontology(self):
        """Create version of ontology without N3 rules for RDFLib parsing"""

        schema_path = self.data_folder / "smart_building_schema_only.ttl"

        with open(self.ontology_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split content at the rules section
        rules_start_markers = [
            "# N3 REASONING RULES",
            "# Building Structure and Hierarchy Validation",
            "# Smart building management rules",
            "# Reasoning Rules"
        ]

        schema_content = content
        for marker in rules_start_markers:
            if marker in content:
                schema_content = content.split(marker)[0]
                break

        # Ensure proper ending
        if not schema_content.strip().endswith('.'):
            schema_content += '\n'

        # Write schema-only version
        with open(schema_path, 'w', encoding='utf-8') as f:
            f.write(schema_content)

        print(f"Created schema-only ontology: {schema_path}")
        return schema_path

    def load_complete_graph(self):
        """Load ontology schema and populate with CSV data"""

        # Create and load schema-only version
        schema_path = self.create_schema_only_ontology()

        print("Loading ontology schema...")
        try:
            self.graph.parse(schema_path, format='turtle')
            print(f"Schema loaded: {len(self.graph)} triples")
        except Exception as e:
            print(f"Error loading schema: {e}")
            return None

        # Load and add CSV data
        data_loaded = self.load_csv_data()
        self.add_relationships_from_data(data_loaded)

        print(f"Complete graph loaded: {len(self.graph)} triples")
        return self.graph

    # def load_complete_graph(self):
    #     """Load ontology and populate with CSV data"""

    #     # Load the ontology structure
    #     print("Loading ontology...")
    #     self.graph.parse(self.ontology_path, format='turtle')
    #     print(f"Ontology loaded: {len(self.graph)} triples")

    #     # Load and add CSV data
    #     data_loaded = self.load_csv_data()
    #     self.add_relationships_from_data(data_loaded)

    #     print(f"Complete graph loaded: {len(self.graph)} triples")
    #     return self.graph

    def load_csv_data(self):
        """Load all CSV files and convert to RDF triples"""
        data_loaded = {}

        csv_files = list(self.data_folder.glob("*.csv"))
        print(f"Found {len(csv_files)} CSV files")

        for csv_file in csv_files:
            class_name = csv_file.stem
            try:
                df = pd.read_csv(csv_file)
                data_loaded[class_name] = df
                self.add_instances_to_graph(class_name, df)
                print(f"Loaded {len(df)} instances of {class_name}")
            except Exception as e:
                print(f"Error loading {csv_file}: {e}")

        return data_loaded

    def add_instances_to_graph(self, class_name, df):
        """Convert CSV data to RDF triples"""
        class_uri = self.namespace[class_name]

        for _, row in df.iterrows():
            # Use first column as instance identifier
            instance_id = row.iloc[0]
            instance_uri = self.namespace[f"{class_name}_{instance_id}"]

            # Add class assertion
            self.graph.add((instance_uri, RDF.type, class_uri))

            # Add data properties
            for col_name, value in row.items():
                if pd.notna(value):
                    prop_uri = self.namespace[col_name]

                    # Convert to appropriate RDF literal
                    if isinstance(value, str):
                        literal_value = Literal(value, datatype=XSD.string)
                    elif isinstance(value, (int, np.integer)):
                        literal_value = Literal(value, datatype=XSD.integer)
                    elif isinstance(value, (float, np.floating)):
                        literal_value = Literal(value, datatype=XSD.float)
                    else:
                        literal_value = Literal(str(value))

                    self.graph.add((instance_uri, prop_uri, literal_value))

    def add_relationships_from_data(self, data_loaded):
        """Add object property relationships based on foreign keys"""

        # Building -> Floor relationships
        if 'Floor' in data_loaded and 'buildingID' in data_loaded['Floor'].columns:
            for _, row in data_loaded['Floor'].iterrows():
                floor_uri = self.namespace[f"Floor_{row['floorID']}"]
                building_uri = self.namespace[f"Building_{row['buildingID']}"]
                self.graph.add(
                    (building_uri, self.namespace.hasFloor, floor_uri))

        # Floor -> Zone relationships
        if 'Zone' in data_loaded and 'floorID' in data_loaded['Zone'].columns:
            for _, row in data_loaded['Zone'].iterrows():
                zone_uri = self.namespace[f"Zone_{row['zoneID']}"]
                floor_uri = self.namespace[f"Floor_{row['floorID']}"]
                self.graph.add((floor_uri, self.namespace.hasZone, zone_uri))

        # Equipment -> Zone relationships
        if 'EquipmentResource' in data_loaded and 'zoneID' in data_loaded['EquipmentResource'].columns:
            for _, row in data_loaded['EquipmentResource'].iterrows():
                equipment_uri = self.namespace[f"EquipmentResource_{row['equipmentID']}"]
                zone_uri = self.namespace[f"Zone_{row['zoneID']}"]
                self.graph.add(
                    (equipment_uri, self.namespace.locatedIn, zone_uri))

        # Sensor -> Zone/Equipment relationships
        if 'Sensor' in data_loaded:
            for _, row in data_loaded['Sensor'].iterrows():
                sensor_uri = self.namespace[f"Sensor_{row['sensorID']}"]

                if 'zoneID' in row and pd.notna(row['zoneID']):
                    zone_uri = self.namespace[f"Zone_{row['zoneID']}"]
                    self.graph.add(
                        (sensor_uri, self.namespace.monitorsZone, zone_uri))

                if 'equipmentID' in row and pd.notna(row['equipmentID']):
                    equipment_uri = self.namespace[f"EquipmentResource_{row['equipmentID']}"]
                    self.graph.add(
                        (sensor_uri, self.namespace.monitorsEquipment, equipment_uri))

        # Occupant -> Zone relationships
        if 'Occupant' in data_loaded and 'zoneID' in data_loaded['Occupant'].columns:
            for _, row in data_loaded['Occupant'].iterrows():
                occupant_uri = self.namespace[f"Occupant_{row['occupantID']}"]
                zone_uri = self.namespace[f"Zone_{row['zoneID']}"]
                self.graph.add(
                    (occupant_uri, self.namespace.occupiesZone, zone_uri))

        # OccupantGroup -> Zone relationships
        if 'OccupantGroup' in data_loaded and 'zoneID' in data_loaded['OccupantGroup'].columns:
            for _, row in data_loaded['OccupantGroup'].iterrows():
                group_uri = self.namespace[f"OccupantGroup_{row['groupID']}"]
                zone_uri = self.namespace[f"Zone_{row['zoneID']}"]
                self.graph.add(
                    (group_uri, self.namespace.occupantGroupZone, zone_uri))

        # MaintenanceTask relationships
        if 'MaintenanceTask' in data_loaded:
            for _, row in data_loaded['MaintenanceTask'].iterrows():
                task_uri = self.namespace[f"MaintenanceTask_{row['taskID']}"]

                if 'equipmentID' in row and pd.notna(row['equipmentID']):
                    equipment_uri = self.namespace[f"EquipmentResource_{row['equipmentID']}"]
                    self.graph.add(
                        (task_uri, self.namespace.targetsEquipment, equipment_uri))

                if 'supplierID' in row and pd.notna(row['supplierID']):
                    supplier_uri = self.namespace[f"Supplier_{row['supplierID']}"]
                    self.graph.add(
                        (task_uri, self.namespace.performedBy, supplier_uri))

        # SimulationScenario relationships
        if 'SimulationScenario' in data_loaded:
            for _, row in data_loaded['SimulationScenario'].iterrows():
                scenario_uri = self.namespace[f"SimulationScenario_{row['scenarioID']}"]

                if 'zoneID' in row and pd.notna(row['zoneID']):
                    zone_uri = self.namespace[f"Zone_{row['zoneID']}"]
                    self.graph.add(
                        (scenario_uri, self.namespace.scenarioFocus, zone_uri))

                if 'equipmentID' in row and pd.notna(row['equipmentID']):
                    equipment_uri = self.namespace[f"EquipmentResource_{row['equipmentID']}"]
                    self.graph.add(
                        (scenario_uri, self.namespace.scenarioEquipmentFail, equipment_uri))

        print(f"Added relationships: {len(self.graph)} total triples")

    def save_graph_multiple_formats(self):
        """Save the complete graph in multiple RDF formats"""

        formats = {
            'turtle': 'smart_building_complete.ttl',
            'n3': 'smart_building_complete.n3',
            'xml': 'smart_building_complete.rdf',
            'json-ld': 'smart_building_complete.jsonld',
            'nt': 'smart_building_complete.nt'
        }

        saved_files = []

        for format_name, filename in formats.items():
            try:
                file_path = self.data_folder / filename
                self.graph.serialize(destination=str(
                    file_path), format=format_name)
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                print(
                    f"Saved {format_name.upper()} format: {filename} ({file_size_mb:.2f} MB)")
                saved_files.append(file_path)
            except Exception as e:
                print(f"Error saving {format_name} format: {e}")

        return saved_files

    # def generate_graph_statistics(self):
    #     """Generate comprehensive statistics about the graph"""

    #     stats = {
    #         'total_triples': len(self.graph),
    #         'classes': {},
    #         'properties': {},
    #         'instances': {}
    #     }

    #     # Count instances by class
    #     class_query = """
    #     SELECT ?class (COUNT(?instance) as ?count) WHERE {
    #         ?instance a ?class .
    #         FILTER(STRSTARTS(STR(?class), "http://example.org/smartbuilding#"))
    #     } GROUP BY ?class ORDER BY DESC(?count)
    #     """

    #     for row in self.graph.query(class_query):
    #         class_name = str(row['class']).split('#')[-1]
    #         stats['classes'][class_name] = int(row['count'])

    #     # Count property usage
    #     prop_query = """
    #     SELECT ?property (COUNT(*) as ?count) WHERE {
    #         ?s ?property ?o .
    #         FILTER(STRSTARTS(STR(?property), "http://example.org/smartbuilding#"))
    #     } GROUP BY ?property ORDER BY DESC(?count)
    #     """

    #     for row in self.graph.query(prop_query):
    #         prop_name = str(row['property']).split('#')[-1]
    #         stats['properties'][prop_name] = int(row['count'])

    #     # Additional statistics
    #     stats['unique_subjects'] = len(set(self.graph.subjects()))
    #     stats['unique_predicates'] = len(set(self.graph.predicates()))
    #     stats['unique_objects'] = len(set(self.graph.objects()))

    #     return stats

    def generate_graph_statistics(self):
        """Generate comprehensive statistics about the graph"""

        stats = {
            'total_triples': len(self.graph),
            'classes': {},
            'properties': {},
            'instances': {}
        }

        # Count instances by class - using bracket notation
        class_query = """
        PREFIX : <http://example.org/smartbuilding#>
        SELECT ?cls (COUNT(?instance) as ?cnt) WHERE {
            ?instance a ?cls .
            FILTER(STRSTARTS(STR(?cls), "http://example.org/smartbuilding#"))
        } GROUP BY ?cls ORDER BY DESC(?cnt)
        """

        try:
            for row in self.graph.query(class_query):
                class_name = str(row['cls']).split('#')[-1]
                stats['classes'][class_name] = int(row['cnt'])
        except Exception as e:
            print(f"Error in class query: {e}")

        # Count property usage - using bracket notation
        prop_query = """
        PREFIX : <http://example.org/smartbuilding#>
        SELECT ?prop (COUNT(*) as ?cnt) WHERE {
            ?s ?prop ?o .
            FILTER(STRSTARTS(STR(?prop), "http://example.org/smartbuilding#"))
        } GROUP BY ?prop ORDER BY DESC(?cnt)
        """

        try:
            for row in self.graph.query(prop_query):
                prop_name = str(row['prop']).split('#')[-1]
                stats['properties'][prop_name] = int(row['cnt'])
        except Exception as e:
            print(f"Error in property query: {e}")

        # Additional statistics
        stats['unique_subjects'] = len(set(self.graph.subjects()))
        stats['unique_predicates'] = len(set(self.graph.predicates()))
        stats['unique_objects'] = len(set(self.graph.objects()))

        return stats

    def print_graph_summary(self, stats):
        """Print formatted graph statistics"""

        print("\n" + "="*60)
        print("SMART BUILDING RDF GRAPH SUMMARY")
        print("="*60)

        print(f"\nGraph Statistics:")
        print(f"  Total triples: {stats['total_triples']:,}")
        print(f"  Unique subjects: {stats['unique_subjects']:,}")
        print(f"  Unique predicates: {stats['unique_predicates']:,}")
        print(f"  Unique objects: {stats['unique_objects']:,}")

        print(f"\nInstances by Class:")
        for class_name, count in sorted(stats['classes'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {class_name}: {count:,}")

        print(f"\nTop Properties by Usage:")
        top_props = sorted(stats['properties'].items(),
                           key=lambda x: x[1], reverse=True)[:15]
        for prop_name, count in top_props:
            print(f"  {prop_name}: {count:,}")

    def save_statistics_report(self, stats):
        """Save statistics to a text file"""

        report_path = self.data_folder / "graph_statistics_report.txt"

        with open(report_path, 'w') as f:
            f.write("SMART BUILDING RDF GRAPH STATISTICS REPORT\n")
            f.write("=" * 50 + "\n\n")

            f.write(
                f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("GRAPH OVERVIEW:\n")
            f.write(f"Total triples: {stats['total_triples']:,}\n")
            f.write(f"Unique subjects: {stats['unique_subjects']:,}\n")
            f.write(f"Unique predicates: {stats['unique_predicates']:,}\n")
            f.write(f"Unique objects: {stats['unique_objects']:,}\n\n")

            f.write("INSTANCES BY CLASS:\n")
            for class_name, count in sorted(stats['classes'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"{class_name}: {count:,}\n")

            f.write("\nPROPERTIES BY USAGE:\n")
            for prop_name, count in sorted(stats['properties'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"{prop_name}: {count:,}\n")

        print(f"Statistics report saved: {report_path}")
        return report_path


def main():
    """Load ontology with data and save complete graph"""

    ontology_path = "./o-11-EPCC-Smart-Building-and-Facility-Management.n3"
    data_folder = "./data"

    if not Path(ontology_path).exists():
        print(f"Ontology file {ontology_path} not found.")
        return

    if not Path(data_folder).exists():
        print(f"Data folder {data_folder} not found.")
        return

    # Initialize exporter
    exporter = GraphExporter(ontology_path, data_folder)

    # Load complete graph (ontology + data)
    graph = exporter.load_complete_graph()

    # Generate statistics
    stats = exporter.generate_graph_statistics()
    exporter.print_graph_summary(stats)

    # Save graph in multiple formats
    print(f"\nSaving complete graph...")
    saved_files = exporter.save_graph_multiple_formats()

    # Save statistics report
    exporter.save_statistics_report(stats)

    print(f"\nGraph export complete!")
    print(f"Files saved to: {data_folder}")

    return {
        'graph': graph,
        'statistics': stats,
        'saved_files': saved_files
    }


if __name__ == "__main__":
    results = main()
