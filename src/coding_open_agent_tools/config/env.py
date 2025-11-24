"""Environment file (.env) parsing and manipulation functions.

Provides tools for parsing, validating, and manipulating .env files.
"""

import re
from typing import Any

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def parse_env_file(env_content: str) -> dict[str, str]:
    """Parse .env file content into a dictionary.

    Handles comments, blank lines, quoted values, and basic variable expansion.

    Args:
        env_content: .env file content as string

    Returns:
        Dictionary with:
        - success: "true" or "false"
        - variable_count: Number of variables parsed
        - variables: JSON string of key-value pairs
        - error_message: Error description if parsing failed

    Raises:
        TypeError: If env_content is not a string
        ValueError: If env_content is empty
    """
    if not isinstance(env_content, str):
        raise TypeError("env_content must be a string")
    if not env_content.strip():
        raise ValueError("env_content cannot be empty")

    variables = {}
    line_num = 0

    try:
        for line in env_content.splitlines():
            line_num += 1
            # Strip whitespace
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Check for valid assignment
            if "=" not in line:
                continue

            # Split on first = only
            key, value = line.split("=", 1)
            key = key.strip()

            # Validate key (alphanumeric and underscore only)
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
                continue

            # Process value
            value = value.strip()

            # Handle quoted values
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            # Remove inline comments (but preserve # in quoted strings)
            if "#" in value and not (value.startswith('"') or value.startswith("'")):
                value = value.split("#")[0].strip()

            variables[key] = value

        import json

        return {
            "success": "true",
            "variable_count": str(len(variables)),
            "variables": json.dumps(variables),
            "error_message": "",
        }

    except Exception as e:
        import json

        return {
            "success": "false",
            "variable_count": "0",
            "variables": json.dumps({}),
            "error_message": f"Parse error at line {line_num}: {str(e)}",
        }


@strands_tool
def validate_env_file(env_content: str) -> dict[str, str]:
    """Validate .env file syntax and structure.

    Checks for common issues like invalid variable names, malformed lines,
    and syntax errors.

    Args:
        env_content: .env file content as string

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - error_count: Number of errors found
        - warning_count: Number of warnings
        - errors: JSON string of error messages
        - warnings: JSON string of warning messages

    Raises:
        TypeError: If env_content is not a string
        ValueError: If env_content is empty
    """
    if not isinstance(env_content, str):
        raise TypeError("env_content must be a string")
    if not env_content.strip():
        raise ValueError("env_content cannot be empty")

    errors = []
    warnings = []

    for line_num, line in enumerate(env_content.splitlines(), 1):
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            continue

        # Check for assignment operator
        if "=" not in stripped:
            errors.append(f"Line {line_num}: Missing '=' assignment operator")
            continue

        # Split on first =
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()

        # Validate key format
        if not key:
            errors.append(f"Line {line_num}: Empty variable name")
        elif not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
            errors.append(
                f"Line {line_num}: Invalid variable name '{key}' (must start with letter/underscore, contain only alphanumeric/underscore)"
            )

        # Check for lowercase keys (warning)
        if key and key.islower():
            warnings.append(
                f"Line {line_num}: Variable '{key}' uses lowercase (convention is UPPERCASE)"
            )

        # Check for unquoted values with spaces
        if " " in value and not (
            (value.startswith('"') and value.endswith('"'))
            or (value.startswith("'") and value.endswith("'"))
        ):
            warnings.append(f"Line {line_num}: Value contains spaces but is not quoted")

        # Check for mismatched quotes
        if value.startswith('"') and not value.endswith('"'):
            errors.append(f"Line {line_num}: Mismatched double quotes")
        elif value.startswith("'") and not value.endswith("'"):
            errors.append(f"Line {line_num}: Mismatched single quotes")

    import json

    return {
        "is_valid": "true" if len(errors) == 0 else "false",
        "error_count": str(len(errors)),
        "warning_count": str(len(warnings)),
        "errors": json.dumps(errors),
        "warnings": json.dumps(warnings),
    }


@strands_tool
def extract_env_variable(env_content: str, variable_name: str) -> dict[str, str]:
    """Extract a specific environment variable value from .env content.

    Args:
        env_content: .env file content as string
        variable_name: Name of the variable to extract

    Returns:
        Dictionary with:
        - found: "true" or "false"
        - value: The variable value if found
        - line_number: Line number where variable was found
        - error_message: Error description if not found

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty
    """
    if not isinstance(env_content, str):
        raise TypeError("env_content must be a string")
    if not isinstance(variable_name, str):
        raise TypeError("variable_name must be a string")
    if not env_content.strip():
        raise ValueError("env_content cannot be empty")
    if not variable_name.strip():
        raise ValueError("variable_name cannot be empty")

    for line_num, line in enumerate(env_content.splitlines(), 1):
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            continue

        # Check for assignment
        if "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()

        if key == variable_name:
            value = value.strip()

            # Remove quotes
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            return {
                "found": "true",
                "value": value,
                "line_number": str(line_num),
                "error_message": "",
            }

    return {
        "found": "false",
        "value": "",
        "line_number": "0",
        "error_message": f"Variable '{variable_name}' not found in .env content",
    }


