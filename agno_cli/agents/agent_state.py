"""
Agent state tracking and management for multi-agent systems
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict, field
from pathlib import Path


class AgentRole(Enum):
    """Agent roles in the multi-agent system"""
    LEADER = "leader"
    WORKER = "worker"
    CONTRIBUTOR = "contributor"
    SPECIALIST = "specialist"
    COORDINATOR = "coordinator"
    OBSERVER = "observer"


class AgentStatus(Enum):
    """Agent status states"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class TaskHistory:
    """Individual task history entry"""
    task_id: str
    description: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "pending"
    result: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'description': self.description,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'result': self.result,
            'error': self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskHistory':
        return cls(
            task_id=data['task_id'],
            description=data['description'],
            started_at=datetime.fromisoformat(data['started_at']),
            completed_at=datetime.fromisoformat(data['completed_at']) if data['completed_at'] else None,
            status=data['status'],
            result=data.get('result'),
            error=data.get('error')
        )


@dataclass
class AgentCapabilities:
    """Agent capabilities and specializations"""
    tools: Set[str] = field(default_factory=set)
    skills: Set[str] = field(default_factory=set)
    languages: Set[str] = field(default_factory=set)
    modalities: Set[str] = field(default_factory=set)  # text, code, image, video, audio
    max_concurrent_tasks: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'tools': list(self.tools),
            'skills': list(self.skills),
            'languages': list(self.languages),
            'modalities': list(self.modalities),
            'max_concurrent_tasks': self.max_concurrent_tasks
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentCapabilities':
        return cls(
            tools=set(data.get('tools', [])),
            skills=set(data.get('skills', [])),
            languages=set(data.get('languages', [])),
            modalities=set(data.get('modalities', [])),
            max_concurrent_tasks=data.get('max_concurrent_tasks', 1)
        )


@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_tokens_used: int = 0
    average_response_time: float = 0.0
    success_rate: float = 0.0
    last_active: Optional[datetime] = None
    
    def update_success_rate(self):
        """Update success rate based on completed and failed tasks"""
        total_tasks = self.tasks_completed + self.tasks_failed
        if total_tasks > 0:
            self.success_rate = self.tasks_completed / total_tasks
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'total_tokens_used': self.total_tokens_used,
            'average_response_time': self.average_response_time,
            'success_rate': self.success_rate,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMetrics':
        return cls(
            tasks_completed=data.get('tasks_completed', 0),
            tasks_failed=data.get('tasks_failed', 0),
            total_tokens_used=data.get('total_tokens_used', 0),
            average_response_time=data.get('average_response_time', 0.0),
            success_rate=data.get('success_rate', 0.0),
            last_active=datetime.fromisoformat(data['last_active']) if data.get('last_active') else None
        )


