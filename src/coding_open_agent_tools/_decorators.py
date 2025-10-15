"""Centralized decorator imports with graceful fallbacks.

This module provides conditional imports for agent framework decorators.
When frameworks are not installed, no-op decorators are used as fallbacks,
allowing the package to work without any required framework dependencies.

Supported Frameworks:
- Google ADK: @adk_tool decorator
- Strands: @strands_tool decorator
- LangGraph: No decorator needed (works with standard callables)

All 84 agent tools use both @adk_tool and @strands_tool decorators
for maximum framework compatibility.
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


# Try to import Google ADK tool decorator
try:
    from google.adk.tools import tool as adk_tool
except ImportError:
    # Create a no-op decorator if google-adk is not installed
    def adk_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[misc]
        """No-op decorator fallback when google-adk is not installed."""
        return func


__all__ = ["strands_tool", "adk_tool"]
