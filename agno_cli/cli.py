"""
Enhanced Agno CLI with multi-agent capabilities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import typer
import json
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from core.config import Config
from core.session import SessionManager
from agents.multi_agent import MultiAgentSystem
from agents.agent_state import AgentRole, AgentStatus
from reasoning.tracer import ReasoningTracer
from reasoning.metrics import MetricsCollector
from commands.chat_commands import ChatCommands
from tools.search_tools import SearchToolsManager
from tools.financial_tools import FinancialToolsManager
from tools.math_tools import MathToolsManager
from tools.file_system_tools import FileSystemToolsManager
from tools.csv_tools import CSVToolsManager
from tools.pandas_tools import PandasToolsManager
from tools.duckdb_tools import DuckDBToolsManager
from tools.sql_tools import SQLToolsManager, DatabaseConnection
from tools.postgres_tools import PostgresToolsManager, PostgresConnection
from tools.shell_tools import ShellToolsManager
from tools.docker_tools import DockerToolsManager
from tools.wikipedia_tools import WikipediaToolsManager
from tools.arxiv_tools import ArxivToolsManager
from tools.pubmed_tools import PubMedToolsManager
from tools.sleep_tools import SleepToolsManager

# Create the main CLI app
app = typer.Typer(
    name="agno",
    help="Enhanced Agno CLI - Multi-Agent Terminal Assistant",
    add_completion=False
)

# Global instances
console = Console()
config = None
session_manager = None
multi_agent_system = None
tracer = None
metrics = None
chat_commands = None
search_tools = None
financial_tools = None
math_tools = None
file_system_tools = None
csv_tools = None
pandas_tools = None
duckdb_tools = None
sql_tools = None
postgres_tools = None


def initialize_system():
    """Initialize the multi-agent system and tools"""
    global multi_agent_system, tracer, metrics, chat_commands
    global search_tools, financial_tools, math_tools, file_system_tools, csv_tools, pandas_tools, duckdb_tools, sql_tools, postgres_tools, shell_tools, docker_tools, wikipedia_tools, arxiv_tools, pubmed_tools, sleep_tools, config, session_manager
    
    if config is None:
        config = Config()
        session_manager = SessionManager()
    
    if multi_agent_system is None:
        multi_agent_system = MultiAgentSystem(config)
        tracer = ReasoningTracer()
        metrics = MetricsCollector()
        chat_commands = ChatCommands(config, multi_agent_system, tracer, metrics)
        
        # Initialize tool managers
        search_tools = SearchToolsManager({})
        financial_tools = FinancialToolsManager({})
        math_tools = MathToolsManager({})
        file_system_tools = FileSystemToolsManager()
        csv_tools = CSVToolsManager()
        pandas_tools = PandasToolsManager()
        duckdb_tools = DuckDBToolsManager()
        sql_tools = SQLToolsManager(DatabaseConnection(type='sqlite'))
        # Don't initialize PostgreSQL tools immediately - they require a connection
        postgres_tools = None
        shell_tools = ShellToolsManager()
        docker_tools = DockerToolsManager()
        wikipedia_tools = WikipediaToolsManager()
        arxiv_tools = ArxivToolsManager()
        pubmed_tools = PubMedToolsManager()
        sleep_tools = SleepToolsManager()


# Chat Commands
@app.command()
def chat(
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Agent name or ID to chat with"),
    trace: bool = typer.Option(False, "--trace", help="Enable reasoning trace"),
    metrics: bool = typer.Option(False, "--metrics", help="Enable metrics collection"),
    context: Optional[str] = typer.Option(None, "--context", help="JSON context to provide to agent"),
    goal: Optional[str] = typer.Option(None, "--goal", help="Set agent goal"),
    quick: Optional[str] = typer.Option(None, "--quick", "-q", help="Send single message and exit")
):
    """Start an interactive chat session with an agent"""
    initialize_system()
    
    # Parse context if provided
    context_dict = {}
    if context:
        try:
            context_dict = json.loads(context)
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON context[/red]")
            return
    
    if goal:
        context_dict['goal'] = goal
    
    if quick:
        # Quick chat mode
        response = chat_commands.quick_chat(quick, agent, trace)
        console.print(Panel(Markdown(response), title="Response", border_style="blue"))
    else:
        # Interactive chat mode
        chat_commands.start_chat(
            agent_id=agent,
            agent_name=agent,
            trace=trace,
            metrics=metrics,
            context=context_dict
        )


# Agent Management Commands
@app.command()
def agents(
    list_agents: bool = typer.Option(False, "--list", "-l", help="List all agents"),
    create: Optional[str] = typer.Option(None, "--create", help="Create new agent with name"),
    role: Optional[str] = typer.Option("worker", "--role", help="Agent role (leader, worker, contributor, specialist, coordinator, observer)"),
    description: Optional[str] = typer.Option("", "--description", help="Agent description"),
    remove: Optional[str] = typer.Option(None, "--remove", help="Remove agent by ID"),
    status: Optional[str] = typer.Option(None, "--status", help="Show agent status by ID"),
    capabilities: Optional[str] = typer.Option(None, "--capabilities", help="JSON capabilities for new agent")
):
    global multi_agent_system
    """Manage agents in the multi-agent system"""
    initialize_system()
    # --- AGENT STATE PERSISTENCE PATCH START ---
    from pathlib import Path
    AGENT_STATE_PATH = Path(__file__).parent.parent / 'agents_state_agents.json'
    if AGENT_STATE_PATH.exists():
        try:
            # Load the saved state and replace the current system
            # Use the agents file as the base path for loading
            base_path = AGENT_STATE_PATH.parent / 'agents_state.json'
            loaded_system = MultiAgentSystem.load_system_state(base_path, config)
            multi_agent_system = loaded_system
        except Exception as e:
            console.print(f"[red]Failed to load agent state: {e}[/red]")
    # --- AGENT STATE PERSISTENCE PATCH END ---
    
    if list_agents:
        agents = multi_agent_system.list_agents()
        
        if not agents:
            console.print("[yellow]No agents found[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=8)
        table.add_column("Name", style="cyan")
        table.add_column("Role", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Workload", style="blue")
        table.add_column("Success Rate", style="red")
        table.add_column("Capabilities", style="white")
        
        for agent in agents:
            capabilities_str = ", ".join(agent['capabilities']['modalities'])
            table.add_row(
                agent['agent_id'][:8],
                agent['name'],
                agent['role'],
                agent['status'],
                f"{agent['workload']:.1%}",
                f"{agent['metrics']['success_rate']:.1%}",
                capabilities_str
            )
        
        console.print(table)
    
    elif create:
        try:
            # Parse role
            agent_role = AgentRole(role.lower())
            
            # Parse capabilities
            caps = {}
            if capabilities:
                caps = json.loads(capabilities)
            else:
                # Default capabilities based on role
                if agent_role == AgentRole.LEADER:
                    caps = {
                        "tools": ["reasoning_tools", "yfinance_tools"],
                        "skills": ["coordination", "planning", "decision_making"],
                        "modalities": ["text"],
                        "languages": ["english"]
                    }
                else:
                    caps = {
                        "tools": ["reasoning_tools"],
                        "skills": ["analysis", "problem_solving"],
                        "modalities": ["text"],
                        "languages": ["english"]
                    }
            
            agent_id = multi_agent_system.create_agent(
                name=create,
                role=agent_role,
                description=description,
                capabilities=caps
            )
            console.print(f"[green]Created agent '{create}' with ID: {agent_id}[/green]")
            # --- AGENT STATE PERSISTENCE PATCH: Save after create ---
            try:
                multi_agent_system.save_system_state(AGENT_STATE_PATH)
            except Exception as e:
                console.print(f"[red]Failed to save agent state: {e}[/red]")
            # --- END PATCH ---
        except ValueError as e:
            console.print(f"[red]Error creating agent: {e}[/red]")
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON capabilities[/red]")
    
    elif remove:
        try:
            if multi_agent_system.remove_agent(remove):
                console.print(f"[green]Removed agent {remove}[/green]")
                # --- AGENT STATE PERSISTENCE PATCH: Save after remove ---
                try:
                    multi_agent_system.save_system_state(AGENT_STATE_PATH)
                except Exception as e:
                    console.print(f"[red]Failed to save agent state: {e}[/red]")
                # --- END PATCH ---
            else:
                console.print(f"[red]Agent {remove} not found[/red]")
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
    
    elif status:
        agent_state = multi_agent_system.get_agent_state(status)
        if not agent_state:
            console.print(f"[red]Agent {status} not found[/red]")
            return
        
        status_text = f"""
**Agent ID:** {agent_state.agent_id}
**Name:** {agent_state.name}
**Role:** {agent_state.role.value}
**Status:** {agent_state.status.value}
**Description:** {agent_state.description or 'No description'}
**Created:** {agent_state.created_at.strftime('%Y-%m-%d %H:%M:%S')}
**Updated:** {agent_state.updated_at.strftime('%Y-%m-%d %H:%M:%S')}

