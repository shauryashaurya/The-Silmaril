import logging
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# === Configuration ===
DATA_DIR = Path("data/big")
VIZ_DATA_DIR = Path("viz_data")
VIZ_OUTPUT_DIR = Path("visualizations")

# Ensure directories exist
VIZ_DATA_DIR.mkdir(parents=True, exist_ok=True)
VIZ_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_data(data_dir: Path = DATA_DIR) -> dict:
    """
    Load CSV files from data_dir; convert any column with 'Date' in its name to datetime.
    Returns a dict of DataFrames.
    """
    files = {
        'mega_projects': 'mega_projects.csv',
        'workstreams': 'workstreams.csv',
        'people': 'people.csv',
        'equipment_list': 'equipment_list.csv',
        'material_list': 'material_list.csv',
        'suppliers': 'suppliers.csv',
        'teams': 'teams.csv',
        'procurement_orders': 'procurement_orders.csv',
        'tasks': 'tasks.csv'
    }
    data = {}
    for key, fname in files.items():
        path = data_dir / fname
        if not path.exists():
            logging.warning(f"{path} not found. Creating empty DataFrame.")
            data[key] = pd.DataFrame()
            continue
        df = pd.read_csv(path)
        # convert date-like columns
        for col in df.columns:
            if 'Date' in col:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        data[key] = df
        logging.info(f"Loaded {key}: {len(df)} rows")
    return data


def save_df(df: pd.DataFrame, name: str) -> Path:
    """
    Save DataFrame to parquet in VIZ_DATA_DIR
    """
    out = VIZ_DATA_DIR / f"{name}.parquet"
    df.to_parquet(out, compression='snappy', index=False)
    logging.info(f"Saved '{name}' to {out}")
    return out


def load_df(name: str) -> pd.DataFrame:
    """
    Load DataFrame from parquet in VIZ_DATA_DIR; returns empty DF if missing.
    """
    path = VIZ_DATA_DIR / f"{name}.parquet"
    if not path.exists():
        logging.warning(
            f"Parquet {path} not found. Returning empty DataFrame.")
        return pd.DataFrame()
    return pd.read_parquet(path)


def generate_pastel_colors(n: int) -> list[str]:
    """Generate n pastel hex colors."""
    import matplotlib.colors as mcolors
    import random
    colors = []
    for i in range(n):
        h = i / n
        s = 0.3 + 0.2 * random.random()
        l = 0.7 + 0.1 * random.random()
        rgb = mcolors.hsv_to_rgb([h, s, l])
        colors.append(mcolors.rgb2hex(rgb))
    return colors


# === Data Preparation Functions ===

def prepare_material_data(data: dict) -> pd.DataFrame:
    df = data['material_list'].copy()
    df['inventory_value'] = df['unitCost'] * df['quantityOnHand']
    summary = (
        df
        .groupby('materialType', as_index=False)
        .agg(
            avg_unit_cost=('unitCost', 'mean'),
            total_inventory=('quantityOnHand', 'sum'),
            inventory_value=('inventory_value', 'sum'),
            count=('materialID', 'size')
        )
    )
    save_df(summary, 'material_analysis_data')
    return summary


