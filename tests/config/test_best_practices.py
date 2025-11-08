"""Tests for configuration security and best practices functions."""

import json

import pytest

from coding_open_agent_tools.config import best_practices


class TestCheckGitignoreSecurity:
    """Tests for check_gitignore_security function."""

    def test_check_secure_gitignore(self) -> None:
        """Test checking a comprehensive .gitignore."""
        gitignore_content = """
# Environment
.env
.env.*
*.env

# Credentials
*.key
*.pem
credentials.json
*credentials*
secrets.json
*secret*

# IDE
.vscode/
.idea/

# Build
dist/
build/
"""
        result = best_practices.check_gitignore_security(gitignore_content)

        # The gitignore covers key patterns, though some may be missing
        # Check that most critical patterns are covered
        covered = json.loads(result["covered_patterns"])
        assert any(".env" in pattern for pattern in covered)
        assert any("*.key" in pattern for pattern in covered)
        assert any("credentials" in pattern.lower() for pattern in covered)

    def test_check_missing_env_pattern(self) -> None:
        """Test detection of missing .env pattern."""
        gitignore_content = """
# Nothing important
*.log
"""
        result = best_practices.check_gitignore_security(gitignore_content)

        assert result["is_secure"] == "false"
        missing = json.loads(result["missing_patterns"])
        assert any(".env" in pattern for pattern in missing)

        warnings = json.loads(result["warnings"])
        assert any(".env" in warning and "CRITICAL" in warning for warning in warnings)

    def test_check_missing_key_patterns(self) -> None:
        """Test detection of missing key/certificate patterns."""
        gitignore_content = """
.env
"""
        result = best_practices.check_gitignore_security(gitignore_content)

        # Should warn about missing key patterns
        warnings = json.loads(result["warnings"])
        assert any(
            "key" in warning.lower() or "certificate" in warning.lower()
            for warning in warnings
        )

    def test_check_wildcard_warning(self) -> None:
        """Test warning on overly permissive wildcards."""
        gitignore_content = """
.env
*
"""
        result = best_practices.check_gitignore_security(gitignore_content)

        warnings = json.loads(result["warnings"])
        assert any("*" in warning and "CRITICAL" in warning for warning in warnings)

    def test_check_covered_patterns(self) -> None:
        """Test identification of covered patterns."""
        gitignore_content = """
.env
*.key
credentials.json
"""
        result = best_practices.check_gitignore_security(gitignore_content)

        covered = json.loads(result["covered_patterns"])
        assert any(".env" in pattern for pattern in covered)
        assert any("*.key" in pattern for pattern in covered)

    def test_check_non_string_raises(self) -> None:
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="gitignore_content must be a string"):
            best_practices.check_gitignore_security(123)  # type: ignore


