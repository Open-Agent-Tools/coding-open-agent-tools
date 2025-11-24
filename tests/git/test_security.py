"""Tests for git security auditing functions."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coding_open_agent_tools.git.security import (
    analyze_file_permissions,
    audit_commit_authors,
    check_force_push_protection,
    check_sensitive_files,
    check_signed_tags,
    detect_security_issues,
    scan_history_for_secrets,
    validate_gpg_signatures,
)


class TestScanHistoryForSecrets:
    """Test scan_history_for_secrets function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            scan_history_for_secrets(123, "10")  # type: ignore

    def test_invalid_max_commits_type(self) -> None:
        """Test TypeError when max_commits is not a string."""
        with pytest.raises(TypeError, match="max_commits must be a string"):
            scan_history_for_secrets("/tmp", 10)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            scan_history_for_secrets("", "10")

    def test_invalid_max_commits_format(self) -> None:
        """Test ValueError when max_commits is not a valid integer."""
        with pytest.raises(ValueError, match="max_commits must be a valid integer"):
            scan_history_for_secrets("/tmp", "not_a_number")

    def test_negative_max_commits(self) -> None:
        """Test ValueError when max_commits is negative."""
        with pytest.raises(ValueError, match="max_commits must be"):
            scan_history_for_secrets("/tmp", "-5")

    def test_zero_max_commits(self) -> None:
        """Test ValueError when max_commits is zero."""
        with pytest.raises(ValueError, match="max_commits must be"):
            scan_history_for_secrets("/tmp", "0")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            scan_history_for_secrets("/nonexistent/path", "10")

    @patch("subprocess.run")
    def test_git_command_failure(self, mock_run: Mock) -> None:
        """Test when git command fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")
            result = scan_history_for_secrets(tmpdir, "10")

            assert result["secrets_found"] == "false"
            assert result["commits_scanned"] == "0"
            assert "Could not scan" in result["recommendations"]

    @patch("subprocess.run")
    @patch("coding_open_agent_tools.analysis.secrets.scan_for_secrets")
    def test_no_secrets_found(self, mock_scan: Mock, mock_run: Mock) -> None:
        """Test when no secrets found in commits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="abc123|Add feature\ndef456|Fix bug\n",
                stderr="",
            )
            # Mock returns dict as expected by scan_history_for_secrets code
            mock_scan.return_value = {"secrets_found": "false", "secrets_count": "0"}

            result = scan_history_for_secrets(tmpdir, "10")

            assert result["secrets_found"] == "false"
            assert result["commits_scanned"] == "2"
            assert "No secrets detected" in result["recommendations"]

    @patch("subprocess.run")
    @patch("coding_open_agent_tools.analysis.secrets.scan_for_secrets")
    def test_secrets_found(self, mock_scan: Mock, mock_run: Mock) -> None:
        """Test when secrets found in commits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="abc123|Add API_KEY=secret123\n",
                stderr="",
            )
            # Mock returns dict as expected by scan_history_for_secrets code
            mock_scan.return_value = {"secrets_found": "true", "secrets_count": "1"}

            result = scan_history_for_secrets(tmpdir, "10")

            assert result["secrets_found"] == "true"
            assert int(result["pattern_matches"]) > 0
            assert "Review and rewrite" in result["recommendations"]


class TestCheckSensitiveFiles:
    """Test check_sensitive_files function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            check_sensitive_files(123)  # type: ignore

    def test_empty_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            check_sensitive_files("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            check_sensitive_files("/nonexistent/path")

    @patch("subprocess.run")
    def test_git_command_failure(self, mock_run: Mock) -> None:
        """Test when git command fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")
            result = check_sensitive_files(tmpdir)

            assert result["has_sensitive_files"] == "false"
            assert result["risk_level"] == "low"

    @patch("subprocess.run")
    def test_no_sensitive_files(self, mock_run: Mock) -> None:
        """Test when no sensitive files found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="src/main.py\nREADME.md\ntests/test_main.py\n",
                stderr="",
            )
            result = check_sensitive_files(tmpdir)

            assert result["has_sensitive_files"] == "false"
            assert result["sensitive_count"] == "0"
            assert result["risk_level"] == "low"
            assert "No sensitive files" in result["recommendations"]

    @patch("subprocess.run")
    def test_high_risk_files(self, mock_run: Mock) -> None:
        """Test when high risk files found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(
                returncode=0,
                stdout=".env\nid_rsa\ncredentials.json\n",
                stderr="",
            )
            result = check_sensitive_files(tmpdir)

            assert result["has_sensitive_files"] == "true"
            assert int(result["sensitive_count"]) >= 3
            assert result["risk_level"] == "high"
            assert "CRITICAL" in result["recommendations"]

    @patch("subprocess.run")
    def test_medium_risk_files(self, mock_run: Mock) -> None:
        """Test when medium risk files found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="auth.json\ntoken.txt\n",
                stderr="",
            )
            result = check_sensitive_files(tmpdir)

            assert result["has_sensitive_files"] == "true"
            assert result["risk_level"] == "medium"

    @patch("subprocess.run")
    def test_low_risk_files(self, mock_run: Mock) -> None:
        """Test when low risk files found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="app.config\nsettings.ini\n",
                stderr="",
            )
            result = check_sensitive_files(tmpdir)

            assert result["has_sensitive_files"] == "true"
            assert result["risk_level"] == "low"


class TestValidateGpgSignatures:
    """Test validate_gpg_signatures function."""

    def test_invalid_repo_path_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            validate_gpg_signatures(123, "main")  # type: ignore

    def test_invalid_branch_name_type(self) -> None:
        """Test TypeError when branch_name is not a string."""
        with pytest.raises(TypeError, match="branch_name must be a string"):
            validate_gpg_signatures("/tmp", 123)  # type: ignore

    def test_empty_repo_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            validate_gpg_signatures("", "main")

    def test_empty_branch_name(self) -> None:
        """Test ValueError when branch_name is empty."""
        with pytest.raises(ValueError, match="branch_name cannot be empty"):
            validate_gpg_signatures("/tmp", "")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            validate_gpg_signatures("/nonexistent/path", "main")

    @patch("subprocess.run")
    def test_git_log_failure(self, mock_run: Mock) -> None:
        """Test when git log fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")
            result = validate_gpg_signatures(tmpdir, "main")

            assert result["all_signed"] == "false"
            assert result["total_commits"] == "0"

    @patch("subprocess.run")
    def test_all_commits_signed(self, mock_run: Mock) -> None:
        """Test when all commits are signed and valid."""
        with tempfile.TemporaryDirectory() as tmpdir:

            def mock_command(*args, **kwargs):
                cmd = args[0]
                if "log" in cmd:
                    return Mock(returncode=0, stdout="abc123\ndef456\n", stderr="")
                elif "verify-commit" in cmd:
                    return Mock(
                        returncode=0, stdout="", stderr="gpg: Good signature from"
                    )
                return Mock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = mock_command
            result = validate_gpg_signatures(tmpdir, "main")

            assert result["all_signed"] == "true"
            assert result["total_commits"] == "2"
            assert result["signed_commits"] == "2"
            assert result["signature_validity"] == "all_valid"

    @patch("subprocess.run")
    def test_unsigned_commits(self, mock_run: Mock) -> None:
        """Test when some commits are unsigned."""
        with tempfile.TemporaryDirectory() as tmpdir:

            def mock_command(*args, **kwargs):
                cmd = args[0]
                if "log" in cmd:
                    return Mock(returncode=0, stdout="abc123\ndef456\n", stderr="")
                elif "verify-commit" in cmd:
                    # First commit signed, second not
                    if "abc123" in cmd:
                        return Mock(returncode=0, stdout="", stderr="Good signature")
                    else:
                        return Mock(returncode=1, stdout="", stderr="no signature")
                return Mock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = mock_command
            result = validate_gpg_signatures(tmpdir, "main")

            assert result["all_signed"] == "false"
            assert result["signed_commits"] == "1"
            assert result["unsigned_commits"] == "1"


