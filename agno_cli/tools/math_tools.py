"""
Math and data analysis tools manager
"""

import json
import math
import statistics
import sqlite3
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CalculationResult:
    """Result of a mathematical calculation"""
    expression: str
    result: Union[float, int, str]
    steps: List[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'expression': self.expression,
            'result': self.result,
            'steps': self.steps or [],
            'error': self.error
        }


class Calculator:
    """Advanced calculator with step-by-step solutions"""
    
    def __init__(self):
        self.variables = {}
        self.functions = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'sqrt': math.sqrt,
            'abs': abs,
            'ceil': math.ceil,
            'floor': math.floor,
            'round': round,
            'pi': math.pi,
            'e': math.e
        }
    
    def evaluate(self, expression: str, show_steps: bool = False) -> CalculationResult:
        """Evaluate a mathematical expression"""
        try:
            # Clean the expression
            cleaned_expr = self._clean_expression(expression)
            
            # Track steps if requested
            steps = []
            if show_steps:
                steps = self._generate_steps(cleaned_expr)
            
            # Create safe namespace
            namespace = {
                '__builtins__': {},
                **self.functions,
                **self.variables
            }
            
            # Evaluate the expression
            result = eval(cleaned_expr, namespace)
            
            return CalculationResult(
                expression=expression,
                result=result,
                steps=steps
            )
            
        except Exception as e:
            return CalculationResult(
                expression=expression,
                result=None,
                error=str(e)
            )
    
    def _clean_expression(self, expr: str) -> str:
        """Clean and prepare expression for evaluation"""
        # Replace common mathematical notation
        expr = expr.replace('^', '**')  # Power operator
        expr = expr.replace('×', '*')   # Multiplication
        expr = expr.replace('÷', '/')   # Division
        
        # Handle implicit multiplication (e.g., 2x -> 2*x)
        import re
        expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
        expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)
        
        return expr
    
    def _generate_steps(self, expression: str) -> List[str]:
        """Generate step-by-step solution (simplified)"""
        steps = []
        steps.append(f"Original expression: {expression}")
        
        # This is a simplified step generator
        # In a full implementation, you'd parse the expression tree
        # and show each operation step by step
        
        try:
            # Show substitutions if variables are used
            for var, value in self.variables.items():
                if var in expression:
                    steps.append(f"Substitute {var} = {value}")
            
            steps.append("Evaluate the expression")
            
        except:
            pass
        
        return steps
    
    def set_variable(self, name: str, value: Union[float, int]) -> None:
        """Set a variable value"""
        self.variables[name] = value
    
    def get_variable(self, name: str) -> Optional[Union[float, int]]:
        """Get a variable value"""
        return self.variables.get(name)
    
    def list_variables(self) -> Dict[str, Union[float, int]]:
        """List all variables"""
        return self.variables.copy()
    
    def clear_variables(self) -> None:
        """Clear all variables"""
        self.variables.clear()


