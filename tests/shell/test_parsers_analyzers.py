"""Tests for shell parsers and analyzers modules."""


from coding_open_agent_tools.shell.analyzers import (
    check_error_handling,
    detect_unquoted_variables,
    find_dangerous_commands,
)
from coding_open_agent_tools.shell.parsers import (
    extract_shell_functions,
    extract_shell_variables,
    parse_shell_script,
)


class TestParseShellScript:
    """Tests for parse_shell_script function."""

    def test_basic_parsing(self):
        """Test parsing of basic shell script."""
        script = """#!/bin/bash
VAR=value
function test_func() {
    echo "test"
}
"""
        result = parse_shell_script(script)
        assert result["shebang"] == "#!/bin/bash"
        assert "VAR" in result["variables"]
        assert "test_func" in result["functions"]

    def test_error_handling_detection(self):
        """Test detection of error handling."""
        script = """#!/bin/bash
set -e
trap cleanup EXIT
"""
        result = parse_shell_script(script)
        assert result["has_error_handling"] == "true"

    def test_no_error_handling(self):
        """Test script without error handling."""
        script = "echo 'test'"
        result = parse_shell_script(script)
        assert result["has_error_handling"] == "false"

    def test_line_count(self):
        """Test line count calculation."""
        script = "line1\nline2\nline3"
        result = parse_shell_script(script)
        assert result["line_count"] == "3"

    def test_comment_count(self):
        """Test comment counting."""
        script = """#!/bin/bash
# Comment 1
echo "test"
# Comment 2
"""
        result = parse_shell_script(script)
        assert int(result["comment_count"]) >= 2


class TestExtractShellFunctions:
    """Tests for extract_shell_functions function."""

    def test_function_extraction(self):
        """Test extracting function names."""
        script = """
function deploy() {
    echo "deploying"
}

test_func() {
    return 0
}
"""
        functions = extract_shell_functions(script)
        assert len(functions) >= 2
        names = [f["name"] for f in functions]
        assert "deploy" in names
        assert "test_func" in names

    def test_function_with_parameters(self):
        """Test detecting function parameter usage."""
        script = """
process() {
    local input=$1
    echo "$input"
}
"""
        functions = extract_shell_functions(script)
        assert len(functions) > 0
        assert functions[0]["has_parameters"] == "true"

    def test_function_with_return(self):
        """Test detecting return statements."""
        script = """
validate() {
    if [ -f "$1" ]; then
        return 0
    fi
    return 1
}
"""
        functions = extract_shell_functions(script)
        assert len(functions) > 0
        assert functions[0]["has_return"] == "true"


class TestExtractShellVariables:
    """Tests for extract_shell_variables function."""

    def test_basic_variable(self):
        """Test extracting basic variable."""
        script = "API_KEY=secret123"
        variables = extract_shell_variables(script)
        assert len(variables) > 0
        assert variables[0]["name"] == "API_KEY"

    def test_exported_variable(self):
        """Test detecting exported variables."""
        script = "export PATH=/usr/local/bin"
        variables = extract_shell_variables(script)
        assert len(variables) > 0
        assert variables[0]["is_exported"] == "true"

    def test_readonly_variable(self):
        """Test detecting readonly variables."""
        script = "readonly VERSION=1.0"
        variables = extract_shell_variables(script)
        assert len(variables) > 0
        assert variables[0]["is_readonly"] == "true"

    def test_line_numbers(self):
        """Test that line numbers are provided."""
        script = """line1
VAR1=value1
line3
VAR2=value2
"""
        variables = extract_shell_variables(script)
        assert len(variables) >= 2
        assert all("line_number" in var for var in variables)


