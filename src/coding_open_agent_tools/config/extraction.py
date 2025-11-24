"""Configuration value extraction and manipulation functions.

Provides tools for extracting specific values from YAML, TOML, and JSON configs,
as well as merging multiple configuration files.
"""

import json
import sys
from typing import Any

from coding_open_agent_tools._decorators import strands_tool

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


def _get_nested_value(data: Any, path: str) -> tuple[bool, Any, str]:
    """Helper to get nested value from dict using dot notation.

    Args:
        data: Dictionary to search
        path: Dot-separated path (e.g., "database.host")

    Returns:
        Tuple of (found, value, error_message)
    """
    keys = path.split(".")
    current = data

    for i, key in enumerate(keys):
        if not isinstance(current, dict):
            return (
                False,
                None,
                f"Path segment '{'.'.join(keys[:i])}' is not a dictionary",
            )

        if key not in current:
            return (
                False,
                None,
                f"Key '{key}' not found at path '{'.'.join(keys[: i + 1])}'",
            )

        current = current[key]

    return True, current, ""


@strands_tool
def extract_yaml_value(yaml_content: str, value_path: str) -> dict[str, str]:
    """Extract a specific value from YAML content using dot notation path.

    Args:
        yaml_content: YAML content as string
        value_path: Dot-separated path to value (e.g., "database.host")

    Returns:
        Dictionary with:
        - found: "true" or "false"
        - value: JSON string of the extracted value
        - value_type: Type of the value (string, number, boolean, array, object)
        - error_message: Error description if extraction failed

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty
    """
    if not isinstance(yaml_content, str):
        raise TypeError("yaml_content must be a string")
    if not isinstance(value_path, str):
        raise TypeError("value_path must be a string")
    if not yaml_content.strip():
        raise ValueError("yaml_content cannot be empty")
    if not value_path.strip():
        raise ValueError("value_path cannot be empty")

    if yaml is None:
        return {
            "found": "false",
            "value": "",
            "value_type": "",
            "error_message": "PyYAML not installed. Install with: pip install PyYAML",
        }

    try:
        data = yaml.safe_load(yaml_content)

        if not isinstance(data, dict):
            return {
                "found": "false",
                "value": "",
                "value_type": "",
                "error_message": "YAML root must be a dictionary/mapping",
            }

        found, value, error = _get_nested_value(data, value_path)

        if not found:
            return {
                "found": "false",
                "value": "",
                "value_type": "",
                "error_message": error,
            }

        # Determine value type
        if isinstance(value, bool):
            value_type = "boolean"
        elif isinstance(value, (int, float)):
            value_type = "number"
        elif isinstance(value, str):
            value_type = "string"
        elif isinstance(value, list):
            value_type = "array"
        elif isinstance(value, dict):
            value_type = "object"
        else:
            value_type = "unknown"

        return {
            "found": "true",
            "value": json.dumps(value),
            "value_type": value_type,
            "error_message": "",
        }

    except yaml.YAMLError as e:
        return {
            "found": "false",
            "value": "",
            "value_type": "",
            "error_message": f"YAML parse error: {str(e)}",
        }
    except Exception as e:
        return {
            "found": "false",
            "value": "",
            "value_type": "",
            "error_message": f"Extraction error: {str(e)}",
        }


@strands_tool
def extract_toml_value(toml_content: str, value_path: str) -> dict[str, str]:
    """Extract a specific value from TOML content using dot notation path.

    Args:
        toml_content: TOML content as string
        value_path: Dot-separated path to value (e.g., "database.host")

    Returns:
        Dictionary with:
        - found: "true" or "false"
        - value: JSON string of the extracted value
        - value_type: Type of the value (string, number, boolean, array, object)
        - error_message: Error description if extraction failed

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty
    """
    if not isinstance(toml_content, str):
        raise TypeError("toml_content must be a string")
    if not isinstance(value_path, str):
        raise TypeError("value_path must be a string")
    if not toml_content.strip():
        raise ValueError("toml_content cannot be empty")
    if not value_path.strip():
        raise ValueError("value_path cannot be empty")

    if tomllib is None:
        return {
            "found": "false",
            "value": "",
            "value_type": "",
            "error_message": "tomli not installed (Python <3.11). Install with: pip install tomli",
        }

    try:
        data = tomllib.loads(toml_content)

        found, value, error = _get_nested_value(data, value_path)

        if not found:
            return {
                "found": "false",
                "value": "",
                "value_type": "",
                "error_message": error,
            }

        # Determine value type
        if isinstance(value, bool):
            value_type = "boolean"
        elif isinstance(value, (int, float)):
            value_type = "number"
        elif isinstance(value, str):
            value_type = "string"
        elif isinstance(value, list):
            value_type = "array"
        elif isinstance(value, dict):
            value_type = "object"
        else:
            value_type = "unknown"

        return {
            "found": "true",
            "value": json.dumps(value),
            "value_type": value_type,
            "error_message": "",
        }

    except Exception as e:
        return {
            "found": "false",
            "value": "",
            "value_type": "",
            "error_message": f"TOML parse error: {str(e)}",
        }


