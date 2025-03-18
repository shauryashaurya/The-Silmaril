import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import networkx as nx
from collections import Counter, defaultdict
import re
import random
import colorsys
import textwrap
import os
from IPython.display import Image, display
import kaleido


# tried to make a function that would automatically render the images - takes too long,
# for GitHub, will download the images and add them manually...
GITHUB_MODE = False  # Set to True when generating for GitHub


def save_and_show_fig(fig, filename):
    """Save figure as static PNG and display interactive version."""
    # Create 'images' directory if it doesn't exist
    os.makedirs('images', exist_ok=True)

    # Show interactive version in notebook
    fig.show()

    # Save static image for GitHub viewing
    # TODO: pick this from the fig layout
    # Configure Kaleido (optional, but recommended)
    # can also be "png" or "jpg", "svg" is typically faster-ish
    pio.kaleido.scope.default_format = "svg"
    fig.write_image(f"images/{filename}.svg", width=800, height=600)

    # Display static image as backup only in GitHub mode
    if GITHUB_MODE:
        print(f"[Static image backup for GitHub viewing]")
        display(Image(filename=f"images/{filename}.png"))
        print("\n---\n")


# 1. Event Significance by Episode


def event_significance_by_episode(data):
    """Visualize how event significance flows through each episode with tilted non-overlapping labels."""
    # Extract events and significance
    timelines = data['timelines']

    episode_arcs = []
    for episode_key, episode_events in timelines.items():
        episode_name = f"Episode {episode_key.replace('episode_', '').upper()}"

        # Create a sequential index for each event to show progression
        for i, event in enumerate(episode_events):
            significance_level = event.get('significanceLevel', 'Medium')

            # Convert significance to numerical value
            if significance_level == 'Low':
                sig_value = 1
            elif significance_level == 'Medium':
                sig_value = 2
            elif significance_level == 'High':
                sig_value = 3
            else:
                sig_value = 4  # Galactic

            episode_arcs.append({
                'Episode': episode_name,
                'Event Index': i,
                'Significance': sig_value,
                'Description': event.get('description', 'Unknown event'),
                'Quote': event.get('quote', '')
            })

    arc_df = pd.DataFrame(episode_arcs)

    # Create the visualization
    fig = px.line(arc_df, x='Event Index', y='Significance', color='Episode',
                  hover_data=['Description', 'Quote'],
                  title='Narrative Arcs Across the Star Wars Trilogy',
                  labels={'Significance': 'Plot Significance',
                          'Event Index': 'Story Progression'})

    # Define colors for episodes with RGBA values directly
    episode_colors = {
        'Episode IV': 'rgba(65, 105, 225, 0.1)',  # royalblue with opacity
        'Episode V': 'rgba(34, 139, 34, 0.1)',    # forestgreen with opacity
        'Episode VI': 'rgba(178, 34, 34, 0.1)'    # firebrick with opacity
    }

    # Define line colors for annotations
    line_colors = {
        'Episode IV': 'rgb(65, 105, 225)',  # royalblue
        'Episode V': 'rgb(34, 139, 34)',    # forestgreen
        'Episode VI': 'rgb(178, 34, 34)'    # firebrick
    }

    # Add filled areas under each line to make the arcs more prominent
    for episode in arc_df['Episode'].unique():
        episode_data = arc_df[arc_df['Episode']
                              == episode].sort_values('Event Index')

        fig.add_trace(
            go.Scatter(
                x=episode_data['Event Index'],
                y=episode_data['Significance'],
                fill='tozeroy',
                mode='none',  # No lines or markers, just the fill
                fillcolor=episode_colors.get(
                    episode, 'rgba(65, 105, 225, 0.1)'),
                showlegend=False,
                hoverinfo='none'
            )
        )

    # Add annotations for all "High" and "Galactic" significance events with tilted labels
    for episode in arc_df['Episode'].unique():
        episode_data = arc_df[arc_df['Episode'] == episode]

        # Get high significance events
        # Significance 3 or 4
        high_events = episode_data[episode_data['Significance'] >= 3]

        for idx, (_, event) in enumerate(high_events.iterrows()):
            # Stagger the vertical position slightly to further reduce overlap
            # Stagger by 10 pixels based on index modulo 3
            y_offset = 30 + (idx % 3) * 10

            # Add tilted labels
            fig.add_annotation(
                x=event['Event Index'],
                y=event['Significance'],
                text=event['Description'],
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=line_colors.get(episode, "black"),
                ax=50,  # Horizontal offset to make room for tilted text
                ay=-y_offset,  # Vertical offset
                # Semi-transparent white background
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor=line_colors.get(episode, "black"),
                borderwidth=1,
                font=dict(color="black", size=9),
                textangle=55  # Tilt the text 45 degrees
            )

    # Improve layout with better labels
    fig.update_layout(
        height=1024,  # Taller height to accommodate labels
        width=2600,  # Wider width to accommodate labels
        yaxis=dict(
            tickvals=[1, 2, 3, 4],
            ticktext=['Low', 'Medium', 'High', 'Galactic'],
            title_font=dict(size=14),
            tickfont=dict(size=12)
        ),
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=10)
        ),
        title=dict(
            text='Narrative Arcs Across the Star Wars Trilogy',
            font=dict(size=20)
        ),
        legend=dict(
            title_font=dict(size=14),
            font=dict(size=12)
        ),
        # Increased bottom margin for tilted labels
        margin=dict(l=50, r=50, t=80, b=150)
    )

    # Add episode separators if multiple episodes
    if len(arc_df['Episode'].unique()) > 1:
        # Get max event index for each episode to place dividers
        episode_max_indices = arc_df.groupby('Episode')['Event Index'].max()

        # Add vertical lines between episodes
        for i, episode in enumerate(sorted(arc_df['Episode'].unique())):
            # Don't add line after last episode
            if i < len(arc_df['Episode'].unique()) - 1:
                divider_x = (episode_max_indices[episode] +
                             arc_df[arc_df['Episode'] == sorted(arc_df['Episode'].unique())[i+1]]['Event Index'].min()) / 2

                fig.add_shape(
                    type="line",
                    x0=divider_x,
                    y0=0,
                    x1=divider_x,
                    y1=4.5,
                    line=dict(
                        color="gray",
                        width=1,
                        dash="dash",
                    )
                )

    return fig

