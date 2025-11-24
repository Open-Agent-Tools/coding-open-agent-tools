"""Python code navigation functions for efficient file exploration.

This module provides navigation functions that enable agents to explore Python
code without reading entire files, saving significant tokens:

- Line number extraction for targeted file reading
- Module overviews for quick understanding
- Function and class discovery
- Signature extraction
- Public API identification

These tools reduce token usage by 80-95% compared to reading entire files.
"""

import ast
import json

from coding_open_agent_tools._decorators import strands_tool
from coding_open_agent_tools.navigation.shared import (
    validate_identifier,
    validate_source_code,
)


@strands_tool
def get_python_function_line_numbers(
    source_code: str, function_name: str
) -> dict[str, str]:
    """Get start and end line numbers for a specific function.

    Enables targeted file reading using Read tool's offset/limit parameters
    instead of reading entire files. Saves 90-95% of tokens.

    Args:
        source_code: Python source code to analyze
        function_name: Name of function to locate

    Returns:
        Dictionary with:
        - start_line: First line of function definition
        - end_line: Last line of function body
        - function_name: The function name (for confirmation)

    Raises:
        TypeError: If source_code or function_name not strings
        ValueError: If source_code is empty or function not found
    """
    validate_source_code(source_code)
    validate_identifier(function_name, "function_name")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return {
                "start_line": str(node.lineno),
                "end_line": str(node.end_lineno)
                if node.end_lineno
                else str(node.lineno),
                "function_name": function_name,
            }

    raise ValueError(f"Function '{function_name}' not found in source code")


@strands_tool
def get_python_class_line_numbers(source_code: str, class_name: str) -> dict[str, str]:
    """Get start and end line numbers for a specific class.

    Enables targeted file reading using Read tool's offset/limit parameters.
    Useful for large classes where reading the entire file is wasteful.

    Args:
        source_code: Python source code to analyze
        class_name: Name of class to locate

    Returns:
        Dictionary with:
        - start_line: First line of class definition
        - end_line: Last line of class body
        - class_name: The class name (for confirmation)

    Raises:
        TypeError: If source_code or class_name not strings
        ValueError: If source_code is empty or class not found
    """
    validate_source_code(source_code)
    validate_identifier(class_name, "class_name")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {
                "start_line": str(node.lineno),
                "end_line": str(node.end_lineno)
                if node.end_lineno
                else str(node.lineno),
                "class_name": class_name,
            }

    raise ValueError(f"Class '{class_name}' not found in source code")


@strands_tool
def get_python_module_overview(source_code: str) -> dict[str, str]:
    """Get high-level overview of Python module contents.

    First function to call when exploring unknown code. Returns structured
    summary instead of requiring agents to parse entire files. Saves 85-90%
    of tokens.

    Args:
        source_code: Python source code to analyze

    Returns:
        Dictionary with:
        - module_docstring: Module-level docstring (empty if none)
        - function_count: Number of top-level functions
        - class_count: Number of top-level classes
        - function_names: JSON array of function names
        - class_names: JSON array of class names
        - import_count: Number of import statements
        - has_main_block: "true" if __name__ == "__main__" present
        - total_lines: Total line count

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty
    """
    validate_source_code(source_code)

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    # Extract module docstring
    module_docstring = ast.get_docstring(tree) or ""

    # Count and collect top-level definitions
    functions: list[str] = []
    classes: list[str] = []
    imports = 0
    has_main = False

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            imports += 1
        elif isinstance(node, ast.If):
            # Check for if __name__ == "__main__"
            if isinstance(node.test, ast.Compare):
                if (
                    isinstance(node.test.left, ast.Name)
                    and node.test.left.id == "__name__"
                ):
                    has_main = True

    total_lines = len(source_code.splitlines())

    return {
        "module_docstring": module_docstring,
        "function_count": str(len(functions)),
        "class_count": str(len(classes)),
        "function_names": json.dumps(functions),
        "class_names": json.dumps(classes),
        "import_count": str(imports),
        "has_main_block": "true" if has_main else "false",
        "total_lines": str(total_lines),
    }