**Current Goals:** {', '.join(agent_state.current_goals) or 'None'}
**Active Tasks:** {len(agent_state.current_tasks)}
**Workload:** {agent_state.get_workload():.1%}

**Capabilities:**
- Tools: {', '.join(agent_state.capabilities.tools) or 'None'}
- Skills: {', '.join(agent_state.capabilities.skills) or 'None'}
- Modalities: {', '.join(agent_state.capabilities.modalities) or 'None'}
- Languages: {', '.join(agent_state.capabilities.languages) or 'None'}

**Metrics:**
- Tasks Completed: {agent_state.metrics.tasks_completed}
- Tasks Failed: {agent_state.metrics.tasks_failed}
- Success Rate: {agent_state.metrics.success_rate:.1%}
- Total Tokens: {agent_state.metrics.total_tokens_used}
"""
        
        panel = Panel(
            Markdown(status_text),
            title=f"Agent Status: {agent_state.name}",
            border_style="cyan"
        )
        console.print(panel)
    
    else:
        console.print("[yellow]Use --list to see agents or --create to make a new one[/yellow]")


# Team Management Commands
@app.command()
def team(
    status: bool = typer.Option(False, "--status", help="Show team status"),
    message: Optional[str] = typer.Option(None, "--message", help="Send message to team"),
    task: Optional[str] = typer.Option(None, "--task", help="Assign task to team"),
    priority: Optional[str] = typer.Option("normal", "--priority", help="Task priority (low, normal, high, urgent, critical)"),
    requirements: Optional[str] = typer.Option(None, "--requirements", help="JSON task requirements")
):
    """Manage team operations and coordination"""
    initialize_system()
    
    if status:
        team_status = multi_agent_system.get_system_status()
        
        status_text = f"""
**System ID:** {team_status['system_id']}
**Total Agents:** {team_status['team_status']['total_agents']}
**Active Agents:** {team_status['team_status']['active_agents']}
**Idle Agents:** {team_status['team_status']['idle_agents']}

**Tasks:**
- Pending: {team_status['team_status']['pending_tasks']}
- Active: {team_status['team_status']['active_tasks']}
- Completed: {team_status['team_status']['completed_tasks']}

**Communication:**
- Total Messages: {team_status['team_status']['total_messages']}
- Uptime: {team_status['team_status']['uptime']:.1f}s

**Configuration:**
- Model Provider: {team_status['configuration']['model_provider']}
- Model ID: {team_status['configuration']['model_id']}
"""
        
        panel = Panel(
            Markdown(status_text),
            title="Team Status",
            border_style="green"
        )
        console.print(panel)
    
    elif message:
        # Broadcast message to all agents
        leader_agents = [a for a in multi_agent_system.list_agents() if a['role'] == 'leader']
        if leader_agents:
            from_agent = leader_agents[0]['agent_id']
        else:
            from_agent = "system"
        
        message_ids = multi_agent_system.broadcast_message(from_agent, message)
        console.print(f"[green]Broadcast message sent to {len(message_ids)} agents[/green]")
    
    elif task:
        # Parse priority
        from .agents.orchestrator import TaskPriority
        priority_map = {
            'low': TaskPriority.LOW,
            'normal': TaskPriority.NORMAL,
            'high': TaskPriority.HIGH,
            'urgent': TaskPriority.URGENT,
            'critical': TaskPriority.CRITICAL
        }
        
        task_priority = priority_map.get(priority.lower(), TaskPriority.NORMAL)
        
        # Parse requirements
        task_requirements = {}
        if requirements:
            try:
                task_requirements = json.loads(requirements)
            except json.JSONDecodeError:
                console.print("[red]Invalid JSON requirements[/red]")
                return
        
        # Assign task
        task_id = multi_agent_system.assign_task(
            description=task,
            requirements=task_requirements,
            priority=task_priority
        )
        
        console.print(f"[green]Task assigned with ID: {task_id}[/green]")
    
    else:
        console.print("[yellow]Use --status, --message, or --task[/yellow]")


# Tool Commands
@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    engine: Optional[str] = typer.Option(None, "--engine", "-e", help="Search engine to use"),
    num_results: int = typer.Option(10, "--num", "-n", help="Number of results"),
    multi: bool = typer.Option(False, "--multi", help="Search with multiple engines"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json, markdown)")
):
    """Search the web using various search engines"""
    initialize_system()
    
    try:
        if multi:
            results = search_tools.search_and_aggregate(query, num_results_per_engine=num_results//2)
        else:
            results = search_tools.search(query, engine, num_results)
        
        if not results:
            console.print("[yellow]No results found[/yellow]")
            return
        
        if format == "table":
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Rank", style="dim", width=4)
            table.add_column("Title", style="cyan")
            table.add_column("URL", style="blue")
            table.add_column("Source", style="green")
            
            for result in results[:10]:  # Limit display
                table.add_row(
                    str(result.rank),
                    result.title[:50] + "..." if len(result.title) > 50 else result.title,
                    result.url[:40] + "..." if len(result.url) > 40 else result.url,
                    result.source
                )
            
            console.print(table)
        
        elif format == "json":
            console.print(search_tools.export_results(results, "json"))
        
        elif format == "markdown":
            console.print(search_tools.export_results(results, "markdown"))
        
    except Exception as e:
        console.print(f"[red]Search error: {e}[/red]")


@app.command()
def finance(
    symbol: str = typer.Argument(..., help="Stock symbol"),
    action: str = typer.Option("info", "--action", "-a", help="Action: info, news, history, analysis"),
    period: str = typer.Option("1y", "--period", "-p", help="Time period for historical data"),
    summary: bool = typer.Option(False, "--summary", help="Show summary information")
):
    """Financial data analysis and stock information"""
    initialize_system()
    
    try:
        if action == "info":
            stock_info = financial_tools.get_stock_info(symbol)
            if not stock_info:
                console.print(f"[red]Stock {symbol} not found[/red]")
                return
            
            info_text = f"""
**{stock_info.name} ({stock_info.symbol})**

**Price:** ${stock_info.price:.2f}
**Change:** ${stock_info.change:.2f} ({stock_info.change_percent:.2f}%)
**Volume:** {stock_info.volume:,}
**Market Cap:** {'${:,.0f}'.format(stock_info.market_cap) if stock_info.market_cap is not None else 'N/A'}
**P/E Ratio:** {'{:.2f}'.format(stock_info.pe_ratio) if stock_info.pe_ratio is not None else 'N/A'}
**52W High:** {'${:.2f}'.format(stock_info.fifty_two_week_high) if stock_info.fifty_two_week_high is not None else 'N/A'}
**52W Low:** {'${:.2f}'.format(stock_info.fifty_two_week_low) if stock_info.fifty_two_week_low is not None else 'N/A'}
"""
            
            panel = Panel(
                Markdown(info_text),
                title=f"Stock Information: {symbol.upper()}",
                border_style="green"
            )
            console.print(panel)
        
        elif action == "news":
            news_items = financial_tools.get_stock_news(symbol, limit=5)
            if not news_items:
                console.print(f"[yellow]No news found for {symbol}[/yellow]")
                return
            
            for i, news in enumerate(news_items, 1):
                news_text = f"""
**{news.title}**
{news.summary}
*Source: {news.source} | Published: {news.published.strftime('%Y-%m-%d %H:%M')}*
[Read more]({news.url})
"""
                panel = Panel(
                    Markdown(news_text),
                    title=f"News {i}",
                    border_style="blue"
                )
                console.print(panel)
        
        elif action == "analysis":
            returns = financial_tools.calculate_returns(symbol, period)
            if not returns:
                console.print(f"[red]Could not analyze {symbol}[/red]")
                return
            
            analysis_text = f"""
**Performance Analysis for {symbol.upper()}**

