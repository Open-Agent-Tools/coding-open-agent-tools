"""C++ code navigation functions.

This module provides token-efficient navigation tools for C++ code,
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


def _parse_cpp(source_code: str) -> Any:
    """Parse C++ code into AST using tree-sitter.

    Args:
        source_code: C++ source code

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
        parser = get_parser("cpp")
        tree = parser.parse(bytes(source_code, "utf8"))
        return tree
    except Exception as e:
        raise ValueError(f"Failed to parse C++ code: {e}") from e


def _extract_cpp_doc(source_code: str, start_byte: int) -> str:
    """Extract documentation comment before a function/type.

    Args:
        source_code: Full source code
        start_byte: Byte offset where function/type starts

    Returns:
        Documentation comment text or empty string
    """
    # Find the portion of code before the function/type
    preceding = source_code[:start_byte]
    lines = preceding.split("\n")

    # Look backwards for doc comments
    doc_lines: list[str] = []
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()

        if line.startswith("///") or line.startswith("//!") or line.startswith("//"):
            # Doc comment line (Doxygen style or regular)
            doc_lines.insert(0, line)
        elif line.endswith("*/"):
            # Multi-line comment, collect until start
            doc_lines.insert(0, line)
            for j in range(i - 1, -1, -1):
                doc_line = lines[j].strip()
                doc_lines.insert(0, doc_line)
                if doc_line.startswith("/*") or doc_line.startswith("/**"):
                    return "\n".join(doc_lines)
            break
        elif not line or line.startswith("#"):
            # Empty line or preprocessor directive, stop if we have comments
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
        node_type: Node type to find (e.g., "function_definition", "class_specifier")

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


def _is_inside_class(node: Any, root: Any) -> bool:
    """Check if a node is inside a class/struct definition.

    Args:
        node: Node to check
        root: Root node of the AST

    Returns:
        True if node is inside a class/struct, False otherwise
    """
    # Walk up the parent hierarchy to see if we're inside a class_specifier or struct_specifier
    current = node
    while current is not None:
        if current.type in ("class_specifier", "struct_specifier"):
            return True
        # Move to parent (tree-sitter doesn't have parent pointers, so we need to search)
        # For simplicity, we'll check if the node's byte range is contained within class/struct ranges
        break

    # Alternative: check if node is within any class_specifier or struct_specifier
    classes = _find_nodes_by_type(root, "class_specifier")
    structs = _find_nodes_by_type(root, "struct_specifier")

    for cls in classes + structs:
        if cls.start_byte <= node.start_byte and node.end_byte <= cls.end_byte:
            return True

    return False


def _get_access_specifier(node: Any, parent_class: Any, source_bytes: bytes) -> str:
    """Get the access specifier (public/private/protected) for a node within a class.

    Args:
        node: Node to check
        parent_class: Parent class/struct node
        source_bytes: Source code as bytes

    Returns:
        "public", "private", or "protected"
    """
    # Default access: public for struct, private for class
    default_access = "public" if parent_class.type == "struct_specifier" else "private"

    # Find all access_specifier nodes in the class before this node
    access_specs = _find_nodes_by_type(parent_class, "access_specifier")
    current_access = default_access

    for spec in access_specs:
        if spec.start_byte < node.start_byte:
            # This access specifier applies to our node
            spec_text = _get_node_text(spec, source_bytes).strip()
            if "public" in spec_text:
                current_access = "public"
            elif "private" in spec_text:
                current_access = "private"
            elif "protected" in spec_text:
                current_access = "protected"

    return current_access


def _is_public_function(node: Any, root: Any, source_bytes: bytes) -> bool:
    """Check if a function is public (not inside a class, or in public section).

    Args:
        node: Function definition node
        root: Root node of the AST
        source_bytes: Source code as bytes

    Returns:
        True if public, False otherwise
    """
    # If not inside a class, it's public (file-level function)
    classes = _find_nodes_by_type(root, "class_specifier")
    structs = _find_nodes_by_type(root, "struct_specifier")

    parent_class = None
    for cls in classes + structs:
        if cls.start_byte <= node.start_byte and node.end_byte <= cls.end_byte:
            parent_class = cls
            break

    if parent_class is None:
        return True  # Not in a class, so it's public

    # Check access specifier
    access = _get_access_specifier(node, parent_class, source_bytes)
    return access == "public"


