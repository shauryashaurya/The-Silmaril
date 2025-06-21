import os
import json
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx

import os

# --- 1. Create the output directory if it doesn't exist ---
output_dir = './images/'
# os.makedirs() creates a directory.
# exist_ok=True prevents an error if the directory already exists.
os.makedirs(output_dir, exist_ok=True)
print(f"Ensured directory exists: {output_dir}")


# --- Configuration ---
DATA_DIR = "./data/"
EXPECTED_CLASSES = [
    "middle_earth", "region", "race", "kingdom", "person",
    "hobbit", "elf", "dwarf", "man", "wizard", "orc",
    "artifact", "weapon", "ring", "fellowship", "location",
    "journey", "battle", "alliance", "beast", "army", "council", "language", "numenorean",
    "gondorian", "elven_script", "palantir"
]
# , "magic_spell", "ancient_prophecy", "dark_fortress""valar", "maiar", "rune", "silmaril", "runesmith", "ent"

KEY_CHARACTER_NAMES = [
    "Frodo Baggins", "Samwise Gamgee", "Gandalf", "Aragorn II Elessar",
    "Legolas Greenleaf", "Gimli", "Boromir", "Meriadoc Brandybuck", "Peregrin Took",
    "Elrond", "Galadriel", "Saruman", "Sauron", "Gollum/Sméagol",
    "Théoden", "Éowyn", "Faramir", "Witch-king of Angmar"
    # Add "Éomer" if available in your person data
]
KEY_BEAST_NAMES = ["Shelob", "Durin's Bane (Balrog)"]

# global variables (I know, I know, focus on the viz, this is just fun...)
# to store the data...
lotr_data = {}
dfs = {}

# --- Helper function to parse dates ---
# JSON doesn't have a date type, dates were saved as ISO strings.
# We might need to convert them back for some plots.
# This basic loader reads them as strings for now.
# Parsing can be done when creating specific plots.


