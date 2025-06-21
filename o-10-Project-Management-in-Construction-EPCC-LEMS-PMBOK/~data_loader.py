import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from typing import Dict, List, Optional, Tuple, Union
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Define color palette (pastel but colorful) with at least 50 colors
COLOR_PALETTE = [
    # Reds/Pinks
    '#FF9AA2', '#FFB7B2', '#FFC3B2', '#FFCCB6', '#FFD6B6',
    '#FFE0CC', '#FFE6CC', '#FFECCC', '#FFF2E6', '#FFCCCC',
    # Yellows/Oranges
    '#FFDAC1', '#FFE6B7', '#FFF2CC', '#FFFACD', '#FDFFB6',
    '#FFD6A5', '#FFEACC', '#FFE0B2', '#FFD699', '#FFCC80',
    # Greens
    '#E2F0CB', '#D1F0B1', '#C1F0A1', '#B5EAD7', '#A1E5C8',
    '#8DE5BE', '#77DEB7', '#CAFFBF', '#A0E7B1', '#80DFA1',
    # Blues/Purples
    '#C7CEEA', '#B5C7F2', '#A2C0FF', '#A0C4FF', '#B2A4FF',
    '#BDB2FF', '#C6BBFF', '#D4BBFF', '#E0C3FF', '#EBD0FF',
    # Cyans/Light Blues
    '#9BF6FF', '#8CE6FF', '#7ADBFF', '#69D2F3', '#57C9E8',
    '#46C0DD', '#34B6D3', '#28ADCF', '#1BA4CA', '#0F9BC6',
    # Neutral/Mixed
    '#F9C0C0', '#F0D0C0', '#E6E0C0', '#D9F0C0', '#C0F0D0',
    '#C0F0E6', '#C0E6F0', '#C0D0F0', '#D0C0F0', '#F0C0E6'
]


def load_project_data(data_path: str = "./data/big/") -> Dict[str, pd.DataFrame]:
    """
    Load all project data from CSV files.

    Args:
        data_path: Path to the directory containing CSV files

    Returns:
        Dictionary containing DataFrames for each entity type
    """
    try:
        # Load all dataframes
        mega_projects = pd.read_csv(f"{data_path}mega_projects.csv")
        workstreams = pd.read_csv(f"{data_path}workstreams.csv")
        tasks = pd.read_csv(f"{data_path}tasks.csv")
        people = pd.read_csv(f"{data_path}people.csv")
        equipment = pd.read_csv(f"{data_path}equipment_list.csv")
        materials = pd.read_csv(f"{data_path}material_list.csv")
        suppliers = pd.read_csv(f"{data_path}suppliers.csv")
        teams = pd.read_csv(f"{data_path}teams.csv")
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
                    df[col] = pd.to_datetime(df[col])

        # Parse list columns (stored as strings)
        if 'dependsOnIDs' in tasks.columns:
            tasks['dependsOnIDs'] = tasks['dependsOnIDs'].apply(
                lambda x: eval(x) if isinstance(x, str) and x.strip() else []
            )

        list_columns = {
            'tasks': ['laborIDs', 'equipmentIDs', 'materialIDs'],
            'teams': ['personIDs'],
            'procurement_orders': ['resourceIDs']
        }

        for df_name, columns in list_columns.items():
            df = locals()[df_name]
            for col in columns:
                if col in df.columns:
                    df[col] = df[col].apply(
                        lambda x: eval(x) if isinstance(
                            x, str) and x.strip() else []
                    )

        # Return consolidated dictionary
        return {
            'mega_projects': mega_projects,
            'workstreams': workstreams,
            'tasks': tasks,
            'people': people,
            'equipment': equipment,
            'materials': materials,
            'suppliers': suppliers,
            'teams': teams,
            'procurement_orders': procurement_orders
        }
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return {}


