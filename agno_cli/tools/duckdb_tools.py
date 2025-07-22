"""
DuckDB Toolkit for Agno CLI
Provides lightweight database operations with SQL query execution
"""

import duckdb
import pandas as pd
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
import sqlite3
import tempfile
import os

console = Console()


@dataclass
class DuckDBQueryResult:
    """Result of DuckDB query operations"""
    success: bool
    message: str
    operation: str
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = None
    execution_time: Optional[float] = None
    rows_affected: Optional[int] = None
    
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
            'rows_affected': self.rows_affected
        }


@dataclass
class DatabaseInfo:
    """Database information structure"""
    tables: List[str]
    views: List[str]
    functions: List[str]
    schemas: List[str]
    size_bytes: int
    table_count: int
    view_count: int
    function_count: int


class DuckDBTools:
    """Core DuckDB operations class"""
    
    def __init__(self, database_path: str = None, memory_mode: bool = True):
        self.database_path = database_path
        self.memory_mode = memory_mode
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            if self.memory_mode or self.database_path is None:
                self.connection = duckdb.connect(':memory:')
            else:
                # Ensure directory exists
                db_path = Path(self.database_path)
                db_path.parent.mkdir(parents=True, exist_ok=True)
                self.connection = duckdb.connect(str(db_path))
            
            # Enable extensions
            self.connection.execute("INSTALL httpfs")
            self.connection.execute("LOAD httpfs")
            self.connection.execute("INSTALL parquet")
            self.connection.execute("LOAD parquet")
            
        except Exception as e:
            raise Exception(f"Failed to connect to DuckDB: {str(e)}")
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> DuckDBQueryResult:
        """Execute SQL query"""
        import time
        start_time = time.time()
        
        try:
            if params:
                result = self.connection.execute(query, params)
            else:
                result = self.connection.execute(query)
            
            execution_time = time.time() - start_time
            
            # Check if it's a SELECT query or SHOW query
            if query.strip().upper().startswith('SELECT') or query.strip().upper().startswith('SHOW'):
                # Fetch results
                data = result.fetchdf()
                rows_affected = len(data)
                
                return DuckDBQueryResult(
                    success=True,
                    message=f"Query executed successfully in {execution_time:.3f}s",
                    data=data.to_dict('records') if not data.empty else [],
                    operation="execute_query",
                    execution_time=execution_time,
                    rows_affected=rows_affected
                )
            else:
                # For non-SELECT queries, get rows affected
                rows_affected = result.rowcount if hasattr(result, 'rowcount') else None
                
                return DuckDBQueryResult(
                    success=True,
                    message=f"Query executed successfully in {execution_time:.3f}s",
                    data=None,
                    operation="execute_query",
                    execution_time=execution_time,
                    rows_affected=rows_affected
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return DuckDBQueryResult(
                success=False,
                message=f"Query execution failed: {str(e)}",
                error=str(e),
                operation="execute_query",
                execution_time=execution_time
            )
    
    def create_table(self, table_name: str, schema: Dict[str, str], data: List[Dict] = None) -> DuckDBQueryResult:
        """Create table with schema"""
        try:
            # Build CREATE TABLE statement
            columns = []
            for col_name, col_type in schema.items():
                columns.append(f"{col_name} {col_type}")
            
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            
            result = self.execute_query(create_sql)
            
            if result.success and data:
                # Insert data if provided
                insert_result = self.insert_data(table_name, data)
                if not insert_result.success:
                    return insert_result
            
            return result
            
        except Exception as e:
            return DuckDBQueryResult(
                success=False,
                message=f"Failed to create table: {str(e)}",
                error=str(e),
                operation="create_table"
            )
    
    def insert_data(self, table_name: str, data: List[Dict]) -> DuckDBQueryResult:
        """Insert data into table"""
        if not data:
            return DuckDBQueryResult(
                success=True,
                message="No data to insert",
                operation="insert_data",
                rows_affected=0
            )
        
        try:
            # Convert to DataFrame for easier handling
            df = pd.DataFrame(data)
            
            # Insert data
            self.connection.execute(f"INSERT INTO {table_name} SELECT * FROM df", [df])
            
            return DuckDBQueryResult(
                success=True,
                message=f"Successfully inserted {len(data)} rows into {table_name}",
                operation="insert_data",
                rows_affected=len(data)
            )
            
        except Exception as e:
            return DuckDBQueryResult(
                success=False,
                message=f"Failed to insert data: {str(e)}",
                error=str(e),
                operation="insert_data"
            )
    
    def import_csv(self, file_path: str, table_name: str, options: Dict[str, Any] = None) -> DuckDBQueryResult:
        """Import CSV file into table"""
        try:
            # Default options
            default_options = {
                'delimiter': ',',
                'header': True,
                'auto_detect': True
            }
            if options:
                default_options.update(options)
            
            # First, create table from CSV (DuckDB can auto-detect schema)
            create_sql = f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{file_path}')"
            create_result = self.execute_query(create_sql)
            
            if not create_result.success:
                return create_result
            
            # Get row count
            count_result = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
            if count_result.success:
                row_count = count_result.data[0]['count'] if count_result.data else 0
                create_result.message = f"Successfully imported {row_count} rows from {file_path} into {table_name}"
                create_result.rows_affected = row_count
            
            return create_result
            
        except Exception as e:
            return DuckDBQueryResult(
                success=False,
                message=f"Failed to import CSV: {str(e)}",
                error=str(e),
                operation="import_csv"
            )
    
    def export_csv(self, table_name: str, file_path: str, options: Dict[str, Any] = None) -> DuckDBQueryResult:
        """Export table to CSV file"""
        try:
            # Default options
            default_options = {
                'delimiter': ',',
                'header': True
            }
            if options:
                default_options.update(options)
            
            # Build COPY statement
            copy_sql = f"COPY {table_name} TO '{file_path}' ("
            copy_options = []
            
            if 'delimiter' in default_options:
                copy_options.append(f"DELIMITER '{default_options['delimiter']}'")
            if 'header' in default_options:
                copy_options.append(f"HEADER {str(default_options['header']).upper()}")
            
            copy_sql += ", ".join(copy_options) + ")"
            
            result = self.execute_query(copy_sql)
            
            if result.success:
                # Get row count
                count_result = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
                if count_result.success:
                    row_count = count_result.data[0]['count'] if count_result.data else 0
                    result.message = f"Successfully exported {row_count} rows from {table_name} to {file_path}"
                    result.rows_affected = row_count
            
            return result
            
        except Exception as e:
            return DuckDBQueryResult(
                success=False,
                message=f"Failed to export CSV: {str(e)}",
                error=str(e),
                operation="export_csv"
            )
    
    def get_table_info(self, table_name: str) -> DuckDBQueryResult:
        """Get detailed information about a table"""
        try:
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
                'schema': schema_result.data if schema_result.data else [],
                'row_count': count_result.data[0]['row_count'] if count_result.success and count_result.data else 0,
                'sample_data': sample_result.data if sample_result.success else []
            }
            
            return DuckDBQueryResult(
                success=True,
                message=f"Table information retrieved for {table_name}",
                data=table_info,
                operation="get_table_info"
            )
            
        except Exception as e:
            return DuckDBQueryResult(
                success=False,
                message=f"Failed to get table info: {str(e)}",
                error=str(e),
                operation="get_table_info"
            )
    
    def list_tables(self) -> DuckDBQueryResult:
        """List all tables in database"""
        try:
            query = "SHOW TABLES"
            result = self.execute_query(query)
            
            if result.success:
                tables = [row['name'] for row in result.data] if result.data else []
                result.data = {'tables': tables, 'count': len(tables)}
                result.message = f"Found {len(tables)} tables in database"
            
            return result
            
        except Exception as e:
            return DuckDBQueryResult(
                success=False,
                message=f"Failed to list tables: {str(e)}",
                error=str(e),
                operation="list_tables"
            )
    
    def get_database_info(self) -> DuckDBQueryResult:
        """Get comprehensive database information"""
        try:
            # List tables
            tables_result = self.list_tables()
            if not tables_result.success:
                return tables_result
            
            # Get database size (approximate)
            size_query = """
            SELECT SUM(pg_column_size(column_name)) as total_size
            FROM information_schema.columns
            WHERE table_schema = 'main'
            """
            size_result = self.execute_query(size_query)
            
            # Get table details
            table_details = []
            for table_name in tables_result.data['tables']:
                table_info = self.get_table_info(table_name)
                if table_info.success:
                    table_details.append(table_info.data)
            
            db_info = DatabaseInfo(
                tables=tables_result.data['tables'],
                views=[],  # DuckDB doesn't have views in the same way
                functions=[],  # Could be extended
                schemas=['main'],  # Default schema
                size_bytes=size_result.data[0]['total_size'] if size_result.success and size_result.data else 0,
                table_count=len(tables_result.data['tables']),
                view_count=0,
                function_count=0
            )
            
            return DuckDBQueryResult(
                success=True,
                message=f"Database information retrieved ({db_info.table_count} tables)",
                data=asdict(db_info),
                operation="get_database_info"
            )
            
        except Exception as e:
            return DuckDBQueryResult(
                success=False,
                message=f"Failed to get database info: {str(e)}",
                error=str(e),
                operation="get_database_info"
            )
    
    def backup_database(self, backup_path: str) -> DuckDBQueryResult:
        """Backup database to file"""
        try:
            if self.memory_mode:
                return DuckDBQueryResult(
                    success=False,
                    message="Cannot backup in-memory database",
                    error="MemoryModeError",
                    operation="backup_database"
                )
            
            # For file-based databases, just copy the file
            import shutil
            shutil.copy2(self.database_path, backup_path)
            
            return DuckDBQueryResult(
                success=True,
                message=f"Database backed up to {backup_path}",
                operation="backup_database"
            )
            
        except Exception as e:
            return DuckDBQueryResult(
                success=False,
                message=f"Failed to backup database: {str(e)}",
                error=str(e),
                operation="backup_database"
            )
    
    def restore_database(self, backup_path: str) -> DuckDBQueryResult:
        """Restore database from backup"""
        try:
            if self.memory_mode:
                return DuckDBQueryResult(
                    success=False,
                    message="Cannot restore to in-memory database",
                    error="MemoryModeError",
                    operation="restore_database"
                )
            
            # Close current connection
            if self.connection:
                self.connection.close()
            
            # Copy backup to database path
            import shutil
            shutil.copy2(backup_path, self.database_path)
            
            # Reconnect
            self._connect()
            
            return DuckDBQueryResult(
                success=True,
                message=f"Database restored from {backup_path}",
                operation="restore_database"
            )
            
        except Exception as e:
            return DuckDBQueryResult(
                success=False,
                message=f"Failed to restore database: {str(e)}",
                error=str(e),
                operation="restore_database"
            )
    
    def optimize_database(self) -> DuckDBQueryResult:
        """Optimize database performance"""
        try:
            # Run VACUUM to optimize storage
            vacuum_result = self.execute_query("VACUUM")
            
            # Analyze tables for better query planning
            tables_result = self.list_tables()
            if tables_result.success:
                for table_name in tables_result.data['tables']:
                    self.execute_query(f"ANALYZE {table_name}")
            
            return DuckDBQueryResult(
                success=True,
                message="Database optimization completed",
                operation="optimize_database"
            )
            
        except Exception as e:
            return DuckDBQueryResult(
                success=False,
                message=f"Failed to optimize database: {str(e)}",
                error=str(e),
                operation="optimize_database"
            )
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()


