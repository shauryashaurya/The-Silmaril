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
                        "Ewok", "Hutt", "Gungan", "Zabrak", "Trandoshan",
                        "Ithorian", "Sullustan", "Bothan", "Quarren", "Gamorrean",
                        "Jawa", "Tusken Raider", "Bith", "Aqualish", "Geonosian"]

        # Star systems
        self.system_names = ["Tatoo", "Alderaan", "Hoth", "Dagobah", "Bespin",
                             "Endor", "Yavin", "Corellia", "Kashyyyk", "Naboo",
                             "Kessel", "Dantooine", "Ord Mantell", "Sullust", "Mon Calamari",
                             "Bothawui", "Cato Neimoidia", "Utapau", "Mygeeto", "Felucia"]

        # Planet climate types
        self.climates = ["Desert", "Temperate", "Frozen", "Tropical", "Gaseous",
                         "Volcanic", "Forest", "Swamp", "Ocean", "Mountainous",
                         "Arctic", "Jungle", "Barren", "Urban", "Polluted",
                         "Asteroid", "Subterranean", "Savanna", "Toxic", "Artificial"]

        # Faction names
        self.faction_names = ["Rebel Alliance", "Galactic Empire", "Hutt Cartel",
                              "Bounty Hunters Guild", "Mandalorians", "Trade Federation",
                              "Rogue Squadron", "Imperial Remnant", "Black Sun", "Crimson Dawn",
                              "Death Watch", "Corporate Sector Authority", "Banking Clan"]

        # Faction ideologies
        self.ideologies = ["Democracy", "Authoritarian Control", "Criminal Enterprise",
                           "Profit Seeking", "Warrior Culture", "Sith Doctrine",
                           "Jedi Order", "Freedom Fighting", "Mercenary", "Pacifism",
                           "Isolationist", "Traditionalist", "Technological Superiority"]

        # Force abilities
        self.force_ability_names = ["Force Push", "Force Lightning", "Mind Trick",
                                    "Force Choke", "Force Jump", "Battle Meditation",
                                    "Force Healing", "Force Vision", "Force Speed",
                                    "Force Shield", "Force Telepathy", "Force Valor",
                                    "Force Enlightenment", "Force Rage", "Force Fear",
                                    "Force Drain", "Force Projection", "Force Ghost",
                                    "Force Concealment", "Force Bond"]

        # Force ability types
        self.force_ability_types = ["Offensive", "Defensive", "Control", "Sense", "Alter",
                                    "Light Side", "Dark Side", "Universal", "Telepathic", "Physical"]

        # Lightsaber colors
        self.lightsaber_colors = ["Blue", "Green", "Red", "Purple", "Yellow", "White",
                                  "Orange", "Bronze", "Silver", "Black", "Cyan"]

        # Lightsaber hilt designs
        self.hilt_designs = ["Standard", "Curved", "Double-bladed", "Cross-guard", "Custom",
                             "Dual-phase", "Lightwhip", "Shoto", "Pike", "Training"]

        # Weapon types
        self.weapon_types = ["Blaster", "Rifle", "Cannon", "Thermal Detonator", "Vibroblade",
                             "Bowcaster", "Ion Cannon", "Flamethrower", "Disruptor",
                             "E-web Heavy Repeating Blaster", "Proton Torpedo", "Concussion Missile",
                             "Ion Torpedo", "Wrist Rocket", "Shock Staff", "EMP Grenade",
                             "DL-44 Blaster Pistol", "E-11 Blaster Rifle", "A280 Blaster Rifle"]

        # Battle names template
        self.battle_templates = [
            "Battle of {planet}",
            "Assault on {planet}",
            "Siege of {planet}",
            "Skirmish at {planet}",
            "{planet} Offensive",
            "Raid on {planet}",
            "Defense of {planet}",
            "Liberation of {planet}",
            "Ambush at {planet}",
            "Evacuation of {planet}"
        ]

        # Droid models
        self.droid_models = ["R2 Series", "C-3PO Protocol", "B1 Battle", "IG Assassin",
                             "R5 Astromech", "2-1B Medical", "GNK Power", "EV-9D9 Supervisor",
                             "MSE Mouse", "ASP Labor", "FX Medical", "IT-O Interrogator",
                             "KX Security", "LOM Protocol", "EG-6 Power", "BD Exploration"]

        # Droid functions
        self.droid_functions = ["Astromech", "Protocol", "Battle", "Assassin",
                                "Medical", "Power", "Mining", "Interrogation",
                                "Maintenance", "Security", "Translator", "Analysis",
                                "Tactical", "Navigation", "Entertainment", "Espionage"]

        # Ship models
        self.ship_models = ["X-Wing", "TIE Fighter", "Star Destroyer", "Millennium Falcon",
                            "Y-Wing", "A-Wing", "Lambda Shuttle", "Nebulon-B Frigate",
                            "B-Wing", "TIE Interceptor", "TIE Bomber", "TIE Advanced",
                            "Mon Calamari Cruiser", "Corellian Corvette", "GR-75 Transport",
                            "Imperial Shuttle", "Super Star Destroyer", "Slave I", "Tantive IV"]

        # Ship classes
        self.ship_classes = ["Starfighter", "Freighter", "Cruiser", "Destroyer",
                             "Shuttle", "Transport", "Capital Ship", "Corvette",
                             "Carrier", "Dreadnought", "Gunship", "Bomber",
                             "Interceptor", "Scout", "Patrol Craft", "Assault Ship"]

        # Canon character names (expanded to include more characters from the original trilogy)
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
                "affiliation": "Hutt Cartel", "forceSensitive": False},
            {"name": "Yoda", "species": "Unknown", "gender": "Male",
                "affiliation": "Jedi Order", "forceSensitive": True},
            {"name": "Admiral Ackbar", "species": "Mon Calamari", "gender": "Male",
                "affiliation": "Rebel Alliance", "forceSensitive": False},
            {"name": "Mon Mothma", "species": "Human", "gender": "Female",
                "affiliation": "Rebel Alliance", "forceSensitive": False},
            {"name": "Wedge Antilles", "species": "Human", "gender": "Male",
                "affiliation": "Rebel Alliance", "forceSensitive": False},
            {"name": "Grand Moff Tarkin", "species": "Human", "gender": "Male",
                "affiliation": "Galactic Empire", "forceSensitive": False},
            {"name": "Admiral Piett", "species": "Human", "gender": "Male",
                "affiliation": "Galactic Empire", "forceSensitive": False},
            {"name": "General Veers", "species": "Human", "gender": "Male",
                "affiliation": "Galactic Empire", "forceSensitive": False},
            {"name": "Greedo", "species": "Rodian", "gender": "Male",
                "affiliation": "Bounty Hunters Guild", "forceSensitive": False},
            {"name": "Lobot", "species": "Human", "gender": "Male",
                "affiliation": "Cloud City", "forceSensitive": False},
            {"name": "Wicket W. Warrick", "species": "Ewok", "gender": "Male",
                "affiliation": "Ewok Tribe", "forceSensitive": False},
            {"name": "Nien Nunb", "species": "Sullustan", "gender": "Male",
                "affiliation": "Rebel Alliance", "forceSensitive": False},
            {"name": "Admiral Ozzel", "species": "Human", "gender": "Male",
                "affiliation": "Galactic Empire", "forceSensitive": False}
        ]

        # Canon planets (expanded list from the original trilogy)
        self.canon_planets = [
            {"name": "Tatooine", "climate": "Desert", "system": "Tatoo"},
            {"name": "Hoth", "climate": "Frozen", "system": "Hoth"},
            {"name": "Endor", "climate": "Forest", "system": "Endor"},
            {"name": "Dagobah", "climate": "Swamp", "system": "Dagobah"},
            {"name": "Bespin", "climate": "Gaseous", "system": "Bespin"},
            {"name": "Yavin 4", "climate": "Jungle", "system": "Yavin"},
            {"name": "Alderaan", "climate": "Temperate", "system": "Alderaan"},
            {"name": "Death Star", "climate": "Artificial", "system": "Mobile"},
            {"name": "Sullust", "climate": "Volcanic", "system": "Sullust"},
            {"name": "Cloud City", "climate": "Gaseous", "system": "Bespin"},
            {"name": "Mos Eisley", "climate": "Desert", "system": "Tatoo"},
            {"name": "Jabba's Palace", "climate": "Desert", "system": "Tatoo"},
            {"name": "Death Star II", "climate": "Artificial", "system": "Endor"},
            {"name": "Kessel", "climate": "Barren", "system": "Kessel"},
            {"name": "Coruscant", "climate": "Urban", "system": "Coruscant"}
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
                "class": "Space Station"},
            {"name": "Tantive IV", "model": "CR90 Corvette", "class": "Corvette"},
            {"name": "TIE Advanced x1", "model": "TIE Advanced", "class": "Starfighter"},
            {"name": "Home One", "model": "MC80 Star Cruiser", "class": "Cruiser"},
            {"name": "Imperial Star Destroyer",
                "model": "Imperial-class", "class": "Star Destroyer"},
            {"name": "Nebulon-B Frigate", "model": "EF76", "class": "Frigate"},
            {"name": "Death Star II", "model": "DS-2 Battle Station",
                "class": "Space Station"},
            {"name": "Lambda-class Shuttle", "model": "Lambda", "class": "Shuttle"},
            {"name": "TIE Bomber", "model": "TIE/sa", "class": "Bomber"},
            {"name": "TIE Interceptor", "model": "TIE/in", "class": "Interceptor"},
            {"name": "GR-75 Medium Transport",
                "model": "GR-75", "class": "Transport"}
        ]

        # Key events from the original trilogy
        self.canon_events = [
            # Episode IV: A New Hope
            {"description": "Princess Leia hides Death Star plans in R2-D2",
                "timestamp": "0 BBY", "significanceLevel": "High"},
            {"description": "R2-D2 and C-3PO crash land on Tatooine",
                "timestamp": "0 BBY", "significanceLevel": "Medium"},
            {"description": "Luke Skywalker discovers Obi-Wan Kenobi's message",
                "timestamp": "0 BBY", "significanceLevel": "High"},
            {"description": "Obi-Wan begins training Luke in the ways of the Force",
                "timestamp": "0 BBY", "significanceLevel": "High"},
            {"description": "The Empire destroys Alderaan",
                "timestamp": "0 BBY", "significanceLevel": "High"},
            {"description": "Obi-Wan Kenobi is killed by Darth Vader",
                "timestamp": "0 BBY", "significanceLevel": "High"},
            {"description": "Luke destroys the Death Star",
                "timestamp": "0 BBY", "significanceLevel": "High"},

            # Episode V: The Empire Strikes Back
            {"description": "The Empire attacks Rebel base on Hoth",
                "timestamp": "3 ABY", "significanceLevel": "High"},
            {"description": "Luke begins training with Yoda on Dagobah",
                "timestamp": "3 ABY", "significanceLevel": "High"},
            {"description": "Han Solo is frozen in carbonite",
                "timestamp": "3 ABY", "significanceLevel": "High"},
            {"description": "Darth Vader reveals he is Luke's father",
                "timestamp": "3 ABY", "significanceLevel": "High"},
            {"description": "Luke loses his hand in a duel with Vader",
                "timestamp": "3 ABY", "significanceLevel": "High"},
            {"description": "Lando Calrissian joins the Rebel Alliance",
                "timestamp": "3 ABY", "significanceLevel": "Medium"},

            # Episode VI: Return of the Jedi
            {"description": "Rescue of Han Solo from Jabba's Palace",
                "timestamp": "4 ABY", "significanceLevel": "High"},
            {"description": "Yoda dies and confirms Vader is Luke's father",
                "timestamp": "4 ABY", "significanceLevel": "High"},
            {"description": "Luke learns Leia is his twin sister",
                "timestamp": "4 ABY", "significanceLevel": "High"},
            {"description": "Battle of Endor begins",
                "timestamp": "4 ABY", "significanceLevel": "High"},
            {"description": "Luke confronts Emperor Palpatine and Darth Vader",
                "timestamp": "4 ABY", "significanceLevel": "High"},
            {"description": "Darth Vader turns against the Emperor and saves Luke",
                "timestamp": "4 ABY", "significanceLevel": "High"},
            {"description": "Darth Vader dies after returning to the light side",
                "timestamp": "4 ABY", "significanceLevel": "High"},
            {"description": "Rebels destroy the second Death Star",
                "timestamp": "4 ABY", "significanceLevel": "High"},
            {"description": "Celebration of the fall of the Empire",
                "timestamp": "4 ABY", "significanceLevel": "High"}
        ]

        # Key battles from the original trilogy
        self.canon_battles = [
            {"name": "Battle of Yavin",
                "outcome": "Rebel Alliance Victory", "casualties": 2000},
            {"name": "Battle of Hoth", "outcome": "Empire Victory", "casualties": 1500},
            {"name": "Duel on Cloud City",
                "outcome": "Empire Victory", "casualties": 5},
            {"name": "Battle of Tatooine",
                "outcome": "Rebel Alliance Victory", "casualties": 50},
            {"name": "Battle of Endor",
                "outcome": "Rebel Alliance Victory", "casualties": 5000},
            {"name": "Space Battle over Endor",
                "outcome": "Rebel Alliance Victory", "casualties": 25000}
        ]

        # Notable artifacts from the original trilogy
        self.canon_artifacts = [
            {"name": "Anakin's Lightsaber",
                "originEra": "Clone Wars", "forceRelated": True},
            {"name": "Darth Vader's Lightsaber",
                "originEra": "Imperial Era", "forceRelated": True},
            {"name": "Emperor's Cane", "originEra": "Imperial Era", "forceRelated": True},
            {"name": "Mandalorian Armor (Boba Fett)",
             "originEra": "Pre-Empire", "forceRelated": False},
            {"name": "Death Star Plans",
                "originEra": "Imperial Era", "forceRelated": False},
            {"name": "Holocron of Jedi Knowledge",
                "originEra": "Republic Era", "forceRelated": True}
        ]

        # Key vehicles from the original trilogy
        self.canon_vehicles = [
            {"type": "AT-AT Walker", "speed": 60.0, "terrainType": "Ground"},
            {"type": "AT-ST Walker", "speed": 90.0, "terrainType": "Ground"},
            {"type": "Speeder Bike", "speed": 500.0, "terrainType": "Ground"},
            {"type": "T-47 Airspeeder (Snowspeeder)",
             "speed": 650.0, "terrainType": "Air"},
            {"type": "Sand Crawler", "speed": 30.0, "terrainType": "Desert"},
            {"type": "Jabba's Sail Barge", "speed": 100.0, "terrainType": "Desert"},
            {"type": "Imperial Shuttle", "speed": 850.0, "terrainType": "Air/Space"}
        ]

        # Key technology from the original trilogy
        self.canon_technologies = [
            {"techType": "Lightsaber", "inventor": "Ancient Jedi",
                "functionDescription": "Energy blade weapon"},
            {"techType": "Blaster", "inventor": "Unknown",
                "functionDescription": "Energy projectile weapon"},
            {"techType": "Hyperdrive", "inventor": "Unknown",
                "functionDescription": "Faster-than-light travel"},
            {"techType": "Deflector Shield", "inventor": "Unknown",
                "functionDescription": "Energy barrier protection"},
            {"techType": "Superlaser", "inventor": "Imperial Engineers",
                "functionDescription": "Planet-destroying weapon"},
            {"techType": "Tractor Beam", "inventor": "Unknown",
                "functionDescription": "Gravitational capture beam"},
            {"techType": "Carbonite Freezing", "inventor": "Unknown",
                "functionDescription": "Preservation technology"}
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

    def generate_battle(self, use_canon=True) -> Dict[str, Any]:
        """Generate a battle, optionally using canon battles"""
        battle_id = self.generate_id("battle_")

        # 70% chance to use canon battle
        if use_canon and hasattr(self, 'canon_battles') and random.random() < 0.7:
            template = random.choice(self.canon_battles)

            # Generate random date between 0 BBY and 4 ABY (Episode 4-6 timeframe)
            year = random.randint(-1, 4)  # -1 is 1 BBY, 0 is 0 ABY, etc.
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            battle_date = datetime.datetime(
                year + 1977, month, day)  # Using 1977 as "0 ABY" base

            battle = {
                "battleID": battle_id,
                "name": template["name"],
                "outcome": template["outcome"],
                "battleDate": battle_date.strftime("%Y-%m-%d"),
                "casualties": template["casualties"],
                "factions": []  # To be populated with factions
            }
        else:
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

    def generate_event(self, use_canon=True) -> Dict[str, Any]:
        """Generate a Star Wars event, optionally using canon events"""
        event_id = self.generate_id("event_")

        # 70% chance to use canon event
        if use_canon and hasattr(self, 'canon_events') and random.random() < 0.7:
            template = random.choice(self.canon_events)

            event = {
                "eventID": event_id,
                "description": template["description"],
                "timestamp": template["timestamp"],
                "significanceLevel": template["significanceLevel"]
            }
        else:
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
                "{character} escapes from {character2} using the {ship}",
                "A bounty is placed on {character} by {faction}",
                "{character} is promoted to {rank} within {faction}",
                "{character} is captured by {faction} forces",
                "A spy within {faction} is discovered by {character}",
                "{character} receives a message from {character2}",
                "The plans for {item} are stolen by {character}",
                "A diplomatic mission to {planet} is led by {character}",
                "{character} repairs {ship} after damage in {battle}",
                "{character} trains {character2} in combat techniques",
                "A deal between {character} and {character2} goes wrong",
                "{faction} prepares an assault on {faction2} territory",
                "The construction of {item} is completed"
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
                ship="[Ship]",
                battle="[Battle]",
                rank="[Rank]"
            )

            event = {
                "eventID": event_id,
                "description": description,
                "timestamp": timestamp.strftime("%Y-%m-%d"),
                "significanceLevel": random.choice(["Low", "Medium", "High", "Galactic"])
            }

        self.events[event_id] = event
        return event

    def generate_force_ability(self, light_side=None) -> Dict[str, Any]:
        """Generate a Force ability, optionally specifying light/dark side"""
        ability_id = self.generate_id("ability_")

        # Determine if this is a light or dark side ability
        if light_side is None:
            # Random selection if not specified
            is_light = random.random() < 0.5
        else:
            is_light = light_side

        # Select ability name and type based on light/dark side
        if is_light:
            # Light side abilities tend to be defensive or healing
            ability_names = [name for name in self.force_ability_names if name not in [
                "Force Lightning", "Force Choke", "Force Rage", "Force Fear", "Force Drain"]]
            ability_types = [type for type in self.force_ability_types if type in [
                "Defensive", "Control", "Light Side", "Universal"]]
        else:
            # Dark side abilities tend to be offensive
            ability_names = [name for name in self.force_ability_names if name not in [
                "Force Healing", "Force Enlightenment", "Battle Meditation"]]
            ability_types = [type for type in self.force_ability_types if type in [
                "Offensive", "Alter", "Dark Side", "Universal"]]

        ability = {
            "abilityID": ability_id,
            "name": random.choice(ability_names),
            "type": random.choice(ability_types),
            "difficultyLevel": random.randint(1, 10),
            "isLightSide": is_light,
            "isDarkSide": not is_light
        }

        self.force_abilities[ability_id] = ability
        return ability

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

    def generate_artifact(self, use_canon=True) -> Dict[str, Any]:
        """Generate an artifact, optionally using canon artifacts"""
        artifact_id = self.generate_id("artifact_")

        if use_canon and hasattr(self, 'canon_artifacts') and random.random() < 0.7:
            template = random.choice(self.canon_artifacts)

            artifact = {
                "artifactID": artifact_id,
                "name": template["name"],
                "originEra": template["originEra"],
                "forceRelated": template["forceRelated"]
            }
        else:
            artifact_templates = [
                "Ancient {adj} Holocron",
                "Lost Lightsaber of {character}",
                "The {adj} Crystal of {planet}",
                "Legendary {adj} Armor",
                "{faction} Battle Plans",
                "Stolen {faction} Codes",
                "The {adj} Mask",
                "Force-sensitive {item}"
            ]

            adjectives = ["Ancient", "Mysterious", "Powerful",
                          "Sacred", "Dark", "Light", "Forbidden", "Lost"]
            items = ["Crystal", "Amulet", "Scroll", "Datacron",
                     "Device", "Relic", "Talisman", "Weapon"]

            template = random.choice(artifact_templates)
            name = template.format(
                adj=random.choice(adjectives),
                character="[Character]",
                planet="[Planet]",
                faction="[Faction]",
                item=random.choice(items)
            )

            eras = ["Old Republic", "Clone Wars",
                    "Republic Era", "Imperial Era", "Unknown"]

            artifact = {
                "artifactID": artifact_id,
                "name": name,
                "originEra": random.choice(eras),
                "forceRelated": random.random() < 0.6  # 60% chance of being Force-related
            }

        if not hasattr(self, 'artifacts'):
            self.artifacts = {}

        self.artifacts[artifact_id] = artifact
        return artifact

    def generate_technology(self, use_canon=True) -> Dict[str, Any]:
        """Generate a technology, optionally using canon technologies"""
        tech_id = self.generate_id("tech_")

        if use_canon and hasattr(self, 'canon_technologies') and random.random() < 0.7:
            template = random.choice(self.canon_technologies)

            technology = {
                "technologyID": tech_id,
                "techType": template["techType"],
                "inventor": template["inventor"],
                "functionDescription": template["functionDescription"]
            }
        else:
            tech_types = ["Weapon", "Shield", "Communication",
                          "Transportation", "Medical", "Surveillance", "Tactical"]
            inventors = ["Imperial Engineers", "Rebel Technicians",
                         "Unknown", "Ancient Civilization", "Republic Scientists"]
            functions = [
                "Energy projection system",
                "Defensive barrier technology",
                "Long-range communication",
                "Rapid transport mechanism",
                "Advanced healing device",
                "Force energy manipulation",
                "Sentient life support",
                "Sublight propulsion",
                "Hyperspace navigation"
            ]

            technology = {
                "technologyID": tech_id,
                "techType": random.choice(tech_types),
                "inventor": random.choice(inventors),
                "functionDescription": random.choice(functions)
            }

        if not hasattr(self, 'technologies'):
            self.technologies = {}

        self.technologies[tech_id] = technology
        return technology

    def generate_vehicle(self, use_canon=True) -> Dict[str, Any]:
        """Generate a vehicle, optionally using canon vehicles"""
        vehicle_id = self.generate_id("vehicle_")

        if use_canon and hasattr(self, 'canon_vehicles') and random.random() < 0.7:
            template = random.choice(self.canon_vehicles)

            vehicle = {
                "vehicleID": vehicle_id,
                "type": template["type"],
                "speed": template["speed"],
                "terrainType": template["terrainType"]
            }
        else:
            vehicle_types = [
                "Walker", "Speeder", "Crawler", "Repulsor Tank", "Troop Transport",
                "Hover Craft", "Submersible", "Jetpack", "Landspeeder", "Sandcrawler"
            ]

            terrain_types = ["Ground", "Air", "Water",
                             "Multi-terrain", "Desert", "Snow", "Urban", "Forest"]

            vehicle = {
                "vehicleID": vehicle_id,
                "type": random.choice(vehicle_types),
                "speed": random.uniform(30.0, 700.0),
                "terrainType": random.choice(terrain_types)
            }

        if not hasattr(self, 'vehicles'):
            self.vehicles = {}

        self.vehicles[vehicle_id] = vehicle
        return vehicle

    def generate_creature(self) -> Dict[str, Any]:
        """Generate a Star Wars creature"""
        creature_id = self.generate_id("creature_")

        creature_names = [
            "Rancor", "Wampa", "Sarlacc", "Bantha", "Tauntaun", "Dewback",
            "Wookiee", "Ewok", "Mynock", "Space Slug", "Krayt Dragon",
            "Dianoga", "Acklay", "Nexu", "Reek", "Varactyl", "Opee Sea Killer"
        ]

        habitats = [
            "Desert", "Ice", "Forest", "Swamp", "Mountain", "Ocean",
            "Jungle", "Urban", "Space", "Underground", "Volcanic"
        ]

        creature = {
            "creatureID": creature_id,
            "speciesName": random.choice(creature_names),
            "habitat": random.choice(habitats),
            "dangerLevel": random.uniform(0.1, 10.0)
        }

        if not hasattr(self, 'creatures'):
            self.creatures = {}

        self.creatures[creature_id] = creature
        return creature

    def generate_mission(self) -> Dict[str, Any]:
        """Generate a Star Wars mission"""
        mission_id = self.generate_id("mission_")

        mission_types = [
            "Rescue", "Infiltration", "Reconnaissance", "Assault", "Retrieval",
            "Escort", "Sabotage", "Diplomatic", "Bounty", "Extraction"
        ]

        mission_goals = [
            "Free captured allies",
            "Obtain enemy intel",
            "Destroy enemy installation",
            "Recover valuable artifact",
            "Establish alliance with local faction",
            "Eliminate high-value target",
            "Secure new base location",
            "Test experimental technology",
            "Provide humanitarian aid",
            "Capture enemy leader"
        ]

        # Rule #15: Mission.successRate <= 100.0
        success_rate = min(100.0, random.uniform(10.0, 105.0))

        mission = {
            "missionID": mission_id,
            "missionType": random.choice(mission_types),
            "missionGoal": random.choice(mission_goals),
            "successRate": success_rate
        }

        if not hasattr(self, 'missions'):
            self.missions = {}

        self.missions[mission_id] = mission
        return mission

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

    def _find_or_create_character(self, name: str) -> Dict[str, Any]:
        """Find a character by name or create it if it doesn't exist"""
        for char_id, char in self.characters.items():
            if char["name"] == name:
                return char

        # If character not found, create it
        for canon_char in self.canon_characters:
            if canon_char["name"] == name:
                char = {
                    "characterID": self.generate_id("char_"),
                    **canon_char
                }
                self.characters[char["characterID"]] = char
                return char

        # If not in canon list, create generic
        char = {
            "characterID": self.generate_id("char_"),
            "name": name,
            "species": "Human",
            "gender": "Unknown",
            "affiliation": "Unknown",
            "rank": "Unknown",
            "forceSensitive": False,
            "starSign": "Unknown",
            "cameoAppearance": False
        }
        self.characters[char["characterID"]] = char
        return char

    def _find_or_create_droid(self, name: str) -> Dict[str, Any]:
        """Find a droid by name or create it if it doesn't exist"""
        if not hasattr(self, 'droids'):
            self.droids = {}

        for droid_id, droid in self.droids.items():
            if droid["name"] == name:
                return droid

        # If not found, create it
        droid = {
            "characterID": self.generate_id("droid_"),
            "name": name,
            "species": "Droid",
            "gender": "Programming",
            "affiliation": "Rebel Alliance",
            "rank": "Technical Unit",
            "forceSensitive": False,
            "starSign": "None",
            "cameoAppearance": False,
            "modelNumber": "Unknown",
            "primaryFunction": "Unknown",
            "owner": "",
            "memoryWipes": 0
        }

        self.droids[droid["characterID"]] = droid
        return droid

    def _find_or_create_planet(self, name: str, climate=None, system=None) -> Dict[str, Any]:
        """Find a planet by name or create it if it doesn't exist"""
        for planet_id, planet in self.planets.items():
            if planet["planetName"] == name:
                return planet

        # If planet not found, create it
        for canon_planet in self.canon_planets:
            if canon_planet["name"] == name:
                planet = {
                    "planetID": self.generate_id("planet_"),
                    "planetName": canon_planet["name"],
                    "starSystem": canon_planet["system"],
                    "climate": canon_planet["climate"],
                    "population": random.randint(1000000, 20000000000),
                    "affiliation": random.choice(self.faction_names),
                    "orbitalPeriodDays": random.uniform(200, 999) if name != "Tatooine" else random.uniform(800, 1200)
                }
                self.planets[planet["planetID"]] = planet
                return planet

        # If not in canon list, create generic
        planet = {
            "planetID": self.generate_id("planet_"),
            "planetName": name,
            "starSystem": system or "Unknown",
            "climate": climate or random.choice(self.climates),
            "population": random.randint(1000000, 20000000000),
            "affiliation": random.choice(self.faction_names),
            "orbitalPeriodDays": random.uniform(200, 999) if name != "Tatooine" else random.uniform(800, 1200)
        }
        self.planets[planet["planetID"]] = planet
        return planet

    def _find_or_create_ship(self, name: str) -> Dict[str, Any]:
        """Find a ship by name or create it if it doesn't exist"""
        for ship_id, ship in self.spaceships.items():
            if ship["uniqueName"] == name:
                return ship

        # If ship not found, create it
        for canon_ship in self.canon_ships:
            if canon_ship["name"] == name:
                ship = {
                    "shipID": self.generate_id("ship_"),
                    "model": canon_ship["model"],
                    "shipClass": canon_ship["class"],
                    "speedRating": random.uniform(0.5, 2.0),
                    "hyperdriveEquipped": True,
                    "uniqueName": canon_ship["name"]
                }
                self.spaceships[ship["shipID"]] = ship
                return ship

        # If not in canon list, create generic
        ship = {
            "shipID": self.generate_id("ship_"),
            "model": "Unknown",
            "shipClass": random.choice(self.ship_classes),
            "speedRating": random.uniform(0.5, 2.0),
            "hyperdriveEquipped": True,
            "uniqueName": name
        }
        self.spaceships[ship["shipID"]] = ship
        return ship

    def _create_event(self, description, timestamp, significance, participants=None, location=None, battle=None, quote=None, ship=None) -> Dict[str, Any]:
        """Create an event with the given parameters"""
        event_id = self.generate_id("event_")

        event = {
            "eventID": event_id,
            "description": description,
            "timestamp": timestamp,
            "significanceLevel": significance
        }

        if participants:
            event["participants"] = participants

        if location:
            event["location"] = location

        if battle:
            event["battle"] = battle

        if quote:
            event["quote"] = quote

        if ship:
            event["ship"] = ship

        self.events[event_id] = event
        return event

    def _create_battle(self, name, outcome, casualties) -> Dict[str, Any]:
        """Create a battle with the given parameters"""
        battle_id = self.generate_id("battle_")

        # Generate random date between 0 BBY and 4 ABY (Episode 4-6 timeframe)
        year = random.randint(-1, 4)  # -1 is 1 BBY, 0 is 0 ABY, etc.
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        battle_date = datetime.datetime(
            year + 1977, month, day)  # Using 1977 as "0 ABY" base

        battle = {
            "battleID": battle_id,
            "name": name,
            "outcome": outcome,
            "battleDate": battle_date.strftime("%Y-%m-%d"),
            "casualties": casualties,
            "factions": []
        }

        self.battles[battle_id] = battle
        return battle

    def generate_episode_4_timeline(self) -> List[Dict[str, Any]]:
        """Generate a timeline of key events from Episode 4: A New Hope"""
        timeline = []

        # Key characters
        leia = self._find_or_create_character("Leia Organa")
        luke = self._find_or_create_character("Luke Skywalker")
        vader = self._find_or_create_character("Darth Vader")
        obi_wan = self._find_or_create_character("Obi-Wan Kenobi")
        r2d2 = self._find_or_create_droid("R2-D2")
        c3po = self._find_or_create_droid("C-3PO")
        han = self._find_or_create_character("Han Solo")
        tarkin = self._find_or_create_character("Grand Moff Tarkin")

        # Key locations
        tatooine = self._find_or_create_planet("Tatooine")
        death_star = self._find_or_create_planet(
            "Death Star", "Artificial", "Mobile")
        yavin = self._find_or_create_planet("Yavin 4")
        alderaan = self._find_or_create_planet("Alderaan")

        # Key ships
        falcon = self._find_or_create_ship("Millennium Falcon")
        tantive = self._find_or_create_ship("Tantive IV")
        x_wing = self._find_or_create_ship("X-Wing Red Five")

        # Timeline events
        timeline.append(self._create_event(
            "Princess Leia hides Death Star plans in R2-D2",
            "0 BBY",
            "High",
            participants=[leia["characterID"], r2d2["characterID"]],
            location=tantive["shipID"]
        ))

        timeline.append(self._create_event(
            "R2-D2 and C-3PO escape to Tatooine",
            "0 BBY",
            "Medium",
            participants=[r2d2["characterID"], c3po["characterID"]],
            location=tatooine["planetID"]
        ))

        timeline.append(self._create_event(
            "Luke Skywalker discovers Obi-Wan Kenobi's message",
            "0 BBY",
            "High",
            participants=[luke["characterID"],
                          obi_wan["characterID"], r2d2["characterID"]],
            location=tatooine["planetID"]
        ))

        timeline.append(self._create_event(
            "The Empire destroys Alderaan",
            "0 BBY",
            "High",
            participants=[vader["characterID"],
                          tarkin["characterID"], leia["characterID"]],
            location=alderaan["planetID"]
        ))

        timeline.append(self._create_event(
            "Obi-Wan Kenobi is killed by Darth Vader",
            "0 BBY",
            "High",
            participants=[obi_wan["characterID"],
                          vader["characterID"], luke["characterID"]],
            location=death_star["planetID"]
        ))

        timeline.append(self._create_event(
            "Luke destroys the Death Star",
            "0 BBY",
            "High",
            participants=[luke["characterID"], han["characterID"]],
            location=death_star["planetID"],
            battle="Battle of Yavin"
        ))

        return timeline

    def generate_episode_5_timeline(self) -> List[Dict[str, Any]]:
        """Generate a timeline of key events from Episode 5: The Empire Strikes Back"""
        timeline = []

        # Key characters
        leia = self._find_or_create_character("Leia Organa")
        luke = self._find_or_create_character("Luke Skywalker")
        vader = self._find_or_create_character("Darth Vader")
        han = self._find_or_create_character("Han Solo")
        yoda = self._find_or_create_character("Yoda")
        lando = self._find_or_create_character("Lando Calrissian")
        emperor = self._find_or_create_character("Emperor Palpatine")

        # Key locations
        hoth = self._find_or_create_planet("Hoth")
        dagobah = self._find_or_create_planet("Dagobah")
        bespin = self._find_or_create_planet("Bespin")
        cloud_city = self._find_or_create_planet(
            "Cloud City", "Gaseous", "Bespin")

        # Key ships
        falcon = self._find_or_create_ship("Millennium Falcon")
        executor = self._find_or_create_ship("Executor")

        # Timeline events
        timeline.append(self._create_event(
            "The Empire attacks Rebel base on Hoth",
            "3 ABY",
            "High",
            participants=[luke["characterID"], leia["characterID"],
                          han["characterID"], vader["characterID"]],
            location=hoth["planetID"],
            battle="Battle of Hoth"
        ))

        timeline.append(self._create_event(
            "Luke begins training with Yoda on Dagobah",
            "3 ABY",
            "High",
            participants=[luke["characterID"], yoda["characterID"]],
            location=dagobah["planetID"]
        ))

        timeline.append(self._create_event(
            "Han Solo and crew arrive in Cloud City",
            "3 ABY",
            "Medium",
            participants=[han["characterID"],
                          leia["characterID"], lando["characterID"]],
            location=cloud_city["planetID"]
        ))

        timeline.append(self._create_event(
            "Han Solo is frozen in carbonite",
            "3 ABY",
            "High",
            participants=[han["characterID"], vader["characterID"],
                          leia["characterID"], lando["characterID"]],
            location=cloud_city["planetID"]
        ))

        timeline.append(self._create_event(
            "Darth Vader reveals he is Luke's father",
            "3 ABY",
            "High",
            participants=[luke["characterID"], vader["characterID"]],
            location=cloud_city["planetID"],
            quote="No, I am your father."
        ))

        timeline.append(self._create_event(
            "Luke escapes Cloud City with Leia and Lando",
            "3 ABY",
            "Medium",
            participants=[luke["characterID"],
                          leia["characterID"], lando["characterID"]],
            location=cloud_city["planetID"],
            ship=falcon["shipID"]
        ))

        return timeline

    def generate_episode_6_timeline(self) -> List[Dict[str, Any]]:
        """Generate a timeline of key events from Episode 6: Return of the Jedi"""
        timeline = []

        # Key characters
        leia = self._find_or_create_character("Leia Organa")
        luke = self._find_or_create_character("Luke Skywalker")
        vader = self._find_or_create_character("Darth Vader")
        han = self._find_or_create_character("Han Solo")
        lando = self._find_or_create_character("Lando Calrissian")
        emperor = self._find_or_create_character("Emperor Palpatine")
        jabba = self._find_or_create_character("Jabba the Hutt")
        yoda = self._find_or_create_character("Yoda")

        # Key locations
        tatooine = self._find_or_create_planet("Tatooine")
        jabba_palace = self._find_or_create_planet(
            "Jabba's Palace", "Desert", "Tatoo")
        endor = self._find_or_create_planet("Endor")
        death_star2 = self._find_or_create_planet(
            "Death Star II", "Artificial", "Endor")
        dagobah = self._find_or_create_planet("Dagobah")

        # Key ships
        falcon = self._find_or_create_ship("Millennium Falcon")

        # Timeline events
        timeline.append(self._create_event(
            "Rescue of Han Solo from Jabba's Palace",
            "4 ABY",
            "High",
            participants=[luke["characterID"], leia["characterID"],
                          han["characterID"], jabba["characterID"]],
            location=jabba_palace["planetID"]
        ))

        timeline.append(self._create_event(
            "Yoda dies and confirms Vader is Luke's father",
            "4 ABY",
            "High",
            participants=[luke["characterID"], yoda["characterID"]],
            location=dagobah["planetID"]
        ))

        timeline.append(self._create_event(
            "Luke learns Leia is his twin sister",
            "4 ABY",
            "High",
            participants=[luke["characterID"], leia["characterID"]],
            location=endor["planetID"]
        ))

        timeline.append(self._create_event(
            "Battle of Endor begins",
            "4 ABY",
            "High",
            participants=[luke["characterID"], leia["characterID"],
                          han["characterID"], lando["characterID"]],
            location=endor["planetID"],
            battle="Battle of Endor"
        ))

        timeline.append(self._create_event(
            "Luke confronts Emperor Palpatine and Darth Vader",
            "4 ABY",
            "High",
            participants=[luke["characterID"],
                          vader["characterID"], emperor["characterID"]],
            location=death_star2["planetID"]
        ))

        timeline.append(self._create_event(
            "Darth Vader turns against the Emperor and saves Luke",
            "4 ABY",
            "High",
            participants=[luke["characterID"],
                          vader["characterID"], emperor["characterID"]],
            location=death_star2["planetID"]
        ))

        timeline.append(self._create_event(
            "Rebels destroy the second Death Star",
            "4 ABY",
            "High",
            participants=[lando["characterID"]],
            location=death_star2["planetID"],
            ship=falcon["shipID"]
        ))

        timeline.append(self._create_event(
            "Celebration of the fall of the Empire",
            "4 ABY",
            "High",
            participants=[luke["characterID"], leia["characterID"],
                          han["characterID"], lando["characterID"]],
            location=endor["planetID"]
        ))

        return timeline

    def generate_full_trilogy_dataset(self) -> Dict[str, Any]:
        """Generate a comprehensive dataset for the entire original trilogy"""
        # Initialize data structures
        self._initialize_reference_data()

        # Generate factions
        for _ in range(5):
            self.generate_faction()

        # Generate key characters (this will use canon characters)
        characters = []
        for _ in range(20):
            characters.append(self.generate_character(use_canon=True))

        # Ensure we have Jedis, Siths, and Droids
        jedis = []
        siths = []
        droids = []

        # Create specific characters if they don't exist already
        luke = self._find_or_create_character("Luke Skywalker")
        jedis.append(self.generate_jedi(luke))

        vader = self._find_or_create_character("Darth Vader")
        vader_sith = self.generate_sith(vader)
        vader_sith["darkSideLevel"] = 95
        vader_sith["sithTitle"] = "Darth"
        vader_sith["apprenticeOf"] = "Emperor Palpatine"
        siths.append(vader_sith)

        emperor = self._find_or_create_character("Emperor Palpatine")
        emperor_sith = self.generate_sith(emperor)
        emperor_sith["darkSideLevel"] = 100
        emperor_sith["sithTitle"] = "Darth"
        siths.append(emperor_sith)

        # Generate more Force users
        for i in range(3):
            if i < len(characters):
                if characters[i]["forceSensitive"] and characters[i]["name"] not in ["Luke Skywalker", "Darth Vader", "Emperor Palpatine"]:
                    if characters[i]["affiliation"] == "Rebel Alliance" or characters[i]["affiliation"] == "Jedi Order":
                        jedis.append(self.generate_jedi(characters[i]))
                    elif characters[i]["affiliation"] == "Galactic Empire":
                        siths.append(self.generate_sith(characters[i]))

        # Generate droids including C-3PO and R2-D2
        r2 = self._find_or_create_droid("R2-D2")
        c3po = self._find_or_create_droid("C-3PO")
        droids.append(r2)
        droids.append(c3po)

        for _ in range(5):
            droids.append(self.generate_droid())

        # Generate planets from the original trilogy
        planets = []
        for _ in range(10):
            planets.append(self.generate_planet(use_canon=True))

        # Generate ships
        ships = []
        for _ in range(10):
            ships.append(self.generate_spaceship(use_canon=True))

        # Generate canonical battles
        battles = []
        # Battle of Yavin
        yavin_battle = self._create_battle(
            "Battle of Yavin", "Rebel Alliance Victory", 2000)
        battles.append(yavin_battle)

        # Battle of Hoth
        hoth_battle = self._create_battle(
            "Battle of Hoth", "Empire Victory", 1500)
        battles.append(hoth_battle)

        # Battle of Endor
        endor_battle = self._create_battle(
            "Battle of Endor", "Rebel Alliance Victory", 5000)
        battles.append(endor_battle)

        # Generate more battles
        for _ in range(5):
            battles.append(self.generate_battle(use_canon=True))

        # Generate events for each episode
        ep4_timeline = self.generate_episode_4_timeline()
        ep5_timeline = self.generate_episode_5_timeline()
        ep6_timeline = self.generate_episode_6_timeline()

        # Generate Force abilities
        force_abilities = []
        # Light side abilities
        for _ in range(5):
            force_abilities.append(
                self.generate_force_ability(light_side=True))

        # Dark side abilities
        for _ in range(5):
            force_abilities.append(
                self.generate_force_ability(light_side=False))

        # Neutral abilities
        for _ in range(5):
            force_abilities.append(self.generate_force_ability())

        # Generate lightsabers
        lightsabers = []
        for _ in range(5):
            lightsabers.append(self.generate_lightsaber())

        # Generate artifacts
        artifacts = []
        for _ in range(5):
            artifacts.append(self.generate_artifact(use_canon=True))

        # Generate technologies
        technologies = []
        for _ in range(5):
            technologies.append(self.generate_technology(use_canon=True))

        # Generate vehicles
        vehicles = []
        for _ in range(5):
            vehicles.append(self.generate_vehicle(use_canon=True))

        # Generate missions
        missions = []
        for _ in range(5):
            missions.append(self.generate_mission())

        # Generate creatures
        creatures = []
        for _ in range(5):
            creatures.append(self.generate_creature())

        # Establish relationships
        relationships = []

        # Luke-Vader relationship (father-son)
        vader = self._find_or_create_character("Darth Vader")
        luke = self._find_or_create_character("Luke Skywalker")
        relationships.append({
            "relationshipType": "biologicalParentOf",
            "parent": vader["characterID"],
            "child": luke["characterID"]
        })

        # Luke-Leia relationship (twins)
        leia = self._find_or_create_character("Leia Organa")
        relationships.append({
            "relationshipType": "sibling",
            "sibling1": luke["characterID"],
            "sibling2": leia["characterID"]
        })

        # Vader-Leia relationship (father-daughter)
        relationships.append({
            "relationshipType": "biologicalParentOf",
            "parent": vader["characterID"],
            "child": leia["characterID"]
        })

        # Han-Chewbacca relationship (sidekick)
        han = self._find_or_create_character("Han Solo")
        chewie = self._find_or_create_character("Chewbacca")
        relationships.append({
            "relationshipType": "hasSidekick",
            "character": han["characterID"],
            "sidekick": chewie["characterID"]
        })

        # Droids ownership
        r2 = self._find_or_create_droid("R2-D2")
        c3po = self._find_or_create_droid("C-3PO")
        relationships.append({
            "relationshipType": "ownedBy",
            "droid": r2["characterID"],
            "owner": luke["characterID"]
        })
        relationships.append({
            "relationshipType": "ownedBy",
            "droid": c3po["characterID"],
            "owner": luke["characterID"]
        })

        # Ship piloting
        falcon = self._find_or_create_ship("Millennium Falcon")
        relationships.append({
            "relationshipType": "pilotedBy",
            "ship": falcon["shipID"],
            "pilot": han["characterID"]
        })

        # Compile the full dataset
        dataset = {
            "characters": self.characters,
            "jedis": self.jedis,
            "siths": self.siths,
            "droids": getattr(self, 'droids', {}),
            "planets": self.planets,
            "spaceships": self.spaceships,
            "factions": self.factions,
            "battles": self.battles,
            "events": self.events,
            "force_abilities": self.force_abilities,
            "lightsabers": self.lightsabers,
            "artifacts": getattr(self, 'artifacts', {}),
            "technologies": getattr(self, 'technologies', {}),
            "vehicles": getattr(self, 'vehicles', {}),
            "missions": getattr(self, 'missions', {}),
            "creatures": getattr(self, 'creatures', {}),
            "relationships": relationships,
            "timelines": {
                "episode_4": ep4_timeline,
                "episode_5": ep5_timeline,
                "episode_6": ep6_timeline
            }
        }

        return dataset

    def generate_i_am_your_father_scene(self) -> Dict[str, Any]:
        """Generate the iconic 'I am your father' scene with all relevant data"""
        # Create Vader
        vader = self._find_or_create_character("Darth Vader")
        vader_sith = self.generate_sith(vader)
        vader_sith["darkSideLevel"] = 95
        vader_sith["sithTitle"] = "Darth"
        vader_sith["apprenticeOf"] = "Emperor Palpatine"

        # Create Luke
        luke = self._find_or_create_character("Luke Skywalker")
        luke_jedi = self.generate_jedi(luke)
        luke_jedi["lightsaberColor"] = "Blue"
        luke_jedi["jediRank"] = "Padawan"

        # Create the location
        cloud_city = self._find_or_create_planet(
            "Cloud City", "Gaseous", "Bespin")

        # Create the battle
        duel = self._create_battle("Duel at Cloud City", "Empire Victory", 5)

        # Create the event
        revelation = self._create_event(
            "Darth Vader reveals he is Luke's father",
            "3 ABY",
            "High",
            participants=[vader["characterID"], luke["characterID"]],
            location=cloud_city["planetID"],
            battle=duel["battleID"],
            quote="No, I am your father."
        )

        # Create the relationship
        relationship = {
            "relationshipType": "biologicalParentOf",
            "parent": vader["characterID"],
            "child": luke["characterID"]
        }

        # Create dialogue
        dialogue = [
            {"speaker": vader["characterID"],
                "line": "Obi-Wan never told you what happened to your father."},
            {"speaker": luke["characterID"],
                "line": "He told me enough! He told me you killed him!"},
            {"speaker": vader["characterID"], "line": "No. I am your father."},
            {"speaker": luke["characterID"],
                "line": "No. No. That's not true. That's impossible!"},
            {"speaker": vader["characterID"],
                "line": "Search your feelings; you know it to be true!"},
            {"speaker": luke["characterID"], "line": "No! No!"}
        ]

        # Create Luke's lightsaber
        luke_saber = self.generate_lightsaber()
        luke_saber["color"] = "Blue"
        luke_saber["name"] = "Anakin's Lightsaber"

        # Create Vader's lightsaber
        vader_saber = self.generate_lightsaber()
        vader_saber["color"] = "Red"
        vader_saber["name"] = "Darth Vader's Lightsaber"

        # Create the scene
        scene = {
            "characters": {
                vader["characterID"]: vader,
                luke["characterID"]: luke
            },
            "siths": {
                vader["characterID"]: vader_sith
            },
            "jedis": {
                luke["characterID"]: luke_jedi
            },
            "planets": {
                cloud_city["planetID"]: cloud_city
            },
            "battles": {
                duel["battleID"]: duel
            },
            "events": {
                revelation["eventID"]: revelation
            },
            "lightsabers": {
                luke_saber["weaponID"]: luke_saber,
                vader_saber["weaponID"]: vader_saber
            },
            "relationships": [relationship],
            "dialogue": dialogue
        }

        return scene


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


