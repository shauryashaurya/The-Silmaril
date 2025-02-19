# Ontology #5: Construction         
          
## Ontology Structure                                            
                                                                        
                                              
```mermaid                                              
classDiagram        
    class ManufacturingPlant {        
        %% Data Properties        
        -plantName : string        
        -location : string        
        %% Object Properties        
        +hasProductionLine *--| ProductionLine        
    }        
        
    class ProductionLine {        
        %% Data Properties        
        -lineName : string        
        -capacity : int        
        %% Object Properties        
        +hasMachine *--| Machine        
        +producesProduct *--| Product        
    }        
        
    class Machine {        
        %% Data Properties        
        -machineName : string        
        -machineType : string        
        -maintenanceDueDate : date        
        %% Object Properties        
        +operatedBy *--| Operator        
    }        
        
    class Operator {        
        %% Data Properties        
        -operatorName : string        
        -skillLevel : string        
        -hireDate : date        
        %% Object Properties        
    }        
        
    class Material {        
        %% Data Properties        
        -materialName : string        
        -materialType : string        
        -unitCost : float        
        %% Object Properties        
    }        
        
    class Product {        
        %% Data Properties        
        -productName : string        
        -sku : string        
        -price : float        
        %% Object Properties        
    }        
        
    class WorkOrder {        
        %% Data Properties        
        -workOrderNumber : string        
        -quantity : int        
        -startDate : date        
        -dueDate : date        
        -status : string        
        %% Object Properties        
        +consumesMaterial *--o Material        
        +producesProduct |-| Product        
        +scheduledOn  |-| ProductionLine        
    }        
        
    class QualityInspection {        
        %% Data Properties        
        -inspectionDate : date        
        -result : string        
        -notes : string        
        %% Object Properties        
        +inspectedBy o--| Operator        
        +inspectsWorkOrder  |-| WorkOrder        
    }        
        
    ManufacturingPlant *--| ProductionLine : Association (hasProductionLine)        
    ProductionLine *--| Machine : Association (hasMachine)        
    Machine *--| Operator : Association (operatedBy)        
    WorkOrder *--o Material : Association (consumesMaterial)        
    WorkOrder |-| Product : Association (producesProduct)        
    WorkOrder |-| ProductionLine : Association (scheduledOn)        
    QualityInspection o--| Operator : Association (inspectedBy)        
    QualityInspection |-| WorkOrder : Association (inspectsWorkOrder)        
    ProductionLine *--| Product : Association (producesProduct)             
```                                 
                                            
---                  
                  
```pseudocode                
Class: ManufacturingPlant        
   - plantName: string        
   - location: string        
   - hasProductionLine -> ProductionLine (1..*)        
        
Class: ProductionLine        
   - lineName: string        
   - capacity: integer (units/day)        
   - hasMachine -> Machine (1..*)        
        
Class: Machine        
   - machineName: string        
   - machineType: string        
   - maintenanceDueDate: date        
   - operatedBy -> Operator (1..*)        
        
Class: Operator        
   - operatorName: string        
   - skillLevel: string (e.g., "Beginner", "Intermediate", "Expert")        
   - hireDate: date        
        
Class: Material        
   - materialName: string        
   - materialType: string (e.g., "Raw", "Semi-Finished")        
   - unitCost: float        
        
Class: Product        
   - productName: string        
   - sku: string        
   - price: float        
        
Class: WorkOrder        
   - workOrderNumber: string        
   - quantity: integer        
   - startDate: date        
   - dueDate: date        
   - status: string (e.g., "Scheduled", "In Progress", "Completed", "Cancelled")        
   - consumesMaterial -> Material (0..*)        
   - producesProduct -> Product (1..1)        
   - scheduledOn -> ProductionLine (1..1)        
        
Class: QualityInspection        
   - inspectionDate: date        
   - result: string (e.g., "Pass", "Fail")        
   - notes: string        
   - inspectedBy -> Operator        
   - inspectsWorkOrder -> WorkOrder        
        
            
```                 
          