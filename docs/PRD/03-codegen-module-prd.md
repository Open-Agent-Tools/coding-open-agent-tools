# Python Code Generation Module - Product Requirements

## Module Overview

The Python Code Generation Module provides AI agents with comprehensive capabilities for generating Python code, including functions, classes, docstrings, test skeletons, and project structures. This module focuses on creating high-quality, type-safe, well-documented Python code that follows best practices.

## Goals and Objectives

### Primary Goals

1. **High-Quality Code**: Generate code following PEP 8, type hints, and best practices
2. **Self-Documenting**: All generated code includes comprehensive docstrings
3. **Type-Safe**: Generate code with full type annotations
4. **Test-Ready**: Create corresponding test skeletons
5. **Google ADK Compliant**: Generated code compatible with agent frameworks

### Non-Goals

- Code refactoring (transform existing code)
- Dynamic code execution or evaluation
- Code obfuscation or minification
- Language conversion (Python to other languages)

## User Stories

### Story 1: Function Scaffolding
**As an** AI agent building a Python module
**I want to** generate function definitions with proper signatures and docstrings
**So that** I can focus on implementing business logic

### Story 2: Class Generation
**As an** agent creating data models
**I want to** generate class structures with type hints
**So that** models are type-safe and well-documented

### Story 3: Test Creation
**As an** agent writing tests
**I want to** generate pytest test skeletons from function signatures
**So that** I can quickly scaffold comprehensive test coverage

### Story 4: Project Scaffolding
**As an** agent starting a new project
**I want to** generate standard project structure
**So that** projects follow best practices from the start

### Story 5: Documentation Generation
**As an** agent documenting code
**I want to** generate consistent docstrings
**So that** all functions are well-documented

## Functional Requirements

### FR1: Function Generation

#### FR1.1: generate_python_function
```python
def generate_python_function(
    name: str,
    parameters: list[dict[str, str]],
    return_type: str,
    description: str,
    docstring_style: str,
    add_type_checking: bool,
    add_error_handling: bool,
    raises: list[dict[str, str]]
) -> str:
    """Generate Python function with full signature and docstring.

    Args:
        name: Function name
        parameters: List of param dicts with keys: name, type, description
        return_type: Return type annotation
        description: Function description
        docstring_style: Style (google, numpy, sphinx)
        add_type_checking: Add isinstance checks for parameters
        add_error_handling: Add try/except blocks
        raises: List of exception dicts with keys: type, description

    Returns:
        Complete function definition as string
    """
```

**Example Output**:
```python
def calculate_total(items: list[dict[str, float]], tax_rate: float) -> float:
    """Calculate total price with tax applied.

    Args:
        items: List of item dictionaries with price information
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)

    Returns:
        Total price including tax

    Raises:
        TypeError: If items is not a list or tax_rate is not a float
        ValueError: If tax_rate is negative

    Example:
        >>> items = [{"price": 10.0}, {"price": 20.0}]
        >>> calculate_total(items, 0.08)
        32.4
    """
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    if not isinstance(tax_rate, float):
        raise TypeError("tax_rate must be a float")
    if tax_rate < 0:
        raise ValueError("tax_rate cannot be negative")

    # Implementation placeholder
    pass
```

#### FR1.2: generate_async_function
```python
def generate_async_function(
    name: str,
    parameters: list[dict[str, str]],
    return_type: str,
    description: str,
    docstring_style: str,
    add_error_handling: bool
) -> str:
    """Generate async Python function.

    Args:
        name: Function name
        parameters: List of param dicts with keys: name, type, description
        return_type: Return type annotation (wrapped in Coroutine)
        description: Function description
        docstring_style: Style (google, numpy, sphinx)
        add_error_handling: Add try/except blocks

    Returns:
        Complete async function definition
    """
```

#### FR1.3: generate_lambda_function
```python
def generate_lambda_function(
    parameters: list[str],
    expression: str,
    variable_name: str
) -> str:
    """Generate lambda function assignment.

    Args:
        parameters: List of parameter names
        expression: Lambda body expression
        variable_name: Variable to assign lambda to

    Returns:
        Lambda function assignment statement
    """
```

