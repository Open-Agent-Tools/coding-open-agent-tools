"""Tests for git commit message validation and analysis functions."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coding_open_agent_tools.git.commits import (
    analyze_commit_quality,
    check_breaking_changes,
    extract_commit_type,
    parse_commit_message,
    validate_commit_length,
    validate_commit_scope,
    validate_commit_signature,
    validate_conventional_commit,
)


class TestValidateConventionalCommit:
    """Test validate_conventional_commit function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when commit_message is not a string."""
        with pytest.raises(TypeError, match="commit_message must be a string"):
            validate_conventional_commit(123)  # type: ignore

    def test_empty_message(self) -> None:
        """Test ValueError when commit_message is empty."""
        with pytest.raises(ValueError, match="commit_message cannot be empty"):
            validate_conventional_commit("")

    def test_valid_feat_commit(self) -> None:
        """Test valid feature commit."""
        result = validate_conventional_commit("feat: add new feature")

        assert result["is_valid"] == "true"
        assert result["type"] == "feat"
        assert result["scope"] == ""
        assert result["description"] == "add new feature"
        assert result["breaking"] == "false"

    def test_valid_fix_commit(self) -> None:
        """Test valid fix commit."""
        result = validate_conventional_commit("fix: resolve bug in login")

        assert result["is_valid"] == "true"
        assert result["type"] == "fix"
        assert result["description"] == "resolve bug in login"

    def test_commit_with_scope(self) -> None:
        """Test commit with scope."""
        result = validate_conventional_commit("feat(auth): add OAuth support")

        assert result["is_valid"] == "true"
        assert result["type"] == "feat"
        assert result["scope"] == "auth"
        assert result["description"] == "add OAuth support"

    def test_breaking_change_marker(self) -> None:
        """Test breaking change with ! marker."""
        result = validate_conventional_commit("feat!: remove deprecated API")

        assert result["is_valid"] == "true"
        assert result["type"] == "feat"
        assert result["breaking"] == "true"

    def test_breaking_change_body(self) -> None:
        """Test breaking change in body."""
        message = """feat: update API

BREAKING CHANGE: API endpoint changed
"""
        result = validate_conventional_commit(message)

        assert result["is_valid"] == "true"
        assert result["breaking"] == "true"

    def test_invalid_format(self) -> None:
        """Test invalid commit format."""
        result = validate_conventional_commit("This is not a conventional commit")

        assert result["is_valid"] == "false"
        assert result["type"] == ""
        assert "Does not match" in result["error_message"]

    def test_all_commit_types(self) -> None:
        """Test all valid commit types."""
        types = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert"]

        for commit_type in types:
            result = validate_conventional_commit(f"{commit_type}: test message")
            assert result["is_valid"] == "true"
            assert result["type"] == commit_type


class TestValidateCommitSignature:
    """Test validate_commit_signature function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            validate_commit_signature(123, "abc123")  # type: ignore

    def test_invalid_commit_hash_type(self) -> None:
        """Test TypeError when commit_hash is not a string."""
        with pytest.raises(TypeError, match="commit_hash must be a string"):
            validate_commit_signature("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            validate_commit_signature("", "abc123")

    def test_empty_commit_hash(self) -> None:
        """Test ValueError when commit_hash is empty."""
        with pytest.raises(ValueError, match="commit_hash cannot be empty"):
            validate_commit_signature("/tmp", "")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            validate_commit_signature("/nonexistent/path", "abc123")

    def test_not_a_git_repo(self) -> None:
        """Test behavior when path is not a git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = validate_commit_signature(tmpdir, "abc123")
            assert result["is_signed"] == "false"
            assert result["is_valid"] == "false"
            assert "Not a git repository" in result["error_message"]

    @patch("subprocess.run")
    def test_unsigned_commit(self, mock_run: Mock) -> None:
        """Test unsigned commit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            mock_run.return_value = Mock(
                returncode=1, stdout="", stderr="no signature found"
            )
            result = validate_commit_signature(tmpdir, "abc123")

            assert result["is_signed"] == "false"
            assert result["is_valid"] == "false"
            assert "not signed" in result["error_message"]

    @patch("subprocess.run")
    def test_valid_signed_commit(self, mock_run: Mock) -> None:
        """Test valid signed commit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            def mock_command(*args, **kwargs):
                cmd = args[0]
                if "verify-commit" in cmd:
                    return Mock(returncode=0, stdout="", stderr="")
                elif "show" in cmd:
                    return Mock(
                        returncode=0,
                        stdout='gpg: Good signature from "Alice <alice@example.com>"\nPrimary key fingerprint: ABCD1234567890ABCD1234567890ABCD12345678',
                        stderr="",
                    )
                return Mock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = mock_command
            result = validate_commit_signature(tmpdir, "abc123")

            assert result["is_signed"] == "true"
            assert result["is_valid"] == "true"
            assert "Alice" in result["signer"]

    @patch("subprocess.run")
    def test_invalid_signature(self, mock_run: Mock) -> None:
        """Test invalid signature."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            mock_run.return_value = Mock(
                returncode=1, stdout="", stderr="BAD signature from"
            )
            result = validate_commit_signature(tmpdir, "abc123")

            assert result["is_signed"] == "true"
            assert result["is_valid"] == "false"


