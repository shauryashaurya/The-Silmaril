import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')


def load_project_data(data_path="./data/big/"):
    """
    Load all project data files and perform necessary data cleaning and transformations.
    Returns a dictionary of dataframes ready for visualization.
    """
    # Load all CSV files
    mega_projects = pd.read_csv(f"{data_path}mega_projects.csv")
    workstreams = pd.read_csv(f"{data_path}workstreams.csv")
    tasks = pd.read_csv(f"{data_path}tasks.csv")
    people = pd.read_csv(f"{data_path}people.csv")
    equipment_list = pd.read_csv(f"{data_path}equipment_list.csv")
    material_list = pd.read_csv(f"{data_path}material_list.csv")
    teams = pd.read_csv(f"{data_path}teams.csv")
    suppliers = pd.read_csv(f"{data_path}suppliers.csv")
    procurement_orders = pd.read_csv(f"{data_path}procurement_orders.csv")

    # Convert date columns to datetime
    date_columns = {
        'mega_projects': ['startDate', 'plannedEndDate', 'actualEndDate'],
        'workstreams': ['startDate', 'endDate'],
        'tasks': ['startDate', 'endDate'],
        'procurement_orders': ['orderDate']
    }

    for df_name, columns in date_columns.items():
        df = locals()[df_name]
        for col in columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

    # Handle list columns that might be stored as strings
    list_columns = {
        'tasks': ['dependsOnIDs', 'laborIDs', 'equipmentIDs', 'materialIDs'],
        'teams': ['personIDs']
    }

    for df_name, columns in list_columns.items():
        df = locals()[df_name]
        for col in columns:
            if col in df.columns:
                # Convert string representations of lists to actual lists
                df[col] = df[col].apply(lambda x: [] if pd.isna(x) else
                                        (eval(x) if isinstance(x, str) and x.startswith('[') else
                                         [x.strip("'\"") for x in str(x).strip('[]').split(',') if x.strip()]))

    # Calculate derived fields for critical path analysis
    tasks = calculate_critical_path_metrics(tasks)

    # Add resource counts to tasks - safely handle missing columns
    for col in ['laborIDs', 'equipmentIDs', 'materialIDs']:
        if col not in tasks.columns:
            tasks[col] = np.nan

    tasks['labor_count'] = tasks['laborIDs'].apply(
        lambda x: len(x) if isinstance(x, list) else 0)
    tasks['equipment_count'] = tasks['equipmentIDs'].apply(
        lambda x: len(x) if isinstance(x, list) else 0)
    tasks['material_count'] = tasks['materialIDs'].apply(
        lambda x: len(x) if isinstance(x, list) else 0)
    tasks['total_resources'] = tasks['labor_count'] + \
        tasks['equipment_count'] + tasks['material_count']

    # Calculate task duration in days
    tasks['duration'] = (tasks['endDate'] - tasks['startDate']
                         ).dt.total_seconds() / (24 * 3600)

    # Set resource type explicitly for easier filtering
    people['resource_type'] = 'Labor'
    equipment_list['resource_type'] = 'Equipment'
    material_list['resource_type'] = 'Material'

    # Create a unified resources dataframe for some visualizations
    labor_resources = people[['id', 'personID', 'name', 'skillType', 'hourlyRate', 'resource_type']].rename(
        columns={'personID': 'resourceID', 'name': 'resourceName', 'skillType': 'resourceSubtype', 'hourlyRate': 'unitCost'})

    equipment_resources = equipment_list[['id', 'equipmentID', 'equipmentName', 'equipmentType', 'dailyRentalCost', 'resource_type']].rename(
        columns={'equipmentID': 'resourceID', 'equipmentName': 'resourceName', 'equipmentType': 'resourceSubtype', 'dailyRentalCost': 'unitCost'})

    material_resources = material_list[['id', 'materialID', 'materialName', 'materialType', 'unitCost', 'quantityOnHand', 'resource_type']].rename(
        columns={'materialID': 'resourceID', 'materialName': 'resourceName', 'materialType': 'resourceSubtype'})

    # Combine into a unified resources dataframe
    resources = pd.concat(
        [labor_resources, equipment_resources, material_resources], ignore_index=True)

    # Create resource assignment dataframe by flattening the task assignments
    resource_assignments = create_resource_assignments(tasks, resources)

    # Calculate resource utilization
    resource_utilization = calculate_resource_utilization(tasks, resources, resource_assignments)frame
    resources = pd.concat(
        [labor_resources, equipment_resources, material_resources], ignore_index=True)

    # Create resource assignment dataframe by flattening the task assignments
    resource_assignments = create_resource_assignments(tasks, resources)

    # Calculate resource utilization
    resource_utilization = calculate_resource_utilization(
        tasks, resources, resource_assignments)

    # Return dictionary of all dataframes
    return {
        'mega_projects': mega_projects,
        'workstreams': workstreams,
        'tasks': tasks,
        'people': people,
        'equipment_list': equipment_list,
        'material_list': material_list,
        'teams': teams,
        'suppliers': suppliers,
        'procurement_orders': procurement_orders,
        'resources': resources,
        'resource_assignments': resource_assignments,
        'resource_utilization': resource_utilization
    }frame
    resources = pd.concat(
        [labor_resources, equipment_resources, material_resources], ignore_index=True)

    # Create resource assignment dataframe by flattening the task assignments
    resource_assignments = create_resource_assignments(tasks, resources)

    # Calculate resource utilization
    resource_utilization = calculate_resource_utilization(
        tasks, resources, resource_assignments)

    # Return dictionary of all dataframes
    return {
        'mega_projects': mega_projects,
        'workstreams': workstreams,
        'tasks': tasks,
        'people': people,
        'equipment_list': equipment_list,
        'material_list': material_list,
        'teams': teams,
        'suppliers': suppliers,
        'procurement_orders': procurement_orders,
        'resources': resources,
        'resource_assignments': resource_assignments,
        'resource_utilization': resource_utilization
    }


