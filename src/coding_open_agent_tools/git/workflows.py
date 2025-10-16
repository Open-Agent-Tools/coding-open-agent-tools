"""Git workflow validation and analysis tools.

This module provides functions for validating git workflows like gitflow,
trunk-based development, and branch naming conventions.
"""

import re
import subprocess
from pathlib import Path

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def validate_gitflow_workflow(repo_path: str) -> dict[str, str]:
    """Validate repository follows gitflow workflow conventions.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - is_gitflow: "true" if follows gitflow
        - has_main: "true" if main/master branch exists
        - has_develop: "true" if develop branch exists
        - branch_violations: Newline-separated list of non-gitflow branches
        - compliance_score: Score 0-100 for gitflow compliance

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
            ["git", "branch", "-a"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return {
                "is_gitflow": "false",
                "has_main": "false",
                "has_develop": "false",
                "branch_violations": "Could not list branches",
                "compliance_score": "0",
            }

        branches = [
            b.strip().replace("* ", "") for b in result.stdout.split("\n") if b.strip()
        ]

        # Check for main branches
        has_main = any(b in ("main", "master") for b in branches)
        has_develop = any("develop" in b for b in branches)

        # Check for gitflow pattern branches
        gitflow_patterns = [
            r"^(main|master)$",
            r"^develop$",
            r"^feature/",
            r"^release/",
            r"^hotfix/",
            r"^bugfix/",
            r"^remotes/",
        ]

        violations = []
        for branch in branches:
            if not any(re.match(pattern, branch) for pattern in gitflow_patterns):
                violations.append(branch)

        # Calculate compliance score
        score = 0
        if has_main:
            score += 40
        if has_develop:
            score += 40
        if len(violations) == 0:
            score += 20

        is_gitflow = has_main and has_develop and len(violations) < 3

        return {
            "is_gitflow": "true" if is_gitflow else "false",
            "has_main": "true" if has_main else "false",
            "has_develop": "true" if has_develop else "false",
            "branch_violations": "\n".join(violations[:10]) if violations else "",
            "compliance_score": str(score),
        }
    except Exception as e:
        return {
            "is_gitflow": "false",
            "has_main": "false",
            "has_develop": "false",
            "branch_violations": str(e),
            "compliance_score": "0",
        }


@strands_tool
def validate_trunk_based_workflow(repo_path: str) -> dict[str, str]:
    """Validate repository follows trunk-based development.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - is_trunk_based: "true" if follows trunk-based development
        - main_branch: Name of main branch
        - short_lived_branches: Number of branches
        - long_lived_branches: Number of long-lived branches
        - compliance_score: Score 0-100 for trunk-based compliance

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
        # Get all branches
        branches_result = subprocess.run(
            ["git", "branch", "-a", "--format=%(refname:short)"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if branches_result.returncode != 0:
            return {
                "is_trunk_based": "false",
                "main_branch": "",
                "short_lived_branches": "0",
                "long_lived_branches": "0",
                "compliance_score": "0",
            }

        branches = [
            b
            for b in branches_result.stdout.strip().split("\n")
            if b and not b.startswith("remotes/")
        ]

        # Identify main branch
        main_branch = ""
        if "main" in branches:
            main_branch = "main"
        elif "master" in branches:
            main_branch = "master"

        # Count long-lived branches (common in non-trunk-based workflows)
        long_lived_patterns = ["develop", "release/", "staging", "production"]
        long_lived = sum(
            1 for b in branches if any(pattern in b for pattern in long_lived_patterns)
        )

        # Calculate short-lived branches
        short_lived = len(branches) - long_lived - (1 if main_branch else 0)

        # Calculate compliance score
        score = 0
        if main_branch:
            score += 40
        if long_lived == 0:
            score += 40  # No long-lived branches is good
        if short_lived <= 10:
            score += 20  # Few feature branches

        is_trunk_based = bool(main_branch) and long_lived == 0 and short_lived <= 10

        return {
            "is_trunk_based": "true" if is_trunk_based else "false",
            "main_branch": main_branch,
            "short_lived_branches": str(short_lived),
            "long_lived_branches": str(long_lived),
            "compliance_score": str(score),
        }
    except Exception as e:
        return {
            "is_trunk_based": "false",
            "main_branch": "",
            "short_lived_branches": "0",
            "long_lived_branches": "0",
            "compliance_score": str(e)[:3] if str(e)[:3].isdigit() else "0",
        }


@strands_tool
def validate_branch_naming(repo_path: str, pattern: str) -> dict[str, str]:
    """Validate branch names against a pattern.

    Args:
        repo_path: Path to git repository
        pattern: Regex pattern for valid branch names

    Returns:
        Dictionary with:
        - all_valid: "true" if all branches match pattern
        - total_branches: Total number of branches
        - invalid_count: Number of invalid branches
        - invalid_branches: Newline-separated list of invalid branches
        - compliance_percentage: Percentage of compliant branches

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty or pattern is invalid
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(pattern, str):
        raise TypeError("pattern must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not pattern.strip():
        raise ValueError("pattern cannot be empty")

    # Validate regex pattern
    try:
        re.compile(pattern)
    except re.error:
        raise ValueError("pattern must be a valid regex")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        result = subprocess.run(
            ["git", "branch", "--format=%(refname:short)"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return {
                "all_valid": "false",
                "total_branches": "0",
                "invalid_count": "0",
                "invalid_branches": "Could not list branches",
                "compliance_percentage": "0",
            }

        branches = [b for b in result.stdout.strip().split("\n") if b]
        invalid = []

        for branch in branches:
            if not re.match(pattern, branch):
                invalid.append(branch)

        compliance = (
            0
            if not branches
            else int((len(branches) - len(invalid)) / len(branches) * 100)
        )

        return {
            "all_valid": "true" if len(invalid) == 0 else "false",
            "total_branches": str(len(branches)),
            "invalid_count": str(len(invalid)),
            "invalid_branches": "\n".join(invalid) if invalid else "",
            "compliance_percentage": str(compliance),
        }
    except Exception as e:
        return {
            "all_valid": "false",
            "total_branches": "0",
            "invalid_count": "0",
            "invalid_branches": str(e),
            "compliance_percentage": "0",
        }


@strands_tool
def check_protected_branches(repo_path: str) -> dict[str, str]:
    """Check for protected branch configurations.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - has_protections: "true" if protections configured
        - protected_branches: Newline-separated list of protected branches
        - protection_count: Number of protected branches
        - recommendation: Security recommendations

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
        # Check for receive.denyDeletes config
        delete_result = subprocess.run(
            ["git", "config", "receive.denyDeletes"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Check for receive.denyNonFastForwards
        ff_result = subprocess.run(
            ["git", "config", "receive.denyNonFastForwards"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )

        protections = []
        if delete_result.returncode == 0 and delete_result.stdout.strip() == "true":
            protections.append("Branch deletion prevented")

        if ff_result.returncode == 0 and ff_result.stdout.strip() == "true":
            protections.append("Force push prevented")

        # Check for branch-specific protections in config
        config_result = subprocess.run(
            ["git", "config", "--get-regexp", "branch\\..*\\.pushRemote"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if config_result.returncode == 0:
            for line in config_result.stdout.strip().split("\n"):
                if line:
                    protections.append(f"Protected: {line}")

        recommendations = []
        if not protections:
            recommendations.append("Consider enabling branch protections")
            recommendations.append(
                "Set receive.denyNonFastForwards=true for main branch"
            )

        return {
            "has_protections": "true" if protections else "false",
            "protected_branches": "\n".join(protections) if protections else "",
            "protection_count": str(len(protections)),
            "recommendation": "\n".join(recommendations)
            if recommendations
            else "Branch protections configured",
        }
    except Exception as e:
        return {
            "has_protections": "false",
            "protected_branches": str(e),
            "protection_count": "0",
            "recommendation": "Error checking protections",
        }


@strands_tool
def analyze_merge_strategy(repo_path: str, branch_name: str) -> dict[str, str]:
    """Analyze merge strategy used in branch.

    Args:
        repo_path: Path to git repository
        branch_name: Branch to analyze

    Returns:
        Dictionary with:
        - merge_commits: Number of merge commits
        - rebase_commits: Number of rebased commits
        - squash_merges: Number of squash merges
        - dominant_strategy: "merge", "rebase", or "squash"
        - recommendation: Best practice recommendation

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
        # Get commit log
        result = subprocess.run(
            ["git", "log", branch_name, "--oneline", "--max-count=100"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "merge_commits": "0",
                "rebase_commits": "0",
                "squash_merges": "0",
                "dominant_strategy": "unknown",
                "recommendation": "Could not analyze branch",
            }

        commits = result.stdout.strip().split("\n")

        merge_count = 0
        rebase_count = 0
        squash_count = 0

        for commit in commits:
            if "merge" in commit.lower():
                if "pull request" in commit.lower() or "squashed" in commit.lower():
                    squash_count += 1
                else:
                    merge_count += 1
            # Simple heuristic: linear history suggests rebase
            elif len(commits) > 20 and merge_count == 0:
                rebase_count += 1

        # Determine dominant strategy
        if merge_count > rebase_count and merge_count > squash_count:
            dominant = "merge"
            recommendation = "Using merge commits - consider squash for cleaner history"
        elif squash_count > merge_count and squash_count > rebase_count:
            dominant = "squash"
            recommendation = "Using squash merges - good for clean history"
        elif rebase_count > 0:
            dominant = "rebase"
            recommendation = "Using rebase - good for linear history"
        else:
            dominant = "unknown"
            recommendation = "Unable to determine strategy from recent commits"

        return {
            "merge_commits": str(merge_count),
            "rebase_commits": str(rebase_count),
            "squash_merges": str(squash_count),
            "dominant_strategy": dominant,
            "recommendation": recommendation,
        }
    except Exception as e:
        return {
            "merge_commits": "0",
            "rebase_commits": "0",
            "squash_merges": "0",
            "dominant_strategy": "unknown",
            "recommendation": str(e),
        }


@strands_tool
def validate_commit_frequency(
    repo_path: str, branch_name: str, days: str
) -> dict[str, str]:
    """Validate commit frequency meets workflow standards.

    Args:
        repo_path: Path to git repository
        branch_name: Branch to analyze
        days: Number of days to analyze

    Returns:
        Dictionary with:
        - total_commits: Number of commits in period
        - commits_per_day: Average commits per day
        - is_active: "true" if branch is actively developed
        - recommendation: Development pace recommendation

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty or days is invalid
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(branch_name, str):
        raise TypeError("branch_name must be a string")
    if not isinstance(days, str):
        raise TypeError("days must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not branch_name.strip():
        raise ValueError("branch_name cannot be empty")

    try:
        days_int = int(days)
        if days_int <= 0:
            raise ValueError("days must be positive")
    except ValueError:
        raise ValueError("days must be a valid positive integer")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        result = subprocess.run(
            ["git", "log", branch_name, f"--since={days_int}.days.ago", "--oneline"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "total_commits": "0",
                "commits_per_day": "0.0",
                "is_active": "false",
                "recommendation": "Could not analyze branch",
            }

        commits = [c for c in result.stdout.strip().split("\n") if c]
        total = len(commits)
        per_day = total / days_int if days_int > 0 else 0

        # Determine if active (at least 0.5 commits per day on average)
        is_active = per_day >= 0.5

        if per_day >= 2:
            recommendation = "High activity - ensure code quality is maintained"
        elif per_day >= 0.5:
            recommendation = "Good activity level"
        else:
            recommendation = "Low activity - branch may be stale"

        return {
            "total_commits": str(total),
            "commits_per_day": f"{per_day:.2f}",
            "is_active": "true" if is_active else "false",
            "recommendation": recommendation,
        }
    except Exception as e:
        return {
            "total_commits": "0",
            "commits_per_day": "0.0",
            "is_active": "false",
            "recommendation": str(e),
        }
