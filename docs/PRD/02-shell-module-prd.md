# Shell Script Generation Module - Product Requirements

## Module Overview

The Shell Script Generation Module provides AI agents with comprehensive capabilities for creating, validating, and analyzing shell scripts. This module focuses on bash/shell script generation for deployment automation, CI/CD pipelines, system administration, and development workflows.

## Goals and Objectives

### Primary Goals

1. **Safe Script Generation**: Create syntactically correct, secure shell scripts
2. **Template Library**: Provide reusable templates for common patterns
3. **Security First**: Built-in validation to prevent common security issues
4. **Multi-Purpose**: Support various script types (deployment, CI/CD, systemd, cron)

### Non-Goals

- Interactive shell session management
- Shell script execution (use subprocess from basic-open-agent-tools)
- Real-time shell output parsing
- SSH/remote execution capabilities

## User Stories

### Story 1: Deployment Script Generation
**As an** AI agent building deployment automation
**I want to** generate deployment scripts with error handling and logging
**So that** deployments are reliable and debuggable

### Story 2: CI/CD Pipeline Scripts
**As an** agent creating CI/CD workflows
**I want to** generate pipeline scripts with proper error handling
**So that** build failures are caught and reported correctly

### Story 3: Systemd Service Creation
**As an** agent deploying services
**I want to** generate systemd service files
**So that** applications run as managed services

### Story 4: Security Validation
**As an** agent generating scripts
**I want to** validate scripts for security issues
**So that** generated scripts don't contain vulnerabilities

### Story 5: Cron Job Generation
**As an** agent scheduling tasks
**I want to** generate cron-compatible scripts
**So that** tasks run reliably on schedule

## Functional Requirements

### FR1: Script Generation Functions

#### FR1.1: generate_bash_script
```python
def generate_bash_script(
    commands: list[str],
    variables: dict[str, str],
    add_error_handling: bool,
    add_logging: bool,
    set_flags: list[str]
) -> str:
    """Generate bash script from command list.

    Args:
        commands: List of shell commands to execute
        variables: Environment variables to set
        add_error_handling: Include error handling (set -e, trap)
        add_logging: Add logging statements
        set_flags: Additional set flags (e.g., 'u' for unset vars, 'o pipefail')

    Returns:
        Complete bash script as string
    """
```

**Input Validation**:
- commands must be non-empty list of strings
- variables keys must be valid shell variable names
- set_flags must be valid bash flags

**Output Format**:
```bash
#!/bin/bash
set -euo pipefail

# Variables
APP_DIR="/app"
BRANCH="main"

# Error handling
trap 'echo "Error on line $LINENO"' ERR

# Commands
echo "[$(date)] Starting deployment..."
cd "$APP_DIR"
git pull origin "$BRANCH"
npm install
npm run build

echo "[$(date)] Deployment complete"
```

#### FR1.2: generate_shell_function
```python
def generate_shell_function(
    function_name: str,
    commands: list[str],
    parameters: list[str],
    description: str,
    return_code_handling: bool
) -> str:
    """Generate reusable shell function.

    Args:
        function_name: Name of the function
        commands: Commands in function body
        parameters: Parameter names (accessible as $1, $2, etc.)
        description: Function documentation
        return_code_handling: Add return code validation

    Returns:
        Shell function definition as string
    """
```

#### FR1.3: generate_systemd_service_script
```python
def generate_systemd_service_script(
    service_name: str,
    description: str,
    exec_start: str,
    working_directory: str,
    user: str,
    environment_vars: dict[str, str],
    restart_policy: str
) -> str:
    """Generate systemd service unit file.

    Args:
        service_name: Name of the service
        description: Service description
        exec_start: Command to start service
        working_directory: Working directory for service
        user: User to run service as
        environment_vars: Environment variables
        restart_policy: Restart policy (always, on-failure, no)

    Returns:
        Systemd service file content
    """
```

**Output Format**:
```ini
[Unit]
Description=My Application Service
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/app
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/node /app/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### FR1.4: generate_cron_job_script
```python
def generate_cron_job_script(
    job_name: str,
    command: str,
    schedule: str,
    log_output: bool,
    mailto: str
) -> str:
    """Generate cron job entry with script.

    Args:
        job_name: Descriptive name for the job
        command: Command to execute
        schedule: Cron schedule expression
        log_output: Redirect output to log file
        mailto: Email address for output (empty string for none)

    Returns:
        Cron entry and wrapper script
    """
