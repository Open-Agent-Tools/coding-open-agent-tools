"""Advanced code analysis detectors for security, performance, and compliance.

This module provides deep static analysis capabilities for detecting issues
that agents commonly miss during code generation.
"""

import json
import re
from typing import Any, Callable, Optional

# Conditional import for strands decorator
try:
    from strands_agents import tool as strands_tool
except ImportError:

    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        return func


@strands_tool
def detect_circular_imports(import_graph_json: str) -> dict[str, str]:
    """Detect circular import dependencies in module import graph.

    Analyzes import relationships to find circular dependency chains using
    depth-first search. Identifies all cycles and affected modules.

    Args:
        import_graph_json: JSON string of import graph (module: [imports])

    Returns:
        Dictionary with:
        - has_circular: "true" if circular imports detected
        - cycle_count: Number of circular dependency chains
        - cycles: JSON array of circular chains
        - affected_modules: JSON array of modules in cycles
        - severity: "critical", "high", "medium", or "low"
        - suggestions: Recommended fixes

    Raises:
        TypeError: If import_graph_json is not a string
        ValueError: If import_graph_json is empty or invalid JSON

    Example:
        >>> graph = '{"A": ["B"], "B": ["C"], "C": ["A"]}'
        >>> result = detect_circular_imports(graph)
        >>> result["has_circular"]
        'true'
    """
    if not isinstance(import_graph_json, str):
        raise TypeError("import_graph_json must be a string")
    if not import_graph_json.strip():
        raise ValueError("import_graph_json cannot be empty")

    try:
        graph = json.loads(import_graph_json)
    except json.JSONDecodeError as e:
        return {
            "has_circular": "false",
            "cycle_count": "0",
            "cycles": "[]",
            "affected_modules": "[]",
            "severity": "none",
            "suggestions": "[]",
            "error": f"Invalid JSON: {e}",
        }

    # DFS to detect cycles
    cycles = []
    visited = set()
    rec_stack = set()
    path: list[str] = []

    def dfs(node: str) -> None:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        path.pop()
        rec_stack.remove(node)

    for node in graph:
        if node not in visited:
            dfs(node)

    # Remove duplicate cycles
    unique_cycles = []
    seen_cycles = set()
    for cycle in cycles:
        min_idx = cycle.index(min(cycle))
        normalized = tuple(cycle[min_idx:] + cycle[:min_idx])
        if normalized not in seen_cycles:
            seen_cycles.add(normalized)
            unique_cycles.append(cycle)

    # Get affected modules
    affected = list({mod for cycle in unique_cycles for mod in cycle})

    # Determine severity
    if not unique_cycles:
        severity = "none"
    elif len(unique_cycles) > 5 or any(len(c) > 5 for c in unique_cycles):
        severity = "critical"
    elif len(unique_cycles) > 2 or any(len(c) > 3 for c in unique_cycles):
        severity = "high"
    elif len(unique_cycles) > 1 or any(len(c) > 2 for c in unique_cycles):
        severity = "medium"
    else:
        severity = "low"

    suggestions = []
    if unique_cycles:
        suggestions.append("Refactor to remove circular dependencies")
        suggestions.append("Consider dependency injection or interface abstraction")
        suggestions.append("Move shared code to a separate module")
        if severity in ["critical", "high"]:
            suggestions.append("URGENT: Circular imports can cause runtime errors")

    return {
        "has_circular": "true" if unique_cycles else "false",
        "cycle_count": str(len(unique_cycles)),
        "cycles": json.dumps(unique_cycles),
        "affected_modules": json.dumps(affected),
        "severity": severity,
        "suggestions": json.dumps(suggestions),
    }


