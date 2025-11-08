"""Tests for common configuration format parsing functions."""

import json

import pytest

from coding_open_agent_tools.config import formats


class TestParseIniFile:
    """Tests for parse_ini_file function."""

    def test_parse_simple_ini(self) -> None:
        """Test parsing simple INI file."""
        ini_content = """
[database]
host = localhost
port = 5432

[api]
key = secret123
url = https://api.example.com
"""
        result = formats.parse_ini_file(ini_content)

        assert result["success"] == "true"
        assert result["section_count"] == "2"

        data = json.loads(result["data"])
        assert data["database"]["host"] == "localhost"
        assert data["database"]["port"] == "5432"
        assert data["api"]["key"] == "secret123"

    def test_parse_with_comments(self) -> None:
        """Test parsing INI with comments."""
        ini_content = """
# Database configuration
[database]
host = localhost  ; comment here
port = 5432
"""
        result = formats.parse_ini_file(ini_content)

        assert result["success"] == "true"
        data = json.loads(result["data"])
        assert "database" in data

    def test_parse_multiline_values(self) -> None:
        """Test parsing multiline values."""
        ini_content = """
[section]
value = line1
    line2
    line3
"""
        result = formats.parse_ini_file(ini_content)

        assert result["success"] == "true"

    def test_parse_invalid_ini_error(self) -> None:
        """Test error on invalid INI syntax."""
        ini_content = """
[unclosed section
key = value
"""
        result = formats.parse_ini_file(ini_content)

        assert result["success"] == "false"
        assert "INI parse error" in result["error_message"]

    def test_parse_empty_content_raises(self) -> None:
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError, match="ini_content cannot be empty"):
            formats.parse_ini_file("")


class TestValidateIniSyntax:
    """Tests for validate_ini_syntax function."""

    def test_validate_valid_ini(self) -> None:
        """Test validation of valid INI file."""
        ini_content = """
[database]
host = localhost
port = 5432
"""
        result = formats.validate_ini_syntax(ini_content)

        assert result["is_valid"] == "true"
        assert result["error_count"] == "0"

    def test_validate_duplicate_section_handling(self) -> None:
        """Test handling of duplicate sections."""
        ini_content = """
[database]
host = localhost

[database]
port = 5432
"""
        result = formats.validate_ini_syntax(ini_content)

        # Duplicate sections are caught by configparser as an error
        assert result["is_valid"] == "false"
        errors = json.loads(result["errors"])
        assert any("Duplicate section" in e for e in errors)

    def test_validate_assignment_outside_section_handling(self) -> None:
        """Test handling of assignments outside sections."""
        ini_content = """
key = value

[section]
other = data
"""
        result = formats.validate_ini_syntax(ini_content)

        # Some INI parsers allow global section (assignments before first section)
        # This may produce errors depending on implementation
        # Just check that validation runs without crashing
        assert "is_valid" in result


class TestParsePropertiesFile:
    """Tests for parse_properties_file function."""

    def test_parse_simple_properties(self) -> None:
        """Test parsing simple properties file."""
        properties_content = """
database.host=localhost
database.port=5432
api.key=secret123
"""
        result = formats.parse_properties_file(properties_content)

        assert result["success"] == "true"
        assert result["property_count"] == "3"

        properties = json.loads(result["properties"])
        assert properties["database.host"] == "localhost"
        assert properties["database.port"] == "5432"

    def test_parse_with_comments(self) -> None:
        """Test parsing with comments."""
        properties_content = """
# Database settings
database.host=localhost
! Alternative comment style
database.port=5432
"""
        result = formats.parse_properties_file(properties_content)

        assert result["success"] == "true"
        properties = json.loads(result["properties"])
        assert "database.host" in properties

    def test_parse_line_continuations(self) -> None:
        """Test parsing line continuations."""
        properties_content = r"""
long.value=This is a \
    long value that \
    spans multiple lines
"""
        result = formats.parse_properties_file(properties_content)

        assert result["success"] == "true"
        properties = json.loads(result["properties"])
        assert "long.value" in properties
        # Line continuation should combine lines
        assert "multiple lines" in properties["long.value"]

    def test_parse_escape_sequences(self) -> None:
        """Test parsing escape sequences."""
        properties_content = r"""
message=Line 1\nLine 2\tTabbed
path=C:\\Users\\test
"""
        result = formats.parse_properties_file(properties_content)

        assert result["success"] == "true"
        properties = json.loads(result["properties"])
        assert "\n" in properties["message"]
        assert "\t" in properties["message"]
        assert "\\" in properties["path"]

    def test_parse_colon_separator(self) -> None:
        """Test parsing with colon separator."""
        properties_content = """
database.host: localhost
database.port: 5432
"""
        result = formats.parse_properties_file(properties_content)

        assert result["success"] == "true"
        properties = json.loads(result["properties"])
        assert properties["database.host"] == "localhost"

    def test_parse_quoted_values(self) -> None:
        """Test parsing quoted values."""
        properties_content = """
message="Hello, World!"
"""
        result = formats.parse_properties_file(properties_content)

        assert result["success"] == "true"
        properties = json.loads(result["properties"])
        # Quotes should be removed
        assert properties["message"] == "Hello, World!"


