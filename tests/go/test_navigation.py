"""Tests for Go code navigation and analysis functions."""

import pytest

from coding_open_agent_tools.go.navigation import (
    extract_go_public_api,
    find_go_definitions_by_comment,
    find_go_function_usages,
    get_go_function_body,
    get_go_function_details,
    get_go_function_docstring,
    get_go_function_line_numbers,
    get_go_function_signature,
    get_go_module_overview,
    get_go_specific_function_line_numbers,
    get_go_type_docstring,
    get_go_type_hierarchy,
    get_go_type_line_numbers,
    list_go_function_calls,
    list_go_functions,
    list_go_type_methods,
    list_go_types,
)

# Skip all tests if tree-sitter-language-pack is not installed
pytest_plugins = []

try:
    from tree_sitter_language_pack import get_parser

    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not TREE_SITTER_AVAILABLE,
    reason="tree-sitter-language-pack not installed",
)


class TestGetGoFunctionLineNumbers:
    """Test get_go_function_line_numbers function."""

    def test_simple_function(self) -> None:
        """Test finding line numbers for a simple function."""
        code = """package main

func HelloWorld() {
    println("Hello, World!")
}"""
        result = get_go_function_line_numbers(code, "HelloWorld")
        assert result["start_line"] == "3"
        assert result["end_line"] == "5"
        assert result["function_name"] == "HelloWorld"
        assert result["is_method"] == "false"

    def test_method_with_receiver(self) -> None:
        """Test finding line numbers for a method with receiver."""
        code = """package main

type Person struct {
    Name string
}

func (p *Person) GetName() string {
    return p.Name
}"""
        result = get_go_function_line_numbers(code, "GetName")
        assert result["start_line"] == "7"
        assert result["end_line"] == "9"
        assert result["is_method"] == "true"

    def test_function_with_params(self) -> None:
        """Test finding line numbers for a function with parameters."""
        code = """package main

func Add(a int, b int) int {
    return a + b
}"""
        result = get_go_function_line_numbers(code, "Add")
        assert result["start_line"] == "3"
        assert result["end_line"] == "5"

    def test_function_not_found(self) -> None:
        """Test error when function doesn't exist."""
        code = """package main

func HelloWorld() {}"""
        with pytest.raises(ValueError, match="Function 'goodbye' not found"):
            get_go_function_line_numbers(code, "goodbye")

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            get_go_function_line_numbers("", "test")

    def test_invalid_type(self) -> None:
        """Test behavior with non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            get_go_function_line_numbers(123, "test")  # type: ignore[arg-type]


class TestGetGoTypeLineNumbers:
    """Test get_go_type_line_numbers function."""

    def test_struct_type(self) -> None:
        """Test finding line numbers for a struct type."""
        code = """package main

type Person struct {
    Name string
    Age  int
}"""
        result = get_go_type_line_numbers(code, "Person")
        assert result["start_line"] == "3"
        assert result["end_line"] == "6"
        assert result["type_name"] == "Person"

    def test_interface_type(self) -> None:
        """Test finding line numbers for an interface type."""
        code = """package main

type Reader interface {
    Read() ([]byte, error)
}"""
        result = get_go_type_line_numbers(code, "Reader")
        assert result["start_line"] == "3"
        assert result["end_line"] == "5"

    def test_type_alias(self) -> None:
        """Test finding line numbers for a type alias."""
        code = """package main

type MyInt int"""
        result = get_go_type_line_numbers(code, "MyInt")
        assert result["start_line"] == "3"
        assert result["end_line"] == "3"

    def test_type_not_found(self) -> None:
        """Test error when type doesn't exist."""
        code = """package main

type Person struct {}"""
        with pytest.raises(ValueError, match="Type 'Missing' not found"):
            get_go_type_line_numbers(code, "Missing")

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            get_go_type_line_numbers("", "test")

    def test_invalid_type(self) -> None:
        """Test behavior with non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            get_go_type_line_numbers(123, "test")  # type: ignore[arg-type]


class TestGetGoModuleOverview:
    """Test get_go_module_overview function."""

    def test_simple_overview(self) -> None:
        """Test overview for a simple Go file."""
        code = """package main

