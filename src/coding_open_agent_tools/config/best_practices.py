"""Configuration security and best practices checking functions.

Provides tools for checking gitignore coverage, exposed configs, and file permissions.
"""

import json
import os
import platform
import re

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def check_gitignore_security(gitignore_content: str) -> dict[str, str]:
    """Check gitignore for common security patterns.

    Scans for missing entries that could expose secrets, credentials, or sensitive configs.

    Args:
        gitignore_content: Contents of .gitignore file as string

    Returns:
        Dictionary with:
        - is_secure: "true" or "false"
        - missing_count: Number of recommended patterns missing
        - missing_patterns: JSON list of recommended patterns to add
        - warnings: JSON list of security warnings
        - covered_patterns: JSON list of patterns already covered

    Raises:
        TypeError: If gitignore_content is not a string
    """
    if not isinstance(gitignore_content, str):
        raise TypeError("gitignore_content must be a string")

    # Recommended security patterns
    recommended_patterns = {
        # Environment and secrets
        ".env": "Environment variables with secrets",
        ".env.*": "Environment files for different stages",
        "*.env": "Any .env variant files",
        ".envrc": "direnv configuration with secrets",
        "# Credentials and keys": "Section header for credentials",
        "*.key": "Private key files",
        "*.pem": "Certificate/key files",
        "*.pfx": "Certificate files",
        "*.p12": "Certificate files",
        "*.keystore": "Java keystore files",
        "*.jks": "Java keystore files",
        "*.pkcs12": "Certificate files",
        "credentials.json": "Service account credentials",
        "*credentials*": "Any credentials files",
        "secrets.json": "Secrets configuration",
        "*secret*": "Any secrets files",
        "*.cer": "Certificate files",
        "*.crt": "Certificate files",
        # AWS and cloud credentials
        ".aws/credentials": "AWS credentials",
        ".aws/config": "AWS configuration",
        # Database and service configs
        "*.sqlite": "SQLite database files",
        "*.sqlite3": "SQLite database files",
        "*.db": "Database files",
        "database.yml": "Database credentials",
        # IDE and local configs
        ".vscode/settings.json": "VS Code workspace settings",
        ".idea/": "JetBrains IDE configs",
        "*.iml": "IntelliJ module files",
        # Build artifacts that may contain secrets
        "dist/": "Build distribution",
        "build/": "Build artifacts",
        "*.egg-info/": "Python package metadata",
        "__pycache__/": "Python cache",
        "*.pyc": "Python bytecode",
        ".pytest_cache/": "Pytest cache",
        "node_modules/": "Node.js dependencies",
        "vendor/": "Vendor dependencies",
    }

    # Parse existing patterns from gitignore
    existing_patterns = set()
    for line in gitignore_content.splitlines():
        stripped = line.strip()
        # Skip comments and empty lines
        if stripped and not stripped.startswith("#"):
            existing_patterns.add(stripped)

    # Check for missing patterns
    missing = []
    covered = []
    warnings = []

    for pattern, reason in recommended_patterns.items():
        # Check if pattern is covered (exact match or wildcard match)
        is_covered = False

        if pattern in existing_patterns:
            is_covered = True
        else:
            # Check for wildcard coverage
            for existing in existing_patterns:
                if _pattern_covers(existing, pattern):
                    is_covered = True
                    break

        if is_covered:
            covered.append(f"{pattern} - {reason}")
        else:
            missing.append(f"{pattern} - {reason}")

    # Additional security warnings
    if ".env" not in existing_patterns:
        warnings.append(
            "CRITICAL: .env file not ignored - may expose secrets in version control"
        )

    if not any("*.key" in p or "*.pem" in p for p in existing_patterns):
        warnings.append(
            "WARNING: No key/certificate file patterns - private keys may be committed"
        )

    if not any("credential" in p.lower() for p in existing_patterns):
        warnings.append(
            "WARNING: No credential file patterns - service credentials may be exposed"
        )

    # Check for overly permissive patterns
    for pattern in existing_patterns:
        if pattern == "*":
            warnings.append("CRITICAL: '*' pattern ignores everything in directory")
        elif pattern == "**":
            warnings.append("CRITICAL: '**' pattern ignores everything recursively")

    return {
        "is_secure": "true" if len(missing) == 0 else "false",
        "missing_count": str(len(missing)),
        "missing_patterns": json.dumps(missing),
        "warnings": json.dumps(warnings),
        "covered_patterns": json.dumps(covered),
    }