# 2. Character Appearances Across Timeline


def character_appearances_timeline(data):
    """Track major character appearances throughout the timeline."""
    # Extract character appearances
    timelines = data['timelines']
    characters = data['characters']

    # Key characters to track
    key_characters = [
        'Luke Skywalker', 'Leia Organa', 'Han Solo', 'Darth Vader',
        'Obi-Wan Kenobi', 'Emperor Palpatine', 'Chewbacca',
        'Yoda', 'Lando Calrissian', 'R2-D2', 'C-3PO'
    ]
    key_char_ids = {}

    # Get character IDs by name
    for char_id, char in characters.items():
        if char['name'] in key_characters:
            key_char_ids[char['name']] = char_id

    # Also check droids dict
    droids = data.get('droids', {})
    for droid_id, droid in droids.items():
        if droid['name'] in key_characters:
            key_char_ids[droid['name']] = droid_id

    # Track appearances
    appearances = []

    # For each episode
    for episode_key, episode_events in timelines.items():
        episode_name = f"Episode {episode_key.replace('episode_', '')}"
        episode_num = int(episode_key.replace('episode_', ''))

        # For each event
        for event_idx, event in enumerate(episode_events):
            if 'participants' in event:
                # Record appearance for each character in the event
                for char_name, char_id in key_char_ids.items():
                    if char_id in event['participants']:
                        appearances.append({
                            'Character': char_name,
                            'Episode': episode_name,
                            'Episode Number': episode_num,
                            'Event Index': event_idx,
                            'Description': event.get('description', '')
                        })

    appearance_df = pd.DataFrame(appearances)

    # Create a composite timeline position
    appearance_df['Timeline Position'] = (
        appearance_df['Episode Number'] - 4) * 100 + appearance_df['Event Index']

    # Create the figure
    fig = px.scatter(appearance_df,
                     x='Timeline Position',
                     y='Character',
                     color='Episode',
                     hover_data=['Description'],
                     title='Character Appearances Throughout the Star Wars Trilogy',
                     labels={
                       'Timeline Position': 'Story Progression',
                       'Character': 'Character'
                     })

    # Add connecting lines for each character
    for char in key_characters:
        if char in appearance_df['Character'].values:
            char_data = appearance_df[appearance_df['Character'] == char]
            char_data = char_data.sort_values('Timeline Position')

            fig.add_trace(
                go.Scatter(
                    x=char_data['Timeline Position'],
                    y=[char] * len(char_data),
                    mode='lines',
                    line=dict(width=1, dash='dot'),
                    showlegend=False
                )
            )

    # Add vertical lines separating episodes
    for ep_num in range(4, 7):
        if ep_num > 4:  # Don't add a line before episode 4
            fig.add_vline(x=(ep_num-4)*100, line_dash="dash",
                          line_width=1, line_color="gray")
            fig.add_annotation(
                x=(ep_num-4)*100 + 5,
                y=key_characters[0],
                text=f"Episode {ep_num}",
                showarrow=False
            )

    fig.update_layout(
        height=800,
        width=1400
    )

    return fig

# 3. Scene Context Analysis


def scene_context_analysis(data):
    """Analyze the context of scenes - battles, dialogues, revelations, etc."""
    # Define scene context categories
    context_keywords = {
        "Battle/Combat": ["battle", "attack", "fight", "destroy", "defeat", "combat"],
        "Journey/Travel": ["escape", "arrive", "journey", "travel", "flee", "leave"],
        "Revelation/Discovery": ["reveal", "discover", "learn", "truth", "secret"],
        "Dialogue/Meeting": ["meet", "talk", "discuss", "conversation", "speak"],
        "Rescue/Help": ["rescue", "help", "save", "protect", "free"],
        "Capture/Trap": ["capture", "trap", "imprison", "caught", "frozen"],
        "Force/Jedi/Sith": ["force", "jedi", "sith", "lightsaber", "training"],
        "Emotional Moment": ["love", "father", "sister", "family", "friend", "trust", "betray"]
    }

    # Analyze events
    timelines = data['timelines']

    scene_contexts = []

    for episode_key, events in timelines.items():
        episode_name = f"Episode {episode_key.replace('episode_', '')}"

        # Analyze each event for context keywords
        for event in events:
            description = event.get('description', '').lower()

            # Find matching contexts
            contexts_found = []
            for context, keywords in context_keywords.items():
                if any(keyword in description for keyword in keywords):
                    contexts_found.append(context)

            # If no context found, mark as "Other"
            if not contexts_found:
                contexts_found = ["Other"]

            # Record each context for this event
            for context in contexts_found:
                scene_contexts.append({
                    'Episode': episode_name,
                    'Context': context,
                    'Description': event.get('description', '')
                })

    context_df = pd.DataFrame(scene_contexts)

    # Count contexts by episode
    context_counts = context_df.groupby(
        ['Episode', 'Context']).size().reset_index(name='Count')

    # Create a grouped bar chart
    fig = px.bar(context_counts,
                 x='Context',
                 y='Count',
                 color='Episode',
                 barmode='group',
                 title='Scene Contexts Across the Star Wars Trilogy',
                 labels={
                     'Context': 'Scene Context',
                     'Count': 'Number of Scenes',
                     'Episode': 'Episode'
                 })

    fig.update_layout(
        height=800,
        width=1400,
        xaxis={'categoryorder': 'total descending'}
    )

    return fig

