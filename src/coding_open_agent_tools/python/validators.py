"""Python code validators for syntax, types, imports, and ADK compliance.

This module provides validation functions to catch errors before execution:
- Syntax validation using AST parsing
- Type hint validation and consistency checking
- Import order validation (PEP 8)
- Google ADK compliance checking
"""

import ast
import re
from typing import Any

from coding_open_agent_tools._decorators import strands_tool
from coding_open_agent_tools.types import STDLIB_MODULES


@strands_tool
def validate_python_syntax(source_code: str) -> dict[str, str]:
    """Validate Python source code syntax using AST parsing.

    Prevents execution failures by catching syntax errors early. This saves
    agent tokens by avoiding retry loops from syntax errors.

    Args:
        source_code: Python source code to validate

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - error_message: Error description if invalid, empty if valid
        - line_number: Line number of error if invalid, "0" if valid
        - column_offset: Column offset of error if invalid, "0" if valid
        - error_type: Type of syntax error if invalid, empty if valid

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        ast.parse(source_code)
        return {
            "is_valid": "true",
            "error_message": "",
            "line_number": "0",
            "column_offset": "0",
            "error_type": "",
        }
    except SyntaxError as e:
        return {
            "is_valid": "false",
            "error_message": str(e.msg) if e.msg else "Syntax error",
            "line_number": str(e.lineno) if e.lineno else "0",
            "column_offset": str(e.offset) if e.offset else "0",
            "error_type": "SyntaxError",
        }
    except Exception as e:
        return {
            "is_valid": "false",
            "error_message": str(e),
            "line_number": "0",
            "column_offset": "0",
            "error_type": type(e).__name__,
        }


@strands_tool
def validate_type_hints(source_code: str) -> dict[str, Any]:
    """Validate type hints for correctness and consistency.

    Checks for:
    - Invalid type hint syntax
    - Inconsistent return type annotations
    - Missing type hints on function parameters
    - Use of deprecated typing constructs

    Args:
        source_code: Python source code to validate

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - issues_found: List of issue dictionaries with:
          - line_number: Line number of issue
          - function_name: Name of function with issue
          - issue_type: Type of type hint issue
          - description: Description of the issue
          - recommendation: How to fix the issue
        - total_issues: String count of total issues
        - functions_checked: String count of functions checked

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    issues: list[dict[str, str]] = []

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return {
            "is_valid": "false",
            "issues_found": [
                {
                    "line_number": "0",
                    "function_name": "",
                    "issue_type": "syntax_error",
                    "description": "Cannot parse source code - syntax error",
                    "recommendation": "Fix syntax errors first using validate_python_syntax()",
                }
            ],
            "total_issues": "1",
            "functions_checked": "0",
        }

    functions_checked = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions_checked += 1
            func_name = node.name
            line_num = str(node.lineno)

            # Check for missing return type annotation
            if node.returns is None and func_name != "__init__":
                issues.append(
                    {
                        "line_number": line_num,
                        "function_name": func_name,
                        "issue_type": "missing_return_type",
                        "description": f"Function '{func_name}' missing return type annotation",
                        "recommendation": "Add return type annotation (e.g., -> None, -> str, -> dict[str, str])",
                    }
                )

            # Check for missing parameter type annotations
            for arg in node.args.args:
                if arg.annotation is None and arg.arg != "self" and arg.arg != "cls":
                    issues.append(
                        {
                            "line_number": line_num,
                            "function_name": func_name,
                            "issue_type": "missing_parameter_type",
                            "description": f"Parameter '{arg.arg}' in '{func_name}' missing type annotation",
                            "recommendation": f"Add type annotation for parameter '{arg.arg}'",
                        }
                    )

            # Check for deprecated typing constructs (List, Dict, Tuple vs list, dict, tuple)
            source_lines = source_code.split("\n")
            if node.lineno <= len(source_lines):
                # Check function signature and body for deprecated typing
                func_end = (
                    node.end_lineno
                    if hasattr(node, "end_lineno") and node.end_lineno
                    else node.lineno + 10
                )
                func_lines = source_lines[node.lineno - 1 : func_end]
                func_text = "\n".join(func_lines)

                deprecated_patterns = [
                    (r"\bList\[", "List", "list"),
                    (r"\bDict\[", "Dict", "dict"),
                    (r"\bTuple\[", "Tuple", "tuple"),
                    (r"\bSet\[", "Set", "set"),
                ]

                for pattern, old, new in deprecated_patterns:
                    if re.search(pattern, func_text):
                        issues.append(
                            {
                                "line_number": line_num,
                                "function_name": func_name,
                                "issue_type": "deprecated_typing",
                                "description": f"Function '{func_name}' uses deprecated '{old}' from typing module",
                                "recommendation": f"Use built-in '{new}' instead of 'typing.{old}' (Python 3.9+)",
                            }
                        )

    return {
        "is_valid": "true" if len(issues) == 0 else "false",
        "issues_found": issues,
        "total_issues": str(len(issues)),
        "functions_checked": str(functions_checked),
    }


