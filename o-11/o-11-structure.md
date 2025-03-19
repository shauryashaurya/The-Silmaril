# Ontology Structure                                                                  
                                                                        
```mermaid                                                                        
graph TD                  
                  
%% Top-down layout, ensuring no colons or pipes in labels.                  
%% We now represent cardinalities in parentheses like (0-To-1), (0-To-Many), etc.                  
                  
%% =========================                  
%% CLASSES AND DATA PROPERTIES                  
%% =========================                  
                  
Character["Character<br>characterID<br>name<br>species<br>gender<br>affiliation<br>rank<br>forceSensitive boolean<br>starSign<br>cameoAppearance boolean"]                  
Jedi["Jedi<br>lightsaberColor<br>midiChlorianCount int<br>jediRank"]                  
Sith["Sith<br>darkSideLevel int<br>apprenticeOf<br>sithTitle"]                  
Droid["Droid<br>modelNumber<br>primaryFunction<br>owner<br>memoryWipes int"]                  
Spaceship["Spaceship<br>shipID<br>model<br>shipClass<br>speedRating float<br>hyperdriveEquipped boolean<br>uniqueName"]                  
Planet["Planet<br>planetID<br>planetName<br>starSystem<br>climate<br>population long<br>affiliation<br>orbitalPeriodDays float"]                  
StarSystem["StarSystem<br>systemID<br>systemName<br>coordinates"]                  
Faction["Faction<br>factionID<br>name<br>leader<br>primaryGoal<br>ideology"]                  
Battle["Battle<br>battleID<br>name<br>outcome<br>battleDate dateTime<br>casualties int"]                  
EventNode["Event<br>eventID<br>description<br>timestamp dateTime<br>significanceLevel"]                  
Weapon["Weapon<br>weaponID<br>name<br>weaponType<br>destructiveCapacity float"]                  
Lightsaber["Lightsaber<br>color<br>hiltDesign"]                  
ForceAbility["ForceAbility<br>abilityID<br>name<br>abilityType<br>strengthLevel float"]                  
Vehicle["Vehicle<br>vehicleID<br>type<br>speed float<br>terrainType"]                  
Mission["Mission<br>missionID<br>missionType<br>missionGoal<br>successRate float"]                  
AllianceBase["AllianceBase<br>baseID<br>name<br>hiddenLocation boolean"]                  
EmpireFacility["EmpireFacility<br>facilityID<br>name<br>securityLevel"]                  
RebelAllianceMember["RebelAllianceMember<br>memberID<br>joinedDate dateTime<br>role"]                  
EmpireMember["EmpireMember<br>memberID<br>joinedDate dateTime<br>rank"]                  
Creature["Creature<br>creatureID<br>speciesName<br>habitat<br>dangerLevel float"]                  
Technology["Technology<br>technologyID<br>techType<br>inventor<br>functionDescription"]                  
Artifact["Artifact<br>artifactID<br>artifactName<br>originEra<br>isCursed boolean<br>powerLevel float"]                  
Holocron["Holocron<br>holocronID<br>keeper<br>containsKnowledge"]                  
SpaceStation["SpaceStation<br>stationID<br>name<br>operationalStatus"]                  
DeathStar["DeathStar<br>weaponCapacity float<br>shieldStatus"]                  
BountyHunter["BountyHunter<br>hunterID<br>notorietyLevel<br>pricePerHunt float<br>lethalEfficiency float"]                  
Smuggler["Smuggler<br>smugglerID<br>smugglingSkill float<br>wantedStatus boolean"]                  
Politician["Politician<br>politicianID<br>politicalAffiliation<br>influenceLevel float"]                  
MilitaryUnit["MilitaryUnit<br>unitID<br>size int<br>deploymentStatus"]                  
SimulationScenario["SimulationScenario<br>scenarioID<br>description<br>outcome"]                  
Prophecy["Prophecy<br>prophecyID<br>prophecyText<br>fulfilled boolean"]                  
                  
%% =========================                  
%% SUBCLASS HIERARCHIES (DOTTED LINES)                  
%% use spaces around subClassOf to avoid parse errors                  
%% =========================                  
                  
Jedi -. subClassOf .-> Character                  
Sith -. subClassOf .-> Character                  
RebelAllianceMember -. subClassOf .-> Character                  
EmpireMember -. subClassOf .-> Character                  
                  
%% =========================                  
%% DISJOINT CLASSES (DOTTED LINES)                  
%% e.g., RebelAllianceMember vs EmpireMember                  
%% =========================                  
                  
RebelAllianceMember -. disjointWith .-> EmpireMember                  
                  
%% =========================                  
%% OBJECT PROPERTIES WITH CARDINALITIES IN PARENS                  
%% =========================                  
                  
Character -- "member_Of (0-To-1)" --> Faction                  
Character -- "leads_Faction (0-To-1)" --> Faction                  
Sith -- "apprentice_To (0-To-1)" --> Character                  
Jedi -- "master_Of (0-To-Many)" --> Character                  
Character -- "participates_In (0-To-Many)" --> Battle                  
Battle -- "located_At (0-To-1)" --> Planet                  
Battle -- "triggers_Event (0-To-Many)" --> EventNode                  
Droid -- "owned_By (0-To-1)" --> Character                  
Spaceship -- "piloted_By (0-To-Many)" --> Character                  
Planet -- "within_System (Exactly-1)" --> StarSystem                  
Weapon -- "wielded_By (0-To-Many)" --> Character                  
Character -- "has_Ability (0-To-Many)" --> ForceAbility                  
Vehicle -- "deployed_In (0-To-Many)" --> Battle                  
Mission -- "assigned_To (0-To-Many)" --> Character                  
Mission -- "mission_Location (0-To-1)" --> Planet                  
Faction -- "operates_Facility (0-To-Many)" --> EmpireFacility                  
Faction -- "owns_Base (0-To-Many)" --> AllianceBase                  
Creature -- "inhabits (0-To-1)" --> Planet                  
Technology -- "invented_By (0-To-1)" --> Character                  
Artifact -- "possessed_By (0-To-1)" --> Character                  
SpaceStation -- "controlled_By (0-To-1)" --> Faction                  
SimulationScenario -- "scenario_Includes (0-To-Many)" --> Battle                  
Prophecy -- "predicts (0-To-Many)" --> EventNode                  
Politician -- "influences (0-To-Many)" --> Faction                  
BountyHunter -- "hunts_Target (0-To-Many)" --> Character                  
Smuggler -- "allied_With (0-To-Many)" --> Character                  
MilitaryUnit -- "commanded_By (0-To-1)" --> Character                  
Holocron -- "guarded_By (0-To-1)" --> Jedi                  
                  
%% Additional expansions                  
Character -- "has_Sidekick (0-To-1)" --> Character                  
Faction -- "allied_With_Faction (0-To-Many)" --> Faction                  
Character -- "spied_On_By (0-To-Many)" --> Droid                  
Lightsaber -- "constructed_By (0-To-1)" --> Jedi                  
Battle -- "incorporates_Vehicle (0-To-Many)" --> Vehicle                  
Smuggler -- "hidden_In (0-To-1)" --> Spaceship                  
BountyHunter -- "steals_From (0-To-Many)" --> Smuggler                  
Jedi -- "studied_Holocron (0-To-Many)" --> Holocron                  
Politician -- "oversees_Unit (0-To-Many)" --> MilitaryUnit                  
Mission -- "protects_Artifact (0-To-Many)" --> Artifact                  
                  
%% =========================                  
%% PROPERTY RESTRICTIONS (DOTTED LINES)                  
%% e.g., short constraints or domain notes                  
%% =========================                  
                  
Droid -. "no_Force_Ability" .-> ForceAbility                  
Lightsaber -. "only_Jedi_Or_Sith" .-> Character                  
Battle -. "min_Factions_2" .-> Faction                  
Sith -. "apprentice_Master_Link" .-> Sith                  
Jedi -. "force_Sensitive_Only" .-> Character                  
                   
```                                                           
                                                                      