# 4. Character Co-occurrence Analysis


def character_co_occurrence(data):
    """Analyze which characters appear together most frequently."""
    # Create a matrix of character co-occurrences
    characters = data['characters']
    droids = data.get('droids', {})
    timelines = data['timelines']

    # Get all character IDs and names
    char_names = {}
    for char_id, char in characters.items():
        char_names[char_id] = char['name']
    for droid_id, droid in droids.items():
        char_names[droid_id] = droid['name']

    # Count co-occurrences
    co_occurrences = defaultdict(int)

    for episode_key, events in timelines.items():
        for event in events:
            if 'participants' in event:
                participants = event['participants']
                for i in range(len(participants)):
                    for j in range(i+1, len(participants)):
                        char1 = participants[i]
                        char2 = participants[j]

                        # Ensure we have names for both characters
                        if char1 in char_names and char2 in char_names:
                            # Sort names to create consistent pair keys
                            name_pair = tuple(
                                sorted([char_names[char1], char_names[char2]]))
                            co_occurrences[name_pair] += 1

    # Convert to DataFrame
    co_occur_data = []
    for (char1, char2), count in co_occurrences.items():
        co_occur_data.append({
            'Character 1': char1,
            'Character 2': char2,
            'Co-occurrences': count
        })

    co_df = pd.DataFrame(co_occur_data)

    # Get top character pairs
    top_pairs = co_df.sort_values('Co-occurrences', ascending=False).head(20)

    # Create heatmap data
    unique_chars = set()
    for _, row in top_pairs.iterrows():
        unique_chars.add(row['Character 1'])
        unique_chars.add(row['Character 2'])

    char_list = sorted(list(unique_chars))
    heatmap_matrix = np.zeros((len(char_list), len(char_list)))

    for _, row in co_df.iterrows():
        if row['Character 1'] in char_list and row['Character 2'] in char_list:
            i = char_list.index(row['Character 1'])
            j = char_list.index(row['Character 2'])
            heatmap_matrix[i, j] = row['Co-occurrences']
            heatmap_matrix[j, i] = row['Co-occurrences']  # Make it symmetric

    # Create heatmap figure
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_matrix,
        x=char_list,
        y=char_list,
        colorscale='Viridis',
        hoverongaps=False))

    fig.update_layout(
        title='Character Co-occurrence Heatmap',
        height=800,
        width=1400,
        xaxis_title='Character',
        yaxis_title='Character'
    )

    return fig

# 5. Location Appearances by Episode


def location_appearances_by_episode(data):
    """Analyze where scenes take place across the trilogy."""
    # Extract location data
    timelines = data['timelines']
    planets = data['planets']
    spaceships = data['spaceships']

    location_data = []

    for episode_key, events in timelines.items():
        episode_name = f"Episode {episode_key.replace('episode_', '')}"

        for event in events:
            if 'location' in event:
                location_id = event['location']

                # Try to get location name
                location_name = "Unknown"
                if location_id in planets:
                    location_name = planets[location_id]['planetName']
                elif location_id in spaceships:
                    location_name = spaceships[location_id]['uniqueName']

                location_data.append({
                    'Episode': episode_name,
                    'Location': location_name,
                    'Description': event.get('description', '')
                })

    location_df = pd.DataFrame(location_data)

    # Count location appearances by episode
    location_counts = location_df.groupby(
        ['Episode', 'Location']).size().reset_index(name='Count')

    # Get top locations
    top_locations = location_counts.groupby(
        'Location')['Count'].sum().nlargest(15).index
    location_counts = location_counts[location_counts['Location'].isin(
        top_locations)]

    # Create the treemap
    fig = px.treemap(
        location_counts,
        path=[px.Constant("Star Wars"), 'Episode', 'Location'],
        values='Count',
        color='Episode',
        title='Locations by Episode in Star Wars Trilogy',
        hover_data=['Count']
    )

    fig.update_layout(
        height=700,
        width=1400
    )

    return fig

# 6. Character Network By Episode