import "fmt"

// HelloWorld says hello to the world
func HelloWorld() {
    fmt.Println("Hello, World!")
}

type Person struct {
    Name string
}"""
        result = get_go_module_overview(code)
        assert result["has_package"] == "true"
        assert result["has_imports"] == "true"
        assert result["function_count"] == "1"
        assert result["type_count"] == "1"
        assert "HelloWorld" in result["function_names"]
        assert "Person" in result["type_names"]

    def test_multiple_functions_and_types(self) -> None:
        """Test overview with multiple functions and types."""
        code = """package main

func First() {}
func Second() {}

type TypeA struct {}
type TypeB struct {}"""
        result = get_go_module_overview(code)
        assert result["function_count"] == "2"
        assert result["type_count"] == "2"
        assert result["method_count"] == "0"

    def test_empty_file(self) -> None:
        """Test overview of empty file."""
        code = """package main

// Empty file"""
        result = get_go_module_overview(code)
        assert result["function_count"] == "0"
        assert result["method_count"] == "0"
        assert result["type_count"] == "0"


class TestListGoFunctions:
    """Test list_go_functions function."""

    def test_list_functions(self) -> None:
        """Test listing all functions in a file."""
        import json

        code = """package main

func PublicFunc() {}

func privateFunc() {}

func Add(a int, b int) int {
    return a + b
}"""
        result = list_go_functions(code)
        assert result["function_count"] == "3"
        functions = json.loads(result["functions"])
        function_names = [f["name"] for f in functions]
        assert "PublicFunc" in function_names
        assert "privateFunc" in function_names
        assert "Add" in function_names

    def test_public_vs_private(self) -> None:
        """Test public vs private function detection."""
        import json

        code = """package main

func PublicFunc() {}
func privateFunc() {}"""
        result = list_go_functions(code)
        functions = json.loads(result["functions"])
        public_funcs = [f for f in functions if f["is_public"]]
        private_funcs = [f for f in functions if not f["is_public"]]
        assert len(public_funcs) == 1
        assert len(private_funcs) == 1

    def test_no_functions(self) -> None:
        """Test file with no functions."""
        code = """package main

type Person struct {
    Name string
}"""
        result = list_go_functions(code)
        assert result["function_count"] == "0"
        assert result["functions"] == "[]"

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            list_go_functions("")


class TestListGoTypes:
    """Test list_go_types function."""

    def test_list_types(self) -> None:
        """Test listing all types in a file."""
        import json

        code = """package main

type Person struct {
    Name string
}

type Reader interface {
    Read() []byte
}

type MyInt int"""
        result = list_go_types(code)
        assert result["type_count"] == "3"
        types = json.loads(result["types"])
        type_names = [t["name"] for t in types]
        assert "Person" in type_names
        assert "Reader" in type_names
        assert "MyInt" in type_names

    def test_type_kinds(self) -> None:
        """Test detecting different type kinds."""
        import json

        code = """package main

type Person struct {
    Name string
}

type Reader interface {
    Read() []byte
}

type MyInt int"""
        result = list_go_types(code)
        types = json.loads(result["types"])
        kinds = {t["name"]: t["kind"] for t in types}
        assert kinds["Person"] == "struct"
        assert kinds["Reader"] == "interface"
        assert kinds["MyInt"] == "alias"

    def test_public_vs_private_types(self) -> None:
        """Test public vs private type detection."""
        import json

        code = """package main

type PublicType struct {}
type privateType struct {}"""
        result = list_go_types(code)
        types = json.loads(result["types"])
        public_types = [t for t in types if t["is_public"]]
        private_types = [t for t in types if not t["is_public"]]
        assert len(public_types) == 1
        assert len(private_types) == 1


