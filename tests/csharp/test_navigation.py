"""Tests for C# navigation module.

This module tests all 17 C# navigation functions with comprehensive test coverage.
Total: 75+ tests across 17 test classes.
"""


from coding_open_agent_tools.csharp.navigation import (
    extract_csharp_public_api,
    find_csharp_definitions_by_comment,
    find_csharp_function_usages,
    get_csharp_function_body,
    get_csharp_function_details,
    get_csharp_function_docstring,
    get_csharp_function_line_numbers,
    get_csharp_function_signature,
    get_csharp_module_overview,
    get_csharp_specific_function_line_numbers,
    get_csharp_type_docstring,
    get_csharp_type_hierarchy,
    get_csharp_type_line_numbers,
    list_csharp_function_calls,
    list_csharp_functions,
    list_csharp_type_methods,
    list_csharp_types,
)


class TestGetCSharpFunctionLineNumbers:
    """Test get_csharp_function_line_numbers function."""

    def test_simple_method(self) -> None:
        """Test finding line numbers for a simple method."""
        code = """/// <summary>Calculate sum</summary>
public int Add(int a, int b) {
    return a + b;
}"""
        result = get_csharp_function_line_numbers(code, "Add")
        assert result["found"] == "true"
        assert result["start_line"] == "2"
        assert result["end_line"] == "4"
        assert result["function_name"] == "Add"

    def test_method_in_class(self) -> None:
        """Test finding method inside a class."""
        code = """public class Calculator {
    /// <summary>Calculate sum</summary>
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_function_line_numbers(code, "Add")
        assert result["found"] == "true"
        assert result["start_line"] == "3"
        assert result["end_line"] == "5"

    def test_private_method(self) -> None:
        """Test finding private method."""
        code = """public class Helper {
    private void DoWork() {
        Console.WriteLine("Working");
    }
}"""
        result = get_csharp_function_line_numbers(code, "DoWork")
        assert result["found"] == "true"
        assert result["start_line"] == "2"

    def test_method_not_found(self) -> None:
        """Test method not found."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_function_line_numbers(code, "Subtract")
        assert result["found"] == "false"
        assert "not found" in result["error"].lower()

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = get_csharp_function_line_numbers("", "Add")
        assert result["found"] == "false"


class TestGetCSharpTypeLineNumbers:
    """Test get_csharp_type_line_numbers function."""

    def test_simple_class(self) -> None:
        """Test finding line numbers for a simple class."""
        code = """/// <summary>User class</summary>
public class User {
    public string Name { get; set; }
}"""
        result = get_csharp_type_line_numbers(code, "User")
        assert result["found"] == "true"
        assert result["start_line"] == "2"
        assert result["end_line"] == "4"
        assert result["type_name"] == "User"

    def test_interface(self) -> None:
        """Test finding interface."""
        code = """/// <summary>Repository interface</summary>
public interface IRepository {
    void Save();
}"""
        result = get_csharp_type_line_numbers(code, "IRepository")
        assert result["found"] == "true"
        assert result["start_line"] == "2"

    def test_struct(self) -> None:
        """Test finding struct."""
        code = """public struct Point {
    public int X { get; set; }
    public int Y { get; set; }
}"""
        result = get_csharp_type_line_numbers(code, "Point")
        assert result["found"] == "true"
        assert result["start_line"] == "1"
        assert result["end_line"] == "4"

    def test_enum(self) -> None:
        """Test finding enum."""
        code = """public enum Status {
    Active,
    Inactive
}"""
        result = get_csharp_type_line_numbers(code, "Status")
        assert result["found"] == "true"
        assert result["start_line"] == "1"

    def test_type_not_found(self) -> None:
        """Test type not found."""
        code = """public class User {
    public string Name { get; set; }
}"""
        result = get_csharp_type_line_numbers(code, "Product")
        assert result["found"] == "false"
        assert "not found" in result["error"].lower()

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = get_csharp_type_line_numbers("", "User")
        assert result["found"] == "false"


