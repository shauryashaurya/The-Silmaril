import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from collections import Counter, defaultdict
from plotly.subplots import make_subplots

# Load the data
with open('./data/star_wars_trilogy.json', 'r') as file:
    data = json.load(file)

# For easier reference
characters = data['characters']
jedis = data['jedis']
siths = data['siths']
droids = data.get('droids', {})
planets = data['planets']
spaceships = data['spaceships']
events = data['events']
battles = data['battles']
relationships = data['relationships']
timelines = data['timelines']

# 1. Timeline Visualization: Events across the trilogy - not fun enough, removed.


def timeline_visualization():
    """Create a timeline of events across the original trilogy."""
    # Extract events from timelines
    ep4_events = [(event['timestamp'], event['description'], 'Episode IV')
                  for event in timelines['episode_4']]
    ep5_events = [(event['timestamp'], event['description'], 'Episode V')
                  for event in timelines['episode_5']]
    ep6_events = [(event['timestamp'], event['description'], 'Episode VI')
                  for event in timelines['episode_6']]

    # Combine all events
    all_events = ep4_events + ep5_events + ep6_events

    # Convert to DataFrame
    event_df = pd.DataFrame(all_events, columns=[
                            'Timestamp', 'Description', 'Episode'])

    # Map timestamps to numerical values for plotting
    time_mapping = {'0 BBY': 0, '3 ABY': 3, '4 ABY': 4}
    event_df['TimeValue'] = event_df['Timestamp'].map(time_mapping)

    # Sort by time
    event_df = event_df.sort_values('TimeValue')

    # Create the figure
    fig = px.scatter(event_df, x='TimeValue', y='Episode', color='Episode',
                     hover_data=['Description'], size_max=10,
                     labels={
                         'TimeValue': 'Timeline (BBY/ABY)', 'Episode': 'Movie'},
                     title='Star Wars Original Trilogy Timeline')

    # Add lines connecting events in each episode
    for episode in event_df['Episode'].unique():
        episode_data = event_df[event_df['Episode'] == episode]
        fig.add_trace(go.Scatter(
            x=episode_data['TimeValue'],
            y=episode_data['Episode'],
            mode='lines',
            line=dict(width=1),
            showlegend=False
        ))

    # Customize layout
    fig.update_layout(
        xaxis=dict(
            tickvals=list(time_mapping.values()),
            ticktext=list(time_mapping.keys())
        ),
        height=600,
        width=1000
    )

    return fig

# 2. Character Interaction Network


def character_interaction_network():
    """Visualize which characters interact with each other the most."""
    # Extract character interactions from events
    interactions = []
    for episode_key, episode_events in timelines.items():
        for event in episode_events:
            if 'participants' in event and len(event['participants']) > 1:
                # Get all pairs of participants
                participants = event['participants']
                pairs = [(participants[i], participants[j])
                         for i in range(len(participants))
                         for j in range(i+1, len(participants))]
                interactions.extend(pairs)

    # Count interactions
    interaction_count = Counter(interactions)

    # Get character names
    char_names = {}
    for char_id, char in characters.items():
        char_names[char_id] = char['name']
    for droid_id, droid in droids.items():
        char_names[droid_id] = droid['name']

    # Create a NetworkX graph
    G = nx.Graph()

    # Add nodes (characters)
    for char_id, name in char_names.items():
        # Add main characters and those with interactions
        if char_id in [pair[0] for pair in interaction_count] or char_id in [pair[1] for pair in interaction_count]:
            G.add_node(char_id, name=name)

    # Add edges (interactions)
    for (char1, char2), count in interaction_count.items():
        if char1 in G.nodes and char2 in G.nodes:
            G.add_edge(char1, char2, weight=count)

    # Calculate positions using a spring layout
    pos = nx.spring_layout(G, seed=42)

    # Create edge trace
    edge_x = []
    edge_y = []
    edge_weights = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        weight = G.edges[edge]['weight']
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_weights.append(weight)

    # Scale edge widths
    edge_widths = [np.log2(w+1)*1.5 for w in edge_weights]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    node_size = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(
            f"{char_names[node]}: {len(list(G.neighbors(node)))} connections")
        node_size.append(len(list(G.neighbors(node)))*5 +
                         10)  # Size based on connections

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        text=node_text,
        mode='markers+text',
        hoverinfo='text',
        textposition="top center",
        textfont=dict(size=10),
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=[len(list(G.neighbors(node))) for node in G.nodes()],
            size=node_size,
            colorbar=dict(
                thickness=15,
                title='Number of Connections',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=2)))

    # Create the figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                    title='Character Interaction Network in Star Wars Trilogy',
                    titlefont=dict(size=16),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False,
                               showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False,
                               showticklabels=False),
                    width=2600,
                    height=1200))

    return fig

