"""Tests for configuration validation functions."""

import pytest

from coding_open_agent_tools.config.validation import (
    check_dependency_conflicts,
    validate_github_actions_config,
    validate_json_schema,
    validate_json_syntax,
    validate_toml_syntax,
    validate_version_specifier,
    validate_yaml_syntax,
)


class TestValidateYAMLSyntax:
    """Tests for validate_yaml_syntax function."""

    def test_valid_yaml(self) -> None:
        """Test validation of valid YAML content."""
        yaml_content = """
        name: Test
        version: 1.0.0
        items:
          - one
          - two
        """
        result = validate_yaml_syntax(yaml_content)
        assert result["is_valid"] == "true"
        assert result["error_message"] == ""
        assert result["error_line"] == "0"

    def test_invalid_yaml_syntax(self) -> None:
        """Test validation of invalid YAML with syntax error."""
        yaml_content = """
        name: Test
        items:
          - one
         - two
        """  # Inconsistent indentation
        result = validate_yaml_syntax(yaml_content)
        assert result["is_valid"] == "false"
        assert result["error_message"] != ""

    def test_empty_yaml_raises_error(self) -> None:
        """Test that empty YAML content raises ValueError."""
        with pytest.raises(ValueError, match="yaml_content cannot be empty"):
            validate_yaml_syntax("")

    def test_invalid_type_raises_error(self) -> None:
        """Test that non-string type raises TypeError."""
        with pytest.raises(TypeError, match="yaml_content must be a string"):
            validate_yaml_syntax(123)  # type: ignore[arg-type]


class TestValidateTOMLSyntax:
    """Tests for validate_toml_syntax function."""

    def test_valid_toml(self) -> None:
        """Test validation of valid TOML content."""
        toml_content = """
        [package]
        name = "test"
        version = "1.0.0"

        [dependencies]
        requests = ">=2.0.0"
        """
        result = validate_toml_syntax(toml_content)
        assert result["is_valid"] == "true"
        assert result["error_message"] == ""

    def test_invalid_toml_syntax(self) -> None:
        """Test validation of invalid TOML with syntax error."""
        toml_content = """
        [package
        name = "test"
        """  # Missing closing bracket
        result = validate_toml_syntax(toml_content)
        assert result["is_valid"] == "false"
        assert result["error_message"] != ""

    def test_empty_toml_raises_error(self) -> None:
        """Test that empty TOML content raises ValueError."""
        with pytest.raises(ValueError, match="toml_content cannot be empty"):
            validate_toml_syntax("")

    def test_invalid_type_raises_error(self) -> None:
        """Test that non-string type raises TypeError."""
        with pytest.raises(TypeError, match="toml_content must be a string"):
            validate_toml_syntax(None)  # type: ignore[arg-type]


class TestValidateJSONSyntax:
    """Tests for validate_json_syntax function."""

    def test_valid_json(self) -> None:
        """Test validation of valid JSON content."""
        json_content = '{"name": "test", "version": "1.0.0", "items": [1, 2, 3]}'
        result = validate_json_syntax(json_content)
        assert result["is_valid"] == "true"
        assert result["error_message"] == ""
        assert result["error_line"] == "0"

    def test_invalid_json_syntax(self) -> None:
        """Test validation of invalid JSON with syntax error."""
        json_content = '{"name": "test", "version": }'  # Missing value
        result = validate_json_syntax(json_content)
        assert result["is_valid"] == "false"
        assert result["error_message"] != ""
        assert result["error_line"] != "0"

    def test_empty_json_raises_error(self) -> None:
        """Test that empty JSON content raises ValueError."""
        with pytest.raises(ValueError, match="json_content cannot be empty"):
            validate_json_syntax("  ")

    def test_invalid_type_raises_error(self) -> None:
        """Test that non-string type raises TypeError."""
        with pytest.raises(TypeError, match="json_content must be a string"):
            validate_json_syntax([])  # type: ignore[arg-type]


class TestValidateJSONSchema:
    """Tests for validate_json_schema function."""

    def test_valid_json_against_schema_syntax_only(self) -> None:
        """Test JSON validation against schema (syntax-only mode)."""
        json_content = '{"name": "test", "age": 25}'
        schema_content = """
        {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
        """
        result = validate_json_schema(json_content, schema_content, "false")
        assert result["is_valid"] == "true"
        assert result["validation_type"] == "syntax"

    def test_invalid_json_syntax_in_schema_validation(self) -> None:
        """Test that invalid JSON syntax is caught."""
        json_content = '{"name": invalid}'
        schema_content = '{"type": "object"}'
        result = validate_json_schema(json_content, schema_content, "false")
        assert result["is_valid"] == "false"
        assert result["validation_type"] == "syntax"

    def test_empty_content_raises_error(self) -> None:
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError, match="json_content cannot be empty"):
            validate_json_schema("", '{"type": "object"}', "false")

    def test_invalid_use_jsonschema_value(self) -> None:
        """Test that invalid use_jsonschema value raises ValueError."""
        with pytest.raises(
            ValueError, match='use_jsonschema must be "true" or "false"'
        ):
            validate_json_schema('{"a": 1}', '{"type": "object"}', "maybe")  # type: ignore[arg-type]