def _pattern_covers(broader_pattern: str, specific_pattern: str) -> bool:
    """Check if a gitignore pattern covers another pattern.

    Args:
        broader_pattern: The potentially broader pattern
        specific_pattern: The specific pattern to check coverage for

    Returns:
        True if broader_pattern covers specific_pattern
    """
    # Convert gitignore pattern to regex
    # This is simplified - full gitignore pattern matching is complex
    pattern_regex = broader_pattern.replace(".", r"\.")
    pattern_regex = pattern_regex.replace("*", ".*")
    pattern_regex = pattern_regex.replace("?", ".")

    # Check if specific pattern matches
    try:
        return bool(re.match(f"^{pattern_regex}$", specific_pattern))
    except re.error:
        return False


@strands_tool
def detect_exposed_config_files(directory_structure: str) -> dict[str, str]:
    """Detect configuration files in potentially exposed locations.

    Checks for configs in web-accessible directories or wrong locations.

    Args:
        directory_structure: JSON string representing directory tree
                            Format: {"path/to/file": "file", "path/to/": "dir"}

    Returns:
        Dictionary with:
        - has_exposures: "true" or "false"
        - exposure_count: Number of exposed configs found
        - exposures: JSON list of exposed file paths with risk level
        - recommendations: JSON list of recommended actions

    Raises:
        TypeError: If directory_structure is not a string
        ValueError: If directory_structure is not valid JSON
    """
    if not isinstance(directory_structure, str):
        raise TypeError("directory_structure must be a string")

    try:
        structure = json.loads(directory_structure)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in directory_structure: {str(e)}")

    if not isinstance(structure, dict):
        raise ValueError("directory_structure must be a JSON object/dictionary")

    exposures = []
    recommendations = []

    # Patterns for sensitive files
    sensitive_patterns = {
        r"\.env$": "CRITICAL",
        r"\.env\..*$": "CRITICAL",
        r"credentials\..*": "CRITICAL",
        r"secrets\..*": "CRITICAL",
        r".*\.key$": "CRITICAL",
        r".*\.pem$": "CRITICAL",
        r"database\.yml$": "HIGH",
        r"config\.yml$": "MEDIUM",
        r".*\.sqlite$": "HIGH",
        r".*\.db$": "MEDIUM",
    }

    # Patterns for exposed directories (should not contain configs)
    exposed_dirs = [
        "public/",
        "static/",
        "assets/",
        "dist/",
        "build/",
        "www/",
        "htdocs/",
        "web/",
    ]

    for path, _item_type in structure.items():
        # Check if file matches sensitive pattern
        for pattern, risk_level in sensitive_patterns.items():
            if re.search(pattern, os.path.basename(path)):
                # Check if in exposed directory
                is_exposed = any(path.startswith(exp_dir) for exp_dir in exposed_dirs)

                if is_exposed:
                    exposures.append(
                        {
                            "path": path,
                            "risk_level": risk_level,
                            "reason": "Sensitive file in web-accessible directory",
                        }
                    )

                # Also flag if in root directory
                elif "/" not in path.strip("/"):
                    exposures.append(
                        {
                            "path": path,
                            "risk_level": "MEDIUM",
                            "reason": "Sensitive file in root directory",
                        }
                    )

    # Generate recommendations
    if exposures:
        recommendations.append("Move sensitive config files to a non-public directory")
        recommendations.append("Ensure .gitignore covers all sensitive files")
        recommendations.append(
            "Use environment variables instead of committed config files"
        )
        recommendations.append("Review web server configuration to deny access to .*")

    exposure_strings = [
        f"{exp['path']} - {exp['risk_level']}: {exp['reason']}" for exp in exposures
    ]

    return {
        "has_exposures": "true" if len(exposures) > 0 else "false",
        "exposure_count": str(len(exposures)),
        "exposures": json.dumps(exposure_strings),
        "recommendations": json.dumps(recommendations),
    }


