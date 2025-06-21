from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import os
from datetime import datetime
import json
import matplotlib.colors as mcolors
import random
from typing import List, Dict, Any, Tuple
import pyarrow as pa
import pyarrow.parquet as pq

pio.templates.default = "plotly_white"

# First, define this at the MODULE LEVEL (outside of any other function)


def process_dependency_chunk(task_chunk):
    """
    Process task dependencies for a chunk of tasks.
    This must be at module level for proper pickling.
    """
    links = []
    for task in task_chunk:
        if isinstance(task.get('dependsOnIDs'), str) and task['dependsOnIDs'] != '[]':
            deps = task['dependsOnIDs'].strip(
                '[]').replace("'", "").split(', ')
            for dep_id in deps:
                links.append({
                    'source': dep_id,
                    'target': task['id'],
                    'weight': 1
                })
    return links


def prepare_task_dependency_data(data):
    """
    Prepare task dependency data with sequential processing to avoid pickling issues.
    """
    tasks_df = data['tasks'].copy()  # Make a proper copy

    # Process dependencies sequentially - no parallel processing at all
    dependency_links = []
    for _, task in tasks_df.iterrows():
        if isinstance(task['dependsOnIDs'], str) and task['dependsOnIDs'] != '[]':
            deps = task['dependsOnIDs'].strip(
                '[]').replace("'", "").split(', ')
            for dep_id in deps:
                dependency_links.append({
                    'source': dep_id,
                    'target': task['id'],
                    'weight': 1
                })

    # Create node information efficiently with proper DataFrame copies
    task_nodes = tasks_df[['id', 'taskID', 'taskName',
                           'durationDays', 'isCritical', 'workStreamID']].copy()

    # Fix the dtype issue - create a new column instead of converting in-place
    task_nodes['is_critical'] = task_nodes['isCritical'].astype(int)
    # Remove the original column to avoid conflicts
    task_nodes = task_nodes.drop(columns=['isCritical'])

    # Get workstream and project info
    workstreams_df = data['workstreams'][[
        'workStreamID', 'name', 'projectID']].copy()
    projects_df = data['mega_projects'][['id', 'projectName']].copy()

    # Merge for workstream and project info using proper method
    task_nodes = (task_nodes
                  .merge(workstreams_df, on='workStreamID', how='left')
                  .merge(projects_df, left_on='projectID', right_on='id', how='left', suffixes=('', '_proj')))

    links_df = pd.DataFrame(dependency_links)

    # Calculate dependency counts efficiently
    if len(links_df) > 0:
        # Use value_counts for simple counting
        incoming_counts = links_df['target'].value_counts().reset_index()
        incoming_counts.columns = ['id', 'incoming_deps']

        outgoing_counts = links_df['source'].value_counts().reset_index()
        outgoing_counts.columns = ['id', 'outgoing_deps']

        # Efficient merges
        task_nodes = (task_nodes
                      .merge(incoming_counts, on='id', how='left')
                      .merge(outgoing_counts, on='id', how='left'))

        # Efficient null handling
        task_nodes['incoming_deps'] = task_nodes['incoming_deps'].fillna(0)
        task_nodes['outgoing_deps'] = task_nodes['outgoing_deps'].fillna(0)
        task_nodes['total_deps'] = task_nodes['incoming_deps'] + \
            task_nodes['outgoing_deps']
    else:
        task_nodes['incoming_deps'] = 0
        task_nodes['outgoing_deps'] = 0
        task_nodes['total_deps'] = 0

    # Save with compression
    links_df.to_parquet(
        f"{viz_data_path}task_dependency_links.parquet", compression='snappy')
    task_nodes.to_parquet(
        f"{viz_data_path}task_dependency_nodes.parquet", compression='snappy')

    return links_df, task_nodes


def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def load_all_data(data_path="./data/big/", use_parallel=False):
    """
    Load all data files with option for parallel loading.
    Note: Parallel loading is disabled by default due to potential issues with process pool.
    """
    import os

    file_paths = {
        'mega_projects': f"{data_path}mega_projects.csv",
        'workstreams': f"{data_path}workstreams.csv",
        'people': f"{data_path}people.csv",
        'equipment_list': f"{data_path}equipment_list.csv",
        'material_list': f"{data_path}material_list.csv",
        'suppliers': f"{data_path}suppliers.csv",
        'teams': f"{data_path}teams.csv",
        'procurement_orders': f"{data_path}procurement_orders.csv",
        'tasks': f"{data_path}tasks.csv"
    }

    # Check if files exist
    for key, path in file_paths.items():
        if not os.path.exists(path):
            print(f"Warning: File not found: {path}")

    # Use sequential loading as the default (most reliable) method
    data = {}
    for key, file_path in file_paths.items():
        try:
            print(f"Loading {key}...")
            data[key] = pd.read_csv(file_path)
            # Convert date columns to datetime
            for col in data[key].columns:
                if 'Date' in col:
                    data[key][col] = pd.to_datetime(data[key][col])
        except Exception as e:
            print(f"Error loading {key}: {str(e)}")
            # Create an empty DataFrame as a fallback
            data[key] = pd.DataFrame()

    return data


def generate_pastel_colors(n):
    colors = []
    for i in range(n):
        h = i / n
        s = 0.3 + 0.2 * random.random()
        l = 0.7 + 0.1 * random.random()
        rgb = mcolors.hsv_to_rgb([h, s, l])
        hex_color = mcolors.rgb2hex(rgb)
        colors.append(hex_color)
    return colors


viz_data_path = "./viz_data/"
create_directory_if_not_exists(viz_data_path)

data = load_all_data()

# Visualization 5: Material Cost and Inventory Analysis


def prepare_material_data(data):
    material_df = data['material_list']

    # Calculate inventory value for each row
    material_df['inventory_value'] = material_df['unitCost'] * \
        material_df['quantityOnHand']

    # Now perform the groupby aggregation
    material_data = material_df.groupby('materialType').agg(
        avg_unit_cost=('unitCost', 'mean'),
        total_inventory=('quantityOnHand', 'sum'),
        inventory_value=('inventory_value', 'sum'),
        count=('materialID', 'count')
    ).reset_index()

    material_data.to_parquet(f"{viz_data_path}material_analysis_data.parquet")
    return material_data


