"""
Test Generator module for creating comprehensive test cases.
"""

import os
import logging
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
import ast

class TestGenerator:
    """Handles test case generation and validation."""
    
    def __init__(self):
        self.output_dir = os.getenv('GENERATED_TESTS_DIR', 'generated/tests')
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Ensure output directory exists."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_tests(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Generate test cases for the given code."""
        try:
            # Analyze the code to understand what to test
            code_analysis = self._analyze_code(code, language)
            
            # Generate test cases
            test_code = self._create_test_template(code, code_analysis, language)
            
            # Validate test code
            validation_result = self._validate_tests(test_code, language)
            
            # Save test file
            test_file_path = self._save_tests(test_code, code_analysis, language)
            
            # Run tests to check coverage
            test_results = self._run_tests(test_file_path, language)
            
            return {
                "success": True,
                "test_code": test_code,
                "test_file_path": test_file_path,
                "code_analysis": code_analysis,
                "validation": validation_result,
                "test_results": test_results,
                "language": language
            }
            
        except Exception as e:
            logging.error(f"Error generating tests: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code to understand structure and generate appropriate tests."""
        analysis = {
            "classes": [],
            "functions": [],
            "imports": [],
            "complexity": "low"
        }
        
        try:
            if language.lower() == "python":
                tree = ast.parse(code)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        analysis["classes"].append({
                            "name": node.name,
                            "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                            "line_count": len(node.body)
                        })
                    elif isinstance(node, ast.FunctionDef):
                        analysis["functions"].append({
                            "name": node.name,
                            "args": [arg.arg for arg in node.args.args],
                            "line_count": len(node.body) if node.body else 0
                        })
                    elif isinstance(node, ast.Import):
                        analysis["imports"].extend([alias.name for alias in node.names])
                    elif isinstance(node, ast.ImportFrom):
                        analysis["imports"].append(f"{node.module}.{', '.join([alias.name for alias in node.names])}")
                
                # Determine complexity
                total_lines = len(code.split('\n'))
                if total_lines > 100:
                    analysis["complexity"] = "high"
                elif total_lines > 50:
                    analysis["complexity"] = "medium"
                    
        except Exception as e:
            logging.warning(f"Code analysis failed: {e}")
        
        return analysis
    
    def _create_test_template(self, code: str, analysis: Dict[str, Any], language: str) -> str:
        """Create test template based on code analysis."""
        if language.lower() == "python":
            return self._create_pytest_template(code, analysis)
        else:
            return f"# {language} tests for the generated code\n# TODO: Implement test cases"
    
    def _create_pytest_template(self, code: str, analysis: Dict[str, Any]) -> str:
        """Create pytest template."""
        imports = analysis.get("imports", [])
        classes = analysis.get("classes", [])
        functions = analysis.get("functions", [])
        
        # Add necessary imports for testing
        test_imports = [
            "import pytest",
            "from unittest.mock import Mock, patch, MagicMock",
            "import sys",
            "import os"
        ]
        
        # Add imports from the original code
        for imp in imports:
            if "logging" in imp:
                test_imports.append("import logging")
            if "pathlib" in imp:
                test_imports.append("from pathlib import Path")
        
        test_imports = list(set(test_imports))  # Remove duplicates
        
        # Generate test classes
        test_classes = []
        for cls in classes:
            class_tests = self._generate_class_tests(cls)
            test_classes.append(class_tests)
        
        # Generate function tests
        function_tests = []
        for func in functions:
            if not any(func["name"] in cls["methods"] for cls in classes):
                function_tests.append(self._generate_function_tests(func))
        
        return f'''"""
Generated test cases for the implementation.
"""

{chr(10).join(test_imports)}

# Import the module to test
# Note: You may need to adjust the import path based on your project structure
# from your_module import RequirementImplementation

class TestRequirementImplementation:
    """Test cases for RequirementImplementation class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Initialize test data
        self.test_data = "test input"
        self.expected_result = {{
            "status": "success",
            "processed_data": "test input",
            "message": "Requirement processed successfully"
        }}
    
    def test_initialization(self):
        """Test that the class initializes correctly."""
        # TODO: Uncomment when you have the actual implementation
        # implementation = RequirementImplementation()
        # assert implementation is not None
        # assert hasattr(implementation, 'config')
        pass
    
    def test_process_requirement_success(self):
        """Test successful requirement processing."""
        # TODO: Uncomment when you have the actual implementation
        # implementation = RequirementImplementation()
        # result = implementation.process_requirement(self.test_data)
        # assert result["status"] == "success"
        # assert result["processed_data"] == self.test_data
        pass
    
    def test_process_requirement_error(self):
        """Test error handling in requirement processing."""
        # TODO: Uncomment when you have the actual implementation
        # implementation = RequirementImplementation()
        # result = implementation.process_requirement(None)
        # assert result["status"] == "error"
        # assert "error" in result
        pass
    
    def test_validate_input_valid(self):
        """Test input validation with valid data."""
        # TODO: Uncomment when you have the actual implementation
        # implementation = RequirementImplementation()
        # assert implementation.validate_input(self.test_data) is True
        pass
    
    def test_validate_input_invalid(self):
        """Test input validation with invalid data."""
        # TODO: Uncomment when you have the actual implementation
        # implementation = RequirementImplementation()
        # assert implementation.validate_input(None) is False
        pass
    
    def test_get_status(self):
        """Test status retrieval."""
        # TODO: Uncomment when you have the actual implementation
        # implementation = RequirementImplementation()
        # status = implementation.get_status()
        # assert status["status"] == "ready"
        # assert "config" in status
        # assert "timestamp" in status
        pass

{chr(10).join(function_tests)}

# Integration tests
class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_end_to_end_workflow(self):
        """Test the complete end-to-end workflow."""
        # TODO: Implement integration test
        # This should test the complete flow from input to output
        pass
    
    def test_error_recovery(self):
        """Test error recovery and resilience."""
        # TODO: Implement error recovery test
        # This should test how the system handles and recovers from errors
        pass

# Performance tests
class TestPerformance:
    """Performance tests for the implementation."""
    
    def test_processing_speed(self):
        """Test processing speed with various input sizes."""
        # TODO: Implement performance test
        # This should test processing time with different input sizes
        pass
    
    def test_memory_usage(self):
        """Test memory usage under load."""
        # TODO: Implement memory usage test
        # This should test memory consumption under various loads
        pass

# Fixtures for common test data
@pytest.fixture
def sample_input_data():
    """Provide sample input data for tests."""
    return {{
        "text": "sample text",
        "number": 42,
        "list": [1, 2, 3, 4, 5],
        "dict": {{"key": "value"}}
    }}

@pytest.fixture
def mock_config():
    """Provide mock configuration for tests."""
    return {{
        "debug": True,
        "log_level": "DEBUG"
    }}

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
    
    def _generate_class_tests(self, class_info: Dict[str, Any]) -> str:
        """Generate test methods for a class."""
        class_name = class_info["name"]
        methods = class_info.get("methods", [])
        
        test_methods = []
        for method in methods:
            test_methods.append(f'''
    def test_{method}(self):
        """Test {method} method."""
        # TODO: Implement test for {method} method
        pass
''')
        
        return f'''
class Test{class_name}:
    """Test cases for {class_name} class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # TODO: Initialize {class_name} instance
        pass
    
{chr(10).join(test_methods)}
'''
    
    def _generate_function_tests(self, func_info: Dict[str, Any]) -> str:
        """Generate test methods for a function."""
        func_name = func_info["name"]
        args = func_info.get("args", [])
        
        return f'''
def test_{func_name}():
    """Test {func_name} function."""
    # TODO: Implement test for {func_name} function
    # Args: {', '.join(args)}
    pass

def test_{func_name}_with_invalid_input():
    """Test {func_name} function with invalid input."""
    # TODO: Implement test for {func_name} function with invalid input
    pass
'''
    
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
                
        except SyntaxError as e:
            validation_result["errors"].append(f"Syntax error: {e}")
        except Exception as e:
            validation_result["errors"].append(f"Validation error: {e}")
        
        return validation_result
    
    def _save_tests(self, test_code: str, analysis: Dict[str, Any], language: str) -> str:
        """Save generated tests to file."""
        # Create filename based on analysis
        if analysis.get("classes"):
            main_class = analysis["classes"][0]["name"]
            filename = f"test_{main_class.lower()}"
        else:
            filename = "test_generated_code"
        
        file_path = Path(self.output_dir) / f"{filename}.{self._get_file_extension(language)}"
        
        with open(file_path, 'w') as f:
            f.write(test_code)
        
        return str(file_path)
    
    def _run_tests(self, test_file_path: str, language: str) -> Dict[str, Any]:
        """Run tests to check if they work."""
        try:
            if language.lower() == "python":
                # Run pytest
                result = subprocess.run(
                    ['python', '-m', 'pytest', test_file_path, '--tb=short'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                return {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "tests_passed": result.returncode == 0
                }
            else:
                return {"error": f"Test running not implemented for {language}"}
                
        except subprocess.TimeoutExpired:
            return {"error": "Test execution timed out"}
        except Exception as e:
            return {"error": f"Test execution failed: {e}"}
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for test files."""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "cpp": "cpp",
            "c": "c"
        }
        return extensions.get(language.lower(), "txt") 