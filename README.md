# Agno CLI Enhanced - Multi-Agent Terminal Assistant (Beta)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful, terminal-native multi-agent assistant built on the Agno AI framework. Features advanced reasoning, team collaboration, comprehensive tool integration, and performance analytics.

## 🚀 Features

### 📊 Current Implementation Status
- **✅ Completed**: Multi-agent system, file system operations, basic CLI framework
- **🔄 In Progress**: Additional tool integrations (see [Implementation Plan](IMPLEMENTATION_PLAN.md))
- **📋 Planned**: 73+ Agno AI tools integration for full feature parity

### 🤖 Multi-Agent System
- **Agent Orchestration**: Coordinate multiple AI agents with different roles and specializations
- **Team Collaboration**: Agents can communicate, delegate tasks, and share context
- **Role-Based Architecture**: Leader, Worker, Contributor, Specialist, Coordinator, and Observer roles
- **Dynamic Task Assignment**: Intelligent task routing based on agent capabilities and workload

### 🧠 Advanced Reasoning & Tracing
- **Step-by-Step Reasoning**: Chain-of-Thought (CoT) and ReAct pattern support
- **Reasoning Traces**: Detailed logs of agent thought processes and decision making
- **Performance Metrics**: Token usage, response times, success rates, and confidence scores
- **Real-time Monitoring**: Live trace display with `--trace` flag

### 🔧 Comprehensive Tool Integration

#### ✅ File System Tools (Implemented)
- **File Operations**: Read, write, list, delete, copy, and move files
- **Directory Management**: Create directories, tree view, recursive operations
- **File Search**: Pattern-based file searching with wildcards
- **File Information**: Detailed metadata, permissions, and MIME type detection
- **Security**: Path validation and safe file operations

#### 🔄 Search Tools (In Development)
- **Multiple Engines**: DuckDuckGo, Google, SerpApi, Brave, SearXNG, Baidu
- **Unified Interface**: Single command for multi-engine search and result aggregation
- **Configurable**: Engine-specific settings and API key management

#### 🔄 Financial Tools (In Development)
- **Stock Analysis**: Real-time quotes, historical data, technical indicators
- **Portfolio Management**: Multi-stock analysis and performance comparison
- **Market Data**: Sector performance, analyst recommendations, financial statements
- **News Integration**: Company-specific news and sentiment analysis

#### 🔄 Math & Data Tools (In Development)
- **Advanced Calculator**: Scientific functions, variables, step-by-step solutions
- **Statistical Analysis**: Descriptive stats, correlation, regression analysis
- **CSV Analysis**: Data loading, querying, and group analysis
- **SQL Integration**: In-memory database queries and data manipulation

### 👥 Team Management
- **Shared Context**: Team-wide information sharing and coordination
- **Message Passing**: Inter-agent communication and broadcasting
- **Task Orchestration**: Centralized task assignment and progress tracking
- **Performance Analytics**: Team-wide metrics and individual agent performance

### 🎯 Enhanced CLI Experience
- **Rich Terminal UI**: Beautiful tables, panels, and formatted output
- **Interactive Chat**: Multi-agent conversations with context switching
- **Modular Commands**: Organized command structure for different functionalities
- **Export Capabilities**: JSON, CSV, Markdown output formats

## 🚀 Quick Start

```bash
# Install the CLI
pip install agno-cli

# Configure with your API key
agno configure --provider anthropic --api-key your-api-key

# Start exploring
agno --help                    # See all commands
agno files --list              # List files in current directory
agno chat --quick "Hello!"     # Quick chat with AI
```

## 📦 Installation

### Basic Installation
```bash
pip install agno-cli
```

### With All Features
```bash
pip install agno-cli[all]
```

### Selective Feature Installation
```bash
# Search tools
pip install agno-cli[search]

# Financial analysis
pip install agno-cli[fintech]

# Math and data tools
pip install agno-cli[math]

# Communication tools
pip install agno-cli[comm]

# Media tools
pip install agno-cli[media]

# Knowledge APIs
pip install agno-cli[knowledge]
```

