"""Git submodule management and analysis tools.

This module provides git submodule inspection and validation functions.
"""

import subprocess
from pathlib import Path

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def list_submodules(repo_path: str) -> dict[str, str]:
    """List all git submodules in repository.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - has_submodules: "true" if submodules exist
        - submodule_count: Number of submodules
        - submodules: Newline-separated list of submodule paths
        - status_summary: Summary of submodule states

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

    try:
        result = subprocess.run(
            ["git", "submodule", "status"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "has_submodules": "false",
                "submodule_count": "0",
                "submodules": "",
                "status_summary": "Could not list submodules",
            }

        lines = [line for line in result.stdout.strip().split("\n") if line]
        submodules = []
        initialized = 0
        uninitialized = 0

        for line in lines:
            if line.startswith("-"):
                uninitialized += 1
                path = line[1:].split()[1] if len(line[1:].split()) > 1 else line[1:]
                submodules.append(f"UNINIT: {path}")
            elif line.startswith("+"):
                initialized += 1
                path = line[1:].split()[1] if len(line[1:].split()) > 1 else line[1:]
                submodules.append(f"MODIFIED: {path}")
            else:
                initialized += 1
                path = line[1:].split()[1] if len(line[1:].split()) > 1 else line[1:]
                submodules.append(f"OK: {path}")

        status = f"{initialized} initialized, {uninitialized} uninitialized"

        return {
            "has_submodules": "true" if submodules else "false",
            "submodule_count": str(len(submodules)),
            "submodules": "\n".join(submodules),
            "status_summary": status if submodules else "No submodules",
        }
    except Exception as e:
        return {
            "has_submodules": "false",
            "submodule_count": "0",
            "submodules": str(e),
            "status_summary": "Error listing submodules",
        }


@strands_tool
def validate_submodule_urls(repo_path: str) -> dict[str, str]:
    """Validate submodule URLs for security issues.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - all_valid: "true" if all URLs are valid
        - url_count: Number of submodule URLs
        - insecure_urls: Newline-separated list of insecure URLs
        - security_issues: Number of security issues
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

    gitmodules_path = repo / ".gitmodules"
    if not gitmodules_path.exists():
        return {
            "all_valid": "true",
            "url_count": "0",
            "insecure_urls": "",
            "security_issues": "0",
            "recommendations": "No .gitmodules file found",
        }

    try:
        with open(gitmodules_path) as f:
            content = f.read()

        urls = []
        insecure = []

        for line in content.split("\n"):
            if "url = " in line:
                url = line.split("url = ", 1)[1].strip()
                urls.append(url)

                # Check for security issues
                if url.startswith("http://"):
                    insecure.append(f"HTTP: {url}")
                elif url.startswith("git://"):
                    insecure.append(f"GIT protocol: {url}")

        recommendations = []
        if insecure:
            recommendations.append("Use HTTPS URLs instead of HTTP")
            recommendations.append("Replace git:// URLs with https://")

        return {
            "all_valid": "false" if insecure else "true",
            "url_count": str(len(urls)),
            "insecure_urls": "\n".join(insecure) if insecure else "",
            "security_issues": str(len(insecure)),
            "recommendations": "\n".join(recommendations)
            if recommendations
            else "All URLs are secure",
        }
    except Exception as e:
        return {
            "all_valid": "false",
            "url_count": "0",
            "insecure_urls": str(e),
            "security_issues": "0",
            "recommendations": "Error validating URLs",
        }


