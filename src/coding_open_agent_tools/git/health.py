"""Git repository health analysis and maintenance tools.

This module provides functions for analyzing repository health, detecting issues,
and providing maintenance recommendations.
"""

import subprocess
from pathlib import Path

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def find_large_files(repo_path: str, size_threshold_mb: str) -> dict[str, str]:
    """Find large files in git repository.

    Args:
        repo_path: Path to git repository
        size_threshold_mb: Size threshold in MB (files larger than this)

    Returns:
        Dictionary with:
        - large_files_count: Number of files exceeding threshold
        - largest_file_size_mb: Size of largest file in MB
        - largest_file_path: Path to largest file
        - files_list: Newline-separated list of large files with sizes
        - total_size_mb: Total size of all large files

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty or invalid
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(size_threshold_mb, str):
        raise TypeError("size_threshold_mb must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not size_threshold_mb.strip():
        raise ValueError("size_threshold_mb cannot be empty")

    try:
        threshold_mb = float(size_threshold_mb)
        if threshold_mb <= 0:
            raise ValueError("size_threshold_mb must be positive")
    except ValueError:
        raise ValueError("size_threshold_mb must be a valid number")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")
    if not (repo / ".git").exists():
        return {
            "large_files_count": "0",
            "largest_file_size_mb": "0",
            "largest_file_path": "",
            "files_list": "",
            "total_size_mb": "0",
        }

    try:
        # Use git ls-files to find tracked files
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "large_files_count": "0",
                "largest_file_size_mb": "0",
                "largest_file_path": "",
                "files_list": "",
                "total_size_mb": "0",
            }

        files = result.stdout.strip().split("\n")
        large_files = []
        largest_size = 0
        largest_path = ""
        total_size = 0.0

        threshold_bytes = threshold_mb * 1024 * 1024

        for file_path in files:
            if not file_path:
                continue

            full_path = repo / file_path
            if full_path.exists() and full_path.is_file():
                size_bytes = full_path.stat().st_size
                if size_bytes > threshold_bytes:
                    size_mb = size_bytes / (1024 * 1024)
                    large_files.append(f"{file_path} ({size_mb:.2f} MB)")
                    total_size += size_mb

                    if size_bytes > largest_size:
                        largest_size = size_bytes
                        largest_path = file_path

        return {
            "large_files_count": str(len(large_files)),
            "largest_file_size_mb": f"{largest_size / (1024 * 1024):.2f}"
            if largest_size > 0
            else "0",
            "largest_file_path": largest_path,
            "files_list": "\n".join(large_files) if large_files else "",
            "total_size_mb": f"{total_size:.2f}",
        }

    except subprocess.TimeoutExpired:
        return {
            "large_files_count": "0",
            "largest_file_size_mb": "0",
            "largest_file_path": "",
            "files_list": "",
            "total_size_mb": "0",
        }
    except Exception as e:
        return {
            "large_files_count": "0",
            "largest_file_size_mb": "0",
            "largest_file_path": "",
            "files_list": str(e),
            "total_size_mb": "0",
        }


@strands_tool
def check_repository_size(repo_path: str) -> dict[str, str]:
    """Check git repository size and provide breakdown.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - total_size_mb: Total repository size in MB
        - git_dir_size_mb: .git directory size in MB
        - working_tree_size_mb: Working tree size in MB
        - objects_count: Number of git objects
        - pack_files_count: Number of pack files

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
    if not (repo / ".git").exists():
        return {
            "total_size_mb": "0",
            "git_dir_size_mb": "0",
            "working_tree_size_mb": "0",
            "objects_count": "0",
            "pack_files_count": "0",
        }

    def get_dir_size(path: Path) -> int:
        """Calculate directory size recursively."""
        total = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
        except Exception:
            pass
        return total

    git_dir = repo / ".git"
    git_size = get_dir_size(git_dir)

    # Count objects
    objects_dir = git_dir / "objects"
    objects_count = 0
    pack_files_count = 0

    if objects_dir.exists():
        try:
            # Count loose objects
            for subdir in objects_dir.iterdir():
                if subdir.is_dir() and len(subdir.name) == 2:
                    objects_count += len(list(subdir.iterdir()))

            # Count pack files
            pack_dir = objects_dir / "pack"
            if pack_dir.exists():
                pack_files_count = len(list(pack_dir.glob("*.pack")))

        except Exception:
            pass

    # Calculate working tree size (excluding .git)
    working_tree_size = 0
    for item in repo.rglob("*"):
        if ".git" not in item.parts and item.is_file():
            try:
                working_tree_size += item.stat().st_size
            except Exception:
                pass

    total_size = git_size + working_tree_size

    return {
        "total_size_mb": f"{total_size / (1024 * 1024):.2f}",
        "git_dir_size_mb": f"{git_size / (1024 * 1024):.2f}",
        "working_tree_size_mb": f"{working_tree_size / (1024 * 1024):.2f}",
        "objects_count": str(objects_count),
        "pack_files_count": str(pack_files_count),
    }