@strands_tool
def list_python_functions(source_code: str) -> list[dict[str, str]]:
    """List all top-level functions with signatures and line numbers.

    Returns structured data about all functions without requiring agents to
    parse files or read implementations. Saves 80-85% of tokens.

    Args:
        source_code: Python source code to analyze

    Returns:
        List of dictionaries, each with:
        - name: Function name
        - signature: Complete function signature
        - start_line: First line of function
        - end_line: Last line of function
        - arg_count: Number of parameters
        - has_docstring: "true" or "false"
        - is_async: "true" or "false"
        - decorators: JSON array of decorator names

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty
    """
    validate_source_code(source_code)

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    functions: list[dict[str, str]] = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Build signature
            args = node.args
            params: list[str] = []

            # Regular args
            for arg in args.args:
                param = arg.arg
                if arg.annotation:
                    param += f": {ast.unparse(arg.annotation)}"
                params.append(param)

            # Return type
            returns = ""
            if node.returns:
                returns = f" -> {ast.unparse(node.returns)}"

            signature = f"{node.name}({', '.join(params)}){returns}"

            # Decorators
            decorator_names = [ast.unparse(d) for d in node.decorator_list]

            functions.append(
                {
                    "name": node.name,
                    "signature": signature,
                    "start_line": str(node.lineno),
                    "end_line": str(node.end_lineno)
                    if node.end_lineno
                    else str(node.lineno),
                    "arg_count": str(len(args.args)),
                    "has_docstring": "true" if ast.get_docstring(node) else "false",
                    "is_async": "true"
                    if isinstance(node, ast.AsyncFunctionDef)
                    else "false",
                    "decorators": json.dumps(decorator_names),
                }
            )

    return functions


@strands_tool
def list_python_classes(source_code: str) -> list[dict[str, str]]:
    """List all top-level classes with basic information.

    Returns structured data about all classes without requiring agents to
    parse files or read implementations.

    Args:
        source_code: Python source code to analyze

    Returns:
        List of dictionaries, each with:
        - name: Class name
        - start_line: First line of class definition
        - end_line: Last line of class body
        - method_count: Number of methods
        - method_names: JSON array of method names
        - base_classes: JSON array of base class names
        - has_docstring: "true" or "false"
        - decorators: JSON array of decorator names

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty
    """
    validate_source_code(source_code)

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    classes: list[dict[str, str]] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            # Extract method names
            methods = [
                n.name
                for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]

            # Extract base classes
            bases = [ast.unparse(base) for base in node.bases]

            # Decorators
            decorator_names = [ast.unparse(d) for d in node.decorator_list]

            classes.append(
                {
                    "name": node.name,
                    "start_line": str(node.lineno),
                    "end_line": str(node.end_lineno)
                    if node.end_lineno
                    else str(node.lineno),
                    "method_count": str(len(methods)),
                    "method_names": json.dumps(methods),
                    "base_classes": json.dumps(bases),
                    "has_docstring": "true" if ast.get_docstring(node) else "false",
                    "decorators": json.dumps(decorator_names),
                }
            )

    return classes


