"""
Helper functions for Agno CLI SDK
"""

import re
import json
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


console = Console()


def format_output(content: str, format_type: str = "text") -> None:
    """Format and display output using Rich"""
    
    if format_type == "markdown":
        md = Markdown(content)
        console.print(md)
    elif format_type == "json":
        try:
            parsed = json.loads(content)
            console.print_json(data=parsed)
        except json.JSONDecodeError:
            console.print(content)
    elif format_type == "panel":
        panel = Panel(content, title="Response", border_style="blue")
        console.print(panel)
    else:
        console.print(content)


def validate_input(input_text: str) -> bool:
    """Validate user input"""
    if not input_text or not input_text.strip():
        return False
    
    # Check for potentially harmful commands
    dangerous_patterns = [
        r'rm\s+-rf',
        r'sudo\s+rm',
        r'del\s+/[sf]',
        r'format\s+c:',
        r'shutdown',
        r'reboot'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, input_text, re.IGNORECASE):
            console.print("[red]Warning: Potentially dangerous command detected![/red]")
            return False
    
    return True


def display_session_table(sessions: List[Dict[str, Any]], current_session_id: Optional[str] = None) -> None:
    """Display sessions in a table format"""
    table = Table(title="Chat Sessions")
    
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Messages", justify="right", style="green")
    table.add_column("Created", style="blue")
    table.add_column("Updated", style="blue")
    table.add_column("Current", justify="center")
    
    for session in sessions:
        is_current = "✓" if session['session_id'] == current_session_id else ""
        
        table.add_row(
            session['session_id'][:8] + "...",
            session['name'],
            str(session['message_count']),
            session['created_at'][:16],
            session['updated_at'][:16],
            is_current
        )
    
    console.print(table)


def display_memory_info(memory_data: Dict[str, Any]) -> None:
    """Display memory information"""
    if not memory_data:
        console.print("[yellow]No memory data available[/yellow]")
        return
    
    # User memory
    user_memory = memory_data.get('user_memory', {})
    if user_memory:
        console.print("\n[bold blue]User Memory:[/bold blue]")
        for key, value in user_memory.items():
            if value:
                console.print(f"  {key}: {value}")
    
    # Session summary
    session_summary = memory_data.get('session_summary', {})
    if session_summary:
        console.print("\n[bold blue]Session Summary:[/bold blue]")
        for key, value in session_summary.items():
            if value:
                console.print(f"  {key}: {value}")


def display_tools_table(tools: List[str]) -> None:
    """Display available tools in a table"""
    if not tools:
        console.print("[yellow]No tools available[/yellow]")
        return
    
    table = Table(title="Available Tools")
    table.add_column("Tool Name", style="cyan")
    table.add_column("Description", style="white")
    
    # Tool descriptions (you could expand this)
    tool_descriptions = {
        "reasoning": "Provides reasoning and planning capabilities",
        "yfinance": "Financial data and stock information",
        "duckduckgo": "Web search functionality",
        "calculator": "Mathematical calculations",
        "file_reader": "Read and analyze files",
        "web_scraper": "Extract content from web pages"
    }
    
    for tool in tools:
        description = tool_descriptions.get(tool, "No description available")
        table.add_row(tool, description)
    
    console.print(table)


def display_config_info(config_dict: Dict[str, Any]) -> None:
    """Display configuration information"""
    console.print("\n[bold blue]Current Configuration:[/bold blue]")
    
    for section, settings in config_dict.items():
        console.print(f"\n[bold cyan]{section.title()}:[/bold cyan]")
        for key, value in settings.items():
            # Hide sensitive information
            if 'key' in key.lower() or 'password' in key.lower():
                display_value = "***" if value else "Not set"
            else:
                display_value = str(value)
            console.print(f"  {key}: {display_value}")


def confirm_action(message: str) -> bool:
    """Ask user for confirmation"""
    response = console.input(f"[yellow]{message} (y/N): [/yellow]")
    return response.lower() in ['y', 'yes']


def display_error(error_message: str) -> None:
    """Display error message"""
    console.print(f"[red]Error: {error_message}[/red]")


def display_success(success_message: str) -> None:
    """Display success message"""
    console.print(f"[green]✓ {success_message}[/green]")


def display_warning(warning_message: str) -> None:
    """Display warning message"""
    console.print(f"[yellow]⚠ {warning_message}[/yellow]")


def display_info(info_message: str) -> None:
    """Display info message"""
    console.print(f"[blue]ℹ {info_message}[/blue]")