def visualize_material_cost_inventory(data_path=viz_data_path):
    material_data = pd.read_parquet(
        f"{data_path}material_analysis_data.parquet")

    material_data = material_data.sort_values(
        'inventory_value', ascending=False).head(15)
    colors = generate_pastel_colors(len(material_data))

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=material_data['materialType'],
            y=material_data['inventory_value'],
            marker=dict(color=colors),
            name='Inventory Value',
            hovertemplate='Type: %{x}<br>Inventory Value: $%{y:.2f}<extra></extra>'
        )
    )

    fig.add_trace(
        go.Scatter(
            x=material_data['materialType'],
            y=material_data['avg_unit_cost'],
            mode='markers',
            marker=dict(
                size=material_data['count'] /
                material_data['count'].max() * 30,
                color='rgba(255, 165, 0, 0.6)',
                line=dict(width=1, color='rgba(255, 165, 0, 1)')
            ),
            name='Avg Unit Cost (Size = Item Count)',
            yaxis='y2',
            hovertemplate='Type: %{x}<br>Avg Unit Cost: $%{y:.2f}<br>Item Count: %{marker.size}<extra></extra>'
        )
    )

    fig.update_layout(
        title='Top 15 Material Types by Inventory Value',
        xaxis=dict(
            title='Material Type',
            tickangle=45
        ),
        yaxis=dict(
            title='Inventory Value ($)',
            side='left'
        ),
        yaxis2=dict(
            title='Average Unit Cost ($)',
            side='right',
            overlaying='y',
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600
    )

    return fig

# Visualization 10: Resource Allocation Analysis
# multi-proc this - takes too long...
# Define the function at the module level for proper pickling


def process_task_allocations(task, people_dict, equipment_dict, material_dict):
    """
    Process allocations for a single task.
    All dictionaries must be passed as arguments since they can't be captured from closure.
    """
    task_allocations = []
    task_id = task['taskID']

    # Process labor
    if isinstance(task['laborIDs'], str) and task['laborIDs'] != '[]':
        labor_ids = task['laborIDs'].strip('[]').replace("'", "").split(', ')
        for labor_id in labor_ids:
            if labor_id in people_dict:
                person = people_dict[labor_id]
                task_allocations.append({
                    'taskID': task_id,
                    'resourceID': labor_id,
                    'resourceType': 'Labor',
                    'skillType': person['skillType'],
                    'cost': task['durationDays'] * 8 * person['hourlyRate']
                })

    # Process equipment
    if isinstance(task['equipmentIDs'], str) and task['equipmentIDs'] != '[]':
        equipment_ids = task['equipmentIDs'].strip(
            '[]').replace("'", "").split(', ')
        for equip_id in equipment_ids:
            if equip_id in equipment_dict:
                equip = equipment_dict[equip_id]
                task_allocations.append({
                    'taskID': task_id,
                    'resourceID': equip_id,
                    'resourceType': 'Equipment',
                    'equipmentType': equip['equipmentType'],
                    'cost': task['durationDays'] * equip['dailyRentalCost']
                })

    # Process material
    if isinstance(task['materialIDs'], str) and task['materialIDs'] != '[]':
        material_ids = task['materialIDs'].strip(
            '[]').replace("'", "").split(', ')
        for mat_id in material_ids:
            if mat_id in material_dict:
                mat = material_dict[mat_id]
                task_allocations.append({
                    'taskID': task_id,
                    'resourceID': mat_id,
                    'resourceType': 'Material',
                    'materialType': mat['materialType'],
                    # Assuming average quantity of 100
                    'cost': mat['unitCost'] * 100
                })

    return task_allocations


def prepare_resource_allocation_data(data):
    """
    Prepare resource allocation data with improved performance.
    """
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor

    tasks_df = data['tasks']
    people_df = data['people']
    equipment_df = data['equipment_list']
    material_df = data['material_list']

    # Pre-process data to dictionary lookups for faster access
    # Convert DataFrame rows to dictionaries for easier pickling
    people_dict = {person['id']: person.to_dict()
                   for _, person in people_df.iterrows()}
    equipment_dict = {equip['id']: equip.to_dict()
                      for _, equip in equipment_df.iterrows()}
    material_dict = {mat['id']: mat.to_dict()
                     for _, mat in material_df.iterrows()}

    # Disable parallel processing by default for safer operation
    use_parallel = False

    # Process allocations - now with task and dictionaries as arguments
    # Use parallel processing if multiple cores available and it's enabled
    if use_parallel and mp.cpu_count() > 1:
        all_allocations = []
        try:
            with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
                # Create a wrapper function that partially applies the dictionaries
                def process_task_wrapper(task):
                    return process_task_allocations(task, people_dict, equipment_dict, material_dict)

                # Process in chunks for better efficiency
                tasks_list = [task.to_dict()
                              for _, task in tasks_df.iterrows()]
                chunk_size = max(1, len(tasks_list) // (mp.cpu_count() * 2))
                for i in range(0, len(tasks_list), chunk_size):
                    chunk = tasks_list[i:i+chunk_size]
                    chunk_results = list(executor.map(
                        process_task_wrapper, chunk))
                    for result in chunk_results:
                        all_allocations.extend(result)
        except Exception as e:
            print(
                f"Parallel processing failed: {str(e)}. Falling back to sequential processing.")
            all_allocations = []
            for _, task in tasks_df.iterrows():
                all_allocations.extend(process_task_allocations(
                    task.to_dict(), people_dict, equipment_dict, material_dict))
    else:
        # Sequential processing
        all_allocations = []
        for _, task in tasks_df.iterrows():
            all_allocations.extend(process_task_allocations(
                task.to_dict(), people_dict, equipment_dict, material_dict))

    # Create DataFrame from allocations
    all_resources_df = pd.DataFrame(all_allocations)

    # Use more efficient aggregation with pre-computed columns
    if len(all_resources_df) > 0:
        # Aggregate by resource type
        resource_summary = all_resources_df.groupby('resourceType').agg({
            'cost': 'sum',
            'taskID': 'count'
        }).reset_index().rename(columns={'taskID': 'allocation_count', 'cost': 'total_cost'})

        # Aggregate by specific types
        labor_df = all_resources_df[all_resources_df['resourceType'] == 'Labor']
        equipment_df = all_resources_df[all_resources_df['resourceType'] == 'Equipment']
        material_df = all_resources_df[all_resources_df['resourceType'] == 'Material']

        # Process each resource type
        def process_resource_type(df, type_col, resource_type):
            if len(df) > 0:
                summary = df.groupby(type_col).agg({
                    'cost': 'sum',
                    'taskID': 'count'
                }).reset_index().rename(columns={
                    type_col: 'specificType',
                    'taskID': 'allocation_count',
                    'cost': 'total_cost'
                })
                summary['resourceType'] = resource_type
                return summary
            return pd.DataFrame(columns=['specificType', 'total_cost', 'allocation_count', 'resourceType'])

        labor_summary = process_resource_type(labor_df, 'skillType', 'Labor')
        equipment_summary = process_resource_type(
            equipment_df, 'equipmentType', 'Equipment')
        material_summary = process_resource_type(
            material_df, 'materialType', 'Material')

        specific_summary = pd.concat(
            [labor_summary, equipment_summary, material_summary])
    else:
        resource_summary = pd.DataFrame(
            columns=['resourceType', 'total_cost', 'allocation_count'])
        specific_summary = pd.DataFrame(
            columns=['specificType', 'total_cost', 'allocation_count', 'resourceType'])

    # Use parquet compression for faster I/O
    resource_summary.to_parquet(
        f"{viz_data_path}resource_summary.parquet", compression='snappy')
    specific_summary.to_parquet(
        f"{viz_data_path}specific_resource_summary.parquet", compression='snappy')

    return resource_summary, specific_summary


def visualize_resource_allocation(data_path=viz_data_path):
    resource_summary = pd.read_parquet(f"{data_path}resource_summary.parquet")
    specific_summary = pd.read_parquet(
        f"{data_path}specific_resource_summary.parquet")

    # Sort specific resources by cost within each resource type
    specific_summary = specific_summary.sort_values(
        ['resourceType', 'total_cost'], ascending=[True, False])

    # Generate colors
    resource_colors = {
        'Labor': '#FF9AA2',      # Soft red
        'Equipment': '#FFDAC1',  # Soft orange
        'Material': '#B5EAD7'    # Soft green
    }

    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"colspan": 2, "type": "treemap"}, None]],
        subplot_titles=(
            'Resource Cost Distribution',
            'Top Resource Allocations by Count',
            'Detailed Resource Cost Breakdown (Treemap)'
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )

    # Top left: Pie chart for resource types
    fig.add_trace(
        go.Pie(
            labels=resource_summary['resourceType'],
            values=resource_summary['total_cost'],
            hole=0.4,
            marker=dict(colors=[resource_colors.get(t, '#CCCCCC')
                        for t in resource_summary['resourceType']]),
            textinfo='percent+label',
            hovertemplate='Resource Type: %{label}<br>Total Cost: $%{value:.2f}<br>Allocations: %{customdata}<extra></extra>',
            customdata=resource_summary['allocation_count']
        ),
        row=1, col=1
    )

    # Top right: Bar chart for top resource allocations
    top_specific = specific_summary.sort_values(
        'allocation_count', ascending=False).head(10)

    fig.add_trace(
        go.Bar(
            y=top_specific['specificType'],
            x=top_specific['allocation_count'],
            orientation='h',
            marker=dict(
                color=[resource_colors.get(t, '#CCCCCC')
                       for t in top_specific['resourceType']],
                line=dict(width=1, color='rgba(0, 0, 0, 0.3)')
            ),
            customdata=np.stack(
                (top_specific['total_cost'], top_specific['resourceType']), axis=-1),
            hovertemplate='Type: %{y}<br>Allocations: %{x}<br>Total Cost: $%{customdata[0]:.2f}<br>Resource: %{customdata[1]}<extra></extra>'
        ),
        row=1, col=2
    )

    # Bottom: Treemap for detailed breakdown
    treemap_data = pd.DataFrame({
        'Resource': specific_summary['resourceType'] + ' - ' + specific_summary['specificType'],
        'ResourceType': specific_summary['resourceType'],
        'SpecificType': specific_summary['specificType'],
        'Cost': specific_summary['total_cost'],
        'Allocations': specific_summary['allocation_count']
    })

    fig.add_trace(
        go.Treemap(
            labels=treemap_data['SpecificType'],
            parents=[' ' + t for t in treemap_data['ResourceType']],
            values=treemap_data['Cost'],
            branchvalues='total',
            marker=dict(
                colors=[resource_colors.get(t, '#CCCCCC')
                        for t in treemap_data['ResourceType']],
                line=dict(width=0.5, color='rgba(0, 0, 0, 0.3)')
            ),
            textinfo='label+value',
            hovertemplate='Type: %{label}<br>Total Cost: $%{value:.2f}<br>Allocations: %{customdata}<extra></extra>',
            customdata=treemap_data['Allocations']
        ),
        row=2, col=1
    )

    fig.update_layout(
        title='Resource Allocation Analysis',
        height=900,
        showlegend=False
    )

    fig.update_xaxes(title_text='Allocation Count', row=1, col=2)

    return fig

