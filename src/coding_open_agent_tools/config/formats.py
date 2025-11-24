"""Common configuration format parsing functions.

Provides tools for parsing INI, properties, and XML configuration files.
"""

import configparser
import json
import re
import xml.etree.ElementTree as ET

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def parse_ini_file(ini_content: str) -> dict[str, str]:
    """Parse INI/CFG file content into a nested dictionary.

    Handles sections, key-value pairs, comments, and multi-line values.

    Args:
        ini_content: INI file content as string

    Returns:
        Dictionary with:
        - success: "true" or "false"
        - section_count: Number of sections parsed
        - data: JSON string of nested dict (section -> key -> value)
        - error_message: Error description if parsing failed

    Raises:
        TypeError: If ini_content is not a string
        ValueError: If ini_content is empty
    """
    if not isinstance(ini_content, str):
        raise TypeError("ini_content must be a string")
    if not ini_content.strip():
        raise ValueError("ini_content cannot be empty")

    try:
        parser = configparser.ConfigParser()
        parser.read_string(ini_content)

        # Convert to nested dict
        result = {}
        for section in parser.sections():
            result[section] = dict(parser.items(section))

        return {
            "success": "true",
            "section_count": str(len(result)),
            "data": json.dumps(result),
            "error_message": "",
        }

    except configparser.Error as e:
        return {
            "success": "false",
            "section_count": "0",
            "data": json.dumps({}),
            "error_message": f"INI parse error: {str(e)}",
        }
    except Exception as e:
        return {
            "success": "false",
            "section_count": "0",
            "data": json.dumps({}),
            "error_message": f"Parse error: {str(e)}",
        }


@strands_tool
def validate_ini_syntax(ini_content: str) -> dict[str, str]:
    """Validate INI file syntax and structure.

    Checks for malformed sections, invalid assignments, and syntax errors.

    Args:
        ini_content: INI file content as string

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - error_count: Number of errors found
        - warning_count: Number of warnings
        - errors: JSON string of error messages
        - warnings: JSON string of warning messages

    Raises:
        TypeError: If ini_content is not a string
        ValueError: If ini_content is empty
    """
    if not isinstance(ini_content, str):
        raise TypeError("ini_content must be a string")
    if not ini_content.strip():
        raise ValueError("ini_content cannot be empty")

    errors = []
    warnings = []

    try:
        parser = configparser.ConfigParser()
        parser.read_string(ini_content)

        # Check for duplicate sections
        seen_sections = set()
        for line_num, line in enumerate(ini_content.splitlines(), 1):
            stripped = line.strip()

            # Check section headers
            if stripped.startswith("[") and stripped.endswith("]"):
                section_name = stripped[1:-1]
                if section_name in seen_sections:
                    warnings.append(
                        f"Line {line_num}: Duplicate section '{section_name}'"
                    )
                seen_sections.add(section_name)

            # Check for assignments outside sections
            elif (
                "=" in stripped
                and not stripped.startswith("#")
                and not stripped.startswith(";")
            ):
                if len(seen_sections) == 0:
                    warnings.append(
                        f"Line {line_num}: Key-value pair outside any section"
                    )

    except configparser.DuplicateSectionError as e:
        errors.append(f"Duplicate section: {str(e)}")
    except configparser.DuplicateOptionError as e:
        errors.append(f"Duplicate option: {str(e)}")
    except configparser.MissingSectionHeaderError as e:
        errors.append(f"Missing section header: {str(e)}")
    except configparser.ParsingError as e:
        errors.append(f"Parsing error: {str(e)}")
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")

    return {
        "is_valid": "true" if len(errors) == 0 else "false",
        "error_count": str(len(errors)),
        "warning_count": str(len(warnings)),
        "errors": json.dumps(errors),
        "warnings": json.dumps(warnings),
    }


