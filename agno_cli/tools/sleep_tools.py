"""
Sleep Tools - Delay and Timing Operations

This module provides comprehensive sleep and timing capabilities with:
- Precise delay operations with progress tracking
- Time-based scheduling and countdowns
- Performance timing and benchmarking
- Rate limiting and throttling
- Rich output formatting with progress bars
- Time zone and date utilities
- Caching and performance optimization
"""

import os
import sys
import time
import datetime
import threading
import signal
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass
from pathlib import Path
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.live import Live
from rich.syntax import Syntax
from rich.text import Text
from rich.markdown import Markdown
import psutil


@dataclass
class SleepResult:
    """Result of a sleep operation"""
    duration: float
    start_time: float
    end_time: float
    interrupted: bool
    actual_duration: float
    target_duration: float


@dataclass
class TimerResult:
    """Result of a timer operation"""
    elapsed_time: float
    start_time: float
    end_time: float
    iterations: int
    average_time: float
    min_time: float
    max_time: float


@dataclass
class ScheduleItem:
    """Scheduled item information"""
    id: str
    function: Callable
    args: tuple
    kwargs: dict
    interval: float
    next_run: float
    total_runs: int
    max_runs: Optional[int]
    active: bool


class SleepTools:
    """Core sleep and timing tools"""
    
    def __init__(self):
        self.console = Console()
        self.scheduler = {}
        self.scheduler_thread = None
        self.scheduler_running = False
        self.interrupt_flag = threading.Event()
        
        # Performance tracking
        self.performance_history = []
        self.max_history_size = 1000
        
        # Rate limiting
        self.rate_limiters = {}
        
        # Signal handling for graceful interruption
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        self.interrupt_flag.set()
    
    def sleep(self, duration: float, show_progress: bool = True, 
              description: str = "Sleeping") -> SleepResult:
        """Sleep for a specified duration with optional progress tracking"""
        start_time = time.time()
        target_duration = duration
        interrupted = False
        
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(description, total=duration)
                
                while not progress.finished:
                    if self.interrupt_flag.is_set():
                        interrupted = True
                        break
                    
                    elapsed = time.time() - start_time
                    progress.update(task, completed=elapsed)
                    
                    if elapsed >= duration:
                        break
                    
                    time.sleep(0.1)  # Update every 100ms
        else:
            # Simple sleep without progress
            time.sleep(duration)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        result = SleepResult(
            duration=target_duration,
            start_time=start_time,
            end_time=end_time,
            interrupted=interrupted,
            actual_duration=actual_duration,
            target_duration=target_duration
        )
        
        # Reset interrupt flag
        self.interrupt_flag.clear()
        
        return result
    
    def sleep_until(self, target_time: datetime.datetime, 
                   show_progress: bool = True) -> SleepResult:
        """Sleep until a specific time"""
        now = datetime.datetime.now()
        if target_time <= now:
            return SleepResult(
                duration=0,
                start_time=time.time(),
                end_time=time.time(),
                interrupted=False,
                actual_duration=0,
                target_duration=0
            )
        
        duration = (target_time - now).total_seconds()
        return self.sleep(duration, show_progress, f"Sleeping until {target_time.strftime('%H:%M:%S')}")
    
    def countdown(self, duration: float, show_progress: bool = True,
                 format: str = "seconds") -> SleepResult:
        """Countdown timer with progress tracking"""
        start_time = time.time()
        target_duration = duration
        interrupted = False
        
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task("Countdown", total=duration)
                
                while not progress.finished:
                    if self.interrupt_flag.is_set():
                        interrupted = True
                        break
                    
                    elapsed = time.time() - start_time
                    remaining = max(0, duration - elapsed)
                    
                    # Format remaining time
                    if format == "seconds":
                        desc = f"Countdown: {remaining:.1f}s"
                    elif format == "minutes":
                        desc = f"Countdown: {remaining/60:.1f}m"
                    elif format == "hours":
                        desc = f"Countdown: {remaining/3600:.1f}h"
                    else:
                        desc = f"Countdown: {remaining:.1f}s"
                    
                    progress.update(task, completed=elapsed, description=desc)
                    
                    if elapsed >= duration:
                        break
                    
                    time.sleep(0.1)
        else:
            time.sleep(duration)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        result = SleepResult(
            duration=target_duration,
            start_time=start_time,
            end_time=end_time,
            interrupted=interrupted,
            actual_duration=actual_duration,
            target_duration=target_duration
        )
        
        self.interrupt_flag.clear()
        return result
    
    def timer(self, function: Callable, *args, iterations: int = 1,
              **kwargs) -> TimerResult:
        """Time the execution of a function"""
        times = []
        start_time = time.time()
        
        for i in range(iterations):
            iter_start = time.time()
            result = function(*args, **kwargs)
            iter_end = time.time()
            times.append(iter_end - iter_start)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return TimerResult(
            elapsed_time=total_time,
            start_time=start_time,
            end_time=end_time,
            iterations=iterations,
            average_time=sum(times) / len(times) if times else 0,
            min_time=min(times) if times else 0,
            max_time=max(times) if times else 0
        )
    
    def benchmark(self, functions: Dict[str, Callable], iterations: int = 100,
                 *args, **kwargs) -> Dict[str, TimerResult]:
        """Benchmark multiple functions"""
        results = {}
        
        for name, func in functions.items():
            results[name] = self.timer(func, *args, iterations=iterations, **kwargs)
        
        return results
    
    def rate_limit(self, key: str, max_calls: int, time_window: float) -> bool:
        """Simple rate limiting"""
        now = time.time()
        
        if key not in self.rate_limiters:
            self.rate_limiters[key] = []
        
        # Remove old calls outside the time window
        self.rate_limiters[key] = [
            call_time for call_time in self.rate_limiters[key]
            if now - call_time < time_window
        ]
        
        # Check if we can make another call
        if len(self.rate_limiters[key]) < max_calls:
            self.rate_limiters[key].append(now)
            return True
        
        return False
    
    def wait_for_rate_limit(self, key: str, max_calls: int, time_window: float,
                           show_progress: bool = True) -> bool:
        """Wait until rate limit allows another call"""
        while not self.rate_limit(key, max_calls, time_window):
            if show_progress:
                self.console.print(f"[yellow]Rate limited for {key}, waiting...[/yellow]")
            time.sleep(0.1)
        
        return True
    
    def schedule(self, function: Callable, interval: float, *args,
                max_runs: Optional[int] = None, **kwargs) -> str:
        """Schedule a function to run periodically"""
        import uuid
        
        schedule_id = str(uuid.uuid4())
        next_run = time.time() + interval
        
        self.scheduler[schedule_id] = ScheduleItem(
            id=schedule_id,
            function=function,
            args=args,
            kwargs=kwargs,
            interval=interval,
            next_run=next_run,
            total_runs=0,
            max_runs=max_runs,
            active=True
        )
        
        # Start scheduler thread if not running
        if not self.scheduler_running:
            self._start_scheduler()
        
        return schedule_id
    
    def _start_scheduler(self):
        """Start the scheduler thread"""
        if self.scheduler_running:
            return
        
        self.scheduler_running = True
        
        def scheduler_loop():
            while self.scheduler_running:
                now = time.time()
                
                # Check for items to run
                for schedule_id, item in list(self.scheduler.items()):
                    if not item.active:
                        continue
                    
                    if now >= item.next_run:
                        try:
                            item.function(*item.args, **item.kwargs)
                            item.total_runs += 1
                            
                            # Check if max runs reached
                            if item.max_runs and item.total_runs >= item.max_runs:
                                item.active = False
                            else:
                                item.next_run = now + item.interval
                        except Exception as e:
                            self.console.print(f"[red]Scheduled function error: {e}[/red]")
                
                time.sleep(0.1)  # Check every 100ms
        
        self.scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.scheduler_thread.start()
    
    def stop_schedule(self, schedule_id: str) -> bool:
        """Stop a scheduled function"""
        if schedule_id in self.scheduler:
            self.scheduler[schedule_id].active = False
            return True
        return False
    
    def list_schedules(self) -> List[ScheduleItem]:
        """List all scheduled functions"""
        return list(self.scheduler.values())
    
    def clear_schedules(self):
        """Clear all scheduled functions"""
        self.scheduler.clear()
    
    def get_time_info(self) -> Dict[str, Any]:
        """Get current time information"""
        now = datetime.datetime.now()
        
        return {
            'timestamp': time.time(),
            'datetime': now.isoformat(),
            'date': now.date().isoformat(),
            'time': now.time().isoformat(),
            'timezone': str(now.astimezone().tzinfo),
            'weekday': now.strftime('%A'),
            'month': now.strftime('%B'),
            'year': now.year,
            'day_of_year': now.timetuple().tm_yday,
            'week_of_year': now.isocalendar()[1]
        }
    
    def format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.2f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
        else:
            days = seconds / 86400
            return f"{days:.1f} days"
    
    def wait_for_condition(self, condition: Callable[[], bool], timeout: float = 60,
                          check_interval: float = 0.1, show_progress: bool = True) -> bool:
        """Wait for a condition to become true"""
        start_time = time.time()
        
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task("Waiting for condition...", total=None)
                
                while time.time() - start_time < timeout:
                    if self.interrupt_flag.is_set():
                        return False
                    
                    if condition():
                        return True
                    
                    progress.update(task, description="Waiting for condition...")
                    time.sleep(check_interval)
        else:
            while time.time() - start_time < timeout:
                if self.interrupt_flag.is_set():
                    return False
                
                if condition():
                    return True
                
                time.sleep(check_interval)
        
        return False
    
    def performance_monitor(self, duration: float = 60) -> Dict[str, Any]:
        """Monitor system performance for a duration"""
        start_time = time.time()
        samples = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("Monitoring performance...", total=duration)
            
            while time.time() - start_time < duration:
                if self.interrupt_flag.is_set():
                    break
                
                sample = {
                    'timestamp': time.time(),
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent
                }
                samples.append(sample)
                
                elapsed = time.time() - start_time
                progress.update(task, completed=elapsed)
                
                time.sleep(1)
        
        if not samples:
            return {}
        
        # Calculate statistics
        cpu_values = [s['cpu_percent'] for s in samples]
        memory_values = [s['memory_percent'] for s in samples]
        disk_values = [s['disk_usage'] for s in samples]
        
        return {
            'duration': duration,
            'samples': len(samples),
            'cpu': {
                'average': sum(cpu_values) / len(cpu_values),
                'min': min(cpu_values),
                'max': max(cpu_values)
            },
            'memory': {
                'average': sum(memory_values) / len(memory_values),
                'min': min(memory_values),
                'max': max(memory_values)
            },
            'disk': {
                'average': sum(disk_values) / len(disk_values),
                'min': min(disk_values),
                'max': max(disk_values)
            }
        }


