# CSV Data Schema  
  
This file summarizes the headers and a sample data row of all CSV files found in the `data` folder.  
  
---  
  
## File: `clients.csv`  
**Header:**  
```csv  
id,name,contactInfo  
```  
**Example Data:**  
```csv  
client_0,"Peterson, Washington and Phelps (Client)",+1-789-402-3301x3894  
```  
---  
  
## File: `companies.csv`  
**Header:**  
```csv  
id,companyName,licenseNumber,location  
```  
**Example Data:**  
```csv  
company_0,Perez-Jackson Construction,LIC-40699,Amandaville  
```  
---  
  
## File: `invoices.csv`  
**Header:**  
```csv  
id,invoiceNumber,invoiceDate,amount,status,invoicedByID,invoicedToID  
```  
**Example Data:**  
```csv  
invoice_0,INV-68753,2023-09-22,16468.73,Open,subcontractor_34,company_6  
```  
---  
  
## File: `materials.csv`  
**Header:**  
```csv  
id,materialName,unitCost  
```  
**Example Data:**  
```csv  
material_0,Tiles,53.37  
```  
---  
  
## File: `projects.csv`  
**Header:**  
```csv  
id,projectName,location,startDate,endDate,totalBudget,status,clientID,companyID  
```  
**Example Data:**  
```csv  
project_0,Project_0_key,North Jose,2022-11-26,2024-07-17,2298196.28,Planning,client_44,company_6  
```  
---  
  
## File: `purchaseOrders.csv`  
**Header:**  
```csv  
id,orderNumber,orderDate,totalCost,supplierID,projectID  
```  
**Example Data:**  
```csv  
po_0,PO-79057,2022-12-06,2048.81,supplier_28,project_14  
```  
---  
  
## File: `subContractors.csv`  
**Header:**  
```csv  
id,subContractorName,specialty,licenseNumber  
```  
**Example Data:**  
```csv  
subcontractor_0,Miles-Lee Roofing,Painting,SUB-44283  
```  
---  
  
## File: `suppliers.csv`  
**Header:**  
```csv  
id,supplierName,location,rating  
```  
**Example Data:**  
```csv  
supplier_0,"Morales, Sherman and Singh Supplies",North Alexandraton,2.8  
```  
---  
  