# 3. Location Frequency Analysis


def location_frequency():
    """Visualize the most frequently featured locations across episodes."""
    # Extract locations from events
    location_counts = defaultdict(lambda: defaultdict(int))

    for episode_key, episode_events in timelines.items():
        episode_name = f"Episode {episode_key.replace('episode_', '')}"
        for event in episode_events:
            if 'location' in event:
                location_id = event['location']
                # Check if it's a planet or a ship
                if location_id in planets:
                    location_name = planets[location_id]['planetName']
                elif location_id in spaceships:
                    location_name = spaceships[location_id]['uniqueName']
                else:
                    location_name = 'Unknown'
                location_counts[location_name][episode_name] += 1

    # Convert to DataFrame
    location_data = []
    for location, episodes in location_counts.items():
        for episode, count in episodes.items():
            location_data.append({
                'Location': location,
                'Episode': episode,
                'Count': count
            })

    # Get top locations
    location_df = pd.DataFrame(location_data)
    top_locations = location_df.groupby(
        'Location')['Count'].sum().nlargest(10).index
    location_df = location_df[location_df['Location'].isin(top_locations)]

    # Create the figure
    fig = px.bar(location_df, x='Location', y='Count', color='Episode',
                 title='Top 10 Most Frequently Featured Locations by Episode')

    fig.update_layout(xaxis_title='Location', yaxis_title='Number of Events',
                      legend_title='Episode', height=600, width=1000)

    return fig

# 4. Character Appearances by Episode


def character_appearances():
    """Visualize the count of appearances for main characters across episodes."""
    # Count character appearances in events
    character_appearances = defaultdict(lambda: defaultdict(int))
    for episode_key, episode_events in timelines.items():
        episode_num = episode_key.replace(
            'episode_', '')  # Extract episode number
        for event in episode_events:
            if 'participants' in event:
                for char_id in event['participants']:
                    if char_id in characters:
                        char_name = characters[char_id]['name']
                    elif char_id in droids:
                        char_name = droids[char_id]['name']
                    else:
                        char_name = 'Unknown'
                    character_appearances[char_name][episode_num] += 1

    # Convert to DataFrame
    appearance_data = []
    for char_name, episodes in character_appearances.items():
        for episode, count in episodes.items():
            appearance_data.append({
                'Character': char_name,
                'Episode': f'Episode {episode}',
                'Appearances': count
            })

    appearance_df = pd.DataFrame(appearance_data)

    # Get top characters
    top_chars = appearance_df.groupby(
        'Character')['Appearances'].sum().nlargest(10).index

    # Filter for top characters
    appearance_df = appearance_df[appearance_df['Character'].isin(top_chars)]

    # Create the figure
    fig = px.bar(appearance_df, x='Character', y='Appearances', color='Episode',
                 barmode='group', title='Top 10 Character Appearances by Episode')

    fig.update_layout(xaxis_title='Character', yaxis_title='Number of Appearances',
                      legend_title='Episode', height=600, width=1000)

    return fig

# 5. Event Significance Levels


def event_significance():
    """Visualize the distribution of event significance levels by episode."""
    # Extract event significance levels
    significance_counts = defaultdict(lambda: defaultdict(int))
    for episode_key, episode_events in timelines.items():
        episode_name = f"Episode {episode_key.replace('episode_', '')}"
        for event in episode_events:
            if 'significanceLevel' in event:
                significance_counts[episode_name][event['significanceLevel']] += 1

    # Convert to DataFrame
    significance_data = []
    for episode, levels in significance_counts.items():
        for level, count in levels.items():
            significance_data.append({
                'Episode': episode,
                'Significance': level,
                'Count': count
            })

    significance_df = pd.DataFrame(significance_data)

    # Ensure consistent ordering of significance levels
    significance_order = ['Low', 'Medium', 'High', 'Galactic']
    significance_df['Significance'] = pd.Categorical(
        significance_df['Significance'],
        categories=significance_order,
        ordered=True
    )
    significance_df = significance_df.sort_values(['Episode', 'Significance'])

    # Create the figure
    fig = px.bar(significance_df, x='Episode', y='Count', color='Significance',
                 category_orders={"Significance": significance_order},
                 title='Event Significance Levels by Episode',
                 color_discrete_map={
                     'Low': 'lightblue',
                     'Medium': 'royalblue',
                     'High': 'darkblue',
                     'Galactic': 'purple'
                 })

    fig.update_layout(xaxis_title='Episode', yaxis_title='Number of Events',
                      legend_title='Significance Level', height=600, width=1000)

    return fig

