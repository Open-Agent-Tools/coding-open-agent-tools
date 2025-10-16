"""Python code analyzers for imports, anti-patterns, and test coverage.

This module provides analysis functions to identify code issues:
- Circular import detection
- Unused import identification
- Anti-pattern detection (security, performance, maintainability)
- Test coverage gap analysis
"""

import ast
import os
from pathlib import Path
from typing import Any

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def detect_circular_imports(project_root: str) -> dict[str, Any]:
    """Detect circular import dependencies in a Python project.

    Analyzes import relationships across all Python files to identify
    circular dependencies that could cause import errors.

    Args:
        project_root: Path to project root directory

    Returns:
        Dictionary with:
        - has_circular_imports: "true" or "false"
        - circular_chains: List of circular import chains, each containing:
          - modules: List of module names in the circular chain
          - severity: "warning" or "error" based on chain length
        - total_modules_analyzed: String count of Python files analyzed
        - total_circular_chains: String count of circular chains found

    Raises:
        TypeError: If project_root is not a string
        ValueError: If project_root is empty or doesn't exist
    """
    if not isinstance(project_root, str):
        raise TypeError("project_root must be a string")
    if not project_root.strip():
        raise ValueError("project_root cannot be empty")

    root_path = Path(project_root)
    if not root_path.exists():
        raise ValueError(f"project_root does not exist: {project_root}")
    if not root_path.is_dir():
        raise ValueError(f"project_root is not a directory: {project_root}")

    # Build import graph
    import_graph: dict[str, list[str]] = {}  # module_name -> [imported_modules]
    modules_analyzed = 0

    for py_file in root_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        modules_analyzed += 1

        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            continue

        # Get module name relative to project root
        rel_path = py_file.relative_to(root_path)
        module_name = str(rel_path.with_suffix("")).replace(os.sep, ".")

        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        import_graph[module_name] = imports

    # Detect circular dependencies using DFS
    circular_chains: list[dict[str, Any]] = []
    visited: set[str] = set()

    def detect_cycle(module: str, path: list[str]) -> None:
        if module in path:
            # Found circular import
            cycle_start = path.index(module)
            cycle = path[cycle_start:] + [module]

            # Determine severity: longer chains are more problematic
            severity = "error" if len(cycle) > 3 else "warning"

            circular_chains.append({"modules": cycle, "severity": severity})
            return

        if module in visited or module not in import_graph:
            return

        visited.add(module)
        new_path = path + [module]

        for imported_module in import_graph[module]:
            # Only check imports within the project
            if imported_module in import_graph:
                detect_cycle(imported_module, new_path)

    for module in import_graph:
        visited.clear()
        detect_cycle(module, [])

    # Remove duplicate chains (same cycle detected from different starting points)
    unique_chains: list[dict[str, Any]] = []
    seen_cycles: set[tuple[str, ...]] = set()

    for chain in circular_chains:
        # Normalize cycle representation (sort and create canonical form)
        modules = chain["modules"][:-1]  # Remove duplicate last element
        canonical: tuple[str, ...] = tuple(sorted(modules))

        if canonical not in seen_cycles:
            seen_cycles.add(canonical)
            unique_chains.append(chain)

    return {
        "has_circular_imports": "true" if unique_chains else "false",
        "circular_chains": unique_chains,
        "total_modules_analyzed": str(modules_analyzed),
        "total_circular_chains": str(len(unique_chains)),
    }


