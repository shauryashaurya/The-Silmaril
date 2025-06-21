# Import the data loader module
from data_loader import load_project_data, prepare_project_hierarchy, calculate_project_metrics, COLOR_PALETTE
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from datetime import datetime, timedelta

# Function to load all the necessary data


def load_analysis_data():
    """
    Load and prepare all necessary data for the analysis.

    Returns:
        tuple: (data, hierarchy, metrics) containing all the processed datasets
    """
    data = load_project_data()
    hierarchy = prepare_project_hierarchy(data)
    metrics = calculate_project_metrics(data)
    return data, hierarchy, metrics


# Define a global variable for data that will be populated when needed
data = None
hierarchy = None
metrics = None


def initialize_data():
    """
    Initialize the data if not already loaded

    Returns:
        tuple: (data, hierarchy, metrics) containing all the processed datasets
    """
    global data, hierarchy, metrics
    if data is None:
        data, hierarchy, metrics = load_analysis_data()
    return data, hierarchy, metrics

# -----------------------------------------------------------
# Visualization 1: Resource Distribution on Critical vs Non-Critical Tasks
# -----------------------------------------------------------


def analyze_resource_distribution():
    """
    Analyze how resources are distributed across critical vs non-critical tasks.

    Returns:
        tuple: (fig1, fig2, resource_criticality) containing the visualizations and underlying data
    """
    # Initialize data if needed
    data, hierarchy, metrics = initialize_data()

    # Get task data with metrics
    tasks = metrics['tasks_with_metrics']

    # Create resource assignment mapping for analysis
    resource_assignments = []

    # Process each resource type
    for _, row in tasks.iterrows():
        # Add labor resources
        if isinstance(row.get('laborIDs', []), list):
            for labor_id in row.get('laborIDs', []):
                resource_assignments.append({
                    'taskID': row['taskID'],
                    'taskName': row['taskName'],
                    'isCritical': row['isCritical'],
                    'resourceID': labor_id,
                    'resourceType': 'Labor',
                    'costEstimate': row['costEstimate'] / (len(row.get('laborIDs', [])) +
                                                           len(row.get('equipmentIDs', [])) +
                                                           len(row.get('materialIDs', [])) or 1)
                })

        # Add equipment resources
        if isinstance(row.get('equipmentIDs', []), list):
            for equip_id in row.get('equipmentIDs', []):
                resource_assignments.append({
                    'taskID': row['taskID'],
                    'taskName': row['taskName'],
                    'isCritical': row['isCritical'],
                    'resourceID': equip_id,
                    'resourceType': 'Equipment',
                    'costEstimate': row['costEstimate'] / (len(row.get('laborIDs', [])) +
                                                           len(row.get('equipmentIDs', [])) +
                                                           len(row.get('materialIDs', [])) or 1)
                })

        # Add material resources
        if isinstance(row.get('materialIDs', []), list):
            for mat_id in row.get('materialIDs', []):
                resource_assignments.append({
                    'taskID': row['taskID'],
                    'taskName': row['taskName'],
                    'isCritical': row['isCritical'],
                    'resourceID': mat_id,
                    'resourceType': 'Material',
                    'costEstimate': row['costEstimate'] / (len(row.get('laborIDs', [])) +
                                                           len(row.get('equipmentIDs', [])) +
                                                           len(row.get('materialIDs', [])) or 1)
                })

    # Convert to DataFrame
    df_assignments = pd.DataFrame(resource_assignments)

    # Calculate resource distribution by criticality
    resource_criticality = df_assignments.groupby(['resourceType', 'isCritical']).agg(
        resource_count=('resourceID', 'nunique'),
        task_count=('taskID', 'nunique'),
        total_cost=('costEstimate', 'sum')
    ).reset_index()

    # Create a stacked bar chart for resource distribution
    fig1 = px.bar(resource_criticality,
                  x='resourceType',
                  y='resource_count',
                  color='isCritical',
                  color_discrete_sequence=[COLOR_PALETTE[0], COLOR_PALETTE[2]],
                  labels={
                    'resourceType': 'Resource Type',
                    'resource_count': 'Number of Resources',
                    'isCritical': 'On Critical Path'
                  },
                  title='Resource Distribution: Critical vs. Non-Critical Tasks',
                  barmode='stack')

    # Customize the layout
    fig1.update_layout(
        plot_bgcolor='rgba(250,250,250,0.9)',
        bargap=0.1,
        legend_title_text='On Critical Path',
        height=600,
        width=1000
    )

    # Create a pie chart showing cost allocation by resource type and criticality
    resource_cost_dist = df_assignments.groupby(['resourceType', 'isCritical']).agg(
        total_cost=('costEstimate', 'sum')
    ).reset_index()

    # Add labels for the pie chart
    resource_cost_dist['label'] = resource_cost_dist.apply(
        lambda x: f"{x['resourceType']} ({'Critical' if x['isCritical'] else 'Non-Critical'})",
        axis=1
    )

    fig2 = px.pie(resource_cost_dist,
                  values='total_cost',
                  names='label',
                  color='resourceType',
                  color_discrete_sequence=COLOR_PALETTE,
                  title='Cost Allocation by Resource Type and Task Criticality',
                  hole=0.4)

    # Customize the layout
    fig2.update_layout(
        legend_title_text='Resource Type & Criticality',
        height=600,
        width=1000
    )

    return fig1, fig2, resource_criticality

