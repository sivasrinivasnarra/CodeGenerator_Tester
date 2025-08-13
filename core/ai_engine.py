"""
Integrated AI Engine for handling multiple AI models (OpenAI and Gemini) with template fallback.
"""

import os
import logging
from typing import Dict, Any, Optional, List
import openai
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import re

load_dotenv()

class AIEngine:
    """Handles AI model interactions for code generation and analysis with template fallback."""
    
    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        self.default_model = os.getenv('DEFAULT_MODEL', 'gpt-4')
        self.fallback_model = os.getenv('FALLBACK_MODEL', 'gemini-pro')
        self.max_tokens = int(os.getenv('MAX_TOKENS', 4000))
        self.temperature = float(os.getenv('TEMPERATURE', 0.7))
        
        # Template management
        self.template_dir = Path("templates")
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        self._ensure_template_dir()
        
        self._setup_models()
    
    def _setup_models(self):
        """Initialize AI models."""
        # Setup OpenAI
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            openai.api_key = openai_api_key
            self.openai_client = openai.OpenAI()
        
        # Setup Gemini
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if google_api_key:
            genai.configure(api_key=google_api_key)
            # Try different Gemini models
            try:
                self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
            except Exception:
                try:
                    self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                except Exception:
                    try:
                        self.gemini_model = genai.GenerativeModel('gemini-pro')
                    except Exception as e:
                        logging.warning(f"Could not initialize Gemini model: {e}")
                        self.gemini_model = None
    
    def generate_code(self, requirement: str, language: str = "python") -> Dict[str, Any]:
        """Generate code based on requirement description."""
        prompt = self._create_code_prompt(requirement, language)
        
        try:
            if self.default_model.startswith('gpt') and self.openai_client:
                return self._generate_with_openai(prompt)
            elif self.gemini_model:
                return self._generate_with_gemini(prompt)
            else:
                raise Exception("No AI models available")
        except Exception as e:
            logging.error(f"Error generating code: {e}")
            return self._fallback_generation(prompt)
    
    def generate_tests(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Generate test cases for the given code."""
        prompt = self._create_test_prompt(code, language)
        
        try:
            if self.default_model.startswith('gpt') and self.openai_client:
                return self._generate_with_openai(prompt)
            elif self.gemini_model:
                return self._generate_with_gemini(prompt)
            else:
                raise Exception("No AI models available")
        except Exception as e:
            logging.error(f"Error generating tests: {e}")
            return self._fallback_generation(prompt)
    
    def analyze_deployment_readiness(self, code: str, tests: str) -> Dict[str, Any]:
        """Analyze if the code is ready for deployment."""
        prompt = self._create_deployment_prompt(code, tests)
        
        try:
            if self.default_model.startswith('gpt') and self.openai_client:
                return self._generate_with_openai(prompt)
            elif self.gemini_model:
                return self._generate_with_gemini(prompt)
            else:
                raise Exception("No AI models available")
        except Exception as e:
            logging.error(f"Error analyzing deployment: {e}")
            return self._fallback_generation(prompt)
    
    def generate_response(self, prompt: str, model: str = None) -> str:
        """Generate a general response using the specified or default model."""
        try:
            if not prompt or not prompt.strip():
                raise ValueError("Prompt cannot be empty")
            
            model_to_use = model if model else self.default_model
            
            # Try OpenAI first if specified or as default
            if (model and model.startswith('gpt')) or (not model and self.default_model.startswith('gpt')):
                if self.openai_client:
                    model_to_use = model if model and model.startswith('gpt') else self.default_model
                    response = self.openai_client.chat.completions.create(
                        model=model_to_use,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=self.max_tokens,
                        temperature=self.temperature
                    )
                    return response.choices[0].message.content
                else:
                    logging.warning("OpenAI client not available, trying Gemini")
            
            # Try Gemini if specified or as fallback
            if (model and 'gemini' in model.lower()) or (not model and self.gemini_model):
                if self.gemini_model:
                    response = self.gemini_model.generate_content(prompt)
                    return response.text
                else:
                    logging.warning("Gemini model not available")
            
            # If no specific model requested, try default
            if self.default_model.startswith('gpt') and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=self.default_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                return response.choices[0].message.content
            elif self.gemini_model:
                response = self.gemini_model.generate_content(prompt)
                return response.text
            
            raise Exception("No AI models available. Please check your API keys in the environment configuration.")
            
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            raise
    
    def _create_code_prompt(self, requirement: str, language: str) -> str:
        """Create prompt for code generation."""
        return f"""
        Generate production-ready {language} code based on the following requirement:
        
        Requirement: {requirement}
        
        Please provide:
        1. Complete implementation with proper error handling
        2. Input validation and sanitization
        3. Logging and documentation
        4. Best practices and clean code principles
        5. Type hints (if applicable)
        6. Configuration management
        
        Return the response in JSON format:
        {{
            "code": "the generated code",
            "description": "brief description of what the code does",
            "dependencies": ["list of required packages"],
            "complexity": "low/medium/high",
            "estimated_time": "estimated development time"
        }}
        """
    
    def _create_test_prompt(self, code: str, language: str) -> str:
        """Create prompt for test generation."""
        return f"""
        Generate comprehensive test cases for the following {language} code:
        
        Code:
        {code}
        
        Please provide:
        1. Unit tests for all functions/methods
        2. Edge cases and error scenarios
        3. Integration tests if applicable
        4. Test data and fixtures
        5. Mock objects where needed
        
        Return the response in JSON format:
        {{
            "test_code": "the generated test code",
            "test_cases": ["list of test case descriptions"],
            "coverage_areas": ["areas covered by tests"],
            "test_framework": "pytest/unittest",
            "estimated_coverage": "percentage"
        }}
        """
    
    def _create_deployment_prompt(self, code: str, tests: str) -> str:
        """Create prompt for deployment analysis."""
        return f"""
        Analyze the deployment readiness of the following code and tests:
        
        Code:
        {code}
        
        Tests:
        {tests}
        
        Please assess:
        1. Code quality and best practices
        2. Test coverage and reliability
        3. Security considerations
        4. Performance implications
        5. Dependencies and compatibility
        6. Documentation completeness
        
        Return the response in JSON format:
        {{
            "ready_for_deployment": true/false,
            "score": "0-100",
            "issues": ["list of issues to fix"],
            "recommendations": ["list of improvements"],
            "security_score": "0-100",
            "performance_score": "0-100",
            "test_coverage_score": "0-100"
        }}
        """
    
    def _generate_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Generate response using OpenAI."""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized. Please check your OPENAI_API_KEY.")
        
        response = self.openai_client.chat.completions.create(
            model=self.default_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return self._parse_response(response.choices[0].message.content)
    
    def _generate_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """Generate response using Gemini."""
        if not self.gemini_model:
            raise Exception("Gemini model not initialized. Please check your GOOGLE_API_KEY.")
        
        response = self.gemini_model.generate_content(prompt)
        return self._parse_response(response.text)
    
    def _fallback_generation(self, prompt: str) -> Dict[str, Any]:
        """Fallback to template-based generation when AI models fail."""
        try:
            # Extract requirement from prompt
            requirement = self._extract_requirement_from_prompt(prompt)
            
            # Generate code using template
            code = self.render_code_template(requirement)
            
            return {
                "success": True,
                "code": code,
                "source": "template_fallback",
                "warning": "AI models unavailable, using template-based generation"
            }
        except Exception as e:
            logging.error(f"Template fallback failed: {e}")
            return {
                "success": False,
                "error": f"Both AI models and template fallback failed: {str(e)}"
            }
    
    # Template Management Methods (integrated from TemplateManager)
    
    def _ensure_template_dir(self):
        """Ensure template directory exists."""
        self.template_dir.mkdir(exist_ok=True)
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context."""
        try:
            if not context:
                context = {}
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logging.error(f"Error rendering template {template_name}: {e}")
            return f"# Error rendering template: {e}"
    
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
                           dependencies: List[str] = None, name: str = None) -> str:
        """Render a code template for the given requirement."""
        # Generate class name from requirement
        class_name = self._generate_class_name(requirement)
        
        context = {
            "requirement": requirement,
            "language": language,
            "class_name": class_name,
            "name": name or "main",
            "timestamp": datetime.now().isoformat(),
            "dependencies": dependencies or []
        }
        
        if language.lower() == "python":
            return self.render_template("python_template.py.jinja", context)
        else:
            return f"# {language} code for: {requirement}\n# Implementation needed based on requirement"
    
    def render_test_template(self, requirement: str, language: str = "python",
                           dependencies: List[str] = None) -> str:
        """Render a test template for the given requirement."""
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
            return f"# {language} tests for: {requirement}\n# Test cases needed based on requirement"
    
    def render_requirements_template(self, requirement: str, 
                                   dependencies: List[str] = None) -> str:
        """Render a requirements template."""
        if not dependencies:
            dependencies = []
        
        context = {
            "requirement": requirement,
            "dependencies": dependencies,
            "timestamp": datetime.now().isoformat()
        }
        
        return self.render_template("requirements_template.txt.jinja", context)
    
    def _generate_class_name(self, requirement: str) -> str:
        """Generate a class name from requirement text."""
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
    
    def _extract_requirement_from_prompt(self, prompt: str) -> str:
        """Extract requirement description from AI prompt."""
        # Simple extraction - look for common patterns
        lines = prompt.split('\n')
        for line in lines:
            if 'requirement' in line.lower() or 'create' in line.lower() or 'generate' in line.lower():
                return line.strip()
        
        # Fallback to first meaningful line
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                return line.strip()[:100]  # Limit length
        
        return "Default requirement"
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and extract JSON."""
        try:
            import json
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {"raw_response": response}
        except Exception as e:
            logging.error(f"Error parsing response: {e}")
            return {"raw_response": response, "parse_error": str(e)}    