def prepare_project_hierarchy(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Prepare joined DataFrames showing project hierarchy relationships.

    Args:
        data: Dictionary of loaded DataFrames

    Returns:
        Dictionary containing joined DataFrames showing hierarchy relationships
    """
    try:
        # Create task-workstream joined view
        task_workstream = data['tasks'].merge(
            data['workstreams'][['id', 'workStreamID', 'name', 'projectID']],
            left_on='workStreamID',
            right_on='id',
            how='left',
            suffixes=('', '_workstream')
        )

        # Create task-workstream-project joined view
        task_workstream_project = task_workstream.merge(
            data['mega_projects'][['id', 'projectID',
                                   'projectName', 'overallBudget']],
            left_on='projectID',
            right_on='id',
            how='left',
            suffixes=('', '_project')
        )

        # Create resource assignment mapping
        resource_assignments = {}

        # Add labor (people) assignments
        if 'laborIDs' in data['tasks'].columns:
            labor_assignments = []
            for _, task in data['tasks'].iterrows():
                for labor_id in task.get('laborIDs', []):
                    if labor_id:
                        labor_assignments.append({
                            'taskID': task['taskID'],
                            'resourceID': labor_id,
                            'resourceType': 'Labor'
                        })
            resource_assignments['labor'] = pd.DataFrame(labor_assignments)

        # Add equipment assignments
        if 'equipmentIDs' in data['tasks'].columns:
            equipment_assignments = []
            for _, task in data['tasks'].iterrows():
                for equipment_id in task.get('equipmentIDs', []):
                    if equipment_id:
                        equipment_assignments.append({
                            'taskID': task['taskID'],
                            'resourceID': equipment_id,
                            'resourceType': 'Equipment'
                        })
            resource_assignments['equipment'] = pd.DataFrame(
                equipment_assignments)

        # Add material assignments
        if 'materialIDs' in data['tasks'].columns:
            material_assignments = []
            for _, task in data['tasks'].iterrows():
                for material_id in task.get('materialIDs', []):
                    if material_id:
                        material_assignments.append({
                            'taskID': task['taskID'],
                            'resourceID': material_id,
                            'resourceType': 'Material'
                        })
            resource_assignments['material'] = pd.DataFrame(
                material_assignments)

        # Combine all resource assignments
        all_assignments = pd.concat(
            [df for df in resource_assignments.values()],
            ignore_index=True
        ) if resource_assignments else pd.DataFrame()

        return {
            'task_workstream': task_workstream,
            'task_workstream_project': task_workstream_project,
            'resource_assignments': all_assignments
        }
    except Exception as e:
        print(f"Error preparing hierarchy: {str(e)}")
        return {}


def calculate_project_metrics(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Calculate key project metrics from raw data.

    Args:
        data: Dictionary of loaded DataFrames

    Returns:
        Dictionary containing calculated metrics
    """
    try:
        tasks = data['tasks'].copy()
        workstreams = data['workstreams'].copy()

        # Calculate task duration in days
        if 'startDate' in tasks.columns and 'endDate' in tasks.columns:
            tasks['actualDuration'] = (
                tasks['endDate'] - tasks['startDate']).dt.days
            tasks['durationVariance'] = tasks['actualDuration'] - \
                tasks['durationDays']

        # Calculate cost variance
        if 'costEstimate' in tasks.columns and 'actualCost' in tasks.columns:
            tasks['costVariance'] = tasks['actualCost'] - tasks['costEstimate']
            tasks['costVariancePercent'] = (
                tasks['costVariance'] / tasks['costEstimate']) * 100

        # Aggregate task metrics to workstream level
        workstream_metrics = tasks.groupby('workStreamID').agg(
            task_count=('taskID', 'count'),
            total_duration_days=('durationDays', 'sum'),
            total_cost_estimate=('costEstimate', 'sum'),
            total_actual_cost=('actualCost', 'sum'),
            critical_task_count=('isCritical', lambda x: x.sum()),
            milestone_count=('milestoneFlag', lambda x: x.sum())
        ).reset_index()

        # Join back to workstreams
        workstream_with_metrics = workstreams.merge(
            workstream_metrics,
            left_on='workStreamID',
            right_on='workStreamID',
            how='left'
        )

        # Calculate workstream budget variance
        workstream_with_metrics['budget_variance'] = (
            workstream_with_metrics['total_actual_cost'] -
            workstream_with_metrics['budgetAllocated']
        )

        # Calculate budget utilization percentage
        workstream_with_metrics['budget_utilization_pct'] = (
            workstream_with_metrics['total_actual_cost'] /
            workstream_with_metrics['budgetAllocated'] * 100
        )

        return {
            'tasks_with_metrics': tasks,
            'workstreams_with_metrics': workstream_with_metrics
        }
    except Exception as e:
        print(f"Error calculating metrics: {str(e)}")
        return {}