class TestCheckForcePushProtection:
    """Test check_force_push_protection function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            check_force_push_protection(123)  # type: ignore

    def test_empty_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            check_force_push_protection("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            check_force_push_protection("/nonexistent/path")

    @patch("subprocess.run")
    def test_protection_enabled(self, mock_run: Mock) -> None:
        """Test when force push protection is enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=0, stdout="true\n", stderr="")
            result = check_force_push_protection(tmpdir)

            assert result["is_protected"] == "true"
            assert result["config_value"] == "true"
            assert "No action needed" in result["recommendation"]

    @patch("subprocess.run")
    def test_protection_disabled(self, mock_run: Mock) -> None:
        """Test when force push protection is disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="")
            result = check_force_push_protection(tmpdir)

            assert result["is_protected"] == "false"
            assert "Enable" in result["recommendation"]


class TestAnalyzeFilePermissions:
    """Test analyze_file_permissions function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            analyze_file_permissions(123)  # type: ignore

    def test_empty_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            analyze_file_permissions("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            analyze_file_permissions("/nonexistent/path")

    @patch("subprocess.run")
    def test_no_executable_files(self, mock_run: Mock) -> None:
        """Test when no executable files found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="100644 abc123 0	file.txt\n100644 def456 0	doc.md\n",
                stderr="",
            )
            result = analyze_file_permissions(tmpdir)

            assert result["executable_count"] == "0"
            assert result["has_executables"] == "false"

    @patch("subprocess.run")
    def test_with_executable_files(self, mock_run: Mock) -> None:
        """Test when executable files found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="100755 abc123 0	script.sh\n100755 def456 0	run.py\n",
                stderr="",
            )
            result = analyze_file_permissions(tmpdir)

            assert int(result["executable_count"]) == 2
            assert result["has_executables"] == "true"
            assert "script.sh" in result["executable_files"]
            assert "run.py" in result["executable_files"]


