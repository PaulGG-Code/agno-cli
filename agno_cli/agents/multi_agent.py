"""
Multi-agent system implementation for Agno CLI SDK
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat

from .agent_state import AgentState, AgentRole, AgentStatus
from .orchestrator import AgentOrchestrator, Task, TaskPriority, MessageType
from core.config import Config


class MultiAgentSystem:
    """Multi-agent system that manages multiple Agno agents"""
    
    def __init__(self, config: Config, system_id: str = None):
        self.config = config
        self.system_id = system_id or str(uuid.uuid4())
        self.orchestrator = AgentOrchestrator(f"orchestrator_{self.system_id}")
        self.agno_agents: Dict[str, Agent] = {}  # Actual Agno agents
        self.agent_states: Dict[str, AgentState] = {}  # Agent state tracking
        
        # System configuration
        self.max_agents = 10
        self.default_agent_config = {
            "show_tool_calls": False,
            "markdown": True
        }
        
        # Initialize with a default leader agent
        self._create_default_leader()
    
    def _create_default_leader(self) -> str:
        """Create a default leader agent"""
        leader_id = self.create_agent(
            name="TeamLeader",
            role=AgentRole.LEADER,
            description="Primary coordination and decision-making agent",
            capabilities={
                "tools": ["reasoning_tools", "yfinance_tools"],
                "skills": ["coordination", "planning", "decision_making"],
                "modalities": ["text"],
                "languages": ["english"]
            }
        )
        return leader_id
    
    def create_agent(self, name: str, role: AgentRole, description: str = "",
                    capabilities: Dict[str, List[str]] = None,
                    model_override: str = None) -> str:
        """Create a new agent in the system"""
        
        if len(self.agent_states) >= self.max_agents:
            raise ValueError(f"Maximum number of agents ({self.max_agents}) reached")
        
        agent_id = str(uuid.uuid4())
        
        # Create agent state
        agent_state = AgentState(agent_id, name, role, description)
        
        # Add capabilities
        if capabilities:
            for cap_type, cap_list in capabilities.items():
                for capability in cap_list:
                    agent_state.add_capability(cap_type, capability)
        
        # Create Agno agent
        model = self._get_model_for_agent(model_override)
        tools = self._get_tools_for_agent(agent_state)
        
        agno_agent = Agent(
            name=name,
            role=role.value,
            description=description,
            model=model,
            tools=tools,
            instructions=self._get_instructions_for_role(role),
            session_id=agent_id,
            **self.default_agent_config
        )
        
        # Store agents
        self.agno_agents[agent_id] = agno_agent
        self.agent_states[agent_id] = agent_state
        
        # Register with orchestrator
        self.orchestrator.register_agent(agent_state)
        
        return agent_id
    
    def _get_model_for_agent(self, model_override: str = None) -> Union[Claude, OpenAIChat]:
        """Get model instance for an agent"""
        model_id = model_override or self.config.model.model_id
        api_key = self.config.get_api_key()
        
        if not api_key:
            raise ValueError(f"No API key found for {self.config.model.provider}")
        
        model_config = {
            'id': model_id,
            'api_key': api_key,
            'temperature': self.config.model.temperature,
            'max_tokens': self.config.model.max_tokens
        }
        
        if self.config.model.provider.lower() == 'anthropic':
            return Claude(**model_config)
        elif self.config.model.provider.lower() == 'openai':
            return OpenAIChat(**model_config)
        else:
            raise ValueError(f"Unsupported model provider: {self.config.model.provider}")
    
    def _get_tools_for_agent(self, agent_state: AgentState) -> List:
        """Get tools for a specific agent based on its capabilities"""
        tools = []
        
        # Add tools based on agent capabilities
        if agent_state.has_tool("reasoning_tools"):
            from agno.tools.reasoning import ReasoningTools
            tools.append(ReasoningTools(add_instructions=True))
        
        if agent_state.has_tool("yfinance_tools"):
            from agno.tools.yfinance import YFinanceTools
            tools.append(YFinanceTools(
                stock_price=True,
                analyst_recommendations=True,
                company_info=True,
                company_news=True
            ))
        
        # Add search tools if available
        if agent_state.has_tool("duckduckgo_tools"):
            try:
                from agno.tools.duckduckgo import DuckDuckGoTools
                tools.append(DuckDuckGoTools())
            except ImportError:
                pass
        
                    # Add file system tools if available
            if agent_state.has_tool("file_system_tools"):
                try:
                    from agno.tools.file_system_tools import FileSystemTools
                    tools.append(FileSystemTools())
                except ImportError:
                    pass
            
            # Add CSV tools if available
            if agent_state.has_tool("csv_tools"):
                try:
                    from agno.tools.csv_tools import CSVTools
                    tools.append(CSVTools())
                except ImportError:
                    pass
            
            # Add pandas tools if available
            if agent_state.has_tool("pandas_tools"):
                try:
                    from agno.tools.pandas_tools import PandasTools
                    tools.append(PandasTools())
                except ImportError:
                    pass
            
            # Add DuckDB tools if available
            if agent_state.has_tool("duckdb_tools"):
                try:
                    from agno.tools.duckdb_tools import DuckDBTools
                    tools.append(DuckDBTools())
                except ImportError:
                    pass
            
            # Add SQL tools if available
            if agent_state.has_tool("sql_tools"):
                try:
                    from agno.tools.sql_tools import SQLTools
                    tools.append(SQLTools())
                except ImportError:
                    pass
            
            # Add PostgreSQL tools if available
            if agent_state.has_tool("postgres_tools"):
                try:
                    from agno.tools.postgres_tools import PostgresTools
                    tools.append(PostgresTools())
                except ImportError:
                    pass
            
            # Add Shell tools if available
            if agent_state.has_tool("shell_tools"):
                try:
                    from agno.tools.shell_tools import ShellTools
                    tools.append(ShellTools())
                except ImportError:
                    pass
            
            # Add Docker tools if available
            if agent_state.has_tool("docker_tools"):
                try:
                    from agno.tools.docker_tools import DockerTools
                    tools.append(DockerTools())
                except ImportError:
                    pass
            
            # Add Wikipedia tools if available
            if agent_state.has_tool("wikipedia_tools"):
                try:
                    from agno.tools.wikipedia_tools import WikipediaTools
                    tools.append(WikipediaTools())
                except ImportError:
                    pass
            
            # Add arXiv tools if available
            if agent_state.has_tool("arxiv_tools"):
                try:
                    from agno.tools.arxiv_tools import ArxivTools
                    tools.append(ArxivTools())
                except ImportError:
                    pass
            
            # Add PubMed tools if available
            if agent_state.has_tool("pubmed_tools"):
                try:
                    from agno.tools.pubmed_tools import PubMedTools
                    tools.append(PubMedTools())
                except ImportError:
                    pass
            
            # Add Sleep tools if available
            if agent_state.has_tool("sleep_tools"):
                try:
                    from agno.tools.sleep_tools import SleepTools
                    tools.append(SleepTools())
                except ImportError:
                    pass
            
            # Add Hacker News tools if available
            if agent_state.has_tool("hackernews_tools"):
                try:
                    from agno.tools.hackernews_tools import HackerNewsTools
                    tools.append(HackerNewsTools())
                except ImportError:
                    pass
            
            # Add Visualization tools if available
            if agent_state.has_tool("visualization_tools"):
                try:
                    from agno.tools.visualization_tools import VisualizationTools
                    tools.append(VisualizationTools())
                except ImportError:
                    pass
            
            # Add OpenCV tools if available
            if agent_state.has_tool("opencv_tools"):
                try:
                    from agno.tools.opencv_tools import OpenCVTools
                    tools.append(OpenCVTools())
                except ImportError:
                    pass
            
            # Add Models tools if available
            if agent_state.has_tool("models_tools"):
                try:
                    from agno.tools.models_tools import ModelsTools
                    tools.append(ModelsTools())
                except ImportError:
                    pass
            
            # Add Thinking tools if available
            if agent_state.has_tool("thinking_tools"):
                try:
                    from agno.tools.thinking_tools import ThinkingTools
                    tools.append(ThinkingTools())
                except ImportError:
                    pass
            
            # Add Function tools if available
            if agent_state.has_tool("function_tools"):
                try:
                    from agno.tools.function_tools import FunctionTools
                    tools.append(FunctionTools())
                except ImportError:
                    pass
            
            # Add OpenAI tools if available
            if agent_state.has_tool("openai_tools"):
                try:
                    from agno.tools.openai_tools import OpenAITools
                    tools.append(OpenAITools())
                except ImportError:
                    pass
            
            # Add Crawl4AI tools if available
            if agent_state.has_tool("crawl4ai_tools"):
                try:
                    from agno.tools.crawl4ai_tools import Crawl4AITools
                    tools.append(Crawl4AITools())
                except ImportError:
                    pass
        
        return tools
    
    def _get_instructions_for_role(self, role: AgentRole) -> List[str]:
        """Get role-specific instructions for an agent"""
        base_instructions = [
            "Be helpful and informative",
            "Communicate clearly with other agents",
            "Report task progress and completion"
        ]
        
        role_instructions = {
            AgentRole.LEADER: [
                "Coordinate team activities and delegate tasks",
                "Make strategic decisions for the team",
                "Monitor overall progress and resolve conflicts",
                "Provide guidance and support to other agents"
            ],
            AgentRole.WORKER: [
                "Execute assigned tasks efficiently",
                "Request help when needed",
                "Report progress regularly",
                "Follow team protocols and guidelines"
            ],
            AgentRole.CONTRIBUTOR: [
                "Contribute specialized knowledge and skills",
                "Collaborate effectively with team members",
                "Share insights and findings with the team",
                "Support team goals and objectives"
            ],
            AgentRole.SPECIALIST: [
                "Provide expert knowledge in your domain",
                "Assist other agents with specialized tasks",
                "Maintain high quality standards",
                "Share best practices and expertise"
            ],
            AgentRole.COORDINATOR: [
                "Facilitate communication between agents",
                "Manage task dependencies and scheduling",
                "Ensure smooth workflow coordination",
                "Monitor team performance and efficiency"
            ],
            AgentRole.OBSERVER: [
                "Monitor system performance and behavior",
                "Collect and analyze team metrics",
                "Identify potential issues and improvements",
                "Provide feedback and recommendations"
            ]
        }
        
        return base_instructions + role_instructions.get(role, [])
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the system"""
        if agent_id not in self.agent_states:
            return False
        
        # Don't allow removing the last agent
        if len(self.agent_states) <= 1:
            raise ValueError("Cannot remove the last agent in the system")
        
        # Unregister from orchestrator
        self.orchestrator.unregister_agent(agent_id)
        
        # Remove from storage
        del self.agno_agents[agent_id]
        del self.agent_states[agent_id]
        
        return True
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an Agno agent by ID"""
        return self.agno_agents.get(agent_id)
    
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Get agent state by ID"""
        return self.agent_states.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents in the system"""
        agents = []
        for agent_id, agent_state in self.agent_states.items():
            agents.append({
                "agent_id": agent_id,
                "name": agent_state.name,
                "role": agent_state.role.value,
                "status": agent_state.status.value,
                "workload": agent_state.get_workload(),
                "is_available": agent_state.is_available(),
                "capabilities": agent_state.capabilities.to_dict(),
                "metrics": agent_state.metrics.to_dict()
            })
        return agents
    
    def assign_task(self, description: str, requirements: Dict[str, Any] = None,
                   priority: TaskPriority = TaskPriority.NORMAL,
                   preferred_agent: str = None) -> str:
        """Assign a task to the multi-agent system"""
        task_id = self.orchestrator.create_task(
            description=description,
            requirements=requirements,
            priority=priority
        )
        
        if preferred_agent:
            self.orchestrator.assign_task(task_id, preferred_agent)
        
        return task_id
    
    def execute_task(self, agent_id: str, task_description: str, 
                    context: Dict[str, Any] = None) -> str:
        """Execute a task with a specific agent"""
        if agent_id not in self.agno_agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self.agno_agents[agent_id]
        agent_state = self.agent_states[agent_id]
        
        # Update agent status
        agent_state.update_status(AgentStatus.WORKING)
        
        # Add context to the task description if provided
        full_description = task_description
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            full_description = f"{task_description}\n\nContext:\n{context_str}"
        
        try:
            # Execute with the Agno agent
            response = agent.run(message=full_description)
            
            # Update agent state
            agent_state.update_status(AgentStatus.IDLE)
            agent_state.metrics.tasks_completed += 1
            agent_state.metrics.update_success_rate()
            
            return response or "Task completed successfully"
            
        except Exception as e:
            # Update agent state with error
            agent_state.update_status(AgentStatus.ERROR)
            agent_state.metrics.tasks_failed += 1
            agent_state.metrics.update_success_rate()
            
            error_msg = f"Error executing task: {str(e)}"
            return error_msg
    
    def chat_with_agent(self, agent_id: str, message: str, stream: bool = False) -> str:
        """Chat with a specific agent"""
        if agent_id not in self.agno_agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self.agno_agents[agent_id]
        agent_state = self.agent_states[agent_id]
        
        # Update agent status
        agent_state.update_status(AgentStatus.WORKING)
        
        try:
            if stream:
                response = ""
                for event in agent.stream(message=message):
                    if hasattr(event, 'data') and hasattr(event.data, 'response'):
                        if event.data.response and event.data.response.output:
                            chunk = event.data.response.output
                            response += chunk
                            print(chunk, end="", flush=True)
                print()  # New line after streaming
            else:
                run_response = agent.run(message=message)
                # Extract content from RunResponse object
                if hasattr(run_response, 'content'):
                    response = run_response.content
                else:
                    response = str(run_response)
            
            # Update agent state
            agent_state.update_status(AgentStatus.IDLE)
            agent_state.metrics.last_active = datetime.now()
            
            return response or "No response generated"
            
        except Exception as e:
            agent_state.update_status(AgentStatus.ERROR)
            error_msg = f"Error in chat: {str(e)}"
            return error_msg
    
    def send_agent_message(self, from_agent: str, to_agent: str, message: str,
                          message_type: MessageType = MessageType.INFORMATION_SHARING) -> str:
        """Send a message between agents"""
        return self.orchestrator.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content=message
        )
    
    def broadcast_message(self, from_agent: str, message: str,
                         message_type: MessageType = MessageType.BROADCAST) -> List[str]:
        """Broadcast a message to all agents"""
        return self.orchestrator.broadcast_message(
            from_agent=from_agent,
            message_type=message_type,
            content=message
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        team_status = self.orchestrator.get_team_status()
        
        return {
            "system_id": self.system_id,
            "team_status": team_status,
            "agents": self.list_agents(),
            "configuration": {
                "max_agents": self.max_agents,
                "model_provider": self.config.model.provider,
                "model_id": self.config.model.model_id
            }
        }
    
    def update_agent_capabilities(self, agent_id: str, capabilities: Dict[str, List[str]]) -> bool:
        """Update an agent's capabilities"""
        if agent_id not in self.agent_states:
            return False
        
        agent_state = self.agent_states[agent_id]
        
        # Update capabilities
        for cap_type, cap_list in capabilities.items():
            for capability in cap_list:
                agent_state.add_capability(cap_type, capability)
        
        # Recreate the Agno agent with new tools
        agno_agent = self.agno_agents[agent_id]
        new_tools = self._get_tools_for_agent(agent_state)
        
        # Update the agent's tools (this is a simplified approach)
        # In a real implementation, you might need to recreate the agent
        agno_agent.tools = new_tools
        
        return True
    
    def save_system_state(self, file_path: Path) -> None:
        """Save the entire system state"""
        # Save orchestrator state
        orchestrator_path = file_path.parent / f"{file_path.stem}_orchestrator.json"
        self.orchestrator.save_state(orchestrator_path)
        
        # Save agent states
        agents_path = file_path.parent / f"{file_path.stem}_agents.json"
        agent_data = {
            agent_id: agent_state.to_dict() 
            for agent_id, agent_state in self.agent_states.items()
        }
        
        import json
        with open(agents_path, 'w') as f:
            json.dump({
                "system_id": self.system_id,
                "agents": agent_data,
                "config": self.config.to_dict()
            }, f, indent=2)
    
    @classmethod
    def load_system_state(cls, file_path: Path, config: Config) -> 'MultiAgentSystem':
        """Load system state from files"""
        import json
        
        # Load agent states
        agents_path = file_path.parent / f"{file_path.stem}_agents.json"
        with open(agents_path, 'r') as f:
            data = json.load(f)
        
        system = cls(config, data["system_id"])
        
        # Clear default agents
        system.agent_states.clear()
        system.agno_agents.clear()
        
        # Recreate agents
        for agent_id, agent_data in data["agents"].items():
            agent_state = AgentState.from_dict(agent_data)
            system.agent_states[agent_id] = agent_state
            
            # Recreate Agno agent
            model = system._get_model_for_agent()
            tools = system._get_tools_for_agent(agent_state)
            
            agno_agent = Agent(
                name=agent_state.name,
                role=agent_state.role.value,
                description=agent_state.description,
                model=model,
                tools=tools,
                instructions=system._get_instructions_for_role(agent_state.role),
                session_id=agent_id,
                **system.default_agent_config
            )
            
            system.agno_agents[agent_id] = agno_agent
            system.orchestrator.register_agent(agent_state)
        
        # Load orchestrator state
        orchestrator_path = file_path.parent / f"{file_path.stem}_orchestrator.json"
        if orchestrator_path.exists():
            system.orchestrator = AgentOrchestrator.load_state(orchestrator_path)
        
        return system
    
    def shutdown(self) -> None:
        """Shutdown the multi-agent system"""
        # Update all agents to offline status
        for agent_state in self.agent_states.values():
            agent_state.update_status(AgentStatus.OFFLINE)
        
        # Clear references
        self.agno_agents.clear()
        self.agent_states.clear()
    
    def __len__(self) -> int:
        """Number of agents in the system"""
        return len(self.agent_states)
    
    def __contains__(self, agent_id: str) -> bool:
        """Check if agent exists in the system"""
        return agent_id in self.agent_states

