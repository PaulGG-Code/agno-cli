"""
Thinking Tools - Advanced Thinking and Reasoning

This module provides sophisticated thinking and reasoning capabilities:
- Multiple thinking frameworks (First Principles, Systems Thinking, etc.)
- Problem decomposition and analysis
- Decision tree generation
- Cognitive bias detection and mitigation
- Structured reasoning workflows
- Thought experiments and scenarios
- Rich output formatting
- Multiple thinking strategies
- Advanced analytical tools
"""

import os
import sys
import json
import time
import random
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


class ThinkingFramework(Enum):
    """Thinking frameworks enumeration"""
    FIRST_PRINCIPLES = "first_principles"
    SYSTEMS_THINKING = "systems_thinking"
    DESIGN_THINKING = "design_thinking"
    LATERAL_THINKING = "lateral_thinking"
    CRITICAL_THINKING = "critical_thinking"
    CREATIVE_THINKING = "creative_thinking"
    ANALYTICAL_THINKING = "analytical_thinking"
    STRATEGIC_THINKING = "strategic_thinking"
    CONVERGENT_THINKING = "convergent_thinking"
    DIVERGENT_THINKING = "divergent_thinking"


class CognitiveBias(Enum):
    """Cognitive biases enumeration"""
    CONFIRMATION_BIAS = "confirmation_bias"
    ANCHORING_BIAS = "anchoring_bias"
    AVAILABILITY_BIAS = "availability_bias"
    DUNNING_KRUGER = "dunning_kruger"
    HINDSIGHT_BIAS = "hindsight_bias"
    OVERCONFIDENCE = "overconfidence"
    GROUPTHINK = "groupthink"
    SURVIVORSHIP_BIAS = "survivorship_bias"
    RECENCY_BIAS = "recency_bias"
    STATUS_QUO_BIAS = "status_quo_bias"


