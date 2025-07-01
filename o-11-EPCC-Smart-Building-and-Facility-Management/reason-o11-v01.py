import pandas as pd
import numpy as np
from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef
from rdflib.namespace import XSD
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class OntologyReasoner:
    def __init__(self, ontology_path, data_folder):
        self.graph = Graph()
        self.ontology_path = ontology_path
        self.data_folder = Path(data_folder)
        self.namespace = Namespace("http://example.org/smartbuilding#")
        self.violations = []
        self.insights = []

    def load_ontology(self):
        self.graph.parse(self.ontology_path, format='n3')
        print(f"Loaded ontology with {len(self.graph)} triples")

    def get_classes(self):
        classes = set()
        for s, p, o in self.graph.triples((None, RDF.type, RDFS.Class)):
            class_name = str(s).split('#')[-1]
            if not class_name.startswith('_'):
                classes.add(class_name)
        return classes

    def load_csv_data(self):
        classes = self.get_classes()
        data_loaded = {}

        for class_name in classes:
            csv_path = self.data_folder / f"{class_name}.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                data_loaded[class_name] = df
                self.add_instances_to_graph(class_name, df)
                print(f"Loaded {len(df)} instances of {class_name}")
            else:
                print(f"Warning: {csv_path} not found")

        return data_loaded

    def add_instances_to_graph(self, class_name, df):
        class_uri = self.namespace[class_name]

        for _, row in df.iterrows():
            instance_id = row.iloc[0]
            instance_uri = self.namespace[f"{class_name}_{instance_id}"]
            self.graph.add((instance_uri, RDF.type, class_uri))

            for col_name, value in row.items():
                if pd.notna(value):
                    prop_uri = self.namespace[col_name]
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
        if 'Floor' in data_loaded and 'Building' in data_loaded:
            floor_df = data_loaded['Floor']
            if 'buildingID' in floor_df.columns:
                for _, row in floor_df.iterrows():
                    floor_uri = self.namespace[f"Floor_{row['floorID']}"]
                    building_uri = self.namespace[f"Building_{row['buildingID']}"]
                    self.graph.add(
                        (building_uri, self.namespace.hasFloor, floor_uri))

        if 'Zone' in data_loaded and 'Floor' in data_loaded:
            zone_df = data_loaded['Zone']
            if 'floorID' in zone_df.columns:
                for _, row in zone_df.iterrows():
                    zone_uri = self.namespace[f"Zone_{row['zoneID']}"]
                    floor_uri = self.namespace[f"Floor_{row['floorID']}"]
                    self.graph.add(
                        (floor_uri, self.namespace.hasZone, zone_uri))

        if 'EquipmentResource' in data_loaded:
            equipment_df = data_loaded['EquipmentResource']
            if 'zoneID' in equipment_df.columns:
                for _, row in equipment_df.iterrows():
                    equipment_uri = self.namespace[f"EquipmentResource_{row['equipmentID']}"]
                    zone_uri = self.namespace[f"Zone_{row['zoneID']}"]
                    self.graph.add(
                        (equipment_uri, self.namespace.locatedIn, zone_uri))

        if 'Sensor' in data_loaded:
            sensor_df = data_loaded['Sensor']
            if 'zoneID' in sensor_df.columns:
                for _, row in sensor_df.iterrows():
                    sensor_uri = self.namespace[f"Sensor_{row['sensorID']}"]
                    if pd.notna(row.get('zoneID')):
                        zone_uri = self.namespace[f"Zone_{row['zoneID']}"]
                        self.graph.add(
                            (sensor_uri, self.namespace.monitorsZone, zone_uri))
                    if pd.notna(row.get('equipmentID')):
                        equipment_uri = self.namespace[f"EquipmentResource_{row['equipmentID']}"]
                        self.graph.add(
                            (sensor_uri, self.namespace.monitorsEquipment, equipment_uri))

        print(
            f"Graph now contains {len(self.graph)} triples after adding relationships")

    def apply_reasoning_rules(self, data_loaded):
        self.check_sensor_data_freshness(data_loaded)
        self.check_zone_capacity_violations(data_loaded)
        self.check_energy_waste_detection(data_loaded)
        self.check_maintenance_scheduling(data_loaded)
        self.check_equipment_status_conflicts(data_loaded)

    def check_sensor_data_freshness(self, data_loaded):
        if 'Sensor' not in data_loaded:
            return

        sensor_df = data_loaded['Sensor']
        if 'lastUpdateTime' in sensor_df.columns:
            current_time = pd.Timestamp.now()
            stale_sensors = []

            for _, row in sensor_df.iterrows():
                if pd.notna(row['lastUpdateTime']):
                    last_update = pd.to_datetime(row['lastUpdateTime'])
                    hours_old = (current_time -
                                 last_update).total_seconds() / 3600

                    if hours_old > 24:
                        violation = {
                            'rule': 'Sensor Data Freshness',
                            'sensor_id': row['sensorID'],
                            'hours_old': hours_old,
                            'severity': 'HIGH' if hours_old > 48 else 'MEDIUM'
                        }
                        self.violations.append(violation)
                        stale_sensors.append(row['sensorID'])

            if stale_sensors:
                self.insights.append(
                    f"Found {len(stale_sensors)} sensors with stale data")

    def check_zone_capacity_violations(self, data_loaded):
        if 'OccupantGroup' not in data_loaded or 'Zone' not in data_loaded:
            return

        occupant_df = data_loaded['OccupantGroup']
        zone_df = data_loaded['Zone']

        zone_capacity = dict(
            zip(zone_df['zoneID'], zone_df.get('occupancyCapacity', [])))

        violations_found = 0
        for _, row in occupant_df.iterrows():
            zone_id = row.get('zoneID')
            occupant_count = row.get('occupantCount', 0)

            if zone_id in zone_capacity:
                capacity = zone_capacity[zone_id]
                if occupant_count > capacity:
                    violation = {
                        'rule': 'Zone Capacity Violation',
                        'zone_id': zone_id,
                        'occupant_count': occupant_count,
                        'capacity': capacity,
                        'excess': occupant_count - capacity,
                        'severity': 'CRITICAL'
                    }
                    self.violations.append(violation)
                    violations_found += 1

        if violations_found:
            self.insights.append(
                f"Found {violations_found} zone capacity violations")

    def check_energy_waste_detection(self, data_loaded):
        if 'EquipmentResource' not in data_loaded or 'Zone' not in data_loaded:
            return

        equipment_df = data_loaded['EquipmentResource']
        occupant_df = data_loaded.get('Occupant', pd.DataFrame())

        occupied_zones = set(occupant_df.get('zoneID', []).dropna())

        waste_detected = 0
        for _, row in equipment_df.iterrows():
            if (row.get('equipmentType') == 'Lighting' and
                row.get('status') == 'Running' and
                    row.get('zoneID') not in occupied_zones):

                violation = {
                    'rule': 'Energy Waste Detection',
                    'equipment_id': row['equipmentID'],
                    'zone_id': row.get('zoneID'),
                    'type': 'Lighting in unoccupied zone',
                    'severity': 'MEDIUM'
                }
                self.violations.append(violation)
                waste_detected += 1

        if waste_detected:
            self.insights.append(
                f"Detected {waste_detected} energy waste opportunities")

    def check_maintenance_scheduling(self, data_loaded):
        if 'MaintenanceTask' not in data_loaded:
            return

        maintenance_df = data_loaded['MaintenanceTask']
        scheduling_errors = 0

        for _, row in maintenance_df.iterrows():
            start_time = pd.to_datetime(row.get('plannedStartTime'))
            end_time = pd.to_datetime(row.get('plannedEndTime'))

            if pd.notna(start_time) and pd.notna(end_time) and end_time <= start_time:
                violation = {
                    'rule': 'Maintenance Scheduling Error',
                    'task_id': row['taskID'],
                    'start_time': start_time,
                    'end_time': end_time,
                    'severity': 'HIGH'
                }
                self.violations.append(violation)
                scheduling_errors += 1

        if scheduling_errors:
            self.insights.append(
                f"Found {scheduling_errors} maintenance scheduling errors")

    def check_equipment_status_conflicts(self, data_loaded):
        if 'EquipmentResource' not in data_loaded or 'MaintenanceTask' not in data_loaded:
            return

        equipment_df = data_loaded['EquipmentResource']
        maintenance_df = data_loaded['MaintenanceTask']

        equipment_status = dict(
            zip(equipment_df['equipmentID'], equipment_df.get('status', [])))

        conflicts = 0
        for _, row in maintenance_df.iterrows():
            equipment_id = row.get('equipmentID')
            description = row.get('description', '')

            if (equipment_id in equipment_status and
                'Replace' in description and
                    equipment_status[equipment_id] not in ['Off', 'Maintenance']):

                violation = {
                    'rule': 'Equipment Status Conflict',
                    'equipment_id': equipment_id,
                    'current_status': equipment_status[equipment_id],
                    'attempted_action': 'Replace',
                    'severity': 'HIGH'
                }
                self.violations.append(violation)
                conflicts += 1

        if conflicts:
            self.insights.append(
                f"Found {conflicts} equipment status conflicts")

    def generate_summary_report(self):
        print("\n" + "="*50)
        print("ONTOLOGY REASONING SUMMARY REPORT")
        print("="*50)

        print(f"\nTotal violations found: {len(self.violations)}")
        print(f"Total insights generated: {len(self.insights)}")

        if self.violations:
            severity_counts = {}
            rule_counts = {}

            for violation in self.violations:
                severity = violation.get('severity', 'UNKNOWN')
                rule = violation.get('rule', 'UNKNOWN')

                severity_counts[severity] = severity_counts.get(
                    severity, 0) + 1
                rule_counts[rule] = rule_counts.get(rule, 0) + 1

            print("\nViolations by Severity:")
            for severity, count in sorted(severity_counts.items()):
                print(f"  {severity}: {count}")

            print("\nViolations by Rule:")
            for rule, count in sorted(rule_counts.items()):
                print(f"  {rule}: {count}")

        if self.insights:
            print("\nKey Insights:")
            for i, insight in enumerate(self.insights, 1):
                print(f"  {i}. {insight}")

        return {
            'violations': self.violations,
            'insights': self.insights,
            'summary': {
                'total_violations': len(self.violations),
                'total_insights': len(self.insights)
            }
        }

    def visualize_results(self, data_loaded):
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Smart Building Ontology Analysis Dashboard', fontsize=16)

        self.plot_violations_by_severity(axes[0, 0])
        self.plot_building_hierarchy(axes[0, 1], data_loaded)
        self.plot_equipment_status_distribution(axes[1, 0], data_loaded)
        self.plot_sensor_types_distribution(axes[1, 1], data_loaded)

        plt.tight_layout()
        plt.show()

        self.plot_building_network_graph(data_loaded)

    def plot_violations_by_severity(self, ax):
        if not self.violations:
            ax.text(0.5, 0.5, 'No violations found', ha='center', va='center')
            ax.set_title('Violations by Severity')
            return

        severity_counts = {}
        for violation in self.violations:
            severity = violation.get('severity', 'UNKNOWN')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        severities = list(severity_counts.keys())
        counts = list(severity_counts.values())
        colors = ['red' if s == 'CRITICAL' else 'orange' if s ==
                  'HIGH' else 'yellow' for s in severities]

        ax.bar(severities, counts, color=colors)
        ax.set_title('Violations by Severity')
        ax.set_ylabel('Count')

    def plot_building_hierarchy(self, ax, data_loaded):
        if 'Building' in data_loaded and 'Floor' in data_loaded:
            building_df = data_loaded['Building']
            floor_df = data_loaded['Floor']

            floors_per_building = floor_df.groupby('buildingID').size()

            ax.bar(range(len(floors_per_building)), floors_per_building.values)
            ax.set_title('Floors per Building')
            ax.set_xlabel('Building Index')
            ax.set_ylabel('Number of Floors')
        else:
            ax.text(0.5, 0.5, 'Building/Floor data not available',
                    ha='center', va='center')
            ax.set_title('Building Hierarchy')

    def plot_equipment_status_distribution(self, ax, data_loaded):
        if 'EquipmentResource' in data_loaded:
            equipment_df = data_loaded['EquipmentResource']
            status_counts = equipment_df['status'].value_counts()

            ax.pie(status_counts.values,
                   labels=status_counts.index, autopct='%1.1f%%')
            ax.set_title('Equipment Status Distribution')
        else:
            ax.text(0.5, 0.5, 'Equipment data not available',
                    ha='center', va='center')
            ax.set_title('Equipment Status Distribution')

    def plot_sensor_types_distribution(self, ax, data_loaded):
        if 'Sensor' in data_loaded:
            sensor_df = data_loaded['Sensor']
            type_counts = sensor_df['sensorType'].value_counts()

            ax.bar(type_counts.index, type_counts.values)
            ax.set_title('Sensor Types Distribution')
            ax.set_xlabel('Sensor Type')
            ax.set_ylabel('Count')
            ax.tick_params(axis='x', rotation=45)
        else:
            ax.text(0.5, 0.5, 'Sensor data not available',
                    ha='center', va='center')
            ax.set_title('Sensor Types Distribution')

    def plot_building_network_graph(self, data_loaded):
        G = nx.Graph()

        if 'Building' in data_loaded:
            for _, row in data_loaded['Building'].iterrows():
                G.add_node(f"B_{row['buildingID']}", type='Building', name=row.get(
                    'buildingName', ''))

        if 'Floor' in data_loaded:
            for _, row in data_loaded['Floor'].iterrows():
                floor_id = f"F_{row['floorID']}"
                G.add_node(floor_id, type='Floor',
                           number=row.get('floorNumber', ''))
                if 'buildingID' in row:
                    G.add_edge(f"B_{row['buildingID']}", floor_id)

        if 'Zone' in data_loaded:
            for _, row in data_loaded['Zone'].iterrows():
                zone_id = f"Z_{row['zoneID']}"
                G.add_node(zone_id, type='Zone',
                           function=row.get('zoneFunction', ''))
                if 'floorID' in row:
                    G.add_edge(f"F_{row['floorID']}", zone_id)

        if len(G.nodes()) > 0:
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(G, k=2, iterations=50)

            node_colors = []
            for node in G.nodes():
                if node.startswith('B_'):
                    node_colors.append('lightblue')
                elif node.startswith('F_'):
                    node_colors.append('lightgreen')
                elif node.startswith('Z_'):
                    node_colors.append('lightcoral')
                else:
                    node_colors.append('gray')

            nx.draw(G, pos, node_color=node_colors, with_labels=True,
                    node_size=500, font_size=8, font_weight='bold')

            plt.title('Building Hierarchy Network')
            plt.legend(['Buildings', 'Floors', 'Zones'], loc='upper right')
            plt.show()


