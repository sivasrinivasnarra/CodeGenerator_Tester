# Quick Start Guide

Get your AI-Powered Development Assistant up and running in minutes!

## 🚀 Quick Setup

### 1. Clone or Download
```bash
git clone <your-repo-url>
cd AgenticCodeGen&Tester
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Edit the `.env` file and add your API keys:
```bash
# Get your API keys from:
# OpenAI: https://platform.openai.com/api-keys
# Google: https://makersuite.google.com/app/apikey
# Anthropic: https://console.anthropic.com/ (optional)
# xAI: https://console.x.ai/ (optional)

OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=your-google-key-here
CLAUDE_API_KEY=your-claude-key-here  # Optional, for self-healing
GROK4_API_KEY=your-grok-key-here     # Optional, alternative AI model
```

### 4. Launch the Application
```bash
streamlit run app.py
```

### 5. Open Your Browser
Navigate to the URL shown in the terminal (usually `http://localhost:8501`)

## 📝 First Use - 4-Stage Workflow

### **Stage 1: Input Processing**
1. **Upload Document**: PDF, DOCX, TXT, MD, CSV, or ZIP project
2. **Enter Requirements**: Describe what you want to build
3. **Combine Context**: System merges document content with your requirements

### **Stage 2: Tech Stack Recommendation**
1. **Click "Suggest Tech Stack"**: AI analyzes requirements
2. **Review Options**: See 3 technology stack suggestions with detailed pros/cons
3. **Select Stack**: Choose the best option for your project

### **Stage 3: Project Structure Generation**
1. **Click "Generate Project Structure"**: AI creates complete project architecture
2. **Review Structure**: See file organization, dependencies, and configuration
3. **Approve Structure**: Confirm the project layout

### **Stage 4: Code Generation & Self-Healing**
1. **Click "Generate Code"**: AI creates all project files
2. **Watch Self-Healing**: If errors occur, AI automatically fixes them
3. **Get Results**: Download complete, working project with tests and docs

## 🎯 Example Requirements

Try these example requirements to get started:

### **Simple API Project**
```
Create a Python web API for user management with authentication, CRUD operations, and proper error handling. Include database models, API endpoints, and comprehensive testing.
```

### **Data Processing Application**
```
Build a Python application that processes CSV files, validates data, generates summary statistics, and creates visualizations. Include logging, error handling, and unit tests.
```

### **Web Scraping Tool**
```
Implement a web scraper that extracts product information from e-commerce sites with rate limiting, error recovery, and data storage. Include proper user agent rotation and proxy support.
```

### **Machine Learning Pipeline**
```
Create a machine learning pipeline for text classification with data preprocessing, model training, evaluation, and deployment. Include cross-validation, hyperparameter tuning, and model persistence.
```

## 🔧 Configuration Options

### **AI Models**
- **Gemini 2.5 Pro** (Default): Best for complex code generation
- **GPT-4o-mini**: Fast, cost-effective generation
- **GPT-4o**: High-quality, complex logic
- **Claude Opus 4**: Self-healing and error correction
- **Grok-4**: Alternative generation option

### **User Controls**
- **Creativity Level**: Temperature control (0.0-1.0)
- **Response Length**: Max tokens (1000-4000)
- **Model Selection**: Choose preferred AI model

### **Self-Healing Settings**
- **Max Attempts**: Healing iteration limit (default: 5)
- **Docker Timeout**: Execution time limit (default: 540s)
- **Error Threshold**: When to trigger healing

## 📊 Understanding Results

### **Generated Project Structure**
```
project_name/
├── src/                    # Source code
│   ├── main.py            # Main application
│   ├── models.py          # Data models
│   ├── utils.py           # Utility functions
│   └── config.py          # Configuration
├── tests/                 # Test files
│   ├── test_main.py       # Main tests
│   ├── test_models.py     # Model tests
│   └── conftest.py        # Test configuration
├── docs/                  # Documentation
│   ├── README.md          # Project documentation
│   └── API.md            # API documentation
├── requirements.txt       # Dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Multi-service setup
└── .env.example          # Environment variables
```

