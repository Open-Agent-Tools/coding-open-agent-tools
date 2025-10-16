# Coding Open Agent Tools - Project Overview

## Project Vision

**Coding Open Agent Tools** is a specialized toolkit for AI agents focused on **deterministic code operations** that would waste tokens or cause excessive retry loops. This project complements the foundational `basic-open-agent-tools` by providing parsing, validation, and analysis tools that agents struggle with or are inefficient at performing.

## Relationship to Basic Open Agent Tools

### Division of Responsibilities

**basic-open-agent-tools** (Foundation Layer):
- Core file system operations
- Text/data processing
- Document format handling (PDF, Word, Excel, etc.)
- System utilities
- Low-level, general-purpose operations

**coding-open-agent-tools** (Development Layer):
- **Parsers**: Convert unstructured → structured (AST, tool output, logs)
- **Validators**: Syntax checking, security analysis, compliance checks
- **Extractors**: Pull specific data from complex sources
- **Formatters**: Apply deterministic rules (escaping, quoting, style)
- **Scanners**: Rule-based pattern detection (secrets, anti-patterns)

### Dependency Model

```
coding-open-agent-tools
    └─> basic-open-agent-tools (dependency)
         └─> stdlib (minimal external deps)
```

This project will:
- Depend on `basic-open-agent-tools` for foundational operations
- Build higher-level abstractions for development tasks
- Maintain the same quality standards and philosophy

## Core Philosophy

### Same Principles as Basic Tools

1. **Minimal Dependencies**: Prefer stdlib, add dependencies only when substantial value added
2. **Google ADK Compliance**: All functions use JSON-serializable types, no default parameters
3. **Local Operations**: No HTTP/API calls, focus on local development tasks
4. **Type Safety**: Full mypy compliance with comprehensive type hints
5. **High Quality**: 100% ruff compliance, comprehensive testing
6. **Agent-First Design**: Functions designed for LLM comprehension and use

### Token Efficiency Principles

1. **Deterministic Operations**: Focus on tasks with clear, rule-based logic
2. **Parse, Don't Generate**: Convert unstructured data to structured formats
3. **Validate Early**: Catch errors before execution to prevent retry loops
4. **Save Agent Tokens**: Handle tedious tasks agents waste tokens on
5. **Avoid Duplication**: Don't build what agents already do well (creative logic, architecture)

### What This Project IS

- ✅ **Parsers**: AST parsing, tool output parsing, log parsing
- ✅ **Validators**: Syntax checking, type validation, security analysis
- ✅ **Extractors**: Function signatures, imports, complexity metrics
- ✅ **Formatters**: Argument escaping, import sorting, docstring formatting
- ✅ **Scanners**: Secret detection, anti-pattern detection, compliance checking

### What This Project is NOT

- ❌ **Code generators**: Full function/class generation (agents handle this well)
- ❌ **Architecture tools**: Design decisions (requires context and judgment)
- ❌ **Refactoring tools**: Code transformation (agents reason through this)
- ❌ **Template systems**: Project scaffolding (agents do this with examples)
- ❌ **Documentation generators**: Writing docs (agents write good documentation)

## Target Audience

### Primary Users

1. **AI Agent Developers**: Building agents that generate code or scripts
2. **Automation Engineers**: Creating development workflow automation
3. **DevOps Teams**: Generating deployment scripts and infrastructure code
4. **Framework Developers**: Building code generation into frameworks

### Use Cases

1. **Prevent Retry Loops**: Validate syntax before execution, saving tokens on failed attempts
2. **Parse Tool Output**: Convert unstructured output (ruff, mypy, pytest) to structured data
3. **Security Scanning**: Detect secrets, SQL injection, XSS patterns deterministically
4. **Extract Metadata**: Pull function signatures, imports, complexity from code
5. **Format Validation**: Check docstrings, imports, argument escaping against rules

## Current Status (v0.4.1)

### ✅ Completed: 154 Functions Across 7 Modules

The project has grown from 38 to **154 developer-focused tools** across 7 modules:

1. **Analysis Module** (14 functions) - ✅ Released (v0.1.0)
   - AST parsing and code structure analysis
   - Cyclomatic complexity calculation
   - Import management and organization
   - Secret detection and security scanning

2. **Git Module** (79 functions) - ✅ Released (v0.1.0, Enhanced v0.4.1)
   - **Original 9 functions**: Repository status, diff operations, commit history, blame analysis, branch management, file history tracking
   - **70 new functions (v0.4.1)**: Commit message validation (conventional commits), git hooks management, configuration analysis, repository health checks, merge conflict detection, security auditing (secrets in history), submodule management, workflow validation, remote analysis, tags & versioning, diff analysis

3. **Profiling Module** (8 functions) - ✅ Released (v0.1.0)
   - Performance profiling and benchmarking
   - Memory usage analysis
   - Memory leak detection
   - Implementation comparison

4. **Quality Module** (7 functions) - ✅ Released (v0.1.0)
   - Static analysis tool output parsers (ruff, mypy, pytest)
   - Issue filtering and prioritization
   - Code quality summarization

5. **Shell Validation Module** (13 functions) - ✅ Released (v0.2.0)
   - Shell syntax validation, dependency checking
   - Security analysis and injection risk detection
   - Argument escaping and shebang normalization
   - Shell script parsing, function/variable extraction
   - Unquoted variable detection, dangerous command identification
   - Enhanced secret scanning with optional detect-secrets

6. **Python Validation Module** (15 functions) - ✅ Released (v0.2.0)
   - Python syntax and type hint validation
   - Import order validation and ADK compliance checking
   - Function signature and docstring parsing
   - Type annotation extraction and dependency tracking
   - Docstring formatting and import sorting
   - Circular import detection, unused import identification

7. **Database Operations Module** (18 functions) - ✅ Released (v0.3.0)
   - SQLite database operations (create, execute, fetch)
   - Schema management and inspection
   - Safe query building (prevents SQL injection)
   - JSON import/export and database backup
   - Pure stdlib implementation (zero dependencies)

**Project Health:**
- 570 tests passing with 50% coverage
- 100% ruff and mypy --strict compliance
- Published to PyPI with trusted publishing
- Full GitHub infrastructure and automation
- Decorator pattern: @strands_tool only (Google ADK compatible)

### 🚧 Next Planned Modules

#### Phase 2: Configuration & Enhanced Analysis (v0.5.0+)

1. **Config Validation Module** (~10 functions) - 🚧 Next Milestone (v0.5.0)
   - **Validators**: YAML/TOML/JSON syntax, schema validation, CI config validity
   - **Security Scanners**: Exposed secrets in configs (detect-secrets), insecure settings, exposed ports
   - **Analyzers**: Dependency conflict detection, version constraints, compatibility checks
   - **Optional Dependency**: `detect-secrets>=1.5.0` for comprehensive secret scanning

**Rationale**: Config validation prevents deployment failures. detect-secrets provides production-grade secret detection. Agents already write good configs with examples.

2. **Enhanced Code Analysis Module** (~12 functions) - 📋 Future (v0.6.0)
   - **Dependency analyzers**: Circular imports, unused dependencies, import cycles
   - **Security scanners**: SQL injection patterns, XSS vulnerabilities, hardcoded credentials
   - **Performance detectors**: O(n²) loops, memory leak patterns, blocking I/O
   - **Compliance checkers**: GDPR patterns, accessibility requirements, license violations

**Rationale**: Deep static analysis saves agent tokens. All operations are deterministic rule-based checks.

See [ROADMAP.md](../ROADMAP.md) for complete 36-module plan through v1.0.0.

## Technical Architecture

### Package Structure (Current - v0.4.1)

