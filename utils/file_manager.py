"""
File Manager utility for handling file operations.
"""

import os
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import re
import subprocess
import tempfile
import shutil
import uuid
import shlex
import hashlib

def sanitize_for_filename(text: str) -> str:
    """Sanitize text for safe filenames: remove newlines, excessive whitespace, and special characters."""
    text = text.replace('/', '_').replace('\\', '_')  # Flatten any directory structure
    text = re.sub(r'\s+', ' ', text)  # Replace all whitespace (including newlines) with single space
    text = re.sub(r'[^a-zA-Z0-9_. -]', '', text)  # Allow dot for extensions
    return text.strip()[:100]

class FileManager:
    """Manages file operations for generated code, tests, and other artifacts."""
    
    def __init__(self, base_dir: str = "generated"):
        self.base_dir = Path(base_dir)
        self.code_dir = self.base_dir / "code"
        self.test_dir = self.base_dir / "tests"
        self.assessment_dir = self.base_dir / "assessments"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all necessary directories exist."""
        for directory in [self.base_dir, self.code_dir, self.test_dir, self.assessment_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def list_generated_files(self) -> Dict[str, List[str]]:
        """List all generated files organized by type."""
        files = {
            "code": [],
            "tests": [],
            "assessments": []
        }
        
        # List code files
        for file_path in self.code_dir.glob("*.py"):
            files["code"].append(str(file_path))
        
        # List test files
        for file_path in self.test_dir.glob("*.py"):
            files["tests"].append(str(file_path))
        
        # List assessment files
        for file_path in self.assessment_dir.glob("*.json"):
            files["assessments"].append(str(file_path))
        
        return files
    
    def get_file_contents(self, file_path: str) -> str:
        """Get contents of a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def get_file_size(self, file_path: str) -> str:
        """Get human-readable file size."""
        try:
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        except Exception:
            return "Unknown"
    
    def create_zip_archive(self, file_list: List[Dict[str, Any]]) -> str:
        """Create a ZIP archive of all generated files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"generated_files_{timestamp}.zip"
        zip_path = self.base_dir / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in file_list:
                if os.path.exists(file_info['path']):
                    # Preserve the full relative path under the code directory
                    try:
                        rel_path = os.path.relpath(file_info['path'], self.code_dir)
                    except ValueError:
                        rel_path = os.path.basename(file_info['path'])
                    zipf.write(file_info['path'], rel_path)
        
        return str(zip_path)
    
    def cleanup_old_files(self, days_old: int = 7):
        """Clean up files older than specified days."""
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        for directory in [self.code_dir, self.test_dir, self.assessment_dir]:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_time = file_path.stat().st_mtime
                    if file_time < cutoff_time:
                        try:
                            file_path.unlink()
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed information about a file."""
        try:
            stat = os.stat(file_path)
            return {
                "name": os.path.basename(file_path),
                "path": file_path,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "type": self._get_file_type(file_path)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type based on extension and content."""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.py':
            if 'test_' in os.path.basename(file_path):
                return 'test'
            else:
                return 'code'
        elif ext == '.json':
            return 'assessment'
        else:
            return 'other' 

    def save_project_file(self, requirement: str, filename: str, content: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_req = sanitize_for_filename(requirement)
        sanitized_filename = sanitize_for_filename(filename)
        # Determine the correct directory based on file type
        if sanitized_filename.endswith(('.py', '.js', '.java', '.cpp', '.c', '.go', '.rs')):
            directory = self.code_dir
        elif sanitized_filename.startswith('test_') or sanitized_filename.endswith('_test.py'):
            directory = self.test_dir
        else:
            directory = self.code_dir
        full_filename = f"{timestamp}_{sanitized_req}_{sanitized_filename}"
        file_path = directory / full_filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(file_path) 

    def save_project_structure_file(self, requirement: str, project_structure: Dict[str, Any]) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_req = sanitize_for_filename(requirement)
        filename = f"project_structure_{timestamp}_{sanitized_req}.json"
        file_path = self.assessment_dir / filename
        structure_data = {
            "requirement": requirement,
            "timestamp": datetime.now().isoformat(),
            "project_structure": project_structure
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(structure_data, f, indent=2, ensure_ascii=False)
        return str(file_path) 

    def save_test_file(self, requirement: str, test_code: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_req = sanitize_for_filename(requirement)
        filename = f"test_{timestamp}_{sanitized_req}.py"
        file_path = self.test_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(test_code)
        return str(file_path) 

class DockerSandbox:
    """Run code in a persistent Docker container for safe execution."""
    def __init__(self, image="python:3.11-slim"):
        self.image = image
        self.container_name = f"sandbox_{uuid.uuid4().hex[:8]}"
        self._container_started = False

    def start_container(self):
        # Check if container is already running
        result = subprocess.run([
            "docker", "ps", "-q", "-f", f"name={self.container_name}"
        ], capture_output=True, text=True)
        if result.stdout.strip():
            self._container_started = True
            return
        # Start the container in detached mode
        subprocess.run([
            "docker", "run", "-dit", "--name", self.container_name, "-w", "/sandbox", self.image, "sleep", "infinity"
        ], check=True)
        self._container_started = True
        # Create /sandbox directory inside the container
        subprocess.run(["docker", "exec", self.container_name, "mkdir", "-p", "/sandbox"], check=True)

    def copy_files_to_container(self, files_dict):
        with tempfile.TemporaryDirectory() as temp_dir:
            for rel_path, content in files_dict.items():
                abs_path = os.path.join(temp_dir, rel_path)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "w") as f:
                    f.write(content)
            # Copy all files into the container's /sandbox
            subprocess.run([
                "docker", "cp", temp_dir + "/.", f"{self.container_name}:/sandbox"
            ], check=True)

    def exec_in_container(self, cmd, timeout=540):
        exec_cmd = ["docker", "exec"] + self._parse_cmd(cmd)
        result = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=timeout)
        return result

    def _parse_cmd(self, cmd):
        if isinstance(cmd, list):
            return [self.container_name] + cmd
        elif isinstance(cmd, str):
            return [self.container_name, "/bin/sh", "-c", cmd]
        else:
            raise ValueError("cmd must be a list or str")

    def stop_container(self):
        subprocess.run(["docker", "rm", "-f", self.container_name], capture_output=True)
        self._container_started = False

    def _hash_file_content(self, content):
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def run_code(self, code: str = None, test_code: str = None, files: dict = None, main_file: str = "main.py", timeout: int = 540) -> dict:
        """
        Run code (and optional test code and extra files) in a persistent Docker container. Returns dict with stdout, stderr, exit_code, and test results.
        If files is provided, it should be a dict of {relative_path: content} for all project files.
        """
        try:
            self.start_container()
            # Prepare files
            requirements_content = None
            if files:
                print(f"DEBUG: Files passed to Docker sandbox: {list(files.keys())}")
                
                # Check for requirements files in multiple common locations and formats
                requirements_files = [
                    'requirements.txt',
                    'requirements.txt.txt',
                    'requirements.txt.txt.txt',
                    'requirements.txt.txt.txt.txt',
                    'requirements.txt.txt.txt.txt.txt',
                    'pyproject.toml',
                    'setup.py',
                    'Pipfile',
                    'poetry.lock'
                ]
                
                requirements_found = False
                requirements_file_used = None
                for req_file in requirements_files:
                    if req_file in files:
                        requirements_content = files[req_file]
                        requirements_file_used = req_file
                        print(f"DEBUG: Found requirements file: {req_file} with content length: {len(requirements_content)}")
                        requirements_found = True
                        break
                
                if not requirements_found:
                    print("WARNING: No requirements.txt found in project files dict!")
                    print(f"Available files: {list(files.keys())}")
                    
                    # Look for any file that might contain requirements
                    potential_req_files = [f for f in files.keys() if 'requirement' in f.lower() or f.endswith('.txt')]
                    if potential_req_files:
                        print(f"DEBUG: Potential requirements files found: {potential_req_files}")
                    
                    # Try to detect dependencies from Python files and create a basic requirements.txt
                    print("DEBUG: Attempting to detect dependencies from Python files...")
                    detected_deps = set()
                    gui_dependencies = set()
                    
                    for filename, content in files.items():
                        if filename.endswith('.py') and isinstance(content, str):
                            # Look for common import patterns
                            import_patterns = [
                                r'^import\s+(\w+)',
                                r'^from\s+(\w+)',
                                r'^\s*import\s+(\w+)',
                                r'^\s*from\s+(\w+)'
                            ]
                            for pattern in import_patterns:
                                import re
                                matches = re.findall(pattern, content, re.MULTILINE)
                                for match in matches:
                                    # Filter out standard library modules
                                    if match not in ['os', 'sys', 'json', 'datetime', 'logging', 'pathlib', 'typing', 're', 'subprocess', 'tempfile', 'shutil', 'uuid', 'hashlib']:
                                        detected_deps.add(match)
                                    
                                    # Check for GUI dependencies
                                    if match in ['tkinter', 'tk', 'gui', 'wx', 'pygame', 'matplotlib']:
                                        gui_dependencies.add(match)
                    
                    if detected_deps:
                        print(f"DEBUG: Detected potential dependencies: {detected_deps}")
                        if gui_dependencies:
                            print(f"DEBUG: Detected GUI dependencies: {gui_dependencies}")
                        
                        # Create a basic requirements.txt
                        requirements_content = "# Auto-detected dependencies\n"
                        for dep in sorted(detected_deps):
                            requirements_content += f"{dep}\n"
                        
                        # Add GUI-specific instructions
                        if gui_dependencies:
                            requirements_content += "\n# GUI dependencies detected - may require system packages\n"
                            requirements_content += "# For tkinter: apt-get install python3-tk\n"
                            requirements_content += "# For matplotlib: apt-get install python3-tk python3-dev\n"
                        
                        print(f"DEBUG: Created auto-detected requirements.txt:\n{requirements_content}")
                        requirements_found = True
                        requirements_file_used = "requirements.txt"
                        # Add it to the files dict so it gets copied to container
                        files["requirements.txt"] = requirements_content
                
                self.copy_files_to_container(files)
            else:
                temp_files = {main_file: code}
                if test_code:
                    temp_files["test_main.py"] = test_code
                # Copy requirements.txt from project root if exists
                project_req = os.path.join(os.getcwd(), "requirements.txt")
                if os.path.exists(project_req):
                    with open(project_req, "r") as f:
                        requirements_content = f.read()
                        temp_files["requirements.txt"] = requirements_content
                self.copy_files_to_container(temp_files)
            # Install requirements if present and changed
            req_path = "/sandbox/requirements.txt"
            hash_path = "/sandbox/.requirements_hash"
            pip_install_result = None
            need_pip_install = False
            
            # Check for GUI dependencies that need system packages
            gui_system_deps_installed = False
            
            # Special handling for Django projects
            if main_file == "manage.py" and requirements_content is not None:
                print("DEBUG: Django project detected, ensuring requirements are installed")
                need_pip_install = True
            
            if files:
                for filename, content in files.items():
                    if filename.endswith('.py') and isinstance(content, str):
                        if 'tkinter' in content or 'import tk' in content:
                            print("DEBUG: GUI dependencies detected, installing system packages...")
                            # Install system packages for GUI support
                            system_cmd = ["sh", "-c", "apt-get update && apt-get install -y python3-tk python3-dev"]
                            system_result = self.exec_in_container(system_cmd, timeout=timeout)
                            if system_result.returncode == 0:
                                print("DEBUG: System GUI packages installed successfully")
                                gui_system_deps_installed = True
                            else:
                                print(f"DEBUG: Failed to install system GUI packages: {system_result.stderr}")
                                # Add a fallback for headless environments
                                print("DEBUG: GUI packages failed to install - this is expected in headless Docker environments")
                            break
            if requirements_content is not None:
                current_hash = self._hash_file_content(requirements_content)
                print(f"DEBUG: Current requirements hash: {current_hash}")
                # Get previous hash from container
                prev_hash_result = self.exec_in_container(["cat", hash_path], timeout=timeout)
                prev_hash = prev_hash_result.stdout.strip() if prev_hash_result.returncode == 0 else None
                print(f"DEBUG: Previous requirements hash: {prev_hash}")
                if prev_hash != current_hash:
                    need_pip_install = True
                    print(f"DEBUG: Hash changed, will install requirements")
                else:
                    print(f"DEBUG: Hash unchanged, but checking if packages are actually installed...")
                    # Check if Django is actually installed
                    django_check = self.exec_in_container(["python", "-c", "import django; print('Django installed')"], timeout=timeout)
                    if django_check.returncode != 0:
                        print(f"DEBUG: Django not installed despite hash match, forcing install")
                        need_pip_install = True
            # Check if requirements.txt exists in container
            check_req = self.exec_in_container(["sh", "-c", f"test -f {req_path} && echo exists"], timeout=timeout)
            print(f"DEBUG: requirements.txt exists check: {check_req.stdout.strip()}")
            print(f"DEBUG: need_pip_install: {need_pip_install}")
            
            # Debug: Show contents of requirements.txt in container
            if check_req.returncode == 0 and "exists" in check_req.stdout:
                req_contents = self.exec_in_container(["cat", req_path], timeout=timeout)
                print(f"DEBUG: Requirements.txt contents in container:\n{req_contents.stdout}")
            if need_pip_install and check_req.returncode == 0:
                # Handle different requirements file formats
                if requirements_file_used and requirements_file_used.endswith('.toml'):
                    pip_cmd = ["pip", "install", "-e", "."]
                elif requirements_file_used and requirements_file_used == 'setup.py':
                    pip_cmd = ["pip", "install", "-e", "."]
                elif requirements_file_used and requirements_file_used == 'Pipfile':
                    pip_cmd = ["pipenv", "install"]
                else:
                    pip_cmd = ["pip", "install", "-r", req_path]
                print("Running Docker exec (pip install):", pip_cmd)
                pip_install_result = self.exec_in_container(pip_cmd, timeout=timeout)
                print("pip install stdout:\n", pip_install_result.stdout)
                print("pip install stderr:\n", pip_install_result.stderr)
                if pip_install_result.returncode != 0:
                    print("pip install failed with exit code", pip_install_result.returncode)
                    return {
                        "stdout": pip_install_result.stdout,
                        "stderr": pip_install_result.stderr,
                        "exit_code": pip_install_result.returncode
                    }
                else:
                    # Store new hash in container
                    self.exec_in_container(["sh", "-c", f"echo '{current_hash}' > {hash_path}"])
                    print("pip install succeeded and hash updated.")
            elif requirements_content is not None and check_req.returncode == 0:
                print("requirements.txt unchanged, skipping pip install.")
                # Debug: Show currently installed packages
                pip_list = self.exec_in_container(["pip", "list"], timeout=timeout)
                print(f"DEBUG: Currently installed packages:\n{pip_list.stdout}")
            else:
                print("No requirements.txt found or file doesn't exist. Skipping pip install.")
            # Check if this is a Flask application
            is_flask_app = False
            if files:
                for filename, content in files.items():
                    if filename.endswith('.py') and isinstance(content, str):
                        if 'from flask import' in content or 'Flask(' in content:
                            is_flask_app = True
                            break
            
            # If test code, run pytest; else, run main.py
            if files and "test_main.py" in files:
                cmd = ["pytest", "test_main.py", "--tb=short"]
            elif test_code:
                cmd = ["pytest", "test_main.py", "--tb=short"]
            else:
                cmd = ["python", main_file]
            
            print("Running Docker exec (main/tests):", cmd)
            
            # Use shorter timeout for Flask apps to prevent hanging
            if is_flask_app:
                flask_timeout = min(60, timeout)  # Max 60 seconds for Flask apps
                print(f"Flask app detected, using shorter timeout: {flask_timeout} seconds")
                result = self.exec_in_container(cmd, timeout=flask_timeout)
            else:
                result = self.exec_in_container(cmd, timeout=timeout)
            print("docker exec stdout:\n", result.stdout)
            print("docker exec stderr:\n", result.stderr)
            
            # Check for GUI-related errors and provide helpful message
            if result.returncode != 0 and ("tkinter" in result.stderr.lower() or "libtk" in result.stderr.lower()):
                result.stderr += "\n\nNOTE: This application requires GUI support which is not available in this Docker environment. "
                result.stderr += "The application was generated as a console-based version to work in this environment."
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            print("Docker command timed out.")
            return {"stdout": "", "stderr": "Execution timed out", "exit_code": 124}
        except Exception as e:
            print("DockerSandbox Exception:", str(e))
            return {"stdout": "", "stderr": str(e), "exit_code": 1} 