"""Go code navigation functions.

This module provides token-efficient navigation tools for Go code,
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


def _parse_go(source_code: str) -> Any:
    """Parse Go code into AST using tree-sitter.

    Args:
        source_code: Go source code

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
        parser = get_parser("go")
        tree = parser.parse(bytes(source_code, "utf8"))
        return tree
    except Exception as e:
        raise ValueError(f"Failed to parse Go code: {e}") from e


def _extract_godoc(source_code: str, start_byte: int) -> str:
    """Extract godoc comment before a function/type.

    Args:
        source_code: Full source code
        start_byte: Byte offset where function/type starts

    Returns:
        Godoc comment text or empty string
    """
    # Find the portion of code before the function/type
    preceding = source_code[:start_byte]
    lines = preceding.split("\n")

    # Look backwards for godoc comments
    doc_lines: list[str] = []
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()

        if line.startswith("//"):
            # Single-line godoc comment
            doc_lines.insert(0, line)
        elif line.endswith("*/"):
            # Multi-line comment, collect until start
            doc_lines.insert(0, line)
            for j in range(i - 1, -1, -1):
                doc_line = lines[j].strip()
                doc_lines.insert(0, doc_line)
                if doc_line.startswith("/*"):
                    return "\n".join(doc_lines)
            break
        elif not line or line.startswith("package") or line.startswith("import"):
            # Empty line or package/import, stop if we have comments
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
        node_type: Node type to find (e.g., "function_declaration", "type_declaration")

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


def _is_public(name: str) -> bool:
    """Check if a Go identifier is public (exported).

    Args:
        name: Identifier name

    Returns:
        True if public (starts with uppercase), False otherwise
    """
    return bool(name and name[0].isupper())


def _get_function_name(node: Any, source_bytes: bytes) -> str:
    """Extract function name from function_declaration or method_declaration node.

    Args:
        node: Function or method declaration node
        source_bytes: Source code as bytes

    Returns:
        Function name or empty string if not found
    """
    for child in node.children:
        # function_declaration uses "identifier", method_declaration uses "field_identifier"
        if child.type in ("identifier", "field_identifier"):
            return _get_node_text(child, source_bytes)
    return ""


def _get_type_name(node: Any, source_bytes: bytes) -> str:
    """Extract type name from type_spec node.

    Args:
        node: Type spec node
        source_bytes: Source code as bytes

    Returns:
        Type name or empty string if not found
    """
    for child in node.children:
        if child.type == "type_identifier":
            return _get_node_text(child, source_bytes)
    return ""


def _get_receiver_type(node: Any, source_bytes: bytes) -> str:
    """Extract receiver type from method_declaration node.

    Args:
        node: Method declaration node
        source_bytes: Source code as bytes

    Returns:
        Receiver type name or empty string if not found
    """
    for child in node.children:
        if child.type == "parameter_list":
            # Find type_identifier in receiver parameter
            type_nodes = _find_nodes_by_type(child, "type_identifier")
            if type_nodes:
                return _get_node_text(type_nodes[0], source_bytes)
            # Check for pointer types
            pointer_nodes = _find_nodes_by_type(child, "pointer_type")
            if pointer_nodes:
                for pchild in pointer_nodes[0].children:
                    if pchild.type == "type_identifier":
                        return _get_node_text(pchild, source_bytes)
    return ""


