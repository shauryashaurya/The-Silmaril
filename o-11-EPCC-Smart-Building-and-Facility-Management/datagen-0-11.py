import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from pathlib import Path


class SmartBuildingDataGenerator:
    def __init__(self, data_folder='./data'):
        self.data_folder = Path(data_folder)
        self.data_folder.mkdir(exist_ok=True)
        self.fake = Faker()

        # ID tracking for foreign keys
        self.building_ids = []
        self.floor_ids = []
        self.zone_ids = []
        self.equipment_ids = []
        self.supplier_ids = []

        # Configuration
        self.num_buildings = 8
        self.floors_per_building = (4, 12)
        self.zones_per_floor = (8, 20)
        self.equipment_per_zone = (3, 8)
        self.sensors_per_zone = (2, 5)

    def generate_all_data(self):
        """Generate complete dataset for smart building ontology"""
        print("Generating smart building sample data with Faker...")

        datasets = {}

        # Generate in dependency order
        datasets['Building'] = self.generate_buildings()
        datasets['Floor'] = self.generate_floors()
        datasets['Zone'] = self.generate_zones()
        datasets['EquipmentResource'] = self.generate_equipment()
        datasets['Sensor'] = self.generate_sensors()
        datasets['Supplier'] = self.generate_suppliers()
        datasets['Occupant'] = self.generate_occupants()
        datasets['OccupantGroup'] = self.generate_occupant_groups()
        datasets['MaintenanceTask'] = self.generate_maintenance_tasks()
        datasets['SimulationScenario'] = self.generate_simulation_scenarios()

        # Save all datasets as CSV
        for class_name, df in datasets.items():
            csv_path = self.data_folder / f"{class_name}.csv"
            df.to_csv(csv_path, index=False)
            print(
                f"Generated {len(df)} records for {class_name} -> {csv_path}")

        print(f"\nAll sample data saved to {self.data_folder}")
        return datasets

    def generate_buildings(self):
        """Generate building data"""
        buildings = []

        for i in range(self.num_buildings):
            building_id = f"B{i+1:03d}"
            self.building_ids.append(building_id)

            buildings.append({
                'buildingID': building_id,
                'buildingName': self.fake.company() + " " + random.choice(["Tower", "Center", "Complex", "Plaza"]),
                'totalFloors': random.randint(*self.floors_per_building),
                'managementCompany': self.fake.company() + " Management",
                # Some below 3.0 for violations
                'energyRating': round(random.uniform(1.8, 4.8), 1)
            })

        return pd.DataFrame(buildings)

    def generate_floors(self):
        """Generate floor data"""
        floors = []
        floor_counter = 1

        for building_id in self.building_ids:
            num_floors = random.randint(*self.floors_per_building)

            for floor_num in range(1, num_floors + 1):
                floor_id = f"F{floor_counter:03d}"
                self.floor_ids.append(floor_id)
                floor_counter += 1

                floors.append({
                    'floorID': floor_id,
                    'buildingID': building_id,
                    'floorNumber': floor_num,
                    'usableAreaSqFt': round(random.uniform(5000, 30000), 0),
                })

        return pd.DataFrame(floors)

    def generate_zones(self):
        """Generate zone data - targeting 300+ records"""
        zone_functions = [
            "Office", "Conference", "Reception", "Hallway", "ServerRoom",
            "Kitchen", "Storage", "Laboratory", "Workshop", "Lobby",
            "Restroom", "Break Room", "Training Room", "Data Center"
        ]

        zones = []
        zone_counter = 1

        for floor_id in self.floor_ids:
            num_zones = random.randint(*self.zones_per_floor)

            for zone_num in range(1, num_zones + 1):
                zone_id = f"Z{zone_counter:03d}"
                self.zone_ids.append(zone_id)
                zone_counter += 1

                zone_function = random.choice(zone_functions)
                area = round(random.uniform(150, 2500), 0)

                # Base capacity on area and function
                if zone_function in ["Office", "Conference"]:
                    capacity = int(area / 100)  # ~100 sq ft per person
                elif zone_function in ["Hallway", "Storage"]:
                    capacity = int(area / 200)  # Less dense
                else:
                    capacity = int(area / 150)

                capacity = max(5, capacity)  # Minimum 5

                zones.append({
                    'zoneID': zone_id,
                    'floorID': floor_id,
                    'zoneName': f"{zone_function} {zone_num:02d}",
                    'zoneFunction': zone_function,
                    'areaSqFt': area,
                    'occupancyCapacity': capacity
                })

        return pd.DataFrame(zones)

    def generate_equipment(self):
        """Generate equipment data - targeting 400+ records"""
        equipment_types = [
            "HVACUnit", "Lighting", "SecurityCam", "AccessControl",
            "FireSafety", "AirPurifier", "SmartThermostat", "ProjectorSystem",
            "SoundSystem", "NetworkSwitch", "UPS", "CoffeeMachine"
        ]

        statuses = ["Running", "Off", "Maintenance"]

        equipment = []
        equipment_counter = 1

        for zone_id in self.zone_ids:
            num_equipment = random.randint(*self.equipment_per_zone)

            for eq_num in range(1, num_equipment + 1):
                equipment_id = f"E{equipment_counter:04d}"
                self.equipment_ids.append(equipment_id)
                equipment_counter += 1

                equipment_type = random.choice(equipment_types)

                # Create energy waste scenarios - lighting running when zones empty
                if equipment_type == "Lighting":
                    status = "Running" if random.random() < 0.6 else random.choice(statuses)
                else:
                    status = random.choices(
                        statuses, weights=[0.7, 0.2, 0.1])[0]

                # Power ratings based on equipment type
                power_ranges = {
                    "HVACUnit": (3000, 8000),
                    "Lighting": (50, 500),
                    "SecurityCam": (15, 50),
                    "AccessControl": (25, 100),
                    "FireSafety": (100, 300),
                    "AirPurifier": (80, 200),
                    "SmartThermostat": (5, 15),
                    "ProjectorSystem": (200, 800),
                    "SoundSystem": (50, 300),
                    "NetworkSwitch": (25, 150),
                    "UPS": (500, 2000),
                    "CoffeeMachine": (800, 1500)
                }

                power_range = power_ranges.get(equipment_type, (50, 500))
                power_rating = round(random.uniform(*power_range), 0)

                equipment.append({
                    'equipmentID': equipment_id,
                    'zoneID': zone_id,
                    'equipmentType': equipment_type,
                    'status': status,
                    'powerRating': power_rating
                })

        return pd.DataFrame(equipment)

    def generate_sensors(self):
        """Generate sensor data - targeting 500+ records"""
        sensor_types = [
            "Temperature", "Occupancy", "AirQuality", "Light", "Humidity",
            "Motion", "Sound", "Smoke", "CO2", "Pressure", "Vibration"
        ]

        sensors = []
        sensor_counter = 1

        for zone_id in self.zone_ids:
            num_sensors = random.randint(*self.sensors_per_zone)

            for sensor_num in range(1, num_sensors + 1):
                sensor_id = f"S{sensor_counter:04d}"
                sensor_counter += 1

                sensor_type = random.choice(sensor_types)

                # Create stale data scenarios (20% of sensors)
                if random.random() < 0.2:
                    last_update = self.fake.date_time_between(
                        start_date='-72h', end_date='-25h'
                    )
                else:
                    last_update = self.fake.date_time_between(
                        start_date='-23h', end_date='now'
                    )

                # Generate realistic readings based on sensor type
                reading_ranges = {
                    "Temperature": (65, 85),
                    "Occupancy": (0, 25),
                    "AirQuality": (15, 95),  # Some below 50 for violations
                    "Light": (50, 1000),
                    "Humidity": (30, 70),
                    "Motion": (0, 1),
                    "Sound": (35, 80),
                    "Smoke": (0, 10),
                    "CO2": (300, 1200),
                    "Pressure": (29.5, 30.5),
                    "Vibration": (0, 100)
                }

                reading_range = reading_ranges.get(sensor_type, (0, 100))
                if sensor_type in ["Occupancy", "Motion"]:
                    current_reading = random.randint(*reading_range)
                else:
                    current_reading = round(random.uniform(*reading_range), 1)

                # Some sensors monitor equipment
                equipment_id = None
                if random.random() < 0.3 and self.equipment_ids:
                    equipment_id = random.choice(self.equipment_ids)

                sensors.append({
                    'sensorID': sensor_id,
                    'zoneID': zone_id,
                    'equipmentID': equipment_id,
                    'sensorType': sensor_type,
                    'currentReading': current_reading,
                    'lastUpdateTime': last_update.strftime('%Y-%m-%d %H:%M:%S')
                })

        return pd.DataFrame(sensors)

    def generate_suppliers(self):
        """Generate supplier data"""
        suppliers = []

        for i in range(15):
            supplier_id = f"SUP{i+1:03d}"
            self.supplier_ids.append(supplier_id)

            company_name = self.fake.company()
            suppliers.append({
                'supplierID': supplier_id,
                'supplierName': company_name + " " + random.choice(["Services", "Solutions", "Corp", "LLC"]),
                'contactEmail': self.fake.company_email()
            })

        return pd.DataFrame(suppliers)

    def generate_occupants(self):
        """Generate occupant data - targeting 300+ records"""
        roles = [
            "Employee", "Manager", "Director", "Guest", "Contractor",
            "Visitor", "Executive", "Technician", "Researcher", "Admin",
            "Analyst", "Engineer", "Specialist", "Coordinator"
        ]

        occupants = []
        occupant_counter = 1

        # Leave some zones empty for energy waste detection
        occupied_zones = random.sample(
            self.zone_ids, int(len(self.zone_ids) * 0.75))

        for zone_id in occupied_zones:
            num_occupants = random.randint(1, 15)

            for occ_num in range(1, num_occupants + 1):
                occupant_id = f"O{occupant_counter:04d}"
                occupant_counter += 1

                occupants.append({
                    'occupantID': occupant_id,
                    'zoneID': zone_id,
                    'occupantName': self.fake.name(),
                    'occupantRole': random.choice(roles),
                    'comfortPreference': round(random.uniform(68, 78), 1)
                })

        return pd.DataFrame(occupants)

    def generate_occupant_groups(self):
        """Generate occupant group data with capacity violations"""
        group_types = [
            "Engineering Team", "Sales Team", "Marketing Department",
            "Executive Team", "Research Group", "IT Support", "Facilities Team",
            "Security Team", "Visitors Group", "Contractors", "Training Class",
            "Project Team", "Advisory Board"
        ]

        occupant_types = ["Employees", "Visitors",
                          "Contractors", "Executives", "Trainees"]

        groups = []
        group_counter = 1

        # Create groups for subset of zones, some with capacity violations
        selected_zones = random.sample(
            self.zone_ids, min(50, len(self.zone_ids)))

        for zone_id in selected_zones:
            group_id = f"G{group_counter:03d}"
            group_counter += 1

            # Get realistic capacity (simulate from zone data)
            zone_capacity = random.randint(10, 80)

            # 25% chance of capacity violation
            if random.random() < 0.25:
                occupant_count = zone_capacity + random.randint(5, 25)
            else:
                occupant_count = random.randint(1, max(1, zone_capacity - 5))

            groups.append({
                'groupID': group_id,
                'zoneID': zone_id,
                'groupName': random.choice(group_types),
                'occupantCount': occupant_count,
                'occupantType': random.choice(occupant_types)
            })

        return pd.DataFrame(groups)

    def generate_maintenance_tasks(self):
        """Generate maintenance task data with scheduling errors"""
        descriptions = [
            "HVAC Filter Replacement", "Lighting System Upgrade", "Replace LED Fixtures",
            "Security Camera Maintenance", "Fire System Inspection", "HVAC Calibration",
            "Replace Network Equipment", "Sensor Battery Replacement", "Access Control Update",
            "Emergency System Test", "Replace Air Purifier Filters", "Thermostat Calibration",
            "Replace UPS Batteries", "Clean HVAC Ducts", "Update Firmware"
        ]

        statuses = ["Scheduled", "InProgress", "Completed", "Cancelled"]

        tasks = []
        task_counter = 1

        # Generate tasks for subset of equipment
        selected_equipment = random.sample(
            self.equipment_ids, min(100, len(self.equipment_ids)))

        for equipment_id in selected_equipment:
            task_id = f"T{task_counter:04d}"
            task_counter += 1

            # Generate start and end times
            start_time = self.fake.date_time_between(
                start_date='-30d', end_date='+30d')

            # 15% chance of scheduling error (end before start)
            if random.random() < 0.15:
                end_time = start_time - timedelta(hours=random.randint(1, 8))
            else:
                end_time = start_time + timedelta(hours=random.randint(1, 24))

            tasks.append({
                'taskID': task_id,
                'equipmentID': equipment_id,
                'supplierID': random.choice(self.supplier_ids),
                'description': random.choice(descriptions),
                'plannedStartTime': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'plannedEndTime': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'taskStatus': random.choice(statuses)
            })

        return pd.DataFrame(tasks)

    def generate_simulation_scenarios(self):
        """Generate simulation scenario data"""
        scenario_types = [
            "HVAC System Failure", "Power Outage", "Fire Emergency",
            "Security Breach", "Network Failure", "Elevator Malfunction",
            "Water Leak", "Air Quality Crisis", "Equipment Overload",
            "Occupancy Surge", "Temperature Control Failure"
        ]

        scenarios = []

        for i in range(25):
            scenario_id = f"SC{i+1:03d}"
            scenario_type = random.choice(scenario_types)

            # Select random zones and equipment for scenario
            focus_zones = random.sample(self.zone_ids, random.randint(1, 5))
            fail_equipment = random.sample(
                self.equipment_ids, random.randint(0, 3))

            scenarios.append({
                'scenarioID': scenario_id,
                # Primary zone
                'zoneID': focus_zones[0] if focus_zones else None,
                # Primary equipment
                'equipmentID': fail_equipment[0] if fail_equipment else None,
                'scenarioName': f"{scenario_type} Simulation {i+1}",
                'hypothesis': f"What happens when {scenario_type.lower()} occurs in zone {focus_zones[0] if focus_zones else 'N/A'}",
                'predictedOutcome': self.fake.sentence(nb_words=10)
            })

        return pd.DataFrame(scenarios)


def main():
    """Generate all sample data"""
    generator = SmartBuildingDataGenerator()
    datasets = generator.generate_all_data()

    print(f"\nData generation summary:")
    for class_name, df in datasets.items():
        print(f"  {class_name}: {len(df)} records")

    total_records = sum(len(df) for df in datasets.values())
    print(f"\nTotal records generated: {total_records}")

    return datasets


if __name__ == "__main__":
    datasets = main()