def prepare_resource_allocation_data(data: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    tasks = data['tasks']
    people = data['people'].set_index('id')
    equipment = data['equipment_list'].set_index('id')
    material = data['material_list'].set_index('id')

    records = []
    for _, t in tasks.iterrows():
        tid = t['taskID']
        duration = t['durationDays']
        # labor
        for lid in pd.Series(t['laborIDs'].strip('[]').split(', ')) if isinstance(t['laborIDs'], str) else []:
            if lid in people.index:
                p = people.loc[lid]
                records.append({'taskID': tid, 'resourceType': 'Labor',
                               'specificType': p['skillType'], 'cost': duration*8*p['hourlyRate']})
        # equipment
        for eid in pd.Series(t['equipmentIDs'].strip('[]').split(', ')) if isinstance(t['equipmentIDs'], str) else []:
            if eid in equipment.index:
                e = equipment.loc[eid]
                records.append({'taskID': tid, 'resourceType': 'Equipment',
                               'specificType': e['equipmentType'], 'cost': duration*e['dailyRentalCost']})
        # material
        for mid in pd.Series(t['materialIDs'].strip('[]').split(', ')) if isinstance(t['materialIDs'], str) else []:
            if mid in material.index:
                m = material.loc[mid]
                records.append({'taskID': tid, 'resourceType': 'Material',
                               'specificType': m['materialType'], 'cost': m['unitCost']*100})

    alloc_df = pd.DataFrame(records)
    # overall summary
    resource_summary = (
        alloc_df
        .groupby('resourceType', as_index=False)
        .agg(total_cost=('cost', 'sum'), allocation_count=('taskID', 'size'))
    )
    # detailed
    specific_summary = (
        alloc_df
        .groupby(['resourceType', 'specificType'], as_index=False)
        .agg(total_cost=('cost', 'sum'), allocation_count=('taskID', 'size'))
    )
    save_df(resource_summary, 'resource_summary')
    save_df(specific_summary, 'specific_resource_summary')
    return resource_summary, specific_summary


def prepare_project_schedule_data(data: dict):
    tasks = (
        data['tasks'][['taskID', 'taskName', 'startDate', 'endDate',
                       'durationDays', 'workStreamID', 'milestoneFlag', 'isCritical']]
        .rename(columns={'milestoneFlag': 'milestone', 'isCritical': 'critical'})
    )
    ws = data['workstreams'][['workStreamID',
                              'name', 'startDate', 'endDate', 'projectID']]
    proj = data['mega_projects'][['id', 'projectName']]

    # merge
    tasks = tasks.merge(ws, on='workStreamID', how='left').rename(
        columns={'name': 'workstreamName'})
    tasks = tasks.merge(proj, left_on='projectID', right_on='id', how='left')
    save_df(tasks, 'tasks_with_project')

    # milestones
    milestones = tasks[tasks['milestone'] == True]
    save_df(milestones, 'project_milestones')

    # task counts
    tasks['month'] = tasks['startDate'].dt.to_period('M').astype(str)
    counts = (
        tasks.groupby(['month', 'projectName'], as_index=False)
        .agg(task_count=('taskID', 'size'), critical_count=('critical', 'sum'))
    )
    save_df(counts, 'task_count_by_month')

    # workstream schedule
    ws_sched = ws.copy()
    ws_sched['duration'] = (ws_sched['endDate'] -
                            ws_sched['startDate']).dt.days
    ws_sched = ws_sched.merge(
        proj, left_on='projectID', right_on='id', how='left')
    save_df(ws_sched, 'workstream_schedule')

    return tasks, milestones, counts, ws_sched


def prepare_project_risk_data(data: dict) -> pd.DataFrame:
    proj = data['mega_projects']
    ws = data['workstreams']
    tasks = data['tasks'].copy()
    tasks['critical'] = tasks['isCritical'].astype(int)
    tasks['dependency_count'] = tasks['dependsOnIDs'].apply(lambda s: len(
        s.strip('[]').split(', ')) if isinstance(s, str) and s != '[]' else 0)

    # map ws to project
    ws_map = ws.groupby('projectID').apply(
        lambda df: df.to_dict('records')).to_dict()
    tasks_map = tasks.groupby('workStreamID').apply(
        lambda df: df.to_dict('records')).to_dict()

    risk_list = []
    for _, p in proj.iterrows():
        pws = ws_map.get(p['projectID'], [])
        recs = []
        for w in pws:
            recs.extend(tasks_map.get(w['workStreamID'], []))
        if not recs:
            continue
        tdf = pd.DataFrame(recs)
        total = len(tdf)
        crit = tdf['critical'].sum()
        dep = tdf['dependency_count'].sum()/total
        dur = tdf['durationDays'].mean()
        util = sum(w['budgetAllocated'] for w in pws) / \
            p['overallBudget'] if p['overallBudget'] else 0
        # simple risk scoring
        sched = crit/total*0.6 + dep*0.4
        budg = util*0.5 + np.random.rand()*0.5
        res = np.random.rand()
        scop = dep*0.7 + np.random.rand()*0.3
        overall = 0.3*sched + 0.25*budg + 0.2*res + 0.25*scop
        risk_list.append({
            'projectName': p['projectName'], 'schedule_risk': sched, 'budget_risk': budg,
            'resource_risk': res, 'scope_risk': scop, 'overall_risk': overall
        })
    risk_df = pd.DataFrame(risk_list)
    save_df(risk_df, 'project_risk_assessment')
    return risk_df


def prepare_procurement_network_data(data: dict):
    po = data['procurement_orders']
    sup = data['suppliers'][['id', 'supplierName']]
    proj = data['mega_projects'][['id', 'projectName']]
    mat = data['material_list'][['id', 'materialName']]
    equip = data['equipment_list'][['id', 'equipmentName']]

    po = (
        po.merge(sup, left_on='supplierID', right_on='id', how='left')
          .merge(proj, left_on='belongsToProjectID', right_on='id', how='left')
    )
    records = []
    for _, row in po.iterrows():
        for rid in pd.Series(row['resourceIDs'].strip('[]').split(', ')) if isinstance(row['resourceIDs'], str) else []:
            if rid.startswith('mat_') and rid in mat['id'].values:
                name = mat.set_index('id').loc[rid, 'materialName']
                records.append({'supplierName': row['supplierName'], 'projectName': row['projectName'],
                               'resourceType': 'Material', 'cost': row['totalCost']})
            if rid.startswith('equip_') and rid in equip['id'].values:
                name = equip.set_index('id').loc[rid, 'equipmentName']
                records.append({'supplierName': row['supplierName'], 'projectName': row['projectName'],
                               'resourceType': 'Equipment', 'cost': row['totalCost']})
    df = pd.DataFrame(records)
    links_proj = (
        df.groupby(['supplierName', 'projectName'], as_index=False)
          .agg(order_count=('resourceType', 'size'), total_cost=('cost', 'sum'))
    )
    links_res = (
        df.groupby(['supplierName', 'resourceType'], as_index=False)
          .agg(resource_count=('projectName', 'size'), total_cost=('cost', 'sum'))
    )
    save_df(links_proj, 'supplier_project_links')
    save_df(links_res, 'supplier_resource_links')
    return links_proj, links_res


# === Visualization Functions ===

def visualize_material_cost_inventory():
    df = load_df('material_analysis_data')
    df = df.nlargest(15, 'inventory_value')
    colors = generate_pastel_colors(len(df))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=df['materialType'], y=df['inventory_value'],
                  name='Inventory Value', marker_color=colors))
    fig.add_trace(go.Scatter(x=df['materialType'], y=df['avg_unit_cost'],
                  mode='markers+lines', name='Avg Unit Cost', yaxis='y2'))
    fig.update_layout(xaxis_tickangle=45,
                      title='Top 15 Materials by Inventory Value')
    fig.update_yaxes(title_text='Inventory Value', secondary_y=False)
    fig.update_yaxes(title_text='Avg Unit Cost', secondary_y=True)
    return fig


