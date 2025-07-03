# CSV Data Schema

This file summarizes the headers of all CSV files found in the `data` folder.

---

## File: `manufacturers.csv`
**Header:**
```csv
id,manufacturerName,location,capacity,productIDs
```
---

## File: `orders.csv`
**Header:**
```csv
id,orderNumber,orderDate,status,totalAmount,sellerType,sellerID,retailerID,productIDs
```
---

## File: `products.csv`
**Header:**
```csv
id,productName,sku,productType,unitPrice
```
---

## File: `retailers.csv`
**Header:**
```csv
id,retailerName,location,retailerType
```
---

## File: `shipments.csv`
**Header:**
```csv
id,shipmentID,shipDate,carrier,trackingNumber,orderID,shipperID
```
---

## File: `suppliers.csv`
**Header:**
```csv
id,supplierName,location,rating,manufacturerIDs
```
---

## File: `warehouses.csv`
**Header:**
```csv
id,warehouseName,location,capacity,productIDs
```
---

