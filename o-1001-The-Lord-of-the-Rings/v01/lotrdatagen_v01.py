import datetime


def generate_lotr_data_detailed():

    # --- Data Storage ---
    data = {
        "middle_earth": [], "region": [], "race": [], "kingdom": [], "person": [],
        "hobbit": [], "elf": [], "dwarf": [], "man": [], "wizard": [], "orc": [],
        "artifact": [], "weapon": [], "ring": [], "fellowship": [], "location": [],
        "journey": [], "battle": [], "alliance": [], "beast": [], "ancient_prophecy": [],
        "dark_fortress": [], "army": [], "magic_spell": [], "council": [], "valar": [],
        "maiar": [], "rune": [], "language": [], "silmaril": [], "numenorean": [],
        "gondorian": [], "runesmith": [], "elven_script": [], "palantir": [],
        # We will store relationships primarily via FK IDs in the source objects
    }

    # --- Core World Data ---
    data["middle_earth"].append({
        "worldID": "ME01", "ageCount": 3, "currentAge": 3,
        "ageName": "Third Age", "darkInfluenceLevel": 8.5  # High during War of the Ring
    })

    # --- Races ---
    data["race"].extend([
        {"raceID": "RACE01", "raceName": "Hobbit", "averageLifespan": 100,
            "languageFamily": "Westron (influenced by Mannish)"},
        {"raceID": "RACE02", "raceName": "Elf", "averageLifespan": -1,
            "languageFamily": "Eldarin (Sindarin, Quenya)"},  # Immortal
        {"raceID": "RACE03", "raceName": "Dwarf",
            "averageLifespan": 250, "languageFamily": "Khuzdul"},
        {"raceID": "RACE04", "raceName": "Man", "averageLifespan": 80,
            "languageFamily": "Westron/Various Mannish"},
        {"raceID": "RACE05", "raceName": "Orc", "averageLifespan": 40,
            "languageFamily": "Black Speech/Orkish"},  # Estimated lifespan
        {"raceID": "RACE06", "raceName": "Maiar", "averageLifespan": -1,
            "languageFamily": "Valarin/Quenya/Various"},  # Immortal spirits
        {"raceID": "RACE07", "raceName": "Valar", "averageLifespan": -
            1, "languageFamily": "Valarin"},  # Immortal spirits
        {"raceID": "RACE08", "raceName": "Ent", "averageLifespan": -
            1, "languageFamily": "Entish"},  # Effectively immortal
    ])

    # --- Languages ---
    # (Same as before)
    data["language"].extend([
        {"languageID": "LANG01", "languageName": "Westron",
            "writingSystem": "Certar/Tengwar", "complexityLevel": 5.0},
        {"languageID": "LANG02", "languageName": "Sindarin",
            "writingSystem": "Tengwar/Certar", "complexityLevel": 7.5},
        {"languageID": "LANG03", "languageName": "Quenya",
            "writingSystem": "Tengwar", "complexityLevel": 8.5},
        {"languageID": "LANG04", "languageName": "Khuzdul",
            "writingSystem": "Certar (Angerthas Moria/Erebor)", "complexityLevel": 7.0},
        {"languageID": "LANG05", "languageName": "Black Speech",
            "writingSystem": "Tengwar (adapted)", "complexityLevel": 6.0},
    ])
    data["elven_script"].append({
        "scriptID": "SCRIPT01", "scriptStyle": "Tengwar", "graceFactor": 9.0, "rarityIndex": 6.0,
        "script_BasedOn_LanguageID": "LANG02"
    })

    # --- Regions & Locations ---
    # (Adding more specific locations)
    data["region"].extend([
        {"regionID": "REG01", "regionName": "Eriador", "climateType": "Temperate",
            "notableLandmarks": "Shire, Rivendell, Bree, Weathertop", "localPopulation": 50000},
        {"regionID": "REG02", "regionName": "Rohan", "climateType": "Grasslands/Temperate",
            "notableLandmarks": "Edoras, Helm's Deep", "localPopulation": 150000},
        {"regionID": "REG03", "regionName": "Gondor", "climateType": "Temperate/Mediterranean",
            "notableLandmarks": "Minas Tirith, Osgiliath, Minas Morgul", "localPopulation": 500000},
        {"regionID": "REG04", "regionName": "Mordor", "climateType": "Ash Waste/Volcanic",
            "notableLandmarks": "Mount Doom, Barad-dûr, Cirith Ungol", "localPopulation": 200000},
        {"regionID": "REG05", "regionName": "Misty Mountains", "climateType": "Alpine",
            "notableLandmarks": "Moria, High Pass", "localPopulation": 10000},  # Orcs, Goblins
        {"regionID": "REG06", "regionName": "Rhovanion (Wilderland)", "climateType": "Temperate Forest/Plains",
         "notableLandmarks": "Lothlórien, Mirkwood, Erebor", "localPopulation": 100000},
    ])
    data["location"].extend([
        # Existing
        {"locationID": "LOC01", "locationName": "The Shire", "terrainType": "Hills/Farmland", "magicalAuraLevel": 1.0,
            "riskFactor": 0.5, "situated_In_RegionID": "REG01", "event_notes": ["Return of the Hobbits", "Scouring of the Shire (book)"]},
        {"locationID": "LOC02", "locationName": "Rivendell", "terrainType": "Hidden Valley", "magicalAuraLevel": 8.0, "riskFactor": 1.0,
            "situated_In_RegionID": "REG01", "event_notes": ["Council of Elrond held", "Fellowship formed", "Narsil reforged into Andúril"]},
        {"locationID": "LOC03", "locationName": "Moria (Khazad-dûm)", "terrainType": "Underground City/Mines", "magicalAuraLevel": 3.0, "riskFactor": 9.0,
         "situated_In_RegionID": "REG05", "event_notes": ["Fellowship passage", "Gandalf fights Balrog", "Orc attack at Balin's Tomb"]},
        {"locationID": "LOC04", "locationName": "Lothlórien", "terrainType": "Forest", "magicalAuraLevel": 9.0, "riskFactor": 2.0,
            "situated_In_RegionID": "REG06", "event_notes": ["Fellowship rests", "Meeting with Galadriel", "Receiving of Gifts (Phial, Cloaks, Lembas)"]},
        {"locationID": "LOC05", "locationName": "Helm's Deep", "terrainType": "Fortress/Valley", "magicalAuraLevel": 2.0, "riskFactor": 7.0,
            "situated_In_RegionID": "REG02", "event_notes": ["Battle of the Hornburg", "Arrival of Gandalf & Rohirrim", "Huorns destroy Orc army (book)"]},
        {"locationID": "LOC06", "locationName": "Minas Tirith", "terrainType": "City/Fortress", "magicalAuraLevel": 4.0, "riskFactor": 8.5,
            "situated_In_RegionID": "REG03", "event_notes": ["Siege of Gondor", "Battle of Pelennor Fields", "Aragorn uses Houses of Healing", "Coronation of Aragorn"]},
        {"locationID": "LOC07", "locationName": "Mount Doom (Orodruin)", "terrainType": "Volcano", "magicalAuraLevel": 6.0, "riskFactor": 10.0, "situated_In_RegionID": "REG04", "event_notes": [
            "One Ring destroyed", "Gollum falls", "Frodo & Sam rescued by Eagles"]},
        {"locationID": "LOC08", "locationName": "Isengard (Orthanc)", "terrainType": "Fortress/Plain", "magicalAuraLevel": 5.0, "riskFactor": 8.0, "situated_In_RegionID": "REG02", "event_notes": [
            "Saruman's base", "Ents attack and flood", "Saruman confronted / staff broken", "Palantír recovered"]},
        {"locationID": "LOC09", "locationName": "Barad-dûr", "terrainType": "Dark Tower/Fortress", "magicalAuraLevel": 9.5, "riskFactor": 10.0,
            "situated_In_RegionID": "REG04", "event_notes": ["Sauron's seat of power", "Tower collapses upon Ring's destruction"]},
        # New
        {"locationID": "LOC10", "locationName": "Weathertop (Amon Sûl)", "terrainType": "Hill Ruins", "magicalAuraLevel": 2.5, "riskFactor": 6.0, "situated_In_RegionID": "REG01", "event_notes": [
            "Frodo stabbed by Witch-king", "Gandalf previously fought Nazgûl"]},
        {"locationID": "LOC11", "locationName": "Amon Hen", "terrainType": "Hilltop Seat", "magicalAuraLevel": 3.0, "riskFactor": 5.0,
            "situated_In_RegionID": "REG06", "event_notes": ["Breaking of the Fellowship", "Boromir's death", "Frodo looks into Seat of Seeing"]},
        {"locationID": "LOC12", "locationName": "Cirith Ungol", "terrainType": "Pass/Tower", "magicalAuraLevel": 4.0, "riskFactor": 9.5,
            "situated_In_RegionID": "REG04", "event_notes": ["Frodo stung by Shelob", "Sam fights Shelob", "Orcs fight over Mithril coat"]},
        {"locationID": "LOC13", "locationName": "Edoras", "terrainType": "City/Hillfort", "magicalAuraLevel": 1.5, "riskFactor": 4.0,
            "situated_In_RegionID": "REG02", "event_notes": ["Capital of Rohan", "Gandalf frees Théoden", "Departure for Helm's Deep"]},
        {"locationID": "LOC14", "locationName": "Black Gate (Morannon)", "terrainType": "Fortified Gate", "magicalAuraLevel": 5.0, "riskFactor": 9.0, "situated_In_RegionID": "REG04", "event_notes": [
            "Battle of the Morannon", "Aragorn challenges Sauron", "Frodo & Sam passed nearby earlier"]},
        {"locationID": "LOC15", "locationName": "Paths of the Dead", "terrainType": "Caves/Mountain Pass", "magicalAuraLevel": 7.0,
            "riskFactor": 8.5, "situated_In_RegionID": "REG03", "event_notes": ["Aragorn summons Army of the Dead"]},
    ])

    # --- Kingdoms ---
    data["kingdom"].extend([
        {"kingdomID": "KNG01", "kingdomName": "Gondor", "foundingYear": -3320, "leadershipStructure":
            "Monarchy (Stewards/King)", "allianceStatus": "Allied with Rohan", "situated_In_RegionID": "REG03"},
        {"kingdomID": "KNG02", "kingdomName": "Rohan", "foundingYear": 2510, "leadershipStructure": "Monarchy",
            "allianceStatus": "Allied with Gondor", "situated_In_RegionID": "REG02"},
    ])

    # --- Key Characters (Persons + Subclasses) ---
    # IDs
    frodo_id = "PER001"
    sam_id = "PER002"
    gandalf_id = "PER003"
    aragorn_id = "PER004"
    legolas_id = "PER005"
    gimli_id = "PER006"
    boromir_id = "PER007"
    saruman_id = "PER008"
    sauron_id = "PER009"
    gollum_id = "PER010"
    elrond_id = "PER011"
    galadriel_id = "PER012"
    theoden_id = "PER013"
    eowyn_id = "PER014"
    faramir_id = "PER015"
    merry_id = "PER016"
    pippin_id = "PER017"
    witchking_id = "PER018"

    # Create base Person entries first, then subclass entries
    # Using lists to hold event links (FK IDs or descriptions)
    data["person"].extend([
        {"personID": frodo_id, "personName": "Frodo Baggins", "gender": "Male", "age": 50, "isRingBearer": True, "alignment": "Good", "fateStatus": "Sailed West", "belongs_To_RaceID": "RACE01",
            "events_participated": ["Council of Elrond", "Journey of Fellowship", "Stabbed at Weathertop", "Stung at Cirith Ungol", "Claimed Ring at Mt Doom", "Battle of Bywater (book)"]},
        {"personID": sam_id, "personName": "Samwise Gamgee", "gender": "Male", "age": 33, "isRingBearer": True, "alignment": "Good", "fateStatus": "Sailed West (later)", "belongs_To_RaceID": "RACE01", "events_participated": [
            "Council of Elrond", "Journey of Fellowship", "Fought Shelob", "Carried Frodo", "Used Phial of Galadriel", "Mayor of Shire"]},
        {"personID": gandalf_id, "personName": "Gandalf", "gender": "Male (appearance)", "age": -1, "isRingBearer": True, "alignment": "Good", "fateStatus": "Returned/Sailed West", "belongs_To_RaceID": "RACE06", "events_participated": [
            "Council of Elrond", "Journey of Fellowship", "Fell fighting Balrog", "Returned as White", "Freed Théoden", "Battle of Hornburg", "Battle of Pelennor Fields", "Battle of Morannon"]},
        {"personID": aragorn_id, "personName": "Aragorn II Elessar", "gender": "Male", "age": 87, "isRingBearer": False, "alignment": "Good", "fateStatus": "Died (King)", "belongs_To_RaceID": "RACE04", "events_participated": [
            "Council of Elrond", "Journey of Fellowship", "Battle of Hornburg", "Took Paths of the Dead", "Battle of Pelennor Fields", "Healed in Houses of Healing", "Battle of Morannon", "Crowned King"]},
        {"personID": legolas_id, "personName": "Legolas Greenleaf", "gender": "Male", "age": 2931, "isRingBearer": False, "alignment": "Good", "fateStatus": "Sailed West", "belongs_To_RaceID": "RACE02",
            "events_participated": ["Council of Elrond", "Journey of Fellowship", "Battle of Hornburg", "Battle of Pelennor Fields", "Took Paths of the Dead", "Battle of Morannon"]},
        {"personID": gimli_id, "personName": "Gimli", "gender": "Male", "age": 139, "isRingBearer": False, "alignment": "Good", "fateStatus": "Sailed West", "belongs_To_RaceID": "RACE03",
            "events_participated": ["Council of Elrond", "Journey of Fellowship", "Battle of Hornburg", "Took Paths of the Dead", "Battle of Pelennor Fields", "Battle of Morannon"]},
        {"personID": boromir_id, "personName": "Boromir", "gender": "Male", "age": 40, "isRingBearer": False, "alignment": "Good (flawed)", "fateStatus": "Died", "belongs_To_RaceID": "RACE04", "events_participated": [
            "Council of Elrond", "Journey of Fellowship", "Attempted to take Ring", "Died defending Hobbits at Amon Hen"]},
        {"personID": saruman_id, "personName": "Saruman", "gender": "Male (appearance)", "age": -1, "isRingBearer": False, "alignment": "Evil", "fateStatus": "Died",
         "belongs_To_RaceID": "RACE06", "events_participated": ["Betrayed Council", "Created Uruk-hai", "Defeated at Isengard", "Scouring of the Shire (book)"]},
        {"personID": sauron_id, "personName": "Sauron", "gender": "Male (spirit)", "age": -1, "isRingBearer": True, "alignment": "Evil", "fateStatus": "Defeated (spirit diminished)", "belongs_To_RaceID": "RACE06", "events_participated": [
            "Forged One Ring", "War of the Last Alliance (defeated)", "War of the Ring (directed forces)", "Spirit defeated with Ring"]},
        {"personID": gollum_id, "personName": "Gollum/Sméagol", "gender": "Male", "age": 589, "isRingBearer": True, "alignment": "Neutral/Evil", "fateStatus": "Died",
            "belongs_To_RaceID": "RACE01", "events_participated": ["Found Ring", "Guided Frodo/Sam", "Betrayed Frodo at Cirith Ungol", "Bit off finger", "Fell into Mt Doom"]},
        {"personID": elrond_id, "personName": "Elrond", "gender": "Male", "age": 6520, "isRingBearer": True, "alignment": "Good", "fateStatus": "Sailed West",
            "belongs_To_RaceID": "RACE02", "events_participated": ["Hosted Council", "Reforged Narsil", "Bearer of Vilya"]},
        {"personID": galadriel_id, "personName": "Galadriel", "gender": "Female", "age": 7000, "isRingBearer": True, "alignment": "Good", "fateStatus": "Sailed West",
            "belongs_To_RaceID": "RACE02", "events_participated": ["Hosted Fellowship", "Gave Gifts (Phial)", "Resisted Ring's temptation", "Bearer of Nenya"]},
        {"personID": theoden_id, "personName": "Théoden", "gender": "Male", "age": 71, "isRingBearer": False, "alignment": "Good", "fateStatus": "Died",
            "belongs_To_RaceID": "RACE04", "events_participated": ["Freed by Gandalf", "Led charge at Hornburg", "Led charge at Pelennor Fields", "Killed by Witch-king"]},
        {"personID": eowyn_id, "personName": "Éowyn", "gender": "Female", "age": 24, "isRingBearer": False, "alignment": "Good", "fateStatus": "Married Faramir",
            "belongs_To_RaceID": "RACE04", "events_participated": ["Defended Edoras", "Rode to Pelennor Fields (as Dernhelm)", "Slew Witch-king", "Healed by Aragorn"]},
        {"personID": faramir_id, "personName": "Faramir", "gender": "Male", "age": 36, "isRingBearer": False, "alignment": "Good", "fateStatus": "Steward/Prince of Ithilien",
            "belongs_To_RaceID": "RACE04", "events_participated": ["Defended Osgiliath", "Captured/Released Frodo & Sam", "Wounded at Siege", "Healed by Aragorn"]},
        {"personID": merry_id, "personName": "Meriadoc Brandybuck", "gender": "Male", "age": 36, "isRingBearer": False, "alignment": "Good", "fateStatus": "Master of Buckland/Died in Gondor", "belongs_To_RaceID": "RACE01",
            "events_participated": ["Council of Elrond", "Journey of Fellowship", "Pledged service to Théoden", "Rode to Pelennor Fields", "Helped slay Witch-king", "Battle of Bywater (book)"]},
        {"personID": pippin_id, "personName": "Peregrin Took", "gender": "Male", "age": 28, "isRingBearer": False, "alignment": "Good", "fateStatus": "Thain/Died in Gondor", "belongs_To_RaceID": "RACE01",
            "events_participated": ["Council of Elrond", "Journey of Fellowship", "Looked into Palantír", "Pledged service to Denethor", "Saved Faramir from pyre", "Battle of Morannon"]},
        {"personID": witchking_id, "personName": "Witch-king of Angmar", "gender": "Male (undead)", "age": 4000, "isRingBearer": True, "alignment": "Evil", "fateStatus": "Destroyed", "belongs_To_RaceID": "RACE04", "events_participated": [
            "Leader of Nazgûl", "Stabbed Frodo at Weathertop", "Led Siege of Gondor", "Fought Gandalf", "Slain by Éowyn and Merry at Pelennor Fields"]},

    ])

    # Subclass Data (link attributes specific to subclass)
    data["hobbit"].extend([
        {"personID": frodo_id, "hobbitFamilyName": "Baggins",
            "pipeWeedPreference": "Longbottom Leaf", "stealthSkill": 8.5},
        {"personID": sam_id, "hobbitFamilyName": "Gamgee",
            "pipeWeedPreference": "Unknown", "stealthSkill": 7.0},
        {"personID": gollum_id, "hobbitFamilyName":
            "Unknown (Stoor)", "pipeWeedPreference": "None", "stealthSkill": 9.0},
        {"personID": merry_id, "hobbitFamilyName": "Brandybuck",
            "pipeWeedPreference": "Old Toby", "stealthSkill": 6.5},
        {"personID": pippin_id, "hobbitFamilyName": "Took",
            "pipeWeedPreference": "Unknown", "stealthSkill": 6.0},
    ])
    data["elf"].extend([
        {"personID": legolas_id, "elfTitle": "Prince of Mirkwood",
            "bowSkill": 9.8, "immortalYearsLived": 2931},
        {"personID": elrond_id, "elfTitle": "Lord of Rivendell", "bowSkill": 7.0,
            "immortalYearsLived": 6520},  # Not primarily a warrior in 3rd Age
        # Power is not martial
        {"personID": galadriel_id, "elfTitle": "Lady of Lórien",
            "bowSkill": 5.0, "immortalYearsLived": 7000},
    ])
    data["dwarf"].append({"personID": gimli_id, "dwarfClan": "Durin's Folk",
                         "miningSkill": 7.0, "beardLength": 18.0})
    data["man"].extend([
        {"personID": aragorn_id, "realmAllegiance": "Gondor/Arnor",
            "swordSkill": 9.5, "lifespanVariance": 2.5},
        {"personID": boromir_id, "realmAllegiance": "Gondor",
            "swordSkill": 8.5, "lifespanVariance": 1.0},
        {"personID": theoden_id, "realmAllegiance": "Rohan",
            "swordSkill": 7.5, "lifespanVariance": 1.0},
        {"personID": eowyn_id, "realmAllegiance": "Rohan",
            "swordSkill": 8.0, "lifespanVariance": 1.0},
        {"personID": faramir_id, "realmAllegiance": "Gondor", "swordSkill": 8.0,
            "lifespanVariance": 1.1},  # Slight Numenorean heritage
        {"personID": witchking_id, "realmAllegiance": "Angmar/Mordor",
            "swordSkill": 9.0, "lifespanVariance": -1},  # Undead
    ])
    data["wizard"].extend([
        {"personID": gandalf_id, "wizardOrder": "Istari",
            "staffPowerLevel": 9.0, "robeColor": "Grey/White"},
        {"personID": saruman_id, "wizardOrder": "Istari",
            "staffPowerLevel": 8.5, "robeColor": "White/Many-Coloured"},
    ])
    data["numenorean"].append(
        {"personID": aragorn_id, "lineagePurity": 0.8, "numenorOriginYear": -3319, "royalBlood": True})
    data["gondorian"].extend([
        {"personID": boromir_id,
            "houseName": "Húrin (Stewards)", "militaryTradition": 8.0, "numenorDescent": True},
        {"personID": faramir_id,
            "houseName": "Húrin (Stewards)", "militaryTradition": 7.5, "numenorDescent": True},
    ])

    # --- Artifacts, Weapons, Rings ---
    # (Adding Phial, Mithril Coat, Horn)
    one_ring_id = "RING01"
    data["ring"].append({"ringID": one_ring_id, "ringName": "The One Ring", "ringPowerType": "Dominion/Control",
                        "corruptionIndex": 10.0, "forgingAge": 1600, "isOneRing": True, "artifactID": "ART01"})
    data["artifact"].append({"artifactID": "ART01", "artifactName": "The One Ring", "originEra": "Second Age",
                            "isCursed": True, "powerLevel": 10.0, "possessedByID": frodo_id})  # Current primary possessor for trilogy start

    sting_id = "WEAP01"
    data["weapon"].append({"weaponID": sting_id, "weaponName": "Sting", "weaponType": "Short Sword/Dagger",
                          "forgingSkillRequired": 8.0, "enchantmentLevel": 7.5, "artifactID": "ART02"})
    data["artifact"].append({"artifactID": "ART02", "artifactName": "Sting", "originEra": "First Age",
                            "isCursed": False, "powerLevel": 6.0, "possessedByID": frodo_id})
    anduril_id = "WEAP02"
    data["weapon"].append({"weaponID": anduril_id, "weaponName": "Andúril (Flame of the West)",
                          "weaponType": "Long Sword", "forgingSkillRequired": 9.5, "enchantmentLevel": 8.5, "artifactID": "ART03"})
    data["artifact"].append({"artifactID": "ART03", "artifactName": "Andúril (Narsil reforged)",
                            "originEra": "First Age/Third Age", "isCursed": False, "powerLevel": 9.0, "possessedByID": aragorn_id})
    glamdring_id = "WEAP03"
    data["weapon"].append({"weaponID": glamdring_id, "weaponName": "Glamdring (Foe-hammer)",
                          "weaponType": "Long Sword", "forgingSkillRequired": 8.5, "enchantmentLevel": 8.0, "artifactID": "ART04"})
    data["artifact"].append({"artifactID": "ART04", "artifactName": "Glamdring",
                            "originEra": "First Age", "isCursed": False, "powerLevel": 7.5, "possessedByID": gandalf_id})

    phial_id = "ART05"
    data["artifact"].append({"artifactID": phial_id, "artifactName": "Phial of Galadriel", "originEra": "Timeless (Starlight)",
                            "isCursed": False, "powerLevel": 7.0, "possessedByID": frodo_id})  # Initially given to Frodo, used by Sam
    mithril_id = "ART06"
    data["artifact"].append({"artifactID": mithril_id, "artifactName": "Mithril Coat", "originEra": "Unknown (Dwarven)",
                            "isCursed": False, "powerLevel": 8.5, "possessedByID": frodo_id})  # Armor artifact
    horn_id = "ART07"
    data["artifact"].append({"artifactID": horn_id, "artifactName": "Horn of Gondor", "originEra": "Unknown (Gondorian)",
                            "isCursed": False, "powerLevel": 4.0, "possessedByID": boromir_id})  # Symbolic artifact

    palantir_orthanc_id = "PAL01"
    data["palantir"].append({"palantirID": palantir_orthanc_id, "seeingPower": 8.0,
                            "corruptingInfluence": 7.0, "lostStatus": False, "artifactID": "ART08"})
    data["artifact"].append({"artifactID": "ART08", "artifactName": "Palantír of Orthanc", "originEra": "Second Age?",
                            "isCursed": False, "powerLevel": 8.5, "possessedByID": saruman_id})  # Saruman uses, then Aragorn

    # --- Groups: Fellowship, Armies, Alliances ---
    fellowship_id = "FEL01"
    data["fellowship"].append({"fellowshipID": fellowship_id, "name": "The Fellowship of the Ring",
                              "missionObjective": "Destroy the One Ring", "formationDate": datetime.datetime(3018, 10, 25)})
    # Link members implicitly via participation in Journey/Council

    gondor_army_id = "ARMY01"
    data["army"].append({"armyID": gondor_army_id, "armyName": "Army of Gondor", "totalUnits": 10000, "moraleLevel": 6.5,
                        "bannerSymbol": "White Tree", "commanderID": faramir_id})  # Faramir leads defence initially
    rohan_army_id = "ARMY02"
    data["army"].append({"armyID": rohan_army_id, "armyName": "Rohirrim", "totalUnits": 6000,
                        "moraleLevel": 8.0, "bannerSymbol": "White Horse", "commanderID": theoden_id})
    mordor_army_id = "ARMY03"
    data["army"].append({"armyID": mordor_army_id, "armyName": "Armies of Mordor", "totalUnits": 100000,
                        "moraleLevel": 5.0, "bannerSymbol": "Red Eye", "commanderID": witchking_id})  # Witch-king leads Siege
    isengard_army_id = "ARMY04"
    data["army"].append({"armyID": isengard_army_id, "armyName": "Uruk-hai of Isengard",
                        "totalUnits": 10000, "moraleLevel": 7.0, "bannerSymbol": "White Hand", "commanderID": saruman_id})
    dead_army_id = "ARMY05"
    data["army"].append({"armyID": dead_army_id, "armyName": "Army of the Dead (Oathbreakers)", "totalUnits": 5000,
                        "moraleLevel": 10.0, "bannerSymbol": "None (Spectral)", "commanderID": aragorn_id})  # Aragorn commands

    main_alliance_id = "ALL01"
    data["alliance"].append({"allianceID": main_alliance_id, "allianceName": "Alliance of Free Peoples (Informal)",
                            "primaryGoal": "Defeat Sauron", "strengthRating": 8.0})
    # Link Kingdoms to Alliance
    data["kingdom"][0]["allianceMembershipID"] = main_alliance_id
    data["kingdom"][1]["allianceMembershipID"] = main_alliance_id

    # --- Events: Council, Journeys, Battles ---
    council_elrond_id = "CNCL01"
    data["council"].append({"councilID": council_elrond_id, "councilName": "Council of Elrond", "purpose": "Decide fate of Ring",
                           "convenedDate": datetime.datetime(3018, 10, 25), "secrecyLevel": 8.0, "locationID": "LOC02"})

    # Journeys
    journey_fellowship_id = "JOU01"
    data["journey"].append({"journeyID": journey_fellowship_id, "journeyName": "Journey of the Fellowship (Rivendell to Amon Hen)", "distanceKm": 1500, "startedDate": datetime.datetime(
        3018, 12, 25), "endedDate": datetime.datetime(3019, 2, 26), "startsAtLocationID": "LOC02", "endsAtLocationID": "LOC11", "fellowshipID": fellowship_id})
    journey_frodo_sam_id = "JOU02"
    data["journey"].append({"journeyID": journey_frodo_sam_id, "journeyName": "Journey of Frodo & Sam (Amon Hen to Mt Doom)", "distanceKm": 1300, "startedDate": datetime.datetime(
        3019, 2, 26), "endedDate": datetime.datetime(3019, 3, 25), "startsAtLocationID": "LOC11", "endsAtLocationID": "LOC07"})
    journey_aragorn_company_id = "JOU03"
    data["journey"].append({"journeyID": journey_aragorn_company_id, "journeyName": "Journey of Aragorn, Legolas, Gimli (Post-Fellowship)", "distanceKm": 1000,
                           "startedDate": datetime.datetime(3019, 2, 26), "endedDate": datetime.datetime(3019, 3, 15), "startsAtLocationID": "LOC11", "endsAtLocationID": "LOC06"})  # Ends at Pelennor

    # Battles
    helms_deep_id = "BAT01"
    data["battle"].append({"battleID": helms_deep_id, "battleName": "Battle of the Hornburg", "outcome": "Victory for Rohan/Good", "battleDate": datetime.datetime(
        3019, 3, 3), "casualtyCount": 3000, "durationHours": 8, "locationID": "LOC05", "armiesInvolvedIDs": [rohan_army_id, isengard_army_id]})
    pelennor_id = "BAT02"
    data["battle"].append({"battleID": pelennor_id, "battleName": "Battle of the Pelennor Fields", "outcome": "Victory for Gondor/Rohan/Good", "battleDate": datetime.datetime(3019, 3, 15), "casualtyCount": 25000,
                          "durationHours": 12, "locationID": "LOC06", "armiesInvolvedIDs": [gondor_army_id, rohan_army_id, mordor_army_id, dead_army_id]})  # Army of Dead routed Corsairs enabling Aragorn's arrival
    black_gate_id = "BAT03"
    data["battle"].append({"battleID": black_gate_id, "battleName": "Battle of the Morannon", "outcome": "Victory for Gondor/Rohan/Good", "battleDate": datetime.datetime(
        3019, 3, 25), "casualtyCount": 5000, "durationHours": 4, "locationID": "LOC14", "armiesInvolvedIDs": [gondor_army_id, rohan_army_id, mordor_army_id]})

    # --- Beasts ---
    shelob_id = "BST01"
    data["beast"].append({"beastID": shelob_id, "beastName": "Shelob", "beastType": "Great Spider",
                         "hostilityLevel": 9.8, "tamable": False, "locationID": "LOC12"})
    balrog_id = "BST02"
    data["beast"].append({"beastID": balrog_id, "beastName": "Durin's Bane (Balrog)",
                         "beastType": "Maiar (Corrupted)", "hostilityLevel": 10.0, "tamable": False, "locationID": "LOC03"})

    # --- Final Links & Polish ---
    # Link people to kingdoms / locations (can add more specific occupancy links)
    data["person"][0]["homeLocationID"] = "LOC01"  # Frodo from Shire
    # Aragorn King of Gondor
    data["person"][3]["belongs_To_KingdomID"] = "KNG01"
    data["person"][6]["belongs_To_KingdomID"] = "KNG01"  # Boromir from Gondor
    data["person"][12]["belongs_To_KingdomID"] = "KNG02"  # Theoden King of Rohan

    # Link Artifacts back to characters via 'possessedByID' where relevant
    # Link Battles back to participants via events_participated list or specific battle participation links if ontology supported

    return data


