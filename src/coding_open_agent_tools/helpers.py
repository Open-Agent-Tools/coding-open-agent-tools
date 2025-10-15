"""Helper functions for tool management and loading.

This module provides utility functions for loading and managing tools from
different modules, making it easy to integrate with agent frameworks.
"""

from typing import Any, Callable, Union


def merge_tool_lists(
    *args: Union[list[Callable[..., Any]], Callable[..., Any]],
) -> list[Callable[..., Any]]:
    """Merge multiple tool lists and individual functions into a single list.

    This function automatically deduplicates tools based on their function name and module.
    If the same function appears multiple times, only the first occurrence is kept.

    Args:
        *args: Tool lists (List[Callable]) and/or individual functions (Callable)

    Returns:
        Combined list of all tools with duplicates removed

    Raises:
        TypeError: If any argument is not a list of callables or a callable

    Example:
        >>> def custom_tool(x): return x
        >>> analysis_tools = load_all_analysis_tools()
        >>> git_tools = load_all_git_tools()
        >>> all_tools = merge_tool_lists(analysis_tools, git_tools, custom_tool)
        >>> custom_tool in all_tools
        True
    """
    merged = []
    seen = set()  # Track (name, module) tuples to detect duplicates

    for arg in args:
        if callable(arg):
            # Single function
            func_key = (arg.__name__, getattr(arg, "__module__", ""))
            if func_key not in seen:
                merged.append(arg)
                seen.add(func_key)
        elif isinstance(arg, list):
            # List of functions
            for item in arg:
                if not callable(item):
                    raise TypeError(
                        f"All items in tool lists must be callable, got {type(item)}"
                    )
                func_key = (item.__name__, getattr(item, "__module__", ""))
                if func_key not in seen:
                    merged.append(item)
                    seen.add(func_key)
        else:
            raise TypeError(
                f"Arguments must be callable or list of callables, got {type(arg)}"
            )

    return merged


def load_all_analysis_tools() -> list[Callable[..., Any]]:
    """Load all code analysis tools as a list of callable functions.

    Returns:
        List of 14 code analysis tool functions

    Example:
        >>> analysis_tools = load_all_analysis_tools()
        >>> len(analysis_tools) == 14
        True
    """
    from coding_open_agent_tools import analysis

    tools = []
    for name in analysis.__all__:
        func = getattr(analysis, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_git_tools() -> list[Callable[..., Any]]:
    """Load all git tools as a list of callable functions.

    Returns:
        List of 9 git tool functions

    Example:
        >>> git_tools = load_all_git_tools()
        >>> len(git_tools) == 9
        True
    """
    from coding_open_agent_tools import git

    tools = []
    for name in git.__all__:
        func = getattr(git, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_profiling_tools() -> list[Callable[..., Any]]:
    """Load all profiling tools as a list of callable functions.

    Returns:
        List of 8 profiling tool functions

    Example:
        >>> profiling_tools = load_all_profiling_tools()
        >>> len(profiling_tools) == 8
        True
    """
    from coding_open_agent_tools import profiling

    tools = []
    for name in profiling.__all__:
        func = getattr(profiling, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_quality_tools() -> list[Callable[..., Any]]:
    """Load all quality/static analysis tools as a list of callable functions.

    Returns:
        List of 7 quality tool functions

    Example:
        >>> quality_tools = load_all_quality_tools()
        >>> len(quality_tools) == 7
        True
    """
    from coding_open_agent_tools import quality

    tools = []
    for name in quality.__all__:
        func = getattr(quality, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_shell_tools() -> list[Callable[..., Any]]:
    """Load all shell validation and analysis tools as a list of callable functions.

    Returns:
        List of 13 shell tool functions

    Example:
        >>> shell_tools = load_all_shell_tools()
        >>> len(shell_tools) == 13
        True
    """
    from coding_open_agent_tools import shell

    tools = []
    for name in shell.__all__:
        func = getattr(shell, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_python_tools() -> list[Callable[..., Any]]:
    """Load all Python validation and analysis tools as a list of callable functions.

    Returns:
        List of 15 Python tool functions

    Example:
        >>> python_tools = load_all_python_tools()
        >>> len(python_tools) == 15
        True
    """
    from coding_open_agent_tools import python

    tools = []
    for name in python.__all__:
        func = getattr(python, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_database_tools() -> list[Callable[..., Any]]:
    """Load all SQLite database operation tools as a list of callable functions.

    Returns:
        List of 18 database tool functions

    Example:
        >>> database_tools = load_all_database_tools()
        >>> len(database_tools) == 18
        True
    """
    from coding_open_agent_tools import database

    tools = []
    for name in database.__all__:
        func = getattr(database, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_tools() -> list[Callable[..., Any]]:
    """Load all available tools from all modules.

    Returns:
        List of all 84 tool functions (analysis, git, profiling, quality, shell, python, database)

    Example:
        >>> all_tools = load_all_tools()
        >>> len(all_tools) == 84
        True
    """
    return merge_tool_lists(
        load_all_analysis_tools(),
        load_all_git_tools(),
        load_all_profiling_tools(),
        load_all_quality_tools(),
        load_all_shell_tools(),
        load_all_python_tools(),
        load_all_database_tools(),
    )
