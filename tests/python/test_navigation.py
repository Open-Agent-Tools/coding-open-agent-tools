"""Tests for python navigation module."""

import json

import pytest

from coding_open_agent_tools.python.navigation import (
    extract_python_public_api,
    find_python_definitions_by_decorator,
    find_python_function_usages,
    get_python_class_docstring,
    get_python_class_hierarchy,
    get_python_class_line_numbers,
    get_python_function_body,
    get_python_function_details,
    get_python_function_docstring,
    get_python_function_line_numbers,
    get_python_function_signature,
    get_python_method_line_numbers,
    get_python_module_overview,
    list_python_class_methods,
    list_python_classes,
    list_python_function_calls,
    list_python_functions,
)


class TestGetPythonFunctionLineNumbers:
    """Tests for get_python_function_line_numbers function."""

    def test_simple_function(self):
        """Test getting line numbers for a simple function."""
        code = """def hello():
    return "world"
"""
        result = get_python_function_line_numbers(code, "hello")
        assert result["function_name"] == "hello"
        assert result["start_line"] == "1"
        assert result["end_line"] == "2"

    def test_multiline_function(self):
        """Test getting line numbers for a multiline function."""
        code = """
def process_data(x):
    result = x * 2
    result += 1
    return result
"""
        result = get_python_function_line_numbers(code, "process_data")
        assert result["function_name"] == "process_data"
        assert result["start_line"] == "2"
        assert result["end_line"] == "5"

    def test_nested_function(self):
        """Test getting line numbers for outer function (not nested)."""
        code = """
def outer():
    def inner():
        pass
    return inner
"""
        result = get_python_function_line_numbers(code, "outer")
        assert result["function_name"] == "outer"
        assert result["start_line"] == "2"
        assert result["end_line"] == "5"

    def test_function_not_found(self):
        """Test error when function doesn't exist."""
        code = "def hello(): pass"
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            get_python_function_line_numbers(code, "missing")

    def test_type_error_source_code(self):
        """Test TypeError for non-string source_code."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            get_python_function_line_numbers(123, "test")  # type: ignore[arg-type]

    def test_type_error_function_name(self):
        """Test TypeError for non-string function_name."""
        with pytest.raises(TypeError, match="function_name must be a string"):
            get_python_function_line_numbers("def test(): pass", 123)  # type: ignore[arg-type]

    def test_value_error_empty_code(self):
        """Test ValueError for empty source code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            get_python_function_line_numbers("", "test")

    def test_syntax_error_in_code(self):
        """Test error handling for invalid syntax."""
        code = "def broken(\n    pass"
        with pytest.raises(ValueError, match="Invalid Python syntax"):
            get_python_function_line_numbers(code, "broken")


class TestGetPythonClassLineNumbers:
    """Tests for get_python_class_line_numbers function."""

    def test_simple_class(self):
        """Test getting line numbers for a simple class."""
        code = """class MyClass:
    pass
"""
        result = get_python_class_line_numbers(code, "MyClass")
        assert result["class_name"] == "MyClass"
        assert result["start_line"] == "1"
        assert result["end_line"] == "2"

    def test_class_with_methods(self):
        """Test getting line numbers for class with methods."""
        code = """
class DataProcessor:
    def __init__(self):
        self.data = []

    def process(self, x):
        return x * 2
"""
        result = get_python_class_line_numbers(code, "DataProcessor")
        assert result["class_name"] == "DataProcessor"
        assert result["start_line"] == "2"
        assert result["end_line"] == "7"

    def test_class_not_found(self):
        """Test error when class doesn't exist."""
        code = "class MyClass: pass"
        with pytest.raises(ValueError, match="Class 'Missing' not found"):
            get_python_class_line_numbers(code, "Missing")

    def test_type_error_source_code(self):
        """Test TypeError for non-string source_code."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            get_python_class_line_numbers(123, "Test")  # type: ignore[arg-type]

    def test_type_error_class_name(self):
        """Test TypeError for non-string class_name."""
        with pytest.raises(TypeError, match="class_name must be a string"):
            get_python_class_line_numbers("class Test: pass", 123)  # type: ignore[arg-type]

    def test_value_error_empty_code(self):
        """Test ValueError for empty source code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            get_python_class_line_numbers("", "Test")


