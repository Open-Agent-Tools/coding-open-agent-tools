"""Tests for git workflow validation and analysis functions."""

import tempfile
from unittest.mock import Mock, patch

import pytest

from coding_open_agent_tools.git.workflows import (
    analyze_merge_strategy,
    check_protected_branches,
    validate_branch_naming,
    validate_commit_frequency,
    validate_gitflow_workflow,
    validate_trunk_based_workflow,
)


class TestValidateGitflowWorkflow:
    """Test validate_gitflow_workflow function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            validate_gitflow_workflow(123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            validate_gitflow_workflow("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            validate_gitflow_workflow("/nonexistent/path")

    @patch("subprocess.run")
    def test_gitflow_compliant(self, mock_run: Mock) -> None:
        """Test gitflow-compliant repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "main\ndevelop\nfeature/test\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = validate_gitflow_workflow(tmpdir)
            assert result["has_main"] == "true"
            assert result["has_develop"] == "true"
            assert int(result["compliance_score"]) >= 80

    @patch("subprocess.run")
    def test_non_gitflow(self, mock_run: Mock) -> None:
        """Test non-gitflow repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "main\nrandom-branch\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = validate_gitflow_workflow(tmpdir)
            assert result["is_gitflow"] == "false"


class TestValidateTrunkBasedWorkflow:
    """Test validate_trunk_based_workflow function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            validate_trunk_based_workflow(123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            validate_trunk_based_workflow("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            validate_trunk_based_workflow("/nonexistent/path")

    @patch("subprocess.run")
    def test_trunk_based_compliant(self, mock_run: Mock) -> None:
        """Test trunk-based repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "main\nfeature-1\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = validate_trunk_based_workflow(tmpdir)
            assert result["main_branch"] in ["main", "master", ""]
            assert int(result["long_lived_branches"]) >= 0


class TestValidateBranchNaming:
    """Test validate_branch_naming function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            validate_branch_naming(123, ".*")  # type: ignore

    def test_invalid_pattern_type(self) -> None:
        """Test TypeError when pattern is not a string."""
        with pytest.raises(TypeError, match="pattern must be a string"):
            validate_branch_naming("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            validate_branch_naming("", ".*")

    def test_empty_pattern(self) -> None:
        """Test ValueError when pattern is empty."""
        with pytest.raises(ValueError, match="pattern cannot be empty"):
            validate_branch_naming("/tmp", "")

    def test_invalid_regex(self) -> None:
        """Test ValueError when pattern is invalid regex."""
        with pytest.raises(ValueError, match="pattern must be a valid regex"):
            validate_branch_naming("/tmp", "[invalid")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            validate_branch_naming("/nonexistent/path", ".*")

    @patch("subprocess.run")
    def test_valid_branches(self, mock_run: Mock) -> None:
        """Test all branches match pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "feature/test\nfeature/test2\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = validate_branch_naming(tmpdir, r"^feature/.*")
            assert result["all_valid"] == "true"
            assert result["invalid_count"] == "0"

    @patch("subprocess.run")
    def test_invalid_branches(self, mock_run: Mock) -> None:
        """Test some branches don't match pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "feature/test\nrandom\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = validate_branch_naming(tmpdir, r"^feature/.*")
            assert result["all_valid"] == "false"
            assert int(result["invalid_count"]) >= 1


class TestCheckProtectedBranches:
    """Test check_protected_branches function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            check_protected_branches(123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            check_protected_branches("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            check_protected_branches("/nonexistent/path")

    @patch("subprocess.run")
    def test_no_protections(self, mock_run: Mock) -> None:
        """Test repository with no branch protections."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="")
            result = check_protected_branches(tmpdir)
            assert result["has_protections"] == "false"


class TestAnalyzeMergeStrategy:
    """Test analyze_merge_strategy function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            analyze_merge_strategy(123, "main")  # type: ignore

    def test_invalid_branch_name_type(self) -> None:
        """Test TypeError when branch_name is not a string."""
        with pytest.raises(TypeError, match="branch_name must be a string"):
            analyze_merge_strategy("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            analyze_merge_strategy("", "main")

    def test_empty_branch_name(self) -> None:
        """Test ValueError when branch_name is empty."""
        with pytest.raises(ValueError, match="branch_name cannot be empty"):
            analyze_merge_strategy("/tmp", "")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            analyze_merge_strategy("/nonexistent/path", "main")

    @patch("subprocess.run")
    def test_merge_strategy(self, mock_run: Mock) -> None:
        """Test analyzing merge strategy."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "abc123 Merge branch 'feature'\ndef456 Add feature\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = analyze_merge_strategy(tmpdir, "main")
            assert result["dominant_strategy"] in ["merge", "rebase", "squash", "unknown"]


class TestValidateCommitFrequency:
    """Test validate_commit_frequency function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            validate_commit_frequency(123, "main", "30")  # type: ignore

    def test_invalid_branch_name_type(self) -> None:
        """Test TypeError when branch_name is not a string."""
        with pytest.raises(TypeError, match="branch_name must be a string"):
            validate_commit_frequency("/tmp", 123, "30")  # type: ignore

    def test_invalid_days_type(self) -> None:
        """Test TypeError when days is not a string."""
        with pytest.raises(TypeError, match="days must be a string"):
            validate_commit_frequency("/tmp", "main", 30)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            validate_commit_frequency("", "main", "30")

    def test_empty_branch_name(self) -> None:
        """Test ValueError when branch_name is empty."""
        with pytest.raises(ValueError, match="branch_name cannot be empty"):
            validate_commit_frequency("/tmp", "", "30")

    def test_invalid_days_format(self) -> None:
        """Test ValueError when days is not a valid integer."""
        with pytest.raises(ValueError, match="days must be a valid positive integer"):
            validate_commit_frequency("/tmp", "main", "not_a_number")

    def test_negative_days(self) -> None:
        """Test ValueError when days is negative."""
        with pytest.raises(ValueError, match="days must be a valid positive integer"):
            validate_commit_frequency("/tmp", "main", "-5")

    def test_zero_days(self) -> None:
        """Test ValueError when days is zero."""
        with pytest.raises(ValueError, match="days must be a valid positive integer"):
            validate_commit_frequency("/tmp", "main", "0")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            validate_commit_frequency("/nonexistent/path", "main", "30")

    @patch("subprocess.run")
    def test_active_branch(self, mock_run: Mock) -> None:
        """Test active branch."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = "abc123 commit1\ndef456 commit2\nghi789 commit3\n"
            mock_run.return_value = Mock(returncode=0, stdout=output, stderr="")
            result = validate_commit_frequency(tmpdir, "main", "7")
            assert int(result["total_commits"]) >= 0
            assert result["is_active"] in ["true", "false"]
