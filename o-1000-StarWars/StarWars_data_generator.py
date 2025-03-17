import random
import datetime
import uuid
import json
from typing import Dict, List, Any, Optional, Union


class StarWarsDataGenerator:
    """
    A data generator for a Star Wars ontology based on Episodes 4-6.
    Creates realistic-looking data objects and relationships.
    """

    def __init__(self, seed=None):
        """Initialize the generator with optional seed for reproducibility"""
        if seed:
            random.seed(seed)

        # Initialize database dictionaries for each entity type
        self.characters = {}
        self.jedis = {}
        self.siths = {}
        self.droids = {}
        self.spaceships = {}
        self.planets = {}
        self.star_systems = {}
        self.factions = {}
        self.battles = {}
        self.events = {}
        self.weapons = {}
        self.lightsabers = {}
        self.force_abilities = {}

        # Load reference data
        self._initialize_reference_data()

    def _initialize_reference_data(self):
        """Set up the reference data for generating realistic Star Wars content"""
        # Species
        self.species = ["Human", "Wookiee", "Rodian", "Twi'lek", "Mon Calamari",
                        "Ewok", "Hutt", "Gungan", "Zabrak", "Trandoshan"]

        # Star systems
        self.system_names = ["Tatoo", "Alderaan", "Hoth", "Dagobah", "Bespin",
                             "Endor", "Yavin", "Corellia", "Kashyyyk", "Naboo"]

        # Planet climate types
        self.climates = ["Desert", "Temperate", "Frozen", "Tropical", "Gaseous",
                         "Volcanic", "Forest", "Swamp", "Ocean", "Mountainous"]

        # Faction names
        self.faction_names = ["Rebel Alliance", "Galactic Empire", "Hutt Cartel",
                              "Bounty Hunters Guild", "Mandalorians", "Trade Federation"]

        # Faction ideologies
        self.ideologies = ["Democracy", "Authoritarian Control", "Criminal Enterprise",
                           "Profit Seeking", "Warrior Culture", "Sith Doctrine"]

        # Force abilities
        self.force_ability_names = ["Force Push", "Force Lightning", "Mind Trick",
                                    "Force Choke", "Force Jump", "Battle Meditation",
                                    "Force Healing", "Force Vision"]

        # Force ability types
        self.force_ability_types = ["Offensive",
                                    "Defensive", "Control", "Sense", "Alter"]

        # Lightsaber colors
        self.lightsaber_colors = ["Blue", "Green",
                                  "Red", "Purple", "Yellow", "White"]

        # Lightsaber hilt designs
        self.hilt_designs = ["Standard", "Curved",
                             "Double-bladed", "Cross-guard", "Custom"]

        # Weapon types
        self.weapon_types = ["Blaster", "Rifle", "Cannon", "Thermal Detonator", "Vibroblade",
                             "Bowcaster", "Ion Cannon", "Flamethrower"]

        # Battle names template
        self.battle_templates = [
            "Battle of {planet}",
            "Assault on {planet}",
            "Siege of {planet}",
            "Skirmish at {planet}",
            "{planet} Offensive"
        ]

        # Droid models
        self.droid_models = ["R2 Series", "C-3PO Protocol", "B1 Battle", "IG Assassin",
                             "R5 Astromech", "2-1B Medical", "GNK Power", "EV-9D9 Supervisor"]

        # Droid functions
        self.droid_functions = ["Astromech", "Protocol", "Battle", "Assassin",
                                "Medical", "Power", "Mining", "Interrogation"]

        # Ship models
        self.ship_models = ["X-Wing", "TIE Fighter", "Star Destroyer", "Millennium Falcon",
                            "Y-Wing", "A-Wing", "Lambda Shuttle", "Nebulon-B Frigate"]

        # Ship classes
        self.ship_classes = ["Starfighter", "Freighter", "Cruiser", "Destroyer",
                             "Shuttle", "Transport", "Capital Ship", "Corvette"]

        # Canon character names (small selection from the original trilogy)
        self.canon_characters = [
            {"name": "Luke Skywalker", "species": "Human", "gender": "Male",
                "affiliation": "Rebel Alliance", "forceSensitive": True},
            {"name": "Leia Organa", "species": "Human", "gender": "Female",
                "affiliation": "Rebel Alliance", "forceSensitive": True},
            {"name": "Han Solo", "species": "Human", "gender": "Male",
                "affiliation": "Rebel Alliance", "forceSensitive": False},
            {"name": "Darth Vader", "species": "Human", "gender": "Male",
                "affiliation": "Galactic Empire", "forceSensitive": True},
            {"name": "Emperor Palpatine", "species": "Human", "gender": "Male",
                "affiliation": "Galactic Empire", "forceSensitive": True},
            {"name": "Obi-Wan Kenobi", "species": "Human", "gender": "Male",
                "affiliation": "Rebel Alliance", "forceSensitive": True},
            {"name": "Chewbacca", "species": "Wookiee", "gender": "Male",
                "affiliation": "Rebel Alliance", "forceSensitive": False},
            {"name": "C-3PO", "species": "Droid", "gender": "Programming",
                "affiliation": "Rebel Alliance", "forceSensitive": False},
            {"name": "R2-D2", "species": "Droid", "gender": "Programming",
                "affiliation": "Rebel Alliance", "forceSensitive": False},
            {"name": "Lando Calrissian", "species": "Human", "gender": "Male",
                "affiliation": "Rebel Alliance", "forceSensitive": False},
            {"name": "Boba Fett", "species": "Human", "gender": "Male",
                "affiliation": "Bounty Hunters Guild", "forceSensitive": False},
            {"name": "Jabba the Hutt", "species": "Hutt", "gender": "Male",
                "affiliation": "Hutt Cartel", "forceSensitive": False}
        ]

        # Canon planets (small selection)
        self.canon_planets = [
            {"name": "Tatooine", "climate": "Desert", "system": "Tatoo"},
            {"name": "Hoth", "climate": "Frozen", "system": "Hoth"},
            {"name": "Endor", "climate": "Forest", "system": "Endor"},
            {"name": "Dagobah", "climate": "Swamp", "system": "Dagobah"},
            {"name": "Bespin", "climate": "Gaseous", "system": "Bespin"},
            {"name": "Yavin 4", "climate": "Jungle", "system": "Yavin"},
            {"name": "Alderaan", "climate": "Temperate", "system": "Alderaan"},
            {"name": "Coruscant", "climate": "Temperate", "system": "Coruscant"}
        ]

        # Canon ships
        self.canon_ships = [
            {"name": "Millennium Falcon",
                "model": "YT-1300 Freighter", "class": "Freighter"},
            {"name": "X-Wing Red Five", "model": "T-65 X-Wing", "class": "Starfighter"},
            {"name": "Slave I", "model": "Firespray-31", "class": "Patrol Craft"},
            {"name": "Executor", "model": "Executor-class",
                "class": "Super Star Destroyer"},
            {"name": "Death Star", "model": "DS-1 Orbital Battle Station",
                "class": "Space Station"}
        ]

    def generate_id(self, prefix=""):
        """Generate a unique ID with optional prefix"""
        return f"{prefix}{uuid.uuid4().hex[:8]}"

    def generate_character(self, use_canon=True) -> Dict[str, Any]:
        """Generate a character, optionally using canon characters"""
        if use_canon and random.random() < 0.7:  # 70% chance to use canon character
            template = random.choice(self.canon_characters)
            char_id = self.generate_id("char_")

            character = {
                "characterID": char_id,
                "name": template["name"],
                "species": template["species"],
                "gender": template["gender"],
                "affiliation": template["affiliation"],
                "rank": random.choice(["Commander", "Captain", "Lieutenant", "General", "Admiral", "Private"]),
                "forceSensitive": template["forceSensitive"],
                "starSign": random.choice(["Krayt", "Sarlacc", "Bantha", "Rancor", "Mynock"]),
                "cameoAppearance": random.random() < 0.1  # 10% chance for cameo
            }
        else:
            char_id = self.generate_id("char_")
            character = {
                "characterID": char_id,
                "name": f"SW-{random.randint(1000, 9999)}",
                "species": random.choice(self.species),
                "gender": random.choice(["Male", "Female", "Other", "Unknown"]),
                "affiliation": random.choice(self.faction_names),
                "rank": random.choice(["Commander", "Captain", "Lieutenant", "General", "Admiral", "Private"]),
                "forceSensitive": random.random() < 0.2,  # 20% chance of force sensitivity
                "starSign": random.choice(["Krayt", "Sarlacc", "Bantha", "Rancor", "Mynock"]),
                "cameoAppearance": random.random() < 0.1  # 10% chance for cameo
            }

        self.characters[char_id] = character
        return character

    def generate_jedi(self, character=None) -> Dict[str, Any]:
        """Generate a Jedi instance, optionally based on existing character"""
        if not character:
            character = self.generate_character()
            character["forceSensitive"] = True  # Jedis must be force sensitive

        # According to rule #7, only Jedi or Sith can be force sensitive
        if not character["forceSensitive"]:
            character["forceSensitive"] = True

        jedi_id = character["characterID"]

        jedi = {
            **character,  # Inherit character properties (rule #1)
            # No red for Jedi
            "lightsaberColor": random.choice(["Blue", "Green", "Purple", "Yellow"]),
            "midiChlorianCount": random.randint(8000, 20000),
            "jediRank": random.choice(["Padawan", "Knight", "Master", "Grand Master"])
        }

        self.jedis[jedi_id] = jedi
        return jedi

    def generate_sith(self, character=None) -> Dict[str, Any]:
        """Generate a Sith instance, optionally based on existing character"""
        if not character:
            character = self.generate_character()
            character["forceSensitive"] = True  # Siths must be force sensitive
            # Siths are typically Empire-aligned
            character["affiliation"] = "Galactic Empire"

        # According to rule #7, only Jedi or Sith can be force sensitive
        if not character["forceSensitive"]:
            character["forceSensitive"] = True

        sith_id = character["characterID"]
        dark_side_level = random.randint(60, 100)

        # According to rule #10, if darkSideLevel > 80, sithTitle must exist
        sith_title = "Darth" if dark_side_level > 80 else ""

        sith = {
            **character,  # Inherit character properties (rule #1)
            "darkSideLevel": dark_side_level,
            "apprenticeOf": "",  # Will be filled if master is assigned
            "sithTitle": sith_title
        }

        self.siths[sith_id] = sith
        return sith

    def generate_droid(self) -> Dict[str, Any]:
        """Generate a droid"""
        droid_id = self.generate_id("droid_")
        model = random.choice(self.droid_models)
        function = random.choice(self.droid_functions)

        droid = {
            "characterID": droid_id,
            "name": f"{model[0]}-{random.randint(1000, 9999)}",
            "species": "Droid",
            "gender": "Programming",
            "affiliation": random.choice(self.faction_names),
            "rank": "Technical Unit",
            "forceSensitive": False,  # According to rule #2, droids cannot have Force abilities
            "starSign": "None",
            "cameoAppearance": random.random() < 0.1,
            "modelNumber": model,
            "primaryFunction": function,
            "owner": "",  # Will be filled if owner is assigned
            "memoryWipes": random.randint(0, 10)
        }

        self.droids[droid_id] = droid
        return droid

    def generate_planet(self, use_canon=True) -> Dict[str, Any]:
        """Generate a planet, optionally using canon planets"""
        if use_canon and random.random() < 0.7:  # 70% chance to use canon planet
            template = random.choice(self.canon_planets)
            planet_id = self.generate_id("planet_")

            # Handle rule #12: orbital period < 1000 if not Tatooine
            if template["name"] == "Tatooine":
                orbital_period = random.uniform(800, 1200)
            else:
                orbital_period = random.uniform(200, 999)

            planet = {
                "planetID": planet_id,
                "planetName": template["name"],
                "starSystem": template["system"],
                "climate": template["climate"],
                "population": random.randint(1000000, 20000000000),
                "affiliation": random.choice(self.faction_names),
                "orbitalPeriodDays": orbital_period
            }
        else:
            planet_id = self.generate_id("planet_")
            planet_name = f"Planet-{random.randint(1000, 9999)}"

            # Handle rule #12: orbital period < 1000 if not Tatooine
            if planet_name == "Tatooine":
                orbital_period = random.uniform(800, 1200)
            else:
                orbital_period = random.uniform(200, 999)

            planet = {
                "planetID": planet_id,
                "planetName": planet_name,
                "starSystem": random.choice(self.system_names),
                "climate": random.choice(self.climates),
                "population": random.randint(1000000, 20000000000),
                "affiliation": random.choice(self.faction_names),
                "orbitalPeriodDays": orbital_period
            }

        self.planets[planet_id] = planet
        return planet

    def generate_spaceship(self, use_canon=True) -> Dict[str, Any]:
        """Generate a spaceship, optionally using canon ships"""
        if use_canon and random.random() < 0.6:  # 60% chance to use canon ship
            template = random.choice(self.canon_ships)
            ship_id = self.generate_id("ship_")

            ship = {
                "shipID": ship_id,
                "model": template["model"],
                "shipClass": template["class"],
                "speedRating": random.uniform(0.5, 2.0),
                "hyperdriveEquipped": True,  # Famous ships usually have hyperdrives
                "uniqueName": template["name"]
            }
        else:
            ship_id = self.generate_id("ship_")
            model = random.choice(self.ship_models)
            ship_class = random.choice(self.ship_classes)

            ship = {
                "shipID": ship_id,
                "model": model,
                "shipClass": ship_class,
                "speedRating": random.uniform(0.5, 2.0),
                "hyperdriveEquipped": random.random() < 0.8,  # 80% chance of having hyperdrive
                "uniqueName": f"{model}-{random.randint(1000, 9999)}"
            }

        self.spaceships[ship_id] = ship
        return ship

    def generate_faction(self) -> Dict[str, Any]:
        """Generate a faction"""
        faction_id = self.generate_id("faction_")
        name_index = random.randint(0, len(self.faction_names) - 1)
        ideology_index = random.randint(0, len(self.ideologies) - 1)

        faction = {
            "factionID": faction_id,
            "name": self.faction_names[name_index],
            "leader": "",  # Will be filled when characters are assigned
            "primaryGoal": random.choice(["Galactic Domination", "Freedom", "Wealth", "Power", "Peace", "Balance"]),
            "ideology": self.ideologies[ideology_index]
        }

        # Rule #14: If ideology is 'Sith Doctrine', leader must reference a Sith
        if faction["ideology"] == "Sith Doctrine":
            # Create a placeholder - in a full implementation this would be properly linked later
            faction["leaderMustBeSith"] = True

        self.factions[faction_id] = faction
        return faction

    def generate_battle(self) -> Dict[str, Any]:
        """Generate a battle"""
        battle_id = self.generate_id("battle_")
        planet = self.generate_planet() if not self.planets else random.choice(
            list(self.planets.values()))

        # Generate random date between 0 BBY and 4 ABY (Episode 4-6 timeframe)
        year = random.randint(-1, 4)  # -1 is 1 BBY, 0 is 0 ABY, etc.
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        battle_date = datetime.datetime(
            year + 1977, month, day)  # Using 1977 as "0 ABY" base

        # Apply rule #13: If Empire wins, casualties must be > 0
        outcome = random.choice(
            ["Rebel Alliance Victory", "Empire Victory", "Stalemate", "Inconclusive"])
        if outcome == "Empire Victory":
            # Significant casualties for Empire victory
            casualties = random.randint(100, 10000)
        else:
            # Could be 0 for other outcomes
            casualties = random.randint(0, 10000)

        template = random.choice(self.battle_templates)
        battle_name = template.format(planet=planet["planetName"])

        battle = {
            "battleID": battle_id,
            "name": battle_name,
            "outcome": outcome,
            "battleDate": battle_date.strftime("%Y-%m-%d"),
            "casualties": casualties,
            # Rule #4: Each battle must have at least two factions
            "factions": []  # To be populated with at least 2 factions
        }

        self.battles[battle_id] = battle
        return battle

    def generate_event(self) -> Dict[str, Any]:
        """Generate a Star Wars event"""
        event_id = self.generate_id("event_")

        # Create a timestamp between Episode 4 and 6 (0 BBY to 4 ABY)
        year = random.randint(-1, 4)  # -1 is 1 BBY, 0 is 0 ABY, etc.
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        # Using 1977 as "0 ABY" base
        timestamp = datetime.datetime(year + 1977, month, day)

        event_templates = [
            "The {character} discovers a hidden {item} on {planet}",
            "{character} confronts {character2} during the Battle of {planet}",
            "A secret alliance forms between {faction} and {faction2}",
            "{character} reveals a shocking truth to {character2}",
            "The destruction of {item} by {character}",
            "{character} learns to use the Force ability {force_ability}",
            "The {faction} establishes a new base on {planet}",
            "{character} escapes from {character2} using the {ship}"
        ]

        template = random.choice(event_templates)

        # Create placeholder description - in a full implementation,
        # we would populate with actual entities
        description = template.format(
            character="[Character]",
            character2="[Character]",
            item="[Item]",
            planet="[Planet]",
            faction="[Faction]",
            faction2="[Faction]",
            force_ability="[Force Ability]",
            ship="[Ship]"
        )

        event = {
            "eventID": event_id,
            "description": description,
            "timestamp": timestamp.strftime("%Y-%m-%d"),
            "significanceLevel": random.choice(["Low", "Medium", "High", "Galactic"])
        }

        self.events[event_id] = event
        return event

    def generate_lightsaber(self) -> Dict[str, Any]:
        """Generate a lightsaber"""
        lightsaber_id = self.generate_id("saber_")

        lightsaber = {
            "weaponID": lightsaber_id,
            "name": f"Lightsaber of {random.randint(1000, 9999)}",
            "weaponType": "Lightsaber",
            "destructiveCapacity": random.uniform(80.0, 100.0),
            "color": random.choice(self.lightsaber_colors),
            "hiltDesign": random.choice(self.hilt_designs)
        }

        self.lightsabers[lightsaber_id] = lightsaber
        return lightsaber

    def generate_force_ability(self) -> Dict[str, Any]:
        """Generate a Force ability"""
        ability_id = self.generate_id("force_")

        ability = {
            "abilityID": ability_id,
            "name": random.choice(self.force_ability_names),
            "abilityType": random.choice(self.force_ability_types),
            "strengthLevel": random.uniform(1.0, 10.0)
        }

        self.force_abilities[ability_id] = ability
        return ability

    def generate_vader_luke_revelation(self) -> Dict[str, Any]:
        """
        Generate the famous "I am your father" revelation as an Event
        with proper character references
        """
        # Create or retrieve Darth Vader
        vader = None
        for char_id, char in self.characters.items():
            if char["name"] == "Darth Vader":
                vader = char
                break

        if not vader:
            # Create Vader and make him a Sith
            vader_char = {
                "characterID": self.generate_id("char_"),
                "name": "Darth Vader",
                "species": "Human",
                "gender": "Male",
                "affiliation": "Galactic Empire",
                "rank": "Supreme Commander",
                "forceSensitive": True,
                "starSign": "Unknown",
                "cameoAppearance": False
            }
            self.characters[vader_char["characterID"]] = vader_char

            vader = self.generate_sith(vader_char)
            vader["darkSideLevel"] = 95
            vader["sithTitle"] = "Darth"
            vader["apprenticeOf"] = "Emperor Palpatine"

        # Create or retrieve Luke Skywalker
        luke = None
        for char_id, char in self.characters.items():
            if char["name"] == "Luke Skywalker":
                luke = char
                break

        if not luke:
            # Create Luke and make him a Jedi
            luke_char = {
                "characterID": self.generate_id("char_"),
                "name": "Luke Skywalker",
                "species": "Human",
                "gender": "Male",
                "affiliation": "Rebel Alliance",
                "rank": "Commander",
                "forceSensitive": True,
                "starSign": "Unknown",
                "cameoAppearance": False
            }
            self.characters[luke_char["characterID"]] = luke_char

            luke = self.generate_jedi(luke_char)
            luke["lightsaberColor"] = "Green"
            luke["jediRank"] = "Padawan"

        # Create the revelation event
        event_id = self.generate_id("event_")

        event = {
            "eventID": event_id,
            "description": "Darth Vader reveals to Luke Skywalker that he is his father",
            "timestamp": "3-ABY",  # Empire Strikes Back timeframe
            "significanceLevel": "High",
            "location": "Cloud City, Bespin",
            "participants": [vader["characterID"], luke["characterID"]],
            "quote": "No, I am your father."  # The actual quote, not the misquoted version
        }

        # Add a relationship between Vader and Luke (we need to extend the ontology for this)
        # Since our ontology doesn't explicitly have a biological relationship,
        # we're adding it as a custom relationship
        family_relation = {
            "relationshipType": "biologicalParentOf",
            "parent": vader["characterID"],
            "child": luke["characterID"]
        }

        # Add the event and relationship to data
        self.events[event_id] = event

        if not hasattr(self, 'relationships'):
            self.relationships = []

        self.relationships.append(family_relation)

        return {
            "event": event,
            "relationship": family_relation,
            "vader": vader,
            "luke": luke
        }

    def generate_dataset(self, num_characters=10, num_battles=3, num_events=5,
                         include_vader_luke=True) -> Dict[str, Any]:
        """
        Generate a complete Star Wars dataset with interconnected entities

        Args:
            num_characters: Number of characters to generate
            num_battles: Number of battles to generate
            num_events: Number of events to generate
            include_vader_luke: Whether to include the Vader-Luke revelation

        Returns:
            Dict containing all generated data
        """
        # Generate factions first (needed for other entities)
        for _ in range(3):
            self.generate_faction()

        # Generate characters
        characters = []
        for _ in range(num_characters):
            characters.append(self.generate_character())

        # Ensure some Jedi and Sith are created
        jedis = []
        siths = []
        for i in range(2):
            if i < len(characters):
                jedis.append(self.generate_jedi(characters[i]))
            else:
                jedis.append(self.generate_jedi())

        for i in range(2, 4):
            if i < len(characters):
                siths.append(self.generate_sith(characters[i]))
            else:
                siths.append(self.generate_sith())

        # Generate droids
        droids = []
        for _ in range(3):
            droids.append(self.generate_droid())

        # Generate planets
        planets = []
        for _ in range(5):
            planets.append(self.generate_planet())

        # Generate battles
        battles = []
        for _ in range(num_battles):
            battle = self.generate_battle()

            # Ensure rule #4: Each battle must have at least two factions
            factions = list(self.factions.values())
            if len(factions) >= 2:
                battle["factions"] = [
                    factions[0]["factionID"],
                    factions[1]["factionID"]
                ]

                # Rule #9: If "Battle.outcome = 'AllianceVictory'," at least one faction must be "Rebel Alliance"
                if battle["outcome"] == "Rebel Alliance Victory":
                    # Check if Rebel Alliance exists in our factions
                    rebel_alliance_factions = [
                        f for f in factions if f["name"] == "Rebel Alliance"]

                    if not rebel_alliance_factions:
                        # If there's no Rebel Alliance faction, change the outcome
                        battle["outcome"] = "Empire Victory"
                    else:
                        # Ensure at least one faction is Rebel Alliance
                        battle["factions"][0] = rebel_alliance_factions[0]["factionID"]

            battles.append(battle)

        # Generate events
        events = []
        for _ in range(num_events):
            event = self.generate_event()
            events.append(event)

        # Generate special "I am your father" event if requested
        if include_vader_luke:
            vader_luke_data = self.generate_vader_luke_revelation()
            events.append(vader_luke_data["event"])

        # Generate force abilities
        force_abilities = []
        for _ in range(5):
            force_abilities.append(self.generate_force_ability())

        # Generate lightsabers
        lightsabers = []
        for _ in range(3):
            lightsabers.append(self.generate_lightsaber())

        # Apply rule #3: Only Jedi or Sith may have Lightsaber
        # Assign lightsabers to force users
        for i, lightsaber in enumerate(lightsabers):
            force_users = jedis + siths
            if i < len(force_users):
                # Create wielded_by relationship
                if not hasattr(self, 'wielded_by_relationships'):
                    self.wielded_by_relationships = []

                self.wielded_by_relationships.append({
                    "weapon": lightsaber["weaponID"],
                    "character": force_users[i]["characterID"]
                })

        # Apply other rules and constraints
        self._apply_ontology_rules()

        # Compile the complete dataset
        dataset = {
            "characters": self.characters,
            "jedis": self.jedis,
            "siths": self.siths,
            "droids": self.droids,
            "planets": self.planets,
            "spaceships": self.spaceships,
            "factions": self.factions,
            "battles": self.battles,
            "events": self.events,
            "force_abilities": self.force_abilities,
            "lightsabers": self.lightsabers,
            "relationships": getattr(self, 'relationships', []),
            "wielded_by": getattr(self, 'wielded_by_relationships', [])
        }

        return dataset

    def _apply_ontology_rules(self):
        """Apply various rules and constraints from the ontology"""
        # Rule #2: Droid cannot have ForceAbility
        for droid_id in self.droids:
            if hasattr(self, 'hasAbility_relationships'):
                # Remove any force abilities assigned to droids
                self.hasAbility_relationships = [
                    rel for rel in self.hasAbility_relationships
                    if rel["character"] != droid_id
                ]

        # Rule #5: A Character can be either RebelAllianceMember or EmpireMember, but not both
        for char_id, char in self.characters.items():
            if "affiliation" in char:
                if char["affiliation"] == "Rebel Alliance":
                    char["isRebelMember"] = True
                    char["isEmpireMember"] = False
                elif char["affiliation"] == "Galactic Empire":
                    char["isRebelMember"] = False
                    char["isEmpireMember"] = True

        # Rule #6: If apprenticeTo(Sith -> Character), that Character must be a Sith
        for sith_id, sith in self.siths.items():
            if sith["apprenticeOf"] and sith["apprenticeOf"] not in self.siths:
                # The master must be a Sith - find a valid one
                valid_masters = [s for s_id,
                                 s in self.siths.items() if s_id != sith_id]
                if valid_masters:
                    master = random.choice(valid_masters)
                    sith["apprenticeOf"] = master["name"]

        # Rule #8: If spaceship.hyperdriveEquipped = false, restrict interstellar travel
        for ship_id, ship in self.spaceships.items():
            if not ship["hyperdriveEquipped"]:
                ship["canTravelInterstellar"] = False
            else:
                ship["canTravelInterstellar"] = True

        # Rule #10: If Sith.darkSideLevel > 80, then sithTitle must exist
        for sith_id, sith in self.siths.items():
            if sith["darkSideLevel"] > 80 and not sith["sithTitle"]:
                sith["sithTitle"] = "Darth"

        # Rule #11: BountyHunter.lethalEfficiency must be > 0 if notorietyLevel is not novice
        if hasattr(self, 'bounty_hunters'):
            for hunter_id, hunter in self.bounty_hunters.items():
                if hunter["notorietyLevel"] != "novice" and hunter["lethalEfficiency"] <= 0:
                    hunter["lethalEfficiency"] = random.uniform(0.1, 1.0)

        # Rule #15: Mission.successRate <= 100.0
        if hasattr(self, 'missions'):
            for mission_id, mission in self.missions.items():
                if "successRate" in mission and mission["successRate"] > 100.0:
                    mission["successRate"] = 100.0


