"""
PostgreSQL Toolkit for Agno CLI
Provides specialized PostgreSQL database integration with advanced features
"""

import psycopg2
import psycopg2.extras
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
class PostgresQueryResult:
    """Result of PostgreSQL query operations"""
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
class PostgresConnection:
    """PostgreSQL connection configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "postgres"
    username: str = "postgres"
    password: Optional[str] = None
    ssl_mode: str = "prefer"
    connection_timeout: int = 10


@dataclass
class TableInfo:
    """PostgreSQL table information"""
    table_name: str
    table_schema: str
    table_type: str
    row_count: int
    size_bytes: int
    index_count: int
    column_count: int
    last_vacuum: Optional[datetime] = None
    last_analyze: Optional[datetime] = None


@dataclass
class IndexInfo:
    """PostgreSQL index information"""
    index_name: str
    table_name: str
    index_type: str
    columns: List[str]
    is_unique: bool
    size_bytes: int


class PostgresTools:
    """Core PostgreSQL operations class"""
    
    def __init__(self, connection_config: PostgresConnection):
        self.connection_config = connection_config
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Establish PostgreSQL connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.connection_config.host,
                port=self.connection_config.port,
                database=self.connection_config.database,
                user=self.connection_config.username,
                password=self.connection_config.password,
                sslmode=self.connection_config.ssl_mode,
                connect_timeout=self.connection_config.connection_timeout
            )
            
            # Enable autocommit for DDL operations
            self.connection.autocommit = True
            
        except Exception as e:
            raise Exception(f"Failed to connect to PostgreSQL: {str(e)}")
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> PostgresQueryResult:
        """Execute PostgreSQL query"""
        import time
        start_time = time.time()
        
        try:
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            execution_time = time.time() - start_time
            
            # Check if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                # Fetch results
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # Convert to list of dictionaries
                data = [dict(row) for row in rows]
                
                return PostgresQueryResult(
                    success=True,
                    message=f"Query executed successfully in {execution_time:.3f}s",
                    data=data,
                    operation="execute_query",
                    execution_time=execution_time,
                    rows_affected=len(data),
                    columns=columns
                )
            else:
                # For non-SELECT queries, get rows affected
                rows_affected = cursor.rowcount
                
                return PostgresQueryResult(
                    success=True,
                    message=f"Query executed successfully in {execution_time:.3f}s",
                    data=None,
                    operation="execute_query",
                    execution_time=execution_time,
                    rows_affected=rows_affected
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return PostgresQueryResult(
                success=False,
                message=f"Query execution failed: {str(e)}",
                error=str(e),
                operation="execute_query",
                execution_time=execution_time
            )
    
    def execute_script(self, script: str) -> PostgresQueryResult:
        """Execute PostgreSQL script with multiple statements"""
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
            
            execution_time = time.time() - start_time
            
            return PostgresQueryResult(
                success=True,
                message=f"Script executed successfully in {execution_time:.3f}s ({len(statements)} statements)",
                data=results,
                operation="execute_script",
                execution_time=execution_time,
                rows_affected=total_rows_affected
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return PostgresQueryResult(
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
    
    def get_table_info(self, table_name: str, schema: str = "public") -> PostgresQueryResult:
        """Get detailed information about a PostgreSQL table"""
        try:
            # Get table schema
            schema_query = """
            SELECT column_name, data_type, is_nullable, column_default, 
                   character_maximum_length, numeric_precision, numeric_scale
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = %s
            ORDER BY ordinal_position
            """
            schema_result = self.execute_query(schema_query, {'table_name': table_name, 'schema': schema})
            
            if not schema_result.success:
                return schema_result
            
            # Get row count
            count_query = f"SELECT COUNT(*) as row_count FROM {schema}.{table_name}"
            count_result = self.execute_query(count_query)
            
            # Get table size
            size_query = """
            SELECT pg_total_relation_size(%s) as size_bytes
            """
            size_result = self.execute_query(size_query, {f'{schema}.{table_name}'})
            
            # Get index count
            index_query = """
            SELECT COUNT(*) as index_count
            FROM pg_indexes
            WHERE tablename = %s AND schemaname = %s
            """
            index_result = self.execute_query(index_query, {'table_name': table_name, 'schema': schema})
            
            # Get sample data
            sample_query = f"SELECT * FROM {schema}.{table_name} LIMIT 5"
            sample_result = self.execute_query(sample_query)
            
            # Get last vacuum and analyze
            stats_query = """
            SELECT last_vacuum, last_analyze
            FROM pg_stat_user_tables
            WHERE relname = %s AND schemaname = %s
            """
            stats_result = self.execute_query(stats_query, {'table_name': table_name, 'schema': schema})
            
            table_info = {
                'name': table_name,
                'schema': schema,
                'columns': schema_result.data,
                'row_count': count_result.data[0]['row_count'] if count_result.success and count_result.data else 0,
                'size_bytes': size_result.data[0]['size_bytes'] if size_result.success and size_result.data else 0,
                'index_count': index_result.data[0]['index_count'] if index_result.success and index_result.data else 0,
                'sample_data': sample_result.data if sample_result.success else [],
                'last_vacuum': stats_result.data[0]['last_vacuum'] if stats_result.success and stats_result.data else None,
                'last_analyze': stats_result.data[0]['last_analyze'] if stats_result.success and stats_result.data else None
            }
            
            return PostgresQueryResult(
                success=True,
                message=f"Table information retrieved for {schema}.{table_name}",
                data=table_info,
                operation="get_table_info"
            )
            
        except Exception as e:
            return PostgresQueryResult(
                success=False,
                message=f"Failed to get table info: {str(e)}",
                error=str(e),
                operation="get_table_info"
            )
    
    def list_tables(self, schema: str = "public") -> PostgresQueryResult:
        """List all tables in PostgreSQL database"""
        try:
            query = """
            SELECT table_name, table_type
            FROM information_schema.tables
            WHERE table_schema = %s
            ORDER BY table_name
            """
            
            result = self.execute_query(query, {'schema': schema})
            
            if result.success:
                tables = [row['table_name'] for row in result.data]
                result.data = {'tables': tables, 'count': len(tables), 'schema': schema}
                result.message = f"Found {len(tables)} tables in schema '{schema}'"
            
            return result
            
        except Exception as e:
            return PostgresQueryResult(
                success=False,
                message=f"Failed to list tables: {str(e)}",
                error=str(e),
                operation="list_tables"
            )
    
    def list_schemas(self) -> PostgresQueryResult:
        """List all schemas in PostgreSQL database"""
        try:
            query = """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY schema_name
            """
            
            result = self.execute_query(query)
            
            if result.success:
                schemas = [row['schema_name'] for row in result.data]
                result.data = {'schemas': schemas, 'count': len(schemas)}
                result.message = f"Found {len(schemas)} user schemas"
            
            return result
            
        except Exception as e:
            return PostgresQueryResult(
                success=False,
                message=f"Failed to list schemas: {str(e)}",
                error=str(e),
                operation="list_schemas"
            )
    
    def get_database_info(self) -> PostgresQueryResult:
        """Get comprehensive PostgreSQL database information"""
        try:
            # List schemas
            schemas_result = self.list_schemas()
            if not schemas_result.success:
                return schemas_result
            
            # List tables in public schema
            tables_result = self.list_tables("public")
            if not tables_result.success:
                return tables_result
            
            # Get database size
            size_query = "SELECT pg_database_size(current_database()) as size_bytes"
            size_result = self.execute_query(size_query)
            
            # Get connection info
            conn_query = """
            SELECT current_database() as database_name,
                   current_user as username,
                   inet_server_addr() as host,
                   inet_server_port() as port,
                   version() as version
            """
            conn_result = self.execute_query(conn_query)
            
            # Get table statistics
            stats_query = """
            SELECT COUNT(*) as table_count,
                   SUM(pg_total_relation_size(schemaname||'.'||tablename)) as total_size
            FROM pg_tables
            WHERE schemaname = 'public'
            """
            stats_result = self.execute_query(stats_query)
            
            db_info = {
                'schemas': schemas_result.data['schemas'],
                'schema_count': len(schemas_result.data['schemas']),
                'tables': tables_result.data['tables'],
                'table_count': len(tables_result.data['tables']),
                'size_bytes': size_result.data[0]['size_bytes'] if size_result.success and size_result.data else 0,
                'connection_info': conn_result.data[0] if conn_result.success and conn_result.data else {},
                'statistics': stats_result.data[0] if stats_result.success and stats_result.data else {}
            }
            
            return PostgresQueryResult(
                success=True,
                message=f"Database information retrieved ({db_info['table_count']} tables, {db_info['schema_count']} schemas)",
                data=db_info,
                operation="get_database_info"
            )
            
        except Exception as e:
            return PostgresQueryResult(
                success=False,
                message=f"Failed to get database info: {str(e)}",
                error=str(e),
                operation="get_database_info"
            )
    
    def get_index_info(self, table_name: str, schema: str = "public") -> PostgresQueryResult:
        """Get index information for a table"""
        try:
            query = """
            SELECT i.relname as index_name,
                   t.relname as table_name,
                   am.amname as index_type,
                   array_to_string(array_agg(a.attname), ', ') as columns,
                   ix.indisunique as is_unique,
                   pg_relation_size(i.oid) as size_bytes
            FROM pg_index ix
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_class t ON t.oid = ix.indrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            JOIN pg_am am ON am.oid = i.relam
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            WHERE t.relname = %s AND n.nspname = %s
            GROUP BY i.relname, t.relname, am.amname, ix.indisunique, i.oid
            ORDER BY i.relname
            """
            
            result = self.execute_query(query, {'table_name': table_name, 'schema': schema})
            
            if result.success:
                result.message = f"Found {len(result.data)} indexes for {schema}.{table_name}"
            
            return result
            
        except Exception as e:
            return PostgresQueryResult(
                success=False,
                message=f"Failed to get index info: {str(e)}",
                error=str(e),
                operation="get_index_info"
            )
    
    def vacuum_table(self, table_name: str, schema: str = "public", full: bool = False, analyze: bool = True) -> PostgresQueryResult:
        """Vacuum a PostgreSQL table"""
        try:
            import time
            start_time = time.time()
            
            # Build VACUUM command
            vacuum_cmd = f"VACUUM"
            if full:
                vacuum_cmd += " FULL"
            if analyze:
                vacuum_cmd += " ANALYZE"
            vacuum_cmd += f" {schema}.{table_name}"
            
            cursor = self.connection.cursor()
            cursor.execute(vacuum_cmd)
            
            execution_time = time.time() - start_time
            
            return PostgresQueryResult(
                success=True,
                message=f"VACUUM completed for {schema}.{table_name} in {execution_time:.3f}s",
                operation="vacuum_table",
                execution_time=execution_time
            )
            
        except Exception as e:
            return PostgresQueryResult(
                success=False,
                message=f"VACUUM failed: {str(e)}",
                error=str(e),
                operation="vacuum_table"
            )
    
    def reindex_table(self, table_name: str, schema: str = "public") -> PostgresQueryResult:
        """Reindex a PostgreSQL table"""
        try:
            import time
            start_time = time.time()
            
            reindex_cmd = f"REINDEX TABLE {schema}.{table_name}"
            
            cursor = self.connection.cursor()
            cursor.execute(reindex_cmd)
            
            execution_time = time.time() - start_time
            
            return PostgresQueryResult(
                success=True,
                message=f"REINDEX completed for {schema}.{table_name} in {execution_time:.3f}s",
                operation="reindex_table",
                execution_time=execution_time
            )
            
        except Exception as e:
            return PostgresQueryResult(
                success=False,
                message=f"REINDEX failed: {str(e)}",
                error=str(e),
                operation="reindex_table"
            )
    
    def backup_database(self, backup_path: str, format: str = "custom") -> PostgresQueryResult:
        """Backup PostgreSQL database using pg_dump"""
        try:
            import subprocess
            import time
            start_time = time.time()
            
            # Build pg_dump command
            cmd = [
                "pg_dump",
                f"--host={self.connection_config.host}",
                f"--port={self.connection_config.port}",
                f"--username={self.connection_config.username}",
                f"--dbname={self.connection_config.database}",
                f"--file={backup_path}"
            ]
            
            if format == "custom":
                cmd.append("--format=custom")
            elif format == "plain":
                cmd.append("--format=plain")
            elif format == "directory":
                cmd.append("--format=directory")
            
            # Set password environment variable if provided
            env = os.environ.copy()
            if self.connection_config.password:
                env["PGPASSWORD"] = self.connection_config.password
            
            # Execute pg_dump
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                return PostgresQueryResult(
                    success=True,
                    message=f"Database backed up to {backup_path} in {execution_time:.3f}s",
                    operation="backup_database",
                    execution_time=execution_time
                )
            else:
                return PostgresQueryResult(
                    success=False,
                    message=f"Backup failed: {result.stderr}",
                    error=result.stderr,
                    operation="backup_database",
                    execution_time=execution_time
                )
            
        except Exception as e:
            return PostgresQueryResult(
                success=False,
                message=f"Backup failed: {str(e)}",
                error=str(e),
                operation="backup_database"
            )
    
    def restore_database(self, backup_path: str) -> PostgresQueryResult:
        """Restore PostgreSQL database using pg_restore"""
        try:
            import subprocess
            import time
            start_time = time.time()
            
            # Build pg_restore command
            cmd = [
                "pg_restore",
                f"--host={self.connection_config.host}",
                f"--port={self.connection_config.port}",
                f"--username={self.connection_config.username}",
                f"--dbname={self.connection_config.database}",
                "--clean",  # Drop objects before recreating
                "--if-exists",  # Don't error if objects don't exist
                backup_path
            ]
            
            # Set password environment variable if provided
            env = os.environ.copy()
            if self.connection_config.password:
                env["PGPASSWORD"] = self.connection_config.password
            
            # Execute pg_restore
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                return PostgresQueryResult(
                    success=True,
                    message=f"Database restored from {backup_path} in {execution_time:.3f}s",
                    operation="restore_database",
                    execution_time=execution_time
                )
            else:
                return PostgresQueryResult(
                    success=False,
                    message=f"Restore failed: {result.stderr}",
                    error=result.stderr,
                    operation="restore_database",
                    execution_time=execution_time
                )
            
        except Exception as e:
            return PostgresQueryResult(
                success=False,
                message=f"Restore failed: {str(e)}",
                error=str(e),
                operation="restore_database"
            )
    
    def close(self):
        """Close PostgreSQL connection"""
        if self.connection:
            self.connection.close()


class PostgresToolsManager:
    """Manager class for PostgreSQL operations with CLI integration"""
    
    def __init__(self, connection_config: PostgresConnection):
        self.connection_config = connection_config
        self.postgres_tools = PostgresTools(connection_config)
        self.console = Console()
    
    def execute_query(self, query: str, params: Dict[str, Any] = None, format: str = "table") -> None:
        """Execute PostgreSQL query and display results"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Executing query...", total=None)
            result = self.postgres_tools.execute_query(query, params)
        
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
        """Execute PostgreSQL script and display results"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Executing script...", total=None)
            result = self.postgres_tools.execute_script(script)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            if result.rows_affected:
                self.console.print(f"📊 Total rows affected: {result.rows_affected}")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def show_table_info(self, table_name: str, schema: str = "public", format: str = "table") -> None:
        """Show detailed table information"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Getting table info...", total=None)
            result = self.postgres_tools.get_table_info(table_name, schema)
        
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
        # Summary table
        summary_table = Table(show_header=True, header_style="bold magenta", title=f"Table Summary: {table_info['schema']}.{table_info['name']}")
        summary_table.add_column("Property", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Schema", table_info['schema'])
        summary_table.add_row("Name", table_info['name'])
        summary_table.add_row("Row Count", f"{table_info['row_count']:,}")
        summary_table.add_row("Size", f"{table_info['size_bytes'] / 1024 / 1024:.2f} MB")
        summary_table.add_row("Index Count", str(table_info['index_count']))
        summary_table.add_row("Column Count", str(len(table_info['columns'])))
        
        if table_info['last_vacuum']:
            summary_table.add_row("Last Vacuum", table_info['last_vacuum'].strftime('%Y-%m-%d %H:%M:%S'))
        if table_info['last_analyze']:
            summary_table.add_row("Last Analyze", table_info['last_analyze'].strftime('%Y-%m-%d %H:%M:%S'))
        
        self.console.print(summary_table)
        
        # Columns table
        if table_info['columns']:
            columns_table = Table(show_header=True, header_style="bold blue", title="Columns")
            columns_table.add_column("Name", style="cyan")
            columns_table.add_column("Type", style="blue")
            columns_table.add_column("Nullable", style="yellow")
            columns_table.add_column("Default", style="red")
            
            for col in table_info['columns']:
                columns_table.add_row(
                    col['column_name'],
                    col['data_type'],
                    col['is_nullable'],
                    col['column_default'] or 'NULL'
                )
            
            self.console.print(columns_table)
        
        # Sample data table
        if table_info['sample_data']:
            sample_table = Table(show_header=True, header_style="bold green", title="Sample Data")
            
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
    
    def list_tables(self, schema: str = "public", format: str = "table") -> None:
        """List all tables in PostgreSQL database"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Listing tables...", total=None)
            result = self.postgres_tools.list_tables(schema)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            
            if format == "table":
                self._display_tables_list(result.data['tables'], schema)
            elif format == "json":
                self.console.print(json.dumps(result.data, indent=2))
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def _display_tables_list(self, tables: List[str], schema: str) -> None:
        """Display tables list in a table"""
        if not tables:
            self.console.print(f"[yellow]No tables found in schema '{schema}'[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta", title=f"Tables in Schema: {schema}")
        table.add_column("Table Name", style="cyan")
        table.add_column("Status", style="green")
        
        for table_name in tables:
            table.add_row(table_name, "✅ Active")
        
        self.console.print(table)
    
    def list_schemas(self, format: str = "table") -> None:
        """List all schemas in PostgreSQL database"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Listing schemas...", total=None)
            result = self.postgres_tools.list_schemas()
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            
            if format == "table":
                self._display_schemas_list(result.data['schemas'])
            elif format == "json":
                self.console.print(json.dumps(result.data, indent=2))
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def _display_schemas_list(self, schemas: List[str]) -> None:
        """Display schemas list in a table"""
        if not schemas:
            self.console.print("[yellow]No user schemas found[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta", title="Database Schemas")
        table.add_column("Schema Name", style="cyan")
        table.add_column("Status", style="green")
        
        for schema_name in schemas:
            table.add_row(schema_name, "✅ Active")
        
        self.console.print(table)
    
    def show_database_info(self, format: str = "table") -> None:
        """Show comprehensive database information"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Getting database info...", total=None)
            result = self.postgres_tools.get_database_info()
        
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
        
        info_table.add_row("Database", db_info['connection_info'].get('database_name', 'N/A'))
        info_table.add_row("User", db_info['connection_info'].get('username', 'N/A'))
        info_table.add_row("Host", db_info['connection_info'].get('host', 'N/A'))
        info_table.add_row("Port", str(db_info['connection_info'].get('port', 'N/A')))
        info_table.add_row("Version", db_info['connection_info'].get('version', 'N/A').split(',')[0])
        info_table.add_row("Schemas", str(db_info['schema_count']))
        info_table.add_row("Tables", str(db_info['table_count']))
        info_table.add_row("Size", f"{db_info['size_bytes'] / 1024 / 1024:.2f} MB")
        
        self.console.print(info_table)
        
        # Schemas list
        if db_info['schemas']:
            schemas_table = Table(show_header=True, header_style="bold blue", title="Schemas")
            schemas_table.add_column("Schema Name", style="cyan")
            
            for schema_name in db_info['schemas']:
                schemas_table.add_row(schema_name)
            
            self.console.print(schemas_table)
        
        # Tables list
        if db_info['tables']:
            tables_table = Table(show_header=True, header_style="bold green", title="Tables in Public Schema")
            tables_table.add_column("Table Name", style="cyan")
            
            for table_name in db_info['tables']:
                tables_table.add_row(table_name)
            
            self.console.print(tables_table)
    
    def show_index_info(self, table_name: str, schema: str = "public", format: str = "table") -> None:
        """Show index information for a table"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Getting index info...", total=None)
            result = self.postgres_tools.get_index_info(table_name, schema)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            
            if format == "table":
                self._display_index_info_table(result.data)
            elif format == "json":
                self.console.print(json.dumps(result.data, indent=2))
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def _display_index_info_table(self, indexes: List[Dict]) -> None:
        """Display index information in a table"""
        if not indexes:
            self.console.print("[yellow]No indexes found[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta", title="Table Indexes")
        table.add_column("Index Name", style="cyan")
        table.add_column("Type", style="blue")
        table.add_column("Columns", style="yellow")
        table.add_column("Unique", style="green")
        table.add_column("Size", style="red")
        
        for index in indexes:
            table.add_row(
                index['index_name'],
                index['index_type'],
                index['columns'],
                "Yes" if index['is_unique'] else "No",
                f"{index['size_bytes'] / 1024:.2f} KB"
            )
        
        self.console.print(table)
    
    def vacuum_table(self, table_name: str, schema: str = "public", full: bool = False, analyze: bool = True) -> None:
        """Vacuum a PostgreSQL table"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Vacuuming table...", total=None)
            result = self.postgres_tools.vacuum_table(table_name, schema, full, analyze)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def reindex_table(self, table_name: str, schema: str = "public") -> None:
        """Reindex a PostgreSQL table"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Reindexing table...", total=None)
            result = self.postgres_tools.reindex_table(table_name, schema)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def backup_database(self, backup_path: str, format: str = "custom") -> None:
        """Backup PostgreSQL database"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Backing up database...", total=None)
            result = self.postgres_tools.backup_database(backup_path, format)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def restore_database(self, backup_path: str) -> None:
        """Restore PostgreSQL database"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Restoring database...", total=None)
            result = self.postgres_tools.restore_database(backup_path)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def close(self):
        """Close database connection"""
        self.postgres_tools.close() 