# 6. Memorable Quotes Analysis


def quote_analysis():
    """Analyze characters with the most memorable quotes."""
    # Extract quotes from events
    quotes = []
    for episode_key, episode_events in timelines.items():
        episode_name = f"Episode {episode_key.replace('episode_', '')}"
        for event in episode_events:
            if 'quote' in event:
                # Find the character who said the quote (using first participant as an approximation)
                speaker = 'Unknown'
                if 'participants' in event and len(event['participants']) > 0:
                    speaker_id = event['participants'][0]
                    if speaker_id in characters:
                        speaker = characters[speaker_id]['name']
                    elif speaker_id in droids:
                        speaker = droids[speaker_id]['name']

                quotes.append({
                    'Episode': episode_name,
                    'Speaker': speaker,
                    'Quote': event['quote']
                })

    # Convert to DataFrame
    quotes_df = pd.DataFrame(quotes)

    # Create a subplot with quote count and table
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.6, 0.4],
        specs=[[{"type": "bar"}], [{"type": "table"}]],
        vertical_spacing=0.05,
        subplot_titles=("Characters with Most Memorable Quotes",
                        "Top Memorable Quotes")
    )

    # Count quotes by character
    quote_counts = quotes_df.groupby(
        'Speaker').size().reset_index(name='Quote Count')
    quote_counts = quote_counts.sort_values(
        'Quote Count', ascending=False).head(10)

    # Add bar chart
    fig.add_trace(
        go.Bar(
            x=quote_counts['Speaker'],
            y=quote_counts['Quote Count'],
            marker_color='royalblue'
        ),
        row=1, col=1
    )

    # Get most memorable quotes for table
    top_quotes = quotes_df.sample(n=min(5, len(quotes_df))) if len(
        quotes_df) > 0 else pd.DataFrame()

    # Add table
    if not top_quotes.empty:
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Speaker', 'Quote', 'Episode'],
                    fill_color='paleturquoise',
                    align='left'
                ),
                cells=dict(
                    values=[
                        top_quotes['Speaker'],
                        top_quotes['Quote'],
                        top_quotes['Episode']
                    ],
                    fill_color='lavender',
                    align='left'
                )
            ),
            row=2, col=1
        )

    fig.update_layout(
        title='Memorable Quotes in Star Wars Trilogy',
        height=800,
        width=1000,
        showlegend=False
    )

    return fig

# 7. Battle Analysis


def battle_analysis():
    """Visualize battle casualties and outcomes."""
    # Extract battle casualties
    battle_casualties = []
    for battle_id, battle in battles.items():
        battle_casualties.append({
            'Battle': battle['name'],
            'Outcome': battle['outcome'],
            'Casualties': battle['casualties']
        })

    # Convert to DataFrame
    battle_df = pd.DataFrame(battle_casualties)

    # Make Rebels vs Empire clearer with colors
    colors = {
        'Rebel Alliance Victory': 'blue',
        'Empire Victory': 'red',
        'Stalemate': 'gray',
        'Inconclusive': 'lightgray'
    }

    battle_df = battle_df.sort_values('Casualties', ascending=False)

    # Create the figure
    fig = px.bar(battle_df, x='Battle', y='Casualties', color='Outcome',
                 color_discrete_map=colors,
                 title='Casualties in Major Star Wars Battles')

    fig.update_layout(xaxis_title='Battle', yaxis_title='Casualties',
                      legend_title='Outcome', height=600, width=1000)

    # Add text annotations for casualty counts
    for i, row in battle_df.iterrows():
        fig.add_annotation(
            x=row['Battle'],
            y=row['Casualties'],
            text=str(row['Casualties']),
            showarrow=False,
            yshift=10
        )

    return fig

# 8. Force User Analysis


