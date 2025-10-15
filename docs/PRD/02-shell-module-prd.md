# Shell Validation & Security Module - Product Requirements

## Module Overview

The Shell Validation & Security Module provides AI agents with comprehensive capabilities for **validating, analyzing, and securing** shell scripts. This module focuses on deterministic operations that save agent tokens: syntax validation, security scanning, argument escaping, and script parsing.

**Philosophy**: Agents excel at writing shell scripts with examples. This module prevents errors before execution, catches security issues deterministically, and handles tedious formatting tasks.

## Goals and Objectives

### Primary Goals

1. **Prevent Execution Failures**: Validate syntax before running scripts (saves retry loops)
2. **Security First**: Detect injection risks, unquoted variables, dangerous commands
3. **Safe Formatting**: Provide deterministic argument escaping and quoting
4. **Parse Structure**: Extract functions, variables, commands from scripts

### Non-Goals

- ❌ Full script generation (agents write scripts well with prompting)
- ❌ Template systems (agents use examples effectively)
- ❌ Script execution (use subprocess from basic-open-agent-tools)
- ❌ Interactive shell session management

## User Stories

### Story 1: Syntax Validation Before Execution
**As an** AI agent generating deployment scripts
**I want to** validate shell syntax before execution
**So that** I avoid retry loops from syntax errors

### Story 2: Security Issue Detection
**As an** agent creating automation scripts
**I want to** detect security issues deterministically
**So that** generated scripts don't contain vulnerabilities

### Story 3: Safe Argument Escaping
**As an** agent building shell commands
**I want to** safely escape user input for shell use
**So that** I prevent command injection

### Story 4: Script Structure Extraction
**As an** agent analyzing existing scripts
**I want to** parse script structure (functions, variables, commands)
**So that** I understand script composition without manual parsing

### Story 5: Enhanced Secret Detection
**As an** agent scanning scripts for sensitive data
**I want to** detect hardcoded secrets using production-grade tools
**So that** I catch API keys, tokens, and credentials before deployment

## Functional Requirements

### FR1: Validation Functions

#### FR1.1: validate_shell_syntax
```python
def validate_shell_syntax(script_content: str, shell_type: str) -> dict[str, str]:
    """Validate shell script syntax without execution.

    Prevents execution failures by catching syntax errors early.
    Saves agent tokens on retry loops.

    Args:
        script_content: Script content to validate
        shell_type: Shell to validate for (bash, sh, zsh)

    Returns:
        Dict with keys: is_valid (bool as string), errors (string)

    Example:
        >>> result = validate_shell_syntax("echo 'test'", "bash")
        >>> result['is_valid']
        'true'
        >>> result = validate_shell_syntax("echo 'missing quote", "bash")
        >>> result['is_valid']
        'false'
    """
```

**Implementation**: Use `bash -n` for syntax checking (no execution)

**Token Savings**: Prevents retry loops from syntax errors. Agents waste 100+ tokens regenerating scripts with simple syntax errors.

#### FR1.2: check_shell_dependencies
```python
def check_shell_dependencies(script_content: str) -> dict[str, str]:
    """Identify external commands required by script.

    Deterministic parsing to detect missing dependencies before execution.

    Args:
        script_content: Script content to analyze

    Returns:
        Dict with keys: commands (JSON list of command names),
                       builtins (JSON list of bash builtins used)

    Example:
        >>> deps = check_shell_dependencies("git pull && npm install")
        >>> json.loads(deps['commands'])
        ['git', 'npm']
    """
```

**Detection Strategy**:
- Parse script for command invocations
- Exclude bash built-ins (echo, cd, test, etc.)
- Return external command names as JSON

### FR2: Security Analysis Functions

#### FR2.1: analyze_shell_security
```python
def analyze_shell_security(script_content: str) -> dict[str, str]:
    """Analyze script for security issues using deterministic rules.

    Catches common security anti-patterns that agents miss.

    Args:
        script_content: Script content to analyze

    Returns:
        Dict with keys: issues (JSON list of issue dicts),
                       severity_counts (JSON dict of severity: count)

        Each issue dict has keys: severity, line, issue, recommendation

    Example:
        >>> analysis = analyze_shell_security('cd $APP_DIR')
        >>> issues = json.loads(analysis['issues'])
        >>> issues[0]['severity']
        'high'
        >>> issues[0]['issue']
        'Unquoted variable expansion'
    """
```

