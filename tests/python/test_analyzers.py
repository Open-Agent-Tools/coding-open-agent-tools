"""Tests for python analyzers module."""

import tempfile
from pathlib import Path

import pytest

from coding_open_agent_tools.python.analyzers import (
    check_test_coverage_gaps,
    detect_circular_imports,
    find_unused_imports,
    identify_anti_patterns,
)


class TestDetectCircularImports:
    """Tests for detect_circular_imports function."""

    def test_no_circular_imports(self, tmp_path: Path):
        """Test project with no circular imports."""
        # Create test files
        (tmp_path / "module_a.py").write_text("import os\n")
        (tmp_path / "module_b.py").write_text("import module_a\n")

        result = detect_circular_imports(str(tmp_path))
        assert result["has_circular_imports"] == "false"
        assert len(result["circular_chains"]) == 0

    def test_circular_import_detected(self, tmp_path: Path):
        """Test detection of circular import."""
        (tmp_path / "module_a.py").write_text("import module_b\n")
        (tmp_path / "module_b.py").write_text("import module_a\n")

        result = detect_circular_imports(str(tmp_path))
        assert result["has_circular_imports"] == "true"
        assert len(result["circular_chains"]) > 0

    def test_modules_analyzed_count(self, tmp_path: Path):
        """Test that modules analyzed count is correct."""
        (tmp_path / "module_a.py").write_text("pass\n")
        (tmp_path / "module_b.py").write_text("pass\n")
        (tmp_path / "module_c.py").write_text("pass\n")

        result = detect_circular_imports(str(tmp_path))
        assert int(result["total_modules_analyzed"]) == 3

    def test_skips_pycache(self, tmp_path: Path):
        """Test that __pycache__ directories are skipped."""
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "test.py").write_text("pass\n")
        (tmp_path / "module.py").write_text("pass\n")

        result = detect_circular_imports(str(tmp_path))
        assert int(result["total_modules_analyzed"]) == 1

    def test_type_error(self):
        """Test TypeError for non-string input."""
        with pytest.raises(TypeError, match="project_root must be a string"):
            detect_circular_imports(123)  # type: ignore[arg-type]

    def test_value_error_empty(self):
        """Test ValueError for empty input."""
        with pytest.raises(ValueError, match="project_root cannot be empty"):
            detect_circular_imports("")

    def test_value_error_not_exists(self):
        """Test ValueError for non-existent path."""
        with pytest.raises(ValueError, match="project_root does not exist"):
            detect_circular_imports("/nonexistent/path")

    def test_value_error_not_directory(self, tmp_path: Path):
        """Test ValueError for non-directory path."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("test")

        with pytest.raises(ValueError, match="project_root is not a directory"):
            detect_circular_imports(str(file_path))


class TestFindUnusedImports:
    """Tests for find_unused_imports function."""

    def test_no_unused_imports(self):
        """Test code with all imports used."""
        code = """import os

path = os.path.join("a", "b")
"""
        result = find_unused_imports(code)
        assert result["has_unused_imports"] == "false"
        assert len(result["unused_imports"]) == 0

    def test_unused_import_detected(self):
        """Test detection of unused import."""
        code = """import os
import sys

path = os.path.join("a", "b")
"""
        result = find_unused_imports(code)
        assert result["has_unused_imports"] == "true"
        assert any(imp["import_name"] == "sys" for imp in result["unused_imports"])

    def test_from_import_unused(self):
        """Test detection of unused from import."""
        code = """from pathlib import Path
from os import environ

p = Path(".")
"""
        result = find_unused_imports(code)
        assert any(imp["import_name"] == "environ" for imp in result["unused_imports"])

    def test_aliased_import_used(self):
        """Test that aliased imports are correctly tracked."""
        code = """import numpy as np

arr = np.array([1, 2, 3])
"""
        result = find_unused_imports(code)
        # np is used, so should not be flagged as unused
        assert result["has_unused_imports"] == "false"

    def test_total_counts(self):
        """Test total import and unused counts."""
        code = """import os
import sys
import json

