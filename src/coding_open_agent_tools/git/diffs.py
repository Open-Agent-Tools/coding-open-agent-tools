"""Git diff analysis and change inspection tools.

This module provides functions for analyzing git diffs, calculating
code churn, and understanding change patterns.
"""

import subprocess
from pathlib import Path

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def analyze_diff_stats(repo_path: str, ref1: str, ref2: str) -> dict[str, str]:
    """Analyze statistics of diff between two refs.

    Args:
        repo_path: Path to git repository
        ref1: First reference (commit, branch, tag)
        ref2: Second reference (commit, branch, tag)

    Returns:
        Dictionary with:
        - files_changed: Number of files changed
        - insertions: Total lines inserted
        - deletions: Total lines deleted
        - net_change: Net change in lines (insertions - deletions)
        - summary: Human-readable summary

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(ref1, str):
        raise TypeError("ref1 must be a string")
    if not isinstance(ref2, str):
        raise TypeError("ref2 must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not ref1.strip():
        raise ValueError("ref1 cannot be empty")
    if not ref2.strip():
        raise ValueError("ref2 cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        result = subprocess.run(
            ["git", "diff", "--shortstat", ref1, ref2],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "files_changed": "0",
                "insertions": "0",
                "deletions": "0",
                "net_change": "0",
                "summary": f"Could not compare {ref1} and {ref2}",
            }

        output = result.stdout.strip()

        if not output:
            return {
                "files_changed": "0",
                "insertions": "0",
                "deletions": "0",
                "net_change": "0",
                "summary": "No differences found",
            }

        # Parse output like: "5 files changed, 120 insertions(+), 45 deletions(-)"
        files_changed = 0
        insertions = 0
        deletions = 0

        parts = output.split(",")
        for part in parts:
            part = part.strip()
            if "file" in part:
                files_changed = int(part.split()[0])
            elif "insertion" in part:
                insertions = int(part.split()[0])
            elif "deletion" in part:
                deletions = int(part.split()[0])

        net_change = insertions - deletions

        summary = f"{files_changed} file(s), +{insertions}/-{deletions} lines"

        return {
            "files_changed": str(files_changed),
            "insertions": str(insertions),
            "deletions": str(deletions),
            "net_change": str(net_change),
            "summary": summary,
        }
    except Exception as e:
        return {
            "files_changed": "0",
            "insertions": "0",
            "deletions": "0",
            "net_change": "0",
            "summary": str(e)[:200],
        }


@strands_tool
def calculate_code_churn(repo_path: str, file_path: str, days: str) -> dict[str, str]:
    """Calculate code churn for a specific file.

    Code churn is the number of times lines have been added/modified/deleted.

    Args:
        repo_path: Path to git repository
        file_path: Path to file relative to repo root
        days: Number of days to analyze

    Returns:
        Dictionary with:
        - total_commits: Number of commits affecting file
        - total_changes: Total line changes (additions + deletions)
        - churn_rate: Average changes per commit
        - stability: "stable", "moderate", or "high_churn"
        - recommendation: Code health recommendation

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty or days is invalid
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(days, str):
        raise TypeError("days must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not file_path.strip():
        raise ValueError("file_path cannot be empty")

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
        # Get commit count for file
        count_result = subprocess.run(
            [
                "git",
                "log",
                f"--since={days_int}.days.ago",
                "--oneline",
                "--",
                file_path,
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if count_result.returncode != 0:
            return {
                "total_commits": "0",
                "total_changes": "0",
                "churn_rate": "0.0",
                "stability": "unknown",
                "recommendation": f"Could not analyze {file_path}",
            }

        commits = [c for c in count_result.stdout.strip().split("\n") if c]
        total_commits = len(commits)

        if total_commits == 0:
            return {
                "total_commits": "0",
                "total_changes": "0",
                "churn_rate": "0.0",
                "stability": "stable",
                "recommendation": "No changes in specified period",
            }

        # Get total changes
        stats_result = subprocess.run(
            [
                "git",
                "log",
                f"--since={days_int}.days.ago",
                "--numstat",
                "--",
                file_path,
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        total_changes = 0
        for line in stats_result.stdout.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                total_changes += int(parts[0]) + int(parts[1])  # additions + deletions

        churn_rate = total_changes / total_commits if total_commits > 0 else 0

        # Determine stability
        if churn_rate < 50:
            stability = "stable"
            recommendation = "File shows good stability"
        elif churn_rate < 200:
            stability = "moderate"
            recommendation = "Moderate churn - monitor for code quality"
        else:
            stability = "high_churn"
            recommendation = "High churn detected - consider refactoring or stabilizing"

        return {
            "total_commits": str(total_commits),
            "total_changes": str(total_changes),
            "churn_rate": f"{churn_rate:.2f}",
            "stability": stability,
            "recommendation": recommendation,
        }
    except Exception as e:
        return {
            "total_commits": "0",
            "total_changes": "0",
            "churn_rate": "0.0",
            "stability": "unknown",
            "recommendation": str(e)[:200],
        }


@strands_tool
def get_file_diff(
    repo_path: str, ref1: str, ref2: str, file_path: str
) -> dict[str, str]:
    """Get diff for a specific file between two refs.

    Args:
        repo_path: Path to git repository
        ref1: First reference (commit, branch, tag)
        ref2: Second reference (commit, branch, tag)
        file_path: Path to file relative to repo root

    Returns:
        Dictionary with:
        - has_changes: "true" if file changed between refs
        - lines_added: Number of lines added
        - lines_removed: Number of lines removed
        - diff_summary: Summary of changes
        - diff_preview: First 50 lines of diff

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(ref1, str):
        raise TypeError("ref1 must be a string")
    if not isinstance(ref2, str):
        raise TypeError("ref2 must be a string")
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not ref1.strip():
        raise ValueError("ref1 cannot be empty")
    if not ref2.strip():
        raise ValueError("ref2 cannot be empty")
    if not file_path.strip():
        raise ValueError("file_path cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        # Get diff
        result = subprocess.run(
            ["git", "diff", ref1, ref2, "--", file_path],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "has_changes": "false",
                "lines_added": "0",
                "lines_removed": "0",
                "diff_summary": f"Could not get diff for {file_path}",
                "diff_preview": "",
            }

        diff_output = result.stdout

        if not diff_output.strip():
            return {
                "has_changes": "false",
                "lines_added": "0",
                "lines_removed": "0",
                "diff_summary": "No changes",
                "diff_preview": "",
            }

        # Count additions and deletions
        lines_added = sum(
            1
            for line in diff_output.split("\n")
            if line.startswith("+") and not line.startswith("+++")
        )
        lines_removed = sum(
            1
            for line in diff_output.split("\n")
            if line.startswith("-") and not line.startswith("---")
        )

        # Get preview (first 50 lines)
        diff_lines = diff_output.split("\n")
        preview = "\n".join(diff_lines[:50])

        summary = f"+{lines_added}/-{lines_removed} lines in {file_path}"

        return {
            "has_changes": "true",
            "lines_added": str(lines_added),
            "lines_removed": str(lines_removed),
            "diff_summary": summary,
            "diff_preview": preview,
        }
    except Exception as e:
        return {
            "has_changes": "false",
            "lines_added": "0",
            "lines_removed": "0",
            "diff_summary": str(e)[:200],
            "diff_preview": "",
        }


@strands_tool
def find_largest_changes(
    repo_path: str, ref1: str, ref2: str, limit: str
) -> dict[str, str]:
    """Find files with largest changes between two refs.

    Args:
        repo_path: Path to git repository
        ref1: First reference (commit, branch, tag)
        ref2: Second reference (commit, branch, tag)
        limit: Maximum number of files to return

    Returns:
        Dictionary with:
        - total_files_changed: Total number of files changed
        - largest_changes: Newline-separated list of files with change counts
        - summary: Overall summary of changes

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty or limit is invalid
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(ref1, str):
        raise TypeError("ref1 must be a string")
    if not isinstance(ref2, str):
        raise TypeError("ref2 must be a string")
    if not isinstance(limit, str):
        raise TypeError("limit must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not ref1.strip():
        raise ValueError("ref1 cannot be empty")
    if not ref2.strip():
        raise ValueError("ref2 cannot be empty")

    try:
        limit_int = int(limit)
        if limit_int <= 0:
            raise ValueError("limit must be positive")
    except ValueError:
        raise ValueError("limit must be a valid positive integer")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        result = subprocess.run(
            ["git", "diff", "--numstat", ref1, ref2],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "total_files_changed": "0",
                "largest_changes": f"Could not compare {ref1} and {ref2}",
                "summary": "Error",
            }

        # Parse numstat output (format: additions deletions filename)
        file_changes = []
        total_files = 0

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            parts = line.split(None, 2)
            if len(parts) >= 3:
                try:
                    additions = int(parts[0]) if parts[0] != "-" else 0
                    deletions = int(parts[1]) if parts[1] != "-" else 0
                    filename = parts[2]
                    total_changes = additions + deletions
                    file_changes.append((total_changes, additions, deletions, filename))
                    total_files += 1
                except ValueError:
                    continue

        # Sort by total changes (descending)
        file_changes.sort(reverse=True)

        # Get top N files
        largest = file_changes[:limit_int]
        largest_list = [
            f"{filename} (+{adds}/-{dels}, {total} total)"
            for total, adds, dels, filename in largest
        ]

        total_changes = sum(total for total, _, _, _ in file_changes)
        summary = f"{total_files} file(s) changed, {total_changes} total line changes"

        return {
            "total_files_changed": str(total_files),
            "largest_changes": "\n".join(largest_list) if largest_list else "",
            "summary": summary,
        }
    except Exception as e:
        return {
            "total_files_changed": "0",
            "largest_changes": str(e)[:200],
            "summary": "Error analyzing changes",
        }
