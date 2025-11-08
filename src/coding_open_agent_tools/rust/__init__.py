"""Rust code navigation and analysis module.

This module provides navigation capabilities for Rust code.
It focuses on efficient code exploration without reading entire files (saving 70-95% of tokens).

Key Capabilities:
- Code navigation (line numbers, signatures, overviews) - SAVES TOKENS!
- Function and type extraction
- Documentation parsing (doc comments)
- Module and crate analysis

Supports:
- Modern Rust (2021 edition)
- Generics and lifetimes
- Traits and implementations
- Macros and attributes
"""

from .navigation import (
    extract_rust_public_api,
    find_rust_definitions_by_comment,
    find_rust_function_usages,
    get_rust_function_body,
    get_rust_function_details,
    get_rust_function_docstring,
    get_rust_function_line_numbers,
    get_rust_function_signature,
    get_rust_module_overview,
    get_rust_specific_function_line_numbers,
    get_rust_type_docstring,
    get_rust_type_hierarchy,
    get_rust_type_line_numbers,
    list_rust_function_calls,
    list_rust_functions,
    list_rust_type_methods,
    list_rust_types,
)

__all__: list[str] = [
    # Basic navigation functions (10 total)
    "get_rust_function_line_numbers",
    "get_rust_type_line_numbers",
    "get_rust_module_overview",
    "list_rust_functions",
    "list_rust_types",
    "get_rust_function_signature",
    "get_rust_function_docstring",
    "list_rust_type_methods",
    "extract_rust_public_api",
    "get_rust_function_details",
    # Advanced navigation (7 functions)
    "get_rust_function_body",
    "list_rust_function_calls",
    "find_rust_function_usages",
    "get_rust_specific_function_line_numbers",
    "get_rust_type_hierarchy",
    "find_rust_definitions_by_comment",
    "get_rust_type_docstring",
]