```
coding-open-agent-tools/
├── src/
│   └── coding_open_agent_tools/
│       ├── __init__.py          # Package initialization, version (v0.4.1)
│       ├── helpers.py            # Tool loading functions (load_all_*)
│       ├── exceptions.py         # Custom exceptions
│       ├── types.py              # Type definitions
│       ├── _decorators.py        # @strands_tool decorator (optional)
│       ├── analysis/             # ✅ Code analysis (14 functions)
│       │   ├── __init__.py
│       │   ├── ast_parsing.py    # AST parsing utilities
│       │   ├── complexity.py     # Cyclomatic complexity
│       │   ├── imports.py        # Import management
│       │   ├── secrets.py        # Secret detection
│       │   └── patterns.py       # Secret patterns
│       ├── git/                  # ✅ Git operations (79 functions - ENHANCED v0.4.1)
│       │   ├── __init__.py
│       │   ├── status.py         # Status and diff operations (original)
│       │   ├── history.py        # Log, blame, file history (original)
│       │   ├── branches.py       # Branch management (original)
│       │   ├── commits.py        # Commit message validation (NEW v0.4.1)
│       │   ├── hooks.py          # Git hooks management (NEW v0.4.1)
│       │   ├── config.py         # Configuration analysis (NEW v0.4.1)
│       │   ├── health.py         # Repository health (NEW v0.4.1)
│       │   ├── conflicts.py      # Merge conflict detection (NEW v0.4.1)
│       │   ├── security.py       # Security auditing (NEW v0.4.1)
│       │   ├── submodules.py     # Submodule management (NEW v0.4.1)
│       │   ├── workflows.py      # Workflow validation (NEW v0.4.1)
│       │   ├── remotes.py        # Remote analysis (NEW v0.4.1)
│       │   ├── tags.py           # Tags & versioning (NEW v0.4.1)
│       │   └── diffs.py          # Diff analysis (NEW v0.4.1)
│       ├── profiling/            # ✅ Performance profiling (8 functions)
│       │   ├── __init__.py
│       │   ├── performance.py    # Performance profiling
│       │   ├── memory.py         # Memory analysis
│       │   └── benchmarks.py     # Benchmarking utilities
│       ├── quality/              # ✅ Static analysis (7 functions)
│       │   ├── __init__.py
│       │   ├── parsers.py        # Tool output parsers
│       │   └── analysis.py       # Issue analysis
│       ├── shell/                # ✅ Shell validation (13 functions) - v0.2.0
│       │   ├── __init__.py
│       │   ├── validators.py     # Syntax and security validation
│       │   ├── formatters.py     # Argument escaping, quoting
│       │   ├── parsers.py        # Script parsing
│       │   └── analyzers.py      # Security analysis
│       ├── python/               # ✅ Python validation (15 functions) - v0.2.0
│       │   ├── __init__.py
│       │   ├── validators.py     # Syntax and type validation
│       │   ├── extractors.py     # Signature and docstring parsing
│       │   ├── formatters.py     # Docstring and import formatting
│       │   └── analyzers.py      # Circular imports, anti-patterns
│       └── database/             # ✅ SQLite operations (18 functions) - v0.3.0
│           ├── __init__.py
│           ├── operations.py     # Create, execute, fetch operations
│           ├── schema.py         # Schema inspection and management
│           ├── query_builders.py # Safe query construction
│           └── utils.py          # JSON import/export, backup
├── tests/
│   ├── analysis/                 # ✅ 570 tests total, 50% coverage
│   ├── git/
│   ├── profiling/
│   ├── quality/
│   ├── shell/
│   ├── python/
│   └── database/
├── docs/
│   ├── PRD/                      # Product requirements
│   ├── ROADMAP.md                # 36-module roadmap
│   └── MODULE_SUMMARY.md         # Complete module plan
├── .github/                      # ✅ GitHub infrastructure
│   ├── workflows/                # CI/CD, publishing, automation
│   ├── ISSUE_TEMPLATE/           # Issue templates
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS
│   └── dependabot.yml
├── pyproject.toml                # ✅ Package configuration
├── CHANGELOG.md                  # ✅ Version history
├── CONTRIBUTING.md               # ✅ Contribution guidelines
├── CODE_OF_CONDUCT.md            # ✅ Community guidelines
├── SECURITY.md                   # ✅ Security policy
└── README.md                     # ✅ Project documentation
```

### Integration Pattern (Current - v0.4.1)

