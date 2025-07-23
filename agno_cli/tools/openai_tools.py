"""
OpenAI Tools - Direct OpenAI API Integration

This module provides direct access to OpenAI's API capabilities:
- Chat completions with various models
- Text embeddings generation
- Image generation with DALL-E
- Audio transcription and text-to-speech
- Function calling and tools
- Fine-tuning operations
- Model management and usage tracking
- Rich output formatting
- Multiple operation modes
- Advanced API features
"""

import os
import sys
import json
import time
import base64
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.syntax import Syntax
from rich.text import Text
from rich.markdown import Markdown
from rich.tree import Tree
from rich.align import Align
from rich.layout import Layout
import requests

# OpenAI imports
try:
    from openai import OpenAI
    from openai.types.chat import ChatCompletion
    from openai.types.audio import Transcription
    from openai.types.images_response import ImagesResponse
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not available. Install with: pip install openai")


class OpenAIOperation(Enum):
    """OpenAI operations enumeration"""
    CHAT = "chat"
    EMBED = "embed"
    GENERATE_IMAGE = "generate_image"
    EDIT_IMAGE = "edit_image"
    VARIATE_IMAGE = "variate_image"
    TRANSCRIBE = "transcribe"
    TRANSLATE = "translate"
    TEXT_TO_SPEECH = "text_to_speech"
    SPEECH_TO_TEXT = "speech_to_text"
    FUNCTION_CALL = "function_call"
    FINE_TUNE = "fine_tune"
    MODERATE = "moderate"


class OpenAIModel(Enum):
    """OpenAI models enumeration"""
    # Chat models
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    
    # Embedding models
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"
    
    # Image models
    DALL_E_3 = "dall-e-3"
    DALL_E_2 = "dall-e-2"
    
    # Audio models
    WHISPER_1 = "whisper-1"
    TTS_1 = "tts-1"
    TTS_1_HD = "tts-1-hd"


@dataclass
class ChatMessage:
    """Chat message structure"""
    role: str  # system, user, assistant, tool
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


@dataclass
class ChatCompletionRequest:
    """Chat completion request"""
    model: str
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    stream: bool = False
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = None
    response_format: Optional[Dict[str, str]] = None


@dataclass
class ChatCompletionResponse:
    """Chat completion response"""
    id: str
    model: str
    created: int
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    system_fingerprint: Optional[str] = None


@dataclass
class EmbeddingRequest:
    """Embedding request"""
    model: str
    input: Union[str, List[str]]
    encoding_format: str = "float"
    dimensions: Optional[int] = None
    user: Optional[str] = None


@dataclass
class EmbeddingResponse:
    """Embedding response"""
    object: str
    data: List[Dict[str, Any]]
    model: str
    usage: Dict[str, int]


@dataclass
class ImageGenerationRequest:
    """Image generation request"""
    model: str
    prompt: str
    size: str = "1024x1024"
    quality: str = "standard"
    style: str = "vivid"
    n: int = 1
    response_format: str = "url"
    user: Optional[str] = None


@dataclass
class ImageGenerationResponse:
    """Image generation response"""
    created: int
    data: List[Dict[str, Any]]


@dataclass
class AudioTranscriptionRequest:
    """Audio transcription request"""
    model: str
    file: str
    language: Optional[str] = None
    prompt: Optional[str] = None
    response_format: str = "json"
    temperature: float = 0.0
    timestamp_granularities: Optional[List[str]] = None


@dataclass
class AudioTranscriptionResponse:
    """Audio transcription response"""
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None
    segments: Optional[List[Dict[str, Any]]] = None


@dataclass
class FunctionDefinition:
    """Function definition for function calling"""
    name: str
    description: str
    parameters: Dict[str, Any]


