"""Tests for shell validators module."""

import pytest

from coding_open_agent_tools.shell.validators import (
    check_shell_dependencies,
    validate_shell_syntax,
)


class TestValidateShellSyntax:
    """Tests for validate_shell_syntax function."""

    def test_valid_bash_script(self):
        """Test validation of syntactically correct bash script."""
        script = """#!/bin/bash
echo "Hello World"
if [ -f /tmp/test ]; then
    echo "File exists"
fi
"""
        result = validate_shell_syntax(script, "bash")
        assert result["is_valid"] == "true"
        assert result["error_message"] == ""
        assert result["line_number"] == "0"
        assert result["shell_type"] == "bash"

    def test_invalid_bash_script(self):
        """Test validation of syntactically incorrect bash script."""
        script = """#!/bin/bash
echo "Unclosed quote
"""
        result = validate_shell_syntax(script, "bash")
        assert result["is_valid"] == "false"
        assert result["error_message"] != ""
        assert result["shell_type"] == "bash"

    def test_missing_fi(self):
        """Test script with missing fi."""
        script = """#!/bin/bash
if [ -f /tmp/test ]; then
    echo "Missing fi"
"""
        result = validate_shell_syntax(script, "bash")
        assert result["is_valid"] == "false"
        assert (
            "fi" in result["error_message"].lower()
            or "end" in result["error_message"].lower()
        )

    def test_sh_shell_type(self):
        """Test validation with sh shell type."""
        script = 'echo "test"'
        result = validate_shell_syntax(script, "sh")
        assert result["is_valid"] == "true"
        assert result["shell_type"] == "sh"

    def test_type_error_script_content(self):
        """Test TypeError for non-string script_content."""
        with pytest.raises(TypeError, match="script_content must be a string"):
            validate_shell_syntax(123, "bash")  # type: ignore[arg-type]

    def test_type_error_shell_type(self):
        """Test TypeError for non-string shell_type."""
        with pytest.raises(TypeError, match="shell_type must be a string"):
            validate_shell_syntax("echo test", 123)  # type: ignore[arg-type]

    def test_empty_script(self):
        """Test ValueError for empty script."""
        with pytest.raises(ValueError, match="script_content cannot be empty"):
            validate_shell_syntax("", "bash")

    def test_whitespace_only_script(self):
        """Test ValueError for whitespace-only script."""
        with pytest.raises(ValueError, match="script_content cannot be empty"):
            validate_shell_syntax("   \n  \t  ", "bash")

    def test_invalid_shell_type(self):
        """Test ValueError for unsupported shell type."""
        with pytest.raises(ValueError, match="shell_type must be one of"):
            validate_shell_syntax("echo test", "invalid")

    def test_complex_valid_script(self):
        """Test complex but valid script."""
        script = """#!/bin/bash
set -e
function deploy() {
    local env=$1
    echo "Deploying to $env"
}
for i in {1..5}; do
    echo "Iteration $i"
done
"""
        result = validate_shell_syntax(script, "bash")
        assert result["is_valid"] == "true"


class TestCheckShellDependencies:
    """Tests for check_shell_dependencies function."""

    def test_basic_commands(self):
        """Test detection of basic shell commands."""
        script = """#!/bin/bash
ls -la
grep "pattern" file.txt
awk '{print $1}' data.csv
"""
        result = check_shell_dependencies(script)
        assert "ls" in result["commands_used"]
        assert "grep" in result["commands_used"]
        assert "awk" in result["commands_used"]

    def test_piped_commands(self):
        """Test detection of commands in pipelines."""
        script = "cat file.txt | grep test | sort | uniq"
        result = check_shell_dependencies(script)
        assert "cat" in result["commands_used"]
        assert "grep" in result["commands_used"]
        assert "sort" in result["commands_used"]
        assert "uniq" in result["commands_used"]

    def test_command_substitution(self):
        """Test detection of commands in command substitution."""
        script = "result=$(date +%Y%m%d)"
        result = check_shell_dependencies(script)
        assert "date" in result["commands_used"]

    def test_builtin_exclusion(self):
        """Test that shell builtins are excluded."""
        script = """#!/bin/bash
echo "test"
cd /tmp
pwd
export VAR=value
"""
        result = check_shell_dependencies(script)
        # These are builtins and should be excluded
        assert "echo" not in result["commands_used"]
        assert "cd" not in result["commands_used"]
        assert "pwd" not in result["commands_used"]
        assert "export" not in result["commands_used"]

    def test_available_vs_missing(self):
        """Test categorization of available vs missing commands."""
        script = """#!/bin/bash
ls /tmp
nonexistent_command_xyz123
"""
        result = check_shell_dependencies(script)
        # ls should be available on most systems
        assert (
            "ls" in result["commands_available"] or "ls" in result["commands_missing"]
        )
        # This command definitely doesn't exist
        assert "nonexistent_command_xyz123" in result["commands_missing"]

    def test_sudo_commands(self):
        """Test detection of commands with sudo."""
        script = "sudo apt-get update"
        result = check_shell_dependencies(script)
        # Should detect apt-get, not sudo (handled separately)
        assert "apt" in result["commands_used"] or "apt-get" in result["commands_used"]

    def test_comment_exclusion(self):
        """Test that commands in comments are excluded."""
        script = """#!/bin/bash
# This is a comment with fake_command
echo "real command"  # inline_comment_command
"""
        result = check_shell_dependencies(script)
        # Comment commands should be excluded
        assert "fake_command" not in result["commands_used"]
        assert "inline_comment_command" not in result["commands_used"]

    def test_type_error(self):
        """Test TypeError for non-string input."""
        with pytest.raises(TypeError, match="script_content must be a string"):
            check_shell_dependencies(123)  # type: ignore[arg-type]

    def test_empty_script(self):
        """Test ValueError for empty script."""
        with pytest.raises(ValueError, match="script_content cannot be empty"):
            check_shell_dependencies("")

    def test_total_commands_count(self):
        """Test that total_commands is correctly calculated."""
        script = """#!/bin/bash
git status
git add .
git commit -m "test"
"""
        result = check_shell_dependencies(script)
        # Should have git and possibly other commands
        total = int(result["total_commands"])
        assert total >= 1
        assert total == len(result["commands_used"])

    def test_duplicate_commands(self):
        """Test that duplicate commands are counted once."""
        script = """#!/bin/bash
ls /tmp
ls /var
ls /home
"""
        result = check_shell_dependencies(script)
        # ls should appear once even though used 3 times
        assert result["commands_used"].count("ls") == 1
