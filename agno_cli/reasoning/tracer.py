"""
Reasoning tracer for step-by-step reasoning and Chain-of-Thought tracking
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path


class TraceType(Enum):
    """Types of reasoning traces"""
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    REFLECTION = "reflection"
    DECISION = "decision"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    PLANNING = "planning"
    EXECUTION = "execution"


@dataclass
class TraceStep:
    """Individual step in reasoning trace"""
    step_id: str
    trace_type: TraceType
    content: str
    timestamp: datetime
    agent_id: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    parent_step_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'step_id': self.step_id,
            'trace_type': self.trace_type.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'agent_id': self.agent_id,
            'tool_name': self.tool_name,
            'tool_args': self.tool_args,
            'tool_result': self.tool_result,
            'confidence': self.confidence,
            'metadata': self.metadata or {},
            'parent_step_id': self.parent_step_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TraceStep':
        return cls(
            step_id=data['step_id'],
            trace_type=TraceType(data['trace_type']),
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            agent_id=data.get('agent_id'),
            tool_name=data.get('tool_name'),
            tool_args=data.get('tool_args'),
            tool_result=data.get('tool_result'),
            confidence=data.get('confidence'),
            metadata=data.get('metadata', {}),
            parent_step_id=data.get('parent_step_id')
        )


class ReasoningTrace:
    """Complete reasoning trace for a task or conversation"""
    
    def __init__(self, trace_id: str, task_description: str, agent_id: str = None):
        self.trace_id = trace_id
        self.task_description = task_description
        self.agent_id = agent_id
        self.created_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.steps: List[TraceStep] = []
        self.status = "active"  # active, completed, failed
        self.final_result: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
    
    def add_step(self, trace_type: TraceType, content: str, **kwargs) -> str:
        """Add a step to the reasoning trace"""
        step_id = str(uuid.uuid4())
        step = TraceStep(
            step_id=step_id,
            trace_type=trace_type,
            content=content,
            timestamp=datetime.now(),
            agent_id=self.agent_id,
            **kwargs
        )
        self.steps.append(step)
        return step_id
    
    def add_thought(self, thought: str, confidence: float = None) -> str:
        """Add a thought step"""
        return self.add_step(TraceType.THOUGHT, thought, confidence=confidence)
    
    def add_action(self, action: str, tool_name: str = None, tool_args: Dict[str, Any] = None) -> str:
        """Add an action step"""
        return self.add_step(TraceType.ACTION, action, tool_name=tool_name, tool_args=tool_args)
    
    def add_observation(self, observation: str, parent_step_id: str = None) -> str:
        """Add an observation step"""
        return self.add_step(TraceType.OBSERVATION, observation, parent_step_id=parent_step_id)
    
    def add_tool_call(self, tool_name: str, tool_args: Dict[str, Any], description: str = "") -> str:
        """Add a tool call step"""
        content = description or f"Calling {tool_name} with args: {tool_args}"
        return self.add_step(TraceType.TOOL_CALL, content, tool_name=tool_name, tool_args=tool_args)
    
    def add_tool_result(self, result: str, parent_step_id: str = None, tool_name: str = None) -> str:
        """Add a tool result step"""
        return self.add_step(TraceType.TOOL_RESULT, result, parent_step_id=parent_step_id, tool_name=tool_name)
    
    def add_reflection(self, reflection: str, confidence: float = None) -> str:
        """Add a reflection step"""
        return self.add_step(TraceType.REFLECTION, reflection, confidence=confidence)
    
    def add_decision(self, decision: str, confidence: float = None) -> str:
        """Add a decision step"""
        return self.add_step(TraceType.DECISION, decision, confidence=confidence)
    
    def add_error(self, error: str, metadata: Dict[str, Any] = None) -> str:
        """Add an error step"""
        return self.add_step(TraceType.ERROR, error, metadata=metadata)
    
    def complete(self, result: str = None, status: str = "completed") -> None:
        """Mark the trace as completed"""
        self.completed_at = datetime.now()
        self.status = status
        self.final_result = result
    
    def get_steps_by_type(self, trace_type: TraceType) -> List[TraceStep]:
        """Get all steps of a specific type"""
        return [step for step in self.steps if step.trace_type == trace_type]
    
    def get_duration(self) -> Optional[float]:
        """Get total duration of the trace in seconds"""
        if self.completed_at:
            return (self.completed_at - self.created_at).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary"""
        return {
            'trace_id': self.trace_id,
            'task_description': self.task_description,
            'agent_id': self.agent_id,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'steps': [step.to_dict() for step in self.steps],
            'status': self.status,
            'final_result': self.final_result,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReasoningTrace':
        trace = cls(
            trace_id=data['trace_id'],
            task_description=data['task_description'],
            agent_id=data.get('agent_id')
        )
        
        trace.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('completed_at'):
            trace.completed_at = datetime.fromisoformat(data['completed_at'])
        
        trace.steps = [TraceStep.from_dict(step_data) for step_data in data.get('steps', [])]
        trace.status = data.get('status', 'active')
        trace.final_result = data.get('final_result')
        trace.metadata = data.get('metadata', {})
        
        return trace


class ReasoningTracer:
    """Manages reasoning traces for agents"""
    
    def __init__(self, traces_dir: str = "~/.agno_cli/traces"):
        self.traces_dir = Path(traces_dir).expanduser()
        self.traces_dir.mkdir(parents=True, exist_ok=True)
        
        self.active_traces: Dict[str, ReasoningTrace] = {}
        self.trace_history: List[str] = []  # List of trace IDs
        
        # Configuration
        self.max_active_traces = 50
        self.auto_save = True
        self.verbose_output = False
    
    def start_trace(self, task_description: str, agent_id: str = None, trace_id: str = None) -> str:
        """Start a new reasoning trace"""
        if trace_id is None:
            trace_id = str(uuid.uuid4())
        
        trace = ReasoningTrace(trace_id, task_description, agent_id)
        self.active_traces[trace_id] = trace
        
        # Limit active traces
        if len(self.active_traces) > self.max_active_traces:
            oldest_trace_id = min(self.active_traces.keys(), 
                                key=lambda tid: self.active_traces[tid].created_at)
            self.complete_trace(oldest_trace_id, auto_save=True)
        
        if self.verbose_output:
            print(f"🧠 Started reasoning trace: {trace_id}")
            print(f"   Task: {task_description}")
        
        return trace_id
    
    def get_trace(self, trace_id: str) -> Optional[ReasoningTrace]:
        """Get an active trace"""
        return self.active_traces.get(trace_id)
    
    def add_step(self, trace_id: str, trace_type: TraceType, content: str, **kwargs) -> Optional[str]:
        """Add a step to a trace"""
        if trace_id not in self.active_traces:
            return None
        
        trace = self.active_traces[trace_id]
        step_id = trace.add_step(trace_type, content, **kwargs)
        
        if self.verbose_output:
            self._print_step(trace_type, content, **kwargs)
        
        return step_id
    
    def _print_step(self, trace_type: TraceType, content: str, **kwargs):
        """Print a trace step for verbose output"""
        icons = {
            TraceType.THOUGHT: "💭",
            TraceType.ACTION: "🎯",
            TraceType.OBSERVATION: "👁️",
            TraceType.REFLECTION: "🤔",
            TraceType.DECISION: "⚡",
            TraceType.TOOL_CALL: "🔧",
            TraceType.TOOL_RESULT: "📊",
            TraceType.ERROR: "❌",
            TraceType.PLANNING: "📋",
            TraceType.EXECUTION: "⚙️"
        }
        
        icon = icons.get(trace_type, "📝")
        print(f"{icon} {trace_type.value.upper()}: {content}")
        
        if kwargs.get('tool_name'):
            print(f"   Tool: {kwargs['tool_name']}")
        if kwargs.get('confidence'):
            print(f"   Confidence: {kwargs['confidence']:.2f}")
    
    def add_thought(self, trace_id: str, thought: str, confidence: float = None) -> Optional[str]:
        """Add a thought to a trace"""
        return self.add_step(trace_id, TraceType.THOUGHT, thought, confidence=confidence)
    
    def add_action(self, trace_id: str, action: str, tool_name: str = None, 
                  tool_args: Dict[str, Any] = None) -> Optional[str]:
        """Add an action to a trace"""
        return self.add_step(trace_id, TraceType.ACTION, action, tool_name=tool_name, tool_args=tool_args)
    
    def add_observation(self, trace_id: str, observation: str, parent_step_id: str = None) -> Optional[str]:
        """Add an observation to a trace"""
        return self.add_step(trace_id, TraceType.OBSERVATION, observation, parent_step_id=parent_step_id)
    
    def add_tool_call(self, trace_id: str, tool_name: str, tool_args: Dict[str, Any], 
                     description: str = "") -> Optional[str]:
        """Add a tool call to a trace"""
        return self.add_step(trace_id, TraceType.TOOL_CALL, description or f"Calling {tool_name}", 
                           tool_name=tool_name, tool_args=tool_args)
    
    def add_tool_result(self, trace_id: str, result: str, parent_step_id: str = None, 
                       tool_name: str = None) -> Optional[str]:
        """Add a tool result to a trace"""
        return self.add_step(trace_id, TraceType.TOOL_RESULT, result, 
                           parent_step_id=parent_step_id, tool_name=tool_name)
    
    def add_reflection(self, trace_id: str, reflection: str, confidence: float = None) -> Optional[str]:
        """Add a reflection to a trace"""
        return self.add_step(trace_id, TraceType.REFLECTION, reflection, confidence=confidence)
    
    def add_decision(self, trace_id: str, decision: str, confidence: float = None) -> Optional[str]:
        """Add a decision to a trace"""
        return self.add_step(trace_id, TraceType.DECISION, decision, confidence=confidence)
    
    def add_error(self, trace_id: str, error: str, metadata: Dict[str, Any] = None) -> Optional[str]:
        """Add an error to a trace"""
        return self.add_step(trace_id, TraceType.ERROR, error, metadata=metadata)
    
    def complete_trace(self, trace_id: str, result: str = None, status: str = "completed", 
                      auto_save: bool = None) -> bool:
        """Complete a reasoning trace"""
        if trace_id not in self.active_traces:
            return False
        
        trace = self.active_traces[trace_id]
        trace.complete(result, status)
        
        # Move to history
        self.trace_history.append(trace_id)
        
        # Save if auto_save is enabled
        if auto_save or (auto_save is None and self.auto_save):
            self.save_trace(trace_id)
        
        # Remove from active traces
        del self.active_traces[trace_id]
        
        if self.verbose_output:
            print(f"✅ Completed reasoning trace: {trace_id}")
            if result:
                print(f"   Result: {result}")
        
        return True
    
    def save_trace(self, trace_id: str) -> bool:
        """Save a trace to file"""
        trace = self.active_traces.get(trace_id)
        if not trace:
            return False
        
        trace_file = self.traces_dir / f"{trace_id}.json"
        
        try:
            with open(trace_file, 'w') as f:
                json.dump(trace.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving trace {trace_id}: {e}")
            return False
    
    def load_trace(self, trace_id: str) -> Optional[ReasoningTrace]:
        """Load a trace from file"""
        trace_file = self.traces_dir / f"{trace_id}.json"
        
        if not trace_file.exists():
            return None
        
        try:
            with open(trace_file, 'r') as f:
                data = json.load(f)
            return ReasoningTrace.from_dict(data)
        except Exception as e:
            print(f"Error loading trace {trace_id}: {e}")
            return None
    
    def list_traces(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent traces"""
        traces = []
        
        # Add active traces
        for trace in self.active_traces.values():
            traces.append({
                'trace_id': trace.trace_id,
                'task_description': trace.task_description,
                'agent_id': trace.agent_id,
                'status': trace.status,
                'created_at': trace.created_at.isoformat(),
                'steps_count': len(trace.steps),
                'is_active': True
            })
        
        # Add recent completed traces
        recent_trace_ids = self.trace_history[-limit:]
        for trace_id in reversed(recent_trace_ids):
            trace = self.load_trace(trace_id)
            if trace:
                traces.append({
                    'trace_id': trace.trace_id,
                    'task_description': trace.task_description,
                    'agent_id': trace.agent_id,
                    'status': trace.status,
                    'created_at': trace.created_at.isoformat(),
                    'completed_at': trace.completed_at.isoformat() if trace.completed_at else None,
                    'steps_count': len(trace.steps),
                    'duration': trace.get_duration(),
                    'is_active': False
                })
        
        # Sort by creation time (most recent first)
        traces.sort(key=lambda x: x['created_at'], reverse=True)
        
        return traces[:limit]
    
    def get_trace_summary(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a trace"""
        trace = self.active_traces.get(trace_id) or self.load_trace(trace_id)
        if not trace:
            return None
        
        step_counts = {}
        for step in trace.steps:
            step_type = step.trace_type.value
            step_counts[step_type] = step_counts.get(step_type, 0) + 1
        
        return {
            'trace_id': trace.trace_id,
            'task_description': trace.task_description,
            'agent_id': trace.agent_id,
            'status': trace.status,
            'created_at': trace.created_at.isoformat(),
            'completed_at': trace.completed_at.isoformat() if trace.completed_at else None,
            'duration': trace.get_duration(),
            'total_steps': len(trace.steps),
            'step_counts': step_counts,
            'final_result': trace.final_result
        }
    
    def export_trace(self, trace_id: str, format: str = "json") -> Optional[str]:
        """Export a trace in different formats"""
        trace = self.active_traces.get(trace_id) or self.load_trace(trace_id)
        if not trace:
            return None
        
        if format == "json":
            return json.dumps(trace.to_dict(), indent=2)
        
        elif format == "markdown":
            md_lines = [
                f"# Reasoning Trace: {trace.trace_id}",
                f"**Task:** {trace.task_description}",
                f"**Agent:** {trace.agent_id or 'Unknown'}",
                f"**Status:** {trace.status}",
                f"**Created:** {trace.created_at.isoformat()}",
                ""
            ]
            
            if trace.completed_at:
                md_lines.append(f"**Completed:** {trace.completed_at.isoformat()}")
                md_lines.append(f"**Duration:** {trace.get_duration():.2f}s")
                md_lines.append("")
            
            md_lines.append("## Reasoning Steps")
            md_lines.append("")
            
            for i, step in enumerate(trace.steps, 1):
                md_lines.append(f"### Step {i}: {step.trace_type.value.title()}")
                md_lines.append(f"**Time:** {step.timestamp.isoformat()}")
                md_lines.append(f"**Content:** {step.content}")
                
                if step.tool_name:
                    md_lines.append(f"**Tool:** {step.tool_name}")
                if step.confidence:
                    md_lines.append(f"**Confidence:** {step.confidence:.2f}")
                
                md_lines.append("")
            
            if trace.final_result:
                md_lines.append("## Final Result")
                md_lines.append(trace.final_result)
            
            return "\n".join(md_lines)
        
        elif format == "text":
            lines = [
                f"Reasoning Trace: {trace.trace_id}",
                f"Task: {trace.task_description}",
                f"Agent: {trace.agent_id or 'Unknown'}",
                f"Status: {trace.status}",
                f"Created: {trace.created_at.isoformat()}",
                ""
            ]
            
            if trace.completed_at:
                lines.append(f"Completed: {trace.completed_at.isoformat()}")
                lines.append(f"Duration: {trace.get_duration():.2f}s")
                lines.append("")
            
            lines.append("Reasoning Steps:")
            lines.append("-" * 50)
            
            for i, step in enumerate(trace.steps, 1):
                lines.append(f"{i}. [{step.trace_type.value.upper()}] {step.content}")
                if step.tool_name:
                    lines.append(f"   Tool: {step.tool_name}")
                if step.confidence:
                    lines.append(f"   Confidence: {step.confidence:.2f}")
                lines.append("")
            
            if trace.final_result:
                lines.append("Final Result:")
                lines.append("-" * 50)
                lines.append(trace.final_result)
            
            return "\n".join(lines)
        
        return None
    
    def clear_traces(self, keep_recent: int = 10) -> int:
        """Clear old traces, keeping only recent ones"""
        cleared_count = 0
        
        # Clear old trace files
        trace_files = list(self.traces_dir.glob("*.json"))
        if len(trace_files) > keep_recent:
            # Sort by modification time
            trace_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            for trace_file in trace_files[keep_recent:]:
                try:
                    trace_file.unlink()
                    cleared_count += 1
                except Exception as e:
                    print(f"Error deleting trace file {trace_file}: {e}")
        
        # Update trace history
        if len(self.trace_history) > keep_recent:
            self.trace_history = self.trace_history[-keep_recent:]
        
        return cleared_count
    
    def set_verbose(self, verbose: bool) -> None:
        """Enable or disable verbose output"""
        self.verbose_output = verbose
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tracer statistics"""
        return {
            'active_traces': len(self.active_traces),
            'total_traces_in_history': len(self.trace_history),
            'traces_directory': str(self.traces_dir),
            'auto_save_enabled': self.auto_save,
            'verbose_output': self.verbose_output,
            'max_active_traces': self.max_active_traces
        }

