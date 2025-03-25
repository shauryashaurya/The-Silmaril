# **Ontology #11** - **Smart Building / Facility Management**                       
                                    
---                                    
                                    
## A. High-Level Description                    
                    
1. **Domain**: A large commercial or institutional building (or campus) with:                    
   - **Floors** and **Zones** (subdivisions for occupant grouping).                      
   - **Equipment** resources (HVAC units, lighting, security devices).                      
   - **Sensors** (temperature, occupancy, air quality).                      
   - **OccupantGroups** or individual occupants.                      
   - **MaintenanceTasks** to keep equipment functional.                      
   - **SimulationScenarios** (e.g., “What if HVAC fails in Zone 3?”).                      
                    
2. **Purpose**: Provide a digital twin or **smart facility** approach, capturing:                    
   - **Real-time** or near real-time sensor data.                      
   - **Equipment** statuses (running, off, maintenance).                      
   - **Occupant** or occupant group patterns for comfort or security.                      
   - **Maintenance** scheduling.                      
   - Potential for **simulation** of “what if” equipment fails or occupant density changes.                    
                    
3. **Use Cases**:                    
   - **Real-Time Monitoring**: Summarize sensor readings, occupant comfort, equipment usage.                      
   - **Energy Efficiency**: Simulate equipment behavior under occupant load changes.                      
   - **Maintenance**: Identify tasks for failing equipment, assign technicians, or schedule tasks.                      
   - **Scenario**: “What if occupant density is 30% higher next week in floor 2’s zone B?” and see if HVAC can handle it.                      
                    
## B. Pseudocode (Classes, Data Properties, Object Properties, and Constraints)                    
                    
```plaintext                    
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
                    
```                    
                    
## Explanation & Use Cases                    
                    
- **Classes**:                     
  - `Building`, `Floor`, `Zone` handle the physical structure.                      
  - `EquipmentResource` and `Sensor` track the building’s devices.                      
  - `Occupant` or `OccupantGroup` represent the people.                      
  - `MaintenanceTask` ties equipment maintenance scheduling.                      
  - `Supplier` for external contractor references.                      
  - `SimulationScenario` for what-if logic.                    
                    
- **Object Properties** specify cardinalities. E.g., `hasFloor (Building -> Floor, 1-To-Many)` means each building has at least one floor. `scenarioFocus` might reference multiple zones or equipment.                      
- **Constraints** ensure domain consistency (like sensor reading staleness or occupant group capacity).          
          
          
          
# How This Ontology Works in Palantir Foundry (Not OWL)          
          
- Each **class** becomes a “**Type**” or “Object Type” referencing Foundry datasets or typed transformations (e.g., `Zone`, `EquipmentResource`, `Sensor`).            
- **Relationships** become typed reference fields: e.g. “EquipmentResource.locatedIn -> zoneID.”            
- **Constraints** or domain logic are usually enforced via **pipeline transforms** or **code-workbooks** that check if occupant count surpasses a zone’s capacity, etc. If a constraint is violated, you might see pipeline errors or special flags.            
- **Scenarios**: You can create separate Foundry branches to tweak data properties or relationships (like “Equipment X = status=Maintenance”). Then re-run the pipeline or code-workbook logic to see new outcomes.          
          
          
          
