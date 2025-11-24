"""Tests for dependency analysis module."""

import json

import pytest

from coding_open_agent_tools.dependencies import analysis


class TestParseRequirementsTxt:
    """Tests for parse_requirements_txt function."""

    def test_invalid_type_content(self) -> None:
        """Test TypeError when content is not a string."""
        with pytest.raises(TypeError, match="content must be a string"):
            analysis.parse_requirements_txt(123)  # type: ignore

    def test_empty_content(self) -> None:
        """Test ValueError when content is empty."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            analysis.parse_requirements_txt("")

    def test_simple_requirements(self) -> None:
        """Test parsing simple requirements."""
        content = """requests==2.28.0
django>=4.0.0
flask<3.0.0"""
        result = analysis.parse_requirements_txt(content)
        assert result["package_count"] == "3"
        packages = json.loads(result["packages"])
        assert len(packages) == 3
        assert any(p["name"] == "requests" for p in packages)

    def test_requirements_with_comments(self) -> None:
        """Test parsing requirements with comments."""
        content = """# Web framework
django==4.1.0
# Database
psycopg2>=2.9.0"""
        result = analysis.parse_requirements_txt(content)
        assert result["comments"] == "2"
        assert result["package_count"] == "2"

    def test_git_dependencies(self) -> None:
        """Test detection of git dependencies."""
        content = """requests==2.28.0
git+https://github.com/user/repo.git@v1.0#egg=mypackage"""
        result = analysis.parse_requirements_txt(content)
        assert result["has_git_dependencies"] == "true"

    def test_extras_syntax(self) -> None:
        """Test parsing extras syntax."""
        content = "requests[security]==2.28.0"
        result = analysis.parse_requirements_txt(content)
        assert result["has_extras"] == "true"


class TestParsePackageJson:
    """Tests for parse_package_json function."""

    def test_invalid_type_content(self) -> None:
        """Test TypeError when content is not a string."""
        with pytest.raises(TypeError, match="content must be a string"):
            analysis.parse_package_json(None)  # type: ignore

    def test_empty_content(self) -> None:
        """Test ValueError when content is empty."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            analysis.parse_package_json("   ")

    def test_invalid_json(self) -> None:
        """Test ValueError for invalid JSON."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            analysis.parse_package_json("{invalid}")

    def test_valid_package_json(self) -> None:
        """Test parsing valid package.json."""
        content = json.dumps(
            {
                "name": "test-app",
                "version": "1.0.0",
                "dependencies": {"express": "^4.18.0", "lodash": "~4.17.0"},
                "devDependencies": {"jest": "^29.0.0"},
            }
        )
        result = analysis.parse_package_json(content)
        assert result["package_name"] == "test-app"
        assert result["version"] == "1.0.0"
        assert result["dependency_count"] == "2"
        assert result["dev_dependency_count"] == "1"

    def test_package_with_scripts(self) -> None:
        """Test detection of scripts."""
        content = json.dumps(
            {"name": "app", "scripts": {"test": "jest", "build": "webpack"}}
        )
        result = analysis.parse_package_json(content)
        assert result["has_scripts"] == "true"

    def test_package_with_workspaces(self) -> None:
        """Test detection of workspaces."""
        content = json.dumps({"name": "monorepo", "workspaces": ["packages/*"]})
        result = analysis.parse_package_json(content)
        assert result["has_workspaces"] == "true"


class TestParsePoetryLock:
    """Tests for parse_poetry_lock function."""

    def test_invalid_type_content(self) -> None:
        """Test TypeError when content is not a string."""
        with pytest.raises(TypeError, match="content must be a string"):
            analysis.parse_poetry_lock([])  # type: ignore

    def test_empty_content(self) -> None:
        """Test ValueError when content is empty."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            analysis.parse_poetry_lock("")

    def test_simple_poetry_lock(self) -> None:
        """Test parsing simple poetry.lock."""
        content = """[[package]]
name = "requests"
version = "2.28.0"

