"""Configuration validation and manipulation tools.

Provides validation for YAML, TOML, JSON, CI/CD configs, dependency conflicts,
security scanning, .env file parsing, config extraction, format parsing,
and security best practices for configuration files.
"""

from .best_practices import (
    check_gitignore_security,
    detect_exposed_config_files,
    validate_config_permissions,
)
from .env import (
    extract_env_variable,
    merge_env_files,
    parse_env_file,
    substitute_env_variables,
    validate_env_file,
)
from .extraction import (
    extract_json_value,
    extract_toml_value,
    extract_yaml_value,
    interpolate_config_variables,
    merge_toml_files,
    merge_yaml_files,
)
from .formats import (
    parse_ini_file,
    parse_properties_file,
    parse_xml_value,
    validate_ini_syntax,
    validate_xml_syntax,
)
from .security import (
    detect_insecure_settings,
    scan_config_for_secrets,
)
from .validation import (
    check_dependency_conflicts,
    validate_github_actions_config,
    validate_json_schema,
    validate_json_syntax,
    validate_toml_syntax,
    validate_version_specifier,
    validate_yaml_syntax,
)

__all__ = [
    # Security
    "detect_insecure_settings",
    "scan_config_for_secrets",
    # Validation
    "check_dependency_conflicts",
    "validate_github_actions_config",
    "validate_json_schema",
    "validate_json_syntax",
    "validate_toml_syntax",
    "validate_version_specifier",
    "validate_yaml_syntax",
    # .env file support
    "extract_env_variable",
    "merge_env_files",
    "parse_env_file",
    "substitute_env_variables",
    "validate_env_file",
    # Config extraction
    "extract_json_value",
    "extract_toml_value",
    "extract_yaml_value",
    "interpolate_config_variables",
    "merge_toml_files",
    "merge_yaml_files",
    # Common formats
    "parse_ini_file",
    "parse_properties_file",
    "parse_xml_value",
    "validate_ini_syntax",
    "validate_xml_syntax",
    # Best practices
    "check_gitignore_security",
    "detect_exposed_config_files",
    "validate_config_permissions",
]