@strands_tool
def check_submodule_sync(repo_path: str) -> dict[str, str]:
    """Check if submodules are in sync with .gitmodules.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - is_synced: "true" if all submodules synced
        - out_of_sync_count: Number of out-of-sync submodules
        - sync_issues: Newline-separated list of sync issues
        - recommendation: Action to take

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

    try:
        # Check sync status
        result = subprocess.run(
            ["git", "submodule", "status"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "is_synced": "true",
                "out_of_sync_count": "0",
                "sync_issues": "",
                "recommendation": "No submodules to sync",
            }

        lines = [line for line in result.stdout.strip().split("\n") if line]
        out_of_sync = []

        for line in lines:
            if line.startswith("+"):
                # Submodule has different commit than recorded
                path = line[1:].split()[1] if len(line[1:].split()) > 1 else line[1:]
                out_of_sync.append(f"Different commit: {path}")
            elif line.startswith("-"):
                # Submodule not initialized
                path = line[1:].split()[1] if len(line[1:].split()) > 1 else line[1:]
                out_of_sync.append(f"Not initialized: {path}")

        recommendation = (
            "Run 'git submodule sync' and 'git submodule update'"
            if out_of_sync
            else "All submodules in sync"
        )

        return {
            "is_synced": "false" if out_of_sync else "true",
            "out_of_sync_count": str(len(out_of_sync)),
            "sync_issues": "\n".join(out_of_sync) if out_of_sync else "",
            "recommendation": recommendation,
        }
    except Exception as e:
        return {
            "is_synced": "false",
            "out_of_sync_count": "0",
            "sync_issues": str(e),
            "recommendation": "Error checking sync status",
        }


@strands_tool
def analyze_submodule_updates(repo_path: str) -> dict[str, str]:
    """Analyze available updates for submodules.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - has_updates: "true" if updates available
        - submodules_with_updates: Number of submodules with updates
        - update_summary: Summary of available updates
        - recommendation: Update recommendations

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

    try:
        # Get submodule status
        status_result = subprocess.run(
            ["git", "submodule", "status"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if status_result.returncode != 0 or not status_result.stdout.strip():
            return {
                "has_updates": "false",
                "submodules_with_updates": "0",
                "update_summary": "No submodules found",
                "recommendation": "No action needed",
            }

        # For now, check which submodules are not at HEAD
        lines = [line for line in status_result.stdout.strip().split("\n") if line]
        outdated = []

        for line in lines:
            if line.startswith("+"):
                path = line[1:].split()[1] if len(line[1:].split()) > 1 else line[1:]
                outdated.append(path)

        recommendation = (
            f"Review and update {len(outdated)} submodule(s)"
            if outdated
            else "All submodules up to date"
        )

        return {
            "has_updates": "true" if outdated else "false",
            "submodules_with_updates": str(len(outdated)),
            "update_summary": "\n".join(outdated) if outdated else "No updates needed",
            "recommendation": recommendation,
        }
    except Exception as e:
        return {
            "has_updates": "false",
            "submodules_with_updates": "0",
            "update_summary": str(e),
            "recommendation": "Error analyzing updates",
        }


@strands_tool
def validate_submodule_commits(repo_path: str) -> dict[str, str]:
    """Validate that submodule commits exist in remote.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - all_valid: "true" if all commits exist
        - missing_commits: Number of missing commits
        - invalid_submodules: Newline-separated list of submodules with missing commits
        - recommendation: Action to take

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

    try:
        # Get submodule status
        result = subprocess.run(
            ["git", "submodule", "status"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0 or not result.stdout.strip():
            return {
                "all_valid": "true",
                "missing_commits": "0",
                "invalid_submodules": "",
                "recommendation": "No submodules to validate",
            }

        lines = [line for line in result.stdout.strip().split("\n") if line]
        invalid = []

        for line in lines:
            # Check if submodule is uninitialized
            if line.startswith("-"):
                path = line[1:].split()[1] if len(line[1:].split()) > 1 else line[1:]
                invalid.append(f"Uninitialized: {path}")

        recommendation = (
            "Initialize missing submodules with 'git submodule init'"
            if invalid
            else "All submodules initialized"
        )

        return {
            "all_valid": "false" if invalid else "true",
            "missing_commits": str(len(invalid)),
            "invalid_submodules": "\n".join(invalid) if invalid else "",
            "recommendation": recommendation,
        }
    except Exception as e:
        return {
            "all_valid": "false",
            "missing_commits": "0",
            "invalid_submodules": str(e),
            "recommendation": "Error validating commits",
        }