if __name__ == "__main__":
    lotr_detailed_data = generate_lotr_data_detailed()

    print(f"Generated {len(lotr_detailed_data['person'])} Person instances.")
    print(
        f"Generated {len(lotr_detailed_data['location'])} Location instances with event notes.")
    print(f"Generated {len(lotr_detailed_data['battle'])} Battle instances.")
    print(f"Generated {len(lotr_detailed_data['journey'])} Journey instances.")

    # Example: Find Aragorn and list some events/links
    aragorn = next(
        (p for p in lotr_detailed_data['person'] if p['personName'].startswith('Aragorn')), None)
    if aragorn:
        print(
            f"\nDetails for {aragorn['personName']} (ID: {aragorn['personID']}):")
        print(f"  Race: {aragorn['belongs_To_RaceID']}")
        print(f"  Kingdom: {aragorn.get('belongs_To_KingdomID')}")
        print(f"  Events Participated: {aragorn.get('events_participated')}")
        # Note: Need to add this FK link during generation if desired
        weapon_id = aragorn.get('has_WeaponID')
        if weapon_id:
            weapon = next(
                (w for w in lotr_detailed_data['weapon'] if w['weaponID'] == weapon_id), None)
            if weapon:
                print(f"  Wields: {weapon['weaponName']}")

    # Example: Find Minas Tirith and its events
    minas_tirith = next(
        (loc for loc in lotr_detailed_data['location'] if loc['locationName'] == 'Minas Tirith'), None)
    if minas_tirith:
        print(
            f"\nDetails for {minas_tirith['locationName']} (ID: {minas_tirith['locationID']}):")
        print(f"  Region: {minas_tirith['situated_In_RegionID']}")
        print(f"  Event Notes: {minas_tirith.get('event_notes')}")
        battles_here = [b['battleName'] for b in lotr_detailed_data['battle'] if b.get(
            'locationID') == minas_tirith['locationID']]
        if battles_here:
            print(f"  Battles Fought Here: {battles_here}")