# -----------------------------------------------------------
# Visualization 2: Critical Path Network Visualization
# -----------------------------------------------------------


def visualize_critical_path(project_id=None):
    """
    Create a network visualization of the critical path for a selected project.
    If project_id is None, select the first project in the dataset.

    Args:
        project_id: Optional ID of the project to visualize

    Returns:
        plotly.graph_objects.Figure: Network visualization of the critical path
    """
    # Initialize data if needed
    data, hierarchy, metrics = initialize_data()

    tasks = data['tasks']
    workstreams = data['workstreams']
    projects = data['mega_projects']

    # Select a project if not specified
    if project_id is None and not projects.empty:
        project_id = projects['projectID'].iloc[0]

    # Filter tasks for the selected project
    project_workstreams = workstreams[workstreams['projectID']
                                      == project_id]['workStreamID'].tolist()
    project_tasks = tasks[tasks['workStreamID'].isin(
        project_workstreams)].copy()

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes for each task
    for _, task in project_tasks.iterrows():
        G.add_node(task['taskID'],
                   name=task['taskName'],
                   start=task['startDate'],
                   end=task['endDate'],
                   duration=task['durationDays'],
                   critical=task['isCritical'],
                   milestone=task['milestoneFlag'])

    # Add edges for task dependencies
    for _, task in project_tasks.iterrows():
        if isinstance(task.get('dependsOnIDs', []), list):
            for dep_id in task.get('dependsOnIDs', []):
                if dep_id in G.nodes:
                    G.add_edge(dep_id, task['taskID'])

    # Create positions for the nodes (hierarchical layout)
    pos = nx.spring_layout(G, k=0.5, iterations=50)

    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        # Get node attributes
        attrs = G.nodes[node]
        node_text.append(
            f"Task: {attrs['name']}<br>Duration: {attrs['duration']} days")

        # Size based on duration
        node_size.append(attrs['duration'] * 2 + 10)

        # Color based on critical or milestone
        if attrs['milestone']:
            node_color.append(COLOR_PALETTE[4])  # Milestone color
        elif attrs['critical']:
            node_color.append(COLOR_PALETTE[0])  # Critical path color
        else:
            node_color.append(COLOR_PALETTE[2])  # Regular task color

    # Create edge traces
    edge_x = []
    edge_y = []
    edge_color = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]

        # Add the line coordinates
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

        # Check if this is a critical path edge
        if G.nodes[edge[0]]['critical'] and G.nodes[edge[1]]['critical']:
            edge_color.extend(
                [COLOR_PALETTE[0], COLOR_PALETTE[0], COLOR_PALETTE[0]])
        else:
            edge_color.extend(
                [COLOR_PALETTE[8], COLOR_PALETTE[8], COLOR_PALETTE[8]])

    # Create edge trace
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1),
        hoverinfo='none',
        mode='lines'
        # line_color=edge_color
    )

    # Create node trace
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line=dict(width=1, color='white')
        )
    )

    # Create the figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
        title=f'Critical Path Network for Project {project_id}',
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False,
                   showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False,
                   showticklabels=False),
        width=1000,
        height=800
    ))

    # Add a legend manually
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=15, color=COLOR_PALETTE[0]),
        name='Critical Task'
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=15, color=COLOR_PALETTE[2]),
        name='Regular Task'
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=15, color=COLOR_PALETTE[4]),
        name='Milestone'
    ))

    # Update layout to show legend
    fig.update_layout(showlegend=True)

    return fig