### Development Installation
```bash
git clone https://github.com/paulgg-code/agno-cli.git
cd agno-cli
pip install -e ".[dev]"
```

## ⚙️ Configuration

### Initial Setup
```bash
# Configure API keys and model settings
agno configure --provider anthropic --api-key your-api-key
agno configure --model claude-3-sonnet-20240229

# Or use OpenAI
agno configure --provider openai --api-key your-openai-key
agno configure --model gpt-4

# View current configuration
agno configure --show
```

### Environment Variables
```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
export AGNO_CONFIG_DIR="~/.agno_cli"
```

## 🎮 Usage Examples

### Available Commands
```bash
# Core commands
agno --help                    # Show all available commands
agno version                   # Show version information

# Agent management
agno agents --help             # Agent operations
agno agents --list             # List all agents
agno agents --create           # Create new agent
agno agents --remove           # Remove agent

# Chat interface
agno chat --help               # Chat operations
agno chat                      # Interactive chat
agno chat --quick "message"    # Quick single message

# File system operations
agno files --help              # File system operations
agno files --list              # List directory contents
agno files --read file.txt     # Read file contents
agno files --write file.txt    # Write to file
agno files --delete file.txt   # Delete file
agno files --search "*.py"     # Search for files
agno files --tree              # Display directory tree

# Configuration
agno configure --help          # Configuration management
agno configure --show          # Show current config
agno configure --set           # Set configuration values
```

### Interactive Chat
```bash
# Start chat with default agent
agno chat

# Chat with specific agent with reasoning trace
agno chat --agent researcher --trace

# Quick single message
agno chat --quick "Explain quantum computing"

# Chat with context and goals
agno chat --context '{"domain": "finance"}' --goal "Analyze market trends"
```

### Agent Management
```bash
# List all agents
agno agents --list

# Create specialized agent
agno agents --create "DataAnalyst" --role specialist \
  --description "Expert in data analysis and visualization" \
  --capabilities '{"tools": ["math_tools", "csv_tools"], "skills": ["statistics", "visualization"]}'

# Check agent status
agno agents --status agent-id

# Remove agent
agno agents --remove agent-id
```

### Team Operations
```bash
# View team status
agno team --status

# Assign task to team
agno team --task "Analyze Q3 financial performance" --priority high \
  --requirements '{"skills": ["finance", "analysis"], "tools": ["yfinance_tools"]}'

# Broadcast message to team
agno team --message "New market data available for analysis"
```

### Search Operations
```bash
# Basic search
agno search "artificial intelligence trends 2024"

# Multi-engine search
agno search "climate change solutions" --multi --format markdown

# Specific search engine
agno search "python best practices" --engine duckduckgo --num 5
```

### Financial Analysis
```bash
# Stock information
agno finance AAPL --action info

# Stock news
agno finance TSLA --action news

# Performance analysis
agno finance MSFT --action analysis --period 2y

# Market summary
agno finance --summary
```

### Mathematical Calculations
```bash
# Basic calculation
agno calc "2^10 + sqrt(144)"

# With step-by-step solution
agno calc "solve: 2x + 5 = 13" --steps

# Set variables
agno calc --var "x=10"
agno calc "3*x + 2*x^2"

# List variables
agno calc --list-vars
```

### File System Operations
```bash
# List directory contents
agno files --list

# List with hidden files and recursive search
agno files --list --hidden --recursive

# Read file contents
agno files --read README.md

# Write content to file
agno files --write output.txt --content "Hello, World!"

# Get file information
agno files --info config.yaml

# Search for files
agno files --search "*.py"

# Create directory
agno files --mkdir new_project

# Copy file
agno files --copy source.txt:destination.txt

# Move file
agno files --move old_name.txt:new_name.txt

# Delete file (with confirmation)
agno files --delete temp_file.txt

# Delete without confirmation
agno files --delete temp_file.txt --no-confirm

# Display directory tree
agno files --tree

# Display tree with hidden files
agno files --tree --hidden
```

