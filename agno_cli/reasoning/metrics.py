"""
Metrics collection and analysis for agent performance tracking
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque


@dataclass
class TokenUsage:
    """Token usage metrics"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    def add(self, other: 'TokenUsage') -> None:
        """Add another TokenUsage to this one"""
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.total_tokens += other.total_tokens
    
    def to_dict(self) -> Dict[str, int]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'TokenUsage':
        return cls(**data)


@dataclass
class ToolMetrics:
    """Tool usage metrics"""
    tool_name: str
    calls_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_duration: float = 0.0
    average_duration: float = 0.0
    last_used: Optional[datetime] = None
    
    def add_call(self, success: bool, duration: float) -> None:
        """Add a tool call result"""
        self.calls_count += 1
        self.total_duration += duration
        self.average_duration = self.total_duration / self.calls_count
        self.last_used = datetime.now()
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.calls_count == 0:
            return 0.0
        return self.success_count / self.calls_count
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.last_used:
            data['last_used'] = self.last_used.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolMetrics':
        if 'last_used' in data and data['last_used']:
            data['last_used'] = datetime.fromisoformat(data['last_used'])
        return cls(**data)


@dataclass
class ConversationMetrics:
    """Metrics for a single conversation/task"""
    conversation_id: str
    agent_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    message_count: int = 0
    token_usage: TokenUsage = None
    tool_calls: Dict[str, ToolMetrics] = None
    response_times: List[float] = None
    confidence_scores: List[float] = None
    success: Optional[bool] = None
    error_count: int = 0
    
    def __post_init__(self):
        if self.token_usage is None:
            self.token_usage = TokenUsage()
        if self.tool_calls is None:
            self.tool_calls = {}
        if self.response_times is None:
            self.response_times = []
        if self.confidence_scores is None:
            self.confidence_scores = []
    
    @property
    def duration(self) -> Optional[float]:
        """Get conversation duration in seconds"""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def average_response_time(self) -> float:
        """Get average response time"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    @property
    def average_confidence(self) -> float:
        """Get average confidence score"""
        if not self.confidence_scores:
            return 0.0
        return sum(self.confidence_scores) / len(self.confidence_scores)
    
    def add_message(self, response_time: float, token_usage: TokenUsage = None, 
                   confidence: float = None) -> None:
        """Add a message to the conversation"""
        self.message_count += 1
        self.response_times.append(response_time)
        
        if token_usage:
            self.token_usage.add(token_usage)
        
        if confidence is not None:
            self.confidence_scores.append(confidence)
    
    def add_tool_call(self, tool_name: str, success: bool, duration: float) -> None:
        """Add a tool call result"""
        if tool_name not in self.tool_calls:
            self.tool_calls[tool_name] = ToolMetrics(tool_name)
        
        self.tool_calls[tool_name].add_call(success, duration)
    
    def complete(self, success: bool = True) -> None:
        """Mark conversation as completed"""
        self.completed_at = datetime.now()
        self.success = success
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'conversation_id': self.conversation_id,
            'agent_id': self.agent_id,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'message_count': self.message_count,
            'token_usage': self.token_usage.to_dict(),
            'tool_calls': {name: metrics.to_dict() for name, metrics in self.tool_calls.items()},
            'response_times': self.response_times,
            'confidence_scores': self.confidence_scores,
            'success': self.success,
            'error_count': self.error_count,
            'duration': self.duration,
            'average_response_time': self.average_response_time,
            'average_confidence': self.average_confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMetrics':
        metrics = cls(
            conversation_id=data['conversation_id'],
            agent_id=data['agent_id'],
            started_at=datetime.fromisoformat(data['started_at']),
            message_count=data.get('message_count', 0),
            success=data.get('success'),
            error_count=data.get('error_count', 0)
        )
        
        if data.get('completed_at'):
            metrics.completed_at = datetime.fromisoformat(data['completed_at'])
        
        if 'token_usage' in data:
            metrics.token_usage = TokenUsage.from_dict(data['token_usage'])
        
        if 'tool_calls' in data:
            metrics.tool_calls = {
                name: ToolMetrics.from_dict(tool_data) 
                for name, tool_data in data['tool_calls'].items()
            }
        
        metrics.response_times = data.get('response_times', [])
        metrics.confidence_scores = data.get('confidence_scores', [])
        
        return metrics


class AgentMetrics:
    """Comprehensive metrics for an agent"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.created_at = datetime.now()
        
        # Conversation tracking
        self.conversations: Dict[str, ConversationMetrics] = {}
        self.active_conversations: Dict[str, ConversationMetrics] = {}
        
        # Aggregated metrics
        self.total_conversations = 0
        self.successful_conversations = 0
        self.total_messages = 0
        self.total_token_usage = TokenUsage()
        self.total_tool_calls = defaultdict(lambda: ToolMetrics(""))
        
        # Performance tracking
        self.response_times = deque(maxlen=1000)  # Keep last 1000 response times
        self.confidence_scores = deque(maxlen=1000)  # Keep last 1000 confidence scores
        
        # Time-based metrics
        self.daily_stats: Dict[str, Dict[str, Any]] = {}
        self.hourly_stats: Dict[str, Dict[str, Any]] = {}
    
    def start_conversation(self, conversation_id: str) -> ConversationMetrics:
        """Start tracking a new conversation"""
        conversation = ConversationMetrics(
            conversation_id=conversation_id,
            agent_id=self.agent_id,
            started_at=datetime.now()
        )
        
        self.active_conversations[conversation_id] = conversation
        return conversation
    
    def end_conversation(self, conversation_id: str, success: bool = True) -> bool:
        """End a conversation and move it to completed"""
        if conversation_id not in self.active_conversations:
            return False
        
        conversation = self.active_conversations[conversation_id]
        conversation.complete(success)
        
        # Move to completed conversations
        self.conversations[conversation_id] = conversation
        del self.active_conversations[conversation_id]
        
        # Update aggregated metrics
        self._update_aggregated_metrics(conversation)
        self._update_time_based_metrics(conversation)
        
        return True
    
    def add_message(self, conversation_id: str, response_time: float, 
                   token_usage: TokenUsage = None, confidence: float = None) -> bool:
        """Add a message to a conversation"""
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            return False
        
        conversation.add_message(response_time, token_usage, confidence)
        
        # Update performance tracking
        self.response_times.append(response_time)
        if confidence is not None:
            self.confidence_scores.append(confidence)
        
        return True
    
    def add_tool_call(self, conversation_id: str, tool_name: str, 
                     success: bool, duration: float) -> bool:
        """Add a tool call to a conversation"""
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            return False
        
        conversation.add_tool_call(tool_name, success, duration)
        return True
    
    def _update_aggregated_metrics(self, conversation: ConversationMetrics) -> None:
        """Update aggregated metrics with completed conversation"""
        self.total_conversations += 1
        if conversation.success:
            self.successful_conversations += 1
        
        self.total_messages += conversation.message_count
        self.total_token_usage.add(conversation.token_usage)
        
        # Update tool metrics
        for tool_name, tool_metrics in conversation.tool_calls.items():
            if tool_name not in self.total_tool_calls:
                self.total_tool_calls[tool_name] = ToolMetrics(tool_name)
            
            total_tool = self.total_tool_calls[tool_name]
            total_tool.calls_count += tool_metrics.calls_count
            total_tool.success_count += tool_metrics.success_count
            total_tool.failure_count += tool_metrics.failure_count
            total_tool.total_duration += tool_metrics.total_duration
            total_tool.average_duration = total_tool.total_duration / total_tool.calls_count
            total_tool.last_used = tool_metrics.last_used
    
    def _update_time_based_metrics(self, conversation: ConversationMetrics) -> None:
        """Update time-based metrics"""
        date_key = conversation.started_at.strftime("%Y-%m-%d")
        hour_key = conversation.started_at.strftime("%Y-%m-%d-%H")
        
        # Daily stats
        if date_key not in self.daily_stats:
            self.daily_stats[date_key] = {
                'conversations': 0,
                'messages': 0,
                'tokens': TokenUsage(),
                'success_rate': 0.0
            }
        
        daily = self.daily_stats[date_key]
        daily['conversations'] += 1
        daily['messages'] += conversation.message_count
        daily['tokens'].add(conversation.token_usage)
        
        # Hourly stats
        if hour_key not in self.hourly_stats:
            self.hourly_stats[hour_key] = {
                'conversations': 0,
                'messages': 0,
                'tokens': TokenUsage(),
                'avg_response_time': 0.0
            }
        
        hourly = self.hourly_stats[hour_key]
        hourly['conversations'] += 1
        hourly['messages'] += conversation.message_count
        hourly['tokens'].add(conversation.token_usage)
        hourly['avg_response_time'] = conversation.average_response_time
    
    @property
    def success_rate(self) -> float:
        """Calculate overall success rate"""
        if self.total_conversations == 0:
            return 0.0
        return self.successful_conversations / self.total_conversations
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    @property
    def average_confidence(self) -> float:
        """Calculate average confidence score"""
        if not self.confidence_scores:
            return 0.0
        return sum(self.confidence_scores) / len(self.confidence_scores)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of agent metrics"""
        return {
            'agent_id': self.agent_id,
            'created_at': self.created_at.isoformat(),
            'total_conversations': self.total_conversations,
            'successful_conversations': self.successful_conversations,
            'success_rate': self.success_rate,
            'total_messages': self.total_messages,
            'average_response_time': self.average_response_time,
            'average_confidence': self.average_confidence,
            'token_usage': self.total_token_usage.to_dict(),
            'active_conversations': len(self.active_conversations),
            'tool_usage': {
                name: metrics.to_dict() 
                for name, metrics in self.total_tool_calls.items()
            }
        }
    
    def get_daily_stats(self, days: int = 7) -> Dict[str, Dict[str, Any]]:
        """Get daily statistics for the last N days"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        stats = {}
        current_date = start_date
        
        while current_date <= end_date:
            date_key = current_date.strftime("%Y-%m-%d")
            stats[date_key] = self.daily_stats.get(date_key, {
                'conversations': 0,
                'messages': 0,
                'tokens': TokenUsage().to_dict(),
                'success_rate': 0.0
            })
            current_date += timedelta(days=1)
        
        return stats
    
    def get_tool_performance(self) -> List[Dict[str, Any]]:
        """Get tool performance metrics"""
        tools = []
        for tool_metrics in self.total_tool_calls.values():
            tools.append(tool_metrics.to_dict())
        
        # Sort by usage count
        tools.sort(key=lambda x: x['calls_count'], reverse=True)
        return tools
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'agent_id': self.agent_id,
            'created_at': self.created_at.isoformat(),
            'conversations': {
                conv_id: conv.to_dict() 
                for conv_id, conv in self.conversations.items()
            },
            'active_conversations': {
                conv_id: conv.to_dict() 
                for conv_id, conv in self.active_conversations.items()
            },
            'total_conversations': self.total_conversations,
            'successful_conversations': self.successful_conversations,
            'total_messages': self.total_messages,
            'total_token_usage': self.total_token_usage.to_dict(),
            'total_tool_calls': {
                name: metrics.to_dict() 
                for name, metrics in self.total_tool_calls.items()
            },
            'response_times': list(self.response_times),
            'confidence_scores': list(self.confidence_scores),
            'daily_stats': self.daily_stats,
            'hourly_stats': self.hourly_stats
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMetrics':
        metrics = cls(data['agent_id'])
        metrics.created_at = datetime.fromisoformat(data['created_at'])
        
        # Load conversations
        for conv_id, conv_data in data.get('conversations', {}).items():
            metrics.conversations[conv_id] = ConversationMetrics.from_dict(conv_data)
        
        for conv_id, conv_data in data.get('active_conversations', {}).items():
            metrics.active_conversations[conv_id] = ConversationMetrics.from_dict(conv_data)
        
        # Load aggregated data
        metrics.total_conversations = data.get('total_conversations', 0)
        metrics.successful_conversations = data.get('successful_conversations', 0)
        metrics.total_messages = data.get('total_messages', 0)
        
        if 'total_token_usage' in data:
            metrics.total_token_usage = TokenUsage.from_dict(data['total_token_usage'])
        
        if 'total_tool_calls' in data:
            for name, tool_data in data['total_tool_calls'].items():
                metrics.total_tool_calls[name] = ToolMetrics.from_dict(tool_data)
        
        # Load performance data
        metrics.response_times = deque(data.get('response_times', []), maxlen=1000)
        metrics.confidence_scores = deque(data.get('confidence_scores', []), maxlen=1000)
        
        # Load time-based stats
        metrics.daily_stats = data.get('daily_stats', {})
        metrics.hourly_stats = data.get('hourly_stats', {})
        
        return metrics