@strands_tool
def extract_json_value(json_content: str, value_path: str) -> dict[str, str]:
    """Extract a specific value from JSON content using dot notation path.

    Args:
        json_content: JSON content as string
        value_path: Dot-separated path to value (e.g., "database.host")

    Returns:
        Dictionary with:
        - found: "true" or "false"
        - value: JSON string of the extracted value
        - value_type: Type of the value (string, number, boolean, array, object, null)
        - error_message: Error description if extraction failed

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty
    """
    if not isinstance(json_content, str):
        raise TypeError("json_content must be a string")
    if not isinstance(value_path, str):
        raise TypeError("value_path must be a string")
    if not json_content.strip():
        raise ValueError("json_content cannot be empty")
    if not value_path.strip():
        raise ValueError("value_path cannot be empty")

    try:
        data = json.loads(json_content)

        if not isinstance(data, dict):
            return {
                "found": "false",
                "value": "",
                "value_type": "",
                "error_message": "JSON root must be an object/dictionary",
            }

        found, value, error = _get_nested_value(data, value_path)

        if not found:
            return {
                "found": "false",
                "value": "",
                "value_type": "",
                "error_message": error,
            }

        # Determine value type
        if value is None:
            value_type = "null"
        elif isinstance(value, bool):
            value_type = "boolean"
        elif isinstance(value, (int, float)):
            value_type = "number"
        elif isinstance(value, str):
            value_type = "string"
        elif isinstance(value, list):
            value_type = "array"
        elif isinstance(value, dict):
            value_type = "object"
        else:
            value_type = "unknown"

        return {
            "found": "true",
            "value": json.dumps(value),
            "value_type": value_type,
            "error_message": "",
        }

    except json.JSONDecodeError as e:
        return {
            "found": "false",
            "value": "",
            "value_type": "",
            "error_message": f"JSON parse error: {str(e)}",
        }
    except Exception as e:
        return {
            "found": "false",
            "value": "",
            "value_type": "",
            "error_message": f"Extraction error: {str(e)}",
        }