class TestGetCSharpModuleOverview:
    """Test get_csharp_module_overview function."""

    def test_simple_module(self) -> None:
        """Test overview of simple module."""
        code = """/// <summary>Calculator class</summary>
public class Calculator {
    /// <summary>Add two numbers</summary>
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_module_overview(code)
        assert "Calculator" in result["overview"]
        assert "Add" in result["overview"]
        assert "class_count" in result
        assert result["class_count"] == "1"

    def test_multiple_types(self) -> None:
        """Test module with multiple types."""
        code = """public class User {
    public string Name { get; set; }
}

public interface IRepository {
    void Save();
}

public enum Status {
    Active
}"""
        result = get_csharp_module_overview(code)
        assert "User" in result["overview"]
        assert "IRepository" in result["overview"]
        assert "Status" in result["overview"]

    def test_empty_module(self) -> None:
        """Test empty module."""
        result = get_csharp_module_overview("")
        assert result["overview"] == ""
        assert result["class_count"] == "0"

    def test_with_namespace(self) -> None:
        """Test module with namespace."""
        code = """namespace MyApp.Models {
    public class User {
        public string Name { get; set; }
    }
}"""
        result = get_csharp_module_overview(code)
        assert "User" in result["overview"]


class TestListCSharpFunctions:
    """Test list_csharp_functions function."""

    def test_simple_functions(self) -> None:
        """Test listing simple functions."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }

    public int Subtract(int a, int b) {
        return a - b;
    }
}"""
        result = list_csharp_functions(code)
        functions = result["functions"].split(", ")
        assert "Add" in functions
        assert "Subtract" in functions
        assert result["count"] == "2"

    def test_mixed_visibility(self) -> None:
        """Test listing functions with mixed visibility."""
        code = """public class Helper {
    public void PublicMethod() { }
    private void PrivateMethod() { }
    protected void ProtectedMethod() { }
}"""
        result = list_csharp_functions(code)
        functions = result["functions"].split(", ")
        assert "PublicMethod" in functions
        assert "PrivateMethod" in functions
        assert "ProtectedMethod" in functions
        assert result["count"] == "3"

    def test_no_functions(self) -> None:
        """Test module with no functions."""
        code = """public class Empty {
}"""
        result = list_csharp_functions(code)
        assert result["functions"] == ""
        assert result["count"] == "0"

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = list_csharp_functions("")
        assert result["functions"] == ""
        assert result["count"] == "0"


class TestListCSharpTypes:
    """Test list_csharp_types function."""

    def test_simple_types(self) -> None:
        """Test listing simple types."""
        code = """public class User {
    public string Name { get; set; }
}

public class Product {
    public string Title { get; set; }
}"""
        result = list_csharp_types(code)
        types = result["types"].split(", ")
        assert "User" in types
        assert "Product" in types
        assert result["count"] == "2"

    def test_mixed_types(self) -> None:
        """Test listing mixed type kinds."""
        code = """public class User { }
public interface IRepository { }
public struct Point { }
public enum Status { Active }"""
        result = list_csharp_types(code)
        types = result["types"].split(", ")
        assert "User" in types
        assert "IRepository" in types
        assert "Point" in types
        assert "Status" in types

    def test_no_types(self) -> None:
        """Test code with no types."""
        code = """// Just a comment"""
        result = list_csharp_types(code)
        assert result["types"] == ""
        assert result["count"] == "0"

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = list_csharp_types("")
        assert result["types"] == ""
        assert result["count"] == "0"


class TestGetCSharpFunctionSignature:
    """Test get_csharp_function_signature function."""

    def test_simple_method(self) -> None:
        """Test getting signature of simple method."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_function_signature(code, "Add")
        assert result["found"] == "true"
        assert "int Add" in result["signature"]
        assert "int a" in result["signature"]
        assert "int b" in result["signature"]

    def test_void_method(self) -> None:
        """Test getting signature of void method."""
        code = """public class Logger {
    public void Log(string message) {
        Console.WriteLine(message);
    }
}"""
        result = get_csharp_function_signature(code, "Log")
        assert result["found"] == "true"
        assert "void Log" in result["signature"]
        assert "string message" in result["signature"]

    def test_private_method(self) -> None:
        """Test getting signature of private method."""
        code = """public class Helper {
    private bool IsValid(string input) {
        return !string.IsNullOrEmpty(input);
    }
}"""
        result = get_csharp_function_signature(code, "IsValid")
        assert result["found"] == "true"
        assert "bool IsValid" in result["signature"]

    def test_method_not_found(self) -> None:
        """Test method not found."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_function_signature(code, "Subtract")
        assert result["found"] == "false"

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = get_csharp_function_signature("", "Add")
        assert result["found"] == "false"


