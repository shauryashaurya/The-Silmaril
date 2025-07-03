# CSV Data Schema

This file summarizes the headers of all CSV files found in the `data` folder.

---

## File: `equipment_list.csv`
**Header:**
```csv
id,equipmentID,equipmentName,equipmentType,dailyRentalCost,capacityOrSpecs
```
---

## File: `material_list.csv`
**Header:**
```csv
id,materialID,materialName,materialType,unitCost,quantityOnHand,supplierID
```
---

## File: `people.csv`
**Header:**
```csv
id,personID,name,skillType,hourlyRate
```
---

## File: `suppliers.csv`
**Header:**
```csv
id,supplierID,supplierName,location
```
---

## File: `tasks.csv`
**Header:**
```csv
id,taskID,taskName,startDate,endDate,durationDays,costEstimate,actualCost,isCritical,milestoneFlag,workStreamID,dependsOnIDs,laborIDs,equipmentIDs,materialIDs
```
---

## File: `workstreams.csv`
**Header:**
```csv
id,workStreamID,name,description,startDate,endDate,budgetAllocated,projectID
```
---

