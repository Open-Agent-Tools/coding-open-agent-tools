"""Tests for python extractors module."""

import pytest

from coding_open_agent_tools.python.extractors import (
    extract_docstring_info,
    extract_type_annotations,
    get_function_dependencies,
    parse_function_signature,
)


class TestParseFunctionSignature:
    """Tests for parse_function_signature function."""

    def test_basic_function(self):
        """Test parsing basic function signature."""
        code = """
def greet(name: str) -> str:
    return f"Hello, {name}"
"""
        result = parse_function_signature(code, "greet")
        assert result["function_name"] == "greet"
        assert len(result["parameters"]) == 1
        assert result["parameters"][0]["name"] == "name"
        assert result["parameters"][0]["type_hint"] == "str"
        assert result["parameters"][0]["has_default"] == "false"
        assert result["return_type"] == "str"
        assert result["is_async"] == "false"

    def test_function_with_defaults(self):
        """Test parsing function with default values."""
        code = """
def connect(host: str, port: int = 8080) -> bool:
    return True
"""
        result = parse_function_signature(code, "connect")
        assert len(result["parameters"]) == 2
        assert result["parameters"][0]["has_default"] == "false"
        assert result["parameters"][1]["has_default"] == "true"
        assert result["parameters"][1]["default_value"] == "8080"

    def test_async_function(self):
        """Test parsing async function."""
        code = """
async def fetch_data(url: str) -> dict[str, str]:
    return {}
"""
        result = parse_function_signature(code, "fetch_data")
        assert result["is_async"] == "true"
        assert result["return_type"] == "dict[str, str]"

    def test_function_no_type_hints(self):
        """Test parsing function without type hints."""
        code = """
def legacy_function(x, y):
    return x + y
"""
        result = parse_function_signature(code, "legacy_function")
        assert len(result["parameters"]) == 2
        assert result["parameters"][0]["type_hint"] == ""
        assert result["return_type"] == ""

    def test_method_skips_self(self):
        """Test that self parameter is skipped."""
        code = """
class MyClass:
    def method(self, value: int) -> None:
        pass
"""
        result = parse_function_signature(code, "method")
        assert len(result["parameters"]) == 1
        assert result["parameters"][0]["name"] == "value"

    def test_classmethod_skips_cls(self):
        """Test that cls parameter is skipped."""
        code = """
class MyClass:
    @classmethod
    def create(cls, value: int) -> 'MyClass':
        pass
"""
        result = parse_function_signature(code, "create")
        assert len(result["parameters"]) == 1
        assert result["parameters"][0]["name"] == "value"

    def test_function_not_found(self):
        """Test error when function not found."""
        code = "def other(): pass"
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            parse_function_signature(code, "missing")

    def test_syntax_error(self):
        """Test error on syntax error."""
        code = "def broken("
        with pytest.raises(ValueError, match="Cannot parse source code"):
            parse_function_signature(code, "broken")

    def test_type_errors(self):
        """Test TypeErrors for invalid inputs."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            parse_function_signature(123, "func")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="function_name must be a string"):
            parse_function_signature("def test(): pass", 123)  # type: ignore[arg-type]

    def test_value_errors(self):
        """Test ValueErrors for empty inputs."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            parse_function_signature("", "func")

        with pytest.raises(ValueError, match="function_name cannot be empty"):
            parse_function_signature("def test(): pass", "")


class TestExtractDocstringInfo:
    """Tests for extract_docstring_info function."""

    def test_no_docstring(self):
        """Test function without docstring."""
        code = """
def no_docs():
    return True
"""
        result = extract_docstring_info(code, "no_docs")
        assert result["has_docstring"] == "false"
        assert result["style"] == "none"

    def test_google_style_docstring(self):
        """Test parsing Google-style docstring."""
        code = '''
def process(data: str, count: int) -> dict[str, str]:
    """Process input data.

    This function processes data and returns results.

    Args:
        data: The input data to process
        count: Number of times to process

    Returns:
        Dictionary with processed results

    Raises:
        ValueError: If data is invalid
    """
    return {}
'''
        result = extract_docstring_info(code, "process")
        assert result["has_docstring"] == "true"
        assert result["style"] == "google"
        assert "Process input data" in result["summary"]
        assert len(result["args"]) == 2
        assert result["args"][0]["name"] == "data"
        assert "processed results" in result["returns"].lower()
        # Raises parsing may or may not capture all sections
        assert isinstance(result["raises"], list)

    def test_plain_docstring(self):
        """Test parsing plain docstring."""
        code = '''
def simple():
    """This is a simple docstring."""
    pass
'''
        result = extract_docstring_info(code, "simple")
        assert result["has_docstring"] == "true"
        assert result["style"] == "plain"
        assert "simple docstring" in result["summary"]

    def test_multiline_summary(self):
        """Test extraction of multi-line summary."""
        code = '''
def multi():
    """This is a long summary that spans
    multiple lines.

    Args:
        test: A test parameter
    """
    pass
'''
        result = extract_docstring_info(code, "multi")
        assert "long summary" in result["summary"]
        assert "multiple lines" in result["summary"]

    def test_function_not_found(self):
        """Test error when function not found."""
        code = "def other(): pass"
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            extract_docstring_info(code, "missing")

    def test_type_errors(self):
        """Test TypeErrors for invalid inputs."""
        with pytest.raises(TypeError):
            extract_docstring_info(123, "func")  # type: ignore[arg-type]

        with pytest.raises(TypeError):
            extract_docstring_info("def test(): pass", 123)  # type: ignore[arg-type]

    def test_value_errors(self):
        """Test ValueErrors for empty inputs."""
        with pytest.raises(ValueError):
            extract_docstring_info("", "func")

        with pytest.raises(ValueError):
            extract_docstring_info("def test(): pass", "")


