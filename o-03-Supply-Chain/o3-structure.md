# Ontology Structure                                        
                                          
```mermaid                                          
classDiagram    
    class Supplier {    
        %% Data Properties    
        supplierName : string    
        location : string    
        rating : float    
        %% Object Properties    
        suppliesTo *--o Manufacturer : many-to-many    
    }    
    
    class Manufacturer {    
        %% Data Properties    
        manufacturerName : string    
        location : string    
        capacity : int    
        %% Object Properties    
        manufactures *--o Product : many-to-many    
        suppliedBy o--* Supplier : many-to-many    
    }    
    
    class Warehouse {    
        %% Data Properties    
        warehouseName : string    
        location : string    
        capacity : int    
        %% Object Properties    
        stores *--o Product : many-to-many    
        ships *--1 Shipment : one-to-many    
    }    
    
    class Retailer {    
        %% Data Properties    
        retailerName : string    
        location : string    
        retailerType : string    
        %% Object Properties    
        ordersFrom *--o Warehouse : many-to-many    
        ordersFrom *--o Manufacturer : many-to-many    
        receivesInvoice 1--* Invoice: one-to-many    
    }    
    
    class Product {    
        %% Data Properties    
        productName : string    
        sku : string    
        productType : string    
        unitPrice : float    
        %% Object Properties    
        manufacturedBy o--* Manufacturer : many-to-many    
        storedIn o--* Warehouse : many-to-many    
        orderLineOf o--* Order : many-to-many    
    
    }    
    
    class Order {    
        %% Data Properties    
        orderNumber : string    
        orderDate : date    
        status : string    
        totalAmount : float    
        %% Object Properties    
        hasOrderLine *--o Product : many-to-many    
        shippedIn 1--1 Shipment : one-to-one    
    
    }    
    
    class Shipment {    
        %% Data Properties    
        shipmentID : string    
        shipDate : date    
        carrier : string    
        trackingNumber : string    
        %% Object Properties    
        shipsOrder 1--1 Order : one-to-one    
        hasShipper 1--1 Warehouse : one-to-one    
        hasShipper o--1 Manufacturer: one-to-one    
    }    
    
    class Invoice {    
        %% Data Properties    
        invoiceNumber : string    
        invoiceDate : date    
        amountDue : float    
        dueDate : date    
        %% Object Properties    
        billedBy o--1 Warehouse : one-to-one    
        billedBy o--1 Manufacturer : one-to-one    
        billedTo 1--* Retailer : many-to-one    
    }    
    
    %% Relationships    
    Manufacturer "0..*" --o "0..*" Supplier : Association (suppliesTo)    
    Manufacturer "0..*" --o "0..*" Product : Association (manufactures)    
    Warehouse "0..*" --o "0..*" Product : Association (stores)    
    Retailer "0..*" --o "0..*" Warehouse : Association (ordersFrom)    
    Retailer "0..*" --o "0..*" Manufacturer : Association (ordersFrom)    
    Order "0..*" --o "1..*" Product : Association (hasOrderLine)    
    Shipment "1..1" -- "1..1" Order : Association (shipsOrder)    
    Shipment "1..1" -- "1..1" Warehouse : Association (hasShipper)    
    Shipment "0..1" -- "1..1" Manufacturer : Association (hasShipper)    
    Invoice "1..1" --o "0..1" Warehouse : Association (billedBy)    
    Invoice "1..1" --o "0..1" Manufacturer : Association (billedBy)    
    Invoice "1..*" -- "1..1" Retailer : Association (billedTo)                  
```                             
                                        
---              
              
```pseudocode            
Class: Supplier    
   - supplierName: string    
   - location: string    
   - rating: float    
   - suppliesTo -> Manufacturer (0..*)    
    
Class: Manufacturer    
   - manufacturerName: string    
   - location: string    
   - capacity: int    
   - manufactures -> Product (0..*)    
    
Class: Warehouse    
   - warehouseName: string    
   - location: string    
   - capacity: int    
   - stores -> Product (0..*)    
    
Class: Retailer    
   - retailerName: string    
   - location: string    
   - retailerType: string    
   - ordersFrom -> Warehouse or Manufacturer (?)    
    
Class: Product    
   - productName: string    
   - sku: string    
   - productType: string    
   - unitPrice: float    
    
Class: Order    
   - orderNumber: string    
   - orderDate: date    
   - status: string    
   - totalAmount: float    
   - hasOrderLine -> Product (0..*)   // or a separate object for each line    
    
Class: Shipment    
   - shipmentID: string    
   - shipDate: date    
   - carrier: string    
   - trackingNumber: string    
   - shipsOrder -> Order (1..1)    
   - hasShipper -> Warehouse (1..1)   // or Manufacturer if shipping direct    
    
Class: Invoice    
   - invoiceNumber: string    
   - invoiceDate: date    
   - amountDue: float    
   - dueDate: date    
   - billedBy -> Warehouse or Manufacturer    
   - billedTo -> Retailer    
    
```             
              
*Note: Real supply chains can be far more complex, with sub-assemblies, multi-tier suppliers, partial shipments, returns, etc. We’re keeping it “complex enough” to illustrate the domain.*              
  