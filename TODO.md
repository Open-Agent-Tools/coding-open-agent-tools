# Coding Open Agent Tools - TODO

## High Priority

### Module Migration from basic-open-agent-tools

The following modules currently exist in `basic-open-agent-tools` but are software engineering-specific and should be migrated to this project:

#### 1. **code_analysis/** (14 functions) - READY TO MIGRATE
**Source**: `basic-open-agent-tools/src/basic_open_agent_tools/code_analysis/`

Functions to migrate:
- **AST Parsing** (4 functions):
  - `parse_python_ast` - Parse Python code into AST
  - `extract_functions` - Extract function definitions
  - `extract_classes` - Extract class definitions
  - `extract_imports` - Extract import statements

- **Complexity Analysis** (4 functions):
  - `calculate_complexity` - Calculate cyclomatic complexity
  - `calculate_function_complexity` - Calculate per-function complexity
  - `get_code_metrics` - Get comprehensive code metrics
  - `identify_complex_functions` - Find overly complex functions

- **Import Management** (3 functions):
  - `find_unused_imports` - Detect unused imports
  - `organize_imports` - Sort and organize imports
  - `validate_import_order` - Check import ordering

- **Secret Detection** (3 functions):
  - `scan_for_secrets` - Scan code for hardcoded secrets
  - `scan_directory_for_secrets` - Recursive secret scanning
  - `validate_secret_patterns` - Validate secret pattern configs

**Migration Target**: `coding-open-agent-tools/src/coding_open_agent_tools/analysis/`

**Rationale**: These are Python code analysis tools that fit perfectly with code generation capabilities. Essential for validating generated code quality.

---

#### 2. **git/** (10 functions) - READY TO MIGRATE
**Source**: `basic-open-agent-tools/src/basic_open_agent_tools/git/`

Functions to migrate:
- **Status Operations** (3 functions):
  - `get_git_status` - Get working tree status
  - `get_current_branch` - Get current branch name
  - `get_git_diff` - Get diff between commits

- **History Operations** (4 functions):
  - `get_git_log` - Get commit history
  - `get_git_blame` - Get line-by-line authorship
  - `get_file_history` - Get history for specific file
  - `get_file_at_commit` - Get file contents at commit

- **Branch Operations** (2 functions):
  - `list_branches` - List all branches
  - `get_branch_info` - Get detailed branch information

- **Diff Operations** (1 function already counted above)

**Migration Target**: `coding-open-agent-tools/src/coding_open_agent_tools/git/`

**Rationale**: Git operations are developer workflow tools. Essential for code generation projects that need version control context. Read-only operations only (no commit/push for safety).

---

#### 3. **profiling/** (9 functions) - READY TO MIGRATE
**Source**: `basic-open-agent-tools/src/basic_open_agent_tools/profiling/`

Functions to migrate:
- **Performance Profiling** (3 functions):
  - `profile_function` - Profile function execution time
  - `profile_code_block` - Profile arbitrary code block
  - `get_performance_stats` - Get execution statistics

- **Memory Profiling** (3 functions):
  - `get_memory_usage` - Get current memory usage
  - `track_memory_allocations` - Track memory allocations
  - `profile_memory` - Profile memory usage over time

- **Benchmarking** (3 functions):
  - `benchmark_function` - Benchmark function performance
  - `run_benchmark_suite` - Run multiple benchmarks
  - `compare_benchmarks` - Compare benchmark results

**Migration Target**: `coding-open-agent-tools/src/coding_open_agent_tools/profiling/`

**Rationale**: Performance and memory profiling are developer tools for optimizing code. Useful for analyzing and optimizing generated code performance.

---

#### 4. **static_analysis/** (6 functions) - READY TO MIGRATE
**Source**: `basic-open-agent-tools/src/basic_open_agent_tools/static_analysis/`

Functions to migrate:
- **Code Quality** (2 functions):
  - `analyze_code_quality` - Comprehensive quality analysis
  - `detect_code_smells` - Detect common code smells

- **Type Checking** (2 functions):
  - `validate_type_hints` - Check type hint correctness
  - `check_type_coverage` - Calculate type hint coverage

- **Documentation** (2 functions):
  - `check_docstring_coverage` - Calculate docstring coverage
  - `validate_docstrings` - Check docstring format/completeness

**Migration Target**: `coding-open-agent-tools/src/coding_open_agent_tools/quality/`

**Rationale**: Static analysis for code quality directly relates to code generation validation. Ensures generated code meets quality standards.

---

### Migration Summary

**Total Functions to Migrate**: 38 functions across 4 modules

**Module Mapping**:
```
basic-open-agent-tools          →  coding-open-agent-tools
├── code_analysis/ (14)         →  analysis/
├── git/ (9)                    →  git/
├── profiling/ (8)              →  profiling/
└── static_analysis/ (7)        →  quality/
```

**Migration Benefits**:
1. Clear separation between foundational tools and coding-specific tools
2. Reduces basic-open-agent-tools scope to ~153 functions (from 200+)
3. Gives coding-open-agent-tools strong start: 38 existing + 33 planned = 71 functions
4. Better organization for users looking for code-related capabilities
5. Allows coding project to add heavier dependencies without bloating basic tools

**Migration Steps**:
1. Copy module code to coding-open-agent-tools
2. Update imports (basic_open_agent_tools → coding_open_agent_tools)
3. Update tests and move to new project
4. Add to helpers.py with load_all_*_tools() functions
5. Update documentation and README
6. Mark as deprecated in basic-open-agent-tools with migration guide
7. Remove from basic-open-agent-tools in next major version

