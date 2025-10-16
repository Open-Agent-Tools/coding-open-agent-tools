# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Configuration validation module (v0.5.0)

## [0.4.1] - 2025-10-15

### Added
- **Git Enhancement Module** (70 new functions added to git module):
  - **Commit Management** (8 functions): `validate_commit_message`, `parse_commit_message`, `analyze_commit_quality`, `check_conventional_commits`, `suggest_commit_message`, `validate_commit_signature`, `analyze_commit_size`, `check_commit_author`
  - **Git Hooks** (9 functions): `validate_hook_syntax`, `list_git_hooks`, `check_hook_executable`, `analyze_hook_security`, `test_hook_execution`, `get_hook_output`, `check_hook_dependencies`, `validate_hook_shebang`, `suggest_hook_improvements`
  - **Configuration** (6 functions): `parse_git_config`, `validate_gitignore`, `analyze_gitattributes`, `check_git_lfs_config`, `validate_git_config_section`, `suggest_config_improvements`
  - **Repository Health** (8 functions): `analyze_repository_size`, `find_large_files`, `check_branch_staleness`, `analyze_commit_frequency`, `check_repository_activity`, `detect_abandoned_branches`, `analyze_contributor_activity`, `suggest_repository_cleanup`
  - **Merge Conflicts** (6 functions): `detect_merge_conflicts`, `parse_conflict_markers`, `analyze_conflict_complexity`, `suggest_conflict_resolution`, `check_merge_in_progress`, `predict_merge_conflicts`
  - **Security Auditing** (8 functions): `scan_history_for_secrets`, `check_sensitive_files`, `validate_gpg_signatures`, `check_force_push_protection`, `analyze_file_permissions`, `check_signed_tags`, `detect_security_issues`, `audit_commit_authors`
  - **Submodules** (5 functions): `list_submodules`, `parse_gitmodules`, `validate_submodule_urls`, `check_submodule_status`, `analyze_submodule_updates`
  - **Workflow Validation** (6 functions): `validate_gitflow_workflow`, `validate_trunk_based_workflow`, `validate_branch_naming`, `check_protected_branches`, `analyze_merge_strategy`, `validate_commit_frequency`
  - **Remote Analysis** (5 functions): `list_remotes`, `parse_remote_url`, `validate_remote_url`, `check_remote_accessibility`, `analyze_push_pull_config`
  - **Tags & Versioning** (5 functions): `list_tags`, `parse_tag_version`, `validate_semantic_version`, `check_version_consistency`, `suggest_next_version`
  - **Diff Analysis** (4 functions): `analyze_diff_stats`, `calculate_code_churn`, `get_file_diff`, `find_largest_changes`

### Changed
- **BREAKING**: Deprecated `@adk_tool` decorator
  - Removed all `@adk_tool` decorator usage (159 instances)
  - Updated to use only `@strands_tool` decorator
  - Google ADK works with standard callables (no special decorator needed)
  - Updated `_decorators.py` to remove adk_tool import attempt

### Updated
- Git module: 9 → 79 functions (70 new functions added)
- Total tools: 84 → 154 functions across 7 modules
- Module breakdown: analysis (14), git (79), profiling (8), quality (7), shell (13), python (15), database (18)
- Helper functions updated with new counts
- Documentation updated (README.md, TODO.md, CLAUDE.md)

### Testing
- All 570 tests passing
- Code coverage: 50% overall
- 100% ruff compliance maintained
- 100% mypy --strict compliance maintained

### Documentation
- Updated README.md with new tool counts and git module highlights
- Updated TODO.md with Phase 7 completion status
- Updated CLAUDE.md with correct decorator requirements
- Updated helpers.py docstrings with accurate counts

## [0.3.0] - 2025-10-15

### Added
- **SQLite Database Operations Module** (16 functions):
  - Database operations: `create_sqlite_database`, `execute_query`, `execute_many`, `fetch_all`, `fetch_one`
  - Schema management: `inspect_schema`, `create_table_from_dict`, `add_column`, `create_index`
  - Safe query building: `build_select_query`, `build_insert_query`, `build_update_query`, `build_delete_query`, `escape_sql_identifier`, `validate_sql_query`
  - Migration helpers: `export_to_json`, `import_from_json`, `backup_database`
  - Pure stdlib implementation (sqlite3) with zero external dependencies
  - SQL injection prevention via parameterized queries and identifier validation
  - Comprehensive schema inspection with type information
  - JSON import/export for data migration

- **Helper Functions**:
  - `load_all_database_tools()` - Load all 16 database functions
  - Updated `load_all_tools()` to include database module (84 total functions)

### Testing
- Added 81 new comprehensive tests for database module
- Total: 532 tests passing in 7.7s
- Database module coverage: 75-89% per file (avg ~78%)
- Overall project coverage: 85% (exceeds 80% target)

### Documentation
- Updated helpers.py with database module integration
- Updated main __init__.py to export database module

### Quality
- 100% ruff compliance maintained
- 100% mypy --strict compliance maintained
- All functions follow Google ADK compliance (JSON-serializable, no defaults)

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