def load_all_data(data_dir, expected_classes):
    """Loads all JSON data files for expected classes from the data directory."""
    loaded_data = {}
    # print(f"Attempting to load data from: {os.path.abspath(data_dir)}")

    if not os.path.isdir(data_dir):
        print(
            f"Error: Data directory '{data_dir}' not found. Please run the generator script first.")
        return None

    for class_name in expected_classes:
        file_path = os.path.join(data_dir, f"{class_name}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_data[class_name] = json.load(f)
            print(
                f"Successfully loaded: {class_name}.json ({len(loaded_data[class_name])} entries)")
        except FileNotFoundError:
            print(
                f"Warning: File not found for class '{class_name}' at '{file_path}'. Skipping.")
            loaded_data[class_name] = []  # Add empty list if file missing
        except json.JSONDecodeError:
            print(
                f"Error: Could not decode JSON from file '{file_path}'. Skipping.")
            loaded_data[class_name] = []
        except Exception as e:
            print(f"Error loading file '{file_path}': {e}")
            loaded_data[class_name] = []

    print("\nData loading process complete.")
    # Basic verification: Check if key classes have loaded data
    key_classes_to_check = ["person", "location", "battle", "artifact", "race"]
    for key in key_classes_to_check:
        if key not in loaded_data or not loaded_data[key]:
            print(
                f"Verification Warning: No data loaded for key class '{key}'. Ensure generator ran and saved files.")
        else:
            print(f"Verification OK: Data loaded for key class '{key}'.")

    return loaded_data


def setup():
    print("loading data")
    # --- Load the data ---
    lotr_data = load_all_data(DATA_DIR, EXPECTED_CLASSES)

    # --- Convert lists to Pandas DataFrames (recommended for plotting) ---
    if lotr_data:
        dfs = {}
        for name, data_list in lotr_data.items():
            if data_list:  # Only create DataFrame if data exists
                dfs[name] = pd.DataFrame(data_list)
        print("\nConverted loaded data lists to Pandas DataFrames where possible.")
    else:
        print("\nCould not load data, cannot proceed with visualizations.")
        dfs = None  # Ensure dfs is None if loading failed

    # return lotr_data, dfs


#
# setup()
print("lotr_data: ", lotr_data)
print("loading data")
# --- Load the data ---
lotr_data = load_all_data(DATA_DIR, EXPECTED_CLASSES)

# --- Convert lists to Pandas DataFrames (recommended for plotting) ---
if lotr_data:
    dfs = {}
    for name, data_list in lotr_data.items():
        if data_list:  # Only create DataFrame if data exists
            dfs[name] = pd.DataFrame(data_list)
            print(f"successfully converted {name} to dataframe")
    print("\nConverted loaded data lists to Pandas DataFrames where possible.")
else:
    print("\nCould not load data, cannot proceed with visualizations.")
    dfs = None  # Ensure dfs is None if loading failed
#


# --- Viz 1 (Analysis 1): Pie Chart - Characters by Race ---
def viz1():
    print("\nGenerating Viz 1: Character Distribution by Race")
    if 'person' in dfs and 'race' in dfs:
        try:
            df_person = dfs['person'].copy()
            df_race = dfs['race'].copy()
            # Merge to get race names
            df_person_race = pd.merge(
                df_person, df_race, left_on='belongs_To_RaceID', right_on='raceID', how='left')
            # Count characters per race
            race_counts = df_person_race['raceName'].value_counts(
            ).reset_index()
            race_counts.columns = ['Race', 'Count']

            fig1 = px.pie(race_counts, names='Race', values='Count',
                          title='Distribution of Key Characters by Race',
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            # # fig1.show()
            # show_fig_or_image(fig1)
            # fig1.write_image(fig1.layout.title.text.replace(' ', '_'))
            return fig1
        except Exception as e:
            print(f"Error generating Viz 1: {e}")
    else:
        print("Skipping Viz 1: Missing 'person' or 'race' data.")


# --- Viz 2 (Analysis 1): Stacked Bar Chart - Characters by Race & Alignment ---
def viz2():
    print("\nGenerating Viz 2: Character Alignment by Race")
    if 'person' in dfs and 'race' in dfs:
        try:
            df_person = dfs['person'].copy()
            df_race = dfs['race'].copy()
            df_person_race = pd.merge(
                df_person, df_race, left_on='belongs_To_RaceID', right_on='raceID', how='left')

            # Group by Race and Alignment
            alignment_counts = df_person_race.groupby(
                ['raceName', 'alignment']).size().reset_index(name='Count')

            fig2 = px.bar(alignment_counts, x='raceName', y='Count', color='alignment',
                          title='Character Alignment Distribution within Each Race',
                          labels={
                              'raceName': 'Race', 'Count': 'Number of Characters', 'alignment': 'Alignment'},
                          color_discrete_sequence=px.colors.qualitative.Pastel,
                          barmode='stack')
            fig2.update_layout(xaxis_title="Race",
                               yaxis_title="Number of Characters")
            # fig2.show()
            return fig2
        except Exception as e:
            print(f"Error generating Viz 2: {e}")
    else:
        print("Skipping Viz 2: Missing 'person' or 'race' data.")


# --- Viz 3 (Analysis 2): Bar Chart - Significant Item Count per Character ---
# Simplified from Network Graph - shows count of significant items linked
def viz3():
    print("\nGenerating Viz 3: Significant Item Count per Character")
    if 'person' in dfs and 'artifact' in dfs:
        try:
            df_person = dfs['person'].copy()
            df_artifact = dfs['artifact'].copy()

            # Count artifacts possessed by each person
            # Note: This uses 'possessedByID'. Expand if using 'wields_RingID', 'has_WeaponID' etc.
            item_counts = df_artifact['possessedByID'].value_counts(
            ).reset_index()
            item_counts.columns = ['personID', 'ItemCount']

            # Merge with person names
            df_person_items = pd.merge(
                item_counts, df_person[['personID', 'personName']], on='personID', how='left')
            # Filter for characters who possess items
            df_person_items = df_person_items.dropna(subset=['personName'])

            fig3 = px.bar(df_person_items, x='personName', y='ItemCount',
                          title='Number of Significant Artifacts Possessed by Key Characters',
                          labels={'personName': 'Character',
                                  'ItemCount': 'Number of Artifacts'},
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            fig3.update_layout(xaxis_title="Character",
                               yaxis_title="Number of Artifacts")
            # fig3.show()
            return fig3
        except Exception as e:
            print(f"Error generating Viz 3: {e}")
    else:
        print("Skipping Viz 3: Missing 'person' or 'artifact' data.")

# --- Viz 4 (Analysis 2): Bar Chart - Item Power Levels ---


def viz4():
    print("\nGenerating Viz 4: Power Levels of Major Artifacts/Weapons")
    if 'artifact' in dfs:
        try:
            df_artifact = dfs['artifact'].copy()
            # Filter for artifacts with a defined power level and maybe exclude the One Ring for scale
            df_powerful_items = df_artifact[df_artifact['powerLevel'].notna() & (df_artifact['artifactName'] != "The One Ring")].sort_values(
                'powerLevel', ascending=False).head(10)  # Top 10 excluding One Ring

            fig4 = px.bar(df_powerful_items, x='artifactName', y='powerLevel',
                          title='Power Levels of Major Artifacts (Top 10 excluding One Ring)',
                          labels={'artifactName': 'Artifact Name',
                                  'powerLevel': 'Power Level'},
                          color='powerLevel',  # Color by power level
                          color_continuous_scale=px.colors.sequential.PuBu)  # Using a sequential scale here
            fig4.update_layout(xaxis_title="Artifact",
                               yaxis_title="Estimated Power Level")
            # fig4.show()
            return fig4
        except Exception as e:
            print(f"Error generating Viz 4: {e}")
    else:
        print("Skipping Viz 4: Missing 'artifact' data.")


# ---  Viz 5 (Analysis 3): Fellowship Journey Path (Sequence vs. Risk) ---
def viz5():
    print("\nGenerating Viz 5: Fellowship Journey Path (Sequence vs. Risk Factor)")
    # This replaces the previous, flawed timeline chart for Viz #5

    df_location = dfs['location'].copy()
    df_journey = dfs['journey'].copy()

    # --- Data Preparation ---
    # Manually define key locations in sequence for the main Fellowship journey (JOU01)
    # This sequence is based on story knowledge, we only added start/end int the dadata :(
    # bu buh buh y'kno'wha'a'mean...
    loc_map = df_location.set_index('locationName')['locationID'].to_dict()
    fellowship_loc_names_in_order = [
        "Rivendell",
        "Moria (Khazad-dûm)",
        "Lothlórien",
        "Amon Hen"
        # Add more intermediate points if desired
    ]
    fellowship_loc_ids_in_order = [loc_map.get(
        name) for name in fellowship_loc_names_in_order if loc_map.get(name)]

    # Filter location data for these IDs
    df_journey_path = df_location[df_location['locationID'].isin(
        fellowship_loc_ids_in_order)].copy()

    # Order the DataFrame according to the defined sequence
    # Convert locationID to a categorical type with the specified order
    df_journey_path['locationID'] = pd.Categorical(
        df_journey_path['locationID'],
        categories=fellowship_loc_ids_in_order,
        ordered=True
    )
    df_journey_path = df_journey_path.sort_values('locationID')

    # Add a sequence number for plotting on the x-axis
    df_journey_path['Sequence'] = range(1, len(df_journey_path) + 1)

    # Ensure riskFactor is numeric
    df_journey_path['riskFactor'] = pd.to_numeric(
        df_journey_path['riskFactor'], errors='coerce')
    # Drop rows where risk factor couldn't be determined
    df_journey_path = df_journey_path.dropna(subset=['riskFactor'])

    # --- Plotting ---
    if not df_journey_path.empty:
        fig5 = go.Figure()

        # Add the line connecting locations in sequence
        fig5.add_trace(go.Scatter(
            x=df_journey_path['Sequence'],
            y=df_journey_path['riskFactor'],
            mode='lines+markers',  # Show line and points
            marker=dict(
                color=px.colors.qualitative.Pastel[0],  # Use a pastel color
                size=10,
                line=dict(width=1, color='DarkSlateGrey')
            ),
            line=dict(
                # Different pastel color for line
                color=px.colors.qualitative.Pastel[1],
                width=2
            ),
            name='Journey Risk Profile'  # Name for hover/legend if needed
        ))

        # Add location names as text labels slightly above the markers
        fig5.add_trace(go.Scatter(
            x=df_journey_path['Sequence'],
            y=df_journey_path['riskFactor'],
            mode='text',
            text=df_journey_path['locationName'],
            textposition="top center",  # Position text above marker
            textfont=dict(size=10),
            showlegend=False  # Don't show text trace in legend
        ))

        fig5.update_layout(
            title="Fellowship Journey - Location Sequence vs. Risk Factor",
            xaxis_title="Sequence in Journey",
            yaxis_title="Estimated Risk Factor",
            xaxis=dict(
                tickmode='array',  # Explicitly set ticks
                tickvals=df_journey_path['Sequence'],
                # Label ticks
                ticktext=[f"Step {s}" for s in df_journey_path['Sequence']]
            ),
            showlegend=False,  # Hide legend for cleaner look
            plot_bgcolor='rgba(245, 245, 245, 1)'  # Light grey background
        )
        # fig5.show()
        return fig5
    else:
        print("Could not generate data for alternative Viz 5 - check location names, sequence, and risk factor data.")

# --- Viz 5_1: Line Chart - Journey Risk Profile ---


def viz6():
    # This is the same as the "Viz 5" provided previously. Re-using the logic.
    print("\nGenerating Viz 5_1: Journey Risk Profile (Same as Viz 5)")

    # Re-use code from Viz 5 (Sequence vs Risk)
    # Define paths for different journeys if desired
    df_location = dfs['location'].copy()
    loc_map = df_location.set_index('locationName')['locationID'].to_dict()

    journeys_to_plot = {
        "Fellowship (JOU01)": ["Rivendell", "Moria (Khazad-dûm)", "Lothlórien", "Amon Hen"],
        # Simplified
        "Frodo & Sam (JOU02)": ["Amon Hen", "Cirith Ungol", "Mount Doom (Orodruin)"],
    }

    fig5_1 = go.Figure()
    colors = px.colors.qualitative.Pastel

    for i, (journey_name, loc_names) in enumerate(journeys_to_plot.items()):
        loc_ids_in_order = [loc_map.get(name)
                            for name in loc_names if loc_map.get(name)]
        if not loc_ids_in_order:
            continue  # Skip if no valid locations found

        df_journey_path = df_location[df_location['locationID'].isin(
            loc_ids_in_order)].copy()
        df_journey_path['locationID'] = pd.Categorical(
            df_journey_path['locationID'], categories=loc_ids_in_order, ordered=True)
        df_journey_path = df_journey_path.sort_values('locationID')
        df_journey_path['Sequence'] = range(1, len(df_journey_path) + 1)
        df_journey_path['riskFactor'] = pd.to_numeric(
            df_journey_path['riskFactor'], errors='coerce')
        df_journey_path = df_journey_path.dropna(subset=['riskFactor'])

        if not df_journey_path.empty:
            fig5_1.add_trace(go.Scatter(
                x=df_journey_path['Sequence'],
                y=df_journey_path['riskFactor'],
                mode='lines+markers',
                name=journey_name,
                marker=dict(color=colors[i % len(colors)], size=8),
                line=dict(color=colors[(i+1) % len(colors)], width=2),
                text=df_journey_path['locationName'],  # Add hover text
                hoverinfo='text+y'
            ))

    fig5_1.update_layout(
        title="Journey Risk Profiles",
        xaxis_title="Sequence Step in Journey",
        yaxis_title="Estimated Risk Factor",
        hovermode="x unified"
    )
    # fig5_1.show()
    return fig5_1

# --- Viz 5_2 (Analysis 3): Bar Chart - Average Journey Risk ---


def viz7():
    print("\nGenerating Viz 5_2: Average Risk Factor per Major Journey")
    if 'location' in dfs and 'journey' in dfs:
        try:
            df_location = dfs['location'].copy()
            df_journey = dfs['journey'].copy()
            df_location['riskFactor'] = pd.to_numeric(
                df_location['riskFactor'], errors='coerce')
            loc_risk_map = df_location.set_index(
                'locationID')['riskFactor'].dropna().to_dict()

            avg_risks = []
            # Define locations roughly associated with each journey (more robust than just start/end)
            journey_locs = {
                'JOU01': ["LOC02", "LOC03", "LOC04", "LOC11"],  # Fellowship
                'JOU02': ["LOC11", "LOC12", "LOC07"],  # Frodo/Sam
                'JOU03': ["LOC11", "LOC15", "LOC06"]  # Aragorn et al.
            }

            for journey_id, loc_ids in journey_locs.items():
                journey_info = df_journey[df_journey['journeyID']
                                          == journey_id]
                if not journey_info.empty:
                    journey_name = journey_info.iloc[0]['journeyName']
                    risks = [loc_risk_map.get(
                        loc_id) for loc_id in loc_ids if loc_id in loc_risk_map]
                    if risks:
                        avg_risk = sum(risks) / len(risks)
                        avg_risks.append(
                            {'Journey': journey_name, 'AverageRisk': avg_risk})

            if avg_risks:
                df_avg_risk = pd.DataFrame(avg_risks)
                fig5_2 = px.bar(df_avg_risk, x='Journey', y='AverageRisk',
                                title='Average Location Risk Factor per Major Journey',
                                labels={'AverageRisk': 'Average Risk Factor'},
                                color='Journey',  # Color bars by Journey
                                color_discrete_sequence=px.colors.qualitative.Pastel)
                fig5_2.update_layout(xaxis_title="Journey",
                                     yaxis_title="Average Risk Factor")
                # fig5_2.show()
                return fig5_2
            else:
                print("Could not calculate average risks for journeys.")

        except Exception as e:
            print(f"Error generating Viz 5_2: {e}")
    else:
        print("Skipping Viz 5_2: Missing 'location' or 'journey' data.")


# --- Viz 6 (Analysis 4): Bar Chart - Battle Casualties ---
def viz8():
    print("\nGenerating Viz 6: Estimated Casualties in Major Battles")
    if 'battle' in dfs:
        try:
            df_battle = dfs['battle'].copy()
            # Ensure casualtyCount is numeric
            df_battle['casualtyCount'] = pd.to_numeric(
                df_battle['casualtyCount'], errors='coerce')
            df_battle_casualties = df_battle.dropna(
                subset=['casualtyCount']).sort_values('casualtyCount', ascending=False)

            fig6 = px.bar(df_battle_casualties, x='battleName', y='casualtyCount',
                          title='Estimated Casualties in Major Battles',
                          labels={'battleName': 'Battle',
                                  'casualtyCount': 'Estimated Casualties'},
                          color='casualtyCount',
                          color_continuous_scale=px.colors.sequential.OrRd)  # Red scale for casualties
            fig6.update_layout(xaxis_title="Battle",
                               yaxis_title="Estimated Casualties")
            # fig6.show()
            return fig6
        except Exception as e:
            print(f"Error generating Viz 6: {e}")
    else:
        print("Skipping Viz 6: Missing 'battle' data.")


# --- Viz 7 (Analysis 4): Sankey Diagram - Armies in Pelennor Fields ---
def viz9():
    print("\nGenerating Viz 7: Army Participation in Pelennor Fields")
    if 'battle' in dfs and 'army' in dfs:
        try:
            df_battle = dfs['battle'].copy()
            df_army = dfs['army'].copy()

            # Focus on Pelennor Fields
            pelennor_battle_series = df_battle[df_battle['battleName']
                                               == 'Battle of the Pelennor Fields']

            if not pelennor_battle_series.empty:
                pelennor_battle = pelennor_battle_series.iloc[0]
                involved_army_ids = pelennor_battle.get(
                    'armiesInvolvedIDs', [])

                if involved_army_ids:
                    # Map IDs to names
                    army_id_to_name = df_army.set_index(
                        'armyID')['armyName'].to_dict()
                    involved_army_names = [army_id_to_name.get(
                        id, f"Unknown Army ({id})") for id in involved_army_ids]

                    # Define nodes (Armies + Battle)
                    all_labels = involved_army_names + \
                        [pelennor_battle['battleName']]
                    # Create mapping from label to index
                    nodes = {name: i for i, name in enumerate(all_labels)}

                    # Define links (Army -> Battle)
                    source_indices = [nodes[name]
                                      for name in involved_army_names]
                    target_index = nodes[pelennor_battle['battleName']]
                    target_indices = [target_index] * len(involved_army_names)
                    # Values (e.g., army sizes - handle missing data/ensure numeric)
                    df_army['totalUnits'] = pd.to_numeric(
                        df_army['totalUnits'], errors='coerce').fillna(1)  # Ensure numeric, default 1
                    army_id_to_size = df_army.set_index(
                        'armyID')['totalUnits'].to_dict()
                    # Use 1 if size unknown
                    values = [army_id_to_size.get(id, 1)
                              for id in involved_army_ids]

                    # Define colors using Pastel palette indices
                    colors = px.colors.qualitative.Pastel
                    node_colors = [colors[i % len(colors)]
                                   for i in range(len(all_labels))]

                    link_colors = []
                    for i in range(len(source_indices)):
                        base_color_rgb = colors[i %
                                                len(colors)]  # Gets 'rgb(R,G,B)'
                        # Extract the R,G,B part and format as rgba
                        # Removes 'rgb(' and ')'
                        rgb_values = base_color_rgb[4:-1]
                        # Append rgba string with 0.6 alpha
                        link_colors.append(f"rgba({rgb_values}, 0.6)")

                    # Create Sankey diagram
                    fig7 = go.Figure(data=[go.Sankey(
                        node=dict(
                            pad=15,
                            thickness=20,
                            line=dict(color="black", width=0.5),
                            label=all_labels,
                            color=node_colors
                        ),
                        link=dict(
                            source=source_indices,
                            target=target_indices,
                            value=values,
                            color=link_colors
                        )
                    )])

                    fig7.update_layout(
                        title_text=f"Armies Participating in {pelennor_battle['battleName']}", font_size=10)
                    # fig7.show()
                    return fig7
                else:
                    print("Skipping Viz 7: No army IDs found for Pelennor Fields.")
            else:
                print("Skipping Viz 7: Pelennor Fields battle not found in data.")

        except Exception as e:
            print(f"Error generating Viz 7: {e}")
    else:
        print("Skipping Viz 7: Missing 'battle' or 'army' data.")

# --- Viz 8 (Analysis 4): Table - Battle Summary (MODIFIED - Dates Removed) ---


def viz10():
    print("\nGenerating Viz 8: Summary Table of Major Battles (Dates Removed)")
    if 'battle' in dfs and 'location' in dfs:
        try:
            df_battle = dfs['battle'].copy()
            df_location = dfs['location'].copy()

            # Merge location names
            df_battle_loc = pd.merge(df_battle, df_location[[
                                     'locationID', 'locationName']], on='locationID', how='left')

            # **MODIFICATION:** Select columns *excluding* battleDate
            columns_to_display = ['battleName',
                                  'locationName', 'outcome', 'casualtyCount']
            df_table = df_battle_loc[columns_to_display].copy()

            # Rename columns for display
            df_table.rename(columns={
                'battleName': 'Battle',
                # 'battleDate': 'Date', # Removed
                'locationName': 'Location',
                'outcome': 'Outcome',
                'casualtyCount': 'Casualties (Est.)'
            }, inplace=True)

            # Apply corrected color fix for rgba
            header_fill_color = px.colors.qualitative.Pastel[0]
            cell_fill_base_color = px.colors.qualitative.Pastel[1]
            try:
                cell_rgb_values = cell_fill_base_color.split('(')[1].split(')')[
                    0]
                # Slightly adjusted alpha
                cell_fill_color_rgba = f"rgba({cell_rgb_values}, 0.65)"
            except IndexError:
                cell_fill_color_rgba = "rgba(200, 200, 200, 0.6)"  # Fallback

            fig8 = go.Figure(data=[go.Table(
                header=dict(values=list(df_table.columns),
                            fill_color=header_fill_color,
                            align='left', font=dict(color='black', size=12)),
                cells=dict(values=[df_table[col] for col in df_table.columns],
                           fill_color=cell_fill_color_rgba,
                           align='left', font=dict(color='black', size=11))
            )])
            fig8.update_layout(
                title="Summary Table of Major Battles (Location, Outcome, Casualties)")
            # fig8.show()
            return fig8

        except Exception as e:
            print(f"Error generating Viz 8: {e}")
    else:
        print("Skipping Viz 8: Missing 'battle' or 'location' data.")


# --- Battle Viz 8_1: Pie Chart of Battle Outcomes ---
def viz11():
    print("\nGenerating Battle Viz 8_1: Pie Chart of Battle Outcomes")
    if 'battle' in dfs:
        try:
            df_battle = dfs['battle'].copy()
            # Consider only major battles if needed, or all listed
            outcome_counts = df_battle['outcome'].value_counts().reset_index()
            outcome_counts.columns = ['Outcome', 'Count']

            # Define a color map using Pastel colors
            # Ensure outcomes exactly match those in your data
            color_map = {
                'Victory for Rohan/Good': px.colors.qualitative.Pastel[0],
                'Victory for Gondor/Rohan/Good': px.colors.qualitative.Pastel[1],
                # Add mappings for other potential outcomes if they exist
                # 'Defeat': px.colors.qualitative.Pastel[3],
            }

            fig_b1 = px.pie(outcome_counts, names='Outcome', values='Count',
                            title='Distribution of Outcomes for Major Battles',
                            color='Outcome',  # Color slices by outcome category
                            color_discrete_map=color_map
                            )
            fig_b1.update_traces(textposition='inside', textinfo='percent+label', pull=[
                                 0.05] * len(outcome_counts))  # Explode slices slightly
            # fig_b1.show()
            return fig_b1
        except Exception as e:
            print(f"Error generating NEW Battle Viz 1: {e}")
    else:
        print("Skipping Battle Viz 8_1: Missing 'battle' data.")

# --- Battle Viz 8_2: Bar Chart of Battle Durations ---


def viz12():
    print("\nGenerating Battle Viz 8_2: Bar Chart of Battle Durations")
    if 'battle' in dfs:
        try:
            df_battle = dfs['battle'].copy()
            # Ensure durationHours is numeric and handle missing values
            df_battle['durationHours'] = pd.to_numeric(
                df_battle['durationHours'], errors='coerce')
            df_battle_durations = df_battle.dropna(
                subset=['durationHours']).sort_values('durationHours', ascending=False)

            fig_b2 = px.bar(df_battle_durations, x='battleName', y='durationHours',
                            title='Estimated Duration of Major Battles',
                            labels={'battleName': 'Battle',
                                    'durationHours': 'Duration (Hours)'},
                            color='battleName',  # Color each bar differently
                            color_discrete_sequence=px.colors.qualitative.Pastel)  # Use pastel sequence
            fig_b2.update_layout(
                xaxis_title="Battle", yaxis_title="Estimated Duration (Hours)", showlegend=False)
            # fig_b2.show()
            return fig_b2
        except Exception as e:
            print(f"Error generating Battle Viz 2: {e}")
    else:
        print("Skipping Battle Viz 8_2: Missing 'battle' data.")


# ---  Battle Viz 8_3: Bar Chart of Number of Armies Involved ---
def viz13():
    print("\nGenerating  Battle Viz 8_3: Number of Armies Involved per Battle")
    if 'battle' in dfs:
        try:
            df_battle = dfs['battle'].copy()

            # Calculate the number of armies involved for each battle
            # Ensure 'armiesInvolvedIDs' is treated as a list
            def count_armies(id_list):
                if isinstance(id_list, list):
                    return len(id_list)
                return 0  # Return 0 if it's not a list or is missing

            df_battle['numArmies'] = df_battle['armiesInvolvedIDs'].apply(
                count_armies)
            df_battle_armies = df_battle[df_battle['numArmies'] > 0].sort_values(
                'numArmies', ascending=False)

            fig_b3 = px.bar(df_battle_armies, x='battleName', y='numArmies',
                            title='Number of Distinct Armies Involved in Major Battles',
                            labels={'battleName': 'Battle',
                                    'numArmies': 'Number of Armies'},
                            color='numArmies',  # Color bars by the count
                            color_continuous_scale=px.colors.sequential.Blues_r)  # Use a reversed sequential scale
            fig_b3.update_layout(xaxis_title="Battle",
                                 yaxis_title="Number of Armies Involved")
            # fig_b3.show()
            return fig_b3
        except Exception as e:
            print(f"Error generating  Battle Viz 3: {e}")
    else:
        print("Skipping Battle Viz 3: Missing 'battle' data or 'armiesInvolvedIDs'.")


# --- Viz 9 (Analysis 5): Scatter Plot - Location Risk vs. Events ---
def viz14():
    print("\nGenerating Viz 9: Location Risk Factor vs. Number of Major Events")
    if 'location' in dfs and 'battle' in dfs and 'council' in dfs:
        try:
            df_location = dfs['location'].copy()
            df_battle = dfs['battle'].copy()
            df_council = dfs['council'].copy()
            # df_journey = dfs.get('journey', pd.DataFrame()) # Handle missing journey data

            # Count events per location
            battle_counts = df_battle['locationID'].value_counts()
            council_counts = df_council['locationID'].value_counts()
            # journey_start_counts = df_journey['startsAtLocationID'].value_counts() if not df_journey.empty else pd.Series(dtype=int)
            # journey_end_counts = df_journey['endsAtLocationID'].value_counts() if not df_journey.empty else pd.Series(dtype=int)

            # Combine counts
            df_location['battleCount'] = df_location['locationID'].map(
                battle_counts).fillna(0)
            df_location['councilCount'] = df_location['locationID'].map(
                council_counts).fillna(0)
            # df_location['journeyStartCount'] = df_location['locationID'].map(journey_start_counts).fillna(0)
            # df_location['journeyEndCount'] = df_location['locationID'].map(journey_end_counts).fillna(0)
            # df_location['totalEvents'] = df_location['battleCount'] + df_location['councilCount'] + df_location['journeyStartCount'] + df_location['journeyEndCount']
            df_location['totalEvents'] = df_location['battleCount'] + \
                df_location['councilCount']  # Simplified event count

            # Ensure riskFactor is numeric
            df_location['riskFactor'] = pd.to_numeric(
                df_location['riskFactor'], errors='coerce')
            df_plot = df_location.dropna(subset=['riskFactor', 'totalEvents'])

            fig9 = px.scatter(df_plot, x="riskFactor", y="totalEvents",
                              text="locationName",  # Label points with location names
                              title="Location Risk Factor vs. Number of Major Events (Battles or Councils)",
                              labels={'riskFactor': 'Risk Factor',
                                      'totalEvents': 'Number of Events'},
                              color_discrete_sequence=px.colors.qualitative.Pastel)
            fig9.update_traces(textposition='top center')
            fig9.update_layout(xaxis_title="Estimated Risk Factor",
                               yaxis_title="Number of Major Events")
            # fig9.show()
            return fig9
        except Exception as e:
            print(f"Error generating Viz 9: {e}")
    else:
        print("Skipping Viz 9: Missing 'location', 'battle', or 'council' data.")


# --- Viz 10 (Analysis 5): Bar Chart - Events per Location ---
def viz15():
    print("\nGenerating Viz 10: Number of Major Events per Location")
    if 'location' in dfs and 'battle' in dfs and 'council' in dfs:  # Using pre-calculated df_plot from Viz 8
        try:
            # Reuse df_plot from Viz 8 calculation if possible, otherwise recalculate
            if 'df_plot' not in locals() or df_plot.empty:  # Recalculate if needed
                df_location = dfs['location'].copy()
                df_battle = dfs['battle'].copy()
                df_council = dfs['council'].copy()
                battle_counts = df_battle['locationID'].value_counts()
                council_counts = df_council['locationID'].value_counts()
                df_location['battleCount'] = df_location['locationID'].map(
                    battle_counts).fillna(0)
                df_location['councilCount'] = df_location['locationID'].map(
                    council_counts).fillna(0)
                df_location['totalEvents'] = df_location['battleCount'] + \
                    df_location['councilCount']
                df_plot = df_location[df_location['totalEvents'] > 0].sort_values(
                    'totalEvents', ascending=False)  # Only plot locations with events

            if not df_plot.empty:
                fig10 = px.bar(df_plot, x='locationName', y='totalEvents',
                               title='Number of Major Events (Battles or Councils) per Location',
                               labels={'locationName': 'Location',
                                       'totalEvents': 'Number of Events'},
                               color_discrete_sequence=px.colors.qualitative.Pastel)
                fig10.update_layout(xaxis_title="Location",
                                    yaxis_title="Number of Major Events")
                # fig10.show()
                return fig10
            else:
                print("No locations with associated events found for Viz 10.")

        except Exception as e:
            print(f"Error generating Viz 10: {e}")
    else:
        print("Skipping Viz 10: Missing 'location', 'battle', or 'council' data.")


# --- Viz 11 (Analysis 5): Treemap - Regions & Locations by Population ---
def viz16():
    print("\nGenerating Viz 11: Treemap of Regions and Locations by Population")
    if 'location' in dfs and 'region' in dfs:
        try:
            df_location = dfs['location'].copy()
            df_region = dfs['region'].copy()

            # Merge location with region names
            df_loc_reg = pd.merge(df_location, df_region[[
                                  'regionID', 'regionName', 'localPopulation']], left_on='situated_In_RegionID', right_on='regionID', how='left')

            # Use location 'riskFactor' as a proxy for size if population not available/meaningful at location level
            # Or use region population? Let's use Region population for region size and location count for location size
            # Simple count for location box size
            df_loc_reg['location_count_for_size'] = 1
            df_loc_reg['regionPopulation'] = pd.to_numeric(
                df_loc_reg['localPopulation'], errors='coerce').fillna(1)  # Use region population for region size

            fig11 = px.treemap(df_loc_reg, path=[px.Constant("Middle-earth"), 'regionName', 'locationName'],  # Hierarchy
                               # values='location_count_for_size', # Size boxes by location count (or riskFactor?)
                               # color='regionPopulation', # Color boxes by region population (or riskFactor/aura?)
                               color_discrete_sequence=px.colors.qualitative.Pastel,  # Use pastel sequence
                               title='Treemap of Locations within Regions')
            # color_continuous_scale='Blues')
            fig11.update_traces(root_color="lightgrey")
            fig11.update_layout(margin=dict(t=50, l=25, r=25, b=25))
            # fig11.show()
            return fig11
        except Exception as e:
            print(f"Error generating Viz 11: {e}")
    else:
        print("Skipping Viz 11: Missing 'location' or 'region' data.")


# --- Viz 12 (Analysis 6): Network Graph - Character Interactions (Comprehensive Edges) ---
def viz17():
    print("\nGenerating Viz 12: Character Interaction Network (Comprehensive Edges)")
    if all(k in dfs for k in ['person', 'fellowship', 'battle', 'army', 'beast', 'council', 'location']):
        try:
            # --- Step 1: Identify Nodes (Characters & Key Beasts) ---
            # Use the expanded list, ensure names match data for successful ID lookup
            key_character_names = [
                "Frodo Baggins", "Samwise Gamgee", "Gandalf", "Aragorn II Elessar",
                "Legolas Greenleaf", "Gimli", "Boromir", "Meriadoc Brandybuck", "Peregrin Took",
                "Elrond", "Galadriel", "Saruman", "Sauron", "Gollum/Sméagol",
                "Théoden", "Éowyn", "Faramir", "Witch-king of Angmar"
                # Add "Éomer" if available in your person data
            ]
            key_beast_names = ["Shelob", "Durin's Bane (Balrog)"]

            nodes_to_add = []
            df_person = dfs['person'].copy()
            df_beast = dfs['beast'].copy()
            person_id_map = df_person.set_index(
                'personName')['personID'].to_dict()
            beast_id_map = df_beast.set_index('beastName')['beastID'].to_dict()
            person_data_map = df_person.set_index('personID').to_dict('index')

            print("Looking up node IDs...")
            missing_chars = []
            missing_beasts = []
            for name in key_character_names:
                pid = person_id_map.get(name)
                if pid:
                    nodes_to_add.append({'id': pid, 'name': name, 'type': 'Person', 'alignment': person_data_map.get(
                        pid, {}).get('alignment', 'Unknown')})
                else:
                    missing_chars.append(name)
            for name in key_beast_names:
                bid = beast_id_map.get(name)
                if bid:
                    # Assign alignment
                    nodes_to_add.append(
                        {'id': bid, 'name': name, 'type': 'Beast', 'alignment': 'Evil'})
                else:
                    missing_beasts.append(name)

            if missing_chars:
                print(
                    f"Warning: Characters not found and skipped: {missing_chars}")
            if missing_beasts:
                print(
                    f"Warning: Beasts not found and skipped: {missing_beasts}")

            # Set of IDs actually added
            node_ids_in_graph = {n['id'] for n in nodes_to_add}

            # --- Step 2: Define Edges Systematically ---
            print("Defining edges based on interactions...")
            edges_to_add = {}  # { (u,v): {'weight': W, 'types': set()} }

            def add_edge(u_name, v_name, type_label, weight=1):
                # Use names for lookup, then add edge using IDs
                u_id = person_id_map.get(u_name) or beast_id_map.get(u_name)
                v_id = person_id_map.get(v_name) or beast_id_map.get(v_name)

                if u_id and v_id and u_id in node_ids_in_graph and v_id in node_ids_in_graph:
                    u_node = min(u_id, v_id, key=str)
                    v_node = max(u_id, v_id, key=str)
                    edge = (u_node, v_node)
                    if edge[0] == edge[1]:
                        return
                    if edge not in edges_to_add:
                        edges_to_add[edge] = {'weight': 0, 'types': set()}
                    edges_to_add[edge]['weight'] += weight
                    edges_to_add[edge]['types'].add(type_label)
                # else: # Optional debug for skipped edges
                    # print(f"Skipping edge: {u_name} ({u_id}) - {v_name} ({v_id}). Reason: Node(s) missing.")

            # Helper to interconnect all pairs in a list of names
            def link_group(name_list, type_label, weight=1):
                for i in range(len(name_list)):
                    for j in range(i + 1, len(name_list)):
                        add_edge(name_list[i], name_list[j],
                                 type_label, weight)

            # 2.1: Fellowship (High Weight)
            fellowship_names = key_character_names[0:9]
            link_group(fellowship_names, 'Fellowship', weight=3)

            # 2.2: Council of Elrond
            council_participants = ["Frodo Baggins", "Gandalf", "Aragorn II Elessar",
                                    "Legolas Greenleaf", "Gimli", "Boromir", "Elrond"]
            link_group(council_participants, 'Council', weight=1)

            # 2.3: Battle Allies (Good Side)
            helms_deep_good = ["Aragorn II Elessar", "Legolas Greenleaf",
                               "Gimli", "Théoden", "Gandalf"]  # Add Eomer?
            pelennor_good = ["Aragorn II Elessar", "Legolas Greenleaf", "Gimli", "Théoden",
                             "Éowyn", "Meriadoc Brandybuck", "Gandalf", "Faramir", "Peregrin Took"]  # Add Eomer?
            morannon_good = ["Aragorn II Elessar", "Legolas Greenleaf",
                             "Gimli", "Peregrin Took", "Gandalf"]  # Add Eomer?
            link_group(helms_deep_good, 'Battle Ally (Helm\'s Deep)', weight=1)
            link_group(pelennor_good, 'Battle Ally (Pelennor)', weight=1)
            link_group(morannon_good, 'Battle Ally (Morannon)', weight=1)

            # 2.4: Journey Companions
            link_group(["Aragorn II Elessar", "Legolas Greenleaf",
                       "Gimli"], 'Travel Companion (3 Hunters)', weight=2)
            add_edge("Frodo Baggins", "Gollum/Sméagol",
                     'Guide/Conflict', weight=2)
            add_edge("Samwise Gamgee", "Gollum/Sméagol",
                     'Guide/Conflict', weight=1)

            # 2.5: Direct Conflicts (Higher weight for major ones)
            add_edge("Éowyn", "Witch-king of Angmar", 'Conflict', weight=2)
            add_edge("Meriadoc Brandybuck",
                     "Witch-king of Angmar", 'Conflict', weight=1)
            add_edge("Gandalf", "Witch-king of Angmar", 'Conflict', weight=1)
            add_edge("Gandalf", "Durin's Bane (Balrog)", 'Conflict', weight=3)
            add_edge("Samwise Gamgee", "Shelob", 'Conflict', weight=2)
            add_edge("Frodo Baggins", "Shelob", 'Conflict (Victim)', weight=1)
            add_edge("Frodo Baggins", "Gollum/Sméagol",
                     'Conflict (Mt Doom)', weight=2)

            # 2.6: Key Friendships/Alliances (Higher Weight)
            add_edge("Legolas Greenleaf", "Gimli", 'Friendship', weight=3)
            add_edge("Frodo Baggins", "Samwise Gamgee", 'Friendship', weight=4)
            add_edge("Gandalf", "Aragorn II Elessar",
                     'Alliance/Friendship', weight=2)
            add_edge("Gandalf", "Galadriel", 'Alliance/Wisdom',
                     weight=2)  # Added as requested
            add_edge("Gandalf", "Elrond", 'Alliance/Council', weight=1)
            add_edge("Galadriel", "Elrond", 'Kin/Alliance',
                     weight=1)  # Connected through Celebrian

            # 2.7: Healings
            add_edge("Aragorn II Elessar", "Éowyn", 'Healing', weight=1)
            add_edge("Aragorn II Elessar", "Faramir", 'Healing', weight=1)
            add_edge("Aragorn II Elessar",
                     "Meriadoc Brandybuck", 'Healing', weight=1)

            # 2.8: Kin/Ruler (Examples)
            add_edge("Théoden", "Éowyn", 'Kin/Allegiance', weight=1)
            add_edge("Elrond", "Aragorn II Elessar",
                     'Kin/Allegiance (Foster)', weight=1)
            add_edge("Boromir", "Faramir", 'Kin (Brother)',
                     weight=1)  # Assuming Faramir exists

            # 2.9: Antagonist Links
            add_edge("Saruman", "Sauron", 'Allegiance (Evil)', weight=2)
            add_edge("Witch-king of Angmar", "Sauron",
                     'Allegiance (Evil)', weight=3)

            # --- Step 3: Create Graph & Calculate Layout/Degrees ---
            print("Building graph and calculating layout...")
            G = nx.Graph()
            node_attributes = {n['id']: n for n in nodes_to_add}
            valid_node_ids = list(node_attributes.keys())

            for node_id in valid_node_ids:
                G.add_node(node_id, **node_attributes[node_id])

            edge_count = 0
            for (u, v), attrs in edges_to_add.items():
                if u in valid_node_ids and v in valid_node_ids:
                    G.add_edge(u, v, weight=attrs['weight'], types=', '.join(
                        sorted(list(attrs['types']))))
                    edge_count += 1
            print(
                f"Graph created with {G.number_of_nodes()} nodes and {edge_count} edges.")
            if G.number_of_nodes() == 0:
                raise ValueError("Graph has no nodes after processing.")

            degrees = dict(G.degree(weight='weight'))
            if not degrees:
                # Check if degrees calculation worked
                raise ValueError("Could not calculate node degrees.")

            min_degree = min(degrees.values())
            max_degree = max(degrees.values())
            if max_degree <= min_degree:
                max_degree = min_degree + 1
            base_node_size = 8
            max_additional_size = 30.0
            node_sizes = {node: max(base_node_size, base_node_size + (max_additional_size * (
                degrees.get(node, 0) - min_degree) / (max_degree - min_degree))) for node in G.nodes()}

            # Use default spring layout parameters first, ensure weight is used
            # Moderate k, high iterations
            pos = nx.spring_layout(
                G, k=0.1, iterations=3, weight='weight', seed=42)

            # --- Step 4: Create Plotly Traces ---
            print("Creating plot traces...")
            # Edges
            edge_x, edge_y, edge_hover_texts = [], [], []
            for edge in G.edges(data=True):
                if edge[0] in pos and edge[1] in pos:
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                    edge_types = edge[2].get('types', '?')
                    weight = edge[2].get('weight', 1)
                    edge_hover_texts.extend(
                        [f"Type(s): {edge_types}<br>Weight: {weight}"]*2 + [None])
            edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(
                width=1.0, color='rgba(140, 140, 140, 0.7)'), hoverinfo='text', hovertext=edge_hover_texts, mode='lines')

            # Nodes
            node_x, node_y, node_hover_text, node_color_list, node_size_list = [], [], [], [], []
            alignment_color_map = {
                'Good': px.colors.qualitative.Pastel[1], 'Evil': px.colors.qualitative.Pastel[3],
                'Neutral/Flawed': px.colors.qualitative.Pastel[4], 'Unknown': px.colors.qualitative.Pastel[5],
            }
            beast_color = px.colors.qualitative.Pastel[6]
            node_list = list(G.nodes())
            #
            # Look up Frodo's ID first
            frodo_id_lookup = person_id_map.get("Frodo Baggins")
            frodo_color = 'yellow'
            #
            # Look up Gandalf's ID
            gandalf_id_lookup = person_id_map.get("Gandalf")
            gandalf_color = 'green'
            #
            # Look up Sauron's ID
            sauron_id_lookup = person_id_map.get("Sauron")
            sauron_color = 'red'
            #
            for node in node_list:
                if node in pos:
                    x, y = pos[node]
                    node_x.append(x)
                    node_y.append(y)
                    node_info = G.nodes[node]
                    degree = degrees.get(node, 0)
                    hover_text = f"<b>{node_info.get('name', node)}</b><br>Type: {node_info.get('type', 'N/A')}<br>Connections (Weighted): {degree}<br>Alignment: {node_info.get('alignment', 'N/A')}"
                    node_hover_text.append(hover_text)
                    node_type = node_info.get('type')
                    if node_type == 'Beast':
                        node_color_list.append(beast_color)
                    # custom colors for nodes
                    elif node == frodo_id_lookup:
                        node_color_list.append(frodo_color)
                    elif node == gandalf_id_lookup:
                        node_color_list.append(gandalf_color)
                    elif node == sauron_id_lookup:
                        node_color_list.append(sauron_color)
                    else:
                        node_color_list.append(alignment_color_map.get(node_info.get(
                            'alignment', 'Unknown'), px.colors.qualitative.Pastel[5]))
                    if node == sauron_id_lookup:
                        # make sauron's node larger and more prominent
                        node_size_list.append(
                            node_sizes.get(node, base_node_size)*4)
                    else:
                        node_size_list.append(
                            node_sizes.get(node, base_node_size))
            node_trace = go.Scatter(x=node_x, y=node_y, mode='markers', hoverinfo='text', hovertext=node_hover_text, marker=dict(
                size=node_size_list, color=node_color_list, line_width=1.2, line_color='rgba(30, 30, 30, 0.9)'))

            # --- Step 5: Create Figure ---
            print("Rendering figure...")
            fig12_comprehensive = go.Figure(data=[edge_trace, node_trace],
                                            layout=go.Layout(
                title=dict(
                    text='Comprehensive Character Interaction Network', font=dict(size=16)),
                showlegend=False, hovermode='closest',
                margin=dict(b=10, l=10, r=10, t=40),
                xaxis=dict(
                    showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(
                    showgrid=False, zeroline=False, showticklabels=False),
                width=600,
                height=900,
                plot_bgcolor='rgba(248, 248, 248, 1)')
            )
            # fig12_comprehensive.show()
            return fig12_comprehensive

        except Exception as e:
            print(f"Error generating Comprehensive Viz 12: {e}")
            import traceback
            traceback.print_exc()  # Print detailed traceback for debugging
    else:
        print("Skipping Comprehensive Viz 12: Missing required dataframes.")


# --- Viz 14 (Analysis 8): Simplified Ring Journey Sequence Plot ---
def viz18():
    print("\nGenerating Viz 14: The One Ring's Journey")
    # Check if required dataframes exist
    if 'person' in dfs and 'ring' in dfs and 'council' in dfs and 'journey' in dfs and 'location' in dfs:
        try:
            df_person = dfs['person'].copy()
            df_ring = dfs['ring'].copy()

            # --- FIX: Look up required IDs from loaded data ---
            try:
                frodo_id = df_person.loc[df_person['personName']
                                         == 'Frodo Baggins', 'personID'].iloc[0]
                sam_id = df_person.loc[df_person['personName']
                                       == 'Samwise Gamgee', 'personID'].iloc[0]
                boromir_id = df_person.loc[df_person['personName']
                                           == 'Boromir', 'personID'].iloc[0]
                gollum_id = df_person.loc[df_person['personName']
                                          == 'Gollum/Sméagol', 'personID'].iloc[0]
                faramir_id = df_person.loc[df_person['personName']
                                           == 'Faramir', 'personID'].iloc[0]
                one_ring_id = df_ring.loc[df_ring['isOneRing']
                                          == True, 'ringID'].iloc[0]
                # Assume Event/Location IDs are known or look them up if needed
                council_elrond_id = "CNCL01"
                journey_fellowship_id = "JOU01"
                journey_frodo_sam_id = "JOU02"
                loc_amon_hen_id = dfs['location'].loc[dfs['location']['locationName']
                                                      == 'Amon Hen', 'locationID'].iloc[0]  # Example lookup
                loc_cirith_ungol_id = dfs['location'].loc[dfs['location']
                                                          ['locationName'] == 'Cirith Ungol', 'locationID'].iloc[0]
                loc_mount_doom_id = dfs['location'].loc[dfs['location']
                                                        ['locationName'] == 'Mount Doom (Orodruin)', 'locationID'].iloc[0]

            except (IndexError, KeyError) as e:
                print(
                    f"Error finding required IDs for Viz 14 in loaded data: {e}. Skipping plot.")
                # Set a flag or raise error to prevent plot generation
                raise e  # Re-raise to stop execution here if IDs are critical

            # Manually define sequence using looked-up IDs
            ring_journey_steps = [
                {'Step': 1, 'Label': 'Frodo Receives Ring',
                    'EntityID': frodo_id, 'Type': 'Person'},
                {'Step': 2, 'Label': 'Council of Elrond',
                    'EntityID': council_elrond_id, 'Type': 'Event'},
                {'Step': 3, 'Label': 'Journey South',
                    'EntityID': journey_fellowship_id, 'Type': 'Event'},
                {'Step': 4, 'Label': f'Boromir Tempted ({loc_amon_hen_id})',
                 'EntityID': boromir_id, 'Type': 'Person'},
                {'Step': 5, 'Label': 'Frodo & Sam Journey East',
                    'EntityID': journey_frodo_sam_id, 'Type': 'Event'},
                {'Step': 6, 'Label': 'Gollum Guides',
                    'EntityID': gollum_id, 'Type': 'Person'},
                {'Step': 7, 'Label': 'Captured by Faramir',
                    'EntityID': faramir_id, 'Type': 'Person'},
                {'Step': 8, 'Label': f'Cirith Ungol ({loc_cirith_ungol_id})',
                 'EntityID': loc_cirith_ungol_id, 'Type': 'Location'},
                {'Step': 9,
                    'Label': 'Sam Bears Ring (briefly)', 'EntityID': sam_id, 'Type': 'Person'},
                {'Step': 10, 'Label': f'Mount Doom ({loc_mount_doom_id})',
                 'EntityID': loc_mount_doom_id, 'Type': 'Location'},
                {'Step': 11, 'Label': 'Gollum Takes Ring',
                    'EntityID': gollum_id, 'Type': 'Person'},
                {'Step': 12, 'Label': 'Ring Destroyed',
                    'EntityID': one_ring_id, 'Type': 'Item Destroyed'},
            ]
            df_ring_journey = pd.DataFrame(ring_journey_steps)

            # --- Plotting  ---
            fig14 = go.Figure()
            fig14.add_trace(go.Scatter(
                x=df_ring_journey['Step'], y=[1] * len(df_ring_journey),
                mode='lines+markers+text',
                marker=dict(color=px.colors.qualitative.Pastel[2], size=12),
                line=dict(
                    color=px.colors.qualitative.Pastel[3], width=1, dash='dot'),
                text=df_ring_journey['Label'],
                textposition="top center",
                hovertext=df_ring_journey['Type'] +
                ': ' + df_ring_journey['EntityID'],
                name='Ring Journey'
            ))
            fig14.update_layout(
                title="Conceptual Journey of the One Ring (Key Moments and Bearers)",
                xaxis_title="Sequence Step",
                yaxis=dict(showticklabels=False, showgrid=False,
                           zeroline=False, range=[0.5, 1.5]),
                xaxis=dict(tickvals=df_ring_journey['Step']),
                showlegend=False
            )
            # fig14.show()
            return fig14

        except Exception as e:
            print(f"Error generating Viz 14: {e}")
    else:
        print("Skipping Viz 14: Missing required dataframes (person, ring, council, etc.).")


# --- Viz 15 (Analysis 8): Network Graph - Palantír Connections ---
def viz19():
    print("\nGenerating Viz 15: Palantír User Network (Orthanc Stone)")
    # Check if required dataframes exist
    if 'palantir' in dfs and 'person' in dfs and 'artifact' in dfs:
        try:
            df_palantir = dfs['palantir'].copy()
            df_person = dfs['person'].copy()
            # Need artifact table for name
            df_artifact = dfs['artifact'].copy()

            # --- look up IDs and Palantir Name ---
            try:
                # Look up person IDs
                saruman_id = df_person.loc[df_person['personName']
                                           == 'Saruman', 'personID'].iloc[0]
                pippin_id = df_person.loc[df_person['personName']
                                          == 'Peregrin Took', 'personID'].iloc[0]
                aragorn_id = df_person.loc[df_person['personName']
                                           == 'Aragorn II Elessar', 'personID'].iloc[0]
                sauron_id = df_person.loc[df_person['personName']
                                          == 'Sauron', 'personID'].iloc[0]

                # Look up Palantir info and its name via the linked Artifact entry
                palantir_id = "PAL01"  # Assume Orthanc stone ID is PAL01
                palantir_info = df_palantir[df_palantir['palantirID']
                                            == palantir_id]
                palantir_name = palantir_id  # Default name

                if not palantir_info.empty:
                    linked_artifact_id = palantir_info.iloc[0].get(
                        'artifactID')  # Get linked artifact ID
                    if linked_artifact_id:
                        artifact_info = df_artifact[df_artifact['artifactID']
                                                    == linked_artifact_id]
                        if not artifact_info.empty:
                            # Get name from the artifact table
                            palantir_name = artifact_info.iloc[0].get(
                                'artifactName', palantir_id)

            except (IndexError, KeyError) as e:
                print(
                    f"Error finding required IDs/Names for Viz 15 in loaded data: {e}. Skipping plot.")
                # Use raise e if you want execution to stop
                # If you want to continue, ensure entities list below handles potential missing IDs
                raise e  # Reraising to prevent further errors if IDs missing

            # Define entities and build graph using looked-up names/IDs
            users = [saruman_id, pippin_id, aragorn_id]
            entities = [palantir_id] + users + [sauron_id]
            entity_map = df_person.set_index(
                'personID')['personName'].to_dict()
            # Use the correctly looked-up name
            entity_map[palantir_id] = palantir_name

            edges = []
            # Link users to the Palantir
            for user_id in users:
                edges.append((user_id, palantir_id))
            # Link Palantir users to Sauron (implied communication)
            for user_id in users:
                edges.append((user_id, sauron_id))

            G_palantir = nx.Graph()
            valid_entities = []  # Keep track of entities actually found and added
            for node_id in entities:
                if node_id in entity_map:  # Check if ID exists in loaded data map
                    G_palantir.add_node(
                        node_id, name=entity_map.get(node_id, node_id))
                    valid_entities.append(node_id)
                else:
                    print(
                        f"Warning: Node ID {node_id} not found in entity map for Viz 15.")

            # Only add edges where both nodes are valid
            valid_edges = [
                (u, v) for u, v in edges if u in valid_entities and v in valid_entities]
            G_palantir.add_edges_from(valid_edges)

            # --- Plotting (using corrected entity_map and only valid nodes/edges) ---
            if G_palantir.number_of_nodes() > 0:  # Proceed only if graph has nodes
                pos = nx.forceatlas2_layout(
                    G_palantir, strong_gravity=True)  # Layout requires nodes

                edge_x, edge_y = [], []
                for edge in G_palantir.edges():
                    # Ensure pos exists for both nodes (should if they are in G_palantir.nodes)
                    if edge[0] in pos and edge[1] in pos:
                        x0, y0 = pos[edge[0]]
                        x1, y1 = pos[edge[1]]
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])

                node_x, node_y, node_text, node_color = [], [], [], []
                colors = px.colors.qualitative.Pastel
                # Get list of nodes actually in the graph
                node_list = list(G_palantir.nodes())
                for i, node in enumerate(node_list):
                    if node in pos:  # Ensure node has a position
                        x, y = pos[node]
                        node_x.append(x)
                        node_y.append(y)
                        node_text.append(
                            G_palantir.nodes[node].get('name', node))
                        node_color.append(colors[i % len(colors)])

                edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(
                    width=1, color='#AAA'), hoverinfo='none', mode='lines')
                node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text', hoverinfo='text', text=node_text,
                                        textposition="bottom center", marker=dict(size=15, color=node_color, line_width=1))

                fig15 = go.Figure(data=[edge_trace, node_trace],
                                  layout=go.Layout(
                    # Using corrected title format
                    title=dict(
                        text='Palantír User Network (Orthanc Stone & Sauron)', font=dict(size=16)),
                    showlegend=False, hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    width=800,
                    height=900,
                    xaxis=dict(
                        showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
                # fig15.show()
                return fig15
            else:
                print(
                    "Could not generate graph for Viz 15 - no valid nodes found after lookup.")

        except Exception as e:
            print(f"Error generating Viz 15: {e}")
    else:
        print("Skipping Viz 15: Missing 'palantir', 'person', or 'artifact' data.")


# --- Viz 16 (Analysis 9): Radar Chart - Race Skills ---
# look what a little rest and clarity of thought can do...
# just build df_skills intead of the ugly joining nonsense that was going on in the previous method
# keeping it as viz20_stupid() - so there's a lesson to be learned.
def viz20():
    print("\nGenerating Viz 16: Representative Skills by Race (Radar Chart)")
    # 1) Ensure all necessary dataframes are present
    required = ['person', 'race', 'hobbit', 'elf', 'dwarf', 'man', 'wizard']
    if all(k in dfs for k in required):
        try:
            # 2) Copy the base person and race data to avoid side-effects
            df_person = dfs['person'].copy()
            df_race = dfs['race'].copy()

            # 3) Define the skill columns we want to plot
            skills = ['stealthSkill', 'bowSkill', 'miningSkill',
                      'swordSkill', 'staffPowerLevel']

            # 4) Concatenate all subclass tables to one table of personID + all skills
            df_skills = pd.concat(
                [dfs['hobbit'], dfs['elf'], dfs['dwarf'], dfs['man'], dfs['wizard']],
                ignore_index=True
            )[['personID'] + skills]

            # 5) If a person appears multiple times across subclasses, take the first record
            df_skills = df_skills.groupby('personID', as_index=False)[
                skills].first()

            # 6) Merge the skills table back onto the person table (left join)
            df_person = pd.merge(
                df_person,
                df_skills,
                on='personID',
                how='left'
            )

            # 7) Merge in race names (joining on the raceID foreign key)
            df_person = pd.merge(
                df_person,
                df_race[['raceID', 'raceName']],
                left_on='belongs_To_RaceID',
                right_on='raceID',
                how='left'
            )

            # 8) Fill missing skill values (people without a given subclass) with 0
            df_person[skills] = df_person[skills].fillna(0)

            # 9) Compute the average of each skill per race
            race_avg_skills = (
                df_person
                .groupby('raceName')[skills]
                .mean()
                .reset_index()
            )

            # 10) Filter to only the races we're interested in
            races_to_show = ['Hobbit', 'Elf', 'Dwarf', 'Man', 'Wizard']
            race_avg_skills = race_avg_skills[
                race_avg_skills['raceName'].isin(races_to_show)
            ]

            # 11) Rename columns for clearer plot labels
            skill_rename = {
                'stealthSkill':    'Stealth',
                'bowSkill':        'Archery',
                'miningSkill':     'Mining/Craft',
                'swordSkill':      'Melee (Sword)',
                'staffPowerLevel': 'Magic/Staff'
            }
            race_avg_skills = race_avg_skills.rename(columns=skill_rename)
            categories = list(skill_rename.values())

            # 12) Initialize the radar chart figure
            fig16 = go.Figure()
            fig16 = go.Figure()
            # colors = px.colors.qualitative.Pastel
            # colors = px.colors.qualitative.Safe
            # colors = px.colors.qualitative.G10
            colors = px.colors.qualitative.Bold  # High-contrast palette

            # 13) Add one trace per race, with fill, opacity, and a bold outline
            for i, row in race_avg_skills.iterrows():
                values = row[categories].tolist()
                # Close the loop by appending the first value/category again
                r = values + [values[0]]
                theta = categories + [categories[0]]
                color = colors[i % len(colors)]

                fig16.add_trace(go.Scatterpolar(
                    r=r,
                    theta=theta,
                    fill='toself',
                    fillcolor=color,
                    marker_color=color,
                    opacity=0.6,
                    # Outline around each filled area
                    line=dict(color=color, width=2),
                    name=row['raceName']
                ))

            # 14) Final layout settings: axis range, legend, size, and title
            fig16.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 10])
                ),
                showlegend=True,
                width=800,
                height=1040,
                title="Representative Skills by Race (Averages)"
            )

            return fig16

        except Exception as e:
            print(f"Error generating Viz 16: {e}")
    else:
        print("Skipping Viz 16: Missing required person/race/subclass data.")