def generate_sample_data():
    """Generate and return a sample Star Wars dataset"""
    generator = StarWarsDataGenerator(seed=42)  # Use seed for reproducibility
    dataset = generator.generate_dataset(
        num_characters=10,
        num_battles=3,
        num_events=5,
        include_vader_luke=True
    )
    return dataset


def serialize_to_json(dataset, filename="./data/star_wars_data.json"):
    """Serialize the dataset to JSON file"""
    # Convert any datetime objects to strings
    def json_serial(obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    with open(filename, 'w') as f:
        json.dump(dataset, f, default=json_serial, indent=2)

    print(f"Dataset saved to {filename}")


def generate_family_tree_example():
    """Generate and display Skywalker family connections as example"""
    generator = StarWarsDataGenerator()

    # Create Anakin/Vader
    anakin = {
        "characterID": generator.generate_id("char_"),
        "name": "Anakin Skywalker / Darth Vader",
        "species": "Human",
        "gender": "Male",
        "affiliation": "Galactic Empire",
        "rank": "Supreme Commander",
        "forceSensitive": True,
        "starSign": "Unknown",
        "cameoAppearance": False
    }

    # Create Padme
    padme = {
        "characterID": generator.generate_id("char_"),
        "name": "Padmé Amidala",
        "species": "Human",
        "gender": "Female",
        "affiliation": "Republic",
        "rank": "Senator",
        "forceSensitive": False,
        "starSign": "Unknown",
        "cameoAppearance": False
    }

    # Create Luke
    luke = {
        "characterID": generator.generate_id("char_"),
        "name": "Luke Skywalker",
        "species": "Human",
        "gender": "Male",
        "affiliation": "Rebel Alliance",
        "rank": "Commander",
        "forceSensitive": True,
        "starSign": "Unknown",
        "cameoAppearance": False
    }

    # Create Leia
    leia = {
        "characterID": generator.generate_id("char_"),
        "name": "Leia Organa",
        "species": "Human",
        "gender": "Female",
        "affiliation": "Rebel Alliance",
        "rank": "Princess",
        "forceSensitive": True,
        "starSign": "Unknown",
        "cameoAppearance": False
    }

    # Create family relationships
    relationships = [
        {
            "relationshipType": "biologicalParentOf",
            "parent": anakin["characterID"],
            "child": luke["characterID"]
        },
        {
            "relationshipType": "biologicalParentOf",
            "parent": anakin["characterID"],
            "child": leia["characterID"]
        },
        {
            "relationshipType": "biologicalParentOf",
            "parent": padme["characterID"],
            "child": luke["characterID"]
        },
        {
            "relationshipType": "biologicalParentOf",
            "parent": padme["characterID"],
            "child": leia["characterID"]
        }
    ]

    # Create the "I am your father" event
    vader_revelation = {
        "eventID": generator.generate_id("event_"),
        "description": "Darth Vader reveals to Luke Skywalker that he is his father",
        "timestamp": "3-ABY",
        "significanceLevel": "High",
        "location": "Cloud City, Bespin",
        "participants": [anakin["characterID"], luke["characterID"]],
        "quote": "No, I am your father."
    }

    result = {
        "characters": [anakin, padme, luke, leia],
        "relationships": relationships,
        "events": [vader_revelation]
    }

    return result


if __name__ == "__main__":
    # Generate and save a sample dataset
    dataset = generate_sample_data()
    serialize_to_json(dataset)

    # Generate the family tree example
    family_tree = generate_family_tree_example()
    serialize_to_json(family_tree, "./data/skywalker_family.json")

    # Print the famous revelation event
    print("\nThe famous revelation:")
    vader_luke_data = StarWarsDataGenerator().generate_vader_luke_revelation()
    print(f"Event: {vader_luke_data['event']['description']}")
    print(f"Quote: {vader_luke_data['event']['quote']}")
    print(
        f"Relationship: {vader_luke_data['vader']['name']} is the biological parent of {vader_luke_data['luke']['name']}")