@strands_tool
def get_python_function_signature(
    source_code: str, function_name: str
) -> dict[str, str]:
    """Get just the signature of a specific function.

    Answers "How do I call this function?" without reading implementations
    or full files. Saves 85-90% of tokens.

    Args:
        source_code: Python source code to analyze
        function_name: Name of function to extract signature from

    Returns:
        Dictionary with:
        - signature: Complete function signature with types
        - function_name: The function name (for confirmation)
        - arg_count: Number of parameters
        - has_return_type: "true" or "false"
        - is_async: "true" or "false"

    Raises:
        TypeError: If source_code or function_name not strings
        ValueError: If source_code is empty or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == function_name
        ):
            # Build signature
            args = node.args
            params: list[str] = []

            # Regular args
            for arg in args.args:
                param = arg.arg
                if arg.annotation:
                    param += f": {ast.unparse(arg.annotation)}"
                params.append(param)

            # Return type
            returns = ""
            if node.returns:
                returns = f" -> {ast.unparse(node.returns)}"

            signature = f"{node.name}({', '.join(params)}){returns}"

            return {
                "signature": signature,
                "function_name": function_name,
                "arg_count": str(len(args.args)),
                "has_return_type": "true" if node.returns else "false",
                "is_async": "true"
                if isinstance(node, ast.AsyncFunctionDef)
                else "false",
            }

    raise ValueError(f"Function '{function_name}' not found in source code")


@strands_tool
def get_python_function_docstring(
    source_code: str, function_name: str
) -> dict[str, str]:
    """Get just the docstring of a specific function.

    Answers "What does this function do?" without reading implementations.
    Saves 80-85% of tokens.

    Args:
        source_code: Python source code to analyze
        function_name: Name of function to extract docstring from

    Returns:
        Dictionary with:
        - docstring: Function docstring (empty if none)
        - function_name: The function name (for confirmation)
        - has_docstring: "true" or "false"

    Raises:
        TypeError: If source_code or function_name not strings
        ValueError: If source_code is empty or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == function_name
        ):
            docstring = ast.get_docstring(node) or ""
            return {
                "docstring": docstring,
                "function_name": function_name,
                "has_docstring": "true" if docstring else "false",
            }

    raise ValueError(f"Function '{function_name}' not found in source code")


@strands_tool
def list_python_class_methods(
    source_code: str, class_name: str
) -> list[dict[str, str]]:
    """List all methods in a specific class with signatures.

    Answers "What can this class do?" without reading full implementations.
    Saves 80-85% of tokens.

    Args:
        source_code: Python source code to analyze
        class_name: Name of class to extract methods from

    Returns:
        List of dictionaries, each with:
        - name: Method name
        - signature: Complete method signature
        - start_line: First line of method
        - end_line: Last line of method
        - arg_count: Number of parameters (including self)
        - has_docstring: "true" or "false"
        - is_async: "true" or "false"
        - is_property: "true" or "false"
        - is_classmethod: "true" or "false"
        - is_staticmethod: "true" or "false"

    Raises:
        TypeError: If source_code or class_name not strings
        ValueError: If source_code is empty or class not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(class_name, "class_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            methods: list[dict[str, str]] = []

            for method_node in node.body:
                if isinstance(method_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Build signature
                    args = method_node.args
                    params: list[str] = []

                    for arg in args.args:
                        param = arg.arg
                        if arg.annotation:
                            param += f": {ast.unparse(arg.annotation)}"
                        params.append(param)

                    returns = ""
                    if method_node.returns:
                        returns = f" -> {ast.unparse(method_node.returns)}"

                    signature = f"{method_node.name}({', '.join(params)}){returns}"

                    # Check for decorators
                    decorator_names = [
                        ast.unparse(d) if not isinstance(d, ast.Name) else d.id
                        for d in method_node.decorator_list
                    ]
                    is_property = "property" in decorator_names
                    is_classmethod = "classmethod" in decorator_names
                    is_staticmethod = "staticmethod" in decorator_names

                    methods.append(
                        {
                            "name": method_node.name,
                            "signature": signature,
                            "start_line": str(method_node.lineno),
                            "end_line": str(method_node.end_lineno)
                            if method_node.end_lineno
                            else str(method_node.lineno),
                            "arg_count": str(len(args.args)),
                            "has_docstring": "true"
                            if ast.get_docstring(method_node)
                            else "false",
                            "is_async": "true"
                            if isinstance(method_node, ast.AsyncFunctionDef)
                            else "false",
                            "is_property": "true" if is_property else "false",
                            "is_classmethod": "true" if is_classmethod else "false",
                            "is_staticmethod": "true" if is_staticmethod else "false",
                        }
                    )

            return methods

    raise ValueError(f"Class '{class_name}' not found in source code")


@strands_tool
def extract_python_public_api(source_code: str) -> dict[str, str]:
    """Extract the public API (functions and classes intended for external use).

    Returns functions/classes in __all__ or public (no leading underscore).
    Answers "What's the public interface?" Saves 75-80% of tokens.

    Args:
        source_code: Python source code to analyze

    Returns:
        Dictionary with:
        - has_all_defined: "true" if __all__ is defined
        - public_functions: JSON array of public function names
        - public_classes: JSON array of public class names
        - all_contents: JSON array of names in __all__ (empty if not defined)

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty
    """
    validate_source_code(source_code)

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    # Look for __all__ definition
    all_names: list[str] = []
    has_all = False

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    has_all = True
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(
                                elt.value, str
                            ):
                                all_names.append(elt.value)

    # Get all public (non-underscore) functions and classes
    public_functions: list[str] = []
    public_classes: list[str] = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith("_"):
                public_functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                public_classes.append(node.name)

    return {
        "has_all_defined": "true" if has_all else "false",
        "public_functions": json.dumps(public_functions),
        "public_classes": json.dumps(public_classes),
        "all_contents": json.dumps(all_names),
    }


@strands_tool
def get_python_function_details(source_code: str, function_name: str) -> dict[str, str]:
    """Get complete details about a function (signature, docstring, decorators, line numbers).

    Combines multiple queries into one for efficiency. Returns everything
    EXCEPT the function body/implementation. Saves 70-80% of tokens.

    Args:
        source_code: Python source code to analyze
        function_name: Name of function to analyze

    Returns:
        Dictionary with:
        - function_name: The function name
        - signature: Complete function signature with types
        - docstring: Function docstring (empty if none)
        - start_line: First line of function
        - end_line: Last line of function
        - arg_count: Number of parameters
        - has_return_type: "true" or "false"
        - has_docstring: "true" or "false"
        - is_async: "true" or "false"
        - decorators: JSON array of decorator names

    Raises:
        TypeError: If source_code or function_name not strings
        ValueError: If source_code is empty or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == function_name
        ):
            # Build signature
            args = node.args
            params: list[str] = []

            for arg in args.args:
                param = arg.arg
                if arg.annotation:
                    param += f": {ast.unparse(arg.annotation)}"
                params.append(param)

            returns = ""
            if node.returns:
                returns = f" -> {ast.unparse(node.returns)}"

            signature = f"{node.name}({', '.join(params)}){returns}"

            # Get docstring
            docstring = ast.get_docstring(node) or ""

            # Decorators
            decorator_names = [ast.unparse(d) for d in node.decorator_list]

            return {
                "function_name": function_name,
                "signature": signature,
                "docstring": docstring,
                "start_line": str(node.lineno),
                "end_line": str(node.end_lineno)
                if node.end_lineno
                else str(node.lineno),
                "arg_count": str(len(args.args)),
                "has_return_type": "true" if node.returns else "false",
                "has_docstring": "true" if docstring else "false",
                "is_async": "true"
                if isinstance(node, ast.AsyncFunctionDef)
                else "false",
                "decorators": json.dumps(decorator_names),
            }

    raise ValueError(f"Function '{function_name}' not found in source code")


