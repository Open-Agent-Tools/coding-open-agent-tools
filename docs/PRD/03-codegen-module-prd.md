# Python Validation & Analysis Module - Product Requirements

## Module Overview

The Python Validation & Analysis Module provides AI agents with comprehensive capabilities for **validating, parsing, and formatting** Python code. This module focuses on deterministic operations that save agent tokens: syntax validation, type hint validation, docstring parsing, import analysis, and ADK compliance checking.

**Philosophy**: Agents excel at writing Python code. This module prevents errors before execution, handles tedious parsing tasks, and validates compliance with standards.

## Goals and Objectives

### Primary Goals

1. **Prevent Errors**: Validate syntax and type hints before execution (saves retry loops)
2. **Parse Structure**: Extract function signatures, docstrings, type annotations
3. **Format Consistently**: Normalize imports, format docstrings deterministically
4. **Ensure Compliance**: Check Google ADK compliance, PEP 8 adherence

### Non-Goals

- ❌ Full code generation (agents write excellent Python code)
- ❌ Test generation (agents create comprehensive tests)
- ❌ Project scaffolding (agents use cookiecutter/examples)
- ❌ Documentation generation (agents write clear docs)
- ❌ Refactoring tools (agents reason through transformations)

## User Stories

### Story 1: Syntax Validation Before Execution
**As an** AI agent generating Python code
**I want to** validate syntax before execution
**So that** I avoid retry loops from syntax errors

### Story 2: Function Signature Parsing
**As an** agent analyzing Python code
**I want to** extract function signatures deterministically
**So that** I don't waste tokens on manual parsing

### Story 3: Type Hint Validation
**As an** agent writing type-safe code
**I want to** validate type hints for correctness
**So that** I catch type errors before mypy runs

### Story 4: ADK Compliance Checking
**As an** agent building tools for Google ADK
**I want to** verify ADK compliance automatically
**So that** tools work with agent frameworks

### Story 5: Docstring Formatting
**As an** agent documenting code
**I want to** format docstrings consistently
**So that** documentation follows standards

## Functional Requirements

### FR1: Validation Functions

#### FR1.1: validate_python_syntax
```python
def validate_python_syntax(code: str) -> dict[str, str]:
    """Validate Python code syntax without execution.

    Prevents execution failures by catching syntax errors early.
    Saves agent tokens on retry loops.

    Args:
        code: Python code to validate

    Returns:
        Dict with keys: is_valid (bool as string),
                       error_message (string),
                       line_number (string of int)

    Example:
        >>> result = validate_python_syntax("def foo(): pass")
        >>> result['is_valid']
        'true'
        >>> result = validate_python_syntax("def foo( pass")
        >>> result['is_valid']
        'false'
        >>> result['line_number']
        '1'
    """
```

**Implementation**: Use `compile()` for syntax checking (no execution)

**Token Savings**: Prevents retry loops from syntax errors. Agents waste 100+ tokens regenerating code with simple syntax errors.

#### FR1.2: validate_type_hints
```python
def validate_type_hints(code: str) -> dict[str, str]:
    """Validate type hints for correctness.

    Checks type hint syntax and compatibility (Python 3.9+ syntax).

    Args:
        code: Python code with type hints to validate

    Returns:
        Dict with keys: is_valid (bool as string),
                       issues (JSON list of issue dicts),
                       coverage_percentage (string of float)

        Each issue dict has keys: line, issue, hint, recommendation

    Example:
        >>> code = "def foo(x: list[int]) -> dict[str, int]: pass"
        >>> result = validate_type_hints(code)
        >>> result['is_valid']
        'true'
        >>> result['coverage_percentage']
        '100.0'
    """
```

**Validation Checks**:
- Valid type hint syntax (PEP 484, 585, 604)
- Compatible with Python 3.9+ (no `typing.List`, use `list`)
- Type annotation coverage percentage
- Invalid combinations (e.g., `list[str, int]`)

#### FR1.3: validate_import_order
```python
def validate_import_order(code: str) -> dict[str, str]:
    """Validate import statement order and grouping.

    Checks PEP 8 import ordering: stdlib, third-party, local.

    Args:
        code: Python code to validate

    Returns:
        Dict with keys: is_valid (bool as string),
                       violations (JSON list of violation dicts),
                       suggested_order (string)

        Each violation dict has keys: line, issue, recommendation

    Example:
        >>> code = "import os\\nfrom myapp import foo\\nimport sys"
        >>> result = validate_import_order(code)
        >>> result['is_valid']
        'false'
    """
```