# BROKEN...DO NOT USE --- Viz 16 (Analysis 9): Radar Chart - Race Skills
def viz20_stupid():
    print("\nGenerating Viz 16: Representative Skills by Race (Radar Chart)")
    # NOTE: This requires aggregating skill data which might be sparse or require assumptions
    if all(k in dfs for k in ['person', 'race', 'hobbit', 'elf', 'dwarf', 'man', 'wizard']):
        try:
            df_person = dfs['person'].copy()
            df_race = dfs['race'].copy()
            # Merge all relevant subclass skill dataframes with person, then with race
            df_person = pd.merge(df_person, dfs['hobbit'][[
                                 'personID', 'stealthSkill']], on='personID', how='left')
            df_person = pd.merge(
                df_person, dfs['elf'][['personID', 'bowSkill']], on='personID', how='left')
            df_person = pd.merge(
                df_person, dfs['dwarf'][['personID', 'miningSkill']], on='personID', how='left')
            df_person = pd.merge(
                df_person, dfs['man'][['personID', 'swordSkill']], on='personID', how='left')
            df_person = pd.merge(df_person, dfs['wizard'][[
                                 'personID', 'staffPowerLevel']], on='personID', how='left')
            df_person = pd.merge(df_person, df_race[[
                                 'raceID', 'raceName']], left_on='belongs_To_RaceID', right_on='raceID', how='left')

            print("data = ", df_person)

            # Define skills to plot and fill NaNs
            skills = ['stealthSkill', 'bowSkill',
                      'miningSkill', 'swordSkill', 'staffPowerLevel']
            # Fill missing skills with 0 for averaging
            df_person[skills] = df_person[skills].fillna(0)

            # Calculate average skills per race (only races with characters in our data)
            race_avg_skills = df_person.groupby(
                'raceName')[skills].mean().reset_index()
            # Filter for races we expect skills for
            races_to_show = ['Hobbit', 'Elf', 'Dwarf', 'Man',
                             'Wizard']  # Wizard represents Maiar here
            race_avg_skills = race_avg_skills[race_avg_skills['raceName'].isin(
                races_to_show)]

            # Rename skills for clarity
            skill_rename = {'stealthSkill': 'Stealth', 'bowSkill': 'Archery', 'miningSkill': 'Mining/Craft',
                            'swordSkill': 'Melee (Sword)', 'staffPowerLevel': 'Magic/Staff'}
            race_avg_skills = race_avg_skills.rename(columns=skill_rename)
            categories = list(skill_rename.values())

            fig16 = go.Figure()
            colors = px.colors.qualitative.Pastel

            for i, row in race_avg_skills.iterrows():
                # TODO: improve data to ensure everyone has well rounded skills.
                # updated man.json, hobbit.json, elf.json, dwarf.json and wizard.json but shit's not sticking...
                print("row racename = ", row['raceName'])
                print("scatterPolar r = ", row[categories].values.tolist(
                ) + [row[categories].values[0]])
                print("scatterPolar theta=", categories + [categories[0]])
                fig16.add_trace(go.Scatterpolar(
                    r=row[categories].values.tolist(
                    ) + [row[categories].values[0]],  # Close the loop
                    theta=categories + [categories[0]],  # Close the loop
                    fill='tonext',
                    name=row['raceName'],
                    # Cycle through pastel colors
                    marker_color=colors[i % len(colors)]
                ))

            fig16.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]  # Assuming skills are roughly 0-10 scale
                    )),
                showlegend=True,
                width=800,
                height=1040,
                title="Representative Skills by Race (Averages)"
            )
            # fig16.show()
            return fig16

        except Exception as e:
            print(f"Error generating Viz 16: {e}")
    else:
        print("Skipping Viz 16: Missing required person/race/subclass data.")


