"""Tests for python validators module."""

import pytest

from coding_open_agent_tools.python.validators import (
    check_adk_compliance,
    validate_import_order,
    validate_python_syntax,
    validate_type_hints,
)


class TestValidatePythonSyntax:
    """Tests for validate_python_syntax function."""

    def test_valid_syntax(self):
        """Test validation of valid Python code."""
        code = """
def hello(name: str) -> str:
    return f"Hello, {name}!"
"""
        result = validate_python_syntax(code)
        assert result["is_valid"] == "true"
        assert result["error_message"] == ""
        assert result["line_number"] == "0"
        assert result["error_type"] == ""

    def test_syntax_error(self):
        """Test detection of syntax error."""
        code = "def broken(\n    return 'missing colon'"
        result = validate_python_syntax(code)
        assert result["is_valid"] == "false"
        assert result["error_message"] != ""
        assert result["error_type"] == "SyntaxError"
        assert int(result["line_number"]) > 0

    def test_indentation_error(self):
        """Test detection of indentation error."""
        code = """
def test():
return 'bad indent'
"""
        result = validate_python_syntax(code)
        assert result["is_valid"] == "false"
        assert "indent" in result["error_message"].lower() or result["error_type"] == "IndentationError"

    def test_type_error_non_string(self):
        """Test TypeError for non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            validate_python_syntax(123)  # type: ignore[arg-type]

    def test_value_error_empty(self):
        """Test ValueError for empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            validate_python_syntax("")

    def test_value_error_whitespace_only(self):
        """Test ValueError for whitespace-only input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            validate_python_syntax("   \n\t  ")


class TestValidateTypeHints:
    """Tests for validate_type_hints function."""

    def test_valid_type_hints(self):
        """Test validation of code with proper type hints."""
        code = """
def calculate(x: int, y: int) -> int:
    return x + y
"""
        result = validate_type_hints(code)
        assert result["is_valid"] == "true"
        assert len(result["issues_found"]) == 0
        assert result["total_issues"] == "0"
        assert int(result["functions_checked"]) == 1

    def test_missing_return_type(self):
        """Test detection of missing return type."""
        code = """
def process(data: str):
    return data.upper()
"""
        result = validate_type_hints(code)
        assert result["is_valid"] == "false"
        assert len(result["issues_found"]) > 0
        assert any(issue["issue_type"] == "missing_return_type" for issue in result["issues_found"])

    def test_missing_parameter_type(self):
        """Test detection of missing parameter type."""
        code = """
def greet(name) -> str:
    return f"Hello, {name}"
"""
        result = validate_type_hints(code)
        assert result["is_valid"] == "false"
        assert any(issue["issue_type"] == "missing_parameter_type" for issue in result["issues_found"])

    def test_deprecated_typing_list(self):
        """Test detection of deprecated List from typing."""
        code = """
from typing import List

def get_names() -> List[str]:
    return ["Alice", "Bob"]
"""
        result = validate_type_hints(code)
        assert result["is_valid"] == "false"
        assert any(issue["issue_type"] == "deprecated_typing" for issue in result["issues_found"])
        assert any("List" in issue["description"] for issue in result["issues_found"])

    def test_deprecated_typing_dict(self):
        """Test detection of deprecated Dict from typing."""
        code = """
from typing import Dict

def get_config() -> Dict[str, str]:
    return {"key": "value"}
"""
        result = validate_type_hints(code)
        assert result["is_valid"] == "false"
        assert any("Dict" in issue["description"] for issue in result["issues_found"])

    def test_init_without_return_type_ok(self):
        """Test that __init__ doesn't require return type."""
        code = """
class MyClass:
    def __init__(self, value: int):
        self.value = value
"""
        result = validate_type_hints(code)
        # Should not flag __init__ as missing return type
        init_issues = [i for i in result["issues_found"] if "issue_type" in i and i["issue_type"] == "missing_return_type"]
        assert len(init_issues) == 0

    def test_self_parameter_ok(self):
        """Test that self parameter doesn't need type hint."""
        code = """
class MyClass:
    def method(self, value: int) -> None:
        pass
"""
        result = validate_type_hints(code)
        # Should not flag 'self' as missing type
        self_issues = [i for i in result["issues_found"] if "'self'" in i.get("description", "")]
        assert len(self_issues) == 0

    def test_syntax_error_handling(self):
        """Test handling of syntax errors."""
        code = "def broken("
        result = validate_type_hints(code)
        assert result["is_valid"] == "false"
        assert result["total_issues"] == "1"
        assert result["functions_checked"] == "0"

    def test_type_error(self):
        """Test TypeError for non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            validate_type_hints(123)  # type: ignore[arg-type]

    def test_value_error_empty(self):
        """Test ValueError for empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            validate_type_hints("")


