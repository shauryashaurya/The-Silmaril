# Ontology Structure                                                
                                                  
```mermaid                                                  
classDiagram        
    class PharmaManufacturer {        
        %% Data Properties        
        -manufacturerName : string        
        -location : string        
        -licenseNumber : string        
        %% Object Properties        
        +manufacturesProduct *--| MedicationProduct        
    }        
        
    class Distributor {        
        %% Data Properties        
        -distributorName : string        
        -location : string        
        -distributorID : string        
        %% Object Properties        
    }        
        
    class PharmacyOrHospital {        
        %% Data Properties        
        -facilityName : string        
        -facilityType : string        
        -location : string        
        %% Object Properties        
    }        
        
  class MedicationProduct{        
        %% Data Properties        
        -internalProductCode : string        
        -brandName : string        
        -genericName : string        
        -strength : string        
        -form : string        
        -rxNormCode : string        
        %% Object Properties        
        +approvedBy *--| RegulatoryApproval        
    }        
        
    class BatchOrLot {        
        %% Data Properties        
        -batchNumber : string        
        -expiryDate : date        
        -quantityProduced : int        
        %% Object Properties        
        +belongsToProduct |-| MedicationProduct        
    }        
        
    class Shipment {        
        %% Data Properties        
        -shipmentID : string        
        -shipDate : dateTime        
        -receiveDate : dateTime        
        %% Object Properties        
        +fromEntity o--| PharmaManufacturer        
        +fromEntity2 o--| Distributor          
        +toEntity o--| Distributor        
        +toEntity2 o--| PharmacyOrHospital        
        +includesBatch *--o BatchOrLot        
    }        
        
    class Prescription {        
        %% Data Properties        
        -prescriptionID : string        
        -prescribedDate : date        
        -quantity : int        
        %% Object Properties        
        +medicationRef o--| MedicationProduct        
    }        
        
  class RegulatoryApproval{        
        %% Data Properties        
        -approvalID : string        
        -agencyName : string        
        -approvalDate : date        
        %% Object Properties        
        +referencesProduct |-| MedicationProduct        
  }        
        
    PharmaManufacturer *--| MedicationProduct : Association (manufacturesProduct)        
    BatchOrLot |-| MedicationProduct : Association (belongsToProduct)        
    Shipment *--o BatchOrLot : Association (includesBatch)        
    Prescription o--| MedicationProduct : Association (medicationRef)        
    RegulatoryApproval |-| MedicationProduct : Association (referencesProduct)        
    MedicationProduct *--| RegulatoryApproval : Association (approvedBy)        
             
    Shipment o--| PharmaManufacturer : Association (fromEntity)        
    Shipment o--| Distributor : Association (fromEntity2)        
    Shipment o--| Distributor : Association (toEntity)        
    Shipment o--| PharmacyOrHospital : Association (toEntity2)        
```                                     
                                                
---                      
                      
```pseudocode                    
Class: PharmaManufacturer        
   - manufacturerName: string        
   - location: string        
   - licenseNumber: string  // e.g. FDA or other regulatory body        
   // Potentially references an external Manufacturer ID used in another ontology        
        
Class: Distributor        
   - distributorName: string        
   - location: string        
   - distributorID: string        
   // ROLE: Intermediary shipping or storing pharma products        
        
Class: PharmacyOrHospital        
   - facilityName: string        
   - facilityType: string  // "RetailPharmacy", "HospitalPharmacy"        
   - location: string        
        
Class: MedicationProduct        
   - internalProductCode: string    // unique code in supply chain        
   - brandName: string        
   - genericName: string        
   - strength: string        
   - form: string  // "Tablet", "Capsule", etc.        
   - rxNormCode: string    // This links to a clinical ontology code (matching scenario)        
   // Potentially a second code from some internal system (like "WMS-34342")        
        
Class: BatchOrLot        
   - batchNumber: string        
   - expiryDate: date        
   - quantityProduced: int        
   - belongsToProduct -> MedicationProduct (1..1)        
   // RULE: Each batch references exactly one MedicationProduct        
        
Class: Shipment        
   - shipmentID: string        
   - shipDate: dateTime        
   - receiveDate: dateTime        
   - fromEntity: could be (PharmaManufacturer or Distributor)        
   - toEntity: (Distributor or PharmacyOrHospital)        
   // RULE: fromEntity and toEntity must be different roles (no self-shipment).        
   - includesBatch -> BatchOrLot (0..*)        
        
Class: Prescription        
   - prescriptionID: string        
   - prescribedDate: date        
   - quantity: int        
   - medicationRef -> MedicationProduct        
   // Possibly references a separate "Patient" or "Doctor," but we keep it minimal here.        
        
Class: RegulatoryApproval        
   - approvalID: string        
   - agencyName: string  // e.g. "FDA"        
   - approvalDate: date        
   - referencesProduct -> MedicationProduct (1..1)        
   // RULE: If a product is sold in the U.S., must have FDA approval        
        
// Matching Scenario:         
// Suppose we have a separate "Clinical Ontology" with a class "Drug" (with rxNormCode).        
// We want to align "MedicationProduct" (in supply chain ontology) to "Drug" (in clinical ontology).        
// We can do an equivalence:         
//  MedicationProduct  owl:equivalentClass  Drug        
//  MedicationProduct.rxNormCode  owl:sameAs  Drug.rxNormCode        
// or use a bridging concept to unify them.        
```        
        
### Potential Matching Approach        
        
- If the separate **clinical ontology** has a class **Drug** with property `rxNormCode`, and our **MedicationProduct** also has `rxNormCode`, we could do an **ontology matching** rule:        
  - *“MedicationProduct and Drug are the same concept if they share the same rxNormCode.”*          
  - In formal terms, we might define a **SWRL** or **OWL** equivalence assertion:        
    - `MedicationProduct ≡ Drug` (some conditions)          
    - `MedicationProduct.rxNormCode = Drug.rxNormCode` implies `MedicationProduct` owl:sameAs `Drug`.          
        
*(This is a simplified example—real matching often uses more attributes and possibly string distance metrics on brand/generic names, etc.)*