@strands_tool
def validate_config_permissions(file_permissions: str) -> dict[str, str]:
    """Validate configuration file permissions for security.

    Checks for overly permissive file permissions on sensitive configs.

    Note: This function validates Unix-style permissions (Linux/macOS/BSD).
    On Windows, it returns a message indicating permission validation is not
    supported, as Windows uses a different permissions model (ACLs).

    Args:
        file_permissions: JSON string of file paths and their permissions
                         Format: {"path/to/file": "0644", "path/to/key": "0600"}

    Returns:
        Dictionary with:
        - is_secure: "true" or "false"
        - violation_count: Number of permission violations
        - violations: JSON list of files with insecure permissions
        - recommendations: JSON list of recommended permission changes

    Raises:
        TypeError: If file_permissions is not a string
        ValueError: If file_permissions is not valid JSON
    """
    if not isinstance(file_permissions, str):
        raise TypeError("file_permissions must be a string")

    try:
        permissions_dict = json.loads(file_permissions)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file_permissions: {str(e)}")

    if not isinstance(permissions_dict, dict):
        raise ValueError("file_permissions must be a JSON object/dictionary")

    # Windows uses ACLs, not Unix permissions - skip validation on Windows
    if platform.system() == "Windows":
        return {
            "is_secure": "true",
            "violation_count": "0",
            "violations": json.dumps([]),
            "recommendations": json.dumps(
                [
                    "Permission validation is not supported on Windows",
                    "Windows uses ACLs (Access Control Lists) instead of Unix permissions",
                    "Use Windows File Explorer or icacls command to manage file permissions",
                    "Ensure sensitive files like .env are not readable by all users",
                ]
            ),
        }

    violations = []
    recommendations = []

    # Define secure permission requirements
    permission_rules = {
        r"\.env$": "0600",  # Only owner read/write
        r"\.env\..*": "0600",
        r".*credentials.*": "0600",
        r".*secret.*": "0600",
        r".*\.key$": "0600",
        r".*\.pem$": "0600",
        r"database\.yml$": "0640",  # Owner RW, group R
        r"config\.yml$": "0644",  # Owner RW, others R
    }

    for file_path, perms in permissions_dict.items():
        # Convert permission string to octal integer
        try:
            perm_value = int(perms, 8) if isinstance(perms, str) else perms
        except ValueError:
            violations.append(
                {
                    "path": file_path,
                    "current": perms,
                    "recommended": "0644",
                    "reason": "Invalid permission format",
                }
            )
            continue

        # Check against rules
        for pattern, required_perms in permission_rules.items():
            if re.search(pattern, os.path.basename(file_path)):
                required_value = int(required_perms, 8)

                # Check if permissions are too open
                if perm_value > required_value:
                    violations.append(
                        {
                            "path": file_path,
                            "current": perms,
                            "recommended": required_perms,
                            "reason": "Permissions too permissive for sensitive file",
                        }
                    )
                break

        # Always check for world-writable (risky for any config)
        if perm_value & 0o002:  # World-writable bit
            violations.append(
                {
                    "path": file_path,
                    "current": perms,
                    "recommended": oct(perm_value & ~0o002),
                    "reason": "World-writable permissions are dangerous",
                }
            )

        # Check for group-writable on sensitive files
        if re.search(r"\.(env|key|pem|credentials)", file_path) and (
            perm_value & 0o020
        ):
            violations.append(
                {
                    "path": file_path,
                    "current": perms,
                    "recommended": "0600",
                    "reason": "Sensitive file should not be group-writable",
                }
            )

    # Generate recommendations
    if violations:
        recommendations.append("Use chmod to fix file permissions")
        recommendations.append(
            "Sensitive files (.env, .key) should be 0600 (owner only)"
        )
        recommendations.append("Never use 0777 (world-writable) on config files")
        recommendations.append(
            "Review umask settings to prevent overly permissive defaults"
        )

    violation_strings = [
        f"{v['path']}: {v['current']} -> {v['recommended']} ({v['reason']})"
        for v in violations
    ]

    return {
        "is_secure": "true" if len(violations) == 0 else "false",
        "violation_count": str(len(violations)),
        "violations": json.dumps(violation_strings),
        "recommendations": json.dumps(recommendations),
    }
