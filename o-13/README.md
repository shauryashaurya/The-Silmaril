# Ontology #13: Ecological & Migration Tracking Domain               



## **Competency Questions**:

1. “Which migrations have overlapping dates that cause species to compete for the same habitat?”  
2. “Which rangers are assigned to handle alert signals from a specific tracking device with battery < 20%?”  
3. “Which protection policies govern an entire ecosystem vs. only certain habitats?”  
4. “How many population groups are associated with each research study, and what is the growth rate trend?”

**Palantir Foundry Context**:
- **Habitats**, **Species**, **PopulationGroups**, and **TrackingDevices** are separate object types.  
- Real-time sensor data or migration logs can be ingested into Foundry.  
- A transform merges “MigrationEvent → PopulationGroup,” referencing geospatial data for habitats.  
- Foundry’s branching approach helps if new species or policy changes arrive. You can update the ontology object types and test the pipeline before merging.   
              
## **Scenario-based competency questions** for Ontology #13: Ecological & Migration Tracking Domain           
           
1. **Migration Overlap**: “If two **Species** with different **PopulationGroup** attempt to migrate into the same **Habitat** simultaneously, how does the system handle resource conflict signals or generate a new **AlertSignal** for the relevant **Ranger**?”           
2. **Device Battery Failure**: “What if a **TrackingDevice** used by a certain **PopulationGroup** runs out of battery while mid-migration—does that trigger a new ‘MigrationEvent’ status or an ‘AlertSignal’ indicating lost tracking?”           
3. **Policy vs. Ecosystem**: “If we expand a **ProtectionPolicy** from just one **Ecosystem** to multiple habitats, do we alter the ‘governedBy’ relationships enough to require a new **MonitoringProgram** for each habitat species?”           
4. **ResearchStudy Funding**: “What if a newly introduced **ResearchStudy** focuses on a rarely monitored **Species**—does that force a reallocation of **Ranger** patrol routes or new device usage under ‘usesDevice’? ”           
5. **Mass Decline**: “If we artificially reduce the ‘estimatedCount’ in a certain **PopulationGroup** below a threshold, do we trigger an emergency migration event or a new **AlertSignal** referencing that group?”           
6. **Habitat Fragmentation**: “Which **Habitat** can support a certain **Species**’ population if we forcibly classify the original habitat as ‘lost or destroyed’? Do we produce a new policy or an extended **MigrationEvent** for that species?”           
7. **Low Battery Warnings**: “Which **TrackingDevice** have lastCheckIn older than 48 hours, and how do we reassign **Ranger** or issue a new device to keep coverage continuity?”           
8. **Multi-Policy Conflicts**: “What if two **ProtectionPolicy** objects with contradictory rules apply to the same **Ecosystem**—how do we unify them in the domain or highlight the conflict for a ‘MonitoringProgram’ to address?”           
9. **Multi-Habitat Scenario**: “If a single **MigrationEvent** covers multiple **Habitat** (like a traveling herd), does that require each habitat’s climate to remain consistent with the species’ range? If not, do we fail the migration or produce partial success?”           
                          
                
## Ontology Structure: Core Classes / Entities (Domain Ontology)                
                
Below is a conceptual structure, with a **pseudocode** approach.         
        
                
                
                                                              
```mermaid                                                              
       
         
```                                                 
                                                            
---                                  
                                  
```pseudocode                                
      
        
                 
```                    
                    
           

---        