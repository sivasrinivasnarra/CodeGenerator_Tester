"""
Integrated AI Engine for handling multiple AI models (OpenAI and Gemini).
"""

import os
import logging
from typing import Dict, Any, Optional, List
import openai
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import re

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
            try:
                openai.api_key = openai_api_key
                self.openai_client = openai.OpenAI()
                logging.info("OpenAI client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        
        # Setup Gemini
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if google_api_key:
            try:
                genai.configure(api_key=google_api_key)
                # Try the default model first
                default_model = os.getenv('DEFAULT_MODEL', 'gemini-1.5-pro')
                try:
                    self.gemini_model = genai.GenerativeModel(default_model)
                    logging.info(f"Gemini model {default_model} initialized successfully")
                except Exception as e:
                    logging.warning(f"Could not initialize {default_model}, trying fallback models")
                    # Try fallback models
                    fallback_models = ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro']
                    for model in fallback_models:
                        if model != default_model:
                            try:
                                self.gemini_model = genai.GenerativeModel(model)
                                logging.info(f"Gemini model {model} initialized successfully")
                                break
                            except Exception:
                                continue
                    
                    if not self.gemini_model:
                        logging.error("Could not initialize any Gemini model")
            except Exception as e:
                logging.error(f"Failed to configure Gemini: {e}")
                self.gemini_model = None
        
        # Log model availability
        if not self.openai_client and not self.gemini_model:
            logging.warning("No AI models available. Please check your API keys.")
        else:
            available_models = []
            if self.openai_client:
                available_models.append("OpenAI")
            if self.gemini_model:
                available_models.append("Gemini")
            logging.info(f"Available AI models: {', '.join(available_models)}")
    
    def generate_response(self, prompt: str, model: str = None) -> str:
        """Generate response using available AI models."""
        try:
            # Use the specified model or fall back to default
            if model:
                if model.startswith('gpt') and self.openai_client:
                    return self._generate_with_openai(prompt, model)
                elif 'gemini' in model.lower() and self.gemini_model:
                    return self._generate_with_gemini(prompt)
                elif 'claude' in model.lower() and self.openai_client:
                    return self._generate_with_openai(prompt, model)
                elif 'grok' in model.lower() and self.openai_client:
                    return self._generate_with_openai(prompt, model)
            
            # Fall back to default model selection
            if self.default_model.startswith('gpt') and self.openai_client:
                return self._generate_with_openai(prompt, self.default_model)
            elif self.gemini_model:
                return self._generate_with_gemini(prompt)
            else:
                raise Exception("No AI models available")
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return f"Error generating response: {e}"
    
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
            return {"error": str(e)}
    
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
            return {"error": str(e)}
    
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
            logging.error(f"Error analyzing deployment readiness: {e}")
            return {"error": str(e)}
    
    def _generate_with_openai(self, prompt: str, model: str = None) -> str:
        """Generate response using OpenAI."""
        try:
            model_to_use = model or self.default_model
            response = self.openai_client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI generation failed: {e}")
            raise
    
    def _generate_with_gemini(self, prompt: str) -> str:
        """Generate response using Gemini."""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logging.error(f"Gemini generation failed: {e}")
            raise
    
    def _create_code_prompt(self, requirement: str, language: str) -> str:
        """Create prompt for code generation."""
        return f"""
You are a senior software engineer. Generate production-ready {language} code based on the following requirement:

REQUIREMENT:
{requirement}

Please provide:
1. Complete, runnable code
2. Proper error handling
3. Documentation and comments
4. Best practices for {language}

Return only the code without any explanations.
"""
    
    def _create_test_prompt(self, code: str, language: str) -> str:
        """Create prompt for test generation."""
        return f"""
You are a senior software engineer. Generate comprehensive test cases for the following {language} code:

CODE:
{code}

Please provide:
1. Unit tests covering all functions/methods
2. Integration tests where appropriate
3. Edge cases and error conditions
4. Proper test structure and assertions

Return only the test code without any explanations.
"""
    
    def _create_deployment_prompt(self, code: str, tests: str) -> str:
        """Create prompt for deployment readiness analysis."""
        return f"""
You are a senior DevOps engineer. Analyze the following code and tests for deployment readiness:

CODE:
{code}

TESTS:
{tests}

Please provide:
1. Deployment readiness score (0-100)
2. Identified issues and recommendations
3. Security considerations
4. Performance considerations
5. Required infrastructure changes

Return your analysis in a structured format.
""" 