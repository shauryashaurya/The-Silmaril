# Ontology #21 - Global Energy Grid & Market                     
           
## Domain
Models a global energy grid with PowerPlants, Lines, Substations, Consumers, Storage, MarketOperator, Contract, LoadSheddingPlans, Simulations, etc.
## Sample Competency Questions:
“Which power plants feed which transmission lines, eventually supplying which consumer endpoints?”
“Which system is governed by which market operator and contract, and how are we doing carbon offset or compliance with a regulatory standard?”
“Which flood or demand response simulation references which substation or pipeline?”    
---                
                
## Ontology Structure: Core Classes / Entities (Domain Ontology)                
                
Below is a conceptual structure, with a **pseudocode** approach.         
        
                
                
```mermaid                                                                      
              
                 
```                                                         
                                                                    
---                                          
                                          
```pseudocode                                                
Class: GlobalEnergyGrid        
  - gridID: string        
  - region: string        
  - peakDemand: float                       
  - operationalStatus: string               
  - primaryEnergySource: string             
        
Class: PowerPlant        
  - plantID: string        
  - plantType: string        
  - capacityMW: float        
  - annualGeneration: float         // (e.g., total MWh produced yearly)        
  - operationalCosts: float                 
        
Class: TransmissionLine        
  - lineID: string        
  - voltageLevel: float        
  - lengthKm: float        
  - lineLossPercent: float                  
        
Class: Substation        
  - subID: string        
  - substationName: string        
  - maxLoad: float        
  - inspectionScore: int                    
        
Class: DistributionFeeder        
  - feederID: string        
  - feederName: string        
  - lineVoltage: float        
        
Class: ConsumerEndpoint        
  - endpointID: string        
  - endpointType: string        
  - usageKWh: float        
        
Class: StorageFacility        
  - facilityID: string        
  - storageType: string        
  - capacityKWh: float        
        
Class: MarketOperator        
  - operatorID: string        
  - operatorName: string        
        
Class: EnergyContract        
  - contractID: string        
  - contractTerms: string        
  - contractPrice: float        
        
Class: LoadSheddingPlan        
  - planID: string        
  - planDescription: string        
        
Class: IncidentReport        
  - reportID: string        
  - incidentType: string        
  - severity: string        
  - incidentTime: dateTime                  
        
Class: WeatherSystem        
  - weatherID: string        
  - weatherType: string        
  - intensityLevel: string        
        
Class: CurtailmentOrder        
  - orderID: string        
  - reason: string        
  - reductionPercent: float        
        
Class: GridMaintenance        
  - maintenanceID: string        
  - scheduleDate: dateTime        
  - status: string        
        
Class: EmissionSensor        
  - sensorID: string        
  - emissionRate: float        
  - location: string        
        
Class: CarbonCredit        
  - creditID: string        
  - creditValue: float        
        
Class: RegulatoryStandard        
  - standardID: string        
  - standardName: string        
        
Class: EnergySimulation        
  - simID: string        
  - scenarioType: string        
        
Class: DemandResponseProgram        
  - programID: string        
  - programName: string        
  - enrollment: int        
        
// Existing relationships (19 total, unchanged):        
// (1) hasPlant (GlobalEnergyGrid → PowerPlant, 1..*)        
// (2) connectsLine (PowerPlant → TransmissionLine, 0..*)        
// (3) hasSubstation (TransmissionLine → Substation, 0..1)        
// (4) distributesFeeder (Substation → DistributionFeeder, 1..*)        
// (5) suppliesEndpoint (DistributionFeeder → ConsumerEndpoint, 0..*)        
// (6) includesStorage (GlobalEnergyGrid → StorageFacility, 0..*)        
// (7) governedBy (GlobalEnergyGrid → MarketOperator, 0..1)        
// (8) linkedContract (MarketOperator → EnergyContract, 0..*)        
// (9) planLoadShedding (LoadSheddingPlan → Substation, 0..*)        
// (10) logsIncident (IncidentReport → DistributionFeeder, 0..1)        
// (11) influencesWeather (WeatherSystem → PowerPlant, 0..*)        
// (12) triggersCurtailment (WeatherSystem → CurtailmentOrder, 0..*)        
// (13) referencesMaintenance (GridMaintenance → TransmissionLine, 0..*)        
// (14) monitorsEmission (EmissionSensor → PowerPlant, 0..*)        
// (15) offsetBy (PowerPlant → CarbonCredit, 0..*)        
// (16) compliesWith (PowerPlant → RegulatoryStandard, 0..*)        
// (17) simEvaluates (EnergySimulation → LoadSheddingPlan, 0..*)        
// (18) offersDemandResponse (DemandResponseProgram → ConsumerEndpoint, 0..*)        
// (19) enforcedBy (CurtailmentOrder → MarketOperator, 0..1)        
        
// More object properties:        
        
Relationship: tradesCredit (MarketOperator → CarbonCredit, 0..*)        
  // e.g., a market operator might trade or manage carbon credits        
        
Relationship: underMaintenance (Substation → GridMaintenance, 0..*)        
  // substation might be under a certain maintenance process        
        
Relationship: conflictsWith (CurtailmentOrder → LoadSheddingPlan, 0..1)        
  // a curtailment order could override or conflict with an existing load-shedding plan        
        
Relationship: collectsData (EmissionSensor → Substation, 0..*)        
  // a sensor placed near or in a substation to collect local emission data        
        
Relationship: mitigates (EnergySimulation → IncidentReport, 0..*)        
  // a simulation might propose solutions that mitigate certain incidents        
                 
                       
'''               
          