class TestGetGoFunctionSignature:
    """Test get_go_function_signature function."""

    def test_simple_signature(self) -> None:
        """Test extracting a simple function signature."""
        code = """package main

func HelloWorld() {
    println("Hello!")
}"""
        result = get_go_function_signature(code, "HelloWorld")
        assert result["function_name"] == "HelloWorld"
        assert "func HelloWorld()" in result["signature"]
        assert result["is_public"] == "true"

    def test_signature_with_params(self) -> None:
        """Test extracting a function signature with parameters."""
        code = """package main

func Add(a int, b int) int {
    return a + b
}"""
        result = get_go_function_signature(code, "Add")
        assert result["function_name"] == "Add"
        assert "int" in result["params"]

    def test_method_signature(self) -> None:
        """Test extracting a method signature with receiver."""
        code = """package main

type Person struct {
    Name string
}

func (p *Person) GetName() string {
    return p.Name
}"""
        result = get_go_function_signature(code, "GetName")
        assert result["function_name"] == "GetName"
        assert "string" in result["returns"]

    def test_function_not_found(self) -> None:
        """Test error for non-existent function."""
        code = """package main

func HelloWorld() {}"""
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            get_go_function_signature(code, "missing")

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            get_go_function_signature("", "test")


class TestGetGoFunctionDocstring:
    """Test get_go_function_docstring function."""

    def test_godoc_comment(self) -> None:
        """Test extracting godoc comment."""
        code = """package main

// HelloWorld says hello to the world.
// It prints a greeting message.
func HelloWorld() {
    println("Hello!")
}"""
        result = get_go_function_docstring(code, "HelloWorld")
        assert result["function_name"] == "HelloWorld"
        assert "says hello to the world" in result["docstring"]
        assert result["has_docstring"] == "true"

    def test_multiline_godoc(self) -> None:
        """Test extracting multiline godoc comment."""
        code = """package main

/*
Add adds two integers together.
It returns the sum of a and b.
*/
func Add(a int, b int) int {
    return a + b
}"""
        result = get_go_function_docstring(code, "Add")
        assert result["function_name"] == "Add"
        assert "adds two integers" in result["docstring"]
        assert result["has_docstring"] == "true"

    def test_no_godoc(self) -> None:
        """Test function without godoc."""
        code = """package main

func HelloWorld() {}"""
        result = get_go_function_docstring(code, "HelloWorld")
        assert result["docstring"] == ""
        assert result["has_docstring"] == "false"

    def test_function_not_found(self) -> None:
        """Test error for non-existent function."""
        code = """package main

func HelloWorld() {}"""
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            get_go_function_docstring(code, "missing")


class TestListGoTypeMethods:
    """Test list_go_type_methods function."""

    def test_list_type_methods(self) -> None:
        """Test listing methods of a specific type."""
        import json

        code = """package main

type Person struct {
    Name string
}

func (p *Person) GetName() string {
    return p.Name
}

func (p *Person) SetName(name string) {
    p.Name = name
}

type Other struct {}

func (o *Other) OtherMethod() {}"""
        result = list_go_type_methods(code, "Person")
        assert result["type_name"] == "Person"
        assert result["method_count"] == "2"
        methods = json.loads(result["methods"])
        method_names = [m["name"] for m in methods]
        assert "GetName" in method_names
        assert "SetName" in method_names
        assert "OtherMethod" not in method_names

    def test_value_and_pointer_receivers(self) -> None:
        """Test methods with both value and pointer receivers."""

        code = """package main

type Counter struct {
    count int
}

func (c Counter) GetCount() int {
    return c.count
}

func (c *Counter) Increment() {
    c.count++
}"""
        result = list_go_type_methods(code, "Counter")
        assert result["method_count"] == "2"

    def test_type_not_found(self) -> None:
        """Test error for non-existent type."""
        code = """package main

type Person struct {}

func (p *Person) Method() {}"""
        with pytest.raises(ValueError, match="Type 'Missing' not found"):
            list_go_type_methods(code, "Missing")

    def test_type_with_no_methods(self) -> None:
        """Test type with no methods."""
        code = """package main

type Person struct {
    Name string
}"""
        result = list_go_type_methods(code, "Person")
        assert result["method_count"] == "0"


