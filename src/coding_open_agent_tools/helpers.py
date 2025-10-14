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


def load_all_tools() -> list[Callable[..., Any]]:
    """Load all available tools from all modules.

    Returns:
        List of all tool functions

    Example:
        >>> all_tools = load_all_tools()
        >>> len(all_tools) >= 0
        True
    """
    # Will be implemented as modules are added
    return []


# Module-specific loaders will be added as modules are implemented:
# def load_all_analysis_tools() -> list[Callable[..., Any]]: ...
# def load_all_git_tools() -> list[Callable[..., Any]]: ...
# def load_all_profiling_tools() -> list[Callable[..., Any]]: ...
# def load_all_quality_tools() -> list[Callable[..., Any]]: ...
# def load_all_shell_tools() -> list[Callable[..., Any]]: ...
# def load_all_codegen_tools() -> list[Callable[..., Any]]: ...