class DuckDBToolsManager:
    """Manager class for DuckDB operations with CLI integration"""
    
    def __init__(self, database_path: str = None, memory_mode: bool = True):
        self.database_path = database_path
        self.memory_mode = memory_mode
        self.duckdb_tools = DuckDBTools(database_path, memory_mode)
        self.console = Console()
    
    def execute_query(self, query: str, params: Dict[str, Any] = None, format: str = "table") -> None:
        """Execute SQL query and display results"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Executing query...", total=None)
            result = self.duckdb_tools.execute_query(query, params)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            
            if result.data:
                if format == "table":
                    self._display_query_results_table(result.data)
                elif format == "json":
                    self.console.print(json.dumps(result.data, indent=2, default=str))
                else:
                    self.console.print(result.data)
            
            if result.rows_affected is not None:
                self.console.print(f"📊 Rows affected: {result.rows_affected}")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def _display_query_results_table(self, data: List[Dict]) -> None:
        """Display query results in a rich table"""
        if not data:
            self.console.print("[yellow]No data returned[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta", title="Query Results")
        
        # Add columns
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
    
    def create_table(self, table_name: str, schema: Dict[str, str], data: List[Dict] = None) -> None:
        """Create table with schema"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Creating table...", total=None)
            result = self.duckdb_tools.create_table(table_name, schema, data)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            if result.rows_affected:
                self.console.print(f"📊 Rows inserted: {result.rows_affected}")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def import_csv(self, file_path: str, table_name: str, options: Dict[str, Any] = None) -> None:
        """Import CSV file into table"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Importing CSV...", total=None)
            result = self.duckdb_tools.import_csv(file_path, table_name, options)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            if result.rows_affected:
                self.console.print(f"📊 Rows imported: {result.rows_affected}")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def export_csv(self, table_name: str, file_path: str, options: Dict[str, Any] = None) -> None:
        """Export table to CSV file"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Exporting CSV...", total=None)
            result = self.duckdb_tools.export_csv(table_name, file_path, options)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            if result.rows_affected:
                self.console.print(f"📊 Rows exported: {result.rows_affected}")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def show_table_info(self, table_name: str, format: str = "table") -> None:
        """Show detailed table information"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Getting table info...", total=None)
            result = self.duckdb_tools.get_table_info(table_name)
        
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
            schema_table.add_column("Column", style="cyan")
            schema_table.add_column("Type", style="blue")
            schema_table.add_column("Null", style="yellow")
            schema_table.add_column("Key", style="green")
            schema_table.add_column("Default", style="red")
            
            for col in table_info['schema']:
                schema_table.add_row(
                    col.get('column_name', ''),
                    col.get('column_type', ''),
                    col.get('is_nullable', ''),
                    col.get('column_key', ''),
                    col.get('column_default', '')
                )
            
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
            result = self.duckdb_tools.list_tables()
        
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
            result = self.duckdb_tools.get_database_info()
        
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
        
        info_table.add_row("Tables", str(db_info['table_count']))
        info_table.add_row("Views", str(db_info['view_count']))
        info_table.add_row("Functions", str(db_info['function_count']))
        info_table.add_row("Schemas", str(len(db_info['schemas'])))
        info_table.add_row("Size", f"{db_info['size_bytes'] / 1024:.2f} KB")
        
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
            result = self.duckdb_tools.backup_database(backup_path)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def restore_database(self, backup_path: str) -> None:
        """Restore database from backup"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Restoring database...", total=None)
            result = self.duckdb_tools.restore_database(backup_path)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def optimize_database(self) -> None:
        """Optimize database performance"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Optimizing database...", total=None)
            result = self.duckdb_tools.optimize_database()
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def close(self):
        """Close database connection"""
        self.duckdb_tools.close() 