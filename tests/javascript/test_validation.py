"""Tests for JavaScript/TypeScript validation module."""

import json

import pytest

from coding_open_agent_tools.javascript import validation


class TestValidateTypescriptSyntax:
    """Tests for validate_typescript_syntax function."""

    def test_invalid_type_source_code(self) -> None:
        """Test TypeError when source_code is not a string."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            validation.validate_typescript_syntax(123)  # type: ignore

    def test_empty_source_code(self) -> None:
        """Test ValueError when source_code is empty."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            validation.validate_typescript_syntax("")

    def test_valid_typescript(self) -> None:
        """Test valid TypeScript code."""
        code = """
interface User {
    name: string;
    age: number;
}

function greet(user: User): string {
    return `Hello, ${user.name}`;
}
"""
        result = validation.validate_typescript_syntax(code)
        assert result["is_valid"] == "true"
        assert result["error_message"] == ""

    def test_unmatched_brackets(self) -> None:
        """Test detection of unmatched brackets."""
        code = "function test() { return 1;"
        result = validation.validate_typescript_syntax(code)
        assert result["is_valid"] == "false"
        assert "Unclosed bracket" in result["error_message"]

    def test_interface_naming_convention(self) -> None:
        """Test interface naming convention check."""
        code = "interface user { name: string; }"
        result = validation.validate_typescript_syntax(code)
        assert result["is_valid"] == "false"
        assert "uppercase" in result["error_message"]


class TestValidateJavascriptSyntax:
    """Tests for validate_javascript_syntax function."""

    def test_invalid_type_source_code(self) -> None:
        """Test TypeError when source_code is not a string."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            validation.validate_javascript_syntax(None)  # type: ignore

    def test_empty_source_code(self) -> None:
        """Test ValueError when source_code is empty."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            validation.validate_javascript_syntax("   ")

    def test_valid_javascript(self) -> None:
        """Test valid JavaScript code."""
        code = """
function add(a, b) {
    return a + b;
}

const multiply = (x, y) => x * y;
"""
        result = validation.validate_javascript_syntax(code)
        assert result["is_valid"] == "true"

    def test_template_literals(self) -> None:
        """Test template literal handling."""
        code = "const msg = `Hello ${name}`;"
        result = validation.validate_javascript_syntax(code)
        assert result["is_valid"] == "true"

    def test_arrow_function_syntax(self) -> None:
        """Test arrow function validation."""
        code = "const func = x => { return x * 2; };"
        result = validation.validate_javascript_syntax(code)
        assert result["is_valid"] == "true"


class TestValidateJsxSyntax:
    """Tests for validate_jsx_syntax function."""

    def test_invalid_type_source_code(self) -> None:
        """Test TypeError when source_code is not a string."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            validation.validate_jsx_syntax([])  # type: ignore

    def test_empty_source_code(self) -> None:
        """Test ValueError when source_code is empty."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            validation.validate_jsx_syntax("")

    def test_valid_jsx(self) -> None:
        """Test valid JSX code."""
        code = """
function Component() {
    return (
        <div>
            <h1>Title</h1>
            <p>Content</p>
        </div>
    );
}
"""
        result = validation.validate_jsx_syntax(code)
        assert result["is_valid"] == "true"

    def test_self_closing_tags(self) -> None:
        """Test self-closing tag handling."""
        code = "<Component prop='value' />"
        result = validation.validate_jsx_syntax(code)
        assert result["is_valid"] == "true"

    def test_mismatched_jsx_tags(self) -> None:
        """Test detection of mismatched JSX tags."""
        code = "<div><span></div></span>"
        result = validation.validate_jsx_syntax(code)
        assert result["is_valid"] == "false"
        assert "Mismatched" in result["error_message"]

    def test_unclosed_jsx_tag(self) -> None:
        """Test detection of unclosed JSX tags."""
        code = "<div><span>text</span>"
        result = validation.validate_jsx_syntax(code)
        assert result["is_valid"] == "false"
        assert "Unclosed" in result["error_message"]