# --- Viz 17 (Analysis 9): Heatmap - Race vs. Event Type Participation ---
def viz21():
    # --- Viz 17 (Analysis 9): Heatmap - Race vs. Event Type Participation ---
    print("\nGenerating Viz 17: Race Participation in Event Types (Heatmap)")
    # Erm...DRY - Don't repeat yourself...
    # but, you know what?
    # I'll fix it later...
    df_battle = dfs['battle'].copy()
    df_army = dfs['army'].copy()
    df_person = dfs['person'].copy()
    fellowship_names = KEY_CHARACTER_NAMES[0:9]

    #
    if 'person' in dfs and 'race' in dfs and 'battle' in dfs and 'council' in dfs and 'fellowship' in dfs:
        try:
            df_person = dfs['person'].copy()
            df_race = dfs['race'].copy()
            df_battle = dfs['battle'].copy()
            df_council = dfs['council'].copy()
            df_fellowship = dfs['fellowship'].copy()
            # Note: Need a way to link people to events more systematically for accurate counts
            # Using the 'events_participated' list is descriptive but hard to parse reliably
            # Simplified approach: Count based on known participants listed earlier

            # Example: Count Fellowship members by race
            fellowship_ids = df_person[df_person['personName'].isin(
                fellowship_names)]['personID'].tolist()  # Use known names
            fellowship_participants = df_person[df_person['personID'].isin(
                fellowship_ids)].copy()
            fellowship_participants = pd.merge(fellowship_participants, df_race[[
                                               'raceID', 'raceName']], left_on='belongs_To_RaceID', right_on='raceID')
            fellowship_counts = fellowship_participants.groupby(
                'raceName').size().reset_index(name='Fellowship')

            # Example: Count Council attendees (if data available)
            # council_attendees = df_person[df_person['attended_council_id'] == 'CNCL01'] # Needs link
            # council_counts = ... (similar grouping)

            # Example: Count Battle Commanders by race
            commanders_ids = df_army['commanderID'].dropna().unique().tolist()
            battle_commanders = df_person[df_person['personID'].isin(
                commanders_ids)].copy()
            battle_commanders = pd.merge(battle_commanders, df_race[[
                                         'raceID', 'raceName']], left_on='belongs_To_RaceID', right_on='raceID')
            battle_counts = battle_commanders.groupby(
                'raceName').size().reset_index(name='Battle Command')

            # Combine counts (example with Fellowship and Battle Command)
            df_heatmap = pd.merge(
                fellowship_counts, battle_counts, on='raceName', how='outer').fillna(0)
            df_heatmap = df_heatmap.set_index('raceName')

            if not df_heatmap.empty:
                fig17 = px.imshow(df_heatmap,
                                  labels=dict(x="Event Type", y="Race",
                                              color="Participation Count"),
                                  x=['Fellowship', 'Battle Command'],
                                  y=df_heatmap.index,
                                  text_auto=True,  # Show counts on cells
                                  color_continuous_scale=px.colors.sequential.PuBu,
                                  title="Race Participation Count in Key Event Types")
                fig17.update_layout(
                    width=800,
                    height=1040
                )
                # fig17.show()
                return fig17
            else:
                print("Could not generate sufficient data for Viz 17 heatmap.")

        except Exception as e:
            print(f"Error generating Viz 17: {e}")
    else:
        print("Skipping Viz 17: Missing required data.")