class TestAnalyzeCommitQuality:
    """Test analyze_commit_quality function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when commit_message is not a string."""
        with pytest.raises(TypeError, match="commit_message must be a string"):
            analyze_commit_quality(123)  # type: ignore

    def test_empty_message(self) -> None:
        """Test ValueError when commit_message is empty."""
        with pytest.raises(ValueError, match="commit_message cannot be empty"):
            analyze_commit_quality("")

    def test_perfect_commit(self) -> None:
        """Test high quality commit."""
        message = """Add user authentication

Implement OAuth2 authentication flow for user login.
This provides secure authentication using industry standards.
"""
        result = analyze_commit_quality(message)

        assert int(result["quality_score"]) >= 80
        assert result["has_subject"] == "true"
        assert result["has_body"] == "true"
        assert result["subject_length_ok"] == "true"
        assert result["has_imperative_mood"] == "true"

    def test_subject_too_long(self) -> None:
        """Test commit with subject line too long."""
        message = "This is a very long subject line that exceeds the recommended 50 character limit"

        result = analyze_commit_quality(message)

        assert result["subject_length_ok"] == "false"
        assert "too long" in result["recommendations"]

    def test_missing_imperative_mood(self) -> None:
        """Test commit without imperative mood."""
        message = "New feature for users"

        result = analyze_commit_quality(message)

        assert result["has_imperative_mood"] == "false"
        assert "imperative mood" in result["recommendations"]

    def test_no_capitalization(self) -> None:
        """Test commit without capitalized subject."""
        message = "add new feature"

        result = analyze_commit_quality(message)

        assert "Capitalize" in result["recommendations"]

    def test_period_at_end(self) -> None:
        """Test commit with period at end of subject."""
        message = "Add new feature."

        result = analyze_commit_quality(message)

        assert "Don't end" in result["recommendations"]

    def test_missing_body_for_complex_change(self) -> None:
        """Test commit with long subject but no body."""
        message = "Update authentication system to use OAuth"

        result = analyze_commit_quality(message)

        assert "adding a body" in result["recommendations"]


class TestParseCommitMessage:
    """Test parse_commit_message function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when commit_message is not a string."""
        with pytest.raises(TypeError, match="commit_message must be a string"):
            parse_commit_message(123)  # type: ignore

    def test_empty_message(self) -> None:
        """Test ValueError when commit_message is empty."""
        with pytest.raises(ValueError, match="commit_message cannot be empty"):
            parse_commit_message("")

    def test_subject_only(self) -> None:
        """Test commit with subject only."""
        result = parse_commit_message("Fix bug in login")

        assert result["subject"] == "Fix bug in login"
        assert result["body"] == ""
        assert result["footer"] == ""
        assert result["line_count"] == "1"

    def test_subject_and_body(self) -> None:
        """Test commit with subject and body."""
        message = """Fix bug in login

The login form was not validating email addresses.
Added proper email validation.
"""
        result = parse_commit_message(message)

        assert result["subject"] == "Fix bug in login"
        assert "validating email" in result["body"]
        assert result["footer"] == ""
        assert int(result["line_count"]) > 1

    def test_with_footer(self) -> None:
        """Test commit with footer trailers."""
        message = """Fix bug in login

The login form was not validating email addresses.

Signed-off-by: Alice <alice@example.com>
Co-authored-by: Bob <bob@example.com>
"""
        result = parse_commit_message(message)

        assert result["subject"] == "Fix bug in login"
        assert "Signed-off-by" in result["footer"]
        assert "Co-authored-by" in result["footer"]

    def test_line_and_length_counts(self) -> None:
        """Test line and character counts."""
        message = """Short subject

Body text here.
"""
        result = parse_commit_message(message)

        assert result["subject_length"] == "13"
        assert int(result["body_length"]) > 0


