# Architecture Overview

## Project Philosophy

### Token Efficiency First

This project is NOT about code generation. It's about validation, parsing, and analysis that saves agent tokens.

**Core Principle:** Build what agents waste tokens on, avoid what they do well.

## What This Project IS

✅ **Validators** - Catch errors before execution
- Syntax validation (shell, Python, YAML, JSON, TOML)
- Type hint validation
- Security validation (injection, secrets, misconfigurations)
- Schema validation (CI/CD configs, API specs)

✅ **Parsers** - Convert unstructured → structured
- AST parsing (Python, shell)
- Tool output parsing (ruff, mypy, pytest, git)
- Log parsing and extraction
- Configuration file parsing

✅ **Extractors** - Pull specific data
- Function signatures
- Docstring information
- Import statements
- Complexity metrics
- Schema information

✅ **Formatters** - Apply deterministic rules
- Argument escaping (shell, SQL)
- Import sorting
- Docstring formatting (Google, NumPy, Sphinx styles)
- Type hint normalization

✅ **Scanners** - Rule-based detection
- Secret detection (API keys, tokens, passwords)
- Security anti-patterns (SQL injection, XSS, eval usage)
- Performance anti-patterns (N+1 queries, unbounded loops)
- Compliance checking (GDPR, accessibility)

## What This Project is NOT

❌ **Code Generators** - Agents excel at creative logic
- Don't build full function/class generators
- Don't build template systems
- Don't build project scaffolding
- Don't build documentation generators

❌ **Architecture Tools** - Requires judgment
- Don't build design pattern generators
- Don't build architecture decision tools
- Don't make opinionated structural choices

❌ **Refactoring Tools** - Agents reason through this
- Don't build code transformation tools
- Don't build migration generators
- Don't build optimization engines

## Module Organization

```
src/coding_open_agent_tools/
├── _decorators.py              # Centralized decorator imports
├── confirmation.py             # Smart confirmation system (3 modes)
├── exceptions.py               # Custom exceptions
├── types.py                    # Type definitions
├── helpers.py                  # Tool loading and management (11 functions)
│
├── navigation/                 # Shared navigation utilities
│   └── shared.py              # Common validation/extraction logic
│
├── analysis/                   # AST parsing, complexity, imports (14 functions)
│   ├── ast_parsing.py         # Python AST operations
│   ├── complexity.py          # Cyclomatic complexity
│   ├── imports.py             # Import analysis
│   ├── patterns.py            # Code pattern detection
│   └── secrets.py             # Secret detection
│
├── git/                        # Git repository operations (14 submodules, 79 functions)
│   ├── branches.py            # Branch management
│   ├── commits.py             # Commit analysis
│   ├── config.py              # Repository configuration
│   ├── conflicts.py           # Merge conflict detection
│   ├── diffs.py               # Diff operations
│   ├── health.py              # Repository health checks
│   ├── history.py             # Git history analysis
│   ├── hooks.py               # Git hooks management
│   ├── remotes.py             # Remote repository operations
│   ├── security.py            # Security scanning
│   ├── status.py              # Working tree status
│   ├── submodules.py          # Submodule management
│   ├── tags.py                # Tag operations
│   └── workflows.py           # CI/CD workflows
│
├── python/                     # Python-specific tools (5 submodules, 32 functions)
│   ├── navigation.py          # Code navigation (17 functions, 70-95% token savings)
│   ├── validators.py          # Syntax validation
│   ├── analyzers.py           # Code analysis
│   ├── extractors.py          # Data extraction
│   └── formatters.py          # Code formatting
│
├── shell/                      # Shell script tools (5 submodules, 13 functions)
│   ├── validators.py          # Syntax validation
│   ├── security.py            # Security scanning
│   ├── analyzers.py           # Script analysis
│   ├── formatters.py          # Argument escaping
│   └── extractors.py          # Command extraction
│
├── config/                     # Configuration file tools (6 submodules, 28 functions)
│   ├── env_parser.py          # .env file operations
│   ├── extractors.py          # Value extraction (YAML/TOML/JSON)
│   ├── parsers.py             # INI/properties/XML parsing
│   ├── security.py            # Gitignore security
│   ├── validators.py          # Format validation
│   └── utils.py               # Helper utilities
│
├── database/                   # SQLite operations (5 submodules, 18 functions)
│   ├── operations.py          # Database operations
│   ├── query_builder.py       # Safe query building
│   ├── schema.py              # Schema inspection
│   └── utils.py               # Helper utilities
│
├── profiling/                  # Performance profiling (8 functions)
│   ├── memory.py              # Memory profiling
│   ├── performance.py         # Performance analysis
│   └── timing.py              # Execution timing
│
├── quality/                    # Code quality analysis (7 functions)
│   ├── parsers.py             # Tool output parsing
│   └── analysis.py            # Quality metrics
│
└── [language]/navigation.py   # Per-language navigation (8 languages)
    ├── cpp/                   # C++ (17 functions)
    ├── csharp/                # C# (17 functions)
    ├── go/                    # Go (17 functions)
    ├── java/                  # Java (17 functions)
    ├── javascript/            # JavaScript/TypeScript (17 functions)
    ├── python/                # Python (included in python/ above)
    ├── ruby/                  # Ruby (17 functions)
    └── rust/                  # Rust (17 functions)
```

