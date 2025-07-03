# CSV Data Schema

This file summarizes the headers of all CSV files found in the `data` folder.

---

## File: `clients.csv`
**Header:**
```csv
id,name,contactInfo
```
---

## File: `companies.csv`
**Header:**
```csv
id,companyName,licenseNumber,location
```
---

## File: `invoices.csv`
**Header:**
```csv
id,invoiceNumber,invoiceDate,amount,status,invoicedByID,invoicedToID
```
---

## File: `materials.csv`
**Header:**
```csv
id,materialName,unitCost
```
---

## File: `projects.csv`
**Header:**
```csv
id,projectName,location,startDate,endDate,totalBudget,status,clientID,companyID
```
---

## File: `purchaseOrders.csv`
**Header:**
```csv
id,orderNumber,orderDate,totalCost,supplierID,projectID
```
---

## File: `subContractors.csv`
**Header:**
```csv
id,subContractorName,specialty,licenseNumber
```
---

## File: `suppliers.csv`
**Header:**
```csv
id,supplierName,location,rating
```
---

