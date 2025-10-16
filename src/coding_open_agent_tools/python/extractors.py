"""Python code extractors for signatures, docstrings, types, and dependencies.

This module provides extraction functions to pull structured data from Python code:
- Function signature parsing (parameters, return types)
- Docstring information extraction (summary, args, returns)
- Type annotation extraction
- Function dependency analysis
"""

import ast
import re
from typing import Any

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def parse_function_signature(source_code: str, function_name: str) -> dict[str, Any]:
    """Extract function signature components from Python code.

    Parses function definition to extract parameters, types, defaults, and return type.
    This is tedious for agents to parse repeatedly, so we provide structured output.

    Args:
        source_code: Python source code containing the function
        function_name: Name of the function to parse

    Returns:
        Dictionary with:
        - function_name: Name of the function
        - parameters: List of parameter dictionaries with:
          - name: Parameter name
          - type_hint: Type annotation (empty if none)
          - has_default: "true" or "false"
          - default_value: Default value (empty if none)
        - return_type: Return type annotation (empty if none)
        - is_async: "true" or "false"
        - total_parameters: String count of parameters

    Raises:
        TypeError: If source_code or function_name is not a string
        ValueError: If source_code is empty or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(function_name, str):
        raise TypeError("function_name must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")
    if not function_name.strip():
        raise ValueError("function_name cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Cannot parse source code: {e}") from e

    function_node = None
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == function_name
        ):
            function_node = node
            break

    if function_node is None:
        raise ValueError(f"Function '{function_name}' not found in source code")

    parameters: list[dict[str, str]] = []

    # Get default values (aligned from the right)
    defaults = function_node.args.defaults
    num_defaults = len(defaults)
    num_args = len(function_node.args.args)

    for i, arg in enumerate(function_node.args.args):
        # Skip self and cls
        if arg.arg in ("self", "cls"):
            continue

        # Check if this parameter has a default value
        default_index = i - (num_args - num_defaults)
        has_default = default_index >= 0

        param_info = {
            "name": arg.arg,
            "type_hint": ast.unparse(arg.annotation) if arg.annotation else "",
            "has_default": "true" if has_default else "false",
            "default_value": ast.unparse(defaults[default_index])
            if has_default
            else "",
        }
        parameters.append(param_info)

    return {
        "function_name": function_name,
        "parameters": parameters,
        "return_type": ast.unparse(function_node.returns)
        if function_node.returns
        else "",
        "is_async": "true"
        if isinstance(function_node, ast.AsyncFunctionDef)
        else "false",
        "total_parameters": str(len(parameters)),
    }


@strands_tool
def extract_docstring_info(source_code: str, function_name: str) -> dict[str, Any]:
    """Extract structured information from a function's docstring.

    Parses Google, NumPy, and Sphinx style docstrings to extract:
    - Summary description
    - Argument descriptions
    - Return value description
    - Raises information
    - Examples

    Args:
        source_code: Python source code containing the function
        function_name: Name of the function to extract docstring from

    Returns:
        Dictionary with:
        - has_docstring: "true" or "false"
        - summary: First line/paragraph of docstring
        - args: List of argument dictionaries with:
          - name: Argument name
          - description: Argument description
        - returns: Description of return value
        - raises: List of exception dictionaries with:
          - exception_type: Exception class name
          - description: When exception is raised
        - examples: List of example code blocks
        - style: Detected docstring style ("google", "numpy", "sphinx", "plain")

    Raises:
        TypeError: If source_code or function_name is not a string
        ValueError: If source_code is empty or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(function_name, str):
        raise TypeError("function_name must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")
    if not function_name.strip():
        raise ValueError("function_name cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Cannot parse source code: {e}") from e

    function_node = None
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == function_name
        ):
            function_node = node
            break

    if function_node is None:
        raise ValueError(f"Function '{function_name}' not found in source code")

    docstring = ast.get_docstring(function_node)

    if not docstring:
        return {
            "has_docstring": "false",
            "summary": "",
            "args": [],
            "returns": "",
            "raises": [],
            "examples": [],
            "style": "none",
        }

    # Extract summary (first non-empty line or paragraph)
    lines = docstring.strip().split("\n")
    summary_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if summary_lines:  # Empty line after content = end of summary
                break
            continue
        # Stop at section headers
        if re.match(
            r"^(Args?|Arguments?|Parameters?|Returns?|Return|Raises?|Examples?|Note|Notes):",
            stripped,
        ):
            break
        summary_lines.append(stripped)

    summary = " ".join(summary_lines)

    # Detect docstring style
    style = "plain"
    if "Args:" in docstring or "Returns:" in docstring or "Raises:" in docstring:
        style = "google"
    elif "Parameters\n" in docstring or "Returns\n" in docstring:
        style = "numpy"
    elif ":param " in docstring or ":return:" in docstring or ":raises:" in docstring:
        style = "sphinx"

    # Extract args (Google style)
    args: list[dict[str, str]] = []
    if style == "google":
        args_match = re.search(r"Args?:\s*\n((?:[ \t]+.+\n)*)", docstring)
        if args_match:
            args_text = args_match.group(1)
            # Parse arg lines: "    param_name: description" or "    param_name (type): description"
            for line in args_text.split("\n"):
                if not line.strip():
                    continue
                # Match "param: desc" or "param (type): desc"
                arg_match = re.match(r"^\s+(\w+)\s*(?:\([^)]+\))?\s*:\s*(.+)$", line)
                if arg_match:
                    args.append(
                        {
                            "name": arg_match.group(1),
                            "description": arg_match.group(2).strip(),
                        }
                    )

    # Extract returns (Google style)
    returns = ""
    if style == "google":
        returns_match = re.search(r"Returns?:\s*\n((?:[ \t]+.+(?:\n|$))*)", docstring)
        if returns_match:
            returns_text = returns_match.group(1)
            returns = " ".join(
                line.strip() for line in returns_text.split("\n") if line.strip()
            )

    # Extract raises (Google style)
    raises: list[dict[str, str]] = []
    if style == "google":
        raises_match = re.search(r"Raises?:\s*\n((?:[ \t]+.+\n)*)", docstring)
        if raises_match:
            raises_text = raises_match.group(1)
            for line in raises_text.split("\n"):
                if not line.strip():
                    continue
                # Match "ExceptionType: description"
                raise_match = re.match(r"^\s+(\w+)\s*:\s*(.+)$", line)
                if raise_match:
                    raises.append(
                        {
                            "exception_type": raise_match.group(1),
                            "description": raise_match.group(2).strip(),
                        }
                    )

    # Extract examples (Google style)
    examples: list[str] = []
    if style == "google":
        examples_match = re.search(r"Examples?:\s*\n((?:[ \t]+.+\n)*)", docstring)
        if examples_match:
            examples_text = examples_match.group(1)
            examples.append(examples_text.strip())

    return {
        "has_docstring": "true",
        "summary": summary,
        "args": args,
        "returns": returns,
        "raises": raises,
        "examples": examples,
        "style": style,
    }