**Total:** 286 functions across 8 core modules + 7 language-specific modules

## Design Patterns

### 1. Decorator Pattern

All agent tools use centralized decorator imports with conditional fallback:

```python
# In _decorators.py
try:
    from strands import tool as strands_tool
except ImportError:
    # No-op decorator if strands not installed
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        return func

# In any module
from coding_open_agent_tools._decorators import strands_tool

@strands_tool
def your_function(param1: str, param2: str) -> dict[str, str]:
    """Function description."""
    # Implementation
    return {"result": "value"}
```

**Why:** Zero required dependencies - package works without strands installed. Graceful degradation.

### 2. Shared Utilities Pattern

Common functionality extracted to shared modules to reduce code duplication:

```python
# In navigation/shared.py
def validate_source_code(source_code: str, param_name: str = "source_code") -> None:
    """Validate source code parameter."""
    if not isinstance(source_code, str):
        raise TypeError(f"{param_name} must be a string")
    if not source_code.strip():
        raise ValueError(f"{param_name} cannot be empty")

def validate_identifier(identifier: str, param_name: str) -> None:
    """Validate identifier parameter."""
    if not isinstance(identifier, str):
        raise TypeError(f"{param_name} must be a string")
    if not identifier.strip():
        raise ValueError(f"{param_name} cannot be empty")
    if not identifier.replace("_", "").isalnum():
        raise ValueError(f"{param_name} must be a valid identifier")

# In any navigation module
from coding_open_agent_tools.navigation.shared import validate_source_code, validate_identifier

@strands_tool
def get_function_signature(source_code: str, function_name: str) -> dict[str, str]:
    validate_source_code(source_code)
    validate_identifier(function_name, "function_name")
    # Implementation
    pass
```

**Why:** Consistent validation, reduced duplication, easier maintenance.

### 3. JSON-Serializable Returns

All functions return `dict[str, str]` for Google ADK compatibility:

```python
@strands_tool
def validate_python_syntax(source_code: str) -> dict[str, str]:
    """Validate Python source code syntax."""
    try:
        ast.parse(source_code)
        return {
            "is_valid": "true",        # Note: string, not boolean
            "error_message": "",
            "line_number": "0",        # Note: string, not int
            "column_offset": "0",
            "error_type": "",
        }
    except SyntaxError as e:
        return {
            "is_valid": "false",
            "error_message": str(e.msg) if e.msg else "Syntax error",
            "line_number": str(e.lineno) if e.lineno else "0",
            "column_offset": str(e.offset) if e.offset else "0",
            "error_type": "SyntaxError",
        }
```

**Why:** Google ADK requires JSON-serializable types only. Agents can easily parse string values.

### 4. Input Validation

All functions validate inputs and raise appropriate exceptions:

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

**Why:** Fail fast with clear error messages. Prevents cryptic failures downstream.

### 5. Smart Confirmation System

Three-mode confirmation handling for write/delete operations:

