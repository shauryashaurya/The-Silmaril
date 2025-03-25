# Ontology #15: Water Infrastructure & Management           

---           
           
## **Scenario-based competency questions** for Ontology #15: Water Infrastructure & Management           
           
1. **Dam Failure**: “If a certain **Dam** hits a structuralHealth threshold indicating near-collapse, do we forcibly reduce the **Canal** flowRate or issue an **AlertEvent** to the entire ‘WaterSystem’?”           
2. **PumpStation Downtime**: “Which **PumpStation** can be safely shut down for a ‘MaintenancePlan’ if we want to preserve basic flow to the relevant **WaterTreatmentPlant**?”           
3. **Flood Simulation**: “If a new ‘FloodSimulation’ scenario references multiple **Dam** objects, do we require all to reduce flow or do some remain at normal capacity? Which distribution pipeline changes result from partial closures?”           
4. **Turbine Power Variation**: “What if **HydroelectricTurbine** output drops below a threshold—does that cause a new maintenance plan or an immediate supply shortfall for certain distribution pipelines?”           
5. **Regulatory Permit** Removal: “If we revoke a **RegulatoryPermit** from a certain dam, do we forcibly close the canal or only partially reduce flow to the **WaterTreatmentPlant** referencing that canal?”           
6. **Expired WaterQualitySensor**: “Which sensors are older than x months—should we forcibly reassign them or trigger a new ‘AlertEvent’ if sensor readings are unverified?”           
7. **Global System Overhaul**: “If we unify multiple water systems under a single ‘hasReservoir’ relationship, how do partial plans or current ‘MaintenancePlan’ for each sub-reservoir conflict or unify?”           
8. **Conservation Mode**: “What if we switch a certain **WaterSystem** to a ‘low usage’ operationalStatus—how does that reduce flow across connected canals and pump stations, and do we meet min supply for each ‘WaterTreatmentPlant’?”           
9. **Incident Cascades**: “If a major contamination event triggers an **AlertEvent** in a certain canal, does that automatically mark the connected ‘WaterTreatmentPlant’ as compromised or do we require manual approval?”           
           
---           

         
        
## Ontology Structure: Core Classes / Entities (Domain Ontology)                
                
Below is a conceptual structure, with a **pseudocode** approach.         
        
                
                
                                                              
```mermaid                                                              
       
         
```                                                 
                                                            
---                                  
                                  
```pseudocode                                
      
        
                 
```                