### FR2: Class Generation

#### FR2.1: generate_python_class
```python
def generate_python_class(
    name: str,
    base_classes: list[str],
    attributes: list[dict[str, str]],
    methods: list[dict[str, str]],
    docstring: str,
    add_init: bool,
    add_repr: bool,
    add_eq: bool
) -> str:
    """Generate Python class definition.

    Args:
        name: Class name
        base_classes: List of base class names
        attributes: List of attribute dicts with keys: name, type, description
        methods: List of method dicts with keys: name, signature, description
        docstring: Class docstring
        add_init: Generate __init__ method
        add_repr: Generate __repr__ method
        add_eq: Generate __eq__ method

    Returns:
        Complete class definition
    """
```

#### FR2.2: generate_dataclass
```python
def generate_dataclass(
    name: str,
    fields: list[dict[str, str]],
    frozen: bool,
    slots: bool,
    docstring: str
) -> str:
    """Generate Python dataclass.

    Args:
        name: Dataclass name
        fields: List of field dicts with keys: name, type, default, description
        frozen: Make dataclass immutable
        slots: Use __slots__ for memory efficiency
        docstring: Class docstring

    Returns:
        Complete dataclass definition with @dataclass decorator
    """
```

**Example Output**:
```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class User:
    """User account information.

    Attributes:
        id: Unique user identifier
        name: User's full name
        email: User's email address
        active: Whether account is active
    """
    id: int
    name: str
    email: str
    active: bool = True
```

#### FR2.3: generate_pydantic_model
```python
def generate_pydantic_model(
    name: str,
    fields: list[dict[str, str]],
    validators: list[dict[str, str]],
    docstring: str,
    config_options: dict[str, str]
) -> str:
    """Generate Pydantic model class.

    Args:
        name: Model name
        fields: List of field dicts with keys: name, type, default, description
        validators: List of validator dicts with keys: field, validation_type
        docstring: Class docstring
        config_options: Pydantic Config class options

    Returns:
        Complete Pydantic model definition
    """
```

#### FR2.4: generate_exception_class
```python
def generate_exception_class(
    name: str,
    base_exception: str,
    docstring: str,
    add_custom_init: bool,
    custom_attributes: list[dict[str, str]]
) -> str:
    """Generate custom exception class.

    Args:
        name: Exception class name
        base_exception: Base exception to inherit from
        docstring: Exception docstring
        add_custom_init: Add custom __init__ method
        custom_attributes: List of custom attribute dicts

    Returns:
        Complete exception class definition
    """
```

### FR3: Documentation Generation

#### FR3.1: generate_google_docstring
```python
def generate_google_docstring(
    description: str,
    parameters: list[dict[str, str]],
    return_description: str,
    raises: list[dict[str, str]],
    examples: list[str],
    notes: list[str]
) -> str:
    """Generate Google-style docstring.

    Args:
        description: Function/class description
        parameters: List of param dicts with keys: name, type, description
        return_description: Description of return value
        raises: List of exception dicts with keys: type, description
        examples: List of usage examples
        notes: List of additional notes

    Returns:
        Formatted Google-style docstring
    """
```

#### FR3.2: generate_numpy_docstring
```python
def generate_numpy_docstring(
    description: str,
    parameters: list[dict[str, str]],
    return_description: str,
    raises: list[dict[str, str]],
    examples: list[str],
    see_also: list[str]
) -> str:
    """Generate NumPy-style docstring.

    Args:
        description: Function/class description
        parameters: List of param dicts
        return_description: Description of return value
        raises: List of exception dicts
        examples: List of usage examples
        see_also: List of related functions

    Returns:
        Formatted NumPy-style docstring
    """
```