```python
from coding_open_agent_tools.confirmation import check_user_confirmation

def write_file(file_path: str, content: str, skip_confirm: str) -> dict[str, str]:
    """Write file with smart confirmation."""
    # Convert string to boolean (ADK compliance)
    skip = skip_confirm.lower() == "true"

    # Check confirmation
    confirmed = check_user_confirmation(
        operation="write file",
        target=file_path,
        skip_confirm=skip,
        preview_info=f"{len(content)} bytes"
    )

    if not confirmed:
        return {
            "success": "false",
            "error": "Operation cancelled by user",
            "path": file_path,
        }

    # Proceed with write
    with open(file_path, 'w') as f:
        f.write(content)

    return {
        "success": "true",
        "error": "",
        "path": file_path,
    }
```

**Modes:**

1. **Bypass Mode** - `skip_confirm=True` or `BYPASS_TOOL_CONSENT=true` env var
   - Proceeds immediately without prompts
   - Perfect for CI/CD and automation

2. **Interactive Mode** - Terminal with `skip_confirm=False`
   - Prompts user with `y/n` confirmation
   - Shows preview info (file sizes, etc.)

3. **Agent Mode** - Non-TTY with `skip_confirm=False`
   - Raises `CONFIRMATION_REQUIRED` error with instructions
   - LLM agents can ask user and retry with `skip_confirm=True`

**Why:** Safe by default, adapts to context (interactive vs automation).

## Framework Compatibility

### Strands Framework
- All tools decorated with `@strands_tool`
- Optional dependency (graceful fallback)
- Import pattern: `from strands import tool as strands_tool`
- Conditional import with no-op fallback

### Google ADK
- Works with `@strands_tool` decorated functions
- Requires JSON-serializable returns (`dict[str, str]`)
- No default parameters allowed
- Comprehensive docstrings for LLM understanding

### LangGraph
- Works with standard Python callables
- No decorator needed
- Can use any function directly

### Other Frameworks
- Standard Python functions work with any framework
- Decorator is transparent to non-Strands frameworks
- Type hints provide IDE autocomplete

## Code Quality Standards

### Required
- ✅ **100% ruff compliance** - No exceptions
- ✅ **100% mypy compliance** - Full type coverage
- ✅ **80%+ test coverage** - Every function tested
- ✅ **Google ADK compliance** - JSON-serializable only
- ✅ **Zero external dependencies (core)** - Prefer stdlib

### Testing Strategy

#### Test Structure
```
tests/
├── analysis/
│   ├── test_ast_parsing.py
│   ├── test_complexity.py
│   └── ...
├── git/
│   ├── test_health.py
│   ├── test_security.py
│   └── ...
├── python/
│   ├── test_navigation.py
│   ├── test_validators.py
│   └── ...
└── [module]/
    └── test_*.py
```

#### Test Patterns

**Type Validation Tests:**
```python
def test_invalid_param_type(self) -> None:
    """Test TypeError when param is not a string."""
    with pytest.raises(TypeError, match="param must be a string"):
        function_name(123, "valid")  # type: ignore
```

**Value Validation Tests:**
```python
def test_empty_param(self) -> None:
    """Test ValueError when param is empty."""
    with pytest.raises(ValueError, match="param cannot be empty"):
        function_name("", "valid")
```

**Path Validation Tests:**
```python
def test_file_not_found(self, tmp_path: Path) -> None:
    """Test FileNotFoundError for missing file."""
    nonexistent = tmp_path / "missing.py"
    with pytest.raises(FileNotFoundError):
        function_name(str(nonexistent))
```

**Happy Path Tests:**
```python
def test_success_case(self, tmp_path: Path) -> None:
    """Test successful operation."""
    result = function_name("valid_input", "valid_param")
    assert result["success"] == "true"
    assert result["error"] == ""
    assert "expected_key" in result
```

**Edge Case Tests:**
```python
def test_edge_case_empty_result(self) -> None:
    """Test handling of empty result."""
    result = function_name("input_with_no_matches")
    assert result["count"] == "0"
    assert result["items"] == "[]"
```

**Mocked Subprocess Tests:**
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

