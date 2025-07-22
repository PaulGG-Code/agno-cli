"""
Models Tools - Model Management and Selection

This module provides comprehensive model management capabilities with:
- Model selection and comparison
- Configuration management
- Performance tracking and metrics
- Model registry and versioning
- Cost analysis and optimization
- Model evaluation and benchmarking
- Rich output formatting
- Multiple model providers and types
- Advanced model management algorithms
"""

import os
import sys
import json
import time
import hashlib
import sqlite3
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
import requests


class ModelType(Enum):
    """Model types enumeration"""
    TEXT_GENERATION = "text_generation"
    TEXT_EMBEDDING = "text_embedding"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    AUDIO_GENERATION = "audio_generation"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    CODE_GENERATION = "code_generation"
    MULTIMODAL = "multimodal"


class ModelProvider(Enum):
    """Model providers enumeration"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    META = "meta"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"
    LOCAL = "local"
    CUSTOM = "custom"


@dataclass
class ModelConfig:
    """Model configuration"""
    name: str
    provider: str
    model_type: str
    version: str
    description: str
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60
    retry_attempts: int = 3
    cost_per_1k_tokens: Optional[float] = None
    cost_per_1k_input: Optional[float] = None
    cost_per_1k_output: Optional[float] = None
    context_length: Optional[int] = None
    parameters: Optional[int] = None
    capabilities: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_name: str
    provider: str
    test_date: str
    latency_ms: float
    throughput_tokens_per_sec: float
    accuracy_score: Optional[float] = None
    cost_per_request: Optional[float] = None
    success_rate: float = 1.0
    error_rate: float = 0.0
    total_requests: int = 1
    total_tokens: int = 0
    total_cost: float = 0.0
    test_duration_sec: float = 0.0
    test_scenario: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ModelComparison:
    """Model comparison result"""
    models: List[str]
    comparison_date: str
    metrics: Dict[str, Dict[str, Any]]
    recommendations: List[str]
    cost_analysis: Dict[str, float]
    performance_analysis: Dict[str, Dict[str, float]]
    winner: Optional[str] = None


@dataclass
class ModelRegistry:
    """Model registry entry"""
    name: str
    provider: str
    model_type: str
    version: str
    status: str  # active, deprecated, experimental
    config: ModelConfig
    performance_history: List[ModelPerformance]
    created_at: str
    updated_at: str
    usage_count: int = 0
    last_used: Optional[str] = None


class ModelsTools:
    """Core model management tools"""
    
    def __init__(self):
        self.console = Console()
        self.db_path = Path("models_database.db")
        self.config_dir = Path("models_config")
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Load default models
        self._load_default_models()
        
        # Model selection strategies
        self.selection_strategies = {
            'fastest': self._select_fastest,
            'cheapest': self._select_cheapest,
            'most_accurate': self._select_most_accurate,
            'balanced': self._select_balanced,
            'highest_throughput': self._select_highest_throughput,
            'lowest_latency': self._select_lowest_latency
        }
    
    def _init_database(self):
        """Initialize SQLite database for model management"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create models table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    provider TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    version TEXT NOT NULL,
                    description TEXT,
                    config_json TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    usage_count INTEGER DEFAULT 0,
                    last_used TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Create performance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    test_date TEXT NOT NULL,
                    latency_ms REAL,
                    throughput_tokens_per_sec REAL,
                    accuracy_score REAL,
                    cost_per_request REAL,
                    success_rate REAL,
                    error_rate REAL,
                    total_requests INTEGER,
                    total_tokens INTEGER,
                    total_cost REAL,
                    test_duration_sec REAL,
                    test_scenario TEXT,
                    notes TEXT,
                    FOREIGN KEY (model_name) REFERENCES models (name)
                )
            ''')
            
            # Create comparisons table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    comparison_date TEXT NOT NULL,
                    models_json TEXT NOT NULL,
                    metrics_json TEXT NOT NULL,
                    winner TEXT,
                    recommendations_json TEXT NOT NULL,
                    cost_analysis_json TEXT NOT NULL,
                    performance_analysis_json TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.console.print(f"[red]Error initializing database: {e}[/red]")
    
    def _load_default_models(self):
        """Load default model configurations"""
        default_models = [
            ModelConfig(
                name="gpt-4o",
                provider="openai",
                model_type="text_generation",
                version="latest",
                description="OpenAI's most advanced multimodal model",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_input=0.005,
                cost_per_1k_output=0.015,
                context_length=128000,
                parameters=175000000000,
                capabilities=["text_generation", "code_generation", "multimodal"],
                tags=["advanced", "multimodal", "latest"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            ModelConfig(
                name="gpt-4o-mini",
                provider="openai",
                model_type="text_generation",
                version="latest",
                description="OpenAI's efficient multimodal model",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_input=0.00015,
                cost_per_1k_output=0.0006,
                context_length=128000,
                parameters=35000000000,
                capabilities=["text_generation", "code_generation", "multimodal"],
                tags=["efficient", "multimodal", "cost_effective"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            ModelConfig(
                name="claude-3-5-sonnet",
                provider="anthropic",
                model_type="text_generation",
                version="latest",
                description="Anthropic's most capable Claude model",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                context_length=200000,
                parameters=200000000000,
                capabilities=["text_generation", "code_generation", "analysis"],
                tags=["advanced", "analysis", "reasoning"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            ModelConfig(
                name="claude-3-haiku",
                provider="anthropic",
                model_type="text_generation",
                version="latest",
                description="Anthropic's fastest Claude model",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_input=0.00025,
                cost_per_1k_output=0.00125,
                context_length=200000,
                parameters=80000000000,
                capabilities=["text_generation", "code_generation"],
                tags=["fast", "efficient", "cost_effective"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            ModelConfig(
                name="gemini-1.5-pro",
                provider="google",
                model_type="multimodal",
                version="latest",
                description="Google's advanced multimodal model",
                max_tokens=8192,
                temperature=0.7,
                cost_per_1k_input=0.00375,
                cost_per_1k_output=0.015,
                context_length=1000000,
                parameters=175000000000,
                capabilities=["text_generation", "multimodal", "analysis"],
                tags=["advanced", "multimodal", "long_context"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        ]
        
        for model_config in default_models:
            self.register_model(model_config)
    
    def register_model(self, config: ModelConfig) -> bool:
        """Register a new model"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if model already exists
            cursor.execute("SELECT name FROM models WHERE name = ?", (config.name,))
            if cursor.fetchone():
                # Update existing model
                cursor.execute('''
                    UPDATE models SET
                        provider = ?, model_type = ?, version = ?, description = ?,
                        config_json = ?, updated_at = ?
                    WHERE name = ?
                ''', (
                    config.provider, config.model_type, config.version, config.description,
                    json.dumps(asdict(config)), datetime.now().isoformat(), config.name
                ))
            else:
                # Insert new model
                cursor.execute('''
                    INSERT INTO models (name, provider, model_type, version, description,
                                      config_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    config.name, config.provider, config.model_type, config.version,
                    config.description, json.dumps(asdict(config)),
                    datetime.now().isoformat(), datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error registering model: {e}[/red]")
            return False
    
    def get_model(self, name: str) -> Optional[ModelConfig]:
        """Get model configuration by name"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT config_json FROM models WHERE name = ?", (name,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                config_dict = json.loads(result[0])
                return ModelConfig(**config_dict)
            
            return None
            
        except Exception as e:
            self.console.print(f"[red]Error getting model: {e}[/red]")
            return None
    
    def list_models(self, provider: Optional[str] = None, model_type: Optional[str] = None,
                   status: Optional[str] = None) -> List[ModelConfig]:
        """List models with optional filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT config_json FROM models WHERE 1=1"
            params = []
            
            if provider:
                query += " AND provider = ?"
                params.append(provider)
            
            if model_type:
                query += " AND model_type = ?"
                params.append(model_type)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            conn.close()
            
            models = []
            for result in results:
                config_dict = json.loads(result[0])
                models.append(ModelConfig(**config_dict))
            
            return models
            
        except Exception as e:
            self.console.print(f"[red]Error listing models: {e}[/red]")
            return []
    
    def update_model(self, name: str, updates: Dict[str, Any]) -> bool:
        """Update model configuration"""
        try:
            model = self.get_model(name)
            if not model:
                return False
            
            # Update fields
            for key, value in updates.items():
                if hasattr(model, key):
                    setattr(model, key, value)
            
            model.updated_at = datetime.now().isoformat()
            
            # Re-register the updated model
            return self.register_model(model)
            
        except Exception as e:
            self.console.print(f"[red]Error updating model: {e}[/red]")
            return False
    
    def delete_model(self, name: str) -> bool:
        """Delete a model"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM models WHERE name = ?", (name,))
            cursor.execute("DELETE FROM performance WHERE model_name = ?", (name,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error deleting model: {e}[/red]")
            return False
    
    def record_performance(self, performance: ModelPerformance) -> bool:
        """Record model performance metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance (
                    model_name, provider, test_date, latency_ms, throughput_tokens_per_sec,
                    accuracy_score, cost_per_request, success_rate, error_rate,
                    total_requests, total_tokens, total_cost, test_duration_sec,
                    test_scenario, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                performance.model_name, performance.provider, performance.test_date,
                performance.latency_ms, performance.throughput_tokens_per_sec,
                performance.accuracy_score, performance.cost_per_request,
                performance.success_rate, performance.error_rate,
                performance.total_requests, performance.total_tokens,
                performance.total_cost, performance.test_duration_sec,
                performance.test_scenario, performance.notes
            ))
            
            # Update model usage count
            cursor.execute('''
                UPDATE models SET usage_count = usage_count + 1, last_used = ?
                WHERE name = ?
            ''', (datetime.now().isoformat(), performance.model_name))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error recording performance: {e}[/red]")
            return False
    
    def get_performance_history(self, model_name: str, days: int = 30) -> List[ModelPerformance]:
        """Get performance history for a model"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT model_name, provider, test_date, latency_ms, throughput_tokens_per_sec,
                       accuracy_score, cost_per_request, success_rate, error_rate,
                       total_requests, total_tokens, total_cost, test_duration_sec,
                       test_scenario, notes
                FROM performance
                WHERE model_name = ? AND test_date >= ?
                ORDER BY test_date DESC
            ''', (model_name, cutoff_date))
            
            results = cursor.fetchall()
            conn.close()
            
            performances = []
            for result in results:
                performances.append(ModelPerformance(
                    model_name=result[0], provider=result[1], test_date=result[2],
                    latency_ms=result[3], throughput_tokens_per_sec=result[4],
                    accuracy_score=result[5], cost_per_request=result[6],
                    success_rate=result[7], error_rate=result[8],
                    total_requests=result[9], total_tokens=result[10],
                    total_cost=result[11], test_duration_sec=result[12],
                    test_scenario=result[13], notes=result[14]
                ))
            
            return performances
            
        except Exception as e:
            self.console.print(f"[red]Error getting performance history: {e}[/red]")
            return []
    
    def compare_models(self, model_names: List[str], test_scenario: str = "general") -> ModelComparison:
        """Compare multiple models"""
        try:
            # Get recent performance data for all models
            all_performances = {}
            for model_name in model_names:
                performances = self.get_performance_history(model_name, days=7)
                if performances:
                    # Use the most recent performance
                    all_performances[model_name] = performances[0]
            
            if not all_performances:
                raise ValueError("No performance data available for comparison")
            
            # Calculate metrics
            metrics = {}
            cost_analysis = {}
            performance_analysis = {}
            
            for model_name, perf in all_performances.items():
                metrics[model_name] = {
                    'latency_ms': perf.latency_ms,
                    'throughput_tokens_per_sec': perf.throughput_tokens_per_sec,
                    'accuracy_score': perf.accuracy_score,
                    'cost_per_request': perf.cost_per_request,
                    'success_rate': perf.success_rate,
                    'error_rate': perf.error_rate
                }
                
                cost_analysis[model_name] = perf.cost_per_request or 0.0
                performance_analysis[model_name] = {
                    'latency': perf.latency_ms,
                    'throughput': perf.throughput_tokens_per_sec,
                    'accuracy': perf.accuracy_score or 0.0
                }
            
            # Determine winner based on balanced scoring
            winner = self._select_balanced(all_performances.keys())
            
            # Generate recommendations
            recommendations = self._generate_recommendations(all_performances, test_scenario)
            
            comparison = ModelComparison(
                models=model_names,
                comparison_date=datetime.now().isoformat(),
                metrics=metrics,
                winner=winner,
                recommendations=recommendations,
                cost_analysis=cost_analysis,
                performance_analysis=performance_analysis
            )
            
            # Save comparison
            self._save_comparison(comparison)
            
            return comparison
            
        except Exception as e:
            self.console.print(f"[red]Error comparing models: {e}[/red]")
            return None
    
    def _save_comparison(self, comparison: ModelComparison):
        """Save comparison to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO comparisons (
                    comparison_date, models_json, metrics_json, winner,
                    recommendations_json, cost_analysis_json, performance_analysis_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                comparison.comparison_date,
                json.dumps(comparison.models),
                json.dumps(comparison.metrics),
                comparison.winner,
                json.dumps(comparison.recommendations),
                json.dumps(comparison.cost_analysis),
                json.dumps(comparison.performance_analysis)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.console.print(f"[red]Error saving comparison: {e}[/red]")
    
    def select_model(self, strategy: str, model_type: str, 
                    requirements: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Select best model based on strategy"""
        try:
            # Get available models of the specified type
            models = self.list_models(model_type=model_type, status="active")
            
            if not models:
                return None
            
            # Get performance data for all models
            model_performances = {}
            for model in models:
                performances = self.get_performance_history(model.name, days=30)
                if performances:
                    # Use average performance over the period
                    avg_perf = self._calculate_average_performance(performances)
                    model_performances[model.name] = avg_perf
            
            if not model_performances:
                return None
            
            # Apply selection strategy
            if strategy in self.selection_strategies:
                return self.selection_strategies[strategy](model_performances.keys())
            else:
                return self._select_balanced(model_performances.keys())
                
        except Exception as e:
            self.console.print(f"[red]Error selecting model: {e}[/red]")
            return None
    
    def _calculate_average_performance(self, performances: List[ModelPerformance]) -> ModelPerformance:
        """Calculate average performance from multiple measurements"""
        if not performances:
            return None
        
        avg_perf = ModelPerformance(
            model_name=performances[0].model_name,
            provider=performances[0].provider,
            test_date=datetime.now().isoformat(),
            latency_ms=sum(p.latency_ms for p in performances) / len(performances),
            throughput_tokens_per_sec=sum(p.throughput_tokens_per_sec for p in performances) / len(performances),
            accuracy_score=sum(p.accuracy_score or 0 for p in performances) / len(performances) if any(p.accuracy_score for p in performances) else None,
            cost_per_request=sum(p.cost_per_request or 0 for p in performances) / len(performances) if any(p.cost_per_request for p in performances) else None,
            success_rate=sum(p.success_rate for p in performances) / len(performances),
            error_rate=sum(p.error_rate for p in performances) / len(performances),
            total_requests=sum(p.total_requests for p in performances),
            total_tokens=sum(p.total_tokens for p in performances),
            total_cost=sum(p.total_cost for p in performances),
            test_duration_sec=sum(p.test_duration_sec for p in performances)
        )
        
        return avg_perf
    
    def _select_fastest(self, model_names: List[str]) -> str:
        """Select fastest model"""
        fastest = None
        min_latency = float('inf')
        
        for model_name in model_names:
            performances = self.get_performance_history(model_name, days=7)
            if performances:
                avg_latency = sum(p.latency_ms for p in performances) / len(performances)
                if avg_latency < min_latency:
                    min_latency = avg_latency
                    fastest = model_name
        
        return fastest
    
    def _select_cheapest(self, model_names: List[str]) -> str:
        """Select cheapest model"""
        cheapest = None
        min_cost = float('inf')
        
        for model_name in model_names:
            performances = self.get_performance_history(model_name, days=7)
            if performances:
                avg_cost = sum(p.cost_per_request or 0 for p in performances) / len(performances)
                if avg_cost < min_cost:
                    min_cost = avg_cost
                    cheapest = model_name
        
        return cheapest
    
    def _select_most_accurate(self, model_names: List[str]) -> str:
        """Select most accurate model"""
        most_accurate = None
        max_accuracy = -1
        
        for model_name in model_names:
            performances = self.get_performance_history(model_name, days=7)
            if performances:
                avg_accuracy = sum(p.accuracy_score or 0 for p in performances) / len(performances)
                if avg_accuracy > max_accuracy:
                    max_accuracy = avg_accuracy
                    most_accurate = model_name
        
        return most_accurate
    
    def _select_balanced(self, model_names: List[str]) -> str:
        """Select balanced model (good performance, reasonable cost)"""
        best_score = -1
        best_model = None
        
        for model_name in model_names:
            performances = self.get_performance_history(model_name, days=7)
            if performances:
                avg_perf = self._calculate_average_performance(performances)
                
                # Calculate balanced score (normalized)
                latency_score = 1.0 / (avg_perf.latency_ms / 1000)  # Convert to seconds
                cost_score = 1.0 / (avg_perf.cost_per_request or 0.01)  # Avoid division by zero
                accuracy_score = avg_perf.accuracy_score or 0.5
                
                # Weighted combination
                balanced_score = (0.4 * latency_score + 0.3 * cost_score + 0.3 * accuracy_score)
                
                if balanced_score > best_score:
                    best_score = balanced_score
                    best_model = model_name
        
        return best_model
    
    def _select_highest_throughput(self, model_names: List[str]) -> str:
        """Select model with highest throughput"""
        highest_throughput = None
        max_throughput = -1
        
        for model_name in model_names:
            performances = self.get_performance_history(model_name, days=7)
            if performances:
                avg_throughput = sum(p.throughput_tokens_per_sec for p in performances) / len(performances)
                if avg_throughput > max_throughput:
                    max_throughput = avg_throughput
                    highest_throughput = model_name
        
        return highest_throughput
    
    def _select_lowest_latency(self, model_names: List[str]) -> str:
        """Select model with lowest latency"""
        return self._select_fastest(model_names)
    
    def _generate_recommendations(self, performances: Dict[str, ModelPerformance], 
                                scenario: str) -> List[str]:
        """Generate recommendations based on performance data"""
        recommendations = []
        
        # Find best performers in different categories
        fastest = min(performances.keys(), key=lambda x: performances[x].latency_ms)
        cheapest = min(performances.keys(), key=lambda x: performances[x].cost_per_request or float('inf'))
        most_accurate = max(performances.keys(), key=lambda x: performances[x].accuracy_score or 0)
        
        recommendations.append(f"Fastest model: {fastest} ({performances[fastest].latency_ms:.1f}ms)")
        recommendations.append(f"Most cost-effective: {cheapest} (${performances[cheapest].cost_per_request:.4f}/request)")
        
        if any(p.accuracy_score for p in performances.values()):
            recommendations.append(f"Most accurate: {most_accurate} ({performances[most_accurate].accuracy_score:.2f})")
        
        # Scenario-specific recommendations
        if scenario == "production":
            recommendations.append("For production: Consider reliability and cost over speed")
        elif scenario == "development":
            recommendations.append("For development: Consider speed and cost-effectiveness")
        elif scenario == "research":
            recommendations.append("For research: Consider accuracy and capabilities")
        
        return recommendations
    
    def export_config(self, model_name: str, format: str = "json") -> str:
        """Export model configuration"""
        try:
            model = self.get_model(model_name)
            if not model:
                return None
            
            if format == "yaml":
                return yaml.dump(asdict(model), default_flow_style=False)
            else:
                return json.dumps(asdict(model), indent=2)
                
        except Exception as e:
            self.console.print(f"[red]Error exporting config: {e}[/red]")
            return None
    
    def import_config(self, config_data: str, format: str = "json") -> bool:
        """Import model configuration"""
        try:
            if format == "yaml":
                config_dict = yaml.safe_load(config_data)
            else:
                config_dict = json.loads(config_data)
            
            config = ModelConfig(**config_dict)
            return self.register_model(config)
            
        except Exception as e:
            self.console.print(f"[red]Error importing config: {e}[/red]")
            return False
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get overall model statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total models
            cursor.execute("SELECT COUNT(*) FROM models")
            total_models = cursor.fetchone()[0]
            
            # Models by provider
            cursor.execute("SELECT provider, COUNT(*) FROM models GROUP BY provider")
            models_by_provider = dict(cursor.fetchall())
            
            # Models by type
            cursor.execute("SELECT model_type, COUNT(*) FROM models GROUP BY model_type")
            models_by_type = dict(cursor.fetchall())
            
            # Total performance records
            cursor.execute("SELECT COUNT(*) FROM performance")
            total_performance_records = cursor.fetchone()[0]
            
            # Recent activity (last 7 days)
            cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute("SELECT COUNT(*) FROM performance WHERE test_date >= ?", (cutoff_date,))
            recent_activity = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_models': total_models,
                'models_by_provider': models_by_provider,
                'models_by_type': models_by_type,
                'total_performance_records': total_performance_records,
                'recent_activity': recent_activity
            }
            
        except Exception as e:
            self.console.print(f"[red]Error getting stats: {e}[/red]")
            return {}


class ModelsToolsManager:
    """CLI integration for models tools"""
    
    def __init__(self):
        self.models_tools = ModelsTools()
        self.console = Console()
    
    def list_models(self, provider: Optional[str] = None, model_type: Optional[str] = None,
                   status: Optional[str] = None, format: str = "table") -> None:
        """List models with optional filtering"""
        try:
            models = self.models_tools.list_models(provider, model_type, status)
            
            if format == "json":
                import json
                self.console.print(json.dumps([asdict(model) for model in models], indent=2))
            else:
                # Show models table
                models_table = Table(title="Registered Models")
                models_table.add_column("Name", style="cyan")
                models_table.add_column("Provider", style="blue")
                models_table.add_column("Type", style="green")
                models_table.add_column("Version", style="yellow")
                models_table.add_column("Description", style="white")
                models_table.add_column("Cost/1K Input", style="red")
                models_table.add_column("Cost/1K Output", style="red")
                
                for model in models:
                    models_table.add_row(
                        model.name,
                        model.provider,
                        model.model_type,
                        model.version,
                        model.description[:50] + "..." if len(model.description) > 50 else model.description,
                        f"${model.cost_per_1k_input:.4f}" if model.cost_per_1k_input else "N/A",
                        f"${model.cost_per_1k_output:.4f}" if model.cost_per_1k_output else "N/A"
                    )
                
                self.console.print(models_table)
                
        except Exception as e:
            self.console.print(f"[red]Error listing models: {e}[/red]")
    
    def show_model(self, name: str, format: str = "table") -> None:
        """Show detailed model information"""
        try:
            model = self.models_tools.get_model(name)
            if not model:
                self.console.print(f"[red]Model not found: {name}[/red]")
                return
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(model), indent=2))
            else:
                # Show model details
                details_table = Table(title=f"Model Details: {name}")
                details_table.add_column("Property", style="cyan")
                details_table.add_column("Value", style="white")
                
                details_table.add_row("Name", model.name)
                details_table.add_row("Provider", model.provider)
                details_table.add_row("Type", model.model_type)
                details_table.add_row("Version", model.version)
                details_table.add_row("Description", model.description)
                details_table.add_row("Max Tokens", str(model.max_tokens) if model.max_tokens else "N/A")
                details_table.add_row("Temperature", str(model.temperature))
                details_table.add_row("Context Length", str(model.context_length) if model.context_length else "N/A")
                details_table.add_row("Parameters", f"{model.parameters:,}" if model.parameters else "N/A")
                details_table.add_row("Cost/1K Input", f"${model.cost_per_1k_input:.4f}" if model.cost_per_1k_input else "N/A")
                details_table.add_row("Cost/1K Output", f"${model.cost_per_1k_output:.4f}" if model.cost_per_1k_output else "N/A")
                
                if model.capabilities:
                    details_table.add_row("Capabilities", ", ".join(model.capabilities))
                
                if model.tags:
                    details_table.add_row("Tags", ", ".join(model.tags))
                
                self.console.print(details_table)
                
        except Exception as e:
            self.console.print(f"[red]Error showing model: {e}[/red]")
    
    def compare_models(self, model_names: List[str], format: str = "table") -> None:
        """Compare multiple models"""
        try:
            comparison = self.models_tools.compare_models(model_names)
            if not comparison:
                self.console.print("[red]No comparison data available[/red]")
                return
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(comparison), indent=2))
            else:
                # Show comparison results
                comparison_table = Table(title="Model Comparison")
                comparison_table.add_column("Metric", style="cyan")
                for model_name in comparison.models:
                    comparison_table.add_column(model_name, style="white")
                
                # Add metrics
                for metric in ['latency_ms', 'throughput_tokens_per_sec', 'accuracy_score', 'cost_per_request']:
                    row = [metric.replace('_', ' ').title()]
                    for model_name in comparison.models:
                        value = comparison.metrics[model_name].get(metric, 'N/A')
                        if isinstance(value, float):
                            if metric == 'latency_ms':
                                row.append(f"{value:.1f}ms")
                            elif metric == 'cost_per_request':
                                row.append(f"${value:.4f}")
                            elif metric == 'accuracy_score':
                                row.append(f"{value:.2f}")
                            else:
                                row.append(f"{value:.2f}")
                        else:
                            row.append(str(value))
                    comparison_table.add_row(*row)
                
                self.console.print(comparison_table)
                
                # Show winner and recommendations
                if comparison.winner:
                    self.console.print(f"\n[green]Winner: {comparison.winner}[/green]")
                
                if comparison.recommendations:
                    recommendations_panel = Panel(
                        "\n".join(f"• {rec}" for rec in comparison.recommendations),
                        title="Recommendations",
                        border_style="blue"
                    )
                    self.console.print(recommendations_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error comparing models: {e}[/red]")
    
    def select_model(self, strategy: str, model_type: str, format: str = "table") -> None:
        """Select best model based on strategy"""
        try:
            selected_model = self.models_tools.select_model(strategy, model_type)
            
            if not selected_model:
                self.console.print(f"[red]No suitable model found for strategy: {strategy}[/red]")
                return
            
            if format == "json":
                import json
                self.console.print(json.dumps({"selected_model": selected_model, "strategy": strategy}, indent=2))
            else:
                self.console.print(f"[green]Selected model: {selected_model}[/green]")
                self.console.print(f"[blue]Strategy: {strategy}[/blue]")
                
                # Show model details
                model = self.models_tools.get_model(selected_model)
                if model:
                    self.console.print(f"[white]Provider: {model.provider}[/white]")
                    self.console.print(f"[white]Description: {model.description}[/white]")
                
        except Exception as e:
            self.console.print(f"[red]Error selecting model: {e}[/red]")
    
    def show_performance(self, model_name: str, days: int = 30, format: str = "table") -> None:
        """Show model performance history"""
        try:
            performances = self.models_tools.get_performance_history(model_name, days)
            
            if not performances:
                self.console.print(f"[yellow]No performance data available for {model_name}[/yellow]")
                return
            
            if format == "json":
                import json
                self.console.print(json.dumps([asdict(p) for p in performances], indent=2))
            else:
                # Show performance table
                perf_table = Table(title=f"Performance History: {model_name}")
                perf_table.add_column("Date", style="cyan")
                perf_table.add_column("Latency (ms)", style="blue")
                perf_table.add_column("Throughput (tokens/s)", style="green")
                perf_table.add_column("Accuracy", style="yellow")
                perf_table.add_column("Cost/Request", style="red")
                perf_table.add_column("Success Rate", style="white")
                
                for perf in performances[:10]:  # Show last 10 entries
                    perf_table.add_row(
                        perf.test_date[:10],  # Just the date part
                        f"{perf.latency_ms:.1f}",
                        f"{perf.throughput_tokens_per_sec:.1f}",
                        f"{perf.accuracy_score:.2f}" if perf.accuracy_score else "N/A",
                        f"${perf.cost_per_request:.4f}" if perf.cost_per_request else "N/A",
                        f"{perf.success_rate:.1%}"
                    )
                
                self.console.print(perf_table)
                
        except Exception as e:
            self.console.print(f"[red]Error showing performance: {e}[/red]")
    
    def show_stats(self, format: str = "table") -> None:
        """Show model management statistics"""
        try:
            stats = self.models_tools.get_model_stats()
            
            if format == "json":
                import json
                self.console.print(json.dumps(stats, indent=2))
            else:
                # Show stats table
                stats_table = Table(title="Model Management Statistics")
                stats_table.add_column("Metric", style="cyan")
                stats_table.add_column("Value", style="white")
                
                stats_table.add_row("Total Models", str(stats['total_models']))
                stats_table.add_row("Total Performance Records", str(stats['total_performance_records']))
                stats_table.add_row("Recent Activity (7 days)", str(stats['recent_activity']))
                
                # Models by provider
                for provider, count in stats['models_by_provider'].items():
                    stats_table.add_row(f"Models - {provider.title()}", str(count))
                
                # Models by type
                for model_type, count in stats['models_by_type'].items():
                    stats_table.add_row(f"Models - {model_type.replace('_', ' ').title()}", str(count))
                
                self.console.print(stats_table)
                
        except Exception as e:
            self.console.print(f"[red]Error showing stats: {e}[/red]")
    
    def list_strategies(self, format: str = "table") -> None:
        """List available model selection strategies"""
        strategies = {
            'fastest': 'Select the fastest model (lowest latency)',
            'cheapest': 'Select the most cost-effective model',
            'most_accurate': 'Select the most accurate model',
            'balanced': 'Select a balanced model (good performance, reasonable cost)',
            'highest_throughput': 'Select the model with highest throughput',
            'lowest_latency': 'Select the model with lowest latency'
        }
        
        if format == "json":
            import json
            self.console.print(json.dumps(strategies, indent=2))
        else:
            # Show strategies table
            strategies_table = Table(title="Available Selection Strategies")
            strategies_table.add_column("Strategy", style="cyan")
            strategies_table.add_column("Description", style="white")
            
            for strategy, description in strategies.items():
                strategies_table.add_row(strategy, description)
            
            self.console.print(strategies_table)
    
    def export_model(self, model_name: str, output_file: str, format: str = "json") -> None:
        """Export model configuration to file"""
        try:
            config_data = self.models_tools.export_config(model_name, format)
            if not config_data:
                self.console.print(f"[red]Failed to export model: {model_name}[/red]")
                return
            
            with open(output_file, 'w') as f:
                f.write(config_data)
            
            self.console.print(f"[green]Model exported to: {output_file}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error exporting model: {e}[/red]")
    
    def import_model(self, input_file: str, format: str = "json") -> None:
        """Import model configuration from file"""
        try:
            with open(input_file, 'r') as f:
                config_data = f.read()
            
            success = self.models_tools.import_config(config_data, format)
            if success:
                self.console.print(f"[green]Model imported from: {input_file}[/green]")
            else:
                self.console.print(f"[red]Failed to import model from: {input_file}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error importing model: {e}[/red]") 