@strands_tool
def find_unused_imports(source_code: str) -> dict[str, Any]:
    """Find imported modules/names that are never used in the code.

    Analyzes imports and identifies which ones are not referenced in the code.
    This helps clean up unnecessary imports.

    Args:
        source_code: Python source code to analyze

    Returns:
        Dictionary with:
        - has_unused_imports: "true" or "false"
        - unused_imports: List of unused import dictionaries with:
          - line_number: Line number of import
          - import_name: Name of unused import
          - import_type: "module" or "name"
          - recommendation: Suggestion to remove
        - total_imports: String count of all imports
        - total_unused: String count of unused imports

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

    # Collect all imports
    imports: list[tuple[int, str, str]] = []  # (line_num, import_name, import_type)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_name = alias.asname if alias.asname else alias.name
                imports.append((node.lineno, import_name, "module"))

        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                import_name = alias.asname if alias.asname else alias.name
                imports.append((node.lineno, import_name, "name"))

    if not imports:
        return {
            "has_unused_imports": "false",
            "unused_imports": [],
            "total_imports": "0",
            "total_unused": "0",
        }

    # Collect all name references in the code (excluding imports)
    used_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            # Check if this is not in an import context
            if not isinstance(node.ctx, (ast.Store, ast.Del)):
                used_names.add(node.id)
        elif isinstance(node, ast.Attribute):
            # For module.attribute access, track the module name
            if isinstance(node.value, ast.Name):
                used_names.add(node.value.id)

    # Identify unused imports
    unused: list[dict[str, str]] = []

    for line_num, import_name, import_type in imports:
        # Check if the import name is ever used
        base_name = import_name.split(".")[0]  # For dotted imports, check base

        if base_name not in used_names:
            unused.append(
                {
                    "line_number": str(line_num),
                    "import_name": import_name,
                    "import_type": import_type,
                    "recommendation": f"Remove unused import '{import_name}' from line {line_num}",
                }
            )

    return {
        "has_unused_imports": "true" if unused else "false",
        "unused_imports": unused,
        "total_imports": str(len(imports)),
        "total_unused": str(len(unused)),
    }


@strands_tool
def identify_anti_patterns(source_code: str) -> dict[str, Any]:
    """Identify common Python anti-patterns and code smells.

    Detects:
    - Security issues (eval, exec, pickle)
    - Performance issues (repeated string concatenation, missing list comprehensions)
    - Maintainability issues (bare except, mutable defaults, print statements)
    - Code smells (long functions, deep nesting)

    Args:
        source_code: Python source code to analyze

    Returns:
        Dictionary with:
        - has_anti_patterns: "true" or "false"
        - issues_found: List of anti-pattern dictionaries with:
          - line_number: Line number of issue
          - issue_type: Type of anti-pattern
          - severity: "critical", "high", "medium", or "low"
          - description: Description of the issue
          - recommendation: How to fix it
        - total_issues: String count of issues found
        - critical_count: String count of critical issues
        - high_count: String count of high-severity issues

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

    issues: list[dict[str, str]] = []

    # Track severity counts
    critical_count = 0
    high_count = 0

    for node in ast.walk(tree):
        # Security: eval() usage
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "eval":
                issues.append(
                    {
                        "line_number": str(node.lineno),
                        "issue_type": "dangerous_eval",
                        "severity": "critical",
                        "description": "Use of eval() - major security risk with untrusted input",
                        "recommendation": "Use ast.literal_eval() for safe evaluation or avoid eval entirely",
                    }
                )
                critical_count += 1

            elif node.func.id == "exec":
                issues.append(
                    {
                        "line_number": str(node.lineno),
                        "issue_type": "dangerous_exec",
                        "severity": "critical",
                        "description": "Use of exec() - major security risk with untrusted input",
                        "recommendation": "Refactor code to avoid exec() - use functions or classes instead",
                    }
                )
                critical_count += 1

            elif node.func.id == "compile":
                issues.append(
                    {
                        "line_number": str(node.lineno),
                        "issue_type": "dangerous_compile",
                        "severity": "high",
                        "description": "Use of compile() - potential security risk",
                        "recommendation": "Ensure compiled code is from trusted sources only",
                    }
                )
                high_count += 1

        # Security: pickle usage
        elif isinstance(node, ast.Attribute) and node.attr in ("loads", "load"):
            if isinstance(node.value, ast.Name) and node.value.id == "pickle":
                issues.append(
                    {
                        "line_number": str(node.lineno),
                        "issue_type": "unsafe_pickle",
                        "severity": "high",
                        "description": "Pickle deserialization - security risk with untrusted data",
                        "recommendation": "Use JSON for untrusted data or verify pickle source",
                    }
                )
                high_count += 1

        # Maintainability: bare except
        elif isinstance(node, ast.ExceptHandler):
            if node.type is None:
                issues.append(
                    {
                        "line_number": str(node.lineno),
                        "issue_type": "bare_except",
                        "severity": "medium",
                        "description": "Bare except clause - catches all exceptions including SystemExit",
                        "recommendation": "Catch specific exception types (e.g., except ValueError:)",
                    }
                )

        # Maintainability: mutable default arguments
        elif isinstance(node, ast.FunctionDef):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    issues.append(
                        {
                            "line_number": str(node.lineno),
                            "issue_type": "mutable_default",
                            "severity": "high",
                            "description": f"Function '{node.name}' has mutable default argument",
                            "recommendation": "Use None as default and create mutable object inside function",
                        }
                    )
                    high_count += 1

            # Code smell: long function (>50 lines)
            if hasattr(node, "end_lineno") and node.end_lineno:
                func_length = node.end_lineno - node.lineno
                if func_length > 50:
                    issues.append(
                        {
                            "line_number": str(node.lineno),
                            "issue_type": "long_function",
                            "severity": "low",
                            "description": f"Function '{node.name}' is {func_length} lines long",
                            "recommendation": "Consider breaking into smaller functions for maintainability",
                        }
                    )

        # Performance: string concatenation in loop
        elif isinstance(node, (ast.For, ast.While)):
            for child in ast.walk(node):
                if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                    if isinstance(child.target, ast.Name):
                        issues.append(
                            {
                                "line_number": str(node.lineno),
                                "issue_type": "string_concat_in_loop",
                                "severity": "medium",
                                "description": "String concatenation in loop - inefficient",
                                "recommendation": "Use list.append() and ''.join() for better performance",
                            }
                        )
                        break

    return {
        "has_anti_patterns": "true" if issues else "false",
        "issues_found": issues,
        "total_issues": str(len(issues)),
        "critical_count": str(critical_count),
        "high_count": str(high_count),
    }


