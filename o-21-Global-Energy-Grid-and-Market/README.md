# Ontology #21 - Global Energy Grid & Market                                           
                                 
## Domain                        
                        
Models a global energy grid with PowerPlants, Lines, Substations, Consumers, Storage, MarketOperator, Contract, LoadSheddingPlans, Simulations, etc.                      
                        
## Sample Competency Questions:                        
1. "Which power plants feed which transmission lines, eventually supplying which consumer endpoints?”                      
1. "Which system is governed by which market operator and contract, and how are we doing carbon offset or compliance with a regulatory standard?”                      
1. "Which flood or demand response simulation references which substation or pipeline?”      
1. “Which power plants have an operationalStatus = ‘offline’ but are still connected to a substation that expects supply?”  
1. “Which consumer endpoints are part of a demand response program that had a curtailment order triggered by extreme weather?”  
1. “How many carbon credits are traded by the market operator for a single power plant in a season?”  
1. “Which lines have lineLossPercent over 10.0 and which storages or lines can mitigate that?”  
1. “Which grid maintenance schedules conflict with load shedding plans for the same substation?”  
1. “Which distribution feeders rely on an overshadowed power plant from a severe storm scenario?”  
1. “Which regulatory standards are not complied with by a certain power plant?”  
1. “Which incident reports are triggered by consumer endpoints with usageKWh above threshold?”  
1. “Which simulation scenario tests a meltdown condition for a majority of the lines or storages?”

**Palantir Foundry Context**:
- Each **PowerPlant**, **TransmissionLine**, **Substation**, **ConsumerEndpoint** is an object type referencing pipeline data from real grid logs or predictions.  
- Code-workbooks might detect lineLoss or usage patterns, generating “CurtailmentOrder” if threshold is exceeded.  
- Branch approach for new policies or expansions, e.g. “GreenEnergyPolicy,” tested in a separate branch to ensure pipeline transformations remain valid.  
- Merging results unify the new logic with production.                    
---                                      
## **Scenario-based competency questions** for Ontology #21: Global Energy Grid & Market Domain                                 
                                 
1. **Plant Shutdown**                                   
   - “Which `PowerPlant` can be safely shut down without triggering loadShedding in multiple `Substation` or `DistributionFeeder`?”                                 
                                 
2. **Extreme Weather**                                   
   - “If a severe `WeatherSystem` triggersCurtailment with `reductionPercent=50`, do we see mass disconnection for certain `ConsumerEndpoint` or partial bridging via `StorageFacility`?”                                 
                                 
3. **Market Operator Overload**                                   
   - “Which `MarketOperator` is forced to handle double carbon credits if multiple ‘PowerPlant’ offsetBy references the same `CarbonCredit`?”                                  
                                 
4. **Regulatory Non-Compliance**                                   
   - “Which `PowerPlant` fails to complyWith a `RegulatoryStandard` if overshadowingEvil is found? (Joke aside, overshadowing is from the domain—use daily transforms to check compliance).”                                 
                                 
5. **Incidents**                                   
   - “If an `IncidentReport` indicates a substation meltdown, do we forcibly remove that `Substation` from the supply chain or partially route lines?”                                 
                                 
6. **Unexpected Demand**                                   
   - “If `ConsumerEndpoint` usageKWh doubles unexpectedly, does the system forcibly trigger a new `LoadSheddingPlan`, or do we rely on surplus from `StorageFacility`?”                                 
                                 
7. **Weather System Gains**                                   
   - “What if certain `WeatherSystem` is beneficial (like strong wind for wind plants)—do we see a negative or zero `reductionPercent` for `CurtailmentOrder`, or do we re-check compliance with `EnergyContract` pricing?”                                 
                                 
8. **New DemandResponse**                                   
   - “If we create a new `DemandResponseProgram` that references all consumer endpoints in a region, does that reduce net usage or cause partial pipeline conflicts with existing `LoadSheddingPlan`?”                                 
                                 
9. **Multi-Grid Merger**                                   
   - “If two `GlobalEnergyGrid` merges, do we unify all references to `PowerPlant`, `TransmissionLine`, `StorageFacility`, or do we keep partial duplicates? Possibly requiring new code transforms in Foundry.”                                 
                                 
