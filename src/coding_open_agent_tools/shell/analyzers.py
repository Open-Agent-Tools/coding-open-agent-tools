"""Shell script static analysis functions.

This module provides deterministic analysis of shell scripts for common
issues like unquoted variables, dangerous commands, and missing error handling.
These are tedious checks that agents often miss.
"""

import re

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def detect_unquoted_variables(script_content: str) -> list[dict[str, str]]:
    """Detect unquoted variable expansions that could cause word splitting.

    Unquoted variables are a common source of bugs in shell scripts.
    When a variable contains spaces or special characters, it will be
    split into multiple arguments if not quoted.

    Args:
        script_content: The shell script content to analyze

    Returns:
        List of unquoted variable issues, each with:
        - line_number: Line number where issue was found
        - variable_name: Name of the unquoted variable
        - context: The line of code with the issue
        - recommendation: How to fix the issue

    Raises:
        TypeError: If script_content is not a string
        ValueError: If script_content is empty
    """
    if not isinstance(script_content, str):
        raise TypeError("script_content must be a string")

    if not script_content.strip():
        raise ValueError("script_content cannot be empty")

    issues: list[dict[str, str]] = []
    lines = script_content.split("\n")

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Skip comments and empty lines
        if not stripped or stripped.startswith("#"):
            continue

        # Look for unquoted variables (not inside quotes or arrays)
        # Pattern: $VAR or ${VAR} that's not inside quotes

        # Simple heuristic: find $VAR not preceded by " or '
        # This is not perfect but catches common cases

        # Find all variable expansions
        var_patterns = [
            r"\$([A-Za-z_][A-Za-z0-9_]*)",  # $VAR
            r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}",  # ${VAR}
        ]

        for pattern in var_patterns:
            for match in re.finditer(pattern, line):
                var_name = match.group(1)
                start_pos = match.start()

                # Check if this variable is quoted
                # Look backwards for nearest quote
                before = line[:start_pos]

                # Count quotes before this position
                double_quotes = before.count('"') - before.count('\\"')
                single_quotes = before.count("'") - before.count("\\'")

                # If odd number of quotes, we're inside quotes
                in_double_quotes = double_quotes % 2 == 1
                in_single_quotes = single_quotes % 2 == 1

                # Single quotes prevent expansion, so not an issue
                if in_single_quotes:
                    continue

                # Check if already in double quotes
                if in_double_quotes:
                    continue

                # Check for common safe contexts where quoting isn't needed
                # (this is heuristic and not exhaustive)

                # In array assignments: VAR=($other)
                if re.search(r"=\s*\(.*\$" + var_name, line):
                    continue

                # In arithmetic contexts: (( ))
                if re.search(r"\(\(.*\$" + var_name, line):
                    continue

                # Comparison contexts that auto-quote: [[ $VAR == ... ]]
                if re.search(r"\[\[.*\$" + var_name, line):
                    continue

                # If we got here, it's likely unquoted in a dangerous context
                issues.append(
                    {
                        "line_number": str(line_num),
                        "variable_name": var_name,
                        "context": stripped,
                        "recommendation": f'Quote variable: "${var_name}" instead of ${var_name}',
                    }
                )

    return issues


