"""Helper functions for tool management and loading.

This module provides utility functions for loading and managing tools from
different modules, making it easy to integrate with agent frameworks.
"""

from typing import Any, Callable


def merge_tool_lists(*tool_lists: list[Callable[..., Any]]) -> list[Callable[..., Any]]:
    """Merge multiple tool lists into one, removing duplicates.

    Args:
        *tool_lists: Variable number of tool lists to merge

    Returns:
        Combined list of unique tools

    Example:
        >>> tools1 = [func1, func2]
        >>> tools2 = [func2, func3]
        >>> merged = merge_tool_lists(tools1, tools2)
        >>> len(merged) == 3
        True
    """
    seen = set()
    merged = []

    for tool_list in tool_lists:
        for tool in tool_list:
            tool_id = id(tool)
            if tool_id not in seen:
                seen.add(tool_id)
                merged.append(tool)

    return merged


def load_all_analysis_tools() -> list[Callable[..., Any]]:
    """Load all code analysis tools.

    Returns:
        List of 14 code analysis tool functions
    """
    from coding_open_agent_tools import analysis

    return [
        # AST Parsing
        analysis.parse_python_ast,
        analysis.extract_functions,
        analysis.extract_classes,
        analysis.extract_imports,
        # Complexity Analysis
        analysis.calculate_complexity,
        analysis.calculate_function_complexity,
        analysis.get_code_metrics,
        analysis.identify_complex_functions,
        # Import Management
        analysis.find_unused_imports,
        analysis.organize_imports,
        analysis.validate_import_order,
        # Secret Detection
        analysis.scan_for_secrets,
        analysis.scan_directory_for_secrets,
        analysis.validate_secret_patterns,
    ]


def load_all_git_tools() -> list[Callable[..., Any]]:
    """Load all git tools.

    Returns:
        List of 9 git tool functions
    """
    from coding_open_agent_tools import git

    return [
        # Status and diff operations
        git.get_git_status,
        git.get_current_branch,
        git.get_git_diff,
        # Log and blame operations
        git.get_git_log,
        git.get_git_blame,
        git.get_file_history,
        git.get_file_at_commit,
        # Branch information
        git.list_branches,
        git.get_branch_info,
    ]


def load_all_profiling_tools() -> list[Callable[..., Any]]:
    """Load all profiling tools.

    Returns:
        List of 8 profiling tool functions
    """
    from coding_open_agent_tools import profiling

    return [
        # Performance profiling
        profiling.profile_function,
        profiling.profile_script,
        profiling.get_hotspots,
        # Memory analysis
        profiling.measure_memory_usage,
        profiling.detect_memory_leaks,
        profiling.get_memory_snapshot,
        # Benchmarking
        profiling.benchmark_execution,
        profiling.compare_implementations,
    ]


def load_all_quality_tools() -> list[Callable[..., Any]]:
    """Load all quality/static analysis tools.

    Returns:
        List of 7 quality tool functions
    """
    from coding_open_agent_tools import quality

    return [
        # Output parsers
        quality.parse_ruff_json,
        quality.parse_mypy_json,
        quality.parse_pytest_json,
        quality.summarize_static_analysis,
        # Issue analysis
        quality.filter_issues_by_severity,
        quality.group_issues_by_file,
        quality.prioritize_issues,
    ]


def load_all_tools() -> list[Callable[..., Any]]:
    """Load all available tools from all modules.

    Returns:
        List of all 39 tool functions (analysis, git, profiling, quality)

    Example:
        >>> all_tools = load_all_tools()
        >>> len(all_tools) == 39
        True
    """
    return merge_tool_lists(
        load_all_analysis_tools(),
        load_all_git_tools(),
        load_all_profiling_tools(),
        load_all_quality_tools(),
    )
