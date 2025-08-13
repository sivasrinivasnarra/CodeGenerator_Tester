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
from core import AIEngine, Generator, ErrorHandler, FileManager
from core.file_manager import DockerSandbox

# Page configuration
st.set_page_config(
    page_title="DevelopmentAssistant.ai by WL Labs",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling (blue theme)
st.markdown("""
<style>
    :root {
        --primary-700: #0d47a1;
        --primary-600: #1565c0;
        --primary-500: #1976d2;
        --primary-400: #1e88e5;
        --primary-300: #42a5f5;
        --surface: #f5f8ff;
        --card: #ffffff;
        --text-900: #0f172a;
        --text-700: #334155;
        --text-500: #64748b;
    }

    .main-hero {
        background: linear-gradient(135deg, var(--primary-700), var(--primary-500));
        color: #fff;
        padding: 24px 28px;
        border-radius: 14px;
        margin: 8px 0 24px 0;
        box-shadow: 0 6px 20px rgba(13, 71, 161, 0.25);
        text-align: center;
    }
    .main-hero h1 {
        margin: 0;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: 0.2px;
    }
    .main-hero p {
        margin: 6px 0 0 0;
        font-size: 0.98rem;
        color: rgba(255,255,255,0.9);
    }

    .feature-card {
        background-color: var(--card);
        padding: 16px;
        border-radius: 12px;
        margin: 10px 0;
        border: 1px solid rgba(25, 118, 210, 0.12);
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }
    .success-box {
        background: #eaf2ff;
        border: 1px solid #cfe0ff;
        border-radius: 10px;
        padding: 14px;
        margin: 12px 0;
    }
    .warning-box {
        background: #f3f6fc;
        border: 1px solid #e2e8f5;
        border-radius: 10px;
        padding: 14px;
        margin: 12px 0;
    }
    .upload-area {
        border: 2px dashed rgba(25, 118, 210, 0.35);
        border-radius: 12px;
        padding: 22px;
        text-align: center;
        background-color: #f8fbff;
    }
    .tech-stack-card {
        background-color: #e3f2fd;
        border: 1px solid #bbdefb;
        border-radius: 10px;
        padding: 14px;
        margin: 10px 0;
    }
    body {
        background-color: var(--surface);
        font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
        color: var(--text-900);
    }
    .stButton>button {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, var(--primary-600), var(--primary-400));
        color: #fff;
        border: 0;
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.35);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, var(--primary-700), var(--primary-500));
    }

    /* Tabs styling */
    div[role="tablist"] > div {
        background: #ffffff;
        border: 1px solid rgba(25, 118, 210, 0.12) !important;
        color: var(--text-700) !important;
        border-radius: 10px 10px 0 0 !important;
        margin-right: 6px;
        padding: 6px 10px !important;
    }
    div[role="tablist"] > div[aria-selected="true"] {
        border-bottom: 3px solid var(--primary-500) !important;
        color: var(--primary-600) !important;
        font-weight: 700 !important;
        background: linear-gradient(180deg, rgba(30,136,229,0.08), rgba(30,136,229,0.02));
    }

    /* Streamlit UI kit overrides to enforce blue */
    .stRadio > label, .stCheckbox > label, .stSlider > label {
        color: var(--text-900) !important;
    }
    .stRadio div[role='radiogroup'] > label[data-baseweb='radio'] svg, .stCheckbox svg {
        fill: var(--primary-500) !important;
        color: var(--primary-500) !important;
    }
    .stRadio div[role='radiogroup'] input:checked + div svg {
        fill: var(--primary-600) !important;
        color: var(--primary-600) !important;
    }
    /* Slider */
    .stSlider [data-baseweb='slider'] div[role='slider'] {
        background: var(--primary-500) !important;
        border-color: var(--primary-500) !important;
    }
    .stSlider [data-baseweb='slider'] div[role='slider']::after {
        background: var(--primary-600) !important;
    }

    /* Force blue accents for radios, checkboxes, sliders, toggles */
    :root {
        --primary-color: #1e88e5; /* Streamlit theme var */
    }
    input[type="radio"], input[type="checkbox"], input[type="range"] {
        accent-color: var(--primary-500) !important;
    }
    /* Baseweb (used by Streamlit) specific radio/slider overrides */
    /* Radio */
    .stRadio [data-baseweb='radio']>div:first-child {
        border-color: var(--primary-500) !important;
    }
    .stRadio [data-baseweb='radio'][aria-checked='true']>div:first-child {
        background-color: var(--primary-500) !important;
        border-color: var(--primary-500) !important;
    }
    .stRadio [data-baseweb='radio'] svg {
        color: var(--primary-500) !important;
        fill: var(--primary-500) !important;
    }
    [data-baseweb="slider"] div[role="slider"], [data-baseweb="slider"] div[role="slider"]::before {
        background-color: var(--primary-500) !important;
        border-color: var(--primary-500) !important;
    }
    [data-baseweb="slider"] div[aria-valuenow] {
        color: var(--text-700) !important;
    }
    /* Slider track colors */
    .stSlider [data-baseweb='slider']>div:first-child {
        background-color: rgba(30,136,229,0.25) !important; /* base track */
    }
    .stSlider [data-baseweb='slider']>div:nth-child(2) {
        background-color: var(--primary-500) !important; /* active track */
    }
    .stSlider span, .stSlider label {
        color: var(--text-700) !important; /* numbers under slider */
    }
    [role="switch"], [data-baseweb="switch"] {
        border-color: rgba(25,118,210,0.35) !important;
    }
    [role="switch"][aria-checked="true"], [data-baseweb="switch"] [aria-checked="true"] {
        background-color: var(--primary-500) !important;
        border-color: var(--primary-500) !important;
    }

    /* Tabs highlight bar (BaseWeb) */
    .stTabs [data-baseweb='tab-highlight'] {
        background-color: var(--primary-500) !important;
    }

    /* Badges and chips */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background: rgba(25,118,210,0.12);
        color: #0d47a1;
        border: 1px solid rgba(25,118,210,0.25);
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge.ok { background: rgba(25,118,210,0.12); color: #0d47a1; border-color: rgba(25,118,210,0.25); }
    .badge.warn { background: rgba(25,118,210,0.08); color: #0f172a; border-color: rgba(25,118,210,0.18); }

    .kpi-card {
        background: #ffffff;
        border: 1px solid rgba(25,118,210,0.12);
        border-radius: 12px;
        padding: 12px 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        text-align: center;
    }
    .kpi-card .label { color: var(--text-500); font-size: 12px; }
    .kpi-card .value { color: var(--primary-600); font-size: 22px; font-weight: 800; }
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
        'generator': Generator(),
        'error_handler': ErrorHandler(),
        'file_manager': FileManager()
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
            # Skip macOS metadata files and hidden files
            if f.endswith('.py') and not f.startswith('._') and not f.startswith('.DS_Store'):
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
                array_str = cleaned_response[start_idx:end_idx]
                # Remove any extra data after the last closing bracket
                array_str = array_str[:array_str.rfind(']')+1]
                result = json.loads(array_str)
                
                # Validate the structure
                if isinstance(result, list) and len(result) > 0:
                    return result
                else:
                    st.error("Invalid tech stack response structure")
                    return []
            else:
                # Try parsing the entire response as JSON
                result = json.loads(cleaned_response)
                if isinstance(result, list) and len(result) > 0:
                    return result
                else:
                    st.error("Response is not a valid JSON array")
                    return []
                    
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse tech stack response as JSON: {str(e)}")
            st.error("Raw response preview:")
            st.code(response[:500] + "..." if len(response) > 500 else response)
            st.error("AI model failed to generate valid tech stack suggestions. Please try again.")
            return []
            
    except Exception as e:
        st.error(f"Error generating tech stack suggestions: {str(e)}")
        return []



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
                object_str = cleaned_response[start_idx:end_idx]
                # Remove any extra data after the last closing brace
                object_str = object_str[:object_str.rfind('}')+1]
                result = json.loads(object_str)
                
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

# Helper to render per-tab header (minimal, professional)
def render_tab_hero(title, badges, subtitle):
    try:
        chips = ''.join([f"<span class='chip'>{b}</span>" for b in badges])
        st.markdown(f"<div class='header-bar'><h1>{title}</h1><p>{chips}{subtitle}</p></div>", unsafe_allow_html=True)
    except Exception:
        pass

# Main application
def main():
    # Per-tab hero is rendered inside each tab
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("""
            <div style='padding: 18px 16px 12px 16px; background: linear-gradient(135deg, #1e3a8a, #1d4ed8); border-radius: 14px; box-shadow: 0 6px 20px rgba(13, 71, 161, 0.25); margin-bottom: 18px; color: #fff;'>
                <h3 style='margin-bottom: 8px;'>Configuration</h3>
                <p style='font-size: 0.95em; opacity: 0.9; margin-bottom: 16px;'>
                    Pick a model and tune responses. Defaults work well for most cases.
                </p>
        """, unsafe_allow_html=True)

        # Model selection
        model = st.selectbox(
            "AI Model",
            ["Gemini 2.5 Pro", "gpt-4o-mini", "gpt-4o", "Claude-Opus-4", "Grok-4"],
            index=0,
            help="Choose the AI model for code and test generation."
        )
        # Subtle status line in blue theme (replaces red default accents on some themes)
        st.markdown("<div style='height:6px;border-radius:6px;background:linear-gradient(90deg,#1e88e5,#42a5f5);margin:6px 0 10px 0;'></div>", unsafe_allow_html=True)

        # Temperature setting
        st.markdown("<div style='color:#0f172a;font-weight:600;margin-top:6px;margin-bottom:2px;'>Creativity</div>", unsafe_allow_html=True)
        temperature = st.slider(
            "",
            0.0, 1.0, 0.7, 0.1,
            help="Lower = deterministic, Higher = more creative."
        )

        # Max tokens
        st.markdown("<div style='color:#0f172a;font-weight:600;margin-top:6px;margin-bottom:2px;'>Response Length</div>", unsafe_allow_html=True)
        max_tokens = st.slider(
            "",
            1000, 4000, 2000, 500,
            help="Maximum tokens in the AI's response."
        )

        st.markdown("""
            <div style='font-size: 0.92em; color: rgba(255,255,255,0.9); margin-top: 10px;'>
                <b>Tip:</b> Defaults are sensible. Raise tokens for long outputs.
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
    tab1, tab_test_gen, tab_dev, tab_onboard, tab5 = st.tabs([
        "Code Generation",
        "Test Generator",
        "Developer",
        "On Boarding",
        "File Manager"
    ])
    


    # Tab 1: Code Generation
    with tab1:
        render_tab_hero(
            "Code Generation",
            ["Gemini", "GPT-4o", "Claude", "Docker"],
            "From idea to runnable code — with self-healing."
        )
        st.header("Code Generation")
        st.caption("Turn requirements into runnable code with self-healing and tests.")
        
        # Upload section for code generation
        st.subheader("Requirements")
        uploaded_file = st.file_uploader(
            "Upload PDF/DOCX/TXT/MD/CSV or a project ZIP",
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
            st.subheader("Action")
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
                                        st.subheader("Project Structure")
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
                                        st.error("AI generation failed. Please try again with different parameters or check your API configuration.")
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
                                        

                                        
                                        # Ensure we have requirements.txt (check common locations)
                                        requirements_found = False
                                        for req_file in ['requirements.txt', 'requirements.txt.txt', 'requirements.txt.txt.txt']:
                                            if req_file in project_files:
                                                requirements_found = True

                                                break
                                        
                                        if not requirements_found:
                                            st.warning("No requirements.txt found in generated files")
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
                                        st.subheader("Final Files")
                                        for fname, content in healing_result['final_files'].items():
                                            with st.expander(fname, expanded=False):
                                                st.code(content, language='python' if fname.endswith('.py') else 'text')
                                        st.subheader("Output")
                                        st.code(healing_result['output'])
                                        st.subheader("Errors")
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
                            st.subheader("Final Files")
                            for fname, content in healing_result['final_files'].items():
                                with st.expander(fname, expanded=False):
                                    st.code(content, language='python' if fname.endswith('.py') else 'text')
                            st.subheader("Output")
                            st.code(healing_result['output'])
                            st.subheader("Errors")
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
        render_tab_hero(
            "File Manager",
            ["ZIP Export", "Preview", "History"],
            "Browse, preview, and export artifacts."
        )
        st.header("Files")
        st.caption("Preview, export, and manage outputs.")
        
        if st.session_state.generated_files:
            st.subheader("Generated Files")
            
            # File statistics as KPI cards
            file_types = {}
            for file_info in st.session_state.generated_files:
                file_type = file_info['type']
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"<div class='kpi-card'><div class='label'>Code Files</div><div class='value'>{file_types.get('code', 0)}</div></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='kpi-card'><div class='label'>Test Files</div><div class='value'>{file_types.get('test', 0)}</div></div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div class='kpi-card'><div class='label'>Assessments</div><div class='value'>{file_types.get('assessment', 0)}</div></div>", unsafe_allow_html=True)
            with c4:
                st.markdown(f"<div class='kpi-card'><div class='label'>Total Files</div><div class='value'>{len(st.session_state.generated_files)}</div></div>", unsafe_allow_html=True)
            
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
        render_tab_hero(
            "Test Generator",
            ["pytest", "Coverage", "Agents"],
            "Design robust tests — faster."
        )
        
        # Test Generation Mode Selection
        test_mode = st.radio(
            "Test Generation Mode",
            ["Code-Based Tests", "Requirements-Based Tests"],
            help="Choose whether to generate tests from existing code or from requirements specifications"
        )
        
        # Model selection for test generation
        test_model = st.selectbox(
            "AI Model for Test Generation",
            ["Gemini 2.5 Pro", "gpt-4o-mini", "gpt-4o", "Claude-Opus-4", "Grok-4"],
            index=0,
            help="Choose the AI model for test generation."
        )
        
        # Check API keys
        if test_model == "Claude-Opus-4" and not os.environ.get("CLAUDE_API_KEY"):
            st.warning("⚠️ Claude API key not found. Please set CLAUDE_API_KEY in your environment.")
        elif test_model == "Grok-4" and not os.environ.get("GROK4_API_KEY"):
            st.warning("⚠️ Grok-4 API key not found. Please set GROK4_API_KEY in your environment.")
        
        # Test-specific upload area
        if test_mode == "Code-Based Tests":
            # File uploader for code-based testing
            uploaded_files = st.file_uploader(
                "Upload Python files or project ZIP to generate unit tests",
                type=['py', 'zip'],
                accept_multiple_files=True,
                help="Upload Python files (.py) or project ZIP to generate comprehensive unit tests"
            )
        else:
            # File uploader for requirements-based testing
            uploaded_files = st.file_uploader(
                "Upload requirements documents to generate test cases",
                type=['pdf', 'docx', 'doc', 'txt', 'md', 'csv'],
                accept_multiple_files=True,
                help="Upload requirements documents (PDF, DOCX, TXT, MD, CSV) to generate comprehensive test cases"
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
                if test_mode == "Requirements-Based Tests":
                    # Requirements-based test generation
                    try:
                        all_content = []
                        file_names = []
                        
                        # Process uploaded requirements documents
                        for file in uploaded_files:
                            doc_content = process_uploaded_document(file)
                            if doc_content:
                                all_content.append(f"# Requirements from: {file.name}\n{doc_content}")
                                file_names.append(f"requirements_{file.name}")
                        
                        if all_content:
                            # Combine all content
                            combined_content = "\n\n".join(all_content)
                            
                            # Debug info - removed to reduce verbosity
                            
                            # Build the requirements-based test prompt
                            requirements_prompt = f"""
Generate comprehensive test cases from the following requirements/specifications document.

CRITICAL REQUIREMENTS:
- Generate AT LEAST 100 comprehensive test cases for thorough QA testing
- HEAVILY FOCUS on FUNCTIONAL TESTING (60-70% of test cases) as these are most suitable for automated agentic testing
- Include non-functional, integration, security, performance, and usability tests for complete coverage
- Each test case should have: Test ID, Category, Subcategory, Description, Expected Result, Priority
- Focus on real-world scenarios and user interactions that can be automated
- Consider hardware, software, connectivity, performance, security, and usability aspects
- Prioritize test cases that can be executed by automated testing tools/agents

TEST CASE STRUCTURE:
- Test ID: TC_XXXX format (TC_0001 to TC_0100+)
- Category: Functional (60-70%), Non-Functional, Integration, Security, Performance, Usability, etc.
- Subcategory: Specific area (WiFi, Battery, Camera, App Integration, Bluetooth, GPS, Sensors, etc.)
- Description: Clear, actionable test scenario that can be automated
- Expected Result: What should happen when test passes
- Priority: High, Medium, Low
- Device Type: Mobile, Tablet, Wearable, Smart TV, etc.

FUNCTIONAL TESTING FOCUS AREAS (60-70% of test cases):
- Connectivity: WiFi, Cellular, Bluetooth, GPS, NFC
- Hardware: Camera, Microphone, Speakers, Sensors, Battery
- App Integration: Background apps, Multi-tasking, App switching
- User Interface: Touch response, Gestures, Navigation
- System Functions: Calls, SMS, Email, Notifications
- Media: Audio, Video, Image capture and playback
- Storage: Internal storage, SD card, Cloud sync
- Security: Biometric authentication, App permissions
- Performance: App launch, Response times, Memory usage

Requirements Document:
{combined_content}

IMPORTANT: You MUST respond with ONLY valid JSON. No additional text, no explanations, no markdown formatting.
CRITICAL: All property names MUST be enclosed in double quotes. All string values MUST be enclosed in double quotes.
Example: "test_id": "TC_0001" (NOT test_id: TC_0001)

Generate comprehensive test cases in this EXACT JSON format:
{{
    "test_cases": [
        {{
            "test_id": "TC_0001",
            "category": "Functional",
            "subcategory": "WiFi",
            "device_type": "Mobile Device",
            "description": "Test WiFi maintains stable connection during phone calls",
            "expected_result": "WiFi connection remains stable, no disconnection during calls",
            "priority": "High"
        }},
        {{
            "test_id": "TC_0002", 
            "category": "Functional",
            "subcategory": "Audio Integration",
            "device_type": "Mobile Device",
            "description": "Test YouTube video playback when incoming call arrives",
            "expected_result": "Video pauses, call audio takes priority, no audio overlap",
            "priority": "Medium"
        }},
        {{
            "test_id": "TC_0003",
            "category": "Functional",
            "subcategory": "Camera",
            "device_type": "Mobile Device", 
            "description": "Test camera app opens and captures photo within 3 seconds",
            "expected_result": "Camera app launches quickly and photo is saved successfully",
            "priority": "High"
        }}
    ]
}}

Generate AT LEAST 100 test cases with 60-70% being functional tests suitable for automated agentic testing.

Respond with ONLY the JSON object:
"""
                            
                            # Add custom prompt if provided
                            if custom_prompt.strip():
                                full_prompt = requirements_prompt + f"\n\nAdditional Requirements:\n{custom_prompt}"
                            else:
                                full_prompt = requirements_prompt
                            
                            # Generate test cases
                            try:
                                with st.spinner("Generating comprehensive test cases from requirements..."):
                                    if test_model == "Grok-4":
                                        ai_response = generate_with_grok(full_prompt)
                                        test_result = {"success": True, "test_code": ai_response}
                                    elif test_model == "Claude-Opus-4":
                                        ai_response = generate_with_claude(full_prompt, model_name="claude-opus-4-20250514")
                                        test_result = {"success": True, "test_code": ai_response}
                                    else:
                                        # Use AI engine for other models
                                        ai_response = components['ai_engine'].generate_response(full_prompt, model=test_model)
                                        test_result = {"success": True, "test_code": ai_response}
                                
                                if test_result['success']:
                                    # Try to parse JSON response
                                    try:
                                        # Extract JSON from response (handle markdown formatting)
                                        response_text = test_result['test_code']
                                        
                                        # Try to find JSON in the response
                                        extracted_text = None
                                        
                                        # Look for JSON code blocks
                                        if '```json' in response_text:
                                            block_start = response_text.find('```json') + 7
                                            block_end = response_text.find('```', block_start)
                                            extracted_text = response_text[block_start:block_end].strip()
                                        elif '```' in response_text:
                                            block_start = response_text.find('```') + 3
                                            block_end = response_text.find('```', block_start)
                                            extracted_text = response_text[block_start:block_end].strip()
                                        else:
                                            # Try to find JSON object in the text
                                            object_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                                            if object_match:
                                                extracted_text = object_match.group(0)
                                            else:
                                                extracted_text = response_text
                                        
                                        # Clean up common JSON formatting issues
                                        if extracted_text:
                                            # Remove any leading/trailing text that's not JSON
                                            extracted_text = re.sub(r'^[^{]*', '', extracted_text)
                                            extracted_text = re.sub(r'[^}]*$', '', extracted_text)
                                            
                                            # More aggressive JSON cleaning
                                            # Fix common AI formatting issues
                                            
                                            # First, fix unquoted property names (this is the main issue)
                                            extracted_text = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', extracted_text)
                                            
                                            # Fix common AI formatting issues
                                            extracted_text = re.sub(r'(\w+):', r'"\1":', extracted_text)  # Add quotes to keys
                                            extracted_text = re.sub(r':\s*([^",\{\}\[\]\s][^,\{\}\[\]]*[^",\{\}\[\]\s])\s*([,\}\]])', r': "\1"\2', extracted_text)  # Add quotes to string values
                                            extracted_text = re.sub(r',\s*}', '}', extracted_text)  # Remove trailing commas
                                            extracted_text = re.sub(r',\s*]', ']', extracted_text)  # Remove trailing commas in arrays
                                            
                                            # Additional fixes for common AI issues
                                            extracted_text = re.sub(r'(["\w])\s*,\s*(["\w])', r'\1,\2', extracted_text)  # Fix spacing around commas
                                            extracted_text = re.sub(r'}\s*,\s*{', '},{', extracted_text)  # Fix object separators
                                            extracted_text = re.sub(r']\s*,\s*{', '},{', extracted_text)  # Fix array-object separators
                                            extracted_text = re.sub(r'}\s*,\s*\[', '},[', extracted_text)  # Fix object-array separators
                                            
                                            # Fix missing quotes around string values
                                            extracted_text = re.sub(r':\s*([^",\{\}\[\]\s][^,\{\}\[\]]*[^",\{\}\[\]\s])\s*([,\}\]])', r': "\1"\2', extracted_text)
                                            
                                            # Fix unclosed quotes in string values
                                            extracted_text = re.sub(r':\s*"([^"]*?)(?=\s*[,}\]])', r': "\1"', extracted_text)
                                            
                                            # Fix escaped quotes and other common issues
                                            extracted_text = extracted_text.replace('\\"', '"')  # Fix escaped quotes
                                            extracted_text = extracted_text.replace('""', '"')   # Fix double quotes
                                            
                                            # Try to fix unclosed quotes
                                            quote_count = extracted_text.count('"')
                                            if quote_count % 2 != 0:
                                                # Add missing quote at the end
                                                extracted_text += '"'
                                            
                                            # Additional cleaning for common AI mistakes
                                            extracted_text = re.sub(r'([^"])\s*,\s*([^"])', r'\1,\2', extracted_text)  # Fix spacing around commas
                                            extracted_text = re.sub(r'}\s*,\s*{', '},{', extracted_text)  # Fix object separators
                                            extracted_text = re.sub(r']\s*,\s*{', '},{', extracted_text)  # Fix array-object separators
                                            extracted_text = re.sub(r'}\s*,\s*\[', '},[', extracted_text)  # Fix object-array separators
                                            
                                            # Remove any remaining problematic characters
                                            extracted_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', extracted_text)  # Remove control characters
                                            
                                            # Final cleanup - ensure proper JSON structure
                                            extracted_text = re.sub(r',\s*([}\]])', r'\1', extracted_text)  # Remove trailing commas before closing brackets
                                        
                                        # Try to parse the cleaned JSON
                                        try:
                                            test_data = json.loads(extracted_text)
                                        except json.JSONDecodeError as inner_e:
                                            # Show debug info for JSON parsing issues
                                            st.warning(f"JSON parsing failed: {inner_e}")
                                            st.info("Attempting to extract test cases array...")
                                            
                                            # Show the cleaned JSON for debugging (first 1000 chars)
                                            st.info("Debug: First 1000 characters of cleaned JSON:")
                                            st.code(extracted_text[:1000], language='json')
                                            # If still failing, try to extract just the test_cases array
                                            # Look for test_cases array specifically
                                            test_cases_match = re.search(r'"test_cases"\s*:\s*\[(.*?)\]', extracted_text, re.DOTALL)
                                            if test_cases_match:
                                                test_cases_text = test_cases_match.group(1)
                                                # Try to parse individual test case objects
                                                test_case_matches = re.findall(r'\{[^{}]*\}', test_cases_text)
                                                test_cases = []
                                                
                                                for i, test_case_text in enumerate(test_case_matches):
                                                    try:
                                                        # Clean up the test case text
                                                        cleaned_case = re.sub(r'(\w+):', r'"\1":', test_case_text)
                                                        cleaned_case = re.sub(r':\s*([^",\{\}\[\]\s][^,\{\}\[\]]*[^",\{\}\[\]\s])\s*([,\}\]])', r': "\1"\2', cleaned_case)
                                                        cleaned_case = re.sub(r',\s*}', '}', cleaned_case)
                                                        
                                                        case_data = json.loads(cleaned_case)
                                                        case_data['test_id'] = case_data.get('test_id', f'TC_{i+1:04d}')
                                                        test_cases.append(case_data)
                                                    except (json.JSONDecodeError, ValueError, KeyError):
                                                        continue
                                                
                                                if test_cases:
                                                    test_data = {'test_cases': test_cases}
                                                else:
                                                    raise inner_e
                                            else:
                                                # Try one more approach - look for individual test case objects
                                                test_case_objects = re.findall(r'\{[^{}]*"test_id"[^{}]*\}', extracted_text, re.DOTALL)
                                                if test_case_objects:
                                                    test_cases = []
                                                    for i, obj in enumerate(test_case_objects):
                                                        try:
                                                            # Clean up the object
                                                            cleaned_obj = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', obj)
                                                            cleaned_obj = re.sub(r':\s*([^",\{\}\[\]\s][^,\{\}\[\]]*[^",\{\}\[\]\s])\s*([,\}\]])', r': "\1"\2', cleaned_obj)
                                                            cleaned_obj = re.sub(r',\s*}', '}', cleaned_obj)
                                                            
                                                            case_data = json.loads(cleaned_obj)
                                                            test_cases.append(case_data)
                                                        except (json.JSONDecodeError, ValueError, KeyError):
                                                            continue
                                                    
                                                    if test_cases:
                                                        test_data = {'test_cases': test_cases}
                                                    else:
                                                        raise inner_e
                                                else:
                                                    raise inner_e
                                        
                                        # Display test cases in a table
                                        st.subheader("Generated Test Cases")
                                        
                                        # Create a DataFrame for better display
                                        import pandas as pd
                                        test_cases = test_data.get('test_cases', [])
                                        if test_cases:
                                            df = pd.DataFrame(test_cases)
                                            st.dataframe(df, use_container_width=True)
                                            
                                            # Export to Excel
                                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                            excel_filename = f"test_cases_{timestamp}.xlsx"
                                            
                                            # Create Excel file with formatting
                                            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                                                df.to_excel(writer, sheet_name='Test Cases', index=False)
                                                
                                                # Auto-adjust column widths
                                                worksheet = writer.sheets['Test Cases']
                                                for column in worksheet.columns:
                                                    max_length = 0
                                                    column_letter = column[0].column_letter
                                                    for cell in column:
                                                        try:
                                                            if len(str(cell.value)) > max_length:
                                                                max_length = len(str(cell.value))
                                                        except (TypeError, AttributeError):
                                                            pass
                                                    adjusted_width = min(max_length + 2, 50)
                                                    worksheet.column_dimensions[column_letter].width = adjusted_width
                                            
                                            # Download buttons
                                            col1, col2 = st.columns(2)
                                            with col1:
                                                with open(excel_filename, 'rb') as f:
                                                    st.download_button(
                                                        "Download Excel File",
                                                        f.read(),
                                                        file_name=excel_filename,
                                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                                    )
                                            
                                            with col2:
                                                # Also provide JSON download
                                                test_cases_filename = f"test_cases_{timestamp}.json"
                                                st.download_button(
                                                    "Download JSON File",
                                                    json.dumps(test_data, indent=2),
                                                    file_name=test_cases_filename,
                                                    mime="application/json"
                                                )
                                            
                                            # Save to session state
                                            st.session_state.generated_files.append({
                                                'name': excel_filename,
                                                'path': os.path.abspath(excel_filename),
                                                'type': 'test_cases',
                                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            })
                                            
                                            st.success(f"✅ Generated {len(test_cases)} test cases successfully!")
                                            
                                        else:
                                            st.warning("No test cases found in the response")
                                            
                                    except json.JSONDecodeError as e:
                                        st.error(f"Failed to parse JSON response: {e}")
                                        st.info("Attempting to generate test cases from raw response...")
                                        
                                        # Enhanced fallback parsing logic
                                        try:
                                            # Try to extract test cases from the raw response
                                            response_text = test_result['test_code']
                                            test_cases = []
                                            
                                            # Look for patterns like "TC_XXXX" or test case structures
                                            lines = response_text.split('\n')
                                            current_case = {}
                                            
                                            for line in lines:
                                                line = line.strip()
                                                if not line:
                                                    continue
                                                
                                                # Try to parse CSV-like format
                                                if line.count(',') >= 5 and '"' in line:
                                                    # Handle malformed CSV with extra quotes and commas
                                                    import re
                                                    
                                                    # Remove leading numbers and tabs
                                                    line = re.sub(r'^[0-9\s\t]*', '', line)
                                                    
                                                    # Extract quoted fields using regex
                                                    quoted_pattern = r'"([^"]*(?:\\"[^"]*)*)"'
                                                    matches = re.findall(quoted_pattern, line)
                                                    
                                                    # Clean each quoted match
                                                    valid_fields = []
                                                    for match in matches:
                                                        # Handle escaped quotes
                                                        cleaned = match.replace('\\"', '"')
                                                        # Remove any remaining artifacts
                                                        cleaned = re.sub(r'^[0-9\s\t]*', '', cleaned)
                                                        cleaned = re.sub(r'["\']+$', '', cleaned)
                                                        cleaned = cleaned.strip()
                                                        
                                                        if cleaned and len(cleaned) > 1:
                                                            valid_fields.append(cleaned)
                                                    
                                                    # If we don't have enough fields, try splitting by comma
                                                    if len(valid_fields) < 6:
                                                        parts = line.split(',')
                                                        valid_fields = []
                                                        
                                                        for part in parts:
                                                            # Remove quotes and extra whitespace
                                                            cleaned = part.strip().strip('"').strip("'")
                                                            # Remove artifacts
                                                            cleaned = re.sub(r'^[0-9\s\t]*["\']*', '', cleaned)
                                                            cleaned = re.sub(r'["\']*[0-9\s\t]*$', '', cleaned)
                                                            cleaned = re.sub(r'\s+', ' ', cleaned)
                                                            cleaned = cleaned.replace('\\"', '"').replace('""', '"')
                                                            # Remove commas and quotes
                                                            cleaned = re.sub(r'^[,\s]*', '', cleaned)
                                                            cleaned = re.sub(r'[,\s]*$', '', cleaned)
                                                            cleaned = re.sub(r'["\']+', '', cleaned)
                                                            cleaned = cleaned.strip()
                                                            
                                                            if cleaned and cleaned != ',' and len(cleaned) > 1:
                                                                valid_fields.append(cleaned)
                                                    
                                                    if len(valid_fields) >= 6:
                                                        test_case = {
                                                            'test_id': valid_fields[0] if len(valid_fields) > 0 else f'TC_{len(test_cases)+1:04d}',
                                                            'category': valid_fields[1] if len(valid_fields) > 1 else 'Functional',
                                                            'subcategory': valid_fields[2] if len(valid_fields) > 2 else 'General',
                                                            'device_type': valid_fields[3] if len(valid_fields) > 3 else 'Mobile Device',
                                                            'description': valid_fields[4] if len(valid_fields) > 4 else 'Test case',
                                                            'expected_result': valid_fields[5] if len(valid_fields) > 5 else 'Expected result',
                                                            'priority': valid_fields[6] if len(valid_fields) > 6 else 'Medium'
                                                        }
                                                        test_cases.append(test_case)
                                                        continue
                                                
                                                # Try to parse key-value format
                                                if ':' in line and ('test_id' in line.lower() or 'tc_' in line.lower()):
                                                    if current_case:
                                                        test_cases.append(current_case)
                                                    current_case = {}
                                                    
                                                    # Extract test ID
                                                    if 'test_id' in line.lower() or 'tc_' in line.lower():
                                                        parts = line.split(':', 1)
                                                        if len(parts) == 2:
                                                            test_id = parts[1].strip().strip('"').strip("'")
                                                            current_case['test_id'] = test_id
                                                
                                                elif ':' in line and current_case:
                                                    parts = line.split(':', 1)
                                                    if len(parts) == 2:
                                                        key = parts[0].strip().lower()
                                                        value = parts[1].strip().strip('"').strip("'")
                                                        
                                                        if 'category' in key:
                                                            current_case['category'] = value
                                                        elif 'subcategory' in key:
                                                            current_case['subcategory'] = value
                                                        elif 'description' in key:
                                                            current_case['description'] = value
                                                        elif 'expected' in key and 'result' in key:
                                                            current_case['expected_result'] = value
                                                        elif 'priority' in key:
                                                            current_case['priority'] = value
                                                        elif 'device' in key and 'type' in key:
                                                            current_case['device_type'] = value
                                            
                                            # Add the last case if exists
                                            if current_case:
                                                test_cases.append(current_case)
                                            
                                            if test_cases:
                                                # Create DataFrame and export
                                                import pandas as pd
                                                df = pd.DataFrame(test_cases)
                                                st.subheader("Generated Test Cases (Parsed from Raw Response)")
                                                st.dataframe(df, use_container_width=True)
                                                
                                                # Export to Excel
                                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                                excel_filename = f"test_cases_{timestamp}.xlsx"
                                                
                                                with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                                                    df.to_excel(writer, sheet_name='Test Cases', index=False)
                                                    worksheet = writer.sheets['Test Cases']
                                                    for column in worksheet.columns:
                                                        max_length = 0
                                                        column_letter = column[0].column_letter
                                                        for cell in column:
                                                            try:
                                                                if len(str(cell.value)) > max_length:
                                                                    max_length = len(str(cell.value))
                                                            except:
                                                                pass
                                                        adjusted_width = min(max_length + 2, 50)
                                                        worksheet.column_dimensions[column_letter].width = adjusted_width
                                                
                                                # Download button
                                                with open(excel_filename, 'rb') as f:
                                                    st.download_button(
                                                        "Download Excel File",
                                                        f.read(),
                                                        file_name=excel_filename,
                                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                                    )
                                                
                                                st.success(f"✅ Successfully parsed {len(test_cases)} test cases from raw response!")
                                                
                                                # Save to session state
                                                st.session_state.generated_files.append({
                                                    'name': excel_filename,
                                                    'path': os.path.abspath(excel_filename),
                                                    'type': 'test_cases',
                                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                })
                                            else:
                                                st.error("Could not extract test cases from the raw response")
                                                st.subheader("Raw AI Response")
                                                st.code(test_result['test_code'], language='text')
                                                
                                        except Exception as parse_error:
                                            st.error(f"Failed to extract test cases: {parse_error}")
                                            st.subheader("Raw AI Response")
                                            st.code(test_result['test_code'], language='text')
                                        
                                else:
                                    st.error(f"❌ Test generation failed: {test_result.get('error', 'Unknown error')}")
                                    
                            except Exception as ai_error:
                                st.error(f"AI model error: {ai_error}")
                                
                        else:
                            st.warning("No content found to generate tests for.")
                            
                    except Exception as e:
                        handle_and_display_error(e, "requirements_test_generation")
                else:
                    # Original code-based test generation
                    with st.spinner("Generating code-based test cases..."):
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
                                                except UnicodeDecodeError as e:
                                                    st.warning(f"Could not read {py_file} due to encoding issues (likely a binary or metadata file): {e}")
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
                                
                                # Debug info
                                st.info(f"Processing {len(file_names)} files with {test_model} model")
                                st.info(f"Combined content length: {len(combined_content)} characters")
                            
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

Generate comprehensive Python unit tests using pytest for the following code and requirements.

CRITICAL REQUIREMENTS:
- Generate ONLY actual, working test code - NO placeholders, NO TODOs, NO commented-out code
- Write real test functions with actual assertions and test data
- For each function/class found in the code, create at least 2-3 meaningful test cases
- Include both positive tests (valid inputs) and negative tests (edge cases, invalid inputs)
- Use realistic test data that matches the expected input/output types
- Use pytest-style assertions (assert statements)
- Import the actual functions/classes being tested
- Make tests that would actually run and validate the code functionality

Code to test:
{combined_content}

Generate the complete test file now:
"""
                                
                                # Add custom prompt if provided
                                if custom_prompt.strip():
                                    full_prompt = base_prompt + f"\n\nAdditional Requirements:\n{custom_prompt}"
                                else:
                                    full_prompt = base_prompt
                                
                                # Generate tests
                                try:
                                    st.info(f"🤖 Generating tests with {test_model}...")
                                    
                                    if test_model == "Grok-4":
                                        ai_response = generate_with_grok(full_prompt)
                                        test_result = {"success": True, "test_code": ai_response}
                                    elif test_model == "Claude-Opus-4":
                                        ai_response = generate_with_claude(full_prompt, model_name="claude-opus-4-20250514")
                                        test_result = {"success": True, "test_code": ai_response}
                                    else:
                                        # Use AI engine for other models
                                        ai_response = components['ai_engine'].generate_response(full_prompt, model=test_model)
                                        test_result = {"success": True, "test_code": ai_response}
                                    
                                    # Validate the response
                                    if not test_result.get("test_code") or len(test_result["test_code"].strip()) < 100:
                                        st.warning("⚠️ AI response seems too short. Falling back to basic test generator.")
                                        test_result = components['test_generator'].generate_tests(combined_content, language='python')
                                        
                                except Exception as ai_error:
                                    st.error(f"AI model error: {ai_error}")
                                    st.info("🔄 Falling back to basic test generator...")
                                    # Fallback to basic test generator
                                    test_result = components['test_generator'].generate_tests(combined_content, language='python')
                                
                                if test_result['success']:
                                    test_code = test_result['test_code']
                                    
                                    # Check if the generated code looks like a template
                                    if "TODO" in test_code or "placeholder" in test_code.lower():
                                        st.warning("⚠️ Generated code appears to be a template. This might indicate an AI model issue.")
                                    
                                    st.success("✅ Tests generated successfully!")
                                    
                                    # Display results
                                    st.subheader("📋 Generated Test Code")
                                    st.code(test_code, language='python')
                                    
                                    # File information
                                    st.subheader("📁 Files Processed")
                                    for file_name in file_names:
                                        st.write(f"• {file_name}")
                                    
                                    # Download button
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    filename = f"test_generated_{timestamp}.py"
                                    st.download_button(
                                        label="📥 Download Test File",
                                        data=test_code,
                                        file_name=filename,
                                        mime="text/plain"
                                    )
                                    
                                    # Show custom prompt if used
                                    if custom_prompt.strip():
                                        st.subheader("📝 Custom Requirements Used")
                                        st.info(custom_prompt)
                                
                                else:
                                    st.error(f"❌ Test generation failed: {test_result.get('error', 'Unknown error')}")
                            else:
                                st.warning("No content found to generate tests for.")
                        except Exception as e:
                            handle_and_display_error(e, "code_test_generation")
        
        # Tips and guidance - removed to reduce verbosity
    
    # Tab: Developer (feature development on existing code)
    with tab_dev:
        render_tab_hero(
            "Developer",
            ["Claude", "Healing", "Docker"],
            "Ship new features with confidence."
        )
        st.header("Developer")
        st.caption("Implement new features with iterative healing.")

        source_choice = st.radio("Source", ["Upload ZIP/Files", "GitHub URL"], horizontal=True)
        project_files = {}
        repo_url = None

        if source_choice == "Upload ZIP/Files":
            up = st.file_uploader("Upload project ZIP or multiple .py files", type=["zip", "py"], accept_multiple_files=True)
            if up:
                for f in up:
                    if f.name.lower().endswith(".zip"):
                        proj_dir = extract_project_zip(f)
                        if proj_dir:
                            for root, _, files in os.walk(proj_dir):
                                for name in files:
                                    path = os.path.join(root, name)
                                    rel = os.path.relpath(path, proj_dir)
                                    try:
                                        with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                                            project_files[rel] = fp.read()
                                    except Exception:
                                        continue
                    elif f.name.lower().endswith(".py"):
                        try:
                            project_files[f.name] = f.read().decode("utf-8", errors="ignore")
                        except Exception:
                            pass
        else:
            repo_url = st.text_input("GitHub repository URL", placeholder="https://github.com/owner/repo")
            if repo_url and st.button("Fetch Repo"):
                try:
                    import tempfile, subprocess, shutil
                    tmpdir = tempfile.mkdtemp(prefix="repo_")
                    subprocess.run(["git", "clone", "--depth", "1", repo_url, tmpdir], check=True, capture_output=True)
                    for root, _, files in os.walk(tmpdir):
                        for name in files:
                            path = os.path.join(root, name)
                            rel = os.path.relpath(path, tmpdir)
                            # Only load text-like files to avoid binary
                            if any(rel.endswith(ext) for ext in [".py", ".txt", ".md", ".toml", ".cfg", ".ini", ".yaml", ".yml", "requirements.txt", "setup.py", "Pipfile", "pyproject.toml"]):
                                try:
                                    with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                                        project_files[rel] = fp.read()
                                except Exception:
                                    continue
                    shutil.rmtree(tmpdir, ignore_errors=True)
                    st.success("Repository fetched.")
                except Exception as e:
                    handle_and_display_error(e, "github_fetch")

        feature_prompt = st.text_area("Describe the new feature to implement", height=140, placeholder="Add a new endpoint /reports that returns aggregated analytics, update auth, add tests, and update requirements if needed.")
        max_attempts = st.slider("Max healing iterations", 1, 7, 5)
        run_button = st.button("Implement Feature and Run")

        if run_button:
            if not project_files:
                st.warning("Please provide code via upload or GitHub.")
            elif not feature_prompt.strip():
                st.warning("Please describe the feature to implement.")
            else:
                try:
                    # Determine main file
                    main_file = detect_main_file(project_files, use_llm=True) or "main.py"

                    # Ask Claude to implement feature by returning updated files
                    file_blocks = []
                    for fname, content in project_files.items():
                        file_blocks.append(f"<<FILENAME:{fname}>>\n{content}\n<<END>>")
                    files_str = "\n".join(file_blocks)
                    prompt = f"""
You are a senior software engineer. Implement the following feature in the provided project. Modify or add files as needed, including tests and requirements.

FEATURE REQUEST:
{feature_prompt}

PROJECT FILES:
{files_str}

Return ONLY updated and new files in this exact format, for each file:
<<FILENAME:path/filename.ext>>
<file content>
<<END>>
"""
                    claude_resp = generate_with_claude(prompt, model_name="claude-opus-4-20250514", max_tokens=3500)

                    import re
                    pattern = re.compile(r"<<FILENAME:(.*?)>>\n(.*?)<<END>>", re.DOTALL)
                    updates = {m.group(1).strip(): m.group(2) for m in pattern.finditer(claude_resp)}
                    if updates:
                        project_files.update(updates)

                    # Run self-healing loop in Docker
                    result = ai_self_healing_workflow(project_files, code_model="claude-opus-4-20250514", main_file=main_file, max_attempts=max_attempts)

                    if result.get("success"):
                        st.success("Feature implemented and project runs successfully.")
                    else:
                        st.warning("Completed iterations but errors remain. Saving latest files anyway.")

                    # Save final files to File Manager and show
                    for fname, content in result.get("final_files", {}).items():
                        saved = components['file_manager'].save_project_file(feature_prompt, fname, content)
                        st.session_state.generated_files.append({
                            'name': os.path.basename(saved),
                            'path': saved,
                            'type': 'code',
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })

                    st.subheader("Docker Output")
                    st.code(result.get("output", ""))
                    if err := result.get("error"):
                        st.error(err)
                except Exception as e:
                    handle_and_display_error(e, "developer_tab")

    # Tab: On Boarding (generate documentation & diagrams)
    with tab_onboard:
        render_tab_hero(
            "On Boarding",
            ["Docs", "Diagrams", "Insights"],
            "Understand any codebase quickly."
        )
        st.header("Onboarding")
        st.caption("Generate clear docs and flow diagrams.")

        source_choice2 = st.radio("Source", ["Upload ZIP/Files", "GitHub URL"], horizontal=True, key="onboard_src")
        onboard_files = {}
        repo_url2 = None

        if source_choice2 == "Upload ZIP/Files":
            up2 = st.file_uploader("Upload project ZIP or multiple files", type=["zip", "py", "md", "txt"], accept_multiple_files=True, key="onboard_upload")
            if up2:
                for f in up2:
                    if f.name.lower().endswith(".zip"):
                        proj_dir = extract_project_zip(f)
                        if proj_dir:
                            for root, _, files in os.walk(proj_dir):
                                for name in files:
                                    path = os.path.join(root, name)
                                    rel = os.path.relpath(path, proj_dir)
                                    if any(rel.endswith(ext) for ext in [".py", ".md", ".txt", ".toml", ".yaml", ".yml", "requirements.txt", "setup.py", "Pipfile", "pyproject.toml"]):
                                        try:
                                            with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                                                onboard_files[rel] = fp.read()
                                        except Exception:
                                            continue
                    else:
                        try:
                            onboard_files[f.name] = f.read().decode("utf-8", errors="ignore")
                        except Exception:
                            pass
        else:
            repo_url2 = st.text_input("GitHub repository URL", placeholder="https://github.com/owner/repo", key="onboard_repo")
            if repo_url2 and st.button("Fetch Repo", key="onboard_fetch"):
                try:
                    import tempfile, subprocess, shutil
                    tmpdir = tempfile.mkdtemp(prefix="repo_")
                    subprocess.run(["git", "clone", "--depth", "1", repo_url2, tmpdir], check=True, capture_output=True)
                    for root, _, files in os.walk(tmpdir):
                        for name in files:
                            path = os.path.join(root, name)
                            rel = os.path.relpath(path, tmpdir)
                            if any(rel.endswith(ext) for ext in [".py", ".md", ".txt", ".toml", ".yaml", ".yml", "requirements.txt", "setup.py", "Pipfile", "pyproject.toml"]):
                                try:
                                    with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                                        onboard_files[rel] = fp.read()
                                except Exception:
                                    continue
                    shutil.rmtree(tmpdir, ignore_errors=True)
                    st.success("Repository fetched.")
                except Exception as e:
                    handle_and_display_error(e, "onboard_github_fetch")

        doc_prompt_extra = st.text_area("Focus areas (optional)", placeholder="Explain the architecture, modules, data flow, key APIs, setup steps, and how to extend.")
        gen_doc_btn = st.button("Generate Documentation")

        if gen_doc_btn:
            if not onboard_files:
                st.warning("Please provide a project via upload or GitHub.")
            else:
                try:
                    # Build combined context
                    file_blocks = []
                    for fname, content in list(onboard_files.items())[:50]:  # limit to 50 files for prompt size
                        snippet = content if len(content) < 8000 else content[:8000]
                        file_blocks.append(f"<<FILENAME:{fname}>>\n{snippet}\n<<END>>")
                    files_str = "\n\n".join(file_blocks)

                    doc_prompt = f"""
You are a senior developer advocate. Create comprehensive onboarding documentation for the following project with clear sections: Overview, Architecture, Module/Directory Guide, Setup & Run, Development Workflow, Key APIs/Endpoints, Data Flow, Testing, Deployment, and How to Extend. Include concise flow diagrams in Mermaid when useful.

PROJECT FILES (partial):
{files_str}

EXTRA FOCUS (optional): {doc_prompt_extra}

Return ONLY Markdown. Include Mermaid diagrams using ```mermaid blocks when appropriate.
"""
                    doc_markdown = generate_with_claude(doc_prompt, model_name="claude-opus-4-20250514", max_tokens=3500)

                    # Save to assessments/docs
                    filename = f"ONBOARDING_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    saved = components['file_manager'].save_project_file("onboarding", filename, doc_markdown)
                    st.session_state.generated_files.append({
                        'name': os.path.basename(saved),
                        'path': saved,
                        'type': 'assessment',
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                    st.success("Documentation generated and saved to File Manager.")
                    st.subheader("Preview")
                    st.markdown(doc_markdown)
                except Exception as e:
                    handle_and_display_error(e, "onboarding_tab")
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

    while attempt < max_attempts:

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
        
        import re
        file_pattern = re.compile(r"<<FILENAME:(.*?)>>\n(.*?)<<END>>", re.DOTALL)
        new_files = {}
        matches = list(file_pattern.finditer(claude_response))
        
        for match in matches:
            fname, content = match.group(1).strip(), match.group(2).strip()
            new_files[fname] = content
        
        if new_files:
            files.update(new_files)
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