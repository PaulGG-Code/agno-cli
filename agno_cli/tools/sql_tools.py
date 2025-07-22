"""
SQL Toolkit for Agno CLI
Provides general SQL query execution with multiple database backends
"""

import sqlite3
import mysql.connector
import psycopg2
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
from rich.syntax import Syntax
import tempfile
import os
import re

console = Console()


@dataclass
class SQLQueryResult:
    """Result of SQL query operations"""
    success: bool
    message: str
    operation: str
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = None
    execution_time: Optional[float] = None
    rows_affected: Optional[int] = None
    columns: Optional[List[str]] = None
    
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
            'timestamp': self.timestamp.isoformat(),
            'execution_time': self.execution_time,
            'rows_affected': self.rows_affected,
            'columns': self.columns
        }


@dataclass
class DatabaseConnection:
    """Database connection configuration"""
    type: str  # sqlite, mysql, postgresql
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    file_path: Optional[str] = None


class SQLTools:
    """Core SQL operations class with multiple database support"""
    
    def __init__(self, connection_config: DatabaseConnection):
        self.connection_config = connection_config
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Establish database connection based on type"""
        try:
            if self.connection_config.type == 'sqlite':
                self.connection = sqlite3.connect(
                    self.connection_config.file_path or ':memory:',
                    check_same_thread=False
                )
                self.connection.row_factory = sqlite3.Row
            
            elif self.connection_config.type == 'mysql':
                self.connection = mysql.connector.connect(
                    host=self.connection_config.host,
                    port=self.connection_config.port,
                    database=self.connection_config.database,
                    user=self.connection_config.username,
                    password=self.connection_config.password
                )
            
            elif self.connection_config.type == 'postgresql':
                self.connection = psycopg2.connect(
                    host=self.connection_config.host,
                    port=self.connection_config.port,
                    database=self.connection_config.database,
                    user=self.connection_config.username,
                    password=self.connection_config.password
                )
            
            else:
                raise ValueError(f"Unsupported database type: {self.connection_config.type}")
                
        except Exception as e:
            raise Exception(f"Failed to connect to {self.connection_config.type}: {str(e)}")
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> SQLQueryResult:
        """Execute SQL query"""
        import time
        start_time = time.time()
        
        try:
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            execution_time = time.time() - start_time
            
            # Check if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                # Fetch results
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description] if cursor.description else []
                
                # Convert to list of dictionaries
                data = []
                for row in rows:
                    if self.connection_config.type == 'sqlite':
                        data.append(dict(row))
                    else:
                        data.append(dict(zip(columns, row)))
                
                return SQLQueryResult(
                    success=True,
                    message=f"Query executed successfully in {execution_time:.3f}s",
                    data=data,
                    operation="execute_query",
                    execution_time=execution_time,
                    rows_affected=len(data),
                    columns=columns
                )
            else:
                # For non-SELECT queries, commit and get rows affected
                self.connection.commit()
                rows_affected = cursor.rowcount
                
                return SQLQueryResult(
                    success=True,
                    message=f"Query executed successfully in {execution_time:.3f}s",
                    data=None,
                    operation="execute_query",
                    execution_time=execution_time,
                    rows_affected=rows_affected
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return SQLQueryResult(
                success=False,
                message=f"Query execution failed: {str(e)}",
                error=str(e),
                operation="execute_query",
                execution_time=execution_time
            )
    
    def execute_script(self, script: str) -> SQLQueryResult:
        """Execute SQL script with multiple statements"""
        import time
        start_time = time.time()
        
        try:
            cursor = self.connection.cursor()
            
            # Split script into individual statements
            statements = self._split_sql_statements(script)
            results = []
            total_rows_affected = 0
            
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
                    if not statement.strip().upper().startswith('SELECT'):
                        total_rows_affected += cursor.rowcount
            
            self.connection.commit()
            execution_time = time.time() - start_time
            
            return SQLQueryResult(
                success=True,
                message=f"Script executed successfully in {execution_time:.3f}s ({len(statements)} statements)",
                data=results,
                operation="execute_script",
                execution_time=execution_time,
                rows_affected=total_rows_affected
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return SQLQueryResult(
                success=False,
                message=f"Script execution failed: {str(e)}",
                error=str(e),
                operation="execute_script",
                execution_time=execution_time
            )
    
    def _split_sql_statements(self, script: str) -> List[str]:
        """Split SQL script into individual statements"""
        # Remove comments
        script = re.sub(r'--.*$', '', script, flags=re.MULTILINE)
        script = re.sub(r'/\*.*?\*/', '', script, flags=re.DOTALL)
        
        # Split by semicolon, but handle strings and other delimiters
        statements = []
        current_statement = ""
        in_string = False
        string_char = None
        paren_count = 0
        
        for char in script:
            current_statement += char
            
            if char in ["'", '"'] and (not in_string or char == string_char):
                if not in_string:
                    in_string = True
                    string_char = char
                else:
                    in_string = False
                    string_char = None
            
            elif char == '(' and not in_string:
                paren_count += 1
            elif char == ')' and not in_string:
                paren_count -= 1
            
            elif char == ';' and not in_string and paren_count == 0:
                statements.append(current_statement.strip())
                current_statement = ""
        
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return [stmt for stmt in statements if stmt.strip()]
    
    def get_table_info(self, table_name: str) -> SQLQueryResult:
        """Get detailed information about a table"""
        try:
            if self.connection_config.type == 'sqlite':
                # Get table schema
                schema_query = f"PRAGMA table_info({table_name})"
                schema_result = self.execute_query(schema_query)
                
                if not schema_result.success:
                    return schema_result
                
                # Get row count
                count_query = f"SELECT COUNT(*) as row_count FROM {table_name}"
                count_result = self.execute_query(count_query)
                
                # Get sample data
                sample_query = f"SELECT * FROM {table_name} LIMIT 5"
                sample_result = self.execute_query(sample_query)
                
                table_info = {
                    'name': table_name,
                    'schema': schema_result.data,
                    'row_count': count_result.data[0]['row_count'] if count_result.success and count_result.data else 0,
                    'sample_data': sample_result.data if sample_result.success else []
                }
                
            elif self.connection_config.type == 'mysql':
                # Get table schema
                schema_query = f"DESCRIBE {table_name}"
                schema_result = self.execute_query(schema_query)
                
                if not schema_result.success:
                    return schema_result
                
                # Get row count
                count_query = f"SELECT COUNT(*) as row_count FROM {table_name}"
                count_result = self.execute_query(count_query)
                
                # Get sample data
                sample_query = f"SELECT * FROM {table_name} LIMIT 5"
                sample_result = self.execute_query(sample_query)
                
                table_info = {
                    'name': table_name,
                    'schema': schema_result.data,
                    'row_count': count_result.data[0]['row_count'] if count_result.success and count_result.data else 0,
                    'sample_data': sample_result.data if sample_result.success else []
                }
                
            elif self.connection_config.type == 'postgresql':
                # Get table schema
                schema_query = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
                """
                schema_result = self.execute_query(schema_query, {'table_name': table_name})
                
                if not schema_result.success:
                    return schema_result
                
                # Get row count
                count_query = f"SELECT COUNT(*) as row_count FROM {table_name}"
                count_result = self.execute_query(count_query)
                
                # Get sample data
                sample_query = f"SELECT * FROM {table_name} LIMIT 5"
                sample_result = self.execute_query(sample_query)
                
                table_info = {
                    'name': table_name,
                    'schema': schema_result.data,
                    'row_count': count_result.data[0]['row_count'] if count_result.success and count_result.data else 0,
                    'sample_data': sample_result.data if sample_result.success else []
                }
            
            return SQLQueryResult(
                success=True,
                message=f"Table information retrieved for {table_name}",
                data=table_info,
                operation="get_table_info"
            )
            
        except Exception as e:
            return SQLQueryResult(
                success=False,
                message=f"Failed to get table info: {str(e)}",
                error=str(e),
                operation="get_table_info"
            )
    
    def list_tables(self) -> SQLQueryResult:
        """List all tables in database"""
        try:
            if self.connection_config.type == 'sqlite':
                query = "SELECT name FROM sqlite_master WHERE type='table'"
            elif self.connection_config.type == 'mysql':
                query = "SHOW TABLES"
            elif self.connection_config.type == 'postgresql':
                query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                """
            
            result = self.execute_query(query)
            
            if result.success:
                if self.connection_config.type == 'mysql':
                    tables = [row[f'Tables_in_{self.connection_config.database}'] for row in result.data]
                else:
                    tables = [row['name'] if 'name' in row else row['table_name'] for row in result.data]
                
                result.data = {'tables': tables, 'count': len(tables)}
                result.message = f"Found {len(tables)} tables in database"
            
            return result
            
        except Exception as e:
            return SQLQueryResult(
                success=False,
                message=f"Failed to list tables: {str(e)}",
                error=str(e),
                operation="list_tables"
            )
    
    def get_database_info(self) -> SQLQueryResult:
        """Get comprehensive database information"""
        try:
            # List tables
            tables_result = self.list_tables()
            if not tables_result.success:
                return tables_result
            
            # Get database size (approximate)
            if self.connection_config.type == 'sqlite':
                size_query = "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"
            elif self.connection_config.type == 'mysql':
                size_query = f"""
                SELECT SUM(data_length + index_length) as size
                FROM information_schema.tables
                WHERE table_schema = '{self.connection_config.database}'
                """
            elif self.connection_config.type == 'postgresql':
                size_query = f"""
                SELECT pg_database_size('{self.connection_config.database}') as size
                """
            
            size_result = self.execute_query(size_query)
            
            db_info = {
                'type': self.connection_config.type,
                'tables': tables_result.data['tables'],
                'table_count': len(tables_result.data['tables']),
                'size_bytes': size_result.data[0]['size'] if size_result.success and size_result.data else 0,
                'connection_info': {
                    'host': self.connection_config.host,
                    'port': self.connection_config.port,
                    'database': self.connection_config.database,
                    'username': self.connection_config.username
                }
            }
            
            return SQLQueryResult(
                success=True,
                message=f"Database information retrieved ({db_info['table_count']} tables)",
                data=db_info,
                operation="get_database_info"
            )
            
        except Exception as e:
            return SQLQueryResult(
                success=False,
                message=f"Failed to get database info: {str(e)}",
                error=str(e),
                operation="get_database_info"
            )
    
    def backup_database(self, backup_path: str) -> SQLQueryResult:
        """Backup database"""
        try:
            if self.connection_config.type == 'sqlite':
                import shutil
                shutil.copy2(self.connection_config.file_path, backup_path)
            else:
                # For other databases, this would require specific backup commands
                return SQLQueryResult(
                    success=False,
                    message=f"Backup not implemented for {self.connection_config.type}",
                    error="NotImplemented",
                    operation="backup_database"
                )
            
            return SQLQueryResult(
                success=True,
                message=f"Database backed up to {backup_path}",
                operation="backup_database"
            )
            
        except Exception as e:
            return SQLQueryResult(
                success=False,
                message=f"Failed to backup database: {str(e)}",
                error=str(e),
                operation="backup_database"
            )
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()


class SQLToolsManager:
    """Manager class for SQL operations with CLI integration"""
    
    def __init__(self, connection_config: DatabaseConnection):
        self.connection_config = connection_config
        self.sql_tools = SQLTools(connection_config)
        self.console = Console()
    
    def execute_query(self, query: str, params: Dict[str, Any] = None, format: str = "table") -> None:
        """Execute SQL query and display results"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Executing query...", total=None)
            result = self.sql_tools.execute_query(query, params)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            
            if result.data:
                if format == "table":
                    self._display_query_results_table(result.data, result.columns)
                elif format == "json":
                    self.console.print(json.dumps(result.data, indent=2, default=str))
                else:
                    self.console.print(result.data)
            
            if result.rows_affected is not None:
                self.console.print(f"📊 Rows affected: {result.rows_affected}")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def _display_query_results_table(self, data: List[Dict], columns: List[str] = None) -> None:
        """Display query results in a rich table"""
        if not data:
            self.console.print("[yellow]No data returned[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta", title="Query Results")
        
        # Add columns
        if columns:
            for column in columns:
                table.add_column(column, style="cyan", max_width=30)
        else:
            for column in data[0].keys():
                table.add_column(column, style="cyan", max_width=30)
        
        # Add rows
        for row in data:
            row_data = []
            for value in row.values():
                if value is None:
                    value = 'NULL'
                elif isinstance(value, (int, float)):
                    value = f"{value:,}" if isinstance(value, int) else f"{value:.2f}"
                else:
                    value = str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
                row_data.append(value)
            table.add_row(*row_data)
        
        self.console.print(table)
    
    def execute_script(self, script: str, format: str = "table") -> None:
        """Execute SQL script and display results"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Executing script...", total=None)
            result = self.sql_tools.execute_script(script)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            if result.rows_affected:
                self.console.print(f"📊 Total rows affected: {result.rows_affected}")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def show_table_info(self, table_name: str, format: str = "table") -> None:
        """Show detailed table information"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Getting table info...", total=None)
            result = self.sql_tools.get_table_info(table_name)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            
            if format == "table":
                self._display_table_info_table(result.data)
            elif format == "json":
                self.console.print(json.dumps(result.data, indent=2, default=str))
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def _display_table_info_table(self, table_info: Dict) -> None:
        """Display table information in tables"""
        # Schema table
        if table_info['schema']:
            schema_table = Table(show_header=True, header_style="bold magenta", title=f"Table Schema: {table_info['name']}")
            
            # Add columns based on schema structure
            if table_info['schema']:
                first_schema = table_info['schema'][0]
                for key in first_schema.keys():
                    schema_table.add_column(key, style="cyan", max_width=20)
                
                for col in table_info['schema']:
                    row_data = []
                    for value in col.values():
                        if value is None:
                            value = 'NULL'
                        else:
                            value = str(value)[:20] + "..." if len(str(value)) > 20 else str(value)
                        row_data.append(value)
                    schema_table.add_row(*row_data)
            
            self.console.print(schema_table)
        else:
            self.console.print(f"[yellow]No schema information available for {table_info['name']}[/yellow]")
        
        # Sample data table
        if table_info['sample_data']:
            sample_table = Table(show_header=True, header_style="bold magenta", title="Sample Data")
            
            # Add columns
            for column in table_info['sample_data'][0].keys():
                sample_table.add_column(column, style="cyan", max_width=20)
            
            # Add rows
            for row in table_info['sample_data']:
                row_data = []
                for value in row.values():
                    if value is None:
                        value = 'NULL'
                    elif isinstance(value, (int, float)):
                        value = f"{value:,}" if isinstance(value, int) else f"{value:.2f}"
                    else:
                        value = str(value)[:20] + "..." if len(str(value)) > 20 else str(value)
                    row_data.append(value)
                sample_table.add_row(*row_data)
            
            self.console.print(sample_table)
        
        # Summary
        self.console.print(f"📊 Total rows: {table_info['row_count']:,}")
    
    def list_tables(self, format: str = "table") -> None:
        """List all tables in database"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Listing tables...", total=None)
            result = self.sql_tools.list_tables()
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            
            if format == "table":
                self._display_tables_list(result.data['tables'])
            elif format == "json":
                self.console.print(json.dumps(result.data, indent=2))
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def _display_tables_list(self, tables: List[str]) -> None:
        """Display tables list in a table"""
        if not tables:
            self.console.print("[yellow]No tables found[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta", title="Database Tables")
        table.add_column("Table Name", style="cyan")
        table.add_column("Status", style="green")
        
        for table_name in tables:
            table.add_row(table_name, "✅ Active")
        
        self.console.print(table)
    
    def show_database_info(self, format: str = "table") -> None:
        """Show comprehensive database information"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Getting database info...", total=None)
            result = self.sql_tools.get_database_info()
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            
            if format == "table":
                self._display_database_info_table(result.data)
            elif format == "json":
                self.console.print(json.dumps(result.data, indent=2))
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def _display_database_info_table(self, db_info: Dict) -> None:
        """Display database information in a table"""
        info_table = Table(show_header=True, header_style="bold magenta", title="Database Information")
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="green")
        
        info_table.add_row("Type", db_info['type'])
        info_table.add_row("Tables", str(db_info['table_count']))
        info_table.add_row("Size", f"{db_info['size_bytes'] / 1024:.2f} KB")
        
        if db_info['connection_info']['host']:
            info_table.add_row("Host", db_info['connection_info']['host'])
        if db_info['connection_info']['database']:
            info_table.add_row("Database", db_info['connection_info']['database'])
        
        self.console.print(info_table)
        
        # Tables list
        if db_info['tables']:
            tables_table = Table(show_header=True, header_style="bold blue", title="Tables")
            tables_table.add_column("Table Name", style="cyan")
            
            for table_name in db_info['tables']:
                tables_table.add_row(table_name)
            
            self.console.print(tables_table)
    
    def backup_database(self, backup_path: str) -> None:
        """Backup database"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Backing up database...", total=None)
            result = self.sql_tools.backup_database(backup_path)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def close(self):
        """Close database connection"""
        self.sql_tools.close() 