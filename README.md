<h1 align="center">
  <img src="images/agno-cli_logo.png" alt="Agno CLI Logo" style="vertical-align:middle" width="60"> Agno CLI:
  <small>A Multi-Agent Terminal Assistant</small>
</h1>

  [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)&nbsp;
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)&nbsp;
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)&nbsp;
  [![GitHub](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/PaulGG-Code/agno-cli)&nbsp;
  [![PyPI](https://img.shields.io/badge/PyPI-agno--cli-blue.svg)](https://pypi.org/project/agno-cli/)


<p align="center">
  &nbsp;&nbsp;
  <a href="https://pepy.tech/projects/agno-cli">
    <img src="https://static.pepy.tech/badge/agno-cli" alt="PyPI Downloads">
  </a>
  <a href = "https://piptrends.com/package/agno-cli" alt = "agno-cli Downloads Last Week">
    <img alt="agno-cli Downloads Last Week by pip Trends" src="https://assets.piptrends.com/get-last-week-downloads-badge/agno-cli.svg">
  </a>
    <a href = "https://piptrends.com/package/agno-cli" alt = "agno-cli Average Daily Downloads">
    <img alt="agno-cli Average Daily Downloads by pip Trends" src="https://assets.piptrends.com/get-average-downloads-badge/agno-cli.svg">
  </a>
</p>


  [![Demo 1](https://raw.githubusercontent.com/PaulGG-Code/agno-cli/refs/heads/main/showcase/examples/recorded_examples/agno_cli-welcome.gif)](https://asciinema.org/a/BCraWRW2fpb6smmRKzp7ZU59E)

Agno CLI Enhanced is a robust, terminal-native multi-agent assistant built upon the innovative Agno AI framework. Designed for developers, researchers, and power users, it offers a comprehensive suite of features for advanced AI-driven task automation and collaboration directly from your command line. This tool integrates sophisticated reasoning capabilities, seamless team coordination, extensive tool integration, and detailed performance analytics to streamline complex workflows.

Whether you're managing files, conducting in-depth research, performing financial analysis, or orchestrating AI teams, Agno CLI provides an intuitive and powerful interface to enhance your productivity and decision-making processes. Its modular architecture ensures flexibility and extensibility, allowing for continuous integration of new functionalities and tools.




## Table of Contents

1. [🚀 Quick Start](#-quick-start)
2. [📦 Installation](#-installation)
   - [Basic Installation](#basic-installation)
   - [With All Features](#with-all-features)
   - [Selective Feature Installation](#selective-feature-installation)
   - [Development Installation](#development-installation)
3. [⚙️ Configuration](#-configuration)
   - [Initial Setup](#initial-setup)
   - [Environment Variables](#environment-variables)
4. [✨ Key Features](#-key-features)
   - [Multi-Agent System](#multi-agent-system)
   - [Advanced Reasoning & Tracing](#advanced-reasoning--tracing)
   - [Comprehensive Tool Integration](#comprehensive-tool-integration)
     - [File System Tools (Implemented)](#file-system-tools-implemented)
     - [Search Tools (In Development)](#search-tools-in-development)
     - [Financial Tools (In Development)](#financial-tools-in-development)
     - [Math & Data Tools (In Development)](#math--data-tools-in-development)
   - [Team Management](#team-management)
   - [Enhanced CLI Experience](#enhanced-cli-experience)
5. [🎮 Usage Examples](#-usage-examples)
   - [Available Commands](#available-commands)
   - [Interactive Chat](#interactive-chat)
   - [Agent Management](#agent-management)
   - [Team Operations](#team-operations)
     - [Team Management Examples](#team-management-examples)
       - [Creating and Managing Agents](#creating-and-managing-agents)
       - [Team Activation and Task Management](#team-activation-and-task-management)
       - [Task Execution and Monitoring](#task-execution-and-monitoring)
       - [Advanced Team Coordination](#advanced-team-coordination)
       - [Task Persistence and State Management](#task-persistence-and-state-management)
   - [Search Operations](#search-operations)
   - [Financial Analysis](#financial-analysis)
   - [Mathematical Calculations](#mathematical-calculations)
   - [File System Operations](#file-system-operations)
   - [CSV Data Operations](#csv-data-operations)
   - [Pandas Data Analysis](#pandas-data-analysis)
   - [DuckDB Database Operations](#duckdb-database-operations)
   - [SQL Query Execution](#sql-query-execution)
   - [PostgreSQL Database Integration](#postgresql-database-integration)
   - [Shell System Operations](#shell-system-operations)
   - [Docker Container Management](#docker-container-management)
   - [Wikipedia Research](#wikipedia-research)
   - [arXiv Academic Papers](#arxiv-academic-papers)
   - [PubMed Medical Research](#pubmed-medical-research)
   - [Sleep & Timing Operations](#sleep--timing-operations)
   - [Hacker News Integration](#hacker-news-integration)
   - [Data Visualization](#data-visualization)
   - [Computer Vision Operations](#computer-vision-operations)
   - [Screenshot Commands](#screenshot-commands)
   - [Model Management Operations](#model-management-operations)
   - [Advanced Thinking Operations](#advanced-thinking-operations)
6. [🎥 Demos and Showcase](#-demos-and-showcase)
7. [📄 License](#-license)




## 🚀 Quick Start

Getting started with Agno CLI Enhanced is straightforward. Follow these steps to quickly install and begin interacting with your multi-agent assistant:

```bash
# Install the CLI
pip install agno-cli

# Configure with your API key (example using Anthropic)
agno configure --provider anthropic --api-key your-api-key

# Start exploring available commands
agno --help

# List files in your current directory using the AI
agno files --list

# Engage in a quick chat with the AI assistant
agno chat --quick "Hello!"
```




## 📦 Installation

Agno CLI Enhanced offers flexible installation options to suit your needs, from a basic setup to a full-featured environment with all available tools.

### Basic Installation

To install the core Agno CLI without additional tool integrations, use the following command:

```bash
pip install agno-cli
```

### With All Features

For a comprehensive installation that includes all current and future tool integrations, use the `[all]` extra:

```bash
pip install agno-cli[all]
```

### Selective Feature Installation

If you prefer to install only specific sets of tools, you can do so by specifying the desired extras. This allows for a more lightweight installation tailored to your particular use cases:

```bash
# Install search tools for web information retrieval
pip install agno-cli[search]

# Install financial analysis tools for market data and insights
pip install agno-cli[fintech]

# Install math and data tools for advanced calculations and data manipulation
pip install agno-cli[math]

# Install communication tools for inter-agent messaging and external communication
pip install agno-cli[comm]

# Install media tools for handling various media types (e.g., image, video processing)
pip install agno-cli[media]

# Install knowledge APIs for accessing specialized knowledge bases
pip install agno-cli[knowledge]
```

### Development Installation

For contributors and developers looking to work on the Agno CLI source code, follow these steps to set up your development environment:

```bash
git clone https://github.com/paulgg-code/agno-cli.git
cd agno-cli
pip install -e ".[dev]"
```




## ⚙️ Configuration

Agno CLI Enhanced is highly configurable, allowing you to tailor its behavior to your specific needs, including API key management and model selection. Configuration settings are managed through the `agno configure` command.

### Initial Setup

To begin, you'll need to configure your API keys for the AI providers you intend to use. The CLI supports various providers, including Anthropic and OpenAI.

```bash
# Configure API keys and model settings for Anthropic
agno configure --provider anthropic --api-key your-api-key
agno configure --model claude-3-5-sonnet-20240229

# Alternatively, configure for OpenAI
agno configure --provider openai --api-key your-openai-key
agno configure --model gpt-4

# View your current configuration settings
agno configure --show
```

### Environment Variables

For persistent configuration and to avoid embedding sensitive information directly in scripts, you can set API keys and other settings as environment variables. Agno CLI will automatically detect and utilize these variables.

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-anthropic-key"

# Set your OpenAI API key
export OPENAI_API_KEY="your-openai-key"

# Customize the configuration directory (optional)
export AGNO_CONFIG_DIR="~/.agno_cli"
```




## ✨ Key Features

Agno CLI Enhanced stands out with its powerful and versatile feature set, designed to empower users with advanced AI capabilities directly within their terminal environment. The core functionalities are categorized as follows:

### Multi-Agent System

At the heart of Agno CLI is its sophisticated multi-agent architecture, enabling complex task execution through coordinated AI collaboration. This system facilitates:

* **Agent Orchestration**: Seamless coordination of multiple AI agents, each assigned distinct roles and specializations to tackle diverse aspects of a task.
* **Team Collaboration**: Agents can communicate effectively, delegate sub-tasks, and share contextual information, fostering a cohesive and efficient problem-solving environment.
* **Role-Based Architecture**: A clearly defined hierarchy of agent roles, including Leader, Worker, Contributor, Specialist, Coordinator, and Observer, ensures structured and efficient task management.
* **Dynamic Task Assignment**: Intelligent routing of tasks based on individual agent capabilities, current workload, and strategic importance, optimizing resource allocation and task completion.

### Advanced Reasoning & Tracing

To ensure transparency and facilitate debugging, Agno CLI incorporates advanced reasoning and tracing mechanisms:

* **Step-by-Step Reasoning**: Support for established AI reasoning patterns such as Chain-of-Thought (CoT) and ReAct, allowing agents to articulate their thought processes and decision-making steps.
* **Reasoning Traces**: Comprehensive, detailed logs of agent thought processes, internal deliberations, and decision paths, providing invaluable insights into AI behavior.
* **Performance Metrics**: Real-time tracking and reporting of key performance indicators, including token usage, response times, success rates, and confidence scores, for continuous optimization.
* **Real-time Monitoring**: Live display of reasoning traces via the `--trace` flag, offering immediate visibility into ongoing agent activities and interactions.

### Comprehensive Tool Integration

Agno CLI's extensibility is powered by its robust tool integration framework, allowing agents to interact with external systems and data sources. The current and planned tool integrations include:

#### File System Tools (Implemented)

These tools provide agents with full control over the local file system, enabling a wide range of data management operations:

* **File Operations**: Capabilities to read, write, list, delete, copy, and move files, ensuring comprehensive file manipulation.
* **Directory Management**: Functions for creating directories, generating tree views, and performing recursive operations on file structures.
* **File Search**: Advanced pattern-based file searching with wildcard support for efficient data retrieval.
* **File Information**: Access to detailed metadata, permissions, and MIME type detection for thorough file analysis.
* **Security**: Built-in path validation and safe file operations to prevent unauthorized access and data corruption.

#### Search Tools (In Development)

Designed to aggregate information from various web sources, these tools will provide agents with powerful research capabilities:

* **Multiple Engines**: Integration with leading search engines such as DuckDuckGo, Google, SerpApi, Brave, SearXNG, and Baidu for diverse information gathering.
* **Unified Interface**: A single command interface for executing multi-engine searches and aggregating results, simplifying complex queries.
* **Configurable**: Customizable settings and API key management for each search engine, allowing for tailored search experiences.

#### Financial Tools (In Development)

These tools are being developed to equip agents with sophisticated financial analysis capabilities:

* **Stock Analysis**: Access to real-time stock quotes, historical data, and technical indicators for in-depth market assessment.
* **Portfolio Management**: Features for multi-stock analysis and performance comparison, aiding in investment strategy.
* **Market Data**: Comprehensive market insights, including sector performance, analyst recommendations, and financial statements.
* **News Integration**: Incorporation of company-specific news and sentiment analysis to provide a holistic view of market dynamics.

#### Math & Data Tools (In Development)

These tools will enhance agents' analytical and computational prowess:

* **Advanced Calculator**: A powerful calculator with scientific functions, variable support, and step-by-step solution capabilities.
* **Statistical Analysis**: Functions for descriptive statistics, correlation, and regression analysis to derive meaningful insights from data.
* **CSV Analysis**: Tools for loading, querying, and group analysis of CSV data, facilitating structured data manipulation.
* **SQL Integration**: In-memory database querying and data manipulation capabilities for advanced data processing.

### Team Management

Agno CLI provides robust features for managing and coordinating AI teams, optimizing collaborative workflows:

* **Shared Context**: Mechanisms for team-wide information sharing and coordinated decision-making, ensuring all agents operate with the latest data.
* **Message Passing**: Efficient inter-agent communication and broadcasting capabilities for seamless information exchange.
* **Task Orchestration**: Centralized assignment and progress tracking of tasks, providing a clear overview of team activities.
* **Performance Analytics**: Team-wide metrics and individual agent performance tracking to identify bottlenecks and optimize team efficiency.

### Enhanced CLI Experience

Beyond its AI capabilities, Agno CLI is designed to offer a superior command-line interface experience:

* **Rich Terminal UI**: A visually appealing and intuitive user interface featuring beautiful tables, panels, and formatted output for enhanced readability.
* **Interactive Chat**: Multi-agent conversations with dynamic context switching, allowing for fluid and engaging interactions.
* **Modular Commands**: An organized command structure that categorizes functionalities, making the CLI easy to navigate and use.
* **Export Capabilities**: Support for exporting output in various formats, including JSON, CSV, and Markdown, for flexible data utilization.




## 🎮 Usage Examples

Agno CLI Enhanced provides a rich set of commands and functionalities. This section demonstrates common use cases and how to interact with the multi-agent system.

### Available Commands

Here's a quick reference to the core commands available in Agno CLI:

```bash
# Core commands
agno --help                    # Display all available commands and their descriptions
agno version                   # Show the current version information of Agno CLI

# Agent management
agno agents --help             # Access help for agent-related operations
agno agents --list             # List all configured AI agents
agno agents --create           # Create a new AI agent with specified roles and capabilities
agno agents --remove           # Remove an existing AI agent

# Chat interface
agno chat --help               # Access help for chat-related operations
agno chat                      # Start an interactive chat session with the default agent
agno chat --quick "message"    # Send a quick, single message to the AI assistant

# File system operations
agno files --help              # Access help for file system operations
agno files --list              # List contents of the current directory
agno files --read file.txt     # Read and display the content of a specified file
agno files --write file.txt    # Write or overwrite content to a specified file
agno files --delete file.txt   # Delete a specified file
agno files --search "*.py"     # Search for files matching a pattern (e.g., all Python files)
agno files --tree              # Display a hierarchical tree view of the current directory

# Configuration management
agno configure --help          # Access help for configuration management
agno configure --show          # Display the current configuration settings
agno configure --set           # Set or update specific configuration values
```

### Interactive Chat

Engage with your AI assistant in various chat modes, from quick queries to contextual conversations:

```bash
# Start an interactive chat session with the default agent
agno chat

# Chat with a specific agent (e.g., 'researcher') and display the reasoning trace
agno chat --agent researcher --trace

# Send a quick, non-interactive message to the AI
agno chat --quick "Explain quantum computing"

# Initiate a chat session with predefined context and a specific goal
agno chat --context '{"domain": "finance"}' --goal "Analyze market trends"
```

### Agent Management

Agno CLI allows for the creation, listing, and management of specialized AI agents, each with unique roles and capabilities:

```bash
# List all currently configured agents
agno agents --list

# Create a specialized Data Analyst agent
agno agents --create "DataAnalyst" --role specialist \
  --description "Expert in data analysis and visualization" \
  --capabilities '{"tools": ["math_tools", "csv_tools"], "skills": ["statistics", "visualization"]}'

# Create a Financial Analyst agent
agno agents --create "FinancialAnalyst" --role specialist --description "Expert in financial analysis and market research" --capabilities '{"tools": ["financial_tools", "math_tools"], "skills": ["statistics", "finance", "analysis"]}'

# Create a Data Scientist agent
agno agents --create "DataScientist" --role specialist --description "Expert in data science and machine learning" --capabilities '{"tools": ["pandas_tools", "math_tools"], "skills": ["statistics", "python", "ml"]}'

# Check the status of a specific agent by its ID
agno agents --status agent-id

# Remove an agent by its ID
agno agents --remove agent-id
```

### Team Operations

Manage and coordinate teams of agents to tackle complex, multi-faceted tasks. The team system facilitates collaboration, task assignment, and progress tracking.

```bash
# View the current status of the team, including active tasks and agent assignments
agno team --status

# Activate the team to enable task execution and agent coordination
agno team --activate

# Assign a high-priority task to the team
agno team --task "Analyze Q3 financial performance" --priority high

# Assign a research task with specific requirements for skills and tools
agno team --task "Research latest AI developments" --priority normal

# Broadcast a message to all team members for coordination or updates
agno team --message "New market data available for analysis"

# Check team status again after assigning tasks
agno team --status

# Execute assigned tasks within the team
agno team --execute-assigned

# Check team status after task execution
agno team --status

# Retrieve results for a specific task ID
agno team --results <taskID>

# Retrieve task results in a summarized format
agno team --results <taskID> --format summary

# Retrieve task results in JSON format
agno team --results <taskID> --format json

# Save task results to a file (e.g., Markdown)
agno team --results <taskID> --save financial_analysis.md

# Examples of retrieving specific task results
agno team --results bba7dcb0 --format summary
agno team --results bba7dcb0 --format json
agno team --results bba7dcb0 --save financial_analysis.md

# Deactivate the team when all tasks are complete or no longer needed
agno team --deactivate
```

#### Team Management Examples

Detailed examples demonstrating various aspects of team and agent management:

##### Creating and Managing Agents

```bash
# List all agents to see their current status and configurations
agno agents --list

# Create a Financial Analyst agent with specific capabilities
agno agents --create "FinancialAnalyst" --role specialist \
  --description "Expert in financial analysis and market research" \
  --capabilities '{"tools": ["financial_tools", "math_tools"], "skills": ["finance", "statistics", "analysis"]}'

# Create a Research Specialist agent for in-depth research tasks
agno agents --create "ResearchSpecialist" --role specialist \
  --description "Expert in research and data analysis" \
  --capabilities '{"tools": ["search_tools", "wikipedia_tools", "arxiv_tools"], "skills": ["research", "analysis", "synthesis"]}'

# Create a Data Scientist agent for machine learning and data science tasks
agno agents --create "DataScientist" --role specialist \
  --description "Expert in data science and machine learning" \
  --capabilities '{"tools": ["pandas_tools", "visualization_tools", "math_tools"], "skills": ["data_science", "ml", "statistics"]}'

# Verify the creation and capabilities of the new agents
agno agents --list
```

##### Team Activation and Task Management

```bash
# Activate the team to prepare for task execution
agno team --activate

# Assign a financial analysis task with high priority
agno team --task "Analyze stock performance for AAPL, MSFT, and GOOGL" \
  --priority high

# Assign a research task with specific skill and tool requirements
agno team --task "Research latest developments in quantum computing" \
  --priority normal \
  --requirements '{"skills": ["research", "analysis"], "tools": ["search_tools", "arxiv_tools"]}'

# Assign a data analysis task with specific skill and tool requirements
agno team --task "Analyze customer satisfaction data and create visualizations" \
  --priority normal \
  --requirements '{"skills": ["data_science", "statistics"], "tools": ["pandas_tools", "visualization_tools"]}'

# Check the team status to see pending tasks and agent assignments
agno team --status

# Send a message to the team to coordinate efforts or provide instructions
agno team --message "Please prioritize the financial analysis task - deadline is approaching"

# Deactivate the team once all tasks are completed or no longer active
agno team --deactivate
```

##### Task Execution and Monitoring

```bash
# Activate team to begin processing assigned tasks
agno team --activate

# Assign multiple tasks with varying priorities
agno team --task "Urgent: Analyze Q4 earnings reports" --priority critical \
  --requirements '{"skills": ["finance", "analysis"], "tools": ["financial_tools"]}'

agno team --task "Research competitor analysis" --priority high \
  --requirements '{"skills": ["research", "analysis"], "tools": ["search_tools"]}'

agno team --task "Create quarterly performance dashboard" --priority normal \
  --requirements '{"skills": ["data_science", "visualization"], "tools": ["pandas_tools", "visualization_tools"]}'

# Monitor the team's progress on assigned tasks
agno team --status

# Send coordination messages to guide the team's focus
agno team --message "Focus on completing the urgent earnings analysis first"

# Continuously monitor the team's status for updates
agno team --status

# Deactivate the team when all tasks are complete
agno team --deactivate
```

##### Advanced Team Coordination

```bash
# Set up a comprehensive team with specialized roles
agno agents --create "TeamLeader" --role leader \
  --description "Team coordinator and decision maker" \
  --capabilities '{"tools": ["search_tools", "communication_tools"], "skills": ["coordination", "decision_making"]}'

agno agents --create "MarketAnalyst" --role specialist \
  --description "Market and financial analysis expert" \
  --capabilities '{"tools": ["financial_tools", "math_tools"], "skills": ["finance", "market_analysis"]}'

agno agents --create "DataEngineer" --role specialist \
  --description "Data processing and engineering expert" \
  --capabilities '{"tools": ["pandas_tools", "sql_tools"], "skills": ["data_engineering", "sql"]}'

# Activate the newly formed team
agno team --activate

# Assign a complex, multi-step project to the team
agno team --task "Complete market analysis project: 1) Gather market data, 2) Analyze trends, 3) Create report" \
  --priority high \
  --requirements '{"skills": ["finance", "data_analysis", "reporting"], "tools": ["financial_tools", "pandas_tools", "visualization_tools"]}'

# Monitor progress and coordinate between phases of the project
agno team --status
agno team --message "Phase 1 complete - moving to trend analysis phase"

# Continue monitoring
agno team --status

# Deactivate the team upon project completion
agno team --deactivate
```

##### Task Persistence and State Management

Agno CLI's team system is designed for robustness, automatically persisting critical information across CLI sessions. This ensures continuity and reliability for long-running tasks.

```bash
# The team system automatically persists:
# - Team activation status (whether the team is active or inactive)
# - Assigned tasks and their current status (pending, in progress, completed)
# - Agent states and their defined capabilities
# - The complete history of task execution

# Example: A long-running task persists even if the CLI session is closed
agno team --activate
agno team --task "Long-running analysis task" --priority normal
agno team --status

# You can exit the CLI and return later; the task will still be present
# (Simulate exiting and re-opening CLI)
# agno team --status  # This command would show the same pending task

# The team activation status also persists across sessions
# (Simulate exiting and re-opening CLI)
# agno team --status  # This command would show the team is still active

# Deactivate the team when the task is finally done
agno team --deactivate
```

### Search Operations

Leverage Agno CLI's search capabilities to quickly find information across multiple search engines:

```bash
# Perform a basic search query
agno search "artificial intelligence trends 2024"

# Execute a multi-engine search and format the output as Markdown
agno search "climate change solutions" --multi --format markdown

# Perform a search using a specific engine (DuckDuckGo) and limit results to 5
agno search "python best practices" --engine duckduckgo --num 5
```

### Financial Analysis

Access real-time financial data and perform analyses directly from the terminal:

```bash
# Get detailed information about a specific stock (e.g., Apple - AAPL)
agno finance AAPL --action info

# Retrieve the latest news related to a company (e.g., Tesla - TSLA)
agno finance TSLA --action news

# Analyze the historical performance of a stock over a specified period (e.g., Microsoft - MSFT over 2 years)
agno finance MSFT --action analysis --period 2y

# Get a summary of the current market conditions
agno finance --summary
```

### Mathematical Calculations

Perform complex mathematical operations, including step-by-step solutions and variable management:

```bash
# Execute a basic mathematical calculation
agno calc "2^10 + sqrt(144)"

# Solve an equation and display the step-by-step solution
agno calc "solve: 2x + 5 = 13" --steps

# Define a variable for use in subsequent calculations
agno calc --var "x=10"

# Perform a calculation using previously defined variables
agno calc "3*x + 2*x^2"

# List all currently defined variables
agno calc --list-vars
```

### File System Operations

Manage your files and directories with a comprehensive set of commands:

```bash
# List the contents of the current directory
agno files --list

# List files, including hidden ones, and recursively search subdirectories
agno files --list --hidden --recursive

# Read and display the content of a file (e.g., README.md)
agno files --read README.md

# Write content to a new file or overwrite an existing one
agno files --write output.txt --content "Hello, World!"

# Get detailed information about a file (e.g., config.yaml)
agno files --info config.yaml

# Search for files matching a specific pattern (e.g., all Python files)
agno files --search "*.py"

# Create a new directory
agno files --mkdir new_project

# Copy a file from a source to a destination
agno files --copy source.txt:destination.txt

# Move or rename a file
agno files --move old_name.txt:new_name.txt

# Delete a file with a confirmation prompt
agno files --delete temp_file.txt

# Delete a file without a confirmation prompt
agno files --delete temp_file.txt --no-confirm

# Display a hierarchical tree view of the current directory
agno files --tree

# Display a directory tree including hidden files
agno files --tree --hidden
```

### CSV Data Operations

Interact with CSV files for data reading, analysis, and manipulation:

```bash
# Read and display the contents of a CSV file
agno csv --read data.csv

# Read a CSV file with custom encoding and delimiter
agno csv --read data.csv --encoding utf-8 --delimiter ";"

# Show a sample of the data
agno csv --read data.csv --sample --sample-size 5

# Get information about the CSV file
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

#### Screenshot Commands

```bash
agno screenshot --full-screen #Capture full screen screenshot
agno screenshot --region x,y,width,height #Capture region screenshot
agno screenshot --window "Window Title" #Capture specific window
agno screenshot --webpage https://example.com #Capture webpage screenshot
agno screenshot --element "url:selector" #Capture webpage element
agno screenshot --scrolling https://example.com #Capture scrolling webpage
agno screenshot --list #List all screenshots
agno screenshot --show-info filename #Show screenshot information
agno screenshot --screen-info #Show screen information
agno screenshot --clear #Clear all screenshots
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
# Show function details
agno function --show "function_id"

# Delete a function
agno function --delete "function_id"

# Create from template
agno function --create-from-template "template_id:name:description"

# Create and manage functions
agno function --create "Function Name:Description:code_file.py"
agno function --create "fibonacci_sequence:Calculate Fibonacci sequence up to n:fibonacci.py"
agno function --execute "864546e:data=10"

agno function --execute "864546e:data=10"
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

## 🎥 Demos and Showcase

Explore the capabilities of Agno CLI Enhanced through these interactive demonstrations:

* **Welcome to Agno CLI**: An introduction to the basic functionalities and interactive interface.
  [![Demo 1](https://raw.githubusercontent.com/PaulGG-Code/agno-cli/refs/heads/main/showcase/examples/recorded_examples/agno_cli-welcome.gif)](https://asciinema.org/a/BCraWRW2fpb6smmRKzp7ZU59E)

* **Using Pandas and CSV with Agno CLI**: Demonstrates data manipulation and analysis using Pandas and CSV tools.
  [![Demo 2](https://asciinema.org/a/uRajitiULt8FSGE2bdkJpimpJ.svg)](https://asciinema.org/a/uRajitiULt8FSGE2bdkJpimpJ)

* **Integrating DuckDB, Pandas, and CSV**: Showcases advanced data workflows with multiple tools.
  [![Demo 3](https://asciinema.org/a/TVLiViDxhYo3foXViYM0R0BCS.svg)](https://asciinema.org/a/TVLiViDxhYo3foXViYM0R0BCS)

* **Shell, Docker, Wikipedia, Arxiv, Screenshot Integration**: Illustrates comprehensive tool integration for diverse tasks.
  [![Demo 4](https://asciinema.org/a/h4sV8yv57zM7XKM6H5RMrrOp3.svg)](https://asciinema.org/a/h4sV8yv57zM7XKM6H5RMrrOp3)

* **Financial Analysis with Agno CLI**: Demonstrates the use of financial tools for market insights.
  [![Demo 5](https://asciinema.org/a/XWeLQWHNYeFFvCXXiHwKDPYJp.svg)](https://asciinema.org/a/XWeLQWHNYeFFvCXXiHwKDPYJp)

* **Automating Functions using Agno CLI**: Highlights the automation capabilities of the CLI.
  [![Demo 6](https://asciinema.org/a/PdSNs6QUUwRf0iWg3OYfv9Eru.svg)](https://asciinema.org/a/PdSNs6QUUwRf0iWg3OYfv9Eru)

* **Agent Creation, Task Assignment, and Execution**: A deep dive into the multi-agent system in action.
  [![Demo 7](https://asciinema.org/a/xVvOqO6r5il2fuATf6bmbfG3k.svg)](https://asciema.org/a/xVvOqO6r5il2fuATf6bmbfG3k)

## 🏗️ Architecture
### Core Components

```bash
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

###  Agent Roles
- Leader: Coordinates team activities, makes strategic decisions
- Worker: Executes assigned tasks efficiently
- Contributor: Provides specialized knowledge and skills
- Specialist: Expert in specific domains
- Coordinator: Facilitates communication and workflow
- Observer: Monitors performance and provides feedback

### Tool Categories
- Search: Web search across multiple engines
- Financial: Stock analysis, market data, portfolio management
- Math: Calculations, statistics, data analysis
- File System: Local file operations, directory management, file search
- CSV Data: CSV reading, writing, analysis, filtering, sorting, conversion
- Pandas Data: Advanced data manipulation, analysis, cleaning, transformation, visualization
- DuckDB Database: Lightweight database operations, SQL queries, data import/export
- SQL Database: General SQL query execution, multi-database support
- PostgreSQL Database: Specialized PostgreSQL integration, advanced features
- Shell Operations: Safe system command execution, process management
- Docker Management: Container lifecycle, image management, system monitoring
- Wikipedia Research: Search, content retrieval, language support, text analysis
- arXiv Papers: Academic paper search, author analysis, category filtering
- PubMed Research: Medical paper search, author analysis, journal filtering
- Sleep & Timing: Delay operations, performance monitoring, scheduling
- Hacker News: Story retrieval, comments, user profiles, trending
- Data Visualization: Chart generation, interactive plots, dashboards
- Computer Vision: Image processing, object detection, feature extraction
- Model Management: Model selection, comparison, performance tracking
- Advanced Thinking: Reasoning frameworks, problem analysis, decision trees
- Function Calling: Dynamic function execution, code generation, automation
- OpenAI Integration: Direct API access for chat, embeddings, images, audio
- Communication: Slack, Discord, email, GitHub integration
- Knowledge: Wikipedia, arXiv, news APIs
Media: Image/video processing, visualization

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


## 🔧 Troubleshooting

### Common Issues and Solutions

### File System Operations

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

### Agent Operations

```bash
# Issue: UnboundLocalError with multi_agent_system
# Solution: Fixed in latest version - proper initialization handling

# Issue: Agent state not loading correctly
# Solution: Check agents_state_agents.json and agents_state_orchestrator.json files
ls -la agents_state*.json  # Verify state files exist
```

### Chat Operations

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

We welcome contributions! Please see our [Contributing Guide](https://pypi.org/project/agno-cli/CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/paulgg-code/agno-cli.git
cd agno-cli
pip install -e .[dev]
pre-commit install
```

### Development Workflow Example

### File System Tool Development Commands Used

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

### 🙏 Acknowledgments

- Built on the [Agno AI framework](https://github.com/agno-agi/agno)
- Inspired by multi-agent research and collaborative AI systems
- Thanks to all contributors and the open-source community

### 📞 Support
- Issues: [GitHub Issues](https://github.com/paulgg-code/agno-cli/issues)
- Discussions: [GitHub Discussions](https://github.com/paulgg-code/agno-cli/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/PaulGG-Code/agno-cli/blob/main/LICENSE) file for details.

Agno CLI - Bringing the power of multi-agent AI to your terminal! 🚀