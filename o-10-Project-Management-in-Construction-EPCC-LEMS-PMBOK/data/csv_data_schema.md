# CSV Data Schema  
  
This file summarizes the headers and a sample data row of all CSV files found in the `data` folder.  
  
---  
  
## File: `equipment_list.csv`  
**Header:**  
```csv  
id,equipmentID,equipmentName,equipmentType,dailyRentalCost,capacityOrSpecs  
```  
**Example Data:**  
```csv  
equip_0,EQ-1000,Crane_0,Crane,1557.6,Crane spec details  
```  
---  
  
## File: `material_list.csv`  
**Header:**  
```csv  
id,materialID,materialName,materialType,unitCost,quantityOnHand,supplierID  
```  
**Example Data:**  
```csv  
mat_0,MAT-1000,Concrete_0,Concrete,220.19,97953,sup_37  
```  
---  
  
## File: `people.csv`  
**Header:**  
```csv  
id,personID,name,skillType,hourlyRate  
```  
**Example Data:**  
```csv  
person_0,EMP-5000,Andrea Gilbert,LandscapeTech,87.61  
```  
---  
  
## File: `suppliers.csv`  
**Header:**  
```csv  
id,supplierID,supplierName,location  
```  
**Example Data:**  
```csv  
sup_0,SUP-1000,Thomas-Wright Supplies,East Louis  
```  
---  
  
## File: `tasks.csv`  
**Header:**  
```csv  
id,taskID,taskName,startDate,endDate,durationDays,costEstimate,actualCost,isCritical,milestoneFlag,workStreamID,dependsOnIDs,laborIDs,equipmentIDs,materialIDs  
```  
**Example Data:**  
```csv  
task_0,TK-10000,Task_0_Monetize Granular Technologies,2024-08-17T21:54:27,2024-09-02T21:54:27,16,256780.9,0.0,False,False,ws_183,['task_634'],"['person_228', 'person_633']","['equip_10', 'equip_24']",[]  
```  
---  
  
## File: `workstreams.csv`  
**Header:**  
```csv  
id,workStreamID,name,description,startDate,endDate,budgetAllocated,projectID  
```  
**Example Data:**  
```csv  
ws_0,WS-1000,Workstream_0_Admit,Growth share national story stuff house cold its federal.,2024-05-20T21:54:27,2024-10-27T21:54:27,3007086.15,proj_0  
```  
---  
  
