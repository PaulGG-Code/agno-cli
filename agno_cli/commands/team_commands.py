"""
Team management commands with full functionality
"""

import json
import threading
import time
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.layout import Layout

from agents.multi_agent import MultiAgentSystem
from agents.orchestrator import TaskPriority, MessageType
from agents.agent_state import AgentRole, AgentStatus


class TeamCommands:
    """Enhanced team management commands with full functionality"""
    
    def __init__(self, multi_agent_system: MultiAgentSystem):
        self.multi_agent_system = multi_agent_system
        self.console = Console()
        self.team_active = False
        self.task_execution_thread = None
        self.stop_execution = False
        
        # State file for persistence
        self.state_file = Path.home() / '.agno_cli' / 'team_state.json'
        self.state_file.parent.mkdir(exist_ok=True)
        
        # System state file for orchestrator persistence
        self.system_state_file = Path.home() / '.agno_cli' / 'system_state.json'
        
        # Load state
        self._load_state()
    
    def _load_state(self):
        """Load team state from file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.team_active = state.get('team_active', False)
        except Exception as e:
            self.console.print(f"[yellow]Could not load team state: {e}[/yellow]")
            self.team_active = False
    
    def _save_state(self):
        """Save team state to file"""
        try:
            state = {
                'team_active': self.team_active,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.console.print(f"[yellow]Could not save team state: {e}[/yellow]")
    
    def _save_system_state(self):
        """Save system state including orchestrator and tasks"""
        try:
            self.multi_agent_system.save_system_state(self.system_state_file)
            self.console.print("[blue]System state saved successfully[/blue]")
        except Exception as e:
            self.console.print(f"[yellow]Could not save system state: {e}[/yellow]")
        
    def activate_team(self) -> bool:
        """Activate the team for task execution"""
        if self.team_active:
            self.console.print("[yellow]Team is already active[/yellow]")
            return True
            
        # Check if we have agents available
        agents = self.multi_agent_system.list_agents()
        if not agents:
            self.console.print("[red]No agents available. Create agents first.[/red]")
            return False
            
        self.team_active = True
        self.stop_execution = False
        self._save_state()
        
        self.console.print("[green]Team activated! Agents are now ready to work on tasks.[/green]")
        self.console.print("[blue]Note: Background task execution is temporarily disabled. Use --execute-pending to run tasks manually.[/blue]")
        
        # Temporarily disable background thread to avoid recursion issues
        # self._start_task_execution_thread()
        return True
    
    def deactivate_team(self) -> bool:
        """Deactivate the team and stop task execution"""
        if not self.team_active:
            self.console.print("[yellow]Team is not active[/yellow]")
            return True
            
        self.team_active = False
        self.stop_execution = True
        self._save_state()
        
        # Stop task execution thread
        if self.task_execution_thread and self.task_execution_thread.is_alive():
            self.task_execution_thread.join(timeout=2)
            
        self.console.print("[green]Team deactivated. No new tasks will be processed.[/green]")
        return True
    
    def _start_task_execution_thread(self):
        """Start the background task execution thread"""
        def task_loop():
            self.console.print("[blue]Task execution thread started[/blue]")
            while self.team_active and not self.stop_execution:
                try:
                    # Check for pending tasks
                    pending_tasks = self._get_pending_tasks()
                    
                    if pending_tasks:
                        self.console.print(f"[blue]Found {len(pending_tasks)} pending tasks[/blue]")
                        
                        for task in pending_tasks:
                            if self.team_active and not self.stop_execution:
                                self.console.print(f"[blue]Processing task: {task['description'][:50]}...[/blue]")
                                self._execute_task(task)
                    
                    # Save system state periodically
                    if pending_tasks:
                        self._save_system_state()
                    
                    # Wait before next check
                    time.sleep(5)  # Increased from 2 to 5 seconds
                    
                except Exception as e:
                    self.console.print(f"[red]Task execution error: {e}[/red]")
                    time.sleep(5)
        
        # Start the thread
        self.task_execution_thread = threading.Thread(target=task_loop, daemon=True)
        self.task_execution_thread.start()
        self.console.print("[green]Task execution thread started successfully[/green]")
    
    def _get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get list of pending tasks from orchestrator"""
        try:
            orchestrator = self.multi_agent_system.orchestrator
            
            pending_tasks = []
            for task_id, task in orchestrator.tasks.items():
                if task.status == "pending":
                    pending_tasks.append({
                        'task_id': task_id,
                        'description': task.description,
                        'priority': task.priority,
                        'requirements': task.requirements
                    })
            
            return pending_tasks
        except Exception as e:
            self.console.print(f"[red]Error getting pending tasks: {e}[/red]")
            return []
    
    def _execute_task(self, task_info: Dict[str, Any]):
        """Execute a specific task"""
        task_id = task_info['task_id']
        
        # Find best agent for the task
        best_agent = self._find_best_agent_for_task(task_info)
        if not best_agent:
            self.console.print(f"[yellow]No suitable agent found for task: {task_info['description']}[/yellow]")
            # Try to assign to any available agent as fallback
            available_agents = [a for a in self.multi_agent_system.list_agents() if a['status'] == 'idle']
            if available_agents:
                best_agent = available_agents[0]
                self.console.print(f"[blue]Falling back to agent: {best_agent['name']}[/blue]")
            else:
                self.console.print(f"[red]No available agents to execute task: {task_info['description']}[/red]")
                return
        
        # Execute task directly without using orchestrator message system
        try:
            self.console.print(f"[blue]Agent {best_agent['name']} starting task: {task_info['description']}[/blue]")
            
            # Update agent status to working
            agent_state = self.multi_agent_system.get_agent_state(best_agent['agent_id'])
            if agent_state:
                agent_state.update_status(AgentStatus.WORKING)
            
            # Execute task directly
            result = self.multi_agent_system.execute_task(
                agent_id=best_agent['agent_id'],
                task_description=task_info['description'],
                context=task_info.get('requirements', {})
            )
            
            # Update task status directly in orchestrator
            if task_id in self.multi_agent_system.orchestrator.tasks:
                task = self.multi_agent_system.orchestrator.tasks[task_id]
                task.assigned_agent = best_agent['agent_id']
                task.status = "completed"
                # Convert RunResponse to string to avoid JSON serialization issues
                task.result = str(result) if result else "Task completed successfully"
            
            # Update agent status back to idle
            if agent_state:
                agent_state.update_status(AgentStatus.IDLE)
                # Convert RunResponse to string to avoid JSON serialization issues
                result_str = str(result) if result else "Task completed successfully"
                agent_state.complete_task(task_id, result_str)
            
            # Save system state after task completion
            self._save_system_state()
            
            self.console.print(f"[green]Task completed by {best_agent['name']}: {task_info['description']}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error executing task {task_id}: {e}[/red]")
            # Mark task as failed
            if task_id in self.multi_agent_system.orchestrator.tasks:
                self.multi_agent_system.orchestrator.tasks[task_id].status = "failed"
            # Update agent status back to idle
            if agent_state:
                agent_state.update_status(AgentStatus.IDLE)
                agent_state.complete_task(task_id, error=str(e))
            # Save system state after task failure
            self._save_system_state()
    
    def _find_best_agent_for_task(self, task_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the best agent for a given task"""
        agents = self.multi_agent_system.list_agents()
        available_agents = [a for a in agents if a['status'] == 'idle']
        
        if not available_agents:
            return None
        
        # Score agents based on capabilities
        scored_agents = []
        requirements = task_info.get('requirements', {})
        
        for agent in available_agents:
            score = self._calculate_agent_score(agent, requirements)
            if score > 0:
                scored_agents.append((agent, score))
        
        if not scored_agents:
            # If no agents match requirements, use any available agent
            self.console.print(f"[yellow]No agents match requirements: {requirements}[/yellow]")
            return available_agents[0]
        
        # Return agent with highest score
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        return scored_agents[0][0]
    
    def _calculate_agent_score(self, agent: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """Calculate how well an agent fits a task"""
        score = 0.0
        
        # Base score from success rate
        success_rate = agent.get('metrics', {}).get('success_rate', 0.0)
        score += success_rate * 50
        
        # Check role match
        if 'role' in requirements:
            required_role = requirements['role']
            if agent['role'] == required_role:
                score += 30
        
        # Check skills match
        if 'skills' in requirements:
            required_skills = set(requirements['skills'])
            agent_skills = set(agent.get('capabilities', {}).get('skills', []))
            skill_matches = required_skills.intersection(agent_skills)
            if skill_matches:
                score += len(skill_matches) * 10
        
        # Check tools match
        if 'tools' in requirements:
            required_tools = set(requirements['tools'])
            agent_tools = set(agent.get('capabilities', {}).get('tools', []))
            tool_matches = required_tools.intersection(agent_tools)
            if tool_matches:
                score += len(tool_matches) * 10
        
        # If no specific requirements, give base score
        if not requirements:
            score += 10
        
        return score
    
    def get_team_status(self) -> Dict[str, Any]:
        """Get comprehensive team status"""
        if not self.team_active:
            return {
                'status': 'inactive',
                'message': 'Team is not active. Use --activate to start the team.'
            }
        
        system_status = self.multi_agent_system.get_system_status()
        team_status = system_status['team_status']
        
        # Group tasks by status
        tasks_by_status = {
            'pending': [],
            'assigned': [],
            'active': [],
            'completed': [],
            'failed': []
        }
        
        for task in self.multi_agent_system.orchestrator.tasks.values():
            task_info = {
                'id': task.task_id,
                'description': task.description,
                'priority': task.priority.value,
                'assigned_agent': task.assigned_agent,
                'created_at': task.created_at.isoformat()
            }
            tasks_by_status[task.status].append(task_info)
        
        return {
            'status': 'active',
            'system_id': system_status['system_id'],
            'team_status': team_status,
            'tasks_by_status': tasks_by_status
        }
    
    def assign_task(self, description: str, requirements: Dict[str, Any] = None,
                   priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """Assign a task to the team"""
        if not self.team_active:
            self.console.print("[yellow]Team is not active. Activate team first with --activate[/yellow]")
            return None
        
        task_id = self.multi_agent_system.assign_task(
            description=description,
            requirements=requirements or {},
            priority=priority
        )
        
        # Save system state after task assignment
        self._save_system_state()
        
        self.console.print(f"[green]Task assigned with ID: {task_id}[/green]")
        self.console.print(f"[blue]Task will be executed by the next available agent[/blue]")
        
        # Try to execute the task immediately if possible
        self._try_execute_pending_tasks()
        
        return task_id
    
    def _try_execute_pending_tasks(self):
        """Try to execute any pending tasks"""
        pending_tasks = self._get_pending_tasks()
        if pending_tasks:
            self.console.print(f"[blue]Found {len(pending_tasks)} pending tasks[/blue]")
            for task in pending_tasks:
                self._execute_task(task)

    def _assign_pending_tasks(self):
        """Manually assign all pending tasks to available agents"""
        pending_tasks = self._get_pending_tasks()
        if not pending_tasks:
            self.console.print("[blue]No pending tasks to assign[/blue]")
            return
        
        self.console.print(f"[blue]Attempting to assign {len(pending_tasks)} pending tasks...[/blue]")
        
        for task in pending_tasks:
            task_id = task['task_id']
            description = task['description']
            
            # Try to assign the task
            success = self.multi_agent_system.orchestrator.assign_task(task_id)
            
            if success:
                self.console.print(f"[green]✓ Task '{description[:50]}...' assigned successfully[/green]")
            else:
                self.console.print(f"[red]✗ Failed to assign task '{description[:50]}...'[/red]")
        
        # Save state after assignment
        self._save_system_state()

    def _execute_assigned_tasks(self):
        """Execute all assigned tasks"""
        assigned_tasks = []
        for task in self.multi_agent_system.orchestrator.tasks.values():
            if task.status == "assigned":
                assigned_tasks.append({
                    'task_id': task.task_id,
                    'description': task.description,
                    'assigned_agent': task.assigned_agent
                })
        
        if not assigned_tasks:
            self.console.print("[blue]No assigned tasks to execute[/blue]")
            return
        
        self.console.print(f"[blue]Executing {len(assigned_tasks)} assigned tasks...[/blue]")
        
        for task_info in assigned_tasks:
            self.console.print(f"[blue]Executing task: {task_info['description'][:50]}...[/blue]")
            self._execute_task(task_info)
    
    def send_message(self, message: str, message_type: MessageType = MessageType.BROADCAST) -> List[str]:
        """Send a message to the team"""
        if not self.team_active:
            self.console.print("[yellow]Team is not active. Activate team first.[/yellow]")
            return []
        
        # Find a leader agent to send the message
        agents = self.multi_agent_system.list_agents()
        leader_agents = [a for a in agents if a['role'] == 'leader']
        
        if leader_agents:
            from_agent = leader_agents[0]['agent_id']
        else:
            from_agent = "system"
        
        message_ids = self.multi_agent_system.broadcast_message(
            from_agent=from_agent,
            message=message,
            message_type=message_type
        )
        
        # Save system state after message
        self._save_system_state()
        
        return message_ids
    
    def display_team_status(self):
        """Display comprehensive team status"""
        status = self.get_team_status()
        
        if status['status'] == 'inactive':
            self.console.print(Panel(
                status['message'],
                title="Team Status",
                border_style="yellow"
            ))
            return
        
        # Get configuration from system status
        system_status = self.multi_agent_system.get_system_status()
        configuration = system_status['configuration']
        
        status_text = f"""
**System ID:** {status['system_id']}

**Team Status:** {status['team_status']['orchestrator_id']}

**Agents:**
- Total: {status['team_status']['total_agents']}
- Active: {status['team_status']['active_agents']}
- Idle: {status['team_status']['idle_agents']}

**Tasks:**
- Pending: {len(status['tasks_by_status']['pending'])}
- Assigned: {len(status['tasks_by_status']['assigned'])}
- Active: {len(status['tasks_by_status']['active'])}
- Completed: {len(status['tasks_by_status']['completed'])}
- Failed: {len(status['tasks_by_status']['failed'])}

**Communication:**
- Total Messages: {status['team_status']['total_messages']}
- Uptime: {status['team_status']['uptime']:.1f}s

**Configuration:**
- Model Provider: {configuration['model_provider']}
- Model ID: {configuration['model_id']}
"""
        
        self.console.print(Panel(
            status_text,
            title="Team Status",
            border_style="green"
        ))
        
        # Show detailed task information if any
        if any(status['tasks_by_status'].values()):
            self._display_task_details(status['tasks_by_status'])
    
    def _display_task_details(self, tasks_by_status: Dict[str, List]):
        """Display detailed task information"""
        table = Table(title="Task Details")
        table.add_column("Status", style="cyan")
        table.add_column("ID", style="magenta")
        table.add_column("Description", style="white")
        table.add_column("Priority", style="yellow")
        table.add_column("Agent", style="green")
        table.add_column("Created", style="blue")
        table.add_column("Result", style="red")
        
        for status, tasks in tasks_by_status.items():
            for task in tasks:
                # Show result preview for completed tasks
                result_preview = "N/A"
                if status == "completed" and task.get('result'):
                    result_text = str(task['result'])
                    result_preview = result_text[:30] + "..." if len(result_text) > 30 else result_text
                
                table.add_row(
                    status.upper(),
                    task['id'][:8],
                    task['description'][:50] + "..." if len(task['description']) > 50 else task['description'],
                    str(task['priority']),
                    task['assigned_agent'][:8] if task['assigned_agent'] else "None",
                    task['created_at'][:19],
                    result_preview
                )
        
        self.console.print(table)
    
    def display_task_results(self, task_id: str = None):
        """Display detailed task results"""
        # Get all tasks from orchestrator
        tasks = self.multi_agent_system.orchestrator.tasks
        
        if not tasks:
            self.console.print("[yellow]No tasks found[/yellow]")
            return
        
        if task_id:
            # Show specific task result
            if task_id in tasks:
                task = tasks[task_id]
                self._display_single_task_result(task)
            else:
                # Try to find by partial ID
                found_task = None
                for t_id, task in tasks.items():
                    if t_id.startswith(task_id):
                        found_task = task
                        break
                
                if found_task:
                    self._display_single_task_result(found_task)
                else:
                    self.console.print(f"[red]Task {task_id} not found[/red]")
                    self.console.print("Available tasks:")
                    for t_id in tasks.keys():
                        self.console.print(f"  - {t_id[:8]}: {tasks[t_id].description[:50]}...")
        else:
            # Show all completed tasks with results
            completed_tasks = [task for task in tasks.values() if task.status == "completed"]
            
            if not completed_tasks:
                self.console.print("[yellow]No completed tasks found[/yellow]")
                return
            
            for task in completed_tasks:
                self._display_single_task_result(task)
                self.console.print("")  # Add spacing between tasks
    
    def _display_single_task_result(self, task):
        """Display a single task result"""
        # Create result panel
        result_panel = Panel(
            f"[bold blue]Task ID:[/bold blue] {task.task_id}\n"
            f"[bold green]Description:[/bold green] {task.description}\n"
            f"[bold yellow]Status:[/bold yellow] {task.status}\n"
            f"[bold magenta]Priority:[/bold magenta] {task.priority.value}\n"
            f"[bold cyan]Assigned Agent:[/bold cyan] {task.assigned_agent[:8] if task.assigned_agent else 'None'}\n"
            f"[bold white]Created:[/bold white] {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            title="Task Information",
            border_style="blue"
        )
        self.console.print(result_panel)
        
        # Show result if available
        if task.result:
            result_text = str(task.result)
            # Remove truncation: always show full result
            result_panel = Panel(
                result_text,
                title="Task Result",
                border_style="green"
            )
            self.console.print(result_panel)
        else:
            self.console.print("[yellow]No result available for this task[/yellow]")
        
        # Show requirements if any
        if task.requirements:
            req_panel = Panel(
                str(task.requirements),
                title="Task Requirements",
                border_style="yellow"
            )
            self.console.print(req_panel)
    
    def display_communication_history(self):
        """Display team communication history"""
        # Get communication log from orchestrator
        communication_log = self.multi_agent_system.orchestrator.communication_log
        
        if not communication_log:
            self.console.print("[yellow]No communication history found[/yellow]")
            return
        
        # Create table for communication history
        table = Table(title="Team Communication History")
        table.add_column("Time", style="cyan", width=20)
        table.add_column("From", style="green", width=12)
        table.add_column("To", style="blue", width=12)
        table.add_column("Type", style="yellow", width=15)
        table.add_column("Content", style="white", width=50)
        
        # Display last 20 messages
        for message in communication_log[-20:]:
            # Get agent names
            from_name = self._get_agent_name(message.from_agent)
            to_name = self._get_agent_name(message.to_agent) if message.to_agent else "ALL"
            
            # Truncate content for display
            content = message.content[:47] + "..." if len(message.content) > 50 else message.content
            
            table.add_row(
                message.timestamp.strftime("%H:%M:%S"),
                from_name,
                to_name,
                message.message_type.value,
                content
            )
        
        self.console.print(table)
        
        # Show message count
        self.console.print(f"\n[blue]Total messages: {len(communication_log)}[/blue]")
    
    def _get_agent_name(self, agent_id: str) -> str:
        """Get agent name from ID"""
        if agent_id == "system" or agent_id == "orchestrator":
            return agent_id
        
        agents = self.multi_agent_system.list_agents()
        for agent in agents:
            if agent['agent_id'] == agent_id:
                return agent['name']
        
        return agent_id[:8]

