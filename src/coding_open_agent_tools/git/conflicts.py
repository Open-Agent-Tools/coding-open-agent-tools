"""Git merge conflict detection and analysis tools.

This module provides functions for detecting, analyzing, and resolving merge conflicts.
"""

import subprocess
from pathlib import Path

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def detect_merge_conflicts(repo_path: str) -> dict[str, str]:
    """Detect if repository has active merge conflicts.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - has_conflicts: "true" if conflicts exist
        - conflicted_files_count: Number of conflicted files
        - conflicted_files: Newline-separated list of files
        - in_merge: "true" if merge is in progress
        - merge_head: Merge head commit if in merge

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
            "has_conflicts": "false",
            "conflicted_files_count": "0",
            "conflicted_files": "",
            "in_merge": "false",
            "merge_head": "",
        }

    try:
        # Check if merge is in progress
        merge_head_file = repo / ".git" / "MERGE_HEAD"
        in_merge = merge_head_file.exists()
        merge_head = ""

        if in_merge:
            try:
                with open(merge_head_file) as f:
                    merge_head = f.read().strip()
            except Exception:
                pass

        # Get conflicted files from status
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        conflicted_files = []
        if result.returncode == 0 and result.stdout.strip():
            conflicted_files = result.stdout.strip().split("\n")

        has_conflicts = len(conflicted_files) > 0

        return {
            "has_conflicts": "true" if has_conflicts else "false",
            "conflicted_files_count": str(len(conflicted_files)),
            "conflicted_files": "\n".join(conflicted_files) if conflicted_files else "",
            "in_merge": "true" if in_merge else "false",
            "merge_head": merge_head,
        }

    except subprocess.TimeoutExpired:
        return {
            "has_conflicts": "false",
            "conflicted_files_count": "0",
            "conflicted_files": "",
            "in_merge": "false",
            "merge_head": "",
        }
    except Exception as e:
        return {
            "has_conflicts": "false",
            "conflicted_files_count": "0",
            "conflicted_files": str(e),
            "in_merge": "false",
            "merge_head": "",
        }


@strands_tool
def parse_conflict_markers(file_content: str) -> dict[str, str]:
    """Parse git conflict markers in file content.

    Args:
        file_content: Content of file with conflict markers

    Returns:
        Dictionary with:
        - has_conflicts: "true" if conflict markers found
        - conflict_count: Number of conflict regions
        - conflicts: JSON-formatted list of conflict regions
        - ours_lines: Total lines from "ours" side
        - theirs_lines: Total lines from "theirs" side

    Raises:
        TypeError: If file_content is not a string
    """
    if not isinstance(file_content, str):
        raise TypeError("file_content must be a string")

    if not file_content.strip():
        return {
            "has_conflicts": "false",
            "conflict_count": "0",
            "conflicts": "",
            "ours_lines": "0",
            "theirs_lines": "0",
        }

    # Pattern for conflict markers
    # <<<<<<< HEAD (ours)
    # =======
    # >>>>>>> branch (theirs)

    conflicts = []
    ours_total = 0
    theirs_total = 0

    lines = file_content.split("\n")
    i = 0

    while i < len(lines):
        if lines[i].startswith("<<<<<<<"):
            # Found conflict start
            conflict_start = i
            ours_start = i + 1
            separator = -1
            conflict_end = -1

            # Find separator and end
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("======="):
                    separator = j
                elif lines[j].startswith(">>>>>>>"):
                    conflict_end = j
                    break

            if separator > 0 and conflict_end > 0:
                # Count conflict regions
                ours_count = separator - ours_start
                theirs_count = conflict_end - separator - 1

                ours_total += ours_count
                theirs_total += theirs_count

                conflicts.append(
                    f"Line {conflict_start + 1}: {ours_count} vs {theirs_count} lines"
                )

                i = conflict_end + 1
            else:
                i += 1
        else:
            i += 1

    has_conflicts = len(conflicts) > 0

    return {
        "has_conflicts": "true" if has_conflicts else "false",
        "conflict_count": str(len(conflicts)),
        "conflicts": "\n".join(conflicts) if conflicts else "",
        "ours_lines": str(ours_total),
        "theirs_lines": str(theirs_total),
    }


@strands_tool
def predict_merge_conflicts(
    repo_path: str, source_branch: str, target_branch: str
) -> dict[str, str]:
    """Predict potential conflicts before merging branches.

    Args:
        repo_path: Path to git repository
        source_branch: Branch to merge from
        target_branch: Branch to merge into

    Returns:
        Dictionary with:
        - will_conflict: "true" if conflicts predicted
        - conflicted_files: Newline-separated list of files
        - can_merge_clean: "true" if clean merge possible
        - merge_base: Common ancestor commit
        - error_message: Error if prediction fails

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(source_branch, str):
        raise TypeError("source_branch must be a string")
    if not isinstance(target_branch, str):
        raise TypeError("target_branch must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not source_branch.strip():
        raise ValueError("source_branch cannot be empty")
    if not target_branch.strip():
        raise ValueError("target_branch cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    try:
        # Find merge base
        base_result = subprocess.run(
            ["git", "merge-base", source_branch, target_branch],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if base_result.returncode != 0:
            return {
                "will_conflict": "false",
                "conflicted_files": "",
                "can_merge_clean": "false",
                "merge_base": "",
                "error_message": "Could not find merge base",
            }

        merge_base = base_result.stdout.strip()

        # Try dry-run merge
        result = subprocess.run(
            ["git", "merge-tree", merge_base, target_branch, source_branch],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Parse output for conflicts
        has_conflicts = "conflict" in result.stdout.lower()

        # Extract conflicted files
        conflicted_files = []
        if has_conflicts:
            # Look for "changed in both" or conflict markers
            for line in result.stdout.split("\n"):
                if "changed in both" in line.lower():
                    # Extract filename
                    parts = line.split()
                    if parts:
                        conflicted_files.append(parts[-1])

        return {
            "will_conflict": "true" if has_conflicts else "false",
            "conflicted_files": "\n".join(set(conflicted_files))
            if conflicted_files
            else "",
            "can_merge_clean": "false" if has_conflicts else "true",
            "merge_base": merge_base,
            "error_message": "",
        }

    except subprocess.TimeoutExpired:
        return {
            "will_conflict": "false",
            "conflicted_files": "",
            "can_merge_clean": "false",
            "merge_base": "",
            "error_message": "Merge prediction timed out",
        }
    except Exception as e:
        return {
            "will_conflict": "false",
            "conflicted_files": "",
            "can_merge_clean": "false",
            "merge_base": "",
            "error_message": str(e),
        }


@strands_tool
def analyze_conflict_complexity(file_content: str) -> dict[str, str]:
    """Analyze complexity of merge conflicts in file.

    Args:
        file_content: Content of file with conflict markers

    Returns:
        Dictionary with:
        - complexity_score: Conflict complexity score (1-10)
        - total_conflicts: Number of conflict regions
        - avg_conflict_size: Average conflict size in lines
        - max_conflict_size: Largest conflict size in lines
        - resolution_difficulty: "easy", "medium", or "hard"

    Raises:
        TypeError: If file_content is not a string
    """
    if not isinstance(file_content, str):
        raise TypeError("file_content must be a string")

    if not file_content.strip():
        return {
            "complexity_score": "0",
            "total_conflicts": "0",
            "avg_conflict_size": "0",
            "max_conflict_size": "0",
            "resolution_difficulty": "easy",
        }

    conflicts = []
    lines = file_content.split("\n")
    i = 0

    while i < len(lines):
        if lines[i].startswith("<<<<<<<"):
            conflict_start = i
            separator = -1
            conflict_end = -1

            for j in range(i + 1, len(lines)):
                if lines[j].startswith("======="):
                    separator = j
                elif lines[j].startswith(">>>>>>>"):
                    conflict_end = j
                    break

            if separator > 0 and conflict_end > 0:
                conflict_size = conflict_end - conflict_start + 1
                conflicts.append(conflict_size)
                i = conflict_end + 1
            else:
                i += 1
        else:
            i += 1

    if not conflicts:
        return {
            "complexity_score": "0",
            "total_conflicts": "0",
            "avg_conflict_size": "0",
            "max_conflict_size": "0",
            "resolution_difficulty": "easy",
        }

    total_conflicts = len(conflicts)
    avg_size = sum(conflicts) / len(conflicts)
    max_size = max(conflicts)

    # Calculate complexity score
    score = 1
    score += min(4, total_conflicts)  # More conflicts = higher score
    score += min(3, int(avg_size / 10))  # Larger conflicts = higher score
    score += min(2, int(max_size / 50))  # Very large conflict = higher score

    # Determine difficulty
    if score <= 3:
        difficulty = "easy"
    elif score <= 6:
        difficulty = "medium"
    else:
        difficulty = "hard"

    return {
        "complexity_score": str(min(10, score)),
        "total_conflicts": str(total_conflicts),
        "avg_conflict_size": f"{avg_size:.1f}",
        "max_conflict_size": str(max_size),
        "resolution_difficulty": difficulty,
    }


@strands_tool
def get_conflict_context(
    repo_path: str, file_path: str, line_number: str
) -> dict[str, str]:
    """Get context around a conflict marker in file.

    Args:
        repo_path: Path to git repository
        file_path: Path to file with conflicts
        line_number: Line number of conflict marker

    Returns:
        Dictionary with:
        - has_conflict: "true" if line has conflict marker
        - conflict_type: "ours", "theirs", or "separator"
        - context_before: Lines before conflict (up to 3)
        - context_after: Lines after conflict (up to 3)
        - full_conflict: Full conflict region if at marker

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If file doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(line_number, str):
        raise TypeError("line_number must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not file_path.strip():
        raise ValueError("file_path cannot be empty")
    if not line_number.strip():
        raise ValueError("line_number cannot be empty")

    try:
        line_num = int(line_number)
        if line_num < 1:
            raise ValueError("line_number must be positive")
    except ValueError:
        raise ValueError("line_number must be a valid integer")

    full_file_path = Path(repo_path) / file_path
    if not full_file_path.exists():
        raise FileNotFoundError(f"File does not exist: {full_file_path}")

    try:
        with open(full_file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return {
            "has_conflict": "false",
            "conflict_type": "",
            "context_before": "",
            "context_after": "",
            "full_conflict": f"Error reading file: {str(e)}",
        }

    if line_num > len(lines):
        return {
            "has_conflict": "false",
            "conflict_type": "",
            "context_before": "",
            "context_after": "",
            "full_conflict": "Line number exceeds file length",
        }

    # Adjust to 0-indexed
    idx = line_num - 1
    target_line = lines[idx].strip()

    # Check conflict marker type
    conflict_type = ""
    if target_line.startswith("<<<<<<<"):
        conflict_type = "ours"
    elif target_line.startswith("======="):
        conflict_type = "separator"
    elif target_line.startswith(">>>>>>>"):
        conflict_type = "theirs"

    has_conflict = bool(conflict_type)

    # Get context
    context_before = []
    for i in range(max(0, idx - 3), idx):
        context_before.append(lines[i].rstrip())

    context_after = []
    for i in range(idx + 1, min(len(lines), idx + 4)):
        context_after.append(lines[i].rstrip())

    # Extract full conflict if at a marker
    full_conflict = ""
    if has_conflict:
        # Find conflict bounds
        start = idx
        end = idx

        if conflict_type == "ours":
            # Find end marker
            for i in range(idx, len(lines)):
                if lines[i].startswith(">>>>>>>"):
                    end = i
                    break
        else:
            # Find start marker backward
            for i in range(idx, -1, -1):
                if lines[i].startswith("<<<<<<<"):
                    start = i
                    break
            # Find end marker forward
            for i in range(idx, len(lines)):
                if lines[i].startswith(">>>>>>>"):
                    end = i
                    break

        if start < end:
            full_conflict = "".join(lines[start : end + 1])

    return {
        "has_conflict": "true" if has_conflict else "false",
        "conflict_type": conflict_type,
        "context_before": "\n".join(context_before),
        "context_after": "\n".join(context_after),
        "full_conflict": full_conflict.strip(),
    }


@strands_tool
def suggest_conflict_resolution(file_content: str) -> dict[str, str]:
    """Suggest resolution strategy for merge conflicts.

    Args:
        file_content: Content of file with conflict markers

    Returns:
        Dictionary with:
        - has_suggestions: "true" if suggestions available
        - strategy: Suggested resolution strategy
        - confidence: Confidence level ("low", "medium", "high")
        - suggestions: Specific suggestions for resolution
        - auto_resolvable: "true" if conflicts might be auto-resolvable

    Raises:
        TypeError: If file_content is not a string
    """
    if not isinstance(file_content, str):
        raise TypeError("file_content must be a string")

    if not file_content.strip():
        return {
            "has_suggestions": "false",
            "strategy": "none",
            "confidence": "low",
            "suggestions": "No conflicts found",
            "auto_resolvable": "false",
        }

    # Parse conflicts
    conflicts = []
    lines = file_content.split("\n")
    i = 0

    while i < len(lines):
        if lines[i].startswith("<<<<<<<"):
            ours_start = i + 1
            separator = -1
            theirs_end = -1

            for j in range(i + 1, len(lines)):
                if lines[j].startswith("======="):
                    separator = j
                elif lines[j].startswith(">>>>>>>"):
                    theirs_end = j
                    break

            if separator > 0 and theirs_end > 0:
                ours = lines[ours_start:separator]
                theirs = lines[separator + 1 : theirs_end]
                conflicts.append({"ours": ours, "theirs": theirs})
                i = theirs_end + 1
            else:
                i += 1
        else:
            i += 1

    if not conflicts:
        return {
            "has_suggestions": "false",
            "strategy": "none",
            "confidence": "low",
            "suggestions": "No conflicts found",
            "auto_resolvable": "false",
        }

    suggestions = []
    auto_resolvable_count = 0

    # Analyze each conflict
    for idx, conflict in enumerate(conflicts, 1):
        ours = conflict["ours"]
        theirs = conflict["theirs"]

        # Check if identical (whitespace only difference)
        if "".join(ours).strip() == "".join(theirs).strip():
            suggestions.append(f"Conflict {idx}: Identical content, choose either side")
            auto_resolvable_count += 1

        # Check if one side is empty
        elif not "".join(ours).strip():
            suggestions.append(
                f"Conflict {idx}: 'Ours' is empty, likely safe to use 'theirs'"
            )
            auto_resolvable_count += 1
        elif not "".join(theirs).strip():
            suggestions.append(
                f"Conflict {idx}: 'Theirs' is empty, likely safe to use 'ours'"
            )
            auto_resolvable_count += 1

        # Check if one is superset of other
        elif all(line in theirs for line in ours):
            suggestions.append(
                f"Conflict {idx}: 'Theirs' includes all of 'ours', consider using 'theirs'"
            )
        elif all(line in ours for line in theirs):
            suggestions.append(
                f"Conflict {idx}: 'Ours' includes all of 'theirs', consider using 'ours'"
            )

        else:
            suggestions.append(
                f"Conflict {idx}: Manual review needed, content differs significantly"
            )

    # Determine strategy and confidence
    auto_resolvable = auto_resolvable_count == len(conflicts)

    if auto_resolvable:
        strategy = "automatic"
        confidence = "high"
    elif auto_resolvable_count > len(conflicts) / 2:
        strategy = "semi-automatic"
        confidence = "medium"
    else:
        strategy = "manual"
        confidence = "low"

    return {
        "has_suggestions": "true",
        "strategy": strategy,
        "confidence": confidence,
        "suggestions": "\n".join(suggestions),
        "auto_resolvable": "true" if auto_resolvable else "false",
    }