def character_network_by_episode(data):
    """Visualize how character networks evolve across episodes."""
    # Get characters
    characters = data['characters']
    droids = data.get('droids', {})
    timelines = data['timelines']

    # Get character names
    char_names = {}
    for char_id, char in characters.items():
        char_names[char_id] = char['name']
    for droid_id, droid in droids.items():
        char_names[droid_id] = droid['name']

    # Create subplot for each episode
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Episode IV: A New Hope",
                        "Episode V: The Empire Strikes Back", "Episode VI: Return of the Jedi"),
        specs=[[{"type": "scatter"}, {"type": "scatter"}, {"type": "scatter"}]]
    )

    # For each episode, create a network
    for i, episode_key in enumerate(['episode_4', 'episode_5', 'episode_6']):
        # Extract character co-occurrences for this episode
        co_occurrences = defaultdict(int)

        for event in timelines[episode_key]:
            if 'participants' in event:
                participants = event['participants']
                for p1_idx in range(len(participants)):
                    for p2_idx in range(p1_idx+1, len(participants)):
                        char1 = participants[p1_idx]
                        char2 = participants[p2_idx]

                        if char1 in char_names and char2 in char_names:
                            co_occurrences[(char1, char2)] += 1

        # Create a graph
        G = nx.Graph()

        # Add nodes
        for char_id, name in char_names.items():
            # Only add characters that appear in this episode
            if any(char_id == pair[0] or char_id == pair[1] for pair in co_occurrences.keys()):
                G.add_node(char_id, name=name)

        # Add edges
        for (char1, char2), weight in co_occurrences.items():
            G.add_edge(char1, char2, weight=weight)

        # Calculate positions
        pos = nx.spring_layout(G, seed=42)

        # Extract top characters by degree
        degrees = dict(G.degree(weight='weight'))
        # top_chars = sorted(
        #     degrees.items(), key=lambda x: x[1], reverse=True)[:10]
        # top_char_ids = [char_id for char_id, _ in top_chars]
        importance = {}
        for char_id in G.nodes():
            # Get base degree importance
            base_importance = degrees.get(char_id, 0)

            # Get character data
            char_data = {}
            if char_id in characters:
                char_data = characters[char_id]
            elif char_id in droids:
                char_data = droids[char_id]

            # Add importance based on event significance
            event_importance = 0
            for episode_key, events in timelines.items():
                for event in events:
                    if 'participants' in event and char_id in event['participants']:
                        # Add significance value
                        sig_level = event.get('significanceLevel', 'Medium')
                        if sig_level == 'High':
                            event_importance += 2
                        elif sig_level == 'Medium':
                            event_importance += 1
                        elif sig_level == 'Galactic':
                            event_importance += 3

            # Combine metrics
            importance[char_id] = base_importance + event_importance * 0.5

        # Use this enhanced importance metric
        top_chars = sorted(importance.items(),
                           key=lambda x: x[1], reverse=True)[:10]
        top_char_ids = [char_id for char_id, _ in top_chars]

        # Create edge traces
        # edge_x = []
        # edge_y = []

        # Create edge traces with varying thickness based on weight
        edge_traces = []
        edge_weights = []

        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            weight = edge[2].get('weight', 1)
            edge_weights.append(weight)

            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                line=dict(
                    # Cap width between 1 and 8
                    width=max(1, min(8, weight/2)),
                    color='rgba(150,150,150,0.6)'  # Semi-transparent gray
                ),
                hoverinfo='none',
                mode='lines',
                showlegend=False
            )
            edge_traces.append(edge_trace)

        # Add all edge traces to the figure
        for edge_trace in edge_traces:
            fig.add_trace(edge_trace, row=1, col=i+1)

        # Create node traces - one for top characters and one for others
        node_x_top = []
        node_y_top = []
        node_text_top = []
        node_size_top = []
        node_color_top = []  # Add color array

        node_x_other = []
        node_y_other = []
        node_text_other = []
        node_size_other = []
        node_color_other = []  # Add color array

        # Color mapping for affiliations
        affiliation_colors = {
            'Rebel Alliance': 'royalblue',
            'Galactic Empire': 'darkred',
            'Jedi Order': 'green',
            'Bounty Hunters Guild': 'orange',
            'Hutt Cartel': 'purple',
            'Ewok Tribe': 'brown'
        }

        for node in G.nodes():
            x, y = pos[node]
            name = G.nodes[node]['name']

            # Get character metadata
            char_data = {}
            if node in characters:
                char_data = characters[node]
            elif node in droids:
                char_data = droids[node]

            # Determine affiliation color
            affiliation = char_data.get('affiliation', 'Unknown')
            color = affiliation_colors.get(affiliation, 'lightgray')

            # Create hover text with metadata
            hover_text = [
                f"Name: {name}",
                f"Affiliation: {affiliation}",
                f"Species: {char_data.get('species', 'Unknown')}",
                f"Force Sensitive: {'Yes' if char_data.get('forceSensitive', False) else 'No'}",
                f"Rank: {char_data.get('rank', 'Unknown')}",
                f"Connections: {len(list(G.neighbors(node)))}"
            ]

            if node in top_char_ids:
                node_x_top.append(x)
                node_y_top.append(y)
                node_text_top.append(name)
                node_size_top.append(degrees[node] * 2 + 10)
                node_color_top.append(color)
            else:
                node_x_other.append(x)
                node_y_other.append(y)
                node_text_other.append(name)
                node_size_other.append(5)
                node_color_other.append(color)

        # Add traces to subplot
        fig.add_trace(
            go.Scatter(
                x=node_x_other, y=node_y_other,
                mode='markers',
                hoverinfo='text',
                text=[f"{txt}<br>Connections: {sz//5}" for txt,
                      sz in zip(node_text_other, node_size_other)],
                marker=dict(
                    size=node_size_other,
                    color=node_color_other,  # Apply colors
                    line=dict(width=1, color='#888')
                ),
                showlegend=False
            ),
            row=1, col=i+1
        )

        fig.add_trace(
            go.Scatter(
                x=node_x_top, y=node_y_top,
                mode='markers+text',
                hoverinfo='text',
                text=node_text_top,
                hovertext=[f"{name}<br>Affiliation: {color}" for name,
                           color in zip(node_text_top, node_color_top)],
                textposition="top center",
                textfont=dict(size=10),
                marker=dict(
                    size=node_size_top,
                    color=node_color_top,  # Apply colors
                    line=dict(width=2, color='#888')
                ),
                showlegend=False
            ),
            row=1, col=i+1
        )

        # Add a legend explaining colors
        for affiliation, color in affiliation_colors.items():
            fig.add_trace(
                go.Scatter(
                    x=[None], y=[None],
                    mode='markers',
                    marker=dict(size=10, color=color),
                    name=affiliation,
                    showlegend=True
                )
            )

        # Then update the showlegend parameter in the final layout:
        fig.update_layout(
            title='Character Networks by Episode',
            height=700,  # Increased height to accommodate legend
            width=1000,
            showlegend=True,  # Changed to True
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )

    fig.update_layout(
        title='Character Networks by Episode',
        height=1024,
        width=2600,
        showlegend=False
    )

    # Hide axes
    for i in range(1, 4):
        fig.update_xaxes(showticklabels=False, showgrid=False,
                         zeroline=False, row=1, col=i)
        fig.update_yaxes(showticklabels=False, showgrid=False,
                         zeroline=False, row=1, col=i)

    return fig