class TestGetCSharpFunctionDocstring:
    """Test get_csharp_function_docstring function."""

    def test_method_with_xml_doc(self) -> None:
        """Test getting XML documentation comment."""
        code = """public class Math {
    /// <summary>Calculate sum of two numbers</summary>
    /// <param name="a">First number</param>
    /// <param name="b">Second number</param>
    /// <returns>Sum of a and b</returns>
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_function_docstring(code, "Add")
        assert result["found"] == "true"
        assert "Calculate sum" in result["docstring"]
        assert "First number" in result["docstring"]
        assert "Second number" in result["docstring"]

    def test_method_without_doc(self) -> None:
        """Test method without documentation."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_function_docstring(code, "Add")
        assert result["found"] == "true"
        assert result["docstring"] == ""

    def test_method_with_single_line_doc(self) -> None:
        """Test method with single line doc."""
        code = """public class Math {
    /// <summary>Add two numbers</summary>
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_function_docstring(code, "Add")
        assert result["found"] == "true"
        assert "Add two numbers" in result["docstring"]

    def test_method_not_found(self) -> None:
        """Test method not found."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_function_docstring(code, "Subtract")
        assert result["found"] == "false"

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = get_csharp_function_docstring("", "Add")
        assert result["found"] == "false"


class TestListCSharpTypeMethods:
    """Test list_csharp_type_methods function."""

    def test_class_methods(self) -> None:
        """Test listing methods of a class."""
        code = """public class User {
    public string GetName() {
        return Name;
    }

    public void SetName(string name) {
        Name = name;
    }
}"""
        result = list_csharp_type_methods(code, "User")
        assert result["found"] == "true"
        methods = result["methods"].split(", ")
        assert "GetName" in methods
        assert "SetName" in methods
        assert result["count"] == "2"

    def test_interface_methods(self) -> None:
        """Test listing methods of an interface."""
        code = """public interface IRepository {
    void Save();
    void Delete();
    void Update();
}"""
        result = list_csharp_type_methods(code, "IRepository")
        assert result["found"] == "true"
        methods = result["methods"].split(", ")
        assert "Save" in methods
        assert "Delete" in methods
        assert "Update" in methods

    def test_type_with_no_methods(self) -> None:
        """Test type with no methods."""
        code = """public class Empty {
}"""
        result = list_csharp_type_methods(code, "Empty")
        assert result["found"] == "true"
        assert result["methods"] == ""
        assert result["count"] == "0"

    def test_type_not_found(self) -> None:
        """Test type not found."""
        code = """public class User {
    public string GetName() {
        return Name;
    }
}"""
        result = list_csharp_type_methods(code, "Product")
        assert result["found"] == "false"

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = list_csharp_type_methods("", "User")
        assert result["found"] == "false"


class TestExtractCSharpPublicAPI:
    """Test extract_csharp_public_api function."""

    def test_public_class_and_methods(self) -> None:
        """Test extracting public API."""
        code = """public class Calculator {
    public int Add(int a, int b) {
        return a + b;
    }

    private int Subtract(int a, int b) {
        return a - b;
    }

    public int Multiply(int a, int b) {
        return a * b;
    }
}"""
        result = extract_csharp_public_api(code)
        assert "Calculator" in result["api"]
        assert "Add" in result["api"]
        assert "Multiply" in result["api"]
        assert "Subtract" not in result["api"]

    def test_multiple_public_types(self) -> None:
        """Test extracting multiple public types."""
        code = """public class User {
    public string GetName() { return Name; }
}

public interface IRepository {
    void Save();
}

internal class Helper {
    public void Work() { }
}"""
        result = extract_csharp_public_api(code)
        assert "User" in result["api"]
        assert "GetName" in result["api"]
        assert "IRepository" in result["api"]
        assert "Helper" not in result["api"]

    def test_public_properties(self) -> None:
        """Test extracting public properties."""
        code = """public class User {
    public string Name { get; set; }
    private int Age { get; set; }
}"""
        result = extract_csharp_public_api(code)
        assert "User" in result["api"]
        assert "Name" in result["api"]

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = extract_csharp_public_api("")
        assert result["api"] == ""


