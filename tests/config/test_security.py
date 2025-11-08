"""Tests for configuration security scanning functions."""

import pytest

from coding_open_agent_tools.config.security import (
    detect_insecure_settings,
    scan_config_for_secrets,
)


class TestScanConfigForSecrets:
    """Tests for scan_config_for_secrets function."""

    def test_no_secrets_found(self) -> None:
        """Test config with no secrets."""
        config = """
        app_name: my_application
        port: 8080
        debug: false
        """
        result = scan_config_for_secrets(config, "false")
        assert result["secrets_found"] == "false"
        assert result["secret_count"] == "0"
        assert result["secret_types"] == ""

    def test_aws_access_key_detected(self) -> None:
        """Test detection of AWS access key."""
        config = """
        aws_access_key_id: AKIAIOSFODNN7EXAMPLE
        region: us-east-1
        """
        result = scan_config_for_secrets(config, "false")
        assert result["secrets_found"] == "true"
        assert int(result["secret_count"]) > 0
        assert "aws" in result["secret_types"].lower() or "key" in result["secret_types"].lower()

    def test_api_key_detected(self) -> None:
        """Test detection of API key."""
        config = """
        api_key: abc123def456ghi789jkl012mno345pqr678
        service: example
        """
        result = scan_config_for_secrets(config, "false")
        assert result["secrets_found"] == "true"
        assert int(result["secret_count"]) > 0

    def test_password_detected(self) -> None:
        """Test detection of password."""
        config = """
        database:
          host: localhost
          password: MySecretPassword123!
          user: admin
        """
        result = scan_config_for_secrets(config, "false")
        assert result["secrets_found"] == "true"
        assert int(result["secret_count"]) > 0

    def test_private_key_detected(self) -> None:
        """Test detection of private key."""
        config = """
        cert: |
          -----BEGIN RSA PRIVATE KEY-----
          MIIEpAIBAAKCAQEA...
          -----END RSA PRIVATE KEY-----
        """
        result = scan_config_for_secrets(config, "false")
        assert result["secrets_found"] == "true"
        assert int(result["secret_count"]) > 0

    def test_github_token_detected(self) -> None:
        """Test detection of GitHub token."""
        config = """
        github_token: ghp_1234567890abcdefghijklmnopqrstuv
        """
        result = scan_config_for_secrets(config, "false")
        assert result["secrets_found"] == "true"
        assert int(result["secret_count"]) > 0

    def test_multiple_secrets_detected(self) -> None:
        """Test detection of multiple different secret types."""
        config = """
        api_key: abc123def456ghi789jkl012mno345pqr678
        password: MySecretPassword123!
        token: secret_token_1234567890abcdef
        """
        result = scan_config_for_secrets(config, "false")
        assert result["secrets_found"] == "true"
        assert int(result["secret_count"]) >= 2

    def test_empty_config_raises_error(self) -> None:
        """Test that empty config raises ValueError."""
        with pytest.raises(ValueError, match="config_content cannot be empty"):
            scan_config_for_secrets("", "false")

    def test_invalid_type_raises_error(self) -> None:
        """Test that non-string type raises TypeError."""
        with pytest.raises(TypeError, match="config_content must be a string"):
            scan_config_for_secrets(123, "false")  # type: ignore[arg-type]

    def test_invalid_use_detect_secrets_value(self) -> None:
        """Test that invalid use_detect_secrets value raises ValueError."""
        with pytest.raises(ValueError, match='use_detect_secrets must be "true" or "false"'):
            scan_config_for_secrets("test", "maybe")  # type: ignore[arg-type]


class TestDetectInsecureSettings:
    """Tests for detect_insecure_settings function."""

    def test_no_insecure_settings(self) -> None:
        """Test config with no insecure settings."""
        config = """
        app_name: my_application
        port: 8080
        ssl_verify: true
        """
        result = detect_insecure_settings(config)
        assert result["issues_found"] == "false"
        assert result["issue_count"] == "0"
        assert result["critical_count"] == "0"

    def test_debug_mode_enabled(self) -> None:
        """Test detection of debug mode enabled."""
        config = """
        debug: true
        environment: production
        """
        result = detect_insecure_settings(config)
        assert result["issues_found"] == "true"
        assert int(result["issue_count"]) > 0
        assert int(result["medium_count"]) > 0

    def test_ssl_verification_disabled(self) -> None:
        """Test detection of SSL verification disabled."""
        config = """
        api:
          url: https://api.example.com
          ssl_verify: false
        """
        result = detect_insecure_settings(config)
        assert result["issues_found"] == "true"
        assert int(result["issue_count"]) > 0
        assert int(result["high_count"]) > 0

    def test_wildcard_cors(self) -> None:
        """Test detection of wildcard CORS."""
        config = """
        cors_origin: "*"
        api_enabled: true
        """
        result = detect_insecure_settings(config)
        assert result["issues_found"] == "true"
        assert int(result["issue_count"]) > 0
        assert int(result["high_count"]) > 0

    def test_permissive_permissions(self) -> None:
        """Test detection of overly permissive file permissions."""
        config = """
        file:
          path: /var/log/app.log
          permissions: 777
        """
        result = detect_insecure_settings(config)
        assert result["issues_found"] == "true"
        assert int(result["issue_count"]) > 0
        assert int(result["high_count"]) > 0

    def test_default_credentials(self) -> None:
        """Test detection of default credentials."""
        config = """
        database:
          host: localhost
          user: admin
          password: admin
        """
        result = detect_insecure_settings(config)
        assert result["issues_found"] == "true"
        assert int(result["issue_count"]) > 0
        assert int(result["critical_count"]) > 0

    def test_insecure_protocol(self) -> None:
        """Test detection of insecure protocol (HTTP instead of HTTPS)."""
        config = """
        api:
          protocol: http
          endpoint: api.example.com
        """
        result = detect_insecure_settings(config)
        assert result["issues_found"] == "true"
        assert int(result["issue_count"]) > 0

    def test_multiple_issues(self) -> None:
        """Test detection of multiple insecure settings."""
        config = """
        debug: true
        ssl_verify: false
        cors_origin: "*"
        password: admin
        """
        result = detect_insecure_settings(config)
        assert result["issues_found"] == "true"
        assert int(result["issue_count"]) >= 3
        assert result["issue_summary"] != ""

    def test_issue_summary_truncation(self) -> None:
        """Test that issue summary is properly truncated for many issues."""
        config = """
        debug: true
        ssl_verify: false
        cors_origin: "*"
        password: admin
        permissions: 777
        """
        result = detect_insecure_settings(config)
        assert result["issues_found"] == "true"
        # Summary should exist
        assert result["issue_summary"] != ""

    def test_empty_config_raises_error(self) -> None:
        """Test that empty config raises ValueError."""
        with pytest.raises(ValueError, match="config_content cannot be empty"):
            detect_insecure_settings("  ")

    def test_invalid_type_raises_error(self) -> None:
        """Test that non-string type raises TypeError."""
        with pytest.raises(TypeError, match="config_content must be a string"):
            detect_insecure_settings(None)  # type: ignore[arg-type]