@strands_tool
def extract_type_annotations(source_code: str) -> dict[str, Any]:
    """Extract all type annotations from Python source code.

    Collects type hints from:
    - Function parameters
    - Function return types
    - Variable annotations
    - Class attributes

    Args:
        source_code: Python source code to extract type annotations from

    Returns:
        Dictionary with:
        - functions: List of function type annotation dictionaries with:
          - name: Function name
          - line_number: Line number
          - parameters: List of parameter type hints
          - return_type: Return type annotation
        - variables: List of variable type annotation dictionaries with:
          - name: Variable name
          - line_number: Line number
          - type_hint: Type annotation
        - total_functions: String count of functions with type hints
        - total_variables: String count of variables with type hints

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Cannot parse source code: {e}") from e

    functions: list[dict[str, Any]] = []
    variables: list[dict[str, str]] = []

    for node in ast.walk(tree):
        # Extract function type annotations
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            param_types: list[str] = []
            for arg in node.args.args:
                if arg.annotation:
                    param_types.append(f"{arg.arg}: {ast.unparse(arg.annotation)}")
                else:
                    param_types.append(f"{arg.arg}: (no type)")

            functions.append(
                {
                    "name": node.name,
                    "line_number": str(node.lineno),
                    "parameters": param_types,
                    "return_type": ast.unparse(node.returns)
                    if node.returns
                    else "(no return type)",
                }
            )

        # Extract variable type annotations
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                variables.append(
                    {
                        "name": node.target.id,
                        "line_number": str(node.lineno),
                        "type_hint": ast.unparse(node.annotation),
                    }
                )

    return {
        "functions": functions,
        "variables": variables,
        "total_functions": str(len(functions)),
        "total_variables": str(len(variables)),
    }


@strands_tool
def get_function_dependencies(source_code: str, function_name: str) -> dict[str, Any]:
    """Analyze function dependencies (calls, imports, global variables used).

    Identifies:
    - Functions called within the target function
    - Modules/imports used
    - Global variables referenced
    - Built-in functions used

    Args:
        source_code: Python source code containing the function
        function_name: Name of the function to analyze

    Returns:
        Dictionary with:
        - function_name: Name of analyzed function
        - functions_called: List of function names called
        - modules_used: List of module names used
        - global_variables: List of global variable names referenced
        - builtins_used: List of built-in functions used
        - total_dependencies: String count of total dependencies

    Raises:
        TypeError: If source_code or function_name is not a string
        ValueError: If source_code is empty or function not found
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(function_name, str):
        raise TypeError("function_name must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")
    if not function_name.strip():
        raise ValueError("function_name cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Cannot parse source code: {e}") from e

    function_node = None
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == function_name
        ):
            function_node = node
            break

    if function_node is None:
        raise ValueError(f"Function '{function_name}' not found in source code")

    functions_called: list[str] = []
    modules_used: list[str] = []
    global_variables: list[str] = []

    # Python built-in functions
    builtins = {
        "abs",
        "all",
        "any",
        "ascii",
        "bin",
        "bool",
        "bytes",
        "callable",
        "chr",
        "dict",
        "dir",
        "divmod",
        "enumerate",
        "eval",
        "exec",
        "filter",
        "float",
        "format",
        "frozenset",
        "getattr",
        "globals",
        "hasattr",
        "hash",
        "help",
        "hex",
        "id",
        "input",
        "int",
        "isinstance",
        "issubclass",
        "iter",
        "len",
        "list",
        "locals",
        "map",
        "max",
        "min",
        "next",
        "object",
        "oct",
        "open",
        "ord",
        "pow",
        "print",
        "range",
        "repr",
        "reversed",
        "round",
        "set",
        "setattr",
        "slice",
        "sorted",
        "str",
        "sum",
        "super",
        "tuple",
        "type",
        "vars",
        "zip",
    }
    builtins_used: list[str] = []

    # Get local variable names defined in the function
    local_vars: set[str] = set()
    for node in ast.walk(function_node):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            local_vars.add(node.id)

    # Analyze function body
    for node in ast.walk(function_node):
        # Function calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in builtins:
                    if func_name not in builtins_used:
                        builtins_used.append(func_name)
                elif func_name not in functions_called:
                    functions_called.append(func_name)
            elif isinstance(node.func, ast.Attribute):
                # Module.function() calls
                if isinstance(node.func.value, ast.Name):
                    module_name = node.func.value.id
                    if module_name not in modules_used:
                        modules_used.append(module_name)

        # Name references (potential global variables)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            name = node.id
            # Not a local variable and not a builtin
            if (
                name not in local_vars
                and name not in builtins
                and name not in global_variables
            ):
                global_variables.append(name)

    total_deps = (
        len(functions_called)
        + len(modules_used)
        + len(global_variables)
        + len(builtins_used)
    )

    return {
        "function_name": function_name,
        "functions_called": functions_called,
        "modules_used": modules_used,
        "global_variables": global_variables,
        "builtins_used": sorted(builtins_used),
        "total_dependencies": str(total_deps),
    }