@strands_tool
def get_python_function_body(source_code: str, function_name: str) -> dict[str, str]:
    """Get just the implementation body of a specific function.

    Extracts function implementation without reading entire file. Useful when
    you need to see the logic without surrounding context. Saves 80-90% of tokens.

    Args:
        source_code: Python source code to analyze
        function_name: Name of function to extract body from

    Returns:
        Dictionary with:
        - body: Function implementation code (without def line)
        - start_line: First line of body
        - end_line: Last line of body
        - function_name: The function name (for confirmation)

    Raises:
        TypeError: If source_code or function_name not strings
        ValueError: If source_code is empty or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    source_lines = source_code.splitlines()

    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == function_name
        ):
            # Start line is the first line after the function definition
            body_start = node.lineno  # def line
            body_end = node.end_lineno if node.end_lineno else node.lineno

            # Extract body lines (skip the def line)
            if body_start < len(source_lines):
                body_lines = source_lines[body_start:body_end]
                body = "\n".join(body_lines)
            else:
                body = ""

            return {
                "body": body,
                "start_line": str(body_start + 1),  # Body starts after def line
                "end_line": str(body_end),
                "function_name": function_name,
            }

    raise ValueError(f"Function '{function_name}' not found in source code")


@strands_tool
def list_python_function_calls(source_code: str, function_name: str) -> dict[str, str]:
    """List all function calls made within a specific function.

    Analyzes dependencies by showing what functions are called. Saves 75-85%
    of tokens compared to reading and parsing manually.

    Args:
        source_code: Python source code to analyze
        function_name: Name of function to analyze

    Returns:
        Dictionary with:
        - calls: JSON array of called function names
        - call_count: Total number of function calls
        - call_details: JSON array of dicts with name, line, and context

    Raises:
        TypeError: If source_code or function_name not strings
        ValueError: If source_code is empty or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    # Find the target function
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == function_name
        ):
            calls: list[str] = []
            call_details: list[dict[str, str]] = []

            # Walk the function body to find calls
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    # Get the function name being called
                    if isinstance(child.func, ast.Name):
                        call_name = child.func.id
                        calls.append(call_name)
                        call_details.append(
                            {
                                "name": call_name,
                                "line": str(child.lineno),
                                "type": "direct_call",
                            }
                        )
                    elif isinstance(child.func, ast.Attribute):
                        call_name = child.func.attr
                        calls.append(call_name)
                        call_details.append(
                            {
                                "name": call_name,
                                "line": str(child.lineno),
                                "type": "method_call",
                            }
                        )

            return {
                "calls": json.dumps(list(set(calls))),  # Unique names
                "call_count": str(len(calls)),
                "call_details": json.dumps(call_details),
            }

    raise ValueError(f"Function '{function_name}' not found in source code")