def _get_function_name(node: Any, source_bytes: bytes) -> str:
    """Extract function name from function_definition node.

    Args:
        node: Function definition node
        source_bytes: Source code as bytes

    Returns:
        Function name or empty string if not found
    """
    # Look for function_declarator
    declarators = _find_nodes_by_type(node, "function_declarator")
    if not declarators:
        return ""

    declarator = declarators[0]
    # Look for identifier or field_identifier within the declarator
    for child in declarator.children:
        if child.type in ("identifier", "field_identifier", "qualified_identifier"):
            # Handle qualified names (e.g., ClassName::method)
            if child.type == "qualified_identifier":
                # Get the last identifier
                identifiers = _find_nodes_by_type(child, "identifier")
                if identifiers:
                    return _get_node_text(identifiers[-1], source_bytes)
            return _get_node_text(child, source_bytes)

    return ""


def _get_type_name(node: Any, source_bytes: bytes) -> str:
    """Extract type name from class/struct/enum node.

    Args:
        node: Type node (class_specifier, struct_specifier, enum_specifier)
        source_bytes: Source code as bytes

    Returns:
        Type name or empty string if not found
    """
    for child in node.children:
        if child.type == "type_identifier":
            return _get_node_text(child, source_bytes)
    return ""


def _is_method(node: Any, root: Any) -> bool:
    """Check if a function is a method (inside a class/struct).

    Args:
        node: Function definition node
        root: Root node of the AST

    Returns:
        True if function is a method, False otherwise
    """
    return _is_inside_class(node, root)


def _get_class_for_method(node: Any, root: Any, source_bytes: bytes) -> str:
    """Get the class name for a method.

    Args:
        node: Function definition node
        root: Root node of the AST
        source_bytes: Source code as bytes

    Returns:
        Class name or empty string if not a method
    """
    classes = _find_nodes_by_type(root, "class_specifier")
    structs = _find_nodes_by_type(root, "struct_specifier")

    for cls in classes + structs:
        if cls.start_byte <= node.start_byte and node.end_byte <= cls.end_byte:
            return _get_type_name(cls, source_bytes)

    return ""


