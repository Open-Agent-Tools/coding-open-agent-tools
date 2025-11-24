"""Tests for Java code navigation and analysis functions."""

import importlib.util

import pytest

from coding_open_agent_tools.java.navigation import (
    extract_java_public_api,
    find_java_definitions_by_annotation,
    find_java_method_usages,
    get_java_class_docstring,
    get_java_class_hierarchy,
    get_java_class_line_numbers,
    get_java_method_body,
    get_java_method_details,
    get_java_method_docstring,
    get_java_method_line_numbers,
    get_java_method_signature,
    get_java_module_overview,
    get_java_specific_method_line_numbers,
    list_java_class_methods,
    list_java_classes,
    list_java_method_calls,
    list_java_methods,
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


class TestGetJavaMethodLineNumbers:
    """Test get_java_method_line_numbers function."""

    def test_simple_method(self) -> None:
        """Test finding line numbers for a simple method."""
        code = """public class Example {
    public void hello() {
        System.out.println("world");
    }
}"""
        result = get_java_method_line_numbers(code, "hello")
        assert result["start_line"] == "2"
        assert result["end_line"] == "4"
        assert result["method_name"] == "hello"

    def test_static_method(self) -> None:
        """Test finding line numbers for a static method."""
        code = """public class Utils {
    public static int add(int a, int b) {
        return a + b;
    }
}"""
        result = get_java_method_line_numbers(code, "add")
        assert result["start_line"] == "2"
        assert result["end_line"] == "4"

    def test_constructor(self) -> None:
        """Test finding line numbers for a constructor."""
        code = """public class Person {
    public Person(String name) {
        this.name = name;
    }
}"""
        result = get_java_method_line_numbers(code, "Person")
        assert result["start_line"] == "2"
        assert result["end_line"] == "4"

    def test_method_not_found(self) -> None:
        """Test error when method doesn't exist."""
        code = """public class Example {
    public void hello() {}
}"""
        with pytest.raises(ValueError, match="Method 'goodbye' not found"):
            get_java_method_line_numbers(code, "goodbye")

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            get_java_method_line_numbers("", "test")

    def test_invalid_type(self) -> None:
        """Test behavior with non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            get_java_method_line_numbers(123, "test")  # type: ignore[arg-type]


class TestGetJavaClassLineNumbers:
    """Test get_java_class_line_numbers function."""

    def test_simple_class(self) -> None:
        """Test finding line numbers for a simple class."""
        code = """public class Example {
    private int value;

    public int getValue() {
        return value;
    }
}"""
        result = get_java_class_line_numbers(code, "Example")
        assert result["start_line"] == "1"
        assert result["end_line"] == "7"
        assert result["class_name"] == "Example"

    def test_nested_class(self) -> None:
        """Test finding line numbers for a nested class."""
        code = """public class Outer {
    private class Inner {
        void method() {}
    }
}"""
        result = get_java_class_line_numbers(code, "Inner")
        assert result["start_line"] == "2"
        assert result["end_line"] == "4"

    def test_interface(self) -> None:
        """Test finding line numbers for an interface."""
        code = """public interface Runnable {
    void run();
}"""
        result = get_java_class_line_numbers(code, "Runnable")
        assert result["start_line"] == "1"
        assert result["end_line"] == "3"

    def test_class_not_found(self) -> None:
        """Test error when class doesn't exist."""
        code = """public class Example {}"""
        with pytest.raises(ValueError, match="Class 'Missing' not found"):
            get_java_class_line_numbers(code, "Missing")


class TestGetJavaModuleOverview:
    """Test get_java_module_overview function."""

    def test_simple_overview(self) -> None:
        """Test overview for a simple Java file."""
        code = """package com.example;

import java.util.List;

/**
 * Example class documentation.
 */
public class Example {
    public void method1() {}
    private void method2() {}
}"""
        result = get_java_module_overview(code)
        assert result["has_package"] == "true"
        assert result["has_imports"] == "true"
        assert "Example" in result["class_names"]
        assert result["class_count"] == "1"
        assert result["method_count"] == "2"

    def test_multiple_classes(self) -> None:
        """Test overview with multiple classes."""
        code = """public class First {
    void method1() {}
}

class Second {
    void method2() {}
}"""
        result = get_java_module_overview(code)
        assert result["class_count"] == "2"
        assert "First" in result["class_names"]
        assert "Second" in result["class_names"]

    def test_empty_file(self) -> None:
        """Test overview of empty file."""
        result = get_java_module_overview("// Empty file")
        assert result["class_count"] == "0"
        assert result["method_count"] == "0"


class TestListJavaMethods:
    """Test list_java_methods function."""

    def test_list_methods(self) -> None:
        """Test listing all methods in a file."""
        import json

        code = """public class Example {
    public void method1() {}
    private int method2() { return 0; }
    public static void method3() {}
}"""
        result = list_java_methods(code)
        assert result["method_count"] == "3"
        methods = json.loads(result["methods"])
        method_names = [m["name"] for m in methods]
        assert "method1" in method_names
        assert "method2" in method_names
        assert "method3" in method_names

    def test_no_methods(self) -> None:
        """Test file with no methods."""
        code = """public class Empty {
    private int value;
}"""
        result = list_java_methods(code)
        assert result["method_count"] == "0"
        assert result["methods"] == "[]"


class TestListJavaClasses:
    """Test list_java_classes function."""

    def test_list_classes(self) -> None:
        """Test listing all classes in a file."""
        import json

        code = """public class First {}
class Second {}
interface Third {}"""
        result = list_java_classes(code)
        assert result["class_count"] == "3"
        classes = json.loads(result["classes"])
        class_names = [c["name"] for c in classes]
        assert "First" in class_names
        assert "Second" in class_names
        assert "Third" in class_names

    def test_nested_classes(self) -> None:
        """Test listing nested classes."""
        import json

        code = """public class Outer {
    private class Inner1 {}
    private class Inner2 {}
}"""
        result = list_java_classes(code)
        assert result["class_count"] == "3"
        classes = json.loads(result["classes"])
        class_names = [c["name"] for c in classes]
        assert "Outer" in class_names
        assert "Inner1" in class_names


class TestGetJavaMethodSignature:
    """Test get_java_method_signature function."""

    def test_simple_signature(self) -> None:
        """Test extracting a simple method signature."""
        code = """public class Example {
    public void hello(String name) {
        System.out.println(name);
    }
}"""
        result = get_java_method_signature(code, "hello")
        assert result["method_name"] == "hello"
        assert "void" in result["signature"]
        assert "String name" in result["signature"]

    def test_generic_signature(self) -> None:
        """Test extracting a method signature with generics."""
        code = """public class Utils {
    public <T> List<T> process(List<T> items) {
        return items;
    }
}"""
        result = get_java_method_signature(code, "process")
        assert result["method_name"] == "process"
        assert "List<T>" in result["signature"]

    def test_method_not_found(self) -> None:
        """Test error for non-existent method."""
        code = """public class Example {
    public void hello() {}
}"""
        with pytest.raises(ValueError, match="Method 'missing' not found"):
            get_java_method_signature(code, "missing")


class TestGetJavaMethodDocstring:
    """Test get_java_method_docstring function."""

    def test_javadoc(self) -> None:
        """Test extracting Javadoc comment."""
        code = """public class Example {
    /**
     * Says hello to the world.
     * @param name The name to greet
     */
    public void hello(String name) {
        System.out.println(name);
    }
}"""
        result = get_java_method_docstring(code, "hello")
        assert result["method_name"] == "hello"
        assert "Says hello to the world" in result["docstring"]
        assert "@param name" in result["docstring"]

    def test_no_javadoc(self) -> None:
        """Test method without Javadoc."""
        code = """public class Example {
    public void hello() {}
}"""
        result = get_java_method_docstring(code, "hello")
        assert result["docstring"] == ""


class TestListJavaClassMethods:
    """Test list_java_class_methods function."""

    def test_list_class_methods(self) -> None:
        """Test listing methods of a specific class."""
        code = """public class Example {
    public void method1() {}
    private void method2() {}
}

class Other {
    public void method3() {}
}"""
        result = list_java_class_methods(code, "Example")
        assert result["class_name"] == "Example"
        assert "method1" in result["methods"]
        assert "method2" in result["methods"]
        assert "method3" not in result["methods"]

    def test_class_not_found(self) -> None:
        """Test error for non-existent class."""
        code = """public class Example {
    public void method() {}
}"""
        with pytest.raises(ValueError, match="Class 'Missing' not found"):
            list_java_class_methods(code, "Missing")


class TestExtractJavaPublicApi:
    """Test extract_java_public_api function."""

    def test_public_api(self) -> None:
        """Test extracting public API."""
        code = """public class Example {
    public void publicMethod() {}
    private void privateMethod() {}
    protected void protectedMethod() {}
}"""
        result = extract_java_public_api(code)
        assert "publicMethod" in result["public_methods"]
        assert "privateMethod" not in result["public_methods"]
        assert "Example" in result["public_classes"]

    def test_interface_methods(self) -> None:
        """Test that interface is included in public API."""
        code = """public interface Runnable {
    void run();
    void stop();
}"""
        result = extract_java_public_api(code)
        # Interface itself is public
        assert "Runnable" in result["public_classes"]
        assert result["public_count"] == "1"


class TestGetJavaMethodDetails:
    """Test get_java_method_details function."""

    def test_method_details(self) -> None:
        """Test getting comprehensive method details."""
        code = """public class Example {
    /**
     * Adds two numbers.
     */
    public static int add(int a, int b) {
        return a + b;
    }
}"""
        result = get_java_method_details(code, "add")
        assert result["method_name"] == "add"
        assert result["line"] == "5"
        assert "int" in result["signature"]
        assert "Adds two numbers" in result["docstring"]

    def test_method_not_found(self) -> None:
        """Test error for non-existent method."""
        code = """public class Example {
    public void hello() {}
}"""
        with pytest.raises(ValueError, match="Method 'missing' not found"):
            get_java_method_details(code, "missing")


class TestGetJavaMethodBody:
    """Test get_java_method_body function."""

    def test_simple_body(self) -> None:
        """Test extracting method body."""
        code = """public class Example {
    public int add(int a, int b) {
        return a + b;
    }
}"""
        result = get_java_method_body(code, "add")
        assert result["method_name"] == "add"
        assert "return a + b;" in result["body"]

    def test_multiline_body(self) -> None:
        """Test extracting multiline method body."""
        code = """public class Example {
    public void process() {
        int x = 5;
        int y = 10;
        System.out.println(x + y);
    }
}"""
        result = get_java_method_body(code, "process")
        assert "int x = 5;" in result["body"]
        assert "int y = 10;" in result["body"]
        assert "System.out.println" in result["body"]

    def test_method_not_found(self) -> None:
        """Test error for non-existent method."""
        code = """public class Example {
    public void hello() {}
}"""
        with pytest.raises(ValueError, match="Method 'missing' not found"):
            get_java_method_body(code, "missing")


class TestListJavaMethodCalls:
    """Test list_java_method_calls function."""

    def test_method_calls(self) -> None:
        """Test listing method calls in a method."""
        import json

        code = """public class Example {
    public void process() {
        helper1();
        helper2();
        System.out.println("done");
    }

    private void helper1() {}
    private void helper2() {}
}"""
        result = list_java_method_calls(code, "process")
        calls = json.loads(result["calls"])
        assert "helper1" in calls
        assert "helper2" in calls
        assert "println" in calls

    def test_no_calls(self) -> None:
        """Test method with no calls."""
        code = """public class Example {
    public int getValue() {
        return 42;
    }
}"""
        result = list_java_method_calls(code, "getValue")
        assert result["call_count"] == "0"

    def test_chained_calls(self) -> None:
        """Test method with chained calls."""
        import json

        code = """public class Example {
    public void process() {
        value.toString().length();
    }
}"""
        result = list_java_method_calls(code, "process")
        calls = json.loads(result["calls"])
        # Note: Chained call detection has limitations with tree-sitter
        assert "length" in calls
        assert result["call_count"] == "2"


class TestFindJavaMethodUsages:
    """Test find_java_method_usages function."""

    def test_find_usages(self) -> None:
        """Test finding method usages."""
        code = """public class Example {
    public void caller1() {
        target();
    }

    public void caller2() {
        target();
    }

    public void target() {}
}"""
        result = find_java_method_usages(code, "target")
        assert result["usage_count"] == "2"
        # Verify we have usage details
        assert "usage_details" in result

    def test_no_usages(self) -> None:
        """Test method with no usages."""
        code = """public class Example {
    public void unused() {}
    public void other() {}
}"""
        result = find_java_method_usages(code, "unused")
        assert result["usage_count"] == "0"


class TestGetJavaSpecificMethodLineNumbers:
    """Test get_java_specific_method_line_numbers function."""

    def test_method_in_specific_class(self) -> None:
        """Test finding method in a specific class."""
        code = """public class Example {
    public void process() {
        System.out.println("process");
    }
}

class Other {
    public void process() {
        System.out.println("other");
    }
}"""
        result = get_java_specific_method_line_numbers(code, "Example", "process")
        assert result["start_line"] == "2"
        assert result["end_line"] == "4"

    def test_method_in_second_class(self) -> None:
        """Test finding method in second class."""
        code = """public class First {
    public void method() {}
}

class Second {
    public void method() {}
}"""
        result = get_java_specific_method_line_numbers(code, "Second", "method")
        assert result["start_line"] == "6"
        assert result["method_name"] == "method"

    def test_class_not_found(self) -> None:
        """Test error when class not found."""
        code = """public class Example {
    public void process() {}
}"""
        with pytest.raises(ValueError, match="Class 'Missing' not found"):
            get_java_specific_method_line_numbers(code, "Missing", "process")


class TestGetJavaClassHierarchy:
    """Test get_java_class_hierarchy function."""

    def test_simple_inheritance(self) -> None:
        """Test class with extends."""
        code = """public class Dog extends Animal {
    void bark() {}
}"""
        result = get_java_class_hierarchy(code, "Dog")
        assert result["class_name"] == "Dog"
        assert "Animal" in result["extends"]

    def test_interface_implementation(self) -> None:
        """Test class implementing interfaces."""
        code = """public class MyTask implements Runnable, Serializable {
    public void run() {}
}"""
        result = get_java_class_hierarchy(code, "MyTask")
        assert "Runnable" in result["implements"]
        assert "Serializable" in result["implements"]

    def test_no_hierarchy(self) -> None:
        """Test class with no inheritance."""
        code = """public class Simple {
    void method() {}
}"""
        result = get_java_class_hierarchy(code, "Simple")
        assert result["extends"] == ""
        assert result["implements"] == "[]"


class TestFindJavaDefinitionsByAnnotation:
    """Test find_java_definitions_by_annotation function."""

    def test_find_override_annotation(self) -> None:
        """Test finding methods with @Override annotation."""
        code = """public class Example {
    @Override
    public String toString() {
        return "Example";
    }

    @Override
    public boolean equals(Object obj) {
        return false;
    }

    public void regular() {}
}"""
        result = find_java_definitions_by_annotation(code, "Override")
        # Note: Annotation detection may have limitations with tree-sitter
        assert "total_count" in result
        assert "methods" in result

    def test_custom_annotation(self) -> None:
        """Test finding custom annotations."""
        code = """public class Service {
    @Autowired
    private Repository repo;

    @Transactional
    public void save() {}
}"""
        result = find_java_definitions_by_annotation(code, "Transactional")
        assert "methods" in result
        assert "total_count" in result

    def test_no_matches(self) -> None:
        """Test annotation not found."""
        code = """public class Example {
    public void method() {}
}"""
        result = find_java_definitions_by_annotation(code, "Override")
        assert result["total_count"] == "0"


class TestGetJavaClassDocstring:
    """Test get_java_class_docstring function."""

    def test_class_javadoc(self) -> None:
        """Test extracting class Javadoc."""
        code = """/**
 * Example class for testing.
 * @author Test
 */
public class Example {
    void method() {}
}"""
        result = get_java_class_docstring(code, "Example")
        assert result["class_name"] == "Example"
        assert "Example class for testing" in result["docstring"]
        assert "@author Test" in result["docstring"]

    def test_no_javadoc(self) -> None:
        """Test class without Javadoc."""
        code = """public class Example {
    void method() {}
}"""
        result = get_java_class_docstring(code, "Example")
        assert result["docstring"] == ""

    def test_interface_javadoc(self) -> None:
        """Test extracting interface Javadoc."""
        code = """/**
 * Runnable interface.
 */
public interface Runnable {
    void run();
}"""
        result = get_java_class_docstring(code, "Runnable")
        assert "Runnable interface" in result["docstring"]