### CSV Data Operations
```bash
# Read and display CSV data
agno csv --read data.csv

# Read with custom encoding and delimiter
agno csv --read data.csv --encoding utf-8 --delimiter ";"

# Show sample of data
agno csv --read data.csv --sample --sample-size 5

# Get CSV file information
agno csv --info data.csv

# Analyze CSV data (statistics, data types, missing values)
agno csv --analyze data.csv

# Filter data by conditions
agno csv --read data.csv --filter '{"age": {"min": 30}}'

# Filter with multiple conditions
agno csv --read data.csv --filter '{"age": {"min": 25, "max": 35}, "city": "New York"}'

# Sort data by columns
agno csv --read data.csv --sort "age" --ascending "1"

# Sort by multiple columns
agno csv --read data.csv --sort "age,salary" --ascending "1,0"

# Convert CSV to JSON
agno csv --convert "data.csv:output.json:json"

# Convert CSV to Excel
agno csv --convert "data.csv:output.xlsx:excel"

# Write new CSV file
agno csv --write new_data.csv

# Merge CSV files
agno csv --merge "file1.csv:file2.csv:key_column" --output merged.csv
```

### Reasoning Traces
```bash
# List recent traces
agno trace --list

# Show detailed trace
agno trace --show trace-id

# Export trace
agno trace --export trace-id --format markdown

# View tracer statistics
agno trace --stats
```

### Performance Metrics
```bash
# System metrics summary
agno metrics --summary

# Agent-specific metrics
agno metrics --agent agent-id

# Performance leaderboard
agno metrics --leaderboard success_rate

# Export metrics
agno metrics --export --format csv
```

## 📋 Implementation Roadmap

This project is actively being developed to achieve full feature parity with Agno AI. See our [Implementation Plan](IMPLEMENTATION_PLAN.md) for detailed progress tracking and upcoming features.

### Current Status
- **✅ Phase 1**: File system operations completed
- **🔄 Phase 1**: Core infrastructure tools in progress
- **📋 Phase 2-7**: AI/ML, Business, Web, Social, Cloud, and Advanced AI tools planned

## 🏗️ Architecture

### Core Components

```
agno_cli/
├── agents/           # Multi-agent system
│   ├── agent_state.py      # Agent state tracking
│   ├── orchestrator.py     # Agent coordination
│   └── multi_agent.py      # Multi-agent system
├── reasoning/        # Reasoning and tracing
│   ├── tracer.py          # Step-by-step reasoning
│   └── metrics.py         # Performance metrics
├── tools/           # Tool integrations
│   ├── search_tools.py    # Search engines
│   ├── financial_tools.py # Financial data
│   ├── math_tools.py      # Math and data
│   ├── file_system_tools.py # File system operations
│   ├── csv_tools.py         # CSV data operations
│   ├── communication_tools.py # Communication
│   ├── knowledge_tools.py # Knowledge APIs
│   └── media_tools.py     # Media processing
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
└── cli.py           # Main CLI entry point
```

### Agent Roles

- **Leader**: Coordinates team activities, makes strategic decisions
- **Worker**: Executes assigned tasks efficiently
- **Contributor**: Provides specialized knowledge and skills
- **Specialist**: Expert in specific domains
- **Coordinator**: Facilitates communication and workflow
- **Observer**: Monitors performance and provides feedback

### Tool Categories

- **Search**: Web search across multiple engines
- **Financial**: Stock analysis, market data, portfolio management
- **Math**: Calculations, statistics, data analysis
- **File System**: Local file operations, directory management, file search
- **CSV Data**: CSV reading, writing, analysis, filtering, sorting, conversion
- **Communication**: Slack, Discord, email, GitHub integration
- **Knowledge**: Wikipedia, arXiv, news APIs
- **Media**: Image/video processing, visualization

## 🔧 Advanced Configuration

### Custom Agent Templates
```yaml
# ~/.agno_cli/templates/researcher.yaml
name: "Research Specialist"
role: "specialist"
description: "Expert researcher with access to knowledge APIs"
capabilities:
  tools: ["search_tools", "knowledge_tools", "reasoning_tools"]
  skills: ["research", "analysis", "synthesis"]
  modalities: ["text", "image"]
  languages: ["english", "spanish"]
instructions:
  - "Conduct thorough research using multiple sources"
  - "Provide citations and references"
  - "Synthesize information from diverse perspectives"
```

