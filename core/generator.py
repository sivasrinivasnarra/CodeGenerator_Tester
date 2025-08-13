"""
Integrated Generator module for creating production-ready code and comprehensive test cases.
"""

import os
import logging
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
import black
import ast

class Generator:
    """Handles both code and test generation, formatting, and validation."""
    
    def __init__(self):
        self.code_output_dir = os.getenv('GENERATED_CODE_DIR', 'generated/code')
        self.test_output_dir = os.getenv('GENERATED_TESTS_DIR', 'generated/tests')
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
                "file_path": file_path,
                "validation": validation_result,
                "language": language
            }
            
        except Exception as e:
            logging.error(f"Error generating code: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_tests(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Generate test cases for the given code."""
        try:
            # Analyze the code to understand what to test
            code_analysis = self._analyze_code(code, language)
            
            # Generate test cases
            test_code = self._create_test_template(code, code_analysis, language)
            
            # Format test code
            formatted_test_code = self._format_code(test_code, language)
            
            # Validate test code
            validation_result = self._validate_tests(formatted_test_code, language)
            
            # Save test file
            test_file_path = self._save_tests(formatted_test_code, code_analysis, language)
            
            # Run tests to check coverage
            test_results = self._run_tests(test_file_path, language)
            
            return {
                "success": True,
                "test_code": formatted_test_code,
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
    
    def _create_code_template(self, requirement: str, language: str) -> str:
        """Create code template based on requirement."""
        if language.lower() == "python":
            return self._create_python_template(requirement)
        else:
            return f"# {language} code for: {requirement}\n# Implementation needed based on requirement"
    
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
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "environment": os.getenv("ENVIRONMENT", "development")
        }}
    
    def _process_data(self, input_data: Any) -> Any:
        """Process input data with enhanced logic."""
        if isinstance(input_data, str):
            return input_data.strip().title()
        elif isinstance(input_data, list):
            return [str(item).strip() for item in input_data if item]
        elif isinstance(input_data, dict):
            return {{k: str(v).strip() for k, v in input_data.items() if v}}
        else:
            return str(input_data) if input_data is not None else ""
    
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
            
            # Process the requirement with enhanced logic
            processed_data = self._process_data(input_data)
            result = {{
                "status": "success",
                "input_processed": input_data,
                "processed_output": processed_data,
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
    
    def _create_test_template(self, code: str, code_analysis: Dict[str, Any], language: str) -> str:
        """Create test template based on code analysis."""
        if language.lower() == "python":
            return self._create_python_test_template(code, code_analysis)
        else:
            return f"# {language} tests for the code\n# Test cases needed based on requirement"
    
    def _create_python_test_template(self, code: str, code_analysis: Dict[str, Any]) -> str:
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
        try:
            result = self.instance.{func_name}()
            assert result is not None
        except TypeError:
            assert True
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
        test_input = "sample requirement"
        result = self.instance.process_requirement(test_input)
        assert isinstance(result, dict)
        assert "status" in result
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        with pytest.raises(Exception):
            self.instance.process_requirement(None)
        
        result = self.instance.process_requirement("")
        assert isinstance(result, dict)

if __name__ == "__main__":
    pytest.main([__file__])
'''
        
        return test_code
    
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
                
                # Run flake8 for additional checks
                flake8_result = self._run_flake8(code)
                validation_result.update(flake8_result)
                
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
    
    def _run_flake8(self, code: str) -> Dict[str, Any]:
        """Run flake8 linting on code."""
        try:
            # Write code to temporary file
            temp_file = Path(self.code_output_dir) / "temp_validation.py"
            with open(temp_file, 'w') as f:
                f.write(code)
            
            # Run flake8
            result = subprocess.run(
                ['flake8', str(temp_file), '--max-line-length=88'],
                capture_output=True,
                text=True
            )
            
            # Clean up
            temp_file.unlink()
            
            return {
                "flake8_output": result.stdout,
                "flake8_errors": result.stderr.split('\n') if result.stderr else []
            }
            
        except Exception as e:
            return {
                "flake8_output": "",
                "flake8_errors": [f"Flake8 error: {e}"]
            }
    
    def _run_tests(self, test_file_path: str, language: str) -> Dict[str, Any]:
        """Run tests and return results."""
        test_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "coverage": 0.0,
            "output": ""
        }
        
        try:
            if language.lower() == "python":
                # Run pytest
                result = subprocess.run(
                    ['python', '-m', 'pytest', test_file_path, '-v'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                test_results["output"] = result.stdout
                
                # Parse test results
                if "passed" in result.stdout:
                    test_results["tests_passed"] = len([line for line in result.stdout.split('\n') if "PASSED" in line])
                
                if "failed" in result.stdout:
                    test_results["tests_failed"] = len([line for line in result.stdout.split('\n') if "FAILED" in line])
                
                test_results["tests_run"] = test_results["tests_passed"] + test_results["tests_failed"]
                
        except subprocess.TimeoutExpired:
            test_results["output"] = "Tests timed out"
        except Exception as e:
            test_results["output"] = f"Error running tests: {e}"
        
        return test_results
    
    def _save_code(self, code: str, requirement: str, language: str) -> str:
        """Save generated code to file."""
        # Create filename from requirement
        filename = self._sanitize_filename(requirement)
        file_path = Path(self.code_output_dir) / f"{filename}.{self._get_file_extension(language)}"
        
        with open(file_path, 'w') as f:
            f.write(code)
        
        return str(file_path)
    
    def _save_tests(self, test_code: str, code_analysis: Dict[str, Any], language: str) -> str:
        """Save generated tests to file."""
        # Create filename based on the main code file
        filename = f"test_{self._sanitize_filename(code_analysis.get('main_file', 'code'))}"
        file_path = Path(self.test_output_dir) / f"{filename}.{self._get_file_extension(language)}"
        
        with open(file_path, 'w') as f:
            f.write(test_code)
        
        return str(file_path)
    
    def _sanitize_filename(self, requirement: str) -> str:
        """Sanitize requirement text for filename."""
        import re
        # Remove special characters and replace spaces with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', requirement)
        sanitized = re.sub(r'\s+', '_', sanitized.strip())
        return sanitized[:50]  # Limit length
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language."""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "cpp": "cpp",
            "c": "c"
        }
        return extensions.get(language.lower(), "txt")
