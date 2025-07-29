"""
Template Manager utility for handling code templates.
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader

class TemplateManager:
    """Manages code templates and template rendering."""
    
    def __init__(self):
        self.template_dir = Path("templates")
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        self._ensure_template_dir()
        self._create_default_templates()
    
    def _ensure_template_dir(self):
        """Ensure template directory exists."""
        self.template_dir.mkdir(exist_ok=True)
    
    def _create_default_templates(self):
        """Create default templates if they don't exist."""
        default_templates = {
            "python_template.py.jinja": self._get_python_template(),
            "test_template.py.jinja": self._get_test_template(),
            "requirements_template.txt.jinja": self._get_requirements_template()
        }
        
        for filename, content in default_templates.items():
            template_path = self.template_dir / filename
            if not template_path.exists():
                with open(template_path, 'w') as f:
                    f.write(content)
    
    def _get_python_template(self) -> str:
        """Get default Python code template."""
        return '''"""
Generated Python code for: {{ requirement }}

Generated on: {{ timestamp }}
Language: {{ language }}
"""

import logging
from typing import Any, Dict, List, Optional
import os
from pathlib import Path
{% if dependencies %}
{% for dep in dependencies %}
import {{ dep }}
{% endfor %}
{% endif %}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class {{ class_name }}:
    """
    Implementation for: {{ requirement }}
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the implementation.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._load_default_config()
        logger.info("{{ class_name }} initialized with config: %s", self.config)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            "debug": os.getenv("DEBUG", "False").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "timeout": int(os.getenv("TIMEOUT", "30"))
        }
    
    def process_requirement(self, input_data: Any) -> Dict[str, Any]:
        """
        Process the requirement with input data.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Dict containing processing results
        """
        try:
            logger.info("Processing requirement with input: %s", input_data)
            
            # Validate input
            if not self._validate_input(input_data):
                raise ValueError("Invalid input data")
            
            # TODO: Implement specific logic based on requirement
            # {{ requirement }}
            
            result = {
                "status": "success",
                "processed_data": input_data,
                "message": "Requirement processed successfully",
                "timestamp": "{{ timestamp }}"
            }
            
            logger.info("Processing completed: %s", result["status"])
            return result
            
        except Exception as e:
            logger.error("Error processing requirement: %s", e)
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to process requirement"
            }
    
    def _validate_input(self, input_data: Any) -> bool:
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
        return {
            "status": "ready",
            "config": self.config,
            "timestamp": "{{ timestamp }}"
        }

def main():
    """Main function to run the implementation."""
    implementation = {{ class_name }}()
    
    # Example usage
    test_data = "test input"
    result = implementation.process_requirement(test_data)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
'''
    
    def _get_test_template(self) -> str:
        """Get default test template."""
        return '''"""
Generated test cases for: {{ requirement }}

Generated on: {{ timestamp }}
Language: {{ language }}
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
{% if dependencies %}
{% for dep in dependencies %}
import {{ dep }}
{% endfor %}
{% endif %}

# Import the module to test
# Note: You may need to adjust the import path based on your project structure
# from your_module import {{ class_name }}

class Test{{ class_name }}:
    """Test cases for {{ class_name }} class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Initialize test data
        self.test_data = "test input"
        self.expected_result = {
            "status": "success",
            "processed_data": "test input",
            "message": "Requirement processed successfully"
        }
    
    def test_initialization(self):
        """Test that the class initializes correctly."""
        # TODO: Uncomment when you have the actual implementation
        # implementation = {{ class_name }}()
        # assert implementation is not None
        # assert hasattr(implementation, 'config')
        pass
    
    def test_process_requirement_success(self):
        """Test successful requirement processing."""
        # TODO: Uncomment when you have the actual implementation
        # implementation = {{ class_name }}()
        # result = implementation.process_requirement(self.test_data)
        # assert result["status"] == "success"
        # assert result["processed_data"] == self.test_data
        pass
    
    def test_process_requirement_error(self):
        """Test error handling in requirement processing."""
        # TODO: Uncomment when you have the actual implementation
        # implementation = {{ class_name }}()
        # result = implementation.process_requirement(None)
        # assert result["status"] == "error"
        # assert "error" in result
        pass
    
    def test_validate_input_valid(self):
        """Test input validation with valid data."""
        # TODO: Uncomment when you have the actual implementation
        # implementation = {{ class_name }}()
        # assert implementation.validate_input(self.test_data) is True
        pass
    
    def test_validate_input_invalid(self):
        """Test input validation with invalid data."""
        # TODO: Uncomment when you have the actual implementation
        # implementation = {{ class_name }}()
        # assert implementation.validate_input(None) is False
        pass
    
    def test_get_status(self):
        """Test status retrieval."""
        # TODO: Uncomment when you have the actual implementation
        # implementation = {{ class_name }}()
        # status = implementation.get_status()
        # assert status["status"] == "ready"
        # assert "config" in status
        # assert "timestamp" in status
        pass

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
    return {
        "text": "sample text",
        "number": 42,
        "list": [1, 2, 3, 4, 5],
        "dict": {"key": "value"}
    }

@pytest.fixture
def mock_config():
    """Provide mock configuration for tests."""
    return {
        "debug": True,
        "log_level": "DEBUG"
    }

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
    
    def _get_requirements_template(self) -> str:
        """Get default requirements template."""
        return '''# Requirements for: {{ requirement }}