### Tool Configuration
```yaml
# ~/.agno_cli/config.yaml
tools:
  search:
    default_engine: "duckduckgo"
    engines:
      google:
        api_key: "your-google-api-key"
        search_engine_id: "your-cse-id"
      serpapi:
        api_key: "your-serpapi-key"
  financial:
    default_period: "1y"
    cache_duration: 300
  math:
    precision: 10
    show_steps_default: false
```

### Team Definitions
```json
{
  "team_id": "research_team",
  "name": "Research Team",
  "description": "Collaborative research and analysis team",
  "agents": [
    {
      "name": "Lead Researcher",
      "role": "leader",
      "capabilities": ["search", "knowledge", "coordination"]
    },
    {
      "name": "Data Analyst", 
      "role": "specialist",
      "capabilities": ["math", "financial", "visualization"]
    },
    {
      "name": "Content Writer",
      "role": "contributor", 
      "capabilities": ["writing", "synthesis", "communication"]
    }
  ],
  "shared_context": {
    "project": "Market Analysis Q4 2024",
    "deadline": "2024-12-31",
    "requirements": ["comprehensive", "data-driven", "actionable"]
  }
}
```

## 🧪 Testing & Development

### Automated Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agno_cli

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

### Manual Testing Commands
```bash
# Test file system operations
agno files --list                                    # List directory contents
agno files --list --hidden --recursive              # List with hidden files and recursive search
agno files --read README.md                         # Read file contents (text format)
agno files --read README.md --format json           # Read file contents (JSON format)
agno files --read setup.py --format text            # Read Python file
agno files --write test.txt --content "Hello World" # Write content to file
agno files --info README.md                         # Get file information
agno files --search "*.py"                          # Search for Python files
agno files --mkdir test_directory                   # Create directory
agno files --copy test.txt:test_directory/copy.txt  # Copy file
agno files --move test.txt:renamed.txt              # Move file
agno files --delete test.txt --no-confirm           # Delete file without confirmation
agno files --delete test_directory --recursive --no-confirm # Delete directory recursively
agno files --tree                                   # Display directory tree
agno files --tree --hidden                          # Display tree with hidden files

# Test CSV operations
agno csv --read sample_data.csv                     # Read CSV file
agno csv --info sample_data.csv                     # Get CSV information
agno csv --analyze sample_data.csv                  # Analyze CSV data
agno csv --read sample_data.csv --filter '{"age": {"min": 30}}' # Filter data
agno csv --read sample_data.csv --sort "age" --ascending "1" # Sort data
agno csv --convert "sample_data.csv:output.json:json" # Convert to JSON
agno csv --write new_data.csv                       # Write new CSV file

# Test agent operations
agno agents --list                                  # List all agents
agno agents --create "DataAnalyst" --role specialist \
  --description "Expert in data analysis" \
  --capabilities '{"tools": ["math_tools"], "skills": ["statistics"]}'

# Test chat functionality
agno chat --quick "Hello, how are you?"             # Quick chat message
agno chat --agent TeamLeader --trace                # Chat with specific agent and trace

# Test configuration
agno configure --show                               # Show current configuration
agno configure --provider anthropic --api-key test-key # Set provider and API key

# Test help and version
agno --help                                         # Show all available commands
agno files --help                                   # Show file system command help
agno version                                        # Show version information
```

### Development Environment Setup
```bash
# Activate virtual environment
pyenv activate agnocli2@virtuelenv

# Install in development mode
pip install -e .

# Run CLI directly
python -m agno_cli.cli --help

# Test specific functionality
python -c "from agno_cli.tools.file_system_tools import FileSystemToolsManager; fs = FileSystemToolsManager(); fs.list_directory()"
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### File System Operations
```bash
# Issue: Read command not showing output
# Solution: Use --format text or --format json explicitly
agno files --read file.txt --format text