class StatisticsCalculator:
    """Statistical analysis calculator"""
    
    @staticmethod
    def descriptive_stats(data: List[Union[float, int]]) -> Dict[str, float]:
        """Calculate descriptive statistics"""
        if not data:
            return {}
        
        try:
            return {
                'count': len(data),
                'mean': statistics.mean(data),
                'median': statistics.median(data),
                'mode': statistics.mode(data) if len(set(data)) < len(data) else None,
                'std_dev': statistics.stdev(data) if len(data) > 1 else 0,
                'variance': statistics.variance(data) if len(data) > 1 else 0,
                'min': min(data),
                'max': max(data),
                'range': max(data) - min(data),
                'sum': sum(data)
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def correlation(x: List[float], y: List[float]) -> Optional[float]:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return None
        
        try:
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_x2 = sum(xi * xi for xi in x)
            sum_y2 = sum(yi * yi for yi in y)
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
            
            if denominator == 0:
                return None
            
            return numerator / denominator
            
        except Exception:
            return None
    
    @staticmethod
    def linear_regression(x: List[float], y: List[float]) -> Optional[Dict[str, float]]:
        """Calculate linear regression"""
        if len(x) != len(y) or len(x) < 2:
            return None
        
        try:
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_x2 = sum(xi * xi for xi in x)
            
            # Calculate slope and intercept
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Calculate R-squared
            y_mean = sum_y / n
            ss_tot = sum((yi - y_mean) ** 2 for yi in y)
            ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            return {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_squared,
                'equation': f'y = {slope:.4f}x + {intercept:.4f}'
            }
            
        except Exception:
            return None


class CSVAnalyzer:
    """CSV file analysis tool"""
    
    def __init__(self):
        try:
            import pandas as pd
            self.pd = pd
        except ImportError:
            raise ImportError("pandas package not installed. Install with: pip install pandas")
    
    def load_csv(self, file_path: str, **kwargs) -> Optional[object]:
        """Load CSV file"""
        try:
            return self.pd.read_csv(file_path, **kwargs)
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return None
    
    def analyze_dataframe(self, df: object) -> Dict[str, Any]:
        """Analyze a pandas DataFrame"""
        try:
            analysis = {
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict(),
                'missing_values': df.isnull().sum().to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'numeric_columns': list(df.select_dtypes(include=['number']).columns),
                'categorical_columns': list(df.select_dtypes(include=['object']).columns)
            }
            
            # Add descriptive statistics for numeric columns
            numeric_df = df.select_dtypes(include=['number'])
            if not numeric_df.empty:
                analysis['descriptive_stats'] = numeric_df.describe().to_dict()
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def query_dataframe(self, df: object, query: str) -> Optional[object]:
        """Query DataFrame using pandas query syntax"""
        try:
            return df.query(query)
        except Exception as e:
            print(f"Query error: {e}")
            return None
    
    def group_analysis(self, df: object, group_by: str, agg_column: str, 
                      agg_func: str = 'mean') -> Optional[Dict[str, Any]]:
        """Perform group analysis"""
        try:
            if group_by not in df.columns or agg_column not in df.columns:
                return None
            
            grouped = df.groupby(group_by)[agg_column].agg(agg_func)
            
            return {
                'group_by': group_by,
                'agg_column': agg_column,
                'agg_function': agg_func,
                'results': grouped.to_dict()
            }
            
        except Exception as e:
            print(f"Group analysis error: {e}")
            return None


class SQLQueryTool:
    """SQL query tool for data analysis"""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from database"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str, params: Tuple = None) -> Optional[List[Dict[str, Any]]]:
        """Execute SQL query and return results"""
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # For SELECT queries, return results
            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                # For other queries, commit and return affected rows
                self.connection.commit()
                return [{'affected_rows': cursor.rowcount}]
                
        except Exception as e:
            print(f"Query execution error: {e}")
            return None
    
    def create_table_from_csv(self, csv_path: str, table_name: str) -> bool:
        """Create table from CSV file"""
        try:
            import pandas as pd
            
            df = pd.read_csv(csv_path)
            
            if not self.connection:
                if not self.connect():
                    return False
            
            df.to_sql(table_name, self.connection, if_exists='replace', index=False)
            return True
            
        except Exception as e:
            print(f"Error creating table from CSV: {e}")
            return False
    
    def list_tables(self) -> List[str]:
        """List all tables in the database"""
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        results = self.execute_query(query)
        
        if results:
            return [row['name'] for row in results]
        return []
    
    def describe_table(self, table_name: str) -> Optional[List[Dict[str, Any]]]:
        """Describe table structure"""
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)


