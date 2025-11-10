# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Advanced Analysis Module (security, performance, compliance scanning)

## [0.9.1] - 2025-11-08

### Fixed
- **Windows Compatibility**: Full cross-platform support for config module
  - Line ending handling: Replace `split("\n")` with `splitlines()` to handle Unix (\n), Windows (\r\n), and Mac (\r) line endings
  - Affects: `parse_env_file`, `validate_env_file`, `extract_env_variable`, `validate_ini_syntax`, `parse_properties_file`, `check_gitignore_security`
  - Permission validation: Add platform detection in `validate_config_permissions`
  - Windows: Skip Unix permission checks, return ACL-specific guidance
  - Unix/Linux/macOS/BSD: Validate octal permissions (0600, 0644) as before

### Testing
- All 1,244 tests passing on Unix systems
- Config module functions properly handle all line ending types
- Public API verified (28 config tools, 286 total)

## [0.9.0] - 2025-11-08

### Added
- **Config Module Expansion** (19 new functions, 28 total in config module):
  - **.env File Support** (5 functions in config/env.py):
    - `parse_env_file()` - Parse .env content into dictionary with comment/quote handling
    - `validate_env_file()` - Validate .env syntax, check variable names, detect errors/warnings
    - `extract_env_variable()` - Extract specific variable value from .env content
    - `merge_env_files()` - Merge two .env files with precedence handling
    - `substitute_env_variables()` - Expand ${VAR} and $VAR references in templates

  - **Config Extraction** (6 functions in config/extraction.py):
    - `extract_yaml_value()` - Extract value from YAML using dot notation (e.g., "database.host")
    - `extract_toml_value()` - Extract value from TOML using dot notation path
    - `extract_json_value()` - Extract value from JSON using dot notation path
    - `merge_yaml_files()` - Deep merge two YAML files with nested dictionary merging
    - `merge_toml_files()` - Deep merge two TOML files with table merging
    - `interpolate_config_variables()` - Expand ${VAR} references in config content

  - **Common Config Formats** (5 functions in config/formats.py):
    - `parse_ini_file()` - Parse INI/CFG files into nested dictionary
    - `validate_ini_syntax()` - Validate INI file syntax and structure
    - `parse_properties_file()` - Parse Java .properties files with continuations/escapes
    - `validate_xml_syntax()` - Validate XML configuration file syntax
    - `parse_xml_value()` - Extract value from XML using XPath-like syntax

  - **Security & Best Practices** (3 functions in config/best_practices.py):
    - `check_gitignore_security()` - Comprehensive .gitignore security pattern scanning
    - `detect_exposed_config_files()` - Find configs in web-accessible directories
    - `validate_config_permissions()` - Check file permissions for sensitive configs

### Changed
- **Config module**: Expanded from 9 to 28 functions (+19 new tools)
- **Total tools**: 267 → 286 functions across all modules (+19)
- Updated `helpers.py` with correct config function count (28)
- Enhanced gitignore security checking (replaced `check_env_in_gitignore` with comprehensive `check_gitignore_security`)

### Testing
- Added 148 comprehensive tests for new config functions across 4 new test files
- Total tests: 1096 → 1244 passing (+148 tests)
- Config module tests: 26 → 174 tests
- All new tools maintain 80%+ coverage target
- 100% ruff compliance maintained
- 100% mypy --strict compliance maintained

### Documentation
- Updated helpers.py with config module documentation
- Updated README.md with config module expansion details
- Created comprehensive module documentation for env, extraction, formats, best_practices

## [0.5.0] - 2025-11-07

### Added
- **Python Navigation Extensions** (7 new advanced functions in python/navigation.py):
  - **Advanced Code Exploration Tools** (70-90% token reduction):
    - `get_python_function_body()` - Extract just the implementation body (80-90% savings)
    - `list_python_function_calls()` - Analyze function dependencies and call patterns (75-85% savings)
    - `find_python_function_usages()` - Impact analysis: where is a function used? (75-85% savings)
    - `get_python_method_line_numbers()` - Target specific methods in classes (85-90% savings)
    - `get_python_class_hierarchy()` - Inheritance and base class analysis (70-80% savings)
    - `find_python_definitions_by_decorator()` - Find all @tool, @property, etc. (70-80% savings)
    - `get_python_class_docstring()` - Extract class documentation only (80-85% savings)

### Changed
- **Python module**: Expanded from 25 to 32 functions (+7 navigation tools)
- **Total tools**: 164 → 171 functions across 7 modules
- Updated helpers.py with correct function counts (171 total, python: 32)
- Enhanced navigation capabilities with dependency analysis and impact tracking

### Testing
- Added 22 comprehensive tests for new navigation functions
- Total tests: 623 → 645 passing
- Navigation module maintains 80%+ coverage target
- 100% ruff compliance maintained
- 100% mypy --strict compliance maintained

### Documentation
- Updated README.md with v0.5.0 features and new tool counts
- Updated TODO.md with Phase 9 completion status
- Updated all function count references (171 total, python: 32)
- Added usage examples for advanced navigation workflows

## [0.4.4] - 2025-11-07

### Added
- **Python Navigation Module** (10 new functions in python/navigation.py):
  - **Token-Saving Tools** (85-95% reduction in typical workflows):
    - `get_python_function_line_numbers()` - Get line numbers for targeted Read operations
    - `get_python_class_line_numbers()` - Get class line numbers for targeted reading
    - `get_python_module_overview()` - High-level file summary without full parse
    - `list_python_functions()` - All function signatures with metadata
    - `list_python_classes()` - All class definitions with methods
    - `get_python_function_signature()` - Extract just the signature
    - `get_python_function_docstring()` - Extract just the docstring
    - `list_python_class_methods()` - List methods with signatures
    - `extract_python_public_api()` - Identify public interface (__all__ or public names)
    - `get_python_function_details()` - Complete function info (signature + docstring + decorators)

### Changed
- **Python module**: Expanded from 15 to 25 functions (+10 navigation tools)
- **Total tools**: 154 → 164 functions across 7 modules
- Updated helpers.py with correct function counts (164 total, python: 25)
- Enhanced python module docstring to emphasize token-saving capabilities

### Testing
- Added 53 comprehensive tests for navigation module (84% coverage)
- Total tests: 570 → 623 passing
- Navigation module exceeds 80% coverage target
- 100% ruff compliance maintained
- 100% mypy --strict compliance maintained

### Documentation
- Updated README.md with new tool counts and navigation examples
- Updated TODO.md with Phase 8 completion status
- Added usage examples demonstrating token savings
- Updated helper function documentation

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
