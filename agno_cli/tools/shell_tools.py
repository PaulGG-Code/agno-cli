"""
Shell Tools - System Command Execution

This module provides safe system command execution capabilities with:
- Command validation and safety checks
- Rich output formatting
- Command history tracking
- Process management
- Security features
"""

import os
import sys
import subprocess
import shlex
import time
import signal
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import threading
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.syntax import Syntax
import psutil


@dataclass
class ShellCommandResult:
    """Result of a shell command execution"""
    command: str
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    success: bool
    pid: Optional[int] = None
    killed: bool = False


@dataclass
class ShellCommand:
    """Shell command configuration"""
    command: str
    timeout: int = 30
    cwd: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    shell: bool = False
    capture_output: bool = True


class ShellTools:
    """Core shell command execution tools"""
    
    def __init__(self):
        self.console = Console()
        self.command_history: List[ShellCommandResult] = []
        self.max_history = 100
        self.dangerous_commands = {
            'rm -rf /', 'rm -rf /*', 'dd if=/dev/zero', 'mkfs', 'fdisk',
            'shutdown', 'reboot', 'halt', 'poweroff', 'init 0', 'init 6'
        }
        self.allowed_commands = {
            'ls', 'cat', 'head', 'tail', 'grep', 'find', 'ps', 'top',
            'df', 'du', 'free', 'uptime', 'who', 'w', 'last', 'history',
            'pwd', 'cd', 'mkdir', 'rmdir', 'cp', 'mv', 'ln', 'chmod',
            'chown', 'tar', 'gzip', 'gunzip', 'zip', 'unzip', 'curl',
            'wget', 'ssh', 'scp', 'rsync', 'git', 'docker', 'kubectl',
            'python', 'pip', 'node', 'npm', 'java', 'mvn', 'gradle'
        }
    
    def _is_dangerous_command(self, command: str) -> bool:
        """Check if command is potentially dangerous"""
        command_lower = command.lower().strip()
        
        # Check for dangerous patterns
        for dangerous in self.dangerous_commands:
            if dangerous in command_lower:
                return True
        
        # Check for dangerous patterns
        dangerous_patterns = [
            'rm -rf', 'dd if=', 'mkfs', 'fdisk', 'shutdown', 'reboot',
            'halt', 'poweroff', 'init 0', 'init 6', '> /dev/sd',
            '> /dev/hd', '> /dev/zero', '> /dev/null'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return True
        
        return False
    
    def _is_allowed_command(self, command: str) -> bool:
        """Check if command is in allowed list"""
        if not command.strip():
            return False
        
        # Extract the first word (command name)
        parts = shlex.split(command)
        if not parts:
            return False
        
        command_name = parts[0].lower()
        
        # Check if it's in allowed commands
        if command_name in self.allowed_commands:
            return True
        
        # Allow commands with full paths
        if command_name.startswith('/') or command_name.startswith('./'):
            return True
        
        # Allow commands in PATH
        try:
            result = subprocess.run(['which', command_name], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _validate_command(self, command: str) -> Tuple[bool, str]:
        """Validate command for safety"""
        if not command.strip():
            return False, "Empty command"
        
        if self._is_dangerous_command(command):
            return False, f"Dangerous command detected: {command}"
        
        if not self._is_allowed_command(command):
            return False, f"Command not in allowed list: {command}"
        
        return True, "Command is safe"
    
    def execute_command(self, command: str, timeout: int = 30, 
                       cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None,
                       shell: bool = False) -> ShellCommandResult:
        """Execute a shell command safely"""
        start_time = time.time()
        
        # Validate command
        is_valid, error_msg = self._validate_command(command)
        if not is_valid:
            return ShellCommandResult(
                command=command,
                return_code=1,
                stdout="",
                stderr=f"Command validation failed: {error_msg}",
                execution_time=time.time() - start_time,
                success=False
            )
        
        try:
            # Prepare environment
            process_env = os.environ.copy()
            if env:
                process_env.update(env)
            
            # Execute command
            if shell:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=cwd,
                    env=process_env,
                    preexec_fn=os.setsid if os.name != 'nt' else None
                )
            else:
                args = shlex.split(command)
                process = subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=cwd,
                    env=process_env
                )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                killed = False
            except subprocess.TimeoutExpired:
                # Kill the process group
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    else:
                        process.kill()
                
                stdout, stderr = process.communicate()
                return_code = -1
                killed = True
            
            execution_time = time.time() - start_time
            
            result = ShellCommandResult(
                command=command,
                return_code=return_code,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                success=return_code == 0,
                pid=process.pid,
                killed=killed
            )
            
            # Add to history
            self.command_history.append(result)
            if len(self.command_history) > self.max_history:
                self.command_history.pop(0)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ShellCommandResult(
                command=command,
                return_code=1,
                stdout="",
                stderr=f"Command execution failed: {str(e)}",
                execution_time=execution_time,
                success=False
            )
    
    def execute_command_live(self, command: str, timeout: int = 30,
                           cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None,
                           shell: bool = False) -> ShellCommandResult:
        """Execute command with live output display"""
        start_time = time.time()
        
        # Validate command
        is_valid, error_msg = self._validate_command(command)
        if not is_valid:
            return ShellCommandResult(
                command=command,
                return_code=1,
                stdout="",
                stderr=f"Command validation failed: {error_msg}",
                execution_time=time.time() - start_time,
                success=False
            )
        
        try:
            # Prepare environment
            process_env = os.environ.copy()
            if env:
                process_env.update(env)
            
            # Execute command
            if shell:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=cwd,
                    env=process_env,
                    bufsize=1,
                    universal_newlines=True,
                    preexec_fn=os.setsid if os.name != 'nt' else None
                )
            else:
                args = shlex.split(command)
                process = subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=cwd,
                    env=process_env,
                    bufsize=1,
                    universal_newlines=True
                )
            
            stdout_lines = []
            stderr_lines = []
            
            # Display live output
            with Live(Panel("Executing command...", title="Shell Command"), 
                     refresh_per_second=10) as live:
                
                while True:
                    # Read stdout
                    stdout_line = process.stdout.readline()
                    if stdout_line:
                        stdout_lines.append(stdout_line)
                        live.update(Panel(
                            f"[green]STDOUT:[/green] {stdout_line.strip()}\n" +
                            f"[red]STDERR:[/red] {''.join(stderr_lines[-5:])}",
                            title=f"Shell Command - {command}"
                        ))
                    
                    # Read stderr
                    stderr_line = process.stderr.readline()
                    if stderr_line:
                        stderr_lines.append(stderr_line)
                        live.update(Panel(
                            f"[green]STDOUT:[/green] {''.join(stdout_lines[-5:])}\n" +
                            f"[red]STDERR:[/red] {stderr_line.strip()}",
                            title=f"Shell Command - {command}"
                        ))
                    
                    # Check if process is still running
                    if process.poll() is not None:
                        break
                    
                    # Check timeout
                    if time.time() - start_time > timeout:
                        if os.name != 'nt':
                            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        else:
                            process.terminate()
                        break
                    
                    time.sleep(0.1)
                
                # Read any remaining output
                remaining_stdout, remaining_stderr = process.communicate()
                stdout_lines.extend(remaining_stdout.splitlines())
                stderr_lines.extend(remaining_stderr.splitlines())
            
            execution_time = time.time() - start_time
            
            result = ShellCommandResult(
                command=command,
                return_code=process.returncode,
                stdout='\n'.join(stdout_lines),
                stderr='\n'.join(stderr_lines),
                execution_time=execution_time,
                success=process.returncode == 0,
                pid=process.pid,
                killed=execution_time > timeout
            )
            
            # Add to history
            self.command_history.append(result)
            if len(self.command_history) > self.max_history:
                self.command_history.pop(0)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ShellCommandResult(
                command=command,
                return_code=1,
                stdout="",
                stderr=f"Command execution failed: {str(e)}",
                execution_time=execution_time,
                success=False
            )
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        info = {}
        
        try:
            # OS information
            info['os'] = {
                'name': os.name,
                'platform': sys.platform,
                'version': os.uname().release if hasattr(os, 'uname') else 'Unknown'
            }
            
            # CPU information
            info['cpu'] = {
                'count': os.cpu_count(),
                'usage': psutil.cpu_percent(interval=1)
            }
            
            # Memory information
            memory = psutil.virtual_memory()
            info['memory'] = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            }
            
            # Disk information
            disk = psutil.disk_usage('/')
            info['disk'] = {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
            
            # Network information
            network = psutil.net_io_counters()
            info['network'] = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # Process information
            info['processes'] = {
                'total': len(psutil.pids()),
                'running': len([p for p in psutil.process_iter() if p.status() == 'running'])
            }
            
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def get_process_info(self, pid: Optional[int] = None) -> Dict[str, Any]:
        """Get process information"""
        if pid is None:
            pid = os.getpid()
        
        try:
            process = psutil.Process(pid)
            return {
                'pid': process.pid,
                'name': process.name(),
                'cmdline': process.cmdline(),
                'status': process.status(),
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'memory_info': process.memory_info()._asdict(),
                'create_time': process.create_time(),
                'num_threads': process.num_threads(),
                'connections': [conn._asdict() for conn in process.connections()],
                'open_files': [f._asdict() for f in process.open_files()],
                'num_fds': process.num_fds() if hasattr(process, 'num_fds') else None
            }
        except Exception as e:
            return {'error': str(e)}
    
    def kill_process(self, pid: int, signal_type: str = 'SIGTERM') -> bool:
        """Kill a process"""
        try:
            process = psutil.Process(pid)
            
            if signal_type == 'SIGTERM':
                process.terminate()
            elif signal_type == 'SIGKILL':
                process.kill()
            else:
                process.send_signal(getattr(signal, signal_type))
            
            return True
        except Exception:
            return False
    
    def get_command_history(self, limit: Optional[int] = None) -> List[ShellCommandResult]:
        """Get command history"""
        if limit is None:
            return self.command_history.copy()
        return self.command_history[-limit:]
    
    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()


class ShellToolsManager:
    """CLI integration for shell tools"""
    
    def __init__(self):
        self.shell_tools = ShellTools()
        self.console = Console()
    
    def execute_command(self, command: str, timeout: int = 30, 
                       cwd: Optional[str] = None, live: bool = False,
                       format: str = "table") -> None:
        """Execute a shell command and display results"""
        self.console.print(f"[bold blue]Executing:[/bold blue] {command}")
        
        if live:
            result = self.shell_tools.execute_command_live(command, timeout, cwd)
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Executing command...", total=None)
                result = self.shell_tools.execute_command(command, timeout, cwd)
        
        self._display_result(result, format)
    
    def _display_result(self, result: ShellCommandResult, format: str = "table"):
        """Display command execution result"""
        if format == "json":
            import json
            self.console.print(json.dumps({
                'command': result.command,
                'return_code': result.return_code,
                'success': result.success,
                'execution_time': result.execution_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'killed': result.killed
            }, indent=2))
            return
        
        # Create result table
        table = Table(title="Command Execution Result")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Command", result.command)
        table.add_row("Return Code", str(result.return_code))
        table.add_row("Success", "✅ Yes" if result.success else "❌ No")
        table.add_row("Execution Time", f"{result.execution_time:.3f}s")
        table.add_row("Killed", "Yes" if result.killed else "No")
        
        if result.pid:
            table.add_row("PID", str(result.pid))
        
        self.console.print(table)
        
        # Display stdout
        if result.stdout:
            self.console.print("\n[bold green]STDOUT:[/bold green]")
            syntax = Syntax(result.stdout, "bash", theme="monokai")
            self.console.print(Panel(syntax, title="Standard Output"))
        
        # Display stderr
        if result.stderr:
            self.console.print("\n[bold red]STDERR:[/bold red]")
            syntax = Syntax(result.stderr, "bash", theme="monokai")
            self.console.print(Panel(syntax, title="Standard Error"))
    
    def show_system_info(self, format: str = "table"):
        """Show system information"""
        info = self.shell_tools.get_system_info()
        
        if format == "json":
            import json
            self.console.print(json.dumps(info, indent=2))
            return
        
        # Create system info table
        table = Table(title="System Information")
        table.add_column("Category", style="cyan")
        table.add_column("Property", style="yellow")
        table.add_column("Value", style="white")
        
        # OS Info
        if 'os' in info:
            for key, value in info['os'].items():
                table.add_row("OS", key.title(), str(value))
        
        # CPU Info
        if 'cpu' in info:
            for key, value in info['cpu'].items():
                if key == 'usage':
                    table.add_row("CPU", "Usage", f"{value:.1f}%")
                else:
                    table.add_row("CPU", key.title(), str(value))
        
        # Memory Info
        if 'memory' in info:
            for key, value in info['memory'].items():
                if key == 'percent':
                    table.add_row("Memory", "Usage", f"{value:.1f}%")
                else:
                    # Convert bytes to human readable
                    if isinstance(value, int):
                        value = self._format_bytes(value)
                    table.add_row("Memory", key.title(), str(value))
        
        # Disk Info
        if 'disk' in info:
            for key, value in info['disk'].items():
                if key == 'percent':
                    table.add_row("Disk", "Usage", f"{value:.1f}%")
                else:
                    # Convert bytes to human readable
                    if isinstance(value, int):
                        value = self._format_bytes(value)
                    table.add_row("Disk", key.title(), str(value))
        
        # Network Info
        if 'network' in info:
            for key, value in info['network'].items():
                if isinstance(value, int):
                    value = self._format_bytes(value)
                table.add_row("Network", key.replace('_', ' ').title(), str(value))
        
        # Process Info
        if 'processes' in info:
            for key, value in info['processes'].items():
                table.add_row("Processes", key.title(), str(value))
        
        self.console.print(table)
    
    def show_process_info(self, pid: Optional[int] = None, format: str = "table"):
        """Show process information"""
        info = self.shell_tools.get_process_info(pid)
        
        if format == "json":
            import json
            self.console.print(json.dumps(info, indent=2))
            return
        
        if 'error' in info:
            self.console.print(f"[red]Error: {info['error']}[/red]")
            return
        
        # Create process info table
        table = Table(title=f"Process Information - PID {info['pid']}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in info.items():
            if key == 'cmdline':
                value = ' '.join(value) if isinstance(value, list) else str(value)
            elif key == 'memory_info':
                # Format memory info
                mem_str = []
                for k, v in value.items():
                    if isinstance(v, int):
                        v = self._format_bytes(v)
                    mem_str.append(f"{k}: {v}")
                value = ', '.join(mem_str)
            elif key == 'connections':
                value = f"{len(value)} connections"
            elif key == 'open_files':
                value = f"{len(value)} files"
            elif isinstance(value, float):
                value = f"{value:.2f}"
            else:
                value = str(value)
            
            table.add_row(key.replace('_', ' ').title(), value)
        
        self.console.print(table)
    
    def show_history(self, limit: Optional[int] = None, format: str = "table"):
        """Show command history"""
        history = self.shell_tools.get_command_history(limit)
        
        if format == "json":
            import json
            self.console.print(json.dumps([{
                'command': h.command,
                'return_code': h.return_code,
                'success': h.success,
                'execution_time': h.execution_time,
                'killed': h.killed
            } for h in history], indent=2))
            return
        
        if not history:
            self.console.print("[yellow]No command history available[/yellow]")
            return
        
        # Create history table
        table = Table(title="Command History")
        table.add_column("#", style="cyan")
        table.add_column("Command", style="white")
        table.add_column("Status", style="green")
        table.add_column("Time", style="yellow")
        table.add_column("Duration", style="blue")
        
        for i, result in enumerate(history, 1):
            status = "✅ Success" if result.success else "❌ Failed"
            if result.killed:
                status = "⏰ Killed"
            
            table.add_row(
                str(i),
                result.command[:50] + "..." if len(result.command) > 50 else result.command,
                status,
                time.strftime("%H:%M:%S", time.localtime()),
                f"{result.execution_time:.3f}s"
            )
        
        self.console.print(table)
    
    def kill_process(self, pid: int, signal_type: str = "SIGTERM"):
        """Kill a process"""
        self.console.print(f"[bold red]Killing process {pid} with {signal_type}...[/bold red]")
        
        success = self.shell_tools.kill_process(pid, signal_type)
        
        if success:
            self.console.print(f"[green]Successfully sent {signal_type} to process {pid}[/green]")
        else:
            self.console.print(f"[red]Failed to kill process {pid}[/red]")
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def close(self):
        """Clean up resources"""
        pass 