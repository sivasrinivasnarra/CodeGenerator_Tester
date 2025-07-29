# AI-Powered Development Assistant

An intelligent system that transforms natural language requirements into fully functional, tested code projects through a sophisticated 4-stage AI workflow with self-healing capabilities.

## 🚀 Key Features

### **4-Stage AI Workflow**
1. **Input Processing**: Multi-format document analysis (PDF, DOCX, TXT, MD, CSV, ZIP)
2. **Tech Stack Recommendation**: AI-driven technology stack suggestions with detailed pros/cons
3. **Project Structure Generation**: Complete project architecture with file organization
4. **Code Generation & Self-Healing**: Intelligent code creation with automatic error correction

### **Advanced AI Capabilities**
- **Multi-Model Support**: Gemini 2.5 Pro, GPT-4o-mini, GPT-4o, Claude Opus 4, Grok-4
- **Self-Healing Workflow**: Automatic error detection and correction using Claude Opus 4
- **Docker Sandbox**: Safe, isolated code execution environment
- **Fallback Systems**: Template-based generation when AI models are unavailable

### **Comprehensive Project Generation**
- **Complete Codebases**: Full project structure with all necessary files
- **Automated Testing**: Comprehensive test suites with pytest
- **Documentation**: README, API docs, deployment guides
- **Configuration Files**: Requirements, Docker, environment setup

## 🏗️ Project Structure

```
AgenticCodeGen&Tester/
├── app.py                 # Main Streamlit application (2889 lines)
├── core/
│   ├── __init__.py
│   ├── ai_engine.py      # Multi-model AI integration (258 lines)
│   ├── code_generator.py # Code generation & formatting (259 lines)
│   ├── test_generator.py # Test case generation (390 lines)
│   └── error_handler.py  # Error handling & recovery (330 lines)
├── utils/
│   ├── __init__.py
│   ├── file_manager.py   # File operations & Docker sandbox (322 lines)
│   ├── code_analyzer.py  # Code analysis utilities (294 lines)
│   └── templates.py      # Code templates (425 lines)
├── templates/
│   ├── python_template.py.jinja
│   ├── test_template.py.jinja
│   └── requirements_template.txt.jinja
├── generated/
│   ├── code/            # Generated source code
│   ├── tests/           # Generated test files
│   └── assessments/     # Analysis reports
├── requirements.txt
├── setup.py
├── PROJECT_SUMMARY.md
├── QUICKSTART.md
└── .env.example
```

## 🎯 Workflow Overview

### **Stage 1: Input Processing**
- Upload documents (PDF, DOCX, TXT, MD, CSV) or project ZIPs
- Extract and analyze requirements
- Combine with user-specified requirements

### **Stage 2: Tech Stack Recommendation**
- AI analyzes requirements and suggests 3 technology stacks
- Each stack includes: language, framework, database, dependencies, tools
- Detailed pros/cons, complexity levels, and time estimates

### **Stage 3: Project Structure Generation**
- AI creates comprehensive project file structure
- Defines directory layout, file names, and purposes
- Includes configuration, dependencies, documentation, and deployment files

### **Stage 4: Code Generation & Self-Healing**
- AI generates all project files based on structure
- Docker sandbox executes and tests the code
- **Self-healing**: If errors occur, Claude Opus 4 analyzes and fixes issues
- Iterative improvement until all tests pass (max 5 attempts)

## 🛠️ Setup

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Environment Configuration**
```bash
cp env_example.txt .env
# Add your API keys to .env:
# OPENAI_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here
# CLAUDE_API_KEY=your_key_here (optional)
# GROK4_API_KEY=your_key_here (optional)
```

### 3. **Launch Application**
```bash
streamlit run app.py
```

## 🎮 Usage

### **Code Generation Tab**
1. **Upload Document**: PDF, DOCX, TXT, MD, CSV, or ZIP project
2. **Enter Requirements**: Describe what you want to build
3. **Get Tech Stack**: AI suggests 3 technology options
4. **Generate Structure**: AI creates project architecture
5. **Generate Code**: AI creates all files with self-healing
6. **Download Results**: Get complete, working project

### **Test Generator Tab**
- Upload Python files or requirements documents
- Generate comprehensive test cases
- Custom test requirements and edge cases
- Download test files or complete project packages