class TestValidateCommitLength:
    """Test validate_commit_length function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when commit_message is not a string."""
        with pytest.raises(TypeError, match="commit_message must be a string"):
            validate_commit_length(123)  # type: ignore

    def test_empty_message(self) -> None:
        """Test ValueError when commit_message is empty."""
        with pytest.raises(ValueError, match="commit_message cannot be empty"):
            validate_commit_length("")

    def test_valid_subject_length(self) -> None:
        """Test subject within recommended length."""
        result = validate_commit_length("Fix bug")

        assert result["subject_valid"] == "true"
        assert result["subject_warning"] == "false"
        assert int(result["subject_length"]) <= 50

    def test_subject_too_long(self) -> None:
        """Test subject exceeding recommended length."""
        message = "This is a very long subject line that exceeds fifty characters"

        result = validate_commit_length(message)

        assert result["subject_valid"] == "false"
        assert int(result["subject_length"]) > 50
        assert int(result["issues_count"]) >= 1

    def test_subject_warning_threshold(self) -> None:
        """Test subject exceeding warning threshold."""
        message = "X" * 73

        result = validate_commit_length(message)

        assert result["subject_valid"] == "false"
        assert result["subject_warning"] == "true"

    def test_body_line_length(self) -> None:
        """Test body line length validation."""
        message = """Short subject

This is a normal body line.
This is another line within the 72 character limit for body text.
"""
        result = validate_commit_length(message)

        assert result["body_valid"] == "true"
        assert int(result["longest_body_line"]) <= 72

    def test_body_line_too_long(self) -> None:
        """Test body line exceeding length."""
        message = """Short subject

This is an extremely long line in the body that exceeds the recommended 72 character limit for commit message body lines.
"""
        result = validate_commit_length(message)

        assert result["body_valid"] == "false"
        assert int(result["longest_body_line"]) > 72


class TestExtractCommitType:
    """Test extract_commit_type function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when commit_message is not a string."""
        with pytest.raises(TypeError, match="commit_message must be a string"):
            extract_commit_type(123)  # type: ignore

    def test_empty_message(self) -> None:
        """Test ValueError when commit_message is empty."""
        with pytest.raises(ValueError, match="commit_message cannot be empty"):
            extract_commit_type("")

    def test_conventional_feat(self) -> None:
        """Test conventional feat commit."""
        result = extract_commit_type("feat: add new feature")

        assert result["type"] == "feat"
        assert result["is_conventional"] == "true"
        assert result["is_feature"] == "true"
        assert result["is_fix"] == "false"

    def test_conventional_fix(self) -> None:
        """Test conventional fix commit."""
        result = extract_commit_type("fix: resolve bug")

        assert result["type"] == "fix"
        assert result["is_conventional"] == "true"
        assert result["is_fix"] == "true"
        assert result["is_feature"] == "false"

    def test_breaking_change_marker(self) -> None:
        """Test breaking change detection with ! marker."""
        result = extract_commit_type("feat!: remove old API")

        assert result["type"] == "feat"
        assert result["is_breaking"] == "true"

    def test_breaking_change_body(self) -> None:
        """Test breaking change detection in body."""
        message = """feat: update API

BREAKING CHANGE: endpoint changed
"""
        result = extract_commit_type(message)

        assert result["is_breaking"] == "true"

    def test_non_conventional_feat(self) -> None:
        """Test non-conventional feature commit."""
        result = extract_commit_type("Add: new feature")

        assert result["type"] == "feat"
        assert result["is_conventional"] == "false"

    def test_non_conventional_fix(self) -> None:
        """Test non-conventional fix commit."""
        result = extract_commit_type("Bugfix: resolve issue")

        assert result["type"] == "fix"
        assert result["is_conventional"] == "false"

    def test_unknown_type(self) -> None:
        """Test unknown commit type."""
        result = extract_commit_type("Random commit message")

        assert result["type"] == "unknown"
        assert result["is_conventional"] == "false"


