"""
Agent wrapper for Agno CLI SDK
"""

import asyncio
from typing import Dict, Any, Optional, List, Iterator
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
# from agno.models.groq import Groq  # Optional dependency
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools
# from agno.tools.duckduckgo import DuckDuckGoTools  # Optional dependency

from .config import Config
from .session import SessionManager


class AgentWrapper:
    """Wrapper for Agno Agent with CLI-specific functionality"""
    
    def __init__(self, config: Config, session_manager: SessionManager):
        self.config = config
        self.session_manager = session_manager
        self._agent: Optional[Agent] = None
        self._setup_agent()
    
    def _setup_agent(self) -> None:
        """Setup the Agno agent with current configuration"""
        # Get model
        model = self._get_model()
        
        # Get tools
        tools = self._get_tools()
        
        # Get session ID
        session_id = self.session_manager.get_or_create_current_session()
        
        # Create agent
        self._agent = Agent(
            name=self.config.agent.name,
            role=self.config.agent.role,
            description=self.config.agent.description,
            model=model,
            tools=tools,
            instructions=self.config.agent.instructions,
            show_tool_calls=self.config.agent.show_tool_calls,
            markdown=self.config.agent.markdown,
            session_id=session_id
        )
    
    def _get_model(self):
        """Get the configured model"""
        api_key = self.config.get_api_key()
        if not api_key:
            raise ValueError(f"No API key found for {self.config.model.provider}")
        
        model_config = {
            'id': self.config.model.model_id,
            'api_key': api_key,
            'temperature': self.config.model.temperature,
            'max_tokens': self.config.model.max_tokens
        }
        
        if self.config.model.provider.lower() == 'anthropic':
            return Claude(**model_config)
        elif self.config.model.provider.lower() == 'openai':
            return OpenAIChat(**model_config)
        elif self.config.model.provider.lower() == 'groq':
            try:
                from agno.models.groq import Groq
                return Groq(**model_config)
            except ImportError:
                raise ValueError("Groq provider requires 'groq' package. Install with: pip install groq")
        else:
            raise ValueError(f"Unsupported model provider: {self.config.model.provider}")
    
    def _get_tools(self) -> List:
        """Get available tools"""
        tools = []
        
        # Add reasoning tools by default
        tools.append(ReasoningTools(add_instructions=True))
        
        # Add YFinance tools
        tools.append(YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            company_info=True,
            company_news=True
        ))
        
        # Add DuckDuckGo tools if available
        try:
            from agno.tools.duckduckgo import DuckDuckGoTools
            tools.append(DuckDuckGoTools())
        except ImportError:
            pass  # DuckDuckGo tools not available
        
        return tools
    
    def chat(self, message: str, stream: bool = None) -> str:
        """Send a message to the agent and get response"""
        if not self._agent:
            raise RuntimeError("Agent not initialized")
        
        stream = stream if stream is not None else self.config.cli.stream
        
        try:
            if stream:
                response = ""
                for event in self._agent.stream(message=message):
                    if hasattr(event, 'data') and hasattr(event.data, 'response'):
                        if event.data.response and event.data.response.output:
                            chunk = event.data.response.output
                            response += chunk
                            print(chunk, end="", flush=True)
                print()  # New line after streaming
                return response
            else:
                response = self._agent.run(message=message)
                return response or ""
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return error_msg
        finally:
            # Update session message count
            session_id = self.session_manager.current_session_id
            if session_id:
                self.session_manager.increment_message_count(session_id)
    
    def get_memory(self) -> Dict[str, Any]:
        """Get agent memory"""
        if not self._agent or not self._agent.memory:
            return {}
        
        try:
            session_id = self.session_manager.current_session_id
            if session_id:
                user_memory = self._agent.memory.get_user_memory(user_id="default")
                session_summary = self._agent.memory.get_session_summary(session_id=session_id)
                
                return {
                    'user_memory': user_memory.model_dump() if user_memory else {},
                    'session_summary': session_summary.model_dump() if session_summary else {}
                }
        except Exception as e:
            print(f"Error retrieving memory: {e}")
        
        return {}
    
    def clear_memory(self) -> bool:
        """Clear agent memory"""
        try:
            if self._agent and self._agent.memory:
                session_id = self.session_manager.current_session_id
                if session_id:
                    # Clear session-specific memory
                    self._agent.memory.clear_session_memory(session_id)
                    return True
        except Exception as e:
            print(f"Error clearing memory: {e}")
        
        return False
    
    def switch_session(self, session_id: str) -> bool:
        """Switch to a different session"""
        if self.session_manager.set_current_session(session_id):
            # Reinitialize agent with new session
            self._setup_agent()
            return True
        return False
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        if not self._agent:
            return []
        
        # Get tools from the agent's tools list
        tool_names = []
        if hasattr(self._agent, 'tools') and self._agent.tools:
            for tool in self._agent.tools:
                if hasattr(tool, 'name'):
                    tool_names.append(tool.name)
                elif hasattr(tool, 'tools'):  # Toolkit
                    for sub_tool in tool.tools:
                        if hasattr(sub_tool, 'name'):
                            tool_names.append(sub_tool.name)
        
        return tool_names
    
    def use_tool(self, tool_name: str, **kwargs) -> str:
        """Use a specific tool directly"""
        if not self._agent:
            raise RuntimeError("Agent not initialized")
        
        if tool_name not in self._agent.available_tools:
            return f"Tool '{tool_name}' not found. Available tools: {', '.join(self.get_available_tools())}"
        
        try:
            tool = self._agent.available_tools[tool_name]
            
            # Run tool synchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(tool.acall(**kwargs))
                return str(result)
            finally:
                loop.close()
                
        except Exception as e:
            return f"Error using tool '{tool_name}': {str(e)}"
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        session = self.session_manager.get_current_session()
        if session:
            return session.to_dict()
        return {}
    
    def reload_config(self) -> None:
        """Reload configuration and reinitialize agent"""
        self.config.load()
        self._setup_agent()
    
    @property
    def agent(self) -> Optional[Agent]:
        """Get the underlying Agno agent"""
        return self._agent

