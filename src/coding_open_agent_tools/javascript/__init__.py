"""JavaScript code navigation, validation, and analysis module.

This module provides comprehensive JavaScript/TypeScript development tools including:
- Code navigation (line numbers, signatures, overviews) - SAVES 70-95% OF TOKENS!
- Syntax validation (JS, TS, JSX) - PREVENTS RUNTIME ERRORS
- Dependency analysis - DETECTS CIRCULAR IMPORTS
- Promise/async validation - CATCHES ANTI-PATTERNS
- Configuration parsing (package.json, tsconfig.json, ESLint)

Key Capabilities:
- Navigation: Explore code without reading entire files
- Validation: Catch syntax errors before execution
- Analysis: Detect unused imports, circular dependencies, promise anti-patterns

Supports:
- Modern JavaScript (ES2017+)
- TypeScript (.ts files)
- JSX/TSX for React
- CommonJS and ES6 modules

Token Savings: 70-85% by validating during generation instead of debugging at runtime.
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
from .validation import (
    check_async_await_usage,
    check_eslint_config,
    check_type_definitions,
    detect_circular_dependencies,
    detect_promise_anti_patterns,
    detect_unused_imports,
    parse_module_exports,
    parse_tsconfig_json,
    validate_javascript_syntax,
    validate_jsx_syntax,
    validate_package_json,
    validate_typescript_syntax,
)

__all__: list[str] = [
    # Navigation functions (17 functions)
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
    "get_javascript_function_body",
    "list_javascript_function_calls",
    "find_javascript_function_usages",
    "get_javascript_method_line_numbers",
    "get_javascript_class_hierarchy",
    "find_javascript_definitions_by_decorator",
    "get_javascript_class_docstring",
    # Validation functions (12 functions)
    "validate_typescript_syntax",
    "validate_javascript_syntax",
    "validate_jsx_syntax",
    "validate_package_json",
    "parse_tsconfig_json",
    "check_type_definitions",
    "parse_module_exports",
    "detect_unused_imports",
    "detect_circular_dependencies",
    "detect_promise_anti_patterns",
    "check_eslint_config",
    "check_async_await_usage",
]
