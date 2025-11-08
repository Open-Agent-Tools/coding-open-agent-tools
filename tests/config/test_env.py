"""Tests for .env file parsing and manipulation functions."""

import json

import pytest

from coding_open_agent_tools.config import env


class TestParseEnvFile:
    """Tests for parse_env_file function."""

    def test_parse_simple_env(self) -> None:
        """Test parsing simple key-value pairs."""
        content = """
DATABASE_HOST=localhost
DATABASE_PORT=5432
API_KEY=secret123
"""
        result = env.parse_env_file(content)

        assert result["success"] == "true"
        assert result["variable_count"] == "3"

        variables = json.loads(result["variables"])
        assert variables["DATABASE_HOST"] == "localhost"
        assert variables["DATABASE_PORT"] == "5432"
        assert variables["API_KEY"] == "secret123"

    def test_parse_with_comments(self) -> None:
        """Test parsing with comments."""
        content = """
# Database configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432  # Default PostgreSQL port

# API settings
API_KEY=secret123
"""
        result = env.parse_env_file(content)

        assert result["success"] == "true"
        assert result["variable_count"] == "3"

    def test_parse_quoted_values(self) -> None:
        """Test parsing quoted values."""
        content = """
MESSAGE="Hello, World!"
PATH='/usr/local/bin:/usr/bin'
DESCRIPTION="Multi word value"
"""
        result = env.parse_env_file(content)

        assert result["success"] == "true"
        variables = json.loads(result["variables"])
        assert variables["MESSAGE"] == "Hello, World!"
        assert variables["PATH"] == "/usr/local/bin:/usr/bin"
        assert variables["DESCRIPTION"] == "Multi word value"

    def test_parse_empty_content_raises(self) -> None:
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError, match="env_content cannot be empty"):
            env.parse_env_file("")

    def test_parse_non_string_raises(self) -> None:
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="env_content must be a string"):
            env.parse_env_file(123)  # type: ignore

    def test_parse_blank_lines(self) -> None:
        """Test parsing with blank lines."""
        content = """
DATABASE_HOST=localhost

DATABASE_PORT=5432


API_KEY=secret123
"""
        result = env.parse_env_file(content)
        assert result["success"] == "true"
        assert result["variable_count"] == "3"


class TestValidateEnvFile:
    """Tests for validate_env_file function."""

    def test_validate_valid_env(self) -> None:
        """Test validation of valid .env file."""
        content = """
DATABASE_HOST=localhost
DATABASE_PORT=5432
API_KEY=secret123
"""
        result = env.validate_env_file(content)

        assert result["is_valid"] == "true"
        assert result["error_count"] == "0"

    def test_validate_missing_equals(self) -> None:
        """Test validation catches missing equals."""
        content = """
DATABASE_HOST localhost
"""
        result = env.validate_env_file(content)

        # Missing equals is an error
        assert result["is_valid"] == "false"
        errors = json.loads(result["errors"])
        assert any("Missing '='" in e for e in errors)

    def test_validate_invalid_variable_name(self) -> None:
        """Test validation catches invalid variable names."""
        content = """
123INVALID=value
"""
        result = env.validate_env_file(content)

        # Invalid variable names are errors
        assert result["is_valid"] == "false"
        errors = json.loads(result["errors"])
        assert any("Invalid variable name" in e for e in errors)

    def test_validate_lowercase_warning(self) -> None:
        """Test validation warns about lowercase variables."""
        content = """
database_host=localhost
"""
        result = env.validate_env_file(content)

        assert result["warning_count"] != "0"
        warnings = json.loads(result["warnings"])
        assert any("lowercase" in w for w in warnings)

    def test_validate_unquoted_spaces_warning(self) -> None:
        """Test validation warns about unquoted spaces."""
        content = """
MESSAGE=Hello World
"""
        result = env.validate_env_file(content)

        warnings = json.loads(result["warnings"])
        assert any("spaces" in w and "not quoted" in w for w in warnings)

    def test_validate_mismatched_quotes_error(self) -> None:
        """Test validation catches mismatched quotes."""
        content = """
MESSAGE="Hello World
"""
        result = env.validate_env_file(content)

        assert result["is_valid"] == "false"
        errors = json.loads(result["errors"])
        assert any("Mismatched" in e for e in errors)


