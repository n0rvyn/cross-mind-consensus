# 🤝 Contributing to Cross-Mind Consensus

Thank you for your interest in contributing to Cross-Mind Consensus! This document provides guidelines and information for contributors.

## 🎯 How to Contribute

We welcome contributions in many forms:

- 🐛 **Bug Reports**: Help us identify and fix issues
- 💡 **Feature Requests**: Suggest new capabilities
- 📝 **Documentation**: Improve guides and examples
- 🔧 **Code Contributions**: Submit pull requests
- 🧪 **Testing**: Help improve test coverage
- 🌐 **Localization**: Translate to other languages

## 🚀 Quick Start for Contributors

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/cross-mind-consensus.git
cd cross-mind-consensus

# Add the original repository as upstream
git remote add upstream https://github.com/original-owner/cross-mind-consensus.git
```

### 2. Setup Development Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install black isort flake8 mypy pytest pytest-cov

# Setup pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## 📋 Development Guidelines

### Code Style

We use several tools to maintain code quality:

```bash
# Format code
black backend/
isort backend/

# Lint code
flake8 backend/
mypy backend/

# Run tests
pytest tests/ -v --cov=backend
```

### Commit Message Format

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(api): add new consensus method`
- `fix(cache): resolve Redis connection timeout`
- `docs(readme): update deployment instructions`
- `test(backend): add unit tests for analytics`

### Pull Request Process

1. **Create a descriptive PR title**
2. **Add detailed description** of changes
3. **Include tests** for new functionality
4. **Update documentation** if needed
5. **Ensure all checks pass** (CI/CD)
6. **Request review** from maintainers

## 🏗️ Project Structure

```
cross-mind-consensus/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── models/             # Pydantic models
│   ├── services/           # Business logic
│   ├── utils/              # Utility functions
│   └── tests/              # Backend tests
├── dashboard/              # Streamlit dashboard
├── nginx/                  # Nginx configuration
├── scripts/                # Deployment scripts
├── tests/                  # Integration tests
│   └── performance/        # Load testing
└── docs/                   # Documentation
```

## 🧪 Testing Guidelines

### Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Performance tests
pytest tests/performance/ -v

# All tests with coverage
pytest tests/ -v --cov=backend --cov-report=html
```

### Writing Tests

- **Unit tests**: Test individual functions/methods
- **Integration tests**: Test API endpoints and services
- **Performance tests**: Test system under load
- **Security tests**: Test authentication and validation

Example test structure:

```python
import pytest
from backend.services.consensus import ConsensusService

class TestConsensusService:
    def test_basic_consensus(self):
        service = ConsensusService()
        result = service.get_consensus("test question")
        assert result is not None
        assert "consensus_score" in result
```

## 🔒 Security Guidelines

### Reporting Security Issues

**Do not create public GitHub issues for security vulnerabilities.**

Instead, please email security@crossmind-consensus.com with:
- Detailed description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested fix (if any)

### Security Best Practices

- **Input Validation**: Always validate and sanitize inputs
- **Authentication**: Use proper authentication mechanisms
- **Authorization**: Implement proper access controls
- **Secrets Management**: Never commit API keys or passwords
- **Dependency Updates**: Keep dependencies updated

## 📝 Documentation Guidelines

### Code Documentation

- Use docstrings for all public functions/classes
- Follow Google docstring format
- Include type hints for all functions

```python
def get_consensus(question: str, models: List[str]) -> ConsensusResult:
    """Get consensus from multiple LLM models.
    
    Args:
        question: The question to get consensus on
        models: List of model IDs to use
        
    Returns:
        ConsensusResult with consensus score and responses
        
    Raises:
        ConsensusError: If consensus cannot be reached
    """
```

### Documentation Updates

When adding new features:
- Update README.md if needed
- Add API documentation
- Update deployment guides
- Add usage examples

## 🌐 Internationalization

We welcome translations! To add a new language:

1. Create translation files in `locales/`
2. Update language detection logic
3. Add language-specific tests
4. Update documentation

## 🏷️ Issue Labels

We use the following labels to categorize issues:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to docs
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority: high`: High priority issues
- `priority: low`: Low priority issues

## 🎉 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Project README (for significant contributions)
- Release notes
- Community announcements

## 📞 Getting Help

If you need help contributing:

- 📧 **Email**: contributors@crossmind-consensus.com
- 💬 **Discord**: [Join our community](https://discord.gg/crossmind)
- 📖 **Documentation**: [Development docs](https://docs.crossmind-consensus.com/dev)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/cross-mind-consensus/issues)

## 📄 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md), which promotes a respectful and inclusive community.

## 📜 License

By contributing to Cross-Mind Consensus, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Cross-Mind Consensus!** 🚀

Your contributions help make AI decision-making more reliable and accessible for everyone. 