@strands_tool
def analyze_branch_staleness(repo_path: str, days_threshold: str) -> dict[str, str]:
    """Analyze stale branches (not updated recently).

    Args:
        repo_path: Path to git repository
        days_threshold: Number of days to consider a branch stale

    Returns:
        Dictionary with:
        - stale_branches_count: Number of stale branches
        - total_branches: Total number of branches
        - stale_branches: Newline-separated list of stale branches
        - oldest_branch_name: Name of oldest branch
        - oldest_branch_days: Days since oldest branch was updated

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty or invalid
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(days_threshold, str):
        raise TypeError("days_threshold must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not days_threshold.strip():
        raise ValueError("days_threshold cannot be empty")

    try:
        threshold_days = int(days_threshold)
        if threshold_days <= 0:
            raise ValueError("days_threshold must be positive")
    except ValueError:
        raise ValueError("days_threshold must be a valid integer")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")
    if not (repo / ".git").exists():
        return {
            "stale_branches_count": "0",
            "total_branches": "0",
            "stale_branches": "",
            "oldest_branch_name": "",
            "oldest_branch_days": "0",
        }

    try:
        # Get all branches with commit date
        result = subprocess.run(
            [
                "git",
                "for-each-ref",
                "--format=%(refname:short)|%(committerdate:unix)",
                "refs/heads/",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "stale_branches_count": "0",
                "total_branches": "0",
                "stale_branches": "",
                "oldest_branch_name": "",
                "oldest_branch_days": "0",
            }

        import time

        current_time = int(time.time())
        threshold_seconds = threshold_days * 24 * 60 * 60

        branches = []
        stale_branches = []
        oldest_name = ""
        oldest_days = 0

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            parts = line.split("|")
            if len(parts) != 2:
                continue

            branch_name = parts[0]
            commit_time = int(parts[1])
            age_seconds = current_time - commit_time
            age_days = age_seconds // (24 * 60 * 60)

            branches.append(branch_name)

            if age_seconds > threshold_seconds:
                stale_branches.append(f"{branch_name} ({age_days} days old)")

            if age_days > oldest_days:
                oldest_days = age_days
                oldest_name = branch_name

        return {
            "stale_branches_count": str(len(stale_branches)),
            "total_branches": str(len(branches)),
            "stale_branches": "\n".join(stale_branches) if stale_branches else "",
            "oldest_branch_name": oldest_name,
            "oldest_branch_days": str(oldest_days),
        }

    except subprocess.TimeoutExpired:
        return {
            "stale_branches_count": "0",
            "total_branches": "0",
            "stale_branches": "",
            "oldest_branch_name": "",
            "oldest_branch_days": "0",
        }
    except Exception as e:
        return {
            "stale_branches_count": "0",
            "total_branches": "0",
            "stale_branches": str(e),
            "oldest_branch_name": "",
            "oldest_branch_days": "0",
        }


@strands_tool
def check_gc_needed(repo_path: str) -> dict[str, str]:
    """Check if git garbage collection is needed.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - gc_needed: "true" if garbage collection recommended
        - loose_objects: Number of loose objects
        - loose_size_mb: Size of loose objects in MB
        - pack_count: Number of pack files
        - recommendations: Maintenance recommendations

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
    if not (repo / ".git").exists():
        return {
            "gc_needed": "false",
            "loose_objects": "0",
            "loose_size_mb": "0",
            "pack_count": "0",
            "recommendations": "Not a git repository",
        }

    try:
        # Count loose objects
        objects_dir = repo / ".git" / "objects"
        loose_count = 0
        loose_size = 0

        if objects_dir.exists():
            for subdir in objects_dir.iterdir():
                if subdir.is_dir() and len(subdir.name) == 2:
                    for obj_file in subdir.iterdir():
                        if obj_file.is_file():
                            loose_count += 1
                            loose_size += obj_file.stat().st_size

        # Count pack files
        pack_dir = objects_dir / "pack"
        pack_count = 0
        if pack_dir.exists():
            pack_count = len(list(pack_dir.glob("*.pack")))

        # Determine if GC is needed
        gc_needed = False
        recommendations = []

        # Heuristics for GC recommendation
        if loose_count > 6700:  # Git's auto gc threshold
            gc_needed = True
            recommendations.append(f"High number of loose objects ({loose_count})")

        if pack_count > 50:
            gc_needed = True
            recommendations.append(
                f"Many pack files ({pack_count}), consider repacking"
            )

        if loose_size > 50 * 1024 * 1024:  # 50 MB
            gc_needed = True
            recommendations.append(
                f"Loose objects using significant space ({loose_size / (1024 * 1024):.2f} MB)"
            )

        if not gc_needed:
            recommendations.append("Repository is in good shape, no GC needed")

        return {
            "gc_needed": "true" if gc_needed else "false",
            "loose_objects": str(loose_count),
            "loose_size_mb": f"{loose_size / (1024 * 1024):.2f}",
            "pack_count": str(pack_count),
            "recommendations": "\n".join(recommendations),
        }

    except Exception as e:
        return {
            "gc_needed": "false",
            "loose_objects": "0",
            "loose_size_mb": "0",
            "pack_count": "0",
            "recommendations": f"Error analyzing repository: {str(e)}",
        }