class TestGetPythonModuleOverview:
    """Tests for get_python_module_overview function."""

    def test_simple_module(self):
        """Test overview of simple module."""
        code = '''"""Module docstring."""

def func1():
    pass

def func2():
    pass

class MyClass:
    pass
'''
        result = get_python_module_overview(code)
        assert result["module_docstring"] == "Module docstring."
        assert result["function_count"] == "2"
        assert result["class_count"] == "1"
        assert json.loads(result["function_names"]) == ["func1", "func2"]
        assert json.loads(result["class_names"]) == ["MyClass"]

    def test_module_with_imports(self):
        """Test counting import statements."""
        code = """import os
from typing import Any
import sys

def test():
    pass
"""
        result = get_python_module_overview(code)
        assert result["import_count"] == "3"
        assert result["function_count"] == "1"

    def test_module_with_main_block(self):
        """Test detection of __main__ block."""
        code = """
def main():
    pass

if __name__ == "__main__":
    main()
"""
        result = get_python_module_overview(code)
        assert result["has_main_block"] == "true"

    def test_module_without_main_block(self):
        """Test no false positive for __main__ detection."""
        code = "def test(): pass"
        result = get_python_module_overview(code)
        assert result["has_main_block"] == "false"

    def test_total_lines(self):
        """Test line count."""
        code = "line1\nline2\nline3"
        result = get_python_module_overview(code)
        assert result["total_lines"] == "3"

    def test_type_error(self):
        """Test TypeError for non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            get_python_module_overview(123)  # type: ignore[arg-type]

    def test_value_error_empty(self):
        """Test ValueError for empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            get_python_module_overview("")


class TestListPythonFunctions:
    """Tests for list_python_functions function."""

    def test_list_simple_functions(self):
        """Test listing simple functions."""
        code = """
def func1(x: int) -> str:
    return str(x)

def func2():
    pass
"""
        result = list_python_functions(code)
        assert len(result) == 2
        assert result[0]["name"] == "func1"
        assert "func1(x: int) -> str" in result[0]["signature"]
        assert result[0]["arg_count"] == "1"
        assert result[1]["name"] == "func2"

    def test_function_with_docstring(self):
        """Test detection of docstrings."""
        code = '''
def documented():
    """This has a docstring."""
    pass

def undocumented():
    pass
'''
        result = list_python_functions(code)
        assert result[0]["has_docstring"] == "true"
        assert result[1]["has_docstring"] == "false"

    def test_async_function(self):
        """Test detection of async functions."""
        code = """
async def async_func():
    pass

def sync_func():
    pass
"""
        result = list_python_functions(code)
        assert result[0]["is_async"] == "true"
        assert result[1]["is_async"] == "false"

    def test_function_with_decorators(self):
        """Test extraction of decorators."""
        code = """
@property
@staticmethod
def decorated():
    pass
"""
        result = list_python_functions(code)
        decorators = json.loads(result[0]["decorators"])
        assert "property" in decorators
        assert "staticmethod" in decorators

    def test_empty_module(self):
        """Test listing functions in empty module."""
        code = "# Just a comment"
        result = list_python_functions(code)
        assert result == []

    def test_type_error(self):
        """Test TypeError for non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            list_python_functions(123)  # type: ignore[arg-type]


class TestListPythonClasses:
    """Tests for list_python_classes function."""

    def test_list_simple_classes(self):
        """Test listing simple classes."""
        code = """
class Class1:
    def method1(self):
        pass

class Class2:
    pass
