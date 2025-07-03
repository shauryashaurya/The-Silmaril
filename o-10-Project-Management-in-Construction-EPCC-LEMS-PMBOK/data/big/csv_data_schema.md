# CSV Data Schema

This file summarizes the headers of all CSV files found in the `big` folder.

---

## File: `equipment_list.csv`
**Header:**
```csv
id,equipmentID,equipmentName,equipmentType,dailyRentalCost,capacityOrSpecs,supplierID
```
---

## File: `material_list.csv`
**Header:**
```csv
id,materialID,materialName,materialType,unitCost,quantityOnHand,supplierID
```
---

## File: `mega_projects.csv`
**Header:**
```csv
id,projectID,projectName,overallBudget,startDate,plannedEndDate,actualEndDate
```
---

## File: `people.csv`
**Header:**
```csv
id,personID,name,skillType,hourlyRate
```
---

## File: `procurement_orders.csv`
**Header:**
```csv
id,orderNumber,orderDate,totalCost,supplierID,resourceIDs,belongsToProjectID
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
id,taskID,taskName,startDate,endDate,durationDays,costEstimate,actualCost,isCritical,milestoneFlag,workStreamID,dependsOnIDs,laborIDs,equipmentIDs,materialIDs,teamID,classType,commissioningChecklist,passDate
```
---

## File: `teams.csv`
**Header:**
```csv
id,teamID,teamName,personIDs
```
---

## File: `workstreams.csv`
**Header:**
```csv
id,workStreamID,name,description,startDate,endDate,budgetAllocated,projectID
```
---

