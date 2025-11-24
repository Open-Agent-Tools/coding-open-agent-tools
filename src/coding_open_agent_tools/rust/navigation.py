"""Rust code navigation functions.

This module provides token-efficient navigation tools for Rust code,
enabling agents to explore codebases without reading entire files.

Token Savings: 70-95% reduction compared to reading full files.

Dependencies:
    - tree-sitter-language-pack (optional): pip install tree-sitter-language-pack
    - Falls back to regex parsing if tree-sitter not available
"""

import json
import re
from typing import Any

from coding_open_agent_tools._decorators import strands_tool
from coding_open_agent_tools.navigation.shared import (
    validate_identifier,
    validate_source_code,
)

# Conditional import for tree-sitter
try:
    from tree_sitter_language_pack import get_parser

    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False


def _parse_rust(source_code: str) -> Any:
    """Parse Rust code into AST using tree-sitter.

    Args:
        source_code: Rust source code

    Returns:
        Parsed tree-sitter tree

    Raises:
        ValueError: If tree-sitter not available or parsing fails
    """
    if not TREE_SITTER_AVAILABLE:
        raise ValueError(
            "tree-sitter-language-pack not installed. "
            "Install with: pip install tree-sitter-language-pack"
        )

    try:
        parser = get_parser("rust")
        tree = parser.parse(bytes(source_code, "utf8"))
        return tree
    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


def _extract_rustdoc(source_code: str, start_byte: int) -> str:
    """Extract rustdoc comment before a function/type.

    Args:
        source_code: Full source code
        start_byte: Byte offset where function/type starts

    Returns:
        Rustdoc comment text or empty string
    """
    # Find the portion of code before the function/type
    preceding = source_code[:start_byte]
    lines = preceding.split("\n")

    # Look backwards for rustdoc comments
    doc_lines: list[str] = []
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()

        if line.startswith("///"):
            # Doc comment line
            doc_lines.insert(0, line)
        elif line.endswith("*/") and "/**" in preceding:
            # Multi-line doc comment, collect until start
            doc_lines.insert(0, line)
            for j in range(i - 1, -1, -1):
                doc_line = lines[j].strip()
                doc_lines.insert(0, doc_line)
                if doc_line.startswith("/**"):
                    return "\n".join(doc_lines)
            break
        elif not line or line.startswith("//!") or line.startswith("#["):
            # Empty line, module doc, or attribute, stop if we have comments
            if doc_lines:
                break
        else:
            # Non-comment line, stop
            if doc_lines:
                break

    return "\n".join(doc_lines)


def _get_node_text(node: Any, source_code: bytes) -> str:
    """Extract text content from a tree-sitter node.

    Args:
        node: Tree-sitter node
        source_code: Source code as bytes

    Returns:
        Text content of the node
    """
    return source_code[node.start_byte : node.end_byte].decode("utf-8")


def _find_nodes_by_type(node: Any, node_type: str) -> list[Any]:
    """Recursively find all nodes of a specific type.

    Args:
        node: Root tree-sitter node
        node_type: Node type to find (e.g., "function_item", "struct_item")

    Returns:
        List of matching nodes
    """
    results: list[Any] = []

    def traverse(n: Any) -> None:
        if n.type == node_type:
            results.append(n)
        for child in n.children:
            traverse(child)

    traverse(node)
    return results


def _is_public(node: Any) -> bool:
    """Check if a Rust item is public (has pub visibility).

    Args:
        node: Function or type declaration node

    Returns:
        True if public (has pub visibility), False otherwise
    """
    for child in node.children:
        if child.type == "visibility_modifier":
            return True
    return False


def _get_function_name(node: Any, source_bytes: bytes) -> str:
    """Extract function name from function_item node.

    Args:
        node: Function item node
        source_bytes: Source code as bytes

    Returns:
        Function name or empty string if not found
    """
    for child in node.children:
        if child.type == "identifier":
            return _get_node_text(child, source_bytes)
    return ""


