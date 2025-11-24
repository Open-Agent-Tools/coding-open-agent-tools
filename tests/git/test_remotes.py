"""Tests for git remote repository analysis functions."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coding_open_agent_tools.git.remotes import (
    analyze_remote_branches,
    check_remote_connectivity,
    check_remote_sync_status,
    list_remotes,
    validate_remote_url_security,
)


class TestListRemotes:
    """Test list_remotes function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            list_remotes(123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            list_remotes("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            list_remotes("/nonexistent/path")

    @patch("subprocess.run")
    def test_no_remotes(self, mock_run: Mock) -> None:
        """Test when no remotes configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            result = list_remotes(tmpdir)
            assert result["has_remotes"] == "false"
            assert result["remote_count"] == "0"

    @patch("subprocess.run")
    def test_with_remotes(self, mock_run: Mock) -> None:
        """Test listing remotes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "origin\thttps://github.com/user/repo.git (fetch)\norigin\thttps://github.com/user/repo.git (push)\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = list_remotes(tmpdir)
            assert result["has_remotes"] == "true"
            assert int(result["remote_count"]) >= 1
            assert result["primary_remote"] == "origin"


class TestCheckRemoteConnectivity:
    """Test check_remote_connectivity function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            check_remote_connectivity(123, "origin")  # type: ignore

    def test_invalid_remote_name_type(self) -> None:
        """Test TypeError when remote_name is not a string."""
        with pytest.raises(TypeError, match="remote_name must be a string"):
            check_remote_connectivity("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            check_remote_connectivity("", "origin")

    def test_empty_remote_name(self) -> None:
        """Test ValueError when remote_name is empty."""
        with pytest.raises(ValueError, match="remote_name cannot be empty"):
            check_remote_connectivity("/tmp", "")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            check_remote_connectivity("/nonexistent/path", "origin")

    @patch("subprocess.run")
    def test_remote_not_found(self, mock_run: Mock) -> None:
        """Test when remote doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="")
            result = check_remote_connectivity(tmpdir, "nonexistent")
            assert result["is_reachable"] == "false"
            assert "not found" in result["error_message"]

    @patch("subprocess.run")
    def test_timeout(self, mock_run: Mock) -> None:
        """Test timeout handling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.side_effect = subprocess.TimeoutExpired("git", 30)
            result = check_remote_connectivity(tmpdir, "origin")
            assert result["is_reachable"] == "false"
            assert "timeout" in result["error_message"]


class TestAnalyzeRemoteBranches:
    """Test analyze_remote_branches function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            analyze_remote_branches(123, "origin")  # type: ignore

    def test_invalid_remote_name_type(self) -> None:
        """Test TypeError when remote_name is not a string."""
        with pytest.raises(TypeError, match="remote_name must be a string"):
            analyze_remote_branches("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            analyze_remote_branches("", "origin")

    def test_empty_remote_name(self) -> None:
        """Test ValueError when remote_name is empty."""
        with pytest.raises(ValueError, match="remote_name cannot be empty"):
            analyze_remote_branches("/tmp", "")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            analyze_remote_branches("/nonexistent/path", "origin")

    @patch("subprocess.run")
    def test_with_branches(self, mock_run: Mock) -> None:
        """Test analyzing remote branches."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "abc123\trefs/heads/main\ndef456\trefs/heads/develop\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = analyze_remote_branches(tmpdir, "origin")
            assert int(result["branch_count"]) >= 1
            assert result["has_main"] == "true"


class TestCheckRemoteSyncStatus:
    """Test check_remote_sync_status function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            check_remote_sync_status(123, "main")  # type: ignore

    def test_invalid_branch_name_type(self) -> None:
        """Test TypeError when branch_name is not a string."""
        with pytest.raises(TypeError, match="branch_name must be a string"):
            check_remote_sync_status("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            check_remote_sync_status("", "main")

    def test_empty_branch_name(self) -> None:
        """Test ValueError when branch_name is empty."""
        with pytest.raises(ValueError, match="branch_name cannot be empty"):
            check_remote_sync_status("/tmp", "")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            check_remote_sync_status("/nonexistent/path", "main")

    @patch("subprocess.run")
    def test_in_sync(self, mock_run: Mock) -> None:
        """Test branch in sync with remote."""
        with tempfile.TemporaryDirectory() as tmpdir:
            call_count = [0]

            def side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:  # fetch
                    return Mock(returncode=0, stdout="", stderr="")
                else:  # rev-list
                    return Mock(returncode=0, stdout="0\t0", stderr="")

            mock_run.side_effect = side_effect
            result = check_remote_sync_status(tmpdir, "main")
            assert result["is_synced"] == "true"
            assert result["commits_ahead"] == "0"
            assert result["commits_behind"] == "0"


class TestValidateRemoteUrlSecurity:
    """Test validate_remote_url_security function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            validate_remote_url_security(123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            validate_remote_url_security("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            validate_remote_url_security("/nonexistent/path")

    @patch("subprocess.run")
    def test_secure_urls(self, mock_run: Mock) -> None:
        """Test with secure URLs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "origin\thttps://github.com/user/repo.git (fetch)\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = validate_remote_url_security(tmpdir)
            assert result["all_secure"] == "true"
            assert result["insecure_count"] == "0"

    @patch("subprocess.run")
    def test_insecure_http_url(self, mock_run: Mock) -> None:
        """Test with insecure HTTP URL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "origin\thttp://example.com/repo.git (fetch)\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = validate_remote_url_security(tmpdir)
            assert result["all_secure"] == "false"
            assert int(result["insecure_count"]) >= 1

    @patch("subprocess.run")
    def test_git_protocol(self, mock_run: Mock) -> None:
        """Test with deprecated git:// protocol."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "origin\tgit://example.com/repo.git (fetch)\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = validate_remote_url_security(tmpdir)
            assert result["all_secure"] == "false"
            assert int(result["insecure_count"]) >= 1