**Validation Rules**:
- Standard library imports first
- Third-party imports second
- Local imports last
- Alphabetical within groups
- Blank line between groups

#### FR1.4: check_adk_compliance
```python
def check_adk_compliance(code: str) -> dict[str, str]:
    """Check function compliance with Google ADK requirements.

    Validates JSON-serializable types, no defaults, proper return types.

    Args:
        code: Python function code to validate

    Returns:
        Dict with keys: is_compliant (bool as string),
                       issues (JSON list of issue dicts),
                       compliant_functions (JSON list of names)

        Each issue dict has keys: function_name, issue, recommendation

    Example:
        >>> code = "def foo(x: int = 5) -> str: pass"
        >>> result = check_adk_compliance(code)
        >>> result['is_compliant']
        'false'
        >>> issues = json.loads(result['issues'])
        >>> issues[0]['issue']
        'Function has default parameter value'
    """
```

**ADK Compliance Checks**:
- No default parameter values
- Return type is JSON-serializable
- Parameter types are JSON-serializable
- Returns `dict[str, str]` or similar JSON type
- Proper type annotations on all parameters

**Token Savings**: Deterministic compliance checking. Agents waste 150+ tokens reasoning through ADK requirements.

### FR2: Parsing Functions

#### FR2.1: parse_function_signature
```python
def parse_function_signature(source_code: str) -> dict[str, str]:
    """Extract function signature components from Python code.

    Tedious parsing task that agents waste tokens on.

    Args:
        source_code: Python source code containing function

    Returns:
        Dict with keys: name (string),
                       parameters (JSON list of param dicts),
                       return_type (string),
                       docstring (string),
                       is_async (string: "true"/"false")

        Each parameter dict has keys: name, type, has_default

    Example:
        >>> code = "def process(data: list[dict], op: str) -> dict: pass"
        >>> result = parse_function_signature(code)
        >>> result['name']
        'process'
        >>> params = json.loads(result['parameters'])
        >>> len(params)
        2
    """
```

**Extraction Details**:
- Use AST parsing for reliability
- Extract all parameter information
- Identify return type annotation
- Extract docstring if present
- Detect async functions

**Token Savings**: Parsing signatures is tedious. Agents spend 200+ tokens on manual parsing. This is instant and deterministic.

#### FR2.2: extract_docstring_info
```python
def extract_docstring_info(docstring: str, style: str) -> dict[str, str]:
    """Parse docstring to extract structured information.

    Deterministic parsing of docstrings by style.

    Args:
        docstring: Docstring to parse
        style: Docstring style (google, numpy, sphinx)

    Returns:
        Dict with keys: description (string),
                       parameters (JSON list of param dicts),
                       returns (string),
                       raises (JSON list of exception dicts),
                       examples (JSON list of example strings)

        Parameter dict keys: name, type, description
        Exception dict keys: type, description

    Example:
        >>> docstring = '''Calculate total.
        ...
        ... Args:
        ...     x: First number
        ...     y: Second number
        ...
        ... Returns:
        ...     Sum of x and y
        ... '''
        >>> result = extract_docstring_info(docstring, "google")
        >>> result['description']
        'Calculate total.'
    """
```

**Style Support**:
- Google style (Args/Returns/Raises)
- NumPy style (Parameters/Returns/Raises)
- Sphinx style (:param/:returns/:raises)

**Token Savings**: Parsing docstrings is tedious and error-prone. Agents spend 150+ tokens on this.

#### FR2.3: extract_type_annotations
```python
def extract_type_annotations(code: str) -> dict[str, str]:
    """Extract all type annotations from Python code.

    Comprehensive type annotation extraction.

    Args:
        code: Python code to analyze

    Returns:
        Dict with keys: functions (JSON list of function type dicts),
                       variables (JSON list of variable type dicts),
                       coverage_stats (JSON dict with metrics)

        Function dict keys: name, parameters, return_type
        Variable dict keys: name, type, scope

    Example:
        >>> code = "x: int = 5\\ndef foo(y: str) -> bool: pass"
        >>> result = extract_type_annotations(code)
        >>> stats = json.loads(result['coverage_stats'])
        >>> stats['annotated_functions']
        1
    """
```