# Issue: DateTime serialization errors
# Solution: Fixed in latest version - datetime objects are properly handled

# Issue: Permission denied errors
# Solution: Check file permissions and ensure safe path operations
agno files --info file.txt  # Check file permissions first
```

#### Agent Operations
```bash
# Issue: UnboundLocalError with multi_agent_system
# Solution: Fixed in latest version - proper initialization handling

# Issue: Agent state not loading correctly
# Solution: Check agents_state_agents.json and agents_state_orchestrator.json files
ls -la agents_state*.json  # Verify state files exist
```

#### Chat Operations
```bash
# Issue: TypeError with RunResponse objects
# Solution: Fixed in latest version - proper content extraction from RunResponse

# Issue: Markdown rendering errors
# Solution: Ensure content is string type before passing to Markdown()
```

### Debug Commands
```bash
# Check CLI installation
which agno
agno --version

# Check Python environment
python --version
pip list | grep agno

# Test file system tools directly
python -c "
from agno_cli.tools.file_system_tools import FileSystemToolsManager
fs = FileSystemToolsManager()
fs.list_directory()
"

# Check configuration
agno configure --show
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/paulgg-code/agno-cli.git
cd agno-cli
pip install -e .[dev]
pre-commit install
```

### Development Workflow Example

#### File System Tool Development Commands Used
```bash
# Initial testing and debugging
agno files --list                                    # Test basic listing
agno files --read README.md                          # Test file reading (initially failed)
agno files --read README.md --format text            # Test with explicit format
agno files --read README.md --format json            # Test JSON output

# Debug commands used during development
python -c "from agno_cli.tools.file_system_tools import FileSystemToolsManager; fs = FileSystemToolsManager(); fs.list_directory()"
python -c "from agno_cli.tools.file_system_tools import FileSystemTools; fs = FileSystemTools(); result = fs.read_file('README.md'); print(result.success)"

# Testing all file operations
agno files --write test.txt --content "Hello World"  # Test file writing
agno files --read test.txt                           # Test reading written file
agno files --info test.txt                           # Test file info
agno files --search "*.txt"                          # Test file search
agno files --mkdir test_dir                          # Test directory creation
agno files --copy test.txt:test_dir/copy.txt         # Test file copying
agno files --move test.txt:renamed.txt               # Test file moving
agno files --delete renamed.txt --no-confirm         # Test file deletion
agno files --delete test_dir --recursive --no-confirm # Test directory deletion
agno files --tree                                    # Test tree view
agno files --tree --hidden                           # Test tree with hidden files

# Help and documentation testing
agno --help                                          # Test main help
agno files --help                                    # Test file system help
```
```bash
# 1. Set up development environment
pyenv activate agnocli2@virtuelenv
pip install -e .

# 2. Test current functionality
agno --help
agno files --help

# 3. Implement new feature (example: file system tools)
# Edit agno_cli/tools/file_system_tools.py
# Edit agno_cli/cli.py to add new commands

# 4. Test the implementation
agno files --list
agno files --read README.md
agno files --write test.txt --content "test"

# 5. Debug issues (if any)
# Add debug output, test, remove debug output
python -c "from agno_cli.tools.file_system_tools import FileSystemToolsManager; fs = FileSystemToolsManager(); fs.list_directory()"

# 6. Update documentation
# Edit README.md with new commands and examples

# 7. Test all functionality
agno files --list --hidden --recursive
agno files --read README.md --format json
agno files --tree
```

### Code Style
- Use [Black](https://black.readthedocs.io/) for code formatting
- Follow [PEP 8](https://pep8.org/) style guidelines
- Add type hints for all functions
- Write comprehensive docstrings

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on the [Agno AI](https://github.com/agno-agi/agno) framework
- Inspired by multi-agent research and collaborative AI systems
- Thanks to all contributors and the open-source community

## 📞 Support


- **Issues**: [GitHub Issues](https://github.com/paulgg-code/agno-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/paulgg-code/agno-cli/discussions)

---

**Agno CLI Enhanced** - Bringing the power of multi-agent AI to your terminal! 🚀

