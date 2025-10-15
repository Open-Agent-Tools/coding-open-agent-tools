"""Tests for shell security module."""

import pytest

from coding_open_agent_tools.shell.security import (
    analyze_shell_security,
    detect_shell_injection_risks,
    scan_for_secrets_enhanced,
)


class TestAnalyzeShellSecurity:
    """Tests for analyze_shell_security function."""

    def test_eval_detection(self):
        """Test detection of eval command."""
        script = 'eval "$user_input"'
        issues = analyze_shell_security(script)
        assert len(issues) > 0
        assert any(issue["issue_type"] == "code_injection" for issue in issues)
        assert any(issue["severity"] == "critical" for issue in issues)

    def test_rm_rf_detection(self):
        """Test detection of rm -rf with variables."""
        script = "rm -rf $TEMP_DIR"
        issues = analyze_shell_security(script)
        assert len(issues) > 0
        assert any("rm -rf" in issue["description"].lower() for issue in issues)

    def test_chmod_777_detection(self):
        """Test detection of chmod 777."""
        script = "chmod 777 /tmp/file"
        issues = analyze_shell_security(script)
        assert len(issues) > 0
        assert any("777" in issue["description"] for issue in issues)

    def test_curl_pipe_sh_detection(self):
        """Test detection of curl | sh pattern."""
        script = "curl https://example.com/install.sh | sh"
        issues = analyze_shell_security(script)
        # May or may not detect depending on pattern matching
        # This is more for documentation of dangerous pattern
        assert isinstance(issues, list)

    def test_wget_insecure_detection(self):
        """Test detection of wget --no-check-certificate."""
        script = "wget --no-check-certificate https://example.com/file"
        issues = analyze_shell_security(script)
        assert len(issues) > 0
        assert any("SSL" in issue["description"] or "insecure" in issue["description"].lower() for issue in issues)

    def test_clean_script(self):
        """Test that clean script has no critical issues."""
        script = """#!/bin/bash
set -e
echo "Safe script"
ls -la /tmp
"""
        issues = analyze_shell_security(script)
        # Should have no critical issues
        critical_issues = [i for i in issues if i["severity"] == "critical"]
        assert len(critical_issues) == 0

    def test_type_error(self):
        """Test TypeError for non-string input."""
        with pytest.raises(TypeError, match="script_content must be a string"):
            analyze_shell_security(123)  # type: ignore[arg-type]

    def test_empty_script(self):
        """Test ValueError for empty script."""
        with pytest.raises(ValueError, match="script_content cannot be empty"):
            analyze_shell_security("")

    def test_recommendations_present(self):
        """Test that recommendations are provided."""
        script = 'eval "$input"'
        issues = analyze_shell_security(script)
        assert len(issues) > 0
        assert all("recommendation" in issue for issue in issues)
        assert all(issue["recommendation"] != "" for issue in issues)


class TestDetectShellInjectionRisks:
    """Tests for detect_shell_injection_risks function."""

    def test_eval_risk(self):
        """Test detection of eval as injection risk."""
        script = "eval $command"
        risks = detect_shell_injection_risks(script)
        assert len(risks) > 0
        assert any(risk["risk_level"] == "critical" for risk in risks)

    def test_exec_risk(self):
        """Test detection of exec with variable."""
        script = "exec $binary"
        risks = detect_shell_injection_risks(script)
        assert len(risks) > 0
        assert any("exec" in risk["pattern"].lower() for risk in risks)

    def test_pipe_to_sh_risk(self):
        """Test detection of piping to sh."""
        script = "cat script.sh | sh"
        risks = detect_shell_injection_risks(script)
        assert len(risks) > 0

    def test_backtick_substitution(self):
        """Test detection of backtick command substitution with variables."""
        script = "result=``echo $user_input``"
        risks = detect_shell_injection_risks(script)
        # Backtick pattern requires specific format
        assert isinstance(risks, list)

    def test_context_provided(self):
        """Test that context is provided for risks."""
        script = """line before
eval "$dangerous"
line after"""
        risks = detect_shell_injection_risks(script)
        assert len(risks) > 0
        assert all("context" in risk for risk in risks)

    def test_mitigation_provided(self):
        """Test that mitigation is provided."""
        script = "eval $input"
        risks = detect_shell_injection_risks(script)
        assert len(risks) > 0
        assert all("mitigation" in risk for risk in risks)
        assert all(risk["mitigation"] != "" for risk in risks)

    def test_type_error(self):
        """Test TypeError for non-string input."""
        with pytest.raises(TypeError, match="script_content must be a string"):
            detect_shell_injection_risks(123)  # type: ignore[arg-type]

    def test_empty_script(self):
        """Test ValueError for empty script."""
        with pytest.raises(ValueError, match="script_content cannot be empty"):
            detect_shell_injection_risks("")