@strands_tool
def parse_properties_file(properties_content: str) -> dict[str, str]:
    """Parse Java .properties file content into a dictionary.

    Handles key-value pairs, comments, line continuations, and Unicode escapes.

    Args:
        properties_content: Properties file content as string

    Returns:
        Dictionary with:
        - success: "true" or "false"
        - property_count: Number of properties parsed
        - properties: JSON string of key-value pairs
        - error_message: Error description if parsing failed

    Raises:
        TypeError: If properties_content is not a string
        ValueError: If properties_content is empty
    """
    if not isinstance(properties_content, str):
        raise TypeError("properties_content must be a string")
    if not properties_content.strip():
        raise ValueError("properties_content cannot be empty")

    try:
        properties = {}
        lines = properties_content.splitlines()
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines and comments
            if not line or line.startswith("#") or line.startswith("!"):
                i += 1
                continue

            # Handle line continuations (backslash at end)
            while line.endswith("\\") and i + 1 < len(lines):
                line = line[:-1] + lines[i + 1].strip()
                i += 1

            # Find separator (=, :, or space)
            match = re.match(r"^([^=:\s]+)\s*[=:]\s*(.*)$", line)
            if match:
                key = match.group(1)
                value = match.group(2)

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]

                # Handle Unicode escapes (\uXXXX)
                value = re.sub(
                    r"\\u([0-9a-fA-F]{4})",
                    lambda m: chr(int(m.group(1), 16)),
                    value,
                )

                # Handle escape sequences
                value = value.replace("\\n", "\n")
                value = value.replace("\\r", "\r")
                value = value.replace("\\t", "\t")
                value = value.replace("\\\\", "\\")

                properties[key] = value

            i += 1

        return {
            "success": "true",
            "property_count": str(len(properties)),
            "properties": json.dumps(properties),
            "error_message": "",
        }

    except Exception as e:
        return {
            "success": "false",
            "property_count": "0",
            "properties": json.dumps({}),
            "error_message": f"Parse error: {str(e)}",
        }


@strands_tool
def validate_xml_syntax(xml_content: str) -> dict[str, str]:
    """Validate XML configuration file syntax.

    Checks for well-formed XML structure and syntax errors.

    Args:
        xml_content: XML content as string

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - root_tag: Root element tag name if valid
        - error_message: Error description if invalid
        - line_number: Line number of error
        - column_number: Column number of error

    Raises:
        TypeError: If xml_content is not a string
        ValueError: If xml_content is empty
    """
    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")
    if not xml_content.strip():
        raise ValueError("xml_content cannot be empty")

    try:
        root = ET.fromstring(xml_content)

        return {
            "is_valid": "true",
            "root_tag": root.tag,
            "error_message": "",
            "line_number": "0",
            "column_number": "0",
        }

    except ET.ParseError as e:
        # Extract line and column from error message
        line_num = "0"
        col_num = "0"

        # ParseError format: "error message: line X, column Y"
        match = re.search(r"line (\d+), column (\d+)", str(e))
        if match:
            line_num = match.group(1)
            col_num = match.group(2)

        return {
            "is_valid": "false",
            "root_tag": "",
            "error_message": str(e),
            "line_number": line_num,
            "column_number": col_num,
        }
    except Exception as e:
        return {
            "is_valid": "false",
            "root_tag": "",
            "error_message": f"XML parse error: {str(e)}",
            "line_number": "0",
            "column_number": "0",
        }


@strands_tool
def parse_xml_value(xml_content: str, xpath: str) -> dict[str, str]:
    """Extract value from XML configuration using XPath-like syntax.

    Supports simple XPath expressions for element selection.

    Args:
        xml_content: XML content as string
        xpath: XPath expression (e.g., "./database/host")

    Returns:
        Dictionary with:
        - found: "true" or "false"
        - value: Text content of element if found
        - attribute_count: Number of attributes on element
        - child_count: Number of child elements
        - error_message: Error description if not found

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty
    """
    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")
    if not isinstance(xpath, str):
        raise TypeError("xpath must be a string")
    if not xml_content.strip():
        raise ValueError("xml_content cannot be empty")
    if not xpath.strip():
        raise ValueError("xpath cannot be empty")

    try:
        root = ET.fromstring(xml_content)
        element = root.find(xpath)

        if element is None:
            return {
                "found": "false",
                "value": "",
                "attribute_count": "0",
                "child_count": "0",
                "error_message": f"No element found at XPath '{xpath}'",
            }

        # Get text content (including tail text)
        text = element.text or ""

        return {
            "found": "true",
            "value": text,
            "attribute_count": str(len(element.attrib)),
            "child_count": str(len(list(element))),
            "error_message": "",
        }

    except ET.ParseError as e:
        return {
            "found": "false",
            "value": "",
            "attribute_count": "0",
            "child_count": "0",
            "error_message": f"XML parse error: {str(e)}",
        }
    except Exception as e:
        return {
            "found": "false",
            "value": "",
            "attribute_count": "0",
            "child_count": "0",
            "error_message": f"XPath error: {str(e)}",
        }
