"""Shell script parsing functions.

This module provides functions to parse shell scripts and extract structural
information like functions, variables, and commands. Parsing is tedious for
agents and wastes tokens.
"""

import re
from typing import Any

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def parse_shell_script(script_content: str) -> dict[str, Any]:
    """Parse shell script to extract high-level structure.

    Extracts key structural elements including shebang, functions,
    variables, comments, and control flow. Useful for understanding
    script organization without executing it.

    Args:
        script_content: The shell script content to parse

    Returns:
        Dictionary with parsed structure:
        - shebang: The shebang line or empty string
        - functions: List of function names
        - variables: List of variable names
        - has_error_handling: "true" if uses set -e or trap, "false" otherwise
        - has_functions: "true" if defines functions, "false" otherwise
        - line_count: Total number of lines
        - comment_count: Number of comment lines

    Raises:
        TypeError: If script_content is not a string
        ValueError: If script_content is empty
    """
    if not isinstance(script_content, str):
        raise TypeError("script_content must be a string")

    if not script_content.strip():
        raise ValueError("script_content cannot be empty")

    lines = script_content.split("\n")
    shebang = ""
    functions = []
    variables = []
    has_error_handling = False
    comment_count = 0

    for line_num, line in enumerate(lines):
        stripped = line.strip()

        # Extract shebang (first line only)
        if line_num == 0 and stripped.startswith("#!"):
            shebang = stripped

        # Count comments
        if stripped.startswith("#") and not stripped.startswith("#!"):
            comment_count += 1

        # Check for error handling
        if re.search(r"\bset\s+-[euxo]", stripped):
            has_error_handling = True
        if re.search(r"\btrap\s+", stripped):
            has_error_handling = True

        # Extract function definitions
        # Pattern: function_name() { or function function_name {
        func_match = re.match(r"^(?:function\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)", line)
        if func_match:
            functions.append(func_match.group(1))

        # Extract variable assignments (simple cases)
        # Pattern: VAR=value or VAR='value' or VAR="value"
        var_match = re.match(
            r"^([A-Z_][A-Z0-9_]*)\s*=\s*[\"']?[^\"']*[\"']?\s*(?:#.*)?$", stripped
        )
        if var_match and not stripped.startswith("export"):
            variables.append(var_match.group(1))

        # Also check for export VAR=value
        export_match = re.match(r"^export\s+([A-Z_][A-Z0-9_]*)\s*=", stripped)
        if export_match:
            variables.append(export_match.group(1))

    return {
        "shebang": shebang,
        "functions": functions,
        "variables": variables,
        "has_error_handling": "true" if has_error_handling else "false",
        "has_functions": "true" if functions else "false",
        "line_count": str(len(lines)),
        "comment_count": str(comment_count),
    }


@strands_tool
def extract_shell_functions(script_content: str) -> list[dict[str, str]]:
    """Extract function definitions from shell script.

    Parses function declarations and extracts their names, line numbers,
    and simple body information. Useful for understanding script organization.

    Args:
        script_content: The shell script content to parse

    Returns:
        List of function dictionaries, each with:
        - name: Function name
        - line_number: Line number where function is defined
        - has_parameters: "true" if function uses $1, $2, etc., "false" otherwise
        - has_return: "true" if function has return statement, "false" otherwise

    Raises:
        TypeError: If script_content is not a string
        ValueError: If script_content is empty
    """
    if not isinstance(script_content, str):
        raise TypeError("script_content must be a string")

    if not script_content.strip():
        raise ValueError("script_content cannot be empty")

    functions: list[dict[str, str]] = []
    lines = script_content.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Match function definition
        # Patterns: function_name() { or function function_name() { or function function_name {
        func_match = re.match(
            r"^(?:function\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)\s*\{?\s*$", stripped
        )

        if func_match:
            func_name = func_match.group(1)
            func_line = str(i + 1)

            # Scan forward to analyze function body
            has_parameters = False
            has_return = False
            brace_count = 1 if "{" in stripped else 0

            j = i + 1
            while j < len(lines) and brace_count >= 0:
                body_line = lines[j].strip()

                # Track braces to find function end
                brace_count += body_line.count("{") - body_line.count("}")

                # Check for parameter usage
                if re.search(r"\$[1-9]|\$@|\$\*", body_line):
                    has_parameters = True

                # Check for return statement
                if re.search(r"\breturn\b", body_line):
                    has_return = True

                j += 1

                # Safety limit
                if j - i > 1000:
                    break

            functions.append(
                {
                    "name": func_name,
                    "line_number": func_line,
                    "has_parameters": "true" if has_parameters else "false",
                    "has_return": "true" if has_return else "false",
                }
            )

        i += 1

    return functions


@strands_tool
def extract_shell_variables(script_content: str) -> list[dict[str, str]]:
    """Extract variable declarations from shell script.

    Finds variable assignments and extracts their names, line numbers,
    and export status. Useful for understanding script state management.

    Args:
        script_content: The shell script content to parse

    Returns:
        List of variable dictionaries, each with:
        - name: Variable name
        - line_number: Line number where variable is assigned
        - is_exported: "true" if variable is exported, "false" otherwise
        - is_readonly: "true" if declared readonly, "false" otherwise

    Raises:
        TypeError: If script_content is not a string
        ValueError: If script_content is empty
    """
    if not isinstance(script_content, str):
        raise TypeError("script_content must be a string")

    if not script_content.strip():
        raise ValueError("script_content cannot be empty")

    variables: list[dict[str, str]] = []
    lines = script_content.split("\n")
    seen_vars: set[str] = set()

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Skip comments and empty lines
        if not stripped or stripped.startswith("#"):
            continue

        is_exported = False
        is_readonly = False

        # Check for export
        if stripped.startswith("export "):
            is_exported = True
            stripped = stripped[7:].strip()

        # Check for readonly
        if stripped.startswith("readonly "):
            is_readonly = True
            stripped = stripped[9:].strip()

        # Match variable assignment
        # Pattern: VAR=value
        var_match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=", stripped)

        if var_match:
            var_name = var_match.group(1)

            # Only add first occurrence (declaration)
            if var_name not in seen_vars:
                seen_vars.add(var_name)
                variables.append(
                    {
                        "name": var_name,
                        "line_number": str(line_num),
                        "is_exported": "true" if is_exported else "false",
                        "is_readonly": "true" if is_readonly else "false",
                    }
                )

    return variables
