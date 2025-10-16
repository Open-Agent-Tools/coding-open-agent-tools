"""Git tag and version management tools.

This module provides functions for analyzing git tags, validating
semantic versioning, and managing release tags.
"""

import re
import subprocess
from pathlib import Path

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def list_tags(repo_path: str, pattern: str) -> dict[str, str]:
    """List git tags matching a pattern.

    Args:
        repo_path: Path to git repository
        pattern: Glob pattern to filter tags (e.g., "v*", "*-rc*")

    Returns:
        Dictionary with:
        - tag_count: Number of matching tags
        - tags: Newline-separated list of tags (most recent first)
        - latest_tag: Most recent tag
        - has_tags: "true" if any tags exist

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
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

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        result = subprocess.run(
            ["git", "tag", "-l", pattern, "--sort=-version:refname"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return {
                "tag_count": "0",
                "tags": "Could not list tags",
                "latest_tag": "",
                "has_tags": "false",
            }

        tags = [tag for tag in result.stdout.strip().split("\n") if tag]

        return {
            "tag_count": str(len(tags)),
            "tags": "\n".join(tags[:50]) if tags else "",  # Limit to 50 tags
            "latest_tag": tags[0] if tags else "",
            "has_tags": "true" if tags else "false",
        }
    except Exception as e:
        return {
            "tag_count": "0",
            "tags": str(e),
            "latest_tag": "",
            "has_tags": "false",
        }


@strands_tool
def validate_semver_tag(tag_name: str) -> dict[str, str]:
    """Validate if tag follows semantic versioning.

    Args:
        tag_name: Tag name to validate

    Returns:
        Dictionary with:
        - is_semver: "true" if valid semantic version
        - major: Major version number
        - minor: Minor version number
        - patch: Patch version number
        - prerelease: Prerelease identifier (if any)
        - error_message: Validation error message

    Raises:
        TypeError: If tag_name is not a string
        ValueError: If tag_name is empty
    """
    if not isinstance(tag_name, str):
        raise TypeError("tag_name must be a string")
    if not tag_name.strip():
        raise ValueError("tag_name cannot be empty")

    # Semantic versioning pattern: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
    # Optionally prefixed with 'v'
    semver_pattern = (
        r"^v?(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\-\.]+))?(?:\+([a-zA-Z0-9\-\.]+))?$"
    )

    match = re.match(semver_pattern, tag_name)

    if match:
        major, minor, patch, prerelease, _build = match.groups()
        return {
            "is_semver": "true",
            "major": major,
            "minor": minor,
            "patch": patch,
            "prerelease": prerelease or "",
            "error_message": "",
        }
    else:
        return {
            "is_semver": "false",
            "major": "0",
            "minor": "0",
            "patch": "0",
            "prerelease": "",
            "error_message": "Tag does not follow semantic versioning (MAJOR.MINOR.PATCH)",
        }


@strands_tool
def compare_versions(version1: str, version2: str) -> dict[str, str]:
    """Compare two semantic version strings.

    Args:
        version1: First version to compare
        version2: Second version to compare

    Returns:
        Dictionary with:
        - comparison: "greater", "less", "equal", or "invalid"
        - version1_parsed: Parsed version1 (M.m.p)
        - version2_parsed: Parsed version2 (M.m.p)
        - difference: Description of difference

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
    """
    if not isinstance(version1, str):
        raise TypeError("version1 must be a string")
    if not isinstance(version2, str):
        raise TypeError("version2 must be a string")
    if not version1.strip():
        raise ValueError("version1 cannot be empty")
    if not version2.strip():
        raise ValueError("version2 cannot be empty")

    # Strip 'v' prefix if present
    v1 = version1.lstrip("v")
    v2 = version2.lstrip("v")

    # Parse versions
    semver_pattern = r"^(\d+)\.(\d+)\.(\d+)"

    match1 = re.match(semver_pattern, v1)
    match2 = re.match(semver_pattern, v2)

    if not match1 or not match2:
        return {
            "comparison": "invalid",
            "version1_parsed": v1,
            "version2_parsed": v2,
            "difference": "One or both versions are not valid semantic versions",
        }

    major1, minor1, patch1 = map(int, match1.groups())
    major2, minor2, patch2 = map(int, match2.groups())

    v1_parsed = f"{major1}.{minor1}.{patch1}"
    v2_parsed = f"{major2}.{minor2}.{patch2}"

    # Compare versions
    if (major1, minor1, patch1) > (major2, minor2, patch2):
        comparison = "greater"
        if major1 > major2:
            difference = f"Major version difference: {major1} > {major2}"
        elif minor1 > minor2:
            difference = f"Minor version difference: {minor1} > {minor2}"
        else:
            difference = f"Patch version difference: {patch1} > {patch2}"
    elif (major1, minor1, patch1) < (major2, minor2, patch2):
        comparison = "less"
        if major1 < major2:
            difference = f"Major version difference: {major1} < {major2}"
        elif minor1 < minor2:
            difference = f"Minor version difference: {minor1} < {minor2}"
        else:
            difference = f"Patch version difference: {patch1} < {patch2}"
    else:
        comparison = "equal"
        difference = "Versions are identical"

    return {
        "comparison": comparison,
        "version1_parsed": v1_parsed,
        "version2_parsed": v2_parsed,
        "difference": difference,
    }


@strands_tool
def analyze_tag_history(repo_path: str, max_tags: str) -> dict[str, str]:
    """Analyze version tag history and release patterns.

    Args:
        repo_path: Path to git repository
        max_tags: Maximum number of tags to analyze

    Returns:
        Dictionary with:
        - total_tags: Total number of tags analyzed
        - release_pattern: "major", "minor", "patch", or "mixed"
        - latest_version: Latest semantic version tag
        - tags_analyzed: Newline-separated list of analyzed tags
        - recommendation: Release recommendation

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty or max_tags is invalid
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(max_tags, str):
        raise TypeError("max_tags must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")

    try:
        max_count = int(max_tags)
        if max_count <= 0:
            raise ValueError("max_tags must be positive")
    except ValueError:
        raise ValueError("max_tags must be a valid positive integer")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        result = subprocess.run(
            ["git", "tag", "-l", "v*", "--sort=-version:refname"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return {
                "total_tags": "0",
                "release_pattern": "unknown",
                "latest_version": "",
                "tags_analyzed": "Could not list tags",
                "recommendation": "No tags found",
            }

        tags = [tag for tag in result.stdout.strip().split("\n") if tag][:max_count]

        if not tags:
            return {
                "total_tags": "0",
                "release_pattern": "unknown",
                "latest_version": "",
                "tags_analyzed": "",
                "recommendation": "Create initial release tag",
            }

        # Analyze version changes
        semver_pattern = r"v?(\d+)\.(\d+)\.(\d+)"
        version_changes = {"major": 0, "minor": 0, "patch": 0}

        for i in range(len(tags) - 1):
            current_match = re.match(semver_pattern, tags[i])
            prev_match = re.match(semver_pattern, tags[i + 1])

            if current_match and prev_match:
                curr_major, curr_minor, curr_patch = map(int, current_match.groups())
                prev_major, prev_minor, prev_patch = map(int, prev_match.groups())

                if curr_major > prev_major:
                    version_changes["major"] += 1
                elif curr_minor > prev_minor:
                    version_changes["minor"] += 1
                elif curr_patch > prev_patch:
                    version_changes["patch"] += 1

        # Determine release pattern
        if (
            version_changes["major"] > version_changes["minor"]
            and version_changes["major"] > version_changes["patch"]
        ):
            pattern = "major"
            recommendation = "Frequent major releases - ensure backward compatibility"
        elif version_changes["minor"] > version_changes["patch"]:
            pattern = "minor"
            recommendation = "Regular minor releases - good feature cadence"
        elif version_changes["patch"] > 0:
            pattern = "patch"
            recommendation = "Frequent patch releases - good bug fix cadence"
        else:
            pattern = "mixed"
            recommendation = "Mixed release pattern"

        return {
            "total_tags": str(len(tags)),
            "release_pattern": pattern,
            "latest_version": tags[0] if tags else "",
            "tags_analyzed": "\n".join(tags),
            "recommendation": recommendation,
        }
    except Exception as e:
        return {
            "total_tags": "0",
            "release_pattern": "unknown",
            "latest_version": "",
            "tags_analyzed": str(e),
            "recommendation": "Error analyzing tags",
        }


@strands_tool
def find_commits_between_tags(repo_path: str, tag1: str, tag2: str) -> dict[str, str]:
    """Find commits between two tags.

    Args:
        repo_path: Path to git repository
        tag1: Earlier tag
        tag2: Later tag

    Returns:
        Dictionary with:
        - commit_count: Number of commits between tags
        - commits: Newline-separated list of commit summaries
        - has_breaking_changes: "true" if breaking changes detected
        - summary: Summary of changes

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(tag1, str):
        raise TypeError("tag1 must be a string")
    if not isinstance(tag2, str):
        raise TypeError("tag2 must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not tag1.strip():
        raise ValueError("tag1 cannot be empty")
    if not tag2.strip():
        raise ValueError("tag2 cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        result = subprocess.run(
            ["git", "log", f"{tag1}..{tag2}", "--oneline", "--no-merges"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "commit_count": "0",
                "commits": f"Could not find commits between {tag1} and {tag2}",
                "has_breaking_changes": "false",
                "summary": "Error fetching commits",
            }

        commits = [c for c in result.stdout.strip().split("\n") if c]

        # Check for breaking changes
        breaking_indicators = ["BREAKING CHANGE", "breaking:", "!:", "major:"]
        has_breaking = any(
            any(
                indicator.lower() in commit.lower() for indicator in breaking_indicators
            )
            for commit in commits
        )

        # Categorize commits
        features = sum(
            1 for c in commits if "feat:" in c.lower() or "feature:" in c.lower()
        )
        fixes = sum(1 for c in commits if "fix:" in c.lower())
        docs = sum(1 for c in commits if "docs:" in c.lower())

        summary_parts = []
        if features > 0:
            summary_parts.append(f"{features} feature(s)")
        if fixes > 0:
            summary_parts.append(f"{fixes} fix(es)")
        if docs > 0:
            summary_parts.append(f"{docs} doc(s)")

        summary = (
            ", ".join(summary_parts) if summary_parts else f"{len(commits)} commit(s)"
        )

        return {
            "commit_count": str(len(commits)),
            "commits": "\n".join(commits[:50])
            if commits
            else "",  # Limit to 50 commits
            "has_breaking_changes": "true" if has_breaking else "false",
            "summary": summary,
        }
    except Exception as e:
        return {
            "commit_count": "0",
            "commits": str(e),
            "has_breaking_changes": "false",
            "summary": "Error analyzing commits",
        }
