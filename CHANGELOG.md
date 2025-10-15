# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- SQLite database operations module (v0.3.5)
- Git enhancement module with 60+ functions (v0.4.0)
- Configuration validation module (v0.5.0)

## [0.2.0] - 2025-10-15

### Added
- **Shell Validation & Security Module** (13 functions):
  - Validators: `validate_shell_syntax`, `check_shell_dependencies`, `validate_shellcheck_integration`
  - Security: `analyze_shell_security`, `detect_shell_injection_risks`
  - Formatters: `escape_shell_argument`, `quote_shell_string`, `normalize_shebang`
  - Parsers: `parse_shell_script`, `extract_shell_functions`, `extract_shell_variables`
  - Analyzers: `detect_unquoted_variables`, `find_dangerous_commands`
  - Enhanced secret scanning with optional detect-secrets integration

- **Python Validation & Analysis Module** (15 functions):
  - Validators: `validate_python_syntax`, `validate_type_hints`, `validate_import_order`, `check_adk_compliance`
  - Extractors: `parse_function_signature`, `extract_docstring_info`, `extract_type_annotations`, `get_function_dependencies`
  - Formatters: `format_docstring`, `sort_imports`, `normalize_type_hints`
  - Analyzers: `detect_circular_imports`, `find_unused_imports`, `identify_anti_patterns`, `check_test_coverage_gaps`

- **Helper Functions**:
  - `load_all_shell_tools()` - Load all 13 shell functions
  - `load_all_python_tools()` - Load all 15 python functions
  - Updated `load_all_tools()` to include shell and python modules (66 total)

### Testing
- Added 271 new tests (127 shell + 144 python)
- Total: 451 tests passing in 3.78s
- Code coverage: 86% overall (exceeds 80% target)
- Shell module: 87-95% coverage per file
- Python module: 85-96% coverage per file

### Documentation
- Updated ROADMAP.md with comprehensive Git Enhancement Module (v0.4.0)
- Added 60+ git functions across 11 subcategories
- Updated TODO.md with v0.2.0 completion status
- Expanded SQLite module planning to 16 functions

### Quality
- 100% ruff compliance maintained
- 100% mypy --strict compliance maintained
- Fixed optional dependency imports (detect-secrets)

## [0.1.1] - 2025-10-14

### Added
- GitHub infrastructure (issue templates, PR templates, CODEOWNERS)
- Automation workflows (stale bot, auto-greet, auto-labeler)
- Repository topics and enhanced description
- GitHub Discussions enabled

### Documentation
- Complete community documentation set
- Enhanced README with badges and quick start

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
  - `load_all_tools()` - Load all 38 functions at once
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
