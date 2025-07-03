# CSV Data Schema

This file summarizes the headers of all CSV files found in the `data` folder.

---

## File: `approvals.csv`
**Header:**
```csv
id,approvalID,agencyName,approvalDate,productID
```
---

## File: `batches.csv`
**Header:**
```csv
id,batchNumber,expiryDate,quantityProduced,productID
```
---

## File: `distributors.csv`
**Header:**
```csv
id,distributorName,location,distributorID
```
---

## File: `manufacturers.csv`
**Header:**
```csv
id,manufacturerName,location,licenseNumber
```
---

## File: `pharmacies.csv`
**Header:**
```csv
id,facilityName,facilityType,location
```
---

## File: `prescriptions.csv`
**Header:**
```csv
id,prescriptionID,prescribedDate,quantity,productID
```
---

## File: `products.csv`
**Header:**
```csv
id,internalProductCode,brandName,genericName,strength,form,rxNormCode
```
---

## File: `shipments.csv`
**Header:**
```csv
id,shipmentID,shipDate,receiveDate,fromEntityID,toEntityID,batchIDs
```
---