# --- Viz 18 (Analysis 11): Bar Chart - Army Sizes ---
def viz22():
    print("\nGenerating Viz 18: Comparison of Major Army Sizes")
    if 'army' in dfs:
        try:
            df_army = dfs['army'].copy()
            # Ensure totalUnits is numeric
            df_army['totalUnits'] = pd.to_numeric(
                df_army['totalUnits'], errors='coerce')
            df_army_plot = df_army.dropna(subset=['totalUnits']).sort_values(
                'totalUnits', ascending=False)

            fig18 = px.bar(df_army_plot, x='armyName', y='totalUnits',
                           title='Estimated Sizes of Major Armies',
                           labels={'armyName': 'Army',
                                   'totalUnits': 'Estimated Total Units'},
                           color='armyName',  # Color by army
                           color_discrete_sequence=px.colors.qualitative.Pastel)
            fig18.update_layout(xaxis_title="Army",
                                yaxis_title="Estimated Total Units")
            # fig18.show()
            return fig18
        except Exception as e:
            print(f"Error generating Viz 18: {e}")
    else:
        print("Skipping Viz 18: Missing 'army' data.")


# --- Viz 19 (Analysis 10): Treemap - Kingdom/Army/Commander ---
def viz23():
    print("\nGenerating Viz 19: Kingdom-Army-Commander Hierarchy (Treemap)")
    if 'kingdom' in dfs and 'army' in dfs and 'person' in dfs:
        try:
            df_kingdom = dfs['kingdom'].copy()
            df_army = dfs['army'].copy()
            df_person = dfs['person'].copy()

            # Find kingdom for each army (this link needs to be established - assuming army name implies kingdom for simplicity)
            def get_kingdom_for_army(army_name):
                if 'Gondor' in army_name:
                    return 'Gondor'
                if 'Rohirrim' in army_name or 'Rohan' in army_name:
                    return 'Rohan'
                if 'Mordor' in army_name:
                    return 'Mordor'
                if 'Isengard' in army_name:
                    return 'Isengard'
                if 'Dead' in army_name:
                    return 'Oathbreakers'  # Conceptual kingdom
                return 'Unknown'
            df_army['kingdomName'] = df_army['armyName'].apply(
                get_kingdom_for_army)

            # Merge commander names
            commander_names = df_person.set_index(
                'personID')['personName'].to_dict()
            df_army['commanderName'] = df_army['commanderID'].map(
                commander_names).fillna('Unknown Commander')

            # Ensure totalUnits is numeric for value
            df_army['totalUnits'] = pd.to_numeric(
                df_army['totalUnits'], errors='coerce').fillna(1)

            fig19 = px.treemap(df_army, path=[px.Constant("All Armies"), 'kingdomName', 'armyName', 'commanderName'],
                               values='totalUnits',  # Size boxes by army size
                               color='kingdomName',  # Color by kingdom
                               color_discrete_sequence=px.colors.qualitative.Pastel,
                               title='Hierarchy of Kingdoms, Armies, and Commanders (Sized by Army Units)')
            fig19.update_traces(root_color="lightgrey")
            fig19.update_layout(margin=dict(t=50, l=25, r=25, b=25))
            # fig19.show()
            return fig19

        except Exception as e:
            print(f"Error generating Viz 19: {e}")
    else:
        print("Skipping Viz 19: Missing required data (kingdom, army, person).")


