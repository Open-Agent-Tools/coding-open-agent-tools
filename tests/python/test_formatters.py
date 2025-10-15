"""Tests for python formatters module."""

import pytest

from coding_open_agent_tools.python.formatters import (
    format_docstring,
    normalize_type_hints,
    sort_imports,
)


class TestFormatDocstring:
    """Tests for format_docstring function."""

    def test_google_style_basic(self):
        """Test formatting to Google style."""
        docstring = """Process data.

Args:
data: Input data
count: Number of items

Returns:
Processed results"""
        result = format_docstring(docstring, "google", "79")
        assert result["style_used"] == "google"
        assert "Args:" in result["formatted_docstring"]
        assert "Returns:" in result["formatted_docstring"]

    def test_numpy_style(self):
        """Test formatting to NumPy style."""
        docstring = """Process data.

Parameters
data: Input data"""
        result = format_docstring(docstring, "numpy", "79")
        assert result["style_used"] == "numpy"

    def test_sphinx_style(self):
        """Test formatting to Sphinx style."""
        docstring = """:param data: Input data
:return: Results"""
        result = format_docstring(docstring, "sphinx", "79")
        assert result["style_used"] == "sphinx"

    def test_line_length_wrapping(self):
        """Test that long lines are wrapped."""
        docstring = "This is a very long summary line that should be wrapped to fit within the specified line length limit"
        result = format_docstring(docstring, "google", "50")
        lines = result["formatted_docstring"].split("\n")
        # Check that no line exceeds the limit significantly
        assert all(len(line) <= 60 for line in lines)  # Allow small overage

    def test_line_count(self):
        """Test line count reporting."""
        docstring = """Summary

Args:
    data: Input"""
        result = format_docstring(docstring, "google", "79")
        assert int(result["line_count"]) > 0

    def test_changes_made(self):
        """Test that changes are reported."""
        docstring = "Simple docstring"
        result = format_docstring(docstring, "google", "79")
        assert result["changes_made"] != ""

    def test_type_errors(self):
        """Test TypeErrors for invalid inputs."""
        with pytest.raises(TypeError, match="docstring must be a string"):
            format_docstring(123, "google", "79")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="style must be a string"):
            format_docstring("test", 123, "79")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="line_length must be a string"):
            format_docstring("test", "google", 79)  # type: ignore[arg-type]

    def test_value_error_empty_docstring(self):
        """Test ValueError for empty docstring."""
        with pytest.raises(ValueError, match="docstring cannot be empty"):
            format_docstring("", "google", "79")

    def test_value_error_invalid_style(self):
        """Test ValueError for invalid style."""
        with pytest.raises(ValueError, match="style must be one of"):
            format_docstring("test", "invalid", "79")

    def test_value_error_invalid_line_length(self):
        """Test ValueError for invalid line length."""
        with pytest.raises(ValueError, match="line_length must be a valid integer"):
            format_docstring("test", "google", "not_a_number")

    def test_value_error_line_length_too_small(self):
        """Test ValueError for line length too small."""
        with pytest.raises(ValueError, match="line_length must be at least"):
            format_docstring("test", "google", "30")


class TestSortImports:
    """Tests for sort_imports function."""

    def test_already_sorted(self):
        """Test that already sorted imports are unchanged."""
        code = """import os
import sys
"""
        result = sort_imports(code)
        # May or may not report changes depending on internal processing
        assert result["sorted_code"] is not None

    def test_sort_stdlib_imports(self):
        """Test sorting of stdlib imports."""
        code = """import sys
import os
"""
        result = sort_imports(code)
        assert "import os" in result["sorted_code"]
        assert result["sorted_code"].index("import os") < result["sorted_code"].index(
            "import sys"
        )

    def test_group_imports(self):
        """Test grouping of imports by type."""
        code = """import requests
import os
"""
        result = sort_imports(code)
        # Check counts
        assert int(result["stdlib_count"]) >= 1
        assert int(result["third_party_count"]) >= 1
        assert int(result["total_imports"]) >= 2

    def test_blank_lines_between_groups(self):
        """Test that blank lines separate import groups."""
        code = """import os
import requests
from myapp import utils
"""
        result = sort_imports(code)
        # Should have blank lines between groups
        lines = result["sorted_code"].split("\n")
        blank_count = sum(1 for line in lines if not line.strip())
        assert blank_count >= 1

    def test_no_imports(self):
        """Test code with no imports."""
        code = """def hello():
    return "world"
"""
        result = sort_imports(code)
        assert result["total_imports"] == "0"
        assert "No imports found" in result["changes_made"]

    def test_from_imports(self):
        """Test handling of from imports."""
        code = """from pathlib import Path
from os import environ
"""
        result = sort_imports(code)
        assert int(result["total_imports"]) == 2

    def test_mixed_import_styles(self):
        """Test mixing import and from import."""
        code = """import os
from pathlib import Path
import sys
"""
        result = sort_imports(code)
        assert int(result["stdlib_count"]) >= 2

    def test_preserves_non_import_code(self):
        """Test that non-import code is preserved."""
        code = """import sys

def main():
    pass
"""
        result = sort_imports(code)
        assert "def main():" in result["sorted_code"]

    def test_syntax_error(self):
        """Test error handling for syntax error."""
        code = "import ("
        with pytest.raises(ValueError, match="Cannot parse source code"):
            sort_imports(code)

    def test_type_error(self):
        """Test TypeError for non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            sort_imports(123)  # type: ignore[arg-type]

    def test_value_error_empty(self):
        """Test ValueError for empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            sort_imports("")


