# AI-Powered Development Assistant

A comprehensive AI-powered development assistant built with Streamlit that helps with code generation, testing, and project management.

## Features

- **AI-Powered Code Generation**: Generate code using multiple AI models
- **Automated Testing**: Generate and run tests for your code
- **Project Management**: Upload and manage project files
- **Code Analysis**: Analyze code quality and provide suggestions
- **Docker Integration**: Run code in isolated Docker containers

## Architecture

The application follows a clean architecture pattern with clear separation of concerns:

```
app.py (UI Layer)
    ↓
Generator.generate_tests() (Single Source of Truth)
    ↓
AIEngine/ErrorHandler/FileManager (Core Services)
```

### Key Components

- **app.py**: Streamlit UI orchestrator - handles user input, file uploads, and result display
- **Generator**: Single source of truth for test generation with unified API
- **AIEngine**: Handles AI model interactions and prompt management
- **ErrorHandler**: Manages error handling and code analysis
- **FileManager**: Handles file operations and Docker sandbox

### Unified API

The `Generator` class provides a clean, unified API for all test generation:

```python
# Code-based test generation
result = generator.generate_tests(
    code="your source code",
    language="python",
    test_type="unit"
)

# Requirements-based test generation
result = generator.generate_requirements_tests(
    requirements="your requirements text",
    test_count=100
)

# Code generation
result = generator.generate_code(
    requirement="your requirement description",
    language="python"
)
```

All methods return a consistent response format:
```python
{
    "success": bool,
    "test_code": str,  # or "code" for generate_code
    "saved_path": str,
    "analysis": dict,
    "run_results": dict  # for test generation
}
```

## Prerequisites

- Python 3.13 or higher
- Docker (for code execution in containers)
- API keys for AI services (OpenAI, Google AI, etc.)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd AgenticCodeGen&Tester
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root with your API keys:
   ```bash
   # AI Model API Keys (at least one required)
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   CLAUDE_API_KEY=your_claude_api_key_here
   GROK4_API_KEY=your_grok4_api_key_here
   
   # Model Configuration
   DEFAULT_MODEL=gemini-1.5-pro
   FALLBACK_MODEL=gemini-1.5-flash
   TEMPERATURE=0.7
   MAX_TOKENS=4000
   
   # Application Settings
   DEBUG=True
   LOG_LEVEL=INFO
   ```

## API Keys Required

The application requires at least one AI model API key for test generation:

- **Google AI (Gemini)**: Recommended for best performance
  - Get from: https://makersuite.google.com/app/apikey
  - Models: gemini-1.5-pro, gemini-1.5-flash, gemini-pro

- **OpenAI**: Alternative option
  - Get from: https://platform.openai.com/api-keys
  - Models: gpt-4, gpt-4o, gpt-3.5-turbo

- **Claude**: Alternative option
  - Get from: https://console.anthropic.com/
  - Models: claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022

- **Grok-4**: Alternative option
  - Get from: https://console.x.ai/
  - Models: grok-3-latest

**Note**: At least one API key is required for requirements-based test generation to work.

## Running the Application

1. **Activate your virtual environment**:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Start the application**:
   ```bash
   streamlit run app.py
   ```

3. **Access the application**:
   Open your browser and go to: http://localhost:8501

## Stopping the Application

- **In the terminal**: Press `Ctrl+C`
- **Or kill the process**: `pkill -f "streamlit run app.py"`

## Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Google AI API
GOOGLE_API_KEY=your_google_api_key

# Other API keys as needed
```

## Usage

### Test Generation

1. **Code-Based Tests**: Upload Python files or project ZIP files to generate unit tests
2. **Requirements-Based Tests**: Upload requirements documents to generate comprehensive test cases
3. **Custom Requirements**: Add specific test scenarios, edge cases, or testing preferences

### Code Generation

1. **Upload Requirements**: Upload documents or enter requirements text
2. **Generate Code**: Use AI to generate production-ready code
3. **Project Structure**: Generate complete project structures with tech stack recommendations

### File Management

- **Upload Files**: Support for Python files, ZIP projects, and various document formats
- **Download Results**: Export generated tests and code in multiple formats
- **Docker Execution**: Run code in isolated containers for safety

## Project Structure

```
AgenticCodeGen&Tester/
├── app.py                 # Main Streamlit application (UI orchestrator)
├── core/                  # Core functionality modules
│   ├── __init__.py       # Module exports
│   ├── generator.py      # Single source of truth for test generation
│   ├── ai_engine.py      # AI model interactions
│   ├── error_handler.py  # Error handling and analysis
│   └── file_manager.py   # File operations and Docker
├── templates/             # Code templates
├── generated/             # Generated code output
├── requirements.txt       # Python dependencies
├── start.sh              # Startup script
└── README.md             # This file
```

## API Reference

### Generator Class

The main entry point for all generation tasks:

#### `generate_tests(code, language="python", test_type="unit")`
Generate test cases for the given code.

**Parameters:**
- `code` (str): Source code to generate tests for
- `language` (str): Programming language (default: "python")
- `test_type` (str): Type of tests to generate (default: "unit")

**Returns:**
- `success` (bool): Whether generation was successful
- `test_code` (str): Generated test code
- `saved_path` (str): Path to saved test file
- `analysis` (dict): Code analysis results
- `run_results` (dict): Test execution results

#### `generate_requirements_tests(requirements, test_count=100)`
Generate test cases from requirements specifications.

**Parameters:**
- `requirements` (str): Requirements text/specifications
- `test_count` (int): Number of test cases to generate

**Returns:**
- `success` (bool): Whether generation was successful
- `test_cases` (list): List of test case dictionaries
- `saved_path` (str): Path to saved test file
- `analysis` (dict): Analysis results

#### `generate_code(requirement, language="python")`
Generate code from requirement description.

**Parameters:**
- `requirement` (str): Requirement description
- `language` (str): Programming language (default: "python")

**Returns:**
- `success` (bool): Whether generation was successful
- `code` (str): Generated code
- `saved_path` (str): Path to saved code file
- `analysis` (dict): Analysis results

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in the startup command
   ```bash
   streamlit run app.py --server.port 8502
   ```

2. **Docker not running**: Make sure Docker is installed and running

3. **API key errors**: Check your `.env` file and ensure API keys are correct

4. **Import errors**: Make sure all dependencies are installed in the virtual environment

### Getting Help

If you encounter issues:
1. Check that all dependencies are installed correctly
2. Verify your API keys are valid
3. Ensure Docker is running
4. Check the console output for error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License. 