path = os.path.join("a", "b")
"""
        result = find_unused_imports(code)
        assert int(result["total_imports"]) == 3
        assert int(result["total_unused"]) == 2  # sys and json unused

    def test_no_imports(self):
        """Test code with no imports."""
        code = """def hello():
    return "world"
"""
        result = find_unused_imports(code)
        assert result["total_imports"] == "0"
        assert result["has_unused_imports"] == "false"

    def test_recommendation_provided(self):
        """Test that recommendations are provided."""
        code = """import unused_module

print("test")
"""
        result = find_unused_imports(code)
        if result["has_unused_imports"] == "true":
            assert all("recommendation" in imp for imp in result["unused_imports"])

    def test_syntax_error(self):
        """Test error handling for syntax error."""
        code = "import ("
        with pytest.raises(ValueError, match="Cannot parse source code"):
            find_unused_imports(code)

    def test_type_error(self):
        """Test TypeError for non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            find_unused_imports(123)  # type: ignore[arg-type]

    def test_value_error_empty(self):
        """Test ValueError for empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            find_unused_imports("")


class TestIdentifyAntiPatterns:
    """Tests for identify_anti_patterns function."""

    def test_eval_usage(self):
        """Test detection of eval() usage."""
        code = """result = eval(user_input)"""
        result = identify_anti_patterns(code)
        assert result["has_anti_patterns"] == "true"
        assert any(issue["issue_type"] == "dangerous_eval" for issue in result["issues_found"])
        assert any(issue["severity"] == "critical" for issue in result["issues_found"])

    def test_exec_usage(self):
        """Test detection of exec() usage."""
        code = """exec(malicious_code)"""
        result = identify_anti_patterns(code)
        assert any(issue["issue_type"] == "dangerous_exec" for issue in result["issues_found"])

    def test_compile_usage(self):
        """Test detection of compile() usage."""
        code = """compiled = compile(source, "file", "exec")"""
        result = identify_anti_patterns(code)
        assert any(issue["issue_type"] == "dangerous_compile" for issue in result["issues_found"])

    def test_pickle_usage(self):
        """Test detection of unsafe pickle usage."""
        code = """import pickle

data = pickle.loads(untrusted_data)
"""
        result = identify_anti_patterns(code)
        assert any(issue["issue_type"] == "unsafe_pickle" for issue in result["issues_found"])

    def test_bare_except(self):
        """Test detection of bare except clause."""
        code = """try:
    risky_operation()
except:
    pass
"""
        result = identify_anti_patterns(code)
        assert any(issue["issue_type"] == "bare_except" for issue in result["issues_found"])

    def test_mutable_default_argument(self):
        """Test detection of mutable default arguments."""
        code = """def append_to(element, target=[]):
    target.append(element)
    return target
"""
        result = identify_anti_patterns(code)
        assert any(issue["issue_type"] == "mutable_default" for issue in result["issues_found"])

    def test_long_function(self):
        """Test detection of long functions."""
        # Create a function with >50 lines
        lines = ["def long_function():"] + ["    pass"] * 52
        code = "\n".join(lines)

        result = identify_anti_patterns(code)
        assert any(issue["issue_type"] == "long_function" for issue in result["issues_found"])

    def test_string_concat_in_loop(self):
        """Test detection of string concatenation in loop."""
        code = """result = ""
for item in items:
    result += str(item)
"""
        result = identify_anti_patterns(code)
        assert any(issue["issue_type"] == "string_concat_in_loop" for issue in result["issues_found"])

    def test_clean_code(self):
        """Test that clean code has no anti-patterns."""
        code = """def process(data: list[str]) -> str:
    return "".join(data)
"""
        result = identify_anti_patterns(code)
        assert result["has_anti_patterns"] == "false"

    def test_severity_counts(self):
        """Test that severity counts are provided."""
        code = """result = eval(user_input)

try:
    pass
except:
    pass
