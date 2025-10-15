# Claude Instructions for Coding Open Agent Tools

## Project Philosophy: Token Efficiency First

This project is **NOT** about code generation. It's about **validation, parsing, and analysis** that saves agent tokens.

### Core Principle

**Build what agents waste tokens on, avoid what they do well.**

## What This Project IS

 **Validators** - Catch errors before execution
- Syntax validation (shell, Python, YAML, JSON, TOML)
- Type hint validation
- Security validation (injection, secrets, misconfigurations)
- Schema validation (CI/CD configs, API specs)

 **Parsers** - Convert unstructured � structured
- AST parsing (Python, shell)
- Tool output parsing (ruff, mypy, pytest, git)
- Log parsing and extraction
- Configuration file parsing

 **Extractors** - Pull specific data
- Function signatures
- Docstring information
- Import statements
- Complexity metrics
- Schema information

 **Formatters** - Apply deterministic rules
- Argument escaping (shell, SQL)
- Import sorting
- Docstring formatting (Google, NumPy, Sphinx styles)
- Type hint normalization

 **Scanners** - Rule-based detection
- Secret detection (API keys, tokens, passwords)
- Security anti-patterns (SQL injection, XSS, eval usage)
- Performance anti-patterns (N+1 queries, unbounded loops)
- Compliance checking (GDPR, accessibility)

## What This Project is NOT

L **Code Generators** - Agents excel at creative logic
- Don't build full function/class generators
- Don't build template systems
- Don't build project scaffolding
- Don't build documentation generators

L **Architecture Tools** - Requires judgment
- Don't build design pattern generators
- Don't build architecture decision tools
- Don't make opinionated structural choices

L **Refactoring Tools** - Agents reason through this
- Don't build code transformation tools
- Don't build migration generators
- Don't build optimization engines

## Module Guidelines

### Current Modules (v0.1.1)

**Analysis Module** (14 functions) -  GOOD
- AST parsing, complexity calculation, import management, secret detection
- All deterministic, rule-based operations
- Saves agent tokens on tedious parsing

**Git Module** (9 functions) -  GOOD
- Wrapper for git commands, output parsing
- Converts unstructured git output � structured JSON
- Saves agents from parsing git output

**Profiling Module** (8 functions) -  GOOD
- Performance and memory profiling
- Deterministic measurement and reporting
- Agents waste tokens setting up profilers

**Quality Module** (7 functions) -  GOOD
- Parses tool output (ruff, mypy, pytest)
- Filters and prioritizes issues
- Prevents agents from parsing tool output repeatedly

### Planned Modules

**Shell Validation Module** (v0.2.0) - ~13 functions
- **Focus**: Validation and security, NOT generation
- Functions: `validate_shell_syntax()`, `analyze_shell_security()`, `escape_shell_argument()`, `parse_shell_script()`, `detect_unquoted_variables()`, `find_dangerous_commands()`, `scan_for_secrets_enhanced()`
- **Why**: Agents waste tons of tokens on shell escaping and miss security issues
- **NOT**: Don't build `generate_bash_script()` - agents write scripts well
- **Optional**: `detect-secrets>=1.5.0` for enhanced secret scanning

**Python Validation Module** (v0.3.0) - ~15 functions
- **Focus**: Validation, parsing, formatting, NOT generation
- Functions: `validate_python_syntax()`, `validate_type_hints()`, `parse_function_signature()`, `extract_docstring_info()`, `format_docstring()`, `check_adk_compliance()`
- **Why**: Prevents syntax errors (saves retry loops), parsing is tedious
- **NOT**: Don't build `generate_python_function()` - agents excel at this

**SQLite Operations Module** (v0.3.5) - ~10 functions
- **Focus**: Local data storage for agent memory (pure stdlib)
- Functions: `create_sqlite_database()`, `execute_query()`, `inspect_schema()`, `build_select_query()`, `export_to_json()`
- **Why**: Essential for agent state/memory, safe query building prevents SQL injection
- **Zero dependencies**: Pure stdlib `sqlite3`

**Config Validation Module** (v0.4.0) - ~10 functions
- **Focus**: Validation and security, NOT generation
- Functions: `validate_yaml_syntax()`, `scan_config_for_secrets()`, `validate_json_schema()`, `detect_dependency_conflicts()`
- **Why**: Prevents deployment failures, deterministic security scanning
- **NOT**: Don't build config generators - agents handle with examples
- **Optional**: `detect-secrets>=1.5.0` for enhanced secret scanning

