"""Git configuration parsing and validation tools.

This module provides functions for parsing and validating git configuration files,
including .git/config, .gitignore, and .gitattributes.
"""

import re
import subprocess
from pathlib import Path

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def parse_git_config(repo_path: str) -> dict[str, str]:
    """Parse git configuration file into structured data.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - has_config: "true" if config file exists
        - sections_count: Number of configuration sections
        - sections: Newline-separated list of section names
        - remotes_count: Number of remote repositories
        - remotes: Newline-separated list of remote names
        - user_name: User name from config
        - user_email: User email from config

    Raises:
        TypeError: If repo_path is not a string
        ValueError: If repo_path is empty
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    config_file = repo / ".git" / "config"
    if not config_file.exists():
        return {
            "has_config": "false",
            "sections_count": "0",
            "sections": "",
            "remotes_count": "0",
            "remotes": "",
            "user_name": "",
            "user_email": "",
        }

    try:
        with open(config_file, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return {
            "has_config": "false",
            "sections_count": "0",
            "sections": "",
            "remotes_count": "0",
            "remotes": "",
            "user_name": "",
            "user_email": "",
        }

    # Parse sections
    sections = []
    remotes = []
    user_name = ""
    user_email = ""

    section_pattern = r"\[([^\]]+)\]"
    for match in re.finditer(section_pattern, content):
        section = match.group(1)
        sections.append(section)

        # Extract remote names
        if section.startswith("remote "):
            remote_name = section.replace("remote ", "").strip('"')
            remotes.append(remote_name)

    # Extract user info using git config command
    try:
        name_result = subprocess.run(
            ["git", "config", "user.name"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if name_result.returncode == 0:
            user_name = name_result.stdout.strip()

        email_result = subprocess.run(
            ["git", "config", "user.email"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if email_result.returncode == 0:
            user_email = email_result.stdout.strip()
    except Exception:
        pass

    return {
        "has_config": "true",
        "sections_count": str(len(sections)),
        "sections": "\n".join(sections),
        "remotes_count": str(len(remotes)),
        "remotes": "\n".join(remotes),
        "user_name": user_name,
        "user_email": user_email,
    }


@strands_tool
def validate_gitignore_patterns(gitignore_content: str) -> dict[str, str]:
    """Validate .gitignore pattern syntax.

    Args:
        gitignore_content: Content of .gitignore file

    Returns:
        Dictionary with:
        - is_valid: "true" if all patterns are valid
        - total_patterns: Total number of patterns
        - valid_patterns: Number of valid patterns
        - invalid_patterns: Number of invalid patterns
        - errors: Newline-separated list of errors
        - warnings: Newline-separated list of warnings

    Raises:
        TypeError: If gitignore_content is not a string
    """
    if not isinstance(gitignore_content, str):
        raise TypeError("gitignore_content must be a string")

    if not gitignore_content.strip():
        return {
            "is_valid": "true",
            "total_patterns": "0",
            "valid_patterns": "0",
            "invalid_patterns": "0",
            "errors": "",
            "warnings": "",
        }

    lines = gitignore_content.split("\n")
    patterns = []
    errors = []
    warnings = []

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            continue

        patterns.append(stripped)

        # Check for common issues
        # Double asterisks not at start/end of path segment
        if "**" in stripped:
            parts = stripped.split("/")
            for part in parts:
                if "**" in part and part != "**":
                    errors.append(
                        f"Line {line_num}: '**' must be alone in path segment: {stripped}"
                    )

        # Trailing spaces (common mistake)
        if line != stripped and not line.startswith("#"):
            warnings.append(f"Line {line_num}: Pattern has trailing/leading whitespace")

        # Patterns starting with / (anchored to repo root)
        if stripped.startswith("/") and "/" not in stripped[1:]:
            warnings.append(
                f"Line {line_num}: Leading / anchors to repo root, may not match expected files"
            )

        # Very broad patterns
        if stripped in ["*", "**", "**/*"]:
            warnings.append(
                f"Line {line_num}: Very broad pattern '{stripped}' - intentional?"
            )

    valid_patterns = len(patterns) - len(errors)
    is_valid = len(errors) == 0

    return {
        "is_valid": "true" if is_valid else "false",
        "total_patterns": str(len(patterns)),
        "valid_patterns": str(valid_patterns),
        "invalid_patterns": str(len(errors)),
        "errors": "\n".join(errors) if errors else "",
        "warnings": "\n".join(warnings) if warnings else "",
    }


@strands_tool
def parse_gitignore(repo_path: str) -> dict[str, str]:
    """Parse .gitignore file into structured pattern list.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - has_gitignore: "true" if .gitignore exists
        - total_lines: Total number of lines
        - pattern_count: Number of ignore patterns
        - comment_count: Number of comment lines
        - negation_count: Number of negation patterns (!)
        - patterns: Newline-separated list of patterns

    Raises:
        TypeError: If repo_path is not a string
        ValueError: If repo_path is empty
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    gitignore_file = repo / ".gitignore"
    if not gitignore_file.exists():
        return {
            "has_gitignore": "false",
            "total_lines": "0",
            "pattern_count": "0",
            "comment_count": "0",
            "negation_count": "0",
            "patterns": "",
        }

    try:
        with open(gitignore_file, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return {
            "has_gitignore": "false",
            "total_lines": "0",
            "pattern_count": "0",
            "comment_count": "0",
            "negation_count": "0",
            "patterns": "",
        }

    lines = content.split("\n")
    patterns = []
    comments = 0
    negations = 0

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            comments += 1
        else:
            patterns.append(stripped)
            if stripped.startswith("!"):
                negations += 1

    return {
        "has_gitignore": "true",
        "total_lines": str(len(lines)),
        "pattern_count": str(len(patterns)),
        "comment_count": str(comments),
        "negation_count": str(negations),
        "patterns": "\n".join(patterns),
    }


@strands_tool
def validate_gitattributes(gitattributes_content: str) -> dict[str, str]:
    """Validate .gitattributes file syntax.

    Args:
        gitattributes_content: Content of .gitattributes file

    Returns:
        Dictionary with:
        - is_valid: "true" if syntax is valid
        - total_rules: Total number of attribute rules
        - pattern_count: Number of file patterns
        - errors: Newline-separated syntax errors
        - warnings: Newline-separated warnings
        - attributes_used: Newline-separated list of attributes

    Raises:
        TypeError: If gitattributes_content is not a string
    """
    if not isinstance(gitattributes_content, str):
        raise TypeError("gitattributes_content must be a string")

    if not gitattributes_content.strip():
        return {
            "is_valid": "true",
            "total_rules": "0",
            "pattern_count": "0",
            "errors": "",
            "warnings": "",
            "attributes_used": "",
        }

    lines = gitattributes_content.split("\n")
    rules = []
    patterns = set()
    attributes = set()
    errors = []
    warnings = []

    # Common attributes
    known_attributes = {
        "text",
        "eol",
        "binary",
        "diff",
        "merge",
        "filter",
        "whitespace",
        "export-ignore",
        "export-subst",
        "delta",
        "encoding",
        "working-tree-encoding",
    }

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            continue

        rules.append(stripped)

        # Parse line: pattern attr=value attr -attr
        parts = stripped.split()
        if len(parts) < 2:
            errors.append(
                f"Line {line_num}: Invalid syntax, need at least pattern and one attribute"
            )
            continue

        pattern = parts[0]
        patterns.add(pattern)

        # Parse attributes
        for attr_spec in parts[1:]:
            # Handle negation (-attr), set (attr), unset (attr=)
            if attr_spec.startswith("-"):
                attr_name = attr_spec[1:]
            elif "=" in attr_spec:
                attr_name = attr_spec.split("=")[0]
            else:
                attr_name = attr_spec

            attributes.add(attr_name)

            # Warn about unknown attributes
            if attr_name not in known_attributes and not attr_name.startswith("diff-"):
                warnings.append(
                    f"Line {line_num}: Unknown attribute '{attr_name}' (may be custom)"
                )

    is_valid = len(errors) == 0

    return {
        "is_valid": "true" if is_valid else "false",
        "total_rules": str(len(rules)),
        "pattern_count": str(len(patterns)),
        "errors": "\n".join(errors) if errors else "",
        "warnings": "\n".join(warnings) if warnings else "",
        "attributes_used": "\n".join(sorted(attributes)),
    }


@strands_tool
def analyze_config_security(repo_path: str) -> dict[str, str]:
    """Analyze git configuration for security issues.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - is_secure: "true" if no security issues found
        - issues_count: Number of security issues
        - has_http_urls: "true" if using insecure HTTP URLs
        - has_global_hooks: "true" if global hooks configured
        - warnings: Newline-separated security warnings
        - recommendations: Security recommendations

    Raises:
        TypeError: If repo_path is not a string
        ValueError: If repo_path is empty
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    config_file = repo / ".git" / "config"
    if not config_file.exists():
        return {
            "is_secure": "true",
            "issues_count": "0",
            "has_http_urls": "false",
            "has_global_hooks": "false",
            "warnings": "",
            "recommendations": "No config file found",
        }

    try:
        with open(config_file, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return {
            "is_secure": "true",
            "issues_count": "0",
            "has_http_urls": "false",
            "has_global_hooks": "false",
            "warnings": "",
            "recommendations": "Unable to read config file",
        }

    warnings = []
    recommendations = []

    # Check for insecure HTTP URLs
    has_http_urls = bool(re.search(r"url\s*=\s*http://", content))
    if has_http_urls:
        warnings.append("Insecure HTTP URLs found in remote configuration")
        recommendations.append("Use HTTPS URLs instead of HTTP for remote repositories")

    # Check for hooks path configuration
    has_global_hooks = bool(re.search(r"hooksPath", content))
    if has_global_hooks:
        warnings.append("Global hooks path configured - verify hooks are trusted")
        recommendations.append("Review hooks in configured hooks path for security")

    # Check for credential helper storing passwords
    if re.search(r"helper\s*=\s*store", content):
        warnings.append("Credentials stored in plaintext (git credential store)")
        recommendations.append(
            "Consider using a more secure credential helper (e.g., osxkeychain, wincred)"
        )

    # Check for push.default = matching (potentially dangerous)
    if re.search(r"default\s*=\s*matching", content):
        warnings.append("push.default set to 'matching' - may push unexpected branches")
        recommendations.append("Consider using push.default = simple or current")

    # Check for core.sharedRepository
    if re.search(r"sharedRepository", content):
        warnings.append("Shared repository mode enabled - verify file permissions")
        recommendations.append(
            "Ensure file permissions are appropriate for shared access"
        )

    is_secure = len(warnings) == 0

    return {
        "is_secure": "true" if is_secure else "false",
        "issues_count": str(len(warnings)),
        "has_http_urls": "true" if has_http_urls else "false",
        "has_global_hooks": "true" if has_global_hooks else "false",
        "warnings": "\n".join(warnings) if warnings else "",
        "recommendations": "\n".join(recommendations)
        if recommendations
        else "No security issues found",
    }


@strands_tool
def get_config_value(repo_path: str, config_key: str) -> dict[str, str]:
    """Get specific configuration value from git config.

    Args:
        repo_path: Path to git repository
        config_key: Configuration key (e.g., "user.name", "remote.origin.url")

    Returns:
        Dictionary with:
        - has_value: "true" if config key exists
        - value: Configuration value
        - scope: Config scope (local, global, system)
        - error_message: Error message if key doesn't exist

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(config_key, str):
        raise TypeError("config_key must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not config_key.strip():
        raise ValueError("config_key cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        # Get config value
        result = subprocess.run(
            ["git", "config", config_key],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            value = result.stdout.strip()

            # Try to determine scope
            scope = "unknown"
            try:
                # Check local config
                local_result = subprocess.run(
                    ["git", "config", "--local", config_key],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if local_result.returncode == 0:
                    scope = "local"
                else:
                    # Check global config
                    global_result = subprocess.run(
                        ["git", "config", "--global", config_key],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if global_result.returncode == 0:
                        scope = "global"
                    else:
                        scope = "system"
            except Exception:
                pass

            return {
                "has_value": "true",
                "value": value,
                "scope": scope,
                "error_message": "",
            }
        else:
            return {
                "has_value": "false",
                "value": "",
                "scope": "",
                "error_message": f"Config key '{config_key}' not found",
            }

    except subprocess.TimeoutExpired:
        return {
            "has_value": "false",
            "value": "",
            "scope": "",
            "error_message": "Command timed out",
        }
    except Exception as e:
        return {
            "has_value": "false",
            "value": "",
            "scope": "",
            "error_message": str(e),
        }