class TestExtractGoPublicApi:
    """Test extract_go_public_api function."""

    def test_public_api(self) -> None:
        """Test extracting public API."""
        import json

        code = """package main

func PublicFunc() {}

func privateFunc() {}

type PublicType struct {}

type privateType struct {}"""
        result = extract_go_public_api(code)
        public_functions = json.loads(result["public_functions"])
        public_types = json.loads(result["public_types"])
        assert "PublicFunc" in public_functions
        assert "privateFunc" not in public_functions
        assert "PublicType" in public_types
        assert "privateType" not in public_types

    def test_public_methods(self) -> None:
        """Test that public methods are included."""
        import json

        code = """package main

type Person struct {}

func (p *Person) PublicMethod() {}

func (p *Person) privateMethod() {}"""
        result = extract_go_public_api(code)
        public_functions = json.loads(result["public_functions"])
        assert "PublicMethod" in public_functions
        assert "privateMethod" not in public_functions

    def test_empty_file(self) -> None:
        """Test extracting public API from empty file."""
        code = """package main"""
        result = extract_go_public_api(code)
        assert result["public_count"] == "0"


class TestGetGoFunctionDetails:
    """Test get_go_function_details function."""

    def test_function_details(self) -> None:
        """Test getting comprehensive function details."""
        code = """package main

// Add adds two integers together.
func Add(a int, b int) int {
    return a + b
}"""
        result = get_go_function_details(code, "Add")
        assert result["function_name"] == "Add"
        assert "int" in result["params"]
        assert result["is_public"] == "true"
        assert "adds two integers" in result["docstring"]
        assert result["line"] == "4"

    def test_method_details(self) -> None:
        """Test getting method details."""
        code = """package main

type Person struct {
    Name string
}

// GetName returns the person's name.
func (p *Person) GetName() string {
    return p.Name
}"""
        result = get_go_function_details(code, "GetName")
        assert result["function_name"] == "GetName"
        assert "string" in result["returns"]
        assert "person's name" in result["docstring"]

    def test_function_not_found(self) -> None:
        """Test error for non-existent function."""
        code = """package main

func HelloWorld() {}"""
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            get_go_function_details(code, "missing")


class TestGetGoFunctionBody:
    """Test get_go_function_body function."""

    def test_simple_body(self) -> None:
        """Test extracting function body."""
        code = """package main

func Add(a int, b int) int {
    return a + b
}"""
        result = get_go_function_body(code, "Add")
        assert result["function_name"] == "Add"
        assert "return a + b" in result["body"]

    def test_multiline_body(self) -> None:
        """Test extracting multiline function body."""
        code = """package main

func Process() {
    x := 5
    y := 10
    println(x + y)
}"""
        result = get_go_function_body(code, "Process")
        assert "x := 5" in result["body"]
        assert "y := 10" in result["body"]
        assert "println" in result["body"]

    def test_method_body(self) -> None:
        """Test extracting method body."""
        code = """package main

type Person struct {
    Name string
}

func (p *Person) SetName(name string) {
    p.Name = name
}"""
        result = get_go_function_body(code, "SetName")
        assert "p.Name = name" in result["body"]

    def test_function_not_found(self) -> None:
        """Test error for non-existent function."""
        code = """package main

func HelloWorld() {}"""
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            get_go_function_body(code, "missing")


