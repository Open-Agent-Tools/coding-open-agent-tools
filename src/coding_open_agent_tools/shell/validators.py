"""Shell script syntax validation functions.

This module provides functions to validate shell script syntax and check for
required dependencies. Validation catches errors before execution, preventing
retry loops and saving agent tokens.
"""

import re
import shutil
import subprocess
from typing import Any

from coding_open_agent_tools._decorators import strands_tool

from ..exceptions import ToolExecutionError


@strands_tool
def validate_shell_syntax(script_content: str, shell_type: str) -> dict[str, str]:
    """Validate shell script syntax using shell's built-in syntax checker.

    Uses shell's -n flag (no-execute mode) to check syntax without running the script.
    This prevents execution failures and saves agent tokens by catching errors early.

    Args:
        script_content: The shell script content to validate
        shell_type: Shell interpreter to use ("bash", "sh", "zsh", "dash")

    Returns:
        Dictionary with validation results:
        - is_valid: "true" if syntax is valid, "false" otherwise
        - error_message: Error description if invalid, empty string otherwise
        - line_number: Line number of first error, "0" if valid
        - shell_type: The shell type used for validation

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If shell_type is not supported or script_content is empty
        ToolExecutionError: If shell executable not found
    """
    if not isinstance(script_content, str):
        raise TypeError("script_content must be a string")
    if not isinstance(shell_type, str):
        raise TypeError("shell_type must be a string")

    if not script_content.strip():
        raise ValueError("script_content cannot be empty")

    valid_shells = ["bash", "sh", "zsh", "dash"]
    if shell_type not in valid_shells:
        raise ValueError(f"shell_type must be one of {valid_shells}, got: {shell_type}")

    # Check if shell executable exists
    shell_path = shutil.which(shell_type)
    if not shell_path:
        raise ToolExecutionError(f"Shell executable '{shell_type}' not found in PATH")

    try:
        # Use -n flag to check syntax without executing
        result = subprocess.run(
            [shell_path, "-n"],
            input=script_content,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        if result.returncode == 0:
            return {
                "is_valid": "true",
                "error_message": "",
                "line_number": "0",
                "shell_type": shell_type,
            }

        # Parse error message to extract line number
        error_msg = result.stderr.strip()
        line_num = "0"

        # Common patterns for line numbers in shell error messages
        line_patterns = [
            r"line (\d+):",  # bash, zsh
            r":(\d+):",  # sh, dash
        ]

        for pattern in line_patterns:
            match = re.search(pattern, error_msg)
            if match:
                line_num = match.group(1)
                break

        return {
            "is_valid": "false",
            "error_message": error_msg,
            "line_number": line_num,
            "shell_type": shell_type,
        }

    except subprocess.TimeoutExpired:
        return {
            "is_valid": "false",
            "error_message": "Validation timed out after 5 seconds",
            "line_number": "0",
            "shell_type": shell_type,
        }
    except Exception as e:
        raise ToolExecutionError(f"Failed to validate shell syntax: {e}") from e


@strands_tool
def check_shell_dependencies(script_content: str) -> dict[str, Any]:
    """Check which external commands/tools are used in a shell script.

    Extracts command names from the script and checks if they're available
    in the current PATH. Helps identify missing dependencies before execution.

    Args:
        script_content: The shell script content to analyze

    Returns:
        Dictionary with dependency analysis:
        - commands_used: List of command names found in script
        - commands_available: List of commands that exist in PATH
        - commands_missing: List of commands not found in PATH
        - total_commands: Total number of unique commands detected

    Raises:
        TypeError: If script_content is not a string
        ValueError: If script_content is empty
    """
    if not isinstance(script_content, str):
        raise TypeError("script_content must be a string")

    if not script_content.strip():
        raise ValueError("script_content cannot be empty")

    commands: set[str] = set()

    # Remove comments and empty lines
    lines = []
    for line in script_content.split("\n"):
        # Remove comments (but preserve strings)
        if "#" in line:
            # Simple heuristic: if # is not in a string, treat as comment
            in_string = False
            quote_char = None
            for i, char in enumerate(line):
                if char in ('"', "'") and (i == 0 or line[i - 1] != "\\"):
                    if not in_string:
                        in_string = True
                        quote_char = char
                    elif char == quote_char:
                        in_string = False
                        quote_char = None
                elif char == "#" and not in_string:
                    line = line[:i]
                    break
        if line.strip():
            lines.append(line)

    script_text = "\n".join(lines)

    # Pattern to match command invocations
    # Matches: command, $(command), `command`, |command, &&command, ;command
    patterns = [
        r"(?:^|\s|;|\||&&|\$\(|`)([\w\-]+)",  # Standard commands
        r"(?:sudo|exec|env|time|nice)\s+([\w\-]+)",  # Commands after prefixes
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, script_text):
            cmd = match.group(1)
            # Filter out shell keywords and builtins
            if cmd not in _SHELL_KEYWORDS and not cmd.startswith("$"):
                commands.add(cmd)

    # Check availability in PATH
    available = []
    missing = []

    for cmd in sorted(commands):
        if shutil.which(cmd):
            available.append(cmd)
        else:
            missing.append(cmd)

    return {
        "commands_used": sorted(commands),
        "commands_available": available,
        "commands_missing": missing,
        "total_commands": str(len(commands)),
    }


# Shell keywords and built-ins to exclude from command detection
_SHELL_KEYWORDS = {
    # Control structures
    "if",
    "then",
    "else",
    "elif",
    "fi",
    "case",
    "esac",
    "for",
    "while",
    "until",
    "do",
    "done",
    "in",
    "select",
    # Built-ins
    "echo",
    "cd",
    "pwd",
    "exit",
    "return",
    "export",
    "set",
    "unset",
    "shift",
    "test",
    "true",
    "false",
    "break",
    "continue",
    "read",
    "readonly",
    "local",
    "declare",
    "typeset",
    "let",
    "eval",
    "exec",
    "source",
    "alias",
    "unalias",
    "function",
    "getopts",
    "hash",
    "help",
    "history",
    "jobs",
    "kill",
    "suspend",
    "times",
    "trap",
    "type",
    "ulimit",
    "umask",
    "wait",
    # Shell variables
    "PATH",
    "HOME",
    "USER",
    "SHELL",
    "PWD",
}
