"""
Code Generator module for creating production-ready code.
"""

import os
import logging
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
import black
import ast

class CodeGenerator:
    """Handles code generation, formatting, and validation."""
    
    def __init__(self):
        self.output_dir = os.getenv('GENERATED_CODE_DIR', 'generated/code')
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Ensure output directory exists."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_code(self, requirement: str, language: str = "python") -> Dict[str, Any]:
        """Generate code from requirement description."""
        try:
            # This would typically call the AI engine
            # For now, we'll create a template-based approach
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
            # {requirement}
            
            result = {{
                "status": "success",
                "processed_data": input_data,
                "message": "Requirement processed successfully"
            }}
            
            logger.info(f"Processing completed: {{result['status']}}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing requirement: {{e}}")
            return {{
                "status": "error",
                "error": str(e),
                "message": "Failed to process requirement"
            }}
    
    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data.
        
        Args:
            input_data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if input_data is None:
            return False
        
        # Add specific validation logic here
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the implementation."""
        return {{
            "status": "ready",
            "config": self.config,
            "timestamp": "2024-01-01T00:00:00Z"
        }}

def main():
    """Main function to run the implementation."""
    implementation = RequirementImplementation()
    
    # Example usage
    test_data = "test input"
    result = implementation.process_requirement(test_data)
    print(f"Result: {{result}}")

if __name__ == "__main__":
    main()
'''
    
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
    
    def _run_flake8(self, code: str) -> Dict[str, Any]:
        """Run flake8 linting on code."""
        try:
            # Write code to temporary file
            temp_file = Path(self.output_dir) / "temp_validation.py"
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
    
    def _save_code(self, code: str, requirement: str, language: str) -> str:
        """Save generated code to file."""
        # Create filename from requirement
        filename = self._sanitize_filename(requirement)
        file_path = Path(self.output_dir) / f"{filename}.{self._get_file_extension(language)}"
        
        with open(file_path, 'w') as f:
            f.write(code)
        
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