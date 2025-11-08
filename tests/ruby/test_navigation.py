"""Basic tests for Ruby navigation module.

These tests verify core functionality of all 17 Ruby navigation functions.
"""


from coding_open_agent_tools.ruby.navigation import (
    extract_ruby_public_api,
    find_ruby_definitions_by_comment,
    find_ruby_function_usages,
    get_ruby_function_body,
    get_ruby_function_details,
    get_ruby_function_docstring,
    get_ruby_function_line_numbers,
    get_ruby_function_signature,
    get_ruby_module_overview,
    get_ruby_specific_function_line_numbers,
    get_ruby_type_docstring,
    get_ruby_type_hierarchy,
    get_ruby_type_line_numbers,
    list_ruby_function_calls,
    list_ruby_functions,
    list_ruby_type_methods,
    list_ruby_types,
)


class TestRubyNavigationBasics:
    """Test basic Ruby navigation functions."""

    def test_get_ruby_function_line_numbers(self) -> None:
        """Test finding method line numbers."""
        code = """# Add two numbers
def add(a, b)
  a + b
end"""
        result = get_ruby_function_line_numbers(code, "add")
        assert result["found"] == "true"
        assert result["function_name"] == "add"
        assert "start_line" in result
        assert "end_line" in result

    def test_get_ruby_type_line_numbers(self) -> None:
        """Test finding class line numbers."""
        code = """# Calculator class
class Calculator
  def add(a, b)
    a + b
  end
end"""
        result = get_ruby_type_line_numbers(code, "Calculator")
        assert result["found"] == "true"
        assert result["type_name"] == "Calculator"

    def test_get_ruby_module_overview(self) -> None:
        """Test getting module overview."""
        code = """class Calculator
  def add(a, b)
    a + b
  end
end"""
        result = get_ruby_module_overview(code)
        assert result["found"] == "true"
        assert "overview" in result
        assert "Calculator" in result["overview"]

    def test_list_ruby_functions(self) -> None:
        """Test listing all methods."""
        code = """class Math
  def add(a, b)
    a + b
  end

  def subtract(a, b)
    a - b
  end
end"""
        result = list_ruby_functions(code)
        assert result["found"] == "true"
        assert "functions" in result
        assert "add" in result["functions"]
        assert "subtract" in result["functions"]

    def test_list_ruby_types(self) -> None:
        """Test listing all classes."""
        code = """class User
  attr_reader :name
end

class Product
  attr_reader :title
end"""
        result = list_ruby_types(code)
        assert result["found"] == "true"
        assert "types" in result
        assert "User" in result["types"]
        assert "Product" in result["types"]

    def test_get_ruby_function_signature(self) -> None:
        """Test getting method signature."""
        code = """def add(a, b)
  a + b
end"""
        result = get_ruby_function_signature(code, "add")
        assert result["found"] == "true"
        assert result["function_name"] == "add"
        assert "signature" in result

    def test_get_ruby_function_docstring(self) -> None:
        """Test getting method documentation."""
        code = """# Add two numbers
def add(a, b)
  a + b
end"""
        result = get_ruby_function_docstring(code, "add")
        assert result["found"] == "true"
        assert "Add two numbers" in result["docstring"]

    def test_list_ruby_type_methods(self) -> None:
        """Test listing methods of a class."""
        code = """class Calculator
  def add(a, b)
    a + b
  end

  def subtract(a, b)
    a - b
  end
end"""
        result = list_ruby_type_methods(code, "Calculator")
        assert result["found"] == "true"
        assert "add" in result["methods"]
        assert "subtract" in result["methods"]

    def test_extract_ruby_public_api(self) -> None:
        """Test extracting public API."""
        code = """class Calculator
  def add(a, b)
    a + b
  end

  private
  def internal_helper
    # helper
  end
end"""
        result = extract_ruby_public_api(code)
        assert result["found"] == "true"
        assert "add" in result["api"]
        assert "internal_helper" not in result["api"]

    def test_get_ruby_function_details(self) -> None:
        """Test getting complete method details."""
        code = """# Add two numbers
def add(a, b)
  a + b
end"""
        result = get_ruby_function_details(code, "add")
        assert result["found"] == "true"
        assert result["function_name"] == "add"
        assert "signature" in result
        assert "docstring" in result

    def test_get_ruby_function_body(self) -> None:
        """Test getting method body."""
        code = """def add(a, b)
  a + b
end"""
        result = get_ruby_function_body(code, "add")
        assert result["found"] == "true"
        assert "a + b" in result["body"]

    def test_list_ruby_function_calls(self) -> None:
        """Test listing function calls."""
        code = """def process(x, y)
  sum = add(x, y)
  multiply(sum, 2)
end"""
        result = list_ruby_function_calls(code, "process")
        assert result["found"] == "true"
        assert "calls" in result

    def test_find_ruby_function_usages(self) -> None:
        """Test finding method usages."""
        code = """def add(a, b)
  a + b
end

def calculate(x, y)
  add(x, y)
end"""
        result = find_ruby_function_usages(code, "add")
        assert result["found"] == "true"
        assert "usage_count" in result

    def test_get_ruby_specific_function_line_numbers(self) -> None:
        """Test finding method in specific class."""
        code = """class MathA
  def add(a, b)
    a + b
  end
end

class MathB
  def add(a, b)
    a + b + 1
  end
end"""
        result = get_ruby_specific_function_line_numbers(code, "MathB", "add")
        assert result["found"] == "true"
        assert result["function_name"] == "add"

    def test_get_ruby_type_hierarchy(self) -> None:
        """Test getting type hierarchy."""
        code = """class Animal
end

class Dog < Animal
end"""
        result = get_ruby_type_hierarchy(code, "Dog")
        assert result["found"] == "true"
        assert "Animal" in result["base_types"]

    def test_find_ruby_definitions_by_comment(self) -> None:
        """Test finding definitions by comment."""
        code = """# Calculate sum of two numbers
def add(a, b)
  a + b
end

# Calculate product
def multiply(a, b)
  a * b
end"""
        result = find_ruby_definitions_by_comment(code, "sum")
        assert result["found"] == "true"
        assert "add" in result["definitions"]

    def test_get_ruby_type_docstring(self) -> None:
        """Test getting class documentation."""
        code = """# User management class
class User
  attr_reader :name
end"""
        result = get_ruby_type_docstring(code, "User")
        assert result["found"] == "true"
        assert "User management" in result["docstring"]


class TestRubyNavigationEdgeCases:
    """Test edge cases and error handling."""

    def test_method_not_found(self) -> None:
        """Test method not found."""
        code = """def add(a, b)
  a + b
end"""
        result = get_ruby_function_line_numbers(code, "subtract")
        assert result["found"] == "false"
        assert "error" in result

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = get_ruby_function_line_numbers("", "add")
        assert result["found"] == "false"

    def test_type_not_found(self) -> None:
        """Test type not found."""
        code = """class User
end"""
        result = get_ruby_type_line_numbers(code, "Product")
        assert result["found"] == "false"

    def test_module_support(self) -> None:
        """Test module (not just class) support."""
        code = """module Helpers
  def self.format(value)
    value.to_s
  end
end"""
        result = get_ruby_type_line_numbers(code, "Helpers")
        assert result["found"] == "true"
        assert result["type_name"] == "Helpers"
