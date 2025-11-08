"""C# code navigation and analysis module.

This module provides navigation capabilities for C# code.
It focuses on efficient code exploration without reading entire files (saving 70-95% of tokens).

Key Capabilities:
- Code navigation (line numbers, signatures, overviews) - SAVES TOKENS!
- Method and class extraction
- Documentation parsing (XML doc comments)
- Namespace and assembly analysis

Supports:
- Modern C# (C# 8.0, 9.0, 10.0, 11.0)
- Properties and events
- Classes and interfaces
- LINQ and async/await
"""

from .navigation import (
    extract_csharp_public_api,
    find_csharp_definitions_by_comment,
    find_csharp_function_usages,
    get_csharp_function_body,
    get_csharp_function_details,
    get_csharp_function_docstring,
    get_csharp_function_line_numbers,
    get_csharp_function_signature,
    get_csharp_module_overview,
    get_csharp_specific_function_line_numbers,
    get_csharp_type_docstring,
    get_csharp_type_hierarchy,
    get_csharp_type_line_numbers,
    list_csharp_function_calls,
    list_csharp_functions,
    list_csharp_type_methods,
    list_csharp_types,
)

__all__: list[str] = [
    # Basic navigation functions (10 total)
    "get_csharp_function_line_numbers",
    "get_csharp_type_line_numbers",
    "get_csharp_module_overview",
    "list_csharp_functions",
    "list_csharp_types",
    "get_csharp_function_signature",
    "get_csharp_function_docstring",
    "list_csharp_type_methods",
    "extract_csharp_public_api",
    "get_csharp_function_details",
    # Advanced navigation (7 functions)
    "get_csharp_function_body",
    "list_csharp_function_calls",
    "find_csharp_function_usages",
    "get_csharp_specific_function_line_numbers",
    "get_csharp_type_hierarchy",
    "find_csharp_definitions_by_comment",
    "get_csharp_type_docstring",
]