```

#### FR1.5: generate_docker_entrypoint
```python
def generate_docker_entrypoint(
    main_command: str,
    pre_commands: list[str],
    environment_validation: list[str],
    signal_handling: bool
) -> str:
    """Generate Docker entrypoint.sh script.

    Args:
        main_command: Main application command
        pre_commands: Setup commands before main
        environment_validation: Required environment variables
        signal_handling: Add signal handling for graceful shutdown

    Returns:
        Docker entrypoint script
    """
```

#### FR1.6: generate_ci_pipeline_script
```python
def generate_ci_pipeline_script(
    pipeline_type: str,
    stages: list[dict[str, str]],
    environment_vars: dict[str, str],
    cache_config: dict[str, str]
) -> str:
    """Generate CI/CD pipeline script.

    Args:
        pipeline_type: Type of CI system (github-actions, gitlab-ci, jenkins)
        stages: List of stage dicts with name, commands
        environment_vars: Environment variables
        cache_config: Cache configuration

    Returns:
        Pipeline configuration file content
    """
```

### FR2: Validation Functions

#### FR2.1: validate_shell_syntax
```python
def validate_shell_syntax(script_content: str, shell_type: str) -> dict[str, str]:
    """Validate shell script syntax.

    Args:
        script_content: Script content to validate
        shell_type: Shell to validate for (bash, sh, zsh)

    Returns:
        Dict with keys: is_valid (bool as string), errors (string)

    Example:
        >>> result = validate_shell_syntax("echo 'test'", "bash")
        >>> result['is_valid']
        'true'
    """
```

**Implementation**: Use `bash -n` for syntax checking

#### FR2.2: check_shell_dependencies
```python
def check_shell_dependencies(script_content: str) -> list[str]:
    """Identify external commands required by script.

    Args:
        script_content: Script content to analyze

    Returns:
        List of command names found in script
    """
```

**Detection Strategy**:
- Parse script for command invocations
- Exclude bash built-ins (echo, cd, etc.)
- Return external command names

#### FR2.3: analyze_shell_security
```python
def analyze_shell_security(script_content: str) -> list[dict[str, str]]:
    """Analyze script for security issues.

    Args:
        script_content: Script content to analyze

    Returns:
        List of issue dicts with keys: severity, line, issue, recommendation
    """
```

**Security Checks**:
- Hardcoded credentials (passwords, API keys)
- Unsafe variable expansion (`$VAR` vs `"$VAR"`)
- Command injection risks
- Missing input validation
- Unsafe use of `eval`
- Insecure temp file usage
- Missing error handling (`set -e`)

#### FR2.4: parse_shell_script
```python
def parse_shell_script(script_content: str) -> dict[str, str]:
    """Extract script structure and components.

    Args:
        script_content: Script content to parse

    Returns:
        Dict with keys: shebang, functions (JSON), variables (JSON),
                       commands (JSON), set_flags
    """
```

### FR3: Utility Functions

#### FR3.1: escape_shell_argument
```python
def escape_shell_argument(argument: str, quote_style: str) -> str:
    """Safely escape argument for shell use.

    Args:
        argument: String to escape
        quote_style: Quoting style (single, double, none)

    Returns:
        Escaped string safe for shell
    """
```

**Escaping Rules**:
- Single quotes: Escape single quotes as '\''
- Double quotes: Escape $, `, \, ", !
- No quotes: Escape shell metacharacters

#### FR3.2: add_shell_shebang
```python
def add_shell_shebang(script_content: str, shell_path: str) -> str:
    """Add or update shebang line.

    Args:
        script_content: Script content
        shell_path: Path to shell interpreter

    Returns:
        Script with shebang line
    """
```

#### FR3.3: set_script_permissions
```python
def set_script_permissions(file_path: str, permissions: str) -> str:
    """Set file permissions for script.

    Args:
        file_path: Path to script file
        permissions: Octal permissions string (e.g., '755', '644')

    Returns:
        Success message

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If cannot change permissions
    """
```

#### FR3.4: generate_shell_documentation
```python
def generate_shell_documentation(
    script_name: str,
    description: str,
    usage_examples: list[str],
    parameters: list[dict[str, str]],
    exit_codes: dict[str, str]
) -> str:
    """Generate script documentation header.

    Args:
        script_name: Name of the script
        description: Script description
        usage_examples: List of usage examples
        parameters: List of parameter dicts with name, description
        exit_codes: Dict mapping codes to descriptions

    Returns:
        Documentation comment block
    """
```

**Output Format**:
```bash
#!/bin/bash
################################################################################
# Script: deploy.sh
# Description: Deploy application to production server
#
# Usage:
#   ./deploy.sh <environment> <version>
#
# Parameters:
#   environment - Target environment (staging, production)
#   version     - Version tag to deploy
#
# Exit Codes:
#   0 - Success
#   1 - Invalid parameters
#   2 - Deployment failed
#
# Examples:
#   ./deploy.sh production v1.2.3
#   ./deploy.sh staging latest
################################################################################
```