class TestListGoFunctionCalls:
    """Test list_go_function_calls function."""

    def test_function_calls(self) -> None:
        """Test listing function calls in a function."""
        import json

        code = """package main

func Process() {
    helper1()
    helper2()
    println("done")
}

func helper1() {}
func helper2() {}"""
        result = list_go_function_calls(code, "Process")
        calls = json.loads(result["calls"])
        assert "helper1" in calls
        assert "helper2" in calls
        assert "println" in calls

    def test_no_calls(self) -> None:
        """Test function with no calls."""
        code = """package main

func GetValue() int {
    return 42
}"""
        result = list_go_function_calls(code, "GetValue")
        assert result["call_count"] == "0"

    def test_method_calls(self) -> None:
        """Test function with method calls."""
        import json

        code = """package main

type Person struct {
    Name string
}

func Process(p *Person) {
    name := p.GetName()
    println(name)
}"""
        result = list_go_function_calls(code, "Process")
        calls = json.loads(result["calls"])
        assert result["call_count"] == "2"

    def test_function_not_found(self) -> None:
        """Test error for non-existent function."""
        code = """package main

func HelloWorld() {}"""
        with pytest.raises(ValueError, match="Function 'missing' not found"):
            list_go_function_calls(code, "missing")


class TestFindGoFunctionUsages:
    """Test find_go_function_usages function."""

    def test_find_usages(self) -> None:
        """Test finding function usages."""
        import json

        code = """package main

func caller1() {
    target()
}

func caller2() {
    target()
}

func target() {}"""
        result = find_go_function_usages(code, "target")
        assert result["usage_count"] == "2"
        usages = json.loads(result["usages"])
        assert len(usages) == 2

    def test_no_usages(self) -> None:
        """Test function with no usages."""
        code = """package main

func unused() {}
func other() {}"""
        result = find_go_function_usages(code, "unused")
        assert result["usage_count"] == "0"

    def test_package_qualified_call(self) -> None:
        """Test finding package-qualified function calls."""
        import json

        code = """package main

import "fmt"

func Process() {
    fmt.Println("hello")
}"""
        result = find_go_function_usages(code, "Println")
        usages = json.loads(result["usages"])
        assert len(usages) == 1

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            find_go_function_usages("", "test")


class TestGetGoSpecificFunctionLineNumbers:
    """Test get_go_specific_function_line_numbers function."""

    def test_method_in_specific_type(self) -> None:
        """Test finding method in a specific type."""
        code = """package main

type Person struct {
    Name string
}

func (p *Person) GetName() string {
    return p.Name
}

type Other struct {}

func (o *Other) GetName() string {
    return "other"
}"""
        result = get_go_specific_function_line_numbers(code, "Person", "GetName")
        assert result["start_line"] == "7"
        assert result["end_line"] == "9"
        assert result["package_name"] == "Person"
        assert result["function_name"] == "GetName"

    def test_method_in_second_type(self) -> None:
        """Test finding method in second type."""
        code = """package main

type First struct {}

func (f *First) Method() {}

type Second struct {}

func (s *Second) Method() {}"""
        result = get_go_specific_function_line_numbers(code, "Second", "Method")
        assert result["start_line"] == "9"
        assert result["function_name"] == "Method"

    def test_type_not_found(self) -> None:
        """Test error when type not found."""
        code = """package main

type Person struct {}

func (p *Person) GetName() string {
    return ""
}"""
        with pytest.raises(ValueError, match="Type 'Missing' not found"):
            get_go_specific_function_line_numbers(code, "Missing", "GetName")

    def test_method_not_found(self) -> None:
        """Test error when method not found for type."""
        code = """package main

type Person struct {}

func (p *Person) GetName() string {
    return ""
}"""
        with pytest.raises(
            ValueError, match="Method 'SetName' not found for type 'Person'"
        ):
            get_go_specific_function_line_numbers(code, "Person", "SetName")


