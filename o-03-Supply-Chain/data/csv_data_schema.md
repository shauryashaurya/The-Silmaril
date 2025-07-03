# CSV Data Schema  
  
This file summarizes the headers and a sample data row of all CSV files found in the `data` folder.  
  
---  
  
## File: `manufacturers.csv`  
**Header:**  
```csv  
id,manufacturerName,location,capacity,productIDs  
```  
**Example Data:**  
```csv  
manufacturer_0,Elliott and Sons Manufacturing,Taylorchester,8902,"['product_65', 'product_208', 'product_202', 'product_38', 'product_58', 'product_189', 'product_191', 'product_32', 'product_249', 'product_197', 'product_147', 'product_215', 'product_70']"  
```  
---  
  
## File: `orders.csv`  
**Header:**  
```csv  
id,orderNumber,orderDate,status,totalAmount,sellerType,sellerID,retailerID,productIDs  
```  
**Example Data:**  
```csv  
order_0,ON-0-1734,2024-09-13,Delivered,8918.25,manufacturer,manufacturer_5,retailer_30,"['product_222', 'product_239', 'product_2', 'product_69']"  
```  
---  
  
## File: `products.csv`  
**Header:**  
```csv  
id,productName,sku,productType,unitPrice  
```  
**Example Data:**  
```csv  
product_0,Realigned next generation software,SKU-0-399,RawMaterial,19.77  
```  
---  
  
## File: `retailers.csv`  
**Header:**  
```csv  
id,retailerName,location,retailerType  
```  
**Example Data:**  
```csv  
retailer_0,"Smith, Neal and Nunez Retail",Wattshaven,Online  
```  
---  
  
## File: `shipments.csv`  
**Header:**  
```csv  
id,shipmentID,shipDate,carrier,trackingNumber,orderID,shipperID  
```  
**Example Data:**  
```csv  
shipment_0,SHIP-0-6570,2025-02-10,UPS,TRK-6703169,order_1385,warehouse_0  
```  
---  
  
## File: `suppliers.csv`  
**Header:**  
```csv  
id,supplierName,location,rating,manufacturerIDs  
```  
**Example Data:**  
```csv  
supplier_0,Lee Ltd,East Annette,4.13,['manufacturer_1']  
```  
---  
  
## File: `warehouses.csv`  
**Header:**  
```csv  
id,warehouseName,location,capacity,productIDs  
```  
**Example Data:**  
```csv  
warehouse_0,Ross-Jones Distribution,Kyleview,8892,"['product_246', 'product_2', 'product_97', 'product_238', 'product_169', 'product_227', 'product_188', 'product_214', 'product_103', 'product_176', 'product_151', 'product_133', 'product_190', 'product_8', 'product_126']"  
```  
---  
  
