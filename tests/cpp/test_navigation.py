"""Tests for C++ code navigation and analysis functions."""

import importlib.util

import pytest

from coding_open_agent_tools.cpp.navigation import (
    extract_cpp_public_api,
    find_cpp_definitions_by_comment,
    find_cpp_function_usages,
    get_cpp_function_body,
    get_cpp_function_details,
    get_cpp_function_docstring,
    get_cpp_function_line_numbers,
    get_cpp_function_signature,
    get_cpp_module_overview,
    get_cpp_specific_function_line_numbers,
    get_cpp_type_docstring,
    get_cpp_type_hierarchy,
    get_cpp_type_line_numbers,
    list_cpp_function_calls,
    list_cpp_functions,
    list_cpp_type_methods,
    list_cpp_types,
)

# Skip all tests if tree-sitter-language-pack is not installed
pytest_plugins = []

TREE_SITTER_AVAILABLE = (
    importlib.util.find_spec("tree_sitter_language_pack") is not None
)

pytestmark = pytest.mark.skipif(
    not TREE_SITTER_AVAILABLE,
    reason="tree-sitter-language-pack not installed",
)


class TestGetCppFunctionLineNumbers:
    """Test get_cpp_function_line_numbers function."""

    def test_simple_function(self) -> None:
        """Test finding line numbers for a simple function."""
        code = """void hello_world() {
    std::cout << "Hello, World!" << std::endl;
}"""
        result = get_cpp_function_line_numbers(code, "hello_world")
        assert result["start_line"] == "1"
        assert result["end_line"] == "3"
        assert result["function_name"] == "hello_world"
        assert result["is_method"] == "false"

    def test_method_with_class(self) -> None:
        """Test finding line numbers for a method within a class."""
        code = """class Person {
public:
    std::string getName() {
        return name;
    }
private:
    std::string name;
};"""
        result = get_cpp_function_line_numbers(code, "getName")
        assert result["start_line"] == "3"
        assert result["end_line"] == "5"
        assert result["is_method"] == "true"

    def test_function_with_params(self) -> None:
        """Test finding line numbers for a function with parameters."""
        code = """int add(int a, int b) {
    return a + b;
}"""
        result = get_cpp_function_line_numbers(code, "add")
        assert result["start_line"] == "1"
        assert result["end_line"] == "3"

    def test_function_not_found(self) -> None:
        """Test error when function doesn't exist."""
        code = """void hello_world() {}"""
        with pytest.raises(ValueError, match="Function 'goodbye' not found"):
            get_cpp_function_line_numbers(code, "goodbye")

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            get_cpp_function_line_numbers("", "test")

    def test_invalid_type(self) -> None:
        """Test behavior with non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            get_cpp_function_line_numbers(123, "test")  # type: ignore[arg-type]


class TestGetCppTypeLineNumbers:
    """Test get_cpp_type_line_numbers function."""

    def test_class_type(self) -> None:
        """Test finding line numbers for a class type."""
        code = """class Person {
    std::string name;
    int age;
};"""
        result = get_cpp_type_line_numbers(code, "Person")
        assert result["start_line"] == "1"
        assert result["end_line"] == "4"
        assert result["type_name"] == "Person"

    def test_struct_type(self) -> None:
        """Test finding line numbers for a struct type."""
        code = """struct Point {
    int x;
    int y;
};"""
        result = get_cpp_type_line_numbers(code, "Point")
        assert result["start_line"] == "1"
        assert result["end_line"] == "4"

    def test_enum_type(self) -> None:
        """Test finding line numbers for an enum type."""
        code = """enum Color {
    RED,
    GREEN,
    BLUE
};"""
        result = get_cpp_type_line_numbers(code, "Color")
        assert result["start_line"] == "1"
        assert result["end_line"] == "5"

    def test_type_not_found(self) -> None:
        """Test error when type doesn't exist."""
        code = """class Person {};"""
        with pytest.raises(ValueError, match="Type 'Missing' not found"):
            get_cpp_type_line_numbers(code, "Missing")

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            get_cpp_type_line_numbers("", "test")

    def test_invalid_type(self) -> None:
        """Test behavior with non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            get_cpp_type_line_numbers(123, "test")  # type: ignore[arg-type]


class TestGetCppModuleOverview:
    """Test get_cpp_module_overview function."""

    def test_simple_overview(self) -> None:
        """Test overview for a simple C++ file."""
        code = """/// HelloWorld says hello to the world
