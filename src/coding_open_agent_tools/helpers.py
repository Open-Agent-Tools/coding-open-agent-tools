"""Helper functions for tool management and loading.

This module provides utility functions for loading and managing tools from
different modules, making it easy to integrate with agent frameworks.
"""

import inspect
from typing import Any, Callable, Union

__all__ = [
    "merge_tool_lists",
    "load_all_advanced_analysis_tools",
    "load_all_analysis_tools",
    "load_all_config_tools",
    "load_all_git_tools",
    "load_all_profiling_tools",
    "load_all_quality_tools",
    "load_all_shell_tools",
    "load_all_python_tools",
    "load_all_database_tools",
    "load_all_dependencies_tools",
    "load_all_javascript_tools",
    "load_all_java_tools",
    "load_all_go_tools",
    "load_all_rust_tools",
    "load_all_cpp_tools",
    "load_all_csharp_tools",
    "load_all_ruby_tools",
    "load_all_tools",
    "load_python_loadout",
    "load_javascript_loadout",
    "load_java_loadout",
    "load_cpp_loadout",
    "load_csharp_loadout",
    "load_go_loadout",
    "load_rust_loadout",
    "load_ruby_loadout",
    "load_swift_loadout",
    "load_kotlin_loadout",
    "load_typescript_loadout",
    "get_tool_info",
    "list_all_available_tools",
]


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