---                                 
                                 
                      
                                      
## Ontology Structure: Core Classes / Entities (Domain Ontology)                                      
                                      
Below is a conceptual structure, with a **pseudocode** approach.                               
                              
                                      
                                      
```mermaid                                                                                            
       %% ONTOLOGY #21: Global Energy Grid & Market                                
                                
classDiagram                                
                                
class GlobalEnergyGrid {                                
  string gridID                                
  string region                                
}                                
                                
class PowerPlant {                                
  string plantID                                
  string plantType                                
  float capacityMW                                
}                                
                                
class TransmissionLine {                                
  string lineID                                
  float voltageLevel                                
  float lengthKm                                
}                                
                                
class Substation {                                
  string subID                                
  string substationName                                
  float maxLoad                                
}                                
                                
class DistributionFeeder {                                
  string feederID                                
  string feederName                                
  float lineVoltage                                
}                                
                                
class ConsumerEndpoint {                                
  string endpointID                                
  string endpointType                                
  float usageKWh                                
}                                
                                
class StorageFacility {                                
  string facilityID                                
  string storageType                                
  float capacityKWh                                
}                                
                                
class MarketOperator {                                
  string operatorID                                
  string operatorName                                
}                                
                                
class EnergyContract {                                
  string contractID                                
  string contractTerms                                
  float contractPrice                                
}                                
                                
class LoadSheddingPlan {                                
  string planID                                
  string planDescription                                
}                                
                                
class IncidentReport {                                
  string reportID                                
  string incidentType                                
  string severity                                
}                                
                                
class WeatherSystem {                                
  string weatherID                                
  string weatherType                                
  string intensityLevel                                
}                                
                                
class CurtailmentOrder {                                
  string orderID                                
  string reason                                
  float reductionPercent                                
}                                
                                
class GridMaintenance {                                
  string maintenanceID                                
  dateTime scheduleDate                                
  string status                                
}                                
                                
class EmissionSensor {                                
  string sensorID                                
  float emissionRate                                
  string location                                
}                                
                                
class CarbonCredit {                                
  string creditID                                
  float creditValue                                
}                                
                                
class RegulatoryStandard {                                
  string standardID                                
  string standardName                                
}                                
                                
class EnergySimulation {                                
  string simID                                
  string scenarioType                                
}                                
                                
class DemandResponseProgram {                                
  string programID                                
  string programName                                
  int enrollment                                
}                                
                                
GlobalEnergyGrid "1" --o "1..*" PowerPlant : hasPlant                                
PowerPlant "1" --o "0..*" TransmissionLine : connectsLine                                
TransmissionLine "1" --o "0..1" Substation : hasSubstation                                
Substation "1" --o "1..*" DistributionFeeder : distributesFeeder                                
DistributionFeeder "1" --o "0..*" ConsumerEndpoint : suppliesEndpoint                                
GlobalEnergyGrid "1" --o "0..*" StorageFacility : includesStorage                                
GlobalEnergyGrid "1" --o "0..1" MarketOperator : governedBy                                
MarketOperator "1" --o "0..*" EnergyContract : linkedContract                                
LoadSheddingPlan "1" --o "0..*" Substation : planLoadShedding                                
IncidentReport "1" --o "0..1" DistributionFeeder : logsIncident                                
WeatherSystem "1" --o "0..*" PowerPlant : influencesWeather                                
WeatherSystem "1" --o "0..*" CurtailmentOrder : triggersCurtailment                                
GridMaintenance "1" --o "0..1" TransmissionLine : referencesMaintenance                                
EmissionSensor "1" --o "0..1" PowerPlant : monitorsEmission                                
PowerPlant "1" --o "0..1" CarbonCredit : offsetBy                                
PowerPlant "1" --o "0..1" RegulatoryStandard : compliesWith                                
EnergySimulation "1" --o "0..*" LoadSheddingPlan : simEvaluates                                
DemandResponseProgram "1" --o "0..*" ConsumerEndpoint : offersDemandResponse                                
CurtailmentOrder "1" --o "0..1" MarketOperator : enforcedBy                                       
                                       
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
          