# Star Wars Data Generator - Data Dictionary
## Overview
This dataset contains information about the Star Wars original trilogy (Episodes IV-VI) including characters, locations, events, and relationships.
### Movies Included
- Episode IV: A New Hope (1977)
- Episode V: The Empire Strikes Back (1980)
- Episode VI: Return of the Jedi (1983)

### Abbreviations
- **BBY**: Before Battle of Yavin - Years before the destruction of the first Death Star in Episode IV
- **ABY**: After Battle of Yavin - Years after the destruction of the first Death Star in Episode IV
- **0 BBY**: The year of the Battle of Yavin (Death Star destruction) in Episode IV
- **3 ABY**: Approximately when the events of Empire Strikes Back occur
- **4 ABY**: Approximately when the events of Return of the Jedi occur

## Entities
### Characters
Individuals that appear in the Star Wars universe

| Field | Description |
| ----- | ----------- |
| characterID | Unique identifier for the character |
| name | Character's name |
| species | Character's species or race |
| gender | Character's gender |
| affiliation | Organization or faction the character belongs to |
| rank | Character's position or title within their organization |
| forceSensitive | Boolean indicating if the character can use the Force |
| starSign | Fictional star sign within the Star Wars universe |
| cameoAppearance | Boolean indicating if the character appears briefly |

### Jedis
Force-sensitive characters aligned with the light side

| Field | Description |
| ----- | ----------- |
| characterID | Reference to the base character |
| lightsaberColor | Color of their lightsaber (typically blue, green, or purple) |
| midiChlorianCount | Fictional measure of Force potential |
| jediRank | Rank within the Jedi Order (Padawan, Knight, Master, etc.) |

### Siths
Force-sensitive characters aligned with the dark side

| Field | Description |
| ----- | ----------- |
| characterID | Reference to the base character |
| darkSideLevel | Measure of dark side corruption (0-100) |
| apprenticeOf | Their Sith master (if applicable) |
| sithTitle | Sith title (typically 'Darth') |

### Droids
Robotic characters

| Field | Description |
| ----- | ----------- |
| characterID | Reference to the base character |
| modelNumber | Droid model or series designation |
| primaryFunction | Main purpose the droid was built for |
| owner | Character who owns or is associated with the droid |
| memoryWipes | Number of times the droid's memory has been reset |

### Planets
Celestial bodies that serve as locations

| Field | Description |
| ----- | ----------- |
| planetID | Unique identifier for the planet |
| planetName | Name of the planet |
| starSystem | Star system the planet belongs to |
| climate | Predominant climate type |
| population | Approximate number of inhabitants |
| affiliation | Faction controlling the planet |
| orbitalPeriodDays | Days required for one orbit around its star |

### Spaceships
Vehicles capable of space travel

| Field | Description |
| ----- | ----------- |
| shipID | Unique identifier for the ship |
| model | Ship's model designation |
| shipClass | Category of spaceship |
| speedRating | Relative speed capability |
| hyperdriveEquipped | Boolean indicating FTL travel capability |
| uniqueName | Specific name for notable ships |
| canTravelInterstellar | Boolean indicating capability for interstellar travel |

### Factions
Political or military organizations

| Field | Description |
| ----- | ----------- |
| factionID | Unique identifier for the faction |
| name | Name of the organization |
| leader | Character leading the faction |
| primaryGoal | Main objective of the faction |
| ideology | Guiding principles of the faction |

### Battles
Military conflicts

| Field | Description |
| ----- | ----------- |
| battleID | Unique identifier for the battle |
| name | Name of the battle |
| outcome | Result of the conflict |
| battleDate | Date when the battle occurred |
| casualties | Approximate number of deaths |
| factions | List of factions involved in the battle |

### Events
Significant moments in the timeline

| Field | Description |
| ----- | ----------- |
| eventID | Unique identifier for the event |
| description | What happened during the event |
| timestamp | When the event occurred (BBY/ABY format) |
| significanceLevel | Importance of the event (Low/Medium/High/Galactic) |
| participants | Characters involved in the event |
| location | Where the event took place |
| battle | Associated battle (if applicable) |
| quote | Memorable quote from the event |
| ship | Associated ship (if applicable) |

### Force Abilities
Powers that Force-sensitive characters can use

| Field | Description |
| ----- | ----------- |
| abilityID | Unique identifier for the ability |
| name | Name of the Force power |
| type | Category of ability |
| difficultyLevel | Difficulty to master (1-10) |
| isLightSide | Boolean indicating light side association |
| isDarkSide | Boolean indicating dark side association |