class MathToolsManager:
    """Manager for all math and data analysis tools"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.calculator = Calculator()
        self.stats_calculator = StatisticsCalculator()
        self.csv_analyzer = CSVAnalyzer()
        self.sql_tools = {}  # Dictionary of SQL connections
    
    def calculate(self, expression: str, show_steps: bool = False) -> CalculationResult:
        """Perform mathematical calculation"""
        return self.calculator.evaluate(expression, show_steps)
    
    def set_variable(self, name: str, value: Union[float, int]) -> None:
        """Set calculator variable"""
        self.calculator.set_variable(name, value)
    
    def get_variable(self, name: str) -> Optional[Union[float, int]]:
        """Get calculator variable"""
        return self.calculator.get_variable(name)
    
    def list_variables(self) -> Dict[str, Union[float, int]]:
        """List all calculator variables"""
        return self.calculator.list_variables()
    
    def clear_variables(self) -> None:
        """Clear all calculator variables"""
        self.calculator.clear_variables()
    
    def analyze_data(self, data: List[Union[float, int]]) -> Dict[str, float]:
        """Perform statistical analysis on data"""
        return self.stats_calculator.descriptive_stats(data)
    
    def correlation(self, x: List[float], y: List[float]) -> Optional[float]:
        """Calculate correlation between two datasets"""
        return self.stats_calculator.correlation(x, y)
    
    def linear_regression(self, x: List[float], y: List[float]) -> Optional[Dict[str, float]]:
        """Perform linear regression analysis"""
        return self.stats_calculator.linear_regression(x, y)
    
    def load_csv(self, file_path: str, **kwargs) -> Optional[object]:
        """Load and return CSV data"""
        return self.csv_analyzer.load_csv(file_path, **kwargs)
    
    def analyze_csv(self, file_path: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Analyze CSV file"""
        df = self.csv_analyzer.load_csv(file_path, **kwargs)
        if df is not None:
            return self.csv_analyzer.analyze_dataframe(df)
        return None
    
    def query_csv(self, file_path: str, query: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Query CSV file using pandas query syntax"""
        df = self.csv_analyzer.load_csv(file_path, **kwargs)
        if df is not None:
            result_df = self.csv_analyzer.query_dataframe(df, query)
            if result_df is not None:
                return {
                    'query': query,
                    'result_count': len(result_df),
                    'results': result_df.to_dict('records')
                }
        return None
    
    def create_sql_connection(self, connection_name: str, db_path: str = ":memory:") -> bool:
        """Create a new SQL connection"""
        sql_tool = SQLQueryTool(db_path)
        if sql_tool.connect():
            self.sql_tools[connection_name] = sql_tool
            return True
        return False
    
    def execute_sql(self, connection_name: str, query: str, params: Tuple = None) -> Optional[List[Dict[str, Any]]]:
        """Execute SQL query on a connection"""
        if connection_name not in self.sql_tools:
            return None
        
        return self.sql_tools[connection_name].execute_query(query, params)
    
    def import_csv_to_sql(self, connection_name: str, csv_path: str, table_name: str) -> bool:
        """Import CSV file to SQL table"""
        if connection_name not in self.sql_tools:
            return False
        
        return self.sql_tools[connection_name].create_table_from_csv(csv_path, table_name)
    
    def list_sql_tables(self, connection_name: str) -> List[str]:
        """List tables in SQL connection"""
        if connection_name not in self.sql_tools:
            return []
        
        return self.sql_tools[connection_name].list_tables()
    
    def solve_equation(self, equation: str, variable: str = 'x') -> Optional[List[float]]:
        """Solve algebraic equation (simplified implementation)"""
        try:
            # Clean the equation
            equation = equation.lower().replace('solve:', '').replace('solve', '').strip()
            
            # Handle simple linear equations like "2x + 3 = 7"
            if '=' in equation:
                left, right = equation.split('=')
                left = left.strip()
                right = right.strip()
                
                # Try to solve simple linear equation
                if variable in left and variable not in right:
                    import re
                    
                    # Handle various formats: 2x + 5, x + 3, -3x - 2, etc.
                    # Pattern to match: coefficient*variable + constant
                    pattern = rf'([+-]?\s*\d*\.?\d*)\s*{variable}\s*([+-]\s*\d+\.?\d*)?'
                    match = re.search(pattern, left)
                    
                    if match:
                        coeff_str = match.group(1).replace(' ', '')
                        const_str = (match.group(2) or '0').replace(' ', '')
                        
                        # Parse coefficient
                        if not coeff_str or coeff_str in ['+', '-']:
                            coeff = 1 if coeff_str != '-' else -1
                        else:
                            coeff = float(coeff_str)
                        
                        # Parse constant
                        const = float(const_str)
                        
                        # Parse right side
                        right_val = float(right)
                        
                        # Solve ax + b = c -> x = (c - b) / a
                        if coeff != 0:
                            solution = (right_val - const) / coeff
                            return [solution]
                        else:
                            # Division by zero
                            return None
                    
                    # Try simpler pattern for just "x + number" or "number + x"
                    simple_pattern = rf'({variable}\s*[+-]\s*\d+\.?\d*|\d+\.?\d*\s*[+-]\s*{variable})'
                    match = re.search(simple_pattern, left)
                    
                    if match:
                        term = match.group(1)
                        if term.startswith(variable):
                            # Format: x + number
                            const_str = term[len(variable):].replace(' ', '')
                            const = float(const_str)
                            right_val = float(right)
                            solution = right_val - const
                            return [solution]
                        else:
                            # Format: number + x
                            const_str = term[:term.find(variable)].replace(' ', '')
                            const = float(const_str)
                            right_val = float(right)
                            solution = right_val - const
                            return [solution]
            
            return None
            
        except Exception as e:
            print(f"Equation solving error: {e}")
            return None
    
    def convert_units(self, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Convert between units"""
        # Basic unit conversion (can be extended)
        conversions = {
            # Length
            ('m', 'cm'): 100,
            ('m', 'mm'): 1000,
            ('m', 'km'): 0.001,
            ('cm', 'm'): 0.01,
            ('mm', 'm'): 0.001,
            ('km', 'm'): 1000,
            ('ft', 'm'): 0.3048,
            ('m', 'ft'): 3.28084,
            ('in', 'cm'): 2.54,
            ('cm', 'in'): 0.393701,
            
            # Weight
            ('kg', 'g'): 1000,
            ('g', 'kg'): 0.001,
            ('kg', 'lb'): 2.20462,
            ('lb', 'kg'): 0.453592,
            
            # Temperature (special handling needed)
            # Volume
            ('l', 'ml'): 1000,
            ('ml', 'l'): 0.001,
            ('gal', 'l'): 3.78541,
            ('l', 'gal'): 0.264172,
        }
        
        try:
            # Handle temperature conversions separately
            if from_unit == 'c' and to_unit == 'f':
                return value * 9/5 + 32
            elif from_unit == 'f' and to_unit == 'c':
                return (value - 32) * 5/9
            elif from_unit == 'c' and to_unit == 'k':
                return value + 273.15
            elif from_unit == 'k' and to_unit == 'c':
                return value - 273.15
            
            # Handle other conversions
            key = (from_unit.lower(), to_unit.lower())
            if key in conversions:
                return value * conversions[key]
            
            # Try reverse conversion
            reverse_key = (to_unit.lower(), from_unit.lower())
            if reverse_key in conversions:
                return value / conversions[reverse_key]
            
            return None
            
        except Exception:
            return None
    
    def export_results(self, data: Any, format: str = "json") -> str:
        """Export calculation results in different formats"""
        if format == "json":
            return json.dumps(data, indent=2, default=str)
        
        elif format == "csv":
            if isinstance(data, list) and data and isinstance(data[0], dict):
                try:
                    import pandas as pd
                    df = pd.DataFrame(data)
                    return df.to_csv(index=False)
                except ImportError:
                    # Fallback to manual CSV creation
                    if data:
                        headers = list(data[0].keys())
                        lines = [','.join(headers)]
                        for row in data:
                            values = [str(row.get(h, '')) for h in headers]
                            lines.append(','.join(values))
                        return '\n'.join(lines)
            return str(data)
        
        elif format == "markdown":
            if isinstance(data, dict):
                lines = ["# Calculation Results", ""]
                for key, value in data.items():
                    lines.append(f"**{key}**: {value}")
                return "\n".join(lines)
            elif isinstance(data, list):
                lines = ["# Results", ""]
                for i, item in enumerate(data, 1):
                    lines.append(f"{i}. {item}")
                return "\n".join(lines)
        
        return str(data)
    
    def get_available_functions(self) -> Dict[str, str]:
        """Get list of available mathematical functions"""
        return {
            'sin': 'Sine function',
            'cos': 'Cosine function', 
            'tan': 'Tangent function',
            'asin': 'Arcsine function',
            'acos': 'Arccosine function',
            'atan': 'Arctangent function',
            'log': 'Natural logarithm',
            'log10': 'Base-10 logarithm',
            'exp': 'Exponential function',
            'sqrt': 'Square root',
            'abs': 'Absolute value',
            'ceil': 'Ceiling function',
            'floor': 'Floor function',
            'round': 'Round to nearest integer',
            'pi': 'Pi constant (3.14159...)',
            'e': 'Euler\'s number (2.71828...)'
        }
    
    def cleanup(self) -> None:
        """Clean up resources"""
        for sql_tool in self.sql_tools.values():
            sql_tool.disconnect()
        self.sql_tools.clear()