**Period:** {period}
**Total Return:** {returns['total_return']:.2%}
**Annualized Return:** {returns['annualized_return']:.2%}
**Volatility:** {returns['volatility']:.2%}
**Sharpe Ratio:** {returns['sharpe_ratio']:.2f}
**Max Drawdown:** {returns['max_drawdown']:.2%}
**Best Day:** {returns['best_day']:.2%}
**Worst Day:** {returns['worst_day']:.2%}
"""
            
            panel = Panel(
                Markdown(analysis_text),
                title=f"Analysis: {symbol.upper()}",
                border_style="cyan"
            )
            console.print(panel)
        
    except Exception as e:
        console.print(f"[red]Finance error: {e}[/red]")


@app.command()
def calc(
    expression: str = typer.Argument(..., help="Mathematical expression to evaluate"),
    steps: bool = typer.Option(False, "--steps", help="Show calculation steps"),
    variable: Optional[str] = typer.Option(None, "--var", help="Set variable (format: name=value)"),
    list_vars: bool = typer.Option(False, "--list-vars", help="List all variables")
):
    """Mathematical calculator with advanced functions"""
    initialize_system()
    
    try:
        if list_vars:
            variables = math_tools.list_variables()
            if variables:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Variable", style="cyan")
                table.add_column("Value", style="green")
                
                for name, value in variables.items():
                    table.add_row(name, str(value))
                
                console.print(table)
            else:
                console.print("[yellow]No variables set[/yellow]")
            return
        
        if variable:
            try:
                name, value = variable.split('=')
                math_tools.set_variable(name.strip(), float(value.strip()))
                console.print(f"[green]Set {name} = {value}[/green]")
                return
            except ValueError:
                console.print("[red]Invalid variable format. Use: name=value[/red]")
                return
        
        result = math_tools.calculate(expression, steps)
        
        if result.error:
            console.print(f"[red]Error: {result.error}[/red]")
            return
        
        result_text = f"**Expression:** {result.expression}\n**Result:** {result.result}"
        
        if result.steps and steps:
            result_text += "\n\n**Steps:**\n" + "\n".join(f"{i+1}. {step}" for i, step in enumerate(result.steps))
        
        panel = Panel(
            Markdown(result_text),
            title="Calculation Result",
            border_style="green"
        )
        console.print(panel)
        
    except Exception as e:
        console.print(f"[red]Calculation error: {e}[/red]")


# Trace Commands
@app.command()
def trace(
    list_traces: bool = typer.Option(False, "--list", "-l", help="List recent traces"),
    show: Optional[str] = typer.Option(None, "--show", help="Show trace by ID"),
    export: Optional[str] = typer.Option(None, "--export", help="Export trace by ID"),
    format: str = typer.Option("markdown", "--format", "-f", help="Export format (json, markdown, text)"),
    clear: bool = typer.Option(False, "--clear", help="Clear old traces"),
    stats: bool = typer.Option(False, "--stats", help="Show tracer statistics")
):
    """Manage reasoning traces"""
    initialize_system()
    
    if list_traces:
        traces = tracer.list_traces(limit=20)
        
        if not traces:
            console.print("[yellow]No traces found[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=8)
        table.add_column("Task", style="cyan")
        table.add_column("Agent", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Steps", style="blue")
        table.add_column("Duration", style="red")
        table.add_column("Created", style="white")
        
        for trace in traces:
            duration = f"{trace['duration']:.2f}s" if trace.get('duration') else "Active"
            table.add_row(
                trace['trace_id'][:8],
                trace['task_description'][:30] + "..." if len(trace['task_description']) > 30 else trace['task_description'],
                trace['agent_id'][:8] if trace['agent_id'] else "N/A",
                trace['status'],
                str(trace['steps_count']),
                duration,
                trace['created_at'][:19]
            )
        
        console.print(table)
    
    elif show:
        summary = tracer.get_trace_summary(show)
        if not summary:
            console.print(f"[red]Trace {show} not found[/red]")
            return
        
        duration_text = f"{summary['duration']:.2f}s" if summary['duration'] else 'Active'
        summary_text = f"""
**Trace ID:** {summary['trace_id']}
**Task:** {summary['task_description']}
**Agent:** {summary['agent_id'] or 'N/A'}
**Status:** {summary['status']}
**Created:** {summary['created_at']}
**Duration:** {duration_text}
**Total Steps:** {summary['total_steps']}

**Step Breakdown:**
"""
        
        for step_type, count in summary['step_counts'].items():
            summary_text += f"- {step_type.title()}: {count}\n"
        
        if summary['final_result']:
            summary_text += f"\n**Final Result:** {summary['final_result'][:200]}..."
        
        panel = Panel(
            Markdown(summary_text),
            title=f"Trace Summary: {show[:8]}",
            border_style="cyan"
        )
        console.print(panel)
    
    elif export:
        exported = tracer.export_trace(export, format)
        if exported:
            console.print(exported)
        else:
            console.print(f"[red]Could not export trace {export}[/red]")
    
    elif clear:
        cleared = tracer.clear_traces(keep_recent=10)
        console.print(f"[green]Cleared {cleared} old traces[/green]")
    
    elif stats:
        stats = tracer.get_stats()
        
        stats_text = f"""
**Tracer Statistics**

**Active Traces:** {stats['active_traces']}
**Total Traces in History:** {stats['total_traces_in_history']}
**Traces Directory:** {stats['traces_directory']}
**Auto Save:** {'Enabled' if stats['auto_save_enabled'] else 'Disabled'}
**Verbose Output:** {'Enabled' if stats['verbose_output'] else 'Disabled'}
**Max Active Traces:** {stats['max_active_traces']}
"""
        
        panel = Panel(
            Markdown(stats_text),
            title="Tracer Statistics",
            border_style="blue"
        )
        console.print(panel)
    
    else:
        console.print("[yellow]Use --list, --show, --export, --clear, or --stats[/yellow]")


# Metrics Commands
@app.command()
def metrics(
    summary: bool = typer.Option(False, "--summary", help="Show system metrics summary"),
    agent: Optional[str] = typer.Option(None, "--agent", help="Show metrics for specific agent"),
    leaderboard: Optional[str] = typer.Option(None, "--leaderboard", help="Show leaderboard by metric"),
    export: bool = typer.Option(False, "--export", help="Export metrics"),
    format: str = typer.Option("json", "--format", "-f", help="Export format (json, csv)"),
    clear: bool = typer.Option(False, "--clear", help="Clear old metrics")
):
    """View and manage performance metrics"""
    initialize_system()
    
    if summary:
        system_summary = metrics.get_system_summary()
        
        summary_text = f"""
**System Metrics Summary**

**System Uptime:** {system_summary['system_uptime']:.1f}s
**Total Agents:** {system_summary['total_agents']}
**Total Conversations:** {system_summary['total_conversations']}
**Total Messages:** {system_summary['total_messages']}
**Average Response Time:** {system_summary['system_avg_response_time']:.2f}s
**Average Confidence:** {system_summary['system_avg_confidence']:.2f}
**Total Tokens Used:** {system_summary['total_token_usage']['total_tokens']:,}
"""
        
        panel = Panel(
            Markdown(summary_text),
            title="System Metrics",
            border_style="green"
        )
        console.print(panel)
    
    elif agent:
        agent_summary = metrics.get_agent_summary(agent)
        if not agent_summary:
            console.print(f"[red]No metrics found for agent {agent}[/red]")
            return
        
        summary_text = f"""
**Agent Metrics: {agent}**

**Total Conversations:** {agent_summary['total_conversations']}
**Successful Conversations:** {agent_summary['successful_conversations']}
**Success Rate:** {agent_summary['success_rate']:.1%}
**Total Messages:** {agent_summary['total_messages']}
**Average Response Time:** {agent_summary['average_response_time']:.2f}s
**Average Confidence:** {agent_summary['average_confidence']:.2f}
**Active Conversations:** {agent_summary['active_conversations']}
**Total Tokens Used:** {agent_summary['token_usage']['total_tokens']:,}
"""
        
        panel = Panel(
            Markdown(summary_text),
            title=f"Agent Metrics: {agent}",
            border_style="cyan"
        )
        console.print(panel)
    
    elif leaderboard:
        leaders = metrics.get_leaderboard(leaderboard, limit=10)
        
        if not leaders:
            console.print("[yellow]No metrics available for leaderboard[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="dim", width=4)
        table.add_column("Agent", style="cyan")
        table.add_column("Metric Value", style="green")
        table.add_column("Conversations", style="blue")
        table.add_column("Success Rate", style="yellow")
        
        for i, leader in enumerate(leaders, 1):
            metric_value = leader.get(leaderboard, 0)
            if isinstance(metric_value, float):
                if leaderboard in ['success_rate', 'average_confidence']:
                    metric_display = f"{metric_value:.1%}"
                else:
                    metric_display = f"{metric_value:.2f}"
            else:
                metric_display = str(metric_value)
            
            table.add_row(
                str(i),
                leader['agent_id'][:8],
                metric_display,
                str(leader['total_conversations']),
                f"{leader['success_rate']:.1%}"
            )
        
        console.print(table)
    
    elif export:
        exported = metrics.export_metrics(agent, format)
        console.print(exported)
    
    elif clear:
        cleared = metrics.clear_metrics(agent, older_than_days=30)
        console.print(f"[green]Cleared {cleared} old metric entries[/green]")
    
    else:
        console.print("[yellow]Use --summary, --agent, --leaderboard, --export, or --clear[/yellow]")


# Configuration Commands
@app.command()
def configure(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    set_key: Optional[str] = typer.Option(None, "--set", help="Set configuration key=value"),
    provider: Optional[str] = typer.Option(None, "--provider", help="Set model provider"),
    model: Optional[str] = typer.Option(None, "--model", help="Set model ID"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Set API key"),
    reset: bool = typer.Option(False, "--reset", help="Reset to default configuration")
):
    """Configure the Agno CLI settings"""
    initialize_system()  # Ensure system is initialized before configuring
    if show:
        config_text = f"""