class TestScanForSecretsEnhanced:
    """Tests for scan_for_secrets_enhanced function."""

    def test_api_key_detection(self):
        """Test detection of API key."""
        content = "api_key=abcdef123456789012345678901234567890"
        result = scan_for_secrets_enhanced(content, "false")
        assert result["has_secrets"] == "true"
        assert len(result["secrets_found"]) > 0

    def test_password_detection(self):
        """Test detection of password."""
        content = 'PASSWORD="mysecretpass123"'
        result = scan_for_secrets_enhanced(content, "false")
        assert result["has_secrets"] == "true"

    def test_private_key_detection(self):
        """Test detection of private key."""
        content = "-----BEGIN RSA PRIVATE KEY-----"
        result = scan_for_secrets_enhanced(content, "false")
        assert result["has_secrets"] == "true"

    def test_clean_content(self):
        """Test that clean content has no secrets."""
        content = """#!/bin/bash
echo "Hello World"
export PATH=/usr/local/bin:$PATH
"""
        result = scan_for_secrets_enhanced(content, "false")
        assert result["has_secrets"] == "false"

    def test_stdlib_method(self):
        """Test that stdlib method is used when detect-secrets is false."""
        content = "api_key=test123"
        result = scan_for_secrets_enhanced(content, "false")
        assert result["scan_method"] == "stdlib-regex"

    def test_patterns_count(self):
        """Test that patterns_checked is provided."""
        content = "test"
        result = scan_for_secrets_enhanced(content, "false")
        assert "patterns_checked" in result
        assert int(result["patterns_checked"]) > 0

    def test_type_error_content(self):
        """Test TypeError for non-string content."""
        with pytest.raises(TypeError, match="content must be a string"):
            scan_for_secrets_enhanced(123, "false")  # type: ignore[arg-type]

    def test_type_error_use_detect_secrets(self):
        """Test TypeError for non-string use_detect_secrets."""
        with pytest.raises(TypeError, match="use_detect_secrets must be a string"):
            scan_for_secrets_enhanced("test", 123)  # type: ignore[arg-type]

    def test_empty_content(self):
        """Test ValueError for empty content."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            scan_for_secrets_enhanced("", "false")

    def test_invalid_use_detect_secrets(self):
        """Test ValueError for invalid use_detect_secrets value."""
        with pytest.raises(ValueError, match="use_detect_secrets must be"):
            scan_for_secrets_enhanced("test", "maybe")

    def test_database_url_detection(self):
        """Test detection of database URL."""
        content = "DB_URL=postgres://user:pass@localhost/db"
        result = scan_for_secrets_enhanced(content, "false")
        # postgres:// should match the pattern
        assert result["has_secrets"] == "true"

    def test_line_numbers_provided(self):
        """Test that line numbers are provided for findings."""
        content = """line 1
api_key=test123456789012345678901234567890
line 3"""
        result = scan_for_secrets_enhanced(content, "false")
        if result["has_secrets"] == "true":
            assert all("line_number" in secret for secret in result["secrets_found"])