# Visualization 11: Project Schedule and Milestone Analysis


def prepare_project_schedule_data(data):
    """
    Prepare project schedule data with proper DataFrame handling.
    """
    tasks_df = data['tasks'].copy()  # Make a proper copy
    workstreams_df = data['workstreams'].copy()
    projects_df = data['mega_projects'].copy()

    # Convert boolean flags to numeric for easier aggregation
    tasks_df.loc[:, 'milestone_flag'] = tasks_df['milestoneFlag'].astype(int)
    tasks_df.loc[:, 'critical_flag'] = tasks_df['isCritical'].astype(int)

    # Select columns and create a proper copy
    tasks_with_milestone = tasks_df[['taskID', 'taskName', 'startDate', 'endDate', 'durationDays',
                                     'workStreamID', 'milestone_flag', 'critical_flag']].copy()

    # Convert dates using loc for proper assignment
    tasks_with_milestone.loc[:, 'startDate'] = pd.to_datetime(
        tasks_with_milestone['startDate'])
    tasks_with_milestone.loc[:, 'endDate'] = pd.to_datetime(
        tasks_with_milestone['endDate'])

    # Merge operations create new DataFrames, so no need for copy/loc
    tasks_with_ws = tasks_with_milestone.merge(
        workstreams_df[['workStreamID', 'projectID', 'name']],
        on='workStreamID',
        how='left'
    ).rename(columns={'name': 'workstreamName'})

    tasks_with_project = tasks_with_ws.merge(
        projects_df[['id', 'projectName']],
        left_on='projectID',
        right_on='id',
        how='left'
    )

    # Filter for milestones
    milestones = tasks_with_project[tasks_with_project['milestone_flag'] == 1].copy(
    )

    # Prepare task counts by month
    tasks_with_project.loc[:, 'month'] = tasks_with_project['startDate'].dt.to_period(
        'M').astype(str)
    task_count_by_month = tasks_with_project.groupby(['month', 'projectName']).agg(
        task_count=('taskID', 'count'),
        critical_count=('critical_flag', 'sum')
    ).reset_index()

    # Prepare workstream schedule with proper copy
    workstream_schedule = workstreams_df[[
        'workStreamID', 'name', 'startDate', 'endDate', 'projectID']].copy()

    # Convert dates and calculate duration using loc
    workstream_schedule.loc[:, 'startDate'] = pd.to_datetime(
        workstream_schedule['startDate'])
    workstream_schedule.loc[:, 'endDate'] = pd.to_datetime(
        workstream_schedule['endDate'])
    workstream_schedule.loc[:, 'duration'] = (
        workstream_schedule['endDate'] - workstream_schedule['startDate']).dt.days

    # Merge to get project names
    workstream_schedule = workstream_schedule.merge(
        projects_df[['id', 'projectName']],
        left_on='projectID',
        right_on='id',
        how='left'
    )

    # Save data
    tasks_with_project.to_parquet(f"{viz_data_path}tasks_with_project.parquet")
    milestones.to_parquet(f"{viz_data_path}project_milestones.parquet")
    task_count_by_month.to_parquet(
        f"{viz_data_path}task_count_by_month.parquet")
    workstream_schedule.to_parquet(
        f"{viz_data_path}workstream_schedule.parquet")

    return tasks_with_project, milestones, task_count_by_month, workstream_schedule


