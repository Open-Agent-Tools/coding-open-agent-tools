"""Git commit message validation and analysis tools.

This module provides functions for validating and analyzing git commit messages,
including conventional commit format, signatures, and quality metrics.
"""

import re
import subprocess
from pathlib import Path

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def validate_conventional_commit(commit_message: str) -> dict[str, str]:
    """Validate if commit message follows Conventional Commits specification.

    Conventional Commits format: <type>[optional scope]: <description>

    Args:
        commit_message: The commit message to validate

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - type: Commit type (feat, fix, chore, etc.) or empty
        - scope: Commit scope or empty
        - description: Commit description or empty
        - breaking: "true" if breaking change indicated
        - error_message: Validation error if invalid

    Raises:
        TypeError: If commit_message is not a string
        ValueError: If commit_message is empty
    """
    if not isinstance(commit_message, str):
        raise TypeError("commit_message must be a string")
    if not commit_message.strip():
        raise ValueError("commit_message cannot be empty")

    # Conventional commit pattern: type(scope): description
    # Breaking changes indicated by ! or BREAKING CHANGE in body
    pattern = r"^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(?:\((?P<scope>[^\)]+)\))?(?P<breaking>!)?:\s+(?P<description>.+)"

    lines = commit_message.strip().split("\n")
    subject = lines[0]

    match = re.match(pattern, subject)

    if not match:
        return {
            "is_valid": "false",
            "type": "",
            "scope": "",
            "description": "",
            "breaking": "false",
            "error_message": "Does not match conventional commit format: type(scope): description",
        }

    # Check for BREAKING CHANGE in body
    has_breaking_in_body = "BREAKING CHANGE:" in commit_message
    has_breaking_marker = match.group("breaking") == "!"

    return {
        "is_valid": "true",
        "type": match.group("type"),
        "scope": match.group("scope") or "",
        "description": match.group("description"),
        "breaking": "true"
        if (has_breaking_marker or has_breaking_in_body)
        else "false",
        "error_message": "",
    }


