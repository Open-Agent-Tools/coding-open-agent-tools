"""Configuration security scanning functions.

Provides secret detection and insecure settings analysis for configuration files.
"""

import re

from coding_open_agent_tools._decorators import strands_tool

# Common patterns for secrets in configuration files
SECRET_PATTERNS = {
    "aws_access_key": r"(?i)(aws_access_key_id|aws_access_key)\s*[:=]\s*['\"]?([A-Z0-9]{20})['\"]?",
    "aws_secret_key": r"(?i)(aws_secret_access_key|aws_secret_key)\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?",
    "api_key": r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{20,})['\"]?",
    "password": r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?([^\s'\";]{8,})['\"]?",
    "secret": r"(?i)(secret)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{16,})['\"]?",
    "token": r"(?i)(token|auth_token)\s*[:=]\s*['\"]?([A-Za-z0-9_\-\.]{20,})['\"]?",
    "private_key": r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----",
    "github_token": r"(?i)gh[pousr]_[A-Za-z0-9_]{36,}",
    "slack_token": r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24,}",
    "slack_webhook": r"https://hooks\.slack\.com/services/T[A-Z0-9]{8,}/B[A-Z0-9]{8,}/[A-Za-z0-9]{24,}",
    "connection_string": r"(?i)(mongodb|postgresql|mysql|redis)://[^:]+:[^@]+@",
}

# Patterns for insecure configuration settings
INSECURE_PATTERNS = {
    "debug_enabled": {
        "pattern": r"(?i)(debug|DEBUG)\s*[:=]\s*['\"]?(true|True|1)['\"]?",
        "severity": "medium",
        "message": "Debug mode enabled in configuration",
    },
    "ssl_disabled": {
        "pattern": r"(?i)(ssl_verify|verify_ssl|SSL_VERIFY)\s*[:=]\s*['\"]?(false|False|0)['\"]?",
        "severity": "high",
        "message": "SSL verification disabled",
    },
    "insecure_protocol": {
        "pattern": r"(?i)(protocol|scheme)\s*[:=]\s*['\"]?(http|ftp)['\"]?(?!\s*s)",
        "severity": "medium",
        "message": "Insecure protocol (HTTP/FTP) used instead of HTTPS/FTPS",
    },
    "wildcard_cors": {
        "pattern": r"(?i)(cors_origin|access[_-]control[_-]allow[_-]origin)\s*[:=]\s*['\"]?\*['\"]?",
        "severity": "high",
        "message": "CORS allows all origins (*)",
    },
    "permissive_permissions": {
        "pattern": r"(?i)(permissions|mode|chmod)\s*[:=]\s*['\"]?(777|666)['\"]?",
        "severity": "high",
        "message": "Overly permissive file permissions (777/666)",
    },
    "default_credentials": {
        "pattern": r"(?i)(password|passwd)\s*[:=]\s*['\"]?(admin|password|123456|default)['\"]?",
        "severity": "critical",
        "message": "Default or weak credentials detected",
    },
    "exposed_admin": {
        "pattern": r"(?i)(admin_enabled|enable_admin)\s*[:=]\s*['\"]?(true|True|1)['\"]?",
        "severity": "medium",
        "message": "Admin interface enabled",
    },
    "insecure_session": {
        "pattern": r"(?i)(session_cookie_secure|cookie_secure)\s*[:=]\s*['\"]?(false|False|0)['\"]?",
        "severity": "medium",
        "message": "Secure cookie flag not set",
    },
}


@strands_tool
def scan_config_for_secrets(
    config_content: str, use_detect_secrets: str
) -> dict[str, str]:
    """Scan configuration content for potential secrets.

    Uses detect-secrets library if available and requested, otherwise falls
    back to basic regex pattern matching.

    Args:
        config_content: Configuration file content to scan
        use_detect_secrets: "true" to use detect-secrets library, "false" for regex

    Returns:
        Dictionary with:
        - secrets_found: "true" or "false"
        - secret_count: Number of potential secrets detected
        - secret_types: Comma-separated list of secret types found
        - detection_method: "detect-secrets" or "regex"
        - details: Additional details about findings

    Raises:
        TypeError: If arguments are not strings
        ValueError: If config_content is empty or use_detect_secrets not "true"/"false"
    """
    if not isinstance(config_content, str):
        raise TypeError("config_content must be a string")
    if not isinstance(use_detect_secrets, str):
        raise TypeError("use_detect_secrets must be a string")

    if not config_content.strip():
        raise ValueError("config_content cannot be empty")
    if use_detect_secrets not in ("true", "false"):
        raise ValueError('use_detect_secrets must be "true" or "false"')

    # Try detect-secrets if requested
    if use_detect_secrets == "true":
        try:
            from detect_secrets import SecretsCollection  # type: ignore[import-untyped]
            from detect_secrets.settings import (
                default_settings,  # type: ignore[import-untyped]
            )

            secrets = SecretsCollection()
            with default_settings():
                secrets.scan_file("config", config_content)

            if secrets.data:
                secret_types = set()
                for file_secrets in secrets.data.values():
                    for secret in file_secrets.values():
                        secret_types.add(secret.type)

                return {
                    "secrets_found": "true",
                    "secret_count": str(len(list(secrets))),
                    "secret_types": ", ".join(sorted(secret_types)),
                    "detection_method": "detect-secrets",
                    "details": f"Found {len(list(secrets))} potential secrets using detect-secrets",
                }
            else:
                return {
                    "secrets_found": "false",
                    "secret_count": "0",
                    "secret_types": "",
                    "detection_method": "detect-secrets",
                    "details": "No secrets detected",
                }
        except ImportError:
            # Fall through to regex-based detection
            pass

    # Regex-based detection
    found_secrets = []
    for secret_type, pattern in SECRET_PATTERNS.items():
        matches = re.finditer(pattern, config_content)
        for _match in matches:
            found_secrets.append(secret_type)

    if found_secrets:
        # Count unique types
        unique_types = sorted(set(found_secrets))
        return {
            "secrets_found": "true",
            "secret_count": str(len(found_secrets)),
            "secret_types": ", ".join(unique_types),
            "detection_method": "regex",
            "details": f"Found {len(found_secrets)} potential secrets across {len(unique_types)} types",
        }
    else:
        return {
            "secrets_found": "false",
            "secret_count": "0",
            "secret_types": "",
            "detection_method": "regex",
            "details": "No secrets detected using regex patterns",
        }


@strands_tool
def detect_insecure_settings(config_content: str) -> dict[str, str]:
    """Detect insecure configuration settings using pattern matching.

    Scans for common security misconfigurations like debug mode enabled,
    SSL disabled, wildcard CORS, default credentials, etc.

    Args:
        config_content: Configuration file content to analyze

    Returns:
        Dictionary with:
        - issues_found: "true" or "false"
        - issue_count: Number of insecure settings detected
        - critical_count: Number of critical severity issues
        - high_count: Number of high severity issues
        - medium_count: Number of medium severity issues
        - issue_summary: Brief summary of issues found

    Raises:
        TypeError: If config_content is not a string
        ValueError: If config_content is empty
    """
    if not isinstance(config_content, str):
        raise TypeError("config_content must be a string")
    if not config_content.strip():
        raise ValueError("config_content cannot be empty")

    issues = []
    severity_counts = {"critical": 0, "high": 0, "medium": 0}

    for setting_name, setting_info in INSECURE_PATTERNS.items():
        pattern = setting_info["pattern"]
        severity = setting_info["severity"]
        message = setting_info["message"]

        matches = re.finditer(pattern, config_content)
        for match in matches:
            issues.append(
                {
                    "setting": setting_name,
                    "severity": severity,
                    "message": message,
                    "line": config_content[: match.start()].count("\n") + 1,
                }
            )
            severity_counts[severity] += 1

    if issues:
        issue_messages = [
            f"{str(issue['severity']).upper()}: {issue['message']}"
            for issue in issues[:3]
        ]
        summary = "; ".join(issue_messages)
        if len(issues) > 3:
            summary += f" (and {len(issues) - 3} more)"

        return {
            "issues_found": "true",
            "issue_count": str(len(issues)),
            "critical_count": str(severity_counts["critical"]),
            "high_count": str(severity_counts["high"]),
            "medium_count": str(severity_counts["medium"]),
            "issue_summary": summary,
        }
    else:
        return {
            "issues_found": "false",
            "issue_count": "0",
            "critical_count": "0",
            "high_count": "0",
            "medium_count": "0",
            "issue_summary": "No insecure settings detected",
        }
