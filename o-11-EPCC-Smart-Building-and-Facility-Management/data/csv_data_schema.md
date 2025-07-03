# CSV Data Schema

This file summarizes the headers of all CSV files found in the `data` folder.

---

## File: `Building.csv`
**Header:**
```csv
buildingID,buildingName,totalFloors,managementCompany,energyRating
```
---

## File: `EquipmentResource.csv`
**Header:**
```csv
equipmentID,zoneID,equipmentType,status,powerRating
```
---

## File: `Floor.csv`
**Header:**
```csv
floorID,buildingID,floorNumber,usableAreaSqFt
```
---

## File: `MaintenanceTask.csv`
**Header:**
```csv
taskID,equipmentID,supplierID,description,plannedStartTime,plannedEndTime,taskStatus
```
---

## File: `Occupant.csv`
**Header:**
```csv
occupantID,zoneID,occupantName,occupantRole,comfortPreference
```
---

## File: `OccupantGroup.csv`
**Header:**
```csv
groupID,zoneID,groupName,occupantCount,occupantType
```
---

## File: `Sensor.csv`
**Header:**
```csv
sensorID,zoneID,equipmentID,sensorType,currentReading,lastUpdateTime
```
---

## File: `SimulationScenario.csv`
**Header:**
```csv
scenarioID,zoneID,equipmentID,scenarioName,hypothesis,predictedOutcome
```
---

## File: `Supplier.csv`
**Header:**
```csv
supplierID,supplierName,contactEmail
```
---

## File: `Zone.csv`
**Header:**
```csv
zoneID,floorID,zoneName,zoneFunction,areaSqFt,occupancyCapacity
```
---

