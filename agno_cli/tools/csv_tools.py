"""
CSV Toolkit for Agno CLI
Provides comprehensive CSV file reading, writing, manipulation, and analysis capabilities
"""

import csv
import json
import pandas as pd
import io
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
import numpy as np

console = Console()


@dataclass
class CSVInfo:
    """CSV file information structure"""
    filename: str
    path: str
    rows: int
    columns: int
    column_names: List[str]
    data_types: Dict[str, str]
    missing_values: Dict[str, int]
    file_size: int
    encoding: str
    delimiter: str
    created: datetime
    modified: datetime


@dataclass
class CSVOperationResult:
    """Result of CSV operations"""
    success: bool
    message: str
    operation: str
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'error': self.error,
            'operation': self.operation,
            'timestamp': self.timestamp.isoformat()
        }


class CSVTools:
    """Comprehensive CSV file operations tool"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.supported_encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        self.supported_delimiters = [',', ';', '\t', '|', ' ']
    
    def _ensure_safe_path(self, path: Union[str, Path]) -> Path:
        """Ensure path is safe and within allowed directory"""
        path = Path(path)
        
        # Resolve relative paths
        if not path.is_absolute():
            path = self.base_path / path
        
        # Ensure path is within base directory for security
        try:
            path = path.resolve()
            if not str(path).startswith(str(self.base_path.resolve())):
                raise ValueError(f"Path {path} is outside allowed directory")
        except (RuntimeError, ValueError) as e:
            raise ValueError(f"Invalid path: {e}")
        
        return path
    
    def _detect_encoding_and_delimiter(self, file_path: Path) -> Tuple[str, str]:
        """Detect CSV encoding and delimiter"""
        # Try to detect encoding
        encoding = 'utf-8'
        for enc in self.supported_encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    sample = f.read(1024)
                    if sample:
                        encoding = enc
                        break
            except UnicodeDecodeError:
                continue
        
        # Try to detect delimiter
        delimiter = ','
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                sample = f.read(1024)
                if sample:
                    # Use pandas to detect delimiter
                    try:
                        detected = pd.read_csv(io.StringIO(sample), sep=None, engine='python')
                        delimiter = detected._engine.delimiter
                    except:
                        # Fallback to comma
                        delimiter = ','
        except Exception:
            delimiter = ','
        
        return encoding, delimiter
    
    def read_csv(self, path: str, encoding: str = None, delimiter: str = None, 
                 max_rows: int = None, sample: bool = False, sample_size: int = 10) -> CSVOperationResult:
        """Read CSV file and return data"""
        try:
            target_path = self._ensure_safe_path(path)
            
            if not target_path.exists():
                return CSVOperationResult(
                    success=False,
                    message=f"CSV file does not exist: {path}",
                    error="FileNotFound",
                    operation="read_csv"
                )
            
            if not target_path.is_file():
                return CSVOperationResult(
                    success=False,
                    message=f"Path is not a file: {path}",
                    error="NotFile",
                    operation="read_csv"
                )
            
            # Detect encoding and delimiter if not provided
            if encoding is None or delimiter is None:
                detected_encoding, detected_delimiter = self._detect_encoding_and_delimiter(target_path)
                encoding = encoding or detected_encoding
                delimiter = delimiter or detected_delimiter
            
            # Read CSV with pandas
            try:
                if sample:
                    df = pd.read_csv(target_path, encoding=encoding, sep=delimiter, nrows=sample_size)
                elif max_rows:
                    df = pd.read_csv(target_path, encoding=encoding, sep=delimiter, nrows=max_rows)
                else:
                    df = pd.read_csv(target_path, encoding=encoding, sep=delimiter)
            except Exception as e:
                return CSVOperationResult(
                    success=False,
                    message=f"Error reading CSV file: {str(e)}",
                    error=str(e),
                    operation="read_csv"
                )
            
            # Get file info
            file_info = self._get_csv_info(target_path, df, encoding, delimiter)
            
            # Convert DataFrame to records for easier handling
            records = df.to_dict('records')
            
            return CSVOperationResult(
                success=True,
                message=f"Successfully read CSV file: {path} ({len(records)} rows, {len(df.columns)} columns)",
                data={
                    'records': records,
                    'columns': df.columns.tolist(),
                    'dataframe': df,
                    'file_info': asdict(file_info)
                },
                operation="read_csv"
            )
            
        except Exception as e:
            return CSVOperationResult(
                success=False,
                message=f"Error reading CSV: {str(e)}",
                error=str(e),
                operation="read_csv"
            )
    
    def write_csv(self, path: str, data: List[Dict], columns: List[str] = None,
                  encoding: str = "utf-8", delimiter: str = ",", overwrite: bool = True) -> CSVOperationResult:
        """Write data to CSV file"""
        try:
            target_path = self._ensure_safe_path(path)
            
            if not data:
                return CSVOperationResult(
                    success=False,
                    message="No data provided to write",
                    error="NoData",
                    operation="write_csv"
                )
            
            # Check if file exists and overwrite flag
            if target_path.exists() and not overwrite:
                return CSVOperationResult(
                    success=False,
                    message=f"File already exists and overwrite=False: {path}",
                    error="FileExists",
                    operation="write_csv"
                )
            
            # Create parent directories if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Determine columns if not provided
            if columns is None:
                columns = list(data[0].keys()) if data else []
            
            # Write CSV
            try:
                with open(target_path, 'w', newline='', encoding=encoding) as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=columns, delimiter=delimiter)
                    writer.writeheader()
                    writer.writerows(data)
            except Exception as e:
                return CSVOperationResult(
                    success=False,
                    message=f"Error writing CSV file: {str(e)}",
                    error=str(e),
                    operation="write_csv"
                )
            
            # Get file info
            df = pd.DataFrame(data)
            file_info = self._get_csv_info(target_path, df, encoding, delimiter)
            
            return CSVOperationResult(
                success=True,
                message=f"Successfully wrote CSV file: {path} ({len(data)} rows, {len(columns)} columns)",
                data={
                    'file_info': asdict(file_info),
                    'rows_written': len(data),
                    'columns_written': len(columns)
                },
                operation="write_csv"
            )
            
        except Exception as e:
            return CSVOperationResult(
                success=False,
                message=f"Error writing CSV: {str(e)}",
                error=str(e),
                operation="write_csv"
            )
    
    def get_csv_info(self, path: str) -> CSVOperationResult:
        """Get detailed information about CSV file"""
        try:
            target_path = self._ensure_safe_path(path)
            
            if not target_path.exists():
                return CSVOperationResult(
                    success=False,
                    message=f"CSV file does not exist: {path}",
                    error="FileNotFound",
                    operation="get_csv_info"
                )
            
            # Detect encoding and delimiter
            encoding, delimiter = self._detect_encoding_and_delimiter(target_path)
            
            # Read CSV
            try:
                df = pd.read_csv(target_path, encoding=encoding, sep=delimiter)
            except Exception as e:
                return CSVOperationResult(
                    success=False,
                    message=f"Error reading CSV file: {str(e)}",
                    error=str(e),
                    operation="get_csv_info"
                )
            
            # Get file info
            file_info = self._get_csv_info(target_path, df, encoding, delimiter)
            
            return CSVOperationResult(
                success=True,
                message=f"CSV file information retrieved: {path}",
                data=asdict(file_info),
                operation="get_csv_info"
            )
            
        except Exception as e:
            return CSVOperationResult(
                success=False,
                message=f"Error getting CSV info: {str(e)}",
                error=str(e),
                operation="get_csv_info"
            )
    
    def _get_csv_info(self, file_path: Path, df: pd.DataFrame, encoding: str, delimiter: str) -> CSVInfo:
        """Get CSV file information"""
        # Get file stats
        stat = file_path.stat()
        
        # Analyze data types
        data_types = {}
        for col in df.columns:
            if df[col].dtype == 'object':
                data_types[col] = 'string'
            elif df[col].dtype == 'int64':
                data_types[col] = 'integer'
            elif df[col].dtype == 'float64':
                data_types[col] = 'float'
            elif df[col].dtype == 'bool':
                data_types[col] = 'boolean'
            elif df[col].dtype == 'datetime64[ns]':
                data_types[col] = 'datetime'
            else:
                data_types[col] = str(df[col].dtype)
        
        # Count missing values
        missing_values = {}
        for col in df.columns:
            missing_values[col] = df[col].isnull().sum()
        
        return CSVInfo(
            filename=file_path.name,
            path=str(file_path),
            rows=len(df),
            columns=len(df.columns),
            column_names=df.columns.tolist(),
            data_types=data_types,
            missing_values=missing_values,
            file_size=stat.st_size,
            encoding=encoding,
            delimiter=delimiter,
            created=datetime.fromtimestamp(stat.st_ctime),
            modified=datetime.fromtimestamp(stat.st_mtime)
        )
    
    def filter_csv(self, path: str, filters: Dict[str, Any], output_path: str = None) -> CSVOperationResult:
        """Filter CSV data based on conditions"""
        try:
            # Read CSV
            read_result = self.read_csv(path)
            if not read_result.success:
                return read_result
            
            df = read_result.data['dataframe']
            
            # Apply filters
            filtered_df = df.copy()
            for column, condition in filters.items():
                if column in df.columns:
                    if isinstance(condition, dict):
                        # Range filter
                        if 'min' in condition:
                            filtered_df = filtered_df[filtered_df[column] >= condition['min']]
                        if 'max' in condition:
                            filtered_df = filtered_df[filtered_df[column] <= condition['max']]
                        if 'contains' in condition:
                            filtered_df = filtered_df[filtered_df[column].str.contains(condition['contains'], na=False)]
                    elif isinstance(condition, list):
                        # In filter
                        filtered_df = filtered_df[filtered_df[column].isin(condition)]
                    else:
                        # Exact match
                        filtered_df = filtered_df[filtered_df[column] == condition]
            
            # Convert to records
            records = filtered_df.to_dict('records')
            
            # Write to output file if specified
            if output_path:
                write_result = self.write_csv(output_path, records, list(filtered_df.columns))
                if not write_result.success:
                    return write_result
            
            return CSVOperationResult(
                success=True,
                message=f"Filtered CSV data: {len(records)} rows remaining from {len(df)} original rows",
                data={
                    'records': records,
                    'columns': filtered_df.columns.tolist(),
                    'dataframe': filtered_df,
                    'filters_applied': filters,
                    'rows_filtered': len(df) - len(records)
                },
                operation="filter_csv"
            )
            
        except Exception as e:
            return CSVOperationResult(
                success=False,
                message=f"Error filtering CSV: {str(e)}",
                error=str(e),
                operation="filter_csv"
            )
    
    def sort_csv(self, path: str, sort_columns: List[str], ascending: List[bool] = None,
                 output_path: str = None) -> CSVOperationResult:
        """Sort CSV data by columns"""
        try:
            # Read CSV
            read_result = self.read_csv(path)
            if not read_result.success:
                return read_result
            
            df = read_result.data['dataframe']
            
            # Set default ascending order
            if ascending is None:
                ascending = [True] * len(sort_columns)
            
            # Sort DataFrame
            sorted_df = df.sort_values(by=sort_columns, ascending=ascending)
            
            # Convert to records
            records = sorted_df.to_dict('records')
            
            # Write to output file if specified
            if output_path:
                write_result = self.write_csv(output_path, records, list(sorted_df.columns))
                if not write_result.success:
                    return write_result
            
            return CSVOperationResult(
                success=True,
                message=f"Sorted CSV data by {', '.join(sort_columns)}",
                data={
                    'records': records,
                    'columns': sorted_df.columns.tolist(),
                    'dataframe': sorted_df,
                    'sort_columns': sort_columns,
                    'ascending': ascending
                },
                operation="sort_csv"
            )
            
        except Exception as e:
            return CSVOperationResult(
                success=False,
                message=f"Error sorting CSV: {str(e)}",
                error=str(e),
                operation="sort_csv"
            )
    
    def analyze_csv(self, path: str) -> CSVOperationResult:
        """Perform comprehensive analysis of CSV data"""
        try:
            # Read CSV
            read_result = self.read_csv(path)
            if not read_result.success:
                return read_result
            
            df = read_result.data['dataframe']
            
            # Basic statistics
            basic_stats = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values_total': df.isnull().sum().sum(),
                'duplicate_rows': df.duplicated().sum()
            }
            
            # Column analysis
            column_analysis = {}
            for col in df.columns:
                col_stats = {
                    'data_type': str(df[col].dtype),
                    'missing_values': df[col].isnull().sum(),
                    'unique_values': df[col].nunique(),
                    'most_common': df[col].mode().iloc[0] if not df[col].mode().empty else None
                }
                
                # Numeric statistics
                if df[col].dtype in ['int64', 'float64']:
                    col_stats.update({
                        'mean': df[col].mean(),
                        'median': df[col].median(),
                        'std': df[col].std(),
                        'min': df[col].min(),
                        'max': df[col].max(),
                        'quartiles': df[col].quantile([0.25, 0.5, 0.75]).to_dict()
                    })
                
                column_analysis[col] = col_stats
            
            # Correlation analysis for numeric columns
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            correlation_matrix = {}
            if len(numeric_columns) > 1:
                correlation_matrix = df[numeric_columns].corr().to_dict()
            
            return CSVOperationResult(
                success=True,
                message=f"CSV analysis completed for {path}",
                data={
                    'basic_stats': basic_stats,
                    'column_analysis': column_analysis,
                    'correlation_matrix': correlation_matrix,
                    'numeric_columns': numeric_columns.tolist(),
                    'categorical_columns': df.select_dtypes(include=['object']).columns.tolist()
                },
                operation="analyze_csv"
            )
            
        except Exception as e:
            return CSVOperationResult(
                success=False,
                message=f"Error analyzing CSV: {str(e)}",
                error=str(e),
                operation="analyze_csv"
            )
    
    def merge_csv(self, file1: str, file2: str, merge_key: str, how: str = "inner",
                  output_path: str = None) -> CSVOperationResult:
        """Merge two CSV files"""
        try:
            # Read both CSV files
            read1_result = self.read_csv(file1)
            if not read1_result.success:
                return read1_result
            
            read2_result = self.read_csv(file2)
            if not read2_result.success:
                return read2_result
            
            df1 = read1_result.data['dataframe']
            df2 = read2_result.data['dataframe']
            
            # Check if merge key exists in both dataframes
            if merge_key not in df1.columns or merge_key not in df2.columns:
                return CSVOperationResult(
                    success=False,
                    message=f"Merge key '{merge_key}' not found in one or both CSV files",
                    error="MergeKeyNotFound",
                    operation="merge_csv"
                )
            
            # Merge dataframes
            merged_df = pd.merge(df1, df2, on=merge_key, how=how)
            
            # Convert to records
            records = merged_df.to_dict('records')
            
            # Write to output file if specified
            if output_path:
                write_result = self.write_csv(output_path, records, list(merged_df.columns))
                if not write_result.success:
                    return write_result
            
            return CSVOperationResult(
                success=True,
                message=f"Merged CSV files: {len(records)} rows in merged dataset",
                data={
                    'records': records,
                    'columns': merged_df.columns.tolist(),
                    'dataframe': merged_df,
                    'merge_key': merge_key,
                    'merge_type': how,
                    'original_rows_1': len(df1),
                    'original_rows_2': len(df2),
                    'merged_rows': len(merged_df)
                },
                operation="merge_csv"
            )
            
        except Exception as e:
            return CSVOperationResult(
                success=False,
                message=f"Error merging CSV files: {str(e)}",
                error=str(e),
                operation="merge_csv"
            )
    
    def convert_format(self, input_path: str, output_path: str, output_format: str = "json") -> CSVOperationResult:
        """Convert CSV to other formats"""
        try:
            # Read CSV
            read_result = self.read_csv(input_path)
            if not read_result.success:
                return read_result
            
            df = read_result.data['dataframe']
            
            if output_format.lower() == "json":
                # Convert to JSON
                json_data = df.to_dict('records')
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, default=str)
                
                return CSVOperationResult(
                    success=True,
                    message=f"Converted CSV to JSON: {output_path}",
                    data={
                        'output_format': 'json',
                        'rows_converted': len(json_data),
                        'output_path': output_path
                    },
                    operation="convert_format"
                )
            
            elif output_format.lower() == "excel":
                # Convert to Excel
                df.to_excel(output_path, index=False)
                
                return CSVOperationResult(
                    success=True,
                    message=f"Converted CSV to Excel: {output_path}",
                    data={
                        'output_format': 'excel',
                        'rows_converted': len(df),
                        'output_path': output_path
                    },
                    operation="convert_format"
                )
            
            else:
                return CSVOperationResult(
                    success=False,
                    message=f"Unsupported output format: {output_format}",
                    error="UnsupportedFormat",
                    operation="convert_format"
                )
            
        except Exception as e:
            return CSVOperationResult(
                success=False,
                message=f"Error converting format: {str(e)}",
                error=str(e),
                operation="convert_format"
            )


class CSVToolsManager:
    """Manager class for CSV operations with CLI integration"""
    
    def __init__(self, base_path: str = None):
        self.csv_tools = CSVTools(base_path)
        self.console = Console()
    
    def read_csv(self, path: str, encoding: str = None, delimiter: str = None, 
                 max_rows: int = None, sample: bool = False, sample_size: int = 10,
                 format: str = "table") -> None:
        """Read and display CSV contents"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Reading CSV file...", total=None)
            result = self.csv_tools.read_csv(path, encoding, delimiter, max_rows, sample, sample_size)
        
        if not result.success:
            self.console.print(f"[red]{result.message}[/red]")
            return
        
        data = result.data
        records = data['records']
        file_info = data['file_info']
        
        if format == "table":
            self._display_csv_table(records, file_info, path)
        elif format == "json":
            self.console.print(json.dumps(records, indent=2, default=str))
        else:
            self.console.print(records)
    
    def _display_csv_table(self, records: List[Dict], file_info: Dict, path: str) -> None:
        """Display CSV data in a rich table"""
        if not records:
            self.console.print("[yellow]No data to display[/yellow]")
            return
        
        # Create table
        table = Table(show_header=True, header_style="bold magenta", title=f"CSV Data: {path}")
        
        # Add columns
        columns = list(records[0].keys())
        for col in columns:
            table.add_column(col, style="cyan", max_width=30)
        
        # Add rows (limit to first 100 for display)
        display_records = records[:100]
        for record in display_records:
            row_data = []
            for col in columns:
                value = record.get(col, '')
                if value is None:
                    value = 'NULL'
                elif isinstance(value, (int, float)):
                    value = f"{value:,}" if isinstance(value, int) else f"{value:.2f}"
                else:
                    value = str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
                row_data.append(value)
            table.add_row(*row_data)
        
        # Display file info
        info_text = f"""
**File:** {file_info['filename']}
**Rows:** {file_info['rows']:,}
**Columns:** {file_info['columns']}
**Encoding:** {file_info['encoding']}
**Delimiter:** '{file_info['delimiter']}'
**File Size:** {file_info['file_size']:,} bytes
"""
        
        self.console.print(Panel(
            Markdown(info_text),
            title="File Information",
            border_style="blue"
        ))
        
        self.console.print(table)
        
        if len(records) > 100:
            self.console.print(f"[yellow]Showing first 100 rows of {len(records):,} total rows[/yellow]")
    
    def write_csv(self, path: str, data: List[Dict], columns: List[str] = None,
                  encoding: str = "utf-8", delimiter: str = ",", overwrite: bool = True) -> None:
        """Write data to CSV with feedback"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Writing CSV file...", total=None)
            result = self.csv_tools.write_csv(path, data, columns, encoding, delimiter, overwrite)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            data = result.data
            self.console.print(f"📄 File: {path} ({data['rows_written']} rows, {data['columns_written']} columns)")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def get_csv_info(self, path: str, format: str = "table") -> None:
        """Get and display CSV information"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Analyzing CSV file...", total=None)
            result = self.csv_tools.get_csv_info(path)
        
        if not result.success:
            self.console.print(f"[red]{result.message}[/red]")
            return
        
        file_info = result.data
        
        if format == "table":
            # Basic info table
            basic_table = Table(show_header=True, header_style="bold magenta")
            basic_table.add_column("Property", style="cyan")
            basic_table.add_column("Value", style="green")
            
            basic_table.add_row("Filename", file_info['filename'])
            basic_table.add_row("Path", file_info['path'])
            basic_table.add_row("Rows", f"{file_info['rows']:,}")
            basic_table.add_row("Columns", str(file_info['columns']))
            basic_table.add_row("File Size", f"{file_info['file_size']:,} bytes")
            basic_table.add_row("Encoding", file_info['encoding'])
            basic_table.add_row("Delimiter", f"'{file_info['delimiter']}'")
            basic_table.add_row("Created", str(file_info['created']))
            basic_table.add_row("Modified", str(file_info['modified']))
            
            self.console.print(basic_table)
            
            # Column info table
            if file_info['column_names']:
                col_table = Table(show_header=True, header_style="bold magenta", title="Column Information")
                col_table.add_column("Column", style="cyan")
                col_table.add_column("Data Type", style="blue")
                col_table.add_column("Missing Values", style="red")
                
                for col in file_info['column_names']:
                    data_type = file_info['data_types'].get(col, 'unknown')
                    missing = file_info['missing_values'].get(col, 0)
                    col_table.add_row(col, data_type, str(missing))
                
                self.console.print(col_table)
        
        elif format == "json":
            self.console.print(json.dumps(file_info, indent=2, default=str))
    
    def analyze_csv(self, path: str, format: str = "table") -> None:
        """Analyze CSV data and display results"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Analyzing CSV data...", total=None)
            result = self.csv_tools.analyze_csv(path)
        
        if not result.success:
            self.console.print(f"[red]{result.message}[/red]")
            return
        
        data = result.data
        
        if format == "table":
            # Basic statistics
            basic_stats = data['basic_stats']
            stats_table = Table(show_header=True, header_style="bold magenta", title="Basic Statistics")
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="green")
            
            stats_table.add_row("Total Rows", f"{basic_stats['total_rows']:,}")
            stats_table.add_row("Total Columns", str(basic_stats['total_columns']))
            stats_table.add_row("Missing Values", f"{basic_stats['missing_values_total']:,}")
            stats_table.add_row("Duplicate Rows", f"{basic_stats['duplicate_rows']:,}")
            
            self.console.print(stats_table)
            
            # Column analysis
            col_analysis = data['column_analysis']
            if col_analysis:
                analysis_table = Table(show_header=True, header_style="bold magenta", title="Column Analysis")
                analysis_table.add_column("Column", style="cyan")
                analysis_table.add_column("Type", style="blue")
                analysis_table.add_column("Missing", style="red")
                analysis_table.add_column("Unique", style="yellow")
                analysis_table.add_column("Mean", style="green")
                analysis_table.add_column("Min", style="green")
                analysis_table.add_column("Max", style="green")
                
                for col, stats in col_analysis.items():
                    mean_val = f"{stats.get('mean', 'N/A'):.2f}" if stats.get('mean') is not None else 'N/A'
                    min_val = f"{stats.get('min', 'N/A'):.2f}" if stats.get('min') is not None else 'N/A'
                    max_val = f"{stats.get('max', 'N/A'):.2f}" if stats.get('max') is not None else 'N/A'
                    
                    analysis_table.add_row(
                        col,
                        stats['data_type'],
                        str(stats['missing_values']),
                        str(stats['unique_values']),
                        mean_val,
                        min_val,
                        max_val
                    )
                
                self.console.print(analysis_table)
        
        elif format == "json":
            self.console.print(json.dumps(data, indent=2, default=str))
    
    def filter_csv(self, path: str, filters: Dict[str, Any], output_path: str = None) -> None:
        """Filter CSV data and display results"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Filtering CSV data...", total=None)
            result = self.csv_tools.filter_csv(path, filters, output_path)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            data = result.data
            self.console.print(f"📊 Filters applied: {data['filters_applied']}")
            self.console.print(f"📈 Rows filtered: {data['rows_filtered']:,}")
            if output_path:
                self.console.print(f"💾 Output saved to: {output_path}")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def sort_csv(self, path: str, sort_columns: List[str], ascending: List[bool] = None,
                 output_path: str = None) -> None:
        """Sort CSV data and display results"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Sorting CSV data...", total=None)
            result = self.csv_tools.sort_csv(path, sort_columns, ascending, output_path)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            data = result.data
            self.console.print(f"📊 Sorted by: {', '.join(data['sort_columns'])}")
            if output_path:
                self.console.print(f"💾 Output saved to: {output_path}")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def merge_csv(self, file1: str, file2: str, merge_key: str, how: str = "inner",
                  output_path: str = None) -> None:
        """Merge CSV files and display results"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Merging CSV files...", total=None)
            result = self.csv_tools.merge_csv(file1, file2, merge_key, how, output_path)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            data = result.data
            self.console.print(f"🔗 Merge key: {data['merge_key']}")
            self.console.print(f"📊 Merge type: {data['merge_type']}")
            self.console.print(f"📈 Original rows: {data['original_rows_1']:,} + {data['original_rows_2']:,}")
            self.console.print(f"📊 Merged rows: {data['merged_rows']:,}")
            if output_path:
                self.console.print(f"💾 Output saved to: {output_path}")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def convert_format(self, input_path: str, output_path: str, output_format: str = "json") -> None:
        """Convert CSV to other formats"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task(f"Converting to {output_format.upper()}...", total=None)
            result = self.csv_tools.convert_format(input_path, output_path, output_format)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            data = result.data
            self.console.print(f"📊 Rows converted: {data['rows_converted']:,}")
            self.console.print(f"💾 Output saved to: {data['output_path']}")
        else:
            self.console.print(f"[red]{result.message}[/red]") 