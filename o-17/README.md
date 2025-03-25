# Ontology #17 A VERY _"out-there"_ Space Mission & Crew Domain
  
## Domain

Models space missions, spacecraft, crew membership, payload, launch sites, experiments, anomalies, and simulation modules.

## Sample Competency Questions:

* Which mission uses which spacecraft, and who is on the crew?
* Which mission anomalies have been encountered, and how do they affect the mission timeline?
* Which payload is carried by which spacecraft for which experiment or docking module?      
        

---           
           
## **Scenario-based competency questions** for Ontology #17: Space Mission & Crew           
           
1. **Orbit Mismatch**: “If a **SpaceMission** fails to achieve the designated final orbit, do we forcibly reschedule the same mission in the pipeline or create a new ‘SimulationModule’ scenario for re-attempting the orbit injection?”           
2. **Crew Reassignment**: “If half the mission’s crew cannot continue, do we find a partial solution with new characters or do we cancel the mission with an outcome code transform referencing the `SpaceMission.outcome = ‘Aborted’`?”           
3. **Payload Overlimit**: “If a new cargo **Payload** surpasses the maxPayloadMass for the assigned **LaunchVehicle**, do we forcibly remove some items or do we spawn a second mission referencing the same **Spacecraft**?”           
4. **DockingModule Fail**: “What if the **DockingModule** has capacity < the number of incoming vehicles—do we forcibly queue the vehicles or do some remain in orbit referencing the ‘SimulationModule’ fallback scenario?”           
5. **Mission Anomaly**: “If a certain **Mission** encountered a major anomaly that triggers ‘MissionAnomaly’, do we see the final mission outcome as partial success or do we forcibly mark it as ‘Mission.outcome=Failed’ in the pipeline?”           
6. **GroundControl Overload**: “Which **SpaceMission** objects rely on the same `GroundControl` that is also controlling too many concurrent tasks—does that degrade the successRate or produce new anomalies?”           
7. **Crew vs. SpaceWalk**: “If the assigned crew lacks the skill for a certain `SpaceWalk` requiring high durationHrs, do we forcibly cancel or do we reduce the planned walk? We can run a scenario in the pipeline to recalc mission success.”           
8. **Critical Timetable**: “If we shift the launchDate for a given `SpaceMission` earlier by 2 weeks, does that cause a scheduling conflict with the same `LaunchVehicle` or a partially assigned `LaunchSite`?”           
9. **Asteroid Intercept**: “Which BFS or multi-hop scenario scenarioIncludes a new ‘Battle’ or event from an asteroid threat—any reason we must create a code transform to handle the new risk of the mission path?”           
           
---  
                
## Ontology Structure: Core Classes / Entities (Domain Ontology)                
                
Below is a conceptual structure, with a **pseudocode** approach.         
        
                
                
                                                              
```mermaid                                                              
       
         
```                                                 
                                                            
---                                  
                                  
```pseudocode                                
      
        
                 
```                