def generate_full_trilogy_data():
    """Generate a comprehensive dataset covering the entire original trilogy"""
    generator = StarWarsDataGenerator(seed=42)  # Use seed for reproducibility
    dataset = generator.generate_full_trilogy_dataset()
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
        },
        {
            "relationshipType": "sibling",
            "sibling1": luke["characterID"],
            "sibling2": leia["characterID"]
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


def generate_data_dictionary():
    """
    Generate a comprehensive data dictionary that explains the structure, fields,
    abbreviations, and references to movie events in the Star Wars data.

    Returns:
        dict: A structured data dictionary
    """
    data_dictionary = {
        "overview": {
            "description": "This dataset contains information about the Star Wars original trilogy (Episodes IV-VI) including characters, locations, events, and relationships.",
            "dataVersion": "1.0",
            "moviesIncluded": [
                "Episode IV: A New Hope (1977)",
                "Episode V: The Empire Strikes Back (1980)",
                "Episode VI: Return of the Jedi (1983)"
            ],
            "abbreviations": {
                "BBY": "Before Battle of Yavin - Years before the destruction of the first Death Star in Episode IV",
                "ABY": "After Battle of Yavin - Years after the destruction of the first Death Star in Episode IV",
                "0 BBY": "The year of the Battle of Yavin (Death Star destruction) in Episode IV",
                "3 ABY": "Approximately when the events of Empire Strikes Back occur",
                "4 ABY": "Approximately when the events of Return of the Jedi occur"
            }
        },
        "entities": {
            "characters": {
                "description": "Individuals that appear in the Star Wars universe",
                "fields": {
                    "characterID": "Unique identifier for the character",
                    "name": "Character's name",
                    "species": "Character's species or race",
                    "gender": "Character's gender",
                    "affiliation": "Organization or faction the character belongs to",
                    "rank": "Character's position or title within their organization",
                    "forceSensitive": "Boolean indicating if the character can use the Force",
                    "starSign": "Fictional star sign within the Star Wars universe",
                    "cameoAppearance": "Boolean indicating if the character appears briefly"
                }
            },
            "jedis": {
                "description": "Force-sensitive characters aligned with the light side",
                "fields": {
                    "characterID": "Reference to the base character",
                    "lightsaberColor": "Color of their lightsaber (typically blue, green, or purple)",
                    "midiChlorianCount": "Fictional measure of Force potential",
                    "jediRank": "Rank within the Jedi Order (Padawan, Knight, Master, etc.)"
                }
            },
            "siths": {
                "description": "Force-sensitive characters aligned with the dark side",
                "fields": {
                    "characterID": "Reference to the base character",
                    "darkSideLevel": "Measure of dark side corruption (0-100)",
                    "apprenticeOf": "Their Sith master (if applicable)",
                    "sithTitle": "Sith title (typically 'Darth')"
                }
            },
            "droids": {
                "description": "Robotic characters",
                "fields": {
                    "characterID": "Reference to the base character",
                    "modelNumber": "Droid model or series designation",
                    "primaryFunction": "Main purpose the droid was built for",
                    "owner": "Character who owns or is associated with the droid",
                    "memoryWipes": "Number of times the droid's memory has been reset"
                }
            },
            "planets": {
                "description": "Celestial bodies that serve as locations",
                "fields": {
                    "planetID": "Unique identifier for the planet",
                    "planetName": "Name of the planet",
                    "starSystem": "Star system the planet belongs to",
                    "climate": "Predominant climate type",
                    "population": "Approximate number of inhabitants",
                    "affiliation": "Faction controlling the planet",
                    "orbitalPeriodDays": "Days required for one orbit around its star"
                }
            },
            "spaceships": {
                "description": "Vehicles capable of space travel",
                "fields": {
                    "shipID": "Unique identifier for the ship",
                    "model": "Ship's model designation",
                    "shipClass": "Category of spaceship",
                    "speedRating": "Relative speed capability",
                    "hyperdriveEquipped": "Boolean indicating FTL travel capability",
                    "uniqueName": "Specific name for notable ships",
                    "canTravelInterstellar": "Boolean indicating capability for interstellar travel"
                }
            },
            "factions": {
                "description": "Political or military organizations",
                "fields": {
                    "factionID": "Unique identifier for the faction",
                    "name": "Name of the organization",
                    "leader": "Character leading the faction",
                    "primaryGoal": "Main objective of the faction",
                    "ideology": "Guiding principles of the faction"
                }
            },
            "battles": {
                "description": "Military conflicts",
                "fields": {
                    "battleID": "Unique identifier for the battle",
                    "name": "Name of the battle",
                    "outcome": "Result of the conflict",
                    "battleDate": "Date when the battle occurred",
                    "casualties": "Approximate number of deaths",
                    "factions": "List of factions involved in the battle"
                }
            },
            "events": {
                "description": "Significant moments in the timeline",
                "fields": {
                    "eventID": "Unique identifier for the event",
                    "description": "What happened during the event",
                    "timestamp": "When the event occurred (BBY/ABY format)",
                    "significanceLevel": "Importance of the event (Low/Medium/High/Galactic)",
                    "participants": "Characters involved in the event",
                    "location": "Where the event took place",
                    "battle": "Associated battle (if applicable)",
                    "quote": "Memorable quote from the event",
                    "ship": "Associated ship (if applicable)"
                }
            },
            "force_abilities": {
                "description": "Powers that Force-sensitive characters can use",
                "fields": {
                    "abilityID": "Unique identifier for the ability",
                    "name": "Name of the Force power",
                    "type": "Category of ability",
                    "difficultyLevel": "Difficulty to master (1-10)",
                    "isLightSide": "Boolean indicating light side association",
                    "isDarkSide": "Boolean indicating dark side association"
                }
            },
            "lightsabers": {
                "description": "Energy sword weapons used by Jedi and Sith",
                "fields": {
                    "weaponID": "Unique identifier for the lightsaber",
                    "name": "Name of the lightsaber (if notable)",
                    "weaponType": "Always 'Lightsaber'",
                    "destructiveCapacity": "Measure of weapon power",
                    "color": "Color of the lightsaber blade",
                    "hiltDesign": "Style of the lightsaber handle"
                }
            },
            "artifacts": {
                "description": "Notable objects of significance",
                "fields": {
                    "artifactID": "Unique identifier for the artifact",
                    "name": "Name of the artifact",
                    "originEra": "Time period when the artifact was created",
                    "forceRelated": "Boolean indicating if connected to the Force"
                }
            },
            "technologies": {
                "description": "Scientific and technological developments",
                "fields": {
                    "technologyID": "Unique identifier for the technology",
                    "techType": "Category of technology",
                    "inventor": "Creator of the technology",
                    "functionDescription": "What the technology does"
                }
            },
            "vehicles": {
                "description": "Ground, air, or sea transportation",
                "fields": {
                    "vehicleID": "Unique identifier for the vehicle",
                    "type": "Model or category of vehicle",
                    "speed": "Maximum speed in appropriate units",
                    "terrainType": "Environment the vehicle operates in"
                }
            },
            "creatures": {
                "description": "Non-sentient life forms",
                "fields": {
                    "creatureID": "Unique identifier for the creature",
                    "speciesName": "Type of creature",
                    "habitat": "Environment where the creature lives",
                    "dangerLevel": "Threat level (0.1-10.0)"
                }
            },
            "missions": {
                "description": "Objectives undertaken by characters",
                "fields": {
                    "missionID": "Unique identifier for the mission",
                    "missionType": "Category of mission",
                    "missionGoal": "Objective of the mission",
                    "successRate": "Probability of success (0-100)"
                }
            }
        },
        "relationships": {
            "description": "Connections between entities",
            "types": {
                "biologicalParentOf": "Genetic parent-child relationship",
                "sibling": "Characters who share at least one parent",
                "hasSidekick": "Character with a loyal companion",
                "ownedBy": "Droid belonging to a character",
                "pilotedBy": "Ship operated by a character",
                "apprenticeOf": "Force user trained by another Force user",
                "memberOf": "Character belonging to a faction"
            }
        },
        "timelines": {
            "description": "Chronological sequences of events from each film",
            "episode_4": "Events from Episode IV: A New Hope (0 BBY)",
            "episode_5": "Events from Episode V: The Empire Strikes Back (3 ABY)",
            "episode_6": "Events from Episode VI: Return of the Jedi (4 ABY)"
        },
        "keyEvents": {
            "destructionOfAlderaan": {
                "description": "The Empire destroys Princess Leia's home planet",
                "film": "Episode IV: A New Hope",
                "timestamp": "0 BBY",
                "characters": ["Darth Vader", "Grand Moff Tarkin", "Princess Leia"]
            },
            "battleOfYavin": {
                "description": "The Rebels destroy the first Death Star",
                "film": "Episode IV: A New Hope",
                "timestamp": "0 BBY",
                "characters": ["Luke Skywalker", "Han Solo", "Darth Vader"]
            },
            "battleOfHoth": {
                "description": "The Empire attacks the Rebel base on Hoth",
                "film": "Episode V: The Empire Strikes Back",
                "timestamp": "3 ABY",
                "characters": ["Luke Skywalker", "Princess Leia", "Han Solo", "Darth Vader"]
            },
            "iAmYourFather": {
                "description": "Darth Vader reveals to Luke that he is his father",
                "film": "Episode V: The Empire Strikes Back",
                "timestamp": "3 ABY",
                "characters": ["Luke Skywalker", "Darth Vader"],
                "quote": "No, I am your father."
            },
            "hanSoloCarbonite": {
                "description": "Han Solo is frozen in carbonite",
                "film": "Episode V: The Empire Strikes Back",
                "timestamp": "3 ABY",
                "characters": ["Han Solo", "Princess Leia", "Darth Vader", "Boba Fett"]
            },
            "jabbaPalace": {
                "description": "Rescue of Han Solo from Jabba the Hutt",
                "film": "Episode VI: Return of the Jedi",
                "timestamp": "4 ABY",
                "characters": ["Luke Skywalker", "Princess Leia", "Han Solo", "Jabba the Hutt"]
            },
            "vaderRedemption": {
                "description": "Darth Vader turns against the Emperor to save Luke",
                "film": "Episode VI: Return of the Jedi",
                "timestamp": "4 ABY",
                "characters": ["Luke Skywalker", "Darth Vader", "Emperor Palpatine"]
            },
            "battleOfEndor": {
                "description": "The Rebels destroy the second Death Star",
                "film": "Episode VI: Return of the Jedi",
                "timestamp": "4 ABY",
                "characters": ["Lando Calrissian", "Admiral Ackbar"]
            }
        }
    }

    return data_dictionary


def generate_data_dictionary_markdown():
    """
    Generate a markdown formatted version of the data dictionary.

    Returns:
        str: Markdown text of the data dictionary
    """
    data_dict = generate_data_dictionary()
    markdown = []

    # Title
    markdown.append("# Star Wars Data Generator - Data Dictionary\n")

    # Overview
    markdown.append("## Overview\n")
    markdown.append(data_dict["overview"]["description"] + "\n")

    markdown.append("### Movies Included\n")
    for movie in data_dict["overview"]["moviesIncluded"]:
        markdown.append(f"- {movie}\n")

    markdown.append("\n### Abbreviations\n")
    for abbr, desc in data_dict["overview"]["abbreviations"].items():
        markdown.append(f"- **{abbr}**: {desc}\n")

    # Entities
    markdown.append("\n## Entities\n")
    for entity_type, entity_info in data_dict["entities"].items():
        markdown.append(f"### {entity_type.replace('_', ' ').title()}\n")
        markdown.append(f"{entity_info['description']}\n\n")
        markdown.append("| Field | Description |\n")
        markdown.append("| ----- | ----------- |\n")
        for field, desc in entity_info["fields"].items():
            markdown.append(f"| {field} | {desc} |\n")
        markdown.append("\n")

    # Relationships
    markdown.append("## Relationships\n")
    markdown.append(f"{data_dict['relationships']['description']}\n\n")
    markdown.append("| Type | Description |\n")
    markdown.append("| ---- | ----------- |\n")
    for rel_type, desc in data_dict["relationships"]["types"].items():
        markdown.append(f"| {rel_type} | {desc} |\n")

    # Timelines
    markdown.append("\n## Timelines\n")
    markdown.append(f"{data_dict['timelines']['description']}\n\n")
    for timeline, desc in {k: v for k, v in data_dict["timelines"].items() if k != 'description'}.items():
        markdown.append(f"- **{timeline}**: {desc}\n")

    # Key Events
    markdown.append("\n## Key Events\n")
    for event_id, event_info in data_dict["keyEvents"].items():
        markdown.append(f"### {event_id.replace('_', ' ').title()}\n")
        markdown.append(f"- **Description**: {event_info['description']}\n")
        markdown.append(f"- **Film**: {event_info['film']}\n")
        markdown.append(f"- **Timestamp**: {event_info['timestamp']}\n")
        markdown.append(
            f"- **Key Characters**: {', '.join(event_info['characters'])}\n")
        if "quote" in event_info:
            markdown.append(
                f"- **Memorable Quote**: \"{event_info['quote']}\"\n")
        markdown.append("\n")

    return ''.join(markdown)


if __name__ == "__main__":
    # Generate the full trilogy dataset
    dataset = generate_full_trilogy_data()
    serialize_to_json(dataset, "./data/star_wars_trilogy.json")

    # Generate the family tree example
    family_tree = generate_family_tree_example()
    serialize_to_json(family_tree, "./data/skywalker_family.json")

    # Generate the "I am your father" scene
    generator = StarWarsDataGenerator()
    vader_luke_scene = generator.generate_i_am_your_father_scene()
    serialize_to_json(vader_luke_scene, "./data/i_am_your_father.json")

    # Generate the data dictionary and save it
    data_dict = generate_data_dictionary()
    serialize_to_json(data_dict, "./data/star_wars_data_dictionary.json")

    # Generate and save markdown version of the data dictionary
    with open("star_wars_data_dictionary.md", "w") as f:
        f.write(generate_data_dictionary_markdown())

    print("\nGenerated files:")
    print("1. star_wars_trilogy.json - Comprehensive dataset covering Episodes 4-6")
    print("2. skywalker_family.json - The Skywalker family relationships")
    print("3. i_am_your_father.json - The iconic scene from The Empire Strikes Back")
    print("4. star_wars_data_dictionary.json - Data dictionary in JSON format")
    print("5. star_wars_data_dictionary.md - Data dictionary in Markdown format")

    # Print the famous revelation event
    print("\nThe famous revelation:")
    event = list(vader_luke_scene['events'].values())[0]
    print(f"Event: {event['description']}")
    print(f"Quote: {event['quote']}")

    vader_id = list(vader_luke_scene['siths'].keys())[0]
    luke_id = list(vader_luke_scene['jedis'].keys())[0]
    print(
        f"Relationship: {vader_luke_scene['characters'][vader_id]['name']} is the biological parent of {vader_luke_scene['characters'][luke_id]['name']}")
