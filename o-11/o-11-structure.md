# Ontology Structure                                                                  
                                                                        
```mermaid                                                                        
classDiagram
    Building "1" --> "*" Floor: hasFloor
    Building "1" --> "*" Supplier: contractedSupplier
    Floor "1" --> "*" Zone: hasZone
    Zone "1" <-- "*" EquipmentResource: locatedIn
    Zone "1" <-- "*" Sensor: monitorsZone
    Zone "1" <-- "*" Occupant: occupiesZone
    Zone "1" <-- "*" OccupantGroup: occupantGroupZone
    Zone "*" <-- "*" SimulationScenario: scenarioFocus
    EquipmentResource "1" <-- "*" Sensor: monitorsEquipment
    EquipmentResource "1" <-- "1" MaintenanceTask: targetsEquipment
    EquipmentResource "*" <-- "*" SimulationScenario: scenarioEquipmentFail
    EquipmentResource "*" <-- "*" Occupant: occupantUsesEquipment
    Supplier "1" <-- "*" MaintenanceTask: performedBy

    class Building {
        +string buildingID
        +string buildingName
        +int totalFloors
        +string managementCompany
        +float energyRating
    }
    class Floor {
        +string floorID
        +int floorNumber
        +float usableAreaSqFt
        +int occupancyCapacity
    }
    class Zone {
        +string zoneID
        +string zoneName
        +string zoneFunction
        +float areaSqFt
    }
    class EquipmentResource {
        +string equipmentID
        +string equipmentType
        +string status
        +float powerRating
    }
    class Sensor {
        +string sensorID
        +string sensorType
        +float currentReading
        +dateTime lastUpdateTime
    }
    class OccupantGroup {
        +string groupID
        +string groupName
        +int occupantCount
        +string occupantType
    }
    class Occupant {
        +string occupantID
        +string occupantName
        +string occupantRole
        +float comfortPreference
    }
    class MaintenanceTask {
        +string taskID
        +string description
        +dateTime plannedStartTime
        +dateTime plannedEndTime
        +string taskStatus
    }
    class Supplier {
        +string supplierID
        +string supplierName
        +string contactEmail
    }
    class SimulationScenario {
        +string scenarioID
        +string scenarioName
        +string hypothesis
        +string predictedOutcome
    }               
                   
```                                                           
                                                                      
---                                            
                                            
```pseudocode                                                  
// ======================          
// CLASSES & DATA PROPERTIES          
// ======================          
          
Class: Building          
  - buildingID: string          
  - buildingName: string          
  - totalFloors: int          
  - managementCompany: string          
  - energyRating: float          
          
Class: Floor          
  - floorID: string          
  - floorNumber: int          
  - usableAreaSqFt: float          
  - occupancyCapacity: int          
          
Class: Zone          
  - zoneID: string          
  - zoneName: string          
  - zoneFunction: string    // e.g., Office, Hallway, ServerRoom          
  - areaSqFt: float          
          
Class: EquipmentResource          
  - equipmentID: string          
  - equipmentType: string  // HVACUnit, Lighting, SecurityCam, etc.          
  - status: string         // Running, Off, Maintenance          
  - powerRating: float          
          
Class: Sensor          
  - sensorID: string          
  - sensorType: string     // Temperature, Occupancy, AirQuality          
  - currentReading: float          
  - lastUpdateTime: dateTime          
          
Class: OccupantGroup          
  - groupID: string          
  - groupName: string          
  - occupantCount: int          
  - occupantType: string   // e.g., Employees, Visitors          
          
Class: Occupant          
  - occupantID: string          
  - occupantName: string          
  - occupantRole: string   // e.g., Employee, Guest          
  - comfortPreference: float          
          
Class: MaintenanceTask          
  - taskID: string          
  - description: string          
  - plannedStartTime: dateTime          
  - plannedEndTime: dateTime          
  - taskStatus: string     // e.g. Scheduled, InProgress, Completed          
          
Class: Supplier          
  - supplierID: string          
  - supplierName: string          
  - contactEmail: string          
          
Class: SimulationScenario          
  - scenarioID: string          
  - scenarioName: string          
  - hypothesis: string     // e.g., "HVAC fails in zone 2"          
  - predictedOutcome: string          
          
// ======================          
// OBJECT PROPERTIES w/ CARDINALITIES          
// ======================          
          
// Building structure          
Relationship: hasFloor (Building → Floor, 1-To-Many)          
Relationship: hasZone (Floor → Zone, 0-To-Many)          
          
// Equipment & Zones          
Relationship: locatedIn (EquipmentResource → Zone, 0-To-1)          
          
// Sensors & Zones or Equipment          
Relationship: monitorsZone (Sensor → Zone, 0-To-1)          
Relationship: monitorsEquipment (Sensor → EquipmentResource, 0-To-1)          
          
// Occupants & Zones          
Relationship: occupiesZone (Occupant → Zone, 0-To-1)          
Relationship: occupantGroupZone (OccupantGroup → Zone, 0-To-Many)          
          
// Maintenance          
Relationship: targetsEquipment (MaintenanceTask → EquipmentResource, 1-To-1)          
Relationship: performedBy (MaintenanceTask → Supplier, 0-To-1)          
// or if you have Technicians, you can link them, but we keep it simple          
          
// Building Supplier relationships          
Relationship: contractedSupplier (Building → Supplier, 0-To-Many)          
          
// Simulation & Scenarios          
Relationship: scenarioFocus (SimulationScenario → Zone, 0-To-Many)          
Relationship: scenarioEquipmentFail (SimulationScenario → EquipmentResource, 0-To-Many)          
          
// Additional occupant/equipment relationships          
Relationship: occupantUsesEquipment (Occupant → EquipmentResource, 0-To-Many)          
          
// ======================          
// SAMPLE RULES/CONSTRAINTS          
// ======================          
          
// 1) If EquipmentResource.status = "Maintenance", sensor readings in that zone might be partial or flagged          
// 2) A Floor can have multiple zones but must have at least one if floorNumber > 0          
// 3) If occupantCount in OccupantGroup > zoneFunction capacity, occupantGroup must be split          
// 4) A MaintenanceTask must have plannedStartTime < plannedEndTime          
// 5) If building’s energyRating < X, we might require new sensors or maintenance tasks          
// 6) If scenarioFocus references multiple zones, each zone must belong to the same building for the scenario          
// 7) occupantUsesEquipment => occupant must be in the same zone or a super-zone for that equipment          
// 8) If lastUpdateTime > 24 hours old for a sensor, produce an alert or degrade reliability of currentReading          
// 9) Only an EquipmentResource with status="Off" or "Maintenance" can be replaced or upgraded          
          
                  
                         
'''                  