[[package]]
name = "certifi"
version = "2022.12.7"
"""
        result = analysis.parse_poetry_lock(content)
        assert result["package_count"] == "2"
        packages = json.loads(result["packages"])
        assert len(packages) == 2


class TestParseCargoToml:
    """Tests for parse_cargo_toml function."""

    def test_invalid_type_content(self) -> None:
        """Test TypeError when content is not a string."""
        with pytest.raises(TypeError, match="content must be a string"):
            analysis.parse_cargo_toml(123)  # type: ignore

    def test_empty_content(self) -> None:
        """Test ValueError when content is empty."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            analysis.parse_cargo_toml("")

    def test_valid_cargo_toml(self) -> None:
        """Test parsing valid Cargo.toml."""
        content = """[package]
name = "myapp"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = "1.25"

[dev-dependencies]
mockall = "0.11"
"""
        result = analysis.parse_cargo_toml(content)
        assert result["package_name"] == "myapp"
        assert result["version"] == "0.1.0"
        assert result["dependency_count"] == "2"
        assert result["dev_dependency_count"] == "1"

    def test_cargo_with_features(self) -> None:
        """Test detection of features."""
        content = """[package]
name = "app"

[features]
default = ["std"]
"""
        result = analysis.parse_cargo_toml(content)
        assert result["has_features"] == "true"