@strands_tool
def merge_env_files(env_content1: str, env_content2: str) -> dict[str, str]:
    """Merge two .env file contents with precedence for the second file.

    Variables in env_content2 override those in env_content1.

    Args:
        env_content1: First .env file content (lower precedence)
        env_content2: Second .env file content (higher precedence)

    Returns:
        Dictionary with:
        - success: "true" or "false"
        - merged_content: Merged .env file content
        - variable_count: Total number of variables in result
        - overridden_count: Number of variables overridden by second file
        - error_message: Error description if merge failed

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty
    """
    if not isinstance(env_content1, str):
        raise TypeError("env_content1 must be a string")
    if not isinstance(env_content2, str):
        raise TypeError("env_content2 must be a string")
    if not env_content1.strip():
        raise ValueError("env_content1 cannot be empty")
    if not env_content2.strip():
        raise ValueError("env_content2 cannot be empty")

    # Parse both files
    result1 = parse_env_file(env_content1)
    result2 = parse_env_file(env_content2)

    if result1["success"] == "false":
        return {
            "success": "false",
            "merged_content": "",
            "variable_count": "0",
            "overridden_count": "0",
            "error_message": f"Failed to parse env_content1: {result1['error_message']}",
        }

    if result2["success"] == "false":
        return {
            "success": "false",
            "merged_content": "",
            "variable_count": "0",
            "overridden_count": "0",
            "error_message": f"Failed to parse env_content2: {result2['error_message']}",
        }

    import json

    vars1 = json.loads(result1["variables"])
    vars2 = json.loads(result2["variables"])

    # Count overrides
    overridden = sum(1 for key in vars2 if key in vars1)

    # Merge with precedence for vars2
    merged = {**vars1, **vars2}

    # Build merged content
    lines = []
    for key, value in sorted(merged.items()):
        # Quote values with spaces
        if " " in value:
            value = f'"{value}"'
        lines.append(f"{key}={value}")

    merged_content = "\n".join(lines)

    return {
        "success": "true",
        "merged_content": merged_content,
        "variable_count": str(len(merged)),
        "overridden_count": str(overridden),
        "error_message": "",
    }


@strands_tool
def substitute_env_variables(
    template_string: str, env_variables: str
) -> dict[str, str]:
    """Substitute environment variable references in a template string.

    Expands ${VAR} and $VAR patterns using provided variables.

    Args:
        template_string: String with variable references (e.g., "Hello ${NAME}")
        env_variables: JSON string of variable key-value pairs

    Returns:
        Dictionary with:
        - success: "true" or "false"
        - result: String with variables substituted
        - substitution_count: Number of substitutions made
        - unresolved: JSON list of unresolved variable names
        - error_message: Error description if substitution failed

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty or env_variables is invalid JSON
    """
    if not isinstance(template_string, str):
        raise TypeError("template_string must be a string")
    if not isinstance(env_variables, str):
        raise TypeError("env_variables must be a string")
    if not template_string:
        raise ValueError("template_string cannot be empty")
    if not env_variables.strip():
        raise ValueError("env_variables cannot be empty")

    import json

    try:
        variables = json.loads(env_variables)
    except json.JSONDecodeError as e:
        return {
            "success": "false",
            "result": "",
            "substitution_count": "0",
            "unresolved": json.dumps([]),
            "error_message": f"Invalid JSON in env_variables: {str(e)}",
        }

    if not isinstance(variables, dict):
        return {
            "success": "false",
            "result": "",
            "substitution_count": "0",
            "unresolved": json.dumps([]),
            "error_message": "env_variables must be a JSON object/dictionary",
        }

    result = template_string
    substitutions = 0
    unresolved = []

    # Find all variable references
    # Pattern matches ${VAR} and $VAR
    pattern = r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)"

    def replace_var(match: Any) -> str:
        nonlocal substitutions, unresolved

        var_name = match.group(1) or match.group(2)

        if var_name in variables:
            substitutions += 1
            return str(variables[var_name])
        else:
            if var_name not in unresolved:
                unresolved.append(var_name)
            return str(match.group(0))  # Keep original if not found

    result = re.sub(pattern, replace_var, result)

    return {
        "success": "true",
        "result": result,
        "substitution_count": str(substitutions),
        "unresolved": json.dumps(unresolved),
        "error_message": "",
    }