def calculate_critical_path_metrics(tasks_df):
    """
    Calculate critical path metrics including early start, early finish,
    late start, late finish, and slack for each task.
    """
    # If isCritical already exists in the dataframe, use it directly
    if 'isCritical' in tasks_df.columns:
        return tasks_df

    # Convert tasks dataframe to a format suitable for network analysis
    tasks_dict = tasks_df.set_index('taskID').to_dict('index')

    # Create a directed graph for the tasks
    G = nx.DiGraph()

    # Add all tasks as nodes
    for task_id, task in tasks_dict.items():
        G.add_node(task_id, **task)

    # Add dependencies as edges
    for task_id, task in tasks_dict.items():
        if 'dependsOnIDs' in task and task['dependsOnIDs']:
            for dep_id in task['dependsOnIDs']:
                if dep_id in tasks_dict:
                    G.add_edge(dep_id, task_id)

    # Initialize early start and early finish times
    nx.set_node_attributes(G, 0, 'early_start')
    nx.set_node_attributes(G, 0, 'early_finish')

    # Forward pass: Calculate early start and early finish
    for task_id in nx.topological_sort(G):
        # Get task duration
        task_duration = (G.nodes[task_id]['endDate'] - G.nodes[task_id]
                         ['startDate']).total_seconds() / (24 * 3600)

        # Calculate early start (max of predecessors' early finish)
        predecessors = list(G.predecessors(task_id))
        if predecessors:
            G.nodes[task_id]['early_start'] = max(
                G.nodes[pred]['early_finish'] for pred in predecessors)
        else:
            G.nodes[task_id]['early_start'] = 0

        # Calculate early finish
        G.nodes[task_id]['early_finish'] = G.nodes[task_id]['early_start'] + task_duration

    # Initialize late start and late finish times
    project_end = max(G.nodes[task_id]['early_finish'] for task_id in G.nodes)
    nx.set_node_attributes(G, project_end, 'late_finish')
    nx.set_node_attributes(G, project_end, 'late_start')

    # Backward pass: Calculate late start and late finish
    for task_id in reversed(list(nx.topological_sort(G))):
        # Get task duration
        task_duration = (G.nodes[task_id]['endDate'] - G.nodes[task_id]
                         ['startDate']).total_seconds() / (24 * 3600)

        # Calculate late finish (min of successors' late start)
        successors = list(G.successors(task_id))
        if successors:
            G.nodes[task_id]['late_finish'] = min(
                G.nodes[succ]['late_start'] for succ in successors)
        else:
            G.nodes[task_id]['late_finish'] = project_end

        # Calculate late start
        G.nodes[task_id]['late_start'] = G.nodes[task_id]['late_finish'] - task_duration

    # Calculate slack time
    for task_id in G.nodes:
        G.nodes[task_id]['slack'] = G.nodes[task_id]['late_start'] - \
            G.nodes[task_id]['early_start']

    # Convert back to dataframe
    critical_path_metrics = pd.DataFrame([
        {
            'taskID': task_id,
            'early_start': G.nodes[task_id]['early_start'],
            'early_finish': G.nodes[task_id]['early_finish'],
            'late_start': G.nodes[task_id]['late_start'],
            'late_finish': G.nodes[task_id]['late_finish'],
            'slack': G.nodes[task_id]['slack']
        }
        for task_id in G.nodes
    ])

    # Merge with original tasks dataframe
    tasks_df = tasks_df.merge(critical_path_metrics, on='taskID', how='left')

    # Fill NaN values for tasks that aren't in the network
    tasks_df['slack'] = tasks_df['slack'].fillna(0)

    return tasks_df


