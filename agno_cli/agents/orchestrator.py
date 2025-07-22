"""
Agent orchestrator for multi-agent coordination and communication
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Set
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from .agent_state import AgentState, AgentRole, AgentStatus


class MessageType(Enum):
    """Types of messages between agents"""
    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETION = "task_completion"
    INFORMATION_SHARING = "information_sharing"
    REQUEST_HELP = "request_help"
    COORDINATION = "coordination"
    STATUS_UPDATE = "status_update"
    BROADCAST = "broadcast"


@dataclass
class AgentMessage:
    """Message between agents"""
    message_id: str
    from_agent: str
    to_agent: Optional[str]  # None for broadcast
    message_type: MessageType
    content: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: int = 1  # 1=low, 5=high
    requires_response: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'message_id': self.message_id,
            'from_agent': self.from_agent,
            'to_agent': self.to_agent,
            'message_type': self.message_type.value,
            'content': self.content,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority,
            'requires_response': self.requires_response
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        return cls(
            message_id=data['message_id'],
            from_agent=data['from_agent'],
            to_agent=data.get('to_agent'),
            message_type=MessageType(data['message_type']),
            content=data['content'],
            data=data.get('data', {}),
            timestamp=datetime.fromisoformat(data['timestamp']),
            priority=data.get('priority', 1),
            requires_response=data.get('requires_response', False)
        )


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class Task:
    """Task definition for agents"""
    task_id: str
    description: str
    requirements: Dict[str, Any]
    priority: TaskPriority
    assigned_agent: Optional[str] = None
    created_at: datetime = None
    deadline: Optional[datetime] = None
    dependencies: List[str] = None
    result: Optional[str] = None
    status: str = "pending"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.dependencies is None:
            self.dependencies = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'description': self.description,
            'requirements': self.requirements,
            'priority': self.priority.value,
            'assigned_agent': self.assigned_agent,
            'created_at': self.created_at.isoformat(),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'dependencies': self.dependencies,
            'result': self.result,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        return cls(
            task_id=data['task_id'],
            description=data['description'],
            requirements=data.get('requirements', {}),
            priority=TaskPriority(data.get('priority', 2)),
            assigned_agent=data.get('assigned_agent'),
            created_at=datetime.fromisoformat(data['created_at']),
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
            dependencies=data.get('dependencies', []),
            result=data.get('result'),
            status=data.get('status', 'pending')
        )


class AgentOrchestrator:
    """Orchestrates multiple agents for collaborative task execution"""
    
    def __init__(self, orchestrator_id: str = None):
        self.orchestrator_id = orchestrator_id or str(uuid.uuid4())
        self.agents: Dict[str, AgentState] = {}
        self.tasks: Dict[str, Task] = {}
        self.message_queue: List[AgentMessage] = []
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.shared_context: Dict[str, Any] = {}
        self.communication_log: List[AgentMessage] = []
        
        # Performance tracking
        self.total_tasks_completed = 0
        self.total_messages_sent = 0
        self.orchestration_start_time = datetime.now()
        
        # Setup default message handlers
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default message handlers"""
        self.register_message_handler(MessageType.TASK_COMPLETION, self._handle_task_completion)
        self.register_message_handler(MessageType.STATUS_UPDATE, self._handle_status_update)
        self.register_message_handler(MessageType.REQUEST_HELP, self._handle_help_request)
    
    def register_agent(self, agent_state: AgentState) -> None:
        """Register an agent with the orchestrator"""
        self.agents[agent_state.agent_id] = agent_state
        
        # Send welcome message
        self.send_message(
            from_agent="orchestrator",
            to_agent=agent_state.agent_id,
            message_type=MessageType.COORDINATION,
            content=f"Welcome to the team, {agent_state.name}!",
            data={"orchestrator_id": self.orchestrator_id}
        )
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the orchestrator"""
        if agent_id in self.agents:
            # Reassign any active tasks
            for task in self.tasks.values():
                if task.assigned_agent == agent_id and task.status == "active":
                    self.reassign_task(task.task_id)
            
            del self.agents[agent_id]
            return True
        return False
    
    def create_task(self, description: str, requirements: Dict[str, Any] = None, 
                   priority: TaskPriority = TaskPriority.NORMAL,
                   deadline: Optional[datetime] = None) -> str:
        """Create a new task"""
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            description=description,
            requirements=requirements or {},
            priority=priority,
            deadline=deadline
        )
        
        self.tasks[task_id] = task
        
        # Try to assign the task immediately
        self.assign_task(task_id)
        
        return task_id
    
    def assign_task(self, task_id: str, preferred_agent: str = None) -> bool:
        """Assign a task to an appropriate agent"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        # If preferred agent is specified and available
        if preferred_agent and preferred_agent in self.agents:
            agent = self.agents[preferred_agent]
            if agent.is_available() and self._agent_can_handle_task(agent, task):
                return self._assign_task_to_agent(task, agent)
        
        # Find the best agent for the task
        best_agent = self._find_best_agent_for_task(task)
        if best_agent:
            return self._assign_task_to_agent(task, best_agent)
        
        return False
    
    def _find_best_agent_for_task(self, task: Task) -> Optional[AgentState]:
        """Find the best agent for a given task"""
        available_agents = [agent for agent in self.agents.values() if agent.is_available()]
        
        if not available_agents:
            return None
        
        # Score agents based on capabilities and workload
        scored_agents = []
        for agent in available_agents:
            if self._agent_can_handle_task(agent, task):
                score = self._calculate_agent_score(agent, task)
                scored_agents.append((agent, score))
        
        if not scored_agents:
            return None
        
        # Return agent with highest score
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        return scored_agents[0][0]
    
    def _agent_can_handle_task(self, agent: AgentState, task: Task) -> bool:
        """Check if an agent can handle a specific task"""
        requirements = task.requirements
        
        # Check required tools
        if 'tools' in requirements:
            required_tools = set(requirements['tools'])
            if not required_tools.issubset(agent.capabilities.tools):
                return False
        
        # Check required skills
        if 'skills' in requirements:
            required_skills = set(requirements['skills'])
            if not required_skills.issubset(agent.capabilities.skills):
                return False
        
        # Check required modalities
        if 'modalities' in requirements:
            required_modalities = set(requirements['modalities'])
            if not required_modalities.issubset(agent.capabilities.modalities):
                return False
        
        # Check role requirements
        if 'role' in requirements:
            required_role = AgentRole(requirements['role'])
            if agent.role != required_role:
                return False
        
        return True
    
    def _calculate_agent_score(self, agent: AgentState, task: Task) -> float:
        """Calculate a score for how well an agent fits a task"""
        score = 0.0
        
        # Base score from success rate
        score += agent.metrics.success_rate * 50
        
        # Penalty for high workload
        workload = agent.get_workload()
        score -= workload * 20
        
        # Bonus for role match
        if 'role' in task.requirements:
            required_role = AgentRole(task.requirements['role'])
            if agent.role == required_role:
                score += 30
        
        # Bonus for having all required capabilities
        requirements = task.requirements
        capability_bonus = 0
        
        if 'tools' in requirements:
            required_tools = set(requirements['tools'])
            if required_tools.issubset(agent.capabilities.tools):
                capability_bonus += 10
        
        if 'skills' in requirements:
            required_skills = set(requirements['skills'])
            if required_skills.issubset(agent.capabilities.skills):
                capability_bonus += 10
        
        score += capability_bonus
        
        # Priority bonus for leader agents
        if agent.role == AgentRole.LEADER:
            score += 5
        
        return score
    
    def _assign_task_to_agent(self, task: Task, agent: AgentState) -> bool:
        """Assign a specific task to a specific agent"""
        task.assigned_agent = agent.agent_id
        task.status = "assigned"
        
        # Update agent state
        agent.add_task(task.task_id, task.description)
        
        # Send task assignment message
        self.send_message(
            from_agent="orchestrator",
            to_agent=agent.agent_id,
            message_type=MessageType.TASK_ASSIGNMENT,
            content=f"New task assigned: {task.description}",
            data={
                "task_id": task.task_id,
                "task": task.to_dict(),
                "priority": task.priority.value
            },
            requires_response=True
        )
        
        return True
    
    def reassign_task(self, task_id: str) -> bool:
        """Reassign a task to a different agent"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        # Remove from current agent if assigned
        if task.assigned_agent and task.assigned_agent in self.agents:
            current_agent = self.agents[task.assigned_agent]
            current_agent.complete_task(task_id, error="Task reassigned")
        
        # Reset task status
        task.assigned_agent = None
        task.status = "pending"
        
        # Try to assign to a new agent
        return self.assign_task(task_id)
    
    def complete_task(self, task_id: str, result: str = None, agent_id: str = None) -> bool:
        """Mark a task as completed"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = "completed"
        task.result = result
        
        # Update agent state
        if task.assigned_agent and task.assigned_agent in self.agents:
            agent = self.agents[task.assigned_agent]
            agent.complete_task(task_id, result)
        
        self.total_tasks_completed += 1
        
        # Broadcast task completion
        self.broadcast_message(
            from_agent=agent_id or "orchestrator",
            message_type=MessageType.TASK_COMPLETION,
            content=f"Task completed: {task.description}",
            data={
                "task_id": task_id,
                "result": result
            }
        )
        
        return True
    
    def send_message(self, from_agent: str, to_agent: str, message_type: MessageType,
                    content: str, data: Dict[str, Any] = None, priority: int = 1,
                    requires_response: bool = False) -> str:
        """Send a message between agents"""
        message_id = str(uuid.uuid4())
        message = AgentMessage(
            message_id=message_id,
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            data=data or {},
            timestamp=datetime.now(),
            priority=priority,
            requires_response=requires_response
        )
        
        self.message_queue.append(message)
        self.communication_log.append(message)
        self.total_messages_sent += 1
        
        # Process message immediately
        self._process_message(message)
        
        return message_id
    
    def broadcast_message(self, from_agent: str, message_type: MessageType,
                         content: str, data: Dict[str, Any] = None, priority: int = 1) -> List[str]:
        """Broadcast a message to all agents"""
        message_ids = []
        
        for agent_id in self.agents.keys():
            if agent_id != from_agent:  # Don't send to sender
                message_id = self.send_message(
                    from_agent=from_agent,
                    to_agent=agent_id,
                    message_type=message_type,
                    content=content,
                    data=data,
                    priority=priority
                )
                message_ids.append(message_id)
        
        return message_ids
    
    def register_message_handler(self, message_type: MessageType, handler: Callable) -> None:
        """Register a message handler for a specific message type"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    def _process_message(self, message: AgentMessage) -> None:
        """Process a message using registered handlers"""
        if message.message_type in self.message_handlers:
            for handler in self.message_handlers[message.message_type]:
                try:
                    handler(message)
                except Exception as e:
                    print(f"Error processing message {message.message_id}: {e}")
    
    def _handle_task_completion(self, message: AgentMessage) -> None:
        """Handle task completion messages"""
        task_id = message.data.get('task_id')
        result = message.data.get('result')
        
        if task_id:
            self.complete_task(task_id, result, message.from_agent)
    
    def _handle_status_update(self, message: AgentMessage) -> None:
        """Handle agent status update messages"""
        agent_id = message.from_agent
        if agent_id in self.agents:
            status_data = message.data.get('status', {})
            agent = self.agents[agent_id]
            
            # Update agent context with status information
            for key, value in status_data.items():
                agent.update_context(f"status_{key}", value)
    
    def _handle_help_request(self, message: AgentMessage) -> None:
        """Handle help request messages"""
        requesting_agent = message.from_agent
        help_type = message.data.get('help_type', 'general')
        
        # Find agents that can help
        helper_agents = []
        for agent_id, agent in self.agents.items():
            if (agent_id != requesting_agent and 
                agent.is_available() and
                agent.role in [AgentRole.LEADER, AgentRole.SPECIALIST]):
                helper_agents.append(agent_id)
        
        # Send help coordination message
        if helper_agents:
            for helper_id in helper_agents[:2]:  # Limit to 2 helpers
                self.send_message(
                    from_agent="orchestrator",
                    to_agent=helper_id,
                    message_type=MessageType.COORDINATION,
                    content=f"Agent {requesting_agent} needs help with {help_type}",
                    data={
                        "requesting_agent": requesting_agent,
                        "help_type": help_type,
                        "original_message": message.to_dict()
                    }
                )
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of an agent"""
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        return {
            "agent_state": agent.to_dict(),
            "current_workload": agent.get_workload(),
            "is_available": agent.is_available(),
            "recent_messages": [
                msg.to_dict() for msg in self.communication_log[-10:]
                if msg.from_agent == agent_id or msg.to_agent == agent_id
            ]
        }
    
    def get_team_status(self) -> Dict[str, Any]:
        """Get overall team status"""
        total_agents = len(self.agents)
        active_agents = len([a for a in self.agents.values() if a.status == AgentStatus.WORKING])
        idle_agents = len([a for a in self.agents.values() if a.status == AgentStatus.IDLE])
        
        pending_tasks = len([t for t in self.tasks.values() if t.status == "pending"])
        active_tasks = len([t for t in self.tasks.values() if t.status == "assigned"])
        completed_tasks = len([t for t in self.tasks.values() if t.status == "completed"])
        
        return {
            "orchestrator_id": self.orchestrator_id,
            "total_agents": total_agents,
            "active_agents": active_agents,
            "idle_agents": idle_agents,
            "pending_tasks": pending_tasks,
            "active_tasks": active_tasks,
            "completed_tasks": completed_tasks,
            "total_messages": self.total_messages_sent,
            "uptime": (datetime.now() - self.orchestration_start_time).total_seconds(),
            "agents": {agent_id: agent.to_dict() for agent_id, agent in self.agents.items()}
        }
    
    def update_shared_context(self, key: str, value: Any) -> None:
        """Update shared context available to all agents"""
        self.shared_context[key] = value
        
        # Broadcast context update
        self.broadcast_message(
            from_agent="orchestrator",
            message_type=MessageType.INFORMATION_SHARING,
            content=f"Shared context updated: {key}",
            data={
                "context_key": key,
                "context_value": value
            }
        )
    
    def get_shared_context(self, key: str = None) -> Any:
        """Get shared context"""
        if key:
            return self.shared_context.get(key)
        return self.shared_context.copy()
    
    def save_state(self, file_path: Path) -> None:
        """Save orchestrator state to file"""
        state = {
            "orchestrator_id": self.orchestrator_id,
            "agents": {agent_id: agent.to_dict() for agent_id, agent in self.agents.items()},
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "shared_context": self.shared_context,
            "communication_log": [msg.to_dict() for msg in self.communication_log[-100:]],  # Last 100 messages
            "metrics": {
                "total_tasks_completed": self.total_tasks_completed,
                "total_messages_sent": self.total_messages_sent,
                "orchestration_start_time": self.orchestration_start_time.isoformat()
            }
        }
        
        with open(file_path, 'w') as f:
            json.dump(state, f, indent=2)
    
    @classmethod
    def load_state(cls, file_path: Path) -> 'AgentOrchestrator':
        """Load orchestrator state from file"""
        with open(file_path, 'r') as f:
            state = json.load(f)
        
        orchestrator = cls(state["orchestrator_id"])
        
        # Load agents
        for agent_data in state.get("agents", {}).values():
            agent = AgentState.from_dict(agent_data)
            orchestrator.agents[agent.agent_id] = agent
        
        # Load tasks
        for task_data in state.get("tasks", {}).values():
            task = Task.from_dict(task_data)
            orchestrator.tasks[task.task_id] = task
        
        # Load shared context
        orchestrator.shared_context = state.get("shared_context", {})
        
        # Load communication log
        for msg_data in state.get("communication_log", []):
            msg = AgentMessage.from_dict(msg_data)
            orchestrator.communication_log.append(msg)
        
        # Load metrics
        metrics = state.get("metrics", {})
        orchestrator.total_tasks_completed = metrics.get("total_tasks_completed", 0)
        orchestrator.total_messages_sent = metrics.get("total_messages_sent", 0)
        if "orchestration_start_time" in metrics:
            orchestrator.orchestration_start_time = datetime.fromisoformat(metrics["orchestration_start_time"])
        
        return orchestrator