@strands_tool
def find_python_function_usages(source_code: str, function_name: str) -> dict[str, str]:
    """Find all places where a specific function is called.

    Impact analysis tool - shows where function is used before refactoring.
    Saves 75-85% of tokens.

    Args:
        source_code: Python source code to analyze
        function_name: Name of function to find usages of

    Returns:
        Dictionary with:
        - usages: JSON array of usage locations
        - usage_count: Total number of usages found
        - usage_details: JSON array with line, context, and calling function

    Raises:
        TypeError: If source_code or function_name not strings
        ValueError: If source_code is empty
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(function_name, "function_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    usages: list[str] = []
    usage_details: list[dict[str, str]] = []
    source_lines = source_code.splitlines()

    # Track which function we're currently in
    current_function = "module_level"

    for node in ast.walk(tree):
        # Track function context
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            current_function = node.name

        # Find calls to the target function
        if isinstance(node, ast.Call):
            called_name = None
            if isinstance(node.func, ast.Name):
                called_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                called_name = node.func.attr

            if called_name == function_name:
                line_num = node.lineno
                context = (
                    source_lines[line_num - 1].strip()
                    if line_num <= len(source_lines)
                    else ""
                )
                usages.append(str(line_num))
                usage_details.append(
                    {
                        "line": str(line_num),
                        "context": context,
                        "calling_function": current_function,
                    }
                )

    return {
        "usages": json.dumps(usages),
        "usage_count": str(len(usages)),
        "usage_details": json.dumps(usage_details),
    }


@strands_tool
def get_python_method_line_numbers(
    source_code: str, class_name: str, method_name: str
) -> dict[str, str]:
    """Get start and end line numbers for a specific method in a class.

    Like get_python_function_line_numbers but for methods. Enables targeted
    reading of specific methods in large classes. Saves 85-90% of tokens.

    Args:
        source_code: Python source code to analyze
        class_name: Name of class containing the method
        method_name: Name of method to locate

    Returns:
        Dictionary with:
        - start_line: First line of method definition
        - end_line: Last line of method body
        - class_name: The class name (for confirmation)
        - method_name: The method name (for confirmation)

    Raises:
        TypeError: If any parameter is not a string
        ValueError: If source_code is empty, class not found, or method not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(class_name, "class_name")
    validate_identifier(method_name, "method_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    # Find the class
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            # Find the method within the class
            for method_node in node.body:
                if (
                    isinstance(method_node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and method_node.name == method_name
                ):
                    return {
                        "start_line": str(method_node.lineno),
                        "end_line": str(method_node.end_lineno)
                        if method_node.end_lineno
                        else str(method_node.lineno),
                        "class_name": class_name,
                        "method_name": method_name,
                    }

            # Class found but method not found
            raise ValueError(
                f"Method '{method_name}' not found in class '{class_name}'"
            )

    raise ValueError(f"Class '{class_name}' not found in source code")


@strands_tool
def get_python_class_hierarchy(source_code: str, class_name: str) -> dict[str, str]:
    """Get inheritance hierarchy information for a specific class.

    Shows base classes and inheritance structure without reading parent files.
    Saves 70-80% of tokens.

    Args:
        source_code: Python source code to analyze
        class_name: Name of class to analyze

    Returns:
        Dictionary with:
        - base_classes: JSON array of direct base class names
        - base_count: Number of direct base classes
        - has_inheritance: "true" or "false"
        - class_name: The class name (for confirmation)

    Raises:
        TypeError: If source_code or class_name not strings
        ValueError: If source_code is empty or class not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(class_name, "class_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            # Extract base classes
            bases = [ast.unparse(base) for base in node.bases]

            return {
                "base_classes": json.dumps(bases),
                "base_count": str(len(bases)),
                "has_inheritance": "true" if bases else "false",
                "class_name": class_name,
            }

    raise ValueError(f"Class '{class_name}' not found in source code")


@strands_tool
def find_python_definitions_by_decorator(
    source_code: str, decorator_name: str
) -> dict[str, str]:
    """Find all functions/classes with a specific decorator.

    Common use: find all @tool, @property, @cached_property decorated items.
    Saves 70-80% of tokens.

    Args:
        source_code: Python source code to analyze
        decorator_name: Name of decorator to search for (without @)

    Returns:
        Dictionary with:
        - functions: JSON array of function names with this decorator
        - classes: JSON array of class names with this decorator
        - total_count: Total number of definitions found
        - details: JSON array with name, type, line, and full decorator string

    Raises:
        TypeError: If source_code or decorator_name not strings
        ValueError: If source_code is empty
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(decorator_name, "decorator_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    functions: list[str] = []
    classes: list[str] = []
    details: list[dict[str, str]] = []

    for node in ast.walk(tree):
        decorators: list[str] = []

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators = [
                ast.unparse(d) if not isinstance(d, ast.Name) else d.id
                for d in node.decorator_list
            ]
            if decorator_name in decorators or any(
                decorator_name in d for d in decorators
            ):
                functions.append(node.name)
                details.append(
                    {
                        "name": node.name,
                        "type": "function",
                        "line": str(node.lineno),
                        "decorators": json.dumps(decorators),
                    }
                )

        elif isinstance(node, ast.ClassDef):
            decorators = [
                ast.unparse(d) if not isinstance(d, ast.Name) else d.id
                for d in node.decorator_list
            ]
            if decorator_name in decorators or any(
                decorator_name in d for d in decorators
            ):
                classes.append(node.name)
                details.append(
                    {
                        "name": node.name,
                        "type": "class",
                        "line": str(node.lineno),
                        "decorators": json.dumps(decorators),
                    }
                )

    total = len(functions) + len(classes)

    return {
        "functions": json.dumps(functions),
        "classes": json.dumps(classes),
        "total_count": str(total),
        "details": json.dumps(details),
    }


@strands_tool
def get_python_class_docstring(source_code: str, class_name: str) -> dict[str, str]:
    """Get just the docstring of a specific class.

    Like get_python_function_docstring but for classes. Saves 80-85% of tokens.

    Args:
        source_code: Python source code to analyze
        class_name: Name of class to extract docstring from

    Returns:
        Dictionary with:
        - docstring: Class docstring (empty if none)
        - class_name: The class name (for confirmation)
        - has_docstring: "true" or "false"

    Raises:
        TypeError: If source_code or class_name not strings
        ValueError: If source_code is empty or class not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    validate_identifier(class_name, "class_name")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}") from e

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            docstring = ast.get_docstring(node) or ""
            return {
                "docstring": docstring,
                "class_name": class_name,
                "has_docstring": "true" if docstring else "false",
            }

    raise ValueError(f"Class '{class_name}' not found in source code")
