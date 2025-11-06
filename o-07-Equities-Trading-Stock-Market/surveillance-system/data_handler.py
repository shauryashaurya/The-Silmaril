# data_handler.py
# High-performance data I/O handler with Apache Arrow optimization

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import json
import gzip

# Arrow imports
try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    import pyarrow.compute as pc
    import pyarrow.dataset as ds
    ARROW_AVAILABLE = True
except ImportError:
    ARROW_AVAILABLE = False
    print("Warning: PyArrow not available. Performance will be degraded.")

try:
    import fastavro
    AVRO_AVAILABLE = True
except ImportError:
    AVRO_AVAILABLE = False

try:
    from deltalake import DeltaTable
    DELTA_AVAILABLE = True
except ImportError:
    DELTA_AVAILABLE = False

# Configuration


@dataclass
class DataConfig:
    source_format: str = 'parquet'
    output_format: str = 'parquet'
    source_dir: str = './data/parquet_output'
    output_dir: str = './data/surveillance_output'
    compress_output: bool = True
    use_arrow_native: bool = True  # Use Arrow tables instead of pandas where possible
    chunk_size: int = 100000  # For large file processing
    arrow_batch_size: int = 65536  # Arrow batch size

# Optimized Data Loader


class ArrowDataLoader:
    """High-performance data loader using Apache Arrow"""

    def __init__(self, config: DataConfig):
        self.config = config
        self.source_dir = Path(config.source_dir)
        self._table_cache: Dict[str, pa.Table] = {}

    def load_table(self, table_name: str, columns: Optional[List[str]] = None,
                   use_cache: bool = True) -> pd.DataFrame:
        """
        Load table with optional column selection for performance

        Args:
            table_name: Name of the table to load
            columns: List of columns to load (None = all columns)
            use_cache: Whether to use cached Arrow table

        Returns:
            pandas DataFrame
        """
        print(f"Loading {table_name}...", end=' ')

        # Check cache first
        if use_cache and table_name in self._table_cache:
            arrow_table = self._table_cache[table_name]
            if columns:
                arrow_table = arrow_table.select(columns)
            print(f"(from cache, {len(arrow_table):,} rows)")
            return arrow_table.to_pandas()

        format_lower = self.config.source_format.lower()

        if format_lower == 'parquet':
            df = self._load_parquet_arrow(table_name, columns)
        elif format_lower == 'csv':
            df = self._load_csv_arrow(table_name, columns)
        elif format_lower == 'json':
            df = self._load_json(table_name)
        elif format_lower == 'jsonl':
            df = self._load_jsonl_arrow(table_name)
        elif format_lower == 'avro':
            df = self._load_avro(table_name)
        elif format_lower == 'delta':
            df = self._load_delta(table_name)
        else:
            raise ValueError(
                f"Unsupported source format: {self.config.source_format}")

        print(f"({len(df):,} rows)")
        return df

    def load_table_arrow(self, table_name: str, columns: Optional[List[str]] = None) -> pa.Table:
        """Load table as Arrow Table for maximum performance"""
        if not ARROW_AVAILABLE:
            raise RuntimeError("PyArrow not available")

        # Check cache
        if table_name in self._table_cache:
            arrow_table = self._table_cache[table_name]
            if columns:
                arrow_table = arrow_table.select(columns)
            return arrow_table

        format_lower = self.config.source_format.lower()

        if format_lower == 'parquet':
            filepath = self.source_dir / f"{table_name}.parquet"
            arrow_table = pq.read_table(str(filepath), columns=columns)
        else:
            # Fallback to pandas then convert
            df = self.load_table(table_name, columns=columns, use_cache=False)
            arrow_table = pa.Table.from_pandas(df)

        # Cache the table
        self._table_cache[table_name] = arrow_table

        return arrow_table

    def _load_parquet_arrow(self, table_name: str, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Load Parquet using Arrow for optimal performance"""
        filepath = self.source_dir / f"{table_name}.parquet"
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        if ARROW_AVAILABLE:
            # Use Arrow native reading
            arrow_table = pq.read_table(str(filepath), columns=columns)

            # Cache Arrow table
            if columns is None:
                self._table_cache[table_name] = arrow_table

            # Convert to pandas with zero-copy where possible
            return arrow_table.to_pandas(
                split_blocks=True,
                self_destruct=False,
                use_threads=True
            )
        else:
            # Fallback to pandas
            return pd.read_parquet(filepath, columns=columns)

    def _load_csv_arrow(self, table_name: str, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Load CSV using Arrow CSV reader"""
        filepath_gz = self.source_dir / f"{table_name}.csv.gz"
        filepath = self.source_dir / f"{table_name}.csv"

        if filepath_gz.exists():
            target_file = filepath_gz
            compression = 'gzip'
        elif filepath.exists():
            target_file = filepath
            compression = None
        else:
            raise FileNotFoundError(f"File not found: {filepath}")

        if ARROW_AVAILABLE and compression is None:
            # Arrow doesn't support gzip directly, so we use pandas for compressed files
            from pyarrow import csv

            read_options = csv.ReadOptions()
            if columns:
                read_options.column_names = columns

            arrow_table = csv.read_csv(
                str(target_file),
                read_options=read_options
            )
            return arrow_table.to_pandas()
        else:
            # Fallback to pandas
            return pd.read_csv(target_file, compression=compression, usecols=columns)

    def _load_json(self, table_name: str) -> pd.DataFrame:
        """Load JSON file"""
        filepath_gz = self.source_dir / f"{table_name}.json.gz"
        filepath = self.source_dir / f"{table_name}.json"

        if filepath_gz.exists():
            return pd.read_json(filepath_gz, compression='gzip')
        elif filepath.exists():
            return pd.read_json(filepath)
        else:
            raise FileNotFoundError(f"File not found: {filepath}")

    def _load_jsonl_arrow(self, table_name: str) -> pd.DataFrame:
        """Load JSONL using Arrow"""
        filepath_gz = self.source_dir / f"{table_name}.jsonl.gz"
        filepath = self.source_dir / f"{table_name}.jsonl"

        if filepath_gz.exists():
            target_file = filepath_gz
            compression = 'gzip'
        elif filepath.exists():
            target_file = filepath
            compression = None
        else:
            raise FileNotFoundError(f"File not found: {filepath}")

        if ARROW_AVAILABLE and compression is None:
            from pyarrow import json as pa_json

            arrow_table = pa_json.read_json(str(target_file))
            return arrow_table.to_pandas()
        else:
            return pd.read_json(target_file, lines=True, compression=compression)

    def _load_avro(self, table_name: str) -> pd.DataFrame:
        """Load Avro file"""
        if not AVRO_AVAILABLE:
            raise RuntimeError(
                "Avro support not available. Install: pip install fastavro")

        filepath = self.source_dir / f"{table_name}.avro"
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        records = []
        with open(filepath, 'rb') as f:
            reader = fastavro.reader(f)
            for record in reader:
                records.append(record)
        return pd.DataFrame(records)

    def _load_delta(self, table_name: str) -> pd.DataFrame:
        """Load Delta Lake table"""
        if not DELTA_AVAILABLE:
            raise RuntimeError(
                "Delta Lake support not available. Install: pip install deltalake")

        table_path = self.source_dir / f"{table_name}_delta"
        if not table_path.exists():
            raise FileNotFoundError(f"Delta table not found: {table_path}")

        dt = DeltaTable(str(table_path))
        return dt.to_pandas()

    def clear_cache(self):
        """Clear the table cache to free memory"""
        self._table_cache.clear()

# Optimized Data Writer


class ArrowDataWriter:
    """High-performance data writer using Apache Arrow"""

    def __init__(self, config: DataConfig):
        self.config = config
        self.output_dir = Path(config.output_dir)

    def write_table(self, df: pd.DataFrame, category: str, stage: str,
                    table_name: str, partition_cols: Optional[List[str]] = None):
        """
        Write DataFrame with Arrow optimization

        Args:
            df: DataFrame to write
            category: Category name (e.g., 'wash_trading')
            stage: Stage name (e.g., 'intermediate', 'results')
            table_name: Table name
            partition_cols: Columns to partition by (for Parquet)
        """
        if df.empty:
            print(f"  Skipping empty table: {stage}/{category}/{table_name}")
            return

        # Create directory structure
        output_path = self.output_dir / stage / category
        output_path.mkdir(parents=True, exist_ok=True)

        format_lower = self.config.output_format.lower()

        if format_lower == 'parquet':
            self._write_parquet_arrow(
                df, output_path, table_name, partition_cols)
        elif format_lower == 'csv':
            self._write_csv(df, output_path, table_name)
        elif format_lower == 'json':
            self._write_json(df, output_path, table_name)
        elif format_lower == 'jsonl':
            self._write_jsonl(df, output_path, table_name)
        else:
            raise ValueError(
                f"Unsupported output format: {self.config.output_format}")

        print(f"  Saved: {stage}/{category}/{table_name} ({len(df):,} rows)")

    def _write_parquet_arrow(self, df: pd.DataFrame, output_path: Path,
                             table_name: str, partition_cols: Optional[List[str]] = None):
        """Write Parquet using Arrow for best compression and speed"""
        filepath = output_path / f"{table_name}.parquet"

        if ARROW_AVAILABLE:
            # Convert to Arrow table
            arrow_table = pa.Table.from_pandas(df)

            # Write with optimal settings
            pq.write_table(
                arrow_table,
                str(filepath),
                compression='snappy',  # Good balance of speed and compression
                use_dictionary=True,  # Efficient for categorical data
                write_statistics=True,  # Enable predicate pushdown
                version='2.6'  # Latest stable version
            )
        else:
            # Fallback to pandas
            df.to_parquet(filepath, index=False,
                          compression='snappy', engine='pyarrow')

    def _write_csv(self, df: pd.DataFrame, output_path: Path, table_name: str):
        """Write CSV with optional compression"""
        if self.config.compress_output:
            filepath = output_path / f"{table_name}.csv.gz"
            df.to_csv(filepath, index=False, compression='gzip')
        else:
            filepath = output_path / f"{table_name}.csv"
            df.to_csv(filepath, index=False)

    def _write_json(self, df: pd.DataFrame, output_path: Path, table_name: str):
        """Write JSON with optional compression"""
        if self.config.compress_output:
            filepath = output_path / f"{table_name}.json.gz"
            df.to_json(filepath, orient='records',
                       indent=2, compression='gzip')
        else:
            filepath = output_path / f"{table_name}.json"
            df.to_json(filepath, orient='records', indent=2)

    def _write_jsonl(self, df: pd.DataFrame, output_path: Path, table_name: str):
        """Write JSONL with optional compression"""
        if self.config.compress_output:
            filepath = output_path / f"{table_name}.jsonl.gz"
            df.to_json(filepath, orient='records',
                       lines=True, compression='gzip')
        else:
            filepath = output_path / f"{table_name}.jsonl"
            df.to_json(filepath, orient='records', lines=True)

# Helper Functions for Data Optimization


class DataOptimizer:
    """Utilities for optimizing DataFrame memory and performance"""

    @staticmethod
    def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame dtypes to reduce memory usage"""
        df_opt = df.copy()

        # Optimize integer columns
        int_cols = df_opt.select_dtypes(include=['int64']).columns
        for col in int_cols:
            col_min = df_opt[col].min()
            col_max = df_opt[col].max()

            if col_min >= 0:
                if col_max <= 255:
                    df_opt[col] = df_opt[col].astype('uint8')
                elif col_max <= 65535:
                    df_opt[col] = df_opt[col].astype('uint16')
                elif col_max <= 4294967295:
                    df_opt[col] = df_opt[col].astype('uint32')
            else:
                if col_min >= -128 and col_max <= 127:
                    df_opt[col] = df_opt[col].astype('int8')
                elif col_min >= -32768 and col_max <= 32767:
                    df_opt[col] = df_opt[col].astype('int16')
                elif col_min >= -2147483648 and col_max <= 2147483647:
                    df_opt[col] = df_opt[col].astype('int32')

        # Optimize float columns
        float_cols = df_opt.select_dtypes(include=['float64']).columns
        for col in float_cols:
            df_opt[col] = df_opt[col].astype('float32')

        # Convert object columns to category if beneficial
        obj_cols = df_opt.select_dtypes(include=['object']).columns
        for col in obj_cols:
            num_unique = df_opt[col].nunique()
            num_total = len(df_opt[col])

            # Convert to category if < 50% unique values
            if num_unique / num_total < 0.5:
                df_opt[col] = df_opt[col].astype('category')

        return df_opt

    @staticmethod
    def parse_json_columns(df: pd.DataFrame, json_cols: List[str]) -> pd.DataFrame:
        """Parse JSON string columns into lists (vectorized)"""
        df_parsed = df.copy()

        for col in json_cols:
            if col in df_parsed.columns and df_parsed[col].dtype == 'object':
                # Check if first non-null value is a string
                first_val = df_parsed[col].dropna().iloc[0] if len(
                    df_parsed[col].dropna()) > 0 else None

                if isinstance(first_val, str):
                    # Vectorized JSON parsing
                    df_parsed[f"{col}_list"] = df_parsed[col].apply(
                        lambda x: json.loads(x) if pd.notna(
                            x) and x != '' else []
                    )

        return df_parsed

    @staticmethod
    def convert_timestamps(df: pd.DataFrame, timestamp_cols: List[str]) -> pd.DataFrame:
        """Convert timestamp columns to datetime (vectorized)"""
        df_converted = df.copy()

        for col in timestamp_cols:
            if col in df_converted.columns:
                df_converted[col] = pd.to_datetime(
                    df_converted[col], errors='coerce')

        return df_converted

# Batch Processing for Large Datasets


class BatchProcessor:
    """Process large datasets in batches to manage memory"""

    def __init__(self, loader: ArrowDataLoader, batch_size: int = 100000):
        self.loader = loader
        self.batch_size = batch_size

    def process_table_in_batches(self, table_name: str,
                                 process_func,
                                 columns: Optional[List[str]] = None):
        # Process a large table in batches
        # Args:
        #     table_name: Name of table to process
        #     process_func: Function to apply to each batch
        #     columns: Columns to load
        # Returns:
        #     Combined results from all batches

        # For Parquet, we can use Arrow dataset API for efficient batching
        if self.loader.config.source_format == 'parquet' and ARROW_AVAILABLE:
            return self._process_parquet_batches(table_name, process_func, columns)
        else:
            # Fallback: load full table and process
            df = self.loader.load_table(table_name, columns=columns)
            return process_func(df)

    def _process_parquet_batches(self, table_name: str, process_func, columns: Optional[List[str]]):
        # Process Parquet file in batches using Arrow dataset API
        filepath = self.loader.source_dir / f"{table_name}.parquet"

        dataset = ds.dataset(str(filepath), format='parquet')

        results = []
        for batch in dataset.to_batches(batch_size=self.batch_size, columns=columns):
            batch_df = batch.to_pandas()
            result = process_func(batch_df)
            if result is not None:
                results.append(result)

        # Combine results
        if results:
            if isinstance(results[0], pd.DataFrame):
                return pd.concat(results, ignore_index=True)
            else:
                return results
        return None