#### FR3.3: generate_module_header
```python
def generate_module_header(
    module_name: str,
    description: str,
    author: str,
    version: str,
    license_type: str,
    exports: list[str]
) -> str:
    """Generate module-level docstring and metadata.

    Args:
        module_name: Name of the module
        description: Module description
        author: Module author
        version: Module version
        license_type: License type
        exports: List of exported names for __all__

    Returns:
        Module header with docstring and metadata
    """
```

**Example Output**:
```python
"""Module for user authentication and authorization.

This module provides functions for user login, logout, and
permission checking.

Author: Jane Developer
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Jane Developer"
__license__ = "MIT"

__all__: list[str] = [
    "login_user",
    "logout_user",
    "check_permission",
]
```

### FR4: Test Generation

#### FR4.1: generate_test_skeleton
```python
def generate_test_skeleton(
    function_signature: str,
    test_cases: list[dict[str, str]],
    fixtures: list[str],
    docstring: str
) -> str:
    """Generate pytest test skeleton from function signature.

    Args:
        function_signature: Function signature to test
        test_cases: List of test case dicts with keys: name, description, assertions
        fixtures: List of pytest fixtures to use
        docstring: Test docstring

    Returns:
        Complete pytest test function
    """
```

**Example Output**:
```python
import pytest
from mymodule import calculate_total

def test_calculate_total_basic():
    """Test calculate_total with valid inputs."""
    items = [{"price": 10.0}, {"price": 20.0}]
    result = calculate_total(items, 0.08)
    assert result == 32.4

def test_calculate_total_empty_list():
    """Test calculate_total with empty list."""
    result = calculate_total([], 0.08)
    assert result == 0.0

def test_calculate_total_invalid_type():
    """Test calculate_total raises TypeError for invalid input."""
    with pytest.raises(TypeError):
        calculate_total("not a list", 0.08)

def test_calculate_total_negative_rate():
    """Test calculate_total raises ValueError for negative rate."""
    items = [{"price": 10.0}]
    with pytest.raises(ValueError):
        calculate_total(items, -0.08)
```

#### FR4.2: generate_test_fixture
```python
def generate_test_fixture(
    fixture_name: str,
    scope: str,
    return_value: str,
    docstring: str,
    dependencies: list[str]
) -> str:
    """Generate pytest fixture.

    Args:
        fixture_name: Name of the fixture
        scope: Fixture scope (function, class, module, session)
        return_value: Value or expression to return
        docstring: Fixture docstring
        dependencies: List of other fixtures this depends on

    Returns:
        Complete pytest fixture definition
    """
```

#### FR4.3: generate_test_class
```python
def generate_test_class(
    class_name: str,
    test_methods: list[dict[str, str]],
    setup_method: str,
    teardown_method: str,
    docstring: str
) -> str:
    """Generate pytest test class.

    Args:
        class_name: Test class name
        test_methods: List of test method dicts
        setup_method: Setup method code
        teardown_method: Teardown method code
        docstring: Class docstring

    Returns:
        Complete test class definition
    """
```

### FR5: Project Structure Generation

#### FR5.1: generate_project_structure
```python
def generate_project_structure(
    project_name: str,
    package_name: str,
    include_tests: bool,
    include_docs: bool,
    include_ci: bool,
    license_type: str
) -> dict[str, str]:
    """Generate complete project directory structure.

    Args:
        project_name: Name of the project
        package_name: Python package name
        include_tests: Include tests directory
        include_docs: Include docs directory
        include_ci: Include CI/CD configuration
        license_type: License type (MIT, Apache-2.0, GPL-3.0)

    Returns:
        Dict mapping file paths to file contents
    """
```

**Example Output Structure**:
```
myproject/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       └── core.py
├── tests/
│   ├── __init__.py
│   └── test_core.py
├── docs/
│   └── index.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

#### FR5.2: generate_pyproject_toml
```python
def generate_pyproject_toml(
    package_name: str,
    version: str,
    description: str,
    author: str,
    dependencies: list[str],
    dev_dependencies: list[str],
    python_version: str,
    build_system: str
) -> str:
    """Generate pyproject.toml file.

    Args:
        package_name: Package name
        version: Package version
        description: Package description
        author: Package author
        dependencies: List of runtime dependencies
        dev_dependencies: List of development dependencies
        python_version: Minimum Python version
        build_system: Build system (setuptools, poetry, hatch, pdm)

    Returns:
        Complete pyproject.toml content
    """
