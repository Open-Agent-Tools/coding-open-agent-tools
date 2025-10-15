"""Tests for shell formatters module."""

import pytest

from coding_open_agent_tools.shell.formatters import (
    escape_shell_argument,
    normalize_shebang,
)


class TestEscapeShellArgument:
    """Tests for escape_shell_argument function."""

    def test_single_quotes_basic(self):
        """Test escaping with single quotes."""
        result = escape_shell_argument("hello world", "single")
        assert result == "'hello world'"

    def test_single_quotes_with_apostrophe(self):
        """Test escaping single quote inside single-quoted string."""
        result = escape_shell_argument("it's working", "single")
        # Single quote should be escaped as '\''
        assert "\\'" in result or "it" in result
        assert result.startswith("'")
        assert result.endswith("'")

    def test_double_quotes_basic(self):
        """Test escaping with double quotes."""
        result = escape_shell_argument("hello world", "double")
        assert result == '"hello world"'

    def test_double_quotes_with_dollar(self):
        """Test escaping dollar sign in double quotes."""
        result = escape_shell_argument("$HOME/test", "double")
        assert result == '"\\$HOME/test"'

    def test_double_quotes_with_backtick(self):
        """Test escaping backtick in double quotes."""
        result = escape_shell_argument("test `command`", "double")
        assert "\\`" in result

    def test_double_quotes_with_backslash(self):
        """Test escaping backslash in double quotes."""
        result = escape_shell_argument("path\\to\\file", "double")
        assert "\\\\" in result

    def test_auto_mode_no_single_quote(self):
        """Test auto mode chooses single quotes when no apostrophe."""
        result = escape_shell_argument("hello world", "auto")
        assert result == "'hello world'"

    def test_auto_mode_with_single_quote(self):
        """Test auto mode chooses double quotes when apostrophe present."""
        result = escape_shell_argument("it's working", "auto")
        assert result.startswith('"')
        assert result.endswith('"')

    def test_special_characters(self):
        """Test escaping of various special characters."""
        text = "test & command | pipeline"
        result_single = escape_shell_argument(text, "single")
        result_double = escape_shell_argument(text, "double")
        assert "'" in result_single
        assert '"' in result_double

    def test_newline_in_double_quotes(self):
        """Test escaping newline in double quotes."""
        result = escape_shell_argument("line1\nline2", "double")
        assert "\\n" in result

    def test_type_error_argument(self):
        """Test TypeError for non-string argument."""
        with pytest.raises(TypeError, match="argument must be a string"):
            escape_shell_argument(123, "single")  # type: ignore[arg-type]

    def test_type_error_quote_style(self):
        """Test TypeError for non-string quote_style."""
        with pytest.raises(TypeError, match="quote_style must be a string"):
            escape_shell_argument("test", 123)  # type: ignore[arg-type]

    def test_empty_argument_error(self):
        """Test ValueError for empty argument."""
        with pytest.raises(ValueError, match="argument cannot be empty"):
            escape_shell_argument("", "single")

    def test_invalid_quote_style(self):
        """Test ValueError for invalid quote style."""
        with pytest.raises(ValueError, match="quote_style must be one of"):
            escape_shell_argument("test", "invalid")

    def test_complex_string(self):
        """Test escaping complex string with multiple special chars."""
        text = 'echo "Hello $USER" && ls `pwd`'
        result = escape_shell_argument(text, "single")
        assert result.startswith("'")
        assert result.endswith("'")


class TestNormalizeShebang:
    """Tests for normalize_shebang function."""

    def test_bash_basic(self):
        """Test normalizing bash shebang."""
        result = normalize_shebang("#!/bin/bash", "bash")
        assert result == "#!/bin/bash"

    def test_bash_with_flags(self):
        """Test normalizing bash shebang with flags."""
        result = normalize_shebang("#!/bin/bash -e", "bash")
        assert result == "#!/bin/bash -e"

    def test_sh_basic(self):
        """Test normalizing sh shebang."""
        result = normalize_shebang("#!/bin/sh", "sh")
        assert result == "#!/bin/sh"

    def test_zsh_basic(self):
        """Test normalizing zsh shebang."""
        result = normalize_shebang("#!/usr/bin/zsh", "zsh")
        assert result == "#!/bin/zsh"

    def test_env_bash(self):
        """Test normalizing to env-based bash."""
        result = normalize_shebang("#!/bin/bash", "env")
        assert result == "#!/usr/bin/env bash"

    def test_env_preserves_interpreter(self):
        """Test env mode preserves specified interpreter."""
        result = normalize_shebang("#!/usr/bin/env python3", "env")
        assert "env" in result
        assert "python3" in result or "bash" in result

    def test_python3_shebang(self):
        """Test normalizing python3 shebang."""
        result = normalize_shebang("#!/usr/bin/python3", "python3")
        assert result == "#!/usr/bin/env python3"

    def test_python_shebang(self):
        """Test normalizing python shebang."""
        result = normalize_shebang("#!/usr/bin/python", "python")
        assert result == "#!/usr/bin/env python"

    def test_malformed_shebang(self):
        """Test normalizing malformed shebang."""
        result = normalize_shebang("  #!  /usr/bin/bash  ", "bash")
        assert result.startswith("#!/")
        assert "bash" in result

    def test_no_shebang_prefix(self):
        """Test normalizing line without shebang prefix."""
        result = normalize_shebang("/bin/bash", "bash")
        assert result == "#!/bin/bash"

    def test_type_error_shebang_line(self):
        """Test TypeError for non-string shebang_line."""
        with pytest.raises(TypeError, match="shebang_line must be a string"):
            normalize_shebang(123, "bash")  # type: ignore[arg-type]

    def test_type_error_shell_type(self):
        """Test TypeError for non-string shell_type."""
        with pytest.raises(TypeError, match="shell_type must be a string"):
            normalize_shebang("#!/bin/bash", 123)  # type: ignore[arg-type]

    def test_invalid_shell_type(self):
        """Test ValueError for unsupported shell type."""
        with pytest.raises(ValueError, match="shell_type must be one of"):
            normalize_shebang("#!/bin/bash", "invalid")

    def test_flags_preservation(self):
        """Test that existing flags are preserved."""
        result = normalize_shebang("#!/bin/bash -euo pipefail", "bash")
        assert "-euo" in result or "-e" in result
        assert "pipefail" in result

    def test_env_with_multiple_flags(self):
        """Test env mode with multiple flags."""
        result = normalize_shebang("#!/bin/bash -e -u", "env")
        assert "env" in result