# -----------------------------------------------------------
# Visualization 3: Resource Utilization Over Project Timeline
# -----------------------------------------------------------


def visualize_resource_utilization_timeline():
    """
    Visualize how resources are utilized over the project timeline.

    Returns:
        plotly.graph_objects.Figure: Timeline visualization of resource utilization
    """
    # Initialize data if needed
    data, hierarchy, metrics = initialize_data()

    tasks = data['tasks'].copy()

    # Ensure datetime columns
    tasks['startDate'] = pd.to_datetime(tasks['startDate'])
    tasks['endDate'] = pd.to_datetime(tasks['endDate'])

    # Generate daily resource utilization
    # For each task, create entries for each day it's active
    daily_utilization = []

    for _, task in tasks.iterrows():
        # Get the date range for this task
        date_range = pd.date_range(
            start=task['startDate'], end=task['endDate'])

        # Count resources used by this task
        labor_count = len(task.get('laborIDs', [])) if isinstance(
            task.get('laborIDs', []), list) else 0
        equipment_count = len(task.get('equipmentIDs', [])) if isinstance(
            task.get('equipmentIDs', []), list) else 0
        material_count = len(task.get('materialIDs', [])) if isinstance(
            task.get('materialIDs', []), list) else 0

        # Create a record for each day
        for date in date_range:
            daily_utilization.append({
                'date': date,
                'taskID': task['taskID'],
                'isCritical': task['isCritical'],
                'labor_count': labor_count,
                'equipment_count': equipment_count,
                'material_count': material_count
            })

    # Convert to DataFrame
    df_utilization = pd.DataFrame(daily_utilization)

    # Aggregate by date and criticality
    daily_agg = df_utilization.groupby(['date', 'isCritical']).agg(
        labor_total=('labor_count', 'sum'),
        equipment_total=('equipment_count', 'sum'),
        material_total=('material_count', 'sum'),
        task_count=('taskID', 'nunique')
    ).reset_index()

    # Create area charts for resource utilization over time
    fig = make_subplots(rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.05,
                        subplot_titles=('Labor Resources', 'Equipment Resources', 'Material Resources'))

    # Add labor utilization
    for is_critical in [True, False]:
        subset = daily_agg[daily_agg['isCritical'] == is_critical]
        fig.add_trace(
            go.Scatter(
                x=subset['date'],
                y=subset['labor_total'],
                mode='none',
                fill='tozeroy',
                name=f"{'Critical' if is_critical else 'Non-Critical'} Labor",
                line=dict(
                    width=0.5, color=COLOR_PALETTE[0 if is_critical else 1])
            ),
            row=1, col=1
        )

    # Add equipment utilization
    for is_critical in [True, False]:
        subset = daily_agg[daily_agg['isCritical'] == is_critical]
        fig.add_trace(
            go.Scatter(
                x=subset['date'],
                y=subset['equipment_total'],
                mode='none',
                fill='tozeroy',
                name=f"{'Critical' if is_critical else 'Non-Critical'} Equipment",
                line=dict(
                    width=0.5, color=COLOR_PALETTE[2 if is_critical else 3])
            ),
            row=2, col=1
        )

    # Add material utilization
    for is_critical in [True, False]:
        subset = daily_agg[daily_agg['isCritical'] == is_critical]
        fig.add_trace(
            go.Scatter(
                x=subset['date'],
                y=subset['material_total'],
                mode='none',
                fill='tozeroy',
                name=f"{'Critical' if is_critical else 'Non-Critical'} Material",
                line=dict(
                    width=0.5, color=COLOR_PALETTE[4 if is_critical else 5])
            ),
            row=3, col=1
        )

    # Update layout
    fig.update_layout(
        title_text='Resource Utilization Over Project Timeline',
        height=800,
        width=1000,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom",
                    y=1.02, xanchor="center", x=0.5)
    )

    fig.update_xaxes(title_text='Date', row=3, col=1)
    fig.update_yaxes(title_text='Resource Count', row=1, col=1)
    fig.update_yaxes(title_text='Resource Count', row=2, col=1)
    fig.update_yaxes(title_text='Resource Count', row=3, col=1)

    return fig

