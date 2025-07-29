"""
AI Engine for handling multiple AI models (OpenAI and Gemini).
"""

import os
import logging
from typing import Dict, Any, Optional, List
import openai
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AIEngine:
    """Handles AI model interactions for code generation and analysis."""
    
    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        self.default_model = os.getenv('DEFAULT_MODEL', 'gpt-4')
        self.fallback_model = os.getenv('FALLBACK_MODEL', 'gemini-pro')
        self.max_tokens = int(os.getenv('MAX_TOKENS', 4000))
        self.temperature = float(os.getenv('TEMPERATURE', 0.7))
        
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
            
            raise Exception("No AI models available")
            
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"
    
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
        response = self.openai_client.chat.completions.create(
            model=self.default_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return self._parse_response(response.choices[0].message.content)
    
    def _generate_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """Generate response using Gemini."""
        response = self.gemini_model.generate_content(prompt)
        return self._parse_response(response.text)
    
    def _fallback_generation(self, prompt: str) -> Dict[str, Any]:
        """Fallback generation when primary model fails."""
        return {
            "error": "AI model unavailable",
            "fallback_response": "Please check your API keys and try again."
        }
    
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