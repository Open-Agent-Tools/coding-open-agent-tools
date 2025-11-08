"""Java code navigation and analysis module.

This module provides navigation capabilities for Java code.
It focuses on efficient code exploration without reading entire files (saving 70-95% of tokens).

Key Capabilities:
- Code navigation (line numbers, signatures, overviews) - SAVES TOKENS!
- Method and class extraction
- Javadoc parsing
- Package and import analysis
- Annotation detection

Supports:
- Modern Java (Java 8+)
- Annotations (@Override, @Deprecated, custom)
- Generic types
- Lambda expressions
- Interfaces and abstract classes
"""

from .navigation import (
    extract_java_public_api,
    find_java_definitions_by_annotation,
    find_java_method_usages,
    get_java_class_docstring,
    get_java_class_hierarchy,
    get_java_class_line_numbers,
    get_java_method_body,
    get_java_method_details,
    get_java_method_docstring,
    get_java_method_line_numbers,
    get_java_method_signature,
    get_java_module_overview,
    get_java_specific_method_line_numbers,
    list_java_class_methods,
    list_java_classes,
    list_java_method_calls,
    list_java_methods,
)

__all__: list[str] = [
    # Navigation functions (17 total - matching Python/JavaScript modules)
    "get_java_method_line_numbers",
    "get_java_class_line_numbers",
    "get_java_module_overview",
    "list_java_methods",
    "list_java_classes",
    "get_java_method_signature",
    "get_java_method_docstring",
    "list_java_class_methods",
    "extract_java_public_api",
    "get_java_method_details",
    # Advanced navigation (7 functions)
    "get_java_method_body",
    "list_java_method_calls",
    "find_java_method_usages",
    "get_java_specific_method_line_numbers",
    "get_java_class_hierarchy",
    "find_java_definitions_by_annotation",
    "get_java_class_docstring",
]