class TestGetCSharpFunctionDetails:
    """Test get_csharp_function_details function."""

    def test_method_details(self) -> None:
        """Test getting complete method details."""
        code = """public class Math {
    /// <summary>Calculate sum</summary>
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_function_details(code, "Add")
        assert result["found"] == "true"
        assert result["name"] == "Add"
        assert "int Add" in result["signature"]
        assert "Calculate sum" in result["docstring"]
        assert result["start_line"] == "3"

    def test_private_method_details(self) -> None:
        """Test getting private method details."""
        code = """public class Helper {
    private void DoWork() {
        Console.WriteLine("Working");
    }
}"""
        result = get_csharp_function_details(code, "DoWork")
        assert result["found"] == "true"
        assert result["name"] == "DoWork"
        assert "void DoWork" in result["signature"]

    def test_method_not_found(self) -> None:
        """Test method not found."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_function_details(code, "Subtract")
        assert result["found"] == "false"

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = get_csharp_function_details("", "Add")
        assert result["found"] == "false"


class TestGetCSharpFunctionBody:
    """Test get_csharp_function_body function."""

    def test_simple_method_body(self) -> None:
        """Test getting method body."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_function_body(code, "Add")
        assert result["found"] == "true"
        assert "return a + b" in result["body"]

    def test_multiline_method_body(self) -> None:
        """Test getting multiline method body."""
        code = """public class Logger {
    public void Log(string message) {
        var timestamp = DateTime.Now;
        Console.WriteLine($"{timestamp}: {message}");
    }
}"""
        result = get_csharp_function_body(code, "Log")
        assert result["found"] == "true"
        assert "timestamp" in result["body"]
        assert "Console.WriteLine" in result["body"]

    def test_method_with_nested_blocks(self) -> None:
        """Test method with nested blocks."""
        code = """public class Validator {
    public bool Validate(int value) {
        if (value > 0) {
            return true;
        } else {
            return false;
        }
    }
}"""
        result = get_csharp_function_body(code, "Validate")
        assert result["found"] == "true"
        assert "if (value > 0)" in result["body"]

    def test_method_not_found(self) -> None:
        """Test method not found."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_function_body(code, "Subtract")
        assert result["found"] == "false"

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = get_csharp_function_body("", "Add")
        assert result["found"] == "false"


class TestListCSharpFunctionCalls:
    """Test list_csharp_function_calls function."""

    def test_method_with_calls(self) -> None:
        """Test listing function calls in a method."""
        code = """public class Calculator {
    public int Process(int a, int b) {
        var sum = Add(a, b);
        var product = Multiply(a, b);
        return Combine(sum, product);
    }
}"""
        result = list_csharp_function_calls(code, "Process")
        assert result["found"] == "true"
        calls = result["calls"].split(", ")
        assert "Add" in calls
        assert "Multiply" in calls
        assert "Combine" in calls

    def test_method_with_system_calls(self) -> None:
        """Test method calling system methods."""
        code = """public class Logger {
    public void Log(string message) {
        Console.WriteLine(message);
        File.WriteAllText("log.txt", message);
    }
}"""
        result = list_csharp_function_calls(code, "Log")
        assert result["found"] == "true"
        assert "WriteLine" in result["calls"] or "Console.WriteLine" in result["calls"]

    def test_method_with_no_calls(self) -> None:
        """Test method with no function calls."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = list_csharp_function_calls(code, "Add")
        assert result["found"] == "true"
        assert result["count"] == "0"

    def test_method_not_found(self) -> None:
        """Test method not found."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = list_csharp_function_calls(code, "Subtract")
        assert result["found"] == "false"

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = list_csharp_function_calls("", "Process")
        assert result["found"] == "false"