@strands_tool
def find_dangerous_commands(script_content: str) -> list[dict[str, str]]:
    """Find potentially dangerous command patterns in shell script.

    Identifies commands that could cause data loss, security issues,
    or system damage if used improperly. This is a deterministic
    analysis based on command patterns.

    Args:
        script_content: The shell script content to analyze

    Returns:
        List of dangerous command findings, each with:
        - line_number: Line number where command was found
        - command: The dangerous command found
        - risk_level: "high", "medium", or "low"
        - reason: Why this command is potentially dangerous
        - mitigation: Recommended safety measures

    Raises:
        TypeError: If script_content is not a string
        ValueError: If script_content is empty
    """
    if not isinstance(script_content, str):
        raise TypeError("script_content must be a string")

    if not script_content.strip():
        raise ValueError("script_content cannot be empty")

    findings: list[dict[str, str]] = []
    lines = script_content.split("\n")

    dangerous_patterns = [
        {
            "pattern": r"\brm\s+-rf\s+/",
            "command": "rm -rf /",
            "risk_level": "high",
            "reason": "Recursive deletion from root directory",
            "mitigation": "Never use rm -rf with root paths. Always use relative paths",
        },
        {
            "pattern": r"\bdd\s+if=.*of=/dev/",
            "command": "dd to device",
            "risk_level": "high",
            "reason": "Writing directly to device can destroy data",
            "mitigation": "Verify device paths carefully. Consider using safer alternatives",
        },
        {
            "pattern": r"\bmkfs\.",
            "command": "mkfs (format filesystem)",
            "risk_level": "high",
            "reason": "Formatting filesystems destroys all data",
            "mitigation": "Double-check device paths. Prompt for confirmation",
        },
        {
            "pattern": r"\b:>\s*/",
            "command": "Truncate file with :>",
            "risk_level": "medium",
            "reason": "Can accidentally truncate important files",
            "mitigation": "Verify file paths before truncating",
        },
        {
            "pattern": r">\s*/etc/",
            "command": "Redirect to /etc",
            "risk_level": "medium",
            "reason": "Modifying system configuration files",
            "mitigation": "Backup files before modifying. Use appropriate tools",
        },
        {
            "pattern": r"\bchmod\s+777",
            "command": "chmod 777",
            "risk_level": "medium",
            "reason": "World-writable permissions are insecure",
            "mitigation": "Use minimal required permissions (755, 644, etc.)",
        },
        {
            "pattern": r"\bchown\s+.*:.*\s+/",
            "command": "chown on system paths",
            "risk_level": "medium",
            "reason": "Changing ownership of system files can break things",
            "mitigation": "Only change ownership of files you control",
        },
        {
            "pattern": r"\bkillall\s+-9",
            "command": "killall -9",
            "risk_level": "low",
            "reason": "Force-killing all processes by name can cause data loss",
            "mitigation": "Try graceful shutdown first. Target specific PIDs",
        },
        {
            "pattern": r"\bcurl\s+.*\|\s*sh\b",
            "command": "curl | sh",
            "risk_level": "high",
            "reason": "Executing remote code without inspection",
            "mitigation": "Download and inspect scripts before executing",
        },
        {
            "pattern": r"\bwget\s+.*-O-.*\|\s*sh\b",
            "command": "wget -O- | sh",
            "risk_level": "high",
            "reason": "Executing remote code without inspection",
            "mitigation": "Download and inspect scripts before executing",
        },
    ]

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Skip comments
        if stripped.startswith("#"):
            continue

        for danger in dangerous_patterns:
            if re.search(danger["pattern"], line):
                findings.append(
                    {
                        "line_number": str(line_num),
                        "command": danger["command"],
                        "risk_level": danger["risk_level"],
                        "reason": danger["reason"],
                        "mitigation": danger["mitigation"],
                    }
                )

    return findings


@strands_tool
def check_error_handling(script_content: str) -> dict[str, str]:
    """Check if shell script has proper error handling.

    Analyzes whether the script uses error handling mechanisms like
    set -e, trap, or explicit error checks. Scripts without error
    handling can fail silently.

    Args:
        script_content: The shell script content to analyze

    Returns:
        Dictionary with error handling analysis:
        - has_set_e: "true" if uses set -e, "false" otherwise
        - has_set_u: "true" if uses set -u (undefined var check), "false" otherwise
        - has_set_o_pipefail: "true" if uses set -o pipefail, "false" otherwise
        - has_trap: "true" if has trap statements, "false" otherwise
        - has_error_checks: "true" if checks $? or uses ||, "false" otherwise
        - error_handling_score: Score from 0-5 based on mechanisms present
        - recommendation: Suggested improvements

    Raises:
        TypeError: If script_content is not a string
        ValueError: If script_content is empty
    """
    if not isinstance(script_content, str):
        raise TypeError("script_content must be a string")

    if not script_content.strip():
        raise ValueError("script_content cannot be empty")

    has_set_e = False
    has_set_u = False
    has_set_o_pipefail = False
    has_trap = False
    has_error_checks = False

    lines = script_content.split("\n")

    for line in lines:
        stripped = line.strip()

        # Check for set -e (exit on error)
        if re.search(r"\bset\s+-[a-z]*e", stripped):
            has_set_e = True

        # Check for set -u (error on undefined variables)
        if re.search(r"\bset\s+-[a-z]*u", stripped):
            has_set_u = True

        # Check for set -o pipefail
        if re.search(r"\bset\s+-o\s+pipefail", stripped):
            has_set_o_pipefail = True

        # Check for trap statements
        if re.search(r"\btrap\s+", stripped):
            has_trap = True

        # Check for explicit error checking
        if re.search(r"\$\?", stripped) or re.search(r"\|\|", stripped):
            has_error_checks = True

    # Calculate score
    score = 0
    if has_set_e:
        score += 1
    if has_set_u:
        score += 1
    if has_set_o_pipefail:
        score += 1
    if has_trap:
        score += 1
    if has_error_checks:
        score += 1

    # Generate recommendation
    recommendations = []
    if not has_set_e:
        recommendations.append("Add 'set -e' to exit on errors")
    if not has_set_u:
        recommendations.append("Add 'set -u' to catch undefined variables")
    if not has_set_o_pipefail:
        recommendations.append("Add 'set -o pipefail' to catch pipeline failures")
    if not has_trap:
        recommendations.append("Consider adding trap for cleanup on exit")

    recommendation = (
        "; ".join(recommendations) if recommendations else "Good error handling"
    )

    return {
        "has_set_e": "true" if has_set_e else "false",
        "has_set_u": "true" if has_set_u else "false",
        "has_set_o_pipefail": "true" if has_set_o_pipefail else "false",
        "has_trap": "true" if has_trap else "false",
        "has_error_checks": "true" if has_error_checks else "false",
        "error_handling_score": str(score),
        "recommendation": recommendation,
    }