**Current Configuration**

**Model Provider:** {config.model.provider}
**Model ID:** {config.model.model_id}
**Temperature:** {config.model.temperature}
**Max Tokens:** {config.model.max_tokens}
**API Key Set:** {'Yes' if config.get_api_key() else 'No'}

**Directories:**
- Config: {config.cli.config_dir}
- Sessions: {config.cli.session_dir}
- Logs: {config.cli.logs_dir}
"""
        
        panel = Panel(
            Markdown(config_text),
            title="Configuration",
            border_style="blue"
        )
        console.print(panel)
    
    elif set_key:
        try:
            key, value = set_key.split('=', 1)
            config.set(key.strip(), value.strip())
            config.save()
            console.print(f"[green]Set {key} = {value}[/green]")
        except ValueError:
            console.print("[red]Invalid format. Use: key=value[/red]")
    
    elif provider:
        config.model.provider = provider
        config.save()
        console.print(f"[green]Set provider to {provider}[/green]")
    
    elif model:
        config.model.model_id = model
        config.save()
        console.print(f"[green]Set model to {model}[/green]")
    
    elif api_key:
        config.set_api_key(api_key)
        config.save()
        console.print("[green]API key updated[/green]")
    
    elif reset:
        if typer.confirm("Reset configuration to defaults?"):
            config.reset_to_defaults()
            config.save()
            console.print("[green]Configuration reset to defaults[/green]")
    
    else:
        console.print("[yellow]Use --show, --set, --provider, --model, --api-key, or --reset[/yellow]")


# File System Commands
@app.command()
def files(
    list: bool = typer.Option(False, "--list", "-l", help="List directory contents"),
    read: Optional[str] = typer.Option(None, "--read", "-r", help="Read file contents"),
    write: Optional[str] = typer.Option(None, "--write", "-w", help="Write content to file"),
    delete: Optional[str] = typer.Option(None, "--delete", "-d", help="Delete file or directory"),
    info: Optional[str] = typer.Option(None, "--info", "-i", help="Get file information"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search for files"),
    create_dir: Optional[str] = typer.Option(None, "--mkdir", help="Create directory"),
    copy: Optional[str] = typer.Option(None, "--copy", help="Copy file (format: source:destination)"),
    move: Optional[str] = typer.Option(None, "--move", help="Move file (format: source:destination)"),
    show_hidden: bool = typer.Option(False, "--hidden", help="Show hidden files"),
    recursive: bool = typer.Option(False, "--recursive", help="Recursive operations"),
    tree: bool = typer.Option(False, "--tree", help="Display directory tree"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json, tree)"),
    encoding: str = typer.Option("utf-8", "--encoding", help="File encoding"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing files"),
    confirm: bool = typer.Option(True, "--confirm/--no-confirm", help="Confirm deletions"),
    content: Optional[str] = typer.Option(None, "--content", help="Content to write to file")
):
    """File system operations - list, read, write, delete, search files"""
    initialize_system()
    
    try:
        if list:
            file_system_tools.list_directory(
                path=".",
                show_hidden=show_hidden,
                recursive=recursive,
                format=format
            )
        
        elif read:
            file_system_tools.read_file(
                path=read,
                encoding=encoding,
                format=format
            )
        
        elif write:
            if not content:
                console.print("[red]Content required for write operation. Use --content[/red]")
                return
            
            file_system_tools.write_file(
                path=write,
                content=content,
                encoding=encoding,
                overwrite=overwrite
            )
        
        elif delete:
            file_system_tools.delete_file(
                path=delete,
                recursive=recursive,
                confirm=confirm
            )
        
        elif info:
            file_system_tools.get_file_info(
                path=info,
                format=format
            )
        
        elif search:
            file_system_tools.search_files(
                pattern=search,
                recursive=recursive
            )
        
        elif create_dir:
            result = file_system_tools.fs_tools.create_directory(create_dir, parents=True)
            if result.success:
                console.print(f"[green]{result.message}[/green]")
            else:
                console.print(f"[red]{result.message}[/red]")
        
        elif copy:
            try:
                source, destination = copy.split(':', 1)
                result = file_system_tools.fs_tools.copy_file(source.strip(), destination.strip(), overwrite)
                if result.success:
                    console.print(f"[green]{result.message}[/green]")
                else:
                    console.print(f"[red]{result.message}[/red]")
            except ValueError:
                console.print("[red]Invalid copy format. Use: source:destination[/red]")
        
        elif move:
            try:
                source, destination = move.split(':', 1)
                result = file_system_tools.fs_tools.move_file(source.strip(), destination.strip(), overwrite)
                if result.success:
                    console.print(f"[green]{result.message}[/green]")
                else:
                    console.print(f"[red]{result.message}[/red]")
            except ValueError:
                console.print("[red]Invalid move format. Use: source:destination[/red]")
        
        elif tree:
            tree_display = file_system_tools.fs_tools.display_directory_tree(
                path=".",
                show_hidden=show_hidden
            )
            console.print(Panel(tree_display, title="Directory Tree", border_style="green"))
        
        else:
            console.print("[yellow]Use --list, --read, --write, --delete, --info, --search, --mkdir, --copy, --move, or --tree[/yellow]")
    
    except Exception as e:
        console.print(f"[red]File system error: {e}[/red]")


# CSV Commands
@app.command()
def csv(
    read: Optional[str] = typer.Option(None, "--read", "-r", help="Read CSV file"),
    write: Optional[str] = typer.Option(None, "--write", "-w", help="Write CSV file"),
    info: Optional[str] = typer.Option(None, "--info", "-i", help="Get CSV file information"),
    analyze: Optional[str] = typer.Option(None, "--analyze", "-a", help="Analyze CSV data"),
    filter: Optional[str] = typer.Option(None, "--filter", "-f", help="Filter CSV data (JSON format)"),
    sort: Optional[str] = typer.Option(None, "--sort", "-s", help="Sort CSV by columns (comma-separated)"),
    merge: Optional[str] = typer.Option(None, "--merge", "-m", help="Merge CSV files (format: file1:file2:key)"),
    convert: Optional[str] = typer.Option(None, "--convert", "-c", help="Convert CSV to other format (format: input:output:type)"),
    encoding: str = typer.Option("utf-8", "--encoding", help="File encoding"),
    delimiter: str = typer.Option(",", "--delimiter", help="CSV delimiter"),
    max_rows: Optional[int] = typer.Option(None, "--max-rows", help="Maximum rows to read"),
    sample: bool = typer.Option(False, "--sample", help="Show sample of data"),
    sample_size: int = typer.Option(10, "--sample-size", help="Number of sample rows"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("table", "--format", help="Output format (table, json)"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing files"),
    ascending: Optional[str] = typer.Option(None, "--ascending", help="Sort order (comma-separated booleans)")
):
    """CSV file operations - read, write, analyze, filter, sort, merge, convert"""
    initialize_system()
    
    try:
        # Handle filter operation first if both read and filter are specified
        if read and filter:
            try:
                filters = json.loads(filter)
                csv_tools.filter_csv(
                    path=read,
                    filters=filters,
                    output_path=output
                )
                return
            except json.JSONDecodeError:
                console.print("[red]Invalid JSON format for filters[/red]")
                return
        
        # Handle sort operation if both read and sort are specified
        if read and sort:
            sort_columns = [col.strip() for col in sort.split(",")]
            ascending_list = None
            if ascending:
                ascending_list = [bool(int(x.strip())) for x in ascending.split(",")]
            
            csv_tools.sort_csv(
                path=read,
                sort_columns=sort_columns,
                ascending=ascending_list,
                output_path=output
            )
            return
        
        if read:
            csv_tools.read_csv(
                path=read,
                encoding=encoding,
                delimiter=delimiter,
                max_rows=max_rows,
                sample=sample,
                sample_size=sample_size,
                format=format
            )
        
        elif write:
            # For write, we need data - this would typically come from another operation
            # For now, we'll create a sample dataset
            sample_data = [
                {"name": "John", "age": 30, "city": "New York"},
                {"name": "Jane", "age": 25, "city": "Los Angeles"},
                {"name": "Bob", "age": 35, "city": "Chicago"}
            ]
            csv_tools.write_csv(
                path=write,
                data=sample_data,
                encoding=encoding,
                delimiter=delimiter,
                overwrite=overwrite
            )
        
        elif info:
            csv_tools.get_csv_info(
                path=info,
                format=format
            )
        
        elif analyze:
            csv_tools.analyze_csv(
                path=analyze,
                format=format
            )
        

        
        elif merge:
            # Parse merge parameters: file1:file2:key
            parts = merge.split(":")
            if len(parts) >= 3:
                file1, file2, merge_key = parts[0], parts[1], parts[2]
                csv_tools.merge_csv(
                    file1=file1,
                    file2=file2,
                    merge_key=merge_key,
                    output_path=output
                )
            else:
                console.print("[red]Merge format should be: file1:file2:key[/red]")
        
        elif convert:
            # Parse convert parameters: input:output:type
            parts = convert.split(":")
            if len(parts) >= 3:
                input_path, output_path, convert_type = parts[0], parts[1], parts[2]
                csv_tools.convert_format(
                    input_path=input_path,
                    output_path=output_path,
                    output_format=convert_type
                )
            else:
                console.print("[red]Convert format should be: input:output:type[/red]")
        
        else:
            console.print("[yellow]No operation specified. Use --help for available options.[/yellow]")
    
    except Exception as e:
        console.print(f"[red]CSV operation error: {e}[/red]")


# Pandas Commands
@app.command()
def pandas(
    read: Optional[str] = typer.Option(None, "--read", "-r", help="Read data file"),
    write: Optional[str] = typer.Option(None, "--write", "-w", help="Write data to file"),
    analyze: Optional[str] = typer.Option(None, "--analyze", "-a", help="Analyze data (file path or current data)"),
    clean: Optional[str] = typer.Option(None, "--clean", help="Clean data (JSON operations)"),
    transform: Optional[str] = typer.Option(None, "--transform", help="Transform data (JSON operations)"),
    visualize: Optional[str] = typer.Option(None, "--visualize", help="Create visualization (JSON config)"),
    show: Optional[int] = typer.Option(None, "--show", "-s", help="Show data preview (number of rows)"),
    format: str = typer.Option("csv", "--format", help="File format (csv, json, excel, parquet)"),
    output_format: str = typer.Option("table", "--output-format", help="Output format (table, json)"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path")
):
    """Advanced data manipulation and analysis with pandas"""
    initialize_system()
    
    try:
        if read:
            pandas_tools.read_data(
                path=read,
                format=format
            )
        
        if show:
            if pandas_tools.current_dataframe is None:
                console.print("[red]No data loaded. Use --read to load data first.[/red]")
                return
            pandas_tools.show_data(rows=show, format=output_format)
        
        elif write:
            if pandas_tools.current_dataframe is None:
                console.print("[red]No data loaded. Use --read to load data first.[/red]")
                return
            
            pandas_tools.write_data(
                path=write,
                format=format
            )
        
        elif analyze:
            if analyze and analyze != "":  # If file path provided
                pandas_tools.read_data(analyze, format)
            elif pandas_tools.current_dataframe is None:
                console.print("[red]No data loaded. Use --read to load data first.[/red]")
                return
            pandas_tools.analyze_data(format=output_format)
        
        elif clean:
            try:
                operations = json.loads(clean)
                pandas_tools.clean_data(operations)
            except json.JSONDecodeError:
                console.print("[red]Invalid JSON format for clean operations[/red]")
        
        elif transform:
            try:
                operations = json.loads(transform)
                pandas_tools.transform_data(operations)
            except json.JSONDecodeError:
                console.print("[red]Invalid JSON format for transform operations[/red]")
        
        elif visualize:
            try:
                plot_config = json.loads(visualize)
                pandas_tools.create_visualization(plot_config, output_path)
            except json.JSONDecodeError:
                console.print("[red]Invalid JSON format for visualization config[/red]")
        
        elif show:
            pandas_tools.show_data(rows=show, format=output_format)
        
        else:
            console.print("[yellow]No operation specified. Use --help for available options.[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Pandas operation error: {e}[/red]")


# DuckDB Commands
@app.command()
def duckdb(
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Execute SQL query"),
    create_table: Optional[str] = typer.Option(None, "--create-table", help="Create table (format: name:schema_json)"),
    import_csv: Optional[str] = typer.Option(None, "--import", help="Import CSV file (format: file:table)"),
    export_csv: Optional[str] = typer.Option(None, "--export", help="Export table to CSV (format: table:file)"),
    show_table: Optional[str] = typer.Option(None, "--show-table", help="Show table information"),
    list_tables: bool = typer.Option(False, "--list", "-l", help="List all tables"),
    database_info: bool = typer.Option(False, "--info", "-i", help="Show database information"),
    backup: Optional[str] = typer.Option(None, "--backup", help="Backup database to file"),
    restore: Optional[str] = typer.Option(None, "--restore", help="Restore database from backup"),
    optimize: bool = typer.Option(False, "--optimize", help="Optimize database performance"),
    database: Optional[str] = typer.Option(None, "--database", "-d", help="Database file path (default: memory)"),
    memory: bool = typer.Option(True, "--memory/--file", help="Use in-memory database"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json)")
):
    """Lightweight database operations with DuckDB"""
    initialize_system()
    
    try:
        # Initialize database connection if different from default
        if database and not memory:
            duckdb_tools = DuckDBToolsManager(database, memory_mode=False)
        else:
            duckdb_tools = DuckDBToolsManager()
        
        if query:
            duckdb_tools.execute_query(query, format=format)
        
        elif create_table:
            try:
                table_name, schema_json = create_table.split(':', 1)
                schema = json.loads(schema_json)
                duckdb_tools.create_table(table_name, schema)
            except (ValueError, json.JSONDecodeError):
                console.print("[red]Invalid create-table format. Use: name:schema_json[/red]")
        
        elif import_csv:
            try:
                file_path, table_name = import_csv.split(':', 1)
                duckdb_tools.import_csv(file_path, table_name)
            except ValueError:
                console.print("[red]Invalid import format. Use: file:table[/red]")
        
        elif export_csv:
            try:
                table_name, file_path = export_csv.split(':', 1)
                duckdb_tools.export_csv(table_name, file_path)
            except ValueError:
                console.print("[red]Invalid export format. Use: table:file[/red]")
        
        elif show_table:
            duckdb_tools.show_table_info(show_table, format=format)
        
        elif list_tables:
            duckdb_tools.list_tables(format=format)
        
        elif database_info:
            duckdb_tools.show_database_info(format=format)
        
        elif backup:
            duckdb_tools.backup_database(backup)
        
        elif restore:
            duckdb_tools.restore_database(restore)
        
        elif optimize:
            duckdb_tools.optimize_database()
        
        else:
            console.print("[yellow]No operation specified. Use --help for available options.[/yellow]")
        
        # Close connection if we created a new one
        if database and not memory:
            duckdb_tools.close()
    
    except Exception as e:
        console.print(f"[red]DuckDB operation error: {e}[/red]")


# SQL Commands
@app.command()
def sql(
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Execute SQL query"),
    script: Optional[str] = typer.Option(None, "--script", "-s", help="Execute SQL script file"),
    show_table: Optional[str] = typer.Option(None, "--show-table", help="Show table information"),
    list_tables: bool = typer.Option(False, "--list", "-l", help="List all tables"),
    database_info: bool = typer.Option(False, "--info", "-i", help="Show database information"),
    backup: Optional[str] = typer.Option(None, "--backup", help="Backup database to file"),
    database_type: str = typer.Option("sqlite", "--type", help="Database type (sqlite, mysql, postgresql)"),
    host: Optional[str] = typer.Option(None, "--host", help="Database host"),
    port: Optional[int] = typer.Option(None, "--port", help="Database port"),
    database: Optional[str] = typer.Option(None, "--database", "-d", help="Database name"),
    username: Optional[str] = typer.Option(None, "--username", "-u", help="Database username"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="Database password"),
    file_path: Optional[str] = typer.Option(None, "--file", "-f", help="SQLite database file path"),
    format: str = typer.Option("table", "--format", help="Output format (table, json)")
):
    """General SQL query execution with multiple database backends"""
    initialize_system()
    
    try:
        # Create database connection configuration
        connection_config = DatabaseConnection(
            type=database_type,
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
            file_path=file_path
        )
        
        # Initialize SQL tools with connection
        sql_tools = SQLToolsManager(connection_config)
        
        if query:
            sql_tools.execute_query(query, format=format)
        
        elif script:
            # Read script file
            try:
                with open(script, 'r') as f:
                    script_content = f.read()
                sql_tools.execute_script(script_content, format=format)
            except FileNotFoundError:
                console.print(f"[red]Script file not found: {script}[/red]")
            except Exception as e:
                console.print(f"[red]Error reading script file: {e}[/red]")
        
        elif show_table:
            sql_tools.show_table_info(show_table, format=format)
        
        elif list_tables:
            sql_tools.list_tables(format=format)
        
        elif database_info:
            sql_tools.show_database_info(format=format)
        
        elif backup:
            sql_tools.backup_database(backup)
        
        else:
            console.print("[yellow]No operation specified. Use --help for available options.[/yellow]")
        
        # Close connection
        sql_tools.close()
    
    except Exception as e:
        console.print(f"[red]SQL operation error: {e}[/red]")


# PostgreSQL Commands
@app.command()
def postgres(
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Execute PostgreSQL query"),
    script: Optional[str] = typer.Option(None, "--script", "-s", help="Execute PostgreSQL script file"),
    show_table: Optional[str] = typer.Option(None, "--show-table", help="Show table information"),
    list_tables: bool = typer.Option(False, "--list", "-l", help="List all tables"),
    list_schemas: bool = typer.Option(False, "--schemas", help="List all schemas"),
    database_info: bool = typer.Option(False, "--info", "-i", help="Show database information"),
    show_indexes: Optional[str] = typer.Option(None, "--indexes", help="Show index information for table"),
    vacuum: Optional[str] = typer.Option(None, "--vacuum", help="Vacuum table (format: schema.table)"),
    reindex: Optional[str] = typer.Option(None, "--reindex", help="Reindex table (format: schema.table)"),
    backup: Optional[str] = typer.Option(None, "--backup", help="Backup database to file"),
    restore: Optional[str] = typer.Option(None, "--restore", help="Restore database from backup"),
    host: str = typer.Option("localhost", "--host", help="PostgreSQL host"),
    port: int = typer.Option(5432, "--port", help="PostgreSQL port"),
    database: str = typer.Option("postgres", "--database", "-d", help="Database name"),
    username: str = typer.Option("postgres", "--username", "-u", help="Database username"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="Database password"),
    schema: str = typer.Option("public", "--schema", help="Schema name"),
    format: str = typer.Option("table", "--format", help="Output format (table, json)")
):
    """PostgreSQL database integration with advanced features"""
    initialize_system()
    
    try:
        # Create PostgreSQL connection configuration
        connection_config = PostgresConnection(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password
        )
        
        # Initialize PostgreSQL tools with connection
        postgres_tools = PostgresToolsManager(connection_config)
        
        if query:
            postgres_tools.execute_query(query, format=format)
        
        elif script:
            # Read script file
            try:
                with open(script, 'r') as f:
                    script_content = f.read()
                postgres_tools.execute_script(script_content, format=format)
            except FileNotFoundError:
                console.print(f"[red]Script file not found: {script}[/red]")
            except Exception as e:
                console.print(f"[red]Error reading script file: {e}[/red]")
        
        elif show_table:
            postgres_tools.show_table_info(show_table, schema, format=format)
        
        elif list_tables:
            postgres_tools.list_tables(schema, format=format)
        
        elif list_schemas:
            postgres_tools.list_schemas(format=format)
        
        elif database_info:
            postgres_tools.show_database_info(format=format)
        
        elif show_indexes:
            postgres_tools.show_index_info(show_indexes, schema, format=format)
        
        elif vacuum:
            try:
                if '.' in vacuum:
                    schema_name, table_name = vacuum.split('.', 1)
                else:
                    schema_name, table_name = schema, vacuum
                postgres_tools.vacuum_table(table_name, schema_name)
            except ValueError:
                console.print("[red]Invalid vacuum format. Use: schema.table[/red]")
        
        elif reindex:
            try:
                if '.' in reindex:
                    schema_name, table_name = reindex.split('.', 1)
                else:
                    schema_name, table_name = schema, reindex
                postgres_tools.reindex_table(table_name, schema_name)
            except ValueError:
                console.print("[red]Invalid reindex format. Use: schema.table[/red]")
        
        elif backup:
            postgres_tools.backup_database(backup)
        
        elif restore:
            postgres_tools.restore_database(restore)
        
        else:
            console.print("[yellow]No operation specified. Use --help for available options.[/yellow]")
        
        # Close connection
        postgres_tools.close()
    
    except Exception as e:
        console.print(f"[red]PostgreSQL operation error: {e}[/red]")


# Shell Commands
@app.command()
def shell(
    command: Optional[str] = typer.Option(None, "--command", "-c", help="Execute shell command"),
    script: Optional[str] = typer.Option(None, "--script", "-s", help="Execute shell script file"),
    live: bool = typer.Option(False, "--live", "-l", help="Show live output"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Command timeout in seconds"),
    cwd: Optional[str] = typer.Option(None, "--cwd", help="Working directory"),
    system_info: bool = typer.Option(False, "--info", "-i", help="Show system information"),
    process_info: Optional[int] = typer.Option(None, "--process", help="Show process information by PID"),
    kill_process: Optional[int] = typer.Option(None, "--kill", help="Kill process by PID"),
    signal: str = typer.Option("SIGTERM", "--signal", help="Signal to send (SIGTERM, SIGKILL)"),
    history: bool = typer.Option(False, "--history", help="Show command history"),
    history_limit: Optional[int] = typer.Option(None, "--history-limit", help="Limit history entries"),
    clear_history: bool = typer.Option(False, "--clear-history", help="Clear command history"),
    format: str = typer.Option("table", "--format", help="Output format (table, json)")
):
    """Execute shell commands with safety features and rich output"""
    initialize_system()
    
    try:
        if command:
            shell_tools.execute_command(command, timeout, cwd, live, format)
        
        elif script:
            # Read script file
            try:
                with open(script, 'r') as f:
                    script_content = f.read()
                
                # Execute each line
                lines = script_content.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        shell_tools.execute_command(line, timeout, cwd, live, format)
            except FileNotFoundError:
                console.print(f"[red]Script file not found: {script}[/red]")
            except Exception as e:
                console.print(f"[red]Error reading script file: {e}[/red]")
        
        elif system_info:
            shell_tools.show_system_info(format)
        
        elif process_info is not None:
            shell_tools.show_process_info(process_info, format)
        
        elif kill_process is not None:
            shell_tools.kill_process(kill_process, signal)
        
        elif history:
            shell_tools.show_history(history_limit, format)
        
        elif clear_history:
            shell_tools.shell_tools.clear_history()
            console.print("[green]Command history cleared[/green]")
        
        else:
            console.print("[yellow]No operation specified. Use --help for available options.[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Shell operation error: {e}[/red]")


# Docker Commands
@app.command()
def docker(
    list_containers: bool = typer.Option(False, "--list", "-l", help="List containers"),
    all_containers: bool = typer.Option(False, "--all", "-a", help="Show all containers (including stopped)"),
    container_info: Optional[str] = typer.Option(None, "--info", help="Show container information"),
    start: Optional[str] = typer.Option(None, "--start", help="Start container by ID"),
    stop: Optional[str] = typer.Option(None, "--stop", help="Stop container by ID"),
    restart: Optional[str] = typer.Option(None, "--restart", help="Restart container by ID"),
    remove: Optional[str] = typer.Option(None, "--remove", help="Remove container by ID"),
    force: bool = typer.Option(False, "--force", help="Force operation"),
    volumes: bool = typer.Option(False, "--volumes", "-v", help="Remove volumes with container"),
    create: Optional[str] = typer.Option(None, "--create", help="Create container (format: image:name)"),
    command: Optional[str] = typer.Option(None, "--command", "-c", help="Command for container creation"),
    ports: Optional[str] = typer.Option(None, "--ports", "-p", help="Port mappings (format: host:container,host2:container2)"),
    volumes_mount: Optional[str] = typer.Option(None, "--volumes-mount", help="Volume mounts (format: host:container,host2:container2)"),
    environment: Optional[str] = typer.Option(None, "--env", "-e", help="Environment variables (format: VAR=value,VAR2=value2)"),
    detach: bool = typer.Option(True, "--detach/--no-detach", help="Run container in background"),
    exec_command: Optional[str] = typer.Option(None, "--exec", help="Execute command in container (format: container_id:command)"),
    exec_user: Optional[str] = typer.Option(None, "--exec-user", help="User for exec command"),
    logs: Optional[str] = typer.Option(None, "--logs", help="Show container logs by ID"),
    logs_tail: int = typer.Option(100, "--logs-tail", help="Number of log lines to show"),
    logs_follow: bool = typer.Option(False, "--logs-follow", help="Follow log output"),
    list_images: bool = typer.Option(False, "--images", help="List Docker images"),
    pull: Optional[str] = typer.Option(None, "--pull", help="Pull image (format: name:tag)"),
    remove_image: Optional[str] = typer.Option(None, "--rmi", help="Remove image by ID"),
    build: Optional[str] = typer.Option(None, "--build", help="Build image (format: path:tag)"),
    dockerfile: str = typer.Option("Dockerfile", "--dockerfile", help="Dockerfile name"),
    system_info: bool = typer.Option(False, "--system", help="Show Docker system information"),
    prune: bool = typer.Option(False, "--prune", help="Prune unused Docker resources"),
    prune_containers: bool = typer.Option(False, "--prune-containers", help="Prune only containers"),
    prune_images: bool = typer.Option(False, "--prune-images", help="Prune only images"),
    prune_volumes: bool = typer.Option(False, "--prune-volumes", help="Prune only volumes"),
    prune_networks: bool = typer.Option(False, "--prune-networks", help="Prune only networks"),
    format: str = typer.Option("table", "--format", help="Output format (table, json)")
):
    """Docker container management with rich features"""
    initialize_system()
    
    try:
        if list_containers or all_containers:
            docker_tools.list_containers(all_containers, format)
        
        elif container_info:
            docker_tools.show_container_info(container_info, format)
        
        elif start:
            docker_tools.start_container(start)
        
        elif stop:
            docker_tools.stop_container(stop)
        
        elif restart:
            docker_tools.restart_container(restart)
        
        elif remove:
            docker_tools.remove_container(remove, force, volumes)
        
        elif create:
            try:
                if ':' in create:
                    image, name = create.split(':', 1)
                else:
                    image, name = create, None
                docker_tools.create_container(image, name, command, ports, volumes_mount, environment, detach)
            except ValueError:
                console.print("[red]Invalid create format. Use: image:name[/red]")
        
        elif exec_command:
            try:
                if ':' in exec_command:
                    container_id, cmd = exec_command.split(':', 1)
                else:
                    console.print("[red]Invalid exec format. Use: container_id:command[/red]")
                    return
                docker_tools.execute_command(container_id, cmd, exec_user)
            except ValueError:
                console.print("[red]Invalid exec format. Use: container_id:command[/red]")
        
        elif logs:
            docker_tools.show_logs(logs, logs_tail, logs_follow)
        
        elif list_images:
            docker_tools.list_images(format)
        
        elif pull:
            try:
                if ':' in pull:
                    image_name, tag = pull.split(':', 1)
                else:
                    image_name, tag = pull, "latest"
                docker_tools.pull_image(image_name, tag)
            except ValueError:
                console.print("[red]Invalid pull format. Use: name:tag[/red]")
        
        elif remove_image:
            docker_tools.remove_image(remove_image, force)
        
        elif build:
            try:
                if ':' in build:
                    path, tag = build.split(':', 1)
                else:
                    console.print("[red]Invalid build format. Use: path:tag[/red]")
                    return
                docker_tools.build_image(path, tag, dockerfile)
            except ValueError:
                console.print("[red]Invalid build format. Use: path:tag[/red]")
        
        elif system_info:
            docker_tools.show_system_info(format)
        
        elif prune or prune_containers or prune_images or prune_volumes or prune_networks:
            docker_tools.prune_system(
                containers=prune or prune_containers,
                images=prune or prune_images,
                volumes=prune or prune_volumes,
                networks=prune or prune_networks
            )
        
        else:
            console.print("[yellow]No operation specified. Use --help for available options.[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Docker operation error: {e}[/red]")


# Wikipedia Commands
@app.command()
def wikipedia(
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search Wikipedia articles"),
    article: Optional[str] = typer.Option(None, "--article", "-a", help="Get full article by title"),
    summary: Optional[str] = typer.Option(None, "--summary", help="Get article summary by title"),
    random: bool = typer.Option(False, "--random", "-r", help="Get a random Wikipedia article"),
    related: Optional[str] = typer.Option(None, "--related", help="Get articles related to title"),
    suggestions: Optional[str] = typer.Option(None, "--suggestions", help="Get search suggestions for query"),
    keywords: Optional[str] = typer.Option(None, "--keywords", help="Extract keywords from text"),
    categories: Optional[str] = typer.Option(None, "--categories", help="Get categories for article"),
    category_articles: Optional[str] = typer.Option(None, "--category-articles", help="Get articles in category"),
    language_versions: Optional[str] = typer.Option(None, "--language-versions", help="Get available language versions"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of results to return"),
    sentences: int = typer.Option(3, "--sentences", help="Number of sentences for summary"),
    max_keywords: int = typer.Option(10, "--max-keywords", help="Maximum number of keywords to extract"),
    language: str = typer.Option("en", "--language", help="Wikipedia language code"),
    clear_cache: bool = typer.Option(False, "--clear-cache", help="Clear Wikipedia cache"),
    format: str = typer.Option("table", "--format", help="Output format (table, json)")
):
    """Wikipedia research and knowledge retrieval with rich features"""
    initialize_system()
    
    try:
        # Set language if specified
        if language != "en":
            wikipedia_tools.set_language(language)
        
        if clear_cache:
            wikipedia_tools.clear_cache()
        
        elif search:
            wikipedia_tools.search(search, limit, format)
        
        elif article:
            wikipedia_tools.get_article(article, format)
        
        elif summary:
            wikipedia_tools.get_summary(summary, sentences, format)
        
        elif random:
            wikipedia_tools.get_random_article(format)
        
        elif related:
            wikipedia_tools.get_related_articles(related, limit, format)
        
        elif suggestions:
            wikipedia_tools.get_suggestions(suggestions, limit, format)
        
        elif keywords:
            wikipedia_tools.extract_keywords(keywords, max_keywords, format)
        
        elif categories:
            try:
                categories_list = wikipedia_tools.wikipedia_tools.get_article_categories(categories)
                if format == "json":
                    import json
                    console.print(json.dumps({'categories': categories_list}, indent=2))
                else:
                    categories_text = ", ".join(categories_list)
                    console.print(Panel(categories_text, title=f"Categories for '{categories}'", border_style="yellow"))
            except Exception as e:
                console.print(f"[red]Categories error: {e}[/red]")
        
        elif category_articles:
            try:
                articles = wikipedia_tools.wikipedia_tools.get_category_articles(category_articles, limit)
                if format == "json":
                    import json
                    console.print(json.dumps([{
                        'title': a.title,
                        'snippet': a.snippet,
                        'url': a.url,
                        'wordcount': a.wordcount
                    } for a in articles], indent=2))
                else:
                    table = Table(title=f"Articles in Category '{category_articles}'")
                    table.add_column("Title", style="cyan", no_wrap=True)
                    table.add_column("Snippet", style="white")
                    table.add_column("Word Count", style="yellow", justify="right")
                    table.add_column("URL", style="blue", no_wrap=True)
                    
                    for article in articles:
                        snippet = article.snippet[:100] + "..." if len(article.snippet) > 100 else article.snippet
                        table.add_row(article.title, snippet, str(article.wordcount), article.url)
                    
                    console.print(table)
            except Exception as e:
                console.print(f"[red]Category articles error: {e}[/red]")
        
        elif language_versions:
            try:
                versions = wikipedia_tools.wikipedia_tools.get_language_versions(language_versions)
                if format == "json":
                    import json
                    console.print(json.dumps({'language_versions': versions}, indent=2))
                else:
                    versions_text = ", ".join([f"{lang}: {title}" for lang, title in versions.items()])
                    console.print(Panel(versions_text, title=f"Language Versions of '{language_versions}'", border_style="blue"))
            except Exception as e:
                console.print(f"[red]Language versions error: {e}[/red]")
        
        else:
            console.print("[yellow]No operation specified. Use --help for available options.[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Wikipedia operation error: {e}[/red]")


# arXiv Commands
@app.command()
def arxiv(
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search arXiv papers"),
    paper: Optional[str] = typer.Option(None, "--paper", "-p", help="Get paper by ID"),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Search papers by author"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Search papers by category"),
    recent: bool = typer.Option(False, "--recent", "-r", help="Get recent papers"),
    related: Optional[str] = typer.Option(None, "--related", help="Get papers related to paper ID"),
    author_info: Optional[str] = typer.Option(None, "--author-info", help="Get information about author"),
    categories: bool = typer.Option(False, "--categories", help="List available categories"),
    keywords: Optional[str] = typer.Option(None, "--keywords", help="Extract keywords from text"),
    date_range: Optional[str] = typer.Option(None, "--date-range", help="Search by date range (format: start:end)"),
    max_results: int = typer.Option(10, "--max-results", "-m", help="Maximum number of results"),
    sort_by: str = typer.Option("relevance", "--sort-by", help="Sort by (relevance, lastUpdatedDate, submittedDate)"),
    sort_order: str = typer.Option("descending", "--sort-order", help="Sort order (ascending, descending)"),
    filter_categories: Optional[str] = typer.Option(None, "--filter-categories", help="Filter by categories (comma-separated)"),
    max_keywords: int = typer.Option(10, "--max-keywords", help="Maximum number of keywords to extract"),
    clear_cache: bool = typer.Option(False, "--clear-cache", help="Clear arXiv cache"),
    format: str = typer.Option("table", "--format", help="Output format (table, json)")
):
    """arXiv academic paper search and retrieval with rich features"""
    initialize_system()
    
    try:
        if clear_cache:
            arxiv_tools.clear_cache()
        
        elif search:
            categories_list = None
            if filter_categories:
                categories_list = [cat.strip() for cat in filter_categories.split(',')]
            arxiv_tools.search(search, max_results, sort_by, sort_order, categories_list, format)
        
        elif paper:
            arxiv_tools.get_paper(paper, format)
        
        elif author:
            arxiv_tools.search_by_author(author, max_results, format)
        
        elif category:
            arxiv_tools.search_by_category(category, max_results, format)
        
        elif recent:
            arxiv_tools.get_recent_papers(category, max_results, format)
        
        elif related:
            arxiv_tools.get_related_papers(related, max_results, format)
        
        elif author_info:
            arxiv_tools.get_author_info(author_info, format)
        
        elif categories:
            arxiv_tools.get_categories(format)
        
        elif keywords:
            arxiv_tools.extract_keywords(keywords, max_keywords, format)
        
        elif date_range:
            try:
                if ':' in date_range:
                    start_date, end_date = date_range.split(':', 1)
                else:
                    console.print("[red]Invalid date range format. Use: start:end[/red]")
                    return
                
                # This would require implementing date range search in the tools
                console.print("[yellow]Date range search not yet implemented[/yellow]")
            except ValueError:
                console.print("[red]Invalid date range format. Use: start:end[/red]")
        
        else:
            console.print("[yellow]No operation specified. Use --help for available options.[/yellow]")
    
    except Exception as e:
        console.print(f"[red]arXiv operation error: {e}[/red]")


# PubMed Commands
@app.command()
def pubmed(
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search PubMed papers"),
    paper: Optional[str] = typer.Option(None, "--paper", "-p", help="Get paper by PMID"),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Search papers by author"),
    journal: Optional[str] = typer.Option(None, "--journal", "-j", help="Search papers by journal"),
    recent: bool = typer.Option(False, "--recent", "-r", help="Get recent papers"),
    related: Optional[str] = typer.Option(None, "--related", help="Get papers related to PMID"),
    author_info: Optional[str] = typer.Option(None, "--author-info", help="Get information about author"),
    databases: bool = typer.Option(False, "--databases", help="List available databases"),
    keywords: Optional[str] = typer.Option(None, "--keywords", help="Extract keywords from text"),
    date_range: Optional[str] = typer.Option(None, "--date-range", help="Search by date range (format: start:end)"),
    mesh_term: Optional[str] = typer.Option(None, "--mesh-term", help="Search by MeSH term"),
    max_results: int = typer.Option(10, "--max-results", "-m", help="Maximum number of results"),
    database: str = typer.Option("pubmed", "--database", "-d", help="Database to search (pubmed, pmc, gene, protein)"),
    sort_by: str = typer.Option("relevance", "--sort-by", help="Sort by (relevance, date)"),
    max_keywords: int = typer.Option(10, "--max-keywords", help="Maximum number of keywords to extract"),
    email: str = typer.Option("agno-cli@example.com", "--email", help="Email for NCBI API"),
    clear_cache: bool = typer.Option(False, "--clear-cache", help="Clear PubMed cache"),
    format: str = typer.Option("table", "--format", help="Output format (table, json)")
):
    """PubMed medical research paper search and retrieval with rich features"""
    initialize_system()
    
    try:
        if clear_cache:
            pubmed_tools.clear_cache()
        
        elif search:
            pubmed_tools.search(search, max_results, database, sort_by, format)
        
        elif paper:
            pubmed_tools.get_paper(paper, format)
        
        elif author:
            pubmed_tools.search_by_author(author, max_results, format)
        
        elif journal:
            pubmed_tools.search_by_journal(journal, max_results, format)
        
        elif recent:
            pubmed_tools.get_recent_papers(max_results, format)
        
        elif related:
            pubmed_tools.get_related_papers(related, max_results, format)
        
        elif author_info:
            pubmed_tools.get_author_info(author_info, format)
        
        elif databases:
            pubmed_tools.get_databases(format)
        
        elif keywords:
            pubmed_tools.extract_keywords(keywords, max_keywords, format)
        
        elif date_range:
            try:
                if ':' in date_range:
                    start_date, end_date = date_range.split(':', 1)
                else:
                    console.print("[red]Invalid date range format. Use: start:end[/red]")
                    return
                
                # This would require implementing date range search in the tools
                console.print("[yellow]Date range search not yet implemented[/yellow]")
            except ValueError:
                console.print("[red]Invalid date range format. Use: start:end[/red]")
        
        elif mesh_term:
            try:
                # This would require implementing MeSH term search in the tools
                console.print("[yellow]MeSH term search not yet implemented[/yellow]")
            except Exception as e:
                console.print(f"[red]MeSH term search error: {e}[/red]")
        
        else:
            console.print("[yellow]No operation specified. Use --help for available options.[/yellow]")
    
    except Exception as e:
        console.print(f"[red]PubMed operation error: {e}[/red]")


# Sleep Commands
@app.command()
def sleep(
    duration: float = typer.Option(None, "--duration", "-d", help="Sleep duration in seconds"),
    countdown: float = typer.Option(None, "--countdown", "-c", help="Countdown duration in seconds"),
    until: Optional[str] = typer.Option(None, "--until", "-u", help="Sleep until time (format: HH:MM:SS)"),
    timer: Optional[str] = typer.Option(None, "--timer", "-t", help="Time command execution"),
    iterations: int = typer.Option(1, "--iterations", "-i", help="Number of iterations for timer"),
    time_info: bool = typer.Option(False, "--time-info", help="Show current time information"),
    performance: bool = typer.Option(False, "--performance", help="Monitor system performance"),
    monitor_duration: float = typer.Option(60, "--monitor-duration", help="Performance monitor duration"),
    schedules: bool = typer.Option(False, "--schedules", help="List scheduled functions"),
    clear_schedules: bool = typer.Option(False, "--clear-schedules", help="Clear all scheduled functions"),
    rate_limit_info: bool = typer.Option(False, "--rate-limit-info", help="Show rate limiting information"),
    no_progress: bool = typer.Option(False, "--no-progress", help="Disable progress display"),
    format_type: str = typer.Option("seconds", "--format-type", help="Time format (seconds, minutes, hours)"),
    format: str = typer.Option("table", "--format", help="Output format (table, json)")
):
    """Sleep and timing operations with rich features"""
    initialize_system()
    
    try:
        if duration is not None:
            show_progress = not no_progress
            sleep_tools.sleep(duration, show_progress, "Sleeping", format)
        
        elif countdown is not None:
            show_progress = not no_progress
            sleep_tools.countdown(countdown, show_progress, format_type, format)
        
        elif until:
            try:
                # Parse time format
                if ':' in until:
                    time_parts = until.split(':')
                    if len(time_parts) == 3:
                        hour, minute, second = map(int, time_parts)
                        target_time = datetime.datetime.now().replace(hour=hour, minute=minute, second=second, microsecond=0)
                        
                        # If time has passed today, schedule for tomorrow
                        if target_time <= datetime.datetime.now():
                            target_time += datetime.timedelta(days=1)
                        
                        show_progress = not no_progress
                        result = sleep_tools.sleep_tools.sleep_until(target_time, show_progress)
                        
                        if format == "json":
                            import json
                            console.print(json.dumps({
                                'duration': result.duration,
                                'start_time': result.start_time,
                                'end_time': result.end_time,
                                'interrupted': result.interrupted,
                                'actual_duration': result.actual_duration,
                                'target_duration': result.target_duration
                            }, indent=2))
                        else:
                            if result.interrupted:
                                console.print("[yellow]Sleep interrupted[/yellow]")
                            else:
                                console.print("[green]Sleep completed[/green]")
                    else:
                        console.print("[red]Invalid time format. Use HH:MM:SS[/red]")
                else:
                    console.print("[red]Invalid time format. Use HH:MM:SS[/red]")
            except ValueError:
                console.print("[red]Invalid time format. Use HH:MM:SS[/red]")
        
        elif timer:
            sleep_tools.timer(timer, iterations, format)
        
        elif time_info:
            sleep_tools.time_info(format)
        
        elif performance:
            sleep_tools.performance_monitor(monitor_duration, format)
        
        elif schedules:
            sleep_tools.list_schedules(format)
        
        elif clear_schedules:
            sleep_tools.clear_schedules()
        
        elif rate_limit_info:
            sleep_tools.rate_limit_info(format)
        
        else:
            console.print("[yellow]No operation specified. Use --help for available options.[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Sleep operation error: {e}[/red]")


# Version Command
@app.command()
def version():
    """Show version information"""
    version_text = """
**Agno CLI Enhanced Multi-Agent System**
Version: 2.0.0
Build: Enhanced with multi-agent capabilities

**Features:**
- Multi-agent orchestration and coordination
- Advanced reasoning with step-by-step tracing
- Comprehensive performance metrics
- Extended tool integrations (search, finance, math)
- Team collaboration and communication
- Modular CLI architecture

**Powered by:** Agno AI Framework
"""
    
    panel = Panel(
        Markdown(version_text),
        title="Version Information",
        border_style="magenta"
    )
    console.print(panel)


if __name__ == "__main__":
    app()