# --- Viz 13 (Analysis 7): Stacked Bar Chart - Alignment in Battles ---
def viz24():
    print("\nGenerating Viz 13: Alignment Balance in Major Battles")
    if 'battle' in dfs and 'army' in dfs and 'person' in dfs:
        try:
            df_battle = dfs['battle'].copy()
            df_army = dfs['army'].copy()
            df_person = dfs['person'].copy()

            # Map commander ID to person's alignment
            commander_alignment = df_person.set_index(
                'personID')['alignment'].to_dict()
            df_army['commanderAlignment'] = df_army['commanderID'].map(
                commander_alignment).fillna('Unknown')

            battle_alignment_data = []
            major_battle_ids = ["BAT01", "BAT02", "BAT03"]

            for battle_id in major_battle_ids:
                battle_info = df_battle[df_battle['battleID'] == battle_id]
                if not battle_info.empty:
                    battle_name = battle_info.iloc[0]['battleName']
                    involved_army_ids = battle_info.iloc[0].get(
                        'armiesInvolvedIDs', [])
                    if involved_army_ids and isinstance(involved_army_ids, list):
                        participating_armies = df_army[df_army['armyID'].isin(
                            involved_army_ids)].copy()
                        # Ensure totalUnits is numeric
                        participating_armies['totalUnits'] = pd.to_numeric(
                            participating_armies['totalUnits'], errors='coerce').fillna(0)
                        # Group by alignment and sum units
                        alignment_sum = participating_armies.groupby('commanderAlignment')[
                            'totalUnits'].sum().reset_index()
                        for _, row in alignment_sum.iterrows():
                            battle_alignment_data.append({
                                'Battle': battle_name,
                                'Alignment': row['commanderAlignment'],
                                'Strength': row['totalUnits']
                            })

            if battle_alignment_data:
                df_plot_align = pd.DataFrame(battle_alignment_data)
                fig13 = px.bar(df_plot_align, x='Battle', y='Strength', color='Alignment',
                               title='Alignment Strength (Army Units) in Major Battles',
                               labels={'Strength': 'Estimated Army Units'},
                               color_discrete_map={  # Map specific alignments to colors
                                   'Good': px.colors.qualitative.Pastel[1],
                                   'Evil': px.colors.qualitative.Pastel[3],
                                   'Neutral/Flawed': px.colors.qualitative.Pastel[4],
                                   'Unknown': px.colors.qualitative.Pastel[5]
                               },
                               barmode='stack')
                fig13.update_layout(xaxis_title="Battle",
                                    yaxis_title="Estimated Army Units")
                # fig13.show()
                return fig13
            else:
                print("Could not process alignment data for battles.")

        except Exception as e:
            print(f"Error generating Viz 13: {e}")
    else:
        print("Skipping Viz 13: Missing required data (battle, army, person).")