class TestExtractEnvVariable:
    """Tests for extract_env_variable function."""

    def test_extract_existing_variable(self) -> None:
        """Test extracting an existing variable."""
        content = """
DATABASE_HOST=localhost
DATABASE_PORT=5432
"""
        result = env.extract_env_variable(content, "DATABASE_HOST")

        assert result["found"] == "true"
        assert result["value"] == "localhost"
        assert result["line_number"] == "2"

    def test_extract_quoted_variable(self) -> None:
        """Test extracting quoted variable value."""
        content = """
MESSAGE="Hello, World!"
"""
        result = env.extract_env_variable(content, "MESSAGE")

        assert result["found"] == "true"
        assert result["value"] == "Hello, World!"

    def test_extract_nonexistent_variable(self) -> None:
        """Test extracting non-existent variable."""
        content = """
DATABASE_HOST=localhost
"""
        result = env.extract_env_variable(content, "API_KEY")

        assert result["found"] == "false"
        assert "not found" in result["error_message"]

    def test_extract_empty_variable_name_raises(self) -> None:
        """Test that empty variable name raises ValueError."""
        with pytest.raises(ValueError, match="variable_name cannot be empty"):
            env.extract_env_variable("DB=localhost", "")


class TestMergeEnvFiles:
    """Tests for merge_env_files function."""

    def test_merge_non_overlapping(self) -> None:
        """Test merging non-overlapping .env files."""
        content1 = """
DATABASE_HOST=localhost
DATABASE_PORT=5432
"""
        content2 = """
API_KEY=secret123
API_URL=https://api.example.com
"""
        result = env.merge_env_files(content1, content2)

        assert result["success"] == "true"
        assert result["variable_count"] == "4"
        assert result["overridden_count"] == "0"

    def test_merge_with_overrides(self) -> None:
        """Test merging with variable overrides."""
        content1 = """
DATABASE_HOST=localhost
DATABASE_PORT=5432
API_KEY=dev_key
"""
        content2 = """
DATABASE_HOST=production.example.com
API_KEY=prod_key
"""
        result = env.merge_env_files(content1, content2)

        assert result["success"] == "true"
        assert result["variable_count"] == "3"
        assert result["overridden_count"] == "2"

        # Check that second file's values take precedence
        merged_content = result["merged_content"]
        assert "DATABASE_HOST=production.example.com" in merged_content
        assert "API_KEY=prod_key" in merged_content

    def test_merge_quotes_values_with_spaces(self) -> None:
        """Test that merge quotes values with spaces."""
        content1 = """
MESSAGE=Hello
"""
        content2 = """
DESCRIPTION=Multi word value
"""
        result = env.merge_env_files(content1, content2)

        assert result["success"] == "true"
        merged_content = result["merged_content"]
        assert 'DESCRIPTION="Multi word value"' in merged_content


class TestSubstituteEnvVariables:
    """Tests for substitute_env_variables function."""

    def test_substitute_simple_variables(self) -> None:
        """Test simple variable substitution."""
        template = "Database at ${HOST}:${PORT}"
        variables = json.dumps({"HOST": "localhost", "PORT": "5432"})

        result = env.substitute_env_variables(template, variables)

        assert result["success"] == "true"
        assert result["result"] == "Database at localhost:5432"
        assert result["substitution_count"] == "2"

    def test_substitute_dollar_var_syntax(self) -> None:
        """Test $VAR syntax substitution."""
        template = "Connect to $HOST"
        variables = json.dumps({"HOST": "localhost"})

        result = env.substitute_env_variables(template, variables)

        assert result["success"] == "true"
        assert result["result"] == "Connect to localhost"

    def test_substitute_unresolved_variables(self) -> None:
        """Test handling of unresolved variables."""
        template = "Database at ${HOST}:${PORT}"
        variables = json.dumps({"HOST": "localhost"})

        result = env.substitute_env_variables(template, variables)

        assert result["success"] == "true"
        assert result["result"] == "Database at localhost:${PORT}"
        assert result["substitution_count"] == "1"

        unresolved = json.loads(result["unresolved"])
        assert "PORT" in unresolved

    def test_substitute_invalid_json_error(self) -> None:
        """Test error on invalid JSON variables."""
        template = "Test ${VAR}"
        variables = "not valid json"

        result = env.substitute_env_variables(template, variables)

        assert result["success"] == "false"
        assert "Invalid JSON" in result["error_message"]

    def test_substitute_non_dict_json_error(self) -> None:
        """Test error on non-dict JSON."""
        template = "Test ${VAR}"
        variables = json.dumps(["not", "a", "dict"])

        result = env.substitute_env_variables(template, variables)

        assert result["success"] == "false"
        assert "must be a JSON object" in result["error_message"]
