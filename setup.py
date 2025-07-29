#!/usr/bin/env python3
"""
Setup script for AI-Powered Development Assistant
"""

import os
import sys
import subprocess
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version {sys.version.split()[0]} is compatible")

def check_docker():
    """Check if Docker is installed and running."""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Docker is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker is not properly installed")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Docker is not installed or not accessible")
        print("Please install Docker from: https://docs.docker.com/get-docker/")
        return False

def check_docker_daemon():
    """Check if Docker daemon is running."""
    try:
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Docker daemon is running")
            return True
        else:
            print("❌ Docker daemon is not running")
            print("Please start Docker Desktop or Docker daemon")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Cannot connect to Docker daemon")
        return False

def create_directories():
    """Create necessary directories."""
    directories = [
        "generated",
        "generated/code",
        "generated/tests", 
        "generated/assessments",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if not env_file.exists() and env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file and add your API keys")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No .env template found, please create .env file manually")

def install_dependencies():
    """Install Python dependencies."""
    try:
        print("📦 Installing Python dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def run_checks():
    """Run all setup checks."""
    print("🔍 Running setup checks...")
    
    # Check Python version
    check_python_version()
    
    # Check Docker
    docker_installed = check_docker()
    if docker_installed:
        check_docker_daemon()
    else:
        print("⚠️  Docker is required for self-healing functionality")
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    print("\n🎉 Setup checks completed!")

def main():
    """Main setup function."""
    print("🚀 AI-Powered Development Assistant Setup")
    print("=" * 50)
    
    # Run checks
    run_checks()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed due to dependency installation issues")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your API keys")
    print("2. Run: streamlit run app.py")
    print("3. Open your browser to the displayed URL")
    print("\n📚 For more information, see README.md and QUICKSTART.md")

if __name__ == "__main__":
    main()

# Setup configuration for pip install
setup(
    name="ai-powered-dev-assistant",
    version="2.0.0",
    author="AI Development Team",
    author_email="team@example.com",
    description="AI-Powered Development Assistant with 4-stage workflow and self-healing capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-powered-dev-assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Testing",
    "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.28.1",
        "openai>=1.3.7",
        "google-generativeai>=0.3.2",
        "pytest>=7.4.3",
        "black>=23.11.0",
        "flake8>=6.1.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "pandas>=2.1.3",
        "numpy>=1.25.2",
        "jinja2>=3.1.2",
        "markdown>=3.5.1",
        "plotly>=5.17.0",
        "PyPDF2>=3.0.1",
        "python-docx>=0.8.11",
        "docker>=6.1.3",
        "psutil>=5.9.6",
    ],
    extras_require={
        "dev": [
            "pytest-cov>=4.1.0",
            "mypy>=1.7.1",
            "black>=23.11.0",
            "flake8>=6.1.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-dev-assistant=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yml", "*.yaml", "*.json"],
    },
    keywords="ai, code generation, testing, development, automation, streamlit, quality assurance",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ai-powered-dev-assistant/issues",
        "Source": "https://github.com/yourusername/ai-powered-dev-assistant",
        "Documentation": "https://github.com/yourusername/ai-powered-dev-assistant/blob/main/README.md",
    },
) 