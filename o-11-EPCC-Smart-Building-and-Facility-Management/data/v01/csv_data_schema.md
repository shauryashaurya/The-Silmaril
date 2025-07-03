# CSV Data Schema

This file summarizes the headers of all CSV files found in the `v01` folder.

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
floorID,buildingID,floorNumber,usableAreaSqFt,occupancyCapacity
```
---

## File: `MaintenanceTask.csv`
**Header:**
```csv
taskID,equipmentID,description,plannedStartTime,plannedEndTime,taskStatus
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
sensorID,zoneID,sensorType,currentReading,lastUpdateTime
```
---

## File: `Zone.csv`
**Header:**
```csv
zoneID,floorID,zoneName,zoneFunction,areaSqFt
```
---