def visualize_resource_allocation():
    rs = load_df('resource_summary')
    ss = load_df('specific_resource_summary')
    # pie & bar & treemap
    fig = make_subplots(rows=2, cols=2,
                        specs=[[{"type": "pie"}, {"type": "bar"}],
                               [{"colspan": 2, "type": "treemap"}, None]])
    # pie
    fig.add_trace(go.Pie(labels=rs['resourceType'],
                  values=rs['total_cost'], hole=0.4), row=1, col=1)
    # bar
    top = ss.nlargest(10, 'allocation_count')
    fig.add_trace(go.Bar(
        y=top['specificType'], x=top['allocation_count'], orientation='h'), row=1, col=2)
    # treemap
    fig.add_trace(go.Treemap(
        labels=ss['specificType'], parents=ss['resourceType'], values=ss['total_cost']), row=2, col=1)
    fig.update_layout(title='Resource Allocation Analysis', height=800)
    return fig


def visualize_project_schedule():
    tasks = load_df('tasks_with_project')
    miles = load_df('project_milestones')
    counts = load_df('task_count_by_month')
    wsched = load_df('workstream_schedule')
    projects = tasks['projectName'].unique()
    colors = generate_pastel_colors(len(projects))
    cmap = dict(zip(projects, colors))
    fig = make_subplots(rows=2, cols=2,
                        specs=[[{"colspan": 2, "type": "scatter"}, None],
                               [{"type": "bar"}, {"type": "box"}]],
                        subplot_titles=['Gantt with Milestones', 'Task Count by Month', 'Workstream Durations'])
    # Gantt
    for _, row in wsched.iterrows():
        fig.add_trace(go.Bar(x=[row['duration']], y=[row['name']], orientation='h',
                      base=row['startDate'], marker_color=cmap[row['projectName']]), row=1, col=1)
    fig.add_trace(go.Scatter(x=miles['endDate'], y=miles['workstreamName'],
                  mode='markers', marker_symbol='diamond'), row=1, col=1)
    # counts
    for proj in projects:
        dfp = counts[counts['projectName'] == proj]
        fig.add_trace(go.Bar(x=dfp['month'], y=dfp['task_count'],
                      name=proj, marker_color=cmap[proj]), row=2, col=1)
    # durations box
    fig.add_trace(go.Box(x=wsched['projectName'], y=wsched['duration'], marker_color=[
                  cmap[p] for p in wsched['projectName']]), row=2, col=2)
    fig.update_layout(title='Project Schedule Analysis', height=900)
    return fig


