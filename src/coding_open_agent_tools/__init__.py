"""Coding Open Agent Tools.

Advanced code generation and shell scripting toolkit for AI agents, complementing
basic-open-agent-tools with development-focused capabilities.

This project provides specialized code generation, script creation, and development
automation capabilities designed specifically for AI agents.
"""

__version__ = "0.1.1"

# Import migrated modules
from . import analysis, git, profiling, quality

# Import helper functions
from .helpers import (
    load_all_analysis_tools,
    load_all_git_tools,
    load_all_profiling_tools,
    load_all_quality_tools,
    load_all_tools,
    merge_tool_lists,
)

__all__: list[str] = [
    # Modules
    "analysis",
    "git",
    "profiling",
    "quality",
    # Helper functions
    "load_all_analysis_tools",
    "load_all_git_tools",
    "load_all_profiling_tools",
    "load_all_quality_tools",
    "load_all_tools",
    "merge_tool_lists",
]