"""
        result = identify_anti_patterns(code)
        assert "critical_count" in result
        assert "high_count" in result
        assert int(result["critical_count"]) >= 1

    def test_recommendations_provided(self):
        """Test that recommendations are provided."""
        code = """result = eval(user_input)"""
        result = identify_anti_patterns(code)
        assert all("recommendation" in issue for issue in result["issues_found"])

    def test_syntax_error(self):
        """Test error handling for syntax error."""
        code = "def broken("
        with pytest.raises(ValueError, match="Cannot parse source code"):
            identify_anti_patterns(code)

    def test_type_error(self):
        """Test TypeError for non-string input."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            identify_anti_patterns(123)  # type: ignore[arg-type]

    def test_value_error_empty(self):
        """Test ValueError for empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            identify_anti_patterns("")


class TestCheckTestCoverageGaps:
    """Tests for check_test_coverage_gaps function."""

    def test_full_coverage(self):
        """Test source with full test coverage."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as source_file:
            source_file.write("""
def process(data: str) -> str:
    return data.upper()
""")
            source_path = source_file.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as test_file:
            test_file.write("""
from source import process

def test_process():
    result = process("hello")
    assert result == "HELLO"
""")
            test_path = test_file.name

        try:
            result = check_test_coverage_gaps(source_path, test_path)
            assert len(result["untested_functions"]) == 0
        finally:
            Path(source_path).unlink(missing_ok=True)
            Path(test_path).unlink(missing_ok=True)

    def test_coverage_gaps(self):
        """Test detection of coverage gaps."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as source_file:
            source_file.write("""
def tested_function():
    pass

def untested_function():
    pass
""")
            source_path = source_file.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as test_file:
            test_file.write("""
def test_tested_function():
    tested_function()
""")
            test_path = test_file.name

        try:
            result = check_test_coverage_gaps(source_path, test_path)
            assert result["has_coverage_gaps"] == "true"
            assert "untested_function" in result["untested_functions"]
        finally:
            Path(source_path).unlink(missing_ok=True)
            Path(test_path).unlink(missing_ok=True)

    def test_coverage_ratio(self):
        """Test coverage ratio calculation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as source_file:
            source_file.write("""
def func1():
    pass

def func2():
    pass
""")
            source_path = source_file.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as test_file:
            test_file.write("""
def test_func1():
    func1()
""")
            test_path = test_file.name

        try:
            result = check_test_coverage_gaps(source_path, test_path)
            coverage = float(result["coverage_ratio"])
            assert 0 <= coverage <= 100
        finally:
            Path(source_path).unlink(missing_ok=True)
            Path(test_path).unlink(missing_ok=True)

    def test_recommendation_provided(self):
        """Test that recommendations are provided."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as source_file:
            source_file.write("def func(): pass\n")
            source_path = source_file.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as test_file:
            test_file.write("# no tests\n")
            test_path = test_file.name

        try:
            result = check_test_coverage_gaps(source_path, test_path)
            assert result["recommendation"] != ""
        finally:
            Path(source_path).unlink(missing_ok=True)
            Path(test_path).unlink(missing_ok=True)

    def test_type_errors(self):
        """Test TypeErrors for invalid inputs."""
        with pytest.raises(TypeError, match="source_file must be a string"):
            check_test_coverage_gaps(123, "test.py")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="test_file must be a string"):
            check_test_coverage_gaps("source.py", 123)  # type: ignore[arg-type]

    def test_value_errors(self):
        """Test ValueErrors for empty inputs."""
        with pytest.raises(ValueError, match="source_file cannot be empty"):
            check_test_coverage_gaps("", "test.py")

        with pytest.raises(ValueError, match="test_file cannot be empty"):
            check_test_coverage_gaps("source.py", "")

    def test_source_file_not_exists(self):
        """Test error when source file doesn't exist."""
        with pytest.raises(ValueError, match="source_file does not exist"):
            check_test_coverage_gaps("/nonexistent/source.py", "/nonexistent/test.py")

    def test_test_file_not_exists(self):
        """Test error when test file doesn't exist."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as source_file:
            source_file.write("pass\n")
            source_path = source_file.name

        try:
            with pytest.raises(ValueError, match="test_file does not exist"):
                check_test_coverage_gaps(source_path, "/nonexistent/test.py")
        finally:
            Path(source_path).unlink(missing_ok=True)