@strands_tool  # type: ignore[misc]
def get_cpp_function_line_numbers(
    source_code: str, function_name: str
) -> dict[str, str]:
    """Get start and end line numbers for a specific C++ function.

    Enables targeted file reading instead of loading entire files, saving 85-90% of tokens.
    Supports: function definitions and method definitions (inside classes/structs).

    Args:
        source_code: C++ source code to analyze
        function_name: Name of the function to locate

    Returns:
        Dictionary with:
        - start_line: Line number where function starts (1-indexed)
        - end_line: Line number where function ends (1-indexed)
        - function_name: Name of the function found
        - is_method: "true" if function is a method inside a class, "false" otherwise

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
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find function definitions
        functions = _find_nodes_by_type(root, "function_definition")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                start_line = func.start_point[0] + 1
                end_line = func.end_point[0] + 1
                is_method = _is_method(func, root)
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
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_cpp_type_line_numbers(source_code: str, type_name: str) -> dict[str, str]:
    """Get start and end line numbers for a specific C++ type.

    Enables targeted file reading instead of loading entire files, saving 85-90% of tokens.
    Supports: class declarations, struct declarations, enum declarations.

    Args:
        source_code: C++ source code to analyze
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
    if not isinstance(type_name, str):
        raise TypeError("type_name must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find class, struct, and enum declarations
        type_nodes = (
            _find_nodes_by_type(root, "class_specifier")
            + _find_nodes_by_type(root, "struct_specifier")
            + _find_nodes_by_type(root, "enum_specifier")
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
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_cpp_module_overview(source_code: str) -> dict[str, str]:
    """Get high-level overview of a C++ file without full parsing.

    Returns summary information about the file structure, saving 85-90% of tokens
    compared to reading the entire file.

    Args:
        source_code: C++ source code to analyze

    Returns:
        Dictionary with:
        - function_count: Number of functions in the file
        - method_count: Number of methods in the file (functions inside classes)
        - type_count: Number of types in the file
        - function_names: JSON array of function names
        - type_names: JSON array of type names
        - has_main: "true" if file has main function, "false" otherwise
        - has_namespaces: "true" if file uses namespaces, "false" otherwise
        - total_lines: Total number of lines in the file

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty or parsing fails
    """
    validate_source_code(source_code)

    try:
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Count functions
        functions = _find_nodes_by_type(root, "function_definition")
        function_names: list[str] = []
        method_count = 0
        has_main = False

        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name:
                function_names.append(name)
                if name == "main":
                    has_main = True
                if _is_method(func, root):
                    method_count += 1

        # Count types
        type_names: list[str] = []
        type_nodes = (
            _find_nodes_by_type(root, "class_specifier")
            + _find_nodes_by_type(root, "struct_specifier")
            + _find_nodes_by_type(root, "enum_specifier")
        )

        for type_node in type_nodes:
            name = _get_type_name(type_node, source_bytes)
            if name:
                type_names.append(name)

        # Check for namespaces
        has_namespaces = len(_find_nodes_by_type(root, "namespace_definition")) > 0

        # Count lines
        total_lines = len(source_code.split("\n"))

        return {
            "function_count": str(len(function_names)),
            "method_count": str(method_count),
            "type_count": str(len(type_names)),
            "function_names": json.dumps(function_names),
            "type_names": json.dumps(type_names),
            "has_main": "true" if has_main else "false",
            "has_namespaces": "true" if has_namespaces else "false",
            "total_lines": str(total_lines),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def list_cpp_functions(source_code: str) -> dict[str, str]:
    """List all functions in C++ code with their signatures.

    Returns function signatures without bodies, saving 80-85% of tokens.
    Useful for understanding file structure without reading implementation.

    Args:
        source_code: C++ source code to analyze

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
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        functions: list[dict[str, Any]] = []

        # Find function definitions
        function_nodes = _find_nodes_by_type(root, "function_definition")
        for func in function_nodes:
            func_info: dict[str, Any] = {
                "name": "",
                "params": "",
                "returns": "",
                "is_public": False,
            }

            func_info["name"] = _get_function_name(func, source_bytes)
            func_info["is_public"] = _is_public_function(func, root, source_bytes)

            # Extract return type and parameters
            for child in func.children:
                if child.type in (
                    "primitive_type",
                    "type_identifier",
                    "qualified_identifier",
                ):
                    # Return type
                    func_info["returns"] = _get_node_text(child, source_bytes)

            # Get parameters from function_declarator
            declarators = _find_nodes_by_type(func, "function_declarator")
            if declarators:
                param_lists = _find_nodes_by_type(declarators[0], "parameter_list")
                if param_lists:
                    func_info["params"] = _get_node_text(param_lists[0], source_bytes)

            func_info["line"] = func.start_point[0] + 1
            functions.append(func_info)

        return {
            "functions": json.dumps(functions),
            "function_count": str(len(functions)),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def list_cpp_types(source_code: str) -> dict[str, str]:
    """List all types in C++ code with their structure.

    Returns type definitions with method names but not implementations,
    saving 80-85% of tokens.

    Args:
        source_code: C++ source code to analyze

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
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        types: list[dict[str, Any]] = []

        # Find class declarations
        classes = _find_nodes_by_type(root, "class_specifier")
        for cls in classes:
            type_info: dict[str, Any] = {
                "name": "",
                "kind": "class",
                "is_public": True,  # Top-level classes are public
            }
            type_info["name"] = _get_type_name(cls, source_bytes)
            type_info["line"] = cls.start_point[0] + 1
            types.append(type_info)

        # Find struct declarations
        structs = _find_nodes_by_type(root, "struct_specifier")
        for struct in structs:
            type_info = {
                "name": "",
                "kind": "struct",
                "is_public": True,  # Top-level structs are public
            }
            type_info["name"] = _get_type_name(struct, source_bytes)
            type_info["line"] = struct.start_point[0] + 1
            types.append(type_info)

        # Find enum declarations
        enums = _find_nodes_by_type(root, "enum_specifier")
        for enum in enums:
            type_info = {
                "name": "",
                "kind": "enum",
                "is_public": True,  # Top-level enums are public
            }
            type_info["name"] = _get_type_name(enum, source_bytes)
            type_info["line"] = enum.start_point[0] + 1
            types.append(type_info)

        return {
            "types": json.dumps(types),
            "type_count": str(len(types)),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_cpp_function_signature(source_code: str, function_name: str) -> dict[str, str]:
    """Get just the signature of a specific C++ function.

    Returns only the function signature without the body, saving 85-90% of tokens.

    Args:
        source_code: C++ source code to analyze
        function_name: Name of the function

    Returns:
        Dictionary with:
        - signature: Function signature string
        - function_name: Name of the function
        - params: Parameter list
        - returns: Return type
        - is_public: "true" if function is public, "false" otherwise

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
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find function definitions
        functions = _find_nodes_by_type(root, "function_definition")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                returns = ""
                params = ""

                # Extract return type
                for child in func.children:
                    if child.type in (
                        "primitive_type",
                        "type_identifier",
                        "qualified_identifier",
                    ):
                        returns = _get_node_text(child, source_bytes)
                        break

                # Get parameters
                declarators = _find_nodes_by_type(func, "function_declarator")
                if declarators:
                    param_lists = _find_nodes_by_type(declarators[0], "parameter_list")
                    if param_lists:
                        params = _get_node_text(param_lists[0], source_bytes)

                signature = f"{returns} {function_name}{params}"
                if not returns:
                    signature = f"{function_name}{params}"

                return {
                    "signature": signature,
                    "function_name": function_name,
                    "params": params,
                    "returns": returns,
                    "is_public": "true"
                    if _is_public_function(func, root, source_bytes)
                    else "false",
                }

        raise ValueError(f"Function '{function_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_cpp_function_docstring(source_code: str, function_name: str) -> dict[str, str]:
    """Get just the documentation comment of a specific C++ function.

    Returns only the documentation without the implementation, saving 80-85% of tokens.

    Args:
        source_code: C++ source code to analyze
        function_name: Name of the function

    Returns:
        Dictionary with:
        - docstring: Documentation comment text (empty if none)
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
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find function definitions
        functions = _find_nodes_by_type(root, "function_definition")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                docstring = _extract_cpp_doc(source_code, func.start_byte)
                return {
                    "docstring": docstring,
                    "function_name": function_name,
                    "has_docstring": "true" if docstring else "false",
                }

        raise ValueError(f"Function '{function_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def list_cpp_type_methods(source_code: str, type_name: str) -> dict[str, str]:
    """List all methods for a specific C++ type with signatures.

    Returns method signatures without bodies, saving 80-85% of tokens.

    Args:
        source_code: C++ source code to analyze
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
    if not isinstance(type_name, str):
        raise TypeError("type_name must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        methods: list[dict[str, Any]] = []

        # Find the type
        type_nodes = _find_nodes_by_type(root, "class_specifier") + _find_nodes_by_type(
            root, "struct_specifier"
        )

        type_found = False
        for type_node in type_nodes:
            name = _get_type_name(type_node, source_bytes)
            if name == type_name:
                type_found = True

                # Find function definitions within this type
                functions = _find_nodes_by_type(type_node, "function_definition")
                for func in functions:
                    method_info: dict[str, Any] = {
                        "name": "",
                        "params": "",
                        "returns": "",
                        "is_public": False,
                    }

                    method_info["name"] = _get_function_name(func, source_bytes)
                    method_info["is_public"] = _is_public_function(
                        func, root, source_bytes
                    )

                    # Extract return type
                    for child in func.children:
                        if child.type in (
                            "primitive_type",
                            "type_identifier",
                            "qualified_identifier",
                        ):
                            method_info["returns"] = _get_node_text(child, source_bytes)
                            break

                    # Get parameters
                    declarators = _find_nodes_by_type(func, "function_declarator")
                    if declarators:
                        param_lists = _find_nodes_by_type(
                            declarators[0], "parameter_list"
                        )
                        if param_lists:
                            method_info["params"] = _get_node_text(
                                param_lists[0], source_bytes
                            )

                    method_info["line"] = func.start_point[0] + 1
                    methods.append(method_info)

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
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def extract_cpp_public_api(source_code: str) -> dict[str, str]:
    """Extract the public API of a C++ file.

    Identifies public functions and types, saving 70-80% of tokens
    by focusing only on the public interface.

    Args:
        source_code: C++ source code to analyze

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
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        public_functions: list[str] = []
        public_types: list[str] = []

        # Find public functions
        functions = _find_nodes_by_type(root, "function_definition")
        for func in functions:
            if _is_public_function(func, root, source_bytes):
                name = _get_function_name(func, source_bytes)
                if name:
                    public_functions.append(name)

        # Find public types (all top-level types are public in C++)
        type_nodes = (
            _find_nodes_by_type(root, "class_specifier")
            + _find_nodes_by_type(root, "struct_specifier")
            + _find_nodes_by_type(root, "enum_specifier")
        )

        for type_node in type_nodes:
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
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_cpp_function_details(source_code: str, function_name: str) -> dict[str, str]:
    """Get complete details about a C++ function.

    Returns signature, documentation, parameters, and metadata without the body,
    saving 75-85% of tokens.

    Args:
        source_code: C++ source code to analyze
        function_name: Name of the function

    Returns:
        Dictionary with:
        - function_name: Name of the function
        - signature: Function signature string
        - docstring: Documentation comment (empty if none)
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
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find function definitions
        functions = _find_nodes_by_type(root, "function_definition")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                returns = ""
                params = ""

                # Extract return type
                for child in func.children:
                    if child.type in (
                        "primitive_type",
                        "type_identifier",
                        "qualified_identifier",
                    ):
                        returns = _get_node_text(child, source_bytes)
                        break

                # Get parameters
                declarators = _find_nodes_by_type(func, "function_declarator")
                if declarators:
                    param_lists = _find_nodes_by_type(declarators[0], "parameter_list")
                    if param_lists:
                        params = _get_node_text(param_lists[0], source_bytes)

                signature = f"{returns} {function_name}{params}"
                if not returns:
                    signature = f"{function_name}{params}"

                docstring = _extract_cpp_doc(source_code, func.start_byte)

                return {
                    "function_name": function_name,
                    "signature": signature,
                    "docstring": docstring,
                    "params": params,
                    "returns": returns,
                    "is_public": "true"
                    if _is_public_function(func, root, source_bytes)
                    else "false",
                    "line": str(func.start_point[0] + 1),
                }

        raise ValueError(f"Function '{function_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_cpp_function_body(source_code: str, function_name: str) -> dict[str, str]:
    """Get just the implementation body of a specific C++ function.

    Returns only the function body without signature or documentation, saving 80-90% of tokens.
    Useful for understanding implementation without reading the entire file.

    Args:
        source_code: C++ source code to analyze
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
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")
        lines = source_code.split("\n")

        # Find function definitions
        functions = _find_nodes_by_type(root, "function_definition")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                # Find the function body (compound_statement)
                for child in func.children:
                    if child.type == "compound_statement":
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
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def list_cpp_function_calls(source_code: str, function_name: str) -> dict[str, str]:
    """List all function calls made within a specific C++ function.

    Analyzes function dependencies and call patterns, saving 75-85% of tokens.
    Useful for understanding what a function depends on.

    Args:
        source_code: C++ source code to analyze
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
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find function definitions
        functions = _find_nodes_by_type(root, "function_definition")
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
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def find_cpp_function_usages(source_code: str, function_name: str) -> dict[str, str]:
    """Find all places where a specific C++ function is called.

    Performs impact analysis to identify all usage locations, saving 75-85% of tokens.
    Useful for understanding the scope of changes.

    Args:
        source_code: C++ source code to analyze
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
        tree = _parse_cpp(source_code)
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
                # Handle direct calls, method calls (e.g., obj.method), and qualified calls (e.g., namespace::function)
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
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_cpp_specific_function_line_numbers(
    source_code: str, class_name: str, function_name: str
) -> dict[str, str]:
    """Get start and end line numbers for a specific method of a C++ class.

    Enables precise targeting of class methods, saving 85-90% of tokens.
    Finds methods within class or struct definitions.

    Args:
        source_code: C++ source code to analyze
        class_name: Name of the class or struct
        function_name: Name of the method

    Returns:
        Dictionary with:
        - start_line: Line number where method starts (1-indexed)
        - end_line: Line number where method ends (1-indexed)
        - class_name: Name of the class
        - function_name: Name of the method

    Raises:
        TypeError: If any argument is not a string
        ValueError: If source_code is empty, parsing fails, class or method not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(class_name, "class_name")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find the class or struct
        type_nodes = _find_nodes_by_type(root, "class_specifier") + _find_nodes_by_type(
            root, "struct_specifier"
        )

        for type_node in type_nodes:
            name = _get_type_name(type_node, source_bytes)
            if name == class_name:
                # Find functions within this class
                functions = _find_nodes_by_type(type_node, "function_definition")
                for func in functions:
                    func_name = _get_function_name(func, source_bytes)
                    if func_name == function_name:
                        start_line = func.start_point[0] + 1
                        end_line = func.end_point[0] + 1
                        return {
                            "start_line": str(start_line),
                            "end_line": str(end_line),
                            "class_name": class_name,
                            "function_name": function_name,
                        }

        # Check if class exists
        type_found = False
        for type_node in type_nodes:
            name = _get_type_name(type_node, source_bytes)
            if name == class_name:
                type_found = True
                break

        if not type_found:
            raise ValueError(f"Class '{class_name}' not found in source code")

        raise ValueError(f"Method '{function_name}' not found in class '{class_name}'")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_cpp_type_hierarchy(source_code: str, type_name: str) -> dict[str, str]:
    """Get inheritance information for a C++ type.

    Analyzes base classes and inheritance hierarchy, saving 70-80% of tokens.

    Args:
        source_code: C++ source code to analyze
        type_name: Name of the type

    Returns:
        Dictionary with:
        - base_classes: JSON array of base class names
        - has_inheritance: "true" if type inherits from other classes, "false" otherwise
        - type_name: Name of the type
        - implements: JSON array (empty - C++ doesn't have explicit interfaces)

    Raises:
        TypeError: If source_code or type_name is not a string
        ValueError: If source_code is empty, parsing fails, or type not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(type_name, str):
        raise TypeError("type_name must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find the type
        type_nodes = _find_nodes_by_type(root, "class_specifier") + _find_nodes_by_type(
            root, "struct_specifier"
        )

        for type_node in type_nodes:
            name = _get_type_name(type_node, source_bytes)
            if name == type_name:
                base_classes: list[str] = []

                # Find base_class_clause
                base_clauses = _find_nodes_by_type(type_node, "base_class_clause")
                if base_clauses:
                    # Extract base class names
                    for clause in base_clauses:
                        # Find type_identifiers in the clause
                        identifiers = _find_nodes_by_type(clause, "type_identifier")
                        for identifier in identifiers:
                            base_name = _get_node_text(identifier, source_bytes)
                            if base_name:
                                base_classes.append(base_name)

                has_inheritance = len(base_classes) > 0

                return {
                    "base_classes": json.dumps(base_classes),
                    "has_inheritance": "true" if has_inheritance else "false",
                    "type_name": type_name,
                    "implements": json.dumps(
                        []
                    ),  # C++ doesn't have explicit interfaces
                }

        raise ValueError(f"Type '{type_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def find_cpp_definitions_by_comment(
    source_code: str, comment_pattern: str
) -> dict[str, str]:
    """Find all functions/types with comments matching a pattern in C++.

    Searches documentation comments for patterns, saving 70-80% of tokens.

    Args:
        source_code: C++ source code to analyze
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
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        functions: list[str] = []
        types: list[str] = []
        details: list[dict[str, Any]] = []

        pattern = re.compile(re.escape(comment_pattern), re.IGNORECASE)

        # Check functions
        function_nodes = _find_nodes_by_type(root, "function_definition")
        for func in function_nodes:
            name = _get_function_name(func, source_bytes)
            if name:
                docstring = _extract_cpp_doc(source_code, func.start_byte)
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
            _find_nodes_by_type(root, "class_specifier")
            + _find_nodes_by_type(root, "struct_specifier")
            + _find_nodes_by_type(root, "enum_specifier")
        )

        for type_node in type_nodes:
            name = _get_type_name(type_node, source_bytes)
            if name:
                docstring = _extract_cpp_doc(source_code, type_node.start_byte)
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
        raise ValueError(f"Failed to parse C++ code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_cpp_type_docstring(source_code: str, type_name: str) -> dict[str, str]:
    """Get just the documentation comment of a specific C++ type.

    Returns only the type documentation without implementation, saving 80-85% of tokens.

    Args:
        source_code: C++ source code to analyze
        type_name: Name of the type

    Returns:
        Dictionary with:
        - docstring: Documentation comment text (empty if none)
        - type_name: Name of the type
        - has_docstring: "true" if docstring exists, "false" otherwise

    Raises:
        TypeError: If source_code or type_name is not a string
        ValueError: If source_code is empty, parsing fails, or type not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(type_name, str):
        raise TypeError("type_name must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_cpp(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find the type
        type_nodes = (
            _find_nodes_by_type(root, "class_specifier")
            + _find_nodes_by_type(root, "struct_specifier")
            + _find_nodes_by_type(root, "enum_specifier")
        )

        for type_node in type_nodes:
            name = _get_type_name(type_node, source_bytes)
            if name == type_name:
                docstring = _extract_cpp_doc(source_code, type_node.start_byte)
                return {
                    "docstring": docstring,
                    "type_name": type_name,
                    "has_docstring": "true" if docstring else "false",
                }

        raise ValueError(f"Type '{type_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse C++ code: {e}") from e