class MetricsCollector:
    """Collects and manages metrics for multiple agents"""
    
    def __init__(self, metrics_dir: str = "~/.agno_cli/metrics"):
        self.metrics_dir = Path(metrics_dir).expanduser()
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.system_start_time = datetime.now()
        
        # Configuration
        self.auto_save_interval = 300  # 5 minutes
        self.last_save_time = time.time()
    
    def get_or_create_agent_metrics(self, agent_id: str) -> AgentMetrics:
        """Get or create metrics for an agent"""
        if agent_id not in self.agent_metrics:
            # Try to load existing metrics
            metrics_file = self.metrics_dir / f"{agent_id}_metrics.json"
            if metrics_file.exists():
                try:
                    with open(metrics_file, 'r') as f:
                        data = json.load(f)
                    self.agent_metrics[agent_id] = AgentMetrics.from_dict(data)
                except Exception as e:
                    print(f"Error loading metrics for {agent_id}: {e}")
                    self.agent_metrics[agent_id] = AgentMetrics(agent_id)
            else:
                self.agent_metrics[agent_id] = AgentMetrics(agent_id)
        
        return self.agent_metrics[agent_id]
    
    def start_conversation(self, agent_id: str, conversation_id: str) -> ConversationMetrics:
        """Start tracking a conversation"""
        metrics = self.get_or_create_agent_metrics(agent_id)
        return metrics.start_conversation(conversation_id)
    
    def end_conversation(self, agent_id: str, conversation_id: str, success: bool = True) -> bool:
        """End a conversation"""
        if agent_id not in self.agent_metrics:
            return False
        
        result = self.agent_metrics[agent_id].end_conversation(conversation_id, success)
        self._maybe_auto_save()
        return result
    
    def record_message(self, agent_id: str, conversation_id: str, response_time: float,
                      token_usage: TokenUsage = None, confidence: float = None) -> bool:
        """Record a message in a conversation"""
        if agent_id not in self.agent_metrics:
            return False
        
        return self.agent_metrics[agent_id].add_message(
            conversation_id, response_time, token_usage, confidence
        )
    
    def record_tool_call(self, agent_id: str, conversation_id: str, tool_name: str,
                        success: bool, duration: float) -> bool:
        """Record a tool call"""
        if agent_id not in self.agent_metrics:
            return False
        
        return self.agent_metrics[agent_id].add_tool_call(
            conversation_id, tool_name, success, duration
        )
    
    def get_agent_summary(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get summary for a specific agent"""
        if agent_id not in self.agent_metrics:
            return None
        
        return self.agent_metrics[agent_id].get_summary()
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get system-wide metrics summary"""
        total_conversations = sum(m.total_conversations for m in self.agent_metrics.values())
        total_messages = sum(m.total_messages for m in self.agent_metrics.values())
        
        # Calculate system-wide averages
        all_response_times = []
        all_confidence_scores = []
        total_tokens = TokenUsage()
        
        for metrics in self.agent_metrics.values():
            all_response_times.extend(metrics.response_times)
            all_confidence_scores.extend(metrics.confidence_scores)
            total_tokens.add(metrics.total_token_usage)
        
        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0.0
        avg_confidence = sum(all_confidence_scores) / len(all_confidence_scores) if all_confidence_scores else 0.0
        
        return {
            'system_uptime': (datetime.now() - self.system_start_time).total_seconds(),
            'total_agents': len(self.agent_metrics),
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'system_avg_response_time': avg_response_time,
            'system_avg_confidence': avg_confidence,
            'total_token_usage': total_tokens.to_dict(),
            'agents': {
                agent_id: metrics.get_summary() 
                for agent_id, metrics in self.agent_metrics.items()
            }
        }
    
    def get_leaderboard(self, metric: str = "success_rate", limit: int = 10) -> List[Dict[str, Any]]:
        """Get agent leaderboard by metric"""
        agents = []
        
        for agent_id, metrics in self.agent_metrics.items():
            summary = metrics.get_summary()
            summary['agent_id'] = agent_id
            agents.append(summary)
        
        # Sort by metric
        if metric in ['success_rate', 'average_confidence']:
            agents.sort(key=lambda x: x.get(metric, 0), reverse=True)
        elif metric == 'average_response_time':
            agents.sort(key=lambda x: x.get(metric, float('inf')))
        else:
            agents.sort(key=lambda x: x.get(metric, 0), reverse=True)
        
        return agents[:limit]
    
    def export_metrics(self, agent_id: str = None, format: str = "json") -> str:
        """Export metrics in different formats"""
        if agent_id:
            if agent_id not in self.agent_metrics:
                return ""
            data = self.agent_metrics[agent_id].to_dict()
        else:
            data = self.get_system_summary()
        
        if format == "json":
            return json.dumps(data, indent=2)
        elif format == "csv":
            # Simple CSV export for summary data
            if agent_id:
                summary = self.agent_metrics[agent_id].get_summary()
            else:
                summary = data
            
            lines = ["metric,value"]
            for key, value in summary.items():
                if isinstance(value, (int, float, str)):
                    lines.append(f"{key},{value}")
            
            return "\n".join(lines)
        
        return ""
    
    def save_metrics(self, agent_id: str = None) -> bool:
        """Save metrics to disk"""
        try:
            if agent_id:
                if agent_id in self.agent_metrics:
                    metrics_file = self.metrics_dir / f"{agent_id}_metrics.json"
                    with open(metrics_file, 'w') as f:
                        json.dump(self.agent_metrics[agent_id].to_dict(), f, indent=2)
            else:
                # Save all agent metrics
                for aid, metrics in self.agent_metrics.items():
                    metrics_file = self.metrics_dir / f"{aid}_metrics.json"
                    with open(metrics_file, 'w') as f:
                        json.dump(metrics.to_dict(), f, indent=2)
                
                # Save system summary
                system_file = self.metrics_dir / "system_summary.json"
                with open(system_file, 'w') as f:
                    json.dump(self.get_system_summary(), f, indent=2)
            
            self.last_save_time = time.time()
            return True
            
        except Exception as e:
            print(f"Error saving metrics: {e}")
            return False
    
    def _maybe_auto_save(self) -> None:
        """Auto-save metrics if interval has passed"""
        if time.time() - self.last_save_time > self.auto_save_interval:
            self.save_metrics()
    
    def clear_metrics(self, agent_id: str = None, older_than_days: int = 30) -> int:
        """Clear old metrics"""
        cleared_count = 0
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        if agent_id:
            if agent_id in self.agent_metrics:
                metrics = self.agent_metrics[agent_id]
                # Clear old conversations
                old_conversations = [
                    conv_id for conv_id, conv in metrics.conversations.items()
                    if conv.started_at < cutoff_date
                ]
                for conv_id in old_conversations:
                    del metrics.conversations[conv_id]
                    cleared_count += 1
        else:
            # Clear for all agents
            for metrics in self.agent_metrics.values():
                old_conversations = [
                    conv_id for conv_id, conv in metrics.conversations.items()
                    if conv.started_at < cutoff_date
                ]
                for conv_id in old_conversations:
                    del metrics.conversations[conv_id]
                    cleared_count += 1
        
        return cleared_count