### Lightsabers
Energy sword weapons used by Jedi and Sith

| Field | Description |
| ----- | ----------- |
| weaponID | Unique identifier for the lightsaber |
| name | Name of the lightsaber (if notable) |
| weaponType | Always 'Lightsaber' |
| destructiveCapacity | Measure of weapon power |
| color | Color of the lightsaber blade |
| hiltDesign | Style of the lightsaber handle |

### Artifacts
Notable objects of significance

| Field | Description |
| ----- | ----------- |
| artifactID | Unique identifier for the artifact |
| name | Name of the artifact |
| originEra | Time period when the artifact was created |
| forceRelated | Boolean indicating if connected to the Force |

### Technologies
Scientific and technological developments

| Field | Description |
| ----- | ----------- |
| technologyID | Unique identifier for the technology |
| techType | Category of technology |
| inventor | Creator of the technology |
| functionDescription | What the technology does |

### Vehicles
Ground, air, or sea transportation

| Field | Description |
| ----- | ----------- |
| vehicleID | Unique identifier for the vehicle |
| type | Model or category of vehicle |
| speed | Maximum speed in appropriate units |
| terrainType | Environment the vehicle operates in |

### Creatures
Non-sentient life forms

| Field | Description |
| ----- | ----------- |
| creatureID | Unique identifier for the creature |
| speciesName | Type of creature |
| habitat | Environment where the creature lives |
| dangerLevel | Threat level (0.1-10.0) |

### Missions
Objectives undertaken by characters

| Field | Description |
| ----- | ----------- |
| missionID | Unique identifier for the mission |
| missionType | Category of mission |
| missionGoal | Objective of the mission |
| successRate | Probability of success (0-100) |

## Relationships
Connections between entities

| Type | Description |
| ---- | ----------- |
| biologicalParentOf | Genetic parent-child relationship |
| sibling | Characters who share at least one parent |
| hasSidekick | Character with a loyal companion |
| ownedBy | Droid belonging to a character |
| pilotedBy | Ship operated by a character |
| apprenticeOf | Force user trained by another Force user |
| memberOf | Character belonging to a faction |

## Timelines
Chronological sequences of events from each film

- **episode_4**: Events from Episode IV: A New Hope (0 BBY)
- **episode_5**: Events from Episode V: The Empire Strikes Back (3 ABY)
- **episode_6**: Events from Episode VI: Return of the Jedi (4 ABY)

## Key Events
### Destructionofalderaan
- **Description**: The Empire destroys Princess Leia's home planet
- **Film**: Episode IV: A New Hope
- **Timestamp**: 0 BBY
- **Key Characters**: Darth Vader, Grand Moff Tarkin, Princess Leia

### Battleofyavin
- **Description**: The Rebels destroy the first Death Star
- **Film**: Episode IV: A New Hope
- **Timestamp**: 0 BBY
- **Key Characters**: Luke Skywalker, Han Solo, Darth Vader

### Battleofhoth
- **Description**: The Empire attacks the Rebel base on Hoth
- **Film**: Episode V: The Empire Strikes Back
- **Timestamp**: 3 ABY
- **Key Characters**: Luke Skywalker, Princess Leia, Han Solo, Darth Vader

### Iamyourfather
- **Description**: Darth Vader reveals to Luke that he is his father
- **Film**: Episode V: The Empire Strikes Back
- **Timestamp**: 3 ABY
- **Key Characters**: Luke Skywalker, Darth Vader
- **Memorable Quote**: "No, I am your father."

### Hansolocarbonite
- **Description**: Han Solo is frozen in carbonite
- **Film**: Episode V: The Empire Strikes Back
- **Timestamp**: 3 ABY
- **Key Characters**: Han Solo, Princess Leia, Darth Vader, Boba Fett

### Jabbapalace
- **Description**: Rescue of Han Solo from Jabba the Hutt
- **Film**: Episode VI: Return of the Jedi
- **Timestamp**: 4 ABY
- **Key Characters**: Luke Skywalker, Princess Leia, Han Solo, Jabba the Hutt

### Vaderredemption
- **Description**: Darth Vader turns against the Emperor to save Luke
- **Film**: Episode VI: Return of the Jedi
- **Timestamp**: 4 ABY
- **Key Characters**: Luke Skywalker, Darth Vader, Emperor Palpatine

### Battleofendor
- **Description**: The Rebels destroy the second Death Star
- **Film**: Episode VI: Return of the Jedi
- **Timestamp**: 4 ABY
- **Key Characters**: Lando Calrissian, Admiral Ackbar