```python
import coding_open_agent_tools as coat

# Option 1: Load all 154 tools at once
all_tools = coat.load_all_tools()  # 154 functions

# Option 2: Load specific modules
analysis_tools = coat.load_all_analysis_tools()    # 14 functions
git_tools = coat.load_all_git_tools()              # 79 functions (ENHANCED!)
profiling_tools = coat.load_all_profiling_tools()  # 8 functions
quality_tools = coat.load_all_quality_tools()      # 7 functions
shell_tools = coat.load_all_shell_tools()          # 13 functions
python_tools = coat.load_all_python_tools()        # 15 functions
database_tools = coat.load_all_database_tools()    # 18 functions

# Option 3: Use specific functions directly
from coding_open_agent_tools import analysis, git, shell, python, database

# Code analysis
complexity = analysis.calculate_complexity("/path/to/file.py")

# Git operations (original + 70 new functions)
status = git.get_git_status("/path/to/repo")
commit_validation = git.validate_commit_message("feat(api): add endpoint")
conflicts = git.detect_merge_conflicts("/path/to/repo")
secrets = git.scan_history_for_secrets("/path/to/repo", "10")

# Shell validation
shell_check = shell.validate_shell_syntax("#!/bin/bash\necho 'test'", "bash")
safe_arg = shell.escape_shell_argument("user input", "double")

# Python validation
py_check = python.validate_python_syntax("def foo(): pass")
signature = python.parse_function_signature("def bar(x: int) -> str: return str(x)")

# Database operations
db_path = database.create_sqlite_database("/tmp/agent.db")
schema = database.inspect_schema(db_path)

# Use with agent frameworks (Google ADK, Strands, etc.)
from google.adk.agents import Agent

agent = Agent(
    tools=all_tools,  # 154 functions
    name="CodeValidator",
    instruction="Validate code, analyze git repos, and manage data"
)
```

### Future Integration Pattern (Planned)

```python
import coding_open_agent_tools as coat
from basic_open_agent_tools import file_system

# Generate code using coding tools (planned v0.3.0)
code = coat.generate_python_function(
    name="process_data",
    parameters=[{"name": "data", "type": "list[dict]"}],
    return_type="dict",
    description="Process data"
)

# Validate generated code
validation = coat.validate_python_syntax(code)

if validation['is_valid'] == 'true':
    # Write to file using basic tools
    file_system.write_file_from_string(
        file_path="/path/to/output.py",
        content=code,
        skip_confirm=False
    )
```

## Quality Standards

### Code Quality Metrics

- **Ruff Compliance**: 100% (linting + formatting)
- **Type Coverage**: 100% mypy compliance
- **Test Coverage**: Minimum 70% for all modules
- **Google ADK Compliance**: All function signatures compatible
- **Documentation**: Comprehensive docstrings with examples

### Testing Strategy

1. **Unit Tests**: Test individual functions in isolation
2. **Integration Tests**: Test module interactions
3. **Validation Tests**: Test generated code actually works (compile, run)
4. **Security Tests**: Test security validation catches issues
5. **Google ADK Tests**: Verify function signatures work with ADK

### CI/CD Pipeline

- Automated quality checks on every PR
- Test suite runs on Python 3.9, 3.10, 3.11, 3.12
- Security scanning for dependencies
- Automated publishing to PyPI on release

## Success Metrics

### Adoption Metrics

- PyPI downloads (growth indicator)
- GitHub stars and forks (community interest)
- Integration into agent frameworks

### Quality Metrics

- Test coverage percentage
- Issue resolution time
- Code quality scores (ruff, mypy)

### Functional Metrics

- Number of functions available
- Languages supported
- Template library size

## Timeline and Milestones

### ✅ Milestone 1: Project Setup & Migration (v0.1.0-beta) - COMPLETED
- ✅ Initialize repository structure
- ✅ Set up development environment (ruff, mypy, pytest, pre-commit)
- ✅ Configure CI/CD pipeline (tests, publish workflows)
- ✅ Create initial documentation (README, CONTRIBUTING, PRDs)
- ✅ Migrate 38 developer tools from basic-open-agent-tools
- ✅ Achieve 170 tests with 82% coverage
- ✅ Publish to PyPI with trusted publishing