@strands_tool
def find_unused_dependencies(
    dependencies_json: str, imports_json: str
) -> dict[str, str]:
    """Find declared dependencies that are never imported or used.

    Compares declared dependencies against actual imports in the codebase
    to identify unused packages that can be removed.

    Args:
        dependencies_json: JSON array of declared dependency names
        imports_json: JSON array of actual import statements

    Returns:
        Dictionary with:
        - has_unused: "true" if unused dependencies found
        - unused_count: Number of unused dependencies
        - unused_dependencies: JSON array of unused dependency names
        - usage_percentage: Percentage of declared deps actually used
        - potential_savings: Estimated size/install time savings
        - suggestions: Cleanup recommendations

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty or invalid JSON

    Example:
        >>> declared = '["requests", "numpy", "unused-lib"]'
        >>> actual = '["import requests", "import numpy"]'
        >>> result = find_unused_dependencies(declared, actual)
        >>> result["unused_count"]
        '1'
    """
    if not isinstance(dependencies_json, str):
        raise TypeError("dependencies_json must be a string")
    if not isinstance(imports_json, str):
        raise TypeError("imports_json must be a string")
    if not dependencies_json.strip():
        raise ValueError("dependencies_json cannot be empty")
    if not imports_json.strip():
        raise ValueError("imports_json cannot be empty")

    try:
        declared = json.loads(dependencies_json)
        imports = json.loads(imports_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    # Common package name to import name mappings
    PACKAGE_MAPPINGS = {
        "pyyaml": "yaml",
        "pillow": "PIL",
        "python_dateutil": "dateutil",
        "attrs": "attr",
        "beautifulsoup4": "bs4",
        "protobuf": "google_protobuf",
        "googleapis_common_protos": "google",
        "google_cloud_storage": "google_cloud_storage",
    }

    # Normalize names (handle package name vs import name differences)
    def normalize(name: str) -> str:
        normalized = name.lower().replace("-", "_").replace(".", "_")
        # Check if this matches a known package mapping
        if normalized in PACKAGE_MAPPINGS:
            return PACKAGE_MAPPINGS[normalized].lower().replace(".", "_")
        return normalized

    # Extract package names from import statements
    import_names = set()
    for imp in imports:
        # Handle "import package" or "from package import ..."
        match = re.match(r"(?:from|import)\s+([A-Za-z_][A-Za-z0-9_.\-]*)", imp)
        if match:
            pkg = match.group(1)
            # Handle google.cloud.storage -> google_cloud_storage
            import_names.add(pkg.replace(".", "_"))
            # Also add first part for packages like google.cloud.storage -> google
            if "." in pkg:
                import_names.add(pkg.split(".")[0])
        else:
            # If no import keyword, treat as package name directly
            import_names.add(imp.replace(".", "_"))

    declared_normalized = {normalize(d): d for d in declared}
    import_normalized = {normalize(i) for i in import_names}

    # Find unused
    unused = [
        orig_name
        for norm_name, orig_name in declared_normalized.items()
        if norm_name not in import_normalized
    ]

    usage_pct = (
        ((len(declared) - len(unused)) / len(declared) * 100) if declared else 100
    )

    # Estimate savings (rough heuristic)
    if len(unused) <= 2:
        savings = "minimal"
    elif len(unused) <= 5:
        savings = "moderate"
    else:
        savings = "significant"

    suggestions = []
    if unused:
        suggestions.append(f"Remove {len(unused)} unused dependencies")
        suggestions.append("Verify dependencies aren't used dynamically or in tests")
        suggestions.append("Check for different package vs import names")
        if len(unused) > 5:
            suggestions.append("Consider dependency audit for bloat reduction")

    return {
        "has_unused": "true" if unused else "false",
        "unused_count": str(len(unused)),
        "unused_dependencies": json.dumps(unused),
        "usage_percentage": f"{usage_pct:.1f}",
        "potential_savings": savings,
        "suggestions": json.dumps(suggestions),
    }


@strands_tool
def analyze_import_cycles(import_graph_json: str) -> dict[str, str]:
    """Analyze import cycle complexity and provide metrics.

    Calculates metrics about import relationships including cycle count,
    maximum cycle length, and overall graph complexity.

    Args:
        import_graph_json: JSON string of import graph (module: [imports])

    Returns:
        Dictionary with:
        - total_modules: Total number of modules
        - total_imports: Total number of import statements
        - cycle_count: Number of import cycles
        - max_cycle_length: Length of longest cycle
        - avg_dependencies: Average imports per module
        - complexity_score: Overall complexity rating (0-100)
        - health_status: "healthy", "needs_attention", or "critical"
        - recommendations: Architecture improvement suggestions

    Raises:
        TypeError: If import_graph_json is not a string
        ValueError: If import_graph_json is empty or invalid JSON

    Example:
        >>> graph = '{"A": ["B"], "B": ["C"], "C": []}'
        >>> result = analyze_import_cycles(graph)
        >>> result["health_status"]
        'healthy'
    """
    if not isinstance(import_graph_json, str):
        raise TypeError("import_graph_json must be a string")
    if not import_graph_json.strip():
        raise ValueError("import_graph_json cannot be empty")

    try:
        graph = json.loads(import_graph_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    # Calculate basic metrics
    total_modules = len(graph)
    total_imports = sum(len(deps) for deps in graph.values())
    avg_deps = total_imports / total_modules if total_modules else 0

    # Find cycles using detect_circular_imports logic
    cycles = []
    visited = set()
    rec_stack = set()
    path: list[str] = []

    def dfs(node: str) -> None:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:]
                cycles.append(cycle)

        path.pop()
        rec_stack.remove(node)

    for node in graph:
        if node not in visited:
            dfs(node)

    cycle_count = len(cycles)
    max_cycle_length = max((len(c) for c in cycles), default=0)

    # Calculate complexity score (0-100, higher is worse)
    complexity = 0
    complexity += min(cycle_count * 10, 40)  # Cycles: up to 40 points
    complexity += min(int(avg_deps * 5), 30)  # Avg deps: up to 30 points
    complexity += min(max_cycle_length * 5, 30)  # Max cycle: up to 30 points

    # Determine health status
    if complexity >= 70:
        health = "critical"
    elif complexity >= 40:
        health = "needs_attention"
    else:
        health = "healthy"

    recommendations = []
    if cycle_count > 0:
        recommendations.append("Break circular dependencies immediately")
    if avg_deps > 10:
        recommendations.append("Reduce average dependencies per module")
    if max_cycle_length > 3:
        recommendations.append("Long dependency chains indicate architectural issues")
    if health == "healthy":
        recommendations.append("Dependency structure is well-organized")

    return {
        "total_modules": str(total_modules),
        "total_imports": str(total_imports),
        "has_cycles": "true" if cycle_count > 0 else "false",
        "cycle_count": str(cycle_count),
        "max_cycle_length": str(max_cycle_length),
        "average_imports_per_module": f"{avg_deps:.2f}",
        "avg_dependencies": f"{avg_deps:.2f}",
        "complexity_score": f"{complexity:.1f}",
        "health_status": health,
        "recommendations": json.dumps(recommendations),
    }


@strands_tool
def detect_sql_injection_patterns(source_code: str, language: str) -> dict[str, str]:
    """Detect SQL injection vulnerability patterns in code.

    Analyzes code for common SQL injection vulnerabilities including
    string concatenation in queries, unparameterized inputs, and unsafe
    dynamic SQL construction.

    Args:
        source_code: Source code to analyze
        language: Programming language ("python", "javascript", "java", etc.)

    Returns:
        Dictionary with:
        - has_vulnerabilities: "true" if SQL injection risks found
        - vulnerability_count: Number of potential vulnerabilities
        - vulnerabilities: JSON array of vulnerability details
        - severity: "critical", "high", "medium", or "low"
        - affected_lines: JSON array of line numbers
        - remediation: JSON array of fix suggestions

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty

    Example:
        >>> code = 'query = "SELECT * FROM users WHERE id=" + user_id'
        >>> result = detect_sql_injection_patterns(code, "python")
        >>> result["has_vulnerabilities"]
        'true'
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(language, str):
        raise TypeError("language must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")
    if not language.strip():
        raise ValueError("language cannot be empty")

    vulnerabilities = []
    affected_lines = []

    lines = source_code.split("\n")
    lang = language.lower()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Pattern 1: String concatenation in SQL queries
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "CREATE"]
        if any(kw in stripped.upper() for kw in sql_keywords):
            # Check for concatenation
            if lang == "python":
                if (
                    "+" in stripped
                    or ".format(" in stripped
                    or 'f"' in stripped
                    or "f'" in stripped
                ):
                    vulnerabilities.append(
                        {
                            "line": i,
                            "type": "sql_injection",
                            "pattern": "string_concatenation",
                            "severity": "critical",
                        }
                    )
                    affected_lines.append(i)
            elif lang in ["javascript", "typescript"]:
                if "+" in stripped or "${" in stripped:
                    vulnerabilities.append(
                        {
                            "line": i,
                            "type": "sql_injection",
                            "pattern": "string_concatenation",
                            "severity": "critical",
                        }
                    )
                    affected_lines.append(i)

        # Pattern 2: Direct user input in queries
        user_input_vars = ["request", "input", "params", "body", "query", "req."]
        if any(var in stripped for var in user_input_vars):
            if any(kw in stripped.upper() for kw in sql_keywords):
                vulnerabilities.append(
                    {
                        "line": i,
                        "type": "sql_injection",
                        "pattern": "unparameterized_input",
                        "severity": "high",
                    }
                )
                affected_lines.append(i)

        # Pattern 3: exec/execute without parameterization
        if lang == "python":
            if "execute(" in stripped and "%" in stripped:
                vulnerabilities.append(
                    {
                        "line": i,
                        "type": "sql_injection",
                        "pattern": "unsafe_execute",
                        "severity": "critical",
                    }
                )
                affected_lines.append(i)

    # Determine overall severity
    if any(v["severity"] == "critical" for v in vulnerabilities):
        severity = "critical"
    elif any(v["severity"] == "high" for v in vulnerabilities):
        severity = "high"
    elif vulnerabilities:
        severity = "medium"
    else:
        severity = "none"

    remediation = []
    if vulnerabilities:
        remediation.append("Use parameterized queries or prepared statements")
        remediation.append("Never concatenate user input into SQL queries")
        remediation.append("Use ORM methods that automatically parameterize")
        if lang == "python":
            remediation.append(
                "Use execute() with tuple parameters: execute(query, (param1, param2))"
            )
        elif lang in ["javascript", "typescript"]:
            remediation.append(
                "Use placeholders: query('SELECT * FROM users WHERE id = ?', [userId])"
            )

    return {
        "has_vulnerabilities": "true" if vulnerabilities else "false",
        "vulnerability_count": str(len(vulnerabilities)),
        "vulnerabilities": json.dumps(vulnerabilities),
        "severity": severity,
        "affected_lines": json.dumps(affected_lines),
        "remediation": json.dumps(remediation),
    }


@strands_tool
def find_xss_vulnerabilities(source_code: str, language: str) -> dict[str, str]:
    """Find Cross-Site Scripting (XSS) vulnerability patterns.

    Detects potential XSS vulnerabilities including unescaped output,
    innerHTML usage, dangerous DOM methods, and unsanitized user input.

    Args:
        source_code: Source code to analyze
        language: Programming language ("javascript", "python", "java", etc.)

    Returns:
        Dictionary with:
        - has_vulnerabilities: "true" if XSS risks found
        - vulnerability_count: Number of potential XSS issues
        - vulnerabilities: JSON array of XSS patterns found
        - severity: "critical", "high", "medium", or "low"
        - affected_lines: JSON array of line numbers
        - remediation: JSON array of fix suggestions

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty

    Example:
        >>> code = 'element.innerHTML = userInput'
        >>> result = find_xss_vulnerabilities(code, "javascript")
        >>> result["has_vulnerabilities"]
        'true'
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(language, str):
        raise TypeError("language must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")
    if not language.strip():
        raise ValueError("language cannot be empty")

    vulnerabilities = []
    affected_lines = []

    lines = source_code.split("\n")
    lang = language.lower()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Pattern 1: innerHTML/outerHTML usage
        if lang in ["javascript", "typescript"]:
            if ".innerHTML" in stripped or ".outerHTML" in stripped:
                if "=" in stripped:  # Assignment
                    vulnerabilities.append(
                        {
                            "line": i,
                            "type": "xss",
                            "pattern": "innerHTML_assignment",
                            "severity": "high",
                        }
                    )
                    affected_lines.append(i)

            # Pattern 2: document.write
            if "document.write(" in stripped:
                vulnerabilities.append(
                    {
                        "line": i,
                        "type": "xss",
                        "pattern": "document.write",
                        "severity": "high",
                    }
                )
                affected_lines.append(i)

            # Pattern 3: eval() with user input
            if "eval(" in stripped:
                vulnerabilities.append(
                    {
                        "line": i,
                        "type": "xss",
                        "pattern": "eval_usage",
                        "severity": "critical",
                    }
                )
                affected_lines.append(i)

            # Pattern 4: dangerouslySetInnerHTML (React)
            if "dangerouslySetInnerHTML" in stripped:
                vulnerabilities.append(
                    {
                        "line": i,
                        "type": "xss",
                        "pattern": "dangerouslySetInnerHTML",
                        "severity": "high",
                    }
                )
                affected_lines.append(i)

        # Pattern 5: Template rendering without escaping
        if lang == "python":
            if "render_template_string(" in stripped and "{{" in stripped:
                vulnerabilities.append(
                    {
                        "line": i,
                        "type": "xss",
                        "pattern": "unescaped_template",
                        "severity": "high",
                    }
                )
                affected_lines.append(i)

            # Pattern 6: Marking safe without sanitization
            if "|safe" in stripped or "mark_safe(" in stripped:
                vulnerabilities.append(
                    {
                        "line": i,
                        "type": "xss",
                        "pattern": "unsafe_marking",
                        "severity": "medium",
                    }
                )
                affected_lines.append(i)

    # Determine severity
    if any(v["severity"] == "critical" for v in vulnerabilities):
        severity = "critical"
    elif any(v["severity"] == "high" for v in vulnerabilities):
        severity = "high"
    elif vulnerabilities:
        severity = "medium"
    else:
        severity = "none"

    remediation = []
    if vulnerabilities:
        remediation.append("Always escape user input before rendering")
        remediation.append("Use textContent instead of innerHTML")
        remediation.append("Sanitize HTML with DOMPurify or similar libraries")
        if lang in ["javascript", "typescript"]:
            remediation.append("Avoid eval(), document.write(), and innerHTML")
            remediation.append(
                "Use createElement() and textContent for DOM manipulation"
            )
        if lang == "python":
            remediation.append("Use auto-escaping template engines (Jinja2)")

    return {
        "has_vulnerabilities": "true" if vulnerabilities else "false",
        "vulnerability_count": str(len(vulnerabilities)),
        "vulnerabilities": json.dumps(vulnerabilities),
        "severity": severity,
        "affected_lines": json.dumps(affected_lines),
        "remediation": json.dumps(remediation),
    }


@strands_tool
def scan_for_hardcoded_credentials(source_code: str) -> dict[str, str]:
    """Scan code for hardcoded credentials and secrets.

    Detects hardcoded passwords, API keys, tokens, and other sensitive
    credentials that should be in environment variables or secret managers.

    Args:
        source_code: Source code to scan

    Returns:
        Dictionary with:
        - has_secrets: "true" if hardcoded credentials found
        - secret_count: Number of potential secrets
        - secrets: JSON array of secret patterns found
        - severity: "critical", "high", "medium", or "low"
        - affected_lines: JSON array of line numbers
        - remediation: JSON array of fix suggestions

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty

    Example:
        >>> code = 'api_key = "sk-1234567890abcdef"'
        >>> result = scan_for_hardcoded_credentials(code)
        >>> result["has_secrets"]
        'true'
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    secrets = []
    affected_lines = []

    lines = source_code.split("\n")

    # Secret patterns
    patterns = [
        (
            r"password\s*=\s*['\"](?!.*(PASSWORD|password|\{|\$))(.{8,})['\"]",
            "password",
            "critical",
        ),
        (r"api[_-]?key\s*=\s*['\"]([A-Za-z0-9_\-]{10,})['\"]", "api_key", "critical"),
        (
            r"secret([_-]?key)?\s*=\s*['\"]([A-Za-z0-9_\-/+=]{10,})['\"]",
            "secret_key",
            "critical",
        ),
        (
            r"aws[_-]?secret[_-]?(access[_-]?)?key\s*=\s*['\"]([A-Za-z0-9/+=]{20,})['\"]",
            "aws_key",
            "critical",
        ),
        (r"token\s*=\s*['\"]([A-Za-z0-9_\-\.]{10,})['\"]", "token", "high"),
        (
            r"private[_-]?key\s*=\s*['\"]([A-Za-z0-9+/=\n\-]{40,})['\"]",
            "private_key",
            "critical",
        ),
        (
            r"aws[_-]?access[_-]?key[_-]?id\s*=\s*['\"]([A-Z0-9]{20})['\"]",
            "aws_access_key",
            "critical",
        ),
        (
            r"sk-[a-zA-Z0-9\-]{10,}",
            "openai_key",
            "critical",
        ),  # OpenAI keys (flexible length)
        (
            r"ghp_[a-zA-Z0-9]{10,}",
            "github_token",
            "critical",
        ),  # GitHub tokens (flexible length)
    ]

    for i, line in enumerate(lines, 1):
        for pattern, secret_type, sev in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                secrets.append(
                    {
                        "line": i,
                        "type": secret_type,
                        "severity": sev,
                        "snippet": line.strip()[:50] + "...",
                    }
                )
                affected_lines.append(i)

    # Remove duplicates
    unique_secrets = []
    seen_lines = set()
    for secret in secrets:
        if secret["line"] not in seen_lines:
            unique_secrets.append(secret)
            seen_lines.add(secret["line"])

    # Determine severity
    if any(s["severity"] == "critical" for s in unique_secrets):
        severity = "critical"
    elif any(s["severity"] == "high" for s in unique_secrets):
        severity = "high"
    elif unique_secrets:
        severity = "medium"
    else:
        severity = "none"

    remediation = []
    if unique_secrets:
        remediation.append("Move all secrets to environment variables")
        remediation.append(
            "Use secret management services (AWS Secrets Manager, Vault)"
        )
        remediation.append("Add .env to .gitignore")
        remediation.append("Rotate any exposed credentials immediately")
        remediation.append("Use os.environ.get() or process.env to access secrets")

    return {
        "has_secrets": "true" if unique_secrets else "false",
        "secret_count": str(len(unique_secrets)),
        "secrets": json.dumps(unique_secrets),
        "severity": severity,
        "affected_lines": json.dumps(affected_lines),
        "remediation": json.dumps(remediation),
    }


@strands_tool
def identify_n_squared_loops(source_code: str, language: str) -> dict[str, str]:
    """Identify O(n²) nested loop anti-patterns.

    Detects nested loops that may cause performance issues, especially
    when iterating over the same collection or making quadratic operations.

    Args:
        source_code: Source code to analyze
        language: Programming language ("python", "javascript", "java", etc.)

    Returns:
        Dictionary with:
        - has_anti_patterns: "true" if O(n²) patterns found
        - pattern_count: Number of nested loop patterns
        - patterns: JSON array of pattern details
        - severity: "critical", "high", "medium", or "low"
        - affected_lines: JSON array of line numbers
        - optimization_suggestions: JSON array of improvement ideas

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty

    Example:
        >>> code = 'for i in items:\\n  for j in items:\\n    process(i, j)'
        >>> result = identify_n_squared_loops(code, "python")
        >>> result["has_anti_patterns"]
        'true'
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(language, str):
        raise TypeError("language must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")
    if not language.strip():
        raise ValueError("language cannot be empty")

    patterns = []
    affected_lines = []

    lines = source_code.split("\n")
    lang = language.lower()

    # Track loop depth and variables
    loop_stack: list[tuple[int, Optional[str], int]] = []

    for i, line in enumerate(lines, 1):
        # Skip empty or whitespace-only lines for indentation tracking
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # First, clean up the stack based on indentation
        # Remove loops that we've exited (current line dedented back to their level or less)
        loop_stack = [(ind, var, ln) for ind, var, ln in loop_stack if indent > ind]

        # Detect loop start
        is_loop = False
        loop_var = None

        if lang == "python":
            if stripped.startswith("for "):
                is_loop = True
                # Extract variable: "for x in items:"
                match = re.match(r"for\s+(\w+)\s+in\s+(\w+)", stripped)
                if match:
                    loop_var = match.group(2)  # Collection name
        elif lang in ["javascript", "typescript"]:
            if stripped.startswith("for ") or "forEach" in stripped:
                is_loop = True
                # Extract collection
                if "forEach" in stripped:
                    match = re.search(r"(\w+)\.forEach", stripped)
                    if match:
                        loop_var = match.group(1)
                else:
                    match = re.search(r"of\s+(\w+)", stripped)
                    if match:
                        loop_var = match.group(1)

        if is_loop:
            # Check if nested in another loop
            if loop_stack:
                # Check if iterating same collection
                for _outer_indent, outer_var, outer_line in loop_stack:
                    if loop_var and outer_var and outer_var == loop_var:
                        patterns.append(
                            {
                                "line": i,
                                "outer_line": outer_line,
                                "type": "nested loop over same collection",
                                "severity": "high",
                                "collection": loop_var,
                            }
                        )
                        affected_lines.extend([outer_line, i])
                    else:
                        patterns.append(
                            {
                                "line": i,
                                "outer_line": outer_line,
                                "type": "nested loop",
                                "severity": "medium",
                            }
                        )
                        affected_lines.append(i)

            loop_stack.append((indent, loop_var, i))

    # Determine severity
    if any(p["severity"] == "high" for p in patterns):
        severity = "high"
    elif patterns:
        severity = "medium"
    else:
        severity = "none"

    suggestions = []
    if patterns:
        suggestions.append("Consider using hash maps/sets for O(1) lookups")
        suggestions.append(
            "Use list comprehensions or map/filter instead of nested loops"
        )
        suggestions.append("Consider algorithmic improvements (sorting + two-pointer)")
        suggestions.append("Profile to confirm performance impact")
        if any("same collection" in str(p.get("type", "")).lower() for p in patterns):
            suggestions.append("CRITICAL: Nested loops over same collection = O(n²)")

    return {
        "has_anti_patterns": "true" if patterns else "false",
        "pattern_count": str(len(patterns)),
        "patterns": json.dumps(patterns),
        "severity": severity,
        "affected_lines": json.dumps(list(set(affected_lines))),
        "optimization_suggestions": json.dumps(suggestions),
    }


@strands_tool
def detect_memory_leak_patterns(source_code: str, language: str) -> dict[str, str]:
    """Detect common memory leak patterns in code.

    Identifies patterns that commonly cause memory leaks including unclosed
    resources, circular references, global variable accumulation, and event
    listener leaks.

    Args:
        source_code: Source code to analyze
        language: Programming language ("python", "javascript", "java", etc.)

    Returns:
        Dictionary with:
        - has_leak_patterns: "true" if leak patterns found
        - pattern_count: Number of potential leak patterns
        - patterns: JSON array of leak pattern details
        - severity: "critical", "high", "medium", or "low"
        - affected_lines: JSON array of line numbers
        - remediation: JSON array of fix suggestions

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty

    Example:
        >>> code = 'file = open("data.txt")\\ndata = file.read()'
        >>> result = detect_memory_leak_patterns(code, "python")
        >>> result["has_leak_patterns"]
        'true'
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(language, str):
        raise TypeError("language must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")
    if not language.strip():
        raise ValueError("language cannot be empty")

    patterns = []
    affected_lines = []

    lines = source_code.split("\n")
    lang = language.lower()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Pattern 1: Unclosed file handles
        if lang == "python":
            if "open(" in stripped and "with " not in stripped:
                # Check if .close() is present in next few lines (i is 1-indexed, lines is 0-indexed)
                # Skip lines that are comments
                has_close = any(
                    ".close()" in lines[j].strip()
                    and not lines[j].strip().startswith("#")
                    for j in range(i - 1, min(i + 10, len(lines)))
                )
                if not has_close:
                    patterns.append(
                        {
                            "line": i,
                            "type": "file",
                            "severity": "high",
                        }
                    )
                    affected_lines.append(i)

        # Pattern 2: Event listeners without removal
        if lang in ["javascript", "typescript"]:
            if "addEventListener(" in stripped:
                # Check for removeEventListener in reasonable range (i is 1-indexed, lines is 0-indexed)
                has_remove = any(
                    "removeEventListener(" in lines[j].strip()
                    for j in range(i - 1, min(i + 50, len(lines)))
                )
                if not has_remove:
                    patterns.append(
                        {
                            "line": i,
                            "type": "event_listener",
                            "severity": "medium",
                        }
                    )
                    affected_lines.append(i)

            # Pattern 3: setInterval without clearInterval
            if "setInterval(" in stripped:
                # Check for clearInterval in reasonable range (i is 1-indexed, lines is 0-indexed)
                has_clear = any(
                    "clearInterval(" in lines[j].strip()
                    for j in range(i - 1, min(i + 50, len(lines)))
                )
                if not has_clear:
                    patterns.append(
                        {
                            "line": i,
                            "type": "interval",
                            "severity": "high",
                        }
                    )
                    affected_lines.append(i)

        # Pattern 4: Growing global arrays/objects
        # Check for append/push on global-looking variables (lowercase with underscores, no self/this)
        if any(op in stripped for op in [".append(", ".push("]):
            # Python: look for global_var.append() or just var.append() patterns
            # JavaScript: look for var/const declarations or direct .push()
            is_global_pattern = (
                lang == "python" and "self." not in stripped and "." in stripped
            ) or (lang in ["javascript", "typescript"])
            if is_global_pattern:
                patterns.append(
                    {
                        "line": i,
                        "type": "global",
                        "severity": "medium",
                    }
                )
                affected_lines.append(i)

    # Determine severity
    if any(p["severity"] == "high" for p in patterns):
        severity = "high"
    elif patterns:
        severity = "medium"
    else:
        severity = "none"

    remediation = []
    if patterns:
        remediation.append("Use context managers (with statements) for resources")
        remediation.append("Always remove event listeners in cleanup/unmount")
        remediation.append("Clear intervals and timeouts when done")
        remediation.append("Avoid accumulating data in global variables")
        if lang == "python":
            remediation.append("Use 'with open(file) as f:' instead of open()")
        if lang in ["javascript", "typescript"]:
            remediation.append("Use cleanup functions in useEffect() hooks")

    return {
        "has_leak_patterns": "true" if patterns else "false",
        "pattern_count": str(len(patterns)),
        "patterns": json.dumps(patterns),
        "severity": severity,
        "affected_lines": json.dumps(affected_lines),
        "remediation": json.dumps(remediation),
    }


@strands_tool
def find_blocking_io(source_code: str, language: str) -> dict[str, str]:
    """Find blocking I/O operations that should be async.

    Identifies synchronous I/O operations that could block the event loop
    or thread, including file I/O, network requests, and database calls.

    Args:
        source_code: Source code to analyze
        language: Programming language ("python", "javascript", "java", etc.)

    Returns:
        Dictionary with:
        - has_blocking_io: "true" if blocking I/O found
        - blocking_count: Number of blocking operations
        - operations: JSON array of blocking operation details
        - severity: "critical", "high", "medium", or "low"
        - affected_lines: JSON array of line numbers
        - async_suggestions: JSON array of async alternatives

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty

    Example:
        >>> code = 'data = requests.get("https://api.example.com")'
        >>> result = find_blocking_io(code, "python")
        >>> result["has_blocking_io"]
        'true'
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(language, str):
        raise TypeError("language must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")
    if not language.strip():
        raise ValueError("language cannot be empty")

    operations = []
    affected_lines = []

    lines = source_code.split("\n")
    lang = language.lower()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Check if already async
        is_async = "await " in stripped or "async " in stripped

        if not is_async:
            # Pattern 1: Synchronous HTTP requests
            if lang == "python":
                if "requests." in stripped and any(
                    method in stripped
                    for method in [".get(", ".post(", ".put(", ".delete("]
                ):
                    operations.append(
                        {
                            "line": i,
                            "type": "http_request",
                            "library": "requests",
                            "severity": "high",
                        }
                    )
                    affected_lines.append(i)

                # Pattern 2: Synchronous file operations (including with statements)
                if "open(" in stripped:
                    operations.append(
                        {
                            "line": i,
                            "type": "file",
                            "severity": "medium",
                        }
                    )
                    affected_lines.append(i)

                # Pattern 3: time.sleep() - blocking delay
                if "time.sleep(" in stripped:
                    operations.append(
                        {
                            "line": i,
                            "type": "blocking_sleep",
                            "severity": "high",
                        }
                    )
                    affected_lines.append(i)

            elif lang in ["javascript", "typescript"]:
                # Pattern 4: XMLHttpRequest (sync) - look for .open() with false
                if "XMLHttpRequest" in stripped or (
                    ".open(" in stripped and "false" in stripped
                ):
                    operations.append(
                        {
                            "line": i,
                            "type": "xhr",
                            "severity": "critical",
                        }
                    )
                    affected_lines.append(i)

                # Pattern 5: fs.readFileSync
                if "Sync(" in stripped or "Sync " in stripped:
                    operations.append(
                        {
                            "line": i,
                            "type": "sync_fs",
                            "severity": "high",
                        }
                    )
                    affected_lines.append(i)

    # Determine severity
    if any(op["severity"] == "critical" for op in operations):
        severity = "critical"
    elif any(op["severity"] == "high" for op in operations):
        severity = "high"
    elif operations:
        severity = "medium"
    else:
        severity = "none"

    suggestions = []
    if operations:
        if lang == "python":
            suggestions.append("Use aiohttp or httpx for async HTTP requests")
            suggestions.append("Use aiofiles for async file operations")
            suggestions.append("Replace time.sleep() with await asyncio.sleep()")
        elif lang in ["javascript", "typescript"]:
            suggestions.append("Use fetch() or axios with await")
            suggestions.append("Use fs.promises or async variants")
            suggestions.append("Avoid *Sync() methods in Node.js")
        suggestions.append("Wrap operations in async functions")

    return {
        "has_blocking_io": "true" if operations else "false",
        "blocking_count": str(len(operations)),
        "operations": json.dumps(operations),
        "severity": severity,
        "affected_lines": json.dumps(affected_lines),
        "async_suggestions": json.dumps(suggestions),
    }


@strands_tool
def check_gdpr_compliance(source_code: str, language: str) -> dict[str, str]:
    """Check code for GDPR compliance issues.

    Identifies potential GDPR violations including missing consent checks,
    improper data handling, lack of data deletion, and missing audit trails.

    Args:
        source_code: Source code to analyze
        language: Programming language ("python", "javascript", "java", etc.)

    Returns:
        Dictionary with:
        - has_compliance_issues: "true" if GDPR issues found
        - issue_count: Number of potential GDPR violations
        - issues: JSON array of compliance issue details
        - severity: "critical", "high", "medium", or "low"
        - affected_lines: JSON array of line numbers
        - compliance_recommendations: JSON array of fixes

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty

    Example:
        >>> code = 'user_data = {"email": email, "ip": request.ip}'
        >>> result = check_gdpr_compliance(code, "python")
        >>> result["has_compliance_issues"]
        'true'
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not isinstance(language, str):
        raise TypeError("language must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")
    if not language.strip():
        raise ValueError("language cannot be empty")

    issues = []
    affected_lines = []

    lines = source_code.split("\n")

    # PII data identifiers
    pii_keywords = [
        "email",
        "phone",
        "address",
        "ssn",
        "passport",
        "credit_card",
        "ip_address",
        "geolocation",
        "biometric",
        "user",  # user tables/data often contain PII
        "customer",
        "person",
        "profile",
        "contact",
    ]

    for i, line in enumerate(lines, 1):
        stripped = line.strip().lower()

        # Pattern 1: Collecting PII without consent check
        # Check for form data or request parameter collection
        if any(pii in stripped for pii in pii_keywords):
            # Check if this is collecting data from user input (form, request, input, etc.)
            is_collecting = any(
                term in stripped for term in ["request.", "form[", "input(", "params["]
            )
            if is_collecting:
                # Check for consent nearby (i is 1-indexed, lines is 0-indexed)
                # Exclude comments when checking for consent
                has_consent = any(
                    ("consent" in lines[j].lower() or "agree" in lines[j].lower())
                    and not lines[j].strip().startswith("#")
                    for j in range(max(0, i - 10), min(i + 5, len(lines)))
                )
                if not has_consent:
                    issues.append(
                        {
                            "line": i,
                            "type": "consent",
                            "severity": "high",
                        }
                    )
                    affected_lines.append(i)

        # Pattern 2: Storing PII without encryption
        if any(kw in stripped for kw in ["save", "store", "insert", "create"]):
            if any(pii in stripped for pii in pii_keywords):
                has_encryption = any(
                    term in stripped for term in ["encrypt", "hash", "bcrypt", "crypto"]
                )
                if not has_encryption:
                    issues.append(
                        {
                            "line": i,
                            "type": "unencrypted_pii",
                            "severity": "critical",
                        }
                    )
                    affected_lines.append(i)

        # Pattern 3: Missing data retention policy
        if "delete" in stripped or "remove" in stripped:
            # This is good, but check if there's retention logic
            pass  # Presence of deletion is positive

        # Pattern 4: No audit trail for PII access
        if (
            "select" in stripped
            or "query" in stripped
            or "find" in stripped
            or "get_user" in stripped
        ):
            if any(pii in stripped for pii in pii_keywords):
                # Check for logging in current line or nearby lines (i is 1-indexed, lines is 0-indexed)
                has_logging = any(
                    term in lines[j].lower()
                    for term in ["log", "audit", "track"]
                    for j in range(max(0, i - 5), min(i + 5, len(lines)))
                )
                if not has_logging:
                    issues.append(
                        {
                            "line": i,
                            "type": "audit",
                            "severity": "medium",
                        }
                    )
                    affected_lines.append(i)

    # Determine severity
    if any(issue["severity"] == "critical" for issue in issues):
        severity = "critical"
    elif any(issue["severity"] == "high" for issue in issues):
        severity = "high"
    elif issues:
        severity = "medium"
    else:
        severity = "none"

    recommendations = []
    if issues:
        recommendations.append(
            "Implement explicit consent collection before processing PII"
        )
        recommendations.append("Encrypt PII data at rest and in transit")
        recommendations.append("Add audit logging for all PII access")
        recommendations.append("Implement data retention and deletion policies")
        recommendations.append("Provide user data export (right to data portability)")
        recommendations.append("Add data deletion endpoints (right to be forgotten)")

    return {
        "has_compliance_issues": "true" if issues else "false",
        "issue_count": str(len(issues)),
        "issues": json.dumps(issues),
        "severity": severity,
        "affected_lines": json.dumps(affected_lines),
        "compliance_recommendations": json.dumps(recommendations),
    }


@strands_tool
def validate_accessibility(source_code: str) -> dict[str, str]:
    """Validate code for accessibility (a11y) best practices.

    Checks HTML/JSX for accessibility issues including missing alt text,
    missing ARIA labels, keyboard navigation issues, and color contrast.

    Args:
        source_code: Source code containing HTML/JSX to analyze

    Returns:
        Dictionary with:
        - has_accessibility_issues: "true" if a11y issues found
        - issue_count: Number of accessibility violations
        - issues: JSON array of accessibility issue details
        - severity: "critical", "high", "medium", or "low"
        - affected_lines: JSON array of line numbers
        - wcag_level: Highest WCAG level violated ("A", "AA", or "AAA")
        - remediation: JSON array of fix suggestions

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty

    Example:
        >>> code = '<img src="logo.png">'
        >>> result = validate_accessibility(code)
        >>> result["has_accessibility_issues"]
        'true'
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    issues = []
    affected_lines = []

    lines = source_code.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Pattern 1: Images without alt text
        if "<img" in stripped:
            if "alt=" not in stripped:
                issues.append(
                    {
                        "line": i,
                        "type": "missing_alt_text",
                        "severity": "high",
                        "wcag": "A",
                    }
                )
                affected_lines.append(i)

        # Pattern 2: Buttons without aria-label or text content
        if "<button" in stripped and ">" in stripped:
            # Check if button has text content (not just icons/images)
            has_text_content = False
            if "</button>" in stripped:
                # Extract content between <button...> and </button>
                start = stripped.find(">") + 1
                end = stripped.find("</button>")
                content = stripped[start:end]
                # Remove all HTML tags to check for text content
                import re

                text_only = re.sub(r"<[^>]+>", "", content).strip()
                # Check if there's actual text content
                has_text_content = len(text_only) > 0 and any(
                    c.isalpha() for c in text_only
                )
            has_aria = "aria-label=" in stripped
            if not has_text_content and not has_aria:
                issues.append(
                    {
                        "line": i,
                        "type": "button",
                        "severity": "high",
                        "wcag": "A",
                    }
                )
                affected_lines.append(i)

        # Pattern 3: Form inputs without labels
        if "<input" in stripped:
            # Check for associated label in nearby lines (i is 1-indexed, lines is 0-indexed)
            has_label = any(
                "<label" in lines[j]
                for j in range(max(0, i - 3), min(i + 2, len(lines)))
            )
            has_aria = "aria-label=" in stripped or "aria-labelledby=" in stripped
            if not has_label and not has_aria:
                issues.append(
                    {
                        "line": i,
                        "type": "input",
                        "severity": "high",
                        "wcag": "A",
                    }
                )
                affected_lines.append(i)

        # Pattern 4: Non-semantic HTML
        # Check for div with onClick (should be button)
        if ("onClick" in stripped or "onclick" in stripped) and "<div" in stripped:
            issues.append(
                {
                    "line": i,
                    "type": "non_semantic_interactive",
                    "severity": "medium",
                    "wcag": "AA",
                }
            )
            affected_lines.append(i)

        # Check for divs with semantic class names that should use semantic HTML
        if "<div" in stripped:
            semantic_class_names = [
                "header",
                "footer",
                "nav",
                "main",
                "article",
                "section",
                "aside",
            ]
            if any(
                f'class="{name}"' in stripped
                or f"class='{name}'" in stripped
                or f'"{name}"' in stripped
                for name in semantic_class_names
            ):
                issues.append(
                    {
                        "line": i,
                        "type": "semantic",
                        "severity": "medium",
                        "wcag": "AA",
                    }
                )
                affected_lines.append(i)

        # Pattern 5: Missing heading hierarchy
        if any(f"<h{n}" in stripped for n in range(1, 7)):
            # Could check heading order, but simplified here
            pass

        # Pattern 6: Color-only information
        if "color:" in stripped.lower() and "background" not in stripped.lower():
            # Check if there's also text/icon indicator
            # Simplified: just flag potential issue
            if "error" in stripped.lower() or "success" in stripped.lower():
                issues.append(
                    {
                        "line": i,
                        "type": "color_only_indicator",
                        "severity": "medium",
                        "wcag": "AA",
                    }
                )
                affected_lines.append(i)

    # Determine WCAG level violated
    if any(issue["wcag"] == "A" for issue in issues):
        wcag_level = "A"
        severity = "high"
    elif any(issue["wcag"] == "AA" for issue in issues):
        wcag_level = "AA"
        severity = "medium"
    else:
        wcag_level = "AAA"
        severity = "low"

    if not issues:
        severity = "none"
        wcag_level = "compliant"

    remediation = []
    if issues:
        remediation.append("Add alt attributes to all images")
        remediation.append("Ensure all interactive elements have accessible labels")
        remediation.append("Use semantic HTML (button, not div with onClick)")
        remediation.append("Provide text alternatives for color-coded information")
        remediation.append("Maintain proper heading hierarchy (h1, h2, h3...)")
        remediation.append("Test with screen readers")

    return {
        "has_accessibility_issues": "true" if issues else "false",
        "issue_count": str(len(issues)),
        "issues": json.dumps(issues),
        "severity": severity,
        "affected_lines": json.dumps(affected_lines),
        "wcag_level": wcag_level,
        "remediation": json.dumps(remediation),
    }


@strands_tool
def detect_license_violations(
    dependencies_json: str, project_license: str
) -> dict[str, str]:
    """Detect license compatibility violations in dependencies.

    Checks if dependency licenses are compatible with the project license
    to avoid legal issues.

    Args:
        dependencies_json: JSON array of dependencies with license info
        project_license: Project's license (e.g., "MIT", "Apache-2.0", "GPL-3.0")

    Returns:
        Dictionary with:
        - has_violations: "true" if license conflicts found
        - violation_count: Number of license conflicts
        - violations: JSON array of conflict details
        - severity: "critical", "high", "medium", or "low"
        - incompatible_deps: JSON array of problematic dependencies
        - legal_risk: "high", "medium", or "low"
        - remediation: JSON array of resolution options

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty or invalid JSON

    Example:
        >>> deps = '[{"name": "lib", "license": "GPL-3.0"}]'
        >>> result = detect_license_violations(deps, "MIT")
        >>> result["has_violations"]
        'true'
    """
    if not isinstance(dependencies_json, str):
        raise TypeError("dependencies_json must be a string")
    if not isinstance(project_license, str):
        raise TypeError("project_license must be a string")
    if not dependencies_json.strip():
        raise ValueError("dependencies_json cannot be empty")
    if not project_license.strip():
        raise ValueError("project_license cannot be empty")

    try:
        dependencies = json.loads(dependencies_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    violations = []
    incompatible = []

    # License compatibility rules (simplified)
    # GPL/AGPL are strong copyleft - requires derivative works to be GPL
    # LGPL is weak copyleft - compatible with permissive licenses
    # MIT/Apache/BSD are permissive - compatible with most licenses
    copyleft = ["GPL", "AGPL"]
    permissive = ["MIT", "APACHE", "BSD", "ISC"]

    project_license_upper = project_license.upper()
    # Check for LGPL separately to avoid substring matching with GPL
    project_is_lgpl = "LGPL" in project_license_upper
    project_is_copyleft = (
        any(cl in project_license_upper for cl in copyleft) and not project_is_lgpl
    )

    # Handle both dict format {name: license} and array format [{name, license}]
    if isinstance(dependencies, dict):
        dep_items = [(name, license) for name, license in dependencies.items()]
    else:
        dep_items = [
            (dep.get("name", "unknown"), dep.get("license", "")) for dep in dependencies
        ]

    for dep_name, dep_license in dep_items:
        dep_license_upper = dep_license.upper()

        # Check for incompatibilities
        # Check for LGPL separately to avoid substring matching with GPL
        dep_is_lgpl = "LGPL" in dep_license_upper
        dep_is_copyleft = (
            any(cl in dep_license_upper for cl in copyleft) and not dep_is_lgpl
        )
        dep_is_permissive = any(pl in dep_license_upper for pl in permissive)
        dep_is_proprietary = "PROPRIETARY" in dep_license_upper or (
            not dep_license
            and not dep_is_copyleft
            and not dep_is_permissive
            and not dep_is_lgpl
        )

        # Rule 1: Using GPL/AGPL dependency in non-GPL/AGPL project
        if dep_is_copyleft and not project_is_copyleft:
            violations.append(
                {
                    "dependency": dep_name,
                    "dep_license": dep_license,
                    "project_license": project_license,
                    "issue": "Copyleft dependency in non-copyleft project",
                    "severity": "critical",
                }
            )
            incompatible.append(dep_name)

        # Rule 2: Proprietary in GPL/AGPL project
        elif project_is_copyleft and dep_is_proprietary:
            violations.append(
                {
                    "dependency": dep_name,
                    "dep_license": dep_license or "Unknown/Proprietary",
                    "project_license": project_license,
                    "issue": "Proprietary dependency in copyleft project",
                    "severity": "high",
                }
            )
            incompatible.append(dep_name)

        # Rule 3: Proprietary in any project (flag as concern)
        elif dep_is_proprietary and not project_is_copyleft:
            violations.append(
                {
                    "dependency": dep_name,
                    "dep_license": dep_license or "Unknown/Proprietary",
                    "project_license": project_license,
                    "issue": "Proprietary dependency may have redistribution restrictions",
                    "severity": "medium",
                }
            )
            incompatible.append(dep_name)

    # Determine severity
    if any(v["severity"] == "critical" for v in violations):
        severity = "critical"
        legal_risk = "high"
    elif any(v["severity"] == "high" for v in violations):
        severity = "high"
        legal_risk = "medium"
    elif violations:
        severity = "medium"
        legal_risk = "low"
    else:
        severity = "none"
        legal_risk = "low"

    remediation = []
    if violations:
        remediation.append("Review all dependency licenses for compatibility")
        remediation.append("Replace incompatible dependencies with alternatives")
        remediation.append("Consider changing project license if necessary")
        remediation.append("Consult legal counsel for commercial projects")
        if any(v["severity"] == "critical" for v in violations):
            remediation.append(
                "URGENT: GPL violations can have serious legal consequences"
            )

    return {
        "has_violations": "true" if violations else "false",
        "violation_count": str(len(violations)),
        "violations": json.dumps(violations),
        "severity": severity,
        "incompatible_deps": json.dumps(incompatible),
        "legal_risk": legal_risk,
        "remediation": json.dumps(remediation),
    }