class SleepToolsManager:
    """CLI integration for sleep tools"""
    
    def __init__(self):
        self.sleep_tools = SleepTools()
        self.console = Console()
    
    def sleep(self, duration: float, show_progress: bool = True, 
              description: str = "Sleeping", format: str = "table"):
        """Sleep for a specified duration"""
        try:
            result = self.sleep_tools.sleep(duration, show_progress, description)
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'duration': result.duration,
                    'start_time': result.start_time,
                    'end_time': result.end_time,
                    'interrupted': result.interrupted,
                    'actual_duration': result.actual_duration,
                    'target_duration': result.target_duration
                }, indent=2))
                return
            
            # Display result
            if result.interrupted:
                self.console.print("[yellow]Sleep interrupted[/yellow]")
            else:
                self.console.print("[green]Sleep completed[/green]")
            
            # Show timing information
            stats_table = Table(title="Sleep Statistics")
            stats_table.add_column("Property", style="cyan")
            stats_table.add_column("Value", style="white")
            
            stats_table.add_row("Target Duration", self.sleep_tools.format_duration(result.target_duration))
            stats_table.add_row("Actual Duration", self.sleep_tools.format_duration(result.actual_duration))
            stats_table.add_row("Start Time", datetime.datetime.fromtimestamp(result.start_time).strftime('%H:%M:%S'))
            stats_table.add_row("End Time", datetime.datetime.fromtimestamp(result.end_time).strftime('%H:%M:%S'))
            stats_table.add_row("Interrupted", str(result.interrupted))
            
            self.console.print(stats_table)
            
        except Exception as e:
            self.console.print(f"[red]Sleep error: {e}[/red]")
    
    def countdown(self, duration: float, show_progress: bool = True,
                 format_type: str = "seconds", output_format: str = "table"):
        """Countdown timer"""
        try:
            result = self.sleep_tools.countdown(duration, show_progress, format_type)
            
            if output_format == "json":
                import json
                self.console.print(json.dumps({
                    'duration': result.duration,
                    'start_time': result.start_time,
                    'end_time': result.end_time,
                    'interrupted': result.interrupted,
                    'actual_duration': result.actual_duration,
                    'target_duration': result.target_duration
                }, indent=2))
                return
            
            # Display result
            if result.interrupted:
                self.console.print("[yellow]Countdown interrupted[/yellow]")
            else:
                self.console.print("[green]Countdown completed![/green]")
            
            # Show timing information
            stats_table = Table(title="Countdown Statistics")
            stats_table.add_column("Property", style="cyan")
            stats_table.add_column("Value", style="white")
            
            stats_table.add_row("Target Duration", self.sleep_tools.format_duration(result.target_duration))
            stats_table.add_row("Actual Duration", self.sleep_tools.format_duration(result.actual_duration))
            stats_table.add_row("Start Time", datetime.datetime.fromtimestamp(result.start_time).strftime('%H:%M:%S'))
            stats_table.add_row("End Time", datetime.datetime.fromtimestamp(result.end_time).strftime('%H:%M:%S'))
            stats_table.add_row("Interrupted", str(result.interrupted))
            
            self.console.print(stats_table)
            
        except Exception as e:
            self.console.print(f"[red]Countdown error: {e}[/red]")
    
    def timer(self, command: str, iterations: int = 1, format: str = "table"):
        """Time the execution of a command"""
        try:
            import subprocess
            
            def run_command():
                subprocess.run(command, shell=True, capture_output=True)
            
            result = self.sleep_tools.timer(run_command, iterations=iterations)
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'command': command,
                    'iterations': result.iterations,
                    'total_time': result.elapsed_time,
                    'average_time': result.average_time,
                    'min_time': result.min_time,
                    'max_time': result.max_time
                }, indent=2))
                return
            
            # Display result
            stats_table = Table(title=f"Timer Results for '{command}'")
            stats_table.add_column("Property", style="cyan")
            stats_table.add_column("Value", style="white")
            
            stats_table.add_row("Command", command)
            stats_table.add_row("Iterations", str(result.iterations))
            stats_table.add_row("Total Time", self.sleep_tools.format_duration(result.elapsed_time))
            stats_table.add_row("Average Time", self.sleep_tools.format_duration(result.average_time))
            stats_table.add_row("Min Time", self.sleep_tools.format_duration(result.min_time))
            stats_table.add_row("Max Time", self.sleep_tools.format_duration(result.max_time))
            
            self.console.print(stats_table)
            
        except Exception as e:
            self.console.print(f"[red]Timer error: {e}[/red]")
    
    def time_info(self, format: str = "table"):
        """Get current time information"""
        try:
            time_info = self.sleep_tools.get_time_info()
            
            if format == "json":
                import json
                self.console.print(json.dumps(time_info, indent=2))
                return
            
            # Display time information
            time_table = Table(title="Current Time Information")
            time_table.add_column("Property", style="cyan")
            time_table.add_column("Value", style="white")
            
            for key, value in time_info.items():
                time_table.add_row(key.replace('_', ' ').title(), str(value))
            
            self.console.print(time_table)
            
        except Exception as e:
            self.console.print(f"[red]Time info error: {e}[/red]")
    
    def performance_monitor(self, duration: float = 60, format: str = "table"):
        """Monitor system performance"""
        try:
            result = self.sleep_tools.performance_monitor(duration)
            
            if format == "json":
                import json
                self.console.print(json.dumps(result, indent=2))
                return
            
            if not result:
                self.console.print("[yellow]No performance data collected[/yellow]")
                return
            
            # Display performance information
            perf_table = Table(title=f"Performance Monitor ({duration}s)")
            perf_table.add_column("Metric", style="cyan")
            perf_table.add_column("Average", style="white")
            perf_table.add_column("Min", style="green")
            perf_table.add_column("Max", style="red")
            
            perf_table.add_row(
                "CPU %",
                f"{result['cpu']['average']:.1f}%",
                f"{result['cpu']['min']:.1f}%",
                f"{result['cpu']['max']:.1f}%"
            )
            perf_table.add_row(
                "Memory %",
                f"{result['memory']['average']:.1f}%",
                f"{result['memory']['min']:.1f}%",
                f"{result['memory']['max']:.1f}%"
            )
            perf_table.add_row(
                "Disk %",
                f"{result['disk']['average']:.1f}%",
                f"{result['disk']['min']:.1f}%",
                f"{result['disk']['max']:.1f}%"
            )
            
            self.console.print(perf_table)
            
        except Exception as e:
            self.console.print(f"[red]Performance monitor error: {e}[/red]")
    
    def list_schedules(self, format: str = "table"):
        """List scheduled functions"""
        try:
            schedules = self.sleep_tools.list_schedules()
            
            if format == "json":
                import json
                schedule_data = []
                for schedule in schedules:
                    schedule_data.append({
                        'id': schedule.id,
                        'interval': schedule.interval,
                        'next_run': schedule.next_run,
                        'total_runs': schedule.total_runs,
                        'max_runs': schedule.max_runs,
                        'active': schedule.active
                    })
                self.console.print(json.dumps(schedule_data, indent=2))
                return
            
            if not schedules:
                self.console.print("[yellow]No scheduled functions[/yellow]")
                return
            
            # Display schedules
            schedule_table = Table(title="Scheduled Functions")
            schedule_table.add_column("ID", style="cyan")
            schedule_table.add_column("Interval", style="white")
            schedule_table.add_column("Next Run", style="yellow")
            schedule_table.add_column("Total Runs", style="green")
            schedule_table.add_column("Max Runs", style="blue")
            schedule_table.add_column("Active", style="magenta")
            
            for schedule in schedules:
                next_run_str = datetime.datetime.fromtimestamp(schedule.next_run).strftime('%H:%M:%S')
                max_runs_str = str(schedule.max_runs) if schedule.max_runs else "∞"
                
                schedule_table.add_row(
                    schedule.id[:8],
                    self.sleep_tools.format_duration(schedule.interval),
                    next_run_str,
                    str(schedule.total_runs),
                    max_runs_str,
                    str(schedule.active)
                )
            
            self.console.print(schedule_table)
            
        except Exception as e:
            self.console.print(f"[red]List schedules error: {e}[/red]")
    
    def clear_schedules(self):
        """Clear all scheduled functions"""
        try:
            self.sleep_tools.clear_schedules()
            self.console.print("[green]All scheduled functions cleared[/green]")
        except Exception as e:
            self.console.print(f"[red]Clear schedules error: {e}[/red]")
    
    def rate_limit_info(self, format: str = "table"):
        """Show rate limiting information"""
        try:
            rate_limiters = self.sleep_tools.rate_limiters
            
            if format == "json":
                import json
                self.console.print(json.dumps(rate_limiters, indent=2))
                return
            
            if not rate_limiters:
                self.console.print("[yellow]No rate limiters active[/yellow]")
                return
            
            # Display rate limiters
            rate_table = Table(title="Rate Limiters")
            rate_table.add_column("Key", style="cyan")
            rate_table.add_column("Calls", style="white")
            rate_table.add_column("Last Call", style="yellow")
            
            for key, calls in rate_limiters.items():
                if calls:
                    last_call = datetime.datetime.fromtimestamp(calls[-1]).strftime('%H:%M:%S')
                    rate_table.add_row(key, str(len(calls)), last_call)
                else:
                    rate_table.add_row(key, "0", "Never")
            
            self.console.print(rate_table)
            
        except Exception as e:
            self.console.print(f"[red]Rate limit info error: {e}[/red]") 