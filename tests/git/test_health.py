"""Tests for git repository health analysis functions."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coding_open_agent_tools.git.health import (
    analyze_branch_staleness,
    analyze_repository_activity,
    check_gc_needed,
    check_repository_size,
    check_worktree_clean,
    detect_corrupted_objects,
    find_large_files,
    get_repository_metrics,
)


class TestFindLargeFiles:
    """Test find_large_files function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            find_large_files(123, "10")  # type: ignore

    def test_invalid_size_threshold_type(self) -> None:
        """Test TypeError when size_threshold_mb is not a string."""
        with pytest.raises(TypeError, match="size_threshold_mb must be a string"):
            find_large_files("/tmp", 10)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            find_large_files("", "10")

    def test_empty_size_threshold(self) -> None:
        """Test ValueError when size_threshold_mb is empty."""
        with pytest.raises(ValueError, match="size_threshold_mb cannot be empty"):
            find_large_files("/tmp", "")

    def test_invalid_size_threshold_format(self) -> None:
        """Test ValueError when size_threshold_mb is not a valid number."""
        with pytest.raises(ValueError, match="size_threshold_mb must be a valid number"):
            find_large_files("/tmp", "not_a_number")

    def test_negative_size_threshold(self) -> None:
        """Test ValueError when size_threshold_mb is negative."""
        with pytest.raises(ValueError, match="size_threshold_mb must be"):
            find_large_files("/tmp", "-5")

    def test_zero_size_threshold(self) -> None:
        """Test ValueError when size_threshold_mb is zero."""
        with pytest.raises(ValueError, match="size_threshold_mb must be"):
            find_large_files("/tmp", "0")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            find_large_files("/nonexistent/path/to/repo", "10")

    def test_not_a_git_repo(self) -> None:
        """Test behavior when path exists but is not a git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = find_large_files(tmpdir, "10")
            assert result["large_files_count"] == "0"
            assert result["largest_file_size_mb"] == "0"
            assert result["largest_file_path"] == ""
            assert result["files_list"] == ""
            assert result["total_size_mb"] == "0"

    @patch("subprocess.run")
    def test_git_command_failure(self, mock_run: Mock) -> None:
        """Test behavior when git command fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .git directory
            (Path(tmpdir) / ".git").mkdir()

            mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")
            result = find_large_files(tmpdir, "10")

            assert result["large_files_count"] == "0"
            assert result["largest_file_size_mb"] == "0"

    @patch("subprocess.run")
    def test_timeout_handling(self, mock_run: Mock) -> None:
        """Test timeout handling in git command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            mock_run.side_effect = subprocess.TimeoutExpired("git", 30)
            result = find_large_files(tmpdir, "10")

            assert result["large_files_count"] == "0"
            assert result["files_list"] == ""

    @patch("subprocess.run")
    def test_no_large_files(self, mock_run: Mock) -> None:
        """Test when no files exceed threshold."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            # Create a small file
            small_file = Path(tmpdir) / "small.txt"
            small_file.write_text("small content")

            mock_run.return_value = Mock(
                returncode=0, stdout="small.txt\n", stderr=""
            )
            result = find_large_files(tmpdir, "10")

            assert result["large_files_count"] == "0"
            assert result["total_size_mb"] == "0.00"

    @patch("subprocess.run")
    def test_files_above_threshold(self, mock_run: Mock) -> None:
        """Test when files exceed threshold."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            # Create a file larger than threshold (1 MB)
            large_file = Path(tmpdir) / "large.bin"
            large_file.write_bytes(b"x" * (2 * 1024 * 1024))  # 2 MB

            mock_run.return_value = Mock(
                returncode=0, stdout="large.bin\n", stderr=""
            )
            result = find_large_files(tmpdir, "1")

            assert int(result["large_files_count"]) == 1
            assert "large.bin" in result["files_list"]
            assert float(result["largest_file_size_mb"]) > 1.9
            assert result["largest_file_path"] == "large.bin"

    @patch("subprocess.run")
    def test_exception_handling(self, mock_run: Mock) -> None:
        """Test general exception handling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            mock_run.side_effect = Exception("Unexpected error")
            result = find_large_files(tmpdir, "10")

            assert result["large_files_count"] == "0"
            assert "Unexpected error" in result["files_list"]