class TestValidatePackageJson:
    """Tests for validate_package_json function."""

    def test_invalid_type_content(self) -> None:
        """Test TypeError when content is not a string."""
        with pytest.raises(TypeError, match="content must be a string"):
            validation.validate_package_json(123)  # type: ignore

    def test_empty_content(self) -> None:
        """Test ValueError when content is empty."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            validation.validate_package_json("")

    def test_invalid_json(self) -> None:
        """Test invalid JSON syntax."""
        result = validation.validate_package_json("{invalid json")
        assert result["is_valid"] == "false"
        assert "Invalid JSON" in result["error_message"]

    def test_valid_package_json(self) -> None:
        """Test valid package.json."""
        content = json.dumps({
            "name": "test-package",
            "version": "1.0.0",
            "description": "Test package"
        })
        result = validation.validate_package_json(content)
        assert result["is_valid"] == "true"

    def test_missing_required_fields(self) -> None:
        """Test detection of missing required fields."""
        content = json.dumps({"description": "Missing name and version"})
        result = validation.validate_package_json(content)
        assert result["is_valid"] == "false"
        assert "Missing required fields" in result["error_message"]

    def test_invalid_version_format(self) -> None:
        """Test detection of invalid version format."""
        content = json.dumps({
            "name": "test",
            "version": "not-semver"
        })
        result = validation.validate_package_json(content)
        assert result["is_valid"] == "false"
        assert "Invalid version format" in result["error_message"]


class TestParseTsconfigJson:
    """Tests for parse_tsconfig_json function."""

    def test_invalid_type_content(self) -> None:
        """Test TypeError when content is not a string."""
        with pytest.raises(TypeError, match="content must be a string"):
            validation.parse_tsconfig_json(None)  # type: ignore

    def test_empty_content(self) -> None:
        """Test ValueError when content is empty."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            validation.parse_tsconfig_json("")

    def test_valid_tsconfig(self) -> None:
        """Test valid tsconfig.json parsing."""
        content = json.dumps({
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "strict": True
            }
        })
        result = validation.parse_tsconfig_json(content)
        assert result["is_valid"] == "true"
        assert result["target"] == "ES2020"
        assert result["module"] == "commonjs"
        assert result["strict_mode"] == "true"

    def test_with_comments(self) -> None:
        """Test parsing tsconfig with comments."""
        content = """{
// Comment
"compilerOptions": {
    "target": "ES2020" // Another comment
}
}"""
        result = validation.parse_tsconfig_json(content)
        assert result["is_valid"] == "true"


class TestCheckTypeDefinitions:
    """Tests for check_type_definitions function."""

    def test_invalid_type_file_content(self) -> None:
        """Test TypeError when file_content is not a string."""
        with pytest.raises(TypeError, match="file_content must be a string"):
            validation.check_type_definitions(123)  # type: ignore

    def test_empty_file_content(self) -> None:
        """Test ValueError when file_content is empty."""
        with pytest.raises(ValueError, match="file_content cannot be empty"):
            validation.check_type_definitions("")

    def test_type_definitions_with_exports(self) -> None:
        """Test type definition file with exports."""
        content = """
export interface User {
    name: string;
}

export type Status = 'active' | 'inactive';
"""
        result = validation.check_type_definitions(content)
        assert result["has_exports"] == "true"
        assert int(result["export_count"]) >= 2

    def test_ambient_declarations(self) -> None:
        """Test detection of ambient declarations."""
        content = "declare module 'my-module' { }"
        result = validation.check_type_definitions(content)
        assert result["has_ambient_declarations"] == "true"

    def test_namespace_detection(self) -> None:
        """Test namespace detection."""
        content = "namespace MyNamespace { export interface Foo {} }"
        result = validation.check_type_definitions(content)
        namespaces = json.loads(result["namespaces"])
        assert "MyNamespace" in namespaces


class TestParseModuleExports:
    """Tests for parse_module_exports function."""

    def test_invalid_type_source_code(self) -> None:
        """Test TypeError when source_code is not a string."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            validation.parse_module_exports(None)  # type: ignore

    def test_empty_source_code(self) -> None:
        """Test ValueError when source_code is empty."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            validation.parse_module_exports("")

    def test_named_exports(self) -> None:
        """Test parsing of named exports."""
        code = "export const foo = 1; export function bar() {}"
        result = validation.parse_module_exports(code)
        named = json.loads(result["named_exports"])
        assert "foo" in named
        assert "bar" in named
        assert result["has_default"] == "false"

    def test_default_export(self) -> None:
        """Test parsing of default export."""
        code = "export default class MyClass {}"
        result = validation.parse_module_exports(code)
        assert result["has_default"] == "true"
        assert result["default_export"] != ""

    def test_re_exports(self) -> None:
        """Test detection of re-exports."""
        code = "export * from './module';"
        result = validation.parse_module_exports(code)
        re_exports = json.loads(result["re_exports"])
        assert len(re_exports) > 0


class TestDetectUnusedImports:
    """Tests for detect_unused_imports function."""

    def test_invalid_type_source_code(self) -> None:
        """Test TypeError when source_code is not a string."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            validation.detect_unused_imports([])  # type: ignore

    def test_empty_source_code(self) -> None:
        """Test ValueError when source_code is empty."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            validation.detect_unused_imports("")

    def test_no_unused_imports(self) -> None:
        """Test code with all imports used."""
        code = """
import { foo } from './module';
console.log(foo);
"""
        result = validation.detect_unused_imports(code)
        assert result["has_unused"] == "false"

    def test_unused_imports_detected(self) -> None:
        """Test detection of unused imports."""
        code = """
import { foo, bar } from './module';
console.log(foo);
"""
        result = validation.detect_unused_imports(code)
        assert result["has_unused"] == "true"
        unused = json.loads(result["unused_imports"])
        assert "bar" in unused


