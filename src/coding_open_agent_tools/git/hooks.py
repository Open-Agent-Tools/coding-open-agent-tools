"""Git hooks management and validation tools.

This module provides functions for managing, validating, and analyzing git hooks,
including syntax validation, security scanning, and execution testing.
"""

import os
import re
import stat
import subprocess
from pathlib import Path

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def list_installed_hooks(repo_path: str) -> dict[str, str]:
    """List all installed git hooks in repository.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with:
        - hooks_count: Number of installed hooks
        - hooks_list: Newline-separated list of hook names
        - executable_count: Number of executable hooks
        - non_executable_count: Number of non-executable hooks
        - sample_count: Number of .sample files

    Raises:
        TypeError: If repo_path is not a string
        ValueError: If repo_path is empty
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    hooks_dir = repo / ".git" / "hooks"
    if not hooks_dir.exists():
        return {
            "hooks_count": "0",
            "hooks_list": "",
            "executable_count": "0",
            "non_executable_count": "0",
            "sample_count": "0",
        }

    hooks = []
    executable = []
    non_executable = []
    samples = []

    for item in hooks_dir.iterdir():
        if item.is_file():
            if item.name.endswith(".sample"):
                samples.append(item.name)
            else:
                hooks.append(item.name)
                if os.access(item, os.X_OK):
                    executable.append(item.name)
                else:
                    non_executable.append(item.name)

    return {
        "hooks_count": str(len(hooks)),
        "hooks_list": "\n".join(sorted(hooks)),
        "executable_count": str(len(executable)),
        "non_executable_count": str(len(non_executable)),
        "sample_count": str(len(samples)),
    }


@strands_tool
def validate_hook_syntax(repo_path: str, hook_name: str) -> dict[str, str]:
    """Validate shell script syntax of a git hook.

    Args:
        repo_path: Path to git repository
        hook_name: Name of hook to validate (e.g., "pre-commit")

    Returns:
        Dictionary with:
        - is_valid: "true" if syntax is valid
        - shell_type: Detected shell type (bash, sh, etc.)
        - has_shebang: "true" if shebang is present
        - error_message: Syntax error message if invalid
        - line_number: Line number of error if applicable

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If hook file doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(hook_name, str):
        raise TypeError("hook_name must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not hook_name.strip():
        raise ValueError("hook_name cannot be empty")

    hook_file = Path(repo_path) / ".git" / "hooks" / hook_name
    if not hook_file.exists():
        raise FileNotFoundError(f"Hook file does not exist: {hook_file}")

    try:
        with open(hook_file, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {
            "is_valid": "false",
            "shell_type": "unknown",
            "has_shebang": "false",
            "error_message": f"Failed to read hook file: {str(e)}",
            "line_number": "0",
        }

    lines = content.split("\n")
    first_line = lines[0] if lines else ""

    # Check for shebang
    has_shebang = first_line.startswith("#!")
    shell_type = "unknown"

    if has_shebang:
        if "bash" in first_line:
            shell_type = "bash"
        elif "sh" in first_line:
            shell_type = "sh"
        elif "python" in first_line:
            shell_type = "python"
        elif "ruby" in first_line:
            shell_type = "ruby"

    # Validate syntax based on shell type
    if shell_type in ["bash", "sh"]:
        try:
            # Use bash -n for syntax checking
            result = subprocess.run(
                ["bash", "-n", str(hook_file)],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                return {
                    "is_valid": "true",
                    "shell_type": shell_type,
                    "has_shebang": "true" if has_shebang else "false",
                    "error_message": "",
                    "line_number": "0",
                }
            else:
                # Parse error message for line number
                error_msg = result.stderr
                line_match = re.search(r"line (\d+)", error_msg)
                line_number = line_match.group(1) if line_match else "0"

                return {
                    "is_valid": "false",
                    "shell_type": shell_type,
                    "has_shebang": "true" if has_shebang else "false",
                    "error_message": error_msg.strip(),
                    "line_number": line_number,
                }
        except subprocess.TimeoutExpired:
            return {
                "is_valid": "false",
                "shell_type": shell_type,
                "has_shebang": "true" if has_shebang else "false",
                "error_message": "Syntax check timed out",
                "line_number": "0",
            }
        except Exception as e:
            return {
                "is_valid": "false",
                "shell_type": shell_type,
                "has_shebang": "true" if has_shebang else "false",
                "error_message": str(e),
                "line_number": "0",
            }

    # For non-shell scripts, basic validation
    return {
        "is_valid": "true",
        "shell_type": shell_type,
        "has_shebang": "true" if has_shebang else "false",
        "error_message": "",
        "line_number": "0",
    }


@strands_tool
def validate_hook_security(repo_path: str, hook_name: str) -> dict[str, str]:
    """Scan git hook for security issues and dangerous patterns.

    Args:
        repo_path: Path to git repository
        hook_name: Name of hook to validate

    Returns:
        Dictionary with:
        - is_safe: "true" if no security issues found
        - issues_count: Number of security issues
        - dangerous_commands: Newline-separated list of dangerous commands
        - has_user_input: "true" if hook uses user input
        - recommendations: Security recommendations

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If hook file doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(hook_name, str):
        raise TypeError("hook_name must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not hook_name.strip():
        raise ValueError("hook_name cannot be empty")

    hook_file = Path(repo_path) / ".git" / "hooks" / hook_name
    if not hook_file.exists():
        raise FileNotFoundError(f"Hook file does not exist: {hook_file}")

    try:
        with open(hook_file, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {
            "is_safe": "false",
            "issues_count": "1",
            "dangerous_commands": "",
            "has_user_input": "false",
            "recommendations": f"Failed to read hook file: {str(e)}",
        }

    dangerous_patterns = {
        "eval": r"\beval\s+",
        "rm -rf": r"\brm\s+-rf\s+/",
        "curl pipe sh": r"curl\s+.*\|\s*(bash|sh)",
        "wget pipe sh": r"wget\s+.*\|\s*(bash|sh)",
        "chmod 777": r"chmod\s+777",
        "sudo": r"\bsudo\s+",
        "unquoted variables": r"\$[A-Za-z_][A-Za-z0-9_]*(?![\"'])",
    }

    issues = []
    dangerous_commands = []
    recommendations = []

    for pattern_name, pattern in dangerous_patterns.items():
        if re.search(pattern, content):
            issues.append(pattern_name)
            dangerous_commands.append(f"{pattern_name}: Potentially dangerous")

    # Check for user input usage
    has_user_input = bool(re.search(r"(read\s+|stdin|/dev/stdin|\$@|\$\*)", content))

    # Generate recommendations
    if "eval" in issues:
        recommendations.append("Avoid using 'eval' - use safer alternatives")
    if "rm -rf" in issues:
        recommendations.append(
            "Be careful with 'rm -rf' commands, especially with variables"
        )
    if any("pipe sh" in issue for issue in issues):
        recommendations.append("Avoid piping downloaded content directly to shell")
    if "unquoted variables" in issues:
        recommendations.append("Always quote variables to prevent word splitting")
    if has_user_input:
        recommendations.append("Validate and sanitize all user input")

    is_safe = len(issues) == 0

    return {
        "is_safe": "true" if is_safe else "false",
        "issues_count": str(len(issues)),
        "dangerous_commands": "\n".join(dangerous_commands)
        if dangerous_commands
        else "",
        "has_user_input": "true" if has_user_input else "false",
        "recommendations": "\n".join(recommendations)
        if recommendations
        else "No security issues found",
    }


@strands_tool
def check_hook_executable(repo_path: str, hook_name: str) -> dict[str, str]:
    """Check if git hook file has executable permissions.

    Args:
        repo_path: Path to git repository
        hook_name: Name of hook to check

    Returns:
        Dictionary with:
        - is_executable: "true" if hook is executable
        - file_exists: "true" if hook file exists
        - permissions: Octal file permissions (e.g., "755")
        - owner_can_execute: "true" if owner can execute
        - group_can_execute: "true" if group can execute
        - others_can_execute: "true" if others can execute

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If repo_path doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(hook_name, str):
        raise TypeError("hook_name must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not hook_name.strip():
        raise ValueError("hook_name cannot be empty")

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    hook_file = repo / ".git" / "hooks" / hook_name

    if not hook_file.exists():
        return {
            "is_executable": "false",
            "file_exists": "false",
            "permissions": "000",
            "owner_can_execute": "false",
            "group_can_execute": "false",
            "others_can_execute": "false",
        }

    # Get file permissions
    file_stat = hook_file.stat()
    mode = file_stat.st_mode

    # Check executable permissions
    is_executable = os.access(hook_file, os.X_OK)
    owner_can_execute = bool(mode & stat.S_IXUSR)
    group_can_execute = bool(mode & stat.S_IXGRP)
    others_can_execute = bool(mode & stat.S_IXOTH)

    # Get octal permissions
    permissions = oct(stat.S_IMODE(mode))[2:]

    return {
        "is_executable": "true" if is_executable else "false",
        "file_exists": "true",
        "permissions": permissions,
        "owner_can_execute": "true" if owner_can_execute else "false",
        "group_can_execute": "true" if group_can_execute else "false",
        "others_can_execute": "true" if others_can_execute else "false",
    }


@strands_tool
def analyze_hook_script(repo_path: str, hook_name: str) -> dict[str, str]:
    """Analyze git hook script for common issues and best practices.

    Args:
        repo_path: Path to git repository
        hook_name: Name of hook to analyze

    Returns:
        Dictionary with:
        - line_count: Number of lines in hook
        - has_error_handling: "true" if has error handling
        - has_comments: "true" if has comments
        - complexity_score: Complexity score (1-10)
        - external_commands: Newline-separated list of external commands
        - recommendations: Improvement suggestions

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If hook file doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(hook_name, str):
        raise TypeError("hook_name must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not hook_name.strip():
        raise ValueError("hook_name cannot be empty")

    hook_file = Path(repo_path) / ".git" / "hooks" / hook_name
    if not hook_file.exists():
        raise FileNotFoundError(f"Hook file does not exist: {hook_file}")

    try:
        with open(hook_file, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {
            "line_count": "0",
            "has_error_handling": "false",
            "has_comments": "false",
            "complexity_score": "0",
            "external_commands": "",
            "recommendations": f"Failed to read hook file: {str(e)}",
        }

    lines = content.split("\n")
    line_count = len(lines)

    # Check for error handling
    has_error_handling = bool(re.search(r"(set -e|trap|if \[|&&|\|\|)", content))

    # Check for comments
    comment_lines = [line for line in lines if line.strip().startswith("#")]
    has_comments = len(comment_lines) > 0

    # Calculate complexity score (simple heuristic)
    complexity = 1
    complexity += content.count("if ") + content.count("case ")
    complexity += content.count("for ") + content.count("while ")
    complexity += content.count("function ") + content.count("() {")
    complexity_score = min(10, complexity)

    # Find external commands
    external_commands = set()
    common_commands = [
        "git",
        "grep",
        "sed",
        "awk",
        "find",
        "xargs",
        "curl",
        "wget",
        "python",
        "ruby",
        "node",
    ]
    for cmd in common_commands:
        if re.search(rf"\b{cmd}\b", content):
            external_commands.add(cmd)

    # Generate recommendations
    recommendations = []
    if not has_error_handling:
        recommendations.append("Add error handling (e.g., 'set -e' or trap)")
    if not has_comments:
        recommendations.append("Add comments to explain hook behavior")
    if line_count > 100:
        recommendations.append(
            "Consider splitting large hook into separate functions or scripts"
        )
    if complexity_score > 7:
        recommendations.append("High complexity - consider simplifying logic")

    return {
        "line_count": str(line_count),
        "has_error_handling": "true" if has_error_handling else "false",
        "has_comments": "true" if has_comments else "false",
        "complexity_score": str(complexity_score),
        "external_commands": "\n".join(sorted(external_commands))
        if external_commands
        else "",
        "recommendations": "\n".join(recommendations)
        if recommendations
        else "No issues found",
    }


@strands_tool
def test_hook_execution(
    repo_path: str, hook_name: str, test_args: str
) -> dict[str, str]:
    """Test git hook execution with provided arguments (dry run).

    Args:
        repo_path: Path to git repository
        hook_name: Name of hook to test
        test_args: Arguments to pass to hook (space-separated)

    Returns:
        Dictionary with:
        - can_execute: "true" if hook can be executed
        - exit_code: Exit code from hook execution
        - stdout: Standard output from hook
        - stderr: Standard error from hook
        - execution_time: Execution time in milliseconds

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If hook file doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(hook_name, str):
        raise TypeError("hook_name must be a string")
    if not isinstance(test_args, str):
        raise TypeError("test_args must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not hook_name.strip():
        raise ValueError("hook_name cannot be empty")

    hook_file = Path(repo_path) / ".git" / "hooks" / hook_name
    if not hook_file.exists():
        raise FileNotFoundError(f"Hook file does not exist: {hook_file}")

    # Check if executable
    if not os.access(hook_file, os.X_OK):
        return {
            "can_execute": "false",
            "exit_code": "-1",
            "stdout": "",
            "stderr": "Hook file is not executable",
            "execution_time": "0",
        }

    # Prepare arguments
    args = test_args.split() if test_args.strip() else []

    try:
        import time

        start_time = time.time()

        result = subprocess.run(
            [str(hook_file)] + args,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        execution_time = int((time.time() - start_time) * 1000)

        return {
            "can_execute": "true",
            "exit_code": str(result.returncode),
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "execution_time": str(execution_time),
        }

    except subprocess.TimeoutExpired:
        return {
            "can_execute": "false",
            "exit_code": "-1",
            "stdout": "",
            "stderr": "Hook execution timed out (30s limit)",
            "execution_time": "30000",
        }
    except Exception as e:
        return {
            "can_execute": "false",
            "exit_code": "-1",
            "stdout": "",
            "stderr": str(e),
            "execution_time": "0",
        }


@strands_tool
def parse_hook_output(hook_output: str) -> dict[str, str]:
    """Parse git hook output for errors and warnings.

    Args:
        hook_output: Output from hook execution (stdout + stderr)

    Returns:
        Dictionary with:
        - has_errors: "true" if errors detected
        - has_warnings: "true" if warnings detected
        - error_count: Number of errors found
        - warning_count: Number of warnings found
        - errors: Newline-separated error messages
        - warnings: Newline-separated warning messages

    Raises:
        TypeError: If hook_output is not a string
    """
    if not isinstance(hook_output, str):
        raise TypeError("hook_output must be a string")

    if not hook_output.strip():
        return {
            "has_errors": "false",
            "has_warnings": "false",
            "error_count": "0",
            "warning_count": "0",
            "errors": "",
            "warnings": "",
        }

    lines = hook_output.split("\n")

    errors = []
    warnings = []

    # Common error/warning patterns
    error_patterns = [
        r"error:",
        r"fatal:",
        r"failed:",
        r"cannot:",
        r"invalid:",
        r"unexpected:",
    ]
    warning_patterns = [r"warning:", r"warn:", r"deprecated:", r"notice:"]

    for line in lines:
        lower_line = line.lower()

        # Check for errors
        if any(re.search(pattern, lower_line) for pattern in error_patterns):
            errors.append(line.strip())
        # Check for warnings
        elif any(re.search(pattern, lower_line) for pattern in warning_patterns):
            warnings.append(line.strip())

    return {
        "has_errors": "true" if errors else "false",
        "has_warnings": "true" if warnings else "false",
        "error_count": str(len(errors)),
        "warning_count": str(len(warnings)),
        "errors": "\n".join(errors) if errors else "",
        "warnings": "\n".join(warnings) if warnings else "",
    }


@strands_tool
def validate_hook_permissions(repo_path: str, hook_name: str) -> dict[str, str]:
    """Validate git hook file permissions for security.

    Args:
        repo_path: Path to git repository
        hook_name: Name of hook to validate

    Returns:
        Dictionary with:
        - is_secure: "true" if permissions are secure
        - permissions: Octal permissions (e.g., "755")
        - is_writable_by_group: "true" if group writable
        - is_writable_by_others: "true" if world writable
        - recommended_permissions: Recommended permissions
        - issues: Security issues found

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If hook file doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(hook_name, str):
        raise TypeError("hook_name must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not hook_name.strip():
        raise ValueError("hook_name cannot be empty")

    hook_file = Path(repo_path) / ".git" / "hooks" / hook_name
    if not hook_file.exists():
        raise FileNotFoundError(f"Hook file does not exist: {hook_file}")

    # Get file permissions
    file_stat = hook_file.stat()
    mode = file_stat.st_mode

    # Get octal permissions
    permissions = oct(stat.S_IMODE(mode))[2:]

    # Check security
    is_writable_by_group = bool(mode & stat.S_IWGRP)
    is_writable_by_others = bool(mode & stat.S_IWOTH)

    issues = []
    if is_writable_by_group:
        issues.append("Hook is writable by group - security risk")
    if is_writable_by_others:
        issues.append("Hook is writable by others - CRITICAL security risk")

    is_secure = not (is_writable_by_group or is_writable_by_others)

    # Recommended permissions: owner read/write/execute, group/others read/execute
    recommended_permissions = "755"

    return {
        "is_secure": "true" if is_secure else "false",
        "permissions": permissions,
        "is_writable_by_group": "true" if is_writable_by_group else "false",
        "is_writable_by_others": "true" if is_writable_by_others else "false",
        "recommended_permissions": recommended_permissions,
        "issues": "\n".join(issues) if issues else "No permission issues found",
    }


@strands_tool
def get_hook_dependencies(repo_path: str, hook_name: str) -> dict[str, str]:
    """Extract external dependencies from git hook script.

    Args:
        repo_path: Path to git repository
        hook_name: Name of hook to analyze

    Returns:
        Dictionary with:
        - has_dependencies: "true" if dependencies found
        - commands: Newline-separated external commands
        - scripts: Newline-separated script files referenced
        - env_vars: Newline-separated environment variables used
        - dependencies_count: Total number of dependencies

    Raises:
        TypeError: If parameters are not strings
        ValueError: If parameters are empty
        FileNotFoundError: If hook file doesn't exist
    """
    if not isinstance(repo_path, str):
        raise TypeError("repo_path must be a string")
    if not isinstance(hook_name, str):
        raise TypeError("hook_name must be a string")
    if not repo_path.strip():
        raise ValueError("repo_path cannot be empty")
    if not hook_name.strip():
        raise ValueError("hook_name cannot be empty")

    hook_file = Path(repo_path) / ".git" / "hooks" / hook_name
    if not hook_file.exists():
        raise FileNotFoundError(f"Hook file does not exist: {hook_file}")

    try:
        with open(hook_file, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return {
            "has_dependencies": "false",
            "commands": "",
            "scripts": "",
            "env_vars": "",
            "dependencies_count": "0",
        }

    # Extract external commands
    commands = set()
    common_cmds = [
        "git",
        "grep",
        "sed",
        "awk",
        "find",
        "python",
        "ruby",
        "node",
        "npm",
        "curl",
        "wget",
        "jq",
    ]
    for cmd in common_cmds:
        if re.search(rf"\b{cmd}\b", content):
            commands.add(cmd)

    # Extract script files (source/. commands)
    scripts = set()
    script_pattern = r"(?:source|\.) ([^\s;]+)"
    for match in re.finditer(script_pattern, content):
        scripts.add(match.group(1))

    # Extract environment variables
    env_vars = set()
    env_pattern = r"\$\{?([A-Z_][A-Z0-9_]*)\}?"
    for match in re.finditer(env_pattern, content):
        var = match.group(1)
        # Filter out common shell variables
        if var not in ["PATH", "HOME", "USER", "SHELL"]:
            env_vars.add(var)

    total_deps = len(commands) + len(scripts) + len(env_vars)

    return {
        "has_dependencies": "true" if total_deps > 0 else "false",
        "commands": "\n".join(sorted(commands)) if commands else "",
        "scripts": "\n".join(sorted(scripts)) if scripts else "",
        "env_vars": "\n".join(sorted(env_vars)) if env_vars else "",
        "dependencies_count": str(total_deps),
    }