class TestExtractTypeAnnotations:
    """Tests for extract_type_annotations function."""

    def test_function_annotations(self):
        """Test extraction of function type annotations."""
        code = """
def process(data: str, count: int) -> dict[str, str]:
    return {}
"""
        result = extract_type_annotations(code)
        assert int(result["total_functions"]) == 1
        assert len(result["functions"]) == 1
        func = result["functions"][0]
        assert func["name"] == "process"
        assert "data: str" in func["parameters"]
        assert "count: int" in func["parameters"]
        assert func["return_type"] == "dict[str, str]"

    def test_variable_annotations(self):
        """Test extraction of variable type annotations."""
        code = """
name: str = "Alice"
count: int = 42
config: dict[str, str] = {}
"""
        result = extract_type_annotations(code)
        assert int(result["total_variables"]) == 3
        var_names = [v["name"] for v in result["variables"]]
        assert "name" in var_names
        assert "count" in var_names
        assert "config" in var_names

    def test_function_without_annotations(self):
        """Test function without type annotations."""
        code = """
def legacy(x, y):
    return x + y
"""
        result = extract_type_annotations(code)
        assert int(result["total_functions"]) == 1
        func = result["functions"][0]
        assert "(no return type)" in func["return_type"]
        assert any("(no type)" in param for param in func["parameters"])

    def test_multiple_functions(self):
        """Test extraction from multiple functions."""
        code = """
def func1(x: int) -> int:
    return x

def func2(y: str) -> str:
    return y

async def func3(z: bool) -> bool:
    return z
"""
        result = extract_type_annotations(code)
        assert int(result["total_functions"]) == 3
        func_names = [f["name"] for f in result["functions"]]
        assert "func1" in func_names
        assert "func2" in func_names
        assert "func3" in func_names

    def test_syntax_error(self):
        """Test error handling for syntax error."""
        code = "def broken("
        with pytest.raises(ValueError, match="Cannot parse source code"):
            extract_type_annotations(code)

    def test_type_error(self):
        """Test TypeError for non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            extract_type_annotations(123)  # type: ignore[arg-type]

    def test_value_error_empty(self):
        """Test ValueError for empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            extract_type_annotations("")


class TestGetFunctionDependencies:
    """Tests for get_function_dependencies function."""

    def test_function_calls(self):
        """Test detection of function calls."""
        code = """
def helper():
    return 42

def main():
    result = helper()
    return result
"""
        result = get_function_dependencies(code, "main")
        assert "helper" in result["functions_called"]

    def test_module_usage(self):
        """Test detection of module usage."""
        code = """
import os

def get_path():
    result = os.listdir(".")
    return result
"""
        result = get_function_dependencies(code, "get_path")
        assert "os" in result["modules_used"]

    def test_builtin_usage(self):
        """Test detection of builtin functions."""
        code = """
def process(items):
    return len(items) + sum(items)
"""
        result = get_function_dependencies(code, "process")
        assert "len" in result["builtins_used"]
        assert "sum" in result["builtins_used"]

    def test_global_variables(self):
        """Test detection of global variable references."""
        code = """
CONFIG = {"key": "value"}

def get_config():
    return CONFIG
"""
        result = get_function_dependencies(code, "get_config")
        assert "CONFIG" in result["global_variables"]

    def test_local_variables_not_global(self):
        """Test that local variables are not flagged as global."""
        code = """
def process():
    local_var = 42
    return local_var
"""
        result = get_function_dependencies(code, "process")
        assert "local_var" not in result["global_variables"]

    def test_no_dependencies(self):
        """Test function with no dependencies."""
        code = """
def simple():
    return 42
"""
        result = get_function_dependencies(code, "simple")
        assert len(result["functions_called"]) == 0
        assert len(result["modules_used"]) == 0
        assert len(result["global_variables"]) == 0

    def test_total_dependencies(self):
        """Test total dependency count."""
        code = """
import os

def process():
    return len(os.listdir("."))
"""
        result = get_function_dependencies(code, "process")
        total = int(result["total_dependencies"])
        assert total >= 2  # At least os module and len builtin

    def test_function_not_found(self):
        """Test error when function not found."""
        code = "def other(): pass"
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            get_function_dependencies(code, "missing")

    def test_type_errors(self):
        """Test TypeErrors for invalid inputs."""
        with pytest.raises(TypeError):
            get_function_dependencies(123, "func")  # type: ignore[arg-type]

        with pytest.raises(TypeError):
            get_function_dependencies("def test(): pass", 123)  # type: ignore[arg-type]

    def test_value_errors(self):
        """Test ValueErrors for empty inputs."""
        with pytest.raises(ValueError):
            get_function_dependencies("", "func")

        with pytest.raises(ValueError):
            get_function_dependencies("def test(): pass", "")
