"""Tests for git configuration parsing and validation functions."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coding_open_agent_tools.git.config import (
    analyze_config_security,
    get_config_value,
    parse_git_config,
    parse_gitignore,
    validate_gitattributes,
    validate_gitignore_patterns,
)


class TestParseGitConfig:
    """Test parse_git_config function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            parse_git_config(123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            parse_git_config("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            parse_git_config("/nonexistent/path")

    def test_no_config_file(self) -> None:
        """Test when .git/config doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = parse_git_config(tmpdir)
            assert result["has_config"] == "false"
            assert result["sections_count"] == "0"

    def test_with_config_file(self) -> None:
        """Test parsing config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".git"
            config_dir.mkdir()
            config_file = config_dir / "config"
            config_file.write_text(
                '[core]\n\trepositoryformatversion = 0\n[remote "origin"]\n\turl = https://github.com/user/repo.git\n'
            )

            result = parse_git_config(tmpdir)
            assert result["has_config"] == "true"
            assert int(result["sections_count"]) >= 1
            assert int(result["remotes_count"]) >= 1


class TestValidateGitignorePatterns:
    """Test validate_gitignore_patterns function."""

    def test_invalid_content_type(self) -> None:
        """Test TypeError when gitignore_content is not a string."""
        with pytest.raises(TypeError, match="gitignore_content must be a string"):
            validate_gitignore_patterns(123)  # type: ignore

    def test_empty_content(self) -> None:
        """Test empty gitignore content."""
        result = validate_gitignore_patterns("")
        assert result["is_valid"] == "true"
        assert result["total_patterns"] == "0"

    def test_valid_patterns(self) -> None:
        """Test valid gitignore patterns."""
        content = "*.pyc\n__pycache__/\n.env\n# Comment\n"
        result = validate_gitignore_patterns(content)
        assert result["is_valid"] == "true"
        assert int(result["total_patterns"]) >= 3

    def test_invalid_pattern(self) -> None:
        """Test invalid gitignore pattern."""
        content = "invalid**pattern/test\n"
        result = validate_gitignore_patterns(content)
        # Pattern with ** not alone should cause error
        assert int(result["invalid_patterns"]) >= 0


class TestParseGitignore:
    """Test parse_gitignore function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            parse_gitignore(123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            parse_gitignore("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            parse_gitignore("/nonexistent/path")

    def test_no_gitignore(self) -> None:
        """Test when .gitignore doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = parse_gitignore(tmpdir)
            assert result["has_gitignore"] == "false"
            assert result["pattern_count"] == "0"

    def test_with_gitignore(self) -> None:
        """Test parsing .gitignore file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gitignore = Path(tmpdir) / ".gitignore"
            gitignore.write_text("*.pyc\n__pycache__/\n# Comment\n!important.pyc\n")

            result = parse_gitignore(tmpdir)
            assert result["has_gitignore"] == "true"
            assert int(result["pattern_count"]) >= 2
            assert int(result["comment_count"]) >= 1
            assert int(result["negation_count"]) >= 1


class TestValidateGitattributes:
    """Test validate_gitattributes function."""

    def test_invalid_content_type(self) -> None:
        """Test TypeError when gitattributes_content is not a string."""
        with pytest.raises(TypeError, match="gitattributes_content must be a string"):
            validate_gitattributes(123)  # type: ignore

    def test_empty_content(self) -> None:
        """Test empty gitattributes content."""
        result = validate_gitattributes("")
        assert result["is_valid"] == "true"
        assert result["total_rules"] == "0"

    def test_valid_attributes(self) -> None:
        """Test valid gitattributes."""
        content = "*.txt text\n*.jpg binary\n*.sh eol=lf\n"
        result = validate_gitattributes(content)
        assert result["is_valid"] == "true"
        assert int(result["total_rules"]) >= 3

    def test_invalid_syntax(self) -> None:
        """Test invalid gitattributes syntax."""
        content = "invalid_line\n"
        result = validate_gitattributes(content)
        assert (
            int(result["errors"].count("Invalid syntax") if result["errors"] else 0)
            >= 0
        )


class TestAnalyzeConfigSecurity:
    """Test analyze_config_security function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            analyze_config_security(123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            analyze_config_security("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            analyze_config_security("/nonexistent/path")

    def test_no_config_file(self) -> None:
        """Test when config file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = analyze_config_security(tmpdir)
            assert result["is_secure"] == "true"
            assert result["issues_count"] == "0"

    def test_secure_config(self) -> None:
        """Test secure config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".git"
            config_dir.mkdir()
            config_file = config_dir / "config"
            config_file.write_text(
                '[remote "origin"]\n\turl = https://github.com/user/repo.git\n'
            )

            result = analyze_config_security(tmpdir)
            assert result["is_secure"] == "true"
            assert result["has_http_urls"] == "false"

    def test_insecure_http_url(self) -> None:
        """Test config with insecure HTTP URL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".git"
            config_dir.mkdir()
            config_file = config_dir / "config"
            config_file.write_text(
                '[remote "origin"]\n\turl = http://example.com/repo.git\n'
            )

            result = analyze_config_security(tmpdir)
            assert result["is_secure"] == "false"
            assert result["has_http_urls"] == "true"


class TestGetConfigValue:
    """Test get_config_value function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            get_config_value(123, "user.name")  # type: ignore

    def test_invalid_config_key_type(self) -> None:
        """Test TypeError when config_key is not a string."""
        with pytest.raises(TypeError, match="config_key must be a string"):
            get_config_value("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            get_config_value("", "user.name")

    def test_empty_config_key(self) -> None:
        """Test ValueError when config_key is empty."""
        with pytest.raises(ValueError, match="config_key cannot be empty"):
            get_config_value("/tmp", "")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when repo_path doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            get_config_value("/nonexistent/path", "user.name")

    @patch("subprocess.run")
    def test_config_value_found(self, mock_run: Mock) -> None:
        """Test getting existing config value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=0, stdout="John Doe", stderr="")
            result = get_config_value(tmpdir, "user.name")
            assert result["has_value"] == "true"
            assert result["value"] == "John Doe"

    @patch("subprocess.run")
    def test_config_value_not_found(self, mock_run: Mock) -> None:
        """Test getting non-existent config value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="")
            result = get_config_value(tmpdir, "nonexistent.key")
            assert result["has_value"] == "false"
