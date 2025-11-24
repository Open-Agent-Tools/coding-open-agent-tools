# Contributing to Coding Open Agent Tools

Thank you for your interest in contributing! This project provides validators, parsers, and analysis tools specifically designed to save AI agents' tokens.

## Project Status

✅ **v0.9.1 Released**: 286 functions across 8 core modules + 7 language-specific modules
- 83% test coverage, 571 tests passing
- 100% ruff/mypy compliance
- All modules use `@strands_tool` decorator

See [CHANGELOG.md](CHANGELOG.md) for release history and [TODO.md](TODO.md) for roadmap.

## Development Setup

### Prerequisites
- Python 3.9 or higher
- Git
- (Optional) UV, Poetry, or another Python package manager

### Installation

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

4. **Install pre-commit hooks** (optional but recommended)
   ```bash
   pre-commit install
   ```

5. **Verify installation**
   ```bash
   # Run tests
   pytest tests/

   # Run quality checks
   ruff check .
   mypy src/
   ```

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

Follow the coding standards (see below) and write tests for new functionality.

### 3. Run Quality Checks

**Before committing, always run:**

```bash
# Auto-fix linting issues
ruff check . --fix
ruff format .

# Type checking
mypy src/

# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=src --cov-report=term
```

### 4. Commit Changes

Follow conventional commit format:
```bash
git add .
git commit -m "feat: add new functionality"
```

**Commit Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding/updating tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks
- `perf:` - Performance improvements

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- Reference to related issues
- Examples if applicable

## Code Quality Standards

### Required Standards
- ✅ **100% ruff compliance** - No exceptions
- ✅ **100% mypy compliance** - Full type coverage
- ✅ **80%+ test coverage** - Every function tested
- ✅ **Google ADK compliance** - JSON-serializable returns, no defaults
- ✅ **Proper decorators** - All tools must use `@strands_tool`
- ✅ **Comprehensive docstrings** - Help LLMs understand function purpose

### Decorator Requirements

All agent tools MUST use the `@strands_tool` decorator with conditional import:

```python
from coding_open_agent_tools._decorators import strands_tool

@strands_tool
def your_function(param1: str, param2: str) -> dict[str, str]:
    """Brief description.

    Detailed explanation of what the function does and why it exists.
    Explain the token savings rationale.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Dictionary with:
        - key1: Description
        - key2: Description

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty or invalid
        FileNotFoundError: If file does not exist (if applicable)

    Examples:
        >>> result = your_function("value1", "value2")
        >>> print(result["key1"])
        'expected_value'
    """
    # Validate inputs
    if not isinstance(param1, str):
        raise TypeError("param1 must be a string")
    if not param1.strip():
        raise ValueError("param1 cannot be empty")

    # Implementation
    ...

    # Return JSON-serializable dict
    return {
        "key1": "value1",
        "key2": "value2",
        "error": "",
    }
```

### Google ADK Compliance Rules

All functions MUST follow these rules:

1. **JSON-serializable types only**
   - ✅ Use: `str`, `int`, `float`, `bool`, `dict`, `list`
   - ❌ Avoid: `bytes`, `Union`, `Optional`, `Any`, custom classes

2. **Typed collections**
   - ✅ Use: `list[dict[str, str]]`, `dict[str, str]`
   - ❌ Avoid: bare `list`, bare `dict`

3. **No default parameters**
   - ❌ `def func(param: str = "default")` - NOT ALLOWED
   - ✅ `def func(param: str)` - Required parameter

4. **String returns for all primitives**
   - Return `{"count": "42", "is_valid": "true"}` not `{"count": 42, "is_valid": True}`
   - Agents can easily parse string values

5. **Comprehensive docstrings**
   - Include Args, Returns, Raises, Examples
   - Explain token savings rationale
   - Help LLMs understand when to use the function

### Input Validation Pattern

Always validate inputs with clear error messages:

```python
@strands_tool
def analyze_code(file_path: str, threshold: str) -> dict[str, str]:
    """Analyze code complexity."""

    # Type validation
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(threshold, str):
        raise TypeError("threshold must be a string")

    # Value validation
    if not file_path.strip():
        raise ValueError("file_path cannot be empty")

    # Numeric validation (when string represents number)
    try:
        threshold_int = int(threshold)
        if threshold_int < 0:
            raise ValueError("threshold must be non-negative")
    except ValueError as e:
        raise ValueError(f"threshold must be a valid integer: {e}")

    # File existence validation
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Implementation
    pass
```

## Testing Guidelines

### Test Structure

```
tests/
├── [module]/
│   ├── test_[submodule].py
│   └── ...
```

### Required Test Types

**1. Type Validation Tests**
```python
def test_invalid_param_type(self) -> None:
    """Test TypeError when param is not a string."""
    with pytest.raises(TypeError, match="param must be a string"):
        function_name(123, "valid")  # type: ignore
```

**2. Value Validation Tests**
```python
def test_empty_param(self) -> None:
    """Test ValueError when param is empty."""
    with pytest.raises(ValueError, match="param cannot be empty"):
        function_name("", "valid")
```

**3. Path Validation Tests**
```python
def test_file_not_found(self, tmp_path: Path) -> None:
    """Test FileNotFoundError for missing file."""
    nonexistent = tmp_path / "missing.py"
    with pytest.raises(FileNotFoundError):
        function_name(str(nonexistent))
```

**4. Happy Path Tests**
```python
def test_success_case(self) -> None:
    """Test successful operation."""
    result = function_name("valid_input", "valid_param")
    assert result["success"] == "true"
    assert result["error"] == ""
    assert "expected_key" in result
```

