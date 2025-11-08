"""Python code validation, analysis, and navigation module.

This module provides validation, parsing, analysis, and navigation capabilities for
Python code. It focuses on preventing errors, extracting structure, and enabling
efficient code exploration without reading entire files (saving 80-95% of tokens).

Key Capabilities:
- Code navigation (line numbers, signatures, overviews) - SAVES TOKENS!
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
from .navigation import (
    extract_python_public_api,
    find_python_definitions_by_decorator,
    find_python_function_usages,
    get_python_class_docstring,
    get_python_class_hierarchy,
    get_python_class_line_numbers,
    get_python_function_body,
    get_python_function_details,
    get_python_function_docstring,
    get_python_function_line_numbers,
    get_python_function_signature,
    get_python_method_line_numbers,
    get_python_module_overview,
    list_python_class_methods,
    list_python_classes,
    list_python_function_calls,
    list_python_functions,
)
from .validators import (
    check_adk_compliance,
    validate_import_order,
    validate_python_syntax,
    validate_type_hints,
)

__all__: list[str] = [
    # Navigation (v0.4.4 + v0.5.0 - Token-saving code exploration)
    "get_python_function_line_numbers",
    "get_python_class_line_numbers",
    "get_python_module_overview",
    "list_python_functions",
    "list_python_classes",
    "get_python_function_signature",
    "get_python_function_docstring",
    "list_python_class_methods",
    "extract_python_public_api",
    "get_python_function_details",
    # Navigation v0.5.0 additions (7 new functions)
    "get_python_function_body",
    "list_python_function_calls",
    "find_python_function_usages",
    "get_python_method_line_numbers",
    "get_python_class_hierarchy",
    "find_python_definitions_by_decorator",
    "get_python_class_docstring",
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
