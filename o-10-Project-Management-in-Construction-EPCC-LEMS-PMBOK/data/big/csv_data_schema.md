# CSV Data Schema  
  
This file summarizes the headers and a sample data row of all CSV files found in the `big` folder.  
  
---  
  
## File: `equipment_list.csv`  
**Header:**  
```csv  
id,equipmentID,equipmentName,equipmentType,dailyRentalCost,capacityOrSpecs,supplierID  
```  
**Example Data:**  
```csv  
equip_0,EQ-1000,AirCompressor_0,AirCompressor,350.36,AirCompressor spec details,sup_13  
```  
---  
  
## File: `material_list.csv`  
**Header:**  
```csv  
id,materialID,materialName,materialType,unitCost,quantityOnHand,supplierID  
```  
**Example Data:**  
```csv  
mat_0,MAT-1000,AccessPanels_0,AccessPanels,21.06,53668,  
```  
---  
  
## File: `mega_projects.csv`  
**Header:**  
```csv  
id,projectID,projectName,overallBudget,startDate,plannedEndDate,actualEndDate  
```  
**Example Data:**  
```csv  
proj_0,PROJECT-1000,MegaDataCenter_0,460459136.18,2023-11-14T06:25:17,2025-08-30T06:25:17,  
```  
---  
  
## File: `people.csv`  
**Header:**  
```csv  
id,personID,name,skillType,hourlyRate  
```  
**Example Data:**  
```csv  
person_0,EMP-8000,Robin Anderson,CraneOperator,92.18  
```  
---  
  
## File: `procurement_orders.csv`  
**Header:**  
```csv  
id,orderNumber,orderDate,totalCost,supplierID,resourceIDs,belongsToProjectID  
```  
**Example Data:**  
```csv  
po_0,PO-10000,2024-12-16T00:21:45,20926.52,sup_66,['mat_22'],proj_23  
```  
---  
  
## File: `suppliers.csv`  
**Header:**  
```csv  
id,supplierID,supplierName,location  
```  
**Example Data:**  
```csv  
sup_0,SUP-1000,"Dominguez, Allen and Williams Supplies",North Anthony  
```  
---  
  
## File: `tasks.csv`  
**Header:**  
```csv  
id,taskID,taskName,startDate,endDate,durationDays,costEstimate,actualCost,isCritical,milestoneFlag,workStreamID,dependsOnIDs,laborIDs,equipmentIDs,materialIDs,teamID,classType,commissioningChecklist,passDate  
```  
**Example Data:**  
```csv  
task_0,TK-10000,Task_0_Incentivize B2B Interfaces,2024-08-23T06:25:17,2024-09-19T06:25:17,27,257265.06,0.0,False,False,ws_24,[],"['person_506', 'person_1959', 'person_568']","['equip_33', 'equip_52']",['mat_82'],,Task,,  
```  
---  
  
## File: `teams.csv`  
**Header:**  
```csv  
id,teamID,teamName,personIDs  
```  
**Example Data:**  
```csv  
team_0,TM-3000,Team_0_Than,"['person_1859', 'person_530', 'person_578', 'person_1752', 'person_1918', 'person_1792', 'person_1026', 'person_1296']"  
```  
---  
  
## File: `workstreams.csv`  
**Header:**  
```csv  
id,workStreamID,name,description,startDate,endDate,budgetAllocated,projectID  
```  
**Example Data:**  
```csv  
ws_0,WS-5000,Workstream_0_Song,Degree compare much tough pick effect political.,2024-08-20T06:25:17,2024-10-26T06:25:17,639931.73,proj_0  
```  
---  
  
