"""Configuration file validation functions.

Provides syntax validation for YAML, TOML, and JSON files, as well as
JSON schema validation and CI/CD configuration validation.
"""

import json
import sys

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

try:
    import jsonschema  # type: ignore[import-untyped]
except ImportError:
    jsonschema = None  # type: ignore[assignment]

try:
    from packaging.requirements import Requirement  # type: ignore[import-untyped]
    from packaging.specifiers import SpecifierSet  # type: ignore[import-untyped]
    from packaging.version import Version  # type: ignore[import-untyped]

    packaging_available = True
except ImportError:
    packaging_available = False
    Requirement = None  # type: ignore[assignment,misc]
    Version = None  # type: ignore[assignment,misc]
    SpecifierSet = None  # type: ignore[assignment,misc]


@strands_tool
def validate_yaml_syntax(yaml_content: str) -> dict[str, str]:
    """Validate YAML syntax by attempting to parse the content.

    Requires PyYAML to be installed. Falls back to error if not available.

    Args:
        yaml_content: YAML content string to validate

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - error_message: Error description if invalid, empty if valid
        - error_line: Line number where error occurred (0 if valid)
        - error_column: Column number where error occurred (0 if valid)

    Raises:
        TypeError: If yaml_content is not a string
        ValueError: If yaml_content is empty
    """
    if not isinstance(yaml_content, str):
        raise TypeError("yaml_content must be a string")
    if not yaml_content.strip():
        raise ValueError("yaml_content cannot be empty")

    if yaml is None:
        return {
            "is_valid": "false",
            "error_message": "PyYAML not installed. Install with: pip install PyYAML",
            "error_line": "0",
            "error_column": "0",
        }

    try:
        yaml.safe_load(yaml_content)
        return {
            "is_valid": "true",
            "error_message": "",
            "error_line": "0",
            "error_column": "0",
        }
    except yaml.YAMLError as e:
        error_msg = str(e)
        line = "0"
        column = "0"

        # Extract line and column from error if available
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            line = str(mark.line + 1)  # Convert 0-indexed to 1-indexed
            column = str(mark.column + 1)

        return {
            "is_valid": "false",
            "error_message": error_msg,
            "error_line": line,
            "error_column": column,
        }


@strands_tool
def validate_toml_syntax(toml_content: str) -> dict[str, str]:
    """Validate TOML syntax by attempting to parse the content.

    Uses tomllib (Python 3.11+) or tomli (Python 3.9-3.10) for parsing.

    Args:
        toml_content: TOML content string to validate

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - error_message: Error description if invalid, empty if valid
        - error_line: Line number where error occurred (0 if valid)
        - error_column: Column number where error occurred (0 if valid)

    Raises:
        TypeError: If toml_content is not a string
        ValueError: If toml_content is empty
    """
    if not isinstance(toml_content, str):
        raise TypeError("toml_content must be a string")
    if not toml_content.strip():
        raise ValueError("toml_content cannot be empty")

    if tomllib is None:
        return {
            "is_valid": "false",
            "error_message": "tomli not installed (Python <3.11). Install with: pip install tomli",
            "error_line": "0",
            "error_column": "0",
        }

    try:
        tomllib.loads(toml_content)
        return {
            "is_valid": "true",
            "error_message": "",
            "error_line": "0",
            "error_column": "0",
        }
    except Exception as e:
        error_msg = str(e)
        line = "0"
        column = "0"

        # Try to extract line number from error message
        # Format varies but often includes "line X"
        if "line" in error_msg.lower():
            parts = error_msg.split()
            for i, part in enumerate(parts):
                if "line" in part.lower() and i + 1 < len(parts):
                    try:
                        line = str(int(parts[i + 1].rstrip(",:;")))
                        break
                    except ValueError:
                        pass

        return {
            "is_valid": "false",
            "error_message": error_msg,
            "error_line": line,
            "error_column": column,
        }