```

#### FR5.3: generate_readme_template
```python
def generate_readme_template(
    project_name: str,
    description: str,
    installation_steps: list[str],
    usage_examples: list[str],
    features: list[str],
    license_type: str
) -> str:
    """Generate README.md template.

    Args:
        project_name: Project name
        description: Project description
        installation_steps: List of installation steps
        usage_examples: List of usage examples
        features: List of key features
        license_type: License type

    Returns:
        Complete README.md content
    """
```

#### FR5.4: generate_gitignore
```python
def generate_gitignore(
    language: str,
    additional_patterns: list[str],
    include_ide: bool,
    include_os: bool
) -> str:
    """Generate .gitignore file.

    Args:
        language: Primary language (python, javascript, etc.)
        additional_patterns: Additional patterns to ignore
        include_ide: Include IDE-specific patterns
        include_os: Include OS-specific patterns

    Returns:
        Complete .gitignore content
    """
```

### FR6: Code Analysis

#### FR6.1: parse_function_signature
```python
def parse_function_signature(source_code: str) -> dict[str, str]:
    """Extract function signature components.

    Args:
        source_code: Python source code containing function

    Returns:
        Dict with keys: name, parameters (JSON), return_type, docstring
    """
```

#### FR6.2: extract_docstring_info
```python
def extract_docstring_info(docstring: str, style: str) -> dict[str, str]:
    """Parse docstring to extract structured information.

    Args:
        docstring: Docstring to parse
        style: Docstring style (google, numpy, sphinx)

    Returns:
        Dict with keys: description, parameters (JSON), returns, raises (JSON)
    """
```

#### FR6.3: validate_python_syntax
```python
def validate_python_syntax(code: str) -> dict[str, str]:
    """Validate Python code syntax.

    Args:
        code: Python code to validate

    Returns:
        Dict with keys: is_valid (bool as string), error_message, line_number
    """
```

**Implementation**: Use `compile()` for syntax checking

#### FR6.4: infer_type_hints
```python
def infer_type_hints(
    function_code: str,
    usage_examples: list[str]
) -> dict[str, str]:
    """Suggest type hints from function code and usage.

    Args:
        function_code: Function source code
        usage_examples: Example function calls

    Returns:
        Dict with keys: parameters (JSON with types), return_type
    """
```

### FR7: CLI and Configuration Generation

#### FR7.1: generate_cli_argparse
```python
def generate_cli_argparse(
    program_name: str,
    description: str,
    arguments: list[dict[str, str]],
    subcommands: list[dict[str, str]]
) -> str:
    """Generate argparse CLI boilerplate.

    Args:
        program_name: CLI program name
        description: Program description
        arguments: List of argument dicts with keys: name, type, help, required
        subcommands: List of subcommand dicts

    Returns:
        Complete argparse setup code
    """
```

#### FR7.2: generate_config_class
```python
def generate_config_class(
    class_name: str,
    config_fields: list[dict[str, str]],
    use_pydantic: bool,
    validation_rules: list[dict[str, str]]
) -> str:
    """Generate configuration class.

    Args:
        class_name: Configuration class name
        config_fields: List of config field dicts
        use_pydantic: Use Pydantic for validation
        validation_rules: List of validation rule dicts

    Returns:
        Complete configuration class
    """