def load_all_config_tools() -> list[Callable[..., Any]]:
    """Load all configuration validation and manipulation tools as a list of callable functions.

    Returns:
        List of 28 config tool functions (validation, .env, extraction, formats, security)

    Example:
        >>> config_tools = load_all_config_tools()
        >>> len(config_tools) == 28
        True
    """
    from coding_open_agent_tools import config

    tools = []
    for name in config.__all__:
        func = getattr(config, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_git_tools() -> list[Callable[..., Any]]:
    """Load all git tools as a list of callable functions.

    Returns:
        List of 79 git tool functions

    Example:
        >>> git_tools = load_all_git_tools()
        >>> len(git_tools) == 79
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
    """Load all Python validation, analysis, and navigation tools as a list of callable functions.

    Returns:
        List of 32 Python tool functions (15 existing + 17 navigation tools)

    Example:
        >>> python_tools = load_all_python_tools()
        >>> len(python_tools) == 32
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


def load_all_dependencies_tools() -> list[Callable[..., Any]]:
    """Load all dependency analysis tools as a list of callable functions.

    Returns:
        List of 12 dependency analysis tool functions

    Example:
        >>> dependency_tools = load_all_dependencies_tools()
        >>> len(dependency_tools) == 12
        True
    """
    from coding_open_agent_tools import dependencies

    tools = []
    for name in dependencies.__all__:
        func = getattr(dependencies, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_advanced_analysis_tools() -> list[Callable[..., Any]]:
    """Load all advanced analysis tools as a list of callable functions.

    Returns:
        List of 12 advanced analysis tool functions (security, performance, compliance)

    Example:
        >>> advanced_tools = load_all_advanced_analysis_tools()
        >>> len(advanced_tools) == 12
        True
    """
    from coding_open_agent_tools import advanced_analysis

    tools = []
    for name in advanced_analysis.__all__:
        func = getattr(advanced_analysis, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_tools() -> list[Callable[..., Any]]:
    """Load all available tools from all modules as a single list of callable functions.

    This is a convenience function that loads and combines tools from all
    implemented modules.

    Returns:
        List of all 310 unique tool functions from all modules (automatically deduplicated)

    Example:
        >>> all_tools = load_all_tools()
        >>> len(all_tools) == 310
        True
        >>> # Use with agent frameworks
        >>> # agent = Agent(tools=load_all_tools())
    """
    return merge_tool_lists(
        load_all_advanced_analysis_tools(),  # 12 functions
        load_all_analysis_tools(),  # 14 functions
        load_all_config_tools(),  # 28 functions
        load_all_git_tools(),  # 79 functions
        load_all_profiling_tools(),  # 8 functions
        load_all_quality_tools(),  # 7 functions
        load_all_shell_tools(),  # 13 functions
        load_all_python_tools(),  # 32 functions
        load_all_database_tools(),  # 18 functions
        load_all_dependencies_tools(),  # 12 functions
        load_all_javascript_tools(),  # 29 functions
        load_all_java_tools(),  # 17 functions
        load_all_go_tools(),  # 17 functions
        load_all_rust_tools(),  # 17 functions
        load_all_cpp_tools(),  # 17 functions
        load_all_csharp_tools(),  # 17 functions
        load_all_ruby_tools(),  # 17 functions
    )


def get_tool_info(tool: Callable[..., Any]) -> dict[str, Any]:
    """Get information about a tool function.

    Args:
        tool: The tool function to inspect

    Returns:
        Dictionary containing tool information (name, docstring, signature)

    Raises:
        TypeError: If tool is not callable

    Example:
        >>> from coding_open_agent_tools.analysis import parse_python_ast
        >>> info = get_tool_info(parse_python_ast)
        >>> info['name']
        'parse_python_ast'
    """
    if not callable(tool):
        raise TypeError("Tool must be callable")

    sig = inspect.signature(tool)

    return {
        "name": tool.__name__,
        "docstring": tool.__doc__ or "",
        "signature": str(sig),
        "module": getattr(tool, "__module__", "unknown"),
        "parameters": list(sig.parameters.keys()),
    }


def list_all_available_tools() -> dict[str, list[dict[str, Any]]]:
    """List all available tools organized by category.

    Returns:
        Dictionary with tool categories as keys and lists of tool info as values

    Example:
        >>> tools = list_all_available_tools()
        >>> 'analysis' in tools
        True
        >>> 'git' in tools
        True
    """
    return {
        "analysis": [get_tool_info(tool) for tool in load_all_analysis_tools()],
        "config": [get_tool_info(tool) for tool in load_all_config_tools()],
        "git": [get_tool_info(tool) for tool in load_all_git_tools()],
        "profiling": [get_tool_info(tool) for tool in load_all_profiling_tools()],
        "quality": [get_tool_info(tool) for tool in load_all_quality_tools()],
        "shell": [get_tool_info(tool) for tool in load_all_shell_tools()],
        "python": [get_tool_info(tool) for tool in load_all_python_tools()],
        "database": [get_tool_info(tool) for tool in load_all_database_tools()],
        "javascript": [get_tool_info(tool) for tool in load_all_javascript_tools()],
        "java": [get_tool_info(tool) for tool in load_all_java_tools()],
        "go": [get_tool_info(tool) for tool in load_all_go_tools()],
        "rust": [get_tool_info(tool) for tool in load_all_rust_tools()],
        "cpp": [get_tool_info(tool) for tool in load_all_cpp_tools()],
        "csharp": [get_tool_info(tool) for tool in load_all_csharp_tools()],
        "ruby": [get_tool_info(tool) for tool in load_all_ruby_tools()],
    }


def load_all_javascript_tools() -> list[Callable[..., Any]]:
    """Load all JavaScript and TypeScript navigation and validation tools as callable functions.

    Returns:
        List of 29 JavaScript/TypeScript tool functions (17 navigation + 12 validation)

    Example:
        >>> javascript_tools = load_all_javascript_tools()
        >>> len(javascript_tools) == 29
        True
    """
    from coding_open_agent_tools import javascript

    tools = []
    for name in javascript.__all__:
        func = getattr(javascript, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_java_tools() -> list[Callable[..., Any]]:
    """Load all Java code navigation tools as a list of callable functions.

    Returns:
        List of 17 Java navigation tool functions

    Example:
        >>> java_tools = load_all_java_tools()
        >>> len(java_tools) == 17
        True
    """
    from coding_open_agent_tools import java

    tools = []
    for name in java.__all__:
        func = getattr(java, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_go_tools() -> list[Callable[..., Any]]:
    """Load all Go code navigation tools as a list of callable functions.

    Returns:
        List of 17 Go navigation tool functions

    Example:
        >>> go_tools = load_all_go_tools()
        >>> len(go_tools) == 17
        True
    """
    from coding_open_agent_tools import go

    tools = []
    for name in go.__all__:
        func = getattr(go, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_rust_tools() -> list[Callable[..., Any]]:
    """Load all Rust code navigation tools as a list of callable functions.

    Returns:
        List of 17 Rust navigation tool functions

    Example:
        >>> rust_tools = load_all_rust_tools()
        >>> len(rust_tools) == 17
        True
    """
    from coding_open_agent_tools import rust

    tools = []
    for name in rust.__all__:
        func = getattr(rust, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_cpp_tools() -> list[Callable[..., Any]]:
    """Load all C++ code navigation tools as a list of callable functions.

    Returns:
        List of 17 C++ navigation tool functions

    Example:
        >>> cpp_tools = load_all_cpp_tools()
        >>> len(cpp_tools) == 17
        True
    """
    from coding_open_agent_tools import cpp

    tools = []
    for name in cpp.__all__:
        func = getattr(cpp, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_csharp_tools() -> list[Callable[..., Any]]:
    """Load all C# code navigation tools as a list of callable functions.

    Returns:
        List of 17 C# navigation tool functions

    Example:
        >>> csharp_tools = load_all_csharp_tools()
        >>> len(csharp_tools) == 17
        True
    """
    from coding_open_agent_tools import csharp

    tools = []
    for name in csharp.__all__:
        func = getattr(csharp, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_ruby_tools() -> list[Callable[..., Any]]:
    """Load all Ruby code navigation tools as a list of callable functions.

    Returns:
        List of 17 Ruby navigation tool functions

    Example:
        >>> ruby_tools = load_all_ruby_tools()
        >>> len(ruby_tools) == 17
        True
    """
    from coding_open_agent_tools import ruby

    tools = []
    for name in ruby.__all__:
        func = getattr(ruby, name)
        if callable(func):
            tools.append(func)
    return tools


def load_python_loadout() -> list[Callable[..., Any]]:
    """Load the complete toolset for Python-focused development agents.

    This is the recommended loadout for agents working primarily on Python projects.
    Includes navigation, analysis, quality checking, version control, and profiling.

    Included modules:
    - Python navigation/validation (32 functions) - Core language tools
    - Code analysis (14 functions) - AST, complexity, imports, secrets
    - Quality tools (7 functions) - ruff, mypy, pytest parsing
    - Git operations (79 functions) - Version control
    - Shell validation (13 functions) - Script analysis & security
    - Database operations (18 functions) - SQLite for agent memory
    - Profiling tools (8 functions) - Performance & memory analysis

    Returns:
        List of 171 tool functions optimized for Python development

    Example:
        >>> python_agent_tools = load_python_loadout()
        >>> len(python_agent_tools) == 171
        True
    """
    return merge_tool_lists(
        load_all_python_tools(),  # 32 - Python navigation, validation, analysis
        load_all_analysis_tools(),  # 14 - AST parsing, complexity, imports, secrets
        load_all_quality_tools(),  # 7 - ruff, mypy, pytest output parsing
        load_all_git_tools(),  # 79 - Full version control operations
        load_all_shell_tools(),  # 13 - Shell script validation & security
        load_all_database_tools(),  # 18 - SQLite operations for agent memory
        load_all_profiling_tools(),  # 8 - Performance & memory profiling
    )


def load_javascript_loadout() -> list[Callable[..., Any]]:
    """Load the complete toolset for JavaScript/TypeScript-focused development agents.

    This is the recommended loadout for agents working primarily on JavaScript/TypeScript projects.
    Includes navigation, analysis, version control, and database operations.

    Included modules:
    - JavaScript/TypeScript navigation & validation (29 functions) - Core language tools
    - Code analysis (14 functions) - AST, complexity, imports, secrets
    - Git operations (79 functions) - Version control
    - Shell validation (13 functions) - Script analysis & security
    - Database operations (18 functions) - SQLite for agent memory
    - Profiling tools (8 functions) - Performance & memory analysis

    Returns:
        List of 161 tool functions optimized for JavaScript/TypeScript development

    Example:
        >>> js_agent_tools = load_javascript_loadout()
        >>> len(js_agent_tools) == 161
        True
    """
    return merge_tool_lists(
        load_all_javascript_tools(),  # 29 - JavaScript/TypeScript navigation & validation
        load_all_analysis_tools(),  # 14 - AST parsing, complexity, imports, secrets
        load_all_git_tools(),  # 79 - Full version control operations
        load_all_shell_tools(),  # 13 - Shell script validation & security
        load_all_database_tools(),  # 18 - SQLite operations for agent memory
        load_all_profiling_tools(),  # 8 - Performance & memory profiling
    )


def load_java_loadout() -> list[Callable[..., Any]]:
    """Load the complete toolset for Java-focused development agents.

    This is the recommended loadout for agents working primarily on Java projects.
    Includes navigation, analysis, version control, and database operations.

    Included modules:
    - Java navigation (17 functions) - Core language tools
    - Code analysis (14 functions) - AST, complexity, imports, secrets
    - Git operations (79 functions) - Version control
    - Shell validation (13 functions) - Script analysis & security
    - Database operations (18 functions) - SQLite for agent memory
    - Profiling tools (8 functions) - Performance & memory analysis

    Returns:
        List of 149 tool functions optimized for Java development

    Example:
        >>> java_agent_tools = load_java_loadout()
        >>> len(java_agent_tools) == 149
        True
    """
    return merge_tool_lists(
        load_all_java_tools(),  # 17 - Java navigation
        load_all_analysis_tools(),  # 14 - AST parsing, complexity, imports, secrets
        load_all_git_tools(),  # 79 - Full version control operations
        load_all_shell_tools(),  # 13 - Shell script validation & security
        load_all_database_tools(),  # 18 - SQLite operations for agent memory
        load_all_profiling_tools(),  # 8 - Performance & memory profiling
    )


def load_cpp_loadout() -> list[Callable[..., Any]]:
    """Load the complete toolset for C/C++-focused development agents.

    Recommended loadout for agents working on C/C++ projects.
    Optimized for systems programming, performance-critical applications.

    Included modules:
    - C++ navigation (17 functions) - Code exploration (70-95% token savings!)
    - Code analysis (14 functions) - AST, complexity, imports, secrets
    - Git operations (79 functions) - Version control
    - Shell validation (13 functions) - Build scripts, makefiles
    - Database operations (18 functions) - SQLite for tooling/apps
    - Profiling tools (8 functions) - Performance critical for C++

    Returns:
        List of 149 tool functions optimized for C/C++ development

    Example:
        >>> cpp_agent_tools = load_cpp_loadout()
        >>> len(cpp_agent_tools) == 149
        True
    """
    return merge_tool_lists(
        load_all_cpp_tools(),  # 17 - C++ code navigation
        load_all_analysis_tools(),  # 14 - Code analysis
        load_all_git_tools(),  # 79 - Version control
        load_all_shell_tools(),  # 13 - Build scripts, deployment
        load_all_database_tools(),  # 18 - SQLite for applications
        load_all_profiling_tools(),  # 8 - Performance analysis
    )


def load_csharp_loadout() -> list[Callable[..., Any]]:
    """Load the complete toolset for C#-focused development agents.

    Recommended loadout for agents working on C#/.NET projects.
    Optimized for enterprise applications, Unity game development.

    Included modules:
    - C# navigation (17 functions) - Code exploration (70-95% token savings!)
    - Code analysis (14 functions) - AST, complexity, imports, secrets
    - Git operations (79 functions) - Version control
    - Shell validation (13 functions) - Build scripts, deployment
    - Database operations (18 functions) - SQLite for applications
    - Profiling tools (8 functions) - Performance & memory analysis

    Returns:
        List of 149 tool functions optimized for C# development

    Example:
        >>> csharp_agent_tools = load_csharp_loadout()
        >>> len(csharp_agent_tools) == 149
        True
    """
    return merge_tool_lists(
        load_all_csharp_tools(),  # 17 - C# code navigation
        load_all_analysis_tools(),  # 14 - Code analysis
        load_all_git_tools(),  # 79 - Version control
        load_all_shell_tools(),  # 13 - Build scripts, deployment
        load_all_database_tools(),  # 18 - SQLite for applications
        load_all_profiling_tools(),  # 8 - Performance & memory analysis
    )


def load_go_loadout() -> list[Callable[..., Any]]:
    """Load the complete toolset for Go-focused development agents.

    Recommended loadout for agents working on Go projects.
    Optimized for cloud services, microservices, backend development.

    Included modules:
    - Go navigation (17 functions) - Code exploration (70-95% token savings!)
    - Code analysis (14 functions) - AST, complexity, imports, secrets
    - Git operations (79 functions) - Version control
    - Shell validation (13 functions) - Deployment scripts
    - Database operations (18 functions) - SQLite for services
    - Profiling tools (8 functions) - Performance analysis

    Returns:
        List of 149 tool functions optimized for Go development

    Example:
        >>> go_agent_tools = load_go_loadout()
        >>> len(go_agent_tools) == 149
        True
    """
    return merge_tool_lists(
        load_all_go_tools(),  # 17 - Go code navigation
        load_all_analysis_tools(),  # 14 - Code analysis
        load_all_git_tools(),  # 79 - Version control
        load_all_shell_tools(),  # 13 - Deployment scripts
        load_all_database_tools(),  # 18 - SQLite for services
        load_all_profiling_tools(),  # 8 - Performance analysis
    )


def load_rust_loadout() -> list[Callable[..., Any]]:
    """Load the complete toolset for Rust-focused development agents.

    Recommended loadout for agents working on Rust projects.
    Optimized for systems programming, memory-safe applications.

    Included modules:
    - Rust navigation (17 functions) - Code exploration (70-95% token savings!)
    - Code analysis (14 functions) - AST, complexity, imports, secrets
    - Git operations (79 functions) - Version control
    - Shell validation (13 functions) - Cargo scripts, build tools
    - Database operations (18 functions) - SQLite for applications
    - Profiling tools (8 functions) - Performance & memory safety

    Returns:
        List of 149 tool functions optimized for Rust development

    Example:
        >>> rust_agent_tools = load_rust_loadout()
        >>> len(rust_agent_tools) == 149
        True
    """
    return merge_tool_lists(
        load_all_rust_tools(),  # 17 - Rust code navigation
        load_all_analysis_tools(),  # 14 - Code analysis
        load_all_git_tools(),  # 79 - Version control
        load_all_shell_tools(),  # 13 - Cargo scripts, build tools
        load_all_database_tools(),  # 18 - SQLite for applications
        load_all_profiling_tools(),  # 8 - Performance & memory safety
    )


def load_ruby_loadout() -> list[Callable[..., Any]]:
    """Load the complete toolset for Ruby-focused development agents.

    Recommended loadout for agents working on Ruby/Rails projects.
    Optimized for web development, Ruby on Rails applications.

    Included modules:
    - Ruby navigation (17 functions) - Code exploration (70-95% token savings!)
    - Code analysis (14 functions) - AST, complexity, imports, secrets
    - Git operations (79 functions) - Version control
    - Shell validation (13 functions) - Rake tasks, deployment
    - Database operations (18 functions) - SQLite for Rails apps
    - Profiling tools (8 functions) - Performance analysis

    Returns:
        List of 149 tool functions optimized for Ruby development

    Example:
        >>> ruby_agent_tools = load_ruby_loadout()
        >>> len(ruby_agent_tools) == 149
        True
    """
    return merge_tool_lists(
        load_all_ruby_tools(),  # 17 - Ruby code navigation
        load_all_analysis_tools(),  # 14 - Code analysis
        load_all_git_tools(),  # 79 - Version control
        load_all_shell_tools(),  # 13 - Rake tasks, deployment
        load_all_database_tools(),  # 18 - SQLite for Rails apps
        load_all_profiling_tools(),  # 8 - Performance analysis
    )


def load_swift_loadout() -> list[Callable[..., Any]]:
    """Load the complete toolset for Swift-focused development agents.

    Recommended loadout for agents working on Swift projects.
    Optimized for iOS/macOS development, Apple ecosystem.

    Included modules:
    - Code analysis (14 functions) - AST, complexity, imports, secrets
    - Git operations (79 functions) - Version control
    - Shell validation (13 functions) - Build scripts, Xcode automation
    - Database operations (18 functions) - SQLite for apps
    - Profiling tools (8 functions) - Performance analysis

    Returns:
        List of 132 tool functions optimized for Swift development

    Example:
        >>> swift_agent_tools = load_swift_loadout()
        >>> len(swift_agent_tools) == 132
        True
    """
    return merge_tool_lists(
        load_all_analysis_tools(),  # 14 - Code analysis
        load_all_git_tools(),  # 79 - Version control
        load_all_shell_tools(),  # 13 - Build scripts, Xcode automation
        load_all_database_tools(),  # 18 - SQLite for apps
        load_all_profiling_tools(),  # 8 - Performance analysis
    )


def load_kotlin_loadout() -> list[Callable[..., Any]]:
    """Load the complete toolset for Kotlin-focused development agents.

    Recommended loadout for agents working on Kotlin projects.
    Optimized for Android development, JVM ecosystem.

    Included modules:
    - Code analysis (14 functions) - AST, complexity, imports, secrets
    - Git operations (79 functions) - Version control
    - Shell validation (13 functions) - Gradle scripts, deployment
    - Database operations (18 functions) - SQLite for Android apps
    - Profiling tools (8 functions) - Performance analysis

    Returns:
        List of 132 tool functions optimized for Kotlin development

    Example:
        >>> kotlin_agent_tools = load_kotlin_loadout()
        >>> len(kotlin_agent_tools) == 132
        True
    """
    return merge_tool_lists(
        load_all_analysis_tools(),  # 14 - Code analysis
        load_all_git_tools(),  # 79 - Version control
        load_all_shell_tools(),  # 13 - Gradle scripts, deployment
        load_all_database_tools(),  # 18 - SQLite for Android apps
        load_all_profiling_tools(),  # 8 - Performance analysis
    )


def load_typescript_loadout() -> list[Callable[..., Any]]:
    """Load the complete toolset for TypeScript-focused development agents.

    This is an alias for load_javascript_loadout() since TypeScript is a superset
    of JavaScript and shares the same tooling ecosystem.

    Recommended loadout for agents working on TypeScript projects.
    Includes JavaScript/TypeScript navigation and essential development tools.

    Returns:
        List of 149 tool functions optimized for TypeScript development
        (same as JavaScript loadout)

    Example:
        >>> ts_agent_tools = load_typescript_loadout()
        >>> len(ts_agent_tools) == 149
        True
    """
    return load_javascript_loadout()