def force_user_analysis():
    """Analyze the distribution of Force users across the trilogy."""
    # Extract force users
    force_user_data = []

    # Process Jedi
    for jedi_id, jedi in jedis.items():
        char_name = characters[jedi_id]['name'] if jedi_id in characters else 'Unknown Jedi'
        rank = jedi.get('jediRank', 'Unknown')
        saber_color = jedi.get('lightsaberColor', 'Unknown')
        midichlorian = jedi.get('midiChlorianCount', 0)

        force_user_data.append({
            'Name': char_name,
            'Type': 'Jedi',
            'Rank/Title': rank,
            'LightsaberColor': saber_color,
            'PowerLevel': midichlorian
        })

    # Process Sith
    for sith_id, sith in siths.items():
        char_name = characters[sith_id]['name'] if sith_id in characters else 'Unknown Sith'
        title = sith.get('sithTitle', '')
        dark_side = sith.get('darkSideLevel', 0)

        title_with_name = f"{title} {char_name}" if title else char_name

        force_user_data.append({
            'Name': title_with_name,
            'Type': 'Sith',
            'Rank/Title': sith.get('apprenticeOf', 'Master'),
            'LightsaberColor': 'Red',  # Sith typically have red sabers
            'PowerLevel': dark_side
        })

    # Convert to DataFrame
    force_df = pd.DataFrame(force_user_data)

    # Create the figure (two subplots)
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.5, 0.5],
        specs=[[{"type": "bar"}, {"type": "pie"}]],
        subplot_titles=("Force Users Power Levels", "Force User Distribution")
    )

    # Add power level bar chart
    fig.add_trace(
        go.Bar(
            x=force_df['Name'],
            y=force_df['PowerLevel'],
            marker_color=force_df['Type'].map({'Jedi': 'blue', 'Sith': 'red'}),
            name='Power Level'
        ),
        row=1, col=1
    )

    # Add force user type pie chart
    fig.add_trace(
        go.Pie(
            labels=force_df['Type'],
            values=force_df.groupby('Type').size(),
            marker_colors=['blue', 'red'],
            textinfo='percent+label',
            hole=0.4
        ),
        row=1, col=2
    )

    fig.update_layout(
        title_text="Force Users in Star Wars Trilogy",
        showlegend=False,
        height=600,
        width=1000
    )

    return fig

# 9. Ship Analysis


def ship_analysis():
    """Analyze the starships in the Star Wars trilogy."""
    # Extract ship data
    ship_data = []
    for ship_id, ship in spaceships.items():
        appearances = 0

        # Count appearances in events
        for episode_key, episode_events in timelines.items():
            for event in episode_events:
                if ('ship' in event and event['ship'] == ship_id) or \
                   ('location' in event and event['location'] == ship_id):
                    appearances += 1

        ship_data.append({
            'Name': ship['uniqueName'],
            'Model': ship['model'],
            'Class': ship['shipClass'],
            'Speed': ship['speedRating'],
            'Hyperdrive': 'Yes' if ship['hyperdriveEquipped'] else 'No',
            'Appearances': appearances
        })

    # Convert to DataFrame
    ship_df = pd.DataFrame(ship_data)
    ship_df = ship_df.sort_values('Appearances', ascending=False)

    # Create the figure
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.6, 0.4],
        specs=[[{"type": "bar"}, {"type": "pie"}]],
        subplot_titles=("Ship Appearances", "Ship Classes")
    )

    # Top ships by appearances
    top_ships = ship_df.head(10)

    # Add bar chart
    fig.add_trace(
        go.Bar(
            x=top_ships['Name'],
            y=top_ships['Appearances'],
            marker_color='lightblue',
            name='Appearances'
        ),
        row=1, col=1
    )

    # Add ship class pie chart
    class_counts = ship_df.groupby('Class').size().reset_index(name='Count')
    class_counts = class_counts.sort_values('Count', ascending=False)

    fig.add_trace(
        go.Pie(
            labels=class_counts['Class'],
            values=class_counts['Count'],
            textinfo='percent+label',
            hole=0.4
        ),
        row=1, col=2
    )

    fig.update_layout(
        title_text="Starships in Star Wars Trilogy",
        xaxis_title="Ship",
        yaxis_title="Number of Appearances",
        legend_title="Ship Class",
        height=600,
        width=1000
    )

    return fig

# 10. Relationship Map


