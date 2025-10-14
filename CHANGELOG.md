# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Shell script generation module
- Python code generation module

## [0.1.0-beta] - 2024-10-14

### Added
- **Analysis Module** (14 functions migrated from basic-open-agent-tools):
  - AST parsing: `parse_python_ast`, `extract_functions`, `extract_classes`, `extract_imports`
  - Complexity analysis: `calculate_complexity`, `calculate_function_complexity`, `get_code_metrics`, `identify_complex_functions`
  - Import management: `find_unused_imports`, `organize_imports`, `validate_import_order`
  - Secret detection: `scan_for_secrets`, `scan_directory_for_secrets`, `validate_secret_patterns`

- **Git Module** (9 functions migrated from basic-open-agent-tools):
  - Status operations: `get_git_status`, `get_current_branch`, `get_git_diff`
  - History operations: `get_git_log`, `get_git_blame`, `get_file_history`, `get_file_at_commit`
  - Branch operations: `list_branches`, `get_branch_info`

- **Profiling Module** (8 functions migrated from basic-open-agent-tools):
  - Performance profiling: `profile_function`, `profile_script`, `get_hotspots`
  - Memory analysis: `measure_memory_usage`, `detect_memory_leaks`, `get_memory_snapshot`
  - Benchmarking: `benchmark_execution`, `compare_implementations`

- **Quality Module** (7 functions migrated from basic-open-agent-tools/static_analysis):
  - Output parsers: `parse_ruff_json`, `parse_mypy_json`, `parse_pytest_json`, `summarize_static_analysis`
  - Issue analysis: `filter_issues_by_severity`, `group_issues_by_file`, `prioritize_issues`

- **Helper Functions**:
  - `load_all_analysis_tools()` - Load all 14 analysis functions
  - `load_all_git_tools()` - Load all 9 git functions
  - `load_all_profiling_tools()` - Load all 8 profiling functions
  - `load_all_quality_tools()` - Load all 7 quality functions
  - `load_all_tools()` - Load all 39 functions at once
  - `merge_tool_lists()` - Merge and deduplicate tool lists

### Testing
- Migrated 170 test cases with 83% code coverage
- All tests passing with ruff and mypy compliance

### Notes
- This is a beta release with migrated developer-focused tools
- Module names changed: `code_analysis` → `analysis`, `static_analysis` → `quality`
- Exception aliases added for backwards compatibility

## [0.0.1] - 2024-10-14

### Added
- Initial project structure and repository setup
- PyPI package configuration in pyproject.toml
- Development tooling configuration (ruff, mypy, pytest)
- Pre-commit hooks for code quality
- Documentation structure (README, CONTRIBUTING, CODE_OF_CONDUCT)
- Security policy documentation
- MIT License
- Dependency on basic-open-agent-tools >= 0.12.0

### Documentation
- Project README with architecture overview
- Contributing guidelines for open source contributions
- TODO.md with planned module migrations and implementation roadmap
- PRD documents for planned modules

### Infrastructure
- GitHub workflows setup for CI/CD
- Issue and PR templates
- EditorConfig for consistent coding styles
- Test infrastructure with pytest

---

**Note**: This project is in the planning phase. The first functional release (v0.1.0) will include the shell script generation module and migrated code analysis tools.