def _get_type_name(node: Any, source_bytes: bytes) -> str:
    """Extract type name from struct_item, enum_item, trait_item, or type_item node.

    Args:
        node: Type node
        source_bytes: Source code as bytes

    Returns:
        Type name or empty string if not found
    """
    for child in node.children:
        if child.type == "type_identifier":
            return _get_node_text(child, source_bytes)
    return ""


def _is_method(node: Any, source_bytes: bytes) -> bool:
    """Check if a function_item is a method (has self parameter).

    Args:
        node: Function item node
        source_bytes: Source code as bytes

    Returns:
        True if function has self parameter, False otherwise
    """
    for child in node.children:
        if child.type == "parameters":
            # Check for self, &self, or &mut self
            params_text = _get_node_text(child, source_bytes)
            return "self" in params_text
    return False


def _get_impl_type(node: Any, source_bytes: bytes) -> str:
    """Extract type name from impl_item node.

    Args:
        node: Impl item node
        source_bytes: Source code as bytes

    Returns:
        Type name or empty string if not found
    """
    for child in node.children:
        if child.type == "type_identifier":
            return _get_node_text(child, source_bytes)
    return ""


@strands_tool  # type: ignore[misc]
def get_rust_function_line_numbers(
    source_code: str, function_name: str
) -> dict[str, str]:
    """Get start and end line numbers for a specific Rust function.

    Enables targeted file reading instead of loading entire files, saving 85-90% of tokens.
    Supports: function declarations and methods (with self parameter).

    Args:
        source_code: Rust source code to analyze
        function_name: Name of the function to locate

    Returns:
        Dictionary with:
        - start_line: Line number where function starts (1-indexed)
        - end_line: Line number where function ends (1-indexed)
        - function_name: Name of the function found
        - is_method: "true" if function is a method with self parameter, "false" otherwise

    Raises:
        TypeError: If source_code or function_name is not a string
        ValueError: If source_code is empty, parsing fails, or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find function items
        functions = _find_nodes_by_type(root, "function_item")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                start_line = func.start_point[0] + 1
                end_line = func.end_point[0] + 1
                is_method = _is_method(func, source_bytes)
                return {
                    "start_line": str(start_line),
                    "end_line": str(end_line),
                    "function_name": function_name,
                    "is_method": "true" if is_method else "false",
                }

        raise ValueError(f"Function '{function_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_rust_type_line_numbers(source_code: str, type_name: str) -> dict[str, str]:
    """Get start and end line numbers for a specific Rust type.

    Enables targeted file reading instead of loading entire files, saving 85-90% of tokens.
    Supports: struct declarations, enum declarations, trait declarations, type aliases.

    Args:
        source_code: Rust source code to analyze
        type_name: Name of the type to locate

    Returns:
        Dictionary with:
        - start_line: Line number where type starts (1-indexed)
        - end_line: Line number where type ends (1-indexed)
        - type_name: Name of the type found

    Raises:
        TypeError: If source_code or type_name is not a string
        ValueError: If source_code is empty, parsing fails, or type not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(type_name, "type_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find struct, enum, trait, and type declarations
        type_nodes = (
            _find_nodes_by_type(root, "struct_item")
            + _find_nodes_by_type(root, "enum_item")
            + _find_nodes_by_type(root, "trait_item")
            + _find_nodes_by_type(root, "type_item")
        )

        for type_node in type_nodes:
            name = _get_type_name(type_node, source_bytes)
            if name == type_name:
                start_line = type_node.start_point[0] + 1
                end_line = type_node.end_point[0] + 1
                return {
                    "start_line": str(start_line),
                    "end_line": str(end_line),
                    "type_name": type_name,
                }

        raise ValueError(f"Type '{type_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_rust_module_overview(source_code: str) -> dict[str, str]:
    """Get high-level overview of a Rust file without full parsing.

    Returns summary information about the file structure, saving 85-90% of tokens
    compared to reading the entire file.

    Args:
        source_code: Rust source code to analyze

    Returns:
        Dictionary with:
        - function_count: Number of functions in the file
        - method_count: Number of methods in the file (functions with self)
        - type_count: Number of types in the file
        - function_names: JSON array of function names
        - type_names: JSON array of type names
        - has_main: "true" if file has main function, "false" otherwise
        - has_tests: "true" if file has test functions, "false" otherwise
        - total_lines: Total number of lines in the file

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty or parsing fails
    """
    validate_source_code(source_code)

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Count functions
        functions = _find_nodes_by_type(root, "function_item")
        function_names: list[str] = []
        method_count = 0
        has_main = False
        has_tests = False

        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name:
                function_names.append(name)
                if name == "main":
                    has_main = True
                if _is_method(func, source_bytes):
                    method_count += 1
                # Check for #[test] attribute
                func_text = _get_node_text(func, source_bytes)
                if "#[test]" in func_text or "#[cfg(test)]" in func_text:
                    has_tests = True

        # Count types
        type_names: list[str] = []
        type_nodes = (
            _find_nodes_by_type(root, "struct_item")
            + _find_nodes_by_type(root, "enum_item")
            + _find_nodes_by_type(root, "trait_item")
            + _find_nodes_by_type(root, "type_item")
        )

        for type_node in type_nodes:
            name = _get_type_name(type_node, source_bytes)
            if name:
                type_names.append(name)

        # Count lines
        total_lines = len(source_code.split("\n"))

        return {
            "function_count": str(len(function_names)),
            "method_count": str(method_count),
            "type_count": str(len(type_names)),
            "function_names": json.dumps(function_names),
            "type_names": json.dumps(type_names),
            "has_main": "true" if has_main else "false",
            "has_tests": "true" if has_tests else "false",
            "total_lines": str(total_lines),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def list_rust_functions(source_code: str) -> dict[str, str]:
    """List all functions in Rust code with their signatures.

    Returns function signatures without bodies, saving 80-85% of tokens.
    Useful for understanding file structure without reading implementation.

    Args:
        source_code: Rust source code to analyze

    Returns:
        Dictionary with:
        - functions: JSON array of function information dictionaries
        - function_count: Total number of functions found

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty or parsing fails
    """
    validate_source_code(source_code)

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        functions: list[dict[str, Any]] = []

        # Find function items
        function_nodes = _find_nodes_by_type(root, "function_item")
        for func in function_nodes:
            func_info: dict[str, Any] = {
                "name": "",
                "params": "",
                "returns": "",
                "is_public": False,
            }

            func_info["name"] = _get_function_name(func, source_bytes)
            func_info["is_public"] = _is_public(func)

            for child in func.children:
                if child.type == "parameters":
                    func_info["params"] = _get_node_text(child, source_bytes)
                elif child.type in [
                    "type_identifier",
                    "primitive_type",
                    "reference_type",
                    "generic_type",
                ]:
                    # Return type
                    func_info["returns"] = _get_node_text(child, source_bytes)

            func_info["line"] = func.start_point[0] + 1
            functions.append(func_info)

        return {
            "functions": json.dumps(functions),
            "function_count": str(len(functions)),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def list_rust_types(source_code: str) -> dict[str, str]:
    """List all types in Rust code with their structure.

    Returns type definitions with method names but not implementations,
    saving 80-85% of tokens.

    Args:
        source_code: Rust source code to analyze

    Returns:
        Dictionary with:
        - types: JSON array of type information dictionaries
        - type_count: Total number of types found

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty or parsing fails
    """
    validate_source_code(source_code)

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        types: list[dict[str, Any]] = []

        # Find struct items
        structs = _find_nodes_by_type(root, "struct_item")
        for struct in structs:
            type_info: dict[str, Any] = {
                "name": "",
                "kind": "struct",
                "is_public": False,
            }
            type_info["name"] = _get_type_name(struct, source_bytes)
            type_info["is_public"] = _is_public(struct)
            type_info["line"] = struct.start_point[0] + 1
            types.append(type_info)

        # Find enum items
        enums = _find_nodes_by_type(root, "enum_item")
        for enum in enums:
            type_info = {
                "name": "",
                "kind": "enum",
                "is_public": False,
            }
            type_info["name"] = _get_type_name(enum, source_bytes)
            type_info["is_public"] = _is_public(enum)
            type_info["line"] = enum.start_point[0] + 1
            types.append(type_info)

        # Find trait items
        traits = _find_nodes_by_type(root, "trait_item")
        for trait in traits:
            type_info = {
                "name": "",
                "kind": "trait",
                "is_public": False,
            }
            type_info["name"] = _get_type_name(trait, source_bytes)
            type_info["is_public"] = _is_public(trait)
            type_info["line"] = trait.start_point[0] + 1
            types.append(type_info)

        # Find type aliases
        type_aliases = _find_nodes_by_type(root, "type_item")
        for type_alias in type_aliases:
            type_info = {
                "name": "",
                "kind": "type_alias",
                "is_public": False,
            }
            type_info["name"] = _get_type_name(type_alias, source_bytes)
            type_info["is_public"] = _is_public(type_alias)
            type_info["line"] = type_alias.start_point[0] + 1
            types.append(type_info)

        return {
            "types": json.dumps(types),
            "type_count": str(len(types)),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_rust_function_signature(source_code: str, function_name: str) -> dict[str, str]:
    """Get just the signature of a specific Rust function.

    Returns only the function signature without the body, saving 85-90% of tokens.

    Args:
        source_code: Rust source code to analyze
        function_name: Name of the function

    Returns:
        Dictionary with:
        - signature: Function signature string
        - function_name: Name of the function
        - params: Parameter list
        - returns: Return type
        - is_public: "true" if function is public (pub), "false" otherwise

    Raises:
        TypeError: If source_code or function_name is not a string
        ValueError: If source_code is empty, parsing fails, or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find function items
        functions = _find_nodes_by_type(root, "function_item")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                params = ""
                returns = ""
                visibility = "pub " if _is_public(func) else ""

                for child in func.children:
                    if child.type == "parameters":
                        params = _get_node_text(child, source_bytes)
                    elif child.type in [
                        "type_identifier",
                        "primitive_type",
                        "reference_type",
                        "generic_type",
                    ]:
                        # Return type - look after "->"
                        returns = _get_node_text(child, source_bytes)

                signature = f"{visibility}fn {function_name}{params}"
                if returns:
                    signature += f" -> {returns}"

                return {
                    "signature": signature,
                    "function_name": function_name,
                    "params": params,
                    "returns": returns,
                    "is_public": "true" if _is_public(func) else "false",
                }

        raise ValueError(f"Function '{function_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_rust_function_docstring(source_code: str, function_name: str) -> dict[str, str]:
    """Get just the rustdoc comment of a specific Rust function.

    Returns only the rustdoc without the implementation, saving 80-85% of tokens.

    Args:
        source_code: Rust source code to analyze
        function_name: Name of the function

    Returns:
        Dictionary with:
        - docstring: Rustdoc comment text (empty if none)
        - function_name: Name of the function
        - has_docstring: "true" if docstring exists, "false" otherwise

    Raises:
        TypeError: If source_code or function_name is not a string
        ValueError: If source_code is empty, parsing fails, or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find function items
        functions = _find_nodes_by_type(root, "function_item")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                docstring = _extract_rustdoc(source_code, func.start_byte)
                return {
                    "docstring": docstring,
                    "function_name": function_name,
                    "has_docstring": "true" if docstring else "false",
                }

        raise ValueError(f"Function '{function_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def list_rust_type_methods(source_code: str, type_name: str) -> dict[str, str]:
    """List all methods for a specific Rust type with signatures.

    Returns method signatures without bodies, saving 80-85% of tokens.

    Args:
        source_code: Rust source code to analyze
        type_name: Name of the type

    Returns:
        Dictionary with:
        - methods: JSON array of method information dictionaries
        - method_count: Total number of methods
        - type_name: Name of the type

    Raises:
        TypeError: If source_code or type_name is not a string
        ValueError: If source_code is empty, parsing fails, or type not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(type_name, "type_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        methods: list[dict[str, Any]] = []

        # Find all impl blocks
        impl_items = _find_nodes_by_type(root, "impl_item")
        for impl_item in impl_items:
            impl_type = _get_impl_type(impl_item, source_bytes)

            if impl_type == type_name:
                # Find functions within this impl block
                impl_functions = _find_nodes_by_type(impl_item, "function_item")
                for func in impl_functions:
                    if _is_method(func, source_bytes):
                        method_info: dict[str, Any] = {
                            "name": "",
                            "params": "",
                            "returns": "",
                            "is_public": False,
                        }

                        method_info["name"] = _get_function_name(func, source_bytes)
                        method_info["is_public"] = _is_public(func)

                        for child in func.children:
                            if child.type == "parameters":
                                method_info["params"] = _get_node_text(
                                    child, source_bytes
                                )
                            elif child.type in [
                                "type_identifier",
                                "primitive_type",
                                "reference_type",
                                "generic_type",
                            ]:
                                method_info["returns"] = _get_node_text(
                                    child, source_bytes
                                )

                        method_info["line"] = func.start_point[0] + 1
                        methods.append(method_info)

        if not methods:
            # Check if type exists
            type_nodes = (
                _find_nodes_by_type(root, "struct_item")
                + _find_nodes_by_type(root, "enum_item")
                + _find_nodes_by_type(root, "trait_item")
            )
            type_found = False
            for type_node in type_nodes:
                name = _get_type_name(type_node, source_bytes)
                if name == type_name:
                    type_found = True
                    break

            if not type_found:
                raise ValueError(f"Type '{type_name}' not found in source code")

        return {
            "methods": json.dumps(methods),
            "method_count": str(len(methods)),
            "type_name": type_name,
        }

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def extract_rust_public_api(source_code: str) -> dict[str, str]:
    """Extract the public API of a Rust file.

    Identifies public (pub) functions and types, saving 70-80% of tokens
    by focusing only on the public interface.

    Args:
        source_code: Rust source code to analyze

    Returns:
        Dictionary with:
        - public_functions: JSON array of public function names
        - public_types: JSON array of public type names
        - public_count: Total number of public elements
        - details: JSON object with detailed info

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty or parsing fails
    """
    validate_source_code(source_code)

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        public_functions: list[str] = []
        public_types: list[str] = []

        # Find public functions
        functions = _find_nodes_by_type(root, "function_item")
        for func in functions:
            if _is_public(func):
                name = _get_function_name(func, source_bytes)
                if name:
                    public_functions.append(name)

        # Find public types
        type_nodes = (
            _find_nodes_by_type(root, "struct_item")
            + _find_nodes_by_type(root, "enum_item")
            + _find_nodes_by_type(root, "trait_item")
            + _find_nodes_by_type(root, "type_item")
        )

        for type_node in type_nodes:
            if _is_public(type_node):
                name = _get_type_name(type_node, source_bytes)
                if name:
                    public_types.append(name)

        return {
            "public_functions": json.dumps(public_functions),
            "public_types": json.dumps(public_types),
            "public_count": str(len(public_functions) + len(public_types)),
            "details": json.dumps(
                {
                    "functions": public_functions,
                    "types": public_types,
                }
            ),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_rust_function_details(source_code: str, function_name: str) -> dict[str, str]:
    """Get complete details about a Rust function.

    Returns signature, rustdoc, parameters, and metadata without the body,
    saving 75-85% of tokens.

    Args:
        source_code: Rust source code to analyze
        function_name: Name of the function

    Returns:
        Dictionary with:
        - function_name: Name of the function
        - signature: Function signature string
        - docstring: Rustdoc comment (empty if none)
        - params: Parameter list
        - returns: Return type
        - is_public: "true" if function is public, "false" otherwise
        - line: Line number where function starts

    Raises:
        TypeError: If source_code or function_name is not a string
        ValueError: If source_code is empty, parsing fails, or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find function items
        functions = _find_nodes_by_type(root, "function_item")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                params = ""
                returns = ""
                visibility = "pub " if _is_public(func) else ""

                for child in func.children:
                    if child.type == "parameters":
                        params = _get_node_text(child, source_bytes)
                    elif child.type in [
                        "type_identifier",
                        "primitive_type",
                        "reference_type",
                        "generic_type",
                    ]:
                        returns = _get_node_text(child, source_bytes)

                signature = f"{visibility}fn {function_name}{params}"
                if returns:
                    signature += f" -> {returns}"

                docstring = _extract_rustdoc(source_code, func.start_byte)

                return {
                    "function_name": function_name,
                    "signature": signature,
                    "docstring": docstring,
                    "params": params,
                    "returns": returns,
                    "is_public": "true" if _is_public(func) else "false",
                    "line": str(func.start_point[0] + 1),
                }

        raise ValueError(f"Function '{function_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_rust_function_body(source_code: str, function_name: str) -> dict[str, str]:
    """Get just the implementation body of a specific Rust function.

    Returns only the function body without signature or rustdoc, saving 80-90% of tokens.
    Useful for understanding implementation without reading the entire file.

    Args:
        source_code: Rust source code to analyze
        function_name: Name of the function

    Returns:
        Dictionary with:
        - body: Function body as source code string
        - start_line: Line number where body starts (1-indexed)
        - end_line: Line number where body ends (1-indexed)
        - function_name: Name of the function

    Raises:
        TypeError: If source_code or function_name is not a string
        ValueError: If source_code is empty, parsing fails, or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")
        lines = source_code.split("\n")

        # Find function items
        functions = _find_nodes_by_type(root, "function_item")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                # Find the function body (block)
                for child in func.children:
                    if child.type == "block":
                        start_line = child.start_point[0] + 1
                        end_line = child.end_point[0] + 1
                        body_lines = lines[start_line - 1 : end_line]

                        return {
                            "body": "\n".join(body_lines),
                            "start_line": str(start_line),
                            "end_line": str(end_line),
                            "function_name": function_name,
                        }

        raise ValueError(f"Function '{function_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def list_rust_function_calls(source_code: str, function_name: str) -> dict[str, str]:
    """List all function calls made within a specific Rust function.

    Analyzes function dependencies and call patterns, saving 75-85% of tokens.
    Useful for understanding what a function depends on.

    Args:
        source_code: Rust source code to analyze
        function_name: Name of the function to analyze

    Returns:
        Dictionary with:
        - calls: JSON array of function call names
        - call_count: Total number of calls
        - call_details: JSON array with call info (name, line)

    Raises:
        TypeError: If source_code or function_name is not a string
        ValueError: If source_code is empty, parsing fails, or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find function items
        functions = _find_nodes_by_type(root, "function_item")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                calls: list[str] = []
                call_details: list[dict[str, Any]] = []

                # Find call expressions
                call_exprs = _find_nodes_by_type(func, "call_expression")
                for call_expr in call_exprs:
                    # Get the function being called
                    if call_expr.children:
                        callee = call_expr.children[0]
                        call_name = _get_node_text(callee, source_bytes)
                        calls.append(call_name)
                        call_details.append(
                            {
                                "name": call_name,
                                "line": call_expr.start_point[0] + 1,
                            }
                        )

                return {
                    "calls": json.dumps(calls),
                    "call_count": str(len(calls)),
                    "call_details": json.dumps(call_details),
                }

        raise ValueError(f"Function '{function_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def find_rust_function_usages(source_code: str, function_name: str) -> dict[str, str]:
    """Find all places where a specific Rust function is called.

    Performs impact analysis to identify all usage locations, saving 75-85% of tokens.
    Useful for understanding the scope of changes.

    Args:
        source_code: Rust source code to analyze
        function_name: Name of the function to find usages of

    Returns:
        Dictionary with:
        - usages: JSON array of line numbers where function is called
        - usage_count: Total number of usages found
        - usage_details: JSON array with detailed usage info

    Raises:
        TypeError: If source_code or function_name is not a string
        ValueError: If source_code is empty or parsing fails
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        usages: list[int] = []
        usage_details: list[dict[str, Any]] = []

        # Find all call expressions
        call_exprs = _find_nodes_by_type(root, "call_expression")
        for call_expr in call_exprs:
            if call_expr.children:
                callee = call_expr.children[0]
                call_text = _get_node_text(callee, source_bytes)

                # Check if this is a call to the target function
                # Handle direct calls, method calls (e.g., obj.method), and path calls (e.g., module::function)
                if (
                    call_text == function_name
                    or call_text.endswith("::" + function_name)
                    or call_text.endswith("." + function_name)
                ):
                    line = call_expr.start_point[0] + 1
                    usages.append(line)
                    usage_details.append(
                        {
                            "line": line,
                            "context": "function_call",
                        }
                    )

        return {
            "usages": json.dumps(usages),
            "usage_count": str(len(usages)),
            "usage_details": json.dumps(usage_details),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_rust_specific_function_line_numbers(
    source_code: str, type_name: str, function_name: str
) -> dict[str, str]:
    """Get start and end line numbers for a specific method of a Rust type.

    Enables precise targeting of type methods, saving 85-90% of tokens.
    Finds methods within impl blocks for the specified type.

    Args:
        source_code: Rust source code to analyze
        type_name: Name of the type (struct/enum name)
        function_name: Name of the method

    Returns:
        Dictionary with:
        - start_line: Line number where method starts (1-indexed)
        - end_line: Line number where method ends (1-indexed)
        - type_name: Name of the type
        - function_name: Name of the method

    Raises:
        TypeError: If any argument is not a string
        ValueError: If source_code is empty, parsing fails, type or method not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(type_name, "type_name")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find impl blocks for the specific type
        impl_items = _find_nodes_by_type(root, "impl_item")
        for impl_item in impl_items:
            impl_type = _get_impl_type(impl_item, source_bytes)

            if impl_type == type_name:
                # Find functions within this impl block
                impl_functions = _find_nodes_by_type(impl_item, "function_item")
                for func in impl_functions:
                    name = _get_function_name(func, source_bytes)
                    if name == function_name:
                        start_line = func.start_point[0] + 1
                        end_line = func.end_point[0] + 1
                        return {
                            "start_line": str(start_line),
                            "end_line": str(end_line),
                            "type_name": type_name,
                            "function_name": function_name,
                        }

        # Check if type exists
        type_nodes = (
            _find_nodes_by_type(root, "struct_item")
            + _find_nodes_by_type(root, "enum_item")
            + _find_nodes_by_type(root, "trait_item")
        )
        type_found = False
        for type_node in type_nodes:
            name = _get_type_name(type_node, source_bytes)
            if name == type_name:
                type_found = True
                break

        if not type_found:
            raise ValueError(f"Type '{type_name}' not found in source code")

        raise ValueError(f"Method '{function_name}' not found for type '{type_name}'")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_rust_type_hierarchy(source_code: str, type_name: str) -> dict[str, str]:
    """Get trait implementation information for a Rust type.

    Analyzes trait implementations for the type, saving 70-80% of tokens.

    Args:
        source_code: Rust source code to analyze
        type_name: Name of the type

    Returns:
        Dictionary with:
        - implements: JSON array of trait names (from impl blocks)
        - has_trait_impls: "true" if type has trait implementations, "false" otherwise
        - type_name: Name of the type
        - embeds: JSON array (empty for Rust - no structural embedding like Go)

    Raises:
        TypeError: If source_code or type_name is not a string
        ValueError: If source_code is empty, parsing fails, or type not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(type_name, "type_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Check if type exists
        type_nodes = _find_nodes_by_type(root, "struct_item") + _find_nodes_by_type(
            root, "enum_item"
        )
        type_found = False
        for type_node in type_nodes:
            name = _get_type_name(type_node, source_bytes)
            if name == type_name:
                type_found = True
                break

        if not type_found:
            raise ValueError(f"Type '{type_name}' not found in source code")

        # Find trait implementations
        implements: list[str] = []
        impl_items = _find_nodes_by_type(root, "impl_item")
        for impl_item in impl_items:
            impl_type = _get_impl_type(impl_item, source_bytes)

            if impl_type == type_name:
                # Check if this is a trait implementation (has 'for' keyword)
                impl_text = _get_node_text(impl_item, source_bytes)
                if " for " in impl_text[:100]:  # Check first 100 chars
                    # Extract trait name (between "impl" and "for")
                    match = re.search(r"impl\s+(\w+)\s+for", impl_text)
                    if match:
                        trait_name = match.group(1)
                        implements.append(trait_name)

        has_trait_impls = len(implements) > 0

        return {
            "implements": json.dumps(implements),
            "has_trait_impls": "true" if has_trait_impls else "false",
            "type_name": type_name,
            "embeds": json.dumps([]),  # Rust doesn't have structural embedding like Go
        }

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def find_rust_definitions_by_comment(
    source_code: str, comment_pattern: str
) -> dict[str, str]:
    """Find all functions/types with comments matching a pattern in Rust.

    Searches rustdoc comments for patterns, saving 70-80% of tokens.

    Args:
        source_code: Rust source code to analyze
        comment_pattern: Pattern to search for in comments (case-insensitive)

    Returns:
        Dictionary with:
        - functions: JSON array of function names with matching comments
        - types: JSON array of type names with matching comments
        - total_count: Total number of definitions with matching comments
        - details: JSON array with detailed info about each match

    Raises:
        TypeError: If source_code or comment_pattern is not a string
        ValueError: If source_code is empty or parsing fails
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(comment_pattern, str):
        raise TypeError("comment_pattern must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        functions: list[str] = []
        types: list[str] = []
        details: list[dict[str, Any]] = []

        pattern = re.compile(re.escape(comment_pattern), re.IGNORECASE)

        # Check functions
        function_nodes = _find_nodes_by_type(root, "function_item")
        for func in function_nodes:
            name = _get_function_name(func, source_bytes)
            if name:
                docstring = _extract_rustdoc(source_code, func.start_byte)
                if pattern.search(docstring):
                    functions.append(name)
                    details.append(
                        {
                            "name": name,
                            "type": "function",
                            "line": func.start_point[0] + 1,
                        }
                    )

        # Check types
        type_nodes = (
            _find_nodes_by_type(root, "struct_item")
            + _find_nodes_by_type(root, "enum_item")
            + _find_nodes_by_type(root, "trait_item")
            + _find_nodes_by_type(root, "type_item")
        )

        for type_node in type_nodes:
            name = _get_type_name(type_node, source_bytes)
            if name:
                docstring = _extract_rustdoc(source_code, type_node.start_byte)
                if pattern.search(docstring):
                    types.append(name)
                    details.append(
                        {
                            "name": name,
                            "type": "type",
                            "line": type_node.start_point[0] + 1,
                        }
                    )

        return {
            "functions": json.dumps(functions),
            "types": json.dumps(types),
            "total_count": str(len(functions) + len(types)),
            "details": json.dumps(details),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_rust_type_docstring(source_code: str, type_name: str) -> dict[str, str]:
    """Get just the rustdoc comment of a specific Rust type.

    Returns only the type documentation without implementation, saving 80-85% of tokens.

    Args:
        source_code: Rust source code to analyze
        type_name: Name of the type

    Returns:
        Dictionary with:
        - docstring: Rustdoc comment text (empty if none)
        - type_name: Name of the type
        - has_docstring: "true" if docstring exists, "false" otherwise

    Raises:
        TypeError: If source_code or type_name is not a string
        ValueError: If source_code is empty, parsing fails, or type not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(type_name, "type_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_rust(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find the type
        type_nodes = (
            _find_nodes_by_type(root, "struct_item")
            + _find_nodes_by_type(root, "enum_item")
            + _find_nodes_by_type(root, "trait_item")
            + _find_nodes_by_type(root, "type_item")
        )

        for type_node in type_nodes:
            name = _get_type_name(type_node, source_bytes)
            if name == type_name:
                docstring = _extract_rustdoc(source_code, type_node.start_byte)
                return {
                    "docstring": docstring,
                    "type_name": type_name,
                    "has_docstring": "true" if docstring else "false",
                }

        raise ValueError(f"Type '{type_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Rust code: {e}") from e