# 7. Character Affiliation Analysis


def character_affiliation_analysis(data):
    """Analyze the balance of power between different factions."""
    # Extract character affiliations
    characters = data['characters']
    droids = data.get('droids', {})

    # Count affiliations for all characters
    affiliation_counts = defaultdict(int)

    for char_id, char in characters.items():
        if 'affiliation' in char:
            affiliation_counts[char['affiliation']] += 1

    for droid_id, droid in droids.items():
        if 'affiliation' in droid:
            affiliation_counts[droid['affiliation']] += 1

    # Convert to DataFrame
    affiliation_df = pd.DataFrame([
        {'Affiliation': aff, 'Count': count}
        for aff, count in affiliation_counts.items()
    ])

    # Sort by count
    affiliation_df = affiliation_df.sort_values('Count', ascending=False)

    # Highlight the top 2 affiliations (typically Rebel Alliance and Galactic Empire)
    colors = ['darkblue', 'darkred'] + \
        ['lightgray'] * (len(affiliation_df) - 2)

    # Create a bar chart
    fig = px.bar(
        affiliation_df,
        x='Affiliation',
        y='Count',
        title='Character Affiliation Distribution',
        labels={
            'Affiliation': 'Affiliation',
            'Count': 'Number of Characters'
        },
        color='Affiliation',
        color_discrete_sequence=colors
    )

    # Create a second trace with a treemap
    treemap_fig = px.treemap(
        affiliation_df,
        path=['Affiliation'],
        values='Count',
        title='Character Affiliation Distribution',
        color='Count',
        color_continuous_scale='Blues'
    )

    # Combine the visualizations
    combined_fig = make_subplots(
        rows=2, cols=1,
        specs=[[{"type": "bar"}], [{"type": "treemap"}]],
        subplot_titles=("Character Affiliations", "Proportional Distribution"),
        row_heights=[0.4, 0.6],
        vertical_spacing=0.1
    )

    # Add the bar chart
    for trace in fig.data:
        combined_fig.add_trace(trace, row=1, col=1)

    # Add the treemap
    for trace in treemap_fig.data:
        combined_fig.add_trace(trace, row=2, col=1)

    combined_fig.update_layout(
        height=900,
        width=1400,
        title_text="Character Affiliation Analysis"

    )

    return combined_fig

# 8. Quote Analysis by Character


def quote_analysis_by_character(data):
    """Analyze quotes by character across the trilogy."""
    # Extract quotes from events
    timelines = data['timelines']
    characters = data['characters']
    droids = data.get('droids', {})

    # Create a mapping of character IDs to names
    char_names = {}
    for char_id, char in characters.items():
        char_names[char_id] = char['name']
    for droid_id, droid in droids.items():
        char_names[droid_id] = droid['name']

    quotes = []

    for episode_key, events in timelines.items():
        episode_name = f"Episode {episode_key.replace('episode_', '')}"

        for event in events:
            if 'quote' in event and event['quote']:
                # Try to determine who said the quote based on participants
                speaker = "Unknown"
                if 'participants' in event and len(event['participants']) > 0:
                    # Assume first participant is the speaker (simplification)
                    speaker_id = event['participants'][0]
                    if speaker_id in char_names:
                        speaker = char_names[speaker_id]

                quotes.append({
                    'Episode': episode_name,
                    'Speaker': speaker,
                    'Quote': event['quote'],
                    'Description': event.get('description', '')
                })

    quotes_df = pd.DataFrame(quotes)

    # Count quotes by character
    quote_counts = quotes_df.groupby(
        ['Episode', 'Speaker']).size().reset_index(name='Quote Count')

    # Get characters with at least 2 quotes
    top_speakers = quote_counts.groupby('Speaker')['Quote Count'].sum()
    top_speakers = top_speakers[top_speakers >= 2].index

    # Filter for top speakers
    quote_counts = quote_counts[quote_counts['Speaker'].isin(top_speakers)]

    # Create bar chart
    fig = px.bar(
        quote_counts,
        x='Speaker',
        y='Quote Count',
        color='Episode',
        title='Memorable Quotes by Character',
        barmode='group'
    )

    # Create a table of example quotes
    quotes_sample = quotes_df[quotes_df['Speaker'].isin(top_speakers)]
    quotes_sample = quotes_sample.sample(min(10, len(quotes_sample)))

    # Combine visualizations
    combined_fig = make_subplots(
        rows=2, cols=1,
        specs=[[{"type": "bar"}], [{"type": "table"}]],
        subplot_titles=("Quote Counts by Character", "Example Quotes"),
        row_heights=[0.6, 0.4],
        vertical_spacing=0.1
    )

    # Add the bar chart
    for trace in fig.data:
        combined_fig.add_trace(trace, row=1, col=1)

    # Add the table
    combined_fig.add_trace(
        go.Table(
            header=dict(
                values=['Speaker', 'Quote', 'Episode'],
                fill_color='paleturquoise',
                align='left'
            ),
            cells=dict(
                values=[
                    quotes_sample['Speaker'],
                    quotes_sample['Quote'],
                    quotes_sample['Episode']
                ],
                fill_color='lavender',
                align='left'
            )
        ),
        row=2, col=1
    )

    combined_fig.update_layout(
        height=800,
        width=1400,
        title_text="Quote Analysis by Character"
    )

    return combined_fig