class TestDetectUnquotedVariables:
    """Tests for detect_unquoted_variables function."""

    def test_unquoted_detection(self):
        """Test detection of unquoted variables."""
        script = "echo $VAR"
        issues = detect_unquoted_variables(script)
        assert len(issues) > 0
        assert issues[0]["variable_name"] == "VAR"

    def test_quoted_variable_ok(self):
        """Test that quoted variables don't trigger warnings."""
        script = 'echo "$VAR"'
        issues = detect_unquoted_variables(script)
        # Quoted variables should not be flagged
        assert len(issues) == 0

    def test_double_bracket_context(self):
        """Test that [[ ]] context is handled."""
        script = "if [[ $VAR == test ]]; then"
        issues = detect_unquoted_variables(script)
        # Variables in [[ ]] are safe
        assert len(issues) == 0

    def test_recommendations(self):
        """Test that recommendations are provided."""
        script = "rm $FILE"
        issues = detect_unquoted_variables(script)
        if len(issues) > 0:
            assert all("recommendation" in issue for issue in issues)


class TestFindDangerousCommands:
    """Tests for find_dangerous_commands function."""

    def test_rm_rf_root(self):
        """Test detection of rm -rf /."""
        script = "rm -rf /"
        findings = find_dangerous_commands(script)
        assert len(findings) > 0
        assert any(f["risk_level"] == "high" for f in findings)

    def test_dd_to_device(self):
        """Test detection of dd to device."""
        script = "dd if=/dev/zero of=/dev/sda"
        findings = find_dangerous_commands(script)
        assert len(findings) > 0

    def test_mkfs_detection(self):
        """Test detection of mkfs."""
        script = "mkfs.ext4 /dev/sda1"
        findings = find_dangerous_commands(script)
        assert len(findings) > 0

    def test_chmod_777(self):
        """Test detection of chmod 777."""
        script = "chmod 777 /tmp/file"
        findings = find_dangerous_commands(script)
        assert len(findings) > 0

    def test_curl_pipe_sh(self):
        """Test detection of curl | sh."""
        script = "curl https://example.com/script.sh | sh"
        findings = find_dangerous_commands(script)
        assert len(findings) > 0
        assert any(f["risk_level"] == "high" for f in findings)

    def test_mitigation_provided(self):
        """Test that mitigation is provided."""
        script = "rm -rf /"
        findings = find_dangerous_commands(script)
        assert len(findings) > 0
        assert all("mitigation" in f for f in findings)


class TestCheckErrorHandling:
    """Tests for check_error_handling function."""

    def test_set_e_detection(self):
        """Test detection of set -e."""
        script = "set -e"
        result = check_error_handling(script)
        assert result["has_set_e"] == "true"

    def test_set_u_detection(self):
        """Test detection of set -u."""
        script = "set -u"
        result = check_error_handling(script)
        assert result["has_set_u"] == "true"

    def test_set_o_pipefail_detection(self):
        """Test detection of set -o pipefail."""
        script = "set -o pipefail"
        result = check_error_handling(script)
        assert result["has_set_o_pipefail"] == "true"

    def test_trap_detection(self):
        """Test detection of trap."""
        script = "trap cleanup EXIT"
        result = check_error_handling(script)
        assert result["has_trap"] == "true"

    def test_error_checks_detection(self):
        """Test detection of error checks."""
        script = """
if [ $? -ne 0 ]; then
    echo "Error"
fi
"""
        result = check_error_handling(script)
        assert result["has_error_checks"] == "true"

    def test_scoring(self):
        """Test error handling scoring."""
        script = """#!/bin/bash
set -euo pipefail
trap cleanup EXIT
if [ $? -ne 0 ]; then exit 1; fi
"""
        result = check_error_handling(script)
        score = int(result["error_handling_score"])
        assert score >= 4  # Should have high score

    def test_recommendations(self):
        """Test recommendations for missing error handling."""
        script = "echo 'no error handling'"
        result = check_error_handling(script)
        assert "recommendation" in result
        assert result["recommendation"] != ""

    def test_good_error_handling(self):
        """Test script with good error handling."""
        script = """#!/bin/bash
set -euo pipefail
trap cleanup EXIT
"""
        result = check_error_handling(script)
        # Should have good score (3 = set flags + trap)
        score = int(result["error_handling_score"])
        assert score >= 3
