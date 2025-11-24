"""Tests for git tag and version management functions."""

import tempfile
from unittest.mock import Mock, patch

import pytest

from coding_open_agent_tools.git.tags import (
    analyze_tag_history,
    compare_versions,
    find_commits_between_tags,
    list_tags,
    validate_semver_tag,
)


class TestListTags:
    """Test list_tags function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            list_tags(123, "v*")  # type: ignore

    def test_invalid_pattern_type(self) -> None:
        """Test TypeError when pattern is not a string."""
        with pytest.raises(TypeError, match="pattern must be a string"):
            list_tags("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            list_tags("", "v*")

    def test_empty_pattern(self) -> None:
        """Test ValueError when pattern is empty."""
        with pytest.raises(ValueError, match="pattern cannot be empty"):
            list_tags("/tmp", "")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            list_tags("/nonexistent/path", "v*")

    @patch("subprocess.run")
    def test_no_tags(self, mock_run: Mock) -> None:
        """Test when no tags found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            result = list_tags(tmpdir, "v*")
            assert result["tag_count"] == "0"
            assert result["has_tags"] == "false"

    @patch("subprocess.run")
    def test_with_tags(self, mock_run: Mock) -> None:
        """Test listing tags."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "v1.2.3\nv1.2.2\nv1.2.1\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = list_tags(tmpdir, "v*")
            assert result["tag_count"] == "3"
            assert result["has_tags"] == "true"
            assert result["latest_tag"] == "v1.2.3"


class TestValidateSemverTag:
    """Test validate_semver_tag function."""

    def test_invalid_tag_name_type(self) -> None:
        """Test TypeError when tag_name is not a string."""
        with pytest.raises(TypeError, match="tag_name must be a string"):
            validate_semver_tag(123)  # type: ignore

    def test_empty_tag_name(self) -> None:
        """Test ValueError when tag_name is empty."""
        with pytest.raises(ValueError, match="tag_name cannot be empty"):
            validate_semver_tag("")

    def test_valid_semver(self) -> None:
        """Test valid semantic version."""
        result = validate_semver_tag("v1.2.3")
        assert result["is_semver"] == "true"
        assert result["major"] == "1"
        assert result["minor"] == "2"
        assert result["patch"] == "3"

    def test_valid_semver_without_v(self) -> None:
        """Test valid semantic version without v prefix."""
        result = validate_semver_tag("1.2.3")
        assert result["is_semver"] == "true"
        assert result["major"] == "1"

    def test_semver_with_prerelease(self) -> None:
        """Test semantic version with prerelease."""
        result = validate_semver_tag("v1.2.3-alpha.1")
        assert result["is_semver"] == "true"
        assert result["prerelease"] == "alpha.1"

    def test_invalid_semver(self) -> None:
        """Test invalid semantic version."""
        result = validate_semver_tag("invalid-tag")
        assert result["is_semver"] == "false"
        assert "does not follow" in result["error_message"]


class TestCompareVersions:
    """Test compare_versions function."""

    def test_invalid_version1_type(self) -> None:
        """Test TypeError when version1 is not a string."""
        with pytest.raises(TypeError, match="version1 must be a string"):
            compare_versions(123, "1.0.0")  # type: ignore

    def test_invalid_version2_type(self) -> None:
        """Test TypeError when version2 is not a string."""
        with pytest.raises(TypeError, match="version2 must be a string"):
            compare_versions("1.0.0", 123)  # type: ignore

    def test_empty_version1(self) -> None:
        """Test ValueError when version1 is empty."""
        with pytest.raises(ValueError, match="version1 cannot be empty"):
            compare_versions("", "1.0.0")

    def test_empty_version2(self) -> None:
        """Test ValueError when version2 is empty."""
        with pytest.raises(ValueError, match="version2 cannot be empty"):
            compare_versions("1.0.0", "")

    def test_equal_versions(self) -> None:
        """Test comparing equal versions."""
        result = compare_versions("1.2.3", "1.2.3")
        assert result["comparison"] == "equal"
        assert "identical" in result["difference"]

    def test_greater_version(self) -> None:
        """Test v1 greater than v2."""
        result = compare_versions("2.0.0", "1.0.0")
        assert result["comparison"] == "greater"

    def test_less_version(self) -> None:
        """Test v1 less than v2."""
        result = compare_versions("1.0.0", "2.0.0")
        assert result["comparison"] == "less"

    def test_invalid_versions(self) -> None:
        """Test comparing invalid versions."""
        result = compare_versions("invalid", "1.0.0")
        assert result["comparison"] == "invalid"


class TestAnalyzeTagHistory:
    """Test analyze_tag_history function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            analyze_tag_history(123, "10")  # type: ignore

    def test_invalid_max_tags_type(self) -> None:
        """Test TypeError when max_tags is not a string."""
        with pytest.raises(TypeError, match="max_tags must be a string"):
            analyze_tag_history("/tmp", 10)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            analyze_tag_history("", "10")

    def test_invalid_max_tags_format(self) -> None:
        """Test ValueError when max_tags is not a valid integer."""
        with pytest.raises(
            ValueError, match="max_tags must be a valid positive integer"
        ):
            analyze_tag_history("/tmp", "not_a_number")

    def test_negative_max_tags(self) -> None:
        """Test ValueError when max_tags is negative."""
        with pytest.raises(
            ValueError, match="max_tags must be a valid positive integer"
        ):
            analyze_tag_history("/tmp", "-5")

    def test_zero_max_tags(self) -> None:
        """Test ValueError when max_tags is zero."""
        with pytest.raises(
            ValueError, match="max_tags must be a valid positive integer"
        ):
            analyze_tag_history("/tmp", "0")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            analyze_tag_history("/nonexistent/path", "10")

    @patch("subprocess.run")
    def test_no_tags(self, mock_run: Mock) -> None:
        """Test when no tags found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            result = analyze_tag_history(tmpdir, "10")
            assert result["total_tags"] == "0"
            assert "Create initial release" in result["recommendation"]

    @patch("subprocess.run")
    def test_with_tags(self, mock_run: Mock) -> None:
        """Test analyzing tag history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "v1.2.3\nv1.2.2\nv1.2.1\nv1.2.0\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = analyze_tag_history(tmpdir, "10")
            assert int(result["total_tags"]) >= 3
            assert result["release_pattern"] in ["major", "minor", "patch", "mixed"]


