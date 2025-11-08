"""C++ code navigation and analysis module.

This module provides navigation capabilities for C++ code.
It focuses on efficient code exploration without reading entire files (saving 70-95% of tokens).

Key Capabilities:
- Code navigation (line numbers, signatures, overviews) - SAVES TOKENS!
- Function and class extraction
- Documentation parsing (doxygen comments)
- Namespace and header analysis

Supports:
- Modern C++ (C++11, C++14, C++17, C++20)
- Templates and generic programming
- Classes and inheritance
- Namespaces and scope resolution
"""

from .navigation import (
    extract_cpp_public_api,
    find_cpp_definitions_by_comment,
    find_cpp_function_usages,
    get_cpp_function_body,
    get_cpp_function_details,
    get_cpp_function_docstring,
    get_cpp_function_line_numbers,
    get_cpp_function_signature,
    get_cpp_module_overview,
    get_cpp_specific_function_line_numbers,
    get_cpp_type_docstring,
    get_cpp_type_hierarchy,
    get_cpp_type_line_numbers,
    list_cpp_function_calls,
    list_cpp_functions,
    list_cpp_type_methods,
    list_cpp_types,
)

__all__: list[str] = [
    # Basic navigation functions (10 total)
    "get_cpp_function_line_numbers",
    "get_cpp_type_line_numbers",
    "get_cpp_module_overview",
    "list_cpp_functions",
    "list_cpp_types",
    "get_cpp_function_signature",
    "get_cpp_function_docstring",
    "list_cpp_type_methods",
    "extract_cpp_public_api",
    "get_cpp_function_details",
    # Advanced navigation (7 functions)
    "get_cpp_function_body",
    "list_cpp_function_calls",
    "find_cpp_function_usages",
    "get_cpp_specific_function_line_numbers",
    "get_cpp_type_hierarchy",
    "find_cpp_definitions_by_comment",
    "get_cpp_type_docstring",
]