**Security Checks** (Deterministic Rules):
- **Unquoted variables**: `$VAR` vs `"$VAR"` (high severity)
- **Dangerous commands**: `eval`, `source`, `rm -rf` without guards (critical)
- **Command injection risks**: Unsafe variable expansion in commands (critical)
- **Missing error handling**: No `set -e` or equivalent (medium)
- **Insecure temp files**: Predictable paths, missing cleanup (medium)
- **Wildcard expansion**: Unquoted `*` in dangerous contexts (high)

**Rationale**: These are rule-based checks. Agents can write secure code but often miss edge cases. Deterministic scanning catches issues reliably.

#### FR2.2: detect_unquoted_variables
```python
def detect_unquoted_variables(script_content: str) -> dict[str, str]:
    """Detect unquoted variable expansions.

    Focused detector for the most common shell security issue.

    Args:
        script_content: Script content to analyze

    Returns:
        Dict with keys: violations (JSON list of dicts),
                       safe_count (string of int),
                       unsafe_count (string of int)

        Each violation dict has keys: line, variable_name, context

    Example:
        >>> result = detect_unquoted_variables('cp $SRC $DEST')
        >>> violations = json.loads(result['violations'])
        >>> len(violations)
        2
    """
```

#### FR2.3: find_dangerous_commands
```python
def find_dangerous_commands(script_content: str) -> dict[str, str]:
    """Find potentially dangerous command patterns.

    Deterministic detection of high-risk operations.

    Args:
        script_content: Script content to analyze

    Returns:
        Dict with keys: dangerous_commands (JSON list of dicts),
                       total_count (string of int)

        Each command dict has keys: line, command, risk_level, reason

    Example:
        >>> result = find_dangerous_commands('eval "$USER_INPUT"')
        >>> cmds = json.loads(result['dangerous_commands'])
        >>> cmds[0]['risk_level']
        'critical'
    """
```

**Dangerous Patterns**:
- `eval` with variables (critical)
- `rm -rf` without guards (high)
- `chmod 777` (medium)
- `curl | bash` (critical)
- `source` with user input (high)

#### FR2.4: scan_for_secrets_enhanced
```python
def scan_for_secrets_enhanced(
    content: str,
    use_detect_secrets: str  # "true" or "false" (ADK compliance)
) -> dict[str, str]:
    """Scan content for hardcoded secrets with optional detect-secrets integration.

    Falls back to stdlib regex if detect-secrets not installed.

    Args:
        content: Content to scan for secrets
        use_detect_secrets: Whether to use detect-secrets library ("true"/"false")

    Returns:
        Dict with keys: secrets (JSON list of secret dicts),
                       method_used (string: "detect-secrets" or "stdlib"),
                       total_count (string of int)

        Each secret dict has keys: line, type, match, severity

    Example:
        >>> result = scan_for_secrets_enhanced(script, "true")
        >>> secrets = json.loads(result['secrets'])
        >>> result['method_used']
        'detect-secrets'

    Optional Dependency:
        detect-secrets>=1.5.0 (pip install coding-open-agent-tools[enhanced-security])
        Provides 1000+ patterns vs ~30 stdlib patterns
    """
```

**Implementation**:
- If `use_detect_secrets == "true"` and library available: Use detect-secrets
- Otherwise: Fall back to stdlib regex patterns
- Stdlib patterns: API keys, AWS keys, GitHub tokens, private keys, passwords

**Rationale**: Production-grade secret detection as optional enhancement. Graceful degradation if not installed.

### FR3: Formatting Functions

