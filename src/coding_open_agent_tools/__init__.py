"""Coding Open Agent Tools.

Advanced code generation and shell scripting toolkit for AI agents, complementing
basic-open-agent-tools with development-focused capabilities.

This project provides specialized code generation, script creation, and development
automation capabilities designed specifically for AI agents.
"""

__version__ = "0.4.3"

# Import migrated modules
from . import analysis, database, git, profiling, python, quality, shell

# Import helper functions
from .helpers import (
    get_tool_info,
    list_all_available_tools,
    load_all_analysis_tools,
    load_all_database_tools,
    load_all_git_tools,
    load_all_profiling_tools,
    load_all_python_tools,
    load_all_quality_tools,
    load_all_shell_tools,
    load_all_tools,
    merge_tool_lists,
)

__all__: list[str] = [
    # Modules
    "analysis",
    "database",
    "git",
    "profiling",
    "python",
    "quality",
    "shell",
    # Helper functions
    "get_tool_info",
    "list_all_available_tools",
    "load_all_analysis_tools",
    "load_all_database_tools",
    "load_all_git_tools",
    "load_all_profiling_tools",
    "load_all_python_tools",
    "load_all_quality_tools",
    "load_all_shell_tools",
    "load_all_tools",
    "merge_tool_lists",
]
