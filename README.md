# AI-Powered Development Assistant

A comprehensive AI-powered development assistant built with Streamlit that helps with code generation, testing, and project management.

## Features

- **AI-Powered Code Generation**: Generate code using multiple AI models
- **Automated Testing**: Generate and run tests for your code
- **Project Management**: Upload and manage project files
- **Code Analysis**: Analyze code quality and provide suggestions
- **Docker Integration**: Run code in isolated Docker containers

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
   ```bash
   cp env_example.txt .env
   # Edit .env file and add your API keys
   ```

## Running the Application

### Option 1: Using the startup script
```bash
./start.sh
```

### Option 2: Manual startup
```bash
source venv/bin/activate
streamlit run app.py
```

### Option 3: Stop the application
```bash
./stop.sh
```

The application will be available at `http://localhost:8501` (or `http://localhost:8502` if port 8501 is in use)

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

1. **Upload Project Files**: Upload your project files or create new ones
2. **Generate Code**: Use AI to generate code based on your requirements
3. **Run Tests**: Automatically generate and run tests for your code
4. **Analyze Code**: Get code quality analysis and suggestions
5. **Execute in Docker**: Run your code in isolated Docker containers

## Project Structure

```
AgenticCodeGen&Tester/
├── app.py                 # Main Streamlit application
├── core/                  # Core functionality modules
├── utils/                 # Utility modules
├── templates/             # Code templates
├── generated/             # Generated code output
├── requirements.txt       # Python dependencies
├── start.sh              # Startup script
└── README.md             # This file
```

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