```

## Non-Functional Requirements

### NFR1: Performance
- Code generation: < 50ms for single function
- Class generation: < 100ms for complex classes
- Project structure: < 500ms for complete project

### NFR2: Code Quality
- Generated code passes ruff checks
- Generated code passes mypy checks
- Generated code follows PEP 8
- All generated functions are Google ADK compliant

### NFR3: Compatibility
- Support Python 3.9+
- Generated code compatible with Python 3.9+
- Support multiple docstring styles (Google, NumPy, Sphinx)

### NFR4: Maintainability
- Template-based generation for consistency
- Extensible for new patterns
- Clear separation of concerns

## Dependencies

### Required
- `basic-open-agent-tools` - File operations
- Python stdlib: `ast`, `inspect`, `textwrap`, `typing`

### Optional
- `black` - Code formatting validation
- `isort` - Import sorting
- `mypy` - Type checking validation

## Testing Strategy

### Unit Tests
- Test each generation function
- Test all docstring styles
- Test error handling

### Integration Tests
- Generate code and validate syntax
- Run generated code
- Test generated tests execute correctly

### Validation Tests
- Generated code passes ruff
- Generated code passes mypy
- Generated tests run successfully

### Quality Tests
- Generated code follows PEP 8
- Type hints are correct
- Docstrings are complete

## Example Use Cases

### Use Case 1: Generate ADK-Compliant Function
```python
import coding_open_agent_tools as coat

func = coat.generate_python_function(
    name="process_data",
    parameters=[
        {"name": "data", "type": "list[dict[str, str]]", "description": "Input data"},
        {"name": "operation", "type": "str", "description": "Operation type"}
    ],
    return_type="dict[str, str]",
    description="Process data with specified operation",
    docstring_style="google",
    add_type_checking=True,
    add_error_handling=True,
    raises=[
        {"type": "TypeError", "description": "If parameters are wrong type"},
        {"type": "ValueError", "description": "If operation is not supported"}
    ]
)

# Validate generated code
validation = coat.validate_python_syntax(func)
print(func)
```

### Use Case 2: Scaffold New Module
```python
# Generate complete module structure
structure = coat.generate_project_structure(
    project_name="my-agent-tools",
    package_name="my_agent_tools",
    include_tests=True,
    include_docs=True,
    include_ci=True,
    license_type="MIT"
)

# Write files using basic tools
from basic_open_agent_tools import file_system

for file_path, content in structure.items():
    file_system.write_file_from_string(
        file_path=file_path,
        content=content,
        skip_confirm=False
    )
```

### Use Case 3: Generate Test Suite
```python
# Generate tests for existing function
test_code = coat.generate_test_skeleton(
    function_signature="def calculate_total(items: list[dict], tax_rate: float) -> float",
    test_cases=[
        {"name": "basic", "description": "Test with valid inputs", "assertions": "result == 32.4"},
        {"name": "empty", "description": "Test with empty list", "assertions": "result == 0.0"},
        {"name": "invalid_type", "description": "Test type error", "assertions": "raises TypeError"}
    ],
    fixtures=["sample_items"],
    docstring="Test suite for calculate_total function"
)
```

## Success Metrics

### Functional Metrics
- 18 functions implemented
- All docstring styles supported
- Project scaffolding works correctly

### Quality Metrics
- 100% ruff compliance
- 100% mypy compliance
- 80%+ test coverage
- Generated code passes validation

### Usage Metrics
- Agents generate working code
- Generated tests execute successfully
- Projects build without errors

## Open Questions

1. Should we support type stub (.pyi) generation?
2. Do we need support for other docstring styles (reST, Epytext)?
3. Should we integrate with code formatters (black, autopep8)?
4. How do we handle code that doesn't fit templates?
5. Should we support code optimization suggestions?

## Future Enhancements (Post-v0.2.0)

1. **Advanced Templates**: Library of design patterns
2. **Code Refactoring**: Transform existing code
3. **Multi-File Generation**: Generate related files together
4. **Type Inference**: Better type hint suggestions
5. **Performance Optimization**: Suggest optimizations
6. **Documentation Sites**: Generate Sphinx/MkDocs configs
7. **API Client Generation**: Generate API clients from OpenAPI specs

---

**Document Version**: 1.0
**Last Updated**: 2025-10-14
**Status**: Draft
**Owner**: Project Team
