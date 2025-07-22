"""
Visualization Tools - Data Visualization and Charting

This module provides comprehensive data visualization capabilities with:
- Chart generation and plotting
- Interactive visualizations
- Data presentation and analysis
- Rich output formatting
- Multiple chart types and styles
- Export and sharing capabilities
"""

import os
import sys
import json
import time
import base64
import io
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.syntax import Syntax
from rich.text import Text
from rich.markdown import Markdown
import warnings

# Suppress matplotlib warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
warnings.filterwarnings('ignore', category=FutureWarning, module='matplotlib')

# Set matplotlib style
plt.style.use('default')
sns.set_palette("husl")


@dataclass
class ChartConfig:
    """Chart configuration settings"""
    title: str
    x_label: str
    y_label: str
    width: int = 800
    height: int = 600
    theme: str = "plotly_white"
    show_legend: bool = True
    grid: bool = True
    font_size: int = 12


@dataclass
class DataSeries:
    """Data series for visualization"""
    name: str
    data: List[Union[int, float, str]]
    color: Optional[str] = None
    line_style: Optional[str] = None
    marker: Optional[str] = None


@dataclass
class VisualizationResult:
    """Result of a visualization operation"""
    chart_type: str
    data_points: int
    file_path: Optional[str]
    html_content: Optional[str]
    config: ChartConfig
    success: bool
    error_message: Optional[str] = None