class TestGetGoTypeHierarchy:
    """Test get_go_type_hierarchy function."""

    def test_struct_embedding(self) -> None:
        """Test struct with embedded types."""
        import json

        code = """package main

type Base struct {
    ID int
}

type Person struct {
    Base
    Name string
}"""
        result = get_go_type_hierarchy(code, "Person")
        assert result["type_name"] == "Person"
        assert result["has_embedding"] == "true"
        embeds = json.loads(result["embeds"])
        assert "Base" in embeds

    def test_no_embedding(self) -> None:
        """Test struct with no embedding."""
        code = """package main

type Person struct {
    Name string
}"""
        result = get_go_type_hierarchy(code, "Person")
        assert result["has_embedding"] == "false"
        assert result["embeds"] == "[]"

    def test_interface_type(self) -> None:
        """Test interface type hierarchy."""
        code = """package main

type Reader interface {
    Read() []byte
}"""
        result = get_go_type_hierarchy(code, "Reader")
        assert result["type_name"] == "Reader"

    def test_type_not_found(self) -> None:
        """Test error for non-existent type."""
        code = """package main

type Person struct {}"""
        with pytest.raises(ValueError, match="Type 'Missing' not found"):
            get_go_type_hierarchy(code, "Missing")


class TestFindGoDefinitionsByComment:
    """Test find_go_definitions_by_comment function."""

    def test_find_by_comment_pattern(self) -> None:
        """Test finding definitions with matching comments."""
        import json

        code = """package main

// Add performs addition of two integers.
func Add(a int, b int) int {
    return a + b
}

// Subtract performs subtraction.
func Subtract(a int, b int) int {
    return a - b
}

// Multiply multiplies two numbers.
func Multiply(a int, b int) int {
    return a * b
}"""
        result = find_go_definitions_by_comment(code, "performs")
        functions = json.loads(result["functions"])
        assert "Add" in functions
        assert "Subtract" in functions
        assert "Multiply" not in functions

    def test_find_type_by_comment(self) -> None:
        """Test finding types with matching comments."""
        import json

        code = """package main

// Person represents a user of the system.
type Person struct {
    Name string
}

// Counter counts things.
type Counter struct {
    count int
}"""
        result = find_go_definitions_by_comment(code, "represents")
        types = json.loads(result["types"])
        assert "Person" in types
        assert "Counter" not in types

    def test_case_insensitive_search(self) -> None:
        """Test case-insensitive comment search."""
        import json

        code = """package main

// DEPRECATED: Use NewVersion instead.
func OldFunc() {}

// Deprecated: Use Better instead.
func AnotherOld() {}"""
        result = find_go_definitions_by_comment(code, "deprecated")
        functions = json.loads(result["functions"])
        assert len(functions) == 2

    def test_no_matches(self) -> None:
        """Test no matches found."""
        code = """package main

// Add two numbers.
func Add(a int, b int) int {
    return a + b
}"""
        result = find_go_definitions_by_comment(code, "nonexistent")
        assert result["total_count"] == "0"

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            find_go_definitions_by_comment("", "test")


class TestGetGoTypeDocstring:
    """Test get_go_type_docstring function."""

    def test_type_godoc(self) -> None:
        """Test extracting type godoc."""
        code = """package main

// Person represents a user in the system.
// It contains personal information.
type Person struct {
    Name string
}"""
        result = get_go_type_docstring(code, "Person")
        assert result["type_name"] == "Person"
        assert "represents a user" in result["docstring"]
        assert result["has_docstring"] == "true"

    def test_no_godoc(self) -> None:
        """Test type without godoc."""
        code = """package main

type Person struct {
    Name string
}"""
        result = get_go_type_docstring(code, "Person")
        assert result["docstring"] == ""
        assert result["has_docstring"] == "false"

    def test_interface_godoc(self) -> None:
        """Test extracting interface godoc."""
        code = """package main

// Reader reads data from a source.
type Reader interface {
    Read() []byte
}"""
        result = get_go_type_docstring(code, "Reader")
        assert "reads data" in result["docstring"]

    def test_type_not_found(self) -> None:
        """Test error for non-existent type."""
        code = """package main

type Person struct {}"""
        with pytest.raises(ValueError, match="Type 'Missing' not found"):
            get_go_type_docstring(code, "Missing")

    def test_empty_code(self) -> None:
        """Test behavior with empty code."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            get_go_type_docstring("", "test")
