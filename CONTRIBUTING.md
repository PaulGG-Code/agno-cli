# Contributing to Agno CLI

Thank you for your interest in contributing to Agno CLI! This document provides guidelines and information for contributors to help make the contribution process smooth and effective.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Project Architecture](#project-architecture)
5. [Contributing Guidelines](#contributing-guidelines)
6. [Code Style and Standards](#code-style-and-standards)
7. [Testing](#testing)
8. [Documentation](#documentation)
9. [Submitting Changes](#submitting-changes)
10. [Release Process](#release-process)
11. [Community Guidelines](#community-guidelines)

## Project Overview

Agno CLI is a robust, terminal-native multi-agent assistant built upon the innovative Agno AI framework. It provides a comprehensive suite of features for advanced AI-driven task automation and collaboration directly from your command line.

### Key Features

- **Multi-Agent System**: Sophisticated multi-agent architecture with role-based coordination
- **Advanced Reasoning & Tracing**: Step-by-step reasoning with comprehensive tracing
- **Comprehensive Tool Integration**: 25+ tool categories including file system, search, financial, math, and more
- **Team Management**: Robust team coordination and task management
- **Enhanced CLI Experience**: Rich terminal UI with interactive features

### Technology Stack

- **Python 3.8+**: Core programming language
- **Agno AI Framework**: Multi-agent AI framework
- **Typer**: CLI framework
- **Rich**: Terminal UI and formatting
- **Pandas/NumPy**: Data manipulation
- **Various APIs**: OpenAI, Anthropic, financial data, search engines, etc.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package installer)

### Quick Start

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/agno-cli.git
   cd agno-cli
   ```

2. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

4. **Configure your environment**
   ```bash
   agno configure --provider anthropic --api-key your-api-key
   ```

## Development Setup

### Environment Setup

1. **Create a virtual environment**
   ```bash
   python -m venv agno-cli-env
   source agno-cli-env/bin/activate  # On Windows: agno-cli-env\Scripts\activate
   ```

2. **Install the package in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install all optional dependencies (optional)**
   ```bash
   pip install -e ".[all]"
   ```

### Configuration

Create a development configuration file at `~/.agno_cli/config.yaml`:

```yaml
model:
  provider: anthropic
  model_id: claude-3-5-sonnet-20240229
  api_key: your-api-key
  temperature: 0.7
  max_tokens: 4096

agent:
  name: DevelopmentAssistant
  role: AI Assistant
  description: Development environment assistant
  show_tool_calls: true
  markdown: true
  memory_rounds: 10
  message_history: 10

cli:
  debug: true
  verbose: true
  stream: true
  auto_save: true
  session_dir: ~/.agno_cli/sessions
  config_dir: ~/.agno_cli
  logs_dir: ~/.agno_cli/logs
```

## Project Architecture

### Directory Structure

```
agno_cli/
├── agents/           # Multi-agent system
│   ├── agent_state.py      # Agent state tracking
│   ├── orchestrator.py     # Agent coordination
│   └── multi_agent.py      # Multi-agent system
├── reasoning/        # Reasoning and tracing
│   ├── tracer.py          # Step-by-step reasoning
│   └── metrics.py         # Performance metrics
├── tools/           # Tool integrations (25+ categories)
│   ├── search_tools.py    # Search engines
│   ├── financial_tools.py # Financial data
│   ├── math_tools.py      # Math and data
│   ├── file_system_tools.py # File system operations
│   ├── csv_tools.py         # CSV data operations
│   ├── pandas_tools.py      # Pandas data analysis
│   ├── duckdb_tools.py      # DuckDB database operations
│   ├── sql_tools.py         # SQL query execution
│   ├── postgres_tools.py    # PostgreSQL database integration
│   ├── shell_tools.py       # System command execution
│   ├── docker_tools.py      # Docker container management
│   ├── wikipedia_tools.py   # Wikipedia research
│   ├── arxiv_tools.py       # arXiv academic papers
│   ├── pubmed_tools.py      # PubMed medical research
│   ├── sleep_tools.py       # Sleep and timing operations
│   ├── hackernews_tools.py  # Hacker News integration
│   ├── visualization_tools.py # Data visualization
│   ├── opencv_tools.py      # Computer vision operations
│   ├── models_tools.py      # Model management
│   ├── thinking_tools.py    # Advanced thinking and reasoning
│   ├── function_tools.py    # Dynamic function calling
│   ├── openai_tools.py      # OpenAI API integration
│   ├── crawl4ai_tools.py    # Web crawling
│   └── screenshot_tools.py  # Screenshot capture
├── commands/        # CLI command modules
│   ├── chat_commands.py   # Chat interface
│   ├── agent_commands.py  # Agent management
│   ├── team_commands.py   # Team operations
│   ├── tool_commands.py   # Tool operations
│   ├── trace_commands.py  # Trace management
│   └── metrics_commands.py # Metrics analysis
├── core/            # Core functionality
│   ├── config.py          # Configuration
│   ├── session.py         # Session management
│   └── agent.py           # Agent wrapper
├── utils/           # Utility functions
│   ├── helpers.py         # Helper functions
│   └── logging.py         # Logging utilities
└── cli.py           # Main CLI entry point
```

### Core Components

#### Multi-Agent System (`agents/`)
- **AgentState**: Tracks agent capabilities, status, and metadata
- **AgentOrchestrator**: Manages task assignment and agent coordination
- **MultiAgentSystem**: Main system that manages multiple agents

#### Reasoning System (`reasoning/`)
- **ReasoningTracer**: Captures and displays step-by-step reasoning
- **MetricsCollector**: Tracks performance metrics and analytics

#### Tool System (`tools/`)
- **Tool Managers**: Each tool category has its own manager class
- **Standardized Interface**: All tools follow a consistent API pattern
- **Error Handling**: Robust error handling and validation

#### CLI Commands (`commands/`)
- **Command Modules**: Organized by functionality
- **Typer Integration**: Uses Typer for CLI argument parsing
- **Rich Output**: Beautiful terminal output with Rich library

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

1. **Bug Reports**: Report bugs and issues
2. **Feature Requests**: Suggest new features or improvements
3. **Code Contributions**: Submit code changes and improvements
4. **Documentation**: Improve documentation and examples
5. **Testing**: Add tests or improve test coverage
6. **Tool Integrations**: Add new tool categories or improve existing ones

### Contribution Workflow

1. **Create an Issue**: Start by creating an issue to discuss your contribution
2. **Fork and Clone**: Fork the repository and clone your fork
3. **Create a Branch**: Create a feature branch for your changes
4. **Make Changes**: Implement your changes following the guidelines below
5. **Test**: Ensure all tests pass and add new tests if needed
6. **Document**: Update documentation as necessary
7. **Submit PR**: Create a pull request with a clear description

### Issue Guidelines

When creating issues, please:

- Use descriptive titles
- Provide detailed descriptions
- Include reproduction steps for bugs
- Specify your environment (OS, Python version, etc.)
- Use appropriate labels

### Pull Request Guidelines

When submitting pull requests:

- Use descriptive titles
- Provide detailed descriptions of changes
- Reference related issues
- Include tests for new functionality
- Update documentation as needed
- Ensure all CI checks pass

## Code Style and Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line Length**: 100 characters maximum
- **Import Order**: Standard library, third-party, local imports
- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings

### Code Formatting

We use automated tools for code formatting:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Example Code Structure

```python
"""
Tool manager for [Tool Category] operations.

This module provides functionality for [specific operations].
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json

from rich.console import Console
from rich.table import Table


class ToolCategoryManager:
    """Manager for [Tool Category] operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the tool manager.
        
        Args:
            config: Configuration dictionary for the tool
        """
        self.config = config or {}
        self.console = Console()
    
    def operation_name(self, param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
        """Perform [specific operation].
        
        Args:
            param1: Description of parameter 1
            param2: Description of parameter 2
            
        Returns:
            Dictionary containing operation results
            
        Raises:
            ValueError: If parameters are invalid
        """
        try:
            # Implementation here
            result = {"status": "success", "data": "result"}
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
```

## Testing

### Test Structure

Tests are organized in the `tests/` directory:

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── fixtures/       # Test fixtures and data
└── conftest.py     # Pytest configuration
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agno_cli

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run specific test file
pytest tests/unit/test_tool_manager.py

# Run with verbose output
pytest -v
```

### Writing Tests

Follow these guidelines for writing tests:

1. **Test Naming**: Use descriptive test names
2. **Test Organization**: Group related tests in classes
3. **Fixtures**: Use pytest fixtures for common setup
4. **Mocking**: Mock external dependencies
5. **Coverage**: Aim for high test coverage

Example test:

```python
"""Tests for ToolCategoryManager."""

import pytest
from unittest.mock import Mock, patch
from agno_cli.tools.tool_category_tools import ToolCategoryManager


class TestToolCategoryManager:
    """Test cases for ToolCategoryManager."""
    
    def test_initialization(self):
        """Test manager initialization."""
        manager = ToolCategoryManager()
        assert manager.config == {}
        assert manager.console is not None
    
    def test_operation_name_success(self):
        """Test successful operation execution."""
        manager = ToolCategoryManager()
        result = manager.operation_name("test_param")
        assert result["status"] == "success"
    
    def test_operation_name_error(self):
        """Test error handling in operation."""
        manager = ToolCategoryManager()
        with patch.object(manager, '_internal_method', side_effect=Exception("Test error")):
            result = manager.operation_name("test_param")
            assert result["status"] == "error"
            assert "Test error" in result["message"]
```

## Documentation

### Documentation Standards

- **Docstrings**: All public functions and classes must have docstrings
- **README**: Keep the main README updated with new features
- **Examples**: Provide clear examples for new functionality
- **API Documentation**: Document all public APIs

### Documentation Structure

```
docs/
├── api/            # API documentation
├── guides/         # User guides
├── development/    # Development documentation
└── examples/       # Code examples
```

### Updating Documentation

When adding new features:

1. Update docstrings for all new functions/classes
2. Add examples to the README
3. Update relevant guides
4. Add API documentation if needed

## Submitting Changes

### Pull Request Process

1. **Fork the Repository**: Create your own fork of the project
2. **Create a Branch**: Create a feature branch from `main`
3. **Make Changes**: Implement your changes
4. **Test**: Ensure all tests pass
5. **Commit**: Make clear, atomic commits
6. **Push**: Push your branch to your fork
7. **Create PR**: Create a pull request

### Commit Message Guidelines

Use conventional commit messages:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Examples:
```
feat(tools): add new financial analysis tool
fix(agents): resolve agent state loading issue
docs(readme): update installation instructions
```

### Review Process

1. **Automated Checks**: All PRs must pass automated checks
2. **Code Review**: At least one maintainer must approve
3. **Testing**: Changes must be tested
4. **Documentation**: Documentation must be updated

## Release Process

### Version Management

We follow [Semantic Versioning](https://semver.org/):

- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Release Steps

1. **Update Version**: Update version in `pyproject.toml`
2. **Update Changelog**: Add entries to `CHANGELOG.md`
3. **Create Release Branch**: Create a release branch
4. **Test**: Run full test suite
5. **Merge**: Merge to main
6. **Tag**: Create a git tag
7. **Publish**: Publish to PyPI

### Release Checklist

- [ ] Update version number
- [ ] Update changelog
- [ ] Run all tests
- [ ] Update documentation
- [ ] Create release notes
- [ ] Tag the release
- [ ] Publish to PyPI

## Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and inclusive
- Use welcoming and inclusive language
- Be collaborative and constructive
- Focus on what is best for the community
- Show empathy towards other community members

### Communication

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for general questions
- **Discord/Slack**: Join our community channels for real-time discussion

### Getting Help

If you need help:

1. Check the documentation
2. Search existing issues
3. Create a new issue with clear details
4. Join community discussions

## Development Tools

### Recommended IDE Setup

**VS Code Extensions:**
- Python
- Pylance
- Black Formatter
- isort
- Flake8
- MyPy

**PyCharm:**
- Enable type checking
- Configure code formatting
- Set up testing framework

### Debugging

```bash
# Run with debug logging
agno --debug

# Use Python debugger
python -m pdb -m agno_cli.cli

# Use IPython for interactive debugging
python -c "from agno_cli.tools.file_system_tools import FileSystemToolsManager; import IPython; IPython.embed()"
```

### Performance Profiling

```bash
# Profile CLI commands
python -m cProfile -o profile.stats -m agno_cli.cli

# Analyze profile results
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"
```

## License

By contributing to Agno CLI, you agree that your contributions will be licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

Thank you for contributing to Agno CLI! Your contributions help make this project better for everyone in the community.

---

For any questions about contributing, please open an issue or join our community discussions. 