class VisualizationTools:
    """Core data visualization tools"""
    
    def __init__(self):
        self.console = Console()
        self.output_dir = Path("visualizations")
        self.output_dir.mkdir(exist_ok=True)
        
        # Default color palettes
        self.color_palettes = {
            'default': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            'pastel': ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc'],
            'dark': ['#2ecc71', '#3498db', '#e74c3c', '#f39c12', '#9b59b6'],
            'monochrome': ['#000000', '#333333', '#666666', '#999999', '#cccccc']
        }
        
        # Chart type configurations
        self.chart_configs = {
            'line': {'markers': True, 'grid': True},
            'bar': {'grid': True, 'orientation': 'v'},
            'scatter': {'markers': True, 'grid': True},
            'pie': {'grid': False, 'legend': True},
            'histogram': {'grid': True, 'bins': 20},
            'box': {'grid': True, 'points': 'outliers'},
            'heatmap': {'grid': False, 'annotations': True}
        }
    
    def _create_output_path(self, chart_type: str, filename: Optional[str] = None) -> Path:
        """Create output file path"""
        if filename:
            return self.output_dir / f"{filename}.html"
        else:
            timestamp = int(time.time())
            return self.output_dir / f"{chart_type}_{timestamp}.html"
    
    def _validate_data(self, data: Union[pd.DataFrame, List, Dict]) -> pd.DataFrame:
        """Validate and convert data to DataFrame"""
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, list):
            if all(isinstance(item, dict) for item in data):
                return pd.DataFrame(data)
            else:
                return pd.DataFrame({'value': data})
        elif isinstance(data, dict):
            return pd.DataFrame([data])
        else:
            raise ValueError("Data must be DataFrame, list, or dict")
    
    def line_chart(self, data: Union[pd.DataFrame, List, Dict], 
                   x_column: str = None, y_column: str = None,
                   config: Optional[ChartConfig] = None) -> VisualizationResult:
        """Create a line chart"""
        try:
            df = self._validate_data(data)
            
            if config is None:
                config = ChartConfig(
                    title="Line Chart",
                    x_label=x_column or "X",
                    y_label=y_column or "Y"
                )
            
            if x_column and y_column and x_column in df.columns and y_column in df.columns:
                fig = px.line(df, x=x_column, y=y_column, title=config.title)
            else:
                # Use first two numeric columns or create simple line chart
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    fig = px.line(df, x=numeric_cols[0], y=numeric_cols[1], title=config.title)
                else:
                    # Create simple line chart with index
                    fig = px.line(y=df.iloc[:, 0] if len(df.columns) > 0 else [1, 2, 3], title=config.title)
            
            fig.update_layout(
                width=config.width,
                height=config.height,
                template=config.theme,
                showlegend=config.show_legend,
                xaxis_title=config.x_label,
                yaxis_title=config.y_label,
                font=dict(size=config.font_size)
            )
            
            if config.grid:
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            
            # Save to file
            output_path = self._create_output_path("line_chart")
            fig.write_html(str(output_path))
            
            return VisualizationResult(
                chart_type="line",
                data_points=len(df),
                file_path=str(output_path),
                html_content=fig.to_html(),
                config=config,
                success=True
            )
            
        except Exception as e:
            return VisualizationResult(
                chart_type="line",
                data_points=0,
                file_path=None,
                html_content=None,
                config=config or ChartConfig("", "", ""),
                success=False,
                error_message=str(e)
            )
    
    def bar_chart(self, data: Union[pd.DataFrame, List, Dict],
                  x_column: str = None, y_column: str = None,
                  config: Optional[ChartConfig] = None) -> VisualizationResult:
        """Create a bar chart"""
        try:
            df = self._validate_data(data)
            
            if config is None:
                config = ChartConfig(
                    title="Bar Chart",
                    x_label=x_column or "Categories",
                    y_label=y_column or "Values"
                )
            
            if x_column and y_column and x_column in df.columns and y_column in df.columns:
                fig = px.bar(df, x=x_column, y=y_column, title=config.title)
            else:
                # Use first two columns or create simple bar chart
                if len(df.columns) >= 2:
                    fig = px.bar(df, x=df.columns[0], y=df.columns[1], title=config.title)
                else:
                    fig = px.bar(df, title=config.title)
            
            fig.update_layout(
                width=config.width,
                height=config.height,
                template=config.theme,
                showlegend=config.show_legend,
                xaxis_title=config.x_label,
                yaxis_title=config.y_label,
                font=dict(size=config.font_size)
            )
            
            if config.grid:
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            
            # Save to file
            output_path = self._create_output_path("bar_chart")
            fig.write_html(str(output_path))
            
            return VisualizationResult(
                chart_type="bar",
                data_points=len(df),
                file_path=str(output_path),
                html_content=fig.to_html(),
                config=config,
                success=True
            )
            
        except Exception as e:
            return VisualizationResult(
                chart_type="bar",
                data_points=0,
                file_path=None,
                html_content=None,
                config=config or ChartConfig("", "", ""),
                success=False,
                error_message=str(e)
            )
    
    def scatter_plot(self, data: Union[pd.DataFrame, List, Dict],
                     x_column: str = None, y_column: str = None,
                     color_column: str = None, size_column: str = None,
                     config: Optional[ChartConfig] = None) -> VisualizationResult:
        """Create a scatter plot"""
        try:
            df = self._validate_data(data)
            
            if config is None:
                config = ChartConfig(
                    title="Scatter Plot",
                    x_label=x_column or "X",
                    y_label=y_column or "Y"
                )
            
            # Build scatter plot with optional parameters
            scatter_kwargs = {'title': config.title}
            
            if x_column and y_column and x_column in df.columns and y_column in df.columns:
                scatter_kwargs.update({'x': x_column, 'y': y_column})
            else:
                if len(df.columns) >= 2:
                    scatter_kwargs.update({'x': df.columns[0], 'y': df.columns[1]})
            
            if color_column and color_column in df.columns:
                scatter_kwargs['color'] = color_column
            
            if size_column and size_column in df.columns:
                scatter_kwargs['size'] = size_column
            
            fig = px.scatter(df, **scatter_kwargs)
            
            fig.update_layout(
                width=config.width,
                height=config.height,
                template=config.theme,
                showlegend=config.show_legend,
                xaxis_title=config.x_label,
                yaxis_title=config.y_label,
                font=dict(size=config.font_size)
            )
            
            if config.grid:
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            
            # Save to file
            output_path = self._create_output_path("scatter_plot")
            fig.write_html(str(output_path))
            
            return VisualizationResult(
                chart_type="scatter",
                data_points=len(df),
                file_path=str(output_path),
                html_content=fig.to_html(),
                config=config,
                success=True
            )
            
        except Exception as e:
            return VisualizationResult(
                chart_type="scatter",
                data_points=0,
                file_path=None,
                html_content=None,
                config=config or ChartConfig("", "", ""),
                success=False,
                error_message=str(e)
            )
    
    def pie_chart(self, data: Union[pd.DataFrame, List, Dict],
                  values_column: str = None, names_column: str = None,
                  config: Optional[ChartConfig] = None) -> VisualizationResult:
        """Create a pie chart"""
        try:
            df = self._validate_data(data)
            
            if config is None:
                config = ChartConfig(
                    title="Pie Chart",
                    x_label="",
                    y_label=""
                )
            
            if values_column and names_column and values_column in df.columns and names_column in df.columns:
                fig = px.pie(df, values=values_column, names=names_column, title=config.title)
            else:
                # Use first two columns or create simple pie chart
                if len(df.columns) >= 2:
                    fig = px.pie(df, values=df.columns[0], names=df.columns[1], title=config.title)
                else:
                    # Create pie chart from single column
                    fig = px.pie(df, values=df.iloc[:, 0], title=config.title)
            
            fig.update_layout(
                width=config.width,
                height=config.height,
                template=config.theme,
                showlegend=config.show_legend,
                font=dict(size=config.font_size)
            )
            
            # Save to file
            output_path = self._create_output_path("pie_chart")
            fig.write_html(str(output_path))
            
            return VisualizationResult(
                chart_type="pie",
                data_points=len(df),
                file_path=str(output_path),
                html_content=fig.to_html(),
                config=config,
                success=True
            )
            
        except Exception as e:
            return VisualizationResult(
                chart_type="pie",
                data_points=0,
                file_path=None,
                html_content=None,
                config=config or ChartConfig("", "", ""),
                success=False,
                error_message=str(e)
            )
    
    def histogram(self, data: Union[pd.DataFrame, List, Dict],
                  column: str = None, bins: int = 20,
                  config: Optional[ChartConfig] = None) -> VisualizationResult:
        """Create a histogram"""
        try:
            df = self._validate_data(data)
            
            if config is None:
                config = ChartConfig(
                    title="Histogram",
                    x_label=column or "Values",
                    y_label="Frequency"
                )
            
            if column and column in df.columns:
                fig = px.histogram(df, x=column, nbins=bins, title=config.title)
            else:
                # Use first numeric column
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    fig = px.histogram(df, x=numeric_cols[0], nbins=bins, title=config.title)
                else:
                    fig = px.histogram(df, nbins=bins, title=config.title)
            
            fig.update_layout(
                width=config.width,
                height=config.height,
                template=config.theme,
                showlegend=config.show_legend,
                xaxis_title=config.x_label,
                yaxis_title=config.y_label,
                font=dict(size=config.font_size)
            )
            
            if config.grid:
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            
            # Save to file
            output_path = self._create_output_path("histogram")
            fig.write_html(str(output_path))
            
            return VisualizationResult(
                chart_type="histogram",
                data_points=len(df),
                file_path=str(output_path),
                html_content=fig.to_html(),
                config=config,
                success=True
            )
            
        except Exception as e:
            return VisualizationResult(
                chart_type="histogram",
                data_points=0,
                file_path=None,
                html_content=None,
                config=config or ChartConfig("", "", ""),
                success=False,
                error_message=str(e)
            )
    
    def box_plot(self, data: Union[pd.DataFrame, List, Dict],
                 x_column: str = None, y_column: str = None,
                 config: Optional[ChartConfig] = None) -> VisualizationResult:
        """Create a box plot"""
        try:
            df = self._validate_data(data)
            
            if config is None:
                config = ChartConfig(
                    title="Box Plot",
                    x_label=x_column or "Categories",
                    y_label=y_column or "Values"
                )
            
            if x_column and y_column and x_column in df.columns and y_column in df.columns:
                fig = px.box(df, x=x_column, y=y_column, title=config.title)
            else:
                # Use first two columns or create simple box plot
                if len(df.columns) >= 2:
                    fig = px.box(df, x=df.columns[0], y=df.columns[1], title=config.title)
                else:
                    fig = px.box(df, title=config.title)
            
            fig.update_layout(
                width=config.width,
                height=config.height,
                template=config.theme,
                showlegend=config.show_legend,
                xaxis_title=config.x_label,
                yaxis_title=config.y_label,
                font=dict(size=config.font_size)
            )
            
            if config.grid:
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            
            # Save to file
            output_path = self._create_output_path("box_plot")
            fig.write_html(str(output_path))
            
            return VisualizationResult(
                chart_type="box",
                data_points=len(df),
                file_path=str(output_path),
                html_content=fig.to_html(),
                config=config,
                success=True
            )
            
        except Exception as e:
            return VisualizationResult(
                chart_type="box",
                data_points=0,
                file_path=None,
                html_content=None,
                config=config or ChartConfig("", "", ""),
                success=False,
                error_message=str(e)
            )
    
    def heatmap(self, data: Union[pd.DataFrame, List, Dict],
                config: Optional[ChartConfig] = None) -> VisualizationResult:
        """Create a heatmap"""
        try:
            df = self._validate_data(data)
            
            if config is None:
                config = ChartConfig(
                    title="Heatmap",
                    x_label="",
                    y_label=""
                )
            
            # Convert to correlation matrix if not already
            if len(df.columns) > 1:
                # Try to create correlation matrix
                try:
                    numeric_df = df.select_dtypes(include=[np.number])
                    if len(numeric_df.columns) > 1:
                        corr_matrix = numeric_df.corr()
                        fig = px.imshow(corr_matrix, title=config.title, aspect="auto")
                    else:
                        fig = px.imshow(df, title=config.title, aspect="auto")
                except:
                    fig = px.imshow(df, title=config.title, aspect="auto")
            else:
                fig = px.imshow(df, title=config.title, aspect="auto")
            
            fig.update_layout(
                width=config.width,
                height=config.height,
                template=config.theme,
                showlegend=config.show_legend,
                font=dict(size=config.font_size)
            )
            
            # Save to file
            output_path = self._create_output_path("heatmap")
            fig.write_html(str(output_path))
            
            return VisualizationResult(
                chart_type="heatmap",
                data_points=len(df),
                file_path=str(output_path),
                html_content=fig.to_html(),
                config=config,
                success=True
            )
            
        except Exception as e:
            return VisualizationResult(
                chart_type="heatmap",
                data_points=0,
                file_path=None,
                html_content=None,
                config=config or ChartConfig("", "", ""),
                success=False,
                error_message=str(e)
            )
    
    def multi_chart(self, data: Union[pd.DataFrame, List, Dict],
                    chart_types: List[str], columns: List[str] = None,
                    config: Optional[ChartConfig] = None) -> VisualizationResult:
        """Create multiple charts in a subplot layout"""
        try:
            df = self._validate_data(data)
            
            if config is None:
                config = ChartConfig(
                    title="Multi-Chart Dashboard",
                    x_label="",
                    y_label=""
                )
            
            # Create subplots
            n_charts = len(chart_types)
            fig = make_subplots(
                rows=1, cols=n_charts,
                subplot_titles=[f"{chart_type.title()} Chart" for chart_type in chart_types]
            )
            
            for i, chart_type in enumerate(chart_types):
                col = i + 1
                
                if chart_type == "line":
                    if columns and len(columns) >= 2:
                        fig.add_trace(
                            go.Scatter(x=df[columns[0]], y=df[columns[1]], mode='lines+markers'),
                            row=1, col=col
                        )
                elif chart_type == "bar":
                    if columns and len(columns) >= 2:
                        fig.add_trace(
                            go.Bar(x=df[columns[0]], y=df[columns[1]]),
                            row=1, col=col
                        )
                elif chart_type == "scatter":
                    if columns and len(columns) >= 2:
                        fig.add_trace(
                            go.Scatter(x=df[columns[0]], y=df[columns[1]], mode='markers'),
                            row=1, col=col
                        )
                elif chart_type == "histogram":
                    if columns and len(columns) >= 1:
                        fig.add_trace(
                            go.Histogram(x=df[columns[0]]),
                            row=1, col=col
                        )
            
            fig.update_layout(
                width=config.width * n_charts,
                height=config.height,
                template=config.theme,
                showlegend=config.show_legend,
                title=config.title,
                font=dict(size=config.font_size)
            )
            
            # Save to file
            output_path = self._create_output_path("multi_chart")
            fig.write_html(str(output_path))
            
            return VisualizationResult(
                chart_type="multi",
                data_points=len(df),
                file_path=str(output_path),
                html_content=fig.to_html(),
                config=config,
                success=True
            )
            
        except Exception as e:
            return VisualizationResult(
                chart_type="multi",
                data_points=0,
                file_path=None,
                html_content=None,
                config=config or ChartConfig("", "", ""),
                success=False,
                error_message=str(e)
            )
    
    def create_sample_data(self, data_type: str = "random", size: int = 100) -> pd.DataFrame:
        """Create sample data for testing visualizations"""
        np.random.seed(42)
        
        if data_type == "random":
            return pd.DataFrame({
                'x': np.random.randn(size),
                'y': np.random.randn(size),
                'category': np.random.choice(['A', 'B', 'C'], size),
                'value': np.random.randint(1, 100, size)
            })
        elif data_type == "trend":
            x = np.linspace(0, 10, size)
            return pd.DataFrame({
                'x': x,
                'y': 2 * x + np.random.normal(0, 1, size),
                'category': np.random.choice(['Group1', 'Group2'], size),
                'value': np.random.randint(1, 100, size)
            })
        elif data_type == "categorical":
            categories = ['A', 'B', 'C', 'D', 'E']
            return pd.DataFrame({
                'category': np.random.choice(categories, size),
                'value': np.random.randint(10, 100, size),
                'group': np.random.choice(['Group1', 'Group2', 'Group3'], size)
            })
        else:
            return pd.DataFrame({
                'x': np.random.randn(size),
                'y': np.random.randn(size),
                'category': np.random.choice(['A', 'B', 'C'], size),
                'value': np.random.randint(1, 100, size)
            })
    
    def list_chart_types(self) -> List[str]:
        """List available chart types"""
        return ['line', 'bar', 'scatter', 'pie', 'histogram', 'box', 'heatmap', 'multi']
    
    def get_chart_info(self, chart_type: str) -> Dict[str, Any]:
        """Get information about a chart type"""
        info = {
            'line': {
                'description': 'Line chart for showing trends over time or continuous data',
                'best_for': ['Time series', 'Trends', 'Continuous data'],
                'required_columns': 2,
                'optional_features': ['markers', 'grid', 'multiple_lines']
            },
            'bar': {
                'description': 'Bar chart for comparing categories or discrete data',
                'best_for': ['Categories', 'Comparisons', 'Discrete data'],
                'required_columns': 2,
                'optional_features': ['horizontal', 'stacked', 'grouped']
            },
            'scatter': {
                'description': 'Scatter plot for showing relationships between variables',
                'best_for': ['Correlations', 'Relationships', 'Outliers'],
                'required_columns': 2,
                'optional_features': ['color', 'size', 'trend_line']
            },
            'pie': {
                'description': 'Pie chart for showing proportions of a whole',
                'best_for': ['Proportions', 'Percentages', 'Composition'],
                'required_columns': 2,
                'optional_features': ['explode', 'colors', 'legend']
            },
            'histogram': {
                'description': 'Histogram for showing distribution of data',
                'best_for': ['Distributions', 'Frequency', 'Data shape'],
                'required_columns': 1,
                'optional_features': ['bins', 'density', 'cumulative']
            },
            'box': {
                'description': 'Box plot for showing data distribution and outliers',
                'best_for': ['Distributions', 'Outliers', 'Comparisons'],
                'required_columns': 2,
                'optional_features': ['notches', 'points', 'violin']
            },
            'heatmap': {
                'description': 'Heatmap for showing correlation or intensity matrices',
                'best_for': ['Correlations', 'Intensity', 'Matrices'],
                'required_columns': 2,
                'optional_features': ['annotations', 'colorbar', 'clustering']
            }
        }
        
        return info.get(chart_type, {'description': 'Unknown chart type'})