def relationship_map():
    """Create a network visualization of character relationships."""
    # Extract relationships
    relation_data = []
    for relation in relationships:
        relation_type = relation.get('relationshipType', 'Unknown')

        if relation_type == 'biologicalParentOf':
            parent_id = relation.get('parent', '')
            child_id = relation.get('child', '')

            parent_name = characters.get(parent_id, {}).get('name', 'Unknown')
            child_name = characters.get(child_id, {}).get('name', 'Unknown')

            relation_data.append({
                'Source': parent_name,
                'Target': child_name,
                'Type': 'Parent-Child'
            })

        elif relation_type == 'sibling':
            sibling1_id = relation.get('sibling1', '')
            sibling2_id = relation.get('sibling2', '')

            sibling1_name = characters.get(
                sibling1_id, {}).get('name', 'Unknown')
            sibling2_name = characters.get(
                sibling2_id, {}).get('name', 'Unknown')

            relation_data.append({
                'Source': sibling1_name,
                'Target': sibling2_name,
                'Type': 'Siblings'
            })

        elif relation_type == 'hasSidekick':
            char_id = relation.get('character', '')
            sidekick_id = relation.get('sidekick', '')

            char_name = characters.get(char_id, {}).get('name', 'Unknown')
            sidekick_name = characters.get(
                sidekick_id, {}).get('name', 'Unknown')

            relation_data.append({
                'Source': char_name,
                'Target': sidekick_name,
                'Type': 'Has Sidekick'
            })

        elif relation_type == 'ownedBy':
            droid_id = relation.get('droid', '')
            owner_id = relation.get('owner', '')

            droid_name = droids.get(droid_id, {}).get('name', 'Unknown')
            owner_name = characters.get(owner_id, {}).get('name', 'Unknown')

            relation_data.append({
                'Source': owner_name,
                'Target': droid_name,
                'Type': 'Owns Droid'
            })

        elif relation_type == 'pilotedBy':
            ship_id = relation.get('ship', '')
            pilot_id = relation.get('pilot', '')

            ship_name = spaceships.get(ship_id, {}).get(
                'uniqueName', 'Unknown')
            pilot_name = characters.get(pilot_id, {}).get('name', 'Unknown')

            relation_data.append({
                'Source': pilot_name,
                'Target': ship_name,
                'Type': 'Pilots'
            })

    # Convert to DataFrame
    relation_df = pd.DataFrame(relation_data)

    # Create a network graph
    G = nx.from_pandas_edgelist(relation_df, 'Source', 'Target', 'Type')

    # Calculate positions using a spring layout
    pos = nx.spring_layout(G, k=0.5, seed=42)

    # Define edge colors by type
    edge_colors = {
        'Parent-Child': 'blue',
        'Siblings': 'green',
        'Has Sidekick': 'orange',
        'Owns Droid': 'purple',
        'Pilots': 'red'
    }

    # Create edge traces by type
    edge_traces = []
    for edge_type, color in edge_colors.items():
        edge_x = []
        edge_y = []
        edge_text = []

        for edge in G.edges(data=True):
            if 'Type' in edge[2] and edge[2]['Type'] == edge_type:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                edge_text.append(f"{edge[0]} — {edge_type} → {edge[1]}")

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color=color),
            hoverinfo='text',
            text=edge_text,
            mode='lines',
            name=edge_type
        )

        edge_traces.append(edge_trace)

    # Create node trace
    node_x = []
    node_y = []
    node_text = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition='top center',
        textfont=dict(size=10),
        marker=dict(
            size=15,
            color='lightblue',
            line=dict(width=2, color='black')
        ),
        hoverinfo='text'
    )

    # Create the figure
    fig = go.Figure(data=edge_traces + [node_trace],
                    layout=go.Layout(
                    title='Star Wars Character Relationships',
                    titlefont=dict(size=16),
                    showlegend=True,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False,
                               showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False,
                               showticklabels=False),
                    width=1000,
                    height=800
                    ))

    return fig

# 11. Faction Distribution


def faction_distribution():
    """Analyze the distribution of characters by faction."""
    # Count characters by affiliation
    faction_counts = defaultdict(int)
    for char_id, char in characters.items():
        if 'affiliation' in char:
            faction_counts[char['affiliation']] += 1

    for droid_id, droid in droids.items():
        if 'affiliation' in droid:
            faction_counts[droid['affiliation']] += 1

    # Convert to DataFrame
    faction_df = pd.DataFrame(list(faction_counts.items()), columns=[
                              'Affiliation', 'Count'])
    faction_df = faction_df.sort_values('Count', ascending=False)

    # Create a subplot with pie chart and bar chart
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "bar"}]],
        subplot_titles=("Characters by Faction", "Major Factions")
    )

    # Add pie chart
    fig.add_trace(
        go.Pie(
            labels=faction_df['Affiliation'],
            values=faction_df['Count'],
            textinfo='percent+label',
            pull=[0.1 if x in ['Rebel Alliance', 'Galactic Empire']
                  else 0 for x in faction_df['Affiliation']],
            hole=0.3
        ),
        row=1, col=1
    )

    # Add bar chart with top factions
    top_factions = faction_df.head(5)

    fig.add_trace(
        go.Bar(
            x=top_factions['Affiliation'],
            y=top_factions['Count'],
            marker_color='lightgreen'
        ),
        row=1, col=2
    )

    fig.update_layout(
        title_text="Faction Distribution in Star Wars Trilogy",
        height=600,
        width=1000
    )

    return fig