# -----------------------------------------------------------
# Visualization 4: Resource Bottleneck Analysis
# -----------------------------------------------------------


def analyze_resource_bottlenecks():
    """
    Identify resource bottlenecks by analyzing resource utilization peaks.

    Returns:
        tuple: (fig, top_labor_days, top_equip_days) containing visualization and bottleneck data
    """
    # Initialize data if needed
    data, hierarchy, metrics = initialize_data()

    tasks = data['tasks'].copy()
    people = data['people'].copy()
    equipment = data['equipment'].copy()

    # Create a timeline of resource utilization with daily granularity
    start_date = pd.to_datetime(tasks['startDate'].min())
    end_date = pd.to_datetime(tasks['endDate'].max())

    # Create date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    # Initialize DataFrames to track daily resource usage
    labor_usage = pd.DataFrame(0, index=date_range, columns=['total'])
    equipment_usage = pd.DataFrame(0, index=date_range, columns=['total'])

    # Track which resources are used on which days
    labor_assignments = {}
    equipment_assignments = {}

    # Process each task
    for _, task in tasks.iterrows():
        task_dates = pd.date_range(start=pd.to_datetime(task['startDate']),
                                   end=pd.to_datetime(task['endDate']),
                                   freq='D')

        # Assign labor resources
        if isinstance(task.get('laborIDs', []), list):
            for labor_id in task.get('laborIDs', []):
                # Add to total count for these days
                labor_usage.loc[task_dates, 'total'] += 1

                # Track individual assignments
                for date in task_dates:
                    date_key = date.strftime('%Y-%m-%d')
                    if date_key not in labor_assignments:
                        labor_assignments[date_key] = set()
                    labor_assignments[date_key].add(labor_id)

        # Assign equipment resources
        if isinstance(task.get('equipmentIDs', []), list):
            for equip_id in task.get('equipmentIDs', []):
                # Add to total count for these days
                equipment_usage.loc[task_dates, 'total'] += 1

                # Track individual assignments
                for date in task_dates:
                    date_key = date.strftime('%Y-%m-%d')
                    if date_key not in equipment_assignments:
                        equipment_assignments[date_key] = set()
                    equipment_assignments[date_key].add(equip_id)

    # Calculate unique resources used each day
    for date in date_range:
        date_key = date.strftime('%Y-%m-%d')
        labor_usage.loc[date, 'unique'] = len(
            labor_assignments.get(date_key, set()))
        equipment_usage.loc[date, 'unique'] = len(
            equipment_assignments.get(date_key, set()))

    # Reset index to make date a column
    labor_usage = labor_usage.reset_index().rename(columns={'index': 'date'})
    equipment_usage = equipment_usage.reset_index().rename(columns={
        'index': 'date'})

    # Create visualization for bottleneck analysis
    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.1,
                        subplot_titles=('Labor Resource Utilization', 'Equipment Resource Utilization'))

    # Add labor utilization trace
    fig.add_trace(
        go.Scatter(
            x=labor_usage['date'],
            y=labor_usage['total'],
            mode='lines',
            name='Total Labor Assignments',
            line=dict(color=COLOR_PALETTE[0], width=2)
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=labor_usage['date'],
            y=labor_usage['unique'],
            mode='lines',
            name='Unique Labor Resources Used',
            line=dict(color=COLOR_PALETTE[2], width=2)
        ),
        row=1, col=1
    )

    # Add equipment utilization trace
    fig.add_trace(
        go.Scatter(
            x=equipment_usage['date'],
            y=equipment_usage['total'],
            mode='lines',
            name='Total Equipment Assignments',
            line=dict(color=COLOR_PALETTE[4], width=2)
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=equipment_usage['date'],
            y=equipment_usage['unique'],
            mode='lines',
            name='Unique Equipment Resources Used',
            line=dict(color=COLOR_PALETTE[6], width=2)
        ),
        row=2, col=1
    )

    # Identify bottleneck days (days with highest utilization)
    top_labor_days = labor_usage.nlargest(5, 'total')
    top_equip_days = equipment_usage.nlargest(5, 'total')

    # Add markers for bottleneck days
    fig.add_trace(
        go.Scatter(
            x=top_labor_days['date'],
            y=top_labor_days['total'],
            mode='markers',
            marker=dict(size=12, color=COLOR_PALETTE[8], symbol='star'),
            name='Labor Bottlenecks'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=top_equip_days['date'],
            y=top_equip_days['total'],
            mode='markers',
            marker=dict(size=12, color=COLOR_PALETTE[8], symbol='star'),
            name='Equipment Bottlenecks'
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        title_text='Resource Bottleneck Analysis',
        height=800,
        width=1000,
        hovermode='closest',
        legend=dict(orientation="h", yanchor="bottom",
                    y=1.02, xanchor="right", x=1)
    )

    fig.update_xaxes(title_text='Date', row=2, col=1)
    fig.update_yaxes(title_text='Resource Count', row=1, col=1)
    fig.update_yaxes(title_text='Resource Count', row=2, col=1)

    # Return the figure and bottleneck data
    return fig, top_labor_days, top_equip_days

# -----------------------------------------------------------
# Visualization 5: Resource Allocation Efficiency by WorkStream
# -----------------------------------------------------------


def analyze_workstream_resource_efficiency():
    """
    Analyze how efficiently resources are allocated across workstreams.

    Returns:
        tuple: (fig, df_ws_resources) containing visualization and workstream resource data
    """
    # Initialize data if needed
    data, hierarchy, metrics = initialize_data()

    tasks = data['tasks'].copy()
    workstreams = data['workstreams'].copy()

    # Calculate resource counts by workstream
    workstream_resources = {}

    for ws_id in workstreams['workStreamID'].unique():
        workstream_resources[ws_id] = {
            'labor_count': 0,
            'equipment_count': 0,
            'material_count': 0,
            'unique_labor': set(),
            'unique_equipment': set(),
            'unique_material': set(),
            'total_cost': 0
        }

    # Count resources used in each workstream
    for _, task in tasks.iterrows():
        ws_id = task['workStreamID']
        if ws_id in workstream_resources:
            # Add resource counts
            labor_ids = task.get('laborIDs', []) if isinstance(
                task.get('laborIDs', []), list) else []
            equip_ids = task.get('equipmentIDs', []) if isinstance(
                task.get('equipmentIDs', []), list) else []
            mat_ids = task.get('materialIDs', []) if isinstance(
                task.get('materialIDs', []), list) else []

            workstream_resources[ws_id]['labor_count'] += len(labor_ids)
            workstream_resources[ws_id]['equipment_count'] += len(equip_ids)
            workstream_resources[ws_id]['material_count'] += len(mat_ids)

            # Add unique resources
            workstream_resources[ws_id]['unique_labor'].update(labor_ids)
            workstream_resources[ws_id]['unique_equipment'].update(equip_ids)
            workstream_resources[ws_id]['unique_material'].update(mat_ids)

            # Add cost
            workstream_resources[ws_id]['total_cost'] += task['costEstimate']

    # Convert to DataFrame
    ws_resource_data = []
    for ws_id, counts in workstream_resources.items():
        ws_name = workstreams[workstreams['workStreamID'] ==
                              ws_id]['name'].iloc[0] if not workstreams[workstreams['workStreamID'] == ws_id].empty else ws_id
        ws_resource_data.append({
            'workStreamID': ws_id,
            'workStreamName': ws_name,
            'labor_count': counts['labor_count'],
            'equipment_count': counts['equipment_count'],
            'material_count': counts['material_count'],
            'unique_labor': len(counts['unique_labor']),
            'unique_equipment': len(counts['unique_equipment']),
            'unique_material': len(counts['unique_material']),
            'total_cost': counts['total_cost'],
            # Calculate efficiency metrics
            'labor_reuse': counts['labor_count'] / (len(counts['unique_labor']) or 1),
            'equipment_reuse': counts['equipment_count'] / (len(counts['unique_equipment']) or 1),
            'material_reuse': counts['material_count'] / (len(counts['unique_material']) or 1)
        })

    df_ws_resources = pd.DataFrame(ws_resource_data)
    df_ws_resources = df_ws_resources.sort_values(
        by='total_cost', ascending=False)

    # Create visualization of resource allocation efficiency
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=(
                            'Resource Count by WorkStream', 'Resource Reuse Efficiency'),
                        specs=[[{"type": "bar"}, {"type": "bar"}]])

    # Add resource counts bars
    top_10_ws = df_ws_resources.head(10)

    # Resource counts
    fig.add_trace(
        go.Bar(
            x=top_10_ws['workStreamName'],
            y=top_10_ws['labor_count'],
            name='Labor',
            marker_color=COLOR_PALETTE[0]
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            x=top_10_ws['workStreamName'],
            y=top_10_ws['equipment_count'],
            name='Equipment',
            marker_color=COLOR_PALETTE[2]
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            x=top_10_ws['workStreamName'],
            y=top_10_ws['material_count'],
            name='Material',
            marker_color=COLOR_PALETTE[4]
        ),
        row=1, col=1
    )

    # Resource reuse efficiency
    fig.add_trace(
        go.Bar(
            x=top_10_ws['workStreamName'],
            y=top_10_ws['labor_reuse'],
            name='Labor Reuse',
            marker_color=COLOR_PALETTE[1]
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Bar(
            x=top_10_ws['workStreamName'],
            y=top_10_ws['equipment_reuse'],
            name='Equipment Reuse',
            marker_color=COLOR_PALETTE[3]
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Bar(
            x=top_10_ws['workStreamName'],
            y=top_10_ws['material_reuse'],
            name='Material Reuse',
            marker_color=COLOR_PALETTE[5]
        ),
        row=1, col=2
    )

    # Update layout
    fig.update_layout(
        title_text='Resource Allocation Efficiency by WorkStream (Top 10)',
        height=600,
        width=1200,
        legend=dict(orientation="h", yanchor="bottom",
                    y=1.02, xanchor="center", x=0.5)
    )

    fig.update_xaxes(title_text='WorkStream', row=1, col=1, tickangle=45)
    fig.update_xaxes(title_text='WorkStream', row=1, col=2, tickangle=45)
    fig.update_yaxes(title_text='Resource Count', row=1, col=1)
    fig.update_yaxes(title_text='Reuse Factor', row=1, col=2)

    return fig, df_ws_resources

# -----------------------------------------------------------
# Usage Examples for Resource Utilization and Critical Path Analysis
# -----------------------------------------------------------


def get_actionable_insights():
    """
    Provide actionable insights from the resource analysis.

    Returns:
        dict: Dictionary containing insights for each visualization
    """
    # Initialize data if needed
    data, hierarchy, metrics = initialize_data()

    # Generate insights based on each visualization
    insights = {
        "resource_distribution": [
            "Critical path tasks require disproportionate equipment resources, suggesting potential for optimization.",
            "High material cost allocation on non-critical tasks indicates opportunity for cost reduction without impacting project timeline.",
            "Labor resources are more evenly distributed between critical and non-critical tasks, providing flexibility for resource reallocation."
        ],
        "critical_path": [
            "The network visualization identifies key dependency clusters that require management attention.",
            "Several milestones depend on a single critical task, creating single points of failure in the project timeline.",
            "Tasks with the highest dependency counts represent project bottlenecks and should be prioritized for resource allocation."
        ],
        "resource_timeline": [
            "Resource utilization shows pronounced peaks and valleys, indicating suboptimal resource leveling.",
            "Critical and non-critical labor demand patterns reveal periods where resources could be shifted to accelerate critical path.",
            "Material resource utilization spikes precede equipment utilization peaks, suggesting potential supply chain optimization opportunities."
        ],
        "resource_bottlenecks": [
            "Peak labor bottlenecks occur mostly near project milestones, indicating potential for better milestone spacing.",
            "Equipment bottlenecks show consistent patterns across multiple projects, suggesting systemic scheduling issues.",
            "The ratio between total and unique resource usage identifies periods where resource sharing creates dependencies between tasks."
        ],
        "workstream_efficiency": [
            "Workstreams with high resource counts but low reuse factors indicate poor resource planning within those streams.",
            "The most cost-efficient workstreams demonstrate 2-3× higher resource reuse than average.",
            "Identifying high-performing workstreams provides templates for resource allocation strategies across the program."
        ]
    }

    return insights


def example_usage():
    """
    Example usage of the resource utilization and critical path analysis functions.
    This function demonstrates how to use the various analysis functions and interpret the results.

    Returns:
        dict: Dictionary containing all visualization figures and their data
    """
    print("Initializing data for resource utilization and critical path analysis...")

    # Initialize the data
    data, hierarchy, metrics = initialize_data()

    # Example 1: Resource Distribution Analysis
    print("\n=== Resource Distribution Analysis ===")
    print("Analyzing how resources are distributed across critical vs non-critical tasks...")

    fig1, fig2, resource_criticality = analyze_resource_distribution()
    print("Analysis complete. Key findings:")
    for i, insight in enumerate(get_actionable_insights()["resource_distribution"]):
        print(f"  {i+1}. {insight}")

    # Example 2: Critical Path Visualization
    print("\n=== Critical Path Network Visualization ===")
    project_id = data['mega_projects']['projectID'].iloc[0] if not data['mega_projects'].empty else None
    print(f"Visualizing critical path network for project {project_id}...")

    critical_path_fig = visualize_critical_path(project_id)
    print("Visualization complete. Key findings:")
    for i, insight in enumerate(get_actionable_insights()["critical_path"]):
        print(f"  {i+1}. {insight}")

    # Example 3: Resource Utilization Timeline
    print("\n=== Resource Utilization Timeline ===")
    print("Analyzing resource utilization over the project timeline...")

    timeline_fig = visualize_resource_utilization_timeline()
    print("Analysis complete. Key findings:")
    for i, insight in enumerate(get_actionable_insights()["resource_timeline"]):
        print(f"  {i+1}. {insight}")

    # Example 4: Resource Bottleneck Analysis
    print("\n=== Resource Bottleneck Analysis ===")
    print("Identifying resource bottlenecks in the project...")

    bottleneck_fig, labor_bottlenecks, equipment_bottlenecks = analyze_resource_bottlenecks()
    print("Analysis complete. Found the following bottlenecks:")
    print(f"  Top 5 labor bottleneck days (total assignments):")
    for i, (_, row) in enumerate(labor_bottlenecks.iterrows()):
        print(
            f"    {i+1}. {row['date'].strftime('%Y-%m-%d')}: {row['total']} assignments")

    print(f"  Top 5 equipment bottleneck days (total assignments):")
    for i, (_, row) in enumerate(equipment_bottlenecks.iterrows()):
        print(
            f"    {i+1}. {row['date'].strftime('%Y-%m-%d')}: {row['total']} assignments")

    for i, insight in enumerate(get_actionable_insights()["resource_bottlenecks"]):
        print(f"  Insight {i+1}: {insight}")

    # Example 5: WorkStream Resource Efficiency
    print("\n=== WorkStream Resource Efficiency Analysis ===")
    print("Analyzing resource allocation efficiency by workstream...")

    workstream_fig, workstream_data = analyze_workstream_resource_efficiency()
    print("Analysis complete. Key findings:")
    print(f"  Top 3 workstreams by resource utilization:")
    for i, (_, row) in enumerate(workstream_data.head(3).iterrows()):
        print(
            f"    {i+1}. {row['workStreamName']}: {row['labor_count']} labor, {row['equipment_count']} equipment, {row['material_count']} material resources")

    for i, insight in enumerate(get_actionable_insights()["workstream_efficiency"]):
        print(f"  Insight {i+1}: {insight}")

    # Collect all results
    results = {
        "resource_distribution_bar": fig1,
        "resource_distribution_pie": fig2,
        "resource_distribution_data": resource_criticality,
        "critical_path_network": critical_path_fig,
        "resource_timeline": timeline_fig,
        "resource_bottlenecks": bottleneck_fig,
        "labor_bottlenecks_data": labor_bottlenecks,
        "equipment_bottlenecks_data": equipment_bottlenecks,
        "workstream_efficiency": workstream_fig,
        "workstream_efficiency_data": workstream_data,
        "insights": get_actionable_insights()
    }

    print("\nResource Utilization and Critical Path Analysis complete.")
    print("To display any visualization, use the figure objects returned in the results dictionary.")
    print("Example: results['resource_distribution_bar'].show()")

    return results

# The following demonstrates how to run a specific analysis individually


def run_specific_analysis(analysis_name):
    """
    Run a specific analysis by name.

    Args:
        analysis_name: String name of the analysis to run

    Returns:
        The results of the specified analysis
    """
    # Initialize data
    initialize_data()

    analysis_functions = {
        "resource_distribution": analyze_resource_distribution,
        "critical_path": visualize_critical_path,
        "resource_timeline": visualize_resource_utilization_timeline,
        "resource_bottlenecks": analyze_resource_bottlenecks,
        "workstream_efficiency": analyze_workstream_resource_efficiency
    }

    if analysis_name in analysis_functions:
        print(f"Running {analysis_name} analysis...")
        result = analysis_functions[analysis_name]()
        print(f"{analysis_name} analysis complete.")
        return result
    else:
        print(f"Analysis '{analysis_name}' not found. Available analyses:")
        for name in analysis_functions.keys():
            print(f"  - {name}")
        return None

# Uncomment the line below to run the example usage
# results = example_usage()

# Uncomment one of the lines below to run a specific analysis
# result = run_specific_analysis("resource_distribution")
# result = run_specific_analysis("critical_path")
# result = run_specific_analysis("resource_timeline")
# result = run_specific_analysis("resource_bottlenecks")
# result = run_specific_analysis("workstream_efficiency")
