"""Shared utility functions for code navigation across all languages.

This module provides common validation, formatting, and checking functions
used by all language-specific navigation modules to reduce code duplication.
"""

from typing import Any, Optional


def validate_source_code(source_code: Any, param_name: str = "source_code") -> None:
    """Validate source code input.

    Args:
        source_code: The source code to validate
        param_name: Name of the parameter for error messages

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty or whitespace only
    """
    if not isinstance(source_code, str):
        raise TypeError(f"{param_name} must be a string")
    if not source_code.strip():
        raise ValueError(f"{param_name} cannot be empty")


def validate_identifier(identifier: Any, param_name: str) -> None:
    """Validate identifier input.

    Args:
        identifier: The identifier to validate
        param_name: Name of the parameter for error messages

    Raises:
        TypeError: If identifier is not a string
        ValueError: If identifier is empty or whitespace only
    """
    if not isinstance(identifier, str):
        raise TypeError(f"{param_name} must be a string")
    if not identifier.strip():
        raise ValueError(f"{param_name} cannot be empty")


def format_line_range(start_line: int, end_line: int) -> dict[str, str]:
    """Format line range as standardized dictionary.

    Args:
        start_line: Starting line number
        end_line: Ending line number

    Returns:
        Dictionary with start_line, end_line as strings and empty error field
    """
    return {
        "start_line": str(start_line),
        "end_line": str(end_line),
        "error": "",
    }


def format_error(error_message: str) -> dict[str, str]:
    """Format error response with standard structure.

    Args:
        error_message: The error message to include

    Returns:
        Dictionary with zero line numbers and error message
    """
    return {
        "start_line": "0",
        "end_line": "0",
        "error": error_message,
    }


def check_tree_sitter_available(
    language: str, tree_sitter_flag: bool
) -> Optional[dict[str, str]]:
    """Check if tree-sitter is available for the language.

    Args:
        language: Name of the programming language
        tree_sitter_flag: Boolean indicating if tree-sitter is available

    Returns:
        Error dictionary if tree-sitter not available, None otherwise
    """
    if not tree_sitter_flag:
        return {
            "error": "tree-sitter-language-pack not installed. Install with: pip install tree-sitter-language-pack",
            "available": "false",
        }
    return None
