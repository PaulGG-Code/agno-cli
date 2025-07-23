# Agno CLI Enhanced - Multi-Agent Terminal Assistant (Beta)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/PaulGG-Code/agno-cli)
[![PyPI](https://img.shields.io/badge/PyPI-agno--cli-blue.svg)](https://pypi.org/project/agno-cli/)

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

### Pandas Data Analysis
```bash
# Read and analyze data
agno pandas --read data.csv
agno pandas --analyze data.csv
agno pandas --read data.csv --show 10

# Clean and transform data
agno pandas --read data.csv --clean '{"handle_missing": "drop", "remove_duplicates": true}'
agno pandas --read data.csv --transform '{"columns": {"select": ["name", "age"]}, "rows": {"filter": [{"column": "age", "operator": ">=", "value": 30}]}}'

# Write data to different formats
agno pandas --read data.csv --write output.csv
agno pandas --read data.csv --write output.json --format json
agno pandas --read data.csv --write output.xlsx --format excel

# Create visualizations
agno pandas --read data.csv --visualize '{"type": "histogram", "column": "age"}' --output plot.png
agno pandas --read data.csv --visualize '{"type": "scatter", "x": "age", "y": "salary"}' --output scatter.png
```

### DuckDB Database Operations
```bash
# Basic database operations
agno duckdb --database mydb.db --file --import "data.csv:employees"
agno duckdb --database mydb.db --file --list
agno duckdb --database mydb.db --file --info

# SQL queries
agno duckdb --database mydb.db --file --query "SELECT * FROM employees WHERE age > 30"
agno duckdb --database mydb.db --file --query "SELECT name, AVG(salary) FROM employees GROUP BY department"

# Table management
agno duckdb --database mydb.db --file --create-table "products:{\"id\": \"INTEGER\", \"name\": \"VARCHAR(100)\", \"price\": \"DECIMAL(10,2)\"}"
agno duckdb --database mydb.db --file --show-table employees
agno duckdb --database mydb.db --file --export "employees:export.csv"

# Database maintenance
agno duckdb --database mydb.db --file --backup backup.db
agno duckdb --database mydb.db --file --optimize
```

### SQL Query Execution
```bash
# Basic SQL operations
agno sql --file database.db --script create_tables.sql
agno sql --file database.db --list
agno sql --file database.db --info

# SQL queries
agno sql --file database.db --query "SELECT * FROM employees WHERE age > 30"
agno sql --file database.db --query "SELECT city, AVG(salary) FROM employees GROUP BY city"

# Table management
agno sql --file database.db --show-table employees
agno sql --file database.db --backup backup.db

# Multiple database types
agno sql --type mysql --host localhost --database mydb --username user --password pass --query "SELECT * FROM users"
agno sql --type postgresql --host localhost --database mydb --username user --password pass --query "SELECT * FROM users"
```

### PostgreSQL Database Integration
```bash
# Basic PostgreSQL operations
agno postgres --host localhost --database mydb --username user --password pass --info
agno postgres --host localhost --database mydb --username user --password pass --list
agno postgres --host localhost --database mydb --username user --password pass --schemas

# PostgreSQL queries
agno postgres --host localhost --database mydb --username user --password pass --query "SELECT * FROM users WHERE age > 30"
agno postgres --host localhost --database mydb --username user --password pass --query "SELECT schema_name, table_name FROM information_schema.tables"

# Table management
agno postgres --host localhost --database mydb --username user --password pass --show-table users
agno postgres --host localhost --database mydb --username user --password pass --indexes users
agno postgres --host localhost --database mydb --username user --password pass --vacuum public.users
agno postgres --host localhost --database mydb --username user --password pass --reindex public.users

# Database maintenance
agno postgres --host localhost --database mydb --username user --password pass --backup backup.dump
agno postgres --host localhost --database mydb --username user --password pass --restore backup.dump
```

### Shell System Operations
```bash
# Basic shell operations
agno shell --command "ls -la"
agno shell --command "pwd"
agno shell --command "whoami"

# System information
agno shell --info
agno shell --process 1234
agno shell --kill 1234 --signal SIGTERM

# Script execution
agno shell --script script.sh
agno shell --live --command "tail -f log.txt"
agno shell --timeout 60 --command "long-running-process"

# Command history
agno shell --history
agno shell --history-limit 10
agno shell --clear-history
```

### Docker Container Management
```bash
# Container operations
agno docker --list
agno docker --all
agno docker --info container_id
agno docker --start container_id
agno docker --stop container_id
agno docker --restart container_id
agno docker --remove container_id --force

# Container creation
agno docker --create "nginx:latest:my-nginx"
agno docker --create "python:3.9:my-app" --command "python app.py"
agno docker --create "postgres:13:my-db" --ports "5432:5432" --env "POSTGRES_PASSWORD=mypass"

# Container execution
agno docker --exec "container_id:ls -la"
agno docker --exec "container_id:cat /etc/hosts" --exec-user root

# Container logs
agno docker --logs container_id
agno docker --logs container_id --logs-tail 50
agno docker --logs container_id --logs-follow

# Image management
agno docker --images
agno docker --pull "ubuntu:20.04"
agno docker --rmi image_id --force
agno docker --build "./app:my-app" --dockerfile "Dockerfile.prod"

# System management
agno docker --system
agno docker --prune
agno docker --prune-containers
agno docker --prune-images
```

### Wikipedia Research
```bash
# Search operations
agno wikipedia --search "Python programming"
agno wikipedia --search "Machine learning" --limit 5
agno wikipedia --suggestions "artificial intelligence"

# Article operations
agno wikipedia --summary "Python (programming language)"
agno wikipedia --article "Machine learning"
agno wikipedia --random

# Related content
agno wikipedia --related "Python (programming language)"
agno wikipedia --categories "Python (programming language)"
agno wikipedia --category-articles "Programming languages"

# Language support
agno wikipedia --language-versions "Python (programming language)"
agno wikipedia --search "Python" --language "es"

# Text analysis
agno wikipedia --keywords "Python is a high-level programming language"
agno wikipedia --clear-cache
```

### arXiv Academic Papers
```bash
# Search operations
agno arxiv --search "machine learning"
agno arxiv --search "deep learning" --max-results 5
agno arxiv --search "transformer" --filter-categories "cs.AI,cs.LG"

# Paper operations
agno arxiv --paper "2401.00123"
agno arxiv --recent --max-results 10
agno arxiv --related "2401.00123"

# Author and category operations
agno arxiv --author "Yann LeCun"
agno arxiv --category "cs.AI" --max-results 20
agno arxiv --author-info "Geoffrey Hinton"
agno arxiv --categories

# Text analysis
agno arxiv --keywords "This paper presents a novel approach to machine learning"
agno arxiv --clear-cache
```

### PubMed Medical Research
```bash
# Search operations
agno pubmed --search "cancer treatment"
agno pubmed --search "diabetes" --max-results 5
agno pubmed --search "COVID-19" --database "pmc"

# Paper operations
agno pubmed --paper "37828275"
agno pubmed --recent --max-results 10
agno pubmed --related "37828275"

# Author and journal operations
agno pubmed --author "John Smith"
agno pubmed --journal "Nature" --max-results 20
agno pubmed --author-info "Jane Doe"
agno pubmed --databases

# Text analysis
agno pubmed --keywords "This study examines the effects of treatment on patient outcomes"
agno pubmed --clear-cache
```

### Sleep & Timing Operations
```bash
# Basic sleep operations
agno sleep --duration 5
agno sleep --countdown 10
agno sleep --until "14:30:00"

# Timer and performance
agno sleep --timer "ls -la" --iterations 3
agno sleep --performance --monitor-duration 30
agno sleep --time-info

# Scheduling and rate limiting
agno sleep --schedules
agno sleep --clear-schedules
agno sleep --rate-limit-info

# Options
agno sleep --no-progress --duration 3
agno sleep --format json --time-info
```

### Hacker News Integration
```bash
# Story operations
agno hackernews --top --limit 10
agno hackernews --new --limit 5
agno hackernews --best --limit 10
agno hackernews --ask --limit 5
agno hackernews --show --limit 5
agno hackernews --jobs --limit 5

# Story details and comments
agno hackernews --story 44653072
agno hackernews --comments 44653072 --max-depth 3

# User operations
agno hackernews --user "pg"
agno hackernews --user-stories "pg" --limit 10

# Search and trending
agno hackernews --search "AI" --limit 10
agno hackernews --trending --hours 24 --limit 10
agno hackernews --updates

# Options
agno hackernews --clear-cache
agno hackernews --format json --top --limit 5
```

### Data Visualization
```bash
# Chart creation
agno visualization --chart-type line --sample --sample-size 100
agno visualization --chart-type bar --sample --sample-type categorical
agno visualization --chart-type scatter --sample --sample-type trend
agno visualization --chart-type pie --sample --sample-type categorical
agno visualization --chart-type histogram --sample --sample-size 200
agno visualization --chart-type box --sample --sample-type categorical
agno visualization --chart-type heatmap --sample

# Dashboard creation
agno visualization --dashboard --chart-types "line,bar,scatter" --sample-size 100

# Chart information
agno visualization --list-types
agno visualization --chart-info scatter

# Custom data
agno visualization --chart-type line --data-file data.csv --x-column "x" --y-column "y"
agno visualization --chart-type bar --title "Sales Data" --width 1000 --height 800

# Options
agno visualization --format json --chart-type line --sample
```

### Computer Vision Operations
```bash
# Image processing
agno opencv --image image.jpg --operation resize --width 800 --height 600
agno opencv --image image.jpg --operation filter --filter-type blur
agno opencv --image image.jpg --operation brightness_contrast --brightness 50 --contrast 1.5
agno opencv --image image.jpg --operation rotate --angle 45
agno opencv --image image.jpg --operation flip --direction horizontal
agno opencv --image image.jpg --operation crop --crop-x 100 --crop-y 100 --crop-width 200 --crop-height 200

# Object detection
agno opencv --image image.jpg --detect faces
agno opencv --image image.jpg --detect eyes
agno opencv --image image.jpg --detect bodies
agno opencv --image image.jpg --detect cars

# Feature extraction
agno opencv --image image.jpg --extract basic
agno opencv --image image.jpg --extract edges
agno opencv --image image.jpg --extract corners

# Information and lists
agno opencv --image image.jpg --info
agno opencv --list-operations
agno opencv --list-objects
agno opencv --list-features

# Options
agno opencv --format json --image image.jpg --info
```

### Model Management Operations
```bash
# List and explore models
agno models --list
agno models --show gpt-4o
agno models --list-strategies
agno models --stats

# Model selection and comparison
agno models --select text_generation --strategy balanced
agno models --compare "gpt-4o,claude-3-5-sonnet,gemini-1.5-pro"

# Performance tracking
agno models --performance gpt-4o --days 7
agno models --record-performance '{"model_name":"gpt-4o","provider":"openai","test_date":"2024-01-01","latency_ms":150,"throughput_tokens_per_sec":1000}'

# Model management
agno models --register model_config.json
agno models --update "gpt-4o:temperature:0.8"
agno models --export "gpt-4o:exported_model.json"
agno models --import new_model.json

# Options
agno models --format json --list
agno models --provider openai --list
agno models --model-type text_generation --list
```

### Advanced Thinking Operations
```bash
# Start thinking sessions
agno thinking --start "Problem Title:Problem description"
agno thinking --start "Website Optimization:Improve loading speed" --framework systems_thinking

# Manage thinking sessions
agno thinking --list
agno thinking --show session_id
agno thinking --add-node "session_id:Node Title:Content:node_type"

# Problem analysis and decision making
agno thinking --analyze "How to optimize database performance"
agno thinking --decision-tree "Title:Criteria1,Criteria2:Option1,Option2,Option3"
agno thinking --experiment "Title:Scenario:Assumption1,Assumption2"

# Cognitive bias detection
agno thinking --detect-biases session_id

# Explore frameworks and biases
agno thinking --list-frameworks
agno thinking --list-biases

# Options
agno thinking --format json --list-frameworks
agno thinking --framework design_thinking --start "Title:Problem"
```

### Function Calling Operations
```bash
# Create and manage functions
agno function --create "Function Name:Description:code_file.py"
agno function --list
agno function --show function_id
agno function --delete function_id

# Execute functions
agno function --execute "function_id:param1=value1,param2=value2"
agno function --execute "function_id:data=10" --timeout 60

# Templates and code generation
agno function --list-builtin
agno function --list-templates
agno function --create-from-template "template_id:name:description"

# Execution history and monitoring
agno function --history function_id
agno function --history function_id --limit 10

# Filtering and options
agno function --type python --list
agno function --tag math --list
agno function --format json --list
```

### OpenAI Integration Operations
```bash
# Chat completions
agno openai --chat "Hello, how are you?"
agno openai --chat "Explain quantum computing" --model gpt-4o --temperature 0.3
agno openai --chat "Write a Python function" --system "You are a helpful coding assistant"

# Text embeddings
agno openai --embed "This is some text to embed"
agno openai --embed "Another text for embedding" --model text-embedding-3-small

# Image generation
agno openai --generate-image "A beautiful sunset over mountains"
agno openai --generate-image "A futuristic cityscape" --size 1792x1024 --quality hd

# Audio processing
agno openai --transcribe audio_file.mp3
agno openai --transcribe audio_file.mp3 --language en
agno openai --tts "Hello, this is a test" --voice alloy

# Content moderation
agno openai --moderate "This is a test message"

# Model and history management
agno openai --list-models
agno openai --history
agno openai --history --operation-type chat_completion --limit 10

# Options
agno openai --format json --chat "Test message"
agno openai --model gpt-4o-mini --chat "Efficient response"
```

### Web Crawling Operations
```bash
# Crawl a single web page
agno crawl4ai --crawl https://example.com
agno crawl4ai --crawl https://example.com --user-agent "Custom Bot/1.0" --timeout 60

# Create and manage crawl jobs
agno crawl4ai --create-job "My Crawl:Test crawl job:https://example.com"
agno crawl4ai --create-job "Deep Crawl:Comprehensive site crawl:https://example.com" --strategy depth_first --max-depth 5 --max-pages 500

# Execute crawl jobs
agno crawl4ai --execute-job job-id-123

# List and manage jobs
agno crawl4ai --list-jobs
agno crawl4ai --show-job job-id-123
agno crawl4ai --delete-job job-id-123

# Content search and analysis
agno crawl4ai --search "Some text content" --pattern "\\b\\w+\\b" --case-sensitive
agno crawl4ai --search "HTML content" --pattern "<[^>]+>" --format json

# Options
agno crawl4ai --format json --crawl https://example.com
agno crawl4ai --strategy breadth_first --max-depth 3 --delay 2.0
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
│   ├── pandas_tools.py      # Pandas data analysis
│   ├── duckdb_tools.py      # DuckDB database operations
│   ├── sql_tools.py         # SQL query execution
│   ├── postgres_tools.py    # PostgreSQL database integration
│   ├── shell_tools.py       # System command execution
│   ├── docker_tools.py      # Docker container management
│   ├── wikipedia_tools.py   # Wikipedia research and content retrieval
│   ├── arxiv_tools.py       # arXiv academic paper search
│   ├── pubmed_tools.py      # PubMed medical research papers
│   ├── sleep_tools.py       # Sleep and timing operations
│   ├── hackernews_tools.py  # Hacker News integration
│   ├── visualization_tools.py # Data visualization and charting
│   ├── opencv_tools.py # Computer vision operations
│   ├── models_tools.py # Model management and selection
│   ├── thinking_tools.py # Advanced thinking and reasoning
│   ├── function_tools.py # Dynamic function calling and code generation
│   ├── openai_tools.py # OpenAI API integration
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
- **Pandas Data**: Advanced data manipulation, analysis, cleaning, transformation, visualization
- **DuckDB Database**: Lightweight database operations, SQL queries, data import/export
- **SQL Database**: General SQL query execution, multi-database support
- **PostgreSQL Database**: Specialized PostgreSQL integration, advanced features
- **Shell Operations**: Safe system command execution, process management
- **Docker Management**: Container lifecycle, image management, system monitoring
- **Wikipedia Research**: Search, content retrieval, language support, text analysis
- **arXiv Papers**: Academic paper search, author analysis, category filtering
- **PubMed Research**: Medical paper search, author analysis, journal filtering
- **Sleep & Timing**: Delay operations, performance monitoring, scheduling
- **Hacker News**: Story retrieval, comments, user profiles, trending
- **Data Visualization**: Chart generation, interactive plots, dashboards
- **Computer Vision**: Image processing, object detection, feature extraction
- **Model Management**: Model selection, comparison, performance tracking
- **Advanced Thinking**: Reasoning frameworks, problem analysis, decision trees
- **Function Calling**: Dynamic function execution, code generation, automation
- **OpenAI Integration**: Direct API access for chat, embeddings, images, audio
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

# Test pandas operations
agno pandas --read sample_data.csv                  # Read data file
agno pandas --analyze sample_data.csv               # Analyze data
agno pandas --read sample_data.csv --show 5         # Show data preview
agno pandas --read sample_data.csv --clean '{"handle_missing": "drop"}' # Clean data
agno pandas --read sample_data.csv --transform '{"columns": {"select": ["name", "age"]}}' # Transform data
agno pandas --read sample_data.csv --write output.csv # Write data

# Test DuckDB operations
agno duckdb --database test.db --file --import "sample_data.csv:employees" # Import CSV
agno duckdb --database test.db --file --list # List tables
agno duckdb --database test.db --file --query "SELECT * FROM employees WHERE age > 30" # SQL query
agno duckdb --database test.db --file --show-table employees # Show table info
agno duckdb --database test.db --file --export "employees:export.csv" # Export data

# Test SQL operations
agno sql --file test.db --script create_tables.sql # Execute SQL script
agno sql --file test.db --list # List tables
agno sql --file test.db --query "SELECT * FROM employees WHERE age > 30" # SQL query
agno sql --file test.db --show-table employees # Show table info
agno sql --file test.db --backup backup.db # Backup database

# Test PostgreSQL operations
agno postgres --host localhost --database testdb --username user --password pass --info # Database info
agno postgres --host localhost --database testdb --username user --password pass --list # List tables
agno postgres --host localhost --database testdb --username user --password pass --schemas # List schemas
agno postgres --host localhost --database testdb --username user --password pass --show-table users # Show table info
agno postgres --host localhost --database testdb --username user --password pass --indexes users # Show indexes

# Test shell operations
agno shell --info # System information
agno shell --command "ls -la" # List directory
agno shell --process $$ # Current process info
agno shell --history # Command history

# Test Docker operations
agno docker --system
agno docker --list
agno docker --images
agno docker --pull "hello-world:latest"

# Test Wikipedia operations
agno wikipedia --search "Python programming"
agno wikipedia --summary "Python (programming language)"
agno wikipedia --random

# Test arXiv operations
agno arxiv --search "machine learning"
agno arxiv --paper "2401.00123"
agno arxiv --categories

# Test PubMed operations
agno pubmed --search "cancer treatment"
agno pubmed --paper "37828275"
agno pubmed --databases

# Test sleep operations
agno sleep --time-info
agno sleep --countdown 3 --no-progress
agno sleep --performance --monitor-duration 5

# Test Hacker News operations
agno hackernews --top --limit 5
agno hackernews --story 1
agno hackernews --user "pg"

# Test visualization operations
agno visualization --list-types
agno visualization --chart-type line --sample --sample-size 50
agno visualization --dashboard --chart-types "line,bar" --sample-size 30

# Test computer vision operations
agno opencv --list-operations
agno opencv --image test_image.jpg --info
agno opencv --image test_image.jpg --operation resize --width 200 --height 150
agno opencv --image test_image.jpg --extract basic

# Test model management operations
agno models --list
agno models --show gpt-4o
agno models --list-strategies
agno models --stats

# Test advanced thinking operations
agno thinking --list-frameworks
agno thinking --list-biases
agno thinking --start "Test Problem:This is a test problem"
agno thinking --analyze "How to improve system performance"

# Test function calling operations
agno function --list-builtin
agno function --list
agno function --create "Test Function:Test description:test_file.py"

# Test OpenAI integration operations
agno openai --list-models
agno openai --moderate "This is a test message"

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