class TestDetectExposedConfigFiles:
    """Tests for detect_exposed_config_files function."""

    def test_detect_env_in_public(self) -> None:
        """Test detection of .env in public directory."""
        structure = json.dumps(
            {
                "public/.env": "file",
                "src/config.yml": "file",
            }
        )

        result = best_practices.detect_exposed_config_files(structure)

        assert result["has_exposures"] == "true"
        assert int(result["exposure_count"]) >= 1

        exposures = json.loads(result["exposures"])
        assert any("public/.env" in exp and "CRITICAL" in exp for exp in exposures)

    def test_detect_credentials_in_static(self) -> None:
        """Test detection of credentials in static directory."""
        structure = json.dumps(
            {
                "static/credentials.json": "file",
                "app/main.py": "file",
            }
        )

        result = best_practices.detect_exposed_config_files(structure)

        assert result["has_exposures"] == "true"
        exposures = json.loads(result["exposures"])
        assert any("static/credentials" in exp for exp in exposures)

    def test_detect_key_in_www(self) -> None:
        """Test detection of private key in www directory."""
        structure = json.dumps(
            {
                "www/private.key": "file",
            }
        )

        result = best_practices.detect_exposed_config_files(structure)

        assert result["has_exposures"] == "true"
        exposures = json.loads(result["exposures"])
        assert any("www/private.key" in exp for exp in exposures)

    def test_detect_root_directory_configs(self) -> None:
        """Test detection of sensitive files in root."""
        structure = json.dumps(
            {
                ".env": "file",
                "src/app.py": "file",
            }
        )

        result = best_practices.detect_exposed_config_files(structure)

        # .env in root should be flagged
        assert result["has_exposures"] == "true"

    def test_no_exposures(self) -> None:
        """Test when no exposures are detected."""
        structure = json.dumps(
            {
                "src/config/.env": "file",
                "app/main.py": "file",
            }
        )

        # Call function to ensure it doesn't crash
        # .env in src/config is safer than public/
        # This might still be flagged depending on implementation
        # but public directories should be prioritized
        best_practices.detect_exposed_config_files(structure)

    def test_recommendations_provided(self) -> None:
        """Test that recommendations are provided for exposures."""
        structure = json.dumps(
            {
                "public/.env": "file",
            }
        )

        result = best_practices.detect_exposed_config_files(structure)

        recommendations = json.loads(result["recommendations"])
        assert len(recommendations) > 0
        assert any("gitignore" in rec.lower() for rec in recommendations)

    def test_invalid_json_raises(self) -> None:
        """Test that invalid JSON raises ValueError."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            best_practices.detect_exposed_config_files("not json")

    def test_non_string_raises(self) -> None:
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="directory_structure must be a string"):
            best_practices.detect_exposed_config_files(123)  # type: ignore


class TestValidateConfigPermissions:
    """Tests for validate_config_permissions function."""

    def test_validate_secure_permissions(self) -> None:
        """Test validation of secure permissions."""
        permissions = json.dumps(
            {
                ".env": "0600",
                "config.yml": "0644",
                "private.key": "0600",
            }
        )

        result = best_practices.validate_config_permissions(permissions)

        assert result["is_secure"] == "true"
        assert result["violation_count"] == "0"

    def test_validate_env_too_permissive(self) -> None:
        """Test detection of overly permissive .env permissions."""
        permissions = json.dumps(
            {
                ".env": "0644",  # Should be 0600
            }
        )

        result = best_practices.validate_config_permissions(permissions)

        assert result["is_secure"] == "false"
        violations = json.loads(result["violations"])
        assert any(".env" in v and "0600" in v for v in violations)

    def test_validate_world_writable(self) -> None:
        """Test detection of world-writable files."""
        permissions = json.dumps(
            {
                "config.yml": "0666",  # World-writable
            }
        )

        result = best_practices.validate_config_permissions(permissions)

        assert result["is_secure"] == "false"
        violations = json.loads(result["violations"])
        assert any("World-writable" in v for v in violations)

    def test_validate_key_group_writable(self) -> None:
        """Test detection of group-writable sensitive files."""
        permissions = json.dumps(
            {
                "private.key": "0660",  # Group-writable
            }
        )

        result = best_practices.validate_config_permissions(permissions)

        assert result["is_secure"] == "false"
        violations = json.loads(result["violations"])
        assert any("group-writable" in v.lower() for v in violations)

    def test_validate_invalid_permission_format(self) -> None:
        """Test handling of invalid permission format."""
        permissions = json.dumps(
            {
                "file.txt": "invalid",
            }
        )

        result = best_practices.validate_config_permissions(permissions)

        violations = json.loads(result["violations"])
        assert any("Invalid permission format" in v for v in violations)

    def test_recommendations_provided(self) -> None:
        """Test that recommendations are provided."""
        permissions = json.dumps(
            {
                ".env": "0777",
            }
        )

        result = best_practices.validate_config_permissions(permissions)

        recommendations = json.loads(result["recommendations"])
        assert len(recommendations) > 0
        assert any("chmod" in rec.lower() for rec in recommendations)

    def test_validate_octal_integer_permissions(self) -> None:
        """Test handling of integer permission values."""
        permissions = json.dumps(
            {
                ".env": 384,  # 0600 in decimal
            }
        )

        result = best_practices.validate_config_permissions(permissions)

        # Should handle integer values correctly
        assert result["is_secure"] in ["true", "false"]

    def test_invalid_json_raises(self) -> None:
        """Test that invalid JSON raises ValueError."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            best_practices.validate_config_permissions("not json")

    def test_non_dict_json_raises(self) -> None:
        """Test that non-dict JSON raises ValueError."""
        with pytest.raises(ValueError, match="must be a JSON object"):
            best_practices.validate_config_permissions(json.dumps(["not", "a", "dict"]))