"""
        result = list_python_classes(code)
        assert len(result) == 2
        assert result[0]["name"] == "Class1"
        assert result[0]["method_count"] == "1"
        methods = json.loads(result[0]["method_names"])
        assert "method1" in methods

    def test_class_with_inheritance(self):
        """Test extraction of base classes."""
        code = """
class Base:
    pass

class Derived(Base):
    pass

class Multiple(Base, object):
    pass
"""
        result = list_python_classes(code)
        assert len(result) == 3

        derived = result[1]
        bases = json.loads(derived["base_classes"])
        assert "Base" in bases

        multiple = result[2]
        bases = json.loads(multiple["base_classes"])
        assert len(bases) == 2

    def test_class_with_decorators(self):
        """Test extraction of class decorators."""
        code = """
@dataclass
class MyClass:
    pass
"""
        result = list_python_classes(code)
        decorators = json.loads(result[0]["decorators"])
        assert "dataclass" in decorators

    def test_class_docstring(self):
        """Test detection of class docstrings."""
        code = '''
class Documented:
    """Has docstring."""
    pass

class Undocumented:
    pass
'''
        result = list_python_classes(code)
        assert result[0]["has_docstring"] == "true"
        assert result[1]["has_docstring"] == "false"


class TestGetPythonFunctionSignature:
    """Tests for get_python_function_signature function."""

    def test_simple_signature(self):
        """Test extraction of simple signature."""
        code = "def hello(name: str) -> str: return name"
        result = get_python_function_signature(code, "hello")
        assert "hello(name: str) -> str" in result["signature"]
        assert result["arg_count"] == "1"
        assert result["has_return_type"] == "true"

    def test_no_return_type(self):
        """Test function without return type."""
        code = "def process(x): pass"
        result = get_python_function_signature(code, "process")
        assert result["has_return_type"] == "false"

    def test_async_function(self):
        """Test async function detection."""
        code = "async def fetch(): pass"
        result = get_python_function_signature(code, "fetch")
        assert result["is_async"] == "true"

    def test_multiple_parameters(self):
        """Test function with multiple parameters."""
        code = "def calc(x: int, y: int, z: int) -> int: return x + y + z"
        result = get_python_function_signature(code, "calc")
        assert result["arg_count"] == "3"
        assert "x: int" in result["signature"]
        assert "y: int" in result["signature"]
        assert "z: int" in result["signature"]

    def test_function_not_found(self):
        """Test error when function not found."""
        code = "def hello(): pass"
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            get_python_function_signature(code, "missing")


class TestGetPythonFunctionDocstring:
    """Tests for get_python_function_docstring function."""

    def test_function_with_docstring(self):
        """Test extraction of docstring."""
        code = '''
def documented():
    """This is the docstring."""
    pass
'''
        result = get_python_function_docstring(code, "documented")
        assert result["docstring"] == "This is the docstring."
        assert result["has_docstring"] == "true"

    def test_function_without_docstring(self):
        """Test function without docstring."""
        code = "def undocumented(): pass"
        result = get_python_function_docstring(code, "undocumented")
        assert result["docstring"] == ""
        assert result["has_docstring"] == "false"

    def test_multiline_docstring(self):
        """Test multiline docstring extraction."""
        code = '''
def multi():
    """Line 1.

    Line 2.
    Line 3.
    """
    pass
'''
        result = get_python_function_docstring(code, "multi")
        assert "Line 1" in result["docstring"]
        assert "Line 2" in result["docstring"]

    def test_function_not_found(self):
        """Test error when function not found."""
        code = "def hello(): pass"
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            get_python_function_docstring(code, "missing")


class TestListPythonClassMethods:
    """Tests for list_python_class_methods function."""

    def test_simple_methods(self):
        """Test listing simple methods."""
        code = """
class MyClass:
    def __init__(self):
        pass

    def process(self, x: int) -> int:
        return x * 2