@dataclass
class ThoughtNode:
    """A node in a thinking process"""
    id: str
    title: str
    content: str
    node_type: str  # question, insight, assumption, conclusion, etc.
    parent_id: Optional[str] = None
    children: List[str] = None
    confidence: float = 0.5
    evidence: List[str] = None
    assumptions: List[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.evidence is None:
            self.evidence = []
        if self.assumptions is None:
            self.assumptions = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()


@dataclass
class ThinkingSession:
    """A complete thinking session"""
    id: str
    title: str
    description: str
    framework: str
    problem_statement: str
    nodes: List[ThoughtNode]
    conclusions: List[str]
    insights: List[str]
    next_steps: List[str]
    biases_detected: List[str]
    confidence_score: float
    complexity_score: float
    created_at: str
    updated_at: str
    duration_minutes: float = 0.0


@dataclass
class DecisionTree:
    """A decision tree structure"""
    id: str
    title: str
    root_node: ThoughtNode
    nodes: List[ThoughtNode]
    criteria: List[str]
    outcomes: List[str]
    probabilities: Dict[str, float]
    expected_values: Dict[str, float]
    recommendations: List[str]
    created_at: str


@dataclass
class ProblemAnalysis:
    """Problem analysis result"""
    problem_id: str
    problem_statement: str
    components: List[str]
    root_causes: List[str]
    constraints: List[str]
    stakeholders: List[str]
    success_criteria: List[str]
    complexity_factors: List[str]
    risk_factors: List[str]
    opportunities: List[str]
    analysis_date: str


@dataclass
class ThoughtExperiment:
    """A thought experiment"""
    id: str
    title: str
    scenario: str
    assumptions: List[str]
    variables: List[str]
    outcomes: List[str]
    insights: List[str]
    implications: List[str]
    created_at: str


class ThinkingTools:
    """Core thinking and reasoning tools"""
    
    def __init__(self):
        self.console = Console()
        self.sessions_dir = Path("thinking_sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        
        # Thinking frameworks and their methodologies
        self.frameworks = {
            'first_principles': {
                'name': 'First Principles Thinking',
                'description': 'Break down complex problems into fundamental truths',
                'steps': [
                    'Identify and challenge assumptions',
                    'Break down the problem into fundamental parts',
                    'Reconstruct from the ground up',
                    'Validate each principle independently'
                ]
            },
            'systems_thinking': {
                'name': 'Systems Thinking',
                'description': 'Understand how parts of a system interact',
                'steps': [
                    'Identify system boundaries',
                    'Map system components and relationships',
                    'Identify feedback loops',
                    'Analyze system dynamics',
                    'Consider unintended consequences'
                ]
            },
            'design_thinking': {
                'name': 'Design Thinking',
                'description': 'Human-centered approach to problem solving',
                'steps': [
                    'Empathize with users',
                    'Define the problem',
                    'Ideate solutions',
                    'Prototype concepts',
                    'Test and iterate'
                ]
            },
            'lateral_thinking': {
                'name': 'Lateral Thinking',
                'description': 'Creative approach to problem solving',
                'steps': [
                    'Challenge conventional assumptions',
                    'Generate random associations',
                    'Use analogies and metaphors',
                    'Reverse the problem',
                    'Combine unrelated concepts'
                ]
            },
            'critical_thinking': {
                'name': 'Critical Thinking',
                'description': 'Systematic evaluation of arguments and evidence',
                'steps': [
                    'Identify the claim or argument',
                    'Evaluate evidence and sources',
                    'Assess logical structure',
                    'Consider alternative explanations',
                    'Draw reasoned conclusions'
                ]
            }
        }
        
        # Cognitive biases and mitigation strategies
        self.biases = {
            'confirmation_bias': {
                'name': 'Confirmation Bias',
                'description': 'Seeking information that confirms existing beliefs',
                'mitigation': 'Actively seek disconfirming evidence'
            },
            'anchoring_bias': {
                'name': 'Anchoring Bias',
                'description': 'Over-relying on first piece of information',
                'mitigation': 'Consider multiple reference points'
            },
            'availability_bias': {
                'name': 'Availability Bias',
                'description': 'Overestimating probability based on memorable examples',
                'mitigation': 'Seek statistical data and base rates'
            },
            'dunning_kruger': {
                'name': 'Dunning-Kruger Effect',
                'description': 'Overestimating competence in areas of ignorance',
                'mitigation': 'Seek feedback and acknowledge limitations'
            },
            'overconfidence': {
                'name': 'Overconfidence',
                'description': 'Being more confident than accuracy warrants',
                'mitigation': 'Calibrate confidence with actual performance'
            }
        }
    
    def start_thinking_session(self, title: str, problem_statement: str, 
                              framework: str = "first_principles") -> ThinkingSession:
        """Start a new thinking session"""
        session_id = hashlib.md5(f"{title}_{time.time()}".encode()).hexdigest()[:8]
        
        # Create initial problem analysis node
        root_node = ThoughtNode(
            id="root",
            title="Problem Analysis",
            content=problem_statement,
            node_type="problem",
            confidence=0.8
        )
        
        session = ThinkingSession(
            id=session_id,
            title=title,
            description=f"Thinking session using {framework} framework",
            framework=framework,
            problem_statement=problem_statement,
            nodes=[root_node],
            conclusions=[],
            insights=[],
            next_steps=[],
            biases_detected=[],
            confidence_score=0.5,
            complexity_score=0.5,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        return session
    
    def add_thought_node(self, session: ThinkingSession, title: str, content: str,
                        node_type: str, parent_id: str = "root", 
                        confidence: float = 0.5) -> ThoughtNode:
        """Add a new thought node to the session"""
        node_id = hashlib.md5(f"{title}_{time.time()}".encode()).hexdigest()[:8]
        
        node = ThoughtNode(
            id=node_id,
            title=title,
            content=content,
            node_type=node_type,
            parent_id=parent_id,
            confidence=confidence
        )
        
        # Add to parent's children
        for parent_node in session.nodes:
            if parent_node.id == parent_id:
                parent_node.children.append(node_id)
                break
        
        session.nodes.append(node)
        session.updated_at = datetime.now().isoformat()
        
        return node
    
    def apply_thinking_framework(self, session: ThinkingSession) -> List[ThoughtNode]:
        """Apply the selected thinking framework to the session"""
        framework = self.frameworks.get(session.framework, self.frameworks['first_principles'])
        new_nodes = []
        
        for i, step in enumerate(framework['steps']):
            node = self.add_thought_node(
                session=session,
                title=f"Step {i+1}: {step}",
                content=f"Applying {step.lower()} to the problem",
                node_type="framework_step",
                confidence=0.7
            )
            new_nodes.append(node)
        
        return new_nodes
    
    def detect_cognitive_biases(self, session: ThinkingSession) -> List[str]:
        """Detect potential cognitive biases in the thinking process"""
        detected_biases = []
        
        # Analyze nodes for bias indicators
        for node in session.nodes:
            content_lower = node.content.lower()
            
            # Check for confirmation bias
            if any(word in content_lower for word in ['proves', 'confirms', 'supports my view']):
                detected_biases.append('confirmation_bias')
            
            # Check for overconfidence
            if any(word in content_lower for word in ['certain', 'definitely', 'obviously']):
                detected_biases.append('overconfidence')
            
            # Check for anchoring
            if any(word in content_lower for word in ['first', 'initially', 'originally']):
                detected_biases.append('anchoring_bias')
        
        session.biases_detected = list(set(detected_biases))
        return session.biases_detected
    
    def generate_decision_tree(self, title: str, decision_criteria: List[str],
                             options: List[str]) -> DecisionTree:
        """Generate a decision tree for structured decision making"""
        tree_id = hashlib.md5(f"{title}_{time.time()}".encode()).hexdigest()[:8]
        
        # Create root decision node
        root_node = ThoughtNode(
            id="decision_root",
            title=title,
            content=f"Decision: {title}",
            node_type="decision",
            confidence=0.8
        )
        
        nodes = [root_node]
        probabilities = {}
        expected_values = {}
        
        # Create criteria nodes
        for i, criterion in enumerate(decision_criteria):
            criterion_node = ThoughtNode(
                id=f"criterion_{i}",
                title=f"Criterion: {criterion}",
                content=f"Evaluating {criterion}",
                node_type="criterion",
                parent_id="decision_root",
                confidence=0.6
            )
            nodes.append(criterion_node)
            root_node.children.append(criterion_node.id)
        
        # Create option nodes
        for i, option in enumerate(options):
            option_node = ThoughtNode(
                id=f"option_{i}",
                title=f"Option: {option}",
                content=f"Analyzing {option}",
                node_type="option",
                parent_id="decision_root",
                confidence=0.5
            )
            nodes.append(option_node)
            root_node.children.append(option_node.id)
            
            # Assign random probabilities for demonstration
            probabilities[option] = random.uniform(0.1, 0.9)
            expected_values[option] = random.uniform(0.1, 1.0)
        
        # Generate recommendations
        sorted_options = sorted(expected_values.items(), key=lambda x: x[1], reverse=True)
        recommendations = [f"Consider {option} (expected value: {value:.2f})" 
                          for option, value in sorted_options[:3]]
        
        tree = DecisionTree(
            id=tree_id,
            title=title,
            root_node=root_node,
            nodes=nodes,
            criteria=decision_criteria,
            outcomes=options,
            probabilities=probabilities,
            expected_values=expected_values,
            recommendations=recommendations,
            created_at=datetime.now().isoformat()
        )
        
        return tree
    
    def analyze_problem(self, problem_statement: str) -> ProblemAnalysis:
        """Analyze a problem using structured approach"""
        problem_id = hashlib.md5(problem_statement.encode()).hexdigest()[:8]
        
        # Simple keyword-based analysis (in a real implementation, this would be more sophisticated)
        components = self._extract_components(problem_statement)
        root_causes = self._identify_root_causes(problem_statement)
        constraints = self._identify_constraints(problem_statement)
        stakeholders = self._identify_stakeholders(problem_statement)
        
        analysis = ProblemAnalysis(
            problem_id=problem_id,
            problem_statement=problem_statement,
            components=components,
            root_causes=root_causes,
            constraints=constraints,
            stakeholders=stakeholders,
            success_criteria=self._generate_success_criteria(problem_statement),
            complexity_factors=self._assess_complexity(problem_statement),
            risk_factors=self._identify_risks(problem_statement),
            opportunities=self._identify_opportunities(problem_statement),
            analysis_date=datetime.now().isoformat()
        )
        
        return analysis
    
    def _extract_components(self, problem_statement: str) -> List[str]:
        """Extract problem components"""
        components = []
        words = problem_statement.lower().split()
        
        # Simple keyword extraction
        if 'system' in words:
            components.append('System architecture')
        if 'process' in words:
            components.append('Process flow')
        if 'data' in words:
            components.append('Data management')
        if 'user' in words:
            components.append('User experience')
        if 'performance' in words:
            components.append('Performance optimization')
        
        return components if components else ['Core functionality']
    
    def _identify_root_causes(self, problem_statement: str) -> List[str]:
        """Identify potential root causes"""
        causes = []
        words = problem_statement.lower().split()
        
        if 'slow' in words or 'performance' in words:
            causes.append('Inefficient algorithms or processes')
        if 'error' in words or 'bug' in words:
            causes.append('Insufficient testing or validation')
        if 'user' in words and 'confusion' in words:
            causes.append('Poor user interface design')
        if 'data' in words and 'loss' in words:
            causes.append('Inadequate data backup or security')
        
        return causes if causes else ['Insufficient analysis of requirements']
    
    def _identify_constraints(self, problem_statement: str) -> List[str]:
        """Identify problem constraints"""
        constraints = []
        words = problem_statement.lower().split()
        
        if 'budget' in words or 'cost' in words:
            constraints.append('Budget limitations')
        if 'time' in words or 'deadline' in words:
            constraints.append('Time constraints')
        if 'technical' in words:
            constraints.append('Technical limitations')
        if 'legal' in words or 'compliance' in words:
            constraints.append('Legal or compliance requirements')
        
        return constraints if constraints else ['Resource limitations', 'Time constraints']
    
    def _identify_stakeholders(self, problem_statement: str) -> List[str]:
        """Identify problem stakeholders"""
        stakeholders = []
        words = problem_statement.lower().split()
        
        if 'user' in words or 'customer' in words:
            stakeholders.append('End users')
        if 'business' in words or 'company' in words:
            stakeholders.append('Business stakeholders')
        if 'developer' in words or 'team' in words:
            stakeholders.append('Development team')
        if 'manager' in words or 'lead' in words:
            stakeholders.append('Management')
        
        return stakeholders if stakeholders else ['Primary users', 'Development team']
    
    def _generate_success_criteria(self, problem_statement: str) -> List[str]:
        """Generate success criteria"""
        return [
            'Problem is fully resolved',
            'Solution is implemented successfully',
            'Performance meets requirements',
            'User satisfaction is achieved',
            'Cost and time constraints are met'
        ]
    
    def _assess_complexity(self, problem_statement: str) -> List[str]:
        """Assess problem complexity"""
        complexity_factors = []
        words = problem_statement.lower().split()
        
        if len(words) > 20:
            complexity_factors.append('High problem scope')
        if 'integration' in words or 'multiple' in words:
            complexity_factors.append('Multiple system integration')
        if 'real-time' in words or 'concurrent' in words:
            complexity_factors.append('Real-time processing requirements')
        
        return complexity_factors if complexity_factors else ['Moderate complexity']
    
    def _identify_risks(self, problem_statement: str) -> List[str]:
        """Identify potential risks"""
        return [
            'Technical implementation challenges',
            'Resource constraints',
            'Timeline delays',
            'Scope creep',
            'User adoption issues'
        ]
    
    def _identify_opportunities(self, problem_statement: str) -> List[str]:
        """Identify opportunities"""
        return [
            'Process improvement',
            'Technology modernization',
            'User experience enhancement',
            'Performance optimization',
            'Cost reduction'
        ]
    
    def create_thought_experiment(self, title: str, scenario: str,
                                assumptions: List[str]) -> ThoughtExperiment:
        """Create a thought experiment"""
        experiment_id = hashlib.md5(f"{title}_{time.time()}".encode()).hexdigest()[:8]
        
        # Generate variables based on scenario
        variables = self._extract_variables(scenario)
        outcomes = self._generate_outcomes(scenario)
        insights = self._generate_insights(scenario)
        implications = self._generate_implications(scenario)
        
        experiment = ThoughtExperiment(
            id=experiment_id,
            title=title,
            scenario=scenario,
            assumptions=assumptions,
            variables=variables,
            outcomes=outcomes,
            insights=insights,
            implications=implications,
            created_at=datetime.now().isoformat()
        )
        
        return experiment
    
    def _extract_variables(self, scenario: str) -> List[str]:
        """Extract variables from scenario"""
        variables = []
        words = scenario.lower().split()
        
        if 'time' in words:
            variables.append('Time duration')
        if 'cost' in words:
            variables.append('Cost factors')
        if 'user' in words:
            variables.append('User behavior')
        if 'system' in words:
            variables.append('System performance')
        if 'data' in words:
            variables.append('Data volume')
        
        return variables if variables else ['Key factors', 'Environmental conditions']
    
    def _generate_outcomes(self, scenario: str) -> List[str]:
        """Generate possible outcomes"""
        return [
            'Positive outcome with high probability',
            'Moderate success with some challenges',
            'Mixed results with trade-offs',
            'Challenging outcome requiring adaptation',
            'Unforeseen consequences'
        ]
    
    def _generate_insights(self, scenario: str) -> List[str]:
        """Generate insights from scenario"""
        return [
            'Understanding of key dependencies',
            'Identification of critical success factors',
            'Recognition of potential bottlenecks',
            'Awareness of stakeholder needs',
            'Clarity on resource requirements'
        ]
    
    def _generate_implications(self, scenario: str) -> List[str]:
        """Generate implications from scenario"""
        return [
            'Need for careful planning and preparation',
            'Importance of stakeholder communication',
            'Requirement for iterative development',
            'Necessity of risk mitigation strategies',
            'Value of continuous monitoring and adaptation'
        ]
    
    def save_session(self, session: ThinkingSession) -> bool:
        """Save thinking session to file"""
        try:
            session_file = self.sessions_dir / f"session_{session.id}.json"
            with open(session_file, 'w') as f:
                json.dump(asdict(session), f, indent=2, default=str)
            return True
        except Exception as e:
            self.console.print(f"[red]Error saving session: {e}[/red]")
            return False
    
    def load_session(self, session_id: str) -> Optional[ThinkingSession]:
        """Load thinking session from file"""
        try:
            session_file = self.sessions_dir / f"session_{session_id}.json"
            if not session_file.exists():
                return None
            
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            # Reconstruct session object
            nodes = [ThoughtNode(**node_data) for node_data in data['nodes']]
            
            session = ThinkingSession(
                id=data['id'],
                title=data['title'],
                description=data['description'],
                framework=data['framework'],
                problem_statement=data['problem_statement'],
                nodes=nodes,
                conclusions=data['conclusions'],
                insights=data['insights'],
                next_steps=data['next_steps'],
                biases_detected=data['biases_detected'],
                confidence_score=data['confidence_score'],
                complexity_score=data['complexity_score'],
                created_at=data['created_at'],
                updated_at=data['updated_at'],
                duration_minutes=data.get('duration_minutes', 0.0)
            )
            
            return session
        except Exception as e:
            self.console.print(f"[red]Error loading session: {e}[/red]")
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all saved thinking sessions"""
        sessions = []
        
        for session_file in self.sessions_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                
                sessions.append({
                    'id': data['id'],
                    'title': data['title'],
                    'framework': data['framework'],
                    'created_at': data['created_at'],
                    'confidence_score': data['confidence_score'],
                    'complexity_score': data['complexity_score']
                })
            except Exception:
                continue
        
        return sorted(sessions, key=lambda x: x['created_at'], reverse=True)


class ThinkingToolsManager:
    """CLI integration for thinking tools"""
    
    def __init__(self):
        self.thinking_tools = ThinkingTools()
        self.console = Console()
    
    def start_session(self, title: str, problem: str, framework: str = "first_principles",
                     format: str = "table") -> None:
        """Start a new thinking session"""
        try:
            session = self.thinking_tools.start_thinking_session(title, problem, framework)
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(session), indent=2, default=str))
            else:
                # Show session overview
                session_panel = Panel(
                    f"[bold blue]Session ID:[/bold blue] {session.id}\n"
                    f"[bold green]Title:[/bold green] {session.title}\n"
                    f"[bold yellow]Framework:[/bold yellow] {session.framework}\n"
                    f"[bold white]Problem:[/bold white] {session.problem_statement}\n"
                    f"[bold cyan]Created:[/bold cyan] {session.created_at}",
                    title="New Thinking Session",
                    border_style="green"
                )
                self.console.print(session_panel)
                
                # Show framework steps
                framework_info = self.thinking_tools.frameworks.get(framework, {})
                if framework_info:
                    steps_table = Table(title=f"Framework Steps: {framework_info.get('name', framework)}")
                    steps_table.add_column("Step", style="cyan")
                    steps_table.add_column("Description", style="white")
                    
                    for i, step in enumerate(framework_info.get('steps', []), 1):
                        steps_table.add_row(f"{i}", step)
                    
                    self.console.print(steps_table)
                
                # Save session
                self.thinking_tools.save_session(session)
                self.console.print(f"[green]Session saved with ID: {session.id}[/green]")
                
        except Exception as e:
            self.console.print(f"[red]Error starting session: {e}[/red]")
    
    def add_node(self, session_id: str, title: str, content: str, node_type: str,
                parent_id: str = "root", confidence: float = 0.5, format: str = "table") -> None:
        """Add a thought node to a session"""
        try:
            session = self.thinking_tools.load_session(session_id)
            if not session:
                self.console.print(f"[red]Session not found: {session_id}[/red]")
                return
            
            node = self.thinking_tools.add_thought_node(
                session, title, content, node_type, parent_id, confidence
            )
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(node), indent=2, default=str))
            else:
                node_panel = Panel(
                    f"[bold blue]Node ID:[/bold blue] {node.id}\n"
                    f"[bold green]Title:[/bold green] {node.title}\n"
                    f"[bold yellow]Type:[/bold yellow] {node.node_type}\n"
                    f"[bold white]Content:[/bold white] {node.content}\n"
                    f"[bold cyan]Confidence:[/bold cyan] {node.confidence:.2f}",
                    title="New Thought Node",
                    border_style="blue"
                )
                self.console.print(node_panel)
            
            # Save updated session
            self.thinking_tools.save_session(session)
            
        except Exception as e:
            self.console.print(f"[red]Error adding node: {e}[/red]")
    
    def show_session(self, session_id: str, format: str = "table") -> None:
        """Show detailed session information"""
        try:
            session = self.thinking_tools.load_session(session_id)
            if not session:
                self.console.print(f"[red]Session not found: {session_id}[/red]")
                return
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(session), indent=2, default=str))
            else:
                # Show session overview
                overview_table = Table(title=f"Session: {session.title}")
                overview_table.add_column("Property", style="cyan")
                overview_table.add_column("Value", style="white")
                
                overview_table.add_row("ID", session.id)
                overview_table.add_row("Framework", session.framework)
                overview_table.add_row("Problem", session.problem_statement)
                overview_table.add_row("Confidence Score", f"{session.confidence_score:.2f}")
                overview_table.add_row("Complexity Score", f"{session.complexity_score:.2f}")
                overview_table.add_row("Created", session.created_at)
                overview_table.add_row("Updated", session.updated_at)
                
                self.console.print(overview_table)
                
                # Show nodes tree
                if session.nodes:
                    nodes_tree = Tree(f"[bold green]Thought Nodes ({len(session.nodes)})[/bold green]")
                    node_map = {node.id: node for node in session.nodes}
                    
                    for node in session.nodes:
                        if node.parent_id == "root" or node.parent_id is None:
                            node_text = f"[{node.node_type}] {node.title} (confidence: {node.confidence:.2f})"
                            tree_node = nodes_tree.add(node_text)
                            
                            # Add children
                            for child_id in node.children:
                                if child_id in node_map:
                                    child = node_map[child_id]
                                    child_text = f"[{child.node_type}] {child.title} (confidence: {child.confidence:.2f})"
                                    tree_node.add(child_text)
                    
                    self.console.print(nodes_tree)
                
                # Show conclusions and insights
                if session.conclusions:
                    conclusions_panel = Panel(
                        "\n".join(f"• {conclusion}" for conclusion in session.conclusions),
                        title="Conclusions",
                        border_style="green"
                    )
                    self.console.print(conclusions_panel)
                
                if session.insights:
                    insights_panel = Panel(
                        "\n".join(f"• {insight}" for insight in session.insights),
                        title="Insights",
                        border_style="yellow"
                    )
                    self.console.print(insights_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error showing session: {e}[/red]")
    
    def list_sessions(self, format: str = "table") -> None:
        """List all thinking sessions"""
        try:
            sessions = self.thinking_tools.list_sessions()
            
            if format == "json":
                import json
                self.console.print(json.dumps(sessions, indent=2))
            else:
                if not sessions:
                    self.console.print("[yellow]No thinking sessions found[/yellow]")
                    return
                
                sessions_table = Table(title="Thinking Sessions")
                sessions_table.add_column("ID", style="cyan")
                sessions_table.add_column("Title", style="white")
                sessions_table.add_column("Framework", style="blue")
                sessions_table.add_column("Confidence", style="green")
                sessions_table.add_column("Complexity", style="yellow")
                sessions_table.add_column("Created", style="red")
                
                for session in sessions:
                    sessions_table.add_row(
                        session['id'],
                        session['title'][:30] + "..." if len(session['title']) > 30 else session['title'],
                        session['framework'],
                        f"{session['confidence_score']:.2f}",
                        f"{session['complexity_score']:.2f}",
                        session['created_at'][:10]
                    )
                
                self.console.print(sessions_table)
                
        except Exception as e:
            self.console.print(f"[red]Error listing sessions: {e}[/red]")
    
    def analyze_problem(self, problem_statement: str, format: str = "table") -> None:
        """Analyze a problem using structured approach"""
        try:
            analysis = self.thinking_tools.analyze_problem(problem_statement)
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(analysis), indent=2))
            else:
                # Show problem analysis
                analysis_table = Table(title="Problem Analysis")
                analysis_table.add_column("Aspect", style="cyan")
                analysis_table.add_column("Details", style="white")
                
                analysis_table.add_row("Problem ID", analysis.problem_id)
                analysis_table.add_row("Problem Statement", analysis.problem_statement)
                analysis_table.add_row("Components", ", ".join(analysis.components))
                analysis_table.add_row("Root Causes", ", ".join(analysis.root_causes))
                analysis_table.add_row("Constraints", ", ".join(analysis.constraints))
                analysis_table.add_row("Stakeholders", ", ".join(analysis.stakeholders))
                analysis_table.add_row("Success Criteria", ", ".join(analysis.success_criteria))
                analysis_table.add_row("Complexity Factors", ", ".join(analysis.complexity_factors))
                analysis_table.add_row("Risk Factors", ", ".join(analysis.risk_factors))
                analysis_table.add_row("Opportunities", ", ".join(analysis.opportunities))
                
                self.console.print(analysis_table)
                
        except Exception as e:
            self.console.print(f"[red]Error analyzing problem: {e}[/red]")
    
    def create_decision_tree(self, title: str, criteria: List[str], options: List[str],
                           format: str = "table") -> None:
        """Create a decision tree"""
        try:
            tree = self.thinking_tools.generate_decision_tree(title, criteria, options)
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(tree), indent=2, default=str))
            else:
                # Show decision tree
                tree_table = Table(title=f"Decision Tree: {tree.title}")
                tree_table.add_column("Option", style="cyan")
                tree_table.add_column("Probability", style="blue")
                tree_table.add_column("Expected Value", style="green")
                
                for option in tree.outcomes:
                    tree_table.add_row(
                        option,
                        f"{tree.probabilities[option]:.2f}",
                        f"{tree.expected_values[option]:.2f}"
                    )
                
                self.console.print(tree_table)
                
                # Show recommendations
                if tree.recommendations:
                    recommendations_panel = Panel(
                        "\n".join(f"• {rec}" for rec in tree.recommendations),
                        title="Recommendations",
                        border_style="green"
                    )
                    self.console.print(recommendations_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error creating decision tree: {e}[/red]")
    
    def create_thought_experiment(self, title: str, scenario: str, assumptions: List[str],
                                format: str = "table") -> None:
        """Create a thought experiment"""
        try:
            experiment = self.thinking_tools.create_thought_experiment(title, scenario, assumptions)
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(experiment), indent=2))
            else:
                # Show thought experiment
                experiment_panel = Panel(
                    f"[bold blue]Title:[/bold blue] {experiment.title}\n"
                    f"[bold green]Scenario:[/bold green] {experiment.scenario}\n"
                    f"[bold yellow]Variables:[/bold yellow] {', '.join(experiment.variables)}\n"
                    f"[bold white]Assumptions:[/bold white] {', '.join(experiment.assumptions)}",
                    title="Thought Experiment",
                    border_style="blue"
                )
                self.console.print(experiment_panel)
                
                # Show outcomes and insights
                outcomes_panel = Panel(
                    "\n".join(f"• {outcome}" for outcome in experiment.outcomes),
                    title="Possible Outcomes",
                    border_style="green"
                )
                self.console.print(outcomes_panel)
                
                insights_panel = Panel(
                    "\n".join(f"• {insight}" for insight in experiment.insights),
                    title="Key Insights",
                    border_style="yellow"
                )
                self.console.print(insights_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error creating thought experiment: {e}[/red]")
    
    def detect_biases(self, session_id: str, format: str = "table") -> None:
        """Detect cognitive biases in a session"""
        try:
            session = self.thinking_tools.load_session(session_id)
            if not session:
                self.console.print(f"[red]Session not found: {session_id}[/red]")
                return
            
            biases = self.thinking_tools.detect_cognitive_biases(session)
            
            if format == "json":
                import json
                self.console.print(json.dumps({"biases": biases}, indent=2))
            else:
                if not biases:
                    self.console.print("[green]No cognitive biases detected[/green]")
                    return
                
                biases_table = Table(title="Detected Cognitive Biases")
                biases_table.add_column("Bias", style="cyan")
                biases_table.add_column("Description", style="white")
                biases_table.add_column("Mitigation", style="green")
                
                for bias in biases:
                    bias_info = self.thinking_tools.biases.get(bias, {})
                    biases_table.add_row(
                        bias_info.get('name', bias),
                        bias_info.get('description', 'Unknown bias'),
                        bias_info.get('mitigation', 'Consider alternative perspectives')
                    )
                
                self.console.print(biases_table)
            
            # Save updated session
            self.thinking_tools.save_session(session)
            
        except Exception as e:
            self.console.print(f"[red]Error detecting biases: {e}[/red]")
    
    def list_frameworks(self, format: str = "table") -> None:
        """List available thinking frameworks"""
        try:
            frameworks = self.thinking_tools.frameworks
            
            if format == "json":
                import json
                self.console.print(json.dumps(frameworks, indent=2))
            else:
                frameworks_table = Table(title="Available Thinking Frameworks")
                frameworks_table.add_column("Framework", style="cyan")
                frameworks_table.add_column("Name", style="white")
                frameworks_table.add_column("Description", style="blue")
                frameworks_table.add_column("Steps", style="green")
                
                for key, framework in frameworks.items():
                    steps_count = len(framework.get('steps', []))
                    frameworks_table.add_row(
                        key,
                        framework.get('name', 'Unknown'),
                        framework.get('description', 'No description'),
                        str(steps_count)
                    )
                
                self.console.print(frameworks_table)
                
        except Exception as e:
            self.console.print(f"[red]Error listing frameworks: {e}[/red]")
    
    def list_biases(self, format: str = "table") -> None:
        """List cognitive biases and mitigation strategies"""
        try:
            biases = self.thinking_tools.biases
            
            if format == "json":
                import json
                self.console.print(json.dumps(biases, indent=2))
            else:
                biases_table = Table(title="Cognitive Biases and Mitigation")
                biases_table.add_column("Bias", style="cyan")
                biases_table.add_column("Description", style="white")
                biases_table.add_column("Mitigation Strategy", style="green")
                
                for key, bias in biases.items():
                    biases_table.add_row(
                        bias.get('name', key),
                        bias.get('description', 'No description'),
                        bias.get('mitigation', 'No mitigation strategy')
                    )
                
                self.console.print(biases_table)
                
        except Exception as e:
            self.console.print(f"[red]Error listing biases: {e}[/red]") 