@strands_tool
def validate_import_order(source_code: str) -> dict[str, Any]:
    """Validate that imports follow PEP 8 ordering conventions.

    PEP 8 import order:
    1. Standard library imports
    2. Related third-party imports
    3. Local application/library specific imports

    Within each group, imports should be alphabetically sorted.

    Args:
        source_code: Python source code to validate

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - issues_found: List of issue dictionaries with:
          - line_number: Line number of issue
          - import_name: Name of the import
          - issue_type: Type of import order issue
          - description: Description of the issue
          - recommendation: How to fix the issue
        - total_issues: String count of total issues
        - imports_checked: String count of imports checked

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    issues: list[dict[str, str]] = []

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return {
            "is_valid": "false",
            "issues_found": [
                {
                    "line_number": "0",
                    "import_name": "",
                    "issue_type": "syntax_error",
                    "description": "Cannot parse source code - syntax error",
                    "recommendation": "Fix syntax errors first using validate_python_syntax()",
                }
            ],
            "total_issues": "1",
            "imports_checked": "0",
        }

    # Extract all imports with their line numbers and types
    imports: list[tuple[int, str, str]] = []  # (line_num, import_name, import_type)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, alias.name, _classify_import(alias.name)))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(
                    (node.lineno, node.module, _classify_import(node.module))
                )

    imports_checked = len(imports)

    if imports_checked == 0:
        return {
            "is_valid": "true",
            "issues_found": [],
            "total_issues": "0",
            "imports_checked": "0",
        }

    # Check for incorrect ordering between groups
    prev_type = "stdlib"

    for line_num, import_name, import_type in imports:
        # Check if import type goes backward (e.g., stdlib after third-party)
        type_order = {"stdlib": 0, "third_party": 1, "local": 2}

        if type_order[import_type] < type_order[prev_type]:
            issues.append(
                {
                    "line_number": str(line_num),
                    "import_name": import_name,
                    "issue_type": "incorrect_group_order",
                    "description": f"Import '{import_name}' ({import_type}) comes after {prev_type} imports",
                    "recommendation": f"Move {import_type} imports before {prev_type} imports per PEP 8",
                }
            )

        prev_type = import_type

    # Check alphabetical ordering within each group
    groups: dict[str, list[tuple[int, str]]] = {
        "stdlib": [],
        "third_party": [],
        "local": [],
    }

    for line_num, import_name, import_type in imports:
        groups[import_type].append((line_num, import_name))

    for group_type, group_imports in groups.items():
        if len(group_imports) <= 1:
            continue

        # Check if imports are alphabetically sorted
        sorted_names = sorted([name for _, name in group_imports])
        actual_names = [name for _, name in group_imports]

        if sorted_names != actual_names:
            first_line = str(group_imports[0][0])
            issues.append(
                {
                    "line_number": first_line,
                    "import_name": group_type,
                    "issue_type": "incorrect_alphabetical_order",
                    "description": f"Imports in {group_type} group are not alphabetically sorted",
                    "recommendation": "Sort imports alphabetically within each group per PEP 8",
                }
            )

    return {
        "is_valid": "true" if len(issues) == 0 else "false",
        "issues_found": issues,
        "total_issues": str(len(issues)),
        "imports_checked": str(imports_checked),
    }


@strands_tool
def check_adk_compliance(source_code: str, function_name: str) -> dict[str, Any]:
    """Check if a function follows Google ADK compliance standards.

    Google ADK standards:
    - All parameters and return values must be JSON-serializable
    - No default parameter values allowed
    - All parameters must have type hints
    - Return type must be specified
    - Use dict[str, str] or dict[str, Any] for return types, not custom objects

    Args:
        source_code: Python source code containing the function
        function_name: Name of the function to check

    Returns:
        Dictionary with:
        - is_compliant: "true" or "false"
        - issues_found: List of issue dictionaries with:
          - line_number: Line number of issue
          - issue_type: Type of compliance issue
          - description: Description of the issue
          - recommendation: How to fix the issue
        - total_issues: String count of total issues
        - function_name: Name of function checked

    Raises:
        TypeError: If source_code or function_name is not a string
        ValueError: If source_code is empty or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(function_name, str):
        raise TypeError("function_name must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")
    if not function_name.strip():
        raise ValueError("function_name cannot be empty")

    issues: list[dict[str, str]] = []

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return {
            "is_compliant": "false",
            "issues_found": [
                {
                    "line_number": "0",
                    "issue_type": "syntax_error",
                    "description": "Cannot parse source code - syntax error",
                    "recommendation": "Fix syntax errors first using validate_python_syntax()",
                }
            ],
            "total_issues": "1",
            "function_name": function_name,
        }

    function_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            function_node = node
            break

    if function_node is None:
        raise ValueError(f"Function '{function_name}' not found in source code")

    line_num = str(function_node.lineno)

    # Check for missing return type
    if function_node.returns is None:
        issues.append(
            {
                "line_number": line_num,
                "issue_type": "missing_return_type",
                "description": "Function missing return type annotation (required by ADK)",
                "recommendation": "Add return type annotation (e.g., -> dict[str, str])",
            }
        )

    # Check for default parameter values (not allowed in ADK)
    if function_node.args.defaults:
        issues.append(
            {
                "line_number": line_num,
                "issue_type": "default_parameter_values",
                "description": "Function has default parameter values (not allowed by ADK)",
                "recommendation": "Remove default values - all parameters must be explicitly provided",
            }
        )

    # Check for missing parameter type annotations
    for arg in function_node.args.args:
        if arg.annotation is None and arg.arg not in ("self", "cls"):
            issues.append(
                {
                    "line_number": line_num,
                    "issue_type": "missing_parameter_type",
                    "description": f"Parameter '{arg.arg}' missing type annotation (required by ADK)",
                    "recommendation": f"Add type annotation for parameter '{arg.arg}'",
                }
            )

    # Check return type is JSON-serializable
    if function_node.returns:
        return_annotation = ast.unparse(function_node.returns)

        # Non-JSON-serializable type patterns
        non_json_patterns = [
            (r"\bset\b", "set", "list"),
            (r"\btuple\b", "tuple", "list"),
            (r"\bfrozenset\b", "frozenset", "list"),
            (r"\bbytes\b", "bytes", "str"),
            (r"\bbytearray\b", "bytearray", "str"),
        ]

        for pattern, bad_type, suggestion in non_json_patterns:
            if re.search(pattern, return_annotation):
                issues.append(
                    {
                        "line_number": line_num,
                        "issue_type": "non_json_serializable_return",
                        "description": f"Return type uses non-JSON-serializable type '{bad_type}'",
                        "recommendation": f"Use '{suggestion}' instead of '{bad_type}' for JSON serialization",
                    }
                )

    return {
        "is_compliant": "true" if len(issues) == 0 else "false",
        "issues_found": issues,
        "total_issues": str(len(issues)),
        "function_name": function_name,
    }


def _classify_import(import_name: str) -> str:
    """Classify an import as stdlib, third-party, or local.

    Args:
        import_name: Name of the import (e.g., 'os', 'requests', 'myapp.utils')

    Returns:
        One of: "stdlib", "third_party", "local"
    """
    base_module = import_name.split(".")[0]

    if base_module in STDLIB_MODULES:
        return "stdlib"
    elif base_module.startswith("_"):  # Private/local modules often start with _
        return "local"
    else:
        # If it contains a dot and looks like a relative import, it's local
        if "." in import_name and not any(
            import_name.startswith(pkg)
            for pkg in ["google", "microsoft", "amazon", "aws"]
        ):
            return "local"
        return "third_party"
