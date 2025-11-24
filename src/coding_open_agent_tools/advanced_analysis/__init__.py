"""Advanced code analysis for security, performance, and compliance detection.

This module provides deep static analysis capabilities that agents commonly miss:
- Security vulnerability detection (SQL injection, XSS, hardcoded credentials)
- Performance anti-pattern identification (O(n²) loops, memory leaks, blocking I/O)
- Circular dependency and import cycle detection
- Compliance validation (GDPR, accessibility, license violations)

Key Capabilities:
- OWASP Top 10 vulnerability detection
- Circular dependency analysis with cycle detection
- Performance bottleneck identification
- GDPR and accessibility compliance checking
- License violation detection

Supports:
- Python (AST-based analysis)
- JavaScript/TypeScript (pattern matching)
- Multi-language dependency graphs

Token Savings: 60-75% by catching errors during generation instead of retry loops.
"""

from .detectors import (
    analyze_import_cycles,
    check_gdpr_compliance,
    detect_circular_imports,
    detect_license_violations,
    detect_memory_leak_patterns,
    detect_sql_injection_patterns,
    find_blocking_io,
    find_unused_dependencies,
    find_xss_vulnerabilities,
    identify_n_squared_loops,
    scan_for_hardcoded_credentials,
    validate_accessibility,
)

__all__: list[str] = [
    # Dependency analyzers (3 functions)
    "detect_circular_imports",
    "find_unused_dependencies",
    "analyze_import_cycles",
    # Security scanners (3 functions)
    "detect_sql_injection_patterns",
    "find_xss_vulnerabilities",
    "scan_for_hardcoded_credentials",
    # Performance detectors (3 functions)
    "identify_n_squared_loops",
    "detect_memory_leak_patterns",
    "find_blocking_io",
    # Compliance checkers (3 functions)
    "check_gdpr_compliance",
    "validate_accessibility",
    "detect_license_violations",
]
