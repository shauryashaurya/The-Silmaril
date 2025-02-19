# Ontology #5: Construction 
  
## Ontology Structure                                    
                                      
```mermaid                                      
classDiagram
    class Client {
        %% Data Properties
        name : string
        contactInfo : string
        %% Object Properties
        projectHas *--1 Project : one-to-many
    }

    class ConstructionCompany {
        %% Data Properties
        companyName : string
        licenseNumber : string
        location : string
        %% Object Properties
        executes *--1 Project : one-to-many
        receivesInvoice 1--* Invoice: one-to-many
        taskAssignedTo o--* Task : many-to-many
    }

    class Project {
        %% Data Properties
        projectName : string
        location : string
        startDate : date
        endDate : date
        totalBudget : float
        status : string
        %% Object Properties
        hasClient 1--1 Client : one-to-one
        executedBy 1--1 ConstructionCompany : one-to-one
        hasTask *--o Task : many-to-many
        purchaseOrderFor 1--* PurchaseOrder : one-to-many
    }

    class Task {
        %% Data Properties
        taskName : string
        startDate : date
        endDate : date
        status : string
        costEstimate : float
        %% Object Properties
        assignedTo o--* SubContractor : many-to-many
        assignedTo o--* ConstructionCompany : many-to-many
        usesMaterial *--o Material : many-to-many
        projectHas o--* Project: many-to-many
    }

    class Material {
        %% Data Properties
        materialName : string
        unitCost : float
        %% Object Properties
        taskUses o--* Task : many-to-many
    }

    class Supplier {
        %% Data Properties
        supplierName : string
        location : string
        rating : float
        %% Object Properties
        purchaseOrderFrom *--1 PurchaseOrder: One-to-many
        invoices *--1 Invoice: One-to-many
    }

    class SubContractor {
        %% Data Properties
        subContractorName : string
        specialty : string
        licenseNumber : string
        %% Object Properties
        taskAssignedTo o--* Task : many-to-many
        invoices *--1 Invoice: One-to-many

    }

    class PurchaseOrder {
        %% Data Properties
        orderNumber : string
        orderDate : date
        totalCost : float
        %% Object Properties
        purchasedFrom 1--1 Supplier : one-to-one
        forProject 1--1 Project : one-to-one
    }

    class Invoice {
        %% Data Properties
        invoiceNumber : string
        invoiceDate : date
        amount : float
        status : string
        %% Object Properties
        invoicedBy o--1 SubContractor : one-to-one
        invoicedBy o--1 Supplier : one-to-one
        invoicedTo 1--* ConstructionCompany : many-to-one
    }

      %% Relationships
    Project "1..1" -- "1..1" Client : Association (hasClient)
    Project "1..1" -- "1..1" ConstructionCompany : Association (executedBy)
    Project "0..*" -- "1..*" Task : Association (hasTask)
    Task "0..*" --o "0..*" SubContractor : Association (assignedTo)
    Task "0..*" --o "0..*" ConstructionCompany : Association (assignedTo)
    Task "0..*" --o "0..*" Material : Association (usesMaterial)
    PurchaseOrder "1..1" -- "1..1" Supplier : Association (purchasedFrom)
    PurchaseOrder "1..1" -- "1..1" Project : Association (forProject)
    Invoice "0..1" --o "1..1" SubContractor : Association (invoicedBy)
    Invoice "0..1" --o "1..1" Supplier : Association (invoicedBy)
    Invoice "1..*" -- "1..1" ConstructionCompany : Association (invoicedTo)       
```                         
                                    
---          
          
```pseudocode        
Class: Client
  - name: string
  - contactInfo: string

Class: ConstructionCompany
  - companyName: string
  - licenseNumber: string
  - location: string

Class: Project
  - projectName: string
  - location: string
  - startDate: date
  - endDate: date
  - totalBudget: float
  - status: string
  - hasClient -> Client (1..1)
  - executedBy -> ConstructionCompany (1..1)
  - hasTask -> Task (0..*)

Class: Task
  - taskName: string
  - startDate: date
  - endDate: date
  - status: string
  - costEstimate: float
  - assignedTo -> SubContractor or ConstructionCompany
  - usesMaterial -> Material (0..*)

Class: Material
  - materialName: string
  - unitCost: float

Class: Supplier
  - supplierName: string
  - location: string
  - rating: float (1..5)

Class: SubContractor
  - subContractorName: string
  - specialty: string
  - licenseNumber: string

Class: PurchaseOrder
  - orderNumber: string
  - orderDate: date
  - totalCost: float
  - purchasedFrom -> Supplier (1..1)
  - forProject -> Project (1..1)

Class: Invoice
  - invoiceNumber: string
  - invoiceDate: date
  - amount: float
  - status: string
  - invoicedBy -> SubContractor or Supplier
  - invoicedTo -> ConstructionCompany
    
```         
          
*(We could add many more details—like quantity, material unit-of-measure, labor hours, etc. We are still in early stages, for this exercise, this may be enough.)*          
  