class AgentState:
    """Comprehensive agent state tracking"""
    
    def __init__(self, agent_id: str, name: str, role: AgentRole, description: str = ""):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.description = description
        self.status = AgentStatus.IDLE
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Core state
        self.current_goals: List[str] = []
        self.context: Dict[str, Any] = {}
        self.memory_keys: List[str] = []
        
        # Capabilities and tools
        self.capabilities = AgentCapabilities()
        
        # Task management
        self.current_tasks: List[str] = []
        self.task_history: List[TaskHistory] = []
        
        # Performance metrics
        self.metrics = AgentMetrics()
        
        # Communication
        self.team_id: Optional[str] = None
        self.communication_channels: Set[str] = set()
        
        # Configuration
        self.config: Dict[str, Any] = {}
    
    def add_goal(self, goal: str) -> None:
        """Add a new goal to the agent"""
        if goal not in self.current_goals:
            self.current_goals.append(goal)
            self.updated_at = datetime.now()
    
    def remove_goal(self, goal: str) -> bool:
        """Remove a goal from the agent"""
        if goal in self.current_goals:
            self.current_goals.remove(goal)
            self.updated_at = datetime.now()
            return True
        return False
    
    def update_status(self, status: AgentStatus) -> None:
        """Update agent status"""
        self.status = status
        self.updated_at = datetime.now()
        self.metrics.last_active = datetime.now()
    
    def add_task(self, task_id: str, description: str) -> None:
        """Add a new task to the agent"""
        if task_id not in self.current_tasks:
            self.current_tasks.append(task_id)
            task = TaskHistory(
                task_id=task_id,
                description=description,
                started_at=datetime.now()
            )
            self.task_history.append(task)
            self.update_status(AgentStatus.WORKING)
    
    def complete_task(self, task_id: str, result: str = None, error: str = None) -> bool:
        """Mark a task as completed"""
        if task_id in self.current_tasks:
            self.current_tasks.remove(task_id)
            
            # Update task history
            for task in self.task_history:
                if task.task_id == task_id:
                    task.completed_at = datetime.now()
                    task.status = "completed" if not error else "failed"
                    task.result = result
                    task.error = error
                    break
            
            # Update metrics
            if error:
                self.metrics.tasks_failed += 1
            else:
                self.metrics.tasks_completed += 1
            
            self.metrics.update_success_rate()
            
            # Update status
            if not self.current_tasks:
                self.update_status(AgentStatus.IDLE)
            
            return True
        return False
    
    def add_capability(self, capability_type: str, capability: str) -> None:
        """Add a capability to the agent"""
        if capability_type == "tool":
            self.capabilities.tools.add(capability)
        elif capability_type == "skill":
            self.capabilities.skills.add(capability)
        elif capability_type == "language":
            self.capabilities.languages.add(capability)
        elif capability_type == "modality":
            self.capabilities.modalities.add(capability)
        
        self.updated_at = datetime.now()
    
    def can_handle_modality(self, modality: str) -> bool:
        """Check if agent can handle a specific modality"""
        return modality in self.capabilities.modalities
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if agent has access to a specific tool"""
        return tool_name in self.capabilities.tools
    
    def has_skill(self, skill_name: str) -> bool:
        """Check if agent has a specific skill"""
        return skill_name in self.capabilities.skills
    
    def get_workload(self) -> float:
        """Get current workload as a percentage"""
        if self.capabilities.max_concurrent_tasks == 0:
            return 0.0
        return len(self.current_tasks) / self.capabilities.max_concurrent_tasks
    
    def is_available(self) -> bool:
        """Check if agent is available for new tasks"""
        return (self.status in [AgentStatus.IDLE, AgentStatus.WORKING] and 
                len(self.current_tasks) < self.capabilities.max_concurrent_tasks)
    
    def update_context(self, key: str, value: Any) -> None:
        """Update agent context"""
        self.context[key] = value
        self.updated_at = datetime.now()
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get value from agent context"""
        return self.context.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent state to dictionary"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'role': self.role.value,
            'description': self.description,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'current_goals': self.current_goals,
            'context': self.context,
            'memory_keys': self.memory_keys,
            'capabilities': self.capabilities.to_dict(),
            'current_tasks': self.current_tasks,
            'task_history': [task.to_dict() for task in self.task_history],
            'metrics': self.metrics.to_dict(),
            'team_id': self.team_id,
            'communication_channels': list(self.communication_channels),
            'config': self.config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentState':
        """Create agent state from dictionary"""
        agent = cls(
            agent_id=data['agent_id'],
            name=data['name'],
            role=AgentRole(data['role']),
            description=data.get('description', '')
        )
        
        agent.status = AgentStatus(data['status'])
        agent.created_at = datetime.fromisoformat(data['created_at'])
        agent.updated_at = datetime.fromisoformat(data['updated_at'])
        agent.current_goals = data.get('current_goals', [])
        agent.context = data.get('context', {})
        agent.memory_keys = data.get('memory_keys', [])
        agent.capabilities = AgentCapabilities.from_dict(data.get('capabilities', {}))
        agent.current_tasks = data.get('current_tasks', [])
        agent.task_history = [TaskHistory.from_dict(task) for task in data.get('task_history', [])]
        agent.metrics = AgentMetrics.from_dict(data.get('metrics', {}))
        agent.team_id = data.get('team_id')
        agent.communication_channels = set(data.get('communication_channels', []))
        agent.config = data.get('config', {})
        
        return agent
    
    def save_to_file(self, file_path: Path) -> None:
        """Save agent state to file"""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> 'AgentState':
        """Load agent state from file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """String representation of agent state"""
        return f"Agent({self.name}, {self.role.value}, {self.status.value}, tasks={len(self.current_tasks)})"
    
    def __repr__(self) -> str:
        return self.__str__()

