"""
Integrated Generator module for creating production-ready code and comprehensive test cases.
"""

import os
import logging
import subprocess
import re
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import black
import ast
from datetime import datetime

class Generator:
    """Handles both code and test generation, formatting, and validation."""
    
    def __init__(self, ai_engine=None, error_handler=None, file_manager=None):
        self.code_output_dir = os.getenv('GENERATED_CODE_DIR', 'generated/code')
        self.test_output_dir = os.getenv('GENERATED_TESTS_DIR', 'generated/tests')
        self.ai_engine = ai_engine
        self.error_handler = error_handler
        self.file_manager = file_manager
        self._ensure_output_dirs()
    
    def _ensure_output_dirs(self):
        """Ensure output directories exist."""
        Path(self.code_output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.test_output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_code(self, requirement: str, language: str = "python") -> Dict[str, Any]:
        """Generate code from requirement description."""
        try:
            # Create code template
            code = self._create_code_template(requirement, language)
            
            # Format the code
            formatted_code = self._format_code(code, language)
            
            # Validate the code
            validation_result = self._validate_code(formatted_code, language)
            
            # Save the code
            file_path = self._save_code(formatted_code, requirement, language)
            
            return {
                "success": True,
                "code": formatted_code,
                "saved_path": file_path,
                "analysis": {
                    "language": language,
                    "requirement": requirement,
                    "validation": validation_result
                }
            }
            
        except Exception as e:
            logging.error(f"Error generating code: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_tests(self, code: str, language: str = "python", test_type: str = "unit", model: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive test suite for the given code using AI models.
        
        Args:
            code: Source code to generate tests for
            language: Programming language (default: "python")
            test_type: Type of tests to generate (default: "unit")
            model: AI model to use for generation
            
        Returns:
            Dict containing:
            - success: bool
            - test_code: str (generated test code)
            - saved_path: str (path to saved test file)
            - analysis: dict (code analysis results)
            - run_results: dict (test execution results)
            - test_structure: dict (test organization)
        """
        try:
            if not self.ai_engine:
                raise Exception("AI engine not available for code-based test generation")
            
            # Analyze the code to understand what to test
            code_analysis = self._analyze_code(code, language)
            
            # Create comprehensive test suite prompt
            prompt = self._create_comprehensive_test_prompt(code, code_analysis, language, test_type)
            
            # Generate test suite using AI with specified model
            response = self.ai_engine.generate_response(prompt, model=model)
            
            # Check if response is an error message
            if response.startswith("Error generating response:"):
                raise Exception(f"AI engine error: {response}")
            
            # Check if AI returned an error message
            if response.startswith("ERROR:"):
                raise Exception(f"AI generation failed: {response}")
            
            # Check if response is empty or too short
            if not response or len(response.strip()) < 100:
                raise Exception(f"AI response too short or empty: {len(response)} characters")
            
            # Parse and organize the test suite
            test_structure = self._parse_test_suite(response, code_analysis)
            
            # Create the complete test suite structure
            test_suite = self._create_test_suite_structure(test_structure, code)
            
            # Save test suite files
            test_files = self._save_test_suite(test_suite, code_analysis, language)
            
            # Run the test suite
            test_results = self._run_comprehensive_tests(test_files, language)
            
            return {
                "success": True,
                "test_structure": test_structure,
                "test_files": test_files,
                "saved_path": test_files.get("main_test_file", ""),
                "analysis": code_analysis,
                "run_results": test_results
            }
            
        except Exception as e:
            logging.error(f"Error generating comprehensive tests: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_requirements_tests(self, requirements: str, test_count: int = 100, model: str = None) -> Dict[str, Any]:
        """
        Generate test cases from requirements specifications.
        
        Args:
            requirements: Requirements text/specifications
            test_count: Number of test cases to generate
            model: AI model to use for generation
            
        Returns:
            Dict containing test cases in structured format
        """
        try:
            if not self.ai_engine:
                raise Exception("AI engine not available for requirements-based test generation")
            
            # Create requirements-based test prompt
            prompt = self._create_requirements_test_prompt(requirements, test_count)
            
            # Generate test cases using AI with specified model
            response = self.ai_engine.generate_response(prompt, model=model)
            
            # Check if response is an error message
            if response.startswith("Error generating response:"):
                raise Exception(f"AI engine error: {response}")
            
            # Check if AI returned an error message
            if response.startswith("ERROR:"):
                raise Exception(f"AI generation failed: {response}")
            
            # Check if response is empty or too short
            if not response or len(response.strip()) < 100:
                raise Exception(f"AI response too short or empty: {len(response)} characters")
            
            # Parse the structured response
            test_cases = self._parse_requirements_response(response, test_count)
            
            # Check if parsing resulted in test cases
            if not test_cases:
                raise Exception(f"No test cases parsed from AI response. Response length: {len(response)}")
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"requirements_tests_{timestamp}.json"
            file_path = os.path.join(self.test_output_dir, filename)
            
            with open(file_path, 'w') as f:
                json.dump({"test_cases": test_cases}, f, indent=2)
            
            return {
                "success": True,
                "test_cases": test_cases,
                "saved_path": file_path,
                "analysis": {
                    "test_count": len(test_cases),
                    "source": "requirements",
                    "categories": list(set(tc.get('category', 'Unknown') for tc in test_cases))
                }
            }
            
        except Exception as e:
            logging.error(f"Error generating requirements tests: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_cases": [],
                "saved_path": None,
                "analysis": {
                    "test_count": 0,
                    "source": "requirements",
                    "categories": []
                }
            }
    
    def _create_code_template(self, requirement: str, language: str) -> str:
        """Create code template based on requirement."""
        if language.lower() == "python":
            return self._create_python_template(requirement)
        else:
            return f"# {language} code for: {requirement}\n# TODO: Implement based on requirement"
    
    def _create_python_template(self, requirement: str) -> str:
        """Create Python code template."""
        return f'''"""
Generated code for requirement: {requirement}
"""

import logging
from typing import Any, Dict, List, Optional
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequirementImplementation:
    """Implementation for the specified requirement."""
    
    def __init__(self):
        """Initialize the implementation."""
        self.config = self._load_config()
        logger.info("RequirementImplementation initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration settings."""
        return {{
            "debug": os.getenv("DEBUG", "False").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "INFO")
        }}
    
    def process_requirement(self, input_data: Any) -> Dict[str, Any]:
        """
        Process the requirement with input data.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Dict containing processing results
        """
        try:
            logger.info("Processing requirement with input data")
            
            # TODO: Implement specific logic based on requirement
            result = {{
                "status": "success",
                "input_processed": input_data,
                "requirement": "{requirement}",
                "timestamp": datetime.now().isoformat()
            }}
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing requirement: {{e}}")
            return {{
                "status": "error",
                "error": str(e)
            }}

def main():
    """Main function to run the implementation."""
    implementation = RequirementImplementation()
    
    # Example usage
    test_data = "example input"
    result = implementation.process_requirement(test_data)
    print(f"Result: {{result}}")

if __name__ == "__main__":
    main()
'''
    
    def _analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code to understand structure and generate appropriate tests."""
        analysis = {
            "classes": [],
            "functions": [],
            "imports": [],
            "complexity": "low",
            "module_structure": "standard",
            "project_type": "unknown",
            "dependencies": [],
            "entry_points": []
        }
        
        try:
            if language.lower() == "python":
                tree = ast.parse(code)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        methods = []
                        for n in node.body:
                            if isinstance(n, ast.FunctionDef):
                                methods.append({
                                    "name": n.name,
                                    "args": [arg.arg for arg in n.args.args],
                                    "decorators": [d.id for d in n.decorator_list if isinstance(d, ast.Name)]
                                })
                        
                        analysis["classes"].append({
                            "name": node.name,
                            "methods": methods,
                            "line_count": len(node.body),
                            "bases": [base.id for base in node.bases if isinstance(base, ast.Name)]
                        })
                    elif isinstance(node, ast.FunctionDef):
                        analysis["functions"].append({
                            "name": node.name,
                            "args": [arg.arg for arg in node.args.args],
                            "line_count": len(node.body) if node.body else 0,
                            "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
                        })
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            analysis["imports"].append(f"{module}.{alias.name}")
                
                # Determine complexity and project type
                total_lines = len(code.split('\n'))
                if total_lines > 500:
                    analysis["complexity"] = "high"
                elif total_lines > 200:
                    analysis["complexity"] = "medium"
                else:
                    analysis["complexity"] = "low"
                
                # Detect project type based on imports and structure
                imports = [imp.lower() for imp in analysis["imports"]]
                if any(web in imports for web in ['flask', 'django', 'fastapi', 'streamlit']):
                    analysis["project_type"] = "web_application"
                elif any(data in imports for data in ['pandas', 'numpy', 'matplotlib', 'scipy']):
                    analysis["project_type"] = "data_science"
                elif any(ml in imports for ml in ['sklearn', 'tensorflow', 'torch', 'keras']):
                    analysis["project_type"] = "machine_learning"
                elif any(opt in imports for opt in ['pyomo', 'pulp', 'cvxpy']):
                    analysis["project_type"] = "optimization"
                else:
                    analysis["project_type"] = "general_python"
                
                # Detect entry points
                for func in analysis["functions"]:
                    if func["name"] in ["main", "app", "run", "start"]:
                        analysis["entry_points"].append(func["name"])
                
                # Detect module structure
                if len(analysis["classes"]) > 5:
                    analysis["module_structure"] = "class_heavy"
                elif len(analysis["functions"]) > 10:
                    analysis["module_structure"] = "function_heavy"
                else:
                    analysis["module_structure"] = "balanced"
                    
        except Exception as e:
            logging.warning(f"Code analysis failed: {e}")
        
        return analysis
    
    def _create_test_template(self, code: str, code_analysis: Dict[str, Any], language: str, test_type: str) -> str:
        """Create test template based on code analysis."""
        if language.lower() == "python":
            return self._create_python_test_template(code, code_analysis, test_type)
        else:
            return f"# {language} tests for the code\n# TODO: Implement test cases"
    
    def _create_requirements_test_prompt(self, requirements: str, test_count: int) -> str:
        """Create prompt for requirements-based test generation."""
        return f"""
You are a senior Android mobile device testing engineer. Generate exactly {test_count} test cases for the following device specifications/requirements.

Device Specifications/Requirements:
{requirements}

IMPORTANT: Format each test case exactly as follows:

TEST_CASE_1: [Detailed test case description]
CATEGORY_1: [Category]
SUBCATEGORY_1: [Subcategory]
PRIORITY_1: [High/Medium/Low/Critical]

TEST_CASE_2: [Detailed test case description]
CATEGORY_2: [Category]
SUBCATEGORY_2: [Subcategory]
PRIORITY_2: [High/Medium/Low/Critical]

Continue this pattern for all {test_count} test cases.

Test case descriptions should be:
- Action-oriented (start with verbs like "Execute", "Perform", "Navigate", "Test", "Verify", "Launch", "Connect", "Capture", "Check")
- Specific to the device specifications provided
- Detailed enough for an AI agent to execute
- Focused on practical testing scenarios

Available categories: Connectivity, UI/UX, Compatibility, Hardware, Security, Software, Audio, Performance, Usability, Battery, Camera, Storage, Network, Biometrics, System, Functional, Non-Functional, Integration

Test case descriptions should be action-oriented and specific, for example:
- "Execute tap gesture on Settings app icon and verify app launches successfully"
- "Perform swipe up gesture from bottom edge to access recent apps menu"
- "Navigate to Settings > Display > Brightness and adjust slider to 50%"
- "Test WiFi connection stability during phone calls"
- "Verify camera app opens and captures photo within 3 seconds"

Do not include any introductory text or explanations. Start directly with TEST_CASE_1: and continue with the exact format above.
"""

    def _parse_requirements_response(self, response: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse the structured response from requirements-based test generation."""
        test_cases = []
        lines = response.split('\n')
        current_test = {}
        test_case_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Parse structured format
            if line.startswith('TEST_CASE_'):
                # Save previous test case if exists
                if current_test and 'description' in current_test:
                    test_cases.append(current_test)
                    test_case_count += 1
                
                # Start new test case
                current_test = {
                    'test_id': f"TC_{test_case_count+1:04d}",
                    'description': line.split(':', 1)[1].strip() if ':' in line else line,
                    'category': 'Hardware',  # Default
                    'subcategory': 'General',  # Default
                    'device_type': 'Mobile Device',
                    'priority': 'Medium'  # Default
                }
                
            elif line.startswith('CATEGORY_'):
                if current_test:
                    category = line.split(':', 1)[1].strip() if ':' in line else line
                    current_test['category'] = category
                    
            elif line.startswith('SUBCATEGORY_'):
                if current_test:
                    subcategory = line.split(':', 1)[1].strip() if ':' in line else line
                    current_test['subcategory'] = subcategory
                    
            elif line.startswith('PRIORITY_'):
                if current_test:
                    priority = line.split(':', 1)[1].strip() if ':' in line else line
                    current_test['priority'] = priority
        
        # Add the last test case
        if current_test and 'description' in current_test:
            test_cases.append(current_test)
            test_case_count += 1
        
        # Add test_id to all test cases if missing
        for i, test_case in enumerate(test_cases):
            if 'test_id' not in test_case:
                test_case['test_id'] = f"TC_{i+1:04d}"
        
        return test_cases[:expected_count]
    
    def _create_python_test_template(self, code: str, code_analysis: Dict[str, Any], test_type: str) -> str:
        """Create Python test template."""
        test_imports = []
        test_functions = []
        
        # Add imports based on code analysis
        for import_name in code_analysis.get("imports", []):
            if "logging" in import_name:
                test_imports.append("import logging")
            elif "pathlib" in import_name:
                test_imports.append("from pathlib import Path")
            elif "typing" in import_name:
                test_imports.append("from typing import Any, Dict, List, Optional")
        
        # Add test functions for each class and function
        for class_info in code_analysis.get("classes", []):
            class_name = class_info["name"]
            test_functions.append(f'''
class Test{class_name}:
    """Test cases for {class_name} class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.instance = {class_name}()
    
    def test_{class_name.lower()}_initialization(self):
        """Test {class_name} initialization."""
        assert self.instance is not None
        assert hasattr(self.instance, 'config')
    
    def test_{class_name.lower()}_config_loading(self):
        """Test configuration loading."""
        config = self.instance._load_config()
        assert isinstance(config, dict)
        assert "debug" in config
        assert "log_level" in config
''')
        
        for func_info in code_analysis.get("functions", []):
            func_name = func_info["name"]
            if not func_name.startswith("_"):  # Skip private methods
                test_functions.append(f'''
    def test_{func_name}(self):
        """Test {func_name} function."""
        # TODO: Add specific test cases based on function signature
        result = self.instance.{func_name}()
        assert result is not None
''')
        
        # Create the test template
        test_code = f'''"""
Generated test cases for the code.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
{chr(10).join(set(test_imports))}

# Add the parent directory to sys.path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main module (adjust the import based on your actual module structure)
# from your_module import RequirementImplementation

{chr(10).join(test_functions)}

class TestIntegration:
    """Integration tests."""
    
    def test_end_to_end_workflow(self):
        """Test the complete workflow."""
        # TODO: Implement end-to-end test
        assert True
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        # TODO: Test various error conditions
        assert True

if __name__ == "__main__":
    pytest.main([__file__])
'''
        
        return test_code
    
    def _create_comprehensive_test_prompt(self, code: str, code_analysis: Dict[str, Any], language: str, test_type: str) -> str:
        """Create comprehensive test suite prompt for professional-grade testing."""
        return f"""
You are a senior Python Test Engineer. I have uploaded a Python project. Generate a COMPLETE pytest test suite.

⚠️  CRITICAL: You MUST follow the EXACT format below. Any deviation will cause the test generation to fail.
⚠️  You MUST include ALL 5 required sections with the EXACT headers shown.
⚠️  Do not add any explanations, introductions, or markdown formatting outside the sections.

CODE TO TEST:
{code}

CODE ANALYSIS:
- Classes: {len(code_analysis.get('classes', []))}
- Functions: {len(code_analysis.get('functions', []))}
- Imports: {', '.join(code_analysis.get('imports', []))}
- Complexity: {code_analysis.get('complexity', 'unknown')}
- Module Structure: {code_analysis.get('module_structure', 'standard')}

🎯 Goals
- Identify all modules, classes, and functions and write tests for normal, edge, and error cases.
- Achieve ≥85% line coverage (fail under that threshold).
- Make tests deterministic, fast, and isolated (no real network, file system, DB, or time dependencies).

🧱 Test structure
- Create a top-level `tests/` folder mirroring the project/package structure.
- One test file per module: `tests/test_<module>.py`.
- Add a shared `tests/conftest.py` with fixtures, factories, and common mocks.
- Use `pytest`, `pytest-cov`, `hypothesis` (when helpful), and `freezegun` for time.
- Prefer `pytest.mark.parametrize` for input matrices; use `unittest.mock`/`monkeypatch` for external calls.

🔧 What to mock / how
- Network/API calls → `requests`/clients mocked; verify endpoint/params and response handling.
- File I/O → use `tmp_path` fixture; don't write to repo paths.
- Time/randomness → freeze time (`freezegun.freeze_time`) and seed randomness.
- Env vars/config → `monkeypatch.setenv` and temporary config fixtures.

🧪 What to test (per function/class)
- Happy path(s) with realistic inputs.
- Edge cases (empty, None, boundary sizes, large/small numbers, unusual encodings).
- Error handling: raise the right exceptions with the right messages.
- For classes: constructor invariants, key methods, dunder methods, equality/hash if defined.
- For CLIs: parse args, exit codes, and stdout/stderr using `capsys`.

📦 Setup files to add
- `pytest.ini` or `pyproject.toml`:
    - enable pytest, set `addopts = -q --maxfail=1 --cov=<TOP_LEVEL_PACKAGE> --cov-report=term-missing:skip-covered --cov-fail-under=85`
    - set `testpaths = tests`
- Minimal `requirements-dev.txt` (pytest, pytest-cov, hypothesis, freezegun).
- If project uses a package folder (e.g., `src/`), ensure tests import correctly (add to PYTHONPATH if needed).

📋 Deliverables
1) Create all test files under `tests/` with clear names, docstrings, and comments.
2) A brief `tests/TEST_PLAN.md`:
   - modules discovered, functions/classes covered, what's mocked, gaps/TODOs.
3) Run the test suite and show:
   - summary (pass/fail), coverage %, and missing lines (if any).
4) If coverage <85%, iterate: explain the gaps and add targeted tests to raise coverage.
5) Print a short "How to run locally" section:
   - `pip install -r requirements-dev.txt`
   - `pytest`

Assumptions/Notes
- Auto-detect the project's top-level package and entrypoints.
- If something cannot be sensibly tested without huge scaffolding, stub a focused unit test and note it in TEST_PLAN.
- Prefer readable, maintainable tests over over-mocking.

CRITICAL REQUIREMENTS:
- You MUST return ONLY the test suite structure with NO explanations or markdown formatting
- You MUST use EXACTLY this format with ## headers:
- Start with: ## TEST_PLAN.md
- Then: ## tests/conftest.py  
- Then: ## tests/test_main.py (or appropriate test files)
- Then: ## pytest.ini
- Then: ## requirements-dev.txt
- Each section MUST start with ## and end before the next ##
- ALL 5 sections are REQUIRED - do not skip any
- Make tests self-contained (no external imports of the original module)
- Use the embedded code directly in tests
- NEVER import the original module (the code will be embedded in the same file)
- NEVER import external libraries (sentence_transformers, pyomo, pandas, numpy, openai, streamlit, etc.) - only use standard library and pytest
- The original code will be embedded at the top of test files, so you can reference functions/classes directly
- Use classes and functions directly as they will be embedded in the same file
- Ensure proper Python indentation (4 spaces for function bodies)
- All function definitions must have proper indented bodies
- Analyze the code structure and create appropriate tests for all classes and functions
- If you cannot generate proper structured output, return an error message starting with "ERROR:"

MANDATORY SECTIONS (ALL 5 MUST BE INCLUDED):
1. ## TEST_PLAN.md - Test plan documentation
2. ## tests/conftest.py - Shared test configuration and fixtures
3. ## tests/test_main.py - Main test file (or appropriate test files)
4. ## pytest.ini - Pytest configuration file
5. ## requirements-dev.txt - Development dependencies

EXAMPLE STRUCTURE:
## TEST_PLAN.md
# Test Plan for Project

## Overview
Brief description of what is being tested

## Test Strategy
Testing approach and methodology

## Coverage Goals
Target coverage and testing objectives

## tests/conftest.py
import pytest
import unittest.mock as mock
import os
import sys

@pytest.fixture
def sample_data():
    return dict(test="data")

## tests/test_main.py
import pytest
import unittest.mock as mock

class TestMainFunctionality:
    def test_basic_functionality(self):
        assert True

## pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short

## requirements-dev.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
"""

    def _parse_test_suite(self, response: str, code_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the AI response to extract test suite structure."""
        test_structure = {
            "test_plan": "",
            "test_files": {},
            "pytest_config": "",
            "requirements_dev": "",
            "modules": [],
            "coverage_target": 85
        }
        
        try:
            # Parse the response to extract different components
            lines = response.split('\n')
            current_section = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('## TEST_PLAN.md'):
                    if current_section and current_content:
                        if current_section in ["test_plan", "pytest_config", "requirements_dev"]:
                            test_structure[current_section] = '\n'.join(current_content)
                        else:
                            test_structure["test_files"][current_section] = '\n'.join(current_content)
                    current_section = "test_plan"
                    current_content = []
                elif line.startswith('## tests/conftest.py'):
                    if current_section and current_content:
                        if current_section in ["test_plan", "pytest_config", "requirements_dev"]:
                            test_structure[current_section] = '\n'.join(current_content)
                        else:
                            test_structure["test_files"][current_section] = '\n'.join(current_content)
                    current_section = "tests/conftest.py"
                    current_content = []
                elif line.startswith('## tests/test_'):
                    if current_section and current_content:
                        if current_section in ["test_plan", "pytest_config", "requirements_dev"]:
                            test_structure[current_section] = '\n'.join(current_content)
                        else:
                            test_structure["test_files"][current_section] = '\n'.join(current_content)
                    # Extract filename from the header
                    filename = line.replace('## ', '').strip()
                    current_section = filename
                    current_content = []
                elif line.startswith('## pytest.ini'):
                    if current_section and current_content:
                        if current_section in ["test_plan", "pytest_config", "requirements_dev"]:
                            test_structure[current_section] = '\n'.join(current_content)
                        else:
                            test_structure["test_files"][current_section] = '\n'.join(current_content)
                    current_section = "pytest_config"
                    current_content = []
                elif line.startswith('## requirements-dev.txt'):
                    if current_section and current_content:
                        if current_section in ["test_plan", "pytest_config", "requirements_dev"]:
                            test_structure[current_section] = '\n'.join(current_content)
                        else:
                            test_structure["test_files"][current_section] = '\n'.join(current_content)
                    current_section = "requirements_dev"
                    current_content = []
                elif line.startswith('##'):
                    # End of current section
                    if current_section and current_content:
                        if current_section in ["test_plan", "pytest_config", "requirements_dev"]:
                            test_structure[current_section] = '\n'.join(current_content)
                        else:
                            test_structure["test_files"][current_section] = '\n'.join(current_content)
                    current_section = None
                    current_content = []
                elif current_section:
                    current_content.append(line)
            
            # Add the last section
            if current_section and current_content:
                if current_section in ["test_plan", "pytest_config", "requirements_dev"]:
                    test_structure[current_section] = '\n'.join(current_content)
                else:
                    test_structure["test_files"][current_section] = '\n'.join(current_content)
            
            # Validate that we have the required test structure
            if not test_structure["test_files"]:
                raise Exception("No test files found in AI response. Expected structured output with ## headers for test files.")
            if not test_structure["test_plan"]:
                raise Exception("No test plan found in AI response. Expected ## TEST_PLAN.md section.")
            if not test_structure["pytest_config"]:
                raise Exception("No pytest configuration found in AI response. Expected ## pytest.ini section.")
            if not test_structure["requirements_dev"]:
                raise Exception("No requirements file found in AI response. Expected ## requirements-dev.txt section.")
                
        except Exception as e:
            logging.error(f"Error parsing test suite: {e}")
            raise Exception(f"Failed to parse AI response into proper test suite structure: {e}")
        
        return test_structure
    
    def _clean_test_content(self, content: str, original_code: str) -> str:
        """Clean up generated test content to fix common issues."""
        # First, detect the original module name from the code
        module_name = self._detect_module_name(original_code)
        
        # Remove all problematic import statements
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped_line = line.strip()
            
            # Skip problematic import statements for the detected module
            if module_name and any(pattern in line for pattern in [
                f'from {module_name} import',
                f'import {module_name}',
                f'from {module_name} import',
                f'import {module_name} as',
                module_name
            ]):
                continue
            
            # Skip external library imports (keep only standard library and pytest)
            if stripped_line.startswith('import ') or stripped_line.startswith('from '):
                if not self._is_standard_library_import(stripped_line):
                    continue
            
            # Skip empty lines at the beginning
            if not cleaned_lines and not line.strip():
                continue
                
            cleaned_lines.append(line)
        
        # Join and clean up
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Remove any remaining problematic patterns with regex
        if module_name:
            cleaned_content = re.sub(rf'from\s+{re.escape(module_name)}\s+import.*?\n', '', cleaned_content)
            cleaned_content = re.sub(rf'import\s+{re.escape(module_name)}.*?\n', '', cleaned_content)
            cleaned_content = re.sub(rf'{re.escape(module_name)}.*?\n', '', cleaned_content)
        
        # Fix indentation issues - ensure proper function structure
        lines = cleaned_content.split('\n')
        fixed_lines = []
        current_indent = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fixed_lines.append('')
                continue
                
            if stripped.startswith('def ') and ':' in stripped:
                # Function definition - ensure proper indentation
                fixed_lines.append(f"    {stripped}")
                current_indent = 4
            elif stripped.startswith('@pytest.fixture'):
                # Fixture decorator
                fixed_lines.append(f"    {stripped}")
                current_indent = 4
            elif stripped.startswith('return ') or stripped.startswith('yield '):
                # Return/yield statement inside function
                fixed_lines.append(f"        {stripped}")
            elif stripped.startswith('for ') or stripped.startswith('if ') or stripped.startswith('with '):
                # Control flow inside function
                if current_indent > 0:
                    fixed_lines.append(f"        {stripped}")
                else:
                    fixed_lines.append(f"    {stripped}")
            elif stripped.startswith('import ') or stripped.startswith('from '):
                # Import statements at module level
                fixed_lines.append(stripped)
            elif stripped.startswith('class '):
                # Class definition
                fixed_lines.append(f"    {stripped}")
            else:
                # Other lines - maintain context
                if current_indent > 0 and not stripped.startswith('#'):
                    fixed_lines.append(f"        {stripped}")
                else:
                    fixed_lines.append(line)
        
        # Join and final cleanup
        cleaned_content = '\n'.join(fixed_lines)
        cleaned_content = re.sub(r'\n\n\n+', '\n\n', cleaned_content)
        
        return cleaned_content.strip()
    
    def _detect_module_name(self, code: str) -> str:
        """Detect the module name from the uploaded code."""
        try:
            # Parse the code to find class and function definitions
            tree = ast.parse(code)
            
            # Look for class definitions first (most likely to be the main module)
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            if classes:
                # Use the first class name as a base for module name
                class_name = classes[0]
                # Convert CamelCase to snake_case for module name
                module_name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', class_name).lower()
                return module_name
            
            # Look for function definitions
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            if functions:
                # Use the first function name as a base
                func_name = functions[0]
                # Convert to snake_case
                module_name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', func_name).lower()
                return module_name
            
            # If no classes or functions, try to extract from file content
            lines = code.split('\n')
            for line in lines:
                # Look for common patterns that might indicate module name
                if 'class ' in line:
                    match = re.search(r'class\s+(\w+)', line)
                    if match:
                        class_name = match.group(1)
                        module_name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', class_name).lower()
                        return module_name
                
                if 'def ' in line:
                    match = re.search(r'def\s+(\w+)', line)
                    if match:
                        func_name = match.group(1)
                        module_name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', func_name).lower()
                        return module_name
            
            # Default fallback
            return "main_module"
            
        except Exception as e:
            logging.warning(f"Could not detect module name: {e}")
            return "main_module"
    
    def _is_standard_library_import(self, import_line: str) -> bool:
        """Check if an import is from the standard library or pytest."""
        import_line = import_line.lower()
        
        # Standard library modules
        stdlib_modules = {
            'os', 'sys', 're', 'json', 'datetime', 'time', 'random', 'math', 'collections',
            'itertools', 'functools', 'pathlib', 'tempfile', 'shutil', 'subprocess',
            'logging', 'typing', 'unittest', 'threading', 'multiprocessing', 'asyncio',
            'urllib', 'http', 'socket', 'ssl', 'hashlib', 'base64', 'pickle', 'copy',
            'decimal', 'fractions', 'statistics', 'enum', 'dataclasses', 'contextlib',
            'abc', 'weakref', 'gc', 'inspect', 'traceback', 'pdb', 'profile', 'cProfile',
            'argparse', 'configparser', 'csv', 'difflib', 'email', 'html', 'http', 'imaplib',
            'ipaddress', 'json', 'logging', 'mailbox', 'mimetypes', 'netrc', 'nntplib',
            'poplib', 'quopri', 'smtplib', 'telnetlib', 'uu', 'xml', 'zipfile', 'zlib',
            'calendar', 'locale', 'gettext', 'string', 'struct', 'codecs', 'unicodedata',
            'stringprep', 'readline', 'rlcompleter', 'array', 'bisect', 'heapq', 'weakref',
            'types', 'copyreg', 'pickletools', 'shelve', 'dbm', 'sqlite3', 'xmlrpc',
            'webbrowser', 'cgi', 'cgitb', 'wsgiref', 'urllib', 'ftplib', 'socketserver',
            'xml', 'html', 'xmlrpc', 'test', 'doctest', 'unittest', 'test.support'
        }
        
        # Testing libraries (allowed)
        testing_modules = {'pytest', 'unittest', 'mock', 'freezegun', 'hypothesis'}
        
        # Check if it's a standard library import
        if import_line.startswith('import '):
            module = import_line.split('import ')[1].split(' as ')[0].split('.')[0]
            return module in stdlib_modules or module in testing_modules
        elif import_line.startswith('from '):
            parts = import_line.split(' ')
            if len(parts) >= 3:
                module = parts[1].split('.')[0]
                return module in stdlib_modules or module in testing_modules
        
        return False
    
    def _clean_original_code_for_tests(self, original_code: str) -> str:
        """Clean original code to remove external imports and dependencies for test embedding."""
        lines = original_code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped_line = line.strip()
            
            # Skip external library imports
            if stripped_line.startswith('import ') or stripped_line.startswith('from '):
                if not self._is_standard_library_import(stripped_line):
                    # Replace external imports with mock comments and mock objects
                    if stripped_line.startswith('import '):
                        # Handle: import module
                        # Handle: import module as alias
                        import_part = stripped_line.split('import ')[1]
                        if ' as ' in import_part:
                            module, alias = import_part.split(' as ')
                            module = module.strip()
                            alias = alias.strip()
                            cleaned_lines.append(f"# Mock import: {stripped_line}")
                            cleaned_lines.append(f"{alias} = None  # Mocked for testing")
                        else:
                            module = import_part.split('.')[0].strip()
                            cleaned_lines.append(f"# Mock import: {stripped_line}")
                            cleaned_lines.append(f"{module} = None  # Mocked for testing")
                    elif stripped_line.startswith('from '):
                        # Handle: from module import item1, item2
                        # Handle: from module import item as alias
                        parts = stripped_line.split(' ')
                        if len(parts) >= 4:
                            module = parts[1]
                            imported_items = parts[3]
                            cleaned_lines.append(f"# Mock import: {stripped_line}")
                            
                            # Handle multiple imports
                            for item in imported_items.split(','):
                                item = item.strip()
                                if ' as ' in item:
                                    # Handle: item as alias
                                    original_name, alias = item.split(' as ')
                                    original_name = original_name.strip()
                                    alias = alias.strip()
                                    cleaned_lines.append(f"{alias} = None  # Mocked for testing")
                                elif item:
                                    cleaned_lines.append(f"{item} = None  # Mocked for testing")
                    continue
            
            # Keep all other lines
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _extract_standard_imports(self, code: str) -> List[str]:
        """Extract only standard library imports from the original code."""
        try:
            tree = ast.parse(code)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if self._is_standard_library_import(f"import {alias.name}"):
                            imports.append(f"import {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        import_line = f"from {module} import {alias.name}"
                        if self._is_standard_library_import(import_line):
                            imports.append(import_line)
            
            return imports
        except Exception as e:
            logging.warning(f"Error extracting standard imports: {e}")
            return []
    

    
    def _create_minimal_valid_test(self, original_code: str) -> str:
        """Create a minimal valid test when AI generation fails."""
        # Detect classes and functions from original code
        classes = []
        functions = []
        
        try:
            tree = ast.parse(original_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
        except:
            pass
        
        # Generate class tests
        class_tests = ""
        for class_name in classes[:3]:  # Limit to first 3 classes
            class_tests += f"""
    def test_{class_name.lower()}_exists(self):
        \"\"\"Test that {class_name} class exists and can be instantiated.\"\"\"
        # The class is embedded in the same file
        assert '{class_name}' in globals()
"""
        
        # Generate function tests
        function_tests = ""
        for func_name in functions[:5]:  # Limit to first 5 functions
            function_tests += f"""
    def test_{func_name}_exists(self):
        \"\"\"Test that {func_name} function exists.\"\"\"
        # The function is embedded in the same file
        assert '{func_name}' in globals()
"""
        
        return f"""import pytest
import unittest.mock as mock
import os
import sys

# Basic test suite
class TestBasicFunctionality:
    \"\"\"Basic test suite for the main functionality.\"\"\"
    
    def test_basic_imports(self):
        \"\"\"Test that basic imports work.\"\"\"
        assert os is not None
        assert sys is not None
    
    def test_code_structure(self):
        \"\"\"Test that the original code has basic structure.\"\"\"
        # This is a placeholder test
        assert True{class_tests}{function_tests}
    
    @pytest.mark.parametrize("test_input,expected", [
        (1, True),
        (0, False),
        (-1, True),
    ])
    def test_parametrized_example(self, test_input, expected):
        \"\"\"Example of parametrized test.\"\"\"
        result = bool(test_input)
        assert result == expected

@pytest.fixture
def basic_fixture():
    \"\"\"Basic fixture for testing.\"\"\"
    return {{"test": "data"}}

@pytest.fixture
def mock_environment():
    \"\"\"Mock environment for testing.\"\"\"
    with mock.patch.dict('os.environ', {{'TEST_MODE': 'true'}}):
        yield
"""
    
    def _create_test_suite_structure(self, test_structure: Dict[str, Any], original_code: str) -> Dict[str, str]:
        """Create the complete test suite structure with embedded original code."""
        test_suite = {}
        
        # Add original code to each test file
        for filename, content in test_structure["test_files"].items():
            if filename.endswith('.py'):
                # Clean up the content first
                cleaned_content = self._clean_test_content(content, original_code)
                
                # Validate the cleaned content is syntactically correct
                try:
                    ast.parse(cleaned_content)
                except SyntaxError as e:
                    # If still has syntax errors, create a minimal valid test
                    cleaned_content = self._create_minimal_valid_test(original_code)
                
                # Clean the original code to remove external imports before embedding
                cleaned_original_code = self._clean_original_code_for_tests(original_code)
                
                # Embed original code at the top of test files
                embedded_content = f"""# Original code being tested:
{cleaned_original_code}

# Generated tests:
{cleaned_content}
"""
                test_suite[filename] = embedded_content
            else:
                test_suite[filename] = content
        
        # Add configuration files
        if test_structure.get("pytest_config"):
            test_suite["pytest.ini"] = test_structure["pytest_config"]
        
        if test_structure.get("requirements_dev"):
            test_suite["requirements-dev.txt"] = test_structure["requirements_dev"]
        
        if test_structure.get("test_plan"):
            test_suite["tests/TEST_PLAN.md"] = test_structure["test_plan"]
        
        return test_suite
    
    def _save_test_suite(self, test_suite: Dict[str, str], code_analysis: Dict[str, Any], language: str) -> Dict[str, str]:
        """Save the complete test suite to files."""
        saved_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create tests directory
        tests_dir = os.path.join(self.test_output_dir, f"test_suite_{timestamp}")
        os.makedirs(tests_dir, exist_ok=True)
        
        for filename, content in test_suite.items():
            # Determine the full path
            if filename.startswith('tests/'):
                # Create nested directory structure
                full_path = os.path.join(self.test_output_dir, f"test_suite_{timestamp}", filename)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
            else:
                full_path = os.path.join(self.test_output_dir, f"test_suite_{timestamp}", filename)
            
            # Save the file
            with open(full_path, 'w') as f:
                f.write(content)
            
            saved_files[filename] = full_path
        
        # Set main test file
        main_test_files = [f for f in saved_files.keys() if f.startswith('tests/test_')]
        if main_test_files:
            saved_files["main_test_file"] = saved_files[main_test_files[0]]
        else:
            saved_files["main_test_file"] = list(saved_files.values())[0]
        
        return saved_files
    
    def _run_comprehensive_tests(self, test_files: Dict[str, str], language: str) -> Dict[str, Any]:
        """Run the comprehensive test suite with coverage using Docker for isolation."""
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "coverage": 0.0,
            "output": "",
            "error": None,
            "test_files": test_files,
            "execution_method": "docker"
        }
        
        try:
            if language.lower() == "python":
                # Find the test directory
                test_dir = os.path.dirname(test_files.get("main_test_file", ""))
                if not test_dir:
                    results["error"] = "No test directory found"
                    return results
                
                # Try Docker first, then fallback to local execution
                docker_result = self._run_tests_in_docker(test_dir, test_files)
                if docker_result["success"]:
                    return docker_result
                else:
                    # Fallback to local execution
                    results["execution_method"] = "local"
                    return self._run_tests_locally(test_dir, language)
                        
        except Exception as e:
            results["error"] = f"Error running comprehensive tests: {e}"
        
        return results
    
    def _run_tests_in_docker(self, test_dir: str, test_files: Dict[str, str]) -> Dict[str, Any]:
        """Run tests in a Docker container for isolation."""
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "coverage": 0.0,
            "output": "",
            "error": None,
            "execution_method": "docker",
            "success": False
        }
        
        try:
            # Create a Dockerfile for the test environment
            dockerfile_content = self._create_test_dockerfile(test_files)
            dockerfile_path = os.path.join(test_dir, "Dockerfile")
            
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            
            # Create docker-compose.yml for easier management
            compose_content = self._create_docker_compose(test_dir)
            compose_path = os.path.join(test_dir, "docker-compose.yml")
            
            with open(compose_path, 'w') as f:
                f.write(compose_content)
            
            # Build and run the Docker container
            container_name = f"test_suite_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Build the image
            build_cmd = [
                "docker", "build", 
                "-t", container_name,
                "-f", dockerfile_path,
                test_dir
            ]
            
            build_result = subprocess.run(
                build_cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if build_result.returncode != 0:
                results["error"] = f"Docker build failed: {build_result.stderr}"
                return results
            
            # Run the tests in the container
            run_cmd = [
                "docker", "run", 
                "--rm",
                "--name", container_name,
                container_name
            ]
            
            run_result = subprocess.run(
                run_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for comprehensive tests
            )
            
            results["output"] = run_result.stdout + run_result.stderr
            
            # Parse test results
            if run_result.stdout:
                # Count test functions
                test_lines = [line for line in run_result.stdout.split('\n') if '::test_' in line]
                results["tests_run"] = len(test_lines)
                
                # Count passed tests
                passed_lines = [line for line in run_result.stdout.split('\n') if 'PASSED' in line]
                results["tests_passed"] = len(passed_lines)
                
                # Count failed tests
                failed_lines = [line for line in run_result.stdout.split('\n') if 'FAILED' in line]
                results["tests_failed"] = len(failed_lines)
                
                # Extract coverage
                coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', run_result.stdout)
                if coverage_match:
                    results["coverage"] = float(coverage_match.group(1))
            
            if run_result.returncode != 0:
                if results["tests_run"] == 0:
                    results["error"] = f"Test execution failed in Docker: {run_result.stderr}"
                else:
                    results["error"] = f"Some tests failed in Docker (return code: {run_result.returncode})"
            
            results["success"] = True
            
            # Clean up the Docker image
            try:
                subprocess.run(["docker", "rmi", container_name], capture_output=True, timeout=30)
            except:
                pass  # Ignore cleanup errors
                
        except subprocess.TimeoutExpired:
            results["error"] = "Docker test execution timed out (5 minutes)"
        except Exception as e:
            results["error"] = f"Error running tests in Docker: {e}"
        
        return results
    
    def _run_tests_locally(self, test_dir: str, language: str) -> Dict[str, Any]:
        """Fallback to local test execution."""
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "coverage": 0.0,
            "output": "",
            "error": None,
            "execution_method": "local"
        }
        
        try:
            # Try different Python commands, prioritizing virtual environment
            python_commands = []
            
            # Check for virtual environment first
            venv_python = os.path.join(os.getcwd(), "venv", "bin", "python")
            if os.path.exists(venv_python):
                python_commands.append(venv_python)
            
            # Add system Python commands
            python_commands.extend(["python3", "python", "py"])
            
            cmd = None
            
            for python_cmd in python_commands:
                try:
                    # Test if command exists and can import pytest
                    test_cmd = [python_cmd, "-c", "import pytest; print('pytest available')"]
                    result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        # Run pytest with coverage
                        cmd = [
                            python_cmd, "-m", "pytest", 
                            test_dir, 
                            "-v", 
                            "--tb=short",
                            "--cov=.",
                            "--cov-report=term-missing",
                            "--cov-fail-under=85"
                        ]
                        break
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            if not cmd:
                results["error"] = "No Python interpreter with pytest found. Please install pytest: pip install pytest"
                return results
            
            # Run pytest
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minutes for local tests
                cwd=test_dir
            )
            
            results["output"] = process.stdout + process.stderr
            
            # Parse test results
            if process.stdout:
                # Count test functions
                test_lines = [line for line in process.stdout.split('\n') if '::test_' in line]
                results["tests_run"] = len(test_lines)
                
                # Count passed tests
                passed_lines = [line for line in process.stdout.split('\n') if 'PASSED' in line]
                results["tests_passed"] = len(passed_lines)
                
                # Count failed tests
                failed_lines = [line for line in process.stdout.split('\n') if 'FAILED' in line]
                results["tests_failed"] = len(failed_lines)
                
                # Extract coverage
                coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', process.stdout)
                if coverage_match:
                    results["coverage"] = float(coverage_match.group(1))
            
            if process.returncode != 0:
                if results["tests_run"] == 0:
                    results["error"] = f"Test execution failed: {process.stderr}"
                else:
                    results["error"] = f"Some tests failed (return code: {process.returncode})"
                    
        except subprocess.TimeoutExpired:
            results["error"] = "Local test execution timed out (2 minutes)"
        except Exception as e:
            results["error"] = f"Error running local tests: {e}"
        
        return results
    
    def _create_test_dockerfile(self, test_files: Dict[str, str]) -> str:
        """Create a Dockerfile for running tests in isolation."""
        return """# Test environment Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy test files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run tests with coverage
CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "--cov=.", "--cov-report=term-missing", "--cov-fail-under=85"]
"""
    
    def _create_docker_compose(self, test_dir: str) -> str:
        """Create docker-compose.yml for test execution."""
        return """version: '3.8'

services:
  test-runner:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
    command: python -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing --cov-fail-under=85
"""
    
    def _format_code(self, code: str, language: str) -> str:
        """Format code using appropriate formatter."""
        try:
            if language.lower() == "python":
                # Use black for Python formatting
                mode = black.FileMode()
                formatted_code = black.format_str(code, mode=mode)
                return formatted_code
            else:
                return code
        except Exception as e:
            logging.warning(f"Code formatting failed: {e}")
            return code
    
    def _validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate generated code."""
        validation_result = {
            "syntax_valid": False,
            "errors": [],
            "warnings": []
        }
        
        try:
            if language.lower() == "python":
                # Check Python syntax
                ast.parse(code)
                validation_result["syntax_valid"] = True
                
        except SyntaxError as e:
            validation_result["errors"].append(f"Syntax error: {e}")
        except Exception as e:
            validation_result["errors"].append(f"Validation error: {e}")
        
        return validation_result
    
    def _validate_tests(self, test_code: str, language: str) -> Dict[str, Any]:
        """Validate generated test code."""
        validation_result = {
            "syntax_valid": False,
            "errors": [],
            "warnings": []
        }
        
        try:
            if language.lower() == "python":
                # Check Python syntax
                ast.parse(test_code)
                validation_result["syntax_valid"] = True
                
                # Check for test-specific patterns
                if "def test_" not in test_code:
                    validation_result["warnings"].append("No test functions found")
                
                if "assert" not in test_code:
                    validation_result["warnings"].append("No assertions found in tests")
                
        except SyntaxError as e:
            validation_result["errors"].append(f"Test syntax error: {e}")
        except Exception as e:
            validation_result["errors"].append(f"Test validation error: {e}")
        
        return validation_result
    
    def _run_tests(self, test_file_path: str, language: str) -> Dict[str, Any]:
        """Run tests and collect results."""
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "coverage": 0.0,
            "output": "",
            "error": None
        }
        
        try:
            if language.lower() == "python":
                # Try different Python commands, prioritizing virtual environment
                python_commands = []
                
                # Check for virtual environment first
                venv_python = os.path.join(os.getcwd(), "venv", "bin", "python")
                if os.path.exists(venv_python):
                    python_commands.append(venv_python)
                
                # Add system Python commands
                python_commands.extend(["python3", "python", "py"])
                
                cmd = None
                
                for python_cmd in python_commands:
                    try:
                        # Test if command exists and can import pytest
                        test_cmd = [python_cmd, "-c", "import pytest; print('pytest available')"]
                        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            cmd = [python_cmd, "-m", "pytest", test_file_path, "-v", "--tb=short"]
                            break
                    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                        continue
                
                if not cmd:
                    results["error"] = "No Python interpreter with pytest found. Please install pytest: pip install pytest"
                    return results
                
                # Run pytest
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60  # Increased timeout for test execution
                )
                
                results["output"] = process.stdout + process.stderr
                
                # Parse test results more robustly
                if process.stdout:
                    # Count test functions
                    test_lines = [line for line in process.stdout.split('\n') if '::test_' in line]
                    results["tests_run"] = len(test_lines)
                    
                    # Count passed tests
                    passed_lines = [line for line in process.stdout.split('\n') if 'PASSED' in line]
                    results["tests_passed"] = len(passed_lines)
                    
                    # Count failed tests
                    failed_lines = [line for line in process.stdout.split('\n') if 'FAILED' in line]
                    results["tests_failed"] = len(failed_lines)
                    
                    # Calculate coverage if available
                    if "TOTAL" in process.stdout and "%" in process.stdout:
                        try:
                            coverage_line = [line for line in process.stdout.split('\n') if "TOTAL" in line and "%" in line][0]
                            coverage_match = re.search(r'(\d+)%', coverage_line)
                            if coverage_match:
                                results["coverage"] = float(coverage_match.group(1))
                        except (IndexError, ValueError):
                            pass
                
                if process.returncode != 0:
                    if results["tests_run"] == 0:
                        # Check for specific import errors
                        if "ModuleNotFoundError" in process.stderr:
                            missing_module = re.search(r"No module named '([^']+)'", process.stderr)
                            if missing_module:
                                module_name = missing_module.group(1)
                                results["error"] = f"Test execution failed: Missing module '{module_name}'. The generated tests require dependencies that aren't available. This is expected for code with external dependencies."
                            else:
                                results["error"] = f"Test execution failed: Import error - {process.stderr}"
                        elif "ImportError" in process.stderr:
                            results["error"] = f"Test execution failed: Import error - {process.stderr}"
                        else:
                            results["error"] = f"Test execution failed: {process.stderr}"
                    else:
                        results["error"] = f"Some tests failed (return code: {process.returncode})"
                        
        except subprocess.TimeoutExpired:
            results["error"] = "Test execution timed out (60 seconds)"
        except Exception as e:
            results["error"] = f"Error running tests: {e}"
        
        return results
    
    def _save_code(self, code: str, requirement: str, language: str) -> str:
        """Save generated code to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_requirement = self._sanitize_filename(requirement)
        
        # Use correct file extension
        if language.lower() == "python":
            extension = "py"
        else:
            extension = language
        
        filename = f"{sanitized_requirement}_{timestamp}.{extension}"
        file_path = os.path.join(self.code_output_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(code)
        
        return file_path
    
    def _save_tests(self, test_code: str, code_analysis: Dict[str, Any], language: str) -> str:
        """Save generated tests to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Use correct file extension
        if language.lower() == "python":
            extension = "py"
        else:
            extension = language
        
        filename = f"test_generated_{timestamp}.{extension}"
        file_path = os.path.join(self.test_output_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(test_code)
        
        return file_path
    
    def _sanitize_filename(self, requirement: str) -> str:
        """Sanitize requirement text for filename."""
        # Remove special characters and replace spaces with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', requirement)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized[:50]  # Limit length