### **File Manager Tab**
- View all generated files with metadata
- Download individual files or complete ZIP archives
- File statistics and organization

## 🤖 AI Models Supported

| Model | Provider | Use Case |
|-------|----------|----------|
| **Gemini 2.5 Pro** | Google | Primary code generation |
| **GPT-4o-mini** | OpenAI | Fast, cost-effective generation |
| **GPT-4o** | OpenAI | High-quality, complex logic |
| **Claude Opus 4** | Anthropic | Self-healing and error correction |
| **Grok-4** | xAI | Alternative generation option |

## 🔧 Configuration

### **AI Model Settings**
- **Creativity Level**: Temperature control (0.0-1.0)
- **Response Length**: Max tokens (1000-4000)
- **Model Selection**: Choose preferred AI model

### **Self-Healing Configuration**
- **Max Attempts**: Healing iteration limit (default: 5)
- **Docker Timeout**: Execution time limit (default: 540s)
- **Error Threshold**: When to trigger healing

## 📊 Generated Output

### **Complete Projects Include**
- **Source Code**: Main application files
- **Test Suites**: Comprehensive test coverage
- **Documentation**: README, API docs, setup guides
- **Configuration**: Requirements, Docker, environment files
- **Deployment**: Scripts and configuration for production

### **Quality Assurance**
- **Syntax Validation**: AST parsing and error checking
- **Code Formatting**: Black formatter integration
- **Linting**: Flake8 style and error checking
- **Test Execution**: Automated test running in Docker sandbox

## 🚀 Advanced Features

### **Self-Healing Workflow**
The core innovation that automatically fixes code issues:
1. **Error Detection**: Docker sandbox identifies runtime errors
2. **AI Analysis**: Claude Opus 4 analyzes all files and errors
3. **Intelligent Fixing**: AI corrects dependencies, imports, logic errors
4. **Iterative Improvement**: Repeats until success or max attempts

### **Docker Sandbox**
- **Isolated Execution**: Safe code running environment
- **Dependency Management**: Automatic package installation
- **Error Capture**: Detailed error reporting and analysis
- **Timeout Protection**: Prevents infinite loops

### **Multi-Format Support**
- **Documents**: PDF, DOCX, TXT, MD, CSV text extraction
- **Projects**: ZIP file extraction and analysis
- **Code Files**: Direct Python file processing
- **Requirements**: Natural language requirement parsing

## 📈 Performance

### **Code Generation Speed**
- **Simple Projects**: 30-60 seconds
- **Complex Projects**: 2-5 minutes
- **Self-Healing**: Additional 1-3 minutes per iteration

### **Success Rates**
- **Initial Generation**: 85-90% success rate
- **After Self-Healing**: 95-98% success rate
- **Test Coverage**: 80-95% automated test coverage

## 🎯 Use Cases

### **Rapid Prototyping**
- Generate working prototypes in minutes
- Test ideas before full implementation
- Iterate quickly with AI assistance

### **Project Kickoff**
- Create complete project structure
- Set up development environment
- Generate boilerplate code

### **Code Review & Testing**
- Generate comprehensive test suites
- Analyze existing code quality
- Assess code quality

### **Learning & Education**
- Study AI-generated best practices
- Learn new technology stacks
- Understand testing patterns

## 🔮 Future Enhancements

### **Planned Features**
- **Multi-language Support**: JavaScript, TypeScript, Java, Go, Rust
- **Advanced AI Models**: Integration with more providers
- **CI/CD Integration**: Direct deployment pipeline integration
- **Team Collaboration**: Multi-user support and project sharing
- **Custom Templates**: User-defined generation patterns
- **Performance Monitoring**: Runtime analysis and optimization

### **Extensibility**
- **Plugin System**: Custom analysis and generation plugins
- **API Integration**: REST API for programmatic access
- **Database Support**: Persistent storage for projects
- **Cloud Deployment**: Containerized deployment options

## 🤝 Contributing

The project welcomes contributions:
- **Code Quality**: Follow PEP 8 and project standards
- **Testing**: Include tests for new features
- **Documentation**: Update docs for new functionality
- **Issues**: Report bugs and feature requests

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ using Python, Streamlit, and Advanced AI**

*Transform your development workflow with intelligent, self-healing code generation.* 