@strands_tool
def merge_yaml_files(yaml_content1: str, yaml_content2: str) -> dict[str, str]:
    """Merge two YAML files with deep merging of nested dictionaries.

    Values in yaml_content2 override those in yaml_content1.

    Args:
        yaml_content1: First YAML content (lower precedence)
        yaml_content2: Second YAML content (higher precedence)

    Returns:
        Dictionary with:
        - success: "true" or "false"
        - merged_yaml: Merged YAML content
        - key_count: Total number of top-level keys
        - error_message: Error description if merge failed

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty
    """
    if not isinstance(yaml_content1, str):
        raise TypeError("yaml_content1 must be a string")
    if not isinstance(yaml_content2, str):
        raise TypeError("yaml_content2 must be a string")
    if not yaml_content1.strip():
        raise ValueError("yaml_content1 cannot be empty")
    if not yaml_content2.strip():
        raise ValueError("yaml_content2 cannot be empty")

    if yaml is None:
        return {
            "success": "false",
            "merged_yaml": "",
            "key_count": "0",
            "error_message": "PyYAML not installed. Install with: pip install PyYAML",
        }

    try:
        data1 = yaml.safe_load(yaml_content1)
        data2 = yaml.safe_load(yaml_content2)

        if not isinstance(data1, dict) or not isinstance(data2, dict):
            return {
                "success": "false",
                "merged_yaml": "",
                "key_count": "0",
                "error_message": "Both YAML files must have dictionary/mapping at root",
            }

        # Deep merge
        def deep_merge(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
            result = dict1.copy()
            for key, value in dict2.items():
                if (
                    key in result
                    and isinstance(result[key], dict)
                    and isinstance(value, dict)
                ):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        merged = deep_merge(data1, data2)

        # Convert back to YAML
        merged_yaml = yaml.dump(merged, default_flow_style=False, sort_keys=False)

        return {
            "success": "true",
            "merged_yaml": merged_yaml,
            "key_count": str(len(merged)),
            "error_message": "",
        }

    except yaml.YAMLError as e:
        return {
            "success": "false",
            "merged_yaml": "",
            "key_count": "0",
            "error_message": f"YAML parse error: {str(e)}",
        }
    except Exception as e:
        return {
            "success": "false",
            "merged_yaml": "",
            "key_count": "0",
            "error_message": f"Merge error: {str(e)}",
        }


@strands_tool
def merge_toml_files(toml_content1: str, toml_content2: str) -> dict[str, str]:
    """Merge two TOML files with deep merging of nested tables.

    Values in toml_content2 override those in toml_content1.

    Args:
        toml_content1: First TOML content (lower precedence)
        toml_content2: Second TOML content (higher precedence)

    Returns:
        Dictionary with:
        - success: "true" or "false"
        - merged_toml: Merged TOML content as JSON (TOML writing requires extra lib)
        - key_count: Total number of top-level keys
        - error_message: Error description if merge failed

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty
    """
    if not isinstance(toml_content1, str):
        raise TypeError("toml_content1 must be a string")
    if not isinstance(toml_content2, str):
        raise TypeError("toml_content2 must be a string")
    if not toml_content1.strip():
        raise ValueError("toml_content1 cannot be empty")
    if not toml_content2.strip():
        raise ValueError("toml_content2 cannot be empty")

    if tomllib is None:
        return {
            "success": "false",
            "merged_toml": "",
            "key_count": "0",
            "error_message": "tomli not installed (Python <3.11). Install with: pip install tomli",
        }

    try:
        data1 = tomllib.loads(toml_content1)
        data2 = tomllib.loads(toml_content2)

        # Deep merge
        def deep_merge(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
            result = dict1.copy()
            for key, value in dict2.items():
                if (
                    key in result
                    and isinstance(result[key], dict)
                    and isinstance(value, dict)
                ):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        merged = deep_merge(data1, data2)

        # Return as JSON (writing TOML requires toml library which isn't in stdlib)
        merged_json = json.dumps(merged, indent=2)

        return {
            "success": "true",
            "merged_toml": merged_json,
            "key_count": str(len(merged)),
            "error_message": "",
        }

    except Exception as e:
        return {
            "success": "false",
            "merged_toml": "",
            "key_count": "0",
            "error_message": f"TOML parse/merge error: {str(e)}",
        }


@strands_tool
def interpolate_config_variables(config_content: str, variables: str) -> dict[str, str]:
    """Expand variable references like ${VAR} in configuration content.

    Useful for template configs with placeholders.

    Args:
        config_content: Configuration content with ${VAR} references
        variables: JSON string of variable key-value pairs

    Returns:
        Dictionary with:
        - success: "true" or "false"
        - result: Config content with variables expanded
        - substitution_count: Number of substitutions made
        - unresolved: JSON list of unresolved variable names
        - error_message: Error description if interpolation failed

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty or variables is invalid JSON
    """
    if not isinstance(config_content, str):
        raise TypeError("config_content must be a string")
    if not isinstance(variables, str):
        raise TypeError("variables must be a string")
    if not config_content.strip():
        raise ValueError("config_content cannot be empty")
    if not variables.strip():
        raise ValueError("variables cannot be empty")

    try:
        var_dict = json.loads(variables)
    except json.JSONDecodeError as e:
        return {
            "success": "false",
            "result": "",
            "substitution_count": "0",
            "unresolved": json.dumps([]),
            "error_message": f"Invalid JSON in variables: {str(e)}",
        }

    if not isinstance(var_dict, dict):
        return {
            "success": "false",
            "result": "",
            "substitution_count": "0",
            "unresolved": json.dumps([]),
            "error_message": "variables must be a JSON object/dictionary",
        }

    import re

    result = config_content
    substitutions = 0
    unresolved = []

    # Pattern matches ${VAR} and $VAR
    pattern = r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)"

    def replace_var(match: Any) -> str:
        nonlocal substitutions, unresolved

        var_name = match.group(1) or match.group(2)

        if var_name in var_dict:
            substitutions += 1
            return str(var_dict[var_name])
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