# 9. Relationship Types Analysis


def relationship_types_analysis(data):
    """Analyze the types of relationships between characters with enhanced connections."""
    # Extract relationships
    relationships = data['relationships']
    characters = data['characters']
    droids = data.get('droids', {})
    spaceships = data.get('spaceships', {})
    timelines = data['timelines']  # Add timelines for inferring relationships

    # Create character name lookup
    character_names = {}
    for char_id, char in characters.items():
        character_names[char_id] = char['name']
    for droid_id, droid in droids.items():
        character_names[droid_id] = droid['name']

    # 1. Extract explicit relationships
    relationship_data = []

    for relation in relationships:
        relation_type = relation.get('relationshipType', 'Unknown')

        if relation_type == 'biologicalParentOf':
            parent_id = relation.get('parent', '')
            child_id = relation.get('child', '')

            parent_name = characters.get(parent_id, {}).get('name', 'Unknown')
            child_name = characters.get(child_id, {}).get('name', 'Unknown')

            relationship_data.append({
                'Type': 'Family',
                'Character 1': parent_name,
                'Character 2': child_name,
                'Description': f"{parent_name} is parent of {child_name}",
                'Explicit': True
            })

        elif relation_type == 'sibling':
            sibling1_id = relation.get('sibling1', '')
            sibling2_id = relation.get('sibling2', '')

            sibling1_name = characters.get(
                sibling1_id, {}).get('name', 'Unknown')
            sibling2_name = characters.get(
                sibling2_id, {}).get('name', 'Unknown')

            relationship_data.append({
                'Type': 'Family',
                'Character 1': sibling1_name,
                'Character 2': sibling2_name,
                'Description': f"{sibling1_name} and {sibling2_name} are siblings",
                'Explicit': True
            })

        elif relation_type == 'hasSidekick':
            char_id = relation.get('character', '')
            sidekick_id = relation.get('sidekick', '')

            char_name = characters.get(char_id, {}).get('name', 'Unknown')
            sidekick_name = characters.get(
                sidekick_id, {}).get('name', 'Unknown')

            relationship_data.append({
                'Type': 'Alliance',
                'Character 1': char_name,
                'Character 2': sidekick_name,
                'Description': f"{char_name} has sidekick {sidekick_name}",
                'Explicit': True
            })

        elif relation_type == 'ownedBy':
            droid_id = relation.get('droid', '')
            owner_id = relation.get('owner', '')

            droid_name = "Unknown"
            if droid_id in droids:
                droid_name = droids[droid_id]['name']
            elif droid_id in characters:
                droid_name = characters[droid_id]['name']

            owner_name = characters.get(owner_id, {}).get('name', 'Unknown')

            relationship_data.append({
                'Type': 'Ownership',
                'Character 1': owner_name,
                'Character 2': droid_name,
                'Description': f"{owner_name} owns {droid_name}",
                'Explicit': True
            })

        elif relation_type == 'pilotedBy':
            ship_id = relation.get('ship', '')
            pilot_id = relation.get('pilot', '')

            ship_name = spaceships.get(ship_id, {}).get(
                'uniqueName', 'Unknown Ship')
            pilot_name = characters.get(pilot_id, {}).get('name', 'Unknown')

            relationship_data.append({
                'Type': 'Piloting',
                'Character 1': pilot_name,
                'Character 2': ship_name,
                'Description': f"{pilot_name} pilots {ship_name}",
                'Explicit': True
            })

    # 2. Infer relationships from affiliations - characters in same faction are allies
    affiliation_groups = {}
    for char_id, char in characters.items():
        if 'affiliation' in char and char['affiliation'] != 'Unknown':
            if char['affiliation'] not in affiliation_groups:
                affiliation_groups[char['affiliation']] = []
            affiliation_groups[char['affiliation']].append(char_id)

    # Add allied relationships for characters in same faction
    for affiliation, members in affiliation_groups.items():
        # Only create relationships for factions with multiple characters
        if len(members) > 1:
            # For major factions, create relationship between important characters
            if affiliation in ['Rebel Alliance', 'Galactic Empire', 'Jedi Order']:
                for i in range(len(members)):
                    # Limit to avoid too many connections
                    for j in range(i+1, min(i+3, len(members))):
                        char1_id = members[i]
                        char2_id = members[j]
                        char1_name = character_names.get(char1_id, 'Unknown')
                        char2_name = character_names.get(char2_id, 'Unknown')

                        relationship_data.append({
                            'Type': 'Alliance',
                            'Character 1': char1_name,
                            'Character 2': char2_name,
                            'Description': f"Both members of {affiliation}",
                            'Explicit': False
                        })

    # 3. Infer opposing relationships between Rebels and Empire
    rebel_members = affiliation_groups.get('Rebel Alliance', [])
    empire_members = affiliation_groups.get('Galactic Empire', [])

    # Select key characters from each side
    key_rebels = rebel_members[:3] if len(rebel_members) > 3 else rebel_members
    key_imperials = empire_members[:3] if len(
        empire_members) > 3 else empire_members

    # Create opposing relationships
    for rebel_id in key_rebels:
        for imperial_id in key_imperials:
            rebel_name = character_names.get(rebel_id, 'Unknown')
            imperial_name = character_names.get(imperial_id, 'Unknown')

            relationship_data.append({
                'Type': 'Opposition',
                'Character 1': rebel_name,
                'Character 2': imperial_name,
                'Description': f"Rebel vs Empire",
                'Explicit': False
            })

    # 4. Infer relationships from significant events
    significant_events = []
    for episode, events in timelines.items():
        for event in events:
            if event.get('significanceLevel') in ['High', 'Galactic'] and 'participants' in event and len(event['participants']) > 1:
                significant_events.append(event)

    # For each significant event, infer relationships between participants
    for event in significant_events:
        participants = event['participants']
        description = event.get('description', 'Important event')

        # Check for battle events
        is_battle = any(keyword in description.lower()
                        for keyword in ['battle', 'fight', 'duel'])
        is_rescue = any(keyword in description.lower()
                        for keyword in ['rescue', 'save', 'free'])
        is_revelation = any(keyword in description.lower()
                            for keyword in ['reveals', 'father', 'sister'])

        # Determine relationship type based on event content
        rel_type = "Plot Connection"
        if is_battle:
            rel_type = "Battle Comrades"
        elif is_rescue:
            rel_type = "Rescue/Aid"
        elif is_revelation:
            rel_type = "Revelation"

        # Only create a few connections to avoid overcrowding
        if len(participants) <= 4:  # For smaller groups, connect everyone
            for i in range(len(participants)):
                for j in range(i+1, len(participants)):
                    if participants[i] in character_names and participants[j] in character_names:
                        char1_name = character_names[participants[i]]
                        char2_name = character_names[participants[j]]

                        relationship_data.append({
                            'Type': rel_type,
                            'Character 1': char1_name,
                            'Character 2': char2_name,
                            'Description': description,
                            'Explicit': False
                        })
        else:  # For larger groups, just connect the first character with others
            for i in range(1, len(participants)):
                if participants[0] in character_names and participants[i] in character_names:
                    char1_name = character_names[participants[0]]
                    char2_name = character_names[participants[i]]

                    relationship_data.append({
                        'Type': rel_type,
                        'Character 1': char1_name,
                        'Character 2': char2_name,
                        'Description': description,
                        'Explicit': False
                    })

    # Convert to DataFrame
    rel_df = pd.DataFrame(relationship_data)

    # Count relationship types
    type_counts = rel_df['Type'].value_counts().reset_index()
    type_counts.columns = ['Relationship Type', 'Count']

    # Create a colorful bar chart
    fig_bar = px.bar(
        type_counts,
        x='Relationship Type',
        y='Count',
        title='Types of Relationships in Star Wars',
        color='Relationship Type',
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    # Create network diagram
    G = nx.Graph()

    # Add nodes
    all_characters = set(rel_df['Character 1']) | set(rel_df['Character 2'])

    # Filter for human-like characters (exclude ships, etc.)
    human_chars = {
        char_name for char_name in all_characters
        if char_name not in ['Millennium Falcon', 'X-Wing Red Five', 'Unknown Ship']
    }

    for char in human_chars:
        G.add_node(char)

    # Add edges with weights
    edge_weights = {}
    for _, row in rel_df.iterrows():
        if row['Character 1'] in human_chars and row['Character 2'] in human_chars:
            edge_key = tuple(sorted([row['Character 1'], row['Character 2']]))
            if edge_key not in edge_weights:
                edge_weights[edge_key] = 0

            # Explicit relationships get higher weight
            weight_increment = 2 if row['Explicit'] else 1
            edge_weights[edge_key] += weight_increment

    # Add weighted edges to the graph
    for (node1, node2), weight in edge_weights.items():
        G.add_edge(node1, node2, weight=weight)

    # Calculate positions using a better layout
    pos = nx.kamada_kawai_layout(G)  # More balanced layout than spring_layout

    # Edge color mapping
    edge_color_map = {
        'Family': 'rgba(214, 39, 40, 0.8)',  # Red
        'Alliance': 'rgba(44, 160, 44, 0.8)',  # Green
        'Opposition': 'rgba(31, 119, 180, 0.8)',  # Blue
        'Ownership': 'rgba(255, 127, 14, 0.8)',  # Orange
        'Piloting': 'rgba(148, 103, 189, 0.8)',  # Purple
        'Plot Connection': 'rgba(140, 86, 75, 0.8)',  # Brown
        'Battle Comrades': 'rgba(227, 119, 194, 0.8)',  # Pink
        'Rescue/Aid': 'rgba(188, 189, 34, 0.8)',  # Olive
        'Revelation': 'rgba(23, 190, 207, 0.8)'  # Cyan
    }

    # Create edge traces by type
    edge_traces = []

    # Collect all relationship types for a given edge
    edge_types = defaultdict(list)
    for _, row in rel_df.iterrows():
        if row['Character 1'] in human_chars and row['Character 2'] in human_chars:
            edge_key = tuple(sorted([row['Character 1'], row['Character 2']]))
            edge_types[edge_key].append(row['Type'])

    # Create edges with the most meaningful relationship type
    for edge, types in edge_types.items():
        # Prioritize family relationships, then explicit relationships
        if 'Family' in types:
            rel_type = 'Family'
        elif 'Opposition' in types:
            rel_type = 'Opposition'
        elif 'Alliance' in types:
            rel_type = 'Alliance'
        else:
            # Use the first type
            rel_type = types[0]

        # Get edge coordinates
        char1, char2 = edge
        x0, y0 = pos[char1]
        x1, y1 = pos[char2]

        # Get edge weight
        weight = edge_weights.get(edge, 1)

        # Create edge trace
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            line=dict(
                width=max(1, min(5, weight)),  # Scale width by weight
                color=edge_color_map.get(rel_type, 'gray')
            ),
            hoverinfo='text',
            text=f"{char1} — {rel_type} → {char2}",
            mode='lines',
            name=rel_type
        )

        edge_traces.append(edge_trace)

    # Create node trace with better styling
    node_x = []
    node_y = []
    node_text = []
    node_sizes = []
    node_colors = []

    # Calculate node importance by number of connections
    node_importance = {}
    for node in G.nodes():
        # Base importance on number of connections
        conn_importance = len(list(G.neighbors(node)))

        # Check if this is a key character (Luke, Vader, Leia, Han)
        key_character_bonus = 0
        if node in ['Luke Skywalker', 'Darth Vader', 'Leia Organa', 'Han Solo']:
            key_character_bonus = 5

        node_importance[node] = conn_importance + key_character_bonus

    # Node color mapping based on key characters
    node_color_map = {
        'Luke Skywalker': 'rgba(65, 105, 225, 1)',  # Royal blue
        'Darth Vader': 'rgba(178, 34, 34, 1)',      # Firebrick red
        'Leia Organa': 'rgba(186, 85, 211, 1)',     # Medium orchid
        'Han Solo': 'rgba(46, 139, 87, 1)',         # Sea green
        'Chewbacca': 'rgba(139, 69, 19, 1)',        # Saddle brown
        'Obi-Wan Kenobi': 'rgba(70, 130, 180, 1)',  # Steel blue
        'Emperor Palpatine': 'rgba(128, 0, 0, 1)',  # Maroon
        'R2-D2': 'rgba(30, 144, 255, 1)',           # Dodger blue
        'C-3PO': 'rgba(255, 215, 0, 1)',            # Gold
        'Yoda': 'rgba(34, 139, 34, 1)'              # Forest green
    }

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

        # Size based on importance
        node_sizes.append(node_importance[node] * 3 + 10)

        # Color based on character
        node_colors.append(node_color_map.get(
            node, 'rgba(169, 169, 169, 1)'))  # Default gray

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition='top center',
        textfont=dict(size=10, family='Arial'),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='white')
        ),
        hoverinfo='text'
    )

    # Create network figure with improved styling
    fig_network = go.Figure(data=edge_traces + [node_trace])

    # Add a more descriptive title and annotations
    fig_network.update_layout(
        title='Character Relationship Network in Star Wars',
        showlegend=True,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=1400,
        width=1800,
        annotations=[
            dict(
                text="Connections show relationships between characters<br>Node size indicates character importance",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.01, y=0.01,
                font=dict(size=12)
            )
        ]
    )

    # Combine visualizations in a better layout
    combined_fig = make_subplots(
        rows=2, cols=1,
        specs=[[{"type": "bar"}], [{"type": "scatter"}]],
        subplot_titles=("Relationship Types in Star Wars",
                        "Character Relationship Network"),
        row_heights=[0.3, 0.7],
        vertical_spacing=0.1
    )

    # Add the bar chart
    for trace in fig_bar.data:
        combined_fig.add_trace(trace, row=1, col=1)

    # Add the network
    for trace in fig_network.data:
        combined_fig.add_trace(trace, row=2, col=1)

    combined_fig.update_layout(
        height=1400,
        width=2000,
        title_text="Character Relationships in Star Wars",
        showlegend=True,
        legend=dict(
            orientation="v",      # Change from "h" to "v"
            yanchor="top",        # Change from "bottom" to "top"
            y=1,                  # Change from -0.15 to 1
            xanchor="right",      # Change from "center" to "right"
            x=1.2                # Change from 0.5 to 1.05
        )

    )

    # Hide axes for network
    combined_fig.update_xaxes(showticklabels=False,
                              showgrid=False, zeroline=False, row=2, col=1)
    combined_fig.update_yaxes(showticklabels=False,
                              showgrid=False, zeroline=False, row=2, col=1)

    return combined_fig