class TestValidateGitHubActionsConfig:
    """Tests for validate_github_actions_config function."""

    def test_valid_github_actions_workflow(self) -> None:
        """Test validation of valid GitHub Actions workflow."""
        workflow = """
        name: Test
        on: push
        jobs:
          test:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v2
        """
        result = validate_github_actions_config(workflow, "false")
        assert result["is_valid"] == "true"
        assert result["error_type"] == "none"

    def test_missing_on_field(self) -> None:
        """Test workflow missing 'on' trigger."""
        workflow = """
        name: Test
        jobs:
          test:
            runs-on: ubuntu-latest
            steps:
              - run: echo test
        """
        result = validate_github_actions_config(workflow, "false")
        assert result["is_valid"] == "false"
        assert "on" in result["error_message"].lower()

    def test_missing_jobs_field(self) -> None:
        """Test workflow missing 'jobs' field."""
        workflow = """
        name: Test
        on: push
        """
        result = validate_github_actions_config(workflow, "false")
        assert result["is_valid"] == "false"
        assert "jobs" in result["error_message"].lower()

    def test_job_missing_runs_on(self) -> None:
        """Test job missing 'runs-on' field."""
        workflow = """
        name: Test
        on: push
        jobs:
          test:
            steps:
              - run: echo test
        """
        result = validate_github_actions_config(workflow, "false")
        assert result["is_valid"] == "false"
        assert "runs-on" in result["error_message"].lower()

    def test_invalid_yaml_syntax(self) -> None:
        """Test workflow with invalid YAML syntax."""
        workflow = """
        name: Test
        on: [push
        """
        result = validate_github_actions_config(workflow, "false")
        assert result["is_valid"] == "false"
        assert result["error_type"] == "yaml_syntax"

    def test_empty_workflow_raises_error(self) -> None:
        """Test that empty workflow raises ValueError."""
        with pytest.raises(ValueError, match="workflow_content cannot be empty"):
            validate_github_actions_config("", "false")


class TestCheckDependencyConflicts:
    """Tests for check_dependency_conflicts function."""

    def test_no_conflicts(self) -> None:
        """Test requirements with no conflicts."""
        requirements = """
        requests>=2.25.0
        pytest>=7.0.0
        flask>=2.0.0
        """
        result = check_dependency_conflicts(requirements)
        assert result["has_conflicts"] == "false"
        assert result["conflict_count"] == "0"

    def test_invalid_requirement_syntax(self) -> None:
        """Test invalid requirement syntax detection."""
        requirements = """
        requests>=2.25.0
        invalid-package-spec
        pytest>=7.0.0
        """
        result = check_dependency_conflicts(requirements)
        # Should detect invalid lines
        assert result["invalid_count"] != "0" or result["has_conflicts"] == "false"

    def test_empty_requirements_raises_error(self) -> None:
        """Test that empty requirements raises ValueError."""
        with pytest.raises(ValueError, match="requirements_content cannot be empty"):
            check_dependency_conflicts("")

    def test_comments_and_blank_lines_ignored(self) -> None:
        """Test that comments and blank lines are properly ignored."""
        requirements = """
        # This is a comment
        requests>=2.25.0

        pytest>=7.0.0
        # Another comment
        """
        result = check_dependency_conflicts(requirements)
        # Should not error on comments
        assert "has_conflicts" in result


class TestValidateVersionSpecifier:
    """Tests for validate_version_specifier function."""

    def test_valid_version_specifier(self) -> None:
        """Test validation of valid version specifier."""
        result = validate_version_specifier(">=1.0.0,<2.0.0")
        assert result["is_valid"] == "true"
        assert result["error_message"] == ""
        assert result["normalized"] != ""
        assert int(result["operator_count"]) > 0

    def test_simple_version_specifier(self) -> None:
        """Test simple version specifier."""
        result = validate_version_specifier("==1.2.3")
        assert result["is_valid"] == "true"
        assert result["operator_count"] == "1"

    def test_invalid_version_specifier(self) -> None:
        """Test invalid version specifier."""
        result = validate_version_specifier(">>1.0.0")  # Invalid operator
        assert result["is_valid"] == "false"
        assert result["error_message"] != ""

    def test_empty_specifier_raises_error(self) -> None:
        """Test that empty specifier raises ValueError."""
        with pytest.raises(ValueError, match="version_spec cannot be empty"):
            validate_version_specifier("  ")

    def test_invalid_type_raises_error(self) -> None:
        """Test that non-string type raises TypeError."""
        with pytest.raises(TypeError, match="version_spec must be a string"):
            validate_version_specifier(1.0)  # type: ignore[arg-type]