class TestValidateCommitScope:
    """Test validate_commit_scope function."""

    def test_invalid_commit_message_type(self) -> None:
        """Test TypeError when commit_message is not a string."""
        with pytest.raises(TypeError, match="commit_message must be a string"):
            validate_commit_scope(123, "api,ui")  # type: ignore

    def test_invalid_allowed_scopes_type(self) -> None:
        """Test TypeError when allowed_scopes is not a string."""
        with pytest.raises(TypeError, match="allowed_scopes must be a string"):
            validate_commit_scope("feat: add feature", 123)  # type: ignore

    def test_empty_commit_message(self) -> None:
        """Test ValueError when commit_message is empty."""
        with pytest.raises(ValueError, match="commit_message cannot be empty"):
            validate_commit_scope("", "api,ui")

    def test_no_scope_in_message(self) -> None:
        """Test commit without scope."""
        result = validate_commit_scope("feat: add feature", "api,ui")

        assert result["has_scope"] == "false"
        assert result["scope"] == ""
        assert result["is_valid"] == "false"
        assert "No scope found" in result["error_message"]

    def test_valid_scope(self) -> None:
        """Test commit with valid scope."""
        result = validate_commit_scope("feat(api): add endpoint", "api,ui,core")

        assert result["has_scope"] == "true"
        assert result["scope"] == "api"
        assert result["is_valid"] == "true"
        assert result["error_message"] == ""

    def test_invalid_scope(self) -> None:
        """Test commit with invalid scope."""
        result = validate_commit_scope("feat(database): add table", "api,ui")

        assert result["has_scope"] == "true"
        assert result["scope"] == "database"
        assert result["is_valid"] == "false"
        assert "not in allowed list" in result["error_message"]

    def test_no_allowed_scopes(self) -> None:
        """Test with no allowed scopes specified."""
        result = validate_commit_scope("feat(api): add endpoint", "")

        assert result["has_scope"] == "true"
        assert result["is_valid"] == "true"


class TestCheckBreakingChanges:
    """Test check_breaking_changes function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when commit_message is not a string."""
        with pytest.raises(TypeError, match="commit_message must be a string"):
            check_breaking_changes(123)  # type: ignore

    def test_empty_message(self) -> None:
        """Test ValueError when commit_message is empty."""
        with pytest.raises(ValueError, match="commit_message cannot be empty"):
            check_breaking_changes("")

    def test_no_breaking_changes(self) -> None:
        """Test commit without breaking changes."""
        result = check_breaking_changes("feat: add new feature")

        assert result["has_breaking"] == "false"
        assert result["has_breaking_marker"] == "false"
        assert result["has_breaking_keyword"] == "false"

    def test_breaking_marker(self) -> None:
        """Test breaking change with ! marker."""
        result = check_breaking_changes("feat!: remove old API")

        assert result["has_breaking"] == "true"
        assert result["has_breaking_marker"] == "true"

    def test_breaking_keyword(self) -> None:
        """Test breaking change with keyword."""
        message = """feat: update API

BREAKING CHANGE: API v1 is removed
"""
        result = check_breaking_changes(message)

        assert result["has_breaking"] == "true"
        assert result["has_breaking_keyword"] == "true"
        assert "removed" in result["breaking_description"]

    def test_migration_notes(self) -> None:
        """Test extraction of migration notes."""
        message = """feat!: update database schema

BREAKING CHANGE: Database schema changed

MIGRATION: Run migration scripts in order:
1. Update users table
2. Add indexes
"""
        result = check_breaking_changes(message)

        assert result["has_breaking"] == "true"
        assert "Update users table" in result["migration_notes"]
        assert "Add indexes" in result["migration_notes"]

    def test_multiple_breaking_indicators(self) -> None:
        """Test commit with multiple breaking indicators."""
        message = """feat(api)!: overhaul authentication

BREAKING CHANGE: Authentication flow completely redesigned
"""
        result = check_breaking_changes(message)

        assert result["has_breaking"] == "true"
        assert result["has_breaking_marker"] == "true"
        assert result["has_breaking_keyword"] == "true"
