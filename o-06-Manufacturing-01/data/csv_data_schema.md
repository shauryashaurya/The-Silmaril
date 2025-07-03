# CSV Data Schema

This file summarizes the headers of all CSV files found in the `data` folder.

---

## File: `inspections.csv`
**Header:**
```csv
id,inspectionDate,result,notes,workOrderID,operatorID
```
---

## File: `lines.csv`
**Header:**
```csv
id,lineName,capacity,plantID
```
---

## File: `machines.csv`
**Header:**
```csv
id,machineName,machineType,maintenanceDueDate,lineID,operatorIDs
```
---

## File: `materials.csv`
**Header:**
```csv
id,materialName,materialType,unitCost
```
---

## File: `operators.csv`
**Header:**
```csv
id,operatorName,skillLevel,hireDate
```
---

## File: `plants.csv`
**Header:**
```csv
id,plantName,location
```
---

## File: `products.csv`
**Header:**
```csv
id,productName,sku,price
```
---

## File: `work_orders.csv`
**Header:**
```csv
id,workOrderNumber,quantity,startDate,dueDate,status,lineID,materialIDs,productID
```
---