class TestCheckSignedTags:
    """Test check_signed_tags function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            check_signed_tags(123)  # type: ignore

    def test_empty_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            check_signed_tags("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            check_signed_tags("/nonexistent/path")

    @patch("subprocess.run")
    def test_no_tags(self, mock_run: Mock) -> None:
        """Test when repository has no tags."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            result = check_signed_tags(tmpdir)

            assert result["total_tags"] == "0"
            assert result["all_signed"] == "false"

    @patch("subprocess.run")
    def test_all_tags_signed(self, mock_run: Mock) -> None:
        """Test when all tags are signed."""
        with tempfile.TemporaryDirectory() as tmpdir:

            def mock_command(*args, **kwargs):
                cmd = args[0]
                if "tag" in cmd and "verify-tag" not in cmd:
                    return Mock(returncode=0, stdout="v1.0\nv2.0\n", stderr="")
                elif "verify-tag" in cmd:
                    return Mock(returncode=0, stdout="", stderr="Good signature")
                return Mock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = mock_command
            result = check_signed_tags(tmpdir)

            assert result["total_tags"] == "2"
            assert result["signed_tags"] == "2"
            assert result["all_signed"] == "true"

    @patch("subprocess.run")
    def test_unsigned_tags(self, mock_run: Mock) -> None:
        """Test when some tags are unsigned."""
        with tempfile.TemporaryDirectory() as tmpdir:

            def mock_command(*args, **kwargs):
                cmd = args[0]
                if "tag" in cmd and "verify-tag" not in cmd:
                    return Mock(returncode=0, stdout="v1.0\nv2.0\n", stderr="")
                elif "verify-tag" in cmd:
                    if "v1.0" in cmd:
                        return Mock(returncode=0, stdout="", stderr="")
                    else:
                        return Mock(returncode=1, stdout="", stderr="")
                return Mock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = mock_command
            result = check_signed_tags(tmpdir)

            assert result["total_tags"] == "2"
            assert result["signed_tags"] == "1"
            assert result["unsigned_tags"] == "1"
            assert result["all_signed"] == "false"


class TestDetectSecurityIssues:
    """Test detect_security_issues function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            detect_security_issues(123)  # type: ignore

    def test_empty_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            detect_security_issues("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            detect_security_issues("/nonexistent/path")

    def test_secure_repository(self) -> None:
        """Test repository with good security."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()

            # Create secure config
            config_file = git_dir / "config"
            config_file.write_text(
                '[remote "origin"]\n\turl = https://github.com/user/repo\n'
            )

            # Create .gitignore
            (Path(tmpdir) / ".gitignore").write_text("*.pyc\n.env\n")

            result = detect_security_issues(tmpdir)

            assert int(result["security_score"]) >= 80
            assert result["risk_level"] == "low"

    def test_insecure_http_urls(self) -> None:
        """Test repository with insecure HTTP URLs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()

            # Create config with HTTP URL
            config_file = git_dir / "config"
            config_file.write_text(
                '[remote "origin"]\n\turl = http://github.com/user/repo\n'
            )

            result = detect_security_issues(tmpdir)

            assert int(result["security_score"]) < 100
            assert "Insecure HTTP" in result["issues"]

    def test_missing_gitignore(self) -> None:
        """Test repository without .gitignore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()

            config_file = git_dir / "config"
            config_file.write_text(
                '[remote "origin"]\n\turl = https://github.com/user/repo\n'
            )

            result = detect_security_issues(tmpdir)

            assert int(result["security_score"]) < 100
            assert "No .gitignore" in result["issues"]


class TestAuditCommitAuthors:
    """Test audit_commit_authors function."""

    def test_invalid_type(self) -> None:
        """Test TypeError when repo_path is not a string."""
        with pytest.raises(TypeError, match="repo_path must be a string"):
            audit_commit_authors(123)  # type: ignore

    def test_empty_path(self) -> None:
        """Test ValueError when repo_path is empty."""
        with pytest.raises(ValueError, match="repo_path cannot be empty"):
            audit_commit_authors("")

    def test_nonexistent_path(self) -> None:
        """Test FileNotFoundError when path doesn't exist."""
        with pytest.raises(FileNotFoundError):
            audit_commit_authors("/nonexistent/path")

    @patch("subprocess.run")
    def test_valid_authors(self, mock_run: Mock) -> None:
        """Test with valid commit authors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Alice|alice@example.com\nBob|bob@example.com\n",
                stderr="",
            )
            result = audit_commit_authors(tmpdir)

            assert result["unique_authors"] == "2"
            assert result["suspicious_count"] == "0"
            assert result["has_issues"] == "false"

    @patch("subprocess.run")
    def test_invalid_email(self, mock_run: Mock) -> None:
        """Test with invalid email addresses."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Alice|invalid-email\nBob|\n",
                stderr="",
            )
            result = audit_commit_authors(tmpdir)

            assert int(result["suspicious_count"]) >= 2
            assert result["has_issues"] == "true"
            assert "Invalid email" in result["suspicious_authors"]

    @patch("subprocess.run")
    def test_noreply_email(self, mock_run: Mock) -> None:
        """Test with noreply email addresses."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Alice|alice@users.noreply.github.com\n",
                stderr="",
            )
            result = audit_commit_authors(tmpdir)

            assert int(result["suspicious_count"]) >= 1
            assert "No-reply" in result["suspicious_authors"]