#### Coverage Requirements
- Overall: 83% coverage (571 tests passing)
- Critical modules: 90%+ coverage
- Git modules: 80-93% coverage
- Navigation modules: 68-88% coverage
- Python module: 93% coverage
- Config module: 86% coverage

## Optional Dependencies

Core functionality uses stdlib only. Optional dependencies enhance capabilities.

### When to Use Optional Dependencies

✅ **ADD optional dependency if:**
1. It provides substantial value (10x better than stdlib approach)
2. It's pip-installable Python library (not external binary)
3. There's graceful fallback to stdlib
4. It's actively maintained (1000+ stars, recent commits)
5. It's Python-native (can import, not subprocess-only)

❌ **DON'T add optional dependency if:**
1. Stdlib solution is "good enough" (80% as good)
2. It's a Go/Rust binary requiring subprocess
3. No graceful fallback possible
4. Maintenance concerns (unmaintained, <500 stars)
5. Only marginal improvement over stdlib

### detect-secrets Integration (Optional)

**Why detect-secrets:** Production-grade secret detection as optional enhancement

```toml
# In pyproject.toml
[project.optional-dependencies]
enhanced-security = ["detect-secrets>=1.5.0"]
```

Install with: `pip install coding-open-agent-tools[enhanced-security]`

**Implementation Pattern:**

```python
def scan_for_secrets_enhanced(
    content: str,
    use_detect_secrets: str  # "true" or "false" (ADK compliance)
) -> dict[str, str]:
    """Scan content for secrets with optional detect-secrets integration.

    Falls back to stdlib regex if detect-secrets not installed.
    """
    if use_detect_secrets == "true":
        try:
            from detect_secrets import SecretsCollection
            from detect_secrets.settings import default_settings
            # Use detect-secrets for comprehensive scanning
            return _scan_with_detect_secrets(content)
        except ImportError:
            # Graceful fallback to stdlib
            return _scan_with_stdlib_regex(content)
    else:
        return _scan_with_stdlib_regex(content)
```

**Why This Works:**
- ✅ Default behavior uses stdlib (no dependencies)
- ✅ Users opt-in for enhanced detection
- ✅ Graceful degradation if not installed
- ✅ Clear benefit: 1000+ patterns vs ~30 stdlib patterns
- ✅ Python-native library, not external binary

### tree-sitter Integration (Optional)

For enhanced code navigation across multiple languages:

```toml
[project.optional-dependencies]
enhanced-navigation = [
    "tree-sitter>=0.20.0",
    "tree-sitter-language-pack>=0.1.0"
]
```

**Benefits:**
- Accurate parsing for 8 languages (C++, C#, Go, Java, JavaScript, Python, Ruby, Rust)
- Better handling of complex syntax
- More robust navigation

**Fallback:** Basic regex-based navigation when not installed

## Performance Considerations

### Token Savings
- **70-95% reduction** in common workflows
- **Navigation tools:** 70-95% token savings vs reading full files
- **Validation:** Prevents retry loops, saves 30-50% tokens
- **Parsing:** Structured data extraction, 60-80% token savings

### Parsing Efficiency
- **<100ms** for most operations
- **AST parsing:** Near-instant for typical files
- **Git operations:** 50-500ms depending on repo size
- **Navigation:** <50ms for function lookup

### Retry Prevention
- **Validation catches 95%+ of errors** before execution
- **Syntax validation:** Prevents Python/shell syntax errors
- **Security scanning:** Catches injection patterns, secrets
- **Type validation:** Prevents type-related failures

## Success Metrics

Track token savings, not feature count:

1. **Retry loop prevention:** Validation catches X% of errors
2. **Parsing efficiency:** Convert unstructured → structured in <100ms
3. **Token savings:** Document 30-50% reduction in specific workflows
4. **Error prevention:** 95%+ syntax/security error detection

## Key Mantras

1. **Parse, don't generate**
2. **Validate early, save tokens**
3. **Deterministic operations only**
4. **If agents do it well, skip it**
5. **Prevent errors > Generate code**

---

**When in doubt, ask:** "Does this save agent tokens or prevent retry loops?"

If no, it probably doesn't belong here.
