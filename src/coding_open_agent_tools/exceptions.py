"""Common exception classes for coding-open-agent-tools.

This module provides standardized exceptions for consistent error handling
across all modules.
"""


class CodingToolsError(Exception):
    """Base exception for all coding-open-agent-tools errors."""

    pass


class ValidationError(CodingToolsError):
    """Raised when validation fails (syntax, types, etc.)."""

    pass


class SecurityError(CodingToolsError):
    """Raised when security issues are detected."""

    pass


class GenerationError(CodingToolsError):
    """Raised when code or script generation fails."""

    pass


class AnalysisError(CodingToolsError):
    """Raised when code analysis fails."""

    pass


class GitError(CodingToolsError):
    """Raised when git operations fail."""

    pass
