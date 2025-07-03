# CSV Data Schema  
  
This file summarizes the headers and a sample data row of all CSV files found in the `v01` folder.  
  
---  
  
## File: `Building.csv`  
**Header:**  
```csv  
buildingID,buildingName,totalFloors,managementCompany,energyRating  
```  
**Example Data:**  
```csv  
B001,Main Office,5,FacilityCorpA,4.2  
```  
---  
  
## File: `EquipmentResource.csv`  
**Header:**  
```csv  
equipmentID,zoneID,equipmentType,status,powerRating  
```  
**Example Data:**  
```csv  
E001,Z001,Lighting,Running,200  
```  
---  
  
## File: `Floor.csv`  
**Header:**  
```csv  
floorID,buildingID,floorNumber,usableAreaSqFt,occupancyCapacity  
```  
**Example Data:**  
```csv  
F001,B001,1,10000,150  
```  
---  
  
## File: `MaintenanceTask.csv`  
**Header:**  
```csv  
taskID,equipmentID,description,plannedStartTime,plannedEndTime,taskStatus  
```  
**Example Data:**  
```csv  
T001,E004,HVAC Filter Replacement,2024-01-02 09:00:00,2024-01-02 11:00:00,Scheduled  
```  
---  
  
## File: `OccupantGroup.csv`  
**Header:**  
```csv  
groupID,zoneID,groupName,occupantCount,occupantType  
```  
**Example Data:**  
```csv  
G001,Z002,Engineering Team,50,Employees  
```  
---  
  
## File: `Sensor.csv`  
**Header:**  
```csv  
sensorID,zoneID,sensorType,currentReading,lastUpdateTime  
```  
**Example Data:**  
```csv  
S001,Z001,Temperature,72.5,2024-01-01 09:00:00  
```  
---  
  
## File: `Zone.csv`  
**Header:**  
```csv  
zoneID,floorID,zoneName,zoneFunction,areaSqFt  
```  
**Example Data:**  
```csv  
Z001,F001,Reception,Reception,500  
```  
---  
  