@strands_tool
def detect_corrupted_objects(repo_path: str) -> dict[str, str]:
    """Detect corrupted objects in git repository.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - has_corruption: "true" if corruption detected
        - corrupted_count: Number of corrupted objects
        - fsck_output: Output from git fsck
        - error_summary: Summary of errors found
        - is_healthy: "true" if repository is healthy

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
    if not (repo / ".git").exists():
        return {
            "has_corruption": "false",
            "corrupted_count": "0",
            "fsck_output": "",
            "error_summary": "Not a git repository",
            "is_healthy": "false",
        }

    try:
        # Run git fsck
        result = subprocess.run(
            ["git", "fsck", "--no-progress"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=120,  # fsck can take a while
        )

        fsck_output = result.stdout + result.stderr

        # Parse for errors
        errors = []
        for line in fsck_output.split("\n"):
            if "error" in line.lower() or "corrupt" in line.lower():
                errors.append(line.strip())

        has_corruption = result.returncode != 0 or len(errors) > 0

        return {
            "has_corruption": "true" if has_corruption else "false",
            "corrupted_count": str(len(errors)),
            "fsck_output": fsck_output.strip(),
            "error_summary": "\n".join(errors) if errors else "No errors found",
            "is_healthy": "false" if has_corruption else "true",
        }

    except subprocess.TimeoutExpired:
        return {
            "has_corruption": "false",
            "corrupted_count": "0",
            "fsck_output": "",
            "error_summary": "git fsck timed out (may indicate issues)",
            "is_healthy": "false",
        }
    except Exception as e:
        return {
            "has_corruption": "false",
            "corrupted_count": "0",
            "fsck_output": "",
            "error_summary": str(e),
            "is_healthy": "false",
        }


@strands_tool
def analyze_repository_activity(repo_path: str, days: str) -> dict[str, str]:
    """Analyze repository commit activity over time period.

    Args:
        repo_path: Path to git repository
        days: Number of days to analyze

    Returns:
        Dictionary with:
        - total_commits: Total commits in period
        - commits_per_day: Average commits per day
        - active_days: Number of days with commits
        - most_active_day: Date with most commits
        - unique_authors: Number of unique authors

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty or invalid
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(days, str):
        raise TypeError("days must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not days.strip():
        raise ValueError("days cannot be empty")

    try:
        num_days = int(days)
        if num_days <= 0:
            raise ValueError("days must be positive")
    except ValueError:
        raise ValueError("days must be a valid integer")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")
    if not (repo / ".git").exists():
        return {
            "total_commits": "0",
            "commits_per_day": "0",
            "active_days": "0",
            "most_active_day": "",
            "unique_authors": "0",
        }

    try:
        # Get commits from last N days
        result = subprocess.run(
            [
                "git",
                "log",
                f"--since={num_days}.days.ago",
                "--format=%H|%ci|%an",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0 or not result.stdout.strip():
            return {
                "total_commits": "0",
                "commits_per_day": "0",
                "active_days": "0",
                "most_active_day": "",
                "unique_authors": "0",
            }

        commits = result.stdout.strip().split("\n")
        total_commits = len(commits)

        # Track days and authors
        days_set = set()
        authors = set()
        day_counts: dict[str, int] = {}

        for commit in commits:
            parts = commit.split("|")
            if len(parts) != 3:
                continue

            date_str = parts[1].split()[0]  # Extract date part
            author = parts[2]

            days_set.add(date_str)
            authors.add(author)

            day_counts[date_str] = day_counts.get(date_str, 0) + 1

        active_days = len(days_set)
        unique_authors = len(authors)

        # Find most active day
        most_active_day = ""
        max_commits = 0
        for day, count in day_counts.items():
            if count > max_commits:
                max_commits = count
                most_active_day = day

        commits_per_day = total_commits / num_days if num_days > 0 else 0

        return {
            "total_commits": str(total_commits),
            "commits_per_day": f"{commits_per_day:.2f}",
            "active_days": str(active_days),
            "most_active_day": most_active_day,
            "unique_authors": str(unique_authors),
        }

    except subprocess.TimeoutExpired:
        return {
            "total_commits": "0",
            "commits_per_day": "0",
            "active_days": "0",
            "most_active_day": "",
            "unique_authors": "0",
        }
    except Exception as e:
        return {
            "total_commits": "0",
            "commits_per_day": "0",
            "active_days": "0",
            "most_active_day": str(e),
            "unique_authors": "0",
        }


@strands_tool
def check_worktree_clean(repo_path: str) -> dict[str, str]:
    """Check if working tree is clean (no uncommitted changes).

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - is_clean: "true" if no uncommitted changes
        - modified_count: Number of modified files
        - untracked_count: Number of untracked files
        - staged_count: Number of staged files
        - status_summary: Brief status summary

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
    if not (repo / ".git").exists():
        return {
            "is_clean": "false",
            "modified_count": "0",
            "untracked_count": "0",
            "staged_count": "0",
            "status_summary": "Not a git repository",
        }

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "is_clean": "false",
                "modified_count": "0",
                "untracked_count": "0",
                "staged_count": "0",
                "status_summary": "Error checking status",
            }

        if not result.stdout.strip():
            return {
                "is_clean": "true",
                "modified_count": "0",
                "untracked_count": "0",
                "staged_count": "0",
                "status_summary": "Working tree clean",
            }

        # Parse porcelain format
        modified = 0
        untracked = 0
        staged = 0

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            status_code = line[:2]

            # Staged files (first char)
            if status_code[0] in ["A", "M", "D", "R", "C"]:
                staged += 1

            # Modified files (second char)
            if status_code[1] in ["M", "D"]:
                modified += 1

            # Untracked files
            if status_code.startswith("??"):
                untracked += 1

        is_clean = modified == 0 and untracked == 0 and staged == 0

        summary_parts = []
        if staged > 0:
            summary_parts.append(f"{staged} staged")
        if modified > 0:
            summary_parts.append(f"{modified} modified")
        if untracked > 0:
            summary_parts.append(f"{untracked} untracked")

        status_summary = ", ".join(summary_parts) if summary_parts else "Clean"

        return {
            "is_clean": "true" if is_clean else "false",
            "modified_count": str(modified),
            "untracked_count": str(untracked),
            "staged_count": str(staged),
            "status_summary": status_summary,
        }

    except subprocess.TimeoutExpired:
        return {
            "is_clean": "false",
            "modified_count": "0",
            "untracked_count": "0",
            "staged_count": "0",
            "status_summary": "Status check timed out",
        }
    except Exception as e:
        return {
            "is_clean": "false",
            "modified_count": "0",
            "untracked_count": "0",
            "staged_count": "0",
            "status_summary": str(e),
        }


@strands_tool
def get_repository_metrics(repo_path: str) -> dict[str, str]:
    """Get comprehensive repository health metrics.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - total_commits: Total number of commits
        - total_branches: Total number of branches
        - total_tags: Total number of tags
        - total_contributors: Number of unique contributors
        - repo_age_days: Age of repository in days
        - health_score: Overall health score (0-100)

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
    if not (repo / ".git").exists():
        return {
            "total_commits": "0",
            "total_branches": "0",
            "total_tags": "0",
            "total_contributors": "0",
            "repo_age_days": "0",
            "health_score": "0",
        }

    try:
        # Count commits
        commit_result = subprocess.run(
            ["git", "rev-list", "--all", "--count"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        total_commits = (
            int(commit_result.stdout.strip()) if commit_result.returncode == 0 else 0
        )

        # Count branches
        branch_result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        total_branches = (
            len(branch_result.stdout.strip().split("\n"))
            if branch_result.returncode == 0
            else 0
        )

        # Count tags
        tag_result = subprocess.run(
            ["git", "tag"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        total_tags = (
            len([t for t in tag_result.stdout.strip().split("\n") if t])
            if tag_result.returncode == 0
            else 0
        )

        # Count contributors
        author_result = subprocess.run(
            ["git", "log", "--format=%an"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        contributors = (
            len(set(author_result.stdout.strip().split("\n")))
            if author_result.returncode == 0
            else 0
        )

        # Get repository age
        first_commit_result = subprocess.run(
            ["git", "log", "--reverse", "--format=%ci", "--max-count=1"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        repo_age_days = 0
        if first_commit_result.returncode == 0 and first_commit_result.stdout.strip():
            import time
            from datetime import datetime

            first_commit_date = first_commit_result.stdout.strip().split()[0]
            first_dt = datetime.strptime(first_commit_date, "%Y-%m-%d")
            age_seconds = time.time() - first_dt.timestamp()
            repo_age_days = int(age_seconds / (24 * 60 * 60))

        # Calculate health score (simple heuristic)
        health_score = 100
        # Penalize for very few commits
        if total_commits < 10:
            health_score -= 20
        # Bonus for active development
        if total_commits > 100:
            health_score = min(100, health_score + 10)
        # Bonus for multiple contributors
        if contributors > 1:
            health_score = min(100, health_score + 10)

        return {
            "total_commits": str(total_commits),
            "total_branches": str(total_branches),
            "total_tags": str(total_tags),
            "total_contributors": str(contributors),
            "repo_age_days": str(repo_age_days),
            "health_score": str(health_score),
        }

    except subprocess.TimeoutExpired:
        return {
            "total_commits": "0",
            "total_branches": "0",
            "total_tags": "0",
            "total_contributors": "0",
            "repo_age_days": "0",
            "health_score": "0",
        }
    except Exception as e:
        return {
            "total_commits": "0",
            "total_branches": "0",
            "total_tags": "0",
            "total_contributors": "0",
            "repo_age_days": str(e),
            "health_score": "0",
        }