@strands_tool
def validate_commit_signature(repo_path: str, commit_hash: str) -> dict[str, str]:
    """Validate GPG signature of a git commit.

    Args:
        repo_path: Path to git repository
        commit_hash: Commit hash to verify

    Returns:
        Dictionary with:
        - is_signed: "true" or "false"
        - is_valid: "true" if signature valid, "false" otherwise
        - signer: Name of signer or empty
        - key_id: GPG key ID or empty
        - error_message: Error message if validation fails

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(commit_hash, str):
        raise TypeError("commit_hash must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not commit_hash.strip():
        raise ValueError("commit_hash cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")
    if not (repo / ".git").exists():
        return {
            "is_signed": "false",
            "is_valid": "false",
            "signer": "",
            "key_id": "",
            "error_message": "Not a git repository",
        }

    try:
        result = subprocess.run(
            ["git", "verify-commit", commit_hash],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Parse GPG output
        if result.returncode == 0:
            # Try to get signer info
            show_result = subprocess.run(
                ["git", "show", "--show-signature", "--no-patch", commit_hash],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            signer = ""
            key_id = ""

            # Extract signer and key from output
            for line in show_result.stdout.split("\n"):
                if "gpg: Good signature from" in line:
                    match = re.search(r'"([^"]+)"', line)
                    if match:
                        signer = match.group(1)
                if "Primary key fingerprint:" in line or "gpg: " in line:
                    key_match = re.search(r"[A-F0-9]{40}", line)
                    if key_match:
                        key_id = key_match.group(0)

            return {
                "is_signed": "true",
                "is_valid": "true",
                "signer": signer,
                "key_id": key_id,
                "error_message": "",
            }
        else:
            # Commit is not signed or signature is invalid
            if "no signature found" in result.stderr.lower():
                return {
                    "is_signed": "false",
                    "is_valid": "false",
                    "signer": "",
                    "key_id": "",
                    "error_message": "Commit is not signed",
                }
            else:
                return {
                    "is_signed": "true",
                    "is_valid": "false",
                    "signer": "",
                    "key_id": "",
                    "error_message": result.stderr.strip(),
                }

    except subprocess.TimeoutExpired:
        return {
            "is_signed": "false",
            "is_valid": "false",
            "signer": "",
            "key_id": "",
            "error_message": "Command timed out",
        }
    except Exception as e:
        return {
            "is_signed": "false",
            "is_valid": "false",
            "signer": "",
            "key_id": "",
            "error_message": str(e),
        }


@strands_tool
def analyze_commit_quality(commit_message: str) -> dict[str, str]:
    """Analyze quality of a commit message based on best practices.

    Args:
        commit_message: The commit message to analyze

    Returns:
        Dictionary with:
        - quality_score: Score from 0-100
        - has_subject: "true" or "false"
        - has_body: "true" or "false"
        - subject_length_ok: "true" if subject <= 50 chars
        - has_imperative_mood: "true" if starts with verb
        - issues_count: Number of quality issues found
        - recommendations: Newline-separated improvement suggestions

    Raises:
        TypeError: If commit_message is not a string
        ValueError: If commit_message is empty
    """
    if not isinstance(commit_message, str):
        raise TypeError("commit_message must be a string")
    if not commit_message.strip():
        raise ValueError("commit_message cannot be empty")

    lines = commit_message.strip().split("\n")
    subject = lines[0] if lines else ""
    body_lines = lines[2:] if len(lines) > 2 else []
    body = "\n".join(body_lines)

    score = 100
    issues = []
    recommendations = []

    # Check subject
    has_subject = bool(subject)
    if not has_subject:
        score -= 50
        issues.append("missing_subject")
        recommendations.append("Add a subject line")

    # Check subject length (best practice: <= 50 chars)
    subject_length_ok = len(subject) <= 50
    if len(subject) > 50:
        score -= 15
        issues.append("subject_too_long")
        recommendations.append(
            f"Subject line too long ({len(subject)} chars), keep it under 50 characters"
        )

    # Check for imperative mood (starts with verb)
    imperative_verbs = [
        "add",
        "fix",
        "update",
        "remove",
        "refactor",
        "improve",
        "change",
        "implement",
        "create",
        "delete",
        "modify",
        "enhance",
        "optimize",
    ]
    has_imperative = any(subject.lower().startswith(verb) for verb in imperative_verbs)
    if not has_imperative and subject:
        score -= 10
        recommendations.append(
            "Use imperative mood (e.g., 'Add feature' not 'Added feature')"
        )

    # Check for body
    has_body = bool(body.strip())
    if not has_body and len(subject) > 30:
        score -= 10
        recommendations.append(
            "Consider adding a body to explain why this change was made"
        )

    # Check if subject starts with capital letter
    if subject and not subject[0].isupper():
        score -= 5
        recommendations.append("Capitalize the subject line")

    # Check if subject ends with period
    if subject and subject.endswith("."):
        score -= 5
        recommendations.append("Don't end the subject line with a period")

    return {
        "quality_score": str(max(0, score)),
        "has_subject": "true" if has_subject else "false",
        "has_body": "true" if has_body else "false",
        "subject_length_ok": "true" if subject_length_ok else "false",
        "has_imperative_mood": "true" if has_imperative else "false",
        "issues_count": str(len(issues)),
        "recommendations": "\n".join(recommendations)
        if recommendations
        else "No recommendations",
    }


@strands_tool
def parse_commit_message(commit_message: str) -> dict[str, str]:
    """Parse commit message into structured components.

    Args:
        commit_message: The commit message to parse

    Returns:
        Dictionary with:
        - subject: First line of commit message
        - body: Body text (after blank line)
        - footer: Footer text (trailers like Signed-off-by)
        - line_count: Total number of lines
        - subject_length: Length of subject line
        - body_length: Length of body text

    Raises:
        TypeError: If commit_message is not a string
        ValueError: If commit_message is empty
    """
    if not isinstance(commit_message, str):
        raise TypeError("commit_message must be a string")
    if not commit_message.strip():
        raise ValueError("commit_message cannot be empty")

    lines = commit_message.strip().split("\n")

    subject = lines[0] if lines else ""

    # Find body (after first blank line)
    body_start = None
    for i, line in enumerate(lines[1:], start=1):
        if not line.strip():
            body_start = i + 1
            break

    # Find footer (lines with trailers like "Signed-off-by:")
    footer_start = None
    trailer_pattern = r"^[A-Za-z-]+:\s*.+"
    for i in range(len(lines) - 1, 0, -1):
        if re.match(trailer_pattern, lines[i]):
            footer_start = i
        elif lines[i].strip():
            break

    # Extract body and footer
    body = ""
    footer = ""

    if body_start is not None:
        if footer_start is not None and footer_start > body_start:
            body = "\n".join(lines[body_start:footer_start]).strip()
            footer = "\n".join(lines[footer_start:]).strip()
        else:
            body = "\n".join(lines[body_start:]).strip()
    elif footer_start is not None:
        footer = "\n".join(lines[footer_start:]).strip()

    return {
        "subject": subject,
        "body": body,
        "footer": footer,
        "line_count": str(len(lines)),
        "subject_length": str(len(subject)),
        "body_length": str(len(body)),
    }


@strands_tool
def validate_commit_length(commit_message: str) -> dict[str, str]:
    """Validate commit message length requirements.

    Best practices:
    - Subject line: <= 50 characters (warning at 72)
    - Body line length: <= 72 characters

    Args:
        commit_message: The commit message to validate

    Returns:
        Dictionary with:
        - subject_valid: "true" if subject <= 50 chars
        - subject_length: Subject line length
        - subject_warning: "true" if subject > 72 chars
        - body_valid: "true" if all body lines <= 72 chars
        - longest_body_line: Length of longest body line
        - issues_count: Number of length issues

    Raises:
        TypeError: If commit_message is not a string
        ValueError: If commit_message is empty
    """
    if not isinstance(commit_message, str):
        raise TypeError("commit_message must be a string")
    if not commit_message.strip():
        raise ValueError("commit_message cannot be empty")

    lines = commit_message.strip().split("\n")
    subject = lines[0] if lines else ""
    body_lines = lines[2:] if len(lines) > 2 else []

    subject_length = len(subject)
    subject_valid = subject_length <= 50
    subject_warning = subject_length > 72

    # Check body line lengths
    longest_body_line = 0
    body_valid = True
    for line in body_lines:
        line_len = len(line)
        if line_len > longest_body_line:
            longest_body_line = line_len
        if line_len > 72:
            body_valid = False

    issues_count = 0
    if not subject_valid:
        issues_count += 1
    if not body_valid:
        issues_count += 1

    return {
        "subject_valid": "true" if subject_valid else "false",
        "subject_length": str(subject_length),
        "subject_warning": "true" if subject_warning else "false",
        "body_valid": "true" if body_valid else "false",
        "longest_body_line": str(longest_body_line),
        "issues_count": str(issues_count),
    }


@strands_tool
def extract_commit_type(commit_message: str) -> dict[str, str]:
    """Extract commit type from message (feat, fix, chore, etc.).

    Supports both Conventional Commits format and common prefixes.

    Args:
        commit_message: The commit message to analyze

    Returns:
        Dictionary with:
        - type: Extracted commit type or "unknown"
        - is_conventional: "true" if follows conventional format
        - is_feature: "true" if feature commit
        - is_fix: "true" if bug fix commit
        - is_breaking: "true" if breaking change

    Raises:
        TypeError: If commit_message is not a string
        ValueError: If commit_message is empty
    """
    if not isinstance(commit_message, str):
        raise TypeError("commit_message must be a string")
    if not commit_message.strip():
        raise ValueError("commit_message cannot be empty")

    subject = commit_message.strip().split("\n")[0]

    # Try conventional commit format first
    conventional_pattern = r"^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(?:\([^\)]+\))?!?:\s+"
    match = re.match(conventional_pattern, subject)

    if match:
        commit_type = match.group("type")
        is_conventional = True
    else:
        # Try common prefixes
        commit_type = "unknown"
        is_conventional = False

        lower_subject = subject.lower()
        if any(
            lower_subject.startswith(prefix) for prefix in ["feat:", "feature:", "add:"]
        ):
            commit_type = "feat"
        elif any(lower_subject.startswith(prefix) for prefix in ["fix:", "bugfix:"]):
            commit_type = "fix"
        elif lower_subject.startswith("docs:"):
            commit_type = "docs"
        elif lower_subject.startswith("refactor:"):
            commit_type = "refactor"
        elif lower_subject.startswith("test:"):
            commit_type = "test"
        elif lower_subject.startswith("chore:"):
            commit_type = "chore"

    is_breaking = "!" in subject or "BREAKING CHANGE:" in commit_message

    return {
        "type": commit_type,
        "is_conventional": "true" if is_conventional else "false",
        "is_feature": "true" if commit_type == "feat" else "false",
        "is_fix": "true" if commit_type == "fix" else "false",
        "is_breaking": "true" if is_breaking else "false",
    }


@strands_tool
def validate_commit_scope(commit_message: str, allowed_scopes: str) -> dict[str, str]:
    """Validate commit scope against allowed scopes list.

    Args:
        commit_message: The commit message to validate
        allowed_scopes: Comma-separated list of allowed scopes

    Returns:
        Dictionary with:
        - has_scope: "true" if scope is present
        - scope: Extracted scope or empty
        - is_valid: "true" if scope is in allowed list
        - allowed_scopes_list: Newline-separated allowed scopes
        - error_message: Error message if validation fails

    Raises:
        TypeError: If parameters are not strings
        ValueError: If commit_message is empty
    """
    if not isinstance(commit_message, str):
        raise TypeError("commit_message must be a string")
    if not isinstance(allowed_scopes, str):
        raise TypeError("allowed_scopes must be a string")
    if not commit_message.strip():
        raise ValueError("commit_message cannot be empty")

    subject = commit_message.strip().split("\n")[0]

    # Extract scope from conventional commit format
    pattern = r"^[a-z]+\((?P<scope>[^\)]+)\)"
    match = re.match(pattern, subject)

    if not match:
        return {
            "has_scope": "false",
            "scope": "",
            "is_valid": "false",
            "allowed_scopes_list": "\n".join(allowed_scopes.split(","))
            if allowed_scopes
            else "",
            "error_message": "No scope found in commit message",
        }

    scope = match.group("scope")
    allowed_list = [s.strip() for s in allowed_scopes.split(",") if s.strip()]

    # If no allowed scopes specified, any scope is valid
    if not allowed_list:
        is_valid = True
        error_message = ""
    else:
        is_valid = scope in allowed_list
        error_message = (
            ""
            if is_valid
            else f"Scope '{scope}' not in allowed list: {', '.join(allowed_list)}"
        )

    return {
        "has_scope": "true",
        "scope": scope,
        "is_valid": "true" if is_valid else "false",
        "allowed_scopes_list": "\n".join(allowed_list),
        "error_message": error_message,
    }


@strands_tool
def check_breaking_changes(commit_message: str) -> dict[str, str]:
    """Detect breaking change indicators in commit message.

    Checks for:
    - ! in commit type (e.g., feat!:)
    - BREAKING CHANGE: in commit body
    - Breaking change keywords in description

    Args:
        commit_message: The commit message to analyze

    Returns:
        Dictionary with:
        - has_breaking: "true" if breaking change detected
        - has_breaking_marker: "true" if ! marker present
        - has_breaking_keyword: "true" if BREAKING CHANGE: found
        - breaking_description: Description of breaking change
        - migration_notes: Migration notes if present

    Raises:
        TypeError: If commit_message is not a string
        ValueError: If commit_message is empty
    """
    if not isinstance(commit_message, str):
        raise TypeError("commit_message must be a string")
    if not commit_message.strip():
        raise ValueError("commit_message cannot be empty")

    lines = commit_message.strip().split("\n")
    subject = lines[0] if lines else ""

    # Check for ! marker in subject
    has_breaking_marker = "!" in subject.split(":")[0] if ":" in subject else False

    # Check for BREAKING CHANGE: keyword
    has_breaking_keyword = "BREAKING CHANGE:" in commit_message

    # Extract breaking change description
    breaking_description = ""
    migration_notes = ""

    if has_breaking_keyword:
        for i, line in enumerate(lines):
            if "BREAKING CHANGE:" in line:
                # Get description after BREAKING CHANGE:
                desc_parts = [line.split("BREAKING CHANGE:")[-1].strip()]

                # Get following lines until empty line or next section
                for next_line in lines[i + 1 :]:
                    if not next_line.strip() or ":" in next_line:
                        break
                    desc_parts.append(next_line.strip())

                breaking_description = " ".join(desc_parts)
                break

        # Look for migration notes
        for i, line in enumerate(lines):
            if "MIGRATION:" in line or "Migration:" in line:
                migration_parts = [line.split(":")[-1].strip()]
                for next_line in lines[i + 1 :]:
                    if not next_line.strip():
                        break
                    migration_parts.append(next_line.strip())
                migration_notes = " ".join(migration_parts)
                break

    has_breaking = has_breaking_marker or has_breaking_keyword

    return {
        "has_breaking": "true" if has_breaking else "false",
        "has_breaking_marker": "true" if has_breaking_marker else "false",
        "has_breaking_keyword": "true" if has_breaking_keyword else "false",
        "breaking_description": breaking_description,
        "migration_notes": migration_notes,
    }