#### FR3.1: escape_shell_argument
```python
def escape_shell_argument(argument: str, quote_style: str) -> str:
    """Safely escape argument for shell use.

    Deterministic formatting to prevent injection. Agents waste tokens
    getting this right and often make mistakes.

    Args:
        argument: String to escape
        quote_style: Quoting style (single, double, none)

    Returns:
        Escaped string safe for shell use

    Example:
        >>> escape_shell_argument("user's file", "single")
        "'user'\\''s file'"
        >>> escape_shell_argument('echo "test"', "double")
        '"echo \\"test\\""'
    """
```

**Escaping Rules**:
- `single`: Escape single quotes as `'\''`
- `double`: Escape `$`, `` ` ``, `\`, `"`, `!`
- `none`: Escape all shell metacharacters

**Token Savings**: Agents spend 50-100 tokens on escaping logic and often get it wrong. This is purely deterministic.

#### FR3.2: normalize_shebang
```python
def normalize_shebang(script_content: str, shell_path: str) -> str:
    """Add or update shebang line to standard format.

    Deterministic formatting for script headers.

    Args:
        script_content: Script content
        shell_path: Path to shell interpreter (e.g., "/bin/bash", "/usr/bin/env bash")

    Returns:
        Script with normalized shebang line

    Example:
        >>> normalize_shebang("echo test", "/bin/bash")
        '#!/bin/bash\\necho test'
    """
```

### FR4: Parsing Functions

#### FR4.1: parse_shell_script
```python
def parse_shell_script(script_content: str) -> dict[str, str]:
    """Extract script structure and components.

    Tedious parsing task that agents waste tokens on.

    Args:
        script_content: Script content to parse

    Returns:
        Dict with keys: shebang (string),
                       functions (JSON list of function dicts),
                       variables (JSON list of variable dicts),
                       commands (JSON list of command strings),
                       set_flags (JSON list of flags),
                       error_handling (string: "true"/"false")

        Function dict keys: name, line, body
        Variable dict keys: name, value, line

    Example:
        >>> result = parse_shell_script(script)
        >>> functions = json.loads(result['functions'])
        >>> functions[0]['name']
        'deploy_app'
    """
```

**Extraction Strategy**:
- Regex-based parsing for shell constructs
- Identify function definitions
- Extract variable assignments
- Find set flags (`set -e`, `set -u`, etc.)
- Detect error handling patterns

**Token Savings**: Parsing shell scripts is tedious. Agents spend 200+ tokens on manual parsing. This is deterministic.

#### FR4.2: extract_shell_functions
```python
def extract_shell_functions(script_content: str) -> dict[str, str]:
    """Extract function definitions from shell script.

    Focused parser for function extraction.

    Args:
        script_content: Script content to parse

    Returns:
        Dict with keys: functions (JSON list of function dicts),
                       count (string of int)

        Function dict keys: name, line_start, line_end, parameters_description

    Example:
        >>> result = extract_shell_functions(script)
        >>> funcs = json.loads(result['functions'])
        >>> funcs[0]['name']
        'backup_database'
    """
```

#### FR4.3: extract_shell_variables
```python
def extract_shell_variables(script_content: str) -> dict[str, str]:
    """Extract variable assignments from shell script.

    Focused parser for variable extraction.

    Args:
        script_content: Script content to parse

    Returns:
        Dict with keys: variables (JSON list of variable dicts),
                       count (string of int)

        Variable dict keys: name, value, line, is_exported

    Example:
        >>> result = extract_shell_variables("APP_DIR=/app\\nexport NODE_ENV=production")
        >>> vars = json.loads(result['variables'])
        >>> vars[0]['name']
        'APP_DIR'
    """
```

#### FR4.4: check_error_handling
```python
def check_error_handling(script_content: str) -> dict[str, str]:
    """Analyze script's error handling mechanisms.

    Deterministic check for error handling best practices.

    Args:
        script_content: Script content to analyze

    Returns:
        Dict with keys: has_set_e (string: "true"/"false"),
                       has_set_u (string: "true"/"false"),
                       has_pipefail (string: "true"/"false"),
                       has_trap (string: "true"/"false"),
                       score (string: 0-100),
                       recommendations (JSON list of strings)

    Example:
        >>> result = check_error_handling("#!/bin/bash\\nset -euo pipefail")
        >>> result['score']
        '100'
    """
```

