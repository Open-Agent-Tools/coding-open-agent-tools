"""Git security auditing and secret scanning tools.

This module provides git-specific security functions, complementing the
analysis module's general secret detection with git history scanning.
"""

import subprocess
from pathlib import Path

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def scan_history_for_secrets(repo_path: str, max_commits: str) -> dict[str, str]:
    """Scan git commit history for potential secrets.

    Args:
        repo_path: Path to git repository
        max_commits: Maximum number of commits to scan

    Returns:
        Dictionary with:
        - secrets_found: "true" if potential secrets detected
        - commits_scanned: Number of commits scanned
        - suspicious_commits: Newline-separated list of commits with secrets
        - pattern_matches: Number of pattern matches
        - recommendations: Security recommendations

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty or invalid
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(max_commits, str):
        raise TypeError("max_commits must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")

    try:
        max_count = int(max_commits)
        if max_count <= 0:
            raise ValueError("max_commits must be positive")
    except ValueError:
        raise ValueError("max_commits must be a valid integer")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    # Import secret detection from analysis module
    try:
        from coding_open_agent_tools.analysis.secrets import scan_for_secrets

        result = subprocess.run(
            ["git", "log", f"--max-count={max_count}", "--format=%H|%s", "--"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            return {
                "secrets_found": "false",
                "commits_scanned": "0",
                "suspicious_commits": "",
                "pattern_matches": "0",
                "recommendations": "Could not scan commits",
            }

        commits = result.stdout.strip().split("\n")
        suspicious = []
        total_matches = 0

        for commit_line in commits:
            if not commit_line:
                continue
            parts = commit_line.split("|", 1)
            if len(parts) != 2:
                continue
            commit_hash, message = parts

            # Scan commit message
            scan_result = scan_for_secrets(message)
            if scan_result.get("secrets_found") == "true":
                suspicious.append(f"{commit_hash[:8]}: {message[:50]}")
                total_matches += int(scan_result.get("secrets_count", "0"))

        return {
            "secrets_found": "true" if suspicious else "false",
            "commits_scanned": str(len(commits)),
            "suspicious_commits": "\n".join(suspicious[:10]) if suspicious else "",
            "pattern_matches": str(total_matches),
            "recommendations": "Review and rewrite history if secrets confirmed"
            if suspicious
            else "No secrets detected in scanned commits",
        }
    except Exception as e:
        return {
            "secrets_found": "false",
            "commits_scanned": "0",
            "suspicious_commits": str(e),
            "pattern_matches": "0",
            "recommendations": "Error during scan",
        }


@strands_tool
def check_sensitive_files(repo_path: str) -> dict[str, str]:
    """Check for sensitive files in repository.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - has_sensitive_files: "true" if sensitive files found
        - sensitive_count: Number of sensitive files
        - sensitive_files: Newline-separated list of files
        - risk_level: "low", "medium", or "high"
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

    sensitive_patterns = {
        "high": [
            ".env",
            "credentials",
            "secret",
            ".pem",
            ".key",
            "id_rsa",
            ".p12",
            ".pfx",
        ],
        "medium": [".password", "auth", "token", ".cert", "keystore"],
        "low": [".config", ".ini", ".conf"],
    }

    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "has_sensitive_files": "false",
                "sensitive_count": "0",
                "sensitive_files": "",
                "risk_level": "low",
                "recommendations": "Could not scan files",
            }

        files = result.stdout.strip().split("\n")
        sensitive_files = []
        max_risk = "low"

        for file_path in files:
            if not file_path:
                continue
            lower_path = file_path.lower()

            # Check high risk patterns
            for pattern in sensitive_patterns["high"]:
                if pattern in lower_path:
                    sensitive_files.append(f"HIGH: {file_path}")
                    max_risk = "high"
                    break
            else:
                # Check medium risk
                for pattern in sensitive_patterns["medium"]:
                    if pattern in lower_path and max_risk != "high":
                        sensitive_files.append(f"MEDIUM: {file_path}")
                        if max_risk != "high":
                            max_risk = "medium"
                        break
                else:
                    # Check low risk
                    for pattern in sensitive_patterns["low"]:
                        if pattern in lower_path:
                            sensitive_files.append(f"LOW: {file_path}")
                            break

        recommendations = []
        if sensitive_files:
            recommendations.append(
                "Review sensitive files and ensure they should be tracked"
            )
            recommendations.append(
                "Consider adding to .gitignore if they contain secrets"
            )
            if max_risk == "high":
                recommendations.append("CRITICAL: Review high-risk files immediately")

        return {
            "has_sensitive_files": "true" if sensitive_files else "false",
            "sensitive_count": str(len(sensitive_files)),
            "sensitive_files": "\n".join(sensitive_files[:20])
            if sensitive_files
            else "",
            "risk_level": max_risk,
            "recommendations": "\n".join(recommendations)
            if recommendations
            else "No sensitive files detected",
        }
    except Exception as e:
        return {
            "has_sensitive_files": "false",
            "sensitive_count": "0",
            "sensitive_files": str(e),
            "risk_level": "low",
            "recommendations": "Error during scan",
        }


