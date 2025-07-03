# CSV Data Schema  
  
This file summarizes the headers and a sample data row of all CSV files found in the `data` folder.  
  
---  
  
## File: `approvals.csv`  
**Header:**  
```csv  
id,approvalID,agencyName,approvalDate,productID  
```  
**Example Data:**  
```csv  
approval_0,APP-41670,MHRA,2025-02-17,prod_19  
```  
---  
  
## File: `batches.csv`  
**Header:**  
```csv  
id,batchNumber,expiryDate,quantityProduced,productID  
```  
**Example Data:**  
```csv  
batch_0,LOT-93721,2025-05-20,24524,prod_26  
```  
---  
  
## File: `distributors.csv`  
**Header:**  
```csv  
id,distributorName,location,distributorID  
```  
**Example Data:**  
```csv  
dist_0,Spence-Washington Distribution,Gabriellestad,DIST-34612  
```  
---  
  
## File: `manufacturers.csv`  
**Header:**  
```csv  
id,manufacturerName,location,licenseNumber  
```  
**Example Data:**  
```csv  
mfg_0,Thomas PLC Pharma,West Sierraside,MFG-96545  
```  
---  
  
## File: `pharmacies.csv`  
**Header:**  
```csv  
id,facilityName,facilityType,location  
```  
**Example Data:**  
```csv  
ph_0,Peterson-Dyer Hospital,HospitalPharmacy,West Jose  
```  
---  
  
## File: `prescriptions.csv`  
**Header:**  
```csv  
id,prescriptionID,prescribedDate,quantity,productID  
```  
**Example Data:**  
```csv  
rx_0,RX-16192,2025-02-19,40,prod_24  
```  
---  
  
## File: `products.csv`  
**Header:**  
```csv  
id,internalProductCode,brandName,genericName,strength,form,rxNormCode  
```  
**Example Data:**  
```csv  
prod_0,INT-6655,Computer,down,135mg,Tablet,860975  
```  
---  
  
## File: `shipments.csv`  
**Header:**  
```csv  
id,shipmentID,shipDate,receiveDate,fromEntityID,toEntityID,batchIDs  
```  
**Example Data:**  
```csv  
ship_0,SHP-96123,2024-12-14T16:47:59,2025-01-03T16:47:59,dist_7,ph_4,"['batch_10', 'batch_7']"  
```  
---  
  