void hello_world() {
    std::cout << "Hello, World!" << std::endl;
}

class Person {
    std::string name;
};"""
        result = get_cpp_module_overview(code)
        assert result["function_count"] == "1"
        assert result["type_count"] == "1"
        assert "hello_world" in result["function_names"]
        assert "Person" in result["type_names"]

    def test_multiple_functions_and_types(self) -> None:
        """Test overview with multiple functions and types."""
        code = """void first() {}
void second() {}

class TypeA {};
struct TypeB {};"""
        result = get_cpp_module_overview(code)
        assert result["function_count"] == "2"
        assert result["type_count"] == "2"
        assert result["method_count"] == "0"

    def test_empty_file(self) -> None:
        """Test overview of empty file."""
        code = """// Empty file
"""
        result = get_cpp_module_overview(code)
        assert result["function_count"] == "0"
        assert result["method_count"] == "0"
        assert result["type_count"] == "0"

    def test_has_main_function(self) -> None:
        """Test detection of main function."""
        code = """int main() {
    return 0;
}"""
        result = get_cpp_module_overview(code)
        assert result["has_main"] == "true"
        assert result["function_count"] == "1"


class TestListCppFunctions:
    """Test list_cpp_functions function."""

    def test_list_functions(self) -> None:
        """Test listing all functions in a file."""
        import json

        code = """void public_func() {}

void private_func() {}

int add(int a, int b) {
    return a + b;
}"""
        result = list_cpp_functions(code)
        assert result["function_count"] == "3"
        functions = json.loads(result["functions"])
        function_names = [f["name"] for f in functions]
        assert "public_func" in function_names
        assert "private_func" in function_names
        assert "add" in function_names

    def test_public_vs_private(self) -> None:
        """Test public vs private function detection."""
        import json

        code = """class MyClass {
public:
    void public_method() {}
private:
    void private_method() {}
};"""
        result = list_cpp_functions(code)
        functions = json.loads(result["functions"])
        public_funcs = [f for f in functions if f["is_public"]]
        private_funcs = [f for f in functions if not f["is_public"]]
        assert len(public_funcs) == 1
        assert len(private_funcs) == 1

    def test_no_functions(self) -> None:
        """Test file with no functions."""
        code = """class Person {
    std::string name;
};"""
        result = list_cpp_functions(code)
        assert result["function_count"] == "0"
        assert result["functions"] == "[]"

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            list_cpp_functions("")


class TestListCppTypes:
    """Test list_cpp_types function."""

    def test_list_types(self) -> None:
        """Test listing all types in a file."""
        import json

        code = """class Person {
    std::string name;
};

struct Point {
    int x;
    int y;
};

enum Color {
    RED,
    GREEN
};"""
        result = list_cpp_types(code)
        assert result["type_count"] == "3"
        types = json.loads(result["types"])
        type_names = [t["name"] for t in types]
        assert "Person" in type_names
        assert "Point" in type_names
        assert "Color" in type_names

    def test_type_kinds(self) -> None:
        """Test detecting different type kinds."""
        import json

        code = """class Person {
    std::string name;
};

struct Point {
    int x;
};

enum Color {
    RED
};"""
        result = list_cpp_types(code)
        types = json.loads(result["types"])
        kinds = {t["name"]: t["kind"] for t in types}
        assert kinds["Person"] == "class"
        assert kinds["Point"] == "struct"
        assert kinds["Color"] == "enum"

    def test_public_types(self) -> None:
        """Test that all top-level types are marked public."""
        import json

        code = """class PublicClass {};
struct PublicStruct {};"""
        result = list_cpp_types(code)
        types = json.loads(result["types"])
        for t in types:
            assert t["is_public"]


class TestGetCppFunctionSignature:
    """Test get_cpp_function_signature function."""

    def test_simple_signature(self) -> None:
        """Test extracting a simple function signature."""
        code = """void hello_world() {
    std::cout << "Hello!" << std::endl;
}"""
        result = get_cpp_function_signature(code, "hello_world")
        assert result["function_name"] == "hello_world"
        assert "hello_world()" in result["signature"]
        assert result["is_public"] == "true"

    def test_signature_with_params(self) -> None:
        """Test extracting a function signature with parameters."""
        code = """int add(int a, int b) {
    return a + b;
}"""
        result = get_cpp_function_signature(code, "add")
        assert result["function_name"] == "add"
        assert "int" in result["returns"]

    def test_method_signature(self) -> None:
        """Test extracting a method signature."""
        code = """class Person {
public:
    std::string getName() {
        return name;
    }
private:
    std::string name;
};"""
        result = get_cpp_function_signature(code, "getName")
        assert result["function_name"] == "getName"
        assert "std::string" in result["returns"]

    def test_function_not_found(self) -> None:
        """Test error for non-existent function."""
        code = """void hello_world() {}"""
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            get_cpp_function_signature(code, "missing")

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            get_cpp_function_signature("", "test")


class TestGetCppFunctionDocstring:
    """Test get_cpp_function_docstring function."""

    def test_doxygen_comment_triple_slash(self) -> None:
        """Test extracting /// style doc comment."""
        code = """/// HelloWorld says hello to the world.
/// It prints a greeting message.
void hello_world() {
    std::cout << "Hello!" << std::endl;
}"""
        result = get_cpp_function_docstring(code, "hello_world")
        assert result["function_name"] == "hello_world"
        assert "says hello to the world" in result["docstring"]
        assert result["has_docstring"] == "true"

    def test_multiline_doc_comment(self) -> None:
        """Test extracting multiline /** */ doc comment."""
        code = """/**
 * Add adds two integers together.
 * It returns the sum of a and b.
 */
int add(int a, int b) {
    return a + b;
}"""
        result = get_cpp_function_docstring(code, "add")
        assert result["function_name"] == "add"
        assert "adds two integers" in result["docstring"]
        assert result["has_docstring"] == "true"

    def test_no_docstring(self) -> None:
        """Test function without doc comment."""
        code = """void hello_world() {}"""
        result = get_cpp_function_docstring(code, "hello_world")
        assert result["docstring"] == ""
        assert result["has_docstring"] == "false"

    def test_function_not_found(self) -> None:
        """Test error for non-existent function."""
        code = """void hello_world() {}"""
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            get_cpp_function_docstring(code, "missing")


class TestListCppTypeMethods:
    """Test list_cpp_type_methods function."""

    def test_list_type_methods(self) -> None:
        """Test listing methods of a specific type."""
        import json

        code = """class Person {
public:
    std::string getName() {
        return name;
    }

    void setName(std::string n) {
        name = n;
    }
private:
    std::string name;
};

class Other {
public:
    void other_method() {}
};"""
        result = list_cpp_type_methods(code, "Person")
        assert result["type_name"] == "Person"
        assert result["method_count"] == "2"
        methods = json.loads(result["methods"])
        method_names = [m["name"] for m in methods]
        assert "getName" in method_names
        assert "setName" in method_names
        assert "other_method" not in method_names

    def test_public_and_private_methods(self) -> None:
        """Test methods with both public and private access."""

        code = """class Counter {
public:
    int getCount() {
        return count;
    }
private:
    void increment() {
        count++;
    }
    int count;
};"""
        result = list_cpp_type_methods(code, "Counter")
        assert result["method_count"] == "2"

    def test_type_not_found(self) -> None:
        """Test error for non-existent type."""
        code = """class Person {};"""
        with pytest.raises(ValueError, match="Type 'Missing' not found"):
            list_cpp_type_methods(code, "Missing")

    def test_type_with_no_methods(self) -> None:
        """Test type with no methods."""
        code = """class Person {
    std::string name;
};"""
        result = list_cpp_type_methods(code, "Person")
        assert result["method_count"] == "0"


class TestExtractCppPublicApi:
    """Test extract_cpp_public_api function."""

    def test_public_api(self) -> None:
        """Test extracting public API."""
        import json

        code = """void public_func() {}

class PublicClass {};

class MyClass {
public:
    void public_method() {}
private:
    void private_method() {}
};"""
        result = extract_cpp_public_api(code)
        public_functions = json.loads(result["public_functions"])
        public_types = json.loads(result["public_types"])
        assert "public_func" in public_functions
        assert "public_method" in public_functions
        assert "private_method" not in public_functions
        assert "PublicClass" in public_types
        assert "MyClass" in public_types

    def test_public_methods(self) -> None:
        """Test that public methods are included."""
        import json

        code = """class Person {
public:
    void public_method() {}
private:
    void private_method() {}
};"""
        result = extract_cpp_public_api(code)
        public_functions = json.loads(result["public_functions"])
        assert "public_method" in public_functions
        assert "private_method" not in public_functions

    def test_empty_file(self) -> None:
        """Test extracting public API from empty file."""
        code = """// Empty file
"""
        result = extract_cpp_public_api(code)
        assert result["public_count"] == "0"


class TestGetCppFunctionDetails:
    """Test get_cpp_function_details function."""

    def test_function_details(self) -> None:
        """Test getting comprehensive function details."""
        code = """/// Add adds two integers together.
int add(int a, int b) {
    return a + b;
}"""
        result = get_cpp_function_details(code, "add")
        assert result["function_name"] == "add"
        assert "int" in result["returns"]
        assert result["is_public"] == "true"
        assert "adds two integers" in result["docstring"]
        assert result["line"] == "2"

    def test_method_details(self) -> None:
        """Test getting method details."""
        code = """class Person {
public:
    /// GetName returns the person's name.
    std::string getName() {
        return name;
    }
private:
    std::string name;
};"""
        result = get_cpp_function_details(code, "getName")
        assert result["function_name"] == "getName"
        assert "std::string" in result["returns"]
        assert "person's name" in result["docstring"]

    def test_function_not_found(self) -> None:
        """Test error for non-existent function."""
        code = """void hello_world() {}"""
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            get_cpp_function_details(code, "missing")


class TestGetCppFunctionBody:
    """Test get_cpp_function_body function."""

    def test_simple_body(self) -> None:
        """Test extracting function body."""
        code = """int add(int a, int b) {
    return a + b;
}"""
        result = get_cpp_function_body(code, "add")
        assert result["function_name"] == "add"
        assert "return a + b" in result["body"]

    def test_multiline_body(self) -> None:
        """Test extracting multiline function body."""
        code = """void process() {
    int x = 5;
    int y = 10;
    std::cout << x + y << std::endl;
}"""
        result = get_cpp_function_body(code, "process")
        assert "int x = 5" in result["body"]
        assert "int y = 10" in result["body"]
        assert "std::cout" in result["body"]

    def test_method_body(self) -> None:
        """Test extracting method body."""
        code = """class Person {
public:
    void setName(std::string n) {
        name = n;
    }
private:
    std::string name;
};"""
        result = get_cpp_function_body(code, "setName")
        assert "name = n" in result["body"]

    def test_function_not_found(self) -> None:
        """Test error for non-existent function."""
        code = """void hello_world() {}"""
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            get_cpp_function_body(code, "missing")


class TestListCppFunctionCalls:
    """Test list_cpp_function_calls function."""

    def test_function_calls(self) -> None:
        """Test listing function calls in a function."""
        import json

        code = """void helper1() {}
void helper2() {}

void process() {
    helper1();
    helper2();
    std::cout << "done" << std::endl;
}"""
        result = list_cpp_function_calls(code, "process")
        calls = json.loads(result["calls"])
        assert "helper1" in calls
        assert "helper2" in calls

    def test_no_calls(self) -> None:
        """Test function with no calls."""
        code = """int get_value() {
    return 42;
}"""
        result = list_cpp_function_calls(code, "get_value")
        assert result["call_count"] == "0"

    def test_method_calls(self) -> None:
        """Test function with method calls."""
        import json

        code = """class Person {
public:
    std::string getName() { return ""; }
};

void process() {
    Person p;
    std::string name = p.getName();
    helper();
}

void helper() {}"""
        result = list_cpp_function_calls(code, "process")
        calls = json.loads(result["calls"])
        assert len(calls) >= 2

    def test_function_not_found(self) -> None:
        """Test error for non-existent function."""
        code = """void hello_world() {}"""
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            list_cpp_function_calls(code, "missing")


class TestFindCppFunctionUsages:
    """Test find_cpp_function_usages function."""

    def test_find_usages(self) -> None:
        """Test finding function usages."""
        import json

        code = """void target() {}

void caller1() {
    target();
}

void caller2() {
    target();
}"""
        result = find_cpp_function_usages(code, "target")
        assert result["usage_count"] == "2"
        usages = json.loads(result["usages"])
        assert len(usages) == 2

    def test_no_usages(self) -> None:
        """Test function with no usages."""
        code = """void unused() {}
void other() {}"""
        result = find_cpp_function_usages(code, "unused")
        assert result["usage_count"] == "0"

    def test_namespace_qualified_call(self) -> None:
        """Test finding namespace-qualified function calls."""
        import json

        code = """namespace myapp {
    void process() {}
}

void caller() {
    myapp::process();
}"""
        result = find_cpp_function_usages(code, "process")
        usages = json.loads(result["usages"])
        assert len(usages) >= 1

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            find_cpp_function_usages("", "test")


class TestGetCppSpecificFunctionLineNumbers:
    """Test get_cpp_specific_function_line_numbers function."""

    def test_method_in_specific_class(self) -> None:
        """Test finding method in a specific class."""
        code = """class Person {
public:
    std::string getName() {
        return name;
    }
private:
    std::string name;
};

class Other {
public:
    std::string getName() {
        return "other";
    }
};"""
        result = get_cpp_specific_function_line_numbers(code, "Person", "getName")
        assert result["start_line"] == "3"
        assert result["end_line"] == "5"
        assert result["class_name"] == "Person"
        assert result["function_name"] == "getName"

    def test_method_in_second_class(self) -> None:
        """Test finding method in second class."""
        code = """class First {
public:
    void method() {}
};

class Second {
public:
    void method() {}
};"""
        result = get_cpp_specific_function_line_numbers(code, "Second", "method")
        assert result["start_line"] == "8"
        assert result["function_name"] == "method"

    def test_class_not_found(self) -> None:
        """Test error when class not found."""
        code = """class Person {
public:
    std::string getName() {
        return "";
    }
};"""
        with pytest.raises(ValueError, match="Class 'Missing' not found"):
            get_cpp_specific_function_line_numbers(code, "Missing", "getName")

    def test_method_not_found(self) -> None:
        """Test error when method not found for class."""
        code = """class Person {
public:
    std::string getName() {
        return "";
    }
};"""
        with pytest.raises(
            ValueError, match="Method 'setName' not found in class 'Person'"
        ):
            get_cpp_specific_function_line_numbers(code, "Person", "setName")


class TestGetCppTypeHierarchy:
    """Test get_cpp_type_hierarchy function."""

    def test_class_inheritance(self) -> None:
        """Test class with base classes."""
        import json

        code = """class Base {
    int id;
};

class Person : public Base {
    std::string name;
};"""
        result = get_cpp_type_hierarchy(code, "Person")
        assert result["type_name"] == "Person"
        assert result["has_inheritance"] == "true"
        base_classes = json.loads(result["base_classes"])
        assert "Base" in base_classes

    def test_no_inheritance(self) -> None:
        """Test class with no inheritance."""
        code = """class Person {
    std::string name;
};"""
        result = get_cpp_type_hierarchy(code, "Person")
        assert result["has_inheritance"] == "false"
        assert result["base_classes"] == "[]"

    def test_multiple_inheritance(self) -> None:
        """Test class with multiple base classes."""
        import json

        code = """class Base1 {
    int id;
};

class Base2 {
    std::string tag;
};

class Derived : public Base1, public Base2 {
    std::string name;
};"""
        result = get_cpp_type_hierarchy(code, "Derived")
        assert result["has_inheritance"] == "true"
        base_classes = json.loads(result["base_classes"])
        assert "Base1" in base_classes
        assert "Base2" in base_classes

    def test_type_not_found(self) -> None:
        """Test error for non-existent type."""
        code = """class Person {};"""
        with pytest.raises(ValueError, match="Type 'Missing' not found"):
            get_cpp_type_hierarchy(code, "Missing")


class TestFindCppDefinitionsByComment:
    """Test find_cpp_definitions_by_comment function."""

    def test_find_by_comment_pattern(self) -> None:
        """Test finding definitions with matching comments."""
        import json

        code = """/// Add performs addition of two integers.
int add(int a, int b) {
    return a + b;
}

/// Subtract performs subtraction.
int subtract(int a, int b) {
    return a - b;
}

/// Multiply multiplies two numbers.
int multiply(int a, int b) {
    return a * b;
}"""
        result = find_cpp_definitions_by_comment(code, "performs")
        functions = json.loads(result["functions"])
        assert "add" in functions
        assert "subtract" in functions
        assert "multiply" not in functions

    def test_find_type_by_comment(self) -> None:
        """Test finding types with matching comments."""
        import json

        code = """/// Person represents a user of the system.
class Person {
    std::string name;
};

/// Counter counts things.
class Counter {
    int count;
};"""
        result = find_cpp_definitions_by_comment(code, "represents")
        types = json.loads(result["types"])
        assert "Person" in types
        assert "Counter" not in types

    def test_case_insensitive_search(self) -> None:
        """Test case-insensitive comment search."""
        import json

        code = """/// DEPRECATED: Use NewVersion instead.
void old_func() {}

/// Deprecated: Use Better instead.
void another_old() {}"""
        result = find_cpp_definitions_by_comment(code, "deprecated")
        functions = json.loads(result["functions"])
        assert len(functions) == 2

    def test_no_matches(self) -> None:
        """Test no matches found."""
        code = """/// Add two numbers.
int add(int a, int b) {
    return a + b;
}"""
        result = find_cpp_definitions_by_comment(code, "nonexistent")
        assert result["total_count"] == "0"

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            find_cpp_definitions_by_comment("", "test")


class TestGetCppTypeDocstring:
    """Test get_cpp_type_docstring function."""

    def test_class_docstring(self) -> None:
        """Test extracting class doc comment."""
        code = """/// Person represents a user in the system.
/// It contains personal information.
class Person {
    std::string name;
};"""
        result = get_cpp_type_docstring(code, "Person")
        assert result["type_name"] == "Person"
        assert "represents a user" in result["docstring"]
        assert result["has_docstring"] == "true"

    def test_no_docstring(self) -> None:
        """Test type without doc comment."""
        code = """class Person {
    std::string name;
};"""
        result = get_cpp_type_docstring(code, "Person")
        assert result["docstring"] == ""
        assert result["has_docstring"] == "false"

    def test_struct_docstring(self) -> None:
        """Test extracting struct doc comment."""
        code = """/// Point represents a 2D coordinate.
struct Point {
    int x;
    int y;
};"""
        result = get_cpp_type_docstring(code, "Point")
        assert "represents a 2D coordinate" in result["docstring"]

    def test_enum_docstring(self) -> None:
        """Test extracting enum doc comment."""
        code = """/// Color represents different colors.
enum Color {
    RED,
    GREEN
};"""
        result = get_cpp_type_docstring(code, "Color")
        assert "represents different colors" in result["docstring"]

    def test_type_not_found(self) -> None:
        """Test error for non-existent type."""
        code = """class Person {};"""
        with pytest.raises(ValueError, match="Type 'Missing' not found"):
            get_cpp_type_docstring(code, "Missing")

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            get_cpp_type_docstring("", "test")