def visualize_project_schedule(data_path=viz_data_path):
    tasks = pd.read_parquet(f"{data_path}tasks_with_project.parquet")
    milestones = pd.read_parquet(f"{data_path}project_milestones.parquet")
    task_count = pd.read_parquet(f"{data_path}task_count_by_month.parquet")
    workstreams = pd.read_parquet(f"{data_path}workstream_schedule.parquet")

    # Fix datetime columns
    tasks['startDate'] = pd.to_datetime(tasks['startDate'])
    tasks['endDate'] = pd.to_datetime(tasks['endDate'])
    milestones['startDate'] = pd.to_datetime(milestones['startDate'])
    milestones['endDate'] = pd.to_datetime(milestones['endDate'])
    workstreams['startDate'] = pd.to_datetime(workstreams['startDate'])
    workstreams['endDate'] = pd.to_datetime(workstreams['endDate'])

    # Generate project colors
    projects = tasks['projectName'].unique()
    project_colors = generate_pastel_colors(len(projects))
    project_color_map = dict(zip(projects, project_colors))

    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"colspan": 2, "type": "scatter"}, None],
               [{"type": "bar"}, {"type": "scatter"}]],
        subplot_titles=(
            'Project Schedule Gantt Chart with Milestones',
            'Task Count by Month',
            'Workstream Duration Analysis'
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )

    # Top: Gantt chart for workstreams with milestone markers
    sorted_workstreams = workstreams.sort_values(['projectName', 'startDate'])

    for i, ws in sorted_workstreams.iterrows():
        project_color = project_color_map.get(ws['projectName'], '#CCCCCC')

        fig.add_trace(
            go.Bar(
                x=[ws['duration']],
                y=[ws['name']],
                orientation='h',
                base=ws['startDate'],
                marker=dict(
                    color=project_color,
                    line=dict(width=1, color='rgba(0, 0, 0, 0.3)')
                ),
                name=ws['projectName'],
                showlegend=False,
                hovertemplate='Workstream: %{y}<br>Start: %{base}<br>End: %{x}<br>Duration: %{customdata} days<extra></extra>',
                customdata=[ws['duration']]
            ),
            row=1, col=1
        )

    # Add milestone markers
    for i, milestone in milestones.iterrows():
        project_color = project_color_map.get(
            milestone['projectName'], '#CCCCCC')

        fig.add_trace(
            go.Scatter(
                x=[milestone['endDate']],
                y=[milestone['workstreamName']],
                mode='markers',
                marker=dict(
                    symbol='diamond',
                    size=12,
                    color=project_color,
                    line=dict(width=2, color='black')
                ),
                name='Milestone',
                showlegend=False,
                hovertemplate='Milestone: %{text}<br>Date: %{x}<extra></extra>',
                text=[milestone['taskName']]
            ),
            row=1, col=1
        )

    # Bottom left: Task count by month
    months = sorted(task_count['month'].unique())

    for project in projects:
        project_data = task_count[task_count['projectName'] == project]
        if len(project_data) > 0:
            project_color = project_color_map.get(project, '#CCCCCC')

            fig.add_trace(
                go.Bar(
                    x=project_data['month'],
                    y=project_data['task_count'],
                    name=project,
                    marker=dict(color=project_color),
                    hovertemplate='Month: %{x}<br>Tasks: %{y}<br>Critical: %{customdata}<extra></extra>',
                    customdata=project_data['critical_count']
                ),
                row=2, col=1
            )

    # Bottom right: Workstream duration analysis
    fig.add_trace(
        go.Box(
            x=workstreams['projectName'],
            y=workstreams['duration'],
            marker=dict(
                color=[project_color_map.get(p, '#CCCCCC')
                       for p in workstreams['projectName']]
            ),
            boxmean=True,
            notched=True,
            hovertemplate='Project: %{x}<br>Duration: %{y} days<extra></extra>'
        ),
        row=2, col=2
    )

    # Add project legend
    for project in projects:
        project_color = project_color_map.get(project, '#CCCCCC')

        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=10, color=project_color),
                name=project,
                showlegend=True
            ),
            row=1, col=1
        )

    fig.update_layout(
        title='Project Schedule and Milestone Analysis',
        height=900,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_xaxes(title_text='Date', row=1, col=1)
    fig.update_xaxes(title_text='Month', row=2, col=1, tickangle=45)
    fig.update_xaxes(title_text='Project', row=2, col=2)

    fig.update_yaxes(title_text='Workstream', row=1, col=1)
    fig.update_yaxes(title_text='Task Count', row=2, col=1)
    fig.update_yaxes(title_text='Duration (Days)', row=2, col=2)

    return fig

# Visualization 19: Project Risk Assessment Dashboard


# Use parallel processing when appropriate

# Set seed for reproducibility
np.random.seed(42)

# Pre-calculate dependency lengths


def get_dependency_length(dep_str):
    if isinstance(dep_str, str) and dep_str != '[]':
        return len(dep_str.strip('[]').replace("'", "").split(', '))
    return 0

# Process projects in parallel


def process_project(project):
    project_id = project['id']

    # Get project workstreams
    project_ws = project_workstreams.get(project_id, [])

    if len(project_ws) == 0:
        return None

    # Get tasks for this project efficiently
    project_tasks_list = []
    for ws in project_ws:
        ws_tasks = workstream_tasks.get(ws['id'], [])
        if ws_tasks:
            project_tasks_list.extend(ws_tasks)

    if len(project_tasks_list) == 0:
        return None

    # Create DataFrame only once
    project_tasks_df = pd.DataFrame(project_tasks_list)

    # Calculate metrics efficiently
    critical_task_count = project_tasks_df['critical_flag'].sum()
    total_task_count = len(project_tasks_df)
    critical_ratio = critical_task_count / \
        total_task_count if total_task_count > 0 else 0

    # Efficient dependency calculation
    total_deps = project_tasks_df['dependency_count'].sum()
    avg_dependencies = total_deps / total_task_count if total_task_count > 0 else 0

    # Other metrics
    avg_duration = project_tasks_df['durationDays'].mean()

    # Calculate budget utilization
    total_ws_budget = sum(ws['budgetAllocated'] for ws in project_ws)
    budget_utilization = total_ws_budget / \
        project['overallBudget'] if project['overallBudget'] > 0 else 0

    # Calculate synthetic risk scores
    np.random.seed(int(project_id.replace('proj_', ''))
                   if isinstance(project_id, str) else 42)
    schedule_risk = critical_ratio * 0.6 + avg_dependencies / 5 * 0.4
    budget_risk = (budget_utilization * 0.5) + (np.random.random() * 0.5)
    resource_risk = np.random.random()
    scope_risk = avg_dependencies / 5 * 0.7 + np.random.random() * 0.3

    # Overall risk is weighted average
    overall_risk = (
        schedule_risk * 0.3 +
        budget_risk * 0.25 +
        resource_risk * 0.2 +
        scope_risk * 0.25
    )

    return {
        'projectID': project_id,
        'projectName': project['projectName'],
        'critical_ratio': critical_ratio,
        'avg_dependencies': avg_dependencies,
        'avg_duration': avg_duration,
        'budget_utilization': budget_utilization,
        'schedule_risk': min(schedule_risk, 1.0),
        'budget_risk': min(budget_risk, 1.0),
        'resource_risk': min(resource_risk, 1.0),
        'scope_risk': min(scope_risk, 1.0),
        'overall_risk': min(overall_risk, 1.0)
    }


def prepare_project_risk_data(data):
    projects_df = data['mega_projects']
    workstreams_df = data['workstreams']
    tasks_df = data['tasks'].copy()

    # Convert boolean isCritical to numeric for efficient calculations
    tasks_df['critical_flag'] = tasks_df['isCritical'].astype(int)

    # Pre-process relationships for faster lookups
    project_workstreams = {}
    for _, ws in workstreams_df.iterrows():
        project_id = ws['projectID']
        if project_id not in project_workstreams:
            project_workstreams[project_id] = []
        project_workstreams[project_id].append(ws)

    workstream_tasks = {}
    for _, task in tasks_df.iterrows():
        ws_id = task['workStreamID']
        if ws_id not in workstream_tasks:
            workstream_tasks[ws_id] = []
        workstream_tasks[ws_id].append(task)

    tasks_df['dependency_count'] = tasks_df['dependsOnIDs'].apply(
        get_dependency_length)

    if mp.cpu_count() > 1 and len(projects_df) > 10:
        with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
            results = list(executor.map(process_project, [
                           project for _, project in projects_df.iterrows()]))
            project_risk = [r for r in results if r is not None]
    else:
        project_risk = []
        for _, project in projects_df.iterrows():
            result = process_project(project)
            if result:
                project_risk.append(result)

    project_risk_df = pd.DataFrame(project_risk)

    # Save with compression
    project_risk_df.to_parquet(
        f"{viz_data_path}project_risk_assessment.parquet", compression='snappy')

    return project_risk_df

# Visualization 20: Procurement Order Analysis with Supplier Network


def prepare_procurement_network_data(data):
    po_df = data['procurement_orders']
    suppliers_df = data['suppliers']
    projects_df = data['mega_projects']
    material_df = data['material_list']
    equipment_df = data['equipment_list']

    # Merge procurement orders with suppliers and projects
    po_with_info = po_df.merge(
        suppliers_df[['id', 'supplierID', 'supplierName', 'location']],
        left_on='supplierID',
        right_on='id',
        how='left',
        suffixes=('', '_sup')
    )

    po_with_info = po_with_info.merge(
        projects_df[['id', 'projectID', 'projectName']],
        left_on='belongsToProjectID',
        right_on='id',
        how='left',
        suffixes=('', '_proj')
    )

    # Extract resource information
    resource_info = []

    for _, po in po_with_info.iterrows():
        if isinstance(po['resourceIDs'], str) and po['resourceIDs'] != '[]':
            resource_ids = po['resourceIDs'].strip(
                '[]').replace("'", "").split(', ')

            for res_id in resource_ids:
                # Check if it's a material
                if res_id.startswith('mat_'):
                    material = material_df[material_df['id'] == res_id]
                    if len(material) > 0:
                        resource_info.append({
                            'order_number': po['orderNumber'],
                            'resource_id': res_id,
                            'resource_name': material['materialName'].values[0],
                            'resource_type': 'Material',
                            'supplier_id': po['supplierID'],
                            'supplier_name': po['supplierName'],
                            'project_id': po['belongsToProjectID'],
                            'project_name': po.get('projectName', 'Unknown'),
                            'order_date': po['orderDate'],
                            'order_cost': po['totalCost']
                        })

                # Check if it's equipment
                elif res_id.startswith('equip_'):
                    equipment = equipment_df[equipment_df['id'] == res_id]
                    if len(equipment) > 0:
                        resource_info.append({
                            'order_number': po['orderNumber'],
                            'resource_id': res_id,
                            'resource_name': equipment['equipmentName'].values[0],
                            'resource_type': 'Equipment',
                            'supplier_id': po['supplierID'],
                            'supplier_name': po['supplierName'],
                            'project_id': po['belongsToProjectID'],
                            'project_name': po.get('projectName', 'Unknown'),
                            'order_date': po['orderDate'],
                            'order_cost': po['totalCost']
                        })

    resource_df = pd.DataFrame(resource_info)

    # Create supplier-project network links
    if len(resource_df) > 0:
        supplier_project_links = resource_df.groupby(['supplier_id', 'supplier_name', 'project_id', 'project_name']).agg(
            order_count=('order_number', 'count'),
            total_cost=('order_cost', 'sum')
        ).reset_index()
    else:
        supplier_project_links = pd.DataFrame(columns=[
            'supplier_id', 'supplier_name', 'project_id', 'project_name', 'order_count', 'total_cost'
        ])

    # Create supplier-resource type links
    if len(resource_df) > 0:
        supplier_resource_links = resource_df.groupby(['supplier_id', 'supplier_name', 'resource_type']).agg(
            resource_count=('resource_id', 'count'),
            total_cost=('order_cost', 'sum')
        ).reset_index()
    else:
        supplier_resource_links = pd.DataFrame(columns=[
            'supplier_id', 'supplier_name', 'resource_type', 'resource_count', 'total_cost'
        ])

    # Save data
    supplier_project_links.to_parquet(
        f"{viz_data_path}supplier_project_links.parquet")
    supplier_resource_links.to_parquet(
        f"{viz_data_path}supplier_resource_links.parquet")

    return supplier_project_links, supplier_resource_links


def visualize_procurement_network(data_path=viz_data_path):
    supplier_project = pd.read_parquet(
        f"{data_path}supplier_project_links.parquet")
    supplier_resource = pd.read_parquet(
        f"{data_path}supplier_resource_links.parquet")

    # Create a combined visualization
    fig = make_subplots(
        rows=2, cols=2,
        specs=[
            [{"colspan": 2, "type": "scatter"}, None],
            [{"type": "bar"}, {"type": "pie"}]
        ],
        subplot_titles=(
            'Supplier-Project Network Visualization',
            'Top Suppliers by Total Order Value',
            'Resource Type Distribution by Supplier'
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )

    # Top: Network visualization
    if len(supplier_project) == 0:
        # No data available
        fig.add_trace(
            go.Scatter(
                x=[0],
                y=[0],
                mode='text',
                text=['No procurement network data available'],
                textfont=dict(size=14),
                showlegend=False
            ),
            row=1, col=1
        )
    else:
        # Create a simple network layout
        # Position suppliers on the left, projects on the right
        unique_suppliers = supplier_project['supplier_name'].unique()
        unique_projects = supplier_project['project_name'].unique()

        # Create node positions
        supplier_y = np.linspace(0, 1, len(unique_suppliers))
        project_y = np.linspace(0, 1, len(unique_projects))

        supplier_positions = {sup: (0.1, y)
                              for sup, y in zip(unique_suppliers, supplier_y)}
        project_positions = {proj: (0.9, y)
                             for proj, y in zip(unique_projects, project_y)}

        # Generate colors
        supplier_colors = generate_pastel_colors(len(unique_suppliers))
        supplier_color_map = dict(zip(unique_suppliers, supplier_colors))

        # Add supplier nodes
        for supplier, (x, y) in supplier_positions.items():
            fig.add_trace(
                go.Scatter(
                    x=[x],
                    y=[y],
                    mode='markers+text',
                    marker=dict(
                        size=15,
                        color=supplier_color_map.get(supplier, '#CCCCCC'),
                        line=dict(width=1, color='black')
                    ),
                    text=[supplier],
                    textposition='middle left',
                    name=supplier,
                    showlegend=False,
                    hoverinfo='text',
                    hovertext=[f'Supplier: {supplier}']
                ),
                row=1, col=1
            )

        # Add project nodes
        for project, (x, y) in project_positions.items():
            fig.add_trace(
                go.Scatter(
                    x=[x],
                    y=[y],
                    mode='markers+text',
                    marker=dict(
                        size=15,
                        color='rgba(70, 130, 180, 0.7)',
                        symbol='square',
                        line=dict(width=1, color='black')
                    ),
                    text=[project],
                    textposition='middle right',
                    name=project,
                    showlegend=False,
                    hoverinfo='text',
                    hovertext=[f'Project: {project}']
                ),
                row=1, col=1
            )

        # Add links
        for _, link in supplier_project.iterrows():
            supplier = link['supplier_name']
            project = link['project_name']

            if supplier in supplier_positions and project in project_positions:
                sup_x, sup_y = supplier_positions[supplier]
                proj_x, proj_y = project_positions[project]

                # Link width based on cost
                width = 1 + 5 * (link['total_cost'] /
                                 supplier_project['total_cost'].max())

                fig.add_trace(
                    go.Scatter(
                        x=[sup_x, proj_x],
                        y=[sup_y, proj_y],
                        mode='lines',
                        line=dict(
                            width=width,
                            color=supplier_color_map.get(supplier, '#CCCCCC'),
                            shape='spline'
                        ),
                        opacity=0.6,
                        showlegend=False,
                        hoverinfo='text',
                        hovertext=[
                            f'Supplier: {supplier}<br>Project: {project}<br>Orders: {link["order_count"]}<br>Value: ${link["total_cost"]:.2f}']
                    ),
                    row=1, col=1
                )

    # Bottom left: Top suppliers bar chart
    if len(supplier_project) > 0:
        top_suppliers = supplier_project.groupby(
            'supplier_name')['total_cost'].sum().reset_index()
        top_suppliers = top_suppliers.sort_values(
            'total_cost', ascending=False).head(10)

        fig.add_trace(
            go.Bar(
                x=top_suppliers['supplier_name'],
                y=top_suppliers['total_cost'],
                marker=dict(
                    color=[supplier_color_map.get(
                        sup, '#CCCCCC') for sup in top_suppliers['supplier_name']],
                    line=dict(width=1, color='rgba(0, 0, 0, 0.3)')
                ),
                hovertemplate='Supplier: %{x}<br>Total Value: $%{y:.2f}<extra></extra>'
            ),
            row=2, col=1
        )
    else:
        # No data available
        fig.add_trace(
            go.Bar(
                x=['No Data'],
                y=[0],
                marker=dict(color='lightgray')
            ),
            row=2, col=1
        )

    # Bottom right: Resource type distribution by supplier
    if len(supplier_resource) > 0:
        resource_by_supplier = supplier_resource.pivot_table(
            values='total_cost',
            index='supplier_name',
            columns='resource_type',
            aggfunc='sum',
            fill_value=0
        )

        # Get top suppliers for pie chart
        top_suppliers_list = supplier_project.groupby(
            'supplier_name')['total_cost'].sum().nlargest(5).index.tolist()

        for i, supplier in enumerate(top_suppliers_list):
            if supplier in resource_by_supplier.index:
                resource_data = resource_by_supplier.loc[supplier]

                fig.add_trace(
                    go.Pie(
                        labels=resource_data.index,
                        values=resource_data.values,
                        name=supplier,
                        domain=dict(
                            x=[0.5 + (i % 2) * 0.25, 0.75 + (i % 2) * 0.25],
                            y=[0.5 if i < 2 else 0.25, 0.75 if i < 2 else 0.5]
                        ),
                        textinfo='label+percent',
                        hole=0.3,
                        hoverinfo='label+value+percent',
                        title=dict(
                            text=supplier[:10] + '...' if len(supplier) > 10 else supplier)
                    ),
                    row=2, col=2
                )
    else:
        # No data available
        fig.add_trace(
            go.Pie(
                labels=['No Data'],
                values=[1],
                hole=0.3
            ),
            row=2, col=2
        )

    # Update layout
    fig.update_layout(
        title='Procurement Order Analysis with Supplier Network',
        height=900,
        showlegend=False
    )

    fig.update_xaxes(showticklabels=False, row=1, col=1)
    fig.update_yaxes(showticklabels=False, row=1, col=1)

    fig.update_xaxes(title_text='Supplier', row=2, col=1, tickangle=45)
    fig.update_yaxes(title_text='Total Order Value ($)', row=2, col=1)

    return fig


def visualize_project_risk_dashboard(data_path=viz_data_path):
    risk_data = pd.read_parquet(f"{data_path}project_risk_assessment.parquet")

    if len(risk_data) == 0:
        # Create a placeholder figure if no data
        fig = go.Figure(go.Bar(
            x=['No Data'],
            y=[0],
            marker=dict(color='lightgray')
        ))

        fig.update_layout(
            title='Project Risk Assessment Dashboard (No Data Available)',
            height=600
        )

        return fig

    # Sort projects by overall risk
    sorted_risk = risk_data.sort_values('overall_risk', ascending=False)

    # Create the figure
    fig = make_subplots(
        rows=2, cols=2,
        specs=[
            [{"type": "bar"}, {"type": "polar"}],
            [{"colspan": 2, "type": "table"}, None]
        ],
        subplot_titles=(
            'Project Overall Risk Scores',
            'Risk Dimensions Comparison',
            'Detailed Project Risk Assessment'
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )

    # Top left: Overall risk bar chart
    color_scale = px.colors.sequential.Reds

    fig.add_trace(
        go.Bar(
            x=sorted_risk['projectName'],
            y=sorted_risk['overall_risk'],
            marker=dict(
                color=sorted_risk['overall_risk'],
                colorscale=color_scale,
                showscale=True,
                colorbar=dict(title='Risk Level', x=0.45, y=0.83)
            ),
            hovertemplate='Project: %{x}<br>Overall Risk: %{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    # Top right: Radar chart for risk dimensions
    for i, (_, project) in enumerate(sorted_risk.iterrows()):
        fig.add_trace(
            go.Scatterpolar(
                r=[
                    project['schedule_risk'],
                    project['budget_risk'],
                    project['resource_risk'],
                    project['scope_risk']
                ],
                theta=['Schedule', 'Budget', 'Resource', 'Scope'],
                fill='toself',
                name=project['projectName'],
                line=dict(color=px.colors.qualitative.Pastel[i % len(
                    px.colors.qualitative.Pastel)]),
                opacity=0.7
            ),
            row=1, col=2
        )

    # Bottom: Detailed table
    cell_colors = []
    for _, row in sorted_risk.iterrows():
        # Generate color gradient based on risk value
        schedule_color = f'rgba(255, {int(255 * (1 - row["schedule_risk"]))}, {int(255 * (1 - row["schedule_risk"]))}, 0.7)'
        budget_color = f'rgba(255, {int(255 * (1 - row["budget_risk"]))}, {int(255 * (1 - row["budget_risk"]))}, 0.7)'
        resource_color = f'rgba(255, {int(255 * (1 - row["resource_risk"]))}, {int(255 * (1 - row["resource_risk"]))}, 0.7)'
        scope_color = f'rgba(255, {int(255 * (1 - row["scope_risk"]))}, {int(255 * (1 - row["scope_risk"]))}, 0.7)'
        overall_color = f'rgba(255, {int(255 * (1 - row["overall_risk"]))}, {int(255 * (1 - row["overall_risk"]))}, 0.7)'

        cell_colors.append([
            'rgba(255, 255, 255, 0.0)',  # Project name (transparent)
            schedule_color,
            budget_color,
            resource_color,
            scope_color,
            overall_color
        ])

    fig.add_trace(
        go.Table(
            header=dict(
                values=['Project', 'Schedule Risk', 'Budget Risk',
                        'Resource Risk', 'Scope Risk', 'Overall Risk'],
                font=dict(size=12, color='white'),
                fill_color='rgba(70, 130, 180, 0.8)',
                align='left'
            ),
            cells=dict(
                values=[
                    sorted_risk['projectName'],
                    sorted_risk['schedule_risk'].apply(lambda x: f'{x:.2f}'),
                    sorted_risk['budget_risk'].apply(lambda x: f'{x:.2f}'),
                    sorted_risk['resource_risk'].apply(lambda x: f'{x:.2f}'),
                    sorted_risk['scope_risk'].apply(lambda x: f'{x:.2f}'),
                    sorted_risk['overall_risk'].apply(lambda x: f'{x:.2f}')
                ],
                font=dict(size=11),
                fill_color=cell_colors,
                align='left'
            )
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        title='Project Risk Assessment Dashboard',
        height=900,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_xaxes(title_text='Project', row=1, col=1, tickangle=45)
    fig.update_yaxes(title_text='Overall Risk Score', row=1, col=1)

    return fig


def process_visualization(args):
    """
    Process a single visualization function and save the result.
    This function must be defined at the module level for proper pickling.
    """
    i, (visualize_func, filename, title) = args
    try:
        print(f"Generating visualization {i+1}: {title}")
        fig = visualize_func()
        fig.write_html(f"./visualizations/{filename}")
        return i, title, True, None
    except Exception as e:
        return i, title, False, str(e)


def generate_all_visualizations():
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor
    import time

    start_time = time.time()
    print("Loading data...")
    data = load_all_data(use_parallel=False)  # Use reliable sequential loading

    # Create visualizations directory if it doesn't exist
    create_directory_if_not_exists(viz_data_path)
    create_directory_if_not_exists("./visualizations")

    print("\n=== Starting Visualization Generation ===\n")

    # Define visualization pairs (first prepare data, then visualize)
    print("Preparing visualization data...")

    # Prepare all data first(sequentially to avoid dependency issues)
    # prepare_project_budget_data(data)
    # prepare_workstream_budget_data(data)
    # prepare_labor_data(data)
    # prepare_equipment_data(data)
    prepare_material_data(data)
    # prepare_project_timeline_data(data)
    # prepare_team_composition_data(data)
    # prepare_task_analysis_data(data)
    # prepare_procurement_analysis_data(data)
    prepare_resource_allocation_data(data)
    prepare_project_schedule_data(data)
    # prepare_task_dependency_data(data)
    # prepare_material_equipment_correlation(data)
    # prepare_task_performance_data(data)
    # prepare_supplier_performance_data(data)
    # prepare_project_resource_sankey_data(data)
    # prepare_budget_actual_data(data)
    # prepare_resource_utilization_data(data)
    prepare_project_risk_data(data)
    prepare_procurement_network_data(data)

    print("Data preparation complete. Generating visualizations...")

    # Define the visualization functions with their output file names and titles
    visualization_tasks = [
        # (visualize_project_budget_distribution,
        #  "project_budget_distribution.html", "Project Budget Distribution"),
        # (visualize_workstream_budget_allocation, "workstream_budget_allocation.html",
        #  "Workstream Budget Allocation by Project"),
        # (visualize_labor_skill_distribution, "labor_skill_distribution.html",
        #  "Labor Skill Distribution and Hourly Rates"),
        # (visualize_equipment_cost_analysis, "equipment_cost_analysis.html",
        #  "Equipment Cost Analysis by Type"),
        # (visualize_material_cost_inventory, "material_cost_inventory.html",
        #  "Material Cost and Inventory Analysis"),
        # (visualize_project_timeline, "project_timeline.html",
        #  "Project Timeline Gantt Chart"),
        # (visualize_team_composition, "team_composition.html",
        #  "Team Composition Analysis"),
        # (visualize_task_analysis_by_workstream, "task_analysis_by_workstream.html",
        #  "Task Duration and Cost Analysis by Workstream"),
        # (visualize_procurement_analysis,
        #  "procurement_analysis.html", "Procurement Order Analysis"),
        (visualize_resource_allocation, "resource_allocation.html",
         "Resource Allocation Analysis"),
        (visualize_project_schedule, "project_schedule.html",
         "Project Schedule and Milestone Analysis"),
        # (visualize_task_dependency_network, "task_dependency_network.html",
        #  "Task Dependency Network Analysis"),
        # (visualize_material_equipment_correlation, "material_equipment_correlation.html",
        #  "Material and Equipment Cost Correlation"),
        # (visualize_task_performance, "task_performance.html",
        #  "Task Performance and Critical Path Analysis"),
        # (visualize_supplier_performance, "supplier_performance.html",
        #  "Supplier Performance Analysis"),
        # (visualize_project_resource_sankey, "project_resource_sankey.html",
        #  "Project Resource Allocation Sankey Diagram"),
        # (visualize_budget_actual_analysis, "budget_actual_analysis.html",
        #  "Budget vs Actual Cost Analysis"),
        # (visualize_resource_utilization_heatmap,
        #  "resource_utilization_heatmap.html", "Resource Utilization Heatmap"),
        (visualize_project_risk_dashboard, "project_risk_dashboard.html",
         "Project Risk Assessment Dashboard"),
        (visualize_procurement_network, "procurement_network.html",
         "Procurement Order Analysis with Supplier Network")
    ]

    # Try using parallelization with proper error handling
    try:
        if mp.cpu_count() > 1:
            print(
                f"Using {min(mp.cpu_count(), len(visualization_tasks))} processes for visualization generation")
            with ProcessPoolExecutor(max_workers=min(mp.cpu_count(), len(visualization_tasks))) as executor:
                viz_args = list(enumerate(visualization_tasks))
                results = list(executor.map(process_visualization, viz_args))

            # Report results
            for i, title, success, error in sorted(results):
                if success:
                    print(
                        f"✓ Visualization {i+1}: {title} completed successfully")
                else:
                    print(
                        f"✗ Visualization {i+1}: {title} failed with error: {error}")
        else:
            # Sequential processing fallback
            raise ValueError("Forcing sequential processing")
    except Exception as e:
        print(f"Parallel processing failed with error: {str(e)}")
        print("Falling back to sequential processing...")

        # Sequential fallback
        for i, (visualize_func, filename, title) in enumerate(visualization_tasks):
            try:
                print(
                    f"Generating visualization {i+1}/{len(visualization_tasks)}: {title}")
                fig = visualize_func()
                fig.write_html(f"./visualizations/{filename}")
                print(f"✓ Completed successfully")
            except Exception as e:
                print(f"✗ Failed with error: {str(e)}")

    end_time = time.time()
    print(f"\n=== Visualization Generation Complete ===")
    print(f"Total time: {end_time - start_time:.2f} seconds")
    print(f"All visualizations have been saved to ./visualizations/")


if __name__ == "__main__":
    # Generate all visualizations
    generate_all_visualizations()