class VisualizationToolsManager:
    """CLI integration for visualization tools"""
    
    def __init__(self):
        self.viz_tools = VisualizationTools()
        self.console = Console()
    
    def create_chart(self, chart_type: str, data: Union[pd.DataFrame, List, Dict],
                     x_column: str = None, y_column: str = None,
                     title: str = None, width: int = 800, height: int = 600,
                     format: str = "html") -> None:
        """Create a chart of specified type"""
        try:
            config = ChartConfig(
                title=title or f"{chart_type.title()} Chart",
                x_label=x_column or "X",
                y_label=y_column or "Y",
                width=width,
                height=height
            )
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Creating {chart_type} chart...", total=None)
                
                if chart_type == "line":
                    result = self.viz_tools.line_chart(data, x_column, y_column, config)
                elif chart_type == "bar":
                    result = self.viz_tools.bar_chart(data, x_column, y_column, config)
                elif chart_type == "scatter":
                    result = self.viz_tools.scatter_plot(data, x_column, y_column, config=config)
                elif chart_type == "pie":
                    result = self.viz_tools.pie_chart(data, y_column, x_column, config)
                elif chart_type == "histogram":
                    result = self.viz_tools.histogram(data, x_column, config=config)
                elif chart_type == "box":
                    result = self.viz_tools.box_plot(data, x_column, y_column, config)
                elif chart_type == "heatmap":
                    result = self.viz_tools.heatmap(data, config)
                else:
                    self.console.print(f"[red]Unknown chart type: {chart_type}[/red]")
                    return
            
            if result.success:
                self.console.print(f"[green]Chart created successfully![/green]")
                self.console.print(f"[blue]File saved to: {result.file_path}[/blue]")
                
                if format == "json":
                    import json
                    self.console.print(json.dumps({
                        'chart_type': result.chart_type,
                        'data_points': result.data_points,
                        'file_path': result.file_path,
                        'config': {
                            'title': result.config.title,
                            'width': result.config.width,
                            'height': result.config.height
                        }
                    }, indent=2))
                else:
                    # Show chart info
                    info_table = Table(title="Chart Information")
                    info_table.add_column("Property", style="cyan")
                    info_table.add_column("Value", style="white")
                    
                    info_table.add_row("Chart Type", result.chart_type.title())
                    info_table.add_row("Data Points", str(result.data_points))
                    info_table.add_row("File Path", result.file_path)
                    info_table.add_row("Title", result.config.title)
                    info_table.add_row("Dimensions", f"{result.config.width}x{result.config.height}")
                    
                    self.console.print(info_table)
            else:
                self.console.print(f"[red]Error creating chart: {result.error_message}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Chart creation error: {e}[/red]")
    
    def create_sample_chart(self, chart_type: str, data_type: str = "random", 
                           size: int = 100, format: str = "html") -> None:
        """Create a sample chart with generated data"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Generating sample data...", total=None)
                data = self.viz_tools.create_sample_data(data_type, size)
            
            self.create_chart(chart_type, data, format=format)
            
        except Exception as e:
            self.console.print(f"[red]Sample chart creation error: {e}[/red]")
    
    def list_chart_types(self, format: str = "table") -> None:
        """List available chart types"""
        try:
            chart_types = self.viz_tools.list_chart_types()
            
            if format == "json":
                import json
                chart_info = {}
                for chart_type in chart_types:
                    chart_info[chart_type] = self.viz_tools.get_chart_info(chart_type)
                self.console.print(json.dumps(chart_info, indent=2))
                return
            
            # Create chart types table
            table = Table(title="Available Chart Types")
            table.add_column("Chart Type", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Best For", style="yellow")
            
            for chart_type in chart_types:
                info = self.viz_tools.get_chart_info(chart_type)
                description = info.get('description', 'No description available')
                best_for = ', '.join(info.get('best_for', ['General use']))
                
                table.add_row(chart_type.title(), description, best_for)
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Error listing chart types: {e}[/red]")
    
    def get_chart_info(self, chart_type: str, format: str = "table") -> None:
        """Get detailed information about a chart type"""
        try:
            info = self.viz_tools.get_chart_info(chart_type)
            
            if format == "json":
                import json
                self.console.print(json.dumps(info, indent=2))
                return
            
            # Create detailed info table
            table = Table(title=f"Chart Type: {chart_type.title()}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")
            
            for key, value in info.items():
                if isinstance(value, list):
                    table.add_row(key.title(), ', '.join(value))
                else:
                    table.add_row(key.title(), str(value))
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Error getting chart info: {e}[/red]")
    
    def create_dashboard(self, data: Union[pd.DataFrame, List, Dict],
                        chart_types: List[str], columns: List[str] = None,
                        title: str = "Dashboard", format: str = "html") -> None:
        """Create a multi-chart dashboard"""
        try:
            config = ChartConfig(
                title=title,
                x_label="",
                y_label="",
                width=1200,
                height=600
            )
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Creating dashboard...", total=None)
                result = self.viz_tools.multi_chart(data, chart_types, columns, config)
            
            if result.success:
                self.console.print(f"[green]Dashboard created successfully![/green]")
                self.console.print(f"[blue]File saved to: {result.file_path}[/blue]")
                
                if format == "json":
                    import json
                    self.console.print(json.dumps({
                        'chart_type': 'dashboard',
                        'data_points': result.data_points,
                        'file_path': result.file_path,
                        'charts': chart_types,
                        'config': {
                            'title': result.config.title,
                            'width': result.config.width,
                            'height': result.config.height
                        }
                    }, indent=2))
                else:
                    # Show dashboard info
                    info_table = Table(title="Dashboard Information")
                    info_table.add_column("Property", style="cyan")
                    info_table.add_column("Value", style="white")
                    
                    info_table.add_row("Type", "Multi-Chart Dashboard")
                    info_table.add_row("Data Points", str(result.data_points))
                    info_table.add_row("File Path", result.file_path)
                    info_table.add_row("Title", result.config.title)
                    info_table.add_row("Charts", ', '.join(chart_types))
                    info_table.add_row("Dimensions", f"{result.config.width}x{result.config.height}")
                    
                    self.console.print(info_table)
            else:
                self.console.print(f"[red]Error creating dashboard: {result.error_message}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Dashboard creation error: {e}[/red]") 