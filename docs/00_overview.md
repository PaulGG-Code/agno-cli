# Tutorial: agno-cli

The `agno-cli` project is a powerful *command-line interface* designed to interact with a
sophisticated *multi-agent AI system*. It allows users to **configure** core settings,
**manage ongoing chat sessions** with AI agents, and **orchestrate complex tasks** by
delegating them to specialized AI assistants. A rich **AI tool ecosystem** provides
agents with diverse functionalities to interact with the real world, all accessible
and controlled through a user-friendly **command interface**.


## Visual Overview

```mermaid
flowchart TD
    A0["CLI Configuration"]
    A1["Chat Session Management"]
    A2["Agent System Core"]
    A3["Task Orchestrator"]
    A4["AI Tool Ecosystem"]
    A5["User Command Interface"]
    A0 -- "Configures paths" --> A1
    A0 -- "Configures agents" --> A2
    A1 -- "Manages user chats" --> A5
    A2 -- "Hosts orchestrator" --> A3
    A2 -- "Equips agents" --> A4
    A3 -- "Delegates tasks" --> A2
    A4 -- "Exposes functionalities" --> A5
    A5 -- "Updates settings" --> A0
    A5 -- "Sends commands to" --> A2
    A5 -- "Assigns tasks to" --> A3
```

## Chapters

1. [User Command Interface](01_user_command_interface_.md)
2. [CLI Configuration](02_cli_configuration_.md)
3. [Agent System Core](03_agent_system_core_.md)
4. [Task Orchestrator](04_task_orchestrator_.md)
5. [Chat Session Management](05_chat_session_management_.md)
6. [AI Tool Ecosystem](06_ai_tool_ecosystem_.md)

---

<sub><sup>Powered by  [agno-cli](https://github.com/paulgg-code/agno-cli).</sup></sub>