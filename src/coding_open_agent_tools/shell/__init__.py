"""Shell script validation and security analysis module.

This module provides validation, security scanning, parsing, and formatting
capabilities for shell scripts. It focuses on preventing errors and detecting
security issues, NOT on generating shell scripts (agents excel at that).

Key Capabilities:
- Syntax validation (bash, sh, zsh)
- Security analysis (injection risks, dangerous commands, unquoted variables)
- Argument escaping and quoting
- Script parsing and structure extraction
- Enhanced secret detection with optional detect-secrets integration
"""

from .analyzers import (
    check_error_handling,
    detect_unquoted_variables,
    find_dangerous_commands,
)
from .formatters import escape_shell_argument, normalize_shebang
from .parsers import (
    extract_shell_functions,
    extract_shell_variables,
    parse_shell_script,
)
from .security import (
    analyze_shell_security,
    detect_shell_injection_risks,
    scan_for_secrets_enhanced,
)
from .validators import check_shell_dependencies, validate_shell_syntax

__all__: list[str] = [
    # Validators
    "validate_shell_syntax",
    "check_shell_dependencies",
    # Security
    "analyze_shell_security",
    "detect_shell_injection_risks",
    "scan_for_secrets_enhanced",
    # Formatters
    "escape_shell_argument",
    "normalize_shebang",
    # Parsers
    "parse_shell_script",
    "extract_shell_functions",
    "extract_shell_variables",
    # Analyzers
    "detect_unquoted_variables",
    "find_dangerous_commands",
    "check_error_handling",
]