---                                            
                                            
```pseudocode                                                  
// ======================          
// CLASSES & DATA PROPERTIES          
// ======================          
          
Class: Building          
  - buildingID: string          
  - buildingName: string          
  - totalFloors: int          
  - managementCompany: string          
  - energyRating: float          
          
Class: Floor          
  - floorID: string          
  - floorNumber: int          
  - usableAreaSqFt: float          
  - occupancyCapacity: int          
          
Class: Zone          
  - zoneID: string          
  - zoneName: string          
  - zoneFunction: string    // e.g., Office, Hallway, ServerRoom          
  - areaSqFt: float          
          
Class: EquipmentResource          
  - equipmentID: string          
  - equipmentType: string  // HVACUnit, Lighting, SecurityCam, etc.          
  - status: string         // Running, Off, Maintenance          
  - powerRating: float          
          
Class: Sensor          
  - sensorID: string          
  - sensorType: string     // Temperature, Occupancy, AirQuality          
  - currentReading: float          
  - lastUpdateTime: dateTime          
          
Class: OccupantGroup          
  - groupID: string          
  - groupName: string          
  - occupantCount: int          
  - occupantType: string   // e.g., Employees, Visitors          
          
Class: Occupant          
  - occupantID: string          
  - occupantName: string          
  - occupantRole: string   // e.g., Employee, Guest          
  - comfortPreference: float          
          
Class: MaintenanceTask          
  - taskID: string          
  - description: string          
  - plannedStartTime: dateTime          
  - plannedEndTime: dateTime          
  - taskStatus: string     // e.g. Scheduled, InProgress, Completed          
          
Class: Supplier          
  - supplierID: string          
  - supplierName: string          
  - contactEmail: string          
          
Class: SimulationScenario          
  - scenarioID: string          
  - scenarioName: string          
  - hypothesis: string     // e.g., "HVAC fails in zone 2"          
  - predictedOutcome: string          
          
// ======================          
// OBJECT PROPERTIES w/ CARDINALITIES          
// ======================          
          
// Building structure          
Relationship: hasFloor (Building → Floor, 1-To-Many)          
Relationship: hasZone (Floor → Zone, 0-To-Many)          
          
// Equipment & Zones          
Relationship: locatedIn (EquipmentResource → Zone, 0-To-1)          
          
// Sensors & Zones or Equipment          
Relationship: monitorsZone (Sensor → Zone, 0-To-1)          
Relationship: monitorsEquipment (Sensor → EquipmentResource, 0-To-1)          
          
// Occupants & Zones          
Relationship: occupiesZone (Occupant → Zone, 0-To-1)          
Relationship: occupantGroupZone (OccupantGroup → Zone, 0-To-Many)          
          
// Maintenance          
Relationship: targetsEquipment (MaintenanceTask → EquipmentResource, 1-To-1)          
Relationship: performedBy (MaintenanceTask → Supplier, 0-To-1)          
// or if you have Technicians, you can link them, but we keep it simple          
          
// Building Supplier relationships          
Relationship: contractedSupplier (Building → Supplier, 0-To-Many)          
          
// Simulation & Scenarios          
Relationship: scenarioFocus (SimulationScenario → Zone, 0-To-Many)          
Relationship: scenarioEquipmentFail (SimulationScenario → EquipmentResource, 0-To-Many)          
          
// Additional occupant/equipment relationships          
Relationship: occupantUsesEquipment (Occupant → EquipmentResource, 0-To-Many)          
          
// ======================          
// SAMPLE RULES/CONSTRAINTS          
// ======================          
          
// 1) If EquipmentResource.status = "Maintenance", sensor readings in that zone might be partial or flagged          
// 2) A Floor can have multiple zones but must have at least one if floorNumber > 0          
// 3) If occupantCount in OccupantGroup > zoneFunction capacity, occupantGroup must be split          
// 4) A MaintenanceTask must have plannedStartTime < plannedEndTime          
// 5) If building’s energyRating < X, we might require new sensors or maintenance tasks          
// 6) If scenarioFocus references multiple zones, each zone must belong to the same building for the scenario          
// 7) occupantUsesEquipment => occupant must be in the same zone or a super-zone for that equipment          
// 8) If lastUpdateTime > 24 hours old for a sensor, produce an alert or degrade reliability of currentReading          
// 9) Only an EquipmentResource with status="Off" or "Maintenance" can be replaced or upgraded          
          
                  
                         
'''                  