class TestFindCommitsBetweenTags:
    """Test find_commits_between_tags function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            find_commits_between_tags(123, "v1.0.0", "v2.0.0")  # type: ignore

    def test_invalid_tag1_type(self) -> None:
        """Test TypeError when tag1 is not a string."""
        with pytest.raises(TypeError, match="tag1 must be a string"):
            find_commits_between_tags("/tmp", 123, "v2.0.0")  # type: ignore

    def test_invalid_tag2_type(self) -> None:
        """Test TypeError when tag2 is not a string."""
        with pytest.raises(TypeError, match="tag2 must be a string"):
            find_commits_between_tags("/tmp", "v1.0.0", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            find_commits_between_tags("", "v1.0.0", "v2.0.0")

    def test_empty_tag1(self) -> None:
        """Test ValueError when tag1 is empty."""
        with pytest.raises(ValueError, match="tag1 cannot be empty"):
            find_commits_between_tags("/tmp", "", "v2.0.0")

    def test_empty_tag2(self) -> None:
        """Test ValueError when tag2 is empty."""
        with pytest.raises(ValueError, match="tag2 cannot be empty"):
            find_commits_between_tags("/tmp", "v1.0.0", "")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            find_commits_between_tags("/nonexistent/path", "v1.0.0", "v2.0.0")

    @patch("subprocess.run")
    def test_no_commits(self, mock_run: Mock) -> None:
        """Test when no commits found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            result = find_commits_between_tags(tmpdir, "v1.0.0", "v2.0.0")
            assert result["commit_count"] == "0"
            assert result["has_breaking_changes"] == "false"

    @patch("subprocess.run")
    def test_with_commits(self, mock_run: Mock) -> None:
        """Test finding commits between tags."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "abc123 feat: new feature\ndef456 fix: bug fix\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = find_commits_between_tags(tmpdir, "v1.0.0", "v2.0.0")
            assert int(result["commit_count"]) >= 2
            assert result["has_breaking_changes"] == "false"

    @patch("subprocess.run")
    def test_with_breaking_changes(self, mock_run: Mock) -> None:
        """Test commits with breaking changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "abc123 feat!: BREAKING CHANGE major update\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = find_commits_between_tags(tmpdir, "v1.0.0", "v2.0.0")
            assert result["has_breaking_changes"] == "true"
