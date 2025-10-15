"""Conditional decorator imports with fallbacks.

This module provides decorator imports with graceful fallbacks when agent
frameworks are not installed. This allows the package to be used without
requiring all frameworks during development and testing.
"""

from typing import Any, Callable, TypeVar

T = TypeVar("T", bound=Callable[..., Any])


# Try to import strands_tool decorator
try:
    from strands import strands_tool
except ImportError:

    def strands_tool() -> Callable[[T], T]:  # type: ignore[misc]
        """Stub decorator when strands is not installed."""

        def decorator(func: T) -> T:
            return func

        return decorator


# Try to import tool decorator from Google ADK
try:
    from google.adk.tools import tool
except ImportError:

    def tool(func: T) -> T:  # type: ignore[misc]
        """Stub decorator when google-adk is not installed."""
        return func


__all__ = ["strands_tool", "tool"]