def create_resource_assignments(tasks_df, resources_df):
    """
    Create a flattened resource assignment dataframe from tasks.
    """
    # Create empty lists to store the flattened data
    assignments = []

    # Process labor assignments
    for _, task in tasks_df.iterrows():
        task_id = task['taskID']
        start_date = task['startDate']
        end_date = task['endDate']
        duration = (end_date - start_date).total_seconds() / (24 * 3600)
        is_critical = task['isCritical']

        # Process labor resources
        if isinstance(task['laborIDs'], list):
            for labor_id in task['laborIDs']:
                labor_resource = resources_df[resources_df['id'] == labor_id]
                if not labor_resource.empty:
                    assignments.append({
                        'taskID': task_id,
                        'resourceID': labor_id,
                        'resourceType': 'Labor',
                        'startDate': start_date,
                        'endDate': end_date,
                        'duration': duration,
                        'is_critical': is_critical,
                        'workStreamID': task['workStreamID']
                    })

        # Process equipment resources
        if isinstance(task['equipmentIDs'], list):
            for equip_id in task['equipmentIDs']:
                equip_resource = resources_df[resources_df['id'] == equip_id]
                if not equip_resource.empty:
                    assignments.append({
                        'taskID': task_id,
                        'resourceID': equip_id,
                        'resourceType': 'Equipment',
                        'startDate': start_date,
                        'endDate': end_date,
                        'duration': duration,
                        'is_critical': is_critical,
                        'workStreamID': task['workStreamID']
                    })

        # Process material resources
        if isinstance(task['materialIDs'], list):
            for material_id in task['materialIDs']:
                material_resource = resources_df[resources_df['id']
                                                 == material_id]
                if not material_resource.empty:
                    assignments.append({
                        'taskID': task_id,
                        'resourceID': material_id,
                        'resourceType': 'Material',
                        'startDate': start_date,
                        'endDate': end_date,
                        'duration': duration,
                        'is_critical': is_critical,
                        'workStreamID': task['workStreamID']
                    })

    # Convert to dataframe
    assignments_df = pd.DataFrame(assignments)

    # Add resource details
    if not assignments_df.empty:
        assignments_df = assignments_df.merge(
            resources_df[['id', 'resourceName',
                          'resourceSubtype', 'unitCost']],
            left_on='resourceID',
            right_on='id',
            how='left'
        )

    return assignments_df