class TestDetectVersionConflicts:
    """Tests for detect_version_conflicts function."""

    def test_invalid_type_dependencies_json(self) -> None:
        """Test TypeError when dependencies_json is not a string."""
        with pytest.raises(TypeError, match="dependencies_json must be a string"):
            analysis.detect_version_conflicts(None)  # type: ignore

    def test_empty_dependencies_json(self) -> None:
        """Test ValueError when dependencies_json is empty."""
        with pytest.raises(ValueError, match="dependencies_json cannot be empty"):
            analysis.detect_version_conflicts("")

    def test_invalid_json(self) -> None:
        """Test ValueError for invalid JSON."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            analysis.detect_version_conflicts("{invalid}")

    def test_no_conflicts(self) -> None:
        """Test dependencies without conflicts."""
        deps = json.dumps(
            [
                {"name": "pkg1", "version": "1.0.0", "specifier": "=="},
                {"name": "pkg2", "version": "2.0.0", "specifier": "=="},
            ]
        )
        result = analysis.detect_version_conflicts(deps)
        assert result["has_conflicts"] == "false"

    def test_conflicting_versions(self) -> None:
        """Test detection of conflicting versions."""
        deps = json.dumps(
            [
                {"name": "pkg1", "version": "1.0.0", "specifier": "=="},
                {"name": "pkg1", "version": "2.0.0", "specifier": "=="},
            ]
        )
        result = analysis.detect_version_conflicts(deps)
        assert result["has_conflicts"] == "true"
        assert int(result["conflict_count"]) > 0


class TestValidateSemver:
    """Tests for validate_semver function."""

    def test_invalid_type_version(self) -> None:
        """Test TypeError when version is not a string."""
        with pytest.raises(TypeError, match="version must be a string"):
            analysis.validate_semver(123)  # type: ignore

    def test_empty_version(self) -> None:
        """Test ValueError when version is empty."""
        with pytest.raises(ValueError, match="version cannot be empty"):
            analysis.validate_semver("")

    def test_valid_semver(self) -> None:
        """Test valid semantic version."""
        result = analysis.validate_semver("1.2.3")
        assert result["is_valid"] == "true"
        assert result["major"] == "1"
        assert result["minor"] == "2"
        assert result["patch"] == "3"

    def test_semver_with_prerelease(self) -> None:
        """Test semver with prerelease."""
        result = analysis.validate_semver("1.0.0-alpha.1")
        assert result["is_valid"] == "true"
        assert result["prerelease"] == "alpha.1"

    def test_semver_with_build_metadata(self) -> None:
        """Test semver with build metadata."""
        result = analysis.validate_semver("1.0.0+build.123")
        assert result["is_valid"] == "true"
        assert result["build_metadata"] == "build.123"

    def test_invalid_semver(self) -> None:
        """Test invalid semantic version."""
        result = analysis.validate_semver("1.2")
        assert result["is_valid"] == "false"
        assert "Invalid semver" in result["error_message"]


class TestCheckLicenseConflicts:
    """Tests for check_license_conflicts function."""

    def test_invalid_type_packages_json(self) -> None:
        """Test TypeError when packages_json is not a string."""
        with pytest.raises(TypeError, match="packages_json must be a string"):
            analysis.check_license_conflicts(123)  # type: ignore

    def test_empty_packages_json(self) -> None:
        """Test ValueError when packages_json is empty."""
        with pytest.raises(ValueError, match="packages_json cannot be empty"):
            analysis.check_license_conflicts("")

    def test_permissive_licenses(self) -> None:
        """Test packages with permissive licenses."""
        pkgs = json.dumps(
            [
                {"name": "pkg1", "license": "MIT"},
                {"name": "pkg2", "license": "Apache-2.0"},
                {"name": "pkg3", "license": "BSD-3-Clause"},
            ]
        )
        result = analysis.check_license_conflicts(pkgs)
        assert result["permissive_count"] == "3"
        assert result["has_conflicts"] == "false"

    def test_copyleft_licenses(self) -> None:
        """Test detection of copyleft licenses."""
        pkgs = json.dumps(
            [
                {"name": "pkg1", "license": "GPL-3.0"},
                {"name": "pkg2", "license": "AGPL-3.0"},
            ]
        )
        result = analysis.check_license_conflicts(pkgs)
        assert int(result["copyleft_count"]) == 2

    def test_license_conflicts(self) -> None:
        """Test detection of license conflicts."""
        pkgs = json.dumps(
            [
                {"name": "pkg1", "license": "GPL-3.0"},
                {"name": "pkg2", "license": "Proprietary"},
            ]
        )
        result = analysis.check_license_conflicts(pkgs)
        assert result["has_conflicts"] == "true"


class TestCalculateDependencyTree:
    """Tests for calculate_dependency_tree function."""

    def test_invalid_type_dependencies_json(self) -> None:
        """Test TypeError when dependencies_json is not a string."""
        with pytest.raises(TypeError, match="dependencies_json must be a string"):
            analysis.calculate_dependency_tree(None)  # type: ignore

    def test_empty_dependencies_json(self) -> None:
        """Test ValueError when dependencies_json is empty."""
        with pytest.raises(ValueError, match="dependencies_json cannot be empty"):
            analysis.calculate_dependency_tree("")

    def test_simple_tree(self) -> None:
        """Test simple dependency tree."""
        deps = json.dumps(
            [
                {"name": "app", "requires": ["lib1", "lib2"]},
                {"name": "lib1", "requires": []},
                {"name": "lib2", "requires": []},
            ]
        )
        result = analysis.calculate_dependency_tree(deps)
        assert int(result["root_packages"]) >= 1
        assert int(result["leaf_packages"]) >= 2

    def test_deep_tree(self) -> None:
        """Test deep dependency tree."""
        deps = json.dumps(
            [
                {"name": "app", "requires": ["lib1"]},
                {"name": "lib1", "requires": ["lib2"]},
                {"name": "lib2", "requires": ["lib3"]},
                {"name": "lib3", "requires": []},
            ]
        )
        result = analysis.calculate_dependency_tree(deps)
        assert int(result["max_depth"]) >= 3


class TestFindUnusedDependencies:
    """Tests for find_unused_dependencies function."""

    def test_invalid_type_arguments(self) -> None:
        """Test TypeError when arguments are not strings."""
        with pytest.raises(TypeError):
            analysis.find_unused_dependencies(None, "[]")  # type: ignore

    def test_empty_arguments(self) -> None:
        """Test ValueError when arguments are empty."""
        with pytest.raises(ValueError):
            analysis.find_unused_dependencies("", "[]")

    def test_all_used(self) -> None:
        """Test when all dependencies are used."""
        deps = json.dumps(["requests", "django"])
        imports = json.dumps(["requests", "django"])
        result = analysis.find_unused_dependencies(deps, imports)
        assert result["has_unused"] == "false"
        assert result["unused_count"] == "0"

    def test_some_unused(self) -> None:
        """Test when some dependencies are unused."""
        deps = json.dumps(["requests", "django", "unused-lib"])
        imports = json.dumps(["requests", "django"])
        result = analysis.find_unused_dependencies(deps, imports)
        assert result["has_unused"] == "true"
        assert result["unused_count"] == "1"
        unused = json.loads(result["unused_packages"])
        assert "unused-lib" in unused


class TestIdentifyCircularDependencyChains:
    """Tests for identify_circular_dependency_chains function."""

    def test_invalid_type_dependency_graph_json(self) -> None:
        """Test TypeError when dependency_graph_json is not a string."""
        with pytest.raises(TypeError, match="dependency_graph_json must be a string"):
            analysis.identify_circular_dependency_chains(123)  # type: ignore

    def test_empty_dependency_graph_json(self) -> None:
        """Test ValueError when dependency_graph_json is empty."""
        with pytest.raises(ValueError, match="dependency_graph_json cannot be empty"):
            analysis.identify_circular_dependency_chains("")

    def test_no_circular_dependencies(self) -> None:
        """Test graph without circular dependencies."""
        graph = json.dumps({"A": ["B"], "B": ["C"], "C": []})
        result = analysis.identify_circular_dependency_chains(graph)
        assert result["has_circular"] == "false"
        assert result["cycle_count"] == "0"

    def test_circular_dependencies(self) -> None:
        """Test detection of circular dependencies."""
        graph = json.dumps({"A": ["B"], "B": ["C"], "C": ["A"]})
        result = analysis.identify_circular_dependency_chains(graph)
        assert result["has_circular"] == "true"
        assert int(result["cycle_count"]) > 0


class TestCheckOutdatedDependencies:
    """Tests for check_outdated_dependencies function."""

    def test_invalid_type_arguments(self) -> None:
        """Test TypeError when arguments are not strings."""
        with pytest.raises(TypeError):
            analysis.check_outdated_dependencies(None, "[]")  # type: ignore

    def test_empty_arguments(self) -> None:
        """Test ValueError when arguments are empty."""
        with pytest.raises(ValueError):
            analysis.check_outdated_dependencies("", "[]")

    def test_no_outdated(self) -> None:
        """Test when no packages are outdated."""
        installed = json.dumps([{"name": "lib", "version": "2.0.0"}])
        current = json.dumps([{"name": "lib", "version": "2.0.0"}])
        result = analysis.check_outdated_dependencies(installed, current)
        assert result["has_outdated"] == "false"

    def test_some_outdated(self) -> None:
        """Test when some packages are outdated."""
        installed = json.dumps([{"name": "lib", "version": "1.0.0"}])
        current = json.dumps([{"name": "lib", "version": "2.0.0"}])
        result = analysis.check_outdated_dependencies(installed, current)
        assert result["has_outdated"] == "true"
        assert int(result["outdated_count"]) > 0


class TestAnalyzeSecurityAdvisories:
    """Tests for analyze_security_advisories function."""

    def test_invalid_type_arguments(self) -> None:
        """Test TypeError when arguments are not strings."""
        with pytest.raises(TypeError):
            analysis.analyze_security_advisories(None, "[]")  # type: ignore

    def test_empty_arguments(self) -> None:
        """Test ValueError when arguments are empty."""
        with pytest.raises(ValueError):
            analysis.analyze_security_advisories("", "[]")

    def test_no_vulnerabilities(self) -> None:
        """Test when no vulnerabilities found."""
        pkgs = json.dumps([{"name": "safe-lib", "version": "1.0.0"}])
        advisories = json.dumps(
            [{"package": "other-lib", "version": "1.0.0", "cve": "CVE-2023-1234"}]
        )
        result = analysis.analyze_security_advisories(pkgs, advisories)
        assert result["has_vulnerabilities"] == "false"

    def test_vulnerabilities_found(self) -> None:
        """Test when vulnerabilities are found."""
        pkgs = json.dumps([{"name": "vuln-lib", "version": "1.0.0"}])
        advisories = json.dumps(
            [
                {
                    "package": "vuln-lib",
                    "version": "1.0.0",
                    "cve": "CVE-2023-1234",
                    "severity": "high",
                }
            ]
        )
        result = analysis.analyze_security_advisories(pkgs, advisories)
        assert result["has_vulnerabilities"] == "true"
        assert int(result["vulnerability_count"]) > 0

    def test_critical_vulnerabilities(self) -> None:
        """Test detection of critical vulnerabilities."""
        pkgs = json.dumps([{"name": "lib", "version": "1.0.0"}])
        advisories = json.dumps(
            [
                {
                    "package": "lib",
                    "version": "1.0.0",
                    "cve": "CVE-2023-9999",
                    "severity": "critical",
                }
            ]
        )
        result = analysis.analyze_security_advisories(pkgs, advisories)
        assert int(result["critical_count"]) > 0