class TestValidateImportOrder:
    """Tests for validate_import_order function."""

    def test_correct_import_order(self):
        """Test validation of correctly ordered imports."""
        code = """
import os
import sys
"""
        result = validate_import_order(code)
        assert result["is_valid"] == "true"
        assert len(result["issues_found"]) == 0

    def test_incorrect_group_order(self):
        """Test detection of incorrect import group ordering."""
        code = """
import requests
import os
"""
        result = validate_import_order(code)
        assert result["is_valid"] == "false"
        assert any(issue["issue_type"] == "incorrect_group_order" for issue in result["issues_found"])

    def test_incorrect_alphabetical_order(self):
        """Test detection of incorrect alphabetical ordering."""
        code = """
import sys
import os
"""
        result = validate_import_order(code)
        assert result["is_valid"] == "false"
        assert any(issue["issue_type"] == "incorrect_alphabetical_order" for issue in result["issues_found"])

    def test_no_imports(self):
        """Test code with no imports."""
        code = """
def hello():
    return "world"
"""
        result = validate_import_order(code)
        assert result["is_valid"] == "true"
        assert result["imports_checked"] == "0"

    def test_mixed_import_styles(self):
        """Test handling of both import and from import."""
        code = """
import os
from pathlib import Path
import sys
"""
        result = validate_import_order(code)
        # Should detect ordering issue
        assert int(result["imports_checked"]) >= 3

    def test_syntax_error_handling(self):
        """Test handling of syntax errors."""
        code = "import ("
        result = validate_import_order(code)
        assert result["is_valid"] == "false"
        assert result["imports_checked"] == "0"

    def test_type_error(self):
        """Test TypeError for non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            validate_import_order(123)  # type: ignore[arg-type]

    def test_value_error_empty(self):
        """Test ValueError for empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            validate_import_order("")


class TestCheckAdkCompliance:
    """Tests for check_adk_compliance function."""

    def test_compliant_function(self):
        """Test validation of ADK-compliant function."""
        code = """
def process_data(input_data: str, config: dict[str, str]) -> dict[str, str]:
    return {"result": input_data, **config}
"""
        result = check_adk_compliance(code, "process_data")
        assert result["is_compliant"] == "true"
        assert len(result["issues_found"]) == 0
        assert result["function_name"] == "process_data"

    def test_missing_return_type(self):
        """Test detection of missing return type."""
        code = """
def process_data(input_data: str):
    return input_data
"""
        result = check_adk_compliance(code, "process_data")
        assert result["is_compliant"] == "false"
        assert any(issue["issue_type"] == "missing_return_type" for issue in result["issues_found"])

    def test_default_parameter_values(self):
        """Test detection of default parameter values (not allowed in ADK)."""
        code = """
def process_data(input_data: str = "default") -> str:
    return input_data
"""
        result = check_adk_compliance(code, "process_data")
        assert result["is_compliant"] == "false"
        assert any(issue["issue_type"] == "default_parameter_values" for issue in result["issues_found"])

    def test_missing_parameter_type(self):
        """Test detection of missing parameter type."""
        code = """
def process_data(input_data) -> str:
    return str(input_data)
"""
        result = check_adk_compliance(code, "process_data")
        assert result["is_compliant"] == "false"
        assert any(issue["issue_type"] == "missing_parameter_type" for issue in result["issues_found"])

    def test_non_json_serializable_return(self):
        """Test detection of non-JSON-serializable return types."""
        code = """
def get_items() -> set[str]:
    return {"item1", "item2"}
"""
        result = check_adk_compliance(code, "get_items")
        assert result["is_compliant"] == "false"
        assert any(issue["issue_type"] == "non_json_serializable_return" for issue in result["issues_found"])

    def test_bytes_return_type(self):
        """Test detection of bytes return type (not JSON-serializable)."""
        code = """
def get_data() -> bytes:
    return b"data"
"""
        result = check_adk_compliance(code, "get_data")
        assert result["is_compliant"] == "false"
        assert any("bytes" in issue["description"] for issue in result["issues_found"])

    def test_function_not_found(self):
        """Test error when function not found."""
        code = """
def other_function() -> str:
    return "test"
"""
        with pytest.raises(ValueError, match="Function 'missing_function' not found"):
            check_adk_compliance(code, "missing_function")

    def test_syntax_error_handling(self):
        """Test handling of syntax errors."""
        code = "def broken("
        result = check_adk_compliance(code, "broken")
        assert result["is_compliant"] == "false"
        assert any(issue["issue_type"] == "syntax_error" for issue in result["issues_found"])

    def test_type_error_source_code(self):
        """Test TypeError for non-string source_code."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            check_adk_compliance(123, "func")  # type: ignore[arg-type]

    def test_type_error_function_name(self):
        """Test TypeError for non-string function_name."""
        with pytest.raises(TypeError, match="function_name must be a string"):
            check_adk_compliance("def test(): pass", 123)  # type: ignore[arg-type]

    def test_value_error_empty_source(self):
        """Test ValueError for empty source_code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            check_adk_compliance("", "func")

    def test_value_error_empty_function_name(self):
        """Test ValueError for empty function_name."""
        with pytest.raises(ValueError, match="function_name cannot be empty"):
            check_adk_compliance("def test(): pass", "")