@dataclass
class OpenAIOperationResult:
    """OpenAI operation result"""
    operation: str
    model: str
    request_data: Dict[str, Any]
    response_data: Any
    execution_time: float
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    status: str = "success"
    error_message: Optional[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class OpenAITools:
    """Core OpenAI API integration tools"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.console = Console()
        self.operations_dir = Path("openai_operations")
        self.operations_dir.mkdir(exist_ok=True)
        
        # Initialize OpenAI client
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        
        # Operation history
        self.operation_history: List[OpenAIOperationResult] = []
        
        # Model pricing (per 1K tokens)
        self.model_pricing = {
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "text-embedding-3-small": {"input": 0.00002, "output": 0},
            "text-embedding-3-large": {"input": 0.00013, "output": 0},
            "text-embedding-ada-002": {"input": 0.0001, "output": 0}
        }
    
    def chat_completion(self, messages: List[Dict[str, Any]], model: str = "gpt-4o",
                       temperature: float = 0.7, max_tokens: Optional[int] = None,
                       stream: bool = False, tools: Optional[List[Dict[str, Any]]] = None,
                       tool_choice: Optional[str] = None) -> OpenAIOperationResult:
        """Perform chat completion"""
        start_time = time.time()
        
        try:
            # Prepare request
            request_data = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }
            
            if max_tokens:
                request_data["max_tokens"] = max_tokens
            
            if tools:
                request_data["tools"] = tools
                if tool_choice:
                    request_data["tool_choice"] = tool_choice
            
            # Make API call
            if stream:
                response = self.client.chat.completions.create(**request_data)
                # Handle streaming response
                full_content = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_content += chunk.choices[0].delta.content
                
                response_data = {
                    "content": full_content,
                    "model": model,
                    "stream": True
                }
            else:
                response = self.client.chat.completions.create(**request_data)
                response_data = {
                    "content": response.choices[0].message.content,
                    "model": response.model,
                    "usage": response.usage.model_dump() if response.usage else None,
                    "finish_reason": response.choices[0].finish_reason
                }
            
            execution_time = time.time() - start_time
            
            # Calculate cost
            cost = None
            tokens_used = None
            if response_data.get("usage"):
                usage = response_data["usage"]
                tokens_used = usage.get("total_tokens", 0)
                cost = self._calculate_cost(model, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))
            
            result = OpenAIOperationResult(
                operation="chat_completion",
                model=model,
                request_data=request_data,
                response_data=response_data,
                execution_time=execution_time,
                tokens_used=tokens_used,
                cost=cost
            )
            
            self._save_operation(result)
            self.operation_history.append(result)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = OpenAIOperationResult(
                operation="chat_completion",
                model=model,
                request_data=request_data,
                response_data=None,
                execution_time=execution_time,
                status="error",
                error_message=str(e)
            )
            
            self._save_operation(result)
            self.operation_history.append(result)
            
            raise
    
    def generate_embeddings(self, text: Union[str, List[str]], model: str = "text-embedding-3-small",
                           dimensions: Optional[int] = None) -> OpenAIOperationResult:
        """Generate text embeddings"""
        start_time = time.time()
        
        try:
            request_data = {
                "model": model,
                "input": text,
                "encoding_format": "float"
            }
            
            if dimensions:
                request_data["dimensions"] = dimensions
            
            response = self.client.embeddings.create(**request_data)
            
            response_data = {
                "embeddings": [embedding.embedding for embedding in response.data],
                "model": response.model,
                "usage": response.usage.model_dump() if response.usage else None
            }
            
            execution_time = time.time() - start_time
            
            # Calculate cost
            cost = None
            tokens_used = None
            if response_data.get("usage"):
                usage = response_data["usage"]
                tokens_used = usage.get("total_tokens", 0)
                cost = self._calculate_cost(model, tokens_used, 0)
            
            result = OpenAIOperationResult(
                operation="generate_embeddings",
                model=model,
                request_data=request_data,
                response_data=response_data,
                execution_time=execution_time,
                tokens_used=tokens_used,
                cost=cost
            )
            
            self._save_operation(result)
            self.operation_history.append(result)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = OpenAIOperationResult(
                operation="generate_embeddings",
                model=model,
                request_data=request_data,
                response_data=None,
                execution_time=execution_time,
                status="error",
                error_message=str(e)
            )
            
            self._save_operation(result)
            self.operation_history.append(result)
            
            raise
    
    def generate_image(self, prompt: str, model: str = "dall-e-3", size: str = "1024x1024",
                      quality: str = "standard", style: str = "vivid", n: int = 1) -> OpenAIOperationResult:
        """Generate image using DALL-E"""
        start_time = time.time()
        
        try:
            request_data = {
                "model": model,
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "style": style,
                "n": n,
                "response_format": "url"
            }
            
            response = self.client.images.generate(**request_data)
            
            response_data = {
                "images": [image.url for image in response.data],
                "created": response.created,
                "model": model
            }
            
            execution_time = time.time() - start_time
            
            # DALL-E pricing is per image
            cost = n * 0.04 if model == "dall-e-3" else n * 0.02
            
            result = OpenAIOperationResult(
                operation="generate_image",
                model=model,
                request_data=request_data,
                response_data=response_data,
                execution_time=execution_time,
                cost=cost
            )
            
            self._save_operation(result)
            self.operation_history.append(result)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = OpenAIOperationResult(
                operation="generate_image",
                model=model,
                request_data=request_data,
                response_data=None,
                execution_time=execution_time,
                status="error",
                error_message=str(e)
            )
            
            self._save_operation(result)
            self.operation_history.append(result)
            
            raise
    
    def transcribe_audio(self, file_path: str, model: str = "whisper-1",
                        language: Optional[str] = None, prompt: Optional[str] = None) -> OpenAIOperationResult:
        """Transcribe audio file"""
        start_time = time.time()
        
        try:
            with open(file_path, "rb") as audio_file:
                request_data = {
                    "model": model,
                    "file": audio_file,
                    "response_format": "json"
                }
                
                if language:
                    request_data["language"] = language
                if prompt:
                    request_data["prompt"] = prompt
                
                response = self.client.audio.transcriptions.create(**request_data)
                
                response_data = {
                    "text": response.text,
                    "language": getattr(response, 'language', None),
                    "duration": getattr(response, 'duration', None),
                    "segments": getattr(response, 'segments', None)
                }
            
            execution_time = time.time() - start_time
            
            # Whisper pricing is per minute
            file_size = os.path.getsize(file_path)
            duration_minutes = file_size / (16000 * 2 * 60)  # Rough estimate
            cost = duration_minutes * 0.006
            
            result = OpenAIOperationResult(
                operation="transcribe_audio",
                model=model,
                request_data={"file_path": file_path, "language": language, "prompt": prompt},
                response_data=response_data,
                execution_time=execution_time,
                cost=cost
            )
            
            self._save_operation(result)
            self.operation_history.append(result)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = OpenAIOperationResult(
                operation="transcribe_audio",
                model=model,
                request_data={"file_path": file_path, "language": language, "prompt": prompt},
                response_data=None,
                execution_time=execution_time,
                status="error",
                error_message=str(e)
            )
            
            self._save_operation(result)
            self.operation_history.append(result)
            
            raise
    
    def text_to_speech(self, text: str, model: str = "tts-1", voice: str = "alloy",
                      response_format: str = "mp3", speed: float = 1.0) -> OpenAIOperationResult:
        """Convert text to speech"""
        start_time = time.time()
        
        try:
            request_data = {
                "model": model,
                "input": text,
                "voice": voice,
                "response_format": response_format,
                "speed": speed
            }
            
            response = self.client.audio.speech.create(**request_data)
            
            # Save audio file
            output_file = f"speech_{int(time.time())}.{response_format}"
            response.stream_to_file(output_file)
            
            response_data = {
                "output_file": output_file,
                "text": text,
                "voice": voice,
                "format": response_format
            }
            
            execution_time = time.time() - start_time
            
            # TTS pricing is per 1K characters
            characters = len(text)
            cost = (characters / 1000) * 0.015
            
            result = OpenAIOperationResult(
                operation="text_to_speech",
                model=model,
                request_data=request_data,
                response_data=response_data,
                execution_time=execution_time,
                cost=cost
            )
            
            self._save_operation(result)
            self.operation_history.append(result)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = OpenAIOperationResult(
                operation="text_to_speech",
                model=model,
                request_data=request_data,
                response_data=None,
                execution_time=execution_time,
                status="error",
                error_message=str(e)
            )
            
            self._save_operation(result)
            self.operation_history.append(result)
            
            raise
    
    def moderate_content(self, text: str) -> OpenAIOperationResult:
        """Moderate content using OpenAI's moderation API"""
        start_time = time.time()
        
        try:
            request_data = {
                "input": text
            }
            
            response = self.client.moderations.create(**request_data)
            
            response_data = {
                "flagged": response.results[0].flagged,
                "categories": response.results[0].categories.model_dump(),
                "category_scores": response.results[0].category_scores.model_dump()
            }
            
            execution_time = time.time() - start_time
            
            result = OpenAIOperationResult(
                operation="moderate_content",
                model="text-moderation-latest",
                request_data=request_data,
                response_data=response_data,
                execution_time=execution_time
            )
            
            self._save_operation(result)
            self.operation_history.append(result)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = OpenAIOperationResult(
                operation="moderate_content",
                model="text-moderation-latest",
                request_data=request_data,
                response_data=None,
                execution_time=execution_time,
                status="error",
                error_message=str(e)
            )
            
            self._save_operation(result)
            self.operation_history.append(result)
            
            raise
    
    def function_call(self, messages: List[Dict[str, Any]], functions: List[Dict[str, Any]],
                     model: str = "gpt-4o") -> OpenAIOperationResult:
        """Perform function calling"""
        start_time = time.time()
        
        try:
            request_data = {
                "model": model,
                "messages": messages,
                "tools": [{"type": "function", "function": func} for func in functions],
                "tool_choice": "auto"
            }
            
            response = self.client.chat.completions.create(**request_data)
            
            response_data = {
                "content": response.choices[0].message.content,
                "tool_calls": response.choices[0].message.tool_calls,
                "model": response.model,
                "usage": response.usage.model_dump() if response.usage else None
            }
            
            execution_time = time.time() - start_time
            
            # Calculate cost
            cost = None
            tokens_used = None
            if response_data.get("usage"):
                usage = response_data["usage"]
                tokens_used = usage.get("total_tokens", 0)
                cost = self._calculate_cost(model, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))
            
            result = OpenAIOperationResult(
                operation="function_call",
                model=model,
                request_data=request_data,
                response_data=response_data,
                execution_time=execution_time,
                tokens_used=tokens_used,
                cost=cost
            )
            
            self._save_operation(result)
            self.operation_history.append(result)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = OpenAIOperationResult(
                operation="function_call",
                model=model,
                request_data=request_data,
                response_data=None,
                execution_time=execution_time,
                status="error",
                error_message=str(e)
            )
            
            self._save_operation(result)
            self.operation_history.append(result)
            
            raise
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage"""
        if model not in self.model_pricing:
            return 0.0
        
        pricing = self.model_pricing[model]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return input_cost + output_cost
    
    def _save_operation(self, result: OpenAIOperationResult) -> bool:
        """Save operation result to file"""
        try:
            operation_file = self.operations_dir / f"operation_{result.operation}_{int(time.time())}.json"
            with open(operation_file, 'w') as f:
                json.dump(asdict(result), f, indent=2, default=str)
            return True
        except Exception as e:
            self.console.print(f"[red]Error saving operation: {e}[/red]")
            return False
    
    def get_operation_history(self, operation_type: Optional[str] = None, limit: int = 50) -> List[OpenAIOperationResult]:
        """Get operation history"""
        history = self.operation_history.copy()
        
        if operation_type:
            history = [op for op in history if op.operation == operation_type]
        
        return sorted(history, key=lambda x: x.created_at, reverse=True)[:limit]
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available OpenAI models"""
        try:
            models = self.client.models.list()
            return [model.model_dump() for model in models.data]
        except Exception as e:
            self.console.print(f"[red]Error listing models: {e}[/red]")
            return []
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get specific model information"""
        try:
            model = self.client.models.retrieve(model_id)
            return model.model_dump()
        except Exception as e:
            self.console.print(f"[red]Error getting model info: {e}[/red]")
            return None


class OpenAIToolsManager:
    """CLI integration for OpenAI tools"""
    
    def __init__(self):
        self.openai_tools = None
        self.console = Console()
        
        # Try to initialize OpenAI tools
        try:
            self.openai_tools = OpenAITools()
        except Exception as e:
            self.console.print(f"[yellow]Warning: OpenAI tools not available: {e}[/yellow]")
    
    def chat(self, message: str, model: str = "gpt-4o", temperature: float = 0.7,
             max_tokens: Optional[int] = None, system_prompt: Optional[str] = None,
             format: str = "table") -> None:
        """Perform chat completion"""
        if not self.openai_tools:
            self.console.print("[red]OpenAI tools not available[/red]")
            return
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": message})
            
            result = self.openai_tools.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(result), indent=2, default=str))
            else:
                # Show chat result
                chat_panel = Panel(
                    f"[bold blue]Model:[/bold blue] {result.model}\n"
                    f"[bold green]Response:[/bold green]\n{result.response_data['content']}\n\n"
                    f"[bold yellow]Tokens:[/bold yellow] {result.tokens_used or 'N/A'}\n"
                    f"[bold cyan]Cost:[/bold cyan] ${result.cost:.6f}" if result.cost else "N/A\n"
                    f"[bold white]Time:[/bold white] {result.execution_time:.3f}s",
                    title="Chat Completion",
                    border_style="green"
                )
                self.console.print(chat_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error in chat completion: {e}[/red]")
    
    def embed(self, text: str, model: str = "text-embedding-3-small",
              dimensions: Optional[int] = None, format: str = "table") -> None:
        """Generate embeddings"""
        if not self.openai_tools:
            self.console.print("[red]OpenAI tools not available[/red]")
            return
        
        try:
            result = self.openai_tools.generate_embeddings(
                text=text,
                model=model,
                dimensions=dimensions
            )
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(result), indent=2, default=str))
            else:
                # Show embedding result
                embedding_panel = Panel(
                    f"[bold blue]Model:[/bold blue] {result.model}\n"
                    f"[bold green]Dimensions:[/bold green] {len(result.response_data['embeddings'][0])}\n"
                    f"[bold yellow]Tokens:[/bold yellow] {result.tokens_used or 'N/A'}\n"
                    f"[bold cyan]Cost:[/bold cyan] ${result.cost:.6f}" if result.cost else "N/A\n"
                    f"[bold white]Time:[/bold white] {result.execution_time:.3f}s",
                    title="Text Embeddings",
                    border_style="blue"
                )
                self.console.print(embedding_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error generating embeddings: {e}[/red]")
    
    def generate_image(self, prompt: str, model: str = "dall-e-3", size: str = "1024x1024",
                      quality: str = "standard", style: str = "vivid", format: str = "table") -> None:
        """Generate image"""
        if not self.openai_tools:
            self.console.print("[red]OpenAI tools not available[/red]")
            return
        
        try:
            result = self.openai_tools.generate_image(
                prompt=prompt,
                model=model,
                size=size,
                quality=quality,
                style=style
            )
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(result), indent=2, default=str))
            else:
                # Show image generation result
                image_panel = Panel(
                    f"[bold blue]Model:[/bold blue] {result.model}\n"
                    f"[bold green]Prompt:[/bold green] {prompt}\n"
                    f"[bold yellow]Size:[/bold yellow] {size}\n"
                    f"[bold cyan]Cost:[/bold cyan] ${result.cost:.2f}\n"
                    f"[bold white]Time:[/bold white] {result.execution_time:.3f}s\n\n"
                    f"[bold magenta]Image URLs:[/bold magenta]\n" + 
                    "\n".join([f"• {url}" for url in result.response_data['images']]),
                    title="Image Generation",
                    border_style="magenta"
                )
                self.console.print(image_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error generating image: {e}[/red]")
    
    def transcribe(self, file_path: str, model: str = "whisper-1",
                  language: Optional[str] = None, prompt: Optional[str] = None,
                  format: str = "table") -> None:
        """Transcribe audio"""
        if not self.openai_tools:
            self.console.print("[red]OpenAI tools not available[/red]")
            return
        
        try:
            result = self.openai_tools.transcribe_audio(
                file_path=file_path,
                model=model,
                language=language,
                prompt=prompt
            )
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(result), indent=2, default=str))
            else:
                # Show transcription result
                transcribe_panel = Panel(
                    f"[bold blue]Model:[/bold blue] {result.model}\n"
                    f"[bold green]File:[/bold green] {file_path}\n"
                    f"[bold yellow]Language:[/bold yellow] {result.response_data.get('language', 'Auto-detected')}\n"
                    f"[bold cyan]Cost:[/bold cyan] ${result.cost:.6f}" if result.cost else "N/A\n"
                    f"[bold white]Time:[/bold white] {result.execution_time:.3f}s\n\n"
                    f"[bold magenta]Transcription:[/bold magenta]\n{result.response_data['text']}",
                    title="Audio Transcription",
                    border_style="yellow"
                )
                self.console.print(transcribe_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error transcribing audio: {e}[/red]")
    
    def text_to_speech(self, text: str, model: str = "tts-1", voice: str = "alloy",
                      response_format: str = "mp3", speed: float = 1.0,
                      format: str = "table") -> None:
        """Convert text to speech"""
        if not self.openai_tools:
            self.console.print("[red]OpenAI tools not available[/red]")
            return
        
        try:
            result = self.openai_tools.text_to_speech(
                text=text,
                model=model,
                voice=voice,
                response_format=response_format,
                speed=speed
            )
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(result), indent=2, default=str))
            else:
                # Show TTS result
                tts_panel = Panel(
                    f"[bold blue]Model:[/bold blue] {result.model}\n"
                    f"[bold green]Voice:[/bold green] {voice}\n"
                    f"[bold yellow]Format:[/bold yellow] {response_format}\n"
                    f"[bold cyan]Cost:[/bold cyan] ${result.cost:.6f}" if result.cost else "N/A\n"
                    f"[bold white]Time:[/bold white] {result.execution_time:.3f}s\n\n"
                    f"[bold magenta]Output File:[/bold magenta] {result.response_data['output_file']}",
                    title="Text to Speech",
                    border_style="cyan"
                )
                self.console.print(tts_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error in text-to-speech: {e}[/red]")
    
    def moderate(self, text: str, format: str = "table") -> None:
        """Moderate content"""
        if not self.openai_tools:
            self.console.print("[red]OpenAI tools not available[/red]")
            return
        
        try:
            result = self.openai_tools.moderate_content(text=text)
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(result), indent=2, default=str))
            else:
                # Show moderation result
                categories = result.response_data['categories']
                flagged_categories = [cat for cat, flagged in categories.items() if flagged]
                
                moderation_panel = Panel(
                    f"[bold blue]Model:[/bold blue] {result.model}\n"
                    f"[bold green]Flagged:[/bold green] {result.response_data['flagged']}\n"
                    f"[bold yellow]Time:[/bold yellow] {result.execution_time:.3f}s\n\n"
                    f"[bold red]Flagged Categories:[/bold red]\n" +
                    ("None" if not flagged_categories else "\n".join([f"• {cat}" for cat in flagged_categories])),
                    title="Content Moderation",
                    border_style="red" if result.response_data['flagged'] else "green"
                )
                self.console.print(moderation_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error in content moderation: {e}[/red]")
    
    def list_models(self, format: str = "table") -> None:
        """List available models"""
        if not self.openai_tools:
            self.console.print("[red]OpenAI tools not available[/red]")
            return
        
        try:
            models = self.openai_tools.list_models()
            
            if format == "json":
                import json
                self.console.print(json.dumps(models, indent=2))
            else:
                if not models:
                    self.console.print("[yellow]No models found[/yellow]")
                    return
                
                models_table = Table(title="Available OpenAI Models")
                models_table.add_column("ID", style="cyan")
                models_table.add_column("Object", style="blue")
                models_table.add_column("Created", style="green")
                models_table.add_column("Owned By", style="yellow")
                
                for model in models:
                    created = datetime.fromtimestamp(model.get('created', 0)).strftime('%Y-%m-%d')
                    models_table.add_row(
                        model.get('id', 'N/A'),
                        model.get('object', 'N/A'),
                        created,
                        model.get('owned_by', 'N/A')
                    )
                
                self.console.print(models_table)
                
        except Exception as e:
            self.console.print(f"[red]Error listing models: {e}[/red]")
    
    def get_history(self, operation_type: Optional[str] = None, limit: int = 20,
                   format: str = "table") -> None:
        """Get operation history"""
        if not self.openai_tools:
            self.console.print("[red]OpenAI tools not available[/red]")
            return
        
        try:
            history = self.openai_tools.get_operation_history(operation_type, limit)
            
            if format == "json":
                import json
                self.console.print(json.dumps([asdict(op) for op in history], indent=2, default=str))
            else:
                if not history:
                    self.console.print("[yellow]No operation history found[/yellow]")
                    return
                
                history_table = Table(title="OpenAI Operation History")
                history_table.add_column("Operation", style="cyan")
                history_table.add_column("Model", style="blue")
                history_table.add_column("Status", style="green")
                history_table.add_column("Tokens", style="yellow")
                history_table.add_column("Cost", style="magenta")
                history_table.add_column("Time", style="red")
                
                for op in history:
                    status_color = "green" if op.status == "success" else "red"
                    history_table.add_row(
                        op.operation,
                        op.model,
                        f"[{status_color}]{op.status}[/{status_color}]",
                        str(op.tokens_used) if op.tokens_used else "N/A",
                        f"${op.cost:.6f}" if op.cost else "N/A",
                        f"{op.execution_time:.3f}s"
                    )
                
                self.console.print(history_table)
                
        except Exception as e:
            self.console.print(f"[red]Error getting history: {e}[/red]") 