## Non-Functional Requirements

### NFR1: Performance
- Syntax validation: < 500ms for scripts up to 5000 lines
- Security analysis: < 1s for scripts up to 5000 lines
- Argument escaping: < 1ms for typical strings
- Script parsing: < 200ms for scripts up to 2000 lines

### NFR2: Compatibility
- Support bash 3.2+ (macOS default)
- Support bash 4.0+ (Linux default)
- Detect and report version-specific features
- Work with sh, zsh (limited support)

### NFR3: Safety
- Never execute scripts
- Read-only operations
- No file modifications without explicit user action

### NFR4: Code Quality
- 100% ruff compliance
- 100% mypy type coverage
- Minimum 80% test coverage
- All functions Google ADK compliant

## Dependencies

### Required
- Python stdlib: `re`, `subprocess`, `shlex`, `json`
- `bash` binary (for syntax validation via `bash -n`)

### Optional
- `detect-secrets>=1.5.0` - Enhanced secret scanning (pip installable Python library)
  - Install with: `pip install coding-open-agent-tools[enhanced-security]`
  - Provides 1000+ secret patterns vs ~30 stdlib patterns
  - Graceful fallback to stdlib if not installed
- `shellcheck` (external tool) - Advanced linting (future enhancement)

**Why detect-secrets**:
- ✅ Python-native library (can import, not subprocess-only)
- ✅ 10x better than stdlib (1000+ patterns vs ~30)
- ✅ pip-installable (no external binaries)
- ✅ Actively maintained (3.6k stars)
- ✅ Production-grade (used by Yelp, others)
- ✅ Graceful degradation to stdlib

**Alternatives Considered**:
- Gitleaks (Go binary, subprocess-only) ❌
- TruffleHog (Go binary, subprocess-only) ❌

## Testing Strategy

### Unit Tests
- Test each validation function with valid/invalid inputs
- Test security analysis catches known patterns
- Test escaping prevents injection
- Test parsing extracts correct structure
- Mock subprocess calls to bash

### Integration Tests
- Generate scripts and validate they work
- Test validation catches real syntax errors
- Test security analysis on real vulnerable scripts
- Test detect-secrets integration (if installed)

### Security Tests
- Test escaping with injection attempts
- Test security analysis catches OWASP patterns
- Test unquoted variable detection
- Test dangerous command detection
- Test secret detection (both stdlib and detect-secrets)

### Performance Tests
- Benchmark validation on large scripts (5000+ lines)
- Ensure sub-second performance

## Example Use Cases

### Use Case 1: Validate Before Execution
```python
import coding_open_agent_tools as coat

# Agent writes a deployment script (they're good at this)
script = """#!/bin/bash
set -euo pipefail

APP_DIR=/app
cd "$APP_DIR"
git pull origin main
npm install
npm run build
"""

# Validate syntax (prevents execution failure)
validation = coat.validate_shell_syntax(script, "bash")
if validation['is_valid'] == 'true':
    print("✓ Syntax valid")
else:
    print(f"✗ Syntax error: {validation['errors']}")
```

**Token Savings**: Catches syntax errors before execution. Saves 100+ tokens on retry loops.

### Use Case 2: Security Analysis
```python
# Agent writes script with security issues
script = """#!/bin/bash
APP_DIR=/app
cd $APP_DIR  # Unquoted variable!
eval "$USER_INPUT"  # Dangerous!
API_KEY="sk-1234567890abcdef"  # Hardcoded secret!
"""

# Security analysis (deterministic rule checking)
issues = coat.analyze_shell_security(script)
issues_list = json.loads(issues['issues'])

for issue in issues_list:
    print(f"{issue['severity']}: {issue['issue']} (line {issue['line']})")
    print(f"  → {issue['recommendation']}")

# Output:
# high: Unquoted variable expansion (line 3)
#   → Quote variable: cd "$APP_DIR"
# critical: Use of eval with user input (line 4)
#   → Avoid eval with untrusted input
# critical: Hardcoded API key (line 5)
#   → Use environment variables for secrets
```

