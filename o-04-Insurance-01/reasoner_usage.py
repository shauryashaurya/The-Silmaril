import os
import json
import argparse
from typing import Dict, Any
from insurance_reasoner import DataLoader, Reasoner, normalize_id
import pandas as pd
import yaml


def run_pipeline(
    data_location: str = './data',
    json_path: str = './report.json',
    md_path: str = './report.md'
) -> Reasoner:
    """
    Run the full reasoning pipeline end-to-end:
    1. Load data
    2. Process ontology and apply reasoning rules
    3. Generate analytics and insights
    4. Export JSON and Markdown reports

    Returns the Reasoner instance for in-memory inspection.
    """
    loader = DataLoader(data_location)
    reasoner = Reasoner(loader)
    reasoner.load_and_run()
    # Export outputs
    reasoner.export_json_report(json_path)
    md_content = reasoner.generate_markdown_report()
    with open(md_path, 'w') as f:
        f.write(md_content)
    return reasoner


def load_json_report(json_path: str = './report.json') -> Dict[str, Any]:
    """
    Load a previously exported JSON report.
    """
    with open(json_path, 'r') as f:
        return json.load(f)


def print_summary(reasoner: Reasoner) -> None:
    """
    Print a concise summary of key metrics, insights, and recommendations.
    """
    print("\n=== Summary Statistics ===")
    for k, v in reasoner.stats.items():
        print(f"{k}: {v}")
    print("\n=== Business Insights ===")
    for k, v in reasoner.insights.items():
        print(f"{k}: {v}")
    print("\n=== Performance Metrics ===")
    for k, v in reasoner.performance.items():
        print(f"{k}: {v}")
    print("\n=== Recommendations ===")
    for rec in reasoner.recommendations:
        print(f"- {rec}")


def generate_yaml_template_multiple(
    entity_type: str,
    num_templates: int = 3,
    data_location: str = './data'
) -> str:
    """
    Create a YAML template containing `num_templates` empty records for bulk input.
    """
    entity_file_name = entity_type.lower()
    path = os.path.join(data_location, f"{entity_file_name}.csv")
    df = pd.read_csv(path)
    templates = [{col: "" for col in df.columns} for _ in range(num_templates)]
    return yaml.dump({entity_type: templates}, sort_keys=False)


def validate_and_append_records(
    yaml_path: str,
    entity_type: str,
    data_location: str = './data'
) -> bool:
    """
    Load multiple records from YAML (either a list or a mapping with entity key),
    validate all via the full Reasoner pipeline,
    and if _all_ pass, append them to the CSV for entity_type.
    Returns True on success, False on validation failure.
    """
    # Load existing data
    loader = DataLoader(data_location)
    loader.load_all_data()

    # Read the YAML content
    with open(yaml_path) as f:
        content = yaml.safe_load(f)

    # Support both dict-wrapped and bare-list YAML structures
    if isinstance(content, dict):
        raw_records = content.get(entity_type)
    elif isinstance(content, list):
        raw_records = content
    else:
        print(
            f"ERROR: YAML content must be a list or mapping, got {type(content).__name__}")
        return False

    if not isinstance(raw_records, list):
        print(
            f"ERROR: Expected a list of records for '{entity_type}', got {type(raw_records).__name__}")
        return False

    # Normalize IDs in each record
    normalized_records = []
    for rec in raw_records:
        if not isinstance(rec, dict):
            print(
                f"ERROR: Each record must be a mapping, got {type(rec).__name__}")
            return False
        normalized = {}
        for k, v in rec.items():
            normalized[k] = normalize_id(v) if k.lower().endswith('id') else v
        normalized_records.append(normalized)

    # Append to DataFrame
    df = loader.raw_dfs.get(entity_type)
    if df is None:
        raise ValueError(f"Unknown entity type: {entity_type}")
    new_df = df.append(normalized_records, ignore_index=True)
    loader.raw_dfs[entity_type] = new_df

    # Run full pipeline on augmented data
    reasoner = Reasoner(loader)
    reasoner.load_and_run()

    # Overwrite CSV if validation passes
    new_df.to_csv(os.path.join(
        data_location, f"{entity_type}.csv"), index=False)
    print(
        f"All {len(normalized_records)} records appended to {entity_type}.csv successfully.")
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run insurance ontology reasoner and export reports.'
    )
    parser.add_argument(
        '--data', '-d', default='./data',
        help='Path to data directory containing CSV files.'
    )
    parser.add_argument(
        '--json', '-j', default='./report.json',
        help='Output path for JSON report.'
    )
    parser.add_argument(
        '--md', '-m', default='./report.md',
        help='Output path for Markdown report.'
    )
    parser.add_argument(
        '--print', '-p', action='store_true',
        help='Print summary to console after execution.'
    )
    parser.add_argument(
        '--template', '-t', metavar='ENTITY',
        help='Generate a YAML template with multiple records for the given entity.'
    )
    parser.add_argument(
        '--validate-append', '-v', nargs=2, metavar=('YAML_FILE', 'ENTITY'),
        help='Validate & append multiple records from YAML_FILE into the CSV for ENTITY.'
    )
    args = parser.parse_args()

    # Handle template generation
    if args.template:
        print(generate_yaml_template_multiple(
            args.template, data_location=args.data))
        exit(0)

    # Handle bulk YAML validation & append
    if args.validate_append:
        yaml_file, entity = args.validate_append
        success = validate_and_append_records(yaml_file, entity, args.data)
        exit(0 if success else 1)

    # Otherwise run the full pipeline
    reasoner = run_pipeline(
        data_location=args.data,
        json_path=args.json,
        md_path=args.md
    )
    if args.print:
        print_summary(reasoner)