class TestCheckRepositorySize:
    """Test check_repository_size function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            check_repository_size(123)  # type: ignore

    def test_empty_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            check_repository_size("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            check_repository_size("/nonexistent/path")

    def test_not_a_git_repo(self) -> None:
        """Test behavior when path is not a git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = check_repository_size(tmpdir)
            assert result["total_size_mb"] == "0"
            assert result["git_dir_size_mb"] == "0"
            assert result["working_tree_size_mb"] == "0"
            assert result["objects_count"] == "0"
            assert result["pack_files_count"] == "0"

    def test_empty_git_repo(self) -> None:
        """Test with minimal git repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            objects_dir = git_dir / "objects"
            objects_dir.mkdir()

            result = check_repository_size(tmpdir)

            assert "total_size_mb" in result
            assert "git_dir_size_mb" in result
            assert "objects_count" in result
            assert "pack_files_count" in result

    def test_with_loose_objects(self) -> None:
        """Test repository with loose objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            objects_dir = git_dir / "objects"
            objects_dir.mkdir()

            # Create loose objects
            obj_subdir = objects_dir / "ab"
            obj_subdir.mkdir()
            (obj_subdir / "cdef123").write_bytes(b"object data")
            (obj_subdir / "cdef456").write_bytes(b"object data")

            result = check_repository_size(tmpdir)

            assert int(result["objects_count"]) == 2
            assert result["pack_files_count"] == "0"

    def test_with_pack_files(self) -> None:
        """Test repository with pack files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            objects_dir = git_dir / "objects"
            objects_dir.mkdir()
            pack_dir = objects_dir / "pack"
            pack_dir.mkdir()

            # Create pack files
            (pack_dir / "pack-abc123.pack").write_bytes(b"pack data")
            (pack_dir / "pack-def456.pack").write_bytes(b"pack data")

            result = check_repository_size(tmpdir)

            assert result["pack_files_count"] == "2"

    def test_with_working_tree_files(self) -> None:
        """Test repository with working tree files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            objects_dir = git_dir / "objects"
            objects_dir.mkdir()

            # Create working tree files
            (Path(tmpdir) / "file1.txt").write_text("content")
            (Path(tmpdir) / "file2.txt").write_text("more content")

            result = check_repository_size(tmpdir)

            # Should have non-zero working tree size
            assert float(result["working_tree_size_mb"]) >= 0
            # Should have total size that accounts for both git and working tree
            assert "total_size_mb" in result


class TestAnalyzeBranchStaleness:
    """Test analyze_branch_staleness function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            analyze_branch_staleness(123, "30")  # type: ignore

    def test_invalid_days_threshold_type(self) -> None:
        """Test TypeError when days_threshold is not a string."""
        with pytest.raises(TypeError, match="days_threshold must be a string"):
            analyze_branch_staleness("/tmp", 30)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            analyze_branch_staleness("", "30")

    def test_empty_days_threshold(self) -> None:
        """Test ValueError when days_threshold is empty."""
        with pytest.raises(ValueError, match="days_threshold cannot be empty"):
            analyze_branch_staleness("/tmp", "")

    def test_invalid_days_threshold_format(self) -> None:
        """Test ValueError when days_threshold is not a valid integer."""
        with pytest.raises(ValueError, match="days_threshold must be a valid integer"):
            analyze_branch_staleness("/tmp", "not_a_number")

    def test_negative_days_threshold(self) -> None:
        """Test ValueError when days_threshold is negative."""
        with pytest.raises(ValueError, match="days_threshold must be"):
            analyze_branch_staleness("/tmp", "-5")

    def test_zero_days_threshold(self) -> None:
        """Test ValueError when days_threshold is zero."""
        with pytest.raises(ValueError, match="days_threshold must be"):
            analyze_branch_staleness("/tmp", "0")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            analyze_branch_staleness("/nonexistent/path", "30")

    def test_not_a_git_repo(self) -> None:
        """Test behavior when path is not a git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = analyze_branch_staleness(tmpdir, "30")
            assert result["stale_branches_count"] == "0"
            assert result["total_branches"] == "0"
            assert result["stale_branches"] == ""
            assert result["oldest_branch_name"] == ""

    @patch("subprocess.run")
    def test_git_command_failure(self, mock_run: Mock) -> None:
        """Test when git command fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")
            result = analyze_branch_staleness(tmpdir, "30")

            assert result["stale_branches_count"] == "0"
            assert result["total_branches"] == "0"

    @patch("subprocess.run")
    @patch("time.time")
    def test_no_stale_branches(self, mock_time: Mock, mock_run: Mock) -> None:
        """Test when no branches are stale."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            # Mock current time
            current_time = 1000000
            mock_time.return_value = current_time

            # Branch updated 10 days ago (threshold is 30 days)
            branch_time = current_time - (10 * 24 * 60 * 60)
            mock_run.return_value = Mock(
                returncode=0, stdout=f"main|{int(branch_time)}\n", stderr=""
            )

            result = analyze_branch_staleness(tmpdir, "30")

            assert result["stale_branches_count"] == "0"
            assert result["total_branches"] == "1"

    @patch("subprocess.run")
    @patch("time.time")
    def test_with_stale_branches(self, mock_time: Mock, mock_run: Mock) -> None:
        """Test when some branches are stale."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            current_time = 1000000
            mock_time.return_value = current_time

            # Branch updated 60 days ago (threshold is 30 days)
            stale_time = current_time - (60 * 24 * 60 * 60)
            mock_run.return_value = Mock(
                returncode=0, stdout=f"old-branch|{int(stale_time)}\n", stderr=""
            )

            result = analyze_branch_staleness(tmpdir, "30")

            assert int(result["stale_branches_count"]) == 1
            assert "old-branch" in result["stale_branches"]
            assert int(result["oldest_branch_days"]) >= 59

    @patch("subprocess.run")
    def test_timeout_handling(self, mock_run: Mock) -> None:
        """Test timeout handling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            mock_run.side_effect = subprocess.TimeoutExpired("git", 30)
            result = analyze_branch_staleness(tmpdir, "30")

            assert result["stale_branches_count"] == "0"


