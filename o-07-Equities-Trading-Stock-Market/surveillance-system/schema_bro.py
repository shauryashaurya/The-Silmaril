import pyarrow.parquet as pq
import yaml
import os

# just a quick script to dump the schemas
# from all the parquet files in a folder
# and all sub folders..
# into a YAML file


def extract_schemas_from_directory(root_dir, output_yaml):
    schemas = {}
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.parquet'):
                file_path = os.path.join(subdir, file)
                try:
                    schema = pq.read_schema(file_path)
                    schema_dict = {name: str(type) for name, type in zip(
                        schema.names, schema.types)}
                    # Store with relative path as key for clarity
                    relative_path = os.path.relpath(file_path, root_dir)
                    schemas[relative_path] = schema_dict
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")

    with open(output_yaml, 'w') as f:
        yaml.dump(schemas, f, sort_keys=False)


# Example usage:
# extract_schemas_from_directory('path/to/folder', 'schemas_output.yaml')
extract_schemas_from_directory('./', 'surviellance_data_schemas.yaml')
