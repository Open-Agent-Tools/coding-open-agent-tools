"""Tests for git diff analysis and change inspection functions."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coding_open_agent_tools.git.diffs import (
    analyze_diff_stats,
    calculate_code_churn,
    find_largest_changes,
    get_file_diff,
)


class TestAnalyzeDiffStats:
    """Test analyze_diff_stats function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            analyze_diff_stats(123, "ref1", "ref2")  # type: ignore

    def test_invalid_ref1_type(self) -> None:
        """Test TypeError when ref1 is not a string."""
        with pytest.raises(TypeError, match="ref1 must be a string"):
            analyze_diff_stats("/tmp", 123, "ref2")  # type: ignore

    def test_invalid_ref2_type(self) -> None:
        """Test TypeError when ref2 is not a string."""
        with pytest.raises(TypeError, match="ref2 must be a string"):
            analyze_diff_stats("/tmp", "ref1", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            analyze_diff_stats("", "ref1", "ref2")

    def test_empty_ref1(self) -> None:
        """Test ValueError when ref1 is empty."""
        with pytest.raises(ValueError, match="ref1 cannot be empty"):
            analyze_diff_stats("/tmp", "", "ref2")

    def test_empty_ref2(self) -> None:
        """Test ValueError when ref2 is empty."""
        with pytest.raises(ValueError, match="ref2 cannot be empty"):
            analyze_diff_stats("/tmp", "ref1", "")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            analyze_diff_stats("/nonexistent/path", "ref1", "ref2")

    @patch("subprocess.run")
    def test_git_command_failure(self, mock_run: Mock) -> None:
        """Test behavior when git command fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")
            result = analyze_diff_stats(tmpdir, "ref1", "ref2")
            assert result["files_changed"] == "0"
            assert "Could not compare" in result["summary"]

    @patch("subprocess.run")
    def test_no_differences(self, mock_run: Mock) -> None:
        """Test when no differences found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            result = analyze_diff_stats(tmpdir, "ref1", "ref2")
            assert result["files_changed"] == "0"
            assert "No differences" in result["summary"]

    @patch("subprocess.run")
    def test_with_differences(self, mock_run: Mock) -> None:
        """Test parsing diff stats with changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="5 files changed, 120 insertions(+), 45 deletions(-)",
                stderr=""
            )
            result = analyze_diff_stats(tmpdir, "ref1", "ref2")
            assert result["files_changed"] == "5"
            assert result["insertions"] == "120"
            assert result["deletions"] == "45"
            assert int(result["net_change"]) == 75


class TestCalculateCodeChurn:
    """Test calculate_code_churn function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            calculate_code_churn(123, "file.py", "30")  # type: ignore

    def test_invalid_file_path_type(self) -> None:
        """Test TypeError when file_path is not a string."""
        with pytest.raises(TypeError, match="file_path must be a string"):
            calculate_code_churn("/tmp", 123, "30")  # type: ignore

    def test_invalid_days_type(self) -> None:
        """Test TypeError when days is not a string."""
        with pytest.raises(TypeError, match="days must be a string"):
            calculate_code_churn("/tmp", "file.py", 30)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            calculate_code_churn("", "file.py", "30")

    def test_empty_file_path(self) -> None:
        """Test ValueError when file_path is empty."""
        with pytest.raises(ValueError, match="file_path cannot be empty"):
            calculate_code_churn("/tmp", "", "30")

    def test_invalid_days_format(self) -> None:
        """Test ValueError when days is not a valid integer."""
        with pytest.raises(ValueError, match="days must be a valid positive integer"):
            calculate_code_churn("/tmp", "file.py", "not_a_number")

    def test_negative_days(self) -> None:
        """Test ValueError when days is negative."""
        with pytest.raises(ValueError, match="days must be a valid positive integer"):
            calculate_code_churn("/tmp", "file.py", "-5")

    def test_zero_days(self) -> None:
        """Test ValueError when days is zero."""
        with pytest.raises(ValueError, match="days must be a valid positive integer"):
            calculate_code_churn("/tmp", "file.py", "0")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            calculate_code_churn("/nonexistent/path", "file.py", "30")

    @patch("subprocess.run")
    def test_no_commits(self, mock_run: Mock) -> None:
        """Test when file has no commits in period."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            result = calculate_code_churn(tmpdir, "file.py", "30")
            assert result["total_commits"] == "0"
            assert result["stability"] == "stable"

    @patch("subprocess.run")
    def test_stable_file(self, mock_run: Mock) -> None:
        """Test file with low churn (stable)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # First call: commit count
            call_count = [0]

            def side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return Mock(returncode=0, stdout="abc123 commit1\ndef456 commit2", stderr="")
                else:
                    return Mock(returncode=0, stdout="10\t5\tfile.py\n20\t10\tfile.py", stderr="")

            mock_run.side_effect = side_effect
            result = calculate_code_churn(tmpdir, "file.py", "30")
            assert int(result["total_commits"]) > 0
            assert result["stability"] in ["stable", "moderate", "high_churn"]


class TestGetFileDiff:
    """Test get_file_diff function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            get_file_diff(123, "ref1", "ref2", "file.py")  # type: ignore

    def test_invalid_ref1_type(self) -> None:
        """Test TypeError when ref1 is not a string."""
        with pytest.raises(TypeError, match="ref1 must be a string"):
            get_file_diff("/tmp", 123, "ref2", "file.py")  # type: ignore

    def test_invalid_ref2_type(self) -> None:
        """Test TypeError when ref2 is not a string."""
        with pytest.raises(TypeError, match="ref2 must be a string"):
            get_file_diff("/tmp", "ref1", 123, "file.py")  # type: ignore

    def test_invalid_file_path_type(self) -> None:
        """Test TypeError when file_path is not a string."""
        with pytest.raises(TypeError, match="file_path must be a string"):
            get_file_diff("/tmp", "ref1", "ref2", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            get_file_diff("", "ref1", "ref2", "file.py")

    def test_empty_file_path(self) -> None:
        """Test ValueError when file_path is empty."""
        with pytest.raises(ValueError, match="file_path cannot be empty"):
            get_file_diff("/tmp", "ref1", "ref2", "")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            get_file_diff("/nonexistent/path", "ref1", "ref2", "file.py")

    @patch("subprocess.run")
    def test_no_changes(self, mock_run: Mock) -> None:
        """Test when file has no changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            result = get_file_diff(tmpdir, "ref1", "ref2", "file.py")
            assert result["has_changes"] == "false"
            assert result["lines_added"] == "0"

    @patch("subprocess.run")
    def test_with_changes(self, mock_run: Mock) -> None:
        """Test file with changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            diff_output = """--- a/file.py
+++ b/file.py
+added line 1
+added line 2
-removed line 1"""
            mock_run.return_value = Mock(returncode=0, stdout=diff_output, stderr="")
            result = get_file_diff(tmpdir, "ref1", "ref2", "file.py")
            assert result["has_changes"] == "true"
            assert int(result["lines_added"]) >= 1
            assert int(result["lines_removed"]) >= 1


class TestFindLargestChanges:
    """Test find_largest_changes function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            find_largest_changes(123, "ref1", "ref2", "10")  # type: ignore

    def test_invalid_ref1_type(self) -> None:
        """Test TypeError when ref1 is not a string."""
        with pytest.raises(TypeError, match="ref1 must be a string"):
            find_largest_changes("/tmp", 123, "ref2", "10")  # type: ignore

    def test_invalid_ref2_type(self) -> None:
        """Test TypeError when ref2 is not a string."""
        with pytest.raises(TypeError, match="ref2 must be a string"):
            find_largest_changes("/tmp", "ref1", 123, "10")  # type: ignore

    def test_invalid_limit_type(self) -> None:
        """Test TypeError when limit is not a string."""
        with pytest.raises(TypeError, match="limit must be a string"):
            find_largest_changes("/tmp", "ref1", "ref2", 10)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            find_largest_changes("", "ref1", "ref2", "10")

    def test_invalid_limit_format(self) -> None:
        """Test ValueError when limit is not a valid integer."""
        with pytest.raises(ValueError, match="limit must be a valid positive integer"):
            find_largest_changes("/tmp", "ref1", "ref2", "not_a_number")

    def test_negative_limit(self) -> None:
        """Test ValueError when limit is negative."""
        with pytest.raises(ValueError, match="limit must be a valid positive integer"):
            find_largest_changes("/tmp", "ref1", "ref2", "-5")

    def test_zero_limit(self) -> None:
        """Test ValueError when limit is zero."""
        with pytest.raises(ValueError, match="limit must be a valid positive integer"):
            find_largest_changes("/tmp", "ref1", "ref2", "0")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            find_largest_changes("/nonexistent/path", "ref1", "ref2", "10")

    @patch("subprocess.run")
    def test_git_command_failure(self, mock_run: Mock) -> None:
        """Test behavior when git command fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")
            result = find_largest_changes(tmpdir, "ref1", "ref2", "10")
            assert result["total_files_changed"] == "0"
            assert "Could not compare" in result["largest_changes"]

    @patch("subprocess.run")
    def test_with_changes(self, mock_run: Mock) -> None:
        """Test finding largest changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            numstat_output = """100\t50\tfile1.py
200\t100\tfile2.py
50\t25\tfile3.py"""
            mock_run.return_value = Mock(returncode=0, stdout=numstat_output, stderr="")
            result = find_largest_changes(tmpdir, "ref1", "ref2", "2")
            assert result["total_files_changed"] == "3"
            # Should return top 2 files
            assert "file2.py" in result["largest_changes"]
            assert "file1.py" in result["largest_changes"]
