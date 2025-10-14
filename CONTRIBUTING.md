# Contributing to Coding Open Agent Tools

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Project Status

✅ **v0.1.0-beta Released**: The project has successfully migrated 39 functions across 4 modules from basic-open-agent-tools. Check the [TODO.md](TODO.md) for the current roadmap and [CHANGELOG.md](CHANGELOG.md) for release history.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- (Optional) UV, Poetry, or another Python package manager

### Setup Steps

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/coding-open-agent-tools.git
   cd coding-open-agent-tools
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

### Code Quality Standards

All code must meet these standards before merging:

1. **Ruff Compliance** (100%)
   ```bash
   ruff check src/ tests/
   ruff format src/ tests/
   ```

2. **MyPy Compliance** (100%)
   ```bash
   mypy src/
   ```

3. **Test Coverage** (80%+ for new code)
   ```bash
   pytest --cov=src/coding_open_agent_tools
   ```

### Google ADK Compliance

All functions MUST follow Google ADK standards:

- **JSON-serializable types only**: `str`, `int`, `float`, `bool`, `dict`, `list`
- **Typed lists**: Use `list[dict[str, str]]`, never bare `list`
- **No default parameters**: Never use default values
- **No Union/Any types**: Avoid `Union`, `Optional`, `Any`
- **No bytes parameters**: Not JSON-serializable
- **Comprehensive docstrings**: Help LLMs understand function purpose

Example:
```python
def generate_function(
    name: str,
    parameters: list[dict[str, str]],  # Typed list
    return_type: str
) -> str:
    """Generate Python function definition.

    Args:
        name: Function name
        parameters: List of param dicts with keys: name, type, description
        return_type: Return type annotation

    Returns:
        Complete function definition as string

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If name is empty
    """
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    if not name:
        raise ValueError("name cannot be empty")
    # Implementation...
```

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards
   - Write tests for new functionality
   - Update documentation

3. **Run quality checks**
   ```bash
   ruff check src/ tests/ --fix
   ruff format src/ tests/
   mypy src/
   pytest
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

We follow conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Build/tooling changes

## Testing Guidelines

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names: `test_function_name_behavior()`
- Aim for 80%+ coverage on new code

Example:
```python
def test_generate_function_basic():
    """Test generate_function with valid inputs."""
    result = generate_function(
        name="test_func",
        parameters=[{"name": "x", "type": "int", "description": "Input"}],
        return_type="str"
    )
    assert "def test_func(" in result
    assert "-> str:" in result
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_shell.py

# Run with coverage
pytest --cov=src/coding_open_agent_tools

# Run fast tests only (skip slow)
pytest -m "not slow"
```

## Pull Request Process

1. **Ensure all checks pass**
   - All tests pass
   - Code coverage meets minimum (80%+)
   - Ruff and mypy pass
   - Documentation is updated

2. **PR Description**
   - Describe the changes clearly
   - Reference any related issues
   - Include examples if applicable

3. **Review Process**
   - At least one maintainer approval required
   - Address review comments promptly
   - Keep PR scope focused

4. **After Approval**
   - Maintainers will merge the PR
   - Your changes will be included in the next release

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Questions?

- Open an issue for bug reports or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones

## Release Process

This project uses GitHub's trusted publishing to PyPI for secure, automated releases.

### For Maintainers: Creating a Release

1. **Update version number**
   - Update version in `src/coding_open_agent_tools/__init__.py`
   - Update version in `pyproject.toml`
   - Follow semantic versioning (MAJOR.MINOR.PATCH)

2. **Update CHANGELOG.md**
   - Document all changes in the new version
   - Follow Keep a Changelog format
   - Include migration notes if applicable

3. **Create a git tag**
   ```bash
   git tag -a v0.1.0 -m "Release v0.1.0: Brief description"
   git push origin v0.1.0
   ```

4. **Create a GitHub Release**
   - Go to the repository's Releases page
   - Click "Draft a new release"
   - Select the tag you created
   - Title: `v0.1.0: Brief description`
   - Description: Copy relevant section from CHANGELOG.md
   - Publish the release

5. **Automated Publishing**
   - GitHub Actions will automatically build and publish to PyPI
   - Uses trusted publishing (no API tokens needed)
   - Monitor the workflow run for any issues

### Testing Before Release

Test on TestPyPI first:

```bash
# Manually trigger the publish workflow with test_pypi option
# Go to Actions > Publish to PyPI > Run workflow
# Select "Publish to Test PyPI instead of PyPI"
```

Then install from TestPyPI to verify:

```bash
pip install --index-url https://test.pypi.org/simple/ coding-open-agent-tools
```

### Trusted Publishing Setup

This repository is configured for PyPI trusted publishing:

- **Workflow**: `.github/workflows/publish.yml`
- **Permissions**: `id-token: write` for OIDC
- **Triggers**: GitHub releases and manual workflow dispatch
- **Security**: No long-lived API tokens required

The trusted publisher relationship is configured in the PyPI project settings.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
