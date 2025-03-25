# Ontology #16: Healthcare Network & Clinical                             
                              
---                                 
                                 
## **Scenario-based competency questions** for Ontology #16: Healthcare Network & Clinical                                 
                                 
1. **Doctor Shortage**: “If half the **Physician** staff in a certain **MedicalDepartment** are on leave, can the existing department handle all scheduled **Appointment** objects, or must some appointments route to a second department or external clinic?”                                 
2. **Claim Coverage**: “If a certain **InsurancePlan** modifies coverageType, do we see incomplete coverage for existing **BillingAccount** references in the pipeline? Could we detect unbillable **MedicalRecord** items?”                                 
3. **Emergency Overflow**: “If a **Hospital** bedCapacity is over capacity, does that automatically re-route new appointments to a different hospital or remain in a queue? Which code transform handles that logic in Foundry?”                                 
4. **LabTest Failure**: “If a certain lab device is offline, do we forcibly mark ‘requiresLabTest’ as deferred, or do we link patients to a different test center referencing the same ‘MedicalNetwork’?”                                 
5. **Physician Transfer**: “If a **Physician** changes specialization from general to cardiology, do we break existing references to the old dept, or do we keep them with partial references for historical appointments?”                                 
6. **InsurancePlan Mergers**: “If two insurance plans unify, do we unify all relevant ‘coveredBy’ references, or do we keep separate coverage for each existing BillingAccount?”                                 
7. **Clinic No-Show**: “Which **Appointment** remain with status=‘NoShow’ for repeated visits, does that push any new ‘MedicalRecord’ with partial data or no data at all?”                                 
8. **Experimental Trials**: “If a new **ResearchStudy** references a ‘Patient’ group, but that patient has conflicting coverage or is assigned to a certain department, do we see any data pipeline conflict in Foundry?”                                 
9. **Pandemic Surge**: “Which hospitals must forcibly create new ICU expansions or partial bed expansions to handle an influx of patients? If the pipeline indicates bedCapacity < x, do we auto redirect or produce an alert?”                                 
                                 
---                         
                                   
                                      
## Ontology Structure: Core Classes / Entities (Domain Ontology)                                      
                                      
Below is a conceptual structure, with a **pseudocode** approach.                               
                              
                                      
                                      
                                                                                    
```mermaid                                                                                    
                             
                               
```                                                                       
                                                                                  
---                                                        
                                                        
```pseudocode                                                      
                            
                              
                                       
```                