class TestDetectCircularDependencies:
    """Tests for detect_circular_dependencies function."""

    def test_invalid_type_module_structure(self) -> None:
        """Test TypeError when module_structure is not a string."""
        with pytest.raises(TypeError, match="module_structure must be a string"):
            validation.detect_circular_dependencies(123)  # type: ignore

    def test_empty_module_structure(self) -> None:
        """Test ValueError when module_structure is empty."""
        with pytest.raises(ValueError, match="module_structure cannot be empty"):
            validation.detect_circular_dependencies("")

    def test_invalid_json(self) -> None:
        """Test ValueError for invalid JSON."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            validation.detect_circular_dependencies("{invalid}")

    def test_no_circular_dependencies(self) -> None:
        """Test modules without circular dependencies."""
        structure = json.dumps({
            "moduleA": ["moduleB"],
            "moduleB": ["moduleC"],
            "moduleC": []
        })
        result = validation.detect_circular_dependencies(structure)
        assert result["has_circular"] == "false"

    def test_circular_dependencies_detected(self) -> None:
        """Test detection of circular dependencies."""
        structure = json.dumps({
            "moduleA": ["moduleB"],
            "moduleB": ["moduleC"],
            "moduleC": ["moduleA"]
        })
        result = validation.detect_circular_dependencies(structure)
        assert result["has_circular"] == "true"
        assert int(result["cycle_count"]) > 0


class TestDetectPromiseAntiPatterns:
    """Tests for detect_promise_anti_patterns function."""

    def test_invalid_type_source_code(self) -> None:
        """Test TypeError when source_code is not a string."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            validation.detect_promise_anti_patterns(None)  # type: ignore

    def test_empty_source_code(self) -> None:
        """Test ValueError when source_code is empty."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            validation.detect_promise_anti_patterns("")

    def test_no_anti_patterns(self) -> None:
        """Test code without anti-patterns."""
        code = """
async function test() {
    try {
        const result = await fetch('/api');
        return result.json();
    } catch (error) {
        console.error(error);
    }
}
"""
        result = validation.detect_promise_anti_patterns(code)
        assert result["has_anti_patterns"] == "false"

    def test_missing_catch(self) -> None:
        """Test detection of missing .catch()."""
        code = "promise.then(result => console.log(result));"
        result = validation.detect_promise_anti_patterns(code)
        assert result["has_anti_patterns"] == "true"
        patterns = json.loads(result["anti_patterns"])
        assert any(".catch()" in p for p in patterns)

    def test_nested_promises(self) -> None:
        """Test detection of nested promises."""
        code = "promise.then().then();"
        result = validation.detect_promise_anti_patterns(code)
        assert result["has_anti_patterns"] == "true"


class TestCheckEslintConfig:
    """Tests for check_eslint_config function."""

    def test_invalid_type_config_content(self) -> None:
        """Test TypeError when config_content is not a string."""
        with pytest.raises(TypeError, match="config_content must be a string"):
            validation.check_eslint_config(123)  # type: ignore

    def test_empty_config_content(self) -> None:
        """Test ValueError when config_content is empty."""
        with pytest.raises(ValueError, match="config_content cannot be empty"):
            validation.check_eslint_config("")

    def test_valid_eslint_config(self) -> None:
        """Test valid ESLint configuration."""
        config = json.dumps({
            "extends": ["eslint:recommended"],
            "parser": "@typescript-eslint/parser",
            "rules": {
                "semi": ["error", "always"]
            }
        })
        result = validation.check_eslint_config(config)
        assert result["is_valid"] == "true"
        assert result["parser"] == "@typescript-eslint/parser"


class TestCheckAsyncAwaitUsage:
    """Tests for check_async_await_usage function."""

    def test_invalid_type_source_code(self) -> None:
        """Test TypeError when source_code is not a string."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            validation.check_async_await_usage(None)  # type: ignore

    def test_empty_source_code(self) -> None:
        """Test ValueError when source_code is empty."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            validation.check_async_await_usage("")

    def test_proper_async_await(self) -> None:
        """Test proper async/await usage."""
        code = """
async function test() {
    const result = await fetch('/api');
    return result;
}
"""
        result = validation.check_async_await_usage(code)
        assert int(result["async_function_count"]) == 1
        assert int(result["await_count"]) == 1

    def test_async_without_await(self) -> None:
        """Test detection of async function without await."""
        code = """
async function test() {
    return 42;
}
"""
        result = validation.check_async_await_usage(code)
        issues = json.loads(result["issues"])
        assert any("without await" in issue for issue in issues)