**Dependencies to Consider**:
- code_analysis: Uses `ast` module (stdlib)
- git: Uses `subprocess` for git commands (stdlib)
- profiling: Uses `cProfile`, `memory_profiler` (stdlib + optional)
- static_analysis: Uses `ast`, `inspect` (stdlib)

All are lightweight dependencies, mostly stdlib-based.

---

## Project Initialization

### Phase 1: Repository Setup ✅ COMPLETED
- [x] Initialize git repository
- [x] Set up pyproject.toml with basic-open-agent-tools as dependency
- [x] Create package structure (src/coding_open_agent_tools/)
- [x] Configure CI/CD (GitHub Actions)
- [x] Set up pre-commit hooks
- [x] Create initial README and documentation structure
- [x] Add MIT license
- [x] Configure ruff and mypy

### Phase 2: Core Infrastructure ✅ COMPLETED
- [x] Create exceptions.py (common exception patterns)
- [x] Create types.py (shared type definitions)
- [x] Create helpers.py (tool loading functions)
- [x] Set up __init__.py with module exports
- [x] Configure logging
- [x] Set up test infrastructure

---

## Module Implementation

### Phase 3: Migrate Existing Modules (v0.1.0-beta) ✅ COMPLETED
- [x] Migrate code_analysis module (14 functions) → analysis module
- [x] Migrate git module (9 functions)
- [x] Migrate profiling module (8 functions)
- [x] Migrate static_analysis module (7 functions) → quality module
- [x] Update all imports and tests
- [x] Run quality checks (ruff, mypy, pytest)
- [x] Update documentation

**Status**: Completed 2024-10-14
- 38 functions successfully migrated
- 170 tests passing with 82% coverage
- 100% ruff and mypy compliance
- Version updated to 0.1.0-beta

### Phase 4: Shell Module (v0.1.0)
- [ ] Implement generation functions (6 functions)
- [ ] Implement validation functions (4 functions)
- [ ] Implement utility functions (4 functions)
- [ ] Create template library
- [ ] Write comprehensive tests (80%+ coverage)
- [ ] Security testing for generated scripts
- [ ] Documentation and examples

### Phase 5: Codegen Module (v0.2.0)
- [ ] Implement function generation (3 functions)
- [ ] Implement class generation (4 functions)
- [ ] Implement documentation generation (3 functions)
- [ ] Implement test generation (3 functions)
- [ ] Implement project structure generation (4 functions)
- [ ] Implement code analysis (4 functions)
- [ ] Implement CLI/config generation (2 functions)
- [ ] Create template library
- [ ] Write comprehensive tests (80%+ coverage)
- [ ] Validation testing (generated code must work)
- [ ] Documentation and examples

---

## Quality Assurance

### Testing Requirements
- [ ] Unit tests for all functions
- [ ] Integration tests for module interactions
- [ ] Validation tests (generated code actually works)
- [ ] Security tests (generated code is safe)
- [ ] Google ADK compatibility tests
- [ ] Achieve 80%+ test coverage

### Code Quality
- [ ] 100% ruff compliance (linting + formatting)
- [ ] 100% mypy compliance (type checking)
- [ ] All functions Google ADK compliant
- [ ] Comprehensive docstrings
- [ ] Security review for script generation

---

## Documentation

### Core Documentation
- [ ] API reference (all functions documented)
- [ ] Getting started guide
- [ ] Integration guide with basic-open-agent-tools
- [ ] Migration guide for existing users
- [ ] Examples and use cases
- [ ] FAQ and troubleshooting

### Module-Specific Docs
- [ ] Shell module documentation
- [ ] Codegen module documentation
- [ ] Analysis module documentation
- [ ] Git module documentation
- [ ] Profiling module documentation
- [ ] Quality module documentation

---

## Release Planning

### v0.1.0-beta (Migrated Modules)
**Target**: Early preview with migrated functionality
- Migrate 4 modules from basic-open-agent-tools (38 functions)
- Full test coverage and documentation
- PyPI beta release

### v0.1.0 (Shell Module)
**Target**: First stable release with shell generation
- Complete shell module (15 functions)
- Migrated modules stable
- Production-ready quality
- PyPI stable release

### v0.2.0 (Codegen Module)
**Target**: Full Python code generation capabilities
- Complete codegen module (18 functions)
- All core functionality implemented
- Comprehensive templates
- Community release

### v1.0.0 (Stable)
**Target**: Production stability
- All features stable and tested
- Comprehensive documentation
- Integration examples
- Community adoption

---

## Future Enhancements (Post-v1.0)

### Additional Modules
- [ ] Configuration generation (Docker, CI/CD, package managers)
- [ ] Multi-language support (JavaScript, TypeScript, Go, Rust)
- [ ] Code refactoring tools
- [ ] API client generation from OpenAPI specs
- [ ] Template marketplace/library

### Advanced Features
- [ ] Code optimization suggestions
- [ ] Automated testing strategies
- [ ] Documentation site generation (Sphinx, MkDocs)
- [ ] Performance profiling for generated code
- [ ] Integration with popular IDEs

---

## Open Questions

1. Should we support Python 2.7 code generation for legacy systems?
2. How do we handle language-specific style guides (PEP 8 vs Google vs Black)?
3. Should generated code include type stubs (.pyi files)?
4. Do we need a plugin system for custom templates?
5. Should we integrate with existing code generation tools (cookiecutter)?
6. How do we version templates independently from code?
7. Should we provide cloud/SaaS rendering for diagrams and visualizations?

---

**Document Version**: 1.0
**Last Updated**: 2025-10-14
**Status**: Planning
