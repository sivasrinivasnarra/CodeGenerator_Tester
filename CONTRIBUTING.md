# Contributing to AI-Powered Development Assistant

Thank you for your interest in contributing to the AI-Powered Development Assistant! This document provides guidelines and information for contributors.

## 🎯 Project Overview

The AI-Powered Development Assistant is a revolutionary tool that transforms natural language requirements into fully functional, tested code projects through a sophisticated 4-stage AI workflow with self-healing capabilities.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Docker (for self-healing functionality)
- Git
- API keys for AI models (OpenAI, Google, Anthropic, xAI)

### Setup Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/ai-powered-dev-assistant.git
   cd ai-powered-dev-assistant
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development dependencies
   ```

3. **Environment Setup**
   ```bash
   cp env_example.txt .env
   # Edit .env with your API keys
   ```

4. **Run Setup**
   ```bash
   python setup.py
   ```

5. **Start Development Server**
   ```bash
   streamlit run app.py
   ```

## 📋 Contribution Guidelines

### Code Style

We follow PEP 8 and use automated tools for code quality:

- **Black**: Code formatting
- **Flake8**: Linting and style checking
- **MyPy**: Type checking
- **Pytest**: Testing

Run quality checks:
```bash
# Format code
black .

# Lint code
flake8 .

# Type check
mypy .

# Run tests
pytest
```

### Commit Messages

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Examples:
```
feat(ai-engine): add Claude Opus 4 integration
fix(self-healing): resolve Docker timeout issues
docs(readme): update installation instructions
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow code style guidelines
   - Add tests for new features
   - Update documentation

3. **Test Your Changes**
   ```bash
   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=.
   
   # Run quality checks
   black . && flake8 . && mypy .
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **PR Review**
   - Ensure all checks pass
   - Address review comments
   - Update documentation if needed

## 🎯 Areas for Contribution

### High Priority
- **AI Model Integration**: Add support for new AI providers
- **Multi-language Support**: Extend beyond Python
- **Performance Optimization**: Improve generation speed and efficiency
- **Test Coverage**: Increase test coverage for core modules
- **Documentation**: Improve and expand documentation

### Medium Priority
- **UI/UX Improvements**: Enhance Streamlit interface
- **Error Handling**: Improve error messages and recovery
- **Configuration**: Add more customization options
- **Templates**: Create new code generation templates
- **Examples**: Add more example requirements and use cases

### Low Priority
- **CI/CD**: Improve GitHub Actions workflows
- **Monitoring**: Add performance monitoring
- **Security**: Security scanning and vulnerability detection
- **Internationalization**: Multi-language support for UI

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_ai_engine.py

# Run with coverage
pytest --cov=core --cov=utils

# Run with verbose output
pytest -v

# Run with parallel execution
pytest -n auto
```

### Writing Tests
- Follow pytest conventions
- Use descriptive test names
- Mock external dependencies (API calls, file system)
- Test both success and failure cases
- Aim for high test coverage

Example test:
```python
import pytest
from unittest.mock import Mock, patch
from core.ai_engine import AIEngine

class TestAIEngine:
    def test_generate_code_success(self):
        """Test successful code generation."""
        engine = AIEngine()
        with patch('openai.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value = Mock(
                choices=[Mock(message=Mock(content="def test(): pass"))]
            )
            result = engine.generate_code("Create a test function")
            assert result["success"] is True
            assert "def test(): pass" in result["code"]

    def test_generate_code_failure(self):
        """Test code generation failure."""
        engine = AIEngine()
        with patch('openai.OpenAI') as mock_openai:
            mock_openai.side_effect = Exception("API Error")
            result = engine.generate_code("Create a test function")
            assert result["success"] is False
            assert "API Error" in result["error"]
```

## 📚 Documentation

### Documentation Standards
- Use clear, concise language
- Include code examples
- Update documentation with code changes
- Use proper markdown formatting
- Include screenshots for UI changes

### Documentation Files
- **README.md**: Project overview and setup
- **QUICKSTART.md**: Quick start guide
- **PROJECT_SUMMARY.md**: Detailed feature overview
- **CHANGELOG.md**: Version history and changes
- **API Documentation**: Code documentation

### Adding Documentation
```bash
# Update main README
# Update relevant documentation files
# Add inline code comments
# Update docstrings
```

## 🔧 Development Tools

### Pre-commit Hooks
Install pre-commit hooks for automatic code quality:
```bash
pip install pre-commit
pre-commit install
```

### IDE Configuration
Recommended VS Code settings:
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### Debugging
For debugging the application:
```bash
# Run with debug mode
DEBUG=True streamlit run app.py

# Use Python debugger
python -m pdb app.py

# Use VS Code debugger
# Set breakpoints and use F5 to debug
```

## 🐛 Bug Reports

### Reporting Bugs
Use GitHub Issues with the following template:

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., macOS, Windows, Linux]
- Python Version: [e.g., 3.9.7]
- Streamlit Version: [e.g., 1.28.1]
- AI Model: [e.g., Gemini 2.5 Pro]

**Additional Information**
Screenshots, logs, error messages
```

### Bug Fix Process
1. **Reproduce**: Confirm the bug exists
2. **Investigate**: Find the root cause
3. **Fix**: Implement the solution
4. **Test**: Ensure the fix works
5. **Document**: Update changelog and documentation

## 💡 Feature Requests

### Suggesting Features
Use GitHub Issues with the following template:

```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why this feature is needed

**Proposed Implementation**
How you think it should work

**Alternatives Considered**
Other approaches you considered

**Additional Information**
Screenshots, examples, references
```

### Feature Development Process
1. **Discussion**: Discuss the feature with maintainers
2. **Design**: Design the feature architecture
3. **Implementation**: Implement the feature
4. **Testing**: Test thoroughly
5. **Documentation**: Update documentation
6. **Review**: Get code review and approval

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow project conventions
- Ask questions when unsure

### Communication
- Use GitHub Issues for discussions
- Be clear and specific
- Provide context and examples
- Respond to feedback promptly
- Thank contributors for their work

## 📈 Performance Guidelines

### Code Performance
- Optimize for readability first
- Profile code for bottlenecks
- Use appropriate data structures
- Minimize API calls
- Cache results when appropriate

### Memory Usage
- Avoid memory leaks
- Use generators for large datasets
- Clean up resources properly
- Monitor memory usage

### API Usage
- Minimize API calls
- Implement rate limiting
- Handle API errors gracefully
- Use appropriate timeouts

## 🔒 Security Guidelines

### Security Best Practices
- Never commit API keys or secrets
- Validate all inputs
- Sanitize user data
- Use secure defaults
- Follow OWASP guidelines

### Security Reporting
Report security issues privately to maintainers:
- Email: security@example.com
- Include detailed description
- Provide proof of concept
- Allow time for response

## 📝 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

## 🙏 Acknowledgments

Thank you to all contributors who have helped make this project better!

---

**Happy contributing! 🚀** 