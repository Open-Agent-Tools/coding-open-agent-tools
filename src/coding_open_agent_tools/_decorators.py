"""Centralized decorator imports with graceful fallbacks.

This module provides conditional imports for agent framework decorators.
When frameworks are not installed, no-op decorators are used as fallbacks,
allowing the package to work without any required framework dependencies.

Supported Frameworks:
- Strands: @strands_tool decorator
- LangGraph: No decorator needed (works with standard callables)
- Google ADK: No decorator needed (works with standard callables)

All agent tools use @strands_tool decorator for Strands framework compatibility.
"""

from typing import Any, Callable

# Try to import strands_tool decorator
try:
    from strands import tool as strands_tool
except ImportError:
    # Create a no-op decorator if strands is not installed
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[misc]
        """No-op decorator fallback when strands is not installed."""
        return func


__all__ = ["strands_tool"]
