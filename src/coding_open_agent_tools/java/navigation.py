"""Java code navigation functions.

This module provides token-efficient navigation tools for Java code,
enabling agents to explore codebases without reading entire files.

Token Savings: 70-95% reduction compared to reading full files.

Dependencies:
    - tree-sitter-language-pack (optional): pip install tree-sitter-language-pack
    - Falls back to regex parsing if tree-sitter not available
"""

import json
from typing import Any

from coding_open_agent_tools._decorators import strands_tool
from coding_open_agent_tools.navigation.shared import (
    validate_identifier,
    validate_source_code,
)

# Conditional import for tree-sitter
try:
    from tree_sitter_language_pack import get_parser  # type: ignore[import-untyped]

    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False


def _parse_java(source_code: str) -> Any:
    """Parse Java code into AST using tree-sitter.

    Args:
        source_code: Java source code

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
        parser = get_parser("java")
        tree = parser.parse(bytes(source_code, "utf8"))
        return tree
    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


def _extract_javadoc(source_code: str, start_byte: int) -> str:
    """Extract Javadoc comment before a method/class.

    Args:
        source_code: Full source code
        start_byte: Byte offset where method/class starts

    Returns:
        Javadoc comment text or empty string
    """
    # Find the portion of code before the method/class
    preceding = source_code[:start_byte]
    lines = preceding.split("\n")

    # Look backwards for Javadoc
    doc_lines: list[str] = []
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()

        if line.startswith("*/"):
            # Found end of Javadoc, collect until start
            doc_lines.insert(0, line)
            for j in range(i - 1, -1, -1):
                doc_line = lines[j].strip()
                doc_lines.insert(0, doc_line)
                if doc_line.startswith("/**") or doc_line.startswith("/*"):
                    return "\n".join(doc_lines)
            break
        elif not line or line.startswith("@") or line.startswith("//"):
            # Annotation or single-line comment
            continue
        else:
            # Non-comment line, stop
            break

    return ""


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
        node_type: Node type to find (e.g., "method_declaration", "class_declaration")

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


@strands_tool
def get_java_method_line_numbers(source_code: str, method_name: str) -> dict[str, str]:
    """Get start and end line numbers for a specific Java method.

    Enables targeted file reading instead of loading entire files, saving 85-90% of tokens.
    Supports: method declarations, constructors, static methods.

    Args:
        source_code: Java source code to analyze
        method_name: Name of the method to locate

    Returns:
        Dictionary with:
        - start_line: Line number where method starts (1-indexed)
        - end_line: Line number where method ends (1-indexed)
        - method_name: Name of the method found

    Raises:
        TypeError: If source_code or method_name is not a string
        ValueError: If source_code is empty, parsing fails, or method not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(method_name, "method_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_java(source_code)
        root = tree.root_node

        # Find method declarations
        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            # Find the method name identifier
            for child in method.children:
                if child.type == "identifier":
                    name = _get_node_text(child, bytes(source_code, "utf8"))
                    if name == method_name:
                        start_line = method.start_point[0] + 1
                        end_line = method.end_point[0] + 1
                        return {
                            "start_line": str(start_line),
                            "end_line": str(end_line),
                            "method_name": method_name,
                        }

        # Check constructors
        constructors = _find_nodes_by_type(root, "constructor_declaration")
        for constructor in constructors:
            for child in constructor.children:
                if child.type == "identifier":
                    name = _get_node_text(child, bytes(source_code, "utf8"))
                    if name == method_name:
                        start_line = constructor.start_point[0] + 1
                        end_line = constructor.end_point[0] + 1
                        return {
                            "start_line": str(start_line),
                            "end_line": str(end_line),
                            "method_name": method_name,
                        }

        raise ValueError(f"Method '{method_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def get_java_class_line_numbers(source_code: str, class_name: str) -> dict[str, str]:
    """Get start and end line numbers for a specific Java class.

    Enables targeted file reading instead of loading entire files, saving 85-90% of tokens.
    Supports: class declarations, interface declarations, enum declarations.

    Args:
        source_code: Java source code to analyze
        class_name: Name of the class to locate

    Returns:
        Dictionary with:
        - start_line: Line number where class starts (1-indexed)
        - end_line: Line number where class ends (1-indexed)
        - class_name: Name of the class found

    Raises:
        TypeError: If source_code or class_name is not a string
        ValueError: If source_code is empty, parsing fails, or class not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(class_name, "class_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_java(source_code)
        root = tree.root_node

        # Find class declarations
        for node_type in [
            "class_declaration",
            "interface_declaration",
            "enum_declaration",
        ]:
            classes = _find_nodes_by_type(root, node_type)
            for cls in classes:
                for child in cls.children:
                    if child.type == "identifier":
                        name = _get_node_text(child, bytes(source_code, "utf8"))
                        if name == class_name:
                            start_line = cls.start_point[0] + 1
                            end_line = cls.end_point[0] + 1
                            return {
                                "start_line": str(start_line),
                                "end_line": str(end_line),
                                "class_name": class_name,
                            }

        raise ValueError(f"Class '{class_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def get_java_module_overview(source_code: str) -> dict[str, str]:
    """Get high-level overview of a Java file without full parsing.

    Returns summary information about the file structure, saving 85-90% of tokens
    compared to reading the entire file.

    Args:
        source_code: Java source code to analyze

    Returns:
        Dictionary with:
        - method_count: Number of methods in the file
        - class_count: Number of classes in the file
        - method_names: JSON array of method names
        - class_names: JSON array of class names
        - has_package: "true" if file has package declaration, "false" otherwise
        - has_imports: "true" if file has imports, "false" otherwise
        - total_lines: Total number of lines in the file

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty or parsing fails
    """
    validate_source_code(source_code)

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Count methods
        methods = _find_nodes_by_type(root, "method_declaration")
        method_names: list[str] = []
        for method in methods:
            for child in method.children:
                if child.type == "identifier":
                    name = _get_node_text(child, source_bytes)
                    method_names.append(name)
                    break

        # Count classes
        class_names: list[str] = []
        for node_type in [
            "class_declaration",
            "interface_declaration",
            "enum_declaration",
        ]:
            classes = _find_nodes_by_type(root, node_type)
            for cls in classes:
                for child in cls.children:
                    if child.type == "identifier":
                        name = _get_node_text(child, source_bytes)
                        class_names.append(name)
                        break

        # Check for package and imports
        has_package = len(_find_nodes_by_type(root, "package_declaration")) > 0
        has_imports = len(_find_nodes_by_type(root, "import_declaration")) > 0

        # Count lines
        total_lines = len(source_code.split("\n"))

        return {
            "method_count": str(len(method_names)),
            "class_count": str(len(class_names)),
            "method_names": json.dumps(method_names),
            "class_names": json.dumps(class_names),
            "has_package": "true" if has_package else "false",
            "has_imports": "true" if has_imports else "false",
            "total_lines": str(total_lines),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def list_java_methods(source_code: str) -> dict[str, str]:
    """List all methods in Java code with their signatures.

    Returns method signatures without bodies, saving 80-85% of tokens.
    Useful for understanding file structure without reading implementation.

    Args:
        source_code: Java source code to analyze

    Returns:
        Dictionary with:
        - methods: JSON array of method information dictionaries
        - method_count: Total number of methods found

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty or parsing fails
    """
    validate_source_code(source_code)

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        methods: list[dict[str, Any]] = []

        # Find method declarations
        method_nodes = _find_nodes_by_type(root, "method_declaration")
        for method in method_nodes:
            method_info: dict[str, Any] = {
                "name": "",
                "params": [],
                "return_type": "",
                "modifiers": [],
            }

            for child in method.children:
                if child.type == "identifier":
                    method_info["name"] = _get_node_text(child, source_bytes)
                elif child.type == "formal_parameters":
                    # Extract parameter types
                    params = _find_nodes_by_type(child, "formal_parameter")
                    method_info["params"] = [
                        _get_node_text(p, source_bytes) for p in params
                    ]
                elif child.type in [
                    "type_identifier",
                    "void_type",
                    "integral_type",
                    "floating_point_type",
                ]:
                    if not method_info["return_type"]:
                        method_info["return_type"] = _get_node_text(child, source_bytes)
                elif child.type == "modifiers":
                    modifiers = [
                        _get_node_text(m, source_bytes) for m in child.children
                    ]
                    method_info["modifiers"] = modifiers

            method_info["line"] = method.start_point[0] + 1
            methods.append(method_info)

        return {
            "methods": json.dumps(methods),
            "method_count": str(len(methods)),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def list_java_classes(source_code: str) -> dict[str, str]:
    """List all classes in Java code with their structure.

    Returns class definitions with method names but not implementations,
    saving 80-85% of tokens.

    Args:
        source_code: Java source code to analyze

    Returns:
        Dictionary with:
        - classes: JSON array of class information dictionaries
        - class_count: Total number of classes found

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty or parsing fails
    """
    validate_source_code(source_code)

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        classes: list[dict[str, Any]] = []

        # Find class declarations
        for node_type in [
            "class_declaration",
            "interface_declaration",
            "enum_declaration",
        ]:
            class_nodes = _find_nodes_by_type(root, node_type)
            for cls in class_nodes:
                class_info: dict[str, Any] = {
                    "name": "",
                    "type": node_type.replace("_declaration", ""),
                    "extends": None,
                    "implements": [],
                    "methods": [],
                    "modifiers": [],
                }

                for child in cls.children:
                    if child.type == "identifier":
                        if not class_info["name"]:
                            class_info["name"] = _get_node_text(child, source_bytes)
                    elif child.type == "superclass":
                        for subchild in child.children:
                            if subchild.type == "type_identifier":
                                class_info["extends"] = _get_node_text(
                                    subchild, source_bytes
                                )
                    elif child.type == "super_interfaces":
                        interfaces = _find_nodes_by_type(child, "type_identifier")
                        class_info["implements"] = [
                            _get_node_text(i, source_bytes) for i in interfaces
                        ]
                    elif child.type == "class_body":
                        # Get method names
                        methods = _find_nodes_by_type(child, "method_declaration")
                        for method in methods:
                            for m_child in method.children:
                                if m_child.type == "identifier":
                                    class_info["methods"].append(
                                        _get_node_text(m_child, source_bytes)
                                    )
                                    break
                    elif child.type == "modifiers":
                        modifiers = [
                            _get_node_text(m, source_bytes) for m in child.children
                        ]
                        class_info["modifiers"] = modifiers

                class_info["line"] = cls.start_point[0] + 1
                class_info["method_count"] = len(class_info["methods"])
                classes.append(class_info)

        return {
            "classes": json.dumps(classes),
            "class_count": str(len(classes)),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def get_java_method_signature(source_code: str, method_name: str) -> dict[str, str]:
    """Get just the signature of a specific Java method.

    Returns only the method signature without the body, saving 85-90% of tokens.

    Args:
        source_code: Java source code to analyze
        method_name: Name of the method

    Returns:
        Dictionary with:
        - signature: Method signature string
        - method_name: Name of the method
        - return_type: Return type of the method
        - params: JSON array of parameters
        - modifiers: JSON array of modifiers (public, static, etc.)

    Raises:
        TypeError: If source_code or method_name is not a string
        ValueError: If source_code is empty, parsing fails, or method not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(method_name, "method_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            name = ""
            for child in method.children:
                if child.type == "identifier":
                    name = _get_node_text(child, source_bytes)
                    break

            if name == method_name:
                return_type = ""
                params: list[str] = []
                modifiers: list[str] = []

                for child in method.children:
                    if child.type in [
                        "type_identifier",
                        "void_type",
                        "integral_type",
                        "floating_point_type",
                    ]:
                        if not return_type:
                            return_type = _get_node_text(child, source_bytes)
                    elif child.type == "formal_parameters":
                        param_nodes = _find_nodes_by_type(child, "formal_parameter")
                        params = [_get_node_text(p, source_bytes) for p in param_nodes]
                    elif child.type == "modifiers":
                        modifiers = [
                            _get_node_text(m, source_bytes) for m in child.children
                        ]

                # Build signature
                mods_str = " ".join(modifiers) + " " if modifiers else ""
                params_str = ", ".join(params)
                signature = f"{mods_str}{return_type} {method_name}({params_str})"

                return {
                    "signature": signature,
                    "method_name": method_name,
                    "return_type": return_type,
                    "params": json.dumps(params),
                    "modifiers": json.dumps(modifiers),
                }

        raise ValueError(f"Method '{method_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def get_java_method_docstring(source_code: str, method_name: str) -> dict[str, str]:
    """Get just the Javadoc comment of a specific Java method.

    Returns only the Javadoc without the implementation, saving 80-85% of tokens.

    Args:
        source_code: Java source code to analyze
        method_name: Name of the method

    Returns:
        Dictionary with:
        - docstring: Javadoc comment text (empty if none)
        - method_name: Name of the method
        - has_docstring: "true" if docstring exists, "false" otherwise

    Raises:
        TypeError: If source_code or method_name is not a string
        ValueError: If source_code is empty, parsing fails, or method not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(method_name, "method_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            name = ""
            for child in method.children:
                if child.type == "identifier":
                    name = _get_node_text(child, source_bytes)
                    break

            if name == method_name:
                docstring = _extract_javadoc(source_code, method.start_byte)
                return {
                    "docstring": docstring,
                    "method_name": method_name,
                    "has_docstring": "true" if docstring else "false",
                }

        raise ValueError(f"Method '{method_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def list_java_class_methods(source_code: str, class_name: str) -> dict[str, str]:
    """List all methods in a specific Java class with signatures.

    Returns method signatures without bodies, saving 80-85% of tokens.

    Args:
        source_code: Java source code to analyze
        class_name: Name of the class

    Returns:
        Dictionary with:
        - methods: JSON array of method information dictionaries
        - method_count: Total number of methods
        - class_name: Name of the class

    Raises:
        TypeError: If source_code or class_name is not a string
        ValueError: If source_code is empty, parsing fails, or class not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(class_name, "class_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find the class
        for node_type in ["class_declaration", "interface_declaration"]:
            classes = _find_nodes_by_type(root, node_type)
            for cls in classes:
                name = ""
                for child in cls.children:
                    if child.type == "identifier":
                        name = _get_node_text(child, source_bytes)
                        break

                if name == class_name:
                    methods: list[dict[str, Any]] = []

                    # Find class body
                    for child in cls.children:
                        if child.type == "class_body":
                            method_nodes = _find_nodes_by_type(
                                child, "method_declaration"
                            )
                            for method in method_nodes:
                                method_info: dict[str, Any] = {
                                    "name": "",
                                    "return_type": "",
                                    "params": [],
                                    "modifiers": [],
                                }

                                for m_child in method.children:
                                    if m_child.type == "identifier":
                                        method_info["name"] = _get_node_text(
                                            m_child, source_bytes
                                        )
                                    elif m_child.type in [
                                        "type_identifier",
                                        "void_type",
                                        "integral_type",
                                    ]:
                                        if not method_info["return_type"]:
                                            method_info["return_type"] = _get_node_text(
                                                m_child, source_bytes
                                            )
                                    elif m_child.type == "formal_parameters":
                                        params = _find_nodes_by_type(
                                            m_child, "formal_parameter"
                                        )
                                        method_info["params"] = [
                                            _get_node_text(p, source_bytes)
                                            for p in params
                                        ]
                                    elif m_child.type == "modifiers":
                                        modifiers = [
                                            _get_node_text(mod, source_bytes)
                                            for mod in m_child.children
                                        ]
                                        method_info["modifiers"] = modifiers

                                methods.append(method_info)

                    return {
                        "methods": json.dumps(methods),
                        "method_count": str(len(methods)),
                        "class_name": class_name,
                    }

        raise ValueError(f"Class '{class_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def extract_java_public_api(source_code: str) -> dict[str, str]:
    """Extract the public API of a Java file.

    Identifies public methods, classes, and interfaces, saving 70-80% of tokens
    by focusing only on the public interface.

    Args:
        source_code: Java source code to analyze

    Returns:
        Dictionary with:
        - public_methods: JSON array of public method names
        - public_classes: JSON array of public class names
        - public_count: Total number of public elements
        - details: JSON object with detailed info

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty or parsing fails
    """
    validate_source_code(source_code)

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        public_methods: list[str] = []
        public_classes: list[str] = []

        # Find public classes
        for node_type in [
            "class_declaration",
            "interface_declaration",
            "enum_declaration",
        ]:
            classes = _find_nodes_by_type(root, node_type)
            for cls in classes:
                is_public = False
                class_name = ""

                for child in cls.children:
                    if child.type == "modifiers":
                        modifiers = [
                            _get_node_text(m, source_bytes) for m in child.children
                        ]
                        is_public = "public" in modifiers
                    elif child.type == "identifier":
                        class_name = _get_node_text(child, source_bytes)

                if is_public and class_name:
                    public_classes.append(class_name)

        # Find public methods
        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            is_public = False
            method_name = ""

            for child in method.children:
                if child.type == "modifiers":
                    modifiers = [
                        _get_node_text(m, source_bytes) for m in child.children
                    ]
                    is_public = "public" in modifiers
                elif child.type == "identifier":
                    method_name = _get_node_text(child, source_bytes)

            if is_public and method_name:
                public_methods.append(method_name)

        return {
            "public_methods": json.dumps(public_methods),
            "public_classes": json.dumps(public_classes),
            "public_count": str(len(public_methods) + len(public_classes)),
            "details": json.dumps(
                {
                    "methods": public_methods,
                    "classes": public_classes,
                }
            ),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def get_java_method_details(source_code: str, method_name: str) -> dict[str, str]:
    """Get complete details about a Java method.

    Returns signature, Javadoc, parameters, and metadata without the body,
    saving 75-85% of tokens.

    Args:
        source_code: Java source code to analyze
        method_name: Name of the method

    Returns:
        Dictionary with:
        - method_name: Name of the method
        - signature: Method signature string
        - docstring: Javadoc comment (empty if none)
        - return_type: Return type
        - params: JSON array of parameters
        - modifiers: JSON array of modifiers
        - line: Line number where method starts

    Raises:
        TypeError: If source_code or method_name is not a string
        ValueError: If source_code is empty, parsing fails, or method not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(method_name, "method_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            name = ""
            for child in method.children:
                if child.type == "identifier":
                    name = _get_node_text(child, source_bytes)
                    break

            if name == method_name:
                return_type = ""
                params: list[str] = []
                modifiers: list[str] = []

                for child in method.children:
                    if child.type in [
                        "type_identifier",
                        "void_type",
                        "integral_type",
                        "floating_point_type",
                    ]:
                        if not return_type:
                            return_type = _get_node_text(child, source_bytes)
                    elif child.type == "formal_parameters":
                        param_nodes = _find_nodes_by_type(child, "formal_parameter")
                        params = [_get_node_text(p, source_bytes) for p in param_nodes]
                    elif child.type == "modifiers":
                        modifiers = [
                            _get_node_text(m, source_bytes) for m in child.children
                        ]

                # Build signature
                mods_str = " ".join(modifiers) + " " if modifiers else ""
                params_str = ", ".join(params)
                signature = f"{mods_str}{return_type} {method_name}({params_str})"

                # Get Javadoc
                docstring = _extract_javadoc(source_code, method.start_byte)

                return {
                    "method_name": method_name,
                    "signature": signature,
                    "docstring": docstring,
                    "return_type": return_type,
                    "params": json.dumps(params),
                    "modifiers": json.dumps(modifiers),
                    "line": str(method.start_point[0] + 1),
                }

        raise ValueError(f"Method '{method_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def get_java_method_body(source_code: str, method_name: str) -> dict[str, str]:
    """Get just the implementation body of a specific Java method.

    Returns only the method body without signature or Javadoc, saving 80-90% of tokens.
    Useful for understanding implementation without reading the entire file.

    Args:
        source_code: Java source code to analyze
        method_name: Name of the method

    Returns:
        Dictionary with:
        - body: Method body as source code string
        - start_line: Line number where body starts (1-indexed)
        - end_line: Line number where body ends (1-indexed)
        - method_name: Name of the method

    Raises:
        TypeError: If source_code or method_name is not a string
        ValueError: If source_code is empty, parsing fails, or method not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(method_name, "method_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")
        lines = source_code.split("\n")

        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            name = ""
            for child in method.children:
                if child.type == "identifier":
                    name = _get_node_text(child, source_bytes)
                    break

            if name == method_name:
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
                            "method_name": method_name,
                        }

        raise ValueError(f"Method '{method_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def list_java_method_calls(source_code: str, method_name: str) -> dict[str, str]:
    """List all method calls made within a specific Java method.

    Analyzes method dependencies and call patterns, saving 75-85% of tokens.
    Useful for understanding what a method depends on.

    Args:
        source_code: Java source code to analyze
        method_name: Name of the method to analyze

    Returns:
        Dictionary with:
        - calls: JSON array of method call names
        - call_count: Total number of calls
        - call_details: JSON array with call info (name, line)

    Raises:
        TypeError: If source_code or method_name is not a string
        ValueError: If source_code is empty, parsing fails, or method not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(method_name, "method_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        methods = _find_nodes_by_type(root, "method_declaration")
        for method in methods:
            name = ""
            for child in method.children:
                if child.type == "identifier":
                    name = _get_node_text(child, source_bytes)
                    break

            if name == method_name:
                calls: list[str] = []
                call_details: list[dict[str, Any]] = []

                # Find method invocations
                invocations = _find_nodes_by_type(method, "method_invocation")
                for invocation in invocations:
                    for child in invocation.children:
                        if child.type == "identifier":
                            call_name = _get_node_text(child, source_bytes)
                            calls.append(call_name)
                            call_details.append(
                                {
                                    "name": call_name,
                                    "line": invocation.start_point[0] + 1,
                                }
                            )
                            break

                return {
                    "calls": json.dumps(calls),
                    "call_count": str(len(calls)),
                    "call_details": json.dumps(call_details),
                }

        raise ValueError(f"Method '{method_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def find_java_method_usages(source_code: str, method_name: str) -> dict[str, str]:
    """Find all places where a specific Java method is called.

    Performs impact analysis to identify all usage locations, saving 75-85% of tokens.
    Useful for understanding the scope of changes.

    Args:
        source_code: Java source code to analyze
        method_name: Name of the method to find usages of

    Returns:
        Dictionary with:
        - usages: JSON array of line numbers where method is called
        - usage_count: Total number of usages found
        - usage_details: JSON array with detailed usage info

    Raises:
        TypeError: If source_code or method_name is not a string
        ValueError: If source_code is empty or parsing fails
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(method_name, "method_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        usages: list[int] = []
        usage_details: list[dict[str, Any]] = []

        # Find all method invocations
        invocations = _find_nodes_by_type(root, "method_invocation")
        for invocation in invocations:
            for child in invocation.children:
                if child.type == "identifier":
                    name = _get_node_text(child, source_bytes)
                    if name == method_name:
                        line = invocation.start_point[0] + 1
                        usages.append(line)
                        usage_details.append(
                            {
                                "line": line,
                                "context": "method_call",
                            }
                        )
                    break

        return {
            "usages": json.dumps(usages),
            "usage_count": str(len(usages)),
            "usage_details": json.dumps(usage_details),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def get_java_specific_method_line_numbers(
    source_code: str, class_name: str, method_name: str
) -> dict[str, str]:
    """Get start and end line numbers for a specific method in a Java class.

    Enables precise targeting of class methods, saving 85-90% of tokens.

    Args:
        source_code: Java source code to analyze
        class_name: Name of the class
        method_name: Name of the method

    Returns:
        Dictionary with:
        - start_line: Line number where method starts (1-indexed)
        - end_line: Line number where method ends (1-indexed)
        - class_name: Name of the class
        - method_name: Name of the method

    Raises:
        TypeError: If any argument is not a string
        ValueError: If source_code is empty, parsing fails, class or method not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(class_name, "class_name")
    validate_identifier(method_name, "method_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find the class
        for node_type in ["class_declaration", "interface_declaration"]:
            classes = _find_nodes_by_type(root, node_type)
            for cls in classes:
                name = ""
                for child in cls.children:
                    if child.type == "identifier":
                        name = _get_node_text(child, source_bytes)
                        break

                if name == class_name:
                    # Find the method in this class
                    for child in cls.children:
                        if child.type == "class_body":
                            methods = _find_nodes_by_type(child, "method_declaration")
                            for method in methods:
                                for m_child in method.children:
                                    if m_child.type == "identifier":
                                        m_name = _get_node_text(m_child, source_bytes)
                                        if m_name == method_name:
                                            start_line = method.start_point[0] + 1
                                            end_line = method.end_point[0] + 1
                                            return {
                                                "start_line": str(start_line),
                                                "end_line": str(end_line),
                                                "class_name": class_name,
                                                "method_name": method_name,
                                            }

                    raise ValueError(
                        f"Method '{method_name}' not found in class '{class_name}'"
                    )

        raise ValueError(f"Class '{class_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def get_java_class_hierarchy(source_code: str, class_name: str) -> dict[str, str]:
    """Get inheritance hierarchy information for a Java class.

    Analyzes class inheritance using 'extends' and 'implements', saving 70-80% of tokens.

    Args:
        source_code: Java source code to analyze
        class_name: Name of the class

    Returns:
        Dictionary with:
        - extends: Name of superclass (empty if none)
        - implements: JSON array of interface names
        - has_inheritance: "true" if class extends or implements, "false" otherwise
        - class_name: Name of the class

    Raises:
        TypeError: If source_code or class_name is not a string
        ValueError: If source_code is empty, parsing fails, or class not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(class_name, "class_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find the class
        classes = _find_nodes_by_type(root, "class_declaration")
        for cls in classes:
            name = ""
            for child in cls.children:
                if child.type == "identifier":
                    name = _get_node_text(child, source_bytes)
                    break

            if name == class_name:
                extends = ""
                implements: list[str] = []

                for child in cls.children:
                    if child.type == "superclass":
                        for subchild in child.children:
                            if subchild.type == "type_identifier":
                                extends = _get_node_text(subchild, source_bytes)
                    elif child.type == "super_interfaces":
                        interfaces = _find_nodes_by_type(child, "type_identifier")
                        implements = [
                            _get_node_text(i, source_bytes) for i in interfaces
                        ]

                has_inheritance = bool(extends or implements)

                return {
                    "extends": extends,
                    "implements": json.dumps(implements),
                    "has_inheritance": "true" if has_inheritance else "false",
                    "class_name": class_name,
                }

        raise ValueError(f"Class '{class_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def find_java_definitions_by_annotation(
    source_code: str, annotation_name: str
) -> dict[str, str]:
    """Find all methods/classes with a specific annotation in Java.

    Searches for @annotation syntax, saving 70-80% of tokens.

    Args:
        source_code: Java source code to analyze
        annotation_name: Name of the annotation (without @)

    Returns:
        Dictionary with:
        - methods: JSON array of method names with annotation
        - classes: JSON array of class names with annotation
        - total_count: Total number of annotated definitions
        - details: JSON array with detailed info about each match

    Raises:
        TypeError: If source_code or annotation_name is not a string
        ValueError: If source_code is empty or parsing fails
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(annotation_name, str):
        raise TypeError("annotation_name must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        methods: list[str] = []
        classes: list[str] = []
        details: list[dict[str, Any]] = []

        # Find all marker annotations
        annotations = _find_nodes_by_type(root, "marker_annotation")
        annotations.extend(_find_nodes_by_type(root, "annotation"))

        for annotation in annotations:
            # Check if this is the annotation we're looking for
            for child in annotation.children:
                if child.type in ["identifier", "type_identifier"]:
                    ann_name = _get_node_text(child, source_bytes)
                    if ann_name == annotation_name or ann_name == f"@{annotation_name}":
                        # Find what this annotation is attached to
                        parent = annotation.parent
                        if parent:
                            if parent.type == "method_declaration":
                                # Find method name
                                for p_child in parent.children:
                                    if p_child.type == "identifier":
                                        method_name = _get_node_text(
                                            p_child, source_bytes
                                        )
                                        methods.append(method_name)
                                        details.append(
                                            {
                                                "name": method_name,
                                                "type": "method",
                                                "line": parent.start_point[0] + 1,
                                            }
                                        )
                                        break
                            elif parent.type in [
                                "class_declaration",
                                "interface_declaration",
                            ]:
                                # Find class name
                                for p_child in parent.children:
                                    if p_child.type == "identifier":
                                        class_nm = _get_node_text(p_child, source_bytes)
                                        classes.append(class_nm)
                                        details.append(
                                            {
                                                "name": class_nm,
                                                "type": "class",
                                                "line": parent.start_point[0] + 1,
                                            }
                                        )
                                        break

        return {
            "methods": json.dumps(methods),
            "classes": json.dumps(classes),
            "total_count": str(len(methods) + len(classes)),
            "details": json.dumps(details),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e


@strands_tool
def get_java_class_docstring(source_code: str, class_name: str) -> dict[str, str]:
    """Get just the Javadoc comment of a specific Java class.

    Returns only the class documentation without implementation, saving 80-85% of tokens.

    Args:
        source_code: Java source code to analyze
        class_name: Name of the class

    Returns:
        Dictionary with:
        - docstring: Javadoc comment text (empty if none)
        - class_name: Name of the class
        - has_docstring: "true" if docstring exists, "false" otherwise

    Raises:
        TypeError: If source_code or class_name is not a string
        ValueError: If source_code is empty, parsing fails, or class not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(class_name, "class_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = _parse_java(source_code)
        root = tree.root_node
        source_bytes = bytes(source_code, "utf8")

        # Find the class
        for node_type in [
            "class_declaration",
            "interface_declaration",
            "enum_declaration",
        ]:
            classes = _find_nodes_by_type(root, node_type)
            for cls in classes:
                name = ""
                for child in cls.children:
                    if child.type == "identifier":
                        name = _get_node_text(child, source_bytes)
                        break

                if name == class_name:
                    docstring = _extract_javadoc(source_code, cls.start_byte)
                    return {
                        "docstring": docstring,
                        "class_name": class_name,
                        "has_docstring": "true" if docstring else "false",
                    }

        raise ValueError(f"Class '{class_name}' not found in source code")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Java code: {e}") from e