class TestValidateXmlSyntax:
    """Tests for validate_xml_syntax function."""

    def test_validate_valid_xml(self) -> None:
        """Test validation of valid XML."""
        xml_content = """<?xml version="1.0"?>
<configuration>
  <database>
    <host>localhost</host>
    <port>5432</port>
  </database>
</configuration>"""
        result = formats.validate_xml_syntax(xml_content)

        assert result["is_valid"] == "true"
        assert result["root_tag"] == "configuration"

    def test_validate_xml_without_declaration(self) -> None:
        """Test validation of XML without XML declaration."""
        xml_content = """
<config>
  <setting>value</setting>
</config>
"""
        result = formats.validate_xml_syntax(xml_content)

        assert result["is_valid"] == "true"
        assert result["root_tag"] == "config"

    def test_validate_malformed_xml(self) -> None:
        """Test validation of malformed XML."""
        xml_content = """
<configuration>
  <database>
    <host>localhost
  </database>
</configuration>
"""
        result = formats.validate_xml_syntax(xml_content)

        assert result["is_valid"] == "false"
        assert result["error_message"] != ""

    def test_validate_unclosed_tag(self) -> None:
        """Test validation catches unclosed tags."""
        xml_content = """
<configuration>
  <database>
    <host>localhost</host>
  <!-- Missing closing tag for database -->
</configuration>
"""
        result = formats.validate_xml_syntax(xml_content)

        assert result["is_valid"] == "false"

    def test_validate_empty_content_raises(self) -> None:
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError, match="xml_content cannot be empty"):
            formats.validate_xml_syntax("")


class TestParseXmlValue:
    """Tests for parse_xml_value function."""

    def test_parse_simple_element(self) -> None:
        """Test parsing simple element."""
        xml_content = """
<configuration>
  <database>
    <host>localhost</host>
  </database>
</configuration>
"""
        result = formats.parse_xml_value(xml_content, "./database/host")

        assert result["found"] == "true"
        assert result["value"] == "localhost"

    def test_parse_element_with_attributes(self) -> None:
        """Test parsing element with attributes."""
        xml_content = """
<configuration>
  <server name="main" region="us-east">production</server>
</configuration>
"""
        result = formats.parse_xml_value(xml_content, "./server")

        assert result["found"] == "true"
        assert result["value"] == "production"
        assert result["attribute_count"] == "2"

    def test_parse_element_with_children(self) -> None:
        """Test parsing element with child elements."""
        xml_content = """
<configuration>
  <database>
    <host>localhost</host>
    <port>5432</port>
    <credentials>
      <user>admin</user>
    </credentials>
  </database>
</configuration>
"""
        result = formats.parse_xml_value(xml_content, "./database")

        assert result["found"] == "true"
        assert int(result["child_count"]) == 3

    def test_parse_nonexistent_element(self) -> None:
        """Test parsing non-existent element."""
        xml_content = """
<configuration>
  <database>
    <host>localhost</host>
  </database>
</configuration>
"""
        result = formats.parse_xml_value(xml_content, "./nonexistent")

        assert result["found"] == "false"
        assert "No element found" in result["error_message"]

    def test_parse_nested_element(self) -> None:
        """Test parsing deeply nested element."""
        xml_content = """
<configuration>
  <database>
    <credentials>
      <user>admin</user>
    </credentials>
  </database>
</configuration>
"""
        result = formats.parse_xml_value(xml_content, "./database/credentials/user")

        assert result["found"] == "true"
        assert result["value"] == "admin"

    def test_parse_invalid_xml_error(self) -> None:
        """Test error on invalid XML."""
        xml_content = "<invalid>xml"

        result = formats.parse_xml_value(xml_content, "./test")

        assert result["found"] == "false"
        assert "XML parse error" in result["error_message"]

    def test_parse_empty_xpath_raises(self) -> None:
        """Test that empty xpath raises ValueError."""
        with pytest.raises(ValueError, match="xpath cannot be empty"):
            formats.parse_xml_value("<config></config>", "")