## Non-Functional Requirements

### NFR1: Performance
- Script generation: < 100ms for typical scripts (< 500 lines)
- Validation: < 500ms for scripts up to 5000 lines
- Security analysis: < 1s for scripts up to 5000 lines

### NFR2: Compatibility
- Support bash 3.2+ (macOS default)
- Support bash 4.0+ (Linux default)
- Detect and warn about version-specific features

### NFR3: Safety
- Never execute generated scripts automatically
- All file operations require explicit permission
- Security analysis on all generated scripts

### NFR4: Code Quality
- 100% ruff compliance
- 100% mypy type coverage
- Minimum 80% test coverage
- All functions Google ADK compliant

## Dependencies

### Required
- `basic-open-agent-tools` - File operations, text processing
- Python stdlib: `os`, `re`, `subprocess`, `shlex`

### Optional
- `shellcheck` (external tool) - Advanced syntax validation
- `bash` - For syntax validation

## Testing Strategy

### Unit Tests
- Test each function independently
- Mock file system operations
- Test error handling paths

### Integration Tests
- Generate scripts and validate they work
- Test script execution (in safe container)
- Test interaction with basic-open-agent-tools

### Security Tests
- Test security analysis catches known issues
- Test escaping prevents injection
- Test validation catches syntax errors

### Validation Tests
- Generate scripts and run through shellcheck
- Execute generated scripts in container
- Verify output matches expectations

## Example Use Cases

### Use Case 1: Generate Deployment Script
```python
import coding_open_agent_tools as coat

script = coat.generate_bash_script(
    commands=[
        "cd /app",
        "git pull origin main",
        "npm install --production",
        "npm run build",
        "pm2 restart app"
    ],
    variables={
        "NODE_ENV": "production",
        "APP_DIR": "/app"
    },
    add_error_handling=True,
    add_logging=True,
    set_flags=["u", "o pipefail"]
)

# Validate before using
validation = coat.validate_shell_syntax(script, "bash")
if validation['is_valid'] == 'true':
    security = coat.analyze_shell_security(script)
    if not security:
        # Save script using basic tools
        from basic_open_agent_tools import file_system
        file_system.write_file_from_string(
            file_path="/tmp/deploy.sh",
            content=script,
            skip_confirm=False
        )
```

### Use Case 2: Create Systemd Service
```python
service = coat.generate_systemd_service_script(
    service_name="myapp",
    description="My Application Service",
    exec_start="/usr/bin/node /app/server.js",
    working_directory="/app",
    user="appuser",
    environment_vars={"NODE_ENV": "production", "PORT": "3000"},
    restart_policy="always"
)
```

### Use Case 3: Generate CI Pipeline
```python
pipeline = coat.generate_ci_pipeline_script(
    pipeline_type="github-actions",
    stages=[
        {
            "name": "test",
            "commands": "npm test"
        },
        {
            "name": "build",
            "commands": "npm run build"
        },
        {
            "name": "deploy",
            "commands": "./deploy.sh production"
        }
    ],
    environment_vars={"NODE_VERSION": "18"},
    cache_config={"paths": "node_modules"}
)
```

## Success Metrics

### Functional Metrics
- 15 functions implemented
- All security checks pass
- All validation functions work correctly

### Quality Metrics
- 100% ruff compliance
- 100% mypy compliance
- 80%+ test coverage
- Zero security vulnerabilities in generated scripts

### Usage Metrics
- Agent successfully generates working scripts
- Generated scripts pass shellcheck validation
- Scripts execute without errors in test environment

## Open Questions

1. Should we support PowerShell script generation?
2. Do we need Windows batch file (.bat) support?
3. Should we integrate with external validators (shellcheck)?
4. How do we handle shell-specific features (bash vs zsh)?
5. Should we provide script optimization recommendations?

## Future Enhancements (Post-v0.1.0)

1. **Advanced Templates**: Library of common script patterns
2. **Script Optimization**: Analyze and suggest improvements
3. **Multi-Shell Support**: Generate for sh, zsh, fish
4. **Windows Support**: PowerShell and batch files
5. **Integration Testing**: Automated execution validation
6. **Performance Analysis**: Benchmark generated scripts
7. **Interactive Mode**: Q&A to build scripts

---

**Document Version**: 1.0
**Last Updated**: 2025-10-14
**Status**: Draft
**Owner**: Project Team
