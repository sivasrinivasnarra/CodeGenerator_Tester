"""
AI-Powered Development Assistant - Main Streamlit Application
"""

import streamlit as st
import os
import json
import zipfile
from datetime import datetime
import tempfile
import base64
from pathlib import Path
import re
import requests
from dotenv import load_dotenv

# Import core modules
from core import AIEngine, CodeGenerator, TestGenerator, ErrorHandler
from utils.file_manager import FileManager, DockerSandbox
from utils.code_analyzer import CodeAnalyzer
from utils.templates import TemplateManager

# Page configuration
st.set_page_config(
    page_title="AI-Powered Development Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .upload-area {
        border: 2px dashed #ccc;
        border-radius: 0.5rem;
        padding: 2rem;
        text-align: center;
        background-color: #fafafa;
    }
    .tech-stack-card {
        background-color: #e3f2fd;
        border: 1px solid #bbdefb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    body {
        background-color: #f8f9fa;
        font-family: "Segoe UI", sans-serif;
    }
    .stButton>button {
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_files' not in st.session_state:
    st.session_state.generated_files = []
if 'current_requirement' not in st.session_state:
    st.session_state.current_requirement = ""
if 'tech_stack' not in st.session_state:
    st.session_state.tech_stack = None
if 'uploaded_document' not in st.session_state:
    st.session_state.uploaded_document = None
if 'uploaded_project_path' not in st.session_state:
    st.session_state.uploaded_project_path = None
if 'uploaded_project_files' not in st.session_state:
    st.session_state.uploaded_project_files = []
if 'last_healing_input' not in st.session_state:
    st.session_state.last_healing_input = None
if 'last_healing_result' not in st.session_state:
    st.session_state.last_healing_result = None
if 'last_main_file_name' not in st.session_state:
    st.session_state.last_main_file_name = None

# Initialize core components
@st.cache_resource
def initialize_components():
    return {
        'ai_engine': AIEngine(),
        'code_generator': CodeGenerator(),
        'test_generator': TestGenerator(),
        'error_handler': ErrorHandler(),
        'file_manager': FileManager(),
        'code_analyzer': CodeAnalyzer(),
        'template_manager': TemplateManager()
    }

components = initialize_components()

# Helper to log errors and display them
def handle_and_display_error(error: Exception, context: str):
    """Record error via ErrorHandler and display to user."""
    components['error_handler'].handle_error(error, context)
    st.error(f"{context}: {str(error)}")

# Document processing functions
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except ImportError as e:
        handle_and_display_error(e, "extract_text_from_pdf: missing PyPDF2")
        return None
    except Exception as e:
        handle_and_display_error(e, "extract_text_from_pdf")
        return None

def extract_text_from_docx(docx_file):
    """Extract text from Word document"""
    try:
        import docx
        doc = docx.Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except ImportError as e:
        handle_and_display_error(e, "extract_text_from_docx: missing python-docx")
        return None
    except Exception as e:
        handle_and_display_error(e, "extract_text_from_docx")
        return None

def extract_text_from_txt(txt_file):
    """Extract text from text file"""
    try:
        return txt_file.read().decode('utf-8')
    except Exception as e:
        handle_and_display_error(e, "extract_text_from_txt")
        return None

def extract_text_from_md(md_file):
    try:
        return md_file.read().decode('utf-8')
    except Exception as e:
        handle_and_display_error(e, "extract_text_from_md")
        return None

def extract_text_from_csv(csv_file):
    try:
        import pandas as pd
        df = pd.read_csv(csv_file)
        return df.to_string()
    except ImportError as e:
        handle_and_display_error(e, "extract_text_from_csv: missing pandas")
        return None
    except Exception as e:
        handle_and_display_error(e, "extract_text_from_csv")
        return None

def process_uploaded_document(uploaded_file):
    """Process uploaded document and extract text"""
    if uploaded_file is None:
        return None
    
    file_extension = uploaded_file.name.lower().split('.')[-1]
    
    if file_extension == 'pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_extension in ['docx', 'doc']:
        return extract_text_from_docx(uploaded_file)
    elif file_extension == 'txt':
        return extract_text_from_txt(uploaded_file)
    elif file_extension == 'md':
        return extract_text_from_md(uploaded_file)
    elif file_extension == 'csv':
        return extract_text_from_csv(uploaded_file)
    else:
        handle_and_display_error(ValueError("Unsupported file. Supported types: pdf, docx, doc, txt, md, csv"), f"process_uploaded_document: {file_extension}")
        return None

# Helper functions for uploaded projects
def extract_project_zip(uploaded_zip) -> str | None:
    """Extract uploaded project ZIP to a temporary directory."""
    try:
        temp_dir = tempfile.mkdtemp(prefix="uploaded_project_")
        with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        return temp_dir
    except Exception as e:
        handle_and_display_error(e, "extract_project_zip")
        return None

def list_python_files(project_dir: str) -> list[str]:
    """List Python files inside the extracted project."""
    py_files = []
    for root, _, files in os.walk(project_dir):
        for f in files:
            if f.endswith('.py'):
                py_files.append(os.path.join(root, f))
    return py_files

def suggest_tech_stack(requirement_text, ai_engine, model="gpt-4o-mini"):
    """Suggest appropriate tech stack based on requirements"""
    try:
        prompt = f"""
        You are a technical architect. Analyze the following requirement and suggest exactly 3 different technology stack options.

        Requirement: {requirement_text}

        For each tech stack option, provide:
        1. Programming Language (with version)
        2. Framework(s)
        3. Database (if needed)
        4. Additional libraries/dependencies
        5. Development tools
        6. Deployment considerations
        7. Pros and cons
        8. Complexity level (Beginner/Intermediate/Advanced)
        9. Estimated development time
        10. Best use case

        IMPORTANT: Respond with ONLY a valid JSON array. No additional text, no explanations, no markdown formatting.

        [
            {{
                "id": 1,
                "name": "Tech Stack Name",
                "language": "Programming Language",
                "framework": "Main Framework",
                "database": "Database Type",
                "dependencies": ["list", "of", "dependencies"],
                "tools": ["development", "tools"],
                "deployment": "Deployment method",
                "pros": ["pro1", "pro2", "pro3"],
                "cons": ["con1", "con2"],
                "complexity": "Beginner/Intermediate/Advanced",
                "estimated_time": "time estimate",
                "best_use_case": "When to use this stack"
            }},
            {{
                "id": 2,
                "name": "Tech Stack Name 2",
                "language": "Programming Language 2",
                "framework": "Main Framework 2",
                "database": "Database Type 2",
                "dependencies": ["list", "of", "dependencies"],
                "tools": ["development", "tools"],
                "deployment": "Deployment method",
                "pros": ["pro1", "pro2", "pro3"],
                "cons": ["con1", "con2"],
                "complexity": "Beginner/Intermediate/Advanced",
                "estimated_time": "time estimate",
                "best_use_case": "When to use this stack"
            }},
            {{
                "id": 3,
                "name": "Tech Stack Name 3",
                "language": "Programming Language 3",
                "framework": "Main Framework 3",
                "database": "Database Type 3",
                "dependencies": ["list", "of", "dependencies"],
                "tools": ["development", "tools"],
                "deployment": "Deployment method",
                "pros": ["pro1", "pro2", "pro3"],
                "cons": ["con1", "con2"],
                "complexity": "Beginner/Intermediate/Advanced",
                "estimated_time": "time estimate",
                "best_use_case": "When to use this stack"
            }}
        ]
        """
        
        if model == "Grok-4":
            response = generate_with_grok(prompt)
        elif model == "Claude-Opus-4":
            response = generate_with_claude(prompt, model_name="claude-opus-4-20250514")
        else:
            response = ai_engine.generate_response(prompt, model=model)
        
        # Try to parse JSON from response
        try:
            import json
            import re
            
            # Clean the response - remove any markdown formatting
            cleaned_response = response.strip()
            
            # Remove markdown code blocks if present
            cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
            cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
            
            # Insert missing commas between objects in array
            cleaned_response = re.sub(r'\}\s*\{', '},\n{', cleaned_response)
            
            # Find JSON array
            start_idx = cleaned_response.find('[')
            end_idx = cleaned_response.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = cleaned_response[start_idx:end_idx]
                # Remove any extra data after the last closing bracket
                json_str = json_str[:json_str.rfind(']')+1]
                result = json.loads(json_str)
                
                # Validate the structure
                if isinstance(result, list) and len(result) > 0:
                    return result
                else:
                    st.error("Invalid tech stack response structure")
                    return _get_fallback_tech_stacks()
            else:
                # Try parsing the entire response as JSON
                result = json.loads(cleaned_response)
                if isinstance(result, list) and len(result) > 0:
                    return result
                else:
                    st.error("Response is not a valid JSON array")
                    return _get_fallback_tech_stacks()
                    
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse tech stack response as JSON: {str(e)}")
            st.error("Raw response preview:")
            st.code(response[:500] + "..." if len(response) > 500 else response)
            st.info("Using fallback tech stack suggestions...")
            return _get_fallback_tech_stacks()
            
    except Exception as e:
        handle_and_display_error(e, "suggest_tech_stack")
        return _get_fallback_tech_stacks()

def _get_fallback_tech_stacks():
    """Provide fallback tech stack suggestions when AI fails"""
    return [
        {
            "id": 1,
            "name": "Python Django Stack",
            "language": "Python 3.11",
            "framework": "Django 4.2",
            "database": "PostgreSQL",
            "dependencies": ["django", "psycopg2", "djangorestframework", "celery"],
            "tools": ["pip", "virtualenv", "git", "docker"],
            "deployment": "Docker + AWS",
            "pros": ["Rapid development", "Built-in admin", "Large ecosystem", "Mature framework"],
            "cons": ["Monolithic", "Learning curve", "Less flexible"],
            "complexity": "Intermediate",
            "estimated_time": "4-6 weeks",
            "best_use_case": "Web applications with complex business logic"
        },
        {
            "id": 2,
            "name": "React Node.js Stack",
            "language": "JavaScript/TypeScript",
            "framework": "React 18 + Node.js",
            "database": "MongoDB",
            "dependencies": ["react", "express", "mongoose", "socket.io"],
            "tools": ["npm", "webpack", "eslint", "jest"],
            "deployment": "Vercel + MongoDB Atlas",
            "pros": ["Fast development", "Rich ecosystem", "Scalable", "Real-time capable"],
            "cons": ["Complex setup", "Many dependencies", "JavaScript fatigue"],
            "complexity": "Advanced",
            "estimated_time": "6-8 weeks",
            "best_use_case": "Modern web applications with real-time features"
        },
        {
            "id": 3,
            "name": "Python FastAPI Stack",
            "language": "Python 3.11",
            "framework": "FastAPI",
            "database": "SQLite/PostgreSQL",
            "dependencies": ["fastapi", "uvicorn", "sqlalchemy", "pydantic"],
            "tools": ["pip", "poetry", "git", "docker"],
            "deployment": "Docker + Cloud Run",
            "pros": ["Fast performance", "Auto documentation", "Type hints", "Modern"],
            "cons": ["Newer ecosystem", "Less mature", "Smaller community"],
            "complexity": "Intermediate",
            "estimated_time": "3-5 weeks",
            "best_use_case": "API-first applications and microservices"
        }
    ]

def _get_fallback_code(tech_stack_name, requirement):
    """Generate fallback code templates when AI is not available"""
    
    if "Django" in tech_stack_name:
        return {
            "main_code": {
                "success": True,
                "files": {
                    "main.py": f'''"""
{requirement}

Django Application Template
"""

import os
import django
from django.core.wsgi import get_wsgi_application

# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# WSGI application
application = get_wsgi_application()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
''',
                    "config.py": '''"""
Configuration settings for Django application
"""

import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your-secret-key-here'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
''',
                    "utils.py": '''"""
Utility functions for the application
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_input(data: Dict[str, Any]) -> bool:
    """Validate input data"""
    if not isinstance(data, dict):
        return False
    return True

def format_response(data: Any) -> Dict[str, Any]:
    """Format response data"""
    return {
        "success": True,
        "data": data,
        "timestamp": "2024-01-01T00:00:00Z"
    }
''',
                    "models.py": '''"""
Database models for Django application
"""

from django.db import models
from django.contrib.auth.models import User

class BaseModel(models.Model):
    """Base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class ExampleModel(BaseModel):
    """Example model for demonstration"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
''',
                    "api.py": '''"""
API endpoints for Django application
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import ExampleModel

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    })

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_example(request):
    """Example API endpoint"""
    if request.method == "GET":
        return JsonResponse({
            "message": "Hello from Django API",
            "method": "GET"
        })
    elif request.method == "POST":
        data = json.loads(request.body)
        return JsonResponse({
            "message": "Data received",
            "data": data,
            "method": "POST"
        })
'''
                }
            },
            "test_code": {
                "success": True,
                "test_files": {
                    "test_main.py": '''"""
Test cases for main application
"""

import unittest
from django.test import TestCase
from django.urls import reverse

class MainAppTestCase(TestCase):
    """Test cases for main application functionality"""
    
    def setUp(self):
        """Set up test data"""
        pass
    
    def test_home_page(self):
        """Test home page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
''',
                    "test_utils.py": '''"""
Test cases for utility functions
"""

import unittest
from utils import validate_input, format_response

class UtilsTestCase(unittest.TestCase):
    """Test cases for utility functions"""
    
    def test_validate_input_valid(self):
        """Test input validation with valid data"""
        data = {"key": "value"}
        self.assertTrue(validate_input(data))
    
    def test_validate_input_invalid(self):
        """Test input validation with invalid data"""
        data = "not a dict"
        self.assertFalse(validate_input(data))
    
    def test_format_response(self):
        """Test response formatting"""
        data = {"test": "data"}
        response = format_response(data)
        
        self.assertIn("success", response)
        self.assertIn("data", response)
        self.assertIn("timestamp", response)
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], data)

if __name__ == '__main__':
    unittest.main()
''',
                    "test_models.py": '''"""
Test cases for database models
"""

from django.test import TestCase
from .models import ExampleModel

class ExampleModelTestCase(TestCase):
    """Test cases for ExampleModel"""
    
    def test_model_creation(self):
        """Test model creation"""
        model = ExampleModel.objects.create(
            name="Test Model",
            description="Test Description"
        )
        self.assertEqual(model.name, "Test Model")
        self.assertEqual(model.description, "Test Description")
        self.assertTrue(model.is_active)
    
    def test_model_str_representation(self):
        """Test string representation"""
        model = ExampleModel.objects.create(name="Test Model")
        self.assertEqual(str(model), "Test Model")
''',
                    "conftest.py": '''"""
Pytest configuration and fixtures
"""

import pytest
from django.conf import settings

@pytest.fixture
def example_data():
    """Fixture for example data"""
    return {
        "name": "Test Example",
        "description": "Test Description",
        "is_active": True
    }

@pytest.fixture
def api_client():
    """Fixture for API client"""
    from rest_framework.test import APIClient
    return APIClient()
'''
                }
            },
            "additional_files": {
                "success": True,
                "additional_files": {
                    "requirements.txt": '''# Django Project Dependencies

# Core Django
Django==4.2.7
djangorestframework==3.14.0

# Database
psycopg2-binary==2.9.7

# Development
pytest==7.4.3
pytest-django==4.5.2
black==23.9.1
flake8==6.1.0

# Production
gunicorn==21.2.0
whitenoise==6.5.0

# Environment
python-dotenv==1.0.0
''',
                    "README.md": f'''# Django Project

{requirement}

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Start development server:
```bash
python manage.py runserver
```

## Testing

Run tests with:
```bash
pytest
```

## Deployment

Use the provided Dockerfile and docker-compose.yml for deployment.
''',
                    ".env.example": '''# Django Environment Variables

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Static Files
STATIC_URL=/static/
STATIC_ROOT=staticfiles/

# Logging
LOG_LEVEL=INFO
''',
                    ".gitignore": '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
''',
                    "Dockerfile": '''# Django Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
''',
                    "docker-compose.yml": '''# Django Docker Compose

version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://postgres:password@db:5432/django_db
    depends_on:
      - db
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=django_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
  static_volume:
  media_volume:
''',
                    "Makefile": '''# Django Makefile

.PHONY: help install test run clean

help:
	@echo "Available commands:"
	@echo "  install  - Install dependencies"
	@echo "  test     - Run tests"
	@echo "  run      - Start development server"
	@echo "  clean    - Clean up files"

install:
	pip install -r requirements.txt

test:
	pytest

run:
	python manage.py runserver

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
''',
                    "scripts/deploy.sh": '''#!/bin/bash

# Django Deployment Script

echo "Starting deployment..."

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start the application
gunicorn --bind 0.0.0.0:8000 config.wsgi:application
''',
                    "docs/API.md": '''# Django API Documentation

## Endpoints

### Health Check
- **GET** `/health/`
- Returns application health status

### Example API
- **GET** `/api/example/`
- Returns example data
- **POST** `/api/example/`
- Accepts JSON data and returns confirmation

## Authentication

Currently, no authentication is required for these endpoints.

## Response Format

All responses are in JSON format:

```json
{
    "status": "success",
    "data": {},
    "timestamp": "2024-01-01T00:00:00Z"
}
```
'''
                }
            }
        }
    elif "Flask" in tech_stack_name:
        return {
            "main_code": {
                "success": True,
                "files": {
                    "main.py": f'''"""
{requirement}

Flask Application Template
"""

from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['DEBUG'] = os.environ.get('DEBUG', 'True').lower() == 'true'

@app.route('/')
def home():
    """Home page route"""
    return render_template('index.html', title='Flask App')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({{
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Flask Application'
    }})

@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    """Handle data requests"""
    if request.method == 'GET':
        return jsonify({{
            'message': 'Data endpoint',
            'method': 'GET',
            'data': {{'example': 'value'}}
        }})
    elif request.method == 'POST':
        data = request.get_json()
        return jsonify({{
            'message': 'Data received',
            'method': 'POST',
            'data': data
        }})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({{'error': 'Not found'}}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({{'error': 'Internal server error'}}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
''',
                    "config.py": '''"""
Configuration settings for Flask application
"""

import os
from pathlib import Path

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
''',
                    "utils.py": '''"""
Utility functions for Flask application
"""

import logging
from typing import Any, Dict
from datetime import datetime

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_input(data: Dict[str, Any]) -> bool:
    """Validate input data"""
    if not isinstance(data, dict):
        return False
    return True

def format_response(data: Any) -> Dict[str, Any]:
    """Format response data"""
    return {
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

def create_error_response(message: str, status_code: int = 400) -> Dict[str, Any]:
    """Create error response"""
    return {
        "success": False,
        "error": message,
        "status_code": status_code,
        "timestamp": datetime.now().isoformat()
    }
''',
                    "models.py": '''"""
Database models for Flask application
"""

from datetime import datetime
from typing import Optional

class BaseModel:
    """Base model with common fields"""
    
    def __init__(self):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ExampleModel(BaseModel):
    """Example model for demonstration"""
    
    def __init__(self, name: str, description: Optional[str] = None):
        super().__init__()
        self.name = name
        self.description = description or ""
        self.is_active = True
    
    def to_dict(self):
        """Convert to dictionary"""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active
        })
        return base_dict
'''
                }
            },
            "test_code": {
                "success": True,
                "test_files": {
                    "test_main.py": '''"""
Test cases for Flask application
"""

import unittest
import json
from main import app

class FlaskAppTestCase(unittest.TestCase):
    """Test cases for Flask application"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_page(self):
        """Test home page loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_data_endpoint_get(self):
        """Test data endpoint GET method"""
        response = self.app.get('/api/data')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['method'], 'GET')
    
    def test_data_endpoint_post(self):
        """Test data endpoint POST method"""
        test_data = {'test': 'value'}
        response = self.app.post('/api/data', 
                               data=json.dumps(test_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['method'], 'POST')
        self.assertEqual(data['data'], test_data)

if __name__ == '__main__':
    unittest.main()
''',
                    "test_utils.py": '''"""
Test cases for utility functions
"""

import unittest
from utils import validate_input, format_response, create_error_response

class UtilsTestCase(unittest.TestCase):
    """Test cases for utility functions"""
    
    def test_validate_input_valid(self):
        """Test input validation with valid data"""
        data = {"key": "value"}
        self.assertTrue(validate_input(data))
    
    def test_validate_input_invalid(self):
        """Test input validation with invalid data"""
        data = "not a dict"
        self.assertFalse(validate_input(data))
    
    def test_format_response(self):
        """Test response formatting"""
        data = {"test": "data"}
        response = format_response(data)
        
        self.assertIn("success", response)
        self.assertIn("data", response)
        self.assertIn("timestamp", response)
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], data)
    
    def test_create_error_response(self):
        """Test error response creation"""
        error_msg = "Test error"
        response = create_error_response(error_msg, 400)
        
        self.assertIn("success", response)
        self.assertIn("error", response)
        self.assertIn("status_code", response)
        self.assertIn("timestamp", response)
        self.assertFalse(response["success"])
        self.assertEqual(response["error"], error_msg)
        self.assertEqual(response["status_code"], 400)

if __name__ == '__main__':
    unittest.main()
''',
                    "test_models.py": '''"""
Test cases for database models
"""

import unittest
from models import ExampleModel

class ExampleModelTestCase(unittest.TestCase):
    """Test cases for ExampleModel"""
    
    def test_model_creation(self):
        """Test model creation"""
        model = ExampleModel("Test Model", "Test Description")
        self.assertEqual(model.name, "Test Model")
        self.assertEqual(model.description, "Test Description")
        self.assertTrue(model.is_active)
    
    def test_model_to_dict(self):
        """Test model to dictionary conversion"""
        model = ExampleModel("Test Model")
        model_dict = model.to_dict()
        
        self.assertIn('name', model_dict)
        self.assertIn('description', model_dict)
        self.assertIn('is_active', model_dict)
        self.assertIn('created_at', model_dict)
        self.assertIn('updated_at', model_dict)
        
        self.assertEqual(model_dict['name'], "Test Model")
        self.assertTrue(model_dict['is_active'])

if __name__ == '__main__':
    unittest.main()
'''
                }
            },
            "additional_files": {
                "success": True,
                "additional_files": {
                    "requirements.txt": '''# Flask Project Dependencies

# Core Flask
Flask==2.3.3
Werkzeug==2.3.7

# Development
pytest==7.4.3
pytest-flask==1.3.0
black==23.9.1
flake8==6.1.0

# Production
gunicorn==21.2.0

# Environment
python-dotenv==1.0.0

# Optional: Database
# SQLAlchemy==2.0.21
# Flask-SQLAlchemy==3.0.5

# Optional: Authentication
# Flask-Login==0.6.3
# Flask-JWT-Extended==4.5.3
''',
                    "README.md": f'''# Flask Project

{requirement}

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export FLASK_APP=main.py
export FLASK_ENV=development
```

3. Start development server:
```bash
python main.py
```

## Testing

Run tests with:
```bash
pytest
```

## API Endpoints

- `GET /` - Home page
- `GET /api/health` - Health check
- `GET /api/data` - Get data
- `POST /api/data` - Post data

## Deployment

Use the provided Dockerfile and docker-compose.yml for deployment.
''',
                    ".env.example": '''# Flask Environment Variables

# Flask Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
FLASK_ENV=development

# Server
PORT=5000
HOST=0.0.0.0

# Database (optional)
DATABASE_URL=sqlite:///app.db

# Logging
LOG_LEVEL=INFO
''',
                    ".gitignore": '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Flask
instance/
.webassets-cache
*.db

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
''',
                    "Dockerfile": '''# Flask Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
''',
                    "docker-compose.yml": '''# Flask Docker Compose

version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DEBUG=False
      - SECRET_KEY=your-production-secret
    volumes:
      - .:/app
    restart: unless-stopped

  # Optional: Add database service
  # db:
  #   image: postgres:13
  #   environment:
  #     - POSTGRES_DB=flask_db
  #     - POSTGRES_USER=postgres
  #     - POSTGRES_PASSWORD=password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data

# volumes:
#   postgres_data:
''',
                    "Makefile": '''# Flask Makefile

.PHONY: help install test run clean

help:
	@echo "Available commands:"
	@echo "  install  - Install dependencies"
	@echo "  test     - Run tests"
	@echo "  run      - Start development server"
	@echo "  clean    - Clean up files"

install:
	pip install -r requirements.txt

test:
	pytest

run:
	python main.py

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
''',
                    "scripts/deploy.sh": '''#!/bin/bash

# Flask Deployment Script

echo "Starting deployment..."

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start the application
gunicorn --bind 0.0.0.0:5000 main:app
''',
                    "docs/API.md": '''# Flask API Documentation

## Endpoints

### Home Page
- **GET** `/`
- Returns the home page

### Health Check
- **GET** `/api/health`
- Returns application health status

### Data Endpoint
- **GET** `/api/data`
- Returns example data
- **POST** `/api/data`
- Accepts JSON data and returns confirmation

## Authentication

Currently, no authentication is required for these endpoints.

## Response Format

All responses are in JSON format:

```json
{
    "success": true,
    "data": {},
    "timestamp": "2024-01-01T00:00:00Z"
}
```

## Error Responses

```json
{
    "success": false,
    "error": "Error message",
    "status_code": 400,
    "timestamp": "2024-01-01T00:00:00Z"
}
```
'''
                }
            }
        }
    elif "React" in tech_stack_name or "Node.js" in tech_stack_name:
        return {
            "main_code": {
                "success": True,
                "files": {
                    "server.js": f'''/*
{requirement}

Node.js/Express Server
*/

const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const config = require('./config');
const logger = require('./utils/logger');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({{ extended: true }}));

// Database connection
mongoose.connect(config.database.url, {{
    useNewUrlParser: true,
    useUnifiedTopology: true
}})
.then(() => logger.info('Connected to MongoDB'))
.catch(err => logger.error('MongoDB connection error:', err));

// Routes
app.use('/api', require('./routes'));

// Health check
app.get('/health', (req, res) => {{
    res.json({{
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    }});
}});

// Error handling middleware
app.use((err, req, res, next) => {{
    logger.error(err.stack);
    res.status(500).json({{ error: 'Something went wrong!' }});
}});

const PORT = config.port || 3000;
app.listen(PORT, () => {{
    logger.info(`Server running on port ${{PORT}}`);
}});

module.exports = app;
''',
                    "config/index.js": '''/*
Configuration for the application
*/

const env = process.env.NODE_ENV || 'development';

const config = {
    development: {
        port: 3000,
        database: {
            url: 'mongodb://localhost:27017/dev_db'
        },
        cors: {
            origin: 'http://localhost:3000'
        },
        jwt: {
            secret: 'dev-secret-key',
            expiresIn: '24h'
        }
    },
    production: {
        port: process.env.PORT || 3000,
        database: {
            url: process.env.MONGODB_URI
        },
        cors: {
            origin: process.env.ALLOWED_ORIGINS?.split(',') || []
        },
        jwt: {
            secret: process.env.JWT_SECRET,
            expiresIn: '24h'
        }
    }
};

module.exports = config[env];
''',
                    "utils/logger.js": '''/*
Logging utility
*/

const winston = require('winston');

const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
    ),
    defaultMeta: { service: 'api-service' },
    transports: [
        new winston.transports.File({ filename: 'error.log', level: 'error' }),
        new winston.transports.File({ filename: 'combined.log' })
    ]
});

if (process.env.NODE_ENV !== 'production') {
    logger.add(new winston.transports.Console({
        format: winston.format.simple()
    }));
}

module.exports = logger;
''',
                    "utils/validator.js": '''/*
Input validation utilities
*/

const Joi = require('joi');

const validateInput = (data, schema) => {
    const { error, value } = schema.validate(data);
    if (error) {
        throw new Error(error.details[0].message);
    }
    return value;
};

const formatResponse = (data, success = true) => {
    return {
        success,
        data,
        timestamp: new Date().toISOString()
    };
};

module.exports = {
    validateInput,
    formatResponse
};
''',
                    "models/User.js": '''/*
User model
*/

const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    username: {
        type: String,
        required: true,
        unique: true,
        trim: true
    },
    email: {
        type: String,
        required: true,
        unique: true,
        lowercase: true
    },
    password: {
        type: String,
        required: true
    },
    isActive: {
        type: Boolean,
        default: true
    }
}, {
    timestamps: true
});

module.exports = mongoose.model('User', userSchema);
''',
                    "routes/index.js": '''/*
Main routes
*/

const express = require('express');
const router = express.Router();

const userRoutes = require('./users');
const authRoutes = require('./auth');

router.use('/users', userRoutes);
router.use('/auth', authRoutes);

module.exports = router;
''',
                    "routes/users.js": '''/*
User routes
*/

const express = require('express');
const router = express.Router();
const User = require('../models/User');
const { validateInput } = require('../utils/validator');

// Get all users
router.get('/', async (req, res) => {
    try {
        const users = await User.find({ isActive: true });
        res.json({ success: true, data: users });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Get user by ID
router.get('/:id', async (req, res) => {
    try {
        const user = await User.findById(req.params.id);
        if (!user) {
            return res.status(404).json({ success: false, error: 'User not found' });
        }
        res.json({ success: true, data: user });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

module.exports = router;
''',
                    "routes/auth.js": '''/*
Authentication routes
*/

const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const config = require('../config');

// Register
router.post('/register', async (req, res) => {
    try {
        const { username, email, password } = req.body;
        
        // Check if user exists
        const existingUser = await User.findOne({ $or: [{ email }, { username }] });
        if (existingUser) {
            return res.status(400).json({ success: false, error: 'User already exists' });
        }
        
        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);
        
        // Create user
        const user = new User({
            username,
            email,
            password: hashedPassword
        });
        
        await user.save();
        
        res.status(201).json({ success: true, message: 'User created successfully' });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Login
router.post('/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        
        // Find user
        const user = await User.findOne({ email });
        if (!user) {
            return res.status(401).json({ success: false, error: 'Invalid credentials' });
        }
        
        // Check password
        const isValidPassword = await bcrypt.compare(password, user.password);
        if (!isValidPassword) {
            return res.status(401).json({ success: false, error: 'Invalid credentials' });
        }
        
        // Generate token
        const token = jwt.sign(
            { userId: user._id, email: user.email },
            config.jwt.secret,
            { expiresIn: config.jwt.expiresIn }
        );
        
        res.json({ success: true, token });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

module.exports = router;
'''
                }
            },
            "test_code": {
                "success": True,
                "test_files": {
                    "test/server.test.js": '''/*
Server tests
*/

const request = require('supertest');
const app = require('../server');
const mongoose = require('mongoose');

describe('Server', () => {
    beforeAll(async () => {
        // Connect to test database
        await mongoose.connect('mongodb://localhost:27017/test_db');
    });

    afterAll(async () => {
        await mongoose.connection.close();
    });

    describe('GET /health', () => {
        it('should return health status', async () => {
            const response = await request(app).get('/health');
            expect(response.statusCode).toBe(200);
            expect(response.body.status).toBe('healthy');
            expect(response.body.timestamp).toBeDefined();
        });
    });
});
''',
                    "test/routes/users.test.js": '''/*
User routes tests
*/

const request = require('supertest');
const app = require('../server');
const User = require('../models/User');

describe('User Routes', () => {
    beforeEach(async () => {
        await User.deleteMany({});
    });

    describe('GET /api/users', () => {
        it('should return empty array when no users', async () => {
            const response = await request(app).get('/api/users');
            expect(response.statusCode).toBe(200);
            expect(response.body.success).toBe(true);
            expect(response.body.data).toEqual([]);
        });
    });
});
''',
                    "test/routes/auth.test.js": '''/*
Auth routes tests
*/

const request = require('supertest');
const app = require('../server');
const User = require('../models/User');

describe('Auth Routes', () => {
    beforeEach(async () => {
        await User.deleteMany({});
    });

    describe('POST /api/auth/register', () => {
        it('should create new user', async () => {
            const userData = {
                username: 'testuser',
                email: 'test@example.com',
                password: 'password123'
            };

            const response = await request(app)
                .post('/api/auth/register')
                .send(userData);

            expect(response.statusCode).toBe(201);
            expect(response.body.success).toBe(true);
        });
    });
});
''',
                    "test/utils/validator.test.js": '''/*
Validator tests
*/

const { validateInput, formatResponse } = require('../../utils/validator');
const Joi = require('joi');

describe('Validator', () => {
    describe('validateInput', () => {
        it('should validate correct data', () => {
            const schema = Joi.object({
                name: Joi.string().required(),
                email: Joi.string().email().required()
            });

            const data = {
                name: 'Test User',
                email: 'test@example.com'
            };

            const result = validateInput(data, schema);
            expect(result).toEqual(data);
        });

        it('should throw error for invalid data', () => {
            const schema = Joi.object({
                name: Joi.string().required(),
                email: Joi.string().email().required()
            });

            const data = {
                name: 'Test User',
                email: 'invalid-email'
            };

            expect(() => validateInput(data, schema)).toThrow();
        });
    });

    describe('formatResponse', () => {
        it('should format response correctly', () => {
            const data = { test: 'data' };
            const response = formatResponse(data);

            expect(response.success).toBe(true);
            expect(response.data).toEqual(data);
            expect(response.timestamp).toBeDefined();
        });
    });
});
'''
                }
            },
            "additional_files": {
                "success": True,
                "additional_files": {
                    "package.json": '''{
  "name": "nodejs-api",
  "version": "1.0.0",
  "description": "Node.js API with Express and MongoDB",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "jest",
    "test:watch": "jest --watch"
  },
  "dependencies": {
    "express": "^4.18.2",
    "mongoose": "^7.5.0",
    "cors": "^2.8.5",
    "bcryptjs": "^2.4.3",
    "jsonwebtoken": "^9.0.2",
    "joi": "^17.9.2",
    "winston": "^3.10.0",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "jest": "^29.6.2",
    "supertest": "^6.3.3",
    "nodemon": "^3.0.1"
  },
  "keywords": ["nodejs", "express", "mongodb", "api"],
  "author": "Your Name",
  "license": "MIT"
}''',
                    "README.md": f'''# Node.js API Project

{requirement}

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm run dev
```

## Testing

Run tests with:
```bash
npm test
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/users` - Get all users
- `GET /api/users/:id` - Get user by ID
- `POST /api/auth/register`
- `POST /api/auth/login`

## Deployment

Use the provided Dockerfile and docker-compose.yml for deployment.
''',
                    ".env.example": '''# Node.js Environment Variables

# Server
PORT=3000
NODE_ENV=development

# Database
MONGODB_URI=mongodb://localhost:27017/dev_db

# JWT
JWT_SECRET=your-secret-key-here

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
''',
                    ".gitignore": '''# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
''',
                    "Dockerfile": '''# Node.js Dockerfile

FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
''',
                    "docker-compose.yml": '''# Node.js Docker Compose

version: '3.8'

services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - MONGODB_URI=mongodb://mongo:27017/prod_db
      - JWT_SECRET=your-production-secret
    depends_on:
      - mongo
    volumes:
      - .:/app
      - /app/node_modules

  mongo:
    image: mongo:6
    environment:
      - MONGO_INITDB_DATABASE=prod_db
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
''',
                    "jest.config.js": '''module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/test/**/*.test.js'],
  collectCoverageFrom: [
    '**/*.js',
    '!**/node_modules/**',
    '!**/test/**'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov']
};
''',
                    "Makefile": '''# Node.js Makefile

.PHONY: help install test run clean

help:
	@echo "Available commands:"
	@echo "  install  - Install dependencies"
	@echo "  test     - Run tests"
	@echo "  run      - Start development server"
	@echo "  clean    - Clean up files"

install:
	npm install

test:
	npm test

run:
	npm run dev

clean:
	rm -rf node_modules
	rm -rf coverage
	find . -name "*.log" -delete
''',
                    "scripts/deploy.sh": '''#!/bin/bash

# Node.js Deployment Script

echo "Starting deployment..."

# Install dependencies
npm ci --only=production

# Run tests
npm test

# Start the application
npm start
''',
                    "docs/API.md": '''# Node.js API Documentation

## Authentication

Most endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Health Check
- **GET** `/health`
- Returns application health status

### Users
- **GET** `/api/users`
- Get all active users
- **GET** `/api/users/:id`
- Get user by ID

### Authentication
- **POST** `/api/auth/register`
- Register new user
- **POST** `/api/auth/login`
- Login user

## Request/Response Format

### Register Request
```json
{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}
```

### Login Request
```json
{
    "email": "test@example.com",
    "password": "password123"
}
```

### Response Format
```json
{
    "success": true,
    "data": {},
    "timestamp": "2024-01-01T00:00:00Z"
}
```
'''
                }
            }
        }
    else:
        # Default Python template
        return {
            "main_code": {
                "success": True,
                "files": {
                    "main.py": f'''"""
{requirement}

Python Application Template
"""

import logging
from typing import Dict, Any
from utils import setup_logging, validate_input, format_response

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class Application:
    """Main application class"""
    
    def __init__(self):
        self.name = "AI-Generated Application"
        logger.info("Initializing " + self.name)
    
    def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming request"""
        if not validate_input(data):
            return format_response({{"error": "Invalid input"}})
        
        try:
            # Process the data here
            result = {{"processed": True, "data": data}}
            logger.info("Request processed successfully")
            return format_response(result)
        except Exception as e:
            logger.error("Error processing request: " + str(e))
            return format_response({{"error": str(e)}})
    
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return format_response({{"status": "healthy"}})

def main():
    """Main function"""
    app = Application()
    
    # Example usage
    sample_data = {{"key": "value"}}
    result = app.process_request(sample_data)
    print(result)
    
    health = app.health_check()
    print(health)

if __name__ == "__main__":
    main()
''',
                    "config.py": '''"""
Configuration settings
"""

import os
from typing import Dict, Any

class Config:
    """Base configuration class"""
    
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration dictionary"""
        return {
            'debug': Config.DEBUG,
            'secret_key': Config.SECRET_KEY,
            'database_url': Config.DATABASE_URL
        }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
''',
                    "utils.py": '''"""
Utility functions
"""

import logging
from typing import Any, Dict

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_input(data: Dict[str, Any]) -> bool:
    """Validate input data"""
    if not isinstance(data, dict):
        return False
    return True

def format_response(data: Any) -> Dict[str, Any]:
    """Format response data"""
    return {
        "success": True,
        "data": data,
        "timestamp": "2024-01-01T00:00:00Z"
    }
'''
                }
            },
            "test_code": {
                "success": True,
                "test_files": {
                    "test_main.py": '''"""
Test cases for main application
"""

import unittest
from main import Application

class ApplicationTestCase(unittest.TestCase):
    """Test cases for Application class"""
    
    def setUp(self):
        """Set up test data"""
        self.app = Application()
    
    def test_health_check(self):
        """Test health check method"""
        result = self.app.health_check()
        self.assertIn('success', result)
        self.assertTrue(result['success'])
        self.assertIn('data', result['data'])
    
    def test_process_request_valid(self):
        """Test process_request with valid data"""
        data = {"key": "value"}
        result = self.app.process_request(data)
        self.assertIn('success', result)
        self.assertTrue(result['success'])
        self.assertIn('data', result['data'])
    
    def test_process_request_invalid(self):
        """Test process_request with invalid data"""
        data = "not a dict"
        result = self.app.process_request(data)
        self.assertIn('success', result)
        self.assertTrue(result['success'])
        self.assertIn('error', result['data'])

if __name__ == '__main__':
    unittest.main()
''',
                    "test_utils.py": '''"""
Test cases for utility functions
"""

import unittest
from utils import validate_input, format_response

class UtilsTestCase(unittest.TestCase):
    """Test cases for utility functions"""
    
    def test_validate_input_valid(self):
        """Test input validation with valid data"""
        data = {"key": "value"}
        self.assertTrue(validate_input(data))
    
    def test_validate_input_invalid(self):
        """Test input validation with invalid data"""
        data = "not a dict"
        self.assertFalse(validate_input(data))
    
    def test_format_response(self):
        """Test response formatting"""
        data = {"test": "data"}
        response = format_response(data)
        
        self.assertIn("success", response)
        self.assertIn("data", response)
        self.assertIn("timestamp", response)
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], data)

if __name__ == '__main__':
    unittest.main()
'''
                }
            }
        }

def generate_project_structure(selected_tech_stack, requirement_text, ai_engine, model="gpt-4o-mini"):
    """Generate project file structure based on selected tech stack"""
    try:
        prompt = f"""
        You are a software architect. Based on the selected tech stack and requirements, generate a detailed project file structure.

        Selected Tech Stack: {selected_tech_stack}
        Requirements: {requirement_text}

        Create a comprehensive project structure including:
        1. Directory structure with all necessary folders
        2. File names and their purposes
        3. Configuration files needed
        4. Dependencies and requirements files
        5. Documentation files
        6. Testing structure
        7. Deployment files

        CRITICAL: You must respond with ONLY a valid JSON object. Follow these rules:
        - Use proper JSON syntax with commas between all array elements
        - Use proper JSON syntax with commas between all object properties
        - No trailing commas
        - No additional text, explanations, or markdown formatting
        - Ensure all strings are properly quoted
        - Ensure all brackets and braces are properly closed

        Example format:
        {{
            "success": true,
            "project_name": "suggested project name",
            "structure": {{
                "root_files": ["file1", "file2", "file3"],
                "directories": {{
                    "src/": ["main.py", "config.py", "utils.py"],
                    "tests/": ["test_main.py", "test_utils.py"],
                    "docs/": ["README.md", "API.md"],
                    "config/": ["settings.py", "database.py"],
                    "scripts/": ["deploy.sh", "setup.py"]
                }}
            }},
            "dependencies": {{
                "main": ["dependency1", "dependency2"],
                "dev": ["dev-dependency1", "dev-dependency2"],
                "test": ["test-dependency1", "test-dependency2"]
            }},
            "description": "Brief project description"
        }}

        Remember: Every array element must be separated by commas, and every object property must be separated by commas.
        """
        
        if model == "Grok-4":
            response = generate_with_grok(prompt)
        elif model == "Claude-Opus-4":
            response = generate_with_claude(prompt, model_name="claude-opus-4-20250514")
        else:
            response = ai_engine.generate_response(prompt, model=model)
        
        # Try to parse JSON from response
        try:
            import json
            import re
            
            # Clean the response - remove any markdown formatting
            cleaned_response = response.strip()
            
            # Remove markdown code blocks if present
            cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
            cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
            
            # Insert missing commas between objects in array
            cleaned_response = re.sub(r'\}\s*\{', '},\n{', cleaned_response)
            
            # Find JSON object
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = cleaned_response[start_idx:end_idx]
                # Remove any extra data after the last closing brace
                json_str = json_str[:json_str.rfind('}')+1]
                result = json.loads(json_str)
                
                # Validate the structure
                if isinstance(result, dict) and result.get("success") is not None:
                    return result
                else:
                    return {"success": False, "error": "Invalid project structure response format"}
            else:
                # Try parsing the entire response as JSON
                result = json.loads(cleaned_response)
                if isinstance(result, dict) and result.get("success") is not None:
                    return result
                else:
                    return {"success": False, "error": "Response is not a valid JSON object"}
                    
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse project structure response as JSON: {str(e)}")
            st.error("Raw response preview:")
            st.code(response[:500] + "..." if len(response) > 500 else response)
            return {"success": False, "error": f"JSON parsing error: {str(e)}"}
            
    except Exception as e:
        handle_and_display_error(e, "generate_project_structure")
        return {"success": False, "error": str(e)}

def generate_code_for_structure(project_structure, requirement_text, ai_engine, model="gpt-4o-mini"):
    """Generate complete project files based on project structure"""
    import json
    import os
    from pathlib import Path
    import re
    import streamlit as st
    def flatten_structure(structure):
        """Flatten the project structure into a list of file paths."""
        files = []
        # Root files
        for f in structure.get("root_files", []):
            files.append(f)
        # Directory files
        for dir_name, dir_files in structure.get("directories", {}).items():
            for f in dir_files:
                files.append(os.path.join(dir_name, f))
        return files

    try:
        structure = json.loads(project_structure) if isinstance(project_structure, str) else project_structure
        file_paths = flatten_structure(structure)
        all_files = {}
        # Generate code for each file
        for file_path in file_paths:
            # Check if this is a GUI application and modify the prompt accordingly
            is_gui_app = any(keyword in requirement_text.lower() for keyword in ['gui', 'graphical', 'window', 'interface', 'tkinter', 'calculator'])
            
            # Check if this is a Flask/web application
            is_flask_app = any(keyword in requirement_text.lower() for keyword in ['flask', 'web', 'api', 'server', 'http'])
            
            if is_gui_app and file_path.endswith('.py'):
                file_prompt = f"""
                Generate the complete content for the following file as part of the project:
                Project Name: {structure.get('project_name', '')}
                Project Description: {structure.get('description', '')}
                Requirements: {requirement_text}
                File Path: {file_path}
                Project Structure: {json.dumps(structure, indent=2)}
                
                IMPORTANT: This application will run in a Docker container without GUI support.
                If this is a GUI application, create a console-based version instead.
                For calculators, create a command-line interface.
                For GUI applications, create a text-based menu system.
                
                Provide ONLY the code/content for this file, no explanations, no markdown, no extra text.
                """
            elif is_flask_app and file_path.endswith('.py'):
                file_prompt = f"""
                Generate the complete content for the following file as part of the project:
                Project Name: {structure.get('project_name', '')}
                Project Description: {structure.get('description', '')}
                Requirements: {requirement_text}
                File Path: {file_path}
                Project Structure: {json.dumps(structure, indent=2)}
                
                IMPORTANT: For Flask applications, use port 5001 instead of 5000 to avoid conflicts.
                Example: app.run(host='0.0.0.0', port=5001, debug=True)
                
                Provide ONLY the code/content for this file, no explanations, no markdown, no extra text.
                """
            else:
                file_prompt = f"""
                Generate the complete content for the following file as part of the project:
                Project Name: {structure.get('project_name', '')}
                Project Description: {structure.get('description', '')}
                Requirements: {requirement_text}
                File Path: {file_path}
                Project Structure: {json.dumps(structure, indent=2)}
                
                Provide ONLY the code/content for this file, no explanations, no markdown, no extra text.
                """
            if model == "Grok-4":
                file_content = generate_with_grok(file_prompt)
            elif model == "Claude-Opus-4":
                file_content = generate_with_claude(file_prompt, model_name="claude-opus-4-20250514")
            else:
                file_content = ai_engine.generate_response(file_prompt, model=model)
            # Clean up any markdown formatting
            file_content = file_content.strip()
            file_content = re.sub(r'^```[a-zA-Z]*', '', file_content)
            file_content = re.sub(r'```$', '', file_content)
            all_files[file_path] = file_content
        # Save files in correct structure
        saved_files = []
        for file_path, content in all_files.items():
            abs_path = Path("generated/code") / file_path
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)
            saved_files.append(str(abs_path))
        return {
            "success": True,
            "files": all_files,
            "saved_files": saved_files
        }
    except Exception as e:
        handle_and_display_error(e, "generate_code_for_structure")
        return {"success": False, "error": str(e)}

# Main application
def main():
    st.markdown('<h1 class="main-header">AI-Powered Development Assistant</h1>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("""
            <div style='padding: 18px 16px 12px 16px; background: #f7f7fa; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); margin-bottom: 18px;'>
                <h3 style='margin-bottom: 8px; color: #222;'>Configuration</h3>
                <p style='font-size: 0.95em; color: #555; margin-bottom: 18px;'>
                    Select your preferred AI model and adjust generation settings for optimal results.
                </p>
        """, unsafe_allow_html=True)

        # Model selection
        model = st.selectbox(
            "AI Model",
            ["Gemini 2.5 Pro", "gpt-4o-mini", "gpt-4o", "Claude-Opus-4", "Grok-4"],
            index=0,
            help="Choose the AI model for code and test generation."
        )

        # Temperature setting
        temperature = st.slider(
            "Creativity Level",
            0.0, 1.0, 0.7, 0.1,
            help="Controls randomness. Lower values = more deterministic, higher = more creative."
        )

        # Max tokens
        max_tokens = st.slider(
            "Max Response Length",
            1000, 4000, 2000, 500,
            help="Maximum number of tokens (words/pieces) in the AI's response."
        )

        st.markdown("""
            <div style='font-size: 0.92em; color: #888; margin-top: 10px;'>
                <b>Tip:</b> For most use cases, the default settings work well. Adjust only if you need more control.
            </div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # File management
        st.header("Generated Files")
        code_dir = "generated/code"
        file_list = []
        for root, _, files in os.walk(code_dir):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), code_dir)
                file_list.append((rel_path, os.path.join(root, f)))
        st.write("[DEBUG] Files found in generated/code/:", file_list)
        if file_list:
            for rel_path, abs_path in file_list:
                with st.expander(f"{rel_path}"):
                    st.write(f"**Path:** {abs_path}")
                    try:
                        with open(abs_path, 'r', encoding='utf-8') as file:
                            content = file.read()
                        st.code(content, language='python' if rel_path.endswith('.py') else 'text')
                        st.download_button(
                            label="Download",
                            data=content,
                            file_name=rel_path,
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"Error reading file: {e}")
        else:
            st.info("No files generated yet")
    
    # Main tabs
    tab1,tab5, tab_test_gen = st.tabs([
        "Code Generation",
        "File Manager",
        "Test Generator"
    ])
    


    # Tab 1: Code Generation
    with tab1:
        st.header("Automated Code Generation and Error Handling")
        
        # Upload section for code generation
        st.subheader("Upload Requirements Document")
        uploaded_file = st.file_uploader(
            "Choose a document",
            type=['pdf', 'docx', 'doc', 'txt', 'md', 'csv', 'zip'],
            help="Upload PDF, Word, text, markdown, CSV, or a zipped project folder"
        )

        # Process uploaded file and let user choose action
        if uploaded_file is not None:
            file_ext = uploaded_file.name.lower().split('.')[-1]
            if file_ext == 'zip':
                project_dir = extract_project_zip(uploaded_file)
                if project_dir:
                    st.session_state.uploaded_project_path = project_dir
                    st.session_state.uploaded_project_files = list_python_files(project_dir)
                    st.success("Project uploaded and extracted")
            else:
                st.session_state.uploaded_document = process_uploaded_document(uploaded_file)
                if st.session_state.uploaded_document:
                    st.success(f"Document processed: {uploaded_file.name}")
                    with st.expander("View extracted text"):
                        st.text_area("Document Content", st.session_state.uploaded_document, height=200)
            # User action choice
            st.subheader("What would you like to do?")
            user_action = st.radio(
                "Choose an action:",
                [
                    "Generate Code (tech stack, structure, code, tests)",
                    
                ],
                key="user_action_choice"
            )
            st.session_state.user_action = user_action
        
        user_action = st.session_state.get('user_action', None)
        if user_action == "Generate Code (tech stack, structure, code, tests)":
            # Requirement input (if not ZIP)
            if not st.session_state.get('uploaded_project_path', None):
                st.subheader("Describe Your Requirements")
                requirement_input = st.text_area(
                    "Enter your requirements in natural language",
                    placeholder="e.g., Create a Python class for a simple calculator that can perform basic arithmetic operations...",
                    height=150
                )
                if st.session_state.uploaded_document and requirement_input:
                    combined_requirement = f"Additional Context from Document: {st.session_state.uploaded_document} Specific Requirements: {requirement_input}"
                elif st.session_state.uploaded_document:
                    combined_requirement = st.session_state.uploaded_document
                else:
                    combined_requirement = requirement_input
                # Sanitize for file naming
                st.session_state.current_requirement = sanitize_for_filename(combined_requirement)
            

            # Tech stack suggestion and rest of code generation flow
            if combined_requirement:
                # Tech stack suggestion
                if st.button("Suggest Tech Stack", type="primary"):
                    if combined_requirement.strip():
                        with st.spinner("Analyzing requirements and suggesting tech stack..."):
                            tech_stack_options = suggest_tech_stack(combined_requirement, components['ai_engine'], model)
                            if tech_stack_options:
                                st.session_state.tech_stack = tech_stack_options
                                st.markdown('<div class="tech-stack-card">', unsafe_allow_html=True)
                                st.subheader("🎯 Recommended Tech Stack Options")
                                
                                # Create a table for tech stack options
                                tech_data = []
                                for stack in tech_stack_options:
                                    tech_data.append({
                                        "ID": stack.get('id', 'N/A'),
                                        "Name": stack.get('name', 'N/A'),
                                        "Language": stack.get('language', 'N/A'),
                                        "Framework": stack.get('framework', 'N/A'),
                                        "Database": stack.get('database', 'N/A'),
                                        "Complexity": stack.get('complexity', 'N/A'),
                                        "Est. Time": stack.get('estimated_time', 'N/A')
                                    })
                                
                                st.table(tech_data)
                                
                                # Show detailed information for each stack
                                for i, stack in enumerate(tech_stack_options):
                                    with st.expander(f"📋 {stack.get('name', 'Tech Stack')} - Details"):
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            st.write("**Dependencies:**")
                                            deps = stack.get('dependencies', [])
                                            if isinstance(deps, list):
                                                for dep in deps:
                                                    st.write(f"• {dep}")
                                            else:
                                                st.write(f"• {deps}")
                                            
                                            st.write("**Tools:**")
                                            tools = stack.get('tools', [])
                                            if isinstance(tools, list):
                                                for tool in tools:
                                                    st.write(f"• {tool}")
                                            else:
                                                st.write(f"• {tools}")
                                        
                                        with col2:
                                            st.write("**Pros:**")
                                            pros = stack.get('pros', [])
                                            if isinstance(pros, list):
                                                for pro in pros:
                                                    st.write(f"• {pro}")
                                            else:
                                                st.write(f"• {pros}")
                                            
                                            st.write("**Cons:**")
                                            cons = stack.get('cons', [])
                                            if isinstance(cons, list):
                                                for con in cons:
                                                    st.write(f"• {con}")
                                            else:
                                                st.write(f"• {cons}")
                                        
                                        st.write(f"**Best Use Case:** {stack.get('best_use_case', 'N/A')}")
                                        st.write(f"**Deployment:** {stack.get('deployment', 'N/A')}")
                                
                                st.markdown('</div>', unsafe_allow_html=True)

                # Project structure generation
                if st.session_state.tech_stack:
                    selected_tech_stack = st.selectbox(
                        "Select a Tech Stack for Project Structure",
                        options=[ts['name'] for ts in st.session_state.tech_stack],
                        index=0
                    )
                    
                    if st.button("Generate Project Structure", type="primary"):
                        with st.spinner("Generating project structure..."):
                            try:
                                # Find the selected tech stack by name
                                selected_stack_obj = next(
                                    (ts for ts in st.session_state.tech_stack if ts['name'] == selected_tech_stack),
                                    None
                                )
                                
                                if selected_stack_obj:
                                    project_structure_result = generate_project_structure(
                                        json.dumps(selected_stack_obj, indent=2), # Pass as JSON string
                                        combined_requirement,
                                        components['ai_engine'],
                                        model
                                    )
                                    
                                    if project_structure_result['success']:
                                        st.success("Project structure generated successfully!")
                                        st.subheader("Generated Project Structure")
                                        st.json(project_structure_result)
                                        # Save project structure in session state for code generation
                                        st.session_state['approved_project_structure'] = project_structure_result
                                        # Save project structure
                                        project_structure_file = components['file_manager'].save_project_structure_file(
                                            combined_requirement,
                                            project_structure_result
                                        )
                                        st.session_state.generated_files.append({
                                            'name': os.path.basename(project_structure_file),
                                            'path': project_structure_file,
                                            'type': 'project_structure',
                                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        })
                                        st.info(f"Project structure saved to: {project_structure_file}")
                                    
                                    else:
                                        st.error(f"Project structure generation failed: {project_structure_result['error']}")
                                else:
                                    st.warning("Please select a tech stack from the list.")
                                    
                            except Exception as e:
                                handle_and_display_error(e, "project_structure_tab")
                else:
                    st.warning("Please suggest a tech stack first.")

                # Code generation based on structure
                if st.session_state.tech_stack and st.session_state.current_requirement:
                    # Ensure selected_stack_obj is available
                    selected_stack_obj = None
                    if 'approved_project_structure' in st.session_state and st.session_state['approved_project_structure'].get('tech_stack_name'):
                        # Try to find the stack object by name
                        stack_name = st.session_state['approved_project_structure']['tech_stack_name']
                        selected_stack_obj = next((ts for ts in st.session_state.tech_stack if ts['name'] == stack_name), None)
                    if not selected_stack_obj and st.session_state.tech_stack:
                        # Fallback: use the first tech stack
                        selected_stack_obj = st.session_state.tech_stack[0]
                    if st.button("Generate Code", type="primary"):
                        with st.spinner("Generating and healing code (self-healing workflow)..."):
                            try:
                                approved_structure = st.session_state.get('approved_project_structure')
                                if not approved_structure:
                                    st.error("No approved project structure found. Please generate and approve a project structure first.")
                                else:
                                    code_result = generate_code_for_structure(
                                        json.dumps(approved_structure['structure'], indent=2),
                                        combined_requirement,
                                        components['ai_engine'],
                                        model
                                    )
                                    if not code_result or not code_result.get('success'):
                                        st.warning("AI generation failed, using fallback templates...")
                                        if selected_stack_obj:
                                            code_result = _get_fallback_code(selected_stack_obj['name'], combined_requirement)
                                        else:
                                            st.error("No tech stack object available for fallback code generation.")
                                            return
                                    if code_result and code_result.get('success'):
                                        project_files = dict(code_result.get('files', {}))
                                        
                                        # Robust requirements.txt extraction - search all nested structures
                                        def print_nested_structure(data, prefix="", max_depth=3, current_depth=0):
                                            """Debug function to print nested structure"""
                                            if current_depth >= max_depth:
                                                return
                                            
                                            if isinstance(data, dict):
                                                for key, value in data.items():
                                                    current_path = f"{prefix}/{key}" if prefix else key
                                                    if isinstance(value, str) and len(value) < 100:
                                                        print(f"  {'  ' * current_depth}{current_path}: {value[:50]}...")
                                                    elif isinstance(value, dict):
                                                        print(f"  {'  ' * current_depth}{current_path}: {{dict}}")
                                                        print_nested_structure(value, current_path, max_depth, current_depth + 1)
                                                    elif isinstance(value, list):
                                                        print(f"  {'  ' * current_depth}{current_path}: [list with {len(value)} items]")
                                                        for i, item in enumerate(value[:2]):  # Only show first 2 items
                                                            if isinstance(item, dict):
                                                                print_nested_structure(item, f"{current_path}[{i}]", max_depth, current_depth + 1)
                                            elif isinstance(data, list):
                                                for i, item in enumerate(data[:2]):  # Only show first 2 items
                                                    if isinstance(item, dict):
                                                        print_nested_structure(item, f"{prefix}[{i}]", max_depth, current_depth + 1)
                                        
                                        def extract_all_files_recursively(data, prefix=""):
                                            """Recursively extract all files from nested structures"""
                                            extracted_files = {}
                                            
                                            if isinstance(data, dict):
                                                for key, value in data.items():
                                                    current_path = f"{prefix}/{key}" if prefix else key
                                                    
                                                    # If this is a file with content (not a dict)
                                                    if isinstance(value, str) and not key.startswith('_'):
                                                        extracted_files[current_path] = value
                                                    # If this is a nested structure, recurse
                                                    elif isinstance(value, dict):
                                                        nested_files = extract_all_files_recursively(value, current_path)
                                                        extracted_files.update(nested_files)
                                                    # If this is a list, check each item
                                                    elif isinstance(value, list):
                                                        for i, item in enumerate(value):
                                                            if isinstance(item, dict):
                                                                nested_files = extract_all_files_recursively(item, f"{current_path}[{i}]")
                                                                extracted_files.update(nested_files)
                                            
                                            return extracted_files
                                        
                                        # Debug: Print the structure of code_result
                                        print("DEBUG: Code result structure:")
                                        print_nested_structure(code_result)
                                        
                                        # Extract all files from the entire code_result structure
                                        all_files = extract_all_files_recursively(code_result)
                                        
                                        # Add all extracted files to project_files
                                        for file_path, content in all_files.items():
                                            # Clean up the path (remove array indices and normalize)
                                            clean_path = file_path.replace('[0]', '').replace('[1]', '').replace('[2]', '')
                                            clean_path = clean_path.replace('//', '/').lstrip('/')
                                            
                                            # Skip if it's already in project_files (from main files)
                                            if clean_path not in project_files:
                                                project_files[clean_path] = content
                                        
                                        print(f"DEBUG: Extracted {len(all_files)} files from nested structure")
                                        print(f"DEBUG: Final project_files keys: {list(project_files.keys())}")
                                        
                                        # Ensure we have requirements.txt (check common locations)
                                        requirements_found = False
                                        for req_file in ['requirements.txt', 'requirements.txt.txt', 'requirements.txt.txt.txt']:
                                            if req_file in project_files:
                                                requirements_found = True
                                                print(f"DEBUG: Found requirements file: {req_file}")
                                                break
                                        
                                        if not requirements_found:
                                            print("WARNING: No requirements.txt found in any nested structure!")
                                        main_file_name = detect_main_file(project_files, use_llm=True)
                                        if not main_file_name:
                                            py_files = [f for f in project_files if f.endswith('.py')]
                                            if py_files:
                                                main_file_name = st.selectbox("Select the main file to run:", py_files)
                                            else:
                                                st.error("No Python files found in generated files.")
                                                return
                                        # Store for retry
                                        st.session_state.last_healing_input = (project_files, model, main_file_name)
                                        st.session_state.last_main_file_name = main_file_name
                                        healing_result = ai_self_healing_workflow(
                                            project_files,
                                            code_model=model,
                                            main_file=main_file_name,
                                            test_file="test_main.py",
                                            max_attempts=5
                                        )
                                        st.session_state.last_healing_result = healing_result
                                        if healing_result['success']:
                                            st.success("Project healed! All code and tests pass.")
                                        else:
                                            st.warning("Healing attempts exhausted. Showing best effort.")
                                        st.subheader("Final Project Files (after healing)")
                                        for fname, content in healing_result['final_files'].items():
                                            with st.expander(fname, expanded=False):
                                                st.code(content, language='python' if fname.endswith('.py') else 'text')
                                        st.subheader("Final Output")
                                        st.code(healing_result['output'])
                                        st.subheader("Final Error (if any)")
                                        st.code(healing_result['error'])
                                        saved_files = []
                                        for filename, content in healing_result['final_files'].items():
                                            # Skip empty content or directory paths
                                            if not content or not content.strip() or filename.endswith('/'):
                                                continue
                                            
                                            # Clean filename and create safe path
                                            safe_filename = filename.replace('files/', '').replace('//', '/').lstrip('/')
                                            if not safe_filename:
                                                continue
                                                
                                            abs_path = os.path.join("generated/code", safe_filename)
                                            
                                            try:
                                                # Create directory if it doesn't exist
                                                dir_path = os.path.dirname(abs_path)
                                                if dir_path and not os.path.exists(dir_path):
                                                    os.makedirs(dir_path, exist_ok=True)
                                                
                                                # Write file content
                                                with open(abs_path, 'w', encoding='utf-8') as f:
                                                    f.write(content)
                                                
                                                saved_files.append({
                                                    'name': safe_filename,
                                                    'path': abs_path,
                                                    'type': 'code',
                                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                })
                                            except Exception as file_error:
                                                st.warning(f"Could not save {safe_filename}: {file_error}")
                                                continue
                                        st.session_state.generated_files.extend(saved_files)
                            except Exception as e:
                                handle_and_display_error(e, "code_generation_tab")

                # Retry healing button
                if st.session_state.last_healing_input and st.session_state.last_healing_result and not st.session_state.last_healing_result['success']:
                    more_attempts = st.number_input("Number of additional healing attempts", min_value=1, max_value=20, value=5, step=1)
                    if st.button("Retry Healing with More Attempts"):
                        with st.spinner(f"Retrying healing with {more_attempts} more attempts..."):
                            project_files, model, main_file_name = st.session_state.last_healing_input
                            healing_result = ai_self_healing_workflow(
                                project_files,
                                code_model=model,
                                main_file=main_file_name,
                                test_file="test_main.py",
                                max_attempts=more_attempts
                            )
                            st.session_state.last_healing_result = healing_result
                            if healing_result['success']:
                                st.success("Project healed! All code and tests pass.")
                            else:
                                st.warning("Healing attempts exhausted. Showing best effort.")
                            st.subheader("Final Project Files (after healing)")
                            for fname, content in healing_result['final_files'].items():
                                with st.expander(fname, expanded=False):
                                    st.code(content, language='python' if fname.endswith('.py') else 'text')
                            st.subheader("Final Output")
                            st.code(healing_result['output'])
                            st.subheader("Final Error (if any)")
                            st.code(healing_result['error'])
                            saved_files = []
                            for filename, content in healing_result['final_files'].items():
                                # Skip empty content or directory paths
                                if not content or not content.strip() or filename.endswith('/'):
                                    continue
                                
                                # Clean filename and create safe path
                                safe_filename = filename.replace('files/', '').replace('//', '/').lstrip('/')
                                if not safe_filename:
                                    continue
                                    
                                abs_path = os.path.join("generated/code", safe_filename)
                                
                                try:
                                    # Create directory if it doesn't exist
                                    dir_path = os.path.dirname(abs_path)
                                    if dir_path and not os.path.exists(dir_path):
                                        os.makedirs(dir_path, exist_ok=True)
                                    
                                    # Write file content
                                    with open(abs_path, 'w', encoding='utf-8') as f:
                                        f.write(content)
                                    
                                    saved_files.append({
                                        'name': safe_filename,
                                        'path': abs_path,
                                        'type': 'code',
                                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    })
                                except Exception as file_error:
                                    st.warning(f"Could not save {safe_filename}: {file_error}")
                                    continue
                            st.session_state.generated_files.extend(saved_files)
        
    # Tab 5: File Manager
    with tab5:
        st.header("File Management")
        
        if st.session_state.generated_files:
            st.subheader("Generated Files")
            
            # File statistics
            file_types = {}
            for file_info in st.session_state.generated_files:
                file_type = file_info['type']
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Code Files", file_types.get('code', 0))
            with col2:
                st.metric("Test Files", file_types.get('test', 0))
            with col3:
                st.metric("Assessments", file_types.get('assessment', 0))
            with col4:
                st.metric("Total Files", len(st.session_state.generated_files))
            
            # File list
            for i, file_info in enumerate(st.session_state.generated_files):
                with st.expander(f"{file_info['name']} ({file_info['type']})"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Created:** {file_info['timestamp']}")
                        st.write(f"**Path:** {file_info['path']}")
                    
                    with col2:
                        if st.button(f"Download", key=f"dl_{i}"):
                            with open(file_info['path'], 'r') as f:
                                st.download_button(
                                    label="Click to download",
                                    data=f.read(),
                                    file_name=file_info['name'],
                                    mime="text/plain"
                                )
                    
                    with col3:
                        if st.button(f"Delete", key=f"del_{i}"):
                            try:
                                os.remove(file_info['path'])
                                st.session_state.generated_files.pop(i)
                                st.success("File deleted successfully!")
                                st.rerun()
                            except Exception as e:
                                handle_and_display_error(e, "file_delete")
            
            # Export all files
            if st.button("Export All Files", type="primary"):
                try:
                    zip_path = components['file_manager'].create_zip_archive(st.session_state.generated_files)
                    with open(zip_path, 'rb') as f:
                        st.download_button(
                            label="Download ZIP Archive",
                            data=f.read(),
                            file_name="generated_files.zip",
                            mime="application/zip"
                        )
                except Exception as e:
                    handle_and_display_error(e, "create_zip_archive")
            
            # Clear all files
            if st.button("Clear All Files", type="secondary"):
                try:
                    for file_info in st.session_state.generated_files:
                        if os.path.exists(file_info['path']):
                            os.remove(file_info['path'])
                    st.session_state.generated_files = []
                    st.success("All files cleared successfully!")
                    st.rerun()
                except Exception as e:
                    handle_and_display_error(e, "clear_files")
        else:
            st.info("No files generated yet. Start by generating some code!")
    
    # Tab 6: Test Generator
    with tab_test_gen:
        
        # Test-specific upload area
        
        # File uploader that accepts all types for test generation
        uploaded_files = st.file_uploader(
            "Upload files to generate tests from (Python files, project ZIP, or requirements documents)",
            type=['py', 'zip', 'pdf', 'docx', 'doc', 'txt', 'md', 'csv'],
            accept_multiple_files=True,
            help="Upload Python files (.py), project ZIP, or requirements documents (PDF, DOCX, TXT, MD, CSV) to generate comprehensive test cases"
        )
        

        
        # Prompt box
        custom_prompt = st.text_area(
            "Custom Test Requirements",
            placeholder="Describe specific test scenarios, edge cases, testing frameworks, or any special requirements...",
            height=120,
            help="Add specific test requirements, edge cases, or testing preferences"
        )
        
        # Generate button
        if st.button("Generate Tests", type="primary", key="generate_tests_unified"):
            if not uploaded_files:
                st.warning("Please upload files to generate tests.")
            else:
                with st.spinner("Generating comprehensive test cases..."):
                    try:
                        all_content = []
                        file_names = []
                        
                        # Process uploaded files
                        if uploaded_files:
                            for file in uploaded_files:
                                file_ext = file.name.lower().split('.')[-1]
                                
                                if file_ext == 'py':
                                    # Python file
                                    content = file.read().decode('utf-8')
                                    all_content.append(f"# File: {file.name}\n{content}")
                                    file_names.append(file.name)
                                    
                                elif file_ext == 'zip':
                                    # Project ZIP
                                    project_dir = extract_project_zip(file)
                                    if project_dir:
                                        python_files = list_python_files(project_dir)
                                        for py_file in python_files:
                                            try:
                                                with open(py_file, 'r', encoding='utf-8') as f:
                                                    content = f.read()
                                                all_content.append(f"# File: {os.path.basename(py_file)}\n{content}")
                                                file_names.append(os.path.basename(py_file))
                                            except Exception as e:
                                                st.warning(f"Could not read {py_file}: {e}")
                                    
                                else:
                                    # Requirements document
                                    doc_content = process_uploaded_document(file)
                                    if doc_content:
                                        all_content.append(f"# Requirements from: {file.name}\n{doc_content}")
                                        file_names.append(f"requirements_{file.name}")
                        

                        
                        if all_content:
                            # Combine all content
                            combined_content = "\n\n".join(all_content)
                            
                            # Build the prompt
                            one_shot_example = '''
# Example function
def add(a, b):
    """Return the sum of a and b."""
    return a + b

def test_add_valid():
    assert add(2, 3) == 5

def test_add_invalid():
    import pytest
    with pytest.raises(TypeError):
        add(2, None)
'''
                            
                            # Create the full prompt
                            base_prompt = f"""
{one_shot_example}

The output must be a complete, ready-to-run test file with NO placeholders, NO commented-out code, and NO TODOs.

Generate Python unit tests using pytest for the following code and requirements.

STRICT INSTRUCTIONS:
- Do NOT use TODOs, do NOT comment out any code, and do NOT use 'pass' as a placeholder.
- If you cannot generate a real test for a function/class, SKIP it entirely.
- For each function/class, write at least one valid test case with realistic data and one invalid/edge case (e.g., wrong type, empty input, boundary values).
- Use only pytest-style assertions (no unittest boilerplate, no print statements).
- Assume all classes and functions are available for import and implemented as described.
- Avoid unnecessary setup/teardown unless required.
- Use clear, descriptive test function names.
- If relevant, include integration tests for interactions between functions/classes, and for performance or edge scenarios.
- Add concise comments only where the test logic is non-obvious.

Code and Requirements to test:
{combined_content}
"""
                            
                            # Add custom prompt if provided
                            if custom_prompt.strip():
                                full_prompt = base_prompt + f"\n\nAdditional Requirements:\n{custom_prompt}"
                            else:
                                full_prompt = base_prompt
                            
                            # Generate tests
                            if model == "Grok-4":
                                ai_response = generate_with_grok(full_prompt)
                                test_result = {"success": True, "test_code": ai_response}
                            elif model == "Claude-Opus-4":
                                test_result = generate_with_claude(full_prompt, model_name="claude-opus-4-20250514")
                            else:
                                test_result = components['test_generator'].generate_tests(full_prompt, language='python')
                            
                            if test_result['success']:
                                st.success("✅ Tests generated successfully!")
                                
                                # Display results
                                st.subheader("📋 Generated Test Code")
                                st.code(test_result['test_code'], language='python')
                                
                                # File information
                                st.subheader("📁 Files Processed")
                                for file_name in file_names:
                                    st.write(f"• {file_name}")
                                
                                # Save test file
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                test_filename = f"test_generated_{timestamp}.py"
                                test_file_path = components['file_manager'].save_test_file(
                                    test_filename, 
                                    test_result['test_code']
                                )
                                
                                st.session_state.generated_files.append({
                                    'name': test_filename,
                                    'path': test_file_path,
                                    'type': 'test',
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                                
                                st.info(f"💾 Test file saved to: {test_file_path}")
                                
                                # Download options
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        "📥 Download Test File",
                                        test_result['test_code'],
                                        file_name=test_filename,
                                        mime="text/plain"
                                    )
                                with col2:
                                    # Create ZIP with all files
                                    if uploaded_files:
                                        zip_path = components['file_manager'].create_zip_archive(st.session_state.generated_files)
                                        with open(zip_path, 'rb') as f:
                                            st.download_button(
                                                "📦 Download All Files (ZIP)",
                                                f.read(),
                                                file_name=f"test_files_{timestamp}.zip",
                                                mime="application/zip"
                                            )
                                
                                # Show custom requirements if provided
                                if custom_prompt.strip():
                                    st.subheader("💬 Custom Requirements Applied")
                                    st.info(custom_prompt)
                                
                            else:
                                st.error(f"❌ Test generation failed: {test_result.get('error', 'Unknown error')}")
                        else:
                            st.warning("No content found to generate tests for.")
                            
                    except Exception as e:
                        handle_and_display_error(e, "unified_test_generation")
        
        # Tips and guidance
        if not uploaded_files:
            st.info("""
                         **💡 How to Use:**
             
             1. **Upload Files**: Drag and drop Python files (.py), project ZIP, or requirements documents
             2. **Add Requirements**: Optionally add specific test requirements or preferences
             3. **Generate**: Click the button to create comprehensive test cases
            
            **Supported File Types:**
            • Python files (.py)
            • Project ZIP files (.zip)
            • Requirements documents (PDF, DOCX, TXT, MD, CSV)
            
            **Best Practices:**
            • Include edge cases and error scenarios in your requirements
            • Specify expected inputs and outputs clearly
            • Mention any specific testing frameworks or patterns you prefer
            """)
    
    # Footer
    # st.markdown("---")
    # st.markdown(
    #     """
    #     <div style='text-align: center; color: #666;'>
    #         AI-Powered Development Assistant | Built with Streamlit and OpenAI/Gemini
    #     </div>"""
    # )

def sanitize_for_filename(text: str) -> str:
    """Sanitize text for safe filenames: remove newlines, excessive whitespace, and special characters."""
    text = re.sub(r'\s+', ' ', text)  # Replace all whitespace (including newlines) with single space
    text = re.sub(r'[^a-zA-Z0-9 _-]', '', text)  # Remove special characters except space, underscore, hyphen
    return text.strip()[:50]  # Limit length

# Placeholder for Grok-4 API call
def generate_with_grok(prompt, api_key=None, model_name="grok-3-latest", temperature=0.7, stream=False):
    import requests
    import os
    if api_key is None:
        api_key = os.environ.get("GROK4_API_KEY")
    if not api_key:
        raise ValueError("Grok-4 API key not found. Please set GROK4_API_KEY in your environment or .env file.")
    url = "https://api.x.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        "model": model_name,
        "stream": stream,
        "temperature": temperature
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    # Extract the response text from the first choice
    return data["choices"][0]["message"]["content"] if "choices" in data and data["choices"] else ""

# Warn if Grok-4 API key is missing
if 'Grok-4' in ["Gemini 2.5 Pro", "gpt-4o-mini", "gpt-4o", "Grok-4"] and not os.environ.get("GROK4_API_KEY"):
    st.warning("Grok-4 API key is not set. Please add GROK4_API_KEY to your .env file to use Grok-4.")

# Claude API call function
def generate_with_claude(prompt, api_key=None, model_name="claude-3-opus-20240229", temperature=0.7, max_tokens=2048):
    import requests
    import os
    if api_key is None:
        api_key = os.environ.get("CLAUDE_API_KEY")
    if not api_key:
        raise ValueError("Claude API key not found. Please set CLAUDE_API_KEY in your environment or .env file.")
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": model_name,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    # Return the content of the first message
    return data["content"][0]["text"] if "content" in data and data["content"] else ""

# Add a function to orchestrate the workflow

def ai_self_healing_workflow(project_files, code_model, main_file="main.py", test_file="test_main.py", max_attempts=5):
    """
    project_files: dict mapping filename to content (e.g., {"main.py": ..., "test_main.py": ..., "README.md": ..., ...})
    1. Generate code with code_model if files are missing
    2. Run in DockerSandbox (run tests if test file is present)
    3. If error or test fail, send ALL files + error to Claude Opus 4, get fix, repeat
    4. Return final working files/output
    """
    if main_file not in project_files:
        raise ValueError("main_file must be present in project_files for healing workflow")
    code = project_files[main_file]
    test_code = project_files.get(test_file, None)

    sandbox = DockerSandbox()
    attempt = 0
    history = []
    files = dict(project_files)  # working copy
    print(f"DEBUG: Self-healing workflow - Files available: {list(files.keys())}")
    while attempt < max_attempts:
        print(f"DEBUG: Attempt {attempt + 1} - Running with files: {list(files.keys())}")
        result = sandbox.run_code(files=files, main_file=main_file)
        history.append({"files": dict(files), "result": result})
        if result["exit_code"] == 0:
            break
        # Improved prompt for Claude
        file_blocks = []
        for fname, content in files.items():
            file_blocks.append(f"<<FILENAME:{fname}>>\n{content}\n<<END>>")
        files_str = "\n".join(file_blocks)
        fix_prompt = f"""
You are an expert developer and code reviewer. The following project files failed to run or pass all tests. Here are the files and the error message.

**CRITICAL: This is a pip install dependency error. You MUST fix the requirements.txt file first.**

**Your task:**
1. **ANALYZE THE ERROR**: This is a pip install failure due to dependency order issues (numpy must be installed before pandas)
2. **FIX requirements.txt**: Reorder dependencies so that numpy comes before pandas, and update package versions if needed
3. **FIX ANY OTHER ISSUES**: Check for missing imports, syntax errors, or other problems
4. **ENSURE CONSISTENCY**: If you change any file, make sure all related files are updated

**SPECIFIC INSTRUCTIONS FOR DEPENDENCY ERRORS:**
- Move numpy to the top of requirements.txt (before pandas)
- Use compatible package versions
- Add any missing dependencies
- Remove any conflicting dependencies

**Return each file as:**
<<FILENAME:filename.ext>>
<file content>
<<END>>

**Repeat for each file that needs changes. No explanations, just the fixed files.**

FILES:
{files_str}

ERROR:
{result['stderr']}

**Focus on fixing the requirements.txt dependency order first, then any other issues.**
"""
        claude_response = generate_with_claude(fix_prompt, model_name="claude-opus-4-20250514")
        print(f"DEBUG: Claude response length: {len(claude_response)}")
        print(f"DEBUG: Claude response preview: {claude_response[:500]}...")
        
        import re
        file_pattern = re.compile(r"<<FILENAME:(.*?)>>\n(.*?)<<END>>", re.DOTALL)
        new_files = {}
        matches = list(file_pattern.finditer(claude_response))
        print(f"DEBUG: Found {len(matches)} file matches in Claude response")
        
        for match in matches:
            fname, content = match.group(1).strip(), match.group(2).strip()
            new_files[fname] = content
            print(f"DEBUG: Updated file: {fname} (length: {len(content)})")
        
        if new_files:
            files.update(new_files)
            print(f"DEBUG: Updated {len(new_files)} files with Claude fixes")
        else:
            print("DEBUG: No files were updated by Claude - this might indicate an issue with the response format")
        attempt += 1
    return {"final_files": files, "history": history, "success": result["exit_code"] == 0, "output": result["stdout"], "error": result["stderr"]}

def detect_main_file(project_files, use_llm=False):
    # 1. Prefer main.py
    if "main.py" in project_files:
        return "main.py"
    # 2. Prefer app.py
    if "app.py" in project_files:
        return "app.py"
    # 3. Look for __main__ idiom
    for fname, content in project_files.items():
        if fname.endswith('.py') and '__name__ == "__main__"' in content:
            return fname
    # 4. Only one .py file
    py_files = [f for f in project_files if f.endswith('.py')]
    if len(py_files) == 1:
        return py_files[0]
    # 5. Use LLM if needed
    if use_llm and len(py_files) > 1:
        prompt = f"""Given the following Python files, which one is the main entry point? List only the filename.\n\n""" + "\n\n".join([f"{fname}:\n{project_files[fname][:500]}" for fname in py_files])
        main_file = generate_with_claude(prompt, model_name="claude-opus-4-20250514").strip().split()[0]
        if main_file in project_files:
            return main_file
    return None

if __name__ == "__main__":
    load_dotenv()
    main() 