# Core dependencies
{% for dep in dependencies %}
{{ dep }}
{% endfor %}

# Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0

# Optional dependencies
# requests>=2.28.0
# pandas>=1.5.0
# numpy>=1.24.0
'''
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context."""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            return f"Error rendering template {template_name}: {e}"
    
    def get_available_templates(self) -> List[str]:
        """Get list of available templates."""
        return [f.name for f in self.template_dir.glob("*") if f.is_file()]
    
    def create_custom_template(self, name: str, content: str) -> bool:
        """Create a custom template."""
        try:
            template_path = self.template_dir / name
            with open(template_path, 'w') as f:
                f.write(content)
            return True
        except Exception:
            return False
    
    def get_template_content(self, template_name: str) -> str:
        """Get the content of a template."""
        try:
            template_path = self.template_dir / template_name
            with open(template_path, 'r') as f:
                return f.read()
        except Exception:
            return f"Template {template_name} not found"
    
    def render_code_template(self, requirement: str, language: str = "python", 
                           dependencies: List[str] = None) -> str:
        """Render a code template for the given requirement."""
        from datetime import datetime
        
        # Generate class name from requirement
        class_name = self._generate_class_name(requirement)
        
        context = {
            "requirement": requirement,
            "language": language,
            "class_name": class_name,
            "timestamp": datetime.now().isoformat(),
            "dependencies": dependencies or []
        }
        
        if language.lower() == "python":
            return self.render_template("python_template.py.jinja", context)
        else:
            return f"# {language} code for: {requirement}\n# TODO: Implement based on requirement"
    
    def render_test_template(self, requirement: str, language: str = "python",
                           dependencies: List[str] = None) -> str:
        """Render a test template for the given requirement."""
        from datetime import datetime
        
        # Generate class name from requirement
        class_name = self._generate_class_name(requirement)
        
        context = {
            "requirement": requirement,
            "language": language,
            "class_name": class_name,
            "timestamp": datetime.now().isoformat(),
            "dependencies": dependencies or []
        }
        
        if language.lower() == "python":
            return self.render_template("test_template.py.jinja", context)
        else:
            return f"# {language} tests for: {requirement}\n# TODO: Implement test cases"
    
    def render_requirements_template(self, requirement: str, 
                                   dependencies: List[str] = None) -> str:
        """Render a requirements template."""
        context = {
            "requirement": requirement,
            "dependencies": dependencies or []
        }
        
        return self.render_template("requirements_template.txt.jinja", context)
    
    def _generate_class_name(self, requirement: str) -> str:
        """Generate a class name from requirement text."""
        import re
        
        # Clean the requirement text
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', requirement)
        words = clean_text.split()
        
        if not words:
            return "RequirementImplementation"
        
        # Capitalize first letter of each word and join
        class_name = ''.join(word.capitalize() for word in words[:3])  # Limit to 3 words
        
        # Ensure it starts with a letter
        if not class_name[0].isalpha():
            class_name = "Requirement" + class_name
        
        return class_name + "Implementation" 