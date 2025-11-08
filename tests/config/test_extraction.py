"""Tests for configuration extraction and manipulation functions."""

import json

import pytest

from coding_open_agent_tools.config import extraction


class TestExtractYamlValue:
    """Tests for extract_yaml_value function."""

    def test_extract_simple_value(self) -> None:
        """Test extracting simple string value."""
        yaml_content = """
database:
  host: localhost
  port: 5432
"""
        result = extraction.extract_yaml_value(yaml_content, "database.host")

        assert result["found"] == "true"
        assert json.loads(result["value"]) == "localhost"
        assert result["value_type"] == "string"

    def test_extract_number_value(self) -> None:
        """Test extracting number value."""
        yaml_content = """
database:
  port: 5432
"""
        result = extraction.extract_yaml_value(yaml_content, "database.port")

        assert result["found"] == "true"
        assert json.loads(result["value"]) == 5432
        assert result["value_type"] == "number"

    def test_extract_boolean_value(self) -> None:
        """Test extracting boolean value."""
        yaml_content = """
features:
  debug: true
"""
        result = extraction.extract_yaml_value(yaml_content, "features.debug")

        assert result["found"] == "true"
        assert json.loads(result["value"]) is True
        assert result["value_type"] == "boolean"

    def test_extract_array_value(self) -> None:
        """Test extracting array value."""
        yaml_content = """
servers:
  - web1
  - web2
  - web3
"""
        result = extraction.extract_yaml_value(yaml_content, "servers")

        assert result["found"] == "true"
        assert json.loads(result["value"]) == ["web1", "web2", "web3"]
        assert result["value_type"] == "array"

    def test_extract_object_value(self) -> None:
        """Test extracting object/dict value."""
        yaml_content = """
database:
  host: localhost
  port: 5432
"""
        result = extraction.extract_yaml_value(yaml_content, "database")

        assert result["found"] == "true"
        value = json.loads(result["value"])
        assert value["host"] == "localhost"
        assert value["port"] == 5432
        assert result["value_type"] == "object"

    def test_extract_nonexistent_path(self) -> None:
        """Test extracting non-existent path."""
        yaml_content = """
database:
  host: localhost
"""
        result = extraction.extract_yaml_value(yaml_content, "database.port")

        assert result["found"] == "false"
        assert "not found" in result["error_message"]

    def test_extract_empty_content_raises(self) -> None:
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError, match="yaml_content cannot be empty"):
            extraction.extract_yaml_value("", "path")


class TestExtractTomlValue:
    """Tests for extract_toml_value function."""

    def test_extract_simple_value(self) -> None:
        """Test extracting simple value from TOML."""
        toml_content = """
[database]
host = "localhost"
port = 5432
"""
        result = extraction.extract_toml_value(toml_content, "database.host")

        assert result["found"] == "true"
        assert json.loads(result["value"]) == "localhost"
        assert result["value_type"] == "string"

    def test_extract_number(self) -> None:
        """Test extracting number from TOML."""
        toml_content = """
[server]
port = 8080
"""
        result = extraction.extract_toml_value(toml_content, "server.port")

        assert result["found"] == "true"
        assert json.loads(result["value"]) == 8080
        assert result["value_type"] == "number"

    def test_extract_array(self) -> None:
        """Test extracting array from TOML."""
        toml_content = """
servers = ["web1", "web2", "web3"]
"""
        result = extraction.extract_toml_value(toml_content, "servers")

        assert result["found"] == "true"
        assert json.loads(result["value"]) == ["web1", "web2", "web3"]
        assert result["value_type"] == "array"


class TestExtractJsonValue:
    """Tests for extract_json_value function."""

    def test_extract_simple_value(self) -> None:
        """Test extracting simple value from JSON."""
        json_content = """
{
  "database": {
    "host": "localhost",
    "port": 5432
  }
}
"""
        result = extraction.extract_json_value(json_content, "database.host")

        assert result["found"] == "true"
        assert json.loads(result["value"]) == "localhost"
        assert result["value_type"] == "string"

    def test_extract_null_value(self) -> None:
        """Test extracting null value."""
        json_content = """
{
  "optional": null
}
"""
        result = extraction.extract_json_value(json_content, "optional")

        assert result["found"] == "true"
        assert json.loads(result["value"]) is None
        assert result["value_type"] == "null"

    def test_extract_nested_object(self) -> None:
        """Test extracting nested object."""
        json_content = """
{
  "server": {
    "database": {
      "host": "localhost"
    }
  }
}
"""
        result = extraction.extract_json_value(json_content, "server.database.host")

        assert result["found"] == "true"
        assert json.loads(result["value"]) == "localhost"

    def test_extract_invalid_json_error(self) -> None:
        """Test error on invalid JSON."""
        json_content = "{ invalid json }"

        result = extraction.extract_json_value(json_content, "path")

        assert result["found"] == "false"
        assert "JSON parse error" in result["error_message"]


