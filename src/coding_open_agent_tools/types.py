"""Shared type definitions for coding-open-agent-tools.

This module provides common type aliases and constants used across modules.
"""

# Common constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit for code files
MAX_SCRIPT_SIZE = 1 * 1024 * 1024  # 1MB limit for shell scripts

# Docstring styles
DOCSTRING_STYLES = ["google", "numpy", "sphinx"]

# Shell types
SHELL_TYPES = ["bash", "sh", "zsh"]

# Project types
BUILD_SYSTEMS = ["setuptools", "poetry", "hatch", "pdm", "uv"]
