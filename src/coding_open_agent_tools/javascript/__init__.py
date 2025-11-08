"""JavaScript code navigation and analysis module.

This module provides navigation capabilities for JavaScript and TypeScript code.
It focuses on efficient code exploration without reading entire files (saving 70-95% of tokens).

Key Capabilities:
- Code navigation (line numbers, signatures, overviews) - SAVES TOKENS!
- Function and class extraction
- JSDoc docstring parsing
- Module export analysis
- TypeScript support (parsed as JavaScript with type annotations)

Supports:
- Modern JavaScript (ES2017+)
- TypeScript (.ts files)
- JSX/TSX for React
- CommonJS and ES6 modules
"""

from .navigation import (
    extract_javascript_public_api,
    find_javascript_definitions_by_decorator,
    find_javascript_function_usages,
    get_javascript_class_docstring,
    get_javascript_class_hierarchy,
    get_javascript_class_line_numbers,
    get_javascript_function_body,
    get_javascript_function_details,
    get_javascript_function_docstring,
    get_javascript_function_line_numbers,
    get_javascript_function_signature,
    get_javascript_method_line_numbers,
    get_javascript_module_overview,
    list_javascript_class_methods,
    list_javascript_classes,
    list_javascript_function_calls,
    list_javascript_functions,
)

__all__: list[str] = [
    # Navigation functions (17 total - matching Python module)
    "get_javascript_function_line_numbers",
    "get_javascript_class_line_numbers",
    "get_javascript_module_overview",
    "list_javascript_functions",
    "list_javascript_classes",
    "get_javascript_function_signature",
    "get_javascript_function_docstring",
    "list_javascript_class_methods",
    "extract_javascript_public_api",
    "get_javascript_function_details",
    # Advanced navigation (7 functions)
    "get_javascript_function_body",
    "list_javascript_function_calls",
    "find_javascript_function_usages",
    "get_javascript_method_line_numbers",
    "get_javascript_class_hierarchy",
    "find_javascript_definitions_by_decorator",
    "get_javascript_class_docstring",
]