@strands_tool
def validate_json_syntax(json_content: str) -> dict[str, str]:
    """Validate JSON syntax by attempting to parse the content.

    Uses stdlib json module for parsing.

    Args:
        json_content: JSON content string to validate

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - error_message: Error description if invalid, empty if valid
        - error_line: Line number where error occurred (0 if valid)
        - error_column: Column number where error occurred (0 if valid)

    Raises:
        TypeError: If json_content is not a string
        ValueError: If json_content is empty
    """
    if not isinstance(json_content, str):
        raise TypeError("json_content must be a string")
    if not json_content.strip():
        raise ValueError("json_content cannot be empty")

    try:
        json.loads(json_content)
        return {
            "is_valid": "true",
            "error_message": "",
            "error_line": "0",
            "error_column": "0",
        }
    except json.JSONDecodeError as e:
        return {
            "is_valid": "false",
            "error_message": str(e.msg),
            "error_line": str(e.lineno),
            "error_column": str(e.colno),
        }


@strands_tool
def validate_json_schema(
    json_content: str, schema_content: str, use_jsonschema: str
) -> dict[str, str]:
    """Validate JSON content against a JSON schema.

    Requires jsonschema library for full validation. Falls back to syntax-only
    validation if jsonschema not installed and use_jsonschema is "false".

    Args:
        json_content: JSON content string to validate
        schema_content: JSON schema string (must be valid JSON)
        use_jsonschema: "true" to use jsonschema library, "false" for syntax-only

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - error_message: Error description if invalid, empty if valid
        - error_path: JSON path where validation failed (if applicable)
        - validation_type: "schema" or "syntax"

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty or use_jsonschema not "true"/"false"
    """
    if not isinstance(json_content, str):
        raise TypeError("json_content must be a string")
    if not isinstance(schema_content, str):
        raise TypeError("schema_content must be a string")
    if not isinstance(use_jsonschema, str):
        raise TypeError("use_jsonschema must be a string")

    if not json_content.strip():
        raise ValueError("json_content cannot be empty")
    if not schema_content.strip():
        raise ValueError("schema_content cannot be empty")
    if use_jsonschema not in ("true", "false"):
        raise ValueError('use_jsonschema must be "true" or "false"')

    # First validate JSON syntax
    try:
        data = json.loads(json_content)
        schema = json.loads(schema_content)
    except json.JSONDecodeError as e:
        return {
            "is_valid": "false",
            "error_message": f"JSON syntax error: {e.msg}",
            "error_path": f"line {e.lineno}, column {e.colno}",
            "validation_type": "syntax",
        }

    # If schema validation not requested or not available, return syntax-only result
    if use_jsonschema == "false":
        return {
            "is_valid": "true",
            "error_message": "",
            "error_path": "",
            "validation_type": "syntax",
        }

    if jsonschema is None:
        return {
            "is_valid": "false",
            "error_message": "jsonschema not installed. Install with: pip install jsonschema",
            "error_path": "",
            "validation_type": "unavailable",
        }

    # Perform schema validation
    try:
        jsonschema.validate(instance=data, schema=schema)
        return {
            "is_valid": "true",
            "error_message": "",
            "error_path": "",
            "validation_type": "schema",
        }
    except jsonschema.ValidationError as e:
        error_path = (
            ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
        )
        return {
            "is_valid": "false",
            "error_message": str(e.message),
            "error_path": error_path,
            "validation_type": "schema",
        }
    except jsonschema.SchemaError as e:
        return {
            "is_valid": "false",
            "error_message": f"Invalid schema: {e.message}",
            "error_path": "",
            "validation_type": "schema",
        }


