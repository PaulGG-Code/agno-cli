"""
Function Tools - Dynamic Function Calling and Code Generation

This module provides dynamic function execution and code generation capabilities:
- Dynamic function creation and execution
- Code generation and templating
- Function composition and chaining
- Parameter validation and type checking
- Function registry and management
- Execution monitoring and logging
- Error handling and recovery
- Rich output formatting
- Multiple execution modes
- Advanced automation capabilities
"""

import os
import sys
import json
import time
import ast
import inspect
import traceback
import subprocess
import tempfile
from typing import Dict, List, Optional, Any, Tuple, Union, Callable, Type
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.syntax import Syntax
from rich.text import Text
from rich.markdown import Markdown
from rich.tree import Tree
from rich.align import Align
from rich.layout import Layout
import requests


class FunctionType(Enum):
    """Function types enumeration"""
    PYTHON = "python"
    SHELL = "shell"
    HTTP = "http"
    TEMPLATE = "template"
    COMPOSITE = "composite"
    GENERATOR = "generator"


class ExecutionMode(Enum):
    """Execution modes enumeration"""
    SYNC = "sync"
    ASYNC = "async"
    BATCH = "batch"
    STREAM = "stream"
    VALIDATE = "validate"


@dataclass
class FunctionParameter:
    """Function parameter definition"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None
    validator: Optional[str] = None
    example: Optional[str] = None


@dataclass
class FunctionDefinition:
    """Function definition"""
    id: str
    name: str
    description: str
    function_type: str
    parameters: List[FunctionParameter]
    return_type: str
    code: str
    dependencies: List[str]
    tags: List[str]
    created_at: str
    updated_at: str
    version: str = "1.0.0"
    author: Optional[str] = None
    examples: List[str] = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []


@dataclass
class FunctionExecution:
    """Function execution result"""
    id: str
    function_id: str
    function_name: str
    parameters: Dict[str, Any]
    result: Any
    execution_time: float
    status: str  # success, error, timeout
    error_message: Optional[str] = None
    logs: List[str] = None
    metadata: Dict[str, Any] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.logs is None:
            self.logs = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class FunctionTemplate:
    """Function template"""
    id: str
    name: str
    description: str
    template_type: str
    template_code: str
    variables: List[str]
    examples: List[Dict[str, Any]]
    created_at: str


@dataclass
class FunctionChain:
    """Function composition chain"""
    id: str
    name: str
    description: str
    functions: List[str]  # List of function IDs
    data_flow: Dict[str, str]  # Mapping of output to input parameters
    error_handling: Dict[str, str]  # Error handling strategy for each function
    created_at: str


class FunctionTools:
    """Core function calling and code generation tools"""
    
    def __init__(self):
        self.console = Console()
        self.functions_dir = Path("functions")
        self.functions_dir.mkdir(exist_ok=True)
        
        self.executions_dir = Path("function_executions")
        self.executions_dir.mkdir(exist_ok=True)
        
        self.templates_dir = Path("function_templates")
        self.templates_dir.mkdir(exist_ok=True)
        
        # Function registry
        self.function_registry: Dict[str, FunctionDefinition] = {}
        self.execution_history: List[FunctionExecution] = []
        
        # Built-in function templates
        self.builtin_templates = {
            'data_processor': {
                'name': 'Data Processor',
                'description': 'Process data with configurable operations',
                'template_code': '''
def process_data(data, operation="filter", **kwargs):
    """Process data with specified operation"""
    if operation == "filter":
        return [item for item in data if kwargs.get('condition', lambda x: True)(item)]
    elif operation == "map":
        return [kwargs.get('transform', lambda x: x)(item) for item in data]
    elif operation == "reduce":
        from functools import reduce
        return reduce(kwargs.get('reducer', lambda x, y: x + y), data)
    else:
        raise ValueError(f"Unknown operation: {operation}")
''',
                'variables': ['data', 'operation', 'condition', 'transform', 'reducer']
            },
            'http_client': {
                'name': 'HTTP Client',
                'description': 'Make HTTP requests with configurable options',
                'template_code': '''
import requests

def make_request(url, method="GET", headers=None, data=None, **kwargs):
    """Make HTTP request with specified parameters"""
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers or {},
            data=data,
            timeout=kwargs.get('timeout', 30),
            **kwargs
        )
        response.raise_for_status()
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'data': response.text,
            'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
        }
    except Exception as e:
        return {'error': str(e)}
''',
                'variables': ['url', 'method', 'headers', 'data', 'timeout']
            },
            'file_processor': {
                'name': 'File Processor',
                'description': 'Process files with various operations',
                'template_code': '''
import os
from pathlib import Path

def process_file(file_path, operation="read", **kwargs):
    """Process file with specified operation"""
    file_path = Path(file_path)
    
    if operation == "read":
        encoding = kwargs.get('encoding', 'utf-8')
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    elif operation == "write":
        content = kwargs.get('content', '')
        encoding = kwargs.get('encoding', 'utf-8')
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return f"File written: {file_path}"
    elif operation == "append":
        content = kwargs.get('content', '')
        encoding = kwargs.get('encoding', 'utf-8')
        with open(file_path, 'a', encoding=encoding) as f:
            f.write(content)
        return f"Content appended to: {file_path}"
    elif operation == "info":
        stat = file_path.stat()
        return {
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'exists': file_path.exists(),
            'is_file': file_path.is_file(),
            'is_dir': file_path.is_dir()
        }
    else:
        raise ValueError(f"Unknown operation: {operation}")
''',
                'variables': ['file_path', 'operation', 'content', 'encoding']
            },
            'data_validator': {
                'name': 'Data Validator',
                'description': 'Validate data against schemas and rules',
                'template_code': '''
def validate_data(data, schema=None, rules=None, **kwargs):
    """Validate data against schema and rules"""
    errors = []
    
    if schema:
        # Basic schema validation
        if isinstance(schema, dict):
            for key, expected_type in schema.items():
                if key in data:
                    if not isinstance(data[key], expected_type):
                        errors.append(f"Field '{key}' should be {expected_type.__name__}")
                elif kwargs.get('strict', False):
                    errors.append(f"Required field '{key}' missing")
    
    if rules:
        # Custom validation rules
        for rule_name, rule_func in rules.items():
            try:
                if not rule_func(data):
                    errors.append(f"Rule '{rule_name}' failed")
            except Exception as e:
                errors.append(f"Rule '{rule_name}' error: {e}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'data': data
    }
''',
                'variables': ['data', 'schema', 'rules', 'strict']
            }
        }
        
        # Load existing functions
        self._load_functions()
    
    def _load_functions(self):
        """Load existing functions from storage"""
        for func_file in self.functions_dir.glob("*.json"):
            try:
                with open(func_file, 'r') as f:
                    data = json.load(f)
                
                # Reconstruct parameters
                parameters = [FunctionParameter(**param) for param in data.get('parameters', [])]
                
                func_def = FunctionDefinition(
                    id=data['id'],
                    name=data['name'],
                    description=data['description'],
                    function_type=data['function_type'],
                    parameters=parameters,
                    return_type=data['return_type'],
                    code=data['code'],
                    dependencies=data.get('dependencies', []),
                    tags=data.get('tags', []),
                    created_at=data['created_at'],
                    updated_at=data['updated_at'],
                    version=data.get('version', '1.0.0'),
                    author=data.get('author'),
                    examples=data.get('examples', [])
                )
                
                self.function_registry[func_def.id] = func_def
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load function {func_file}: {e}[/yellow]")
    
    def create_function(self, name: str, description: str, code: str,
                       parameters: List[Dict[str, Any]], return_type: str = "Any",
                       function_type: str = "python", tags: List[str] = None,
                       dependencies: List[str] = None, author: Optional[str] = None) -> FunctionDefinition:
        """Create a new function definition"""
        func_id = self._generate_function_id(name)
        
        # Convert parameter dictionaries to FunctionParameter objects
        func_params = []
        for param in parameters:
            func_params.append(FunctionParameter(
                name=param['name'],
                type=param.get('type', 'Any'),
                description=param.get('description', ''),
                required=param.get('required', True),
                default=param.get('default'),
                validator=param.get('validator'),
                example=param.get('example')
            ))
        
        func_def = FunctionDefinition(
            id=func_id,
            name=name,
            description=description,
            function_type=function_type,
            parameters=func_params,
            return_type=return_type,
            code=code,
            dependencies=dependencies or [],
            tags=tags or [],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            author=author
        )
        
        # Save function
        self._save_function(func_def)
        self.function_registry[func_id] = func_def
        
        return func_def
    
    def _generate_function_id(self, name: str) -> str:
        """Generate unique function ID"""
        import hashlib
        timestamp = str(time.time())
        return hashlib.md5(f"{name}_{timestamp}".encode()).hexdigest()[:8]
    
    def _save_function(self, func_def: FunctionDefinition) -> bool:
        """Save function definition to file"""
        try:
            func_file = self.functions_dir / f"{func_def.id}.json"
            with open(func_file, 'w') as f:
                json.dump(asdict(func_def), f, indent=2, default=str)
            return True
        except Exception as e:
            self.console.print(f"[red]Error saving function: {e}[/red]")
            return False
    
    def execute_function(self, function_id: str, parameters: Dict[str, Any],
                        execution_mode: str = "sync", timeout: int = 30) -> FunctionExecution:
        """Execute a function with given parameters"""
        if function_id not in self.function_registry:
            raise ValueError(f"Function not found: {function_id}")
        
        func_def = self.function_registry[function_id]
        execution_id = self._generate_execution_id(function_id)
        
        start_time = time.time()
        result = None
        status = "success"
        error_message = None
        logs = []
        
        try:
            # Validate parameters
            self._validate_parameters(func_def, parameters)
            
            # Execute based on function type
            if func_def.function_type == "python":
                result = self._execute_python_function(func_def, parameters, logs)
            elif func_def.function_type == "shell":
                result = self._execute_shell_function(func_def, parameters, logs, timeout)
            elif func_def.function_type == "http":
                result = self._execute_http_function(func_def, parameters, logs, timeout)
            elif func_def.function_type == "template":
                result = self._execute_template_function(func_def, parameters, logs)
            else:
                raise ValueError(f"Unsupported function type: {func_def.function_type}")
            
        except Exception as e:
            status = "error"
            error_message = str(e)
            logs.append(f"ERROR: {error_message}")
            logs.extend(traceback.format_exc().split('\n'))
        
        execution_time = time.time() - start_time
        
        execution = FunctionExecution(
            id=execution_id,
            function_id=function_id,
            function_name=func_def.name,
            parameters=parameters,
            result=result,
            execution_time=execution_time,
            status=status,
            error_message=error_message,
            logs=logs
        )
        
        # Save execution
        self._save_execution(execution)
        self.execution_history.append(execution)
        
        return execution
    
    def _validate_parameters(self, func_def: FunctionDefinition, parameters: Dict[str, Any]):
        """Validate function parameters"""
        for param in func_def.parameters:
            if param.required and param.name not in parameters:
                raise ValueError(f"Required parameter missing: {param.name}")
            
            if param.name in parameters:
                value = parameters[param.name]
                
                # Type validation
                if param.type != "Any":
                    expected_type = self._get_python_type(param.type)
                    if not isinstance(value, expected_type):
                        raise ValueError(f"Parameter '{param.name}' should be {param.type}, got {type(value).__name__}")
                
                # Custom validation
                if param.validator:
                    if not self._evaluate_validator(param.validator, value):
                        raise ValueError(f"Parameter '{param.name}' failed validation: {param.validator}")
    
    def _get_python_type(self, type_name: str) -> Type:
        """Get Python type from string"""
        type_map = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'Any': object
        }
        return type_map.get(type_name, object)
    
    def _evaluate_validator(self, validator: str, value: Any) -> bool:
        """Evaluate custom validator expression"""
        try:
            # Create a safe evaluation context
            context = {'value': value, 'len': len, 'isinstance': isinstance}
            return eval(validator, {"__builtins__": {}}, context)
        except Exception:
            return False
    
    def _execute_python_function(self, func_def: FunctionDefinition, parameters: Dict[str, Any], logs: List[str]) -> Any:
        """Execute Python function"""
        # Create execution namespace
        namespace = {}
        
        # Add dependencies
        for dep in func_def.dependencies:
            try:
                exec(f"import {dep}", namespace)
                logs.append(f"Imported dependency: {dep}")
            except ImportError as e:
                logs.append(f"Warning: Could not import {dep}: {e}")
        
        # Execute function code
        exec(func_def.code, namespace)
        
        # Get function object
        func_name = func_def.name
        if func_name not in namespace:
            # Try to find function in code
            tree = ast.parse(func_def.code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    break
        
        if func_name not in namespace:
            raise ValueError(f"Function '{func_name}' not found in code")
        
        func = namespace[func_name]
        logs.append(f"Executing function: {func_name}")
        
        # Execute function
        result = func(**parameters)
        logs.append(f"Function executed successfully")
        
        return result
    
    def _execute_shell_function(self, func_def: FunctionDefinition, parameters: Dict[str, Any], logs: List[str], timeout: int) -> str:
        """Execute shell function"""
        # Extract command from code
        command = func_def.code.strip()
        
        # Substitute parameters
        for key, value in parameters.items():
            command = command.replace(f"{{{key}}}", str(value))
        
        logs.append(f"Executing shell command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                logs.append("Shell command executed successfully")
                return result.stdout
            else:
                raise Exception(f"Shell command failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception(f"Shell command timed out after {timeout} seconds")
    
    def _execute_http_function(self, func_def: FunctionDefinition, parameters: Dict[str, Any], logs: List[str], timeout: int) -> Dict[str, Any]:
        """Execute HTTP function"""
        # Parse HTTP request from code
        # This is a simplified implementation
        url = parameters.get('url', '')
        method = parameters.get('method', 'GET')
        headers = parameters.get('headers', {})
        data = parameters.get('data')
        
        logs.append(f"Making HTTP {method} request to: {url}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                timeout=timeout
            )
            
            logs.append(f"HTTP request completed with status: {response.status_code}")
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response.text,
                'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            }
            
        except Exception as e:
            raise Exception(f"HTTP request failed: {e}")
    
    def _execute_template_function(self, func_def: FunctionDefinition, parameters: Dict[str, Any], logs: List[str]) -> str:
        """Execute template function"""
        template = func_def.code
        
        # Substitute parameters in template
        for key, value in parameters.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        logs.append("Template processed successfully")
        return template
    
    def _generate_execution_id(self, function_id: str) -> str:
        """Generate unique execution ID"""
        import hashlib
        timestamp = str(time.time())
        return hashlib.md5(f"{function_id}_{timestamp}".encode()).hexdigest()[:8]
    
    def _save_execution(self, execution: FunctionExecution) -> bool:
        """Save execution result to file"""
        try:
            exec_file = self.executions_dir / f"{execution.id}.json"
            with open(exec_file, 'w') as f:
                json.dump(asdict(execution), f, indent=2, default=str)
            return True
        except Exception as e:
            self.console.print(f"[red]Error saving execution: {e}[/red]")
            return False
    
    def get_function(self, function_id: str) -> Optional[FunctionDefinition]:
        """Get function definition by ID"""
        return self.function_registry.get(function_id)
    
    def list_functions(self, function_type: Optional[str] = None, tag: Optional[str] = None) -> List[FunctionDefinition]:
        """List functions with optional filtering"""
        functions = list(self.function_registry.values())
        
        if function_type:
            functions = [f for f in functions if f.function_type == function_type]
        
        if tag:
            functions = [f for f in functions if tag in f.tags]
        
        return sorted(functions, key=lambda x: x.updated_at, reverse=True)
    
    def delete_function(self, function_id: str) -> bool:
        """Delete function by ID"""
        if function_id not in self.function_registry:
            return False
        
        try:
            # Remove from registry
            del self.function_registry[function_id]
            
            # Delete file
            func_file = self.functions_dir / f"{function_id}.json"
            if func_file.exists():
                func_file.unlink()
            
            return True
        except Exception as e:
            self.console.print(f"[red]Error deleting function: {e}[/red]")
            return False
    
    def create_template(self, name: str, description: str, template_code: str,
                       variables: List[str], examples: List[Dict[str, Any]] = None) -> FunctionTemplate:
        """Create a function template"""
        template_id = self._generate_function_id(name)
        
        template = FunctionTemplate(
            id=template_id,
            name=name,
            description=description,
            template_type="python",
            template_code=template_code,
            variables=variables,
            examples=examples or [],
            created_at=datetime.now().isoformat()
        )
        
        # Save template
        self._save_template(template)
        
        return template
    
    def _save_template(self, template: FunctionTemplate) -> bool:
        """Save template to file"""
        try:
            template_file = self.templates_dir / f"{template.id}.json"
            with open(template_file, 'w') as f:
                json.dump(asdict(template), f, indent=2, default=str)
            return True
        except Exception as e:
            self.console.print(f"[red]Error saving template: {e}[/red]")
            return False
    
    def list_templates(self) -> List[FunctionTemplate]:
        """List all templates"""
        templates = []
        
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    data = json.load(f)
                
                template = FunctionTemplate(**data)
                templates.append(template)
            except Exception:
                continue
        
        return sorted(templates, key=lambda x: x.created_at, reverse=True)
    
    def create_function_from_template(self, template_id: str, name: str, description: str,
                                    parameters: List[Dict[str, Any]], **kwargs) -> FunctionDefinition:
        """Create function from template"""
        # Find template
        templates = self.list_templates()
        template = next((t for t in templates if t.id == template_id), None)
        
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Generate code from template
        code = template.template_code
        
        # Create function
        return self.create_function(
            name=name,
            description=description,
            code=code,
            parameters=parameters,
            **kwargs
        )
    
    def get_execution_history(self, function_id: Optional[str] = None, limit: int = 50) -> List[FunctionExecution]:
        """Get execution history"""
        history = self.execution_history.copy()
        
        if function_id:
            history = [e for e in history if e.function_id == function_id]
        
        return sorted(history, key=lambda x: x.created_at, reverse=True)[:limit]


class FunctionToolsManager:
    """CLI integration for function tools"""
    
    def __init__(self):
        self.function_tools = FunctionTools()
        self.console = Console()
    
    def create_function(self, name: str, description: str, code: str,
                       parameters: List[Dict[str, Any]], return_type: str = "Any",
                       function_type: str = "python", tags: List[str] = None,
                       dependencies: List[str] = None, author: Optional[str] = None,
                       format: str = "table") -> None:
        """Create a new function"""
        try:
            func_def = self.function_tools.create_function(
                name=name,
                description=description,
                code=code,
                parameters=parameters,
                return_type=return_type,
                function_type=function_type,
                tags=tags or [],
                dependencies=dependencies or [],
                author=author
            )
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(func_def), indent=2, default=str))
            else:
                func_panel = Panel(
                    f"[bold blue]Function ID:[/bold blue] {func_def.id}\n"
                    f"[bold green]Name:[/bold green] {func_def.name}\n"
                    f"[bold yellow]Type:[/bold yellow] {func_def.function_type}\n"
                    f"[bold white]Description:[/bold white] {func_def.description}\n"
                    f"[bold cyan]Parameters:[/bold cyan] {len(func_def.parameters)}\n"
                    f"[bold magenta]Tags:[/bold magenta] {', '.join(func_def.tags)}",
                    title="Function Created",
                    border_style="green"
                )
                self.console.print(func_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error creating function: {e}[/red]")
    
    def execute_function(self, function_id: str, parameters: Dict[str, Any],
                        execution_mode: str = "sync", timeout: int = 30,
                        format: str = "table") -> None:
        """Execute a function"""
        try:
            execution = self.function_tools.execute_function(
                function_id=function_id,
                parameters=parameters,
                execution_mode=execution_mode,
                timeout=timeout
            )
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(execution), indent=2, default=str))
            else:
                # Show execution result
                result_panel = Panel(
                    f"[bold blue]Execution ID:[/bold blue] {execution.id}\n"
                    f"[bold green]Function:[/bold green] {execution.function_name}\n"
                    f"[bold yellow]Status:[/bold yellow] {execution.status}\n"
                    f"[bold white]Execution Time:[/bold white] {execution.execution_time:.3f}s",
                    title="Function Execution Result",
                    border_style="green" if execution.status == "success" else "red"
                )
                self.console.print(result_panel)
                
                # Show result
                if execution.status == "success":
                    result_text = str(execution.result)
                    if len(result_text) > 500:
                        result_text = result_text[:500] + "..."
                    
                    result_panel = Panel(
                        result_text,
                        title="Result",
                        border_style="blue"
                    )
                    self.console.print(result_panel)
                else:
                    error_panel = Panel(
                        execution.error_message or "Unknown error",
                        title="Error",
                        border_style="red"
                    )
                    self.console.print(error_panel)
                
                # Show logs if any
                if execution.logs:
                    logs_panel = Panel(
                        "\n".join(execution.logs),
                        title="Execution Logs",
                        border_style="yellow"
                    )
                    self.console.print(logs_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error executing function: {e}[/red]")
    
    def list_functions(self, function_type: Optional[str] = None, tag: Optional[str] = None,
                      format: str = "table") -> None:
        """List functions"""
        try:
            functions = self.function_tools.list_functions(function_type, tag)
            
            if format == "json":
                import json
                self.console.print(json.dumps([asdict(f) for f in functions], indent=2, default=str))
            else:
                if not functions:
                    self.console.print("[yellow]No functions found[/yellow]")
                    return
                
                functions_table = Table(title="Functions")
                functions_table.add_column("ID", style="cyan")
                functions_table.add_column("Name", style="white")
                functions_table.add_column("Type", style="blue")
                functions_table.add_column("Description", style="green")
                functions_table.add_column("Parameters", style="yellow")
                functions_table.add_column("Tags", style="magenta")
                functions_table.add_column("Updated", style="red")
                
                for func in functions:
                    functions_table.add_row(
                        func.id,
                        func.name,
                        func.function_type,
                        func.description[:50] + "..." if len(func.description) > 50 else func.description,
                        str(len(func.parameters)),
                        ", ".join(func.tags[:3]) + "..." if len(func.tags) > 3 else ", ".join(func.tags),
                        func.updated_at[:10]
                    )
                
                self.console.print(functions_table)
                
        except Exception as e:
            self.console.print(f"[red]Error listing functions: {e}[/red]")
    
    def show_function(self, function_id: str, format: str = "table") -> None:
        """Show function details"""
        try:
            func = self.function_tools.get_function(function_id)
            if not func:
                self.console.print(f"[red]Function not found: {function_id}[/red]")
                return
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(func), indent=2, default=str))
            else:
                # Show function overview
                overview_table = Table(title=f"Function: {func.name}")
                overview_table.add_column("Property", style="cyan")
                overview_table.add_column("Value", style="white")
                
                overview_table.add_row("ID", func.id)
                overview_table.add_row("Name", func.name)
                overview_table.add_row("Type", func.function_type)
                overview_table.add_row("Description", func.description)
                overview_table.add_row("Return Type", func.return_type)
                overview_table.add_row("Version", func.version)
                overview_table.add_row("Author", func.author or "Unknown")
                overview_table.add_row("Created", func.created_at)
                overview_table.add_row("Updated", func.updated_at)
                overview_table.add_row("Dependencies", ", ".join(func.dependencies))
                overview_table.add_row("Tags", ", ".join(func.tags))
                
                self.console.print(overview_table)
                
                # Show parameters
                if func.parameters:
                    params_table = Table(title="Parameters")
                    params_table.add_column("Name", style="cyan")
                    params_table.add_column("Type", style="blue")
                    params_table.add_column("Required", style="green")
                    params_table.add_column("Default", style="yellow")
                    params_table.add_column("Description", style="white")
                    
                    for param in func.parameters:
                        params_table.add_row(
                            param.name,
                            param.type,
                            str(param.required),
                            str(param.default) if param.default is not None else "None",
                            param.description
                        )
                    
                    self.console.print(params_table)
                
                # Show code
                code_panel = Panel(
                    Syntax(func.code, "python", theme="monokai"),
                    title="Function Code",
                    border_style="blue"
                )
                self.console.print(code_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error showing function: {e}[/red]")
    
    def delete_function(self, function_id: str) -> None:
        """Delete function"""
        try:
            success = self.function_tools.delete_function(function_id)
            if success:
                self.console.print(f"[green]Function deleted: {function_id}[/green]")
            else:
                self.console.print(f"[red]Function not found: {function_id}[/red]")
        except Exception as e:
            self.console.print(f"[red]Error deleting function: {e}[/red]")
    
    def list_templates(self, format: str = "table") -> None:
        """List function templates"""
        try:
            templates = self.function_tools.list_templates()
            
            if format == "json":
                import json
                self.console.print(json.dumps([asdict(t) for t in templates], indent=2, default=str))
            else:
                if not templates:
                    self.console.print("[yellow]No templates found[/yellow]")
                    return
                
                templates_table = Table(title="Function Templates")
                templates_table.add_column("ID", style="cyan")
                templates_table.add_column("Name", style="white")
                templates_table.add_column("Description", style="blue")
                templates_table.add_column("Variables", style="green")
                templates_table.add_column("Examples", style="yellow")
                templates_table.add_column("Created", style="red")
                
                for template in templates:
                    templates_table.add_row(
                        template.id,
                        template.name,
                        template.description[:50] + "..." if len(template.description) > 50 else template.description,
                        str(len(template.variables)),
                        str(len(template.examples)),
                        template.created_at[:10]
                    )
                
                self.console.print(templates_table)
                
        except Exception as e:
            self.console.print(f"[red]Error listing templates: {e}[/red]")
    
    def list_builtin_templates(self, format: str = "table") -> None:
        """List built-in templates"""
        try:
            templates = self.function_tools.builtin_templates
            
            if format == "json":
                import json
                self.console.print(json.dumps(templates, indent=2))
            else:
                templates_table = Table(title="Built-in Templates")
                templates_table.add_column("ID", style="cyan")
                templates_table.add_column("Name", style="white")
                templates_table.add_column("Description", style="blue")
                templates_table.add_column("Variables", style="green")
                
                for template_id, template in templates.items():
                    templates_table.add_row(
                        template_id,
                        template['name'],
                        template['description'],
                        str(len(template['variables']))
                    )
                
                self.console.print(templates_table)
                
        except Exception as e:
            self.console.print(f"[red]Error listing built-in templates: {e}[/red]")
    
    def get_execution_history(self, function_id: Optional[str] = None, limit: int = 20,
                            format: str = "table") -> None:
        """Get execution history"""
        try:
            history = self.function_tools.get_execution_history(function_id, limit)
            
            if format == "json":
                import json
                self.console.print(json.dumps([asdict(e) for e in history], indent=2, default=str))
            else:
                if not history:
                    self.console.print("[yellow]No execution history found[/yellow]")
                    return
                
                history_table = Table(title="Execution History")
                history_table.add_column("ID", style="cyan")
                history_table.add_column("Function", style="white")
                history_table.add_column("Status", style="blue")
                history_table.add_column("Execution Time", style="green")
                history_table.add_column("Created", style="yellow")
                
                for execution in history:
                    status_color = "green" if execution.status == "success" else "red"
                    history_table.add_row(
                        execution.id,
                        execution.function_name,
                        f"[{status_color}]{execution.status}[/{status_color}]",
                        f"{execution.execution_time:.3f}s",
                        execution.created_at[:19]
                    )
                
                self.console.print(history_table)
                
        except Exception as e:
            self.console.print(f"[red]Error getting execution history: {e}[/red]") 