**Token Savings**: Agents miss security issues. Deterministic scanning is reliable and fast.

### Use Case 3: Safe Argument Escaping
```python
# Agent needs to build command with user input
user_filename = "user's file (test).txt"

# Safe escaping (deterministic formatting)
safe_arg = coat.escape_shell_argument(user_filename, "single")
command = f"cat {safe_arg}"

print(command)
# Output: cat 'user'\''s file (test).txt'
```

**Token Savings**: Agents waste 50-100 tokens getting escaping right. This is instant and correct.

### Use Case 4: Parse Script Structure
```python
# Parse existing script
script = """#!/bin/bash
set -euo pipefail

deploy_app() {
    local ENV=$1
    echo "Deploying to $ENV"
}

APP_DIR=/app
NODE_ENV=production

deploy_app production
"""

result = coat.parse_shell_script(script)
functions = json.loads(result['functions'])
variables = json.loads(result['variables'])

print(f"Found {len(functions)} functions, {len(variables)} variables")
# Output: Found 1 functions, 2 variables
```

**Token Savings**: Parsing is tedious. Agents spend 200+ tokens on manual parsing.

### Use Case 5: Enhanced Secret Detection
```python
# Scan with optional detect-secrets integration
script = """#!/bin/bash
AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
GITHUB_TOKEN="ghp_1234567890abcdefghijklmnopqrstuv"
"""

# Try detect-secrets first, fall back to stdlib
result = coat.scan_for_secrets_enhanced(script, use_detect_secrets="true")
secrets = json.loads(result['secrets'])

print(f"Method: {result['method_used']}")
print(f"Found {result['total_count']} secrets")

for secret in secrets:
    print(f"  Line {secret['line']}: {secret['type']} - {secret['severity']}")

# Output with detect-secrets installed:
# Method: detect-secrets
# Found 2 secrets
#   Line 2: AWS Secret Access Key - critical
#   Line 3: GitHub Token - critical

# Output without detect-secrets:
# Method: stdlib
# Found 2 secrets
#   Line 2: AWS Key Pattern - critical
#   Line 3: Token Pattern - high
```

**Token Savings**: Comprehensive secret detection without agent reasoning. Optional enhancement provides 10x better coverage.

## Success Metrics

### Functional Metrics
- 13 functions implemented and tested
- Validation catches 95%+ of syntax errors
- Security analysis detects OWASP shell injection patterns
- Escaping prevents 100% of test injection attempts
- Parsing extracts structure correctly for 90%+ of scripts
- Enhanced secret detection with detect-secrets (optional)

### Quality Metrics
- 100% ruff compliance
- 100% mypy compliance
- 80%+ test coverage
- All functions Google ADK compliant

### Token Savings Metrics
- Validation prevents retry loops (100+ tokens saved per error)
- Security analysis replaces agent reasoning (200+ tokens saved)
- Escaping saves manual logic (50-100 tokens saved)
- Parsing saves tedious extraction (200+ tokens saved)

**Target**: 30-50% token reduction in shell-related workflows

## Open Questions

1. Should we support PowerShell validation (Windows)?
2. Do we need zsh-specific validation?
3. Should we integrate with shellcheck (external tool)?
4. How deep should security analysis go (balance thoroughness vs performance)?
5. Should we provide auto-fix suggestions (e.g., quote all variables)?

## Future Enhancements (Post-v0.2.0)

1. **ShellCheck Integration**: Optional advanced linting
2. **Auto-Fix Suggestions**: Generate corrected versions
3. **Performance Analysis**: Detect inefficient patterns
4. **Multi-Shell Support**: Enhanced zsh, fish support
5. **Custom Rule Engine**: User-defined security rules
6. **Diff Analysis**: Compare script versions for security regressions

---

**Document Version**: 2.0 - Token Efficiency Focused
**Last Updated**: 2025-10-14
**Status**: Aligned with Project Philosophy
**Owner**: Project Team

## Version History

- **2.0** (2025-10-14): Complete rewrite focused on validation/security/parsing (not generation)
- **1.0** (2025-10-14): Initial draft (generation-focused, deprecated)