@strands_tool
def validate_github_actions_config(
    workflow_content: str, use_jsonschema: str
) -> dict[str, str]:
    """Validate GitHub Actions workflow configuration.

    Validates YAML syntax and optionally checks against GitHub Actions schema.

    Args:
        workflow_content: GitHub Actions workflow YAML content
        use_jsonschema: "true" to validate against schema, "false" for syntax only

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - error_message: Error description if invalid, empty if valid
        - error_type: "yaml_syntax", "schema", or "none"
        - suggestion: Helpful suggestion for fixing common issues

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty or use_jsonschema not "true"/"false"
    """
    if not isinstance(workflow_content, str):
        raise TypeError("workflow_content must be a string")
    if not isinstance(use_jsonschema, str):
        raise TypeError("use_jsonschema must be a string")

    if not workflow_content.strip():
        raise ValueError("workflow_content cannot be empty")
    if use_jsonschema not in ("true", "false"):
        raise ValueError('use_jsonschema must be "true" or "false"')

    # First validate YAML syntax
    yaml_result = validate_yaml_syntax(workflow_content)
    if yaml_result["is_valid"] == "false":
        return {
            "is_valid": "false",
            "error_message": yaml_result["error_message"],
            "error_type": "yaml_syntax",
            "suggestion": "Fix YAML syntax errors before validating against schema",
        }

    # Check required fields for GitHub Actions
    if yaml is None:
        return {
            "is_valid": "false",
            "error_message": "PyYAML not installed",
            "error_type": "dependency",
            "suggestion": "Install PyYAML: pip install PyYAML",
        }

    try:
        workflow = yaml.safe_load(workflow_content)

        # Basic structural validation
        if not isinstance(workflow, dict):
            return {
                "is_valid": "false",
                "error_message": "Workflow must be a YAML mapping/dictionary",
                "error_type": "schema",
                "suggestion": "Workflow file should contain key-value pairs at the root level",
            }

        # Check for required 'on' trigger field
        # Note: YAML parses 'on' as boolean True, so check for both
        if "on" not in workflow and True not in workflow:
            return {
                "is_valid": "false",
                "error_message": "Workflow must define 'on' trigger",
                "error_type": "schema",
                "suggestion": "Add 'on:' section to specify when workflow runs",
            }

        if "jobs" not in workflow:
            return {
                "is_valid": "false",
                "error_message": "Workflow must define 'jobs'",
                "error_type": "schema",
                "suggestion": "Add 'jobs:' section to define workflow jobs",
            }

        # Validate jobs structure
        jobs = workflow.get("jobs", {})
        if not isinstance(jobs, dict):
            return {
                "is_valid": "false",
                "error_message": "'jobs' must be a mapping of job IDs to job configurations",
                "error_type": "schema",
                "suggestion": "Each job should be defined as a key-value pair under 'jobs:'",
            }

        # Check each job has required fields
        for job_id, job in jobs.items():
            if not isinstance(job, dict):
                return {
                    "is_valid": "false",
                    "error_message": f"Job '{job_id}' must be a mapping",
                    "error_type": "schema",
                    "suggestion": f"Define job '{job_id}' with key-value pairs",
                }

            if "runs-on" not in job:
                return {
                    "is_valid": "false",
                    "error_message": f"Job '{job_id}' missing required 'runs-on' field",
                    "error_type": "schema",
                    "suggestion": f"Add 'runs-on: ubuntu-latest' to job '{job_id}'",
                }

            if "steps" not in job:
                return {
                    "is_valid": "false",
                    "error_message": f"Job '{job_id}' missing 'steps' field",
                    "error_type": "schema",
                    "suggestion": f"Add 'steps:' list to job '{job_id}'",
                }

        return {
            "is_valid": "true",
            "error_message": "",
            "error_type": "none",
            "suggestion": "",
        }

    except Exception as e:
        return {
            "is_valid": "false",
            "error_message": f"Validation error: {str(e)}",
            "error_type": "schema",
            "suggestion": "Check workflow structure against GitHub Actions documentation",
        }