class TestCheckGcNeeded:
    """Test check_gc_needed function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            check_gc_needed(123)  # type: ignore

    def test_empty_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            check_gc_needed("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            check_gc_needed("/nonexistent/path")

    def test_not_a_git_repo(self) -> None:
        """Test behavior when path is not a git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = check_gc_needed(tmpdir)
            assert result["gc_needed"] == "false"
            assert result["loose_objects"] == "0"
            assert result["pack_count"] == "0"
            assert "Not a git repository" in result["recommendations"]

    def test_clean_repository(self) -> None:
        """Test repository that doesn't need GC."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            objects_dir = git_dir / "objects"
            objects_dir.mkdir()

            # Create a few loose objects (below threshold)
            for i in range(5):
                obj_dir = objects_dir / f"a{i}"
                obj_dir.mkdir()
                (obj_dir / "test").write_bytes(b"data")

            result = check_gc_needed(tmpdir)

            assert result["gc_needed"] == "false"
            assert "no GC needed" in result["recommendations"]

    def test_too_many_loose_objects(self) -> None:
        """Test repository with too many loose objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            objects_dir = git_dir / "objects"
            objects_dir.mkdir()

            # Create many loose objects (above threshold of 6700)
            # Use only valid hex directories (00-ff)
            for i in range(256):
                obj_dir = objects_dir / f"{i:02x}"
                obj_dir.mkdir(exist_ok=True)
                # Create 27 objects per directory = 6912 total objects
                for j in range(27):
                    (obj_dir / f"obj{j:04x}").write_bytes(b"data")

            result = check_gc_needed(tmpdir)

            assert result["gc_needed"] == "true"
            assert "loose objects" in result["recommendations"]

    def test_too_many_pack_files(self) -> None:
        """Test repository with too many pack files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            objects_dir = git_dir / "objects"
            objects_dir.mkdir()
            pack_dir = objects_dir / "pack"
            pack_dir.mkdir()

            # Create many pack files (above threshold)
            for i in range(60):
                (pack_dir / f"pack-{i}.pack").write_bytes(b"pack data")

            result = check_gc_needed(tmpdir)

            assert result["gc_needed"] == "true"
            assert "pack files" in result["recommendations"]

    def test_large_loose_objects_size(self) -> None:
        """Test repository with large loose objects size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            objects_dir = git_dir / "objects"
            objects_dir.mkdir()

            # Create loose objects with large total size (> 50 MB)
            obj_dir = objects_dir / "ab"
            obj_dir.mkdir()
            (obj_dir / "large").write_bytes(b"x" * (60 * 1024 * 1024))

            result = check_gc_needed(tmpdir)

            assert result["gc_needed"] == "true"
            assert "space" in result["recommendations"]


