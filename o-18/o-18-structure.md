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
Class: GalacticTradeNetwork          
  - networkID: string          
  - regionSector: string          
  - totalPopulation: long          // new data property          
  - dominantCurrency: string       // new data property          
          
Class: Planet          
  - planetID: string          
  - planetName: string          
  - climate: string          
  - gravityLevel: float            // new data property          
          
Class: SpacePort          
  - portID: string          
  - portName: string          
  - maxDockingSlots: int          
  - portSecurityRating: string     // new data property          
          
Class: TradeVessel          
  - vesselID: string          
  - vesselClass: string          
  - cargoCapacity: float          
  - crewCapacity: int              // new data property          
          
Class: CargoItem          
  - cargoID: string          
  - itemName: string          
  - mass: float          
  - declaredValue: float           // new data property          
          
Class: AlienSpecies          
  - speciesID: string          
  - speciesName: string          
  - avgLifespan: float          
          
Class: DiplomaticAgreement          
  - agreementID: string          
  - terms: string          
          
Class: TradeRoute          
  - routeID: string          
  - routeDistance: float          
  - routeStatus: string          
          
Class: CustomsCheckpoint          
  - checkpointID: string          
  - checkpointName: string          
  - complianceLevel: string          
          
Class: Merchant          
  - merchantID: string          
  - merchantName: string          
  - tradeReputation: string          
          
Class: Alliance          
  - allianceID: string          
  - allianceName: string          
          
Class: EnvironmentalHazard          
  - hazardID: string          
  - hazardType: string          
  - severityLevel: string          
          
Class: CurrencyExchange          
  - exchangeID: string          
  - currencyType: string          
  - rate: float          
          
Class: ContrabandItem          
  - contrabandID: string          
  - contrabandType: string          
          
Class: SpaceInsurance          
  - insuranceID: string          
  - coverageDetails: string          
          
Class: AstroSimulation          
  - simID: string          
  - scenarioName: string          
          
// Existing relationships:          
// includesPlanet (GalacticTradeNetwork → Planet, 1..*)          
// hasPort (Planet → SpacePort, 1..*)          
// dockedVessel (SpacePort → TradeVessel, 0..*)          
// carriesCargo (TradeVessel → CargoItem, 0..*)          
// inhabitedBy (Planet → AlienSpecies, 0..*)          
// governedBy (Planet → DiplomaticAgreement, 0..1)          
// assignedRoute (TradeVessel → TradeRoute, 0..1)          
// hasCheckpoint (TradeRoute → CustomsCheckpoint, 0..*)          
// belongsToAlliance (Planet → Alliance, 0..1)          
// facedHazard (TradeRoute → EnvironmentalHazard, 0..*)          
// usesExchange (Merchant → CurrencyExchange, 0..1)          
// flaggedContraband (CustomsCheckpoint → ContrabandItem, 0..*)          
// insuredBy (TradeVessel → SpaceInsurance, 0..1)          
// simAnalyzes (AstroSimulation → TradeRoute, 0..*)          
// dealsWith (AstroSimulation → ContrabandItem, 0..*)          
          
// New object properties (5 total):          
          
Relationship: investsIn (Merchant → TradeVessel, 0..*)            
  // e.g., a merchant might hold partial ownership stake in certain vessels          
          
Relationship: managesCheckpoint (Alliance → CustomsCheckpoint, 0..*)            
  // alliance authority can manage some checkpoint          
          
Relationship: referencesHazard (AstroSimulation → EnvironmentalHazard, 0..*)            
  // the simulation might incorporate hazard conditions          
          
Relationship: endorsesAgreement (Alliance → DiplomaticAgreement, 0..*)            
  // an alliance can endorse certain diplomatic agreements          
          
Relationship: monitorsPlanet (CurrencyExchange → Planet, 0..*)            
  // possibly an exchange has data feeds about planetary economics          
           
'''                  
