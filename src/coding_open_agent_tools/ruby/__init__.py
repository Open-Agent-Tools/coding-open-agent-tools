"""Ruby code navigation and analysis module.

This module provides navigation capabilities for Ruby code.
It focuses on efficient code exploration without reading entire files (saving 70-95% of tokens).

Key Capabilities:
- Code navigation (line numbers, signatures, overviews) - SAVES TOKENS!
- Method and class extraction
- Documentation parsing (RDoc comments)
- Module and class analysis

Supports:
- Ruby 2.x and 3.x
- Classes and modules
- Instance and class methods
- Blocks and lambdas
"""

from .navigation import (
    extract_ruby_public_api,
    find_ruby_definitions_by_comment,
    find_ruby_function_usages,
    get_ruby_function_body,
    get_ruby_function_details,
    get_ruby_function_docstring,
    get_ruby_function_line_numbers,
    get_ruby_function_signature,
    get_ruby_module_overview,
    get_ruby_specific_function_line_numbers,
    get_ruby_type_docstring,
    get_ruby_type_hierarchy,
    get_ruby_type_line_numbers,
    list_ruby_function_calls,
    list_ruby_functions,
    list_ruby_type_methods,
    list_ruby_types,
)

__all__: list[str] = [
    # Basic navigation functions (10 total)
    "get_ruby_function_line_numbers",
    "get_ruby_type_line_numbers",
    "get_ruby_module_overview",
    "list_ruby_functions",
    "list_ruby_types",
    "get_ruby_function_signature",
    "get_ruby_function_docstring",
    "list_ruby_type_methods",
    "extract_ruby_public_api",
    "get_ruby_function_details",
    # Advanced navigation (7 functions)
    "get_ruby_function_body",
    "list_ruby_function_calls",
    "find_ruby_function_usages",
    "get_ruby_specific_function_line_numbers",
    "get_ruby_type_hierarchy",
    "find_ruby_definitions_by_comment",
    "get_ruby_type_docstring",
]