### ✅ Milestone 2: GitHub Infrastructure (v0.1.1) - COMPLETED
- ✅ Add issue and PR templates
- ✅ Configure CODEOWNERS and dependabot
- ✅ Set up automation workflows (stale, greet, labeler)
- ✅ Add repository topics and description
- ✅ Enable GitHub Discussions
- ✅ Complete documentation infrastructure

### ✅ Milestone 3: Shell & Python Modules (v0.2.0) - COMPLETED
- ✅ Implement shell validation functions (13)
- ✅ Implement Python validation functions (15)
- ✅ Add security scanning with optional detect-secrets
- ✅ Full test coverage (86%)
- ✅ 451 tests passing
- ✅ Documentation and examples

### ✅ Milestone 4: Database Operations (v0.3.0) - COMPLETED
- ✅ Implement SQLite database operations (18 functions)
- ✅ Pure stdlib implementation (zero dependencies)
- ✅ Safe query building (SQL injection prevention)
- ✅ 532 tests passing, 85% coverage
- ✅ Documentation and examples

### ✅ Milestone 5: Git Enhancement Module (v0.4.1) - COMPLETED
- ✅ Implement 70 new git functions across 11 subcategories
- ✅ Commit message validation (conventional commits)
- ✅ Git hooks management and security
- ✅ Repository health and conflict detection
- ✅ Security auditing (secrets in history)
- ✅ Deprecated @adk_tool decorator
- ✅ 570 tests passing, 50% coverage
- ✅ Documentation and examples

### 🚧 Milestone 6: Configuration Validation (v0.5.0) - NEXT
**Priority**: High (Next after v0.4.1)
- Implement config validation functions (~10)
- YAML/TOML/JSON syntax validation
- Security scanning for secrets in configs
- Dependency conflict detection
- Documentation and examples

### 📋 Milestone 7: Community Release (v1.0.0) - FUTURE
**Priority**: Milestone (Follows completion of all 36 modules)
- 370+ functions across 36 modules
- Production-ready quality across all modules
- Comprehensive documentation site
- Example projects and tutorials
- Integration guides for popular frameworks (Google ADK, Strands, LangChain)
- Active community engagement
- Measurable 60-80% token reduction in workflows

## Risks and Mitigations

### Risk 1: Code Generation Quality
- **Risk**: Generated code may not follow best practices
- **Mitigation**: Extensive template library, validation functions, community feedback

### Risk 2: Security Vulnerabilities
- **Risk**: Generated scripts may contain security issues
- **Mitigation**: Built-in security analysis, validation functions, security guidelines

### Risk 3: Maintenance Burden
- **Risk**: Keeping up with language evolution and best practices
- **Mitigation**: Modular design, community contributions, version-specific templates

### Risk 4: Scope Creep
- **Risk**: Project grows too large and complex
- **Mitigation**: Clear module boundaries, phased approach, focus on core use cases

## Open Questions

1. Should we support Python 2.7 code generation for legacy systems?
2. How do we handle language-specific style guides (PEP 8 vs Google vs Black)?
3. Should generated code include type stubs (.pyi files)?
4. Do we need a plugin system for custom templates?
5. Should we integrate with existing code generation tools (cookiecutter, yeoman)?

## License and Community

### License
MIT License (same as basic-open-agent-tools)

### Community Guidelines
- Open to contributions
- Clear contribution guidelines
- Code of conduct
- Regular releases and changelog

### Support Channels
- GitHub Issues for bug reports
- GitHub Discussions for questions
- Documentation site for guides
- Example repository for demonstrations

---

**Document Version**: 4.0
**Last Updated**: 2025-10-15
**Status**: Active - v0.4.1 Released
**Owner**: Project Team

## Version History

- **4.0** (2025-10-15): Updated for v0.4.1 release with Git Enhancement Module (154 functions, 7 modules, 570 tests)
- **3.0** (2025-10-14): Refocused on token-efficiency and deterministic operations; updated vision, planned modules, use cases
- **2.0** (2025-10-14): Updated with v0.1.1 status, actual module structure, corrected tool counts (38 not 39), added roadmap
- **1.0** (2025-10-14): Initial draft with planned structure