class TestMergeYamlFiles:
    """Tests for merge_yaml_files function."""

    def test_merge_non_overlapping(self) -> None:
        """Test merging non-overlapping YAML."""
        yaml1 = """
database:
  host: localhost
"""
        yaml2 = """
api:
  key: secret
"""
        result = extraction.merge_yaml_files(yaml1, yaml2)

        assert result["success"] == "true"
        assert result["key_count"] == "2"

        merged = result["merged_yaml"]
        assert "database:" in merged
        assert "host: localhost" in merged
        assert "api:" in merged
        assert "key: secret" in merged

    def test_merge_with_deep_override(self) -> None:
        """Test deep merging with override."""
        yaml1 = """
database:
  host: localhost
  port: 5432
  credentials:
    user: dev
"""
        yaml2 = """
database:
  host: production.example.com
  credentials:
    user: prod
    password: secret
"""
        result = extraction.merge_yaml_files(yaml1, yaml2)

        assert result["success"] == "true"

        # Parse merged YAML to verify deep merge
        import yaml

        merged_data = yaml.safe_load(result["merged_yaml"])
        assert merged_data["database"]["host"] == "production.example.com"
        assert merged_data["database"]["port"] == 5432  # Preserved from yaml1
        assert merged_data["database"]["credentials"]["user"] == "prod"
        assert merged_data["database"]["credentials"]["password"] == "secret"

    def test_merge_invalid_yaml_error(self) -> None:
        """Test error on invalid YAML."""
        yaml1 = "valid: yaml"
        yaml2 = "invalid: yaml: structure:"

        result = extraction.merge_yaml_files(yaml1, yaml2)

        assert result["success"] == "false"
        assert "YAML parse error" in result["error_message"]


class TestMergeTomlFiles:
    """Tests for merge_toml_files function."""

    def test_merge_non_overlapping(self) -> None:
        """Test merging non-overlapping TOML."""
        toml1 = """
[database]
host = "localhost"
"""
        toml2 = """
[api]
key = "secret"
"""
        result = extraction.merge_toml_files(toml1, toml2)

        assert result["success"] == "true"
        assert result["key_count"] == "2"

        # Result is JSON, not TOML
        merged_data = json.loads(result["merged_toml"])
        assert merged_data["database"]["host"] == "localhost"
        assert merged_data["api"]["key"] == "secret"

    def test_merge_with_override(self) -> None:
        """Test merging with value override."""
        toml1 = """
[database]
host = "localhost"
port = 5432
"""
        toml2 = """
[database]
host = "production.example.com"
"""
        result = extraction.merge_toml_files(toml1, toml2)

        assert result["success"] == "true"

        merged_data = json.loads(result["merged_toml"])
        assert merged_data["database"]["host"] == "production.example.com"
        assert merged_data["database"]["port"] == 5432  # Preserved


class TestInterpolateConfigVariables:
    """Tests for interpolate_config_variables function."""

    def test_interpolate_simple_variables(self) -> None:
        """Test simple variable interpolation."""
        config = "database_url: postgresql://${DB_HOST}:${DB_PORT}/mydb"
        variables = json.dumps({"DB_HOST": "localhost", "DB_PORT": "5432"})

        result = extraction.interpolate_config_variables(config, variables)

        assert result["success"] == "true"
        assert result["result"] == "database_url: postgresql://localhost:5432/mydb"
        assert result["substitution_count"] == "2"

    def test_interpolate_dollar_var_syntax(self) -> None:
        """Test $VAR syntax interpolation."""
        config = "server: $HOST:$PORT"
        variables = json.dumps({"HOST": "localhost", "PORT": "8080"})

        result = extraction.interpolate_config_variables(config, variables)

        assert result["success"] == "true"
        assert result["result"] == "server: localhost:8080"

    def test_interpolate_unresolved_variables(self) -> None:
        """Test handling of unresolved variables."""
        config = "url: ${PROTO}://${HOST}:${PORT}"
        variables = json.dumps({"HOST": "localhost"})

        result = extraction.interpolate_config_variables(config, variables)

        assert result["success"] == "true"
        assert "${PROTO}" in result["result"]
        assert "${PORT}" in result["result"]
        assert "localhost" in result["result"]

        unresolved = json.loads(result["unresolved"])
        assert "PROTO" in unresolved
        assert "PORT" in unresolved

    def test_interpolate_invalid_json_error(self) -> None:
        """Test error on invalid JSON variables."""
        config = "test ${VAR}"
        variables = "not json"

        result = extraction.interpolate_config_variables(config, variables)

        assert result["success"] == "false"
        assert "Invalid JSON" in result["error_message"]