**Advanced Analysis Module** (v0.5.0) - ~12 functions
- **Focus**: Deep code analysis (security, performance, compliance)
- Functions: `detect_sql_injection_patterns()`, `find_xss_vulnerabilities()`, `identify_n_squared_loops()`, `check_gdpr_compliance()`
- **Why**: Deterministic rule-based checks agents struggle with

## Decision Framework

When adding a new function, ask:

###  ADD IT if:
1. It's deterministic (same input � same output)
2. Agents waste tokens on it (>100 tokens for trivial task)
3. It prevents errors (syntax, security, type)
4. It converts unstructured � structured
5. It's tedious for agents (parsing, escaping, formatting)

### L DON'T ADD IT if:
1. Agents already do it well (creative logic, architecture)
2. It requires judgment or context
3. It's code generation (unless it's tiny formatters/escapers)
4. It duplicates existing tools (basic-open-agent-tools)
5. It would add external dependencies (prefer stdlib)

## Code Quality Standards

- **100% ruff compliance** - No exceptions
- **100% mypy compliance** - Full type coverage
- **80%+ test coverage** - Every function tested
- **Google ADK compliance** - JSON-serializable only, no defaults, proper decorators
- **Required decorators** - All agent tools MUST have `@strands_tool` and `@tool` decorators
- **Strands framework dependency** - Required (not optional) for agent tool registration
- **Zero external dependencies (core logic)** - Prefer stdlib for implementation (decorators are required)

## Optional Dependencies Pattern

**Philosophy**: Core functionality uses stdlib only. Optional dependencies enhance capabilities.

### When to Use Optional Dependencies

✅ **ADD optional dependency if**:
1. It provides substantial value (10x better than stdlib approach)
2. It's pip-installable Python library (not external binary)
3. There's graceful fallback to stdlib
4. It's actively maintained (1000+ stars, recent commits)
5. It's Python-native (can import, not subprocess-only)

❌ **DON'T add optional dependency if**:
1. Stdlib solution is "good enough" (80% as good)
2. It's a Go/Rust binary requiring subprocess
3. No graceful fallback possible
4. Maintenance concerns (unmaintained, <500 stars)
5. Only marginal improvement over stdlib

### detect-secrets Integration (v0.2.0+)

**Why detect-secrets**: Production-grade secret detection as optional enhancement

```python
# Optional dependency in pyproject.toml
[project.optional-dependencies]
enhanced-security = ["detect-secrets>=1.5.0"]

# Install with: pip install coding-open-agent-tools[enhanced-security]
```

**Implementation Pattern**:

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

**Why This Works**:
- ✅ Default behavior uses stdlib (no dependencies)
- ✅ Users opt-in for enhanced detection
- ✅ Graceful degradation if not installed
- ✅ Clear benefit: 1000+ patterns vs ~30 stdlib patterns
- ✅ Python-native library, not external binary

**Alternatives Considered**:
- **Gitleaks** (17k stars): Go binary, subprocess-only, git-aware ❌
- **TruffleHog** (16k stars): Go binary, verifies secrets, subprocess-only ❌
- **detect-secrets** (3.6k stars): Python library, pip-installable ✅

## Examples of Good vs Bad Functions

###  GOOD: Validator
```python
def validate_shell_syntax(script_content: str, shell_type: str) -> dict[str, str]:
    """Validate shell script syntax using bash -n.

    Prevents execution failures. Deterministic. Saves retry loops.
    """
```

###  GOOD: Parser
```python
def parse_function_signature(source_code: str) -> dict[str, str]:
    """Extract function signature components from Python code.

    Tedious for agents. Returns structured data. Deterministic.
    """
```

###  GOOD: Formatter
```python
def escape_shell_argument(argument: str, quote_style: str) -> str:
    """Safely escape argument for shell use.

    Agents waste tokens on this and get it wrong. Pure formatting.
    """
```

### L BAD: Generator
```python
def generate_python_function(...) -> str:
    """Generate complete Python function with types and docstring.

    Agents excel at this. Not deterministic. Wrong focus.
    """
```

### L BAD: Architecture
```python
def design_microservice_architecture(...) -> dict:
    """Design microservice architecture based on requirements.

    Requires judgment and context. Not deterministic.
    """
```

## Success Metrics

Track token savings, not feature count:
- **Retry loop prevention**: Validation catches X% of errors
- **Parsing efficiency**: Convert unstructured � structured in <100ms
- **Token savings**: Document 30-50% reduction in specific workflows
- **Error prevention**: 95%+ syntax/security error detection

