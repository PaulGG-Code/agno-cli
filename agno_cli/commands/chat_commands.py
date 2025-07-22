"""
Enhanced chat commands with multi-agent support
"""

import uuid
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Prompt, Confirm

from agents.multi_agent import MultiAgentSystem
from agents.agent_state import AgentRole
from reasoning.tracer import ReasoningTracer
from reasoning.metrics import MetricsCollector, TokenUsage
from core.config import Config


class ChatCommands:
    """Enhanced chat commands with multi-agent capabilities"""
    
    def __init__(self, config: Config, multi_agent_system: MultiAgentSystem, 
                 tracer: ReasoningTracer, metrics: MetricsCollector):
        self.config = config
        self.multi_agent_system = multi_agent_system
        self.tracer = tracer
        self.metrics = metrics
        self.console = Console()
        
        # Chat state
        self.current_agent_id = None
        self.current_conversation_id = None
        self.chat_history = []
        self.show_trace = False
        self.show_metrics = False
    
    def start_chat(self, agent_id: str = None, agent_name: str = None, 
                  trace: bool = False, metrics: bool = False,
                  context: Dict[str, Any] = None) -> None:
        """Start a chat session"""
        
        # Set tracing and metrics flags
        self.show_trace = trace
        self.show_metrics = metrics
        
        if self.show_trace:
            self.tracer.set_verbose(True)
        
        # Select agent
        if agent_id:
            if agent_id not in self.multi_agent_system:
                self.console.print(f"[red]Agent {agent_id} not found[/red]")
                return
            self.current_agent_id = agent_id
        elif agent_name:
            # Find agent by name
            for aid, agent_state in self.multi_agent_system.agent_states.items():
                if agent_state.name.lower() == agent_name.lower():
                    self.current_agent_id = aid
                    break
            
            if not self.current_agent_id:
                self.console.print(f"[red]Agent '{agent_name}' not found[/red]")
                return
        else:
            # Use first available agent or prompt user to select
            agents = self.multi_agent_system.list_agents()
            if not agents:
                self.console.print("[red]No agents available[/red]")
                return
            
            if len(agents) == 1:
                self.current_agent_id = agents[0]['agent_id']
            else:
                self.current_agent_id = self._select_agent(agents)
                if not self.current_agent_id:
                    return
        
        # Get agent info
        agent_state = self.multi_agent_system.get_agent_state(self.current_agent_id)
        
        # Start conversation tracking
        self.current_conversation_id = str(uuid.uuid4())
        self.metrics.start_conversation(self.current_agent_id, self.current_conversation_id)
        
        # Add context if provided
        if context:
            for key, value in context.items():
                agent_state.update_context(key, value)
        
        # Display chat header
        self._display_chat_header(agent_state)
        
        # Start chat loop
        self._chat_loop()
    
    def _select_agent(self, agents: List[Dict[str, Any]]) -> Optional[str]:
        """Let user select an agent"""
        self.console.print("\n[bold]Available Agents:[/bold]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("Role", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Workload", style="blue")
        
        for i, agent in enumerate(agents):
            table.add_row(
                str(i + 1),
                agent['name'],
                agent['role'],
                agent['status'],
                f"{agent['workload']:.1%}"
            )
        
        self.console.print(table)
        
        try:
            choice = Prompt.ask("\nSelect agent (number or name)", default="1")
            
            # Try to parse as number
            try:
                index = int(choice) - 1
                if 0 <= index < len(agents):
                    return agents[index]['agent_id']
            except ValueError:
                pass
            
            # Try to match by name
            for agent in agents:
                if agent['name'].lower() == choice.lower():
                    return agent['agent_id']
            
            self.console.print("[red]Invalid selection[/red]")
            return None
            
        except KeyboardInterrupt:
            return None
    
    def _display_chat_header(self, agent_state) -> None:
        """Display chat session header"""
        header_text = f"""
**Agent:** {agent_state.name} ({agent_state.role.value})
**Description:** {agent_state.description or 'No description'}
**Capabilities:** {', '.join(agent_state.capabilities.modalities)}
**Status:** {agent_state.status.value}

Type 'exit' to end chat, 'help' for commands, 'switch' to change agent
"""
        
        if self.show_trace:
            header_text += "\n🧠 **Reasoning trace enabled**"
        
        if self.show_metrics:
            header_text += "\n📊 **Metrics collection enabled**"
        
        panel = Panel(
            Markdown(header_text),
            title="Chat Session Started",
            border_style="green"
        )
        self.console.print(panel)
    
    def _chat_loop(self) -> None:
        """Main chat interaction loop"""
        try:
            while True:
                # Get user input
                try:
                    user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                except KeyboardInterrupt:
                    break
                
                if not user_input.strip():
                    continue
                
                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    break
                elif user_input.lower() == 'help':
                    self._show_chat_help()
                    continue
                elif user_input.lower() == 'switch':
                    self._switch_agent()
                    continue
                elif user_input.lower() == 'status':
                    self._show_agent_status()
                    continue
                elif user_input.lower() == 'trace':
                    self.show_trace = not self.show_trace
                    self.tracer.set_verbose(self.show_trace)
                    self.console.print(f"[yellow]Trace {'enabled' if self.show_trace else 'disabled'}[/yellow]")
                    continue
                elif user_input.lower() == 'metrics':
                    self.show_metrics = not self.show_metrics
                    self.console.print(f"[yellow]Metrics {'enabled' if self.show_metrics else 'disabled'}[/yellow]")
                    continue
                elif user_input.lower() == 'clear':
                    self.console.clear()
                    continue
                
                # Process the message
                self._process_message(user_input)
                
        except KeyboardInterrupt:
            pass
        finally:
            self._end_chat_session()
    
    def _process_message(self, message: str) -> None:
        """Process a user message"""
        import time
        
        start_time = time.time()
        
        # Start reasoning trace if enabled
        trace_id = None
        if self.show_trace:
            trace_id = self.tracer.start_trace(
                task_description=f"Chat message: {message[:50]}...",
                agent_id=self.current_agent_id
            )
            self.tracer.add_thought(trace_id, f"User asked: {message}")
        
        try:
            # Get response from agent
            response = self.multi_agent_system.chat_with_agent(
                self.current_agent_id, 
                message, 
                stream=False
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Display response
            self._display_agent_response(response, response_time)
            
            # Record metrics
            if self.show_metrics:
                # Note: In a real implementation, you'd extract actual token usage from the LLM response
                token_usage = TokenUsage(
                    prompt_tokens=len(message.split()) * 2,  # Rough estimate
                    completion_tokens=len(response.split()) * 2,  # Rough estimate
                    total_tokens=len(message.split()) * 2 + len(response.split()) * 2
                )
                
                self.metrics.record_message(
                    self.current_agent_id,
                    self.current_conversation_id,
                    response_time,
                    token_usage
                )
            
            # Complete reasoning trace
            if trace_id:
                self.tracer.add_observation(trace_id, f"Generated response: {response[:100]}...")
                self.tracer.complete_trace(trace_id, response)
            
            # Add to chat history
            self.chat_history.append({
                'user': message,
                'agent': response,
                'timestamp': time.time(),
                'response_time': response_time
            })
            
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")
            
            if trace_id:
                self.tracer.add_error(trace_id, str(e))
                self.tracer.complete_trace(trace_id, status="failed")
    
    def _display_agent_response(self, response: str, response_time: float) -> None:
        """Display agent response with formatting"""
        agent_state = self.multi_agent_system.get_agent_state(self.current_agent_id)
        
        # Create response panel
        response_text = response
        
        if self.show_metrics:
            response_text += f"\n\n*Response time: {response_time:.2f}s*"
        
        panel = Panel(
            Markdown(response_text),
            title=f"🤖 {agent_state.name}",
            border_style="blue"
        )
        
        self.console.print(panel)
    
    def _show_chat_help(self) -> None:
        """Show chat help"""
        help_text = """
**Chat Commands:**
- `exit`, `quit`, `bye` - End chat session
- `help` - Show this help message
- `switch` - Switch to a different agent
- `status` - Show current agent status
- `trace` - Toggle reasoning trace display
- `metrics` - Toggle metrics collection
- `clear` - Clear the screen

**Tips:**
- Use natural language to interact with the agent
- Agents have different capabilities and specializations
- Enable trace mode to see step-by-step reasoning
"""
        
        panel = Panel(
            Markdown(help_text),
            title="Chat Help",
            border_style="yellow"
        )
        self.console.print(panel)
    
    def _switch_agent(self) -> None:
        """Switch to a different agent"""
        agents = self.multi_agent_system.list_agents()
        
        # Filter out current agent
        other_agents = [a for a in agents if a['agent_id'] != self.current_agent_id]
        
        if not other_agents:
            self.console.print("[yellow]No other agents available[/yellow]")
            return
        
        new_agent_id = self._select_agent(other_agents)
        if new_agent_id:
            # End current conversation
            self.metrics.end_conversation(self.current_agent_id, self.current_conversation_id)
            
            # Switch to new agent
            self.current_agent_id = new_agent_id
            self.current_conversation_id = str(uuid.uuid4())
            self.metrics.start_conversation(self.current_agent_id, self.current_conversation_id)
            
            # Display new agent info
            agent_state = self.multi_agent_system.get_agent_state(self.current_agent_id)
            self._display_chat_header(agent_state)
    
    def _show_agent_status(self) -> None:
        """Show current agent status"""
        agent_state = self.multi_agent_system.get_agent_state(self.current_agent_id)
        
        status_text = f"""
**Agent ID:** {agent_state.agent_id}
**Name:** {agent_state.name}
**Role:** {agent_state.role.value}
**Status:** {agent_state.status.value}
**Current Goals:** {', '.join(agent_state.current_goals) or 'None'}
**Active Tasks:** {len(agent_state.current_tasks)}
**Workload:** {agent_state.get_workload():.1%}
**Success Rate:** {agent_state.metrics.success_rate:.1%}
**Total Messages:** {agent_state.metrics.tasks_completed + agent_state.metrics.tasks_failed}
"""
        
        panel = Panel(
            Markdown(status_text),
            title="Agent Status",
            border_style="cyan"
        )
        self.console.print(panel)
    
    def _end_chat_session(self) -> None:
        """End the chat session"""
        if self.current_conversation_id:
            self.metrics.end_conversation(self.current_agent_id, self.current_conversation_id)
        
        # Show session summary
        if self.chat_history:
            total_messages = len(self.chat_history)
            avg_response_time = sum(h['response_time'] for h in self.chat_history) / total_messages
            
            summary_text = f"""
**Session Summary:**
- Messages exchanged: {total_messages}
- Average response time: {avg_response_time:.2f}s
- Agent: {self.multi_agent_system.get_agent_state(self.current_agent_id).name}
"""
            
            panel = Panel(
                Markdown(summary_text),
                title="Chat Session Ended",
                border_style="red"
            )
            self.console.print(panel)
        
        self.console.print("[dim]Goodbye![/dim]")
    
    def quick_chat(self, message: str, agent_id: str = None, 
                  trace: bool = False) -> str:
        """Send a single message and get response"""
        
        # Select agent
        if agent_id and agent_id in self.multi_agent_system:
            selected_agent_id = agent_id
        else:
            agents = self.multi_agent_system.list_agents()
            if not agents:
                return "No agents available"
            selected_agent_id = agents[0]['agent_id']
        
        # Start conversation tracking
        conversation_id = str(uuid.uuid4())
        self.metrics.start_conversation(selected_agent_id, conversation_id)
        
        # Start trace if requested
        trace_id = None
        if trace:
            trace_id = self.tracer.start_trace(
                task_description=f"Quick chat: {message[:50]}...",
                agent_id=selected_agent_id
            )
        
        try:
            # Get response
            response = self.multi_agent_system.chat_with_agent(
                selected_agent_id, 
                message
            )
            
            # Complete trace
            if trace_id:
                self.tracer.complete_trace(trace_id, response)
            
            # End conversation
            self.metrics.end_conversation(selected_agent_id, conversation_id)
            
            return response
            
        except Exception as e:
            if trace_id:
                self.tracer.add_error(trace_id, str(e))
                self.tracer.complete_trace(trace_id, status="failed")
            
            self.metrics.end_conversation(selected_agent_id, conversation_id, success=False)
            return f"Error: {str(e)}"
    
    def batch_chat(self, messages: List[str], agent_id: str = None) -> List[Dict[str, Any]]:
        """Process multiple messages in batch"""
        results = []
        
        for i, message in enumerate(messages):
            self.console.print(f"[dim]Processing message {i+1}/{len(messages)}...[/dim]")
            
            response = self.quick_chat(message, agent_id)
            results.append({
                'message': message,
                'response': response,
                'index': i
            })
        
        return results
    
    def export_chat_history(self, format: str = "json") -> str:
        """Export chat history in different formats"""
        if not self.chat_history:
            return ""
        
        if format == "json":
            import json
            return json.dumps(self.chat_history, indent=2)
        
        elif format == "markdown":
            lines = ["# Chat History", ""]
            for i, entry in enumerate(self.chat_history, 1):
                lines.append(f"## Message {i}")
                lines.append(f"**User:** {entry['user']}")
                lines.append(f"**Agent:** {entry['agent']}")
                lines.append(f"**Response Time:** {entry['response_time']:.2f}s")
                lines.append("")
            return "\n".join(lines)
        
        elif format == "text":
            lines = []
            for i, entry in enumerate(self.chat_history, 1):
                lines.append(f"=== Message {i} ===")
                lines.append(f"User: {entry['user']}")
                lines.append(f"Agent: {entry['agent']}")
                lines.append(f"Response Time: {entry['response_time']:.2f}s")
                lines.append("")
            return "\n".join(lines)
        
        return str(self.chat_history)

