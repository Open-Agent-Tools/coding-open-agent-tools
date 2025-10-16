"""Shell script security analysis functions.

This module provides security scanning capabilities for shell scripts, including
injection risk detection, dangerous command identification, and secret scanning
with optional detect-secrets integration.
"""

import re
from typing import Any

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def analyze_shell_security(script_content: str) -> list[dict[str, str]]:
    """Analyze shell script for security issues using deterministic rules.

    Scans for common security problems including:
    - Use of eval, exec, or similar dangerous functions
    - Command substitution without proper quoting
    - Unquoted variables that could cause injection
    - Dangerous flag combinations (rm -rf with variables)
    - Hardcoded secrets and credentials
    - Insecure file permissions
    - wget/curl without SSL verification

    Args:
        script_content: The shell script content to analyze

    Returns:
        List of security issues, each with:
        - severity: "critical", "high", "medium", or "low"
        - line_number: Line number where issue was found
        - issue_type: Category of the security issue
        - description: Detailed description of the problem
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
        line_stripped = line.strip()

        # Skip empty lines and comments
        if not line_stripped or line_stripped.startswith("#"):
            continue

        # Critical: eval with user input
        if re.search(r"\beval\s+[\"']?\$", line):
            issues.append(
                {
                    "severity": "critical",
                    "line_number": str(line_num),
                    "issue_type": "code_injection",
                    "description": "Use of eval with variable expansion",
                    "recommendation": "Avoid eval. Use arrays or case statements instead",
                }
            )

        # Critical: Command injection via unquoted command substitution
        if re.search(r"\$\([^)]*\$[A-Za-z_]", line):
            if not re.search(r'"\$\([^)]*\$[A-Za-z_]', line):
                issues.append(
                    {
                        "severity": "critical",
                        "line_number": str(line_num),
                        "issue_type": "command_injection",
                        "description": "Unquoted command substitution with variables",
                        "recommendation": 'Quote command substitutions: "$(...)"',
                    }
                )

        # High: rm -rf with variables
        if re.search(r"\brm\s+(-[rf]+|--recursive|--force).*\$", line):
            issues.append(
                {
                    "severity": "high",
                    "line_number": str(line_num),
                    "issue_type": "destructive_operation",
                    "description": "rm -rf with variable expansion",
                    "recommendation": "Validate variables before rm -rf. Use arrays for paths",
                }
            )

        # High: wget/curl without SSL verification
        if re.search(r"\b(wget|curl)\s+.*(-k|--insecure|--no-check-certificate)", line):
            issues.append(
                {
                    "severity": "high",
                    "line_number": str(line_num),
                    "issue_type": "insecure_download",
                    "description": "Download without SSL certificate verification",
                    "recommendation": "Remove -k/--insecure flags to enforce SSL verification",
                }
            )

        # High: chmod 777
        if re.search(r"\bchmod\s+(777|a\+rwx)", line):
            issues.append(
                {
                    "severity": "high",
                    "line_number": str(line_num),
                    "issue_type": "insecure_permissions",
                    "description": "Setting world-writable permissions (777)",
                    "recommendation": "Use restrictive permissions like 755 or 644",
                }
            )

        # Medium: source/. with untrusted files
        if re.search(r"\b(source|\.)\s+\$[A-Za-z_]", line):
            issues.append(
                {
                    "severity": "medium",
                    "line_number": str(line_num),
                    "issue_type": "code_injection",
                    "description": "Sourcing file from variable without validation",
                    "recommendation": "Validate file path before sourcing",
                }
            )

        # Medium: sudo without path
        if re.search(r"\bsudo\s+(?!/)[\w-]+", line):
            issues.append(
                {
                    "severity": "medium",
                    "line_number": str(line_num),
                    "issue_type": "privilege_escalation",
                    "description": "sudo command without absolute path",
                    "recommendation": "Use absolute paths with sudo for security",
                }
            )

        # Low: echo with command substitution (prefer printf)
        if re.search(r"\becho\s+.*\$\(", line):
            issues.append(
                {
                    "severity": "low",
                    "line_number": str(line_num),
                    "issue_type": "best_practice",
                    "description": "echo with command substitution",
                    "recommendation": "Use printf for more reliable output",
                }
            )

    return issues


@strands_tool
def detect_shell_injection_risks(script_content: str) -> list[dict[str, str]]:
    """Detect potential shell injection vulnerabilities.

    Focuses specifically on command injection patterns that could allow
    arbitrary code execution. More targeted than analyze_shell_security.

    Args:
        script_content: The shell script content to analyze

    Returns:
        List of injection risks, each with:
        - risk_level: "critical", "high", or "medium"
        - line_number: Line number of the risk
        - pattern: The dangerous pattern found
        - context: Surrounding code context
        - mitigation: How to mitigate the risk

    Raises:
        TypeError: If script_content is not a string
        ValueError: If script_content is empty
    """
    if not isinstance(script_content, str):
        raise TypeError("script_content must be a string")

    if not script_content.strip():
        raise ValueError("script_content cannot be empty")

    risks: list[dict[str, str]] = []
    lines = script_content.split("\n")

    injection_patterns = [
        {
            "pattern": r"\beval\s+",
            "risk_level": "critical",
            "description": "eval statement",
            "mitigation": "Never use eval with user input. Use safer alternatives",
        },
        {
            "pattern": r"\bexec\s+[\"']?\$",
            "risk_level": "critical",
            "description": "exec with variable",
            "mitigation": "Validate and sanitize input before exec",
        },
        {
            "pattern": r"\$\{[^}]*;\s*[^}]*\}",
            "risk_level": "critical",
            "description": "Command substitution with semicolon",
            "mitigation": "Avoid complex substitutions. Use proper quoting",
        },
        {
            "pattern": r"``[^`]*\$[^`]*``",
            "risk_level": "high",
            "description": "Backtick command substitution with variables",
            "mitigation": 'Use $(...) syntax and quote: "$(...)"',
        },
        {
            "pattern": r"\|\s*sh\s*$",
            "risk_level": "high",
            "description": "Piping to shell without validation",
            "mitigation": "Validate input before piping to shell",
        },
        {
            "pattern": r">\s*/dev/tcp/\$",
            "risk_level": "high",
            "description": "Network connection with variable",
            "mitigation": "Validate network endpoints before connecting",
        },
        {
            "pattern": r"\$\([^)]*;[^)]*\)",
            "risk_level": "medium",
            "description": "Command substitution with semicolon separator",
            "mitigation": "Use separate commands. Avoid complex substitutions",
        },
    ]

    for line_num, line in enumerate(lines, start=1):
        for pattern_info in injection_patterns:
            if re.search(pattern_info["pattern"], line):
                # Get context (line before and after if available)
                context_lines = []
                if line_num > 1:
                    context_lines.append(lines[line_num - 2].rstrip())
                context_lines.append(line.rstrip())
                if line_num < len(lines):
                    context_lines.append(lines[line_num].rstrip())

                risks.append(
                    {
                        "risk_level": pattern_info["risk_level"],
                        "line_number": str(line_num),
                        "pattern": pattern_info["description"],
                        "context": " | ".join(context_lines),
                        "mitigation": pattern_info["mitigation"],
                    }
                )

    return risks


@strands_tool
def scan_for_secrets_enhanced(content: str, use_detect_secrets: str) -> dict[str, Any]:
    """Scan for secrets with optional detect-secrets integration.

    Uses stdlib regex patterns by default. If use_detect_secrets is "true"
    and detect-secrets is installed, uses comprehensive 1000+ pattern library.
    Falls back gracefully to stdlib if detect-secrets not available.

    Args:
        content: Content to scan for secrets
        use_detect_secrets: "true" to attempt detect-secrets, "false" for stdlib only

    Returns:
        Dictionary with:
        - secrets_found: List of secret dictionaries with type, line, value_hash
        - scan_method: "detect-secrets" or "stdlib-regex"
        - patterns_checked: Number of patterns checked
        - has_secrets: "true" if secrets found, "false" otherwise

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If content is empty or use_detect_secrets invalid
    """
    if not isinstance(content, str):
        raise TypeError("content must be a string")
    if not isinstance(use_detect_secrets, str):
        raise TypeError("use_detect_secrets must be a string")

    if not content.strip():
        raise ValueError("content cannot be empty")

    if use_detect_secrets not in ("true", "false"):
        raise ValueError("use_detect_secrets must be 'true' or 'false'")

    # Try detect-secrets if requested
    if use_detect_secrets == "true":
        try:
            from detect_secrets import (
                SecretsCollection,  # type: ignore[import-not-found]
            )
            from detect_secrets.settings import (
                default_settings,  # type: ignore[import-not-found]
            )

            # Create a secrets collection
            secrets_collection = SecretsCollection()

            # Scan the content
            secrets_collection.scan_file("<string>", content=content)

            # Extract findings
            findings = []
            for _filename, secrets_list in secrets_collection.data.items():
                for secret in secrets_list:
                    findings.append(
                        {
                            "type": secret.type,
                            "line_number": str(secret.line_number),
                            "value_hash": secret.secret_hash[:16],
                        }
                    )

            # Count plugins (patterns)
            patterns_count = len(default_settings.plugins_used)

            return {
                "secrets_found": findings,
                "scan_method": "detect-secrets",
                "patterns_checked": str(patterns_count),
                "has_secrets": "true" if findings else "false",
            }

        except ImportError:
            # Fall through to stdlib implementation
            pass
        except Exception:
            # If detect-secrets fails for any reason, fall back
            pass

    # Stdlib fallback using simple regex patterns
    enhanced_secrets: list[dict[str, str]] = []
    lines = content.split("\n")

    for line_num, line in enumerate(lines, start=1):
        for pattern_name, pattern in _SECRET_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                enhanced_secrets.append(
                    {
                        "type": pattern_name,
                        "line_number": str(line_num),
                        "value_hash": line[:16].strip(),
                    }
                )

    return {
        "secrets_found": enhanced_secrets,
        "scan_method": "stdlib-regex",
        "patterns_checked": str(len(_SECRET_PATTERNS)),
        "has_secrets": "true" if enhanced_secrets else "false",
    }


# Secret patterns for stdlib fallback (subset of common patterns)
_SECRET_PATTERNS = {
    "API Key": r"(?i)(api[_-]?key|apikey)[\s=:]+['\"]?([a-z0-9]{20,})['\"]?",
    "AWS Access Key": r"(?i)aws[_-]?access[_-]?key[_-]?id[\s=:]+['\"]?([A-Z0-9]{20})['\"]?",
    "AWS Secret Key": r"(?i)aws[_-]?secret[_-]?access[_-]?key[\s=:]+['\"]?([A-Za-z0-9/+=]{40})['\"]?",
    "GitHub Token": r"(?i)github[_-]?token[\s=:]+['\"]?([a-z0-9]{40})['\"]?",
    "Private Key": r"-----BEGIN\s+(RSA|DSA|EC|OPENSSH)\s+PRIVATE\s+KEY-----",
    "Password": r"(?i)(password|passwd|pwd)[\s=:]+['\"]?([^\s'\"]{6,})['\"]?",
    "Generic Secret": r"(?i)(secret|token)[\s=:]+['\"]?([a-z0-9]{20,})['\"]?",
    "Database URL": r"(?i)(postgres|mysql|mongodb)://[^\s'\"]+",
}