"""
        result = list_python_class_methods(code, "MyClass")
        assert len(result) == 2
        assert result[0]["name"] == "__init__"
        assert result[1]["name"] == "process"
        assert "x: int" in result[1]["signature"]

    def test_property_decorator(self):
        """Test detection of @property."""
        code = """
class MyClass:
    @property
    def value(self):
        return self._value
"""
        result = list_python_class_methods(code, "MyClass")
        assert result[0]["is_property"] == "true"

    def test_classmethod_staticmethod(self):
        """Test detection of @classmethod and @staticmethod."""
        code = """
class MyClass:
    @classmethod
    def from_string(cls, s):
        pass

    @staticmethod
    def helper():
        pass
"""
        result = list_python_class_methods(code, "MyClass")
        assert result[0]["is_classmethod"] == "true"
        assert result[1]["is_staticmethod"] == "true"

    def test_async_method(self):
        """Test detection of async methods."""
        code = """
class MyClass:
    async def fetch(self):
        pass
"""
        result = list_python_class_methods(code, "MyClass")
        assert result[0]["is_async"] == "true"

    def test_method_docstrings(self):
        """Test detection of method docstrings."""
        code = '''
class MyClass:
    def documented(self):
        """Has docs."""
        pass

    def undocumented(self):
        pass
'''
        result = list_python_class_methods(code, "MyClass")
        assert result[0]["has_docstring"] == "true"
        assert result[1]["has_docstring"] == "false"

    def test_class_not_found(self):
        """Test error when class not found."""
        code = "class MyClass: pass"
        with pytest.raises(ValueError, match="Class 'Missing' not found"):
            list_python_class_methods(code, "Missing")


class TestExtractPythonPublicApi:
    """Tests for extract_python_public_api function."""

    def test_module_with_all(self):
        """Test extraction when __all__ is defined."""
        code = """
__all__ = ["public_func", "PublicClass"]

def public_func():
    pass

def _private_func():
    pass

class PublicClass:
    pass
"""
        result = extract_python_public_api(code)
        assert result["has_all_defined"] == "true"
        all_contents = json.loads(result["all_contents"])
        assert "public_func" in all_contents
        assert "PublicClass" in all_contents

    def test_module_without_all(self):
        """Test extraction when __all__ is not defined."""
        code = """
def public_func():
    pass

def _private_func():
    pass

class PublicClass:
    pass

class _PrivateClass:
    pass
"""
        result = extract_python_public_api(code)
        assert result["has_all_defined"] == "false"

        public_functions = json.loads(result["public_functions"])
        assert "public_func" in public_functions
        assert "_private_func" not in public_functions

        public_classes = json.loads(result["public_classes"])
        assert "PublicClass" in public_classes
        assert "_PrivateClass" not in public_classes

    def test_empty_module(self):
        """Test extraction from empty module."""
        code = "# Just comments"
        result = extract_python_public_api(code)
        assert result["has_all_defined"] == "false"
        assert json.loads(result["public_functions"]) == []
        assert json.loads(result["public_classes"]) == []


class TestGetPythonFunctionDetails:
    """Tests for get_python_function_details function."""

    def test_complete_details(self):
        """Test extraction of all function details."""
        code = '''
@decorator1
@decorator2
def process(x: int, y: str) -> dict[str, str]:
    """Process data.

    Args:
        x: Number
        y: String

    Returns:
        Dictionary result
    """
    return {"x": str(x), "y": y}
'''
        result = get_python_function_details(code, "process")
        assert result["function_name"] == "process"
        assert "x: int" in result["signature"]
        assert "y: str" in result["signature"]
        assert "-> dict[str, str]" in result["signature"]
        assert "Process data" in result["docstring"]
        assert result["arg_count"] == "2"
        assert result["has_return_type"] == "true"
        assert result["has_docstring"] == "true"
        assert result["is_async"] == "false"

        decorators = json.loads(result["decorators"])
        assert len(decorators) == 2

    def test_minimal_function(self):
        """Test details for minimal function."""
        code = "def simple(): pass"
        result = get_python_function_details(code, "simple")
        assert result["function_name"] == "simple"
        assert result["arg_count"] == "0"
        assert result["has_return_type"] == "false"
        assert result["has_docstring"] == "false"
        assert json.loads(result["decorators"]) == []

    def test_async_function_details(self):
        """Test details for async function."""
        code = "async def fetch(): pass"
        result = get_python_function_details(code, "fetch")
        assert result["is_async"] == "true"

    def test_function_not_found(self):
        """Test error when function not found."""
        code = "def hello(): pass"
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            get_python_function_details(code, "missing")


class TestGetPythonFunctionBody:
    """Tests for get_python_function_body function."""

    def test_simple_function_body(self):
        """Test extraction of simple function body."""
        code = """def hello():
    return "world"