class TestFindCSharpFunctionUsages:
    """Test find_csharp_function_usages function."""

    def test_function_with_usages(self) -> None:
        """Test finding function usages."""
        code = """public class Calculator {
    public int Add(int a, int b) {
        return a + b;
    }

    public int Calculate(int x, int y) {
        return Add(x, y);
    }

    public int Process(int m, int n) {
        var result = Add(m, n);
        return result * 2;
    }
}"""
        result = find_csharp_function_usages(code, "Add")
        assert result["found"] == "true"
        assert int(result["count"]) >= 2

    def test_function_with_no_usages(self) -> None:
        """Test function with no usages."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }

    public int Subtract(int a, int b) {
        return a - b;
    }
}"""
        result = find_csharp_function_usages(code, "Add")
        assert result["found"] == "true"
        assert result["count"] == "0"

    def test_function_not_found(self) -> None:
        """Test function not found."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = find_csharp_function_usages(code, "Multiply")
        assert result["found"] == "false"

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = find_csharp_function_usages("", "Add")
        assert result["found"] == "false"


class TestGetCSharpSpecificFunctionLineNumbers:
    """Test get_csharp_specific_function_line_numbers function."""

    def test_specific_method_in_class(self) -> None:
        """Test finding specific method in specific class."""
        code = """public class MathA {
    public int Add(int a, int b) {
        return a + b;
    }
}

public class MathB {
    public int Add(int a, int b) {
        return a + b + 1;
    }
}"""
        result = get_csharp_specific_function_line_numbers(code, "MathB", "Add")
        assert result["found"] == "true"
        assert result["start_line"] == "8"

    def test_method_in_nested_class(self) -> None:
        """Test finding method in nested class."""
        code = """public class Outer {
    public class Inner {
        public void Work() {
            Console.WriteLine("Working");
        }
    }
}"""
        result = get_csharp_specific_function_line_numbers(code, "Inner", "Work")
        assert result["found"] == "true"
        assert result["start_line"] == "3"

    def test_wrong_class(self) -> None:
        """Test with wrong class name."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_specific_function_line_numbers(code, "Calculator", "Add")
        assert result["found"] == "false"

    def test_wrong_method(self) -> None:
        """Test with wrong method name."""
        code = """public class Math {
    public int Add(int a, int b) {
        return a + b;
    }
}"""
        result = get_csharp_specific_function_line_numbers(code, "Math", "Subtract")
        assert result["found"] == "false"

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = get_csharp_specific_function_line_numbers("", "Math", "Add")
        assert result["found"] == "false"


class TestGetCSharpTypeHierarchy:
    """Test get_csharp_type_hierarchy function."""

    def test_class_with_base_class(self) -> None:
        """Test class with base class."""
        code = """public class Animal {
    public void Eat() { }
}

public class Dog : Animal {
    public void Bark() { }
}"""
        result = get_csharp_type_hierarchy(code, "Dog")
        assert result["found"] == "true"
        assert "Animal" in result["base_types"]

    def test_class_with_interface(self) -> None:
        """Test class implementing interface."""
        code = """public interface IDisposable {
    void Dispose();
}

public class Resource : IDisposable {
    public void Dispose() { }
}"""
        result = get_csharp_type_hierarchy(code, "Resource")
        assert result["found"] == "true"
        assert "IDisposable" in result["base_types"]

    def test_class_with_multiple_interfaces(self) -> None:
        """Test class implementing multiple interfaces."""
        code = """public interface IReadable {
    void Read();
}

public interface IWritable {
    void Write();
}

public class File : IReadable, IWritable {
    public void Read() { }
    public void Write() { }
}"""
        result = get_csharp_type_hierarchy(code, "File")
        assert result["found"] == "true"
        assert "IReadable" in result["base_types"]
        assert "IWritable" in result["base_types"]

    def test_class_with_no_base(self) -> None:
        """Test class with no base types."""
        code = """public class Simple {
    public void Work() { }
}"""
        result = get_csharp_type_hierarchy(code, "Simple")
        assert result["found"] == "true"
        assert result["base_types"] == ""

    def test_type_not_found(self) -> None:
        """Test type not found."""
        code = """public class User {
    public string Name { get; set; }
}"""
        result = get_csharp_type_hierarchy(code, "Product")
        assert result["found"] == "false"

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = get_csharp_type_hierarchy("", "Dog")
        assert result["found"] == "false"