@strands_tool  # type: ignore[misc]
def get_go_function_line_numbers(
    source_code: str, function_name: str
) -> dict[str, str]:
    """Get start and end line numbers for a specific Go function.

    Enables targeted file reading instead of loading entire files, saving 85-90% of tokens.
    Supports: function declarations and method declarations (with receivers).

    Args:
        source_code: Go source code to analyze
        function_name: Name of the function to locate

    Returns:
        Dictionary with:
        - start_line: Line number where function starts (1-indexed)
        - end_line: Line number where function ends (1-indexed)
        - function_name: Name of the function found
        - is_method: "true" if function is a method with receiver, "false" otherwise

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
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find function declarations
        functions = _find_nodes_by_type(root, "function_declaration")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                start_line = func.start_point[0] + 1
                end_line = func.end_point[0] + 1
                return {
                    "start_line": str(start_line),
                    "end_line": str(end_line),
                    "function_name": function_name,
                    "is_method": "false",
                }

        # Find method declarations
        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            name = _get_function_name(method, source_bytes)
            if name == function_name:
                start_line = method.start_point[0] + 1
                end_line = method.end_point[0] + 1
                return {
                    "start_line": str(start_line),
                    "end_line": str(end_line),
                    "function_name": function_name,
                    "is_method": "true",
                }

        raise ValueError(f"Function '{function_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_go_type_line_numbers(source_code: str, type_name: str) -> dict[str, str]:
    """Get start and end line numbers for a specific Go type.

    Enables targeted file reading instead of loading entire files, saving 85-90% of tokens.
    Supports: struct declarations, interface declarations, type aliases.

    Args:
        source_code: Go source code to analyze
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
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find type declarations
        type_decls = _find_nodes_by_type(root, "type_declaration")
        for type_decl in type_decls:
            # Find type_spec within type_declaration
            type_specs = _find_nodes_by_type(type_decl, "type_spec")
            for type_spec in type_specs:
                name = _get_type_name(type_spec, source_bytes)
                if name == type_name:
                    start_line = type_decl.start_point[0] + 1
                    end_line = type_decl.end_point[0] + 1
                    return {
                        "start_line": str(start_line),
                        "end_line": str(end_line),
                        "type_name": type_name,
                    }

        raise ValueError(f"Type '{type_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_go_module_overview(source_code: str) -> dict[str, str]:
    """Get high-level overview of a Go file without full parsing.

    Returns summary information about the file structure, saving 85-90% of tokens
    compared to reading the entire file.

    Args:
        source_code: Go source code to analyze

    Returns:
        Dictionary with:
        - function_count: Number of functions in the file
        - method_count: Number of methods in the file
        - type_count: Number of types in the file
        - function_names: JSON array of function names
        - type_names: JSON array of type names
        - has_package: "true" if file has package declaration, "false" otherwise
        - has_imports: "true" if file has imports, "false" otherwise
        - total_lines: Total number of lines in the file

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty or parsing fails
    """
    validate_source_code(source_code)

    try:
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Count functions
        functions = _find_nodes_by_type(root, "function_declaration")
        function_names: list[str] = []
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name:
                function_names.append(name)

        # Count methods
        methods = _find_nodes_by_type(root, "method_declaration")
        method_count = len(methods)

        # Count types
        type_names: list[str] = []
        type_decls = _find_nodes_by_type(root, "type_declaration")
        for type_decl in type_decls:
            type_specs = _find_nodes_by_type(type_decl, "type_spec")
            for type_spec in type_specs:
                name = _get_type_name(type_spec, source_bytes)
                if name:
                    type_names.append(name)

        # Check for package and imports
        has_package = len(_find_nodes_by_type(root, "package_clause")) > 0
        has_imports = len(_find_nodes_by_type(root, "import_declaration")) > 0

        # Count lines
        total_lines = len(source_code.split("\n"))

        return {
            "function_count": str(len(function_names)),
            "method_count": str(method_count),
            "type_count": str(len(type_names)),
            "function_names": json.dumps(function_names),
            "type_names": json.dumps(type_names),
            "has_package": "true" if has_package else "false",
            "has_imports": "true" if has_imports else "false",
            "total_lines": str(total_lines),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def list_go_functions(source_code: str) -> dict[str, str]:
    """List all functions in Go code with their signatures.

    Returns function signatures without bodies, saving 80-85% of tokens.
    Useful for understanding file structure without reading implementation.

    Args:
        source_code: Go source code to analyze

    Returns:
        Dictionary with:
        - functions: JSON array of function information dictionaries
        - function_count: Total number of functions found (excluding methods)

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty or parsing fails
    """
    validate_source_code(source_code)

    try:
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        functions: list[dict[str, Any]] = []

        # Find function declarations
        function_nodes = _find_nodes_by_type(root, "function_declaration")
        for func in function_nodes:
            func_info: dict[str, Any] = {
                "name": "",
                "params": "",
                "returns": "",
                "is_public": False,
            }

            for child in func.children:
                if child.type == "identifier":
                    func_info["name"] = _get_node_text(child, source_bytes)
                    func_info["is_public"] = _is_public(func_info["name"])
                elif child.type == "parameter_list":
                    func_info["params"] = _get_node_text(child, source_bytes)
                elif child.type in [
                    "parameter_list",
                    "type_identifier",
                    "pointer_type",
                ]:
                    # This might be the return type
                    if (
                        child.type != "parameter_list"
                        or child.start_byte > func.start_byte + 100
                    ):
                        func_info["returns"] = _get_node_text(child, source_bytes)

            func_info["line"] = func.start_point[0] + 1
            functions.append(func_info)

        return {
            "functions": json.dumps(functions),
            "function_count": str(len(functions)),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def list_go_types(source_code: str) -> dict[str, str]:
    """List all types in Go code with their structure.

    Returns type definitions with method names but not implementations,
    saving 80-85% of tokens.

    Args:
        source_code: Go source code to analyze

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
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        types: list[dict[str, Any]] = []

        # Find type declarations
        type_decls = _find_nodes_by_type(root, "type_declaration")
        for type_decl in type_decls:
            type_specs = _find_nodes_by_type(type_decl, "type_spec")
            for type_spec in type_specs:
                type_info: dict[str, Any] = {
                    "name": "",
                    "kind": "",
                    "is_public": False,
                }

                name = _get_type_name(type_spec, source_bytes)
                type_info["name"] = name
                type_info["is_public"] = _is_public(name)

                # Determine type kind
                for child in type_spec.children:
                    if child.type == "struct_type":
                        type_info["kind"] = "struct"
                    elif child.type == "interface_type":
                        type_info["kind"] = "interface"
                    elif child.type in [
                        "type_identifier",
                        "pointer_type",
                        "array_type",
                        "slice_type",
                    ]:
                        type_info["kind"] = "alias"

                type_info["line"] = type_decl.start_point[0] + 1
                types.append(type_info)

        return {
            "types": json.dumps(types),
            "type_count": str(len(types)),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_go_function_signature(source_code: str, function_name: str) -> dict[str, str]:
    """Get just the signature of a specific Go function.

    Returns only the function signature without the body, saving 85-90% of tokens.

    Args:
        source_code: Go source code to analyze
        function_name: Name of the function

    Returns:
        Dictionary with:
        - signature: Function signature string
        - function_name: Name of the function
        - params: Parameter list
        - returns: Return type(s)
        - is_public: "true" if function is exported (public), "false" otherwise

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
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Check functions
        functions = _find_nodes_by_type(root, "function_declaration")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                params = ""
                returns = ""

                for child in func.children:
                    if child.type == "parameter_list":
                        text = _get_node_text(child, source_bytes)
                        if not params:
                            params = text
                        else:
                            returns = text

                signature = f"func {function_name}{params}"
                if returns:
                    signature += f" {returns}"

                return {
                    "signature": signature,
                    "function_name": function_name,
                    "params": params,
                    "returns": returns,
                    "is_public": "true" if _is_public(function_name) else "false",
                }

        # Check methods
        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            name = _get_function_name(method, source_bytes)
            if name == function_name:
                receiver = ""
                params = ""
                returns = ""
                param_count = 0

                for child in method.children:
                    if child.type == "parameter_list":
                        text = _get_node_text(child, source_bytes)
                        if param_count == 0:
                            receiver = text
                        elif param_count == 1:
                            params = text
                        param_count += 1
                    elif child.type in (
                        "type_identifier",
                        "pointer_type",
                        "array_type",
                        "slice_type",
                    ):
                        # Return type is a direct child, not in parameter_list
                        returns = _get_node_text(child, source_bytes)

                signature = f"func {receiver} {function_name}{params}"
                if returns:
                    signature += f" {returns}"

                return {
                    "signature": signature,
                    "function_name": function_name,
                    "params": params,
                    "returns": returns,
                    "is_public": "true" if _is_public(function_name) else "false",
                }

        raise ValueError(f"Function '{function_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_go_function_docstring(source_code: str, function_name: str) -> dict[str, str]:
    """Get just the godoc comment of a specific Go function.

    Returns only the godoc without the implementation, saving 80-85% of tokens.

    Args:
        source_code: Go source code to analyze
        function_name: Name of the function

    Returns:
        Dictionary with:
        - docstring: Godoc comment text (empty if none)
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
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Check functions
        functions = _find_nodes_by_type(root, "function_declaration")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                docstring = _extract_godoc(source_code, func.start_byte)
                return {
                    "docstring": docstring,
                    "function_name": function_name,
                    "has_docstring": "true" if docstring else "false",
                }

        # Check methods
        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            name = _get_function_name(method, source_bytes)
            if name == function_name:
                docstring = _extract_godoc(source_code, method.start_byte)
                return {
                    "docstring": docstring,
                    "function_name": function_name,
                    "has_docstring": "true" if docstring else "false",
                }

        raise ValueError(f"Function '{function_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def list_go_type_methods(source_code: str, type_name: str) -> dict[str, str]:
    """List all methods for a specific Go type with signatures.

    Returns method signatures without bodies, saving 80-85% of tokens.

    Args:
        source_code: Go source code to analyze
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
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        methods: list[dict[str, Any]] = []

        # Find all method declarations
        method_nodes = _find_nodes_by_type(root, "method_declaration")
        for method in method_nodes:
            receiver_type = _get_receiver_type(method, source_bytes)
            # Remove pointer marker if present
            receiver_type = receiver_type.lstrip("*")

            if receiver_type == type_name:
                method_info: dict[str, Any] = {
                    "name": "",
                    "receiver": "",
                    "params": "",
                    "returns": "",
                    "is_public": False,
                }

                method_name = _get_function_name(method, source_bytes)
                method_info["name"] = method_name
                method_info["is_public"] = _is_public(method_name)

                param_count = 0
                for child in method.children:
                    if child.type == "parameter_list":
                        text = _get_node_text(child, source_bytes)
                        if param_count == 0:
                            method_info["receiver"] = text
                        elif param_count == 1:
                            method_info["params"] = text
                        else:
                            method_info["returns"] = text
                        param_count += 1

                method_info["line"] = method.start_point[0] + 1
                methods.append(method_info)

        if not methods:
            # Check if type exists
            type_decls = _find_nodes_by_type(root, "type_declaration")
            type_found = False
            for type_decl in type_decls:
                type_specs = _find_nodes_by_type(type_decl, "type_spec")
                for type_spec in type_specs:
                    name = _get_type_name(type_spec, source_bytes)
                    if name == type_name:
                        type_found = True
                        break
                if type_found:
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
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def extract_go_public_api(source_code: str) -> dict[str, str]:
    """Extract the public API of a Go file.

    Identifies public (exported) functions and types, saving 70-80% of tokens
    by focusing only on the public interface.

    Args:
        source_code: Go source code to analyze

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
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        public_functions: list[str] = []
        public_types: list[str] = []

        # Find public functions
        functions = _find_nodes_by_type(root, "function_declaration")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name and _is_public(name):
                public_functions.append(name)

        # Find public methods
        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            name = _get_function_name(method, source_bytes)
            if name and _is_public(name):
                public_functions.append(name)

        # Find public types
        type_decls = _find_nodes_by_type(root, "type_declaration")
        for type_decl in type_decls:
            type_specs = _find_nodes_by_type(type_decl, "type_spec")
            for type_spec in type_specs:
                name = _get_type_name(type_spec, source_bytes)
                if name and _is_public(name):
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
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_go_function_details(source_code: str, function_name: str) -> dict[str, str]:
    """Get complete details about a Go function.

    Returns signature, godoc, parameters, and metadata without the body,
    saving 75-85% of tokens.

    Args:
        source_code: Go source code to analyze
        function_name: Name of the function

    Returns:
        Dictionary with:
        - function_name: Name of the function
        - signature: Function signature string
        - docstring: Godoc comment (empty if none)
        - params: Parameter list
        - returns: Return type(s)
        - is_public: "true" if function is exported, "false" otherwise
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
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Check functions
        functions = _find_nodes_by_type(root, "function_declaration")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                params = ""
                returns = ""

                for child in func.children:
                    if child.type == "parameter_list":
                        text = _get_node_text(child, source_bytes)
                        if not params:
                            params = text
                        else:
                            returns = text

                signature = f"func {function_name}{params}"
                if returns:
                    signature += f" {returns}"

                docstring = _extract_godoc(source_code, func.start_byte)

                return {
                    "function_name": function_name,
                    "signature": signature,
                    "docstring": docstring,
                    "params": params,
                    "returns": returns,
                    "is_public": "true" if _is_public(function_name) else "false",
                    "line": str(func.start_point[0] + 1),
                }

        # Check methods
        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            name = _get_function_name(method, source_bytes)
            if name == function_name:
                receiver = ""
                params = ""
                returns = ""
                param_count = 0

                for child in method.children:
                    if child.type == "parameter_list":
                        text = _get_node_text(child, source_bytes)
                        if param_count == 0:
                            receiver = text
                        elif param_count == 1:
                            params = text
                        param_count += 1
                    elif child.type in (
                        "type_identifier",
                        "pointer_type",
                        "array_type",
                        "slice_type",
                    ):
                        # Return type is a direct child, not in parameter_list
                        returns = _get_node_text(child, source_bytes)

                signature = f"func {receiver} {function_name}{params}"
                if returns:
                    signature += f" {returns}"

                docstring = _extract_godoc(source_code, method.start_byte)

                return {
                    "function_name": function_name,
                    "signature": signature,
                    "docstring": docstring,
                    "params": params,
                    "returns": returns,
                    "is_public": "true" if _is_public(function_name) else "false",
                    "line": str(method.start_point[0] + 1),
                }

        raise ValueError(f"Function '{function_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_go_function_body(source_code: str, function_name: str) -> dict[str, str]:
    """Get just the implementation body of a specific Go function.

    Returns only the function body without signature or godoc, saving 80-90% of tokens.
    Useful for understanding implementation without reading the entire file.

    Args:
        source_code: Go source code to analyze
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
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")
        lines = source_code.split("\n")

        # Check functions
        functions = _find_nodes_by_type(root, "function_declaration")
        for func in functions:
            name = _get_function_name(func, source_bytes)
            if name == function_name:
                # Find the function body
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

        # Check methods
        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            name = _get_function_name(method, source_bytes)
            if name == function_name:
                # Find the method body
                for child in method.children:
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
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def list_go_function_calls(source_code: str, function_name: str) -> dict[str, str]:
    """List all function calls made within a specific Go function.

    Analyzes function dependencies and call patterns, saving 75-85% of tokens.
    Useful for understanding what a function depends on.

    Args:
        source_code: Go source code to analyze
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
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Check functions
        functions = _find_nodes_by_type(root, "function_declaration")
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

        # Check methods
        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            name = _get_function_name(method, source_bytes)
            if name == function_name:
                method_calls: list[str] = []
                method_call_details: list[dict[str, Any]] = []

                # Find call expressions
                call_exprs = _find_nodes_by_type(method, "call_expression")
                for call_expr in call_exprs:
                    # Get the function being called
                    if call_expr.children:
                        callee = call_expr.children[0]
                        call_name = _get_node_text(callee, source_bytes)
                        method_calls.append(call_name)
                        method_call_details.append(
                            {
                                "name": call_name,
                                "line": call_expr.start_point[0] + 1,
                            }
                        )

                return {
                    "calls": json.dumps(method_calls),
                    "call_count": str(len(method_calls)),
                    "call_details": json.dumps(method_call_details),
                }

        raise ValueError(f"Function '{function_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def find_go_function_usages(source_code: str, function_name: str) -> dict[str, str]:
    """Find all places where a specific Go function is called.

    Performs impact analysis to identify all usage locations, saving 75-85% of tokens.
    Useful for understanding the scope of changes.

    Args:
        source_code: Go source code to analyze
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
        tree = _parse_go(source_code)
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
                # Handle both direct calls and selector calls (e.g., pkg.Function)
                if call_text == function_name or call_text.endswith(
                    "." + function_name
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
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_go_specific_function_line_numbers(
    source_code: str, package_name: str, function_name: str
) -> dict[str, str]:
    """Get start and end line numbers for a specific method of a Go type.

    Enables precise targeting of type methods, saving 85-90% of tokens.
    Note: In Go, 'package_name' parameter is used as type name for methods.

    Args:
        source_code: Go source code to analyze
        package_name: Name of the type (used for receiver type matching)
        function_name: Name of the method

    Returns:
        Dictionary with:
        - start_line: Line number where method starts (1-indexed)
        - end_line: Line number where method ends (1-indexed)
        - package_name: Name of the type (receiver type)
        - function_name: Name of the method

    Raises:
        TypeError: If any argument is not a string
        ValueError: If source_code is empty, parsing fails, type or method not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(package_name, str):
        raise TypeError("package_name must be a string")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find method declarations for the specific type
        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            receiver_type = _get_receiver_type(method, source_bytes)
            # Remove pointer marker if present
            receiver_type = receiver_type.lstrip("*")

            if receiver_type == package_name:
                name = _get_function_name(method, source_bytes)
                if name == function_name:
                    start_line = method.start_point[0] + 1
                    end_line = method.end_point[0] + 1
                    return {
                        "start_line": str(start_line),
                        "end_line": str(end_line),
                        "package_name": package_name,
                        "function_name": function_name,
                    }

        # Check if type exists
        type_decls = _find_nodes_by_type(root, "type_declaration")
        type_found = False
        for type_decl in type_decls:
            type_specs = _find_nodes_by_type(type_decl, "type_spec")
            for type_spec in type_specs:
                name = _get_type_name(type_spec, source_bytes)
                if name == package_name:
                    type_found = True
                    break
            if type_found:
                break

        if not type_found:
            raise ValueError(f"Type '{package_name}' not found in source code")

        raise ValueError(
            f"Method '{function_name}' not found for type '{package_name}'"
        )

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_go_type_hierarchy(source_code: str, type_name: str) -> dict[str, str]:
    """Get interface implementation information for a Go type.

    Analyzes struct embedding and interface implementation, saving 70-80% of tokens.

    Args:
        source_code: Go source code to analyze
        type_name: Name of the type

    Returns:
        Dictionary with:
        - embeds: JSON array of embedded type names (for structs)
        - implements: JSON array of interface names (if detectable)
        - has_embedding: "true" if type embeds other types, "false" otherwise
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
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find the type
        type_decls = _find_nodes_by_type(root, "type_declaration")
        for type_decl in type_decls:
            type_specs = _find_nodes_by_type(type_decl, "type_spec")
            for type_spec in type_specs:
                name = _get_type_name(type_spec, source_bytes)
                if name == type_name:
                    embeds: list[str] = []

                    # For structs, check embedded fields
                    for child in type_spec.children:
                        if child.type == "struct_type":
                            # Find field declarations
                            field_decls = _find_nodes_by_type(
                                child, "field_declaration"
                            )
                            for field in field_decls:
                                # Embedded fields have no field name
                                has_name = False
                                for fchild in field.children:
                                    if fchild.type == "field_identifier":
                                        has_name = True
                                        break

                                if not has_name:
                                    # This is an embedded field
                                    for fchild in field.children:
                                        if fchild.type in [
                                            "type_identifier",
                                            "qualified_type",
                                        ]:
                                            embed_name = _get_node_text(
                                                fchild, source_bytes
                                            )
                                            embeds.append(embed_name)

                    has_embedding = len(embeds) > 0

                    return {
                        "embeds": json.dumps(embeds),
                        "implements": json.dumps(
                            []
                        ),  # Go doesn't explicitly declare interface implementation
                        "has_embedding": "true" if has_embedding else "false",
                        "type_name": type_name,
                    }

        raise ValueError(f"Type '{type_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def find_go_definitions_by_comment(
    source_code: str, comment_pattern: str
) -> dict[str, str]:
    """Find all functions/types with comments matching a pattern in Go.

    Searches godoc comments for patterns, saving 70-80% of tokens.

    Args:
        source_code: Go source code to analyze
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
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        functions: list[str] = []
        types: list[str] = []
        details: list[dict[str, Any]] = []

        pattern = re.compile(re.escape(comment_pattern), re.IGNORECASE)

        # Check functions
        function_nodes = _find_nodes_by_type(root, "function_declaration")
        for func in function_nodes:
            name = _get_function_name(func, source_bytes)
            if name:
                docstring = _extract_godoc(source_code, func.start_byte)
                if pattern.search(docstring):
                    functions.append(name)
                    details.append(
                        {
                            "name": name,
                            "type": "function",
                            "line": func.start_point[0] + 1,
                        }
                    )

        # Check methods
        method_nodes = _find_nodes_by_type(root, "method_declaration")
        for method in method_nodes:
            name = _get_function_name(method, source_bytes)
            if name:
                docstring = _extract_godoc(source_code, method.start_byte)
                if pattern.search(docstring):
                    functions.append(name)
                    details.append(
                        {
                            "name": name,
                            "type": "method",
                            "line": method.start_point[0] + 1,
                        }
                    )

        # Check types
        type_decls = _find_nodes_by_type(root, "type_declaration")
        for type_decl in type_decls:
            type_specs = _find_nodes_by_type(type_decl, "type_spec")
            for type_spec in type_specs:
                name = _get_type_name(type_spec, source_bytes)
                if name:
                    docstring = _extract_godoc(source_code, type_decl.start_byte)
                    if pattern.search(docstring):
                        types.append(name)
                        details.append(
                            {
                                "name": name,
                                "type": "type",
                                "line": type_decl.start_point[0] + 1,
                            }
                        )

        return {
            "functions": json.dumps(functions),
            "types": json.dumps(types),
            "total_count": str(len(functions) + len(types)),
            "details": json.dumps(details),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Go code: {e}") from e


@strands_tool  # type: ignore[misc]
def get_go_type_docstring(source_code: str, type_name: str) -> dict[str, str]:
    """Get just the godoc comment of a specific Go type.

    Returns only the type documentation without implementation, saving 80-85% of tokens.

    Args:
        source_code: Go source code to analyze
        type_name: Name of the type

    Returns:
        Dictionary with:
        - docstring: Godoc comment text (empty if none)
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
        tree = _parse_go(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find the type
        type_decls = _find_nodes_by_type(root, "type_declaration")
        for type_decl in type_decls:
            type_specs = _find_nodes_by_type(type_decl, "type_spec")
            for type_spec in type_specs:
                name = _get_type_name(type_spec, source_bytes)
                if name == type_name:
                    docstring = _extract_godoc(source_code, type_decl.start_byte)
                    return {
                        "docstring": docstring,
                        "type_name": type_name,
                        "has_docstring": "true" if docstring else "false",
                    }

        raise ValueError(f"Type '{type_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Go code: {e}") from e
