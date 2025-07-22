# Agno CLI Enhanced - Multi-Agent Terminal Assistant

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful, terminal-native multi-agent assistant built on the Agno AI framework. Features advanced reasoning, team collaboration, comprehensive tool integration, and performance analytics.

## 🚀 Features

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

#### Search Tools
- **Multiple Engines**: DuckDuckGo, Google, SerpApi, Brave, SearXNG, Baidu
- **Unified Interface**: Single command for multi-engine search and result aggregation
- **Configurable**: Engine-specific settings and API key management

#### Financial Tools
- **Stock Analysis**: Real-time quotes, historical data, technical indicators
- **Portfolio Management**: Multi-stock analysis and performance comparison
- **Market Data**: Sector performance, analyst recommendations, financial statements
- **News Integration**: Company-specific news and sentiment analysis

#### Math & Data Tools
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
│   ├── communication_tools.py # Communication
│   ├── knowledge_tools.py # Knowledge APIs
│   ├── media_tools.py     # Media processing
│   └── file_tools.py      # File operations
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
- **Communication**: Slack, Discord, email, GitHub integration
- **Knowledge**: Wikipedia, arXiv, news APIs
- **Media**: Image/video processing, visualization
- **File**: Local file system operations

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

## 🧪 Testing

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

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/paulgg-code/agno-cli.git
cd agno-cli
pip install -e .[dev]
pre-commit install
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

- **Documentation**: [https://agno-cli.readthedocs.io](https://agno-cli.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/paulgg-code/agno-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/paulgg-code/agno-cli/discussions)
- **Discord**: [Join our community](https://discord.gg/agno-cli)

---

**Agno CLI Enhanced** - Bringing the power of multi-agent AI to your terminal! 🚀