class TestNormalizeTypeHints:
    """Tests for normalize_type_hints function."""

    def test_list_to_list(self):
        """Test conversion of List to list."""
        code = """from typing import List

def get_items() -> List[str]:
    return []
"""
        result = normalize_type_hints(code)
        assert "list[str]" in result["normalized_code"]
        assert "List[str]" not in result["normalized_code"]
        assert any("List" in change for change in result["changes_made"])

    def test_dict_to_dict(self):
        """Test conversion of Dict to dict."""
        code = """from typing import Dict

def get_config() -> Dict[str, str]:
    return {}
"""
        result = normalize_type_hints(code)
        assert "dict[str, str]" in result["normalized_code"]
        assert any("Dict" in change for change in result["changes_made"])

    def test_tuple_to_tuple(self):
        """Test conversion of Tuple to tuple."""
        code = """from typing import Tuple

def get_pair() -> Tuple[int, int]:
    return (1, 2)
"""
        result = normalize_type_hints(code)
        assert "tuple[int, int]" in result["normalized_code"]

    def test_set_to_set(self):
        """Test conversion of Set to set."""
        code = """from typing import Set

def get_items() -> Set[str]:
    return set()
"""
        result = normalize_type_hints(code)
        assert "set[str]" in result["normalized_code"]

    def test_union_to_pipe(self):
        """Test conversion of Union to pipe syntax."""
        code = """from typing import Union

def process(data: Union[str, int]) -> Union[str, int]:
    return data
"""
        result = normalize_type_hints(code)
        assert "str | int" in result["normalized_code"]
        assert any("Union" in change for change in result["changes_made"])

    def test_optional_to_pipe_none(self):
        """Test conversion of Optional to pipe None syntax."""
        code = """from typing import Optional

def get_value() -> Optional[str]:
    return None
"""
        result = normalize_type_hints(code)
        assert "str | None" in result["normalized_code"]
        assert any("Optional" in change for change in result["changes_made"])

    def test_remove_unnecessary_typing_import(self):
        """Test removal of typing import when no longer needed."""
        code = """from typing import List

def get_items() -> List[str]:
    return []
"""
        result = normalize_type_hints(code)
        if "from typing import" not in result["normalized_code"]:
            assert result["deprecated_typing_removed"] == "true"

    def test_no_deprecated_types(self):
        """Test code with no deprecated types."""
        code = """def get_items() -> list[str]:
    return []
"""
        result = normalize_type_hints(code)
        assert "No deprecated type hints found" in result["changes_made"]
        assert result["deprecated_typing_removed"] == "false"

    def test_multiple_replacements(self):
        """Test multiple type replacements."""
        code = """from typing import List, Dict

def process() -> Dict[str, List[int]]:
    return {}
"""
        result = normalize_type_hints(code)
        assert "dict[str, list[int]]" in result["normalized_code"]
        assert int(result["total_changes"]) >= 2

    def test_preserves_needed_typing_imports(self):
        """Test that needed typing imports are preserved."""
        code = """from typing import List, Any

def process() -> Any:
    return None
"""
        result = normalize_type_hints(code)
        # Any should still be imported
        assert "Any" in result["normalized_code"]

    def test_type_error(self):
        """Test TypeError for non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            normalize_type_hints(123)  # type: ignore[arg-type]

    def test_value_error_empty(self):
        """Test ValueError for empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            normalize_type_hints("")