## Module Organization

```
src/coding_open_agent_tools/
   analysis/      #  AST, complexity, imports, secrets
   git/           #  Git command wrappers and parsers
   profiling/     #  Performance/memory measurement
   quality/       #  Tool output parsers
   shell/         # =� v0.2.0 - Validation, NOT generation
   python/        # =� v0.3.0 - Validation, NOT generation
   database/      # =� v0.3.5 - SQLite operations
   config/        # =� v0.4.0 - Config validation
```

## Contributing Guidelines

### DO:
- Add validators, parsers, formatters, scanners
- Keep functions small and focused
- Provide clear token-saving rationale
- Write comprehensive tests
- Use pure stdlib when possible

### DON'T:
- Add code generators (except tiny formatters)
- Add external dependencies without strong justification
- Build what agents already do well
- Create opinionated architecture tools
- Skip validation or testing

## Key Mantras

1. **Parse, don't generate**
2. **Validate early, save tokens**
3. **Deterministic operations only**
4. **If agents do it well, skip it**
5. **Prevent errors > Generate code**

---

**When in doubt, ask**: "Does this save agent tokens or prevent retry loops?"
If no, it probably doesn't belong here.

---

## Required Decorator Pattern for All Tools

**CRITICAL**: All 84 agent tools MUST use the `@strands_tool` decorator with conditional import.

### Decorator Requirements (Matches basic-open-agent-tools Pattern)

Every tool module requires conditional import with fallback:

```python
try:
    from strands import tool as strands_tool
except ImportError:
    # Create a no-op decorator if strands is not installed
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        return func

@strands_tool
def your_function_name(param1: str, param2: str) -> dict[str, str]:
    """Function description.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Dictionary with:
        - key1: Description
        - key2: Description
    """
    # Implementation here
    pass
```

### Framework Compatibility

| Framework | Requirement | Notes |
|-----------|-------------|-------|
| **Strands** | `@strands_tool` decorator | Registers function with Strands agent framework (optional dependency) |
| **Google ADK** | Works with `@strands_tool` | ADK can use functions decorated with @strands_tool |
| **LangGraph** | Standard callable | Works automatically - no decorator needed |

### Why This Pattern?

1. **Zero required dependencies** - Package works without strands installed
2. **Graceful degradation** - Functions work normally when strands not available
3. **Framework agnostic** - Same pattern as basic-open-agent-tools
4. **Type safety** - Mypy configured to ignore missing imports

### Example: Complete Tool Function

```python
try:
    from strands import tool as strands_tool
except ImportError:
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        return func

@strands_tool
def validate_python_syntax(source_code: str) -> dict[str, str]:
    """Validate Python source code syntax using AST parsing.

    Prevents execution failures by catching syntax errors early.

    Args:
        source_code: Python source code to validate

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - error_message: Error description if invalid
        - line_number: Line number of error
        - column_offset: Column offset of error
        - error_type: Type of syntax error

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        ast.parse(source_code)
        return {
            "is_valid": "true",
            "error_message": "",
            "line_number": "0",
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

### Common Decorator Mistakes

❌ **Missing decorator:**
```python
def validate_python_syntax(source_code: str) -> dict[str, str]:
    # Will NOT work with Strands framework!
    pass
```

❌ **Using parentheses:**
```python
@strands_tool()  # WRONG! No parentheses needed
def validate_python_syntax(source_code: str) -> dict[str, str]:
    pass
```

❌ **Missing conditional import:**
```python
from strands import tool as strands_tool  # WRONG! Will fail if strands not installed

@strands_tool
def validate_python_syntax(source_code: str) -> dict[str, str]:
    pass
```

✅ **Correct:**
```python
try:
    from strands import tool as strands_tool
except ImportError:
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        return func

@strands_tool
def validate_python_syntax(source_code: str) -> dict[str, str]:
    pass
```

### Dependencies

Add to `pyproject.toml`:

```toml
dependencies = [
    "basic-open-agent-tools>=0.12.0",
]

[project.optional-dependencies]
# Strands integration (OPTIONAL)
strands = [
    "strands>=0.1.0",
    "anthropic>=0.25.0",
    "python-dotenv>=1.0.0",
]

# Development dependencies
dev = [
    "pytest>=7.0.0",
    # ... other dev deps
    "google-adk>=0.1.0",  # For testing ADK compatibility
    "strands>=0.1.0",     # For testing Strands integration
]
```

**Strands is OPTIONAL**, not required. Package works without it.