"""
        result = get_python_function_body(code, "hello")
        assert "return" in result["body"]
        assert result["function_name"] == "hello"

    def test_multiline_function_body(self):
        """Test extraction of multiline function body."""
        code = """
def process(x):
    result = x * 2
    result += 1
    return result
"""
        result = get_python_function_body(code, "process")
        assert "result = x * 2" in result["body"]
        assert "result += 1" in result["body"]

    def test_function_not_found(self):
        """Test error when function not found."""
        code = "def hello(): pass"
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            get_python_function_body(code, "missing")


class TestListPythonFunctionCalls:
    """Tests for list_python_function_calls function."""

    def test_function_with_calls(self):
        """Test listing function calls."""
        code = """
def process():
    validate()
    transform()
    save()
"""
        result = list_python_function_calls(code, "process")
        calls = json.loads(result["calls"])
        assert "validate" in calls
        assert "transform" in calls
        assert "save" in calls
        assert int(result["call_count"]) >= 3

    def test_function_with_method_calls(self):
        """Test detection of method calls."""
        code = """
def process(data):
    data.validate()
    data.transform()
"""
        result = list_python_function_calls(code, "process")
        calls = json.loads(result["calls"])
        assert "validate" in calls
        assert "transform" in calls

    def test_function_with_no_calls(self):
        """Test function with no calls."""
        code = """
def simple():
    x = 1
    return x
"""
        result = list_python_function_calls(code, "simple")
        assert result["call_count"] == "0"

    def test_function_not_found(self):
        """Test error when function not found."""
        code = "def hello(): pass"
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            list_python_function_calls(code, "missing")


class TestFindPythonFunctionUsages:
    """Tests for find_python_function_usages function."""

    def test_find_usages(self):
        """Test finding function usages."""
        code = """
def helper():
    pass

def main():
    helper()
    helper()

def other():
    helper()
"""
        result = find_python_function_usages(code, "helper")
        assert int(result["usage_count"]) == 3
        usages = json.loads(result["usages"])
        assert len(usages) == 3

    def test_no_usages(self):
        """Test function with no usages."""
        code = """
def unused():
    pass

def main():
    pass
"""
        result = find_python_function_usages(code, "unused")
        assert result["usage_count"] == "0"

    def test_usage_details(self):
        """Test usage details include calling function."""
        code = """
def helper():
    pass

def main():
    helper()
"""
        result = find_python_function_usages(code, "helper")
        details = json.loads(result["usage_details"])
        assert len(details) > 0
        assert details[0]["calling_function"] == "main"


class TestGetPythonMethodLineNumbers:
    """Tests for get_python_method_line_numbers function."""

    def test_find_method(self):
        """Test finding method in class."""
        code = """
class MyClass:
    def __init__(self):
        pass

    def process(self):
        return True
