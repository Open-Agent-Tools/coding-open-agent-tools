"""Dependency analysis and conflict detection for multiple languages.

This module provides comprehensive dependency management tools including:
- Multi-language parsing (requirements.txt, package.json, Cargo.toml, Poetry)
- Version conflict detection
- Circular dependency analysis
- Security vulnerability checking
- License compliance validation

Key Capabilities:
- Parse dependency files without external APIs
- Detect version conflicts and incompatibilities
- Identify circular dependency chains
- Check for outdated packages with known vulnerabilities
- Validate semantic versioning

Supports:
- Python (requirements.txt, Poetry)
- JavaScript/Node.js (package.json, package-lock.json)
- Rust (Cargo.toml)
- Multiple package managers

Token Savings: 40-60% by providing deterministic parsing and validation.
"""

from .analysis import (
    analyze_security_advisories,
    calculate_dependency_tree,
    check_license_conflicts,
    check_outdated_dependencies,
    detect_version_conflicts,
    find_unused_dependencies,
    identify_circular_dependency_chains,
    parse_cargo_toml,
    parse_package_json,
    parse_poetry_lock,
    parse_requirements_txt,
    validate_semver,
)

__all__: list[str] = [
    # Multi-language parsers (4 functions)
    "parse_requirements_txt",
    "parse_package_json",
    "parse_poetry_lock",
    "parse_cargo_toml",
    # Conflict & validation (3 functions)
    "detect_version_conflicts",
    "validate_semver",
    "check_license_conflicts",
    # Graph analysis (3 functions)
    "calculate_dependency_tree",
    "find_unused_dependencies",
    "identify_circular_dependency_chains",
    # Security (2 functions)
    "check_outdated_dependencies",
    "analyze_security_advisories",
]
