"""
Streamlit Prompts - Optimized prompts for autonomous agent-driven application generation

This module contains concise, efficient prompts that guide autonomous agents
to create high-quality, modular Streamlit applications while minimizing token usage.
"""

from typing import Dict, Any, List
from enum import Enum


class PromptType(Enum):
    """Types of prompts for different development phases"""
    ARCHITECTURE = "architecture"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"


class StreamlitPrompts:
    """Optimized prompt library for Streamlit application generation"""
    
    @staticmethod
    def get_architecture_prompt(project: Dict[str, Any], complexity: str = "medium") -> str:
        """Get architecture planning prompt based on complexity"""
        
        complexity_instructions = {
            "simple": "Create a SINGLE-FILE application. Everything in app.py. Minimal dependencies. Keep it simple and straightforward.",
            "medium": "Create a MODULAR application with basic separation. 2-3 files maximum. Essential components only.",
            "complex": "Create a FULL enterprise architecture with proper MVC pattern, multiple components, utilities, and comprehensive structure."
        }
        
        return f"""Design architecture for Streamlit app: {project['name']} ({project['type']})
Description: {project['description']}
Complexity Level: {complexity.upper()}

{complexity_instructions[complexity]}

Requirements:
- Follow the complexity level specified
- Create only necessary files for the complexity level
- Ensure all imports are properly mapped
- Keep simple things simple, complex things properly structured

Output JSON structure:
{{
    "architecture": {{
        "pattern": "Single-File|Component-Based|MVC",
        "layers": ["UI"] or ["UI", "Business"] or ["UI", "Business", "Data"],
        "principles": ["KISS"] or ["DRY", "KISS"] or ["SOLID", "DRY", "KISS"]
    }},
    "file_structure": {{
        "main_files": [
            {{
                "file": "app.py",
                "purpose": "Main application entry point",
                "imports": ["list of imports"]
            }},
            {{
                "file": "requirements.txt",
                "purpose": "Dependencies"
            }}
        ],
        "models": [
            {{
                "file": "models/model_name.py",
                "class": "ClassName",
                "attributes": ["attr1", "attr2"],
                "methods": ["method1", "method2"]
            }}
        ],
        "components": [
            {{
                "file": "components/component_name.py",
                "class": "ClassName",
                "purpose": "Component purpose",
                "methods": ["method1", "method2"]
            }}
        ],
        "utils": [
            {{
                "file": "utils/utility_name.py",
                "class": "ClassName",
                "purpose": "Utility purpose",
                "methods": ["method1", "method2"]
            }}
        ]
    }},
    "dependencies": {{
        "required": ["streamlit"],
        "optional": ["other_deps"]
    }},
    "import_mapping": {{
        "app.py": ["imports"],
        "other_files.py": ["imports"]
    }}
}}

IMPORTANT: 
- For SIMPLE: Create only app.py and requirements.txt
- For MEDIUM: Create 2-3 files maximum
- For COMPLEX: Create full architecture
- Every file listed MUST be implemented by the developer"""

    @staticmethod
    def get_design_prompt(project: Dict[str, Any], architecture: str) -> str:
        """Get concise UI/UX design prompt"""
        return f"""Design UI/UX for Streamlit app: {project['name']}
Architecture: {architecture[:200]}...

Requirements:
- Intuitive, engaging user interface
- Responsive design with proper layout
- Interactive elements and user feedback
- Accessibility and usability focus
- Modern, professional appearance

Output JSON structure:
{{
    "ui_design": {{
        "layout": "sidebar|columns|tabs",
        "theme": "light|dark|custom",
        "color_scheme": "primary colors"
    }},
    "components": [
        {{
            "name": "component_name",
            "type": "input|output|visualization|navigation",
            "features": ["feature1", "feature2"],
            "interactions": ["click", "hover", "input"]
        }}
    ],
    "user_flow": [
        {{
            "step": "step_number",
            "action": "user action",
            "response": "system response"
        }}
    ],
    "responsive": {{
        "mobile": "mobile considerations",
        "desktop": "desktop optimizations"
    }}
}}"""

    @staticmethod
    def get_development_prompt(project: Dict[str, Any], architecture: str, design: str) -> str:
        """Get development prompt using architecture's file structure"""
        return f"""Develop Streamlit app: {project['name']}
Architecture: {architecture[:500]}...
Design: {design[:200]}...

CRITICAL REQUIREMENTS:
- Implement EXACTLY the file structure defined by the architect
- Create ALL files listed in the architecture's file_structure
- Follow the import_mapping defined in the architecture
- Ensure all imports are resolved and working
- Keep the implementation appropriate for the complexity level

ARCHITECTURE FILE STRUCTURE:
The architect has defined the following files that MUST be created:

{architecture}

DEVELOPMENT INSTRUCTIONS:
1. Parse the architecture JSON to extract file_structure
2. Create EVERY file listed in file_structure
3. Follow the import_mapping for proper imports
4. Implement the classes and methods specified in the architecture
5. Ensure all files can be imported without errors
6. Keep implementation simple for simple complexity, comprehensive for complex

COMPLEXITY GUIDELINES:
- SIMPLE: Single file, minimal code, basic functionality
- MEDIUM: 2-3 files, basic separation, essential features
- COMPLEX: Full architecture, comprehensive features, proper structure

Output format: Each file must be formatted exactly as:
```python
# file_path: path/to/file.py
# description: Brief description of the file
# actual code here
```

CRITICAL: You MUST implement ALL files from the architecture's file_structure.
Do not add extra files. Do not skip any files. Follow the architect's plan exactly."""

    @staticmethod
    def get_testing_prompt(project: Dict[str, Any], development_result: str, architecture_result: str) -> str:
        """Get testing prompt that validates against architecture"""
        return f"""Test Streamlit app: {project['name']}
Architecture: {architecture_result[:500]}...
Code: {development_result[:500]}...

CRITICAL VALIDATION REQUIREMENTS:
1. Check if app.py can be imported without errors
2. Verify ALL files from the architecture's file_structure exist
3. Validate that all imports in import_mapping are resolved
4. Check for syntax errors and logical issues
5. Ensure all classes and methods from architecture are implemented

SPECIFIC CHECKS:
- Does the implementation match the architect's file_structure?
- Are all files listed in the architecture actually created?
- Do all imports in import_mapping work correctly?
- Are all classes and methods from the architecture implemented?

IMPORTANT: Try to import app.py and catch any ModuleNotFoundError or ImportError.
Look for patterns like "No module named 'models.character'" or "No module named 'components.game_interface'"
and convert them to file paths like "models/character.py" or "components/game_interface.py"

CRITICAL: If you see any "ModuleNotFoundError: No module named" errors, you MUST include those missing modules
in the missing_files list. For example:
- "No module named 'components.game_interface'" → add "components/game_interface.py"
- "No module named 'models.character'" → add "models/character.py"
- "No module named 'utils.session_manager'" → add "utils/session_manager.py"

Output JSON structure:
{{
    "validation": {{
        "code_quality": "score/10",
        "functionality": "score/10",
        "structure": "score/10",
        "imports_valid": true/false,
        "architecture_compliant": true/false
    }},
    "missing_files": [
        "list of files from architecture that are missing (e.g., models/character.py, components/game_interface.py)"
    ],
    "missing_components": [
        "list of classes from architecture that are not implemented"
    ],
    "issues": [
        {{
            "type": "error|warning|suggestion",
            "description": "issue description",
            "fix": "recommended fix"
        }}
    ],
    "production_ready": true/false,
    "needs_developer_fix": true/false,
    "fix_instructions": "specific instructions for developer to fix missing components",
    "summary": "overall assessment"
}}"""

    @staticmethod
    def _get_type_specific_requirements(app_type: str) -> str:
        """Get type-specific requirements"""
        requirements = {
            "dashboard": "Interactive charts, real-time data, filtering, export capabilities",
            "chat": "Message history, user input, AI responses, conversation management",
            "data_analysis": "Data upload, processing, visualization, statistical analysis",
            "file_utility": "File upload/download, processing, format conversion, batch operations",
            "game": "Game logic, scoring, levels, user interaction, progress tracking",
            "ecommerce": "Product catalog, shopping cart, checkout, inventory management",
            "crm": "Contact management, lead tracking, sales pipeline, reporting",
            "inventory": "Stock tracking, alerts, reporting, barcode scanning",
            "research": "Data collection, analysis, visualization, report generation",
            "knowledge_base": "Search, categorization, content management, user contributions",
            "document_analysis": "Text extraction, analysis, summarization, keyword extraction",
            "creative_writing": "Text generation, editing, collaboration, publishing",
            "music": "Audio playback, playlist management, analysis, recommendations",
            "design": "Visual tools, templates, collaboration, export options",
            "education": "Learning modules, progress tracking, assessments, feedback",
            "language_learning": "Vocabulary, grammar, pronunciation, progress tracking",
            "programming_tutorial": "Code examples, exercises, testing, progress tracking",
            "api_testing": "Request builder, response analysis, authentication, documentation",
            "system_monitoring": "Real-time metrics, alerts, logging, performance analysis",
            "custom": "Custom requirements based on specific needs"
        }
        return requirements.get(app_type, "Standard web application features") 