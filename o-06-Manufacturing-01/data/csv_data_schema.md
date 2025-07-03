# CSV Data Schema  
  
This file summarizes the headers and a sample data row of all CSV files found in the `data` folder.  
  
---  
  
## File: `inspections.csv`  
**Header:**  
```csv  
id,inspectionDate,result,notes,workOrderID,operatorID  
```  
**Example Data:**  
```csv  
inspection_0,2024-10-20,Pass,Remember white color letter cultural speech.,wo_38,operator_0  
```  
---  
  
## File: `lines.csv`  
**Header:**  
```csv  
id,lineName,capacity,plantID  
```  
**Example Data:**  
```csv  
line_0,Line_0_make,327,plant_7  
```  
---  
  
## File: `machines.csv`  
**Header:**  
```csv  
id,machineName,machineType,maintenanceDueDate,lineID,operatorIDs  
```  
**Example Data:**  
```csv  
machine_0,CuttingMachine_0,Cutting,2025-05-19T15:15:56.579559,line_28,['operator_36']  
```  
---  
  
## File: `materials.csv`  
**Header:**  
```csv  
id,materialName,materialType,unitCost  
```  
**Example Data:**  
```csv  
material_0,Steel Sheet,Semi-Finished,28.17  
```  
---  
  
## File: `operators.csv`  
**Header:**  
```csv  
id,operatorName,skillLevel,hireDate  
```  
**Example Data:**  
```csv  
operator_0,Jane Morgan,Expert,2024-03-03  
```  
---  
  
## File: `plants.csv`  
**Header:**  
```csv  
id,plantName,location  
```  
**Example Data:**  
```csv  
plant_0,Morris-Casey Plant,East Angela  
```  
---  
  
## File: `products.csv`  
**Header:**  
```csv  
id,productName,sku,price  
```  
**Example Data:**  
```csv  
product_0,Widget A,SKU-5801,144.95  
```  
---  
  
## File: `work_orders.csv`  
**Header:**  
```csv  
id,workOrderNumber,quantity,startDate,dueDate,status,lineID,materialIDs,productID  
```  
**Example Data:**  
```csv  
wo_0,WO-2916,145,2024-12-21,2025-01-07,Completed,line_26,"['material_12', 'material_9', 'material_46']",product_33  
```  
---  
  
