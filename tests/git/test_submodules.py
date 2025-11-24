"""Tests for git submodule management and analysis functions."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coding_open_agent_tools.git.submodules import (
    analyze_submodule_updates,
    check_submodule_sync,
    list_submodules,
    validate_submodule_commits,
    validate_submodule_urls,
)


class TestListSubmodules:
    """Test list_submodules function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            list_submodules(123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            list_submodules("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            list_submodules("/nonexistent/path")

    @patch("subprocess.run")
    def test_no_submodules(self, mock_run: Mock) -> None:
        """Test when no submodules exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            result = list_submodules(tmpdir)
            assert result["has_submodules"] == "false"
            assert result["submodule_count"] == "0"

    @patch("subprocess.run")
    def test_with_initialized_submodule(self, mock_run: Mock) -> None:
        """Test with initialized submodule."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = " abc123 path/to/submodule (commit-message)\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = list_submodules(tmpdir)
            assert result["has_submodules"] == "true"
            assert int(result["submodule_count"]) >= 1

    @patch("subprocess.run")
    def test_with_uninitialized_submodule(self, mock_run: Mock) -> None:
        """Test with uninitialized submodule."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "-abc123 path/to/submodule (commit-message)\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = list_submodules(tmpdir)
            assert result["has_submodules"] == "true"
            assert "UNINIT" in result["submodules"]

    @patch("subprocess.run")
    def test_with_modified_submodule(self, mock_run: Mock) -> None:
        """Test with modified submodule."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "+abc123 path/to/submodule (commit-message)\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = list_submodules(tmpdir)
            assert result["has_submodules"] == "true"
            assert "MODIFIED" in result["submodules"]


class TestValidateSubmoduleUrls:
    """Test validate_submodule_urls function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            validate_submodule_urls(123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            validate_submodule_urls("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            validate_submodule_urls("/nonexistent/path")

    def test_no_gitmodules_file(self) -> None:
        """Test when .gitmodules doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = validate_submodule_urls(tmpdir)
            assert result["all_valid"] == "true"
            assert result["url_count"] == "0"

    def test_secure_urls(self) -> None:
        """Test .gitmodules with secure URLs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gitmodules = Path(tmpdir) / ".gitmodules"
            gitmodules.write_text("[submodule \"lib\"]\n\tpath = lib\n\turl = https://github.com/user/lib.git\n")

            result = validate_submodule_urls(tmpdir)
            assert result["all_valid"] == "true"
            assert int(result["url_count"]) >= 1

    def test_insecure_http_url(self) -> None:
        """Test .gitmodules with insecure HTTP URL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gitmodules = Path(tmpdir) / ".gitmodules"
            gitmodules.write_text("[submodule \"lib\"]\n\tpath = lib\n\turl = http://example.com/lib.git\n")

            result = validate_submodule_urls(tmpdir)
            assert result["all_valid"] == "false"
            assert int(result["security_issues"]) >= 1

    def test_git_protocol_url(self) -> None:
        """Test .gitmodules with git:// protocol."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gitmodules = Path(tmpdir) / ".gitmodules"
            gitmodules.write_text("[submodule \"lib\"]\n\tpath = lib\n\turl = git://example.com/lib.git\n")

            result = validate_submodule_urls(tmpdir)
            assert result["all_valid"] == "false"
            assert "GIT protocol" in result["insecure_urls"]


class TestCheckSubmoduleSync:
    """Test check_submodule_sync function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            check_submodule_sync(123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            check_submodule_sync("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            check_submodule_sync("/nonexistent/path")

    @patch("subprocess.run")
    def test_no_submodules(self, mock_run: Mock) -> None:
        """Test when no submodules exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="")
            result = check_submodule_sync(tmpdir)
            assert result["is_synced"] == "true"
            assert "No submodules" in result["recommendation"]

    @patch("subprocess.run")
    def test_in_sync(self, mock_run: Mock) -> None:
        """Test when submodules are in sync."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = " abc123 path/to/submodule\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = check_submodule_sync(tmpdir)
            assert result["is_synced"] == "true"
            assert result["out_of_sync_count"] == "0"

    @patch("subprocess.run")
    def test_out_of_sync(self, mock_run: Mock) -> None:
        """Test when submodules are out of sync."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "+abc123 path/to/submodule\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = check_submodule_sync(tmpdir)
            assert result["is_synced"] == "false"
            assert int(result["out_of_sync_count"]) >= 1


class TestAnalyzeSubmoduleUpdates:
    """Test analyze_submodule_updates function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            analyze_submodule_updates(123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            analyze_submodule_updates("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            analyze_submodule_updates("/nonexistent/path")

    @patch("subprocess.run")
    def test_no_submodules(self, mock_run: Mock) -> None:
        """Test when no submodules exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="")
            result = analyze_submodule_updates(tmpdir)
            assert result["has_updates"] == "false"
            assert "No submodules" in result["update_summary"]

    @patch("subprocess.run")
    def test_no_updates(self, mock_run: Mock) -> None:
        """Test when submodules have no updates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = " abc123 path/to/submodule\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = analyze_submodule_updates(tmpdir)
            assert result["has_updates"] == "false"

    @patch("subprocess.run")
    def test_with_updates(self, mock_run: Mock) -> None:
        """Test when submodules have updates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "+abc123 path/to/submodule\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = analyze_submodule_updates(tmpdir)
            assert result["has_updates"] == "true"
            assert int(result["submodules_with_updates"]) >= 1


class TestValidateSubmoduleCommits:
    """Test validate_submodule_commits function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            validate_submodule_commits(123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            validate_submodule_commits("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            validate_submodule_commits("/nonexistent/path")

    @patch("subprocess.run")
    def test_no_submodules(self, mock_run: Mock) -> None:
        """Test when no submodules exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="")
            result = validate_submodule_commits(tmpdir)
            assert result["all_valid"] == "true"
            assert "No submodules" in result["recommendation"]

    @patch("subprocess.run")
    def test_all_valid(self, mock_run: Mock) -> None:
        """Test when all submodules have valid commits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = " abc123 path/to/submodule\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = validate_submodule_commits(tmpdir)
            assert result["all_valid"] == "true"
            assert result["missing_commits"] == "0"

    @patch("subprocess.run")
    def test_uninitialized_submodule(self, mock_run: Mock) -> None:
        """Test when submodule is uninitialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "-abc123 path/to/submodule\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = validate_submodule_commits(tmpdir)
            assert result["all_valid"] == "false"
            assert int(result["missing_commits"]) >= 1
            assert "Uninitialized" in result["invalid_submodules"]