@strands_tool
def validate_gpg_signatures(repo_path: str, branch_name: str) -> dict[str, str]:
    """Validate GPG signatures for commits on a branch.

    Args:
        repo_path: Path to git repository
        branch_name: Branch to validate

    Returns:
        Dictionary with:
        - all_signed: "true" if all commits are signed
        - total_commits: Total commits checked
        - signed_commits: Number of signed commits
        - unsigned_commits: Number of unsigned commits
        - signature_validity: "all_valid", "some_invalid", or "none"

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(branch_name, str):
        raise TypeError("branch_name must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not branch_name.strip():
        raise ValueError("branch_name cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        result = subprocess.run(
            ["git", "log", branch_name, "--format=%H", "--max-count=50"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "all_signed": "false",
                "total_commits": "0",
                "signed_commits": "0",
                "unsigned_commits": "0",
                "signature_validity": "none",
            }

        commits = [c for c in result.stdout.strip().split("\n") if c]
        signed_count = 0
        valid_count = 0

        for commit in commits:
            verify_result = subprocess.run(
                ["git", "verify-commit", commit],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if verify_result.returncode == 0:
                signed_count += 1
                if "good signature" in verify_result.stderr.lower():
                    valid_count += 1

        all_signed = signed_count == len(commits)
        unsigned = len(commits) - signed_count

        if valid_count == len(commits):
            validity = "all_valid"
        elif valid_count > 0:
            validity = "some_invalid"
        else:
            validity = "none"

        return {
            "all_signed": "true" if all_signed else "false",
            "total_commits": str(len(commits)),
            "signed_commits": str(signed_count),
            "unsigned_commits": str(unsigned),
            "signature_validity": validity,
        }
    except Exception:
        return {
            "all_signed": "false",
            "total_commits": "0",
            "signed_commits": "0",
            "unsigned_commits": "0",
            "signature_validity": "none",
        }


# Remaining 5 security functions with similar patterns...
@strands_tool
def check_force_push_protection(repo_path: str) -> dict[str, str]:
    """Check if force push protection is enabled."""
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        result = subprocess.run(
            ["git", "config", "receive.denyNonFastForwards"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        enabled = result.returncode == 0 and result.stdout.strip() == "true"
        return {
            "is_protected": "true" if enabled else "false",
            "config_value": result.stdout.strip() if result.returncode == 0 else "",
            "recommendation": "No action needed"
            if enabled
            else "Enable receive.denyNonFastForwards",
        }
    except Exception as e:
        return {"is_protected": "false", "config_value": "", "recommendation": str(e)}


@strands_tool
def analyze_file_permissions(repo_path: str) -> dict[str, str]:
    """Analyze potentially dangerous file permissions in repository."""
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        result = subprocess.run(
            ["git", "ls-files", "-s"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        executable_files = []
        for line in result.stdout.strip().split("\n"):
            if line.startswith("100755"):  # Executable
                parts = line.split()
                if len(parts) >= 4:
                    executable_files.append(parts[3])

        return {
            "executable_count": str(len(executable_files)),
            "executable_files": "\n".join(executable_files[:20]),
            "has_executables": "true" if executable_files else "false",
        }
    except Exception as e:
        return {
            "executable_count": "0",
            "executable_files": str(e),
            "has_executables": "false",
        }


@strands_tool
def check_signed_tags(repo_path: str) -> dict[str, str]:
    """Check if tags are GPG signed."""
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        tags_result = subprocess.run(
            ["git", "tag"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        tags = [t for t in tags_result.stdout.strip().split("\n") if t]
        signed_count = 0

        for tag in tags:
            verify_result = subprocess.run(
                ["git", "verify-tag", tag],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if verify_result.returncode == 0:
                signed_count += 1

        return {
            "total_tags": str(len(tags)),
            "signed_tags": str(signed_count),
            "unsigned_tags": str(len(tags) - signed_count),
            "all_signed": "true"
            if signed_count == len(tags) and len(tags) > 0
            else "false",
        }
    except Exception:
        return {
            "total_tags": "0",
            "signed_tags": "0",
            "unsigned_tags": "0",
            "all_signed": "false",
        }


@strands_tool
def detect_security_issues(repo_path: str) -> dict[str, str]:
    """Comprehensive security issue detection."""
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    issues = []
    score = 100

    # Check various security aspects
    config_file = repo / ".git" / "config"
    if config_file.exists():
        with open(config_file) as f:
            content = f.read()
            if "http://" in content:
                issues.append("Insecure HTTP URLs in config")
                score -= 20

    gitignore = repo / ".gitignore"
    if not gitignore.exists():
        issues.append("No .gitignore file")
        score -= 10

    return {
        "security_score": str(max(0, score)),
        "issues_count": str(len(issues)),
        "issues": "\n".join(issues) if issues else "No issues found",
        "risk_level": "high" if score < 50 else "medium" if score < 80 else "low",
    }


@strands_tool
def audit_commit_authors(repo_path: str) -> dict[str, str]:
    """Audit commit authors for suspicious patterns."""
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        result = subprocess.run(
            ["git", "log", "--format=%an|%ae", "--max-count=100"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        authors: dict[str, int] = {}
        suspicious = []

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|")
            if len(parts) == 2:
                name, email = parts
                key = f"{name} <{email}>"
                authors[key] = authors.get(key, 0) + 1

                # Check for suspicious patterns
                if not email or "@" not in email:
                    suspicious.append(f"Invalid email: {key}")
                elif "noreply" in email:
                    suspicious.append(f"No-reply email: {key}")

        return {
            "unique_authors": str(len(authors)),
            "suspicious_count": str(len(suspicious)),
            "suspicious_authors": "\n".join(suspicious[:10]) if suspicious else "",
            "has_issues": "true" if suspicious else "false",
        }
    except Exception as e:
        return {
            "unique_authors": "0",
            "suspicious_count": "0",
            "suspicious_authors": str(e),
            "has_issues": "false",
        }