"""
        result = get_python_method_line_numbers(code, "MyClass", "process")
        assert result["class_name"] == "MyClass"
        assert result["method_name"] == "process"
        assert int(result["start_line"]) > 0

    def test_method_not_found(self):
        """Test error when method not found."""
        code = """
class MyClass:
    def exists(self):
        pass
"""
        with pytest.raises(ValueError, match="Method 'missing' not found"):
            get_python_method_line_numbers(code, "MyClass", "missing")

    def test_class_not_found(self):
        """Test error when class not found."""
        code = "class MyClass: pass"
        with pytest.raises(ValueError, match="Class 'Missing' not found"):
            get_python_method_line_numbers(code, "Missing", "method")


class TestGetPythonClassHierarchy:
    """Tests for get_python_class_hierarchy function."""

    def test_class_with_inheritance(self):
        """Test class with base classes."""
        code = """
class Base:
    pass

class Derived(Base):
    pass
"""
        result = get_python_class_hierarchy(code, "Derived")
        assert result["has_inheritance"] == "true"
        bases = json.loads(result["base_classes"])
        assert "Base" in bases
        assert result["base_count"] == "1"

    def test_class_without_inheritance(self):
        """Test class without base classes."""
        code = """
class Standalone:
    pass
"""
        result = get_python_class_hierarchy(code, "Standalone")
        assert result["has_inheritance"] == "false"
        assert result["base_count"] == "0"

    def test_multiple_inheritance(self):
        """Test class with multiple base classes."""
        code = """
class Base1:
    pass

class Base2:
    pass

class Derived(Base1, Base2):
    pass
"""
        result = get_python_class_hierarchy(code, "Derived")
        bases = json.loads(result["base_classes"])
        assert len(bases) == 2
        assert "Base1" in bases
        assert "Base2" in bases


class TestFindPythonDefinitionsByDecorator:
    """Tests for find_python_definitions_by_decorator function."""

    def test_find_functions_with_decorator(self):
        """Test finding functions with specific decorator."""
        code = """
@property
def prop1():
    pass

@property
def prop2():
    pass

def regular():
    pass
"""
        result = find_python_definitions_by_decorator(code, "property")
        functions = json.loads(result["functions"])
        assert len(functions) == 2
        assert "prop1" in functions
        assert "prop2" in functions
        assert result["total_count"] == "2"

    def test_find_classes_with_decorator(self):
        """Test finding classes with specific decorator."""
        code = """
@dataclass
class MyClass1:
    pass

@dataclass
class MyClass2:
    pass
"""
        result = find_python_definitions_by_decorator(code, "dataclass")
        classes = json.loads(result["classes"])
        assert len(classes) == 2
        assert "MyClass1" in classes
        assert "MyClass2" in classes

    def test_no_matches(self):
        """Test when no definitions have the decorator."""
        code = """
def regular():
    pass

class RegularClass:
    pass
"""
        result = find_python_definitions_by_decorator(code, "nonexistent")
        assert result["total_count"] == "0"
        assert json.loads(result["functions"]) == []
        assert json.loads(result["classes"]) == []


class TestGetPythonClassDocstring:
    """Tests for get_python_class_docstring function."""

    def test_class_with_docstring(self):
        """Test extraction of class docstring."""
        code = '''
class MyClass:
    """This is a class docstring."""
    pass
'''
        result = get_python_class_docstring(code, "MyClass")
        assert result["docstring"] == "This is a class docstring."
        assert result["has_docstring"] == "true"
        assert result["class_name"] == "MyClass"

    def test_class_without_docstring(self):
        """Test class without docstring."""
        code = """
class MyClass:
    pass
"""
        result = get_python_class_docstring(code, "MyClass")
        assert result["docstring"] == ""
        assert result["has_docstring"] == "false"

    def test_class_not_found(self):
        """Test error when class not found."""
        code = "class MyClass: pass"
        with pytest.raises(ValueError, match="Class 'Missing' not found"):
            get_python_class_docstring(code, "Missing")