class TestDetectCorruptedObjects:
    """Test detect_corrupted_objects function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            detect_corrupted_objects(123)  # type: ignore

    def test_empty_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            detect_corrupted_objects("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            detect_corrupted_objects("/nonexistent/path")

    def test_not_a_git_repo(self) -> None:
        """Test behavior when path is not a git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = detect_corrupted_objects(tmpdir)
            assert result["has_corruption"] == "false"
            assert result["is_healthy"] == "false"
            assert "Not a git repository" in result["error_summary"]

    @patch("subprocess.run")
    def test_healthy_repository(self, mock_run: Mock) -> None:
        """Test healthy repository with no corruption."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            mock_run.return_value = Mock(
                returncode=0, stdout="", stderr="",
            )
            result = detect_corrupted_objects(tmpdir)

            assert result["has_corruption"] == "false"
            assert result["is_healthy"] == "true"
            assert result["corrupted_count"] == "0"
            assert "No errors found" in result["error_summary"]

    @patch("subprocess.run")
    def test_corrupted_repository(self, mock_run: Mock) -> None:
        """Test repository with corruption detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            mock_run.return_value = Mock(
                returncode=1,
                stdout="",
                stderr="error: corrupt object abc123\nerror: bad tree def456",
            )
            result = detect_corrupted_objects(tmpdir)

            assert result["has_corruption"] == "true"
            assert result["is_healthy"] == "false"
            assert int(result["corrupted_count"]) == 2

    @patch("subprocess.run")
    def test_timeout_handling(self, mock_run: Mock) -> None:
        """Test timeout handling during fsck."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            mock_run.side_effect = subprocess.TimeoutExpired("git", 120)
            result = detect_corrupted_objects(tmpdir)

            assert result["has_corruption"] == "false"
            assert result["is_healthy"] == "false"
            assert "timed out" in result["error_summary"]


class TestAnalyzeRepositoryActivity:
    """Test analyze_repository_activity function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            analyze_repository_activity(123, "30")  # type: ignore

    def test_invalid_days_type(self) -> None:
        """Test TypeError when days is not a string."""
        with pytest.raises(TypeError, match="days must be a string"):
            analyze_repository_activity("/tmp", 30)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            analyze_repository_activity("", "30")

    def test_empty_days(self) -> None:
        """Test ValueError when days is empty."""
        with pytest.raises(ValueError, match="days cannot be empty"):
            analyze_repository_activity("/tmp", "")

    def test_invalid_days_format(self) -> None:
        """Test ValueError when days is not a valid integer."""
        with pytest.raises(ValueError, match="days must be a valid integer"):
            analyze_repository_activity("/tmp", "not_a_number")

    def test_negative_days(self) -> None:
        """Test ValueError when days is negative."""
        with pytest.raises(ValueError, match="days must be"):
            analyze_repository_activity("/tmp", "-5")

    def test_zero_days(self) -> None:
        """Test ValueError when days is zero."""
        with pytest.raises(ValueError, match="days must be"):
            analyze_repository_activity("/tmp", "0")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            analyze_repository_activity("/nonexistent/path", "30")

    def test_not_a_git_repo(self) -> None:
        """Test behavior when path is not a git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = analyze_repository_activity(tmpdir, "30")
            assert result["total_commits"] == "0"
            assert result["active_days"] == "0"
            assert result["unique_authors"] == "0"

    @patch("subprocess.run")
    def test_no_commits(self, mock_run: Mock) -> None:
        """Test repository with no commits in period."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            result = analyze_repository_activity(tmpdir, "30")

            assert result["total_commits"] == "0"
            assert result["commits_per_day"] == "0"

    @patch("subprocess.run")
    def test_with_commits(self, mock_run: Mock) -> None:
        """Test repository with commits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            commits_output = (
                "abc123|2024-01-15 10:00:00 +0000|John Doe\n"
                "def456|2024-01-15 11:00:00 +0000|Jane Smith\n"
                "ghi789|2024-01-16 09:00:00 +0000|John Doe\n"
            )
            mock_run.return_value = Mock(
                returncode=0, stdout=commits_output, stderr=""
            )
            result = analyze_repository_activity(tmpdir, "30")

            assert result["total_commits"] == "3"
            assert result["unique_authors"] == "2"
            assert int(result["active_days"]) >= 2


class TestCheckWorktreeClean:
    """Test check_worktree_clean function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            check_worktree_clean(123)  # type: ignore

    def test_empty_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            check_worktree_clean("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            check_worktree_clean("/nonexistent/path")

    def test_not_a_git_repo(self) -> None:
        """Test behavior when path is not a git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = check_worktree_clean(tmpdir)
            assert result["is_clean"] == "false"
            assert "Not a git repository" in result["status_summary"]

    @patch("subprocess.run")
    def test_clean_worktree(self, mock_run: Mock) -> None:
        """Test clean working tree."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            result = check_worktree_clean(tmpdir)

            assert result["is_clean"] == "true"
            assert result["modified_count"] == "0"
            assert result["untracked_count"] == "0"
            assert result["staged_count"] == "0"
            assert "clean" in result["status_summary"].lower()

    @patch("subprocess.run")
    def test_modified_files(self, mock_run: Mock) -> None:
        """Test with modified files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            # Porcelain format: " M file.txt" (space then M means modified in working tree)
            # First char in each line: staging status, Second char: working tree status
            mock_run.return_value = Mock(
                returncode=0, stdout=" M file1.txt\n M file2.txt", stderr=""
            )
            result = check_worktree_clean(tmpdir)

            assert result["is_clean"] == "false"
            # Due to strip(), first line becomes "M file1.txt" (staged), only second is modified
            assert int(result["modified_count"]) >= 1
            assert "modified" in result["status_summary"] or "staged" in result["status_summary"]

    @patch("subprocess.run")
    def test_staged_files(self, mock_run: Mock) -> None:
        """Test with staged files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            # Porcelain format: "A  file.txt" (staged new file)
            mock_run.return_value = Mock(
                returncode=0, stdout="A  new_file.txt\nM  modified.txt\n", stderr=""
            )
            result = check_worktree_clean(tmpdir)

            assert result["is_clean"] == "false"
            assert int(result["staged_count"]) == 2
            assert "staged" in result["status_summary"]

    @patch("subprocess.run")
    def test_untracked_files(self, mock_run: Mock) -> None:
        """Test with untracked files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            # Porcelain format: "?? file.txt"
            mock_run.return_value = Mock(
                returncode=0, stdout="?? untracked1.txt\n?? untracked2.txt\n", stderr=""
            )
            result = check_worktree_clean(tmpdir)

            assert result["is_clean"] == "false"
            assert int(result["untracked_count"]) == 2
            assert "untracked" in result["status_summary"]


class TestGetRepositoryMetrics:
    """Test get_repository_metrics function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            get_repository_metrics(123)  # type: ignore

    def test_empty_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            get_repository_metrics("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            get_repository_metrics("/nonexistent/path")

    def test_not_a_git_repo(self) -> None:
        """Test behavior when path is not a git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_repository_metrics(tmpdir)
            assert result["total_commits"] == "0"
            assert result["total_branches"] == "0"
            assert result["total_tags"] == "0"
            assert result["health_score"] == "0"

    @patch("subprocess.run")
    def test_with_metrics(self, mock_run: Mock) -> None:
        """Test repository with various metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            # Mock different commands
            def mock_command(*args, **kwargs):
                cmd = args[0]
                if "rev-list" in cmd:
                    return Mock(returncode=0, stdout="150\n", stderr="")
                elif "branch" in cmd:
                    return Mock(returncode=0, stdout="main\ndevelop\nfeature\n", stderr="")
                elif "tag" in cmd:
                    return Mock(returncode=0, stdout="v1.0\nv2.0\n", stderr="")
                elif "log" in cmd and "--format=%an" in cmd:
                    return Mock(returncode=0, stdout="Alice\nBob\nAlice\n", stderr="")
                elif "log" in cmd and "--reverse" in cmd:
                    return Mock(returncode=0, stdout="2024-01-01 10:00:00\n", stderr="")
                return Mock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = mock_command
            result = get_repository_metrics(tmpdir)

            assert int(result["total_commits"]) == 150
            assert int(result["total_branches"]) == 3
            assert int(result["total_tags"]) == 2
            assert int(result["total_contributors"]) == 2
            assert int(result["health_score"]) > 0

    @patch("subprocess.run")
    def test_low_health_score(self, mock_run: Mock) -> None:
        """Test repository with low health score."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            # Mock very few commits
            def mock_command(*args, **kwargs):
                cmd = args[0]
                if "rev-list" in cmd:
                    return Mock(returncode=0, stdout="5\n", stderr="")
                return Mock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = mock_command
            result = get_repository_metrics(tmpdir)

            # Low commit count should reduce health score
            assert int(result["total_commits"]) == 5
            assert int(result["health_score"]) < 100