def create_sample_data():
    data_folder = Path('./data')
    data_folder.mkdir(exist_ok=True)

    building_data = pd.DataFrame({
        'buildingID': ['B001', 'B002'],
        'buildingName': ['Main Office', 'Data Center'],
        'totalFloors': [5, 3],
        'managementCompany': ['FacilityCorpA', 'FacilityCorpB'],
        'energyRating': [4.2, 2.8]
    })

    floor_data = pd.DataFrame({
        'floorID': ['F001', 'F002', 'F003', 'F004', 'F005'],
        'buildingID': ['B001', 'B001', 'B001', 'B002', 'B002'],
        'floorNumber': [1, 2, 3, 1, 2],
        'usableAreaSqFt': [10000, 9500, 9500, 15000, 12000],
        'occupancyCapacity': [150, 140, 140, 200, 180]
    })

    zone_data = pd.DataFrame({
        'zoneID': ['Z001', 'Z002', 'Z003', 'Z004', 'Z005'],
        'floorID': ['F001', 'F001', 'F002', 'F003', 'F004'],
        'zoneName': ['Reception', 'Office Area A', 'Office Area B', 'Conference', 'Server Room'],
        'zoneFunction': ['Reception', 'Office', 'Office', 'Conference', 'ServerRoom'],
        'areaSqFt': [500, 4500, 4500, 1000, 8000]
    })

    equipment_data = pd.DataFrame({
        'equipmentID': ['E001', 'E002', 'E003', 'E004', 'E005'],
        'zoneID': ['Z001', 'Z002', 'Z003', 'Z004', 'Z005'],
        'equipmentType': ['Lighting', 'HVACUnit', 'Lighting', 'HVACUnit', 'SecurityCam'],
        'status': ['Running', 'Running', 'Running', 'Maintenance', 'Running'],
        'powerRating': [200, 5000, 300, 4500, 50]
    })

    sensor_data = pd.DataFrame({
        'sensorID': ['S001', 'S002', 'S003', 'S004', 'S005'],
        'zoneID': ['Z001', 'Z002', 'Z003', 'Z004', 'Z005'],
        'sensorType': ['Temperature', 'Occupancy', 'Temperature', 'AirQuality', 'Temperature'],
        'currentReading': [72.5, 0, 71.2, 45, 68.9],
        'lastUpdateTime': ['2024-01-01 09:00:00', '2024-01-01 10:30:00', '2023-12-20 08:00:00', '2024-01-01 11:00:00', '2024-01-01 09:45:00']
    })

    occupant_group_data = pd.DataFrame({
        'groupID': ['G001', 'G002', 'G003'],
        'zoneID': ['Z002', 'Z003', 'Z004'],
        'groupName': ['Engineering Team', 'Sales Team', 'Executive Team'],
        'occupantCount': [50, 30, 200],
        'occupantType': ['Employees', 'Employees', 'Employees']
    })

    maintenance_data = pd.DataFrame({
        'taskID': ['T001', 'T002', 'T003'],
        'equipmentID': ['E004', 'E001', 'E002'],
        'description': ['HVAC Filter Replacement', 'Replace LED Fixtures', 'HVAC Calibration'],
        'plannedStartTime': ['2024-01-02 09:00:00', '2024-01-03 10:00:00', '2024-01-04 14:00:00'],
        'plannedEndTime': ['2024-01-02 11:00:00', '2024-01-03 09:00:00', '2024-01-04 16:00:00'],
        'taskStatus': ['Scheduled', 'Scheduled', 'Scheduled']
    })

    datasets = {
        'Building': building_data,
        'Floor': floor_data,
        'Zone': zone_data,
        'EquipmentResource': equipment_data,
        'Sensor': sensor_data,
        'OccupantGroup': occupant_group_data,
        'MaintenanceTask': maintenance_data
    }

    for class_name, df in datasets.items():
        df.to_csv(data_folder / f"{class_name}.csv", index=False)

    print(f"Sample data created in {data_folder}")


def main():
    ontology_path = "./o-11-EPCC-Smart-Building-and-Facility-Management.n3"
    data_folder = "./data"

    if not Path(data_folder).exists() or not any(Path(data_folder).glob("*.csv")):
        print("Creating sample data...")
        create_sample_data()

    reasoner = OntologyReasoner(ontology_path, data_folder)

    try:
        reasoner.load_ontology()
    except FileNotFoundError:
        print(
            f"Ontology file {ontology_path} not found. Please ensure the file exists.")
        return

    data_loaded = reasoner.load_csv_data()
    reasoner.add_relationships_from_data(data_loaded)
    reasoner.apply_reasoning_rules(data_loaded)

    results = reasoner.generate_summary_report()
    reasoner.visualize_results(data_loaded)

    return results


if __name__ == "__main__":
    results = main()