**5. Edge Case Tests**
```python
def test_edge_case_empty_result(self) -> None:
    """Test handling of empty result."""
    result = function_name("input_with_no_matches")
    assert result["count"] == "0"
    assert result["items"] == "[]"
```

**6. Mocked Subprocess Tests** (for git/shell operations)
```python
@patch("subprocess.run")
def test_git_command(self, mock_run: MagicMock) -> None:
    """Test git command execution."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="mocked output",
        stderr=""
    )
    result = git_function("/path/to/repo")
    assert result["success"] == "true"
    mock_run.assert_called_once()
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/git/test_health.py

# Run with coverage
pytest --cov=src/coding_open_agent_tools

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_validation"

# Run fast tests only (skip slow)
pytest -m "not slow"
```

### Coverage Requirements
- Overall: 80%+ coverage
- Critical modules: 90%+ coverage
- New code: 80%+ coverage minimum

## What to Contribute

### ✅ Good Contributions

1. **Validators** - Catch errors before execution
   - Syntax validation (shell, Python, YAML, JSON)
   - Type hint validation
   - Schema validation

2. **Parsers** - Convert unstructured → structured
   - Tool output parsing (ruff, mypy, pytest, git)
   - Log parsing and extraction
   - Configuration file parsing

3. **Extractors** - Pull specific data
   - Function signatures
   - Docstring information
   - Import statements
   - Complexity metrics

4. **Formatters** - Apply deterministic rules
   - Argument escaping (shell, SQL)
   - Import sorting
   - Docstring formatting

5. **Scanners** - Rule-based detection
   - Secret detection
   - Security anti-patterns
   - Performance anti-patterns
   - Compliance checking

6. **Bug fixes** - Fix existing issues
7. **Tests** - Improve test coverage
8. **Documentation** - Improve examples and guides

### ❌ Not Suitable

1. **Code generators** - Agents excel at creative logic
2. **Architecture tools** - Requires judgment and context
3. **Opinionated refactoring** - Agents handle transformations
4. **External binary dependencies** - Prefer stdlib
5. **Duplicate functionality** - Check existing modules first

## Decision Framework

When adding a new function, ask:

### ✅ ADD IT if:
1. It's deterministic (same input → same output)
2. Agents waste tokens on it (>100 tokens for trivial task)
3. It prevents errors (syntax, security, type)
4. It converts unstructured → structured
5. It's tedious for agents (parsing, escaping, formatting)

### ❌ DON'T ADD IT if:
1. Agents already do it well (creative logic, architecture)
2. It requires judgment or context
3. It's code generation (unless tiny formatters/escapers)
4. It duplicates existing tools
5. It would add external dependencies without strong justification

## Module Organization

When adding new modules, follow the established structure:

```
src/coding_open_agent_tools/
├── [module_name]/
│   ├── __init__.py        # Export public functions
│   ├── validators.py      # Validation functions
│   ├── parsers.py         # Parsing functions
│   ├── analyzers.py       # Analysis functions
│   ├── extractors.py      # Data extraction
│   ├── formatters.py      # Formatting functions
│   └── utils.py           # Helper utilities
```

## Pull Request Process

### Before Submitting

1. ✅ All tests pass
2. ✅ Code coverage meets minimum (80%+)
3. ✅ Ruff and mypy pass with no errors
4. ✅ Documentation is updated
5. ✅ Examples added (if applicable)
6. ✅ CHANGELOG.md updated (for significant changes)

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #(issue number)

## Token Savings
Explain how this change saves agent tokens (if applicable)

## Testing
Describe the tests you added/updated

## Checklist
- [ ] Tests pass locally
- [ ] Code coverage >= 80%
- [ ] Ruff/mypy compliance
- [ ] Documentation updated
- [ ] Examples added (if new feature)
```

### Review Process

1. Automated checks run on all PRs
2. Maintainer review for code quality and design
3. Test coverage verification
4. Documentation review
5. Merge when approved

## Optional Dependencies

When adding optional dependencies:

### ✅ ADD optional dependency if:
1. It provides substantial value (10x better than stdlib)
2. It's pip-installable Python library (not external binary)
3. There's graceful fallback to stdlib
4. It's actively maintained (1000+ stars, recent commits)
5. It's Python-native (can import, not subprocess-only)

### ❌ DON'T add optional dependency if:
1. Stdlib solution is "good enough" (80% as good)
2. It's a Go/Rust binary requiring subprocess
3. No graceful fallback possible
4. Maintenance concerns (unmaintained, <500 stars)
5. Only marginal improvement over stdlib

### Implementation Pattern

```python
def enhanced_function(
    content: str,
    use_enhancement: str  # "true" or "false" (ADK compliance)
) -> dict[str, str]:
    """Function with optional enhanced functionality.

    Falls back to stdlib if enhancement not installed.
    """
    if use_enhancement == "true":
        try:
            from optional_package import enhanced_feature
            return _enhanced_implementation(content)
        except ImportError:
            # Graceful fallback to stdlib
            return _stdlib_implementation(content)
    else:
        return _stdlib_implementation(content)
```

## Documentation

When adding features, update:

1. **README.md** - If adding new module or major feature
2. **ARCHITECTURE.md** - If changing design patterns
3. **docs/examples/** - Add practical examples
4. **Docstrings** - Comprehensive function documentation
5. **CHANGELOG.md** - Document all changes

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Questions?

- Open an issue for bug reports or feature requests
- Start a discussion for design questions
- Check existing issues before creating new ones
- Review [docs/examples/](docs/examples/) for usage patterns

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Key Mantras:**
1. Parse, don't generate
2. Validate early, save tokens
3. Deterministic operations only
4. If agents do it well, skip it
5. Prevent errors > Generate code

**When in doubt, ask:** "Does this save agent tokens or prevent retry loops?"

If no, it probably doesn't belong here.
