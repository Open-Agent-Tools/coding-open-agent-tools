from coding_open_agent_tools._decorators import strands_tool

"""Shell script formatting and escaping functions.

This module provides deterministic formatting utilities for shell scripts,
including argument escaping and shebang normalization. These save agent
tokens by handling tedious escaping rules correctly.
"""


@strands_tool
def escape_shell_argument(argument: str, quote_style: str) -> str:
    """Safely escape an argument for use in shell commands.

    Properly escapes special characters to prevent injection and ensure
    the argument is treated as a single value. Agents often get shell
    escaping wrong, wasting tokens on retry loops.

    Args:
        argument: The argument value to escape
        quote_style: Quote style to use ("single", "double", "auto")

    Returns:
        Properly escaped and quoted argument as string

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If quote_style is invalid or argument is empty
    """
    if not isinstance(argument, str):
        raise TypeError("argument must be a string")
    if not isinstance(quote_style, str):
        raise TypeError("quote_style must be a string")

    if not argument:
        raise ValueError("argument cannot be empty")

    valid_styles = ["single", "double", "auto"]
    if quote_style not in valid_styles:
        raise ValueError(
            f"quote_style must be one of {valid_styles}, got: {quote_style}"
        )

    # Auto mode: choose based on content
    if quote_style == "auto":
        # Use single quotes unless string contains single quotes
        if "'" in argument:
            quote_style = "double"
        else:
            quote_style = "single"

    if quote_style == "single":
        # Single quotes preserve everything literally except single quotes
        # Replace ' with '\'' (end quote, escaped quote, start quote)
        escaped = argument.replace("'", "'\\''")
        return f"'{escaped}'"

    else:  # double quotes
        # Double quotes allow variable expansion but need escaping for special chars
        # Escape: $ ` " \ and newline
        escaped = argument
        escaped = escaped.replace("\\", "\\\\")  # Backslash first
        escaped = escaped.replace('"', '\\"')  # Double quote
        escaped = escaped.replace("$", "\\$")  # Dollar sign
        escaped = escaped.replace("`", "\\`")  # Backtick
        escaped = escaped.replace("\n", "\\n")  # Newline
        return f'"{escaped}"'


@strands_tool
def normalize_shebang(shebang_line: str, shell_type: str) -> str:
    """Normalize shebang line to use proper interpreter path.

    Ensures shebang follows best practices with proper paths and flags.
    Handles common variations and applies standard formatting.

    Args:
        shebang_line: The existing shebang line (may be malformed)
        shell_type: Target shell type ("bash", "sh", "zsh", "python", "env")

    Returns:
        Normalized shebang line as string

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If shell_type is not supported
    """
    if not isinstance(shebang_line, str):
        raise TypeError("shebang_line must be a string")
    if not isinstance(shell_type, str):
        raise TypeError("shell_type must be a string")

    valid_shells = ["bash", "sh", "zsh", "python", "python3", "env"]
    if shell_type not in valid_shells:
        raise ValueError(f"shell_type must be one of {valid_shells}, got: {shell_type}")

    # Remove existing shebang prefix and whitespace
    line = shebang_line.strip()
    if line.startswith("#!"):
        line = line[2:].strip()

    # Parse any existing flags
    parts = line.split()
    existing_flags = []
    if len(parts) > 1:
        # Flags are everything after the interpreter path
        existing_flags = parts[1:]

    # Build normalized shebang based on shell type
    if shell_type == "env":
        # Use env for portability (finds interpreter in PATH)
        # Extract the actual interpreter if provided
        if "env" in line:
            # Already uses env, preserve interpreter
            if len(parts) >= 2 and parts[1] != "env":
                interpreter = parts[1]
            else:
                interpreter = "bash"  # Default to bash
        else:
            interpreter = "bash"  # Default to bash

        result = f"#!/usr/bin/env {interpreter}"

        # Add common flags for the interpreter
        if existing_flags:
            result += " " + " ".join(existing_flags)

        return result

    elif shell_type == "bash":
        # Standard bash path
        result = "#!/bin/bash"

        if existing_flags:
            result += " " + " ".join(existing_flags)

        return result

    elif shell_type == "sh":
        # POSIX sh (most portable)
        return "#!/bin/sh"

    elif shell_type == "zsh":
        # Zsh path
        result = "#!/bin/zsh"
        if existing_flags:
            result += " " + " ".join(existing_flags)
        return result

    elif shell_type in ("python", "python3"):
        # Python shebang - prefer env for portability
        if shell_type == "python3":
            return "#!/usr/bin/env python3"
        else:
            return "#!/usr/bin/env python"

    # Should never reach here due to validation above
    return "#!/bin/sh"