### **Code Quality Metrics**
- **Syntax Validation**: AST parsing and error checking
- **Code Formatting**: Black formatter integration
- **Linting**: Flake8 style and error checking
- **Test Coverage**: Automated test execution and reporting

### **Self-Healing Results**
- **Success**: All tests pass, code runs without errors
- **Partial Success**: Some issues remain after max attempts
- **Error Details**: Comprehensive error analysis and suggestions

## 🛠️ Troubleshooting

### Common Issues

**"API Key Error"**
- Check your `.env` file has correct API keys
- Verify keys are active and have sufficient credits
- Ensure at least one AI model is configured

**"Docker Error"**
- Ensure Docker is installed and running
- Check Docker permissions and access
- Verify Docker daemon is active

**"Import Error"**
- Run `pip install -r requirements.txt`
- Ensure Python 3.8+ is installed
- Check virtual environment activation

**"Permission Error"**
- Check file permissions in the `generated/` directory
- Run with appropriate user permissions
- Ensure write access to project directory

**"Memory Error"**
- Reduce `MAX_TOKENS` in `.env` file
- Close other applications to free memory
- Use smaller AI models for complex projects

### Getting Help

1. **Check Error Logs**: Review detailed error messages in the sidebar
2. **Review Generated Files**: Examine the output for clues
3. **Try Simpler Requirements**: Start with basic functionality
4. **Check Dependencies**: Ensure all packages are installed
5. **Verify API Keys**: Confirm AI model access

## 🚀 Advanced Features

### **Multi-Format Input**
- **Documents**: PDF, DOCX, TXT, MD, CSV text extraction
- **Projects**: ZIP file extraction and analysis
- **Code Files**: Direct Python file processing
- **Requirements**: Natural language requirement parsing

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

### **File Management**
- **Organized Structure**: Separate directories for code, tests, assessments
- **Version Control**: Timestamped file naming
- **Export Options**: Individual files or complete project packages
- **Cleanup Tools**: Automatic removal of old files

## 📈 Best Practices

### Writing Good Requirements
1. **Be Specific**: Include input/output formats, error conditions
2. **Mention Constraints**: Performance, security, compatibility needs
3. **Include Examples**: Provide sample inputs and expected outputs
4. **Specify Dependencies**: Mention required libraries or frameworks
5. **Describe Architecture**: Mention preferred patterns or structures

### Code Review Process
1. **Review Generated Code**: Check logic correctness and structure
2. **Test with Edge Cases**: Verify error handling and boundary conditions
3. **Check Dependencies**: Ensure all required packages are included
4. **Verify Documentation**: Review generated docs for accuracy
5. **Test Deployment**: Verify Docker and deployment configurations

### Iterative Improvement
1. **Start Simple**: Begin with basic functionality
2. **Generate and Review**: Create initial code and examine results
3. **Refine Requirements**: Add details based on generated output
4. **Regenerate**: Create improved versions with new requirements
5. **Repeat**: Iterate until satisfied with results

## 🎉 You're Ready!

Your AI-Powered Development Assistant is now ready to transform your development workflow! 

### **What You Can Do Now:**
- ✅ Generate complete projects from requirements
- ✅ Get AI-driven technology stack recommendations
- ✅ Create comprehensive test suites automatically
- ✅ Benefit from self-healing code generation
- ✅ Download complete, working projects

### **Next Steps:**
1. **Try Simple Projects**: Start with basic requirements
2. **Explore Different Stacks**: Test various technology combinations
3. **Customize Settings**: Adjust AI parameters for your needs
4. **Generate Tests**: Create comprehensive test coverage
5. **Deploy Projects**: Use generated Docker configurations

**Happy coding with AI assistance! 🚀** 