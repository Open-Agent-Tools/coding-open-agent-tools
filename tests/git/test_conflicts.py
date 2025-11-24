"""Tests for git merge conflict detection and analysis functions."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coding_open_agent_tools.git.conflicts import (
    analyze_conflict_complexity,
    detect_merge_conflicts,
    get_conflict_context,
    parse_conflict_markers,
    predict_merge_conflicts,
    suggest_conflict_resolution,
)


class TestDetectMergeConflicts:
    """Test detect_merge_conflicts function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            detect_merge_conflicts(123)  # type: ignore

    def test_empty_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            detect_merge_conflicts("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            detect_merge_conflicts("/nonexistent/path")

    def test_not_a_git_repo(self) -> None:
        """Test behavior when path is not a git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = detect_merge_conflicts(tmpdir)
            assert result["has_conflicts"] == "false"
            assert result["conflicted_files_count"] == "0"
            assert result["in_merge"] == "false"

    @patch("subprocess.run")
    def test_no_conflicts(self, mock_run: Mock) -> None:
        """Test repository with no conflicts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            result = detect_merge_conflicts(tmpdir)

            assert result["has_conflicts"] == "false"
            assert result["conflicted_files_count"] == "0"
            assert result["in_merge"] == "false"

    @patch("subprocess.run")
    def test_with_conflicts(self, mock_run: Mock) -> None:
        """Test repository with active conflicts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()

            # Create MERGE_HEAD to simulate merge in progress
            merge_head = git_dir / "MERGE_HEAD"
            merge_head.write_text("abc123def456\n")

            mock_run.return_value = Mock(
                returncode=0, stdout="file1.txt\nfile2.py\n", stderr=""
            )
            result = detect_merge_conflicts(tmpdir)

            assert result["has_conflicts"] == "true"
            assert result["conflicted_files_count"] == "2"
            assert result["in_merge"] == "true"
            assert result["merge_head"] == "abc123def456"
            assert "file1.txt" in result["conflicted_files"]
            assert "file2.py" in result["conflicted_files"]

    @patch("subprocess.run")
    def test_timeout_handling(self, mock_run: Mock) -> None:
        """Test timeout handling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            mock_run.side_effect = subprocess.TimeoutExpired("git", 30)
            result = detect_merge_conflicts(tmpdir)

            assert result["has_conflicts"] == "false"


class TestParseConflictMarkers:
    """Test parse_conflict_markers function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when file_content is not a string."""
        with pytest.raises(TypeError, match="file_content must be a string"):
            parse_conflict_markers(123)  # type: ignore

    def test_empty_content(self) -> None:
        """Test empty file content."""
        result = parse_conflict_markers("")

        assert result["has_conflicts"] == "false"
        assert result["conflict_count"] == "0"
        assert result["ours_lines"] == "0"
        assert result["theirs_lines"] == "0"

    def test_no_conflicts(self) -> None:
        """Test file with no conflict markers."""
        content = """def hello():
    print("Hello, World!")
"""
        result = parse_conflict_markers(content)

        assert result["has_conflicts"] == "false"
        assert result["conflict_count"] == "0"

    def test_single_conflict(self) -> None:
        """Test file with single conflict."""
        content = """def hello():
<<<<<<< HEAD
    print("Hello from main")
=======
    print("Hello from branch")
>>>>>>> feature-branch
"""
        result = parse_conflict_markers(content)

        assert result["has_conflicts"] == "true"
        assert result["conflict_count"] == "1"
        assert int(result["ours_lines"]) == 1
        assert int(result["theirs_lines"]) == 1

    def test_multiple_conflicts(self) -> None:
        """Test file with multiple conflicts."""
        content = """def hello():
<<<<<<< HEAD
    print("Hello from main")
=======
    print("Hello from branch")
>>>>>>> feature-branch

def goodbye():
<<<<<<< HEAD
    print("Goodbye from main")
=======
    print("Goodbye from branch")
>>>>>>> feature-branch
"""
        result = parse_conflict_markers(content)

        assert result["has_conflicts"] == "true"
        assert result["conflict_count"] == "2"
        assert int(result["ours_lines"]) == 2
        assert int(result["theirs_lines"]) == 2

    def test_large_conflict(self) -> None:
        """Test conflict with many lines."""
        content = """<<<<<<< HEAD
line 1
line 2
line 3
line 4
line 5
=======
different line 1
different line 2
>>>>>>> feature-branch
"""
        result = parse_conflict_markers(content)

        assert result["has_conflicts"] == "true"
        assert int(result["ours_lines"]) == 5
        assert int(result["theirs_lines"]) == 2

    def test_incomplete_conflict_markers(self) -> None:
        """Test file with incomplete conflict markers."""
        content = """<<<<<<< HEAD
some content
"""
        result = parse_conflict_markers(content)

        # Should handle gracefully - may or may not count as conflict
        assert "has_conflicts" in result
        assert "conflict_count" in result


class TestPredictMergeConflicts:
    """Test predict_merge_conflicts function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            predict_merge_conflicts(123, "main", "feature")  # type: ignore

    def test_invalid_source_branch_type(self) -> None:
        """Test TypeError when source_branch is not a string."""
        with pytest.raises(TypeError, match="source_branch must be a string"):
            predict_merge_conflicts("/tmp", 123, "main")  # type: ignore

    def test_invalid_target_branch_type(self) -> None:
        """Test TypeError when target_branch is not a string."""
        with pytest.raises(TypeError, match="target_branch must be a string"):
            predict_merge_conflicts("/tmp", "feature", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            predict_merge_conflicts("", "main", "feature")

    def test_empty_source_branch(self) -> None:
        """Test ValueError when source_branch is empty."""
        with pytest.raises(ValueError, match="source_branch cannot be empty"):
            predict_merge_conflicts("/tmp", "", "main")

    def test_empty_target_branch(self) -> None:
        """Test ValueError when target_branch is empty."""
        with pytest.raises(ValueError, match="target_branch cannot be empty"):
            predict_merge_conflicts("/tmp", "feature", "")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            predict_merge_conflicts("/nonexistent/path", "main", "feature")

    @patch("subprocess.run")
    def test_merge_base_failure(self, mock_run: Mock) -> None:
        """Test when merge base cannot be found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")
            result = predict_merge_conflicts(tmpdir, "main", "feature")

            assert result["will_conflict"] == "false"
            assert result["can_merge_clean"] == "false"
            assert "Could not find merge base" in result["error_message"]

    @patch("subprocess.run")
    def test_clean_merge(self, mock_run: Mock) -> None:
        """Test when merge will be clean."""
        with tempfile.TemporaryDirectory() as tmpdir:

            def mock_command(*args, **kwargs):
                cmd = args[0]
                if "merge-base" in cmd:
                    return Mock(returncode=0, stdout="basecommit123\n", stderr="")
                elif "merge-tree" in cmd:
                    return Mock(returncode=0, stdout="Clean merge\n", stderr="")
                return Mock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = mock_command
            result = predict_merge_conflicts(tmpdir, "main", "feature")

            assert result["will_conflict"] == "false"
            assert result["can_merge_clean"] == "true"
            assert result["merge_base"] == "basecommit123"

    @patch("subprocess.run")
    def test_will_conflict(self, mock_run: Mock) -> None:
        """Test when merge will have conflicts."""
        with tempfile.TemporaryDirectory() as tmpdir:

            def mock_command(*args, **kwargs):
                cmd = args[0]
                if "merge-base" in cmd:
                    return Mock(returncode=0, stdout="basecommit123\n", stderr="")
                elif "merge-tree" in cmd:
                    return Mock(
                        returncode=0,
                        stdout="conflict in file.txt\nchanged in both file.txt\n",
                        stderr="",
                    )
                return Mock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = mock_command
            result = predict_merge_conflicts(tmpdir, "main", "feature")

            assert result["will_conflict"] == "true"
            assert result["can_merge_clean"] == "false"
            assert "file.txt" in result["conflicted_files"]


class TestAnalyzeConflictComplexity:
    """Test analyze_conflict_complexity function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when file_content is not a string."""
        with pytest.raises(TypeError, match="file_content must be a string"):
            analyze_conflict_complexity(123)  # type: ignore

    def test_empty_content(self) -> None:
        """Test empty file content."""
        result = analyze_conflict_complexity("")

        assert result["complexity_score"] == "0"
        assert result["total_conflicts"] == "0"
        assert result["resolution_difficulty"] == "easy"

    def test_no_conflicts(self) -> None:
        """Test file with no conflicts."""
        content = "Normal file content\nNo conflicts here\n"
        result = analyze_conflict_complexity(content)

        assert result["complexity_score"] == "0"
        assert result["total_conflicts"] == "0"
        assert result["resolution_difficulty"] == "easy"

    def test_easy_conflict(self) -> None:
        """Test simple conflict."""
        content = """<<<<<<< HEAD
line 1
=======
line 2
>>>>>>> feature
"""
        result = analyze_conflict_complexity(content)

        assert int(result["complexity_score"]) <= 3
        assert result["total_conflicts"] == "1"
        assert result["resolution_difficulty"] == "easy"

    def test_medium_conflict(self) -> None:
        """Test moderately complex conflicts."""
        content = """<<<<<<< HEAD
line 1
line 2
line 3
line 4
line 5
=======
different 1
different 2
different 3
different 4
different 5
>>>>>>> feature

<<<<<<< HEAD
more content
more content 2
=======
other content
other content 2
>>>>>>> feature

<<<<<<< HEAD
third conflict
=======
third different
>>>>>>> feature
"""
        result = analyze_conflict_complexity(content)

        complexity = int(result["complexity_score"])
        assert 3 < complexity <= 6
        assert result["resolution_difficulty"] == "medium"

    def test_hard_conflict(self) -> None:
        """Test complex conflicts."""
        # Create large conflict
        ours_lines = "\n".join([f"our line {i}" for i in range(50)])
        theirs_lines = "\n".join([f"their line {i}" for i in range(50)])
        content = f"""<<<<<<< HEAD
{ours_lines}
=======
{theirs_lines}
>>>>>>> feature

<<<<<<< HEAD
conflict 2
=======
conflict 2 alt
>>>>>>> feature

<<<<<<< HEAD
conflict 3
=======
conflict 3 alt
>>>>>>> feature
"""
        result = analyze_conflict_complexity(content)

        complexity = int(result["complexity_score"])
        assert complexity > 6
        assert result["resolution_difficulty"] == "hard"

    def test_metrics_accuracy(self) -> None:
        """Test accuracy of conflict metrics."""
        content = """<<<<<<< HEAD
line 1
line 2
line 3
line 4
line 5
=======
different 1
different 2
>>>>>>> feature
"""
        result = analyze_conflict_complexity(content)

        assert result["total_conflicts"] == "1"
        assert int(result["max_conflict_size"]) > 5
        assert float(result["avg_conflict_size"]) > 5


class TestGetConflictContext:
    """Test get_conflict_context function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            get_conflict_context(123, "file.txt", "10")  # type: ignore

    def test_invalid_file_path_type(self) -> None:
        """Test TypeError when file_path is not a string."""
        with pytest.raises(TypeError, match="file_path must be a string"):
            get_conflict_context("/tmp", 123, "10")  # type: ignore

    def test_invalid_line_number_type(self) -> None:
        """Test TypeError when line_number is not a string."""
        with pytest.raises(TypeError, match="line_number must be a string"):
            get_conflict_context("/tmp", "file.txt", 10)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            get_conflict_context("", "file.txt", "10")

    def test_empty_file_path(self) -> None:
        """Test ValueError when file_path is empty."""
        with pytest.raises(ValueError, match="file_path cannot be empty"):
            get_conflict_context("/tmp", "", "10")

    def test_empty_line_number(self) -> None:
        """Test ValueError when line_number is empty."""
        with pytest.raises(ValueError, match="line_number cannot be empty"):
            get_conflict_context("/tmp", "file.txt", "")

    def test_invalid_line_number_format(self) -> None:
        """Test ValueError when line_number is not valid integer."""
        with pytest.raises(ValueError, match="line_number must be a valid integer"):
            get_conflict_context("/tmp", "file.txt", "not_a_number")

    def test_negative_line_number(self) -> None:
        """Test ValueError when line_number is negative."""
        with pytest.raises(ValueError, match="line_number must be"):
            get_conflict_context("/tmp", "file.txt", "-5")

    def test_zero_line_number(self) -> None:
        """Test ValueError when line_number is zero."""
        with pytest.raises(ValueError, match="line_number must be"):
            get_conflict_context("/tmp", "file.txt", "0")

    def test_file_not_found(self) -> None:
        """Test FileNotFoundError when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(FileNotFoundError):
                get_conflict_context(tmpdir, "nonexistent.txt", "1")

    def test_line_number_exceeds_length(self) -> None:
        """Test when line number exceeds file length."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("line 1\nline 2\n")

            result = get_conflict_context(tmpdir, "test.txt", "100")

            assert result["has_conflict"] == "false"
            assert "exceeds file length" in result["full_conflict"]

    def test_conflict_ours_marker(self) -> None:
        """Test getting context at 'ours' marker."""
        with tempfile.TemporaryDirectory() as tmpdir:
            content = """before line
<<<<<<< HEAD
our content
=======
their content
>>>>>>> feature
after line
"""
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text(content)

            result = get_conflict_context(tmpdir, "test.txt", "2")

            assert result["has_conflict"] == "true"
            assert result["conflict_type"] == "ours"
            assert "before line" in result["context_before"]
            assert "our content" in result["context_after"]

    def test_conflict_separator_marker(self) -> None:
        """Test getting context at separator marker."""
        with tempfile.TemporaryDirectory() as tmpdir:
            content = """<<<<<<< HEAD
our content
=======
their content
>>>>>>> feature
"""
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text(content)

            result = get_conflict_context(tmpdir, "test.txt", "3")

            assert result["has_conflict"] == "true"
            assert result["conflict_type"] == "separator"

    def test_conflict_theirs_marker(self) -> None:
        """Test getting context at 'theirs' marker."""
        with tempfile.TemporaryDirectory() as tmpdir:
            content = """<<<<<<< HEAD
our content
=======
their content
>>>>>>> feature
"""
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text(content)

            result = get_conflict_context(tmpdir, "test.txt", "5")

            assert result["has_conflict"] == "true"
            assert result["conflict_type"] == "theirs"

    def test_full_conflict_extraction(self) -> None:
        """Test extraction of full conflict region."""
        with tempfile.TemporaryDirectory() as tmpdir:
            content = """<<<<<<< HEAD
our content
=======
their content
>>>>>>> feature
"""
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text(content)

            result = get_conflict_context(tmpdir, "test.txt", "1")

            assert "our content" in result["full_conflict"]
            assert "their content" in result["full_conflict"]
            assert "<<<<<<< HEAD" in result["full_conflict"]


class TestSuggestConflictResolution:
    """Test suggest_conflict_resolution function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when file_content is not a string."""
        with pytest.raises(TypeError, match="file_content must be a string"):
            suggest_conflict_resolution(123)  # type: ignore

    def test_empty_content(self) -> None:
        """Test empty file content."""
        result = suggest_conflict_resolution("")

        assert result["has_suggestions"] == "false"
        assert result["strategy"] == "none"
        assert result["auto_resolvable"] == "false"

    def test_no_conflicts(self) -> None:
        """Test file with no conflicts."""
        content = "Normal file content\n"
        result = suggest_conflict_resolution(content)

        assert result["has_suggestions"] == "false"
        assert result["strategy"] == "none"

    def test_identical_content(self) -> None:
        """Test conflict with identical content."""
        content = """<<<<<<< HEAD
same content
=======
same content
>>>>>>> feature
"""
        result = suggest_conflict_resolution(content)

        assert result["has_suggestions"] == "true"
        assert result["strategy"] == "automatic"
        assert result["confidence"] == "high"
        assert result["auto_resolvable"] == "true"
        assert "Identical" in result["suggestions"]

    def test_empty_ours(self) -> None:
        """Test conflict where 'ours' is empty."""
        content = """<<<<<<< HEAD
=======
their content
>>>>>>> feature
"""
        result = suggest_conflict_resolution(content)

        assert result["has_suggestions"] == "true"
        assert result["auto_resolvable"] == "true"
        assert "empty" in result["suggestions"]

    def test_empty_theirs(self) -> None:
        """Test conflict where 'theirs' is empty."""
        content = """<<<<<<< HEAD
our content
=======
>>>>>>> feature
"""
        result = suggest_conflict_resolution(content)

        assert result["has_suggestions"] == "true"
        assert result["auto_resolvable"] == "true"
        assert "empty" in result["suggestions"]

    def test_manual_resolution_needed(self) -> None:
        """Test conflict requiring manual resolution."""
        content = """<<<<<<< HEAD
completely different content
=======
totally different approach
>>>>>>> feature
"""
        result = suggest_conflict_resolution(content)

        assert result["has_suggestions"] == "true"
        assert result["strategy"] == "manual"
        assert result["confidence"] == "low"
        assert result["auto_resolvable"] == "false"
        assert "Manual review" in result["suggestions"]

    def test_semi_automatic_resolution(self) -> None:
        """Test mix of auto and manual conflicts."""
        content = """<<<<<<< HEAD
same content
=======
same content
>>>>>>> feature

<<<<<<< HEAD
identical again
=======
identical again
>>>>>>> feature

<<<<<<< HEAD
different content
=======
other content
>>>>>>> feature
"""
        result = suggest_conflict_resolution(content)

        assert result["has_suggestions"] == "true"
        # 2 out of 3 conflicts are auto-resolvable, so semi-automatic
        assert result["strategy"] == "semi-automatic"
        assert result["auto_resolvable"] == "false"

    def test_superset_detection(self) -> None:
        """Test detection when one side is superset."""
        content = """<<<<<<< HEAD
line 1
=======
line 1
line 2
>>>>>>> feature
"""
        result = suggest_conflict_resolution(content)

        assert result["has_suggestions"] == "true"
        assert "includes all" in result["suggestions"]