# 10. Battle Analysis Through the Trilogy


def battle_analysis_through_trilogy(data):
    """Analyze the battles across the trilogy."""
    # Extract battle data
    battles = data['battles']
    timelines = data['timelines']

    battle_data = []

    # Get battle details
    for battle_id, battle in battles.items():
        # Try to determine which episode this battle is from
        episode = "Unknown"

        for episode_key, events in timelines.items():
            episode_name = f"Episode {episode_key.replace('episode_', '')}"

            # Check if this battle is mentioned in any event
            for event in events:
                if 'battle' in event and event['battle'] == battle['name']:
                    episode = episode_name
                    break

            if episode != "Unknown":
                break

        battle_data.append({
            'Name': battle['name'],
            'Episode': episode,
            'Outcome': battle['outcome'],
            'Casualties': battle['casualties']
        })

    battle_df = pd.DataFrame(battle_data)

    # Create bubble chart of battles
    fig = px.scatter(
        battle_df,
        x='Episode',
        y='Casualties',
        size='Casualties',
        color='Outcome',
        hover_name='Name',
        size_max=60,
        title='Battles Across the Star Wars Trilogy'
    )

    # Add battle details table
    table_fig = go.Figure(
        go.Table(
            header=dict(
                values=['Battle Name', 'Episode', 'Outcome', 'Casualties'],
                fill_color='paleturquoise',
                align='left'
            ),
            cells=dict(
                values=[
                    battle_df['Name'],
                    battle_df['Episode'],
                    battle_df['Outcome'],
                    battle_df['Casualties']
                ],
                fill_color='lavender',
                align='left'
            )
        )
    )

    # Combine visualizations
    combined_fig = make_subplots(
        rows=2, cols=1,
        specs=[[{"type": "scatter"}], [{"type": "table"}]],
        subplot_titles=("Battle Scale by Episode", "Battle Details"),
        row_heights=[0.6, 0.4],
        vertical_spacing=0.1
    )

    # Add the bubble chart
    for trace in fig.data:
        combined_fig.add_trace(trace, row=1, col=1)

    # Add the table
    combined_fig.add_trace(
        table_fig.data[0],
        row=2, col=1
    )

    combined_fig.update_layout(
        height=800,
        width=1200,
        title_text="Battle Analysis Through the Trilogy"
    )

    return combined_fig