#### FR2.4: get_function_dependencies
```python
def get_function_dependencies(code: str, function_name: str) -> dict[str, str]:
    """Extract dependencies for a specific function.

    Deterministic dependency analysis.

    Args:
        code: Python module code
        function_name: Name of function to analyze

    Returns:
        Dict with keys: imports (JSON list of import strings),
                       calls (JSON list of called function names),
                       globals_used (JSON list of global names),
                       locals_defined (JSON list of local names)

    Example:
        >>> result = get_function_dependencies(code, "process_data")
        >>> calls = json.loads(result['calls'])
        >>> 'validate_input' in calls
        True
    """
```

### FR3: Formatting Functions

#### FR3.1: format_docstring
```python
def format_docstring(
    description: str,
    parameters: str,  # JSON list of param dicts
    return_description: str,
    style: str,
    raises: str  # JSON list of exception dicts (empty list as "[]")
) -> str:
    """Generate formatted docstring in specified style.

    Deterministic docstring formatting. Agents waste tokens on formatting.

    Args:
        description: Function description
        parameters: JSON-encoded list of parameter dicts with keys: name, type, description
        return_description: Description of return value
        style: Docstring style (google, numpy, sphinx)
        raises: JSON-encoded list of exception dicts with keys: type, description

    Returns:
        Formatted docstring as string

    Example:
        >>> params = '[{"name": "x", "type": "int", "description": "First number"}]'
        >>> docstring = format_docstring(
        ...     "Add numbers",
        ...     params,
        ...     "Sum of numbers",
        ...     "google",
        ...     "[]"
        ... )
        >>> "Args:" in docstring
        True
    """
```

**Token Savings**: Formatting docstrings is purely deterministic. Agents spend 100+ tokens getting formatting right.

#### FR3.2: sort_imports
```python
def sort_imports(code: str) -> str:
    """Sort import statements following PEP 8.

    Deterministic import sorting.

    Args:
        code: Python code with imports to sort

    Returns:
        Code with sorted imports

    Example:
        >>> code = "import sys\\nimport os\\nfrom myapp import foo"
        >>> sorted_code = sort_imports(code)
        >>> sorted_code.startswith("import os")
        True
    """
```

**Sorting Rules**:
- Group: stdlib, third-party, local
- Alphabetical within groups
- `import` statements before `from` statements
- Preserve blank lines between groups

#### FR3.3: normalize_type_hints
```python
def normalize_type_hints(code: str, target_version: str) -> str:
    """Normalize type hints to target Python version syntax.

    Converts old-style to modern type hints (e.g., List[int] → list[int]).

    Args:
        code: Python code with type hints
        target_version: Target Python version (3.9, 3.10, 3.11, 3.12)

    Returns:
        Code with normalized type hints

    Example:
        >>> code = "from typing import List\\ndef foo(x: List[int]): pass"
        >>> normalized = normalize_type_hints(code, "3.9")
        >>> "list[int]" in normalized
        True
    """
```

**Normalization Rules** (Python 3.9+):
- `List[T]` → `list[T]`
- `Dict[K, V]` → `dict[K, V]`
- `Set[T]` → `set[T]`
- `Tuple[T, ...]` → `tuple[T, ...]`
- `Optional[T]` → `T | None` (Python 3.10+)

### FR4: Analysis Functions

#### FR4.1: detect_circular_imports
```python
def detect_circular_imports(project_root: str) -> dict[str, str]:
    """Detect circular import dependencies in project.

    Static analysis to find circular dependencies.

    Args:
        project_root: Root directory of Python project

    Returns:
        Dict with keys: has_cycles (bool as string),
                       cycles (JSON list of cycle dicts),
                       total_modules (string of int)

        Each cycle dict has keys: modules (list of module names)

    Example:
        >>> result = detect_circular_imports("/path/to/project")
        >>> result['has_cycles']
        'false'
    """
```

#### FR4.2: identify_anti_patterns
```python
def identify_anti_patterns(code: str) -> dict[str, str]:
    """Identify common Python anti-patterns.

    Deterministic detection of code smells.

    Args:
        code: Python code to analyze

    Returns:
        Dict with keys: anti_patterns (JSON list of pattern dicts),
                       severity_counts (JSON dict of severity: count)

        Each pattern dict has keys: line, pattern, severity, recommendation

    Example:
        >>> code = "x = []\\nfor i in range(10):\\n    x = x + [i]"
        >>> result = identify_anti_patterns(code)
        >>> patterns = json.loads(result['anti_patterns'])
        >>> any('inefficient list concatenation' in p['pattern'].lower()
        ...     for p in patterns)
        True
    """
```

**Anti-Patterns Detected**:
- Mutable default arguments
- Inefficient list concatenation (`list = list + [item]`)
- Bare `except:` clauses
- Using `==` instead of `is` for None
- String concatenation in loops
- Missing `__init__.py` in packages