def visualize_project_risk_dashboard():
    df = load_df('project_risk_assessment')
    if df.empty:
        fig = go.Figure(go.Bar(x=['No Data'], y=[0]))
        fig.update_layout(title='Project Risk Assessment (No Data)')
        return fig
    df = df.sort_values('overall_risk', ascending=False)
    # bar & radar & table
    fig = make_subplots(rows=2, cols=2,
                        specs=[[{"type": "bar"}, {"type": "polar"}],
                               [{"colspan": 2, "type": "table"}, None]],
                        subplot_titles=['Overall Risk', 'Risk Dimensions', 'Details'])
    # bar
    fig.add_trace(go.Bar(x=df['projectName'], y=df['overall_risk'],
                  marker_color=df['overall_risk'], colorscale='Reds'), row=1, col=1)
    # radar
    for i, r in df.iterrows():
        fig.add_trace(go.Scatterpolar(r=[r['schedule_risk'], r['budget_risk'], r['resource_risk'], r['scope_risk']], theta=[
                      'Schedule', 'Budget', 'Resource', 'Scope'], fill='toself', name=r['projectName']), row=1, col=2)
    # table
    fig.add_trace(go.Table(header=dict(values=['Project', 'Schedule', 'Budget', 'Resource', 'Scope', 'Overall']), cells=dict(values=[
        df['projectName'], df['schedule_risk'], df['budget_risk'], df['resource_risk'], df['scope_risk'], df['overall_risk']
    ])), row=2, col=1)
    fig.update_layout(title='Project Risk Dashboard', height=900)
    return fig


def visualize_procurement_network():
    sp = load_df('supplier_project_links')
    sr = load_df('supplier_resource_links')
    fig = make_subplots(rows=2, cols=2,
                        specs=[[{"type": "scatter"}, None],
                               [{"type": "bar"}, {"type": "pie"}]],
                        subplot_titles=['Supplier-Project', 'Top Suppliers', 'Resource Distribution'])
    # supplier-project network: simplified scatter
    if not sp.empty:
        suppliers = sp['supplierName'].unique()
        projects = sp['projectName'].unique()
        sup_y = np.linspace(0, 1, len(suppliers))
        proj_y = np.linspace(0, 1, len(projects))
        sup_pos = dict(zip(suppliers, zip([0.1]*len(suppliers), sup_y)))
        proj_pos = dict(zip(projects, zip([0.9]*len(projects), proj_y)))
        for s, (x, y) in sup_pos.items():
            fig.add_trace(go.Scatter(x=[x], y=[
                          y], mode='markers+text', text=[s], textposition='middle left'), row=1, col=1)
        for p, (x, y) in proj_pos.items():
            fig.add_trace(go.Scatter(x=[x], y=[
                          y], mode='markers+text', text=[p], textposition='middle right'), row=1, col=1)
        for _, r in sp.iterrows():
            fig.add_trace(go.Scatter(x=[sup_pos[r['supplierName']][0], proj_pos[r['projectName']][0]], y=[
                          sup_pos[r['supplierName']][1], proj_pos[r['projectName']][1]], mode='lines', line=dict(width=1+5*r['total_cost']/sp['total_cost'].max())), row=1, col=1)
    # bar top suppliers
    top = sp.groupby('supplierName', as_index=False).total_cost.sum().nlargest(
        10, 'total_cost')
    fig.add_trace(go.Bar(x=top['supplierName'],
                  y=top['total_cost']), row=2, col=1)
    # pie for first supplier
    if not sr.empty:
        first = sr[sr['supplierName'] == sr['supplierName'].iloc[0]]
        fig.add_trace(go.Pie(
            labels=first['resourceType'], values=first['total_cost'], hole=0.3), row=2, col=2)
    fig.update_layout(title='Procurement Network Analysis', height=900)
    return fig


# === Main Execution ===
if __name__ == '__main__':
    logging.info("Starting data load...")
    data = load_data()

    logging.info("Preparing data...")
    prepare_material_data(data)
    prepare_resource_allocation_data(data)
    prepare_project_schedule_data(data)
    prepare_project_risk_data(data)
    prepare_procurement_network_data(data)

    logging.info("Generating visualizations...")
    figs = [
        (visualize_material_cost_inventory, "material_cost_inventory.html"),
        (visualize_resource_allocation, "resource_allocation.html"),
        (visualize_project_schedule, "project_schedule.html"),
        (visualize_project_risk_dashboard, "project_risk_dashboard.html"),
        (visualize_procurement_network, "procurement_network.html"),
    ]
    for func, fname in figs:
        try:
            fig = func()
            out = VIZ_OUTPUT_DIR / fname
            fig.write_html(out)
            logging.info(f"Wrote {out}")
        except Exception as e:
            logging.error(f"Failed {func.__name__}: {e}")

    logging.info("All tasks complete.")
