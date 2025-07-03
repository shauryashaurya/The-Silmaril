# CSV Data Schema  
  
This file summarizes the headers and a sample data row of all CSV files found in the `data` folder.  
  
---  
  
## File: `Building.csv`  
**Header:**  
```csv  
buildingID,buildingName,totalFloors,managementCompany,energyRating  
```  
**Example Data:**  
```csv  
B001,"Russell, Hall and Hill Plaza",6,Ramsey LLC Management,2.0  
```  
---  
  
## File: `EquipmentResource.csv`  
**Header:**  
```csv  
equipmentID,zoneID,equipmentType,status,powerRating  
```  
**Example Data:**  
```csv  
E0001,Z001,HVACUnit,Off,3263.0  
```  
---  
  
## File: `Floor.csv`  
**Header:**  
```csv  
floorID,buildingID,floorNumber,usableAreaSqFt  
```  
**Example Data:**  
```csv  
F001,B001,1,17720.0  
```  
---  
  
## File: `MaintenanceTask.csv`  
**Header:**  
```csv  
taskID,equipmentID,supplierID,description,plannedStartTime,plannedEndTime,taskStatus  
```  
**Example Data:**  
```csv  
T0001,E2988,SUP011,Update Firmware,2025-07-28 13:37:07,2025-07-28 21:37:07,InProgress  
```  
---  
  
## File: `Occupant.csv`  
**Header:**  
```csv  
occupantID,zoneID,occupantName,occupantRole,comfortPreference  
```  
**Example Data:**  
```csv  
O0001,Z720,Natasha Greer,Admin,77.9  
```  
---  
  
## File: `OccupantGroup.csv`  
**Header:**  
```csv  
groupID,zoneID,groupName,occupantCount,occupantType  
```  
**Example Data:**  
```csv  
G001,Z952,Executive Team,19,Contractors  
```  
---  
  
## File: `Sensor.csv`  
**Header:**  
```csv  
sensorID,zoneID,equipmentID,sensorType,currentReading,lastUpdateTime  
```  
**Example Data:**  
```csv  
S0001,Z001,,Smoke,9.5,2025-07-01 19:55:58  
```  
---  
  
## File: `SimulationScenario.csv`  
**Header:**  
```csv  
scenarioID,zoneID,equipmentID,scenarioName,hypothesis,predictedOutcome  
```  
**Example Data:**  
```csv  
SC001,Z104,E4948,Temperature Control Failure Simulation 1,What happens when temperature control failure occurs in zone Z104,Bed little leader reason need her company western age growth way control.  
```  
---  
  
## File: `Supplier.csv`  
**Header:**  
```csv  
supplierID,supplierName,contactEmail  
```  
**Example Data:**  
```csv  
SUP001,Ortiz-White Solutions,jamesjulie@moore.com  
```  
---  
  
## File: `Zone.csv`  
**Header:**  
```csv  
zoneID,floorID,zoneName,zoneFunction,areaSqFt,occupancyCapacity  
```  
**Example Data:**  
```csv  
Z001,F001,Workshop 01,Workshop,676.0,5  
```  
---  
  