def calculate_resource_utilization(tasks_df, resources_df, resource_assignments_df):
    """
    Calculate resource utilization over time.
    """
    if resource_assignments_df.empty:
        return pd.DataFrame()

    # Get the earliest start date and latest end date
    min_date = tasks_df['startDate'].min()
    max_date = tasks_df['endDate'].max()

    # Generate daily time periods
    time_periods = pd.date_range(start=min_date, end=max_date, freq='D')

    # Initialize utilization dataframe
    utilization_records = []

    # For each resource and time period, calculate utilization
    for resource_id in resource_assignments_df['resourceID'].unique():
        resource_assignments = resource_assignments_df[resource_assignments_df['resourceID'] == resource_id]
        resource_type = resource_assignments['resourceType'].iloc[0] if not resource_assignments.empty else 'Unknown'

        for day in time_periods:
            # Count assignments that overlap with this day
            active_assignments = resource_assignments[
                (resource_assignments['startDate'] <= day) &
                (resource_assignments['endDate'] >= day)
            ]

            # Calculate utilization metrics
            assignment_count = len(active_assignments)
            critical_assignment_count = active_assignments['is_critical'].sum()

            # Calculate utilization percentage (assuming 100% if assigned)
            utilization_pct = min(
                100.0, assignment_count * 100.0) if assignment_count > 0 else 0.0

            utilization_records.append({
                'resourceID': resource_id,
                'date': day,
                'assignment_count': assignment_count,
                'critical_assignment_count': critical_assignment_count,
                'utilization_pct': utilization_pct,
                'resourceType': resource_type
            })

    # Convert to dataframe
    utilization_df = pd.DataFrame(utilization_records)

    # Add resource details
    utilization_df = utilization_df.merge(
        resources_df[['id', 'resourceName', 'resourceSubtype', 'unitCost']],
        left_on='resourceID',
        right_on='id',
        how='left'
    )

    return utilization_df

# Generate color palette functions for consistent but varied visualization colors


def get_pastel_color_palette(n_colors, palette_name='pastel'):
    """Generate a pastel color palette with the specified number of colors."""
    if palette_name == 'pastel':
        # Custom pastel palette
        base_palette = [
            '#FF9AA2', '#FFB7B2', '#FFDAC1', '#E2F0CB', '#B5EAD7',
            '#C7CEEA', '#B5D8EB', '#D7BDE2', '#FFF7D6', '#FFE2E2',
            '#F0DBFF', '#D5F0FF', '#BFFCC6', '#FFFFD1', '#FFC3A0',
            '#E0BBE4', '#957DAD', '#D291BC', '#FFDFD3', '#B0C4DE'
        ]
    elif palette_name == 'pastel_extended':
        # Extended pastel palette
        base_palette = [
            '#FF9AA2', '#FFB7B2', '#FFDAC1', '#E2F0CB', '#B5EAD7',
            '#C7CEEA', '#B5D8EB', '#D7BDE2', '#FFF7D6', '#FFE2E2',
            '#F0DBFF', '#D5F0FF', '#BFFCC6', '#FFFFD1', '#FFC3A0',
            '#E0BBE4', '#957DAD', '#D291BC', '#FFDFD3', '#B0C4DE',
            '#FAD0C9', '#C1E7E3', '#DCFFFB', '#FCE2C2', '#FFD8BE',
            '#FFEEDD', '#CADEFC', '#C3B1E1', '#ABD0CE', '#CFBAF0'
        ]
    else:
        # Default to a plotly color sequence
        return px.colors.qualitative.Pastel if n_colors <= 10 else px.colors.qualitative.Pastel + px.colors.qualitative.Light24

    # If we need more colors than in our base palette, cycle through them
    if n_colors <= len(base_palette):
        return base_palette[:n_colors]
    else:
        return base_palette * (n_colors // len(base_palette) + 1)

# Function to create a date range for timeline views


def create_date_sequence(start_date, end_date, freq='W'):
    """Create a sequence of dates between start and end dates with the specified frequency."""
    return pd.date_range(start=start_date, end=end_date, freq=freq)