#### FR4.3: check_test_coverage_gaps
```python
def check_test_coverage_gaps(source_dir: str, test_dir: str) -> dict[str, str]:
    """Identify functions without corresponding tests.

    Static analysis to find untested code.

    Args:
        source_dir: Directory containing source code
        test_dir: Directory containing tests

    Returns:
        Dict with keys: untested_functions (JSON list of function names),
                       coverage_percentage (string of float),
                       missing_test_files (JSON list of file paths)

    Example:
        >>> result = check_test_coverage_gaps("src/", "tests/")
        >>> result['coverage_percentage']
        '85.5'
    """
```

### FR5: Utility Functions

#### FR5.1: extract_imports
```python
def extract_imports(code: str) -> dict[str, str]:
    """Extract all import statements from Python code.

    Parse and categorize imports.

    Args:
        code: Python code to analyze

    Returns:
        Dict with keys: stdlib (JSON list of module names),
                       third_party (JSON list of module names),
                       local (JSON list of module names),
                       all_imports (JSON list of import statement strings)

    Example:
        >>> code = "import os\\nimport requests\\nfrom myapp import utils"
        >>> result = extract_imports(code)
        >>> stdlib = json.loads(result['stdlib'])
        >>> 'os' in stdlib
        True
    """
```

#### FR5.2: find_unused_code
```python
def find_unused_code(code: str) -> dict[str, str]:
    """Find unused functions, classes, and variables.

    Static analysis for dead code detection.

    Args:
        code: Python code to analyze

    Returns:
        Dict with keys: unused_functions (JSON list of names),
                       unused_classes (JSON list of names),
                       unused_variables (JSON list of names),
                       total_unused (string of int)

    Example:
        >>> code = "def used(): pass\\ndef unused(): pass\\nused()"
        >>> result = find_unused_code(code)
        >>> unused = json.loads(result['unused_functions'])
        >>> 'unused' in unused
        True
    """
```

## Non-Functional Requirements

### NFR1: Performance
- Syntax validation: < 100ms for typical files (< 1000 lines)
- Type hint validation: < 200ms for typical files
- Signature parsing: < 50ms per function
- Import sorting: < 100ms for typical files

### NFR2: Compatibility
- Support Python 3.9+
- Handle all Python 3.9-3.12 syntax features
- Support all three docstring styles (Google, NumPy, Sphinx)

### NFR3: Safety
- Never execute code (use `compile()` and AST only)
- Read-only operations
- No file modifications without explicit user action

### NFR4: Code Quality
- 100% ruff compliance
- 100% mypy type coverage
- Minimum 80% test coverage
- All functions Google ADK compliant

## Dependencies

### Required
- Python stdlib: `ast`, `inspect`, `textwrap`, `typing`, `json`, `re`

### Optional
- `mypy` - Enhanced type checking validation
- `ruff` - Code quality validation

## Testing Strategy

### Unit Tests
- Test each validation function with valid/invalid inputs
- Test parsing with various code structures
- Test formatting produces correct output
- Test ADK compliance checking

### Integration Tests
- Validate real Python files
- Parse complex function signatures
- Check ADK compliance on actual tools
- Test import sorting on real modules

### Validation Tests
- Generated/formatted code passes ruff
- Generated/formatted code passes mypy
- Type hints are correct
- Docstrings are complete

### Performance Tests
- Benchmark on large files (5000+ lines)
- Ensure sub-second validation

## Example Use Cases

### Use Case 1: Validate Before Execution
```python
import coding_open_agent_tools as coat

# Agent writes Python code (they're excellent at this)
code = '''
def process_data(data: list[dict], operation: str) -> dict:
    """Process data with operation."""
    result = {}
    for item in data:
        result[item['id']] = operation(item)
    return result
'''

# Validate syntax (prevents execution failure)
validation = coat.validate_python_syntax(code)
if validation['is_valid'] == 'true':
    print("✓ Syntax valid")
else:
    print(f"✗ Syntax error: {validation['error_message']} (line {validation['line_number']})")
```

**Token Savings**: Catches syntax errors before execution. Saves 100+ tokens on retry loops.

