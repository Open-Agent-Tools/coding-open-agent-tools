"""Git remote repository analysis tools.

This module provides functions for analyzing remote repositories,
checking connectivity, and validating remote configurations.
"""

import subprocess
from pathlib import Path

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def list_remotes(repo_path: str) -> dict[str, str]:
    """List all remote repositories configured.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - has_remotes: "true" if remotes configured
        - remote_count: Number of remotes
        - remotes: Newline-separated list of remote names and URLs
        - primary_remote: Name of primary remote (usually origin)

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
            ["git", "remote", "-v"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return {
                "has_remotes": "false",
                "remote_count": "0",
                "remotes": "Could not list remotes",
                "primary_remote": "",
            }

        lines = [line for line in result.stdout.strip().split("\n") if line]

        # Parse remotes (format: name URL (fetch|push))
        remotes_dict = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                url = parts[1]
                if name not in remotes_dict:
                    remotes_dict[name] = url

        remotes_list = [f"{name}: {url}" for name, url in remotes_dict.items()]

        # Determine primary remote
        primary = (
            "origin"
            if "origin" in remotes_dict
            else (list(remotes_dict.keys())[0] if remotes_dict else "")
        )

        return {
            "has_remotes": "true" if remotes_dict else "false",
            "remote_count": str(len(remotes_dict)),
            "remotes": "\n".join(remotes_list) if remotes_list else "",
            "primary_remote": primary,
        }
    except Exception as e:
        return {
            "has_remotes": "false",
            "remote_count": "0",
            "remotes": str(e),
            "primary_remote": "",
        }


@strands_tool
def check_remote_connectivity(repo_path: str, remote_name: str) -> dict[str, str]:
    """Check connectivity to a remote repository.

    Args:
        repo_path: Path to git repository
        remote_name: Name of remote to check

    Returns:
        Dictionary with:
        - is_reachable: "true" if remote is reachable
        - remote_url: URL of the remote
        - connection_time_ms: Connection time in milliseconds
        - error_message: Error message if unreachable

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(remote_name, str):
        raise TypeError("remote_name must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not remote_name.strip():
        raise ValueError("remote_name cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        # Get remote URL
        url_result = subprocess.run(
            ["git", "remote", "get-url", remote_name],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if url_result.returncode != 0:
            return {
                "is_reachable": "false",
                "remote_url": "",
                "connection_time_ms": "0",
                "error_message": f"Remote '{remote_name}' not found",
            }

        remote_url = url_result.stdout.strip()

        # Test connectivity with ls-remote
        import time

        start_time = time.time()

        ls_result = subprocess.run(
            ["git", "ls-remote", "--heads", remote_name],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        if ls_result.returncode == 0:
            return {
                "is_reachable": "true",
                "remote_url": remote_url,
                "connection_time_ms": str(elapsed_ms),
                "error_message": "",
            }
        else:
            error_msg = (
                ls_result.stderr.strip() if ls_result.stderr else "Connection failed"
            )
            return {
                "is_reachable": "false",
                "remote_url": remote_url,
                "connection_time_ms": str(elapsed_ms),
                "error_message": error_msg[:200],  # Truncate long errors
            }
    except subprocess.TimeoutExpired:
        return {
            "is_reachable": "false",
            "remote_url": remote_url if "remote_url" in locals() else "",
            "connection_time_ms": "30000",
            "error_message": "Connection timeout after 30s",
        }
    except Exception as e:
        return {
            "is_reachable": "false",
            "remote_url": "",
            "connection_time_ms": "0",
            "error_message": str(e)[:200],
        }


@strands_tool
def analyze_remote_branches(repo_path: str, remote_name: str) -> dict[str, str]:
    """Analyze branches on a remote repository.

    Args:
        repo_path: Path to git repository
        remote_name: Name of remote to analyze

    Returns:
        Dictionary with:
        - branch_count: Number of remote branches
        - branches: Newline-separated list of branch names
        - default_branch: Name of default branch
        - has_main: "true" if main/master branch exists

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(remote_name, str):
        raise TypeError("remote_name must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not remote_name.strip():
        raise ValueError("remote_name cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", remote_name],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "branch_count": "0",
                "branches": "Could not fetch remote branches",
                "default_branch": "",
                "has_main": "false",
            }

        lines = [line for line in result.stdout.strip().split("\n") if line]

        # Parse branch names (format: hash refs/heads/branch-name)
        branches = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 2 and "refs/heads/" in parts[1]:
                branch_name = parts[1].replace("refs/heads/", "")
                branches.append(branch_name)

        # Determine default branch
        has_main = "main" in branches
        has_master = "master" in branches
        default_branch = (
            "main"
            if has_main
            else ("master" if has_master else (branches[0] if branches else ""))
        )

        return {
            "branch_count": str(len(branches)),
            "branches": "\n".join(branches[:50])
            if branches
            else "",  # Limit to 50 branches
            "default_branch": default_branch,
            "has_main": "true" if (has_main or has_master) else "false",
        }
    except Exception as e:
        return {
            "branch_count": "0",
            "branches": str(e),
            "default_branch": "",
            "has_main": "false",
        }


@strands_tool
def check_remote_sync_status(repo_path: str, branch_name: str) -> dict[str, str]:
    """Check if local branch is in sync with remote.

    Args:
        repo_path: Path to git repository
        branch_name: Local branch to check

    Returns:
        Dictionary with:
        - is_synced: "true" if in sync with remote
        - commits_ahead: Number of commits ahead of remote
        - commits_behind: Number of commits behind remote
        - recommendation: Sync recommendation

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
        # Fetch remote updates
        subprocess.run(
            ["git", "fetch"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Check commits ahead/behind
        result = subprocess.run(
            [
                "git",
                "rev-list",
                "--left-right",
                "--count",
                f"{branch_name}...origin/{branch_name}",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return {
                "is_synced": "unknown",
                "commits_ahead": "0",
                "commits_behind": "0",
                "recommendation": f"Branch '{branch_name}' may not have a remote tracking branch",
            }

        parts = result.stdout.strip().split()
        if len(parts) != 2:
            return {
                "is_synced": "unknown",
                "commits_ahead": "0",
                "commits_behind": "0",
                "recommendation": "Could not parse sync status",
            }

        ahead = int(parts[0])
        behind = int(parts[1])

        is_synced = ahead == 0 and behind == 0

        if is_synced:
            recommendation = "Branch is in sync with remote"
        elif ahead > 0 and behind == 0:
            recommendation = f"Push {ahead} commit(s) to remote"
        elif ahead == 0 and behind > 0:
            recommendation = f"Pull {behind} commit(s) from remote"
        else:
            recommendation = (
                f"Diverged: {ahead} ahead, {behind} behind - may need rebase or merge"
            )

        return {
            "is_synced": "true" if is_synced else "false",
            "commits_ahead": str(ahead),
            "commits_behind": str(behind),
            "recommendation": recommendation,
        }
    except Exception as e:
        return {
            "is_synced": "false",
            "commits_ahead": "0",
            "commits_behind": "0",
            "recommendation": str(e)[:200],
        }


@strands_tool
def validate_remote_url_security(repo_path: str) -> dict[str, str]:
    """Validate remote URLs for security issues.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - all_secure: "true" if all URLs are secure
        - insecure_count: Number of insecure URLs
        - insecure_remotes: Newline-separated list of insecure remotes
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

    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return {
                "all_secure": "true",
                "insecure_count": "0",
                "insecure_remotes": "",
                "recommendations": "No remotes configured",
            }

        lines = [line for line in result.stdout.strip().split("\n") if line]

        insecure = []
        checked_remotes = set()

        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                url = parts[1]

                # Only check each remote once
                if name in checked_remotes:
                    continue
                checked_remotes.add(name)

                # Check for security issues
                if url.startswith("http://"):
                    insecure.append(f"{name}: HTTP (unencrypted) - {url}")
                elif url.startswith("git://"):
                    insecure.append(f"{name}: git:// protocol (deprecated) - {url}")
                elif "@" in url and ":" in url and not url.startswith("ssh://"):
                    # SSH URLs like git@github.com:user/repo.git are secure
                    pass

        recommendations = []
        if insecure:
            recommendations.append("Replace HTTP URLs with HTTPS")
            recommendations.append("Replace git:// URLs with https:// or ssh://")
            recommendations.append(
                "Use 'git remote set-url <name> <new-url>' to update"
            )

        return {
            "all_secure": "false" if insecure else "true",
            "insecure_count": str(len(insecure)),
            "insecure_remotes": "\n".join(insecure) if insecure else "",
            "recommendations": "\n".join(recommendations)
            if recommendations
            else "All remote URLs are secure",
        }
    except Exception as e:
        return {
            "all_secure": "false",
            "insecure_count": "0",
            "insecure_remotes": str(e),
            "recommendations": "Error validating URLs",
        }