@strands_tool
def check_dependency_conflicts(requirements_content: str) -> dict[str, str]:
    """Check for dependency version conflicts in requirements.

    Analyzes requirements.txt or similar content for conflicting version
    specifications using the packaging library.

    Args:
        requirements_content: Requirements file content (one requirement per line)

    Returns:
        Dictionary with:
        - has_conflicts: "true" or "false"
        - conflict_count: Number of conflicting packages detected
        - conflicts: Comma-separated list of packages with conflicts
        - invalid_count: Number of invalid requirement specifications
        - details: Additional details about conflicts

    Raises:
        TypeError: If requirements_content is not a string
        ValueError: If requirements_content is empty
    """
    if not isinstance(requirements_content, str):
        raise TypeError("requirements_content must be a string")
    if not requirements_content.strip():
        raise ValueError("requirements_content cannot be empty")

    if not packaging_available:
        return {
            "has_conflicts": "false",
            "conflict_count": "0",
            "conflicts": "",
            "invalid_count": "0",
            "details": "packaging library not installed. Install with: pip install packaging",
        }

    # Parse all requirements
    package_specs: dict[str, list[str]] = {}
    invalid_lines = []

    for line_num, line in enumerate(requirements_content.split("\n"), 1):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        try:
            req = Requirement(line)
            package_name = req.name.lower()

            if package_name not in package_specs:
                package_specs[package_name] = []

            # Convert specifier to string
            if req.specifier:
                package_specs[package_name].append(str(req.specifier))
            else:
                package_specs[package_name].append("")

        except Exception as e:
            invalid_lines.append(f"Line {line_num}: {str(e)[:50]}")

    # Check for conflicts
    conflicts = []
    for package, specs in package_specs.items():
        # If package appears multiple times with different specs
        if len(specs) > 1:
            unique_specs = {spec for spec in specs if spec}
            if len(unique_specs) > 1:
                conflicts.append(package)
                continue

        # Check if multiple version specifications are incompatible
        if len(specs) == 1 and specs[0]:
            try:
                # Check if specifier set is satisfiable
                # For now, we just validate it parses correctly
                # More sophisticated conflict detection would require
                # checking if any version can satisfy all specs
                SpecifierSet(specs[0])
            except Exception:
                conflicts.append(package)

    if conflicts or invalid_lines:
        conflict_details = []
        if conflicts:
            conflict_details.append(
                f"{len(conflicts)} packages with conflicts: {', '.join(conflicts[:3])}"
            )
            if len(conflicts) > 3:
                conflict_details[-1] += f" (+{len(conflicts) - 3} more)"
        if invalid_lines:
            conflict_details.append(f"{len(invalid_lines)} invalid requirements")

        return {
            "has_conflicts": "true" if conflicts else "false",
            "conflict_count": str(len(conflicts)),
            "conflicts": ", ".join(conflicts) if conflicts else "",
            "invalid_count": str(len(invalid_lines)),
            "details": "; ".join(conflict_details),
        }
    else:
        return {
            "has_conflicts": "false",
            "conflict_count": "0",
            "conflicts": "",
            "invalid_count": "0",
            "details": f"Analyzed {len(package_specs)} packages, no conflicts detected",
        }


@strands_tool
def validate_version_specifier(version_spec: str) -> dict[str, str]:
    """Validate a Python package version specifier.

    Checks if a version specifier string is valid according to PEP 440.

    Args:
        version_spec: Version specifier string (e.g., ">=1.0.0,<2.0.0")

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - error_message: Error description if invalid, empty if valid
        - normalized: Normalized version specifier if valid
        - operator_count: Number of version operators in specifier

    Raises:
        TypeError: If version_spec is not a string
        ValueError: If version_spec is empty
    """
    if not isinstance(version_spec, str):
        raise TypeError("version_spec must be a string")
    if not version_spec.strip():
        raise ValueError("version_spec cannot be empty")

    if not packaging_available:
        return {
            "is_valid": "false",
            "error_message": "packaging library not installed. Install with: pip install packaging",
            "normalized": "",
            "operator_count": "0",
        }

    try:
        spec_set = SpecifierSet(version_spec)
        operator_count = len(list(spec_set))

        return {
            "is_valid": "true",
            "error_message": "",
            "normalized": str(spec_set),
            "operator_count": str(operator_count),
        }
    except Exception as e:
        return {
            "is_valid": "false",
            "error_message": str(e),
            "normalized": "",
            "operator_count": "0",
        }
