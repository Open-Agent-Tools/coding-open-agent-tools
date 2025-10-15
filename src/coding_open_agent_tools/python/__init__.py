"""Python code validation and analysis module.

This module provides validation, parsing, and analysis capabilities for Python code.
It focuses on preventing errors and extracting structure, NOT on generating Python
code (agents excel at that).

Key Capabilities:
- Syntax and type hint validation
- Function signature and docstring extraction
- Import analysis and formatting
- ADK compliance checking
- Anti-pattern detection
"""

from .analyzers import (
    check_test_coverage_gaps,
    detect_circular_imports,
    find_unused_imports,
    identify_anti_patterns,
)
from .extractors import (
    extract_docstring_info,
    extract_type_annotations,
    get_function_dependencies,
    parse_function_signature,
)
from .formatters import format_docstring, normalize_type_hints, sort_imports
from .validators import (
    check_adk_compliance,
    validate_import_order,
    validate_python_syntax,
    validate_type_hints,
)

__all__: list[str] = [
    # Validators
    "validate_python_syntax",
    "validate_type_hints",
    "validate_import_order",
    "check_adk_compliance",
    # Extractors
    "parse_function_signature",
    "extract_docstring_info",
    "extract_type_annotations",
    "get_function_dependencies",
    # Formatters
    "format_docstring",
    "sort_imports",
    "normalize_type_hints",
    # Analyzers
    "detect_circular_imports",
    "find_unused_imports",
    "identify_anti_patterns",
    "check_test_coverage_gaps",
]