### Use Case 2: Parse Function Signature
```python
# Extract signature (tedious parsing for agents)
code = '''
def calculate_total(
    items: list[dict[str, float]],
    tax_rate: float,
    discount: float
) -> dict[str, str]:
    """Calculate total price with tax and discount."""
    pass
'''

sig = coat.parse_function_signature(code)
print(f"Function: {sig['name']}")
print(f"Return type: {sig['return_type']}")

params = json.loads(sig['parameters'])
for param in params:
    print(f"  - {param['name']}: {param['type']}")

# Output:
# Function: calculate_total
# Return type: dict[str, str]
#   - items: list[dict[str, float]]
#   - tax_rate: float
#   - discount: float
```

**Token Savings**: Parsing is tedious. Agents spend 200+ tokens on manual extraction. This is instant.

### Use Case 3: Check ADK Compliance
```python
# Check ADK compliance (deterministic rules)
code = '''
def process_data(data: list[dict], operation: str = "default") -> dict:
    """Process data."""
    return {}
'''

compliance = coat.check_adk_compliance(code)
if compliance['is_compliant'] == 'false':
    issues = json.loads(compliance['issues'])
    for issue in issues:
        print(f"Function '{issue['function_name']}': {issue['issue']}")
        print(f"  → {issue['recommendation']}")

# Output:
# Function 'process_data': Function has default parameter value
#   → Remove default value from parameter 'operation'
```

**Token Savings**: Deterministic compliance checking. Agents waste 150+ tokens reasoning through ADK requirements.

### Use Case 4: Format Docstring
```python
# Format docstring (deterministic formatting)
params = json.dumps([
    {"name": "data", "type": "list[dict]", "description": "Input data to process"},
    {"name": "operation", "type": "str", "description": "Operation to perform"}
])

raises = json.dumps([
    {"type": "TypeError", "description": "If data is not a list"},
    {"type": "ValueError", "description": "If operation is not supported"}
])

docstring = coat.format_docstring(
    description="Process data with specified operation",
    parameters=params,
    return_description="Processing results as dictionary",
    style="google",
    raises=raises
)

print(docstring)

# Output:
# Process data with specified operation
#
# Args:
#     data: Input data to process
#     operation: Operation to perform
#
# Returns:
#     Processing results as dictionary
#
# Raises:
#     TypeError: If data is not a list
#     ValueError: If operation is not supported
```

**Token Savings**: Formatting is deterministic. Agents spend 100+ tokens getting formatting right.

### Use Case 5: Normalize Type Hints
```python
# Normalize old-style type hints
code = '''
from typing import List, Dict, Optional

def process(items: List[Dict[str, int]], name: Optional[str]) -> Dict[str, str]:
    pass
'''

normalized = coat.normalize_type_hints(code, "3.10")
print(normalized)

# Output:
# def process(items: list[dict[str, int]], name: str | None) -> dict[str, str]:
#     pass
```

**Token Savings**: Deterministic conversion. Agents spend 80+ tokens on manual conversion.

## Success Metrics

### Functional Metrics
- 15 functions implemented and tested
- Validation catches 95%+ of syntax/type errors
- Parsing extracts signatures correctly for 95%+ of functions
- ADK compliance checking 100% accurate
- Formatting produces valid docstrings 100% of time

### Quality Metrics
- 100% ruff compliance
- 100% mypy compliance
- 80%+ test coverage
- All functions Google ADK compliant

### Token Savings Metrics
- Validation prevents retry loops (100+ tokens saved per error)
- Parsing saves manual extraction (200+ tokens saved)
- ADK checking saves reasoning (150+ tokens saved)
- Formatting saves manual work (100+ tokens saved)

**Target**: 30-50% token reduction in Python development workflows

## Open Questions

1. Should we support type stub (.pyi) generation?
2. Do we need support for other docstring styles (reST, Epytext)?
3. Should we integrate with black for validation?
4. How deep should anti-pattern detection go?
5. Should we support auto-fix for simple issues?

## Future Enhancements (Post-v0.3.0)

1. **Auto-Fix Suggestions**: Generate corrected versions of code
2. **Advanced Type Inference**: Better type hint suggestions
3. **Performance Analysis**: Detect O(n²) patterns, memory issues
4. **Black Integration**: Validate code formatting
5. **Custom Rule Engine**: User-defined validation rules
6. **Diff Analysis**: Compare versions for regressions

---

**Document Version**: 2.0 - Token Efficiency Focused
**Last Updated**: 2025-10-14
**Status**: Aligned with Project Philosophy
**Owner**: Project Team

## Version History

- **2.0** (2025-10-14): Complete rewrite focused on validation/parsing/formatting (not generation)
- **1.0** (2025-10-14): Initial draft (generation-focused, deprecated)
