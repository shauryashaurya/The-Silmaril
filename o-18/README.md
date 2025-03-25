# Ontology #18 Galactic Trade & Alliance Domain ;)                                 
                                 
## Domain                                 
                                 
Let's have a little fun with this one.                                    
Models an interplanetary GalacticTradeNetwork with Planets, SpacePorts, TradeVessels, Routes, Checkpoints, Alliances, Contraband checks, etc.                                 
                                 
## Sample Competency Questions:                                 
* “Which planet belongs to which alliance, and which trade routes are subject to environmental hazards?”                                 
* “Which merchant uses which currency exchange, and do they carry contraband items?”                                 
* “Which trade vessel is insured by which space insurance plan?”                                    
                                 
---                                            
                                            
## **Scenario-based competency questions** for Ontology #18: Galactic Trade & Alliance Domain                                            
                                            
1. **Allied Diplomatic Rift**                                              
   - “If two **Factions** that share an `alliedWithFaction` relationship suddenly become rival due to a contraband scandal, which **TradeRoutes** or **CustomsCheckpoints** become inaccessible to each alliance’s merchants?”                                            
                                            
2. **Merchant Bankruptcy**                                              
   - “Which **Merchant** (alliedWith or investsIn certain vessels) goes bankrupt, preventing them from meeting supply obligations on an active route referencing `TradeVessel` or `CargoItem`?”                                            
                                            
3. **Hazard Escalation**                                              
   - “What if an existing **EnvironmentalHazard** intensifies from severityLevel=moderate to high—how many routes referencing `facedHazard` must be rerouted or closed?”                                            
                                            
4. **Insurance Gaps**                                              
   - “If **SpaceInsurance** coverage is partially invalidated for a certain vessel carrying cargo mass beyond the insured limit, do we forcibly restrict that route or produce an alert for the `CustomsCheckpoint`?”                                            
                                            
5. **Alliance Territorial Merge**                                              
   - “If an **Alliance** merges with a second alliance, do they unify `alliedWith` references to multiple planets, or do we force partial leftover routes not recognized by the new group?”                                            
                                            
6. **Contraband Loophole**                                              
   - “Which **ContrabandItem** is repeatedly flagged at a certain checkpoint but never triggers `Merchant` fines—do we see a potential corruption scenario requiring more strict `complianceLevel`?”                                            
                                            
7. **Drones or Attack**                                              
   - “If **TradeVessel** route is attacked by privateers, can the route remain valid or must it produce a new `facedHazard` referencing an unplanned hazard?”                                            
                                            
8. **Currency Collapse**                                              
   - “What if `CurrencyExchange` rate collapses for a major currency—do certain **Merchant** trades become unviable, and do they reroute or reduce cargo shipments?”                                            
                                            
9. **Fallen Planet**                                              
   - “If a key **Planet** in the **GalacticTradeNetwork** is devoured by a cosmic event, do we forcibly break all routes referencing that planet’s `SpacePort`, creating a partial meltdown scenario?”                                            
                                            
---                                             
                                                 
---                                                 
                                                 
## Ontology Structure: Core Classes / Entities (Domain Ontology)                                                 
                                                 
Below is a conceptual structure, with a **pseudocode** approach.                                          
                                         
                                                 
                                                 
                                                                                               
```mermaid                                                                                               
                                        
                                          
```                                                                                  
                                                                                             
---                                                                   
                                                                   
```pseudocode                                                                 
                                       
                                         
                                                  
```                