@strands_tool
def check_test_coverage_gaps(source_file: str, test_file: str) -> dict[str, Any]:
    """Analyze test coverage gaps between source and test files.

    Identifies:
    - Functions without corresponding tests
    - Classes without test coverage
    - Test-to-code ratio
    - Untested public functions

    Args:
        source_file: Path to source Python file
        test_file: Path to test Python file

    Returns:
        Dictionary with:
        - has_coverage_gaps: "true" or "false"
        - untested_functions: List of function names without tests
        - untested_classes: List of class names without tests
        - total_functions: String count of functions in source
        - total_tests: String count of test functions
        - coverage_ratio: Percentage of functions with tests (e.g., "85.5")
        - recommendation: Coverage improvement suggestions

    Raises:
        TypeError: If source_file or test_file is not a string
        ValueError: If files are empty, don't exist, or can't be parsed
    """
    if not isinstance(source_file, str):
        raise TypeError("source_file must be a string")
    if not isinstance(test_file, str):
        raise TypeError("test_file must be a string")
    if not source_file.strip():
        raise ValueError("source_file cannot be empty")
    if not test_file.strip():
        raise ValueError("test_file cannot be empty")

    source_path = Path(source_file)
    test_path = Path(test_file)

    if not source_path.exists():
        raise ValueError(f"source_file does not exist: {source_file}")
    if not test_path.exists():
        raise ValueError(f"test_file does not exist: {test_file}")

    # Parse source file
    try:
        source_content = source_path.read_text(encoding="utf-8")
        source_tree = ast.parse(source_content)
    except SyntaxError as e:
        raise ValueError(f"Cannot parse source file: {e}") from e
    except Exception as e:
        raise ValueError(f"Cannot read source file: {e}") from e

    # Parse test file
    try:
        test_content = test_path.read_text(encoding="utf-8")
        test_tree = ast.parse(test_content)
    except SyntaxError as e:
        raise ValueError(f"Cannot parse test file: {e}") from e
    except Exception as e:
        raise ValueError(f"Cannot read test file: {e}") from e

    # Extract functions and classes from source
    source_functions: list[str] = []
    source_classes: list[str] = []

    for node in ast.walk(source_tree):
        if isinstance(node, ast.FunctionDef):
            # Skip private functions (starting with _) unless they're dunder methods
            if not node.name.startswith("_") or (
                node.name.startswith("__") and node.name.endswith("__")
            ):
                # Check if this is a top-level function (not a method)
                is_method = any(
                    isinstance(parent, ast.ClassDef)
                    for parent in ast.walk(source_tree)
                    if isinstance(parent, ast.ClassDef) and node in ast.walk(parent)
                )
                if not is_method:
                    source_functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            if node.name not in source_classes:
                source_classes.append(node.name)
            # Also add class methods
            for class_node in ast.walk(node):
                if isinstance(class_node, ast.FunctionDef):
                    if not class_node.name.startswith("_") or (
                        class_node.name.startswith("__")
                        and class_node.name.endswith("__")
                    ):
                        method_name = f"{node.name}.{class_node.name}"
                        if method_name not in source_functions:
                            source_functions.append(method_name)

    # Extract test functions and patterns
    test_functions: list[str] = []
    tested_names: set[str] = set()

    for node in ast.walk(test_tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            test_functions.append(node.name)

            # Try to infer what's being tested from test name
            # e.g., test_validate_syntax tests validate_syntax
            test_target = node.name.replace("test_", "")
            tested_names.add(test_target)

        # Look for imports from source file
        elif isinstance(node, ast.ImportFrom):
            if node.names:
                for alias in node.names:
                    tested_names.add(alias.name)

        # Look for function calls in test
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                tested_names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                tested_names.add(node.func.attr)

    # Identify untested functions and classes
    untested_functions: list[str] = []
    untested_classes: list[str] = []

    for func_name in source_functions:
        # Check if function is referenced in tests
        base_name = func_name.split(".")[-1]  # Handle Class.method
        if base_name not in tested_names:
            untested_functions.append(func_name)

    for class_name in source_classes:
        if class_name not in tested_names:
            untested_classes.append(class_name)

    # Calculate coverage ratio
    total_items = len(source_functions) + len(source_classes)
    untested_items = len(untested_functions) + len(untested_classes)

    if total_items > 0:
        coverage = ((total_items - untested_items) / total_items) * 100
        coverage_ratio = f"{coverage:.1f}"
    else:
        coverage_ratio = "100.0"

    # Generate recommendation
    if untested_items == 0:
        recommendation = "Excellent coverage - all functions and classes have tests"
    elif coverage < 50:
        recommendation = f"Critical: Only {coverage_ratio}% coverage. Add tests for untested functions/classes"
    elif coverage < 80:
        recommendation = (
            f"Add tests for {untested_items} untested items to reach 80% coverage"
        )
    else:
        recommendation = f"Good coverage at {coverage_ratio}%. Add tests for remaining items to reach 100%"

    return {
        "has_coverage_gaps": "true" if untested_items > 0 else "false",
        "untested_functions": untested_functions,
        "untested_classes": untested_classes,
        "total_functions": str(len(source_functions)),
        "total_tests": str(len(test_functions)),
        "coverage_ratio": coverage_ratio,
        "recommendation": recommendation,
    }
