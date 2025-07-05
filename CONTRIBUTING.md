# Contributing to DNS Update Service

Thank you for your interest in contributing to the DNS Update Service! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Issues

1. **Check existing issues** - Before creating a new issue, please check if a similar issue already exists.
2. **Use the issue template** - When creating an issue, please provide:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)

### Suggesting Features

1. **Check existing feature requests** - Look for similar feature requests first.
2. **Provide detailed description** - Explain the use case and benefits.
3. **Consider implementation** - If possible, suggest how it might be implemented.

### Code Contributions

#### Prerequisites

- Python 3.7+
- Git
- Basic understanding of Flask and AWS services

#### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/floyd68/dns-update.git
   cd dns-update
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up pre-commit hooks** (optional)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

#### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run the application
   python app.py
   
   # Test with the test script
   python test_dns_update.py
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description of your changes
   - Reference any related issues
   - Include test results if applicable

## Code Style Guidelines

### Python Code

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and concise

### Documentation

- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update docstrings when modifying functions

### Testing

- Add tests for new functionality
- Ensure existing tests still pass
- Test both success and error scenarios

## Pull Request Guidelines

### Before Submitting

1. **Test thoroughly** - Ensure all tests pass
2. **Check formatting** - Run code formatters if available
3. **Update documentation** - Update README and docstrings
4. **Squash commits** - Clean up commit history if needed

### Pull Request Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Other (please describe)

## Testing
- [ ] Added tests for new functionality
- [ ] All existing tests pass
- [ ] Tested manually

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented if necessary)
```

## Getting Help

If you need help with contributing:

1. **Check the documentation** - Start with the README.md
2. **Search existing issues** - Your question might already be answered
3. **Create an issue** - Use the "Question" label for general questions

## Code of Conduct

This project is committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and considerate in all interactions.

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License. 