class TestFindCSharpDefinitionsByComment:
    """Test find_csharp_definitions_by_comment function."""

    def test_find_by_xml_doc_comment(self) -> None:
        """Test finding definitions by XML doc comment."""
        code = """public class Calculator {
    /// <summary>Calculate sum of two numbers</summary>
    public int Add(int a, int b) {
        return a + b;
    }

    /// <summary>Calculate product of two numbers</summary>
    public int Multiply(int a, int b) {
        return a * b;
    }
}"""
        result = find_csharp_definitions_by_comment(code, "sum")
        assert result["found"] == "true"
        assert "Add" in result["definitions"]
        assert int(result["count"]) >= 1

    def test_find_class_by_comment(self) -> None:
        """Test finding class by documentation comment."""
        code = """/// <summary>Represents a user in the system</summary>
public class User {
    public string Name { get; set; }
}

/// <summary>Represents a product</summary>
public class Product {
    public string Title { get; set; }
}"""
        result = find_csharp_definitions_by_comment(code, "user")
        assert result["found"] == "true"
        assert "User" in result["definitions"]

    def test_find_with_no_matches(self) -> None:
        """Test finding with no matches."""
        code = """/// <summary>Calculate sum</summary>
public int Add(int a, int b) {
    return a + b;
}"""
        result = find_csharp_definitions_by_comment(code, "database")
        assert result["found"] == "true"
        assert result["count"] == "0"

    def test_case_insensitive_search(self) -> None:
        """Test case insensitive search."""
        code = """/// <summary>USER management class</summary>
public class UserManager {
    public void AddUser() { }
}"""
        result = find_csharp_definitions_by_comment(code, "user")
        assert result["found"] == "true"
        assert "UserManager" in result["definitions"]

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = find_csharp_definitions_by_comment("", "user")
        assert result["found"] == "true"
        assert result["count"] == "0"


class TestGetCSharpTypeDocstring:
    """Test get_csharp_type_docstring function."""

    def test_class_with_xml_doc(self) -> None:
        """Test getting class XML documentation."""
        code = """/// <summary>Represents a user in the system</summary>
/// <remarks>This class handles user data and authentication</remarks>
public class User {
    public string Name { get; set; }
}"""
        result = get_csharp_type_docstring(code, "User")
        assert result["found"] == "true"
        assert "user in the system" in result["docstring"]
        assert "authentication" in result["docstring"]

    def test_interface_with_doc(self) -> None:
        """Test getting interface documentation."""
        code = """/// <summary>Repository pattern interface</summary>
public interface IRepository {
    void Save();
}"""
        result = get_csharp_type_docstring(code, "IRepository")
        assert result["found"] == "true"
        assert "Repository pattern" in result["docstring"]

    def test_type_without_doc(self) -> None:
        """Test type without documentation."""
        code = """public class User {
    public string Name { get; set; }
}"""
        result = get_csharp_type_docstring(code, "User")
        assert result["found"] == "true"
        assert result["docstring"] == ""

    def test_struct_with_doc(self) -> None:
        """Test getting struct documentation."""
        code = """/// <summary>Represents a point in 2D space</summary>
public struct Point {
    public int X { get; set; }
    public int Y { get; set; }
}"""
        result = get_csharp_type_docstring(code, "Point")
        assert result["found"] == "true"
        assert "point in 2D space" in result["docstring"]

    def test_type_not_found(self) -> None:
        """Test type not found."""
        code = """/// <summary>User class</summary>
public class User {
    public string Name { get; set; }
}"""
        result = get_csharp_type_docstring(code, "Product")
        assert result["found"] == "false"

    def test_empty_code(self) -> None:
        """Test with empty code."""
        result = get_csharp_type_docstring("", "User")
        assert result["found"] == "false"


# Additional edge case tests


class TestCSharpNavigationEdgeCases:
    """Test edge cases for C# navigation functions."""

    def test_properties_as_methods(self) -> None:
        """Test that properties are handled correctly."""
        code = """public class User {
    public string Name { get; set; }
    public int Age { get; private set; }
}"""
        result = list_csharp_type_methods(code, "User")
        # Properties might be included or excluded depending on implementation
        assert result["found"] == "true"

    def test_generic_types(self) -> None:
        """Test handling of generic types."""
        code = """public class Repository<T> where T : class {
    public void Save(T entity) {
        // Implementation
    }
}"""
        result = list_csharp_types(code)
        assert "Repository" in result["types"]

    def test_async_methods(self) -> None:
        """Test handling of async methods."""
        code = """public class Service {
    public async Task<string> GetDataAsync() {
        await Task.Delay(100);
        return "data";
    }
}"""
        result = list_csharp_functions(code)
        assert "GetDataAsync" in result["functions"]

    def test_expression_bodied_members(self) -> None:
        """Test expression-bodied members."""
        code = """public class Math {
    public int Add(int a, int b) => a + b;
}"""
        result = get_csharp_function_line_numbers(code, "Add")
        assert result["found"] == "true"

    def test_nested_classes(self) -> None:
        """Test nested class handling."""
        code = """public class Outer {
    public class Inner {
        public void Work() { }
    }
}"""
        result = list_csharp_types(code)
        types = result["types"]
        assert "Outer" in types
        assert "Inner" in types

    def test_partial_classes(self) -> None:
        """Test partial class handling."""
        code = """public partial class User {
    public string Name { get; set; }
}

public partial class User {
    public int Age { get; set; }
}"""
        result = list_csharp_types(code)
        assert "User" in result["types"]

    def test_record_types(self) -> None:
        """Test record type handling."""
        code = """public record Person(string Name, int Age);"""
        result = list_csharp_types(code)
        assert "Person" in result["types"]

    def test_static_methods(self) -> None:
        """Test static method handling."""
        code = """public class Utility {
    public static void DoWork() {
        Console.WriteLine("Working");
    }
}"""
        result = list_csharp_functions(code)
        assert "DoWork" in result["functions"]

    def test_constructor_handling(self) -> None:
        """Test that constructors are handled."""
        code = """public class User {
    public User() { }
    public User(string name) {
        Name = name;
    }
}"""
        result = list_csharp_functions(code)
        # Constructors might be included depending on implementation
        assert result["found"] == "true"

    def test_operator_overloading(self) -> None:
        """Test operator overloading."""
        code = """public class Point {
    public int X { get; set; }
    public int Y { get; set; }

    public static Point operator +(Point a, Point b) {
        return new Point { X = a.X + b.X, Y = a.Y + b.Y };
    }
}"""
        result = list_csharp_types(code)
        assert "Point" in result["types"]

    def test_abstract_class(self) -> None:
        """Test abstract class handling."""
        code = """public abstract class Animal {
    public abstract void MakeSound();
}"""
        result = list_csharp_types(code)
        assert "Animal" in result["types"]

    def test_sealed_class(self) -> None:
        """Test sealed class handling."""
        code = """public sealed class FinalClass {
    public void Work() { }
}"""
        result = list_csharp_types(code)
        assert "FinalClass" in result["types"]

    def test_extension_methods(self) -> None:
        """Test extension method handling."""
        code = """public static class StringExtensions {
    public static bool IsEmpty(this string str) {
        return string.IsNullOrEmpty(str);
    }
}"""
        result = list_csharp_functions(code)
        assert "IsEmpty" in result["functions"]

    def test_lambda_expressions(self) -> None:
        """Test code with lambda expressions."""
        code = """public class Service {
    public void Process() {
        var items = list.Where(x => x > 0);
    }
}"""
        result = list_csharp_functions(code)
        assert "Process" in result["functions"]

    def test_multiline_attributes(self) -> None:
        """Test methods with attributes."""
        code = """public class Controller {
    [HttpGet]
    [Route("/api/users")]
    public string GetUsers() {
        return "users";
    }
}"""
        result = list_csharp_functions(code)
        assert "GetUsers" in result["functions"]
