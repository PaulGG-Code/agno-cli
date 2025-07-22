"""
Pandas Toolkit for Agno CLI
Provides advanced data manipulation, analysis, and visualization capabilities
"""

import pandas as pd
import numpy as np
import json
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
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

console = Console()

# Set matplotlib to use non-interactive backend for CLI
plt.switch_backend('Agg')


@dataclass
class PandasAnalysisResult:
    """Result of pandas analysis operations"""
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


@dataclass
class DataFrameInfo:
    """DataFrame information structure"""
    shape: Tuple[int, int]
    columns: List[str]
    data_types: Dict[str, str]
    memory_usage: int
    missing_values: Dict[str, int]
    duplicate_rows: int
    numeric_columns: List[str]
    categorical_columns: List[str]
    datetime_columns: List[str]
    object_columns: List[str]


class PandasTools:
    """Advanced pandas data manipulation and analysis tool"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.supported_formats = ['csv', 'json', 'excel', 'parquet', 'pickle', 'hdf5']
    
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
    
    def read_data(self, path: str, format: str = None, **kwargs) -> PandasAnalysisResult:
        """Read data from various formats"""
        try:
            target_path = self._ensure_safe_path(path)
            
            if not target_path.exists():
                return PandasAnalysisResult(
                    success=False,
                    message=f"File does not exist: {path}",
                    error="FileNotFound",
                    operation="read_data"
                )
            
            # Auto-detect format if not specified
            if format is None:
                format = target_path.suffix.lstrip('.').lower()
                if format not in self.supported_formats:
                    format = 'csv'  # Default to CSV
            
            # Read data based on format
            try:
                if format == 'csv':
                    df = pd.read_csv(target_path, **kwargs)
                elif format == 'json':
                    df = pd.read_json(target_path, **kwargs)
                elif format == 'excel':
                    df = pd.read_excel(target_path, **kwargs)
                elif format == 'parquet':
                    df = pd.read_parquet(target_path, **kwargs)
                elif format == 'pickle':
                    df = pd.read_pickle(target_path, **kwargs)
                elif format == 'hdf5':
                    df = pd.read_hdf(target_path, **kwargs)
                else:
                    return PandasAnalysisResult(
                        success=False,
                        message=f"Unsupported format: {format}",
                        error="UnsupportedFormat",
                        operation="read_data"
                    )
            except Exception as e:
                return PandasAnalysisResult(
                    success=False,
                    message=f"Error reading {format} file: {str(e)}",
                    error=str(e),
                    operation="read_data"
                )
            
            # Get DataFrame info
            df_info = self._get_dataframe_info(df)
            
            return PandasAnalysisResult(
                success=True,
                message=f"Successfully read {format.upper()} file: {path} ({df.shape[0]} rows, {df.shape[1]} columns)",
                data={
                    'dataframe': df,
                    'info': asdict(df_info),
                    'format': format,
                    'path': str(target_path)
                },
                operation="read_data"
            )
            
        except Exception as e:
            return PandasAnalysisResult(
                success=False,
                message=f"Error reading data: {str(e)}",
                error=str(e),
                operation="read_data"
            )
    
    def write_data(self, df: pd.DataFrame, path: str, format: str = 'csv', **kwargs) -> PandasAnalysisResult:
        """Write DataFrame to various formats"""
        try:
            target_path = self._ensure_safe_path(path)
            
            # Create parent directories if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write data based on format
            try:
                if format == 'csv':
                    df.to_csv(target_path, **kwargs)
                elif format == 'json':
                    df.to_json(target_path, **kwargs)
                elif format == 'excel':
                    df.to_excel(target_path, **kwargs)
                elif format == 'parquet':
                    df.to_parquet(target_path, **kwargs)
                elif format == 'pickle':
                    df.to_pickle(target_path, **kwargs)
                elif format == 'hdf5':
                    df.to_hdf(target_path, key='data', **kwargs)
                else:
                    return PandasAnalysisResult(
                        success=False,
                        message=f"Unsupported format: {format}",
                        error="UnsupportedFormat",
                        operation="write_data"
                    )
            except Exception as e:
                return PandasAnalysisResult(
                    success=False,
                    message=f"Error writing {format} file: {str(e)}",
                    error=str(e),
                    operation="write_data"
                )
            
            return PandasAnalysisResult(
                success=True,
                message=f"Successfully wrote {format.upper()} file: {path} ({df.shape[0]} rows, {df.shape[1]} columns)",
                data={
                    'rows_written': df.shape[0],
                    'columns_written': df.shape[1],
                    'format': format,
                    'path': str(target_path)
                },
                operation="write_data"
            )
            
        except Exception as e:
            return PandasAnalysisResult(
                success=False,
                message=f"Error writing data: {str(e)}",
                error=str(e),
                operation="write_data"
            )
    
    def _get_dataframe_info(self, df: pd.DataFrame) -> DataFrameInfo:
        """Get comprehensive DataFrame information"""
        # Categorize columns by data type
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=['category']).columns.tolist()
        datetime_columns = df.select_dtypes(include=['datetime64']).columns.tolist()
        object_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        # Get data types
        data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        # Count missing values
        missing_values = df.isnull().sum().to_dict()
        
        return DataFrameInfo(
            shape=df.shape,
            columns=df.columns.tolist(),
            data_types=data_types,
            memory_usage=df.memory_usage(deep=True).sum(),
            missing_values=missing_values,
            duplicate_rows=df.duplicated().sum(),
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            datetime_columns=datetime_columns,
            object_columns=object_columns
        )
    
    def analyze_data(self, df: pd.DataFrame) -> PandasAnalysisResult:
        """Perform comprehensive data analysis"""
        try:
            # Basic statistics
            basic_stats = {
                'shape': df.shape,
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
                'missing_values_total': df.isnull().sum().sum(),
                'missing_percentage': (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100,
                'duplicate_rows': df.duplicated().sum(),
                'duplicate_percentage': (df.duplicated().sum() / df.shape[0]) * 100
            }
            
            # Column analysis
            column_analysis = {}
            for col in df.columns:
                col_stats = {
                    'data_type': str(df[col].dtype),
                    'missing_values': df[col].isnull().sum(),
                    'missing_percentage': (df[col].isnull().sum() / len(df)) * 100,
                    'unique_values': df[col].nunique(),
                    'unique_percentage': (df[col].nunique() / len(df)) * 100
                }
                
                # Numeric statistics
                if df[col].dtype in ['int64', 'float64']:
                    col_stats.update({
                        'mean': df[col].mean(),
                        'median': df[col].median(),
                        'std': df[col].std(),
                        'min': df[col].min(),
                        'max': df[col].max(),
                        'quartiles': df[col].quantile([0.25, 0.5, 0.75]).to_dict(),
                        'skewness': df[col].skew(),
                        'kurtosis': df[col].kurtosis()
                    })
                
                # Categorical statistics
                elif df[col].dtype == 'object' or df[col].dtype == 'category':
                    value_counts = df[col].value_counts()
                    col_stats.update({
                        'most_common': value_counts.index[0] if not value_counts.empty else None,
                        'most_common_count': value_counts.iloc[0] if not value_counts.empty else 0,
                        'top_values': value_counts.head(5).to_dict()
                    })
                
                column_analysis[col] = col_stats
            
            # Correlation analysis for numeric columns
            numeric_df = df.select_dtypes(include=[np.number])
            correlation_matrix = {}
            if numeric_df.shape[1] > 1:
                correlation_matrix = numeric_df.corr().to_dict()
            
            # Summary statistics
            summary_stats = df.describe().to_dict()
            
            return PandasAnalysisResult(
                success=True,
                message=f"Data analysis completed for DataFrame ({df.shape[0]} rows, {df.shape[1]} columns)",
                data={
                    'basic_stats': basic_stats,
                    'column_analysis': column_analysis,
                    'correlation_matrix': correlation_matrix,
                    'summary_stats': summary_stats,
                    'numeric_columns': numeric_df.columns.tolist(),
                    'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist()
                },
                operation="analyze_data"
            )
            
        except Exception as e:
            return PandasAnalysisResult(
                success=False,
                message=f"Error analyzing data: {str(e)}",
                error=str(e),
                operation="analyze_data"
            )
    
    def clean_data(self, df: pd.DataFrame, operations: Dict[str, Any]) -> PandasAnalysisResult:
        """Clean and preprocess data"""
        try:
            cleaned_df = df.copy()
            operations_applied = []
            
            # Handle missing values
            if 'handle_missing' in operations:
                strategy = operations['handle_missing']
                if strategy == 'drop':
                    cleaned_df = cleaned_df.dropna()
                    operations_applied.append(f"Dropped rows with missing values")
                elif strategy == 'fill_mean':
                    numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
                    cleaned_df[numeric_cols] = cleaned_df[numeric_cols].fillna(cleaned_df[numeric_cols].mean())
                    operations_applied.append(f"Filled missing values with mean for numeric columns")
                elif strategy == 'fill_median':
                    numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
                    cleaned_df[numeric_cols] = cleaned_df[numeric_cols].fillna(cleaned_df[numeric_cols].median())
                    operations_applied.append(f"Filled missing values with median for numeric columns")
                elif strategy == 'fill_mode':
                    for col in cleaned_df.columns:
                        if cleaned_df[col].dtype == 'object':
                            mode_val = cleaned_df[col].mode()
                            if not mode_val.empty:
                                cleaned_df[col] = cleaned_df[col].fillna(mode_val.iloc[0])
                    operations_applied.append(f"Filled missing values with mode for categorical columns")
            
            # Remove duplicates
            if operations.get('remove_duplicates', False):
                initial_rows = len(cleaned_df)
                cleaned_df = cleaned_df.drop_duplicates()
                removed_rows = initial_rows - len(cleaned_df)
                operations_applied.append(f"Removed {removed_rows} duplicate rows")
            
            # Handle outliers
            if 'handle_outliers' in operations:
                method = operations['handle_outliers']
                if method == 'iqr':
                    numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
                    for col in numeric_cols:
                        Q1 = cleaned_df[col].quantile(0.25)
                        Q3 = cleaned_df[col].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        cleaned_df = cleaned_df[(cleaned_df[col] >= lower_bound) & (cleaned_df[col] <= upper_bound)]
                    operations_applied.append(f"Removed outliers using IQR method")
                elif method == 'zscore':
                    numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
                    for col in numeric_cols:
                        z_scores = np.abs((cleaned_df[col] - cleaned_df[col].mean()) / cleaned_df[col].std())
                        cleaned_df = cleaned_df[z_scores < 3]
                    operations_applied.append(f"Removed outliers using Z-score method")
            
            # Convert data types
            if 'convert_types' in operations:
                type_conversions = operations['convert_types']
                for col, target_type in type_conversions.items():
                    if col in cleaned_df.columns:
                        try:
                            if target_type == 'datetime':
                                cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                            elif target_type == 'category':
                                cleaned_df[col] = cleaned_df[col].astype('category')
                            elif target_type == 'numeric':
                                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
                            operations_applied.append(f"Converted {col} to {target_type}")
                        except Exception as e:
                            operations_applied.append(f"Failed to convert {col} to {target_type}: {str(e)}")
            
            return PandasAnalysisResult(
                success=True,
                message=f"Data cleaning completed. Applied {len(operations_applied)} operations",
                data={
                    'cleaned_dataframe': cleaned_df,
                    'operations_applied': operations_applied,
                    'original_shape': df.shape,
                    'cleaned_shape': cleaned_df.shape,
                    'rows_removed': df.shape[0] - cleaned_df.shape[0],
                    'columns_removed': df.shape[1] - cleaned_df.shape[1]
                },
                operation="clean_data"
            )
            
        except Exception as e:
            return PandasAnalysisResult(
                success=False,
                message=f"Error cleaning data: {str(e)}",
                error=str(e),
                operation="clean_data"
            )
    
    def transform_data(self, df: pd.DataFrame, operations: Dict[str, Any]) -> PandasAnalysisResult:
        """Transform and engineer features"""
        try:
            transformed_df = df.copy()
            operations_applied = []
            
            # Column operations
            if 'columns' in operations:
                col_ops = operations['columns']
                
                # Rename columns
                if 'rename' in col_ops:
                    rename_map = col_ops['rename']
                    transformed_df = transformed_df.rename(columns=rename_map)
                    operations_applied.append(f"Renamed {len(rename_map)} columns")
                
                # Drop columns
                if 'drop' in col_ops:
                    columns_to_drop = col_ops['drop']
                    transformed_df = transformed_df.drop(columns=columns_to_drop, errors='ignore')
                    operations_applied.append(f"Dropped {len(columns_to_drop)} columns")
                
                # Select columns
                if 'select' in col_ops:
                    columns_to_select = col_ops['select']
                    transformed_df = transformed_df[columns_to_select]
                    operations_applied.append(f"Selected {len(columns_to_select)} columns")
            
            # Row operations
            if 'rows' in operations:
                row_ops = operations['rows']
                
                # Filter rows
                if 'filter' in row_ops:
                    filter_conditions = row_ops['filter']
                    for condition in filter_conditions:
                        if 'column' in condition and 'operator' in condition and 'value' in condition:
                            col = condition['column']
                            op = condition['operator']
                            val = condition['value']
                            
                            if op == '>':
                                transformed_df = transformed_df[transformed_df[col] > val]
                            elif op == '<':
                                transformed_df = transformed_df[transformed_df[col] < val]
                            elif op == '>=':
                                transformed_df = transformed_df[transformed_df[col] >= val]
                            elif op == '<=':
                                transformed_df = transformed_df[transformed_df[col] <= val]
                            elif op == '==':
                                transformed_df = transformed_df[transformed_df[col] == val]
                            elif op == '!=':
                                transformed_df = transformed_df[transformed_df[col] != val]
                            elif op == 'in':
                                transformed_df = transformed_df[transformed_df[col].isin(val)]
                            elif op == 'contains':
                                transformed_df = transformed_df[transformed_df[col].str.contains(val, na=False)]
                    
                    operations_applied.append(f"Applied {len(filter_conditions)} row filters")
                
                # Sort rows
                if 'sort' in row_ops:
                    sort_config = row_ops['sort']
                    columns = sort_config.get('columns', [])
                    ascending = sort_config.get('ascending', True)
                    transformed_df = transformed_df.sort_values(by=columns, ascending=ascending)
                    operations_applied.append(f"Sorted by {columns}")
            
            # Feature engineering
            if 'features' in operations:
                feature_ops = operations['features']
                
                # Create new columns
                if 'create' in feature_ops:
                    for new_col, expression in feature_ops['create'].items():
                        try:
                            # Simple arithmetic operations
                            if isinstance(expression, str):
                                if '+' in expression:
                                    parts = expression.split('+')
                                    transformed_df[new_col] = transformed_df[parts[0].strip()] + transformed_df[parts[1].strip()]
                                elif '-' in expression:
                                    parts = expression.split('-')
                                    transformed_df[new_col] = transformed_df[parts[0].strip()] - transformed_df[parts[1].strip()]
                                elif '*' in expression:
                                    parts = expression.split('*')
                                    transformed_df[new_col] = transformed_df[parts[0].strip()] * transformed_df[parts[1].strip()]
                                elif '/' in expression:
                                    parts = expression.split('/')
                                    transformed_df[new_col] = transformed_df[parts[0].strip()] / transformed_df[parts[1].strip()]
                            operations_applied.append(f"Created new column: {new_col}")
                        except Exception as e:
                            operations_applied.append(f"Failed to create column {new_col}: {str(e)}")
                
                # Aggregate operations
                if 'aggregate' in feature_ops:
                    agg_config = feature_ops['aggregate']
                    group_cols = agg_config.get('group_by', [])
                    agg_cols = agg_config.get('columns', {})
                    
                    if group_cols and agg_cols:
                        agg_df = transformed_df.groupby(group_cols).agg(agg_cols).reset_index()
                        operations_applied.append(f"Aggregated data by {group_cols}")
                        transformed_df = agg_df
            
            return PandasAnalysisResult(
                success=True,
                message=f"Data transformation completed. Applied {len(operations_applied)} operations",
                data={
                    'transformed_dataframe': transformed_df,
                    'operations_applied': operations_applied,
                    'original_shape': df.shape,
                    'transformed_shape': transformed_df.shape
                },
                operation="transform_data"
            )
            
        except Exception as e:
            return PandasAnalysisResult(
                success=False,
                message=f"Error transforming data: {str(e)}",
                error=str(e),
                operation="transform_data"
            )
    
    def create_visualization(self, df: pd.DataFrame, plot_config: Dict[str, Any]) -> PandasAnalysisResult:
        """Create data visualizations"""
        try:
            plot_type = plot_config.get('type', 'line')
            title = plot_config.get('title', 'Data Visualization')
            figsize = plot_config.get('figsize', (10, 6))
            
            # Create figure
            plt.figure(figsize=figsize)
            
            if plot_type == 'histogram':
                column = plot_config.get('column')
                bins = plot_config.get('bins', 30)
                plt.hist(df[column].dropna(), bins=bins, alpha=0.7, edgecolor='black')
                plt.xlabel(column)
                plt.ylabel('Frequency')
                plt.title(f'Histogram of {column}')
            
            elif plot_type == 'scatter':
                x_col = plot_config.get('x')
                y_col = plot_config.get('y')
                plt.scatter(df[x_col], df[y_col], alpha=0.6)
                plt.xlabel(x_col)
                plt.ylabel(y_col)
                plt.title(f'Scatter Plot: {x_col} vs {y_col}')
            
            elif plot_type == 'box':
                column = plot_config.get('column')
                plt.boxplot(df[column].dropna())
                plt.ylabel(column)
                plt.title(f'Box Plot of {column}')
            
            elif plot_type == 'bar':
                x_col = plot_config.get('x')
                y_col = plot_config.get('y')
                if y_col:
                    df.plot(kind='bar', x=x_col, y=y_col)
                else:
                    df[x_col].value_counts().plot(kind='bar')
                plt.title(f'Bar Chart: {x_col}')
                plt.xticks(rotation=45)
            
            elif plot_type == 'line':
                x_col = plot_config.get('x')
                y_col = plot_config.get('y')
                plt.plot(df[x_col], df[y_col])
                plt.xlabel(x_col)
                plt.ylabel(y_col)
                plt.title(f'Line Plot: {x_col} vs {y_col}')
            
            elif plot_type == 'correlation':
                numeric_df = df.select_dtypes(include=[np.number])
                if numeric_df.shape[1] > 1:
                    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', center=0)
                    plt.title('Correlation Matrix')
                else:
                    return PandasAnalysisResult(
                        success=False,
                        message="Not enough numeric columns for correlation plot",
                        error="InsufficientData",
                        operation="create_visualization"
                    )
            
            plt.tight_layout()
            
            # Save plot to bytes
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_data = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return PandasAnalysisResult(
                success=True,
                message=f"Visualization created: {plot_type} plot",
                data={
                    'plot_type': plot_type,
                    'title': title,
                    'image_data': img_data,
                    'image_format': 'png'
                },
                operation="create_visualization"
            )
            
        except Exception as e:
            return PandasAnalysisResult(
                success=False,
                message=f"Error creating visualization: {str(e)}",
                error=str(e),
                operation="create_visualization"
            )
    
    def merge_data(self, df1: pd.DataFrame, df2: pd.DataFrame, merge_config: Dict[str, Any]) -> PandasAnalysisResult:
        """Merge two DataFrames"""
        try:
            how = merge_config.get('how', 'inner')
            left_on = merge_config.get('left_on')
            right_on = merge_config.get('right_on')
            on = merge_config.get('on')
            
            if on:
                merged_df = pd.merge(df1, df2, on=on, how=how)
            elif left_on and right_on:
                merged_df = pd.merge(df1, df2, left_on=left_on, right_on=right_on, how=how)
            else:
                return PandasAnalysisResult(
                    success=False,
                    message="Merge configuration must specify 'on' or both 'left_on' and 'right_on'",
                    error="InvalidMergeConfig",
                    operation="merge_data"
                )
            
            return PandasAnalysisResult(
                success=True,
                message=f"Data merged successfully using {how} join",
                data={
                    'merged_dataframe': merged_df,
                    'original_shape_1': df1.shape,
                    'original_shape_2': df2.shape,
                    'merged_shape': merged_df.shape,
                    'merge_config': merge_config
                },
                operation="merge_data"
            )
            
        except Exception as e:
            return PandasAnalysisResult(
                success=False,
                message=f"Error merging data: {str(e)}",
                error=str(e),
                operation="merge_data"
            )


class PandasToolsManager:
    """Manager class for pandas operations with CLI integration"""
    
    def __init__(self, base_path: str = None):
        self.pandas_tools = PandasTools(base_path)
        self.console = Console()
        self.current_dataframe = None
        self.current_info = None
    
    def read_data(self, path: str, format: str = None, **kwargs) -> None:
        """Read data and store in current DataFrame"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Reading data...", total=None)
            result = self.pandas_tools.read_data(path, format, **kwargs)
        
        if result.success:
            self.current_dataframe = result.data['dataframe']
            self.current_info = result.data['info']
            self.console.print(f"[green]{result.message}[/green]")
            self._display_dataframe_info(result.data['info'])
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def _display_dataframe_info(self, info: Dict) -> None:
        """Display DataFrame information"""
        table = Table(show_header=True, header_style="bold magenta", title="DataFrame Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Shape", f"{info['shape'][0]} rows × {info['shape'][1]} columns")
        table.add_row("Memory Usage", f"{info['memory_usage'] / 1024 / 1024:.2f} MB")
        table.add_row("Missing Values", str(sum(info['missing_values'].values())))
        table.add_row("Duplicate Rows", str(info['duplicate_rows']))
        table.add_row("Numeric Columns", str(len(info['numeric_columns'])))
        table.add_row("Categorical Columns", str(len(info['categorical_columns'])))
        table.add_row("Object Columns", str(len(info['object_columns'])))
        
        self.console.print(table)
    
    def analyze_data(self, format: str = "table") -> None:
        """Analyze current DataFrame"""
        if self.current_dataframe is None:
            self.console.print("[red]No data loaded. Use --read to load data first.[/red]")
            return
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Analyzing data...", total=None)
            result = self.pandas_tools.analyze_data(self.current_dataframe)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            
            if format == "table":
                self._display_analysis_tables(result.data)
            elif format == "json":
                self.console.print(json.dumps(result.data, indent=2, default=str))
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def _display_analysis_tables(self, data: Dict) -> None:
        """Display analysis results in tables"""
        # Basic statistics
        basic_stats = data['basic_stats']
        stats_table = Table(show_header=True, header_style="bold magenta", title="Basic Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Shape", f"{basic_stats['shape'][0]} × {basic_stats['shape'][1]}")
        stats_table.add_row("Memory Usage (MB)", f"{basic_stats['memory_usage_mb']:.2f}")
        stats_table.add_row("Missing Values", f"{basic_stats['missing_values_total']:,}")
        stats_table.add_row("Missing Percentage", f"{basic_stats['missing_percentage']:.2f}%")
        stats_table.add_row("Duplicate Rows", f"{basic_stats['duplicate_rows']:,}")
        stats_table.add_row("Duplicate Percentage", f"{basic_stats['duplicate_percentage']:.2f}%")
        
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
            analysis_table.add_column("Std", style="green")
            
            for col, stats in col_analysis.items():
                mean_val = f"{stats.get('mean', 'N/A'):.2f}" if stats.get('mean') is not None else 'N/A'
                std_val = f"{stats.get('std', 'N/A'):.2f}" if stats.get('std') is not None else 'N/A'
                
                analysis_table.add_row(
                    col,
                    stats['data_type'],
                    f"{stats['missing_values']} ({stats['missing_percentage']:.1f}%)",
                    f"{stats['unique_values']} ({stats['unique_percentage']:.1f}%)",
                    mean_val,
                    std_val
                )
            
            self.console.print(analysis_table)
    
    def clean_data(self, operations: Dict[str, Any]) -> None:
        """Clean current DataFrame"""
        if self.current_dataframe is None:
            self.console.print("[red]No data loaded. Use --read to load data first.[/red]")
            return
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Cleaning data...", total=None)
            result = self.pandas_tools.clean_data(self.current_dataframe, operations)
        
        if result.success:
            self.current_dataframe = result.data['cleaned_dataframe']
            self.console.print(f"[green]{result.message}[/green]")
            
            # Display operations applied
            for op in result.data['operations_applied']:
                self.console.print(f"  • {op}")
            
            self.console.print(f"📊 Shape changed from {result.data['original_shape']} to {result.data['cleaned_shape']}")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def transform_data(self, operations: Dict[str, Any]) -> None:
        """Transform current DataFrame"""
        if self.current_dataframe is None:
            self.console.print("[red]No data loaded. Use --read to load data first.[/red]")
            return
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Transforming data...", total=None)
            result = self.pandas_tools.transform_data(self.current_dataframe, operations)
        
        if result.success:
            self.current_dataframe = result.data['transformed_dataframe']
            self.console.print(f"[green]{result.message}[/green]")
            
            # Display operations applied
            for op in result.data['operations_applied']:
                self.console.print(f"  • {op}")
            
            self.console.print(f"📊 Shape changed from {result.data['original_shape']} to {result.data['transformed_shape']}")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def create_visualization(self, plot_config: Dict[str, Any], output_path: str = None) -> None:
        """Create and display visualization"""
        if self.current_dataframe is None:
            self.console.print("[red]No data loaded. Use --read to load data first.[/red]")
            return
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Creating visualization...", total=None)
            result = self.pandas_tools.create_visualization(self.current_dataframe, plot_config)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            
            # Save to file if specified
            if output_path:
                try:
                    import base64
                    img_data = base64.b64decode(result.data['image_data'])
                    with open(output_path, 'wb') as f:
                        f.write(img_data)
                    self.console.print(f"💾 Visualization saved to: {output_path}")
                except Exception as e:
                    self.console.print(f"[red]Error saving visualization: {e}[/red]")
            
            # Display image data info
            self.console.print(f"📊 Plot type: {result.data['plot_type']}")
            self.console.print(f"📄 Image format: {result.data['image_format']}")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def write_data(self, path: str, format: str = 'csv', **kwargs) -> None:
        """Write current DataFrame to file"""
        if self.current_dataframe is None:
            self.console.print("[red]No data loaded. Use --read to load data first.[/red]")
            return
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Writing data...", total=None)
            result = self.pandas_tools.write_data(self.current_dataframe, path, format, **kwargs)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            data = result.data
            self.console.print(f"📄 File: {data['path']} ({data['rows_written']} rows, {data['columns_written']} columns)")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def show_data(self, rows: int = 10, format: str = "table") -> None:
        """Display current DataFrame"""
        if self.current_dataframe is None:
            self.console.print("[red]No data loaded. Use --read to load data first.[/red]")
            return
        
        df = self.current_dataframe.head(rows)
        
        if format == "table":
            self._display_dataframe_table(df)
        elif format == "json":
            self.console.print(json.dumps(df.to_dict('records'), indent=2, default=str))
    
    def _display_dataframe_table(self, df: pd.DataFrame) -> None:
        """Display DataFrame as a rich table"""
        if df.empty:
            self.console.print("[yellow]DataFrame is empty[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta", title=f"DataFrame Preview ({len(df)} rows)")
        
        # Add columns
        for col in df.columns:
            table.add_column(col, style="cyan", max_width=20)
        
        # Add rows
        for _, row in df.iterrows():
            row_data = []
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    value = 'NULL'
                elif isinstance(value, (int, float)):
                    value = f"{value:,}" if isinstance(value, int) else f"{value:.2f}"
                else:
                    value = str(value)[:20] + "..." if len(str(value)) > 20 else str(value)
                row_data.append(value)
            table.add_row(*row_data)
        
        self.console.print(table) 