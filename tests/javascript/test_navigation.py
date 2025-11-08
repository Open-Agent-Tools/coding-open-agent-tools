"""Tests for JavaScript navigation functions."""

import json

import pytest

from coding_open_agent_tools.javascript.navigation import (
    extract_javascript_public_api,
    find_javascript_definitions_by_decorator,
    find_javascript_function_usages,
    get_javascript_class_docstring,
    get_javascript_class_hierarchy,
    get_javascript_class_line_numbers,
    get_javascript_function_body,
    get_javascript_function_details,
    get_javascript_function_docstring,
    get_javascript_function_line_numbers,
    get_javascript_function_signature,
    get_javascript_method_line_numbers,
    get_javascript_module_overview,
    list_javascript_class_methods,
    list_javascript_classes,
    list_javascript_function_calls,
    list_javascript_functions,
)


class TestGetJavaScriptFunctionLineNumbers:
    """Tests for get_javascript_function_line_numbers."""

    def test_simple_function(self) -> None:
        code = """function hello() {
    return 'world';
}"""
        result = get_javascript_function_line_numbers(code, "hello")
        assert result["start_line"] == "1"
        assert result["end_line"] == "3"
        assert result["function_name"] == "hello"

    def test_arrow_function(self) -> None:
        code = """const greet = (name) => {
    return `Hello, ${name}`;
};"""
        result = get_javascript_function_line_numbers(code, "greet")
        assert result["start_line"] == "1"
        assert result["function_name"] == "greet"

    def test_async_function(self) -> None:
        code = """async function fetchData() {
    const response = await fetch('/api/data');
    return response.json();
}"""
        result = get_javascript_function_line_numbers(code, "fetchData")
        assert result["start_line"] == "1"
        assert result["function_name"] == "fetchData"

    def test_function_not_found(self) -> None:
        code = "function hello() { return 'world'; }"
        with pytest.raises(ValueError, match="not found"):
            get_javascript_function_line_numbers(code, "goodbye")

    def test_type_error_source_code(self) -> None:
        with pytest.raises(TypeError, match="must be a string"):
            get_javascript_function_line_numbers(123, "hello")  # type: ignore[arg-type]

    def test_type_error_function_name(self) -> None:
        with pytest.raises(TypeError, match="must be a string"):
            get_javascript_function_line_numbers("code", 123)  # type: ignore[arg-type]

    def test_value_error_empty_code(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            get_javascript_function_line_numbers("   ", "hello")


class TestGetJavaScriptClassLineNumbers:
    """Tests for get_javascript_class_line_numbers."""

    def test_simple_class(self) -> None:
        code = """class Person {
    constructor(name) {
        this.name = name;
    }
}"""
        result = get_javascript_class_line_numbers(code, "Person")
        assert result["start_line"] == "1"
        assert result["end_line"] == "5"
        assert result["class_name"] == "Person"

    def test_class_with_methods(self) -> None:
        code = """class Calculator {
    add(a, b) {
        return a + b;
    }

    subtract(a, b) {
        return a - b;
    }
}"""
        result = get_javascript_class_line_numbers(code, "Calculator")
        assert result["start_line"] == "1"
        assert result["class_name"] == "Calculator"

    def test_class_not_found(self) -> None:
        code = "class Person {}"
        with pytest.raises(ValueError, match="not found"):
            get_javascript_class_line_numbers(code, "Animal")

    def test_type_error_source_code(self) -> None:
        with pytest.raises(TypeError, match="must be a string"):
            get_javascript_class_line_numbers(123, "Person")  # type: ignore[arg-type]

    def test_type_error_class_name(self) -> None:
        with pytest.raises(TypeError, match="must be a string"):
            get_javascript_class_line_numbers("code", 123)  # type: ignore[arg-type]

    def test_value_error_empty_code(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            get_javascript_class_line_numbers("", "Person")


class TestGetJavaScriptModuleOverview:
    """Tests for get_javascript_module_overview."""

    def test_simple_module(self) -> None:
        code = """function foo() {}
function bar() {}
class MyClass {}"""
        result = get_javascript_module_overview(code)

        assert result["function_count"] == "2"
        assert result["class_count"] == "1"

        func_names = json.loads(result["function_names"])
        assert "foo" in func_names
        assert "bar" in func_names

        class_names = json.loads(result["class_names"])
        assert "MyClass" in class_names

    def test_module_with_exports(self) -> None:
        code = """export function hello() {}
export default class Main {}"""
        result = get_javascript_module_overview(code)

        assert result["has_exports"] == "true"

    def test_module_with_imports(self) -> None:
        code = """import React from 'react';
function Component() {}"""
        result = get_javascript_module_overview(code)

        assert result["has_imports"] == "true"

    def test_total_lines(self) -> None:
        code = "line1\nline2\nline3"
        result = get_javascript_module_overview(code)

        assert result["total_lines"] == "3"

    def test_type_error(self) -> None:
        with pytest.raises(TypeError, match="must be a string"):
            get_javascript_module_overview(123)  # type: ignore[arg-type]

    def test_value_error_empty(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            get_javascript_module_overview("  ")


class TestListJavaScriptFunctions:
    """Tests for list_javascript_functions."""

    def test_list_simple_functions(self) -> None:
        code = """function add(a, b) { return a + b; }
function subtract(a, b) { return a - b; }"""
        result = list_javascript_functions(code)

        assert result["function_count"] == "2"

        functions = json.loads(result["functions"])
        names = [f["name"] for f in functions]
        assert "add" in names
        assert "subtract" in names

    def test_function_with_async(self) -> None:
        code = "async function fetchData() { return await fetch('/api'); }"
        result = list_javascript_functions(code)

        functions = json.loads(result["functions"])
        assert functions[0]["async"] is True

    def test_arrow_function(self) -> None:
        code = "const double = (x) => x * 2;"
        result = list_javascript_functions(code)

        functions = json.loads(result["functions"])
        assert functions[0]["name"] == "double"
        assert functions[0]["type"] == "arrow"

    def test_empty_module(self) -> None:
        code = "const x = 5;"
        result = list_javascript_functions(code)

        assert result["function_count"] == "0"

    def test_type_error(self) -> None:
        with pytest.raises(TypeError, match="must be a string"):
            list_javascript_functions(123)  # type: ignore[arg-type]


class TestListJavaScriptClasses:
    """Tests for list_javascript_classes."""

    def test_list_simple_classes(self) -> None:
        code = """class Dog {}
class Cat {}"""
        result = list_javascript_classes(code)

        assert result["class_count"] == "2"

        classes = json.loads(result["classes"])
        names = [c["name"] for c in classes]
        assert "Dog" in names
        assert "Cat" in names

    def test_class_with_inheritance(self) -> None:
        code = "class Dog extends Animal {}"
        result = list_javascript_classes(code)

        classes = json.loads(result["classes"])
        assert classes[0]["extends"] == "Animal"

    def test_class_with_methods(self) -> None:
        code = """class Calculator {
    add(a, b) { return a + b; }
    subtract(a, b) { return a - b; }
}"""
        result = list_javascript_classes(code)

        classes = json.loads(result["classes"])
        assert classes[0]["method_count"] == 2
        assert "add" in classes[0]["methods"]
        assert "subtract" in classes[0]["methods"]


class TestGetJavaScriptFunctionSignature:
    """Tests for get_javascript_function_signature."""

    def test_simple_signature(self) -> None:
        code = "function greet(name) { return `Hello, ${name}`; }"
        result = get_javascript_function_signature(code, "greet")

        assert result["function_name"] == "greet"
        assert result["async"] == "false"

        params = json.loads(result["params"])
        assert params == ["name"]

    def test_async_function(self) -> None:
        code = "async function fetchData() { return await fetch('/api'); }"
        result = get_javascript_function_signature(code, "fetchData")

        assert result["async"] == "true"
        assert "async" in result["signature"]

    def test_arrow_function(self) -> None:
        code = "const add = (a, b) => a + b;"
        result = get_javascript_function_signature(code, "add")

        assert result["function_name"] == "add"
        params = json.loads(result["params"])
        assert params == ["a", "b"]

    def test_function_not_found(self) -> None:
        code = "function hello() {}"
        with pytest.raises(ValueError, match="not found"):
            get_javascript_function_signature(code, "goodbye")


class TestGetJavaScriptFunctionDocstring:
    """Tests for get_javascript_function_docstring."""

    def test_function_with_jsdoc(self) -> None:
        code = """/**
 * Adds two numbers together.
 * @param {number} a - First number
 * @param {number} b - Second number
 * @returns {number} Sum of a and b
 */
function add(a, b) {
    return a + b;
}"""
        result = get_javascript_function_docstring(code, "add")

        assert result["has_docstring"] == "true"
        assert "Adds two numbers" in result["docstring"]

    def test_function_without_docstring(self) -> None:
        code = "function add(a, b) { return a + b; }"
        result = get_javascript_function_docstring(code, "add")

        assert result["has_docstring"] == "false"
        assert result["docstring"] == ""

    def test_function_not_found(self) -> None:
        code = "function hello() {}"
        with pytest.raises(ValueError, match="not found"):
            get_javascript_function_docstring(code, "goodbye")


class TestListJavaScriptClassMethods:
    """Tests for list_javascript_class_methods."""

    def test_simple_methods(self) -> None:
        code = """class Calculator {
    add(a, b) { return a + b; }
    subtract(a, b) { return a - b; }
}"""
        result = list_javascript_class_methods(code, "Calculator")

        assert result["method_count"] == "2"
        assert result["class_name"] == "Calculator"

        methods = json.loads(result["methods"])
        names = [m["name"] for m in methods]
        assert "add" in names
        assert "subtract" in names

    def test_static_method(self) -> None:
        code = """class Utils {
    static format(text) { return text.toUpperCase(); }
}"""
        result = list_javascript_class_methods(code, "Utils")

        methods = json.loads(result["methods"])
        assert methods[0]["static"] is True

    def test_async_method(self) -> None:
        code = """class API {
    async fetchData() { return await fetch('/api'); }
}"""
        result = list_javascript_class_methods(code, "API")

        methods = json.loads(result["methods"])
        assert methods[0]["async"] is True

    def test_class_not_found(self) -> None:
        code = "class Person {}"
        with pytest.raises(ValueError, match="not found"):
            list_javascript_class_methods(code, "Animal")


class TestExtractJavaScriptPublicApi:
    """Tests for extract_javascript_public_api."""

    def test_named_exports(self) -> None:
        code = """export function hello() {}
export class MyClass {}"""
        result = extract_javascript_public_api(code)

        exports = json.loads(result["exports"])
        assert "hello" in exports
        assert "MyClass" in exports

        export_types = json.loads(result["export_types"])
        assert export_types["hello"] == "function"
        assert export_types["MyClass"] == "class"

    def test_default_export(self) -> None:
        code = "export default class Main {}"
        result = extract_javascript_public_api(code)

        assert result["has_default_export"] == "true"

    def test_variable_exports(self) -> None:
        code = "export const API_KEY = 'secret';"
        result = extract_javascript_public_api(code)

        exports = json.loads(result["exports"])
        assert "API_KEY" in exports


class TestGetJavaScriptFunctionDetails:
    """Tests for get_javascript_function_details."""

    def test_complete_details(self) -> None:
        code = """/**
 * Greets a person.
 */
function greet(name) {
    return `Hello, ${name}`;
}"""
        result = get_javascript_function_details(code, "greet")

        assert result["function_name"] == "greet"
        assert result["async"] == "false"
        assert result["type"] == "function"
        assert "Greets a person" in result["docstring"]

        params = json.loads(result["params"])
        assert "name" in params

    def test_minimal_function(self) -> None:
        code = "function simple() {}"
        result = get_javascript_function_details(code, "simple")

        assert result["function_name"] == "simple"
        assert result["docstring"] == ""

    def test_function_not_found(self) -> None:
        code = "function hello() {}"
        with pytest.raises(ValueError, match="not found"):
            get_javascript_function_details(code, "goodbye")


class TestGetJavaScriptFunctionBody:
    """Tests for get_javascript_function_body."""

    def test_simple_function_body(self) -> None:
        code = """function add(a, b) {
    return a + b;
}"""
        result = get_javascript_function_body(code, "add")

        assert result["function_name"] == "add"
        assert "return a + b" in result["body"]

    def test_arrow_function_body(self) -> None:
        code = """const double = (x) => {
    return x * 2;
};"""
        result = get_javascript_function_body(code, "double")

        assert result["function_name"] == "double"
        assert "return x * 2" in result["body"]

    def test_function_not_found(self) -> None:
        code = "function hello() {}"
        with pytest.raises(ValueError, match="not found"):
            get_javascript_function_body(code, "goodbye")


class TestListJavaScriptFunctionCalls:
    """Tests for list_javascript_function_calls."""

    def test_function_with_calls(self) -> None:
        code = """function process() {
    validate();
    transform();
    save();
}"""
        result = list_javascript_function_calls(code, "process")

        calls = json.loads(result["calls"])
        assert "validate" in calls
        assert "transform" in calls
        assert "save" in calls
        assert result["call_count"] == "3"

    def test_function_with_method_calls(self) -> None:
        code = """function process(data) {
    data.filter();
    data.map();
}"""
        result = list_javascript_function_calls(code, "process")

        calls = json.loads(result["calls"])
        assert "data.filter" in calls
        assert "data.map" in calls

    def test_function_with_no_calls(self) -> None:
        code = "function simple() { return 42; }"
        result = list_javascript_function_calls(code, "simple")

        assert result["call_count"] == "0"

    def test_function_not_found(self) -> None:
        code = "function hello() {}"
        with pytest.raises(ValueError, match="not found"):
            list_javascript_function_calls(code, "goodbye")


class TestFindJavaScriptFunctionUsages:
    """Tests for find_javascript_function_usages."""

    def test_find_usages(self) -> None:
        code = """function helper() {}
function main() {
    helper();
    helper();
}"""
        result = find_javascript_function_usages(code, "helper")

        usages = json.loads(result["usages"])
        assert len(usages) == 2
        assert result["usage_count"] == "2"

    def test_no_usages(self) -> None:
        code = """function helper() {}
function main() {}"""
        result = find_javascript_function_usages(code, "helper")

        assert result["usage_count"] == "0"

    def test_usage_details(self) -> None:
        code = """function helper() {}
function main() {
    helper();
}"""
        result = find_javascript_function_usages(code, "helper")

        details = json.loads(result["usage_details"])
        assert details[0]["context"] == "main"
        assert details[0]["type"] == "call"


class TestGetJavaScriptMethodLineNumbers:
    """Tests for get_javascript_method_line_numbers."""

    def test_find_method(self) -> None:
        code = """class Calculator {
    add(a, b) {
        return a + b;
    }
}"""
        result = get_javascript_method_line_numbers(code, "Calculator", "add")

        assert result["class_name"] == "Calculator"
        assert result["method_name"] == "add"
        assert result["start_line"] == "2"

    def test_method_not_found(self) -> None:
        code = """class Calculator {
    add(a, b) {}
}"""
        with pytest.raises(ValueError, match="Method 'subtract' not found"):
            get_javascript_method_line_numbers(code, "Calculator", "subtract")

    def test_class_not_found(self) -> None:
        code = "class Calculator {}"
        with pytest.raises(ValueError, match="Class 'NotFound' not found"):
            get_javascript_method_line_numbers(code, "NotFound", "add")


class TestGetJavaScriptClassHierarchy:
    """Tests for get_javascript_class_hierarchy."""

    def test_class_with_inheritance(self) -> None:
        code = "class Dog extends Animal {}"
        result = get_javascript_class_hierarchy(code, "Dog")

        assert result["has_inheritance"] == "true"
        base_classes = json.loads(result["base_classes"])
        assert "Animal" in base_classes
        assert result["base_count"] == "1"

    def test_class_without_inheritance(self) -> None:
        code = "class Person {}"
        result = get_javascript_class_hierarchy(code, "Person")

        assert result["has_inheritance"] == "false"
        assert result["base_count"] == "0"


class TestFindJavaScriptDefinitionsByDecorator:
    """Tests for find_javascript_definitions_by_decorator."""

    def test_find_functions_with_decorator(self) -> None:
        code = """@Component
function MyComponent() {}

@Injectable
function MyService() {}"""
        result = find_javascript_definitions_by_decorator(code, "Component")

        functions = json.loads(result["functions"])
        assert "MyComponent" in functions

    def test_find_classes_with_decorator(self) -> None:
        code = """@Entity
class User {}"""
        result = find_javascript_definitions_by_decorator(code, "Entity")

        classes = json.loads(result["classes"])
        assert "User" in classes

    def test_no_matches(self) -> None:
        code = "function plain() {}"
        result = find_javascript_definitions_by_decorator(code, "NonExistent")

        assert result["total_count"] == "0"


class TestGetJavaScriptClassDocstring:
    """Tests for get_javascript_class_docstring."""

    def test_class_with_docstring(self) -> None:
        code = """/**
 * Represents a person.
 */
class Person {}"""
        result = get_javascript_class_docstring(code, "Person")

        assert result["has_docstring"] == "true"
        assert "Represents a person" in result["docstring"]

    def test_class_without_docstring(self) -> None:
        code = "class Person {}"
        result = get_javascript_class_docstring(code, "Person")

        assert result["has_docstring"] == "false"
        assert result["docstring"] == ""

    def test_class_not_found(self) -> None:
        code = "class Person {}"
        with pytest.raises(ValueError, match="not found"):
            get_javascript_class_docstring(code, "Animal")
