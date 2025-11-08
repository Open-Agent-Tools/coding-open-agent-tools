"""Go code navigation and analysis module.

This module provides navigation capabilities for Go code.
It focuses on efficient code exploration without reading entire files (saving 70-95% of tokens).

Key Capabilities:
- Code navigation (line numbers, signatures, overviews) - SAVES TOKENS!
- Function and type extraction
- Documentation parsing (godoc comments)
- Package and import analysis

Supports:
- Modern Go (Go 1.18+)
- Generics
- Methods and receivers
- Interfaces and structs
"""

from .navigation import (
    extract_go_public_api,
    find_go_definitions_by_comment,
    find_go_function_usages,
    get_go_function_body,
    get_go_function_details,
    get_go_function_docstring,
    get_go_function_line_numbers,
    get_go_function_signature,
    get_go_module_overview,
    get_go_specific_function_line_numbers,
    get_go_type_docstring,
    get_go_type_hierarchy,
    get_go_type_line_numbers,
    list_go_function_calls,
    list_go_functions,
    list_go_type_methods,
    list_go_types,
)

__all__: list[str] = [
    # Basic navigation functions (10 total)
    "get_go_function_line_numbers",
    "get_go_type_line_numbers",
    "get_go_module_overview",
    "list_go_functions",
    "list_go_types",
    "get_go_function_signature",
    "get_go_function_docstring",
    "list_go_type_methods",
    "extract_go_public_api",
    "get_go_function_details",
    # Advanced navigation (7 functions)
    "get_go_function_body",
    "list_go_function_calls",
    "find_go_function_usages",
    "get_go_specific_function_line_numbers",
    "get_go_type_hierarchy",
    "find_go_definitions_by_comment",
    "get_go_type_docstring",
]
