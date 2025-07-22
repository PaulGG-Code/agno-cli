"""
Configuration management for Agno CLI SDK
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ModelConfig:
    """Model configuration"""
    provider: str = "anthropic"
    model_id: str = "claude-sonnet-4-20250514"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class AgentConfig:
    """Agent configuration"""
    name: str = "AgnoAssistant"
    role: str = "AI Assistant"
    description: str = "A helpful AI assistant powered by Agno"
    instructions: list = None
    show_tool_calls: bool = False
    markdown: bool = True
    memory_rounds: int = 10
    message_history: int = 10

    def __post_init__(self):
        if self.instructions is None:
            self.instructions = [
                "Be helpful and informative",
                "Use clear and concise language",
                "Ask for clarification when needed"
            ]


@dataclass
class CLIConfig:
    """CLI configuration"""
    debug: bool = False
    verbose: bool = False
    stream: bool = True
    auto_save: bool = True
    session_dir: str = "~/.agno_cli/sessions"
    config_dir: str = "~/.agno_cli"
    logs_dir: str = "~/.agno_cli/logs"


class Config:
    """Configuration manager for Agno CLI SDK"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path or "~/.agno_cli/config.yaml").expanduser()
        self.config_dir = self.config_path.parent
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize default configurations
        self.model = ModelConfig()
        self.agent = AgentConfig()
        self.cli = CLIConfig()
        
        # Load existing configuration
        self.load()
    
    def load(self) -> None:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = yaml.safe_load(f) or {}
                
                # Update configurations
                if 'model' in data:
                    self.model = ModelConfig(**data['model'])
                if 'agent' in data:
                    self.agent = AgentConfig(**data['agent'])
                if 'cli' in data:
                    self.cli = CLIConfig(**data['cli'])
                    
            except Exception as e:
                print(f"Warning: Failed to load config from {self.config_path}: {e}")
    
    def save(self) -> None:
        """Save configuration to file"""
        try:
            data = {
                'model': asdict(self.model),
                'agent': asdict(self.agent),
                'cli': asdict(self.cli)
            }
            
            with open(self.config_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
                
        except Exception as e:
            print(f"Error: Failed to save config to {self.config_path}: {e}")
    
    def get_api_key(self, provider: str = None) -> Optional[str]:
        """Get API key for the specified provider"""
        provider = provider or self.model.provider
        
        # Check configuration first
        if self.model.api_key:
            return self.model.api_key
        
        # Check environment variables
        env_vars = {
            'anthropic': 'ANTHROPIC_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'groq': 'GROQ_API_KEY'
        }
        
        env_var = env_vars.get(provider.lower())
        if env_var:
            return os.getenv(env_var)
        
        return None
    
    def set_api_key(self, api_key: str, provider: str = None) -> None:
        """Set API key for the specified provider"""
        provider = provider or self.model.provider
        self.model.provider = provider
        self.model.api_key = api_key
        self.save()
    
    def update_model_config(self, **kwargs) -> None:
        """Update model configuration"""
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                setattr(self.model, key, value)
        self.save()
    
    def update_agent_config(self, **kwargs) -> None:
        """Update agent configuration"""
        for key, value in kwargs.items():
            if hasattr(self.agent, key):
                setattr(self.agent, key, value)
        self.save()
    
    def update_cli_config(self, **kwargs) -> None:
        """Update CLI configuration"""
        for key, value in kwargs.items():
            if hasattr(self.cli, key):
                setattr(self.cli, key, value)
        self.save()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'model': asdict(self.model),
            'agent': asdict(self.agent),
            'cli': asdict(self.cli)
        }
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return yaml.dump(self.to_dict(), default_flow_style=False, indent=2)
