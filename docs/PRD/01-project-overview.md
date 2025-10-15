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

## Current Status (v0.1.1)

### ✅ Completed: Migrated Developer Tools (v0.1.0-beta)

The project has successfully migrated **38 developer-focused tools** from basic-open-agent-tools:

1. **Analysis Module** (14 functions) - ✅ Released
   - AST parsing and code structure analysis
   - Cyclomatic complexity calculation
   - Import management and organization
   - Secret detection and security scanning

2. **Git Module** (9 functions) - ✅ Released
   - Repository status and diff operations
   - Commit history and blame analysis
   - Branch management
   - File history tracking

3. **Profiling Module** (8 functions) - ✅ Released
   - Performance profiling and benchmarking
   - Memory usage analysis
   - Memory leak detection
   - Implementation comparison

4. **Quality Module** (7 functions) - ✅ Released
   - Static analysis tool output parsers (ruff, mypy, pytest)
   - Issue filtering and prioritization
   - Code quality summarization

**Project Health:**
- 170 tests passing with 82% coverage
- 100% ruff and mypy compliance
- Published to PyPI with trusted publishing
- Full GitHub infrastructure and automation

### 🚧 Planned Modules (Refocused on Token Efficiency)

#### Phase 1: Shell Validation & Security (v0.2.0)

1. **Shell Validation Module** (~13 functions) - 🚧 Planned
   - **Validators**: Bash syntax checking, dependency detection
   - **Security Scanners**: Unquoted variables, eval usage, enhanced secret detection (detect-secrets)
   - **Formatters**: Argument escaping, shebang normalization
   - **Parsers**: Extract functions, variables, commands from scripts
   - **Optional Dependency**: `detect-secrets>=1.5.0` for comprehensive secret scanning
   - See: `02-shell-module-prd.md` (to be updated)

**Rationale**: Agents waste tokens getting shell escaping right and miss security issues. Validation prevents execution failures. detect-secrets provides production-grade secret detection as optional enhancement.

#### Phase 2: Python Validation & Analysis (v0.3.0)

2. **Python Validation Module** (~15 functions) - 🚧 Planned
   - **Validators**: Enhanced syntax validation, type hint checking, import order
   - **Extractors**: Function signatures, docstring parsing, type annotations
   - **Formatters**: Docstring formatting (Google/NumPy/Sphinx), import sorting
   - **Analyzers**: ADK compliance checking, anti-pattern detection
   - See: `03-codegen-module-prd.md` (to be updated)

**Rationale**: Parsing and validation are deterministic. Skip generation—agents handle that well.

#### Phase 3: Configuration Validation (v0.4.0)

3. **Config Validation Module** (~10 functions) - 📋 Future
   - **Validators**: YAML/TOML/JSON syntax, schema validation
   - **Security Scanners**: Exposed secrets in configs (detect-secrets), insecure settings
   - **Analyzers**: Dependency conflict detection, compatibility checks
   - **Parsers**: Extract structured data from CI/CD configs
   - **Optional Dependency**: `detect-secrets>=1.5.0` for comprehensive secret scanning

**Rationale**: Config validation prevents deployment failures. detect-secrets provides production-grade secret detection. Agents already write good configs with examples.

#### Phase 4: Enhanced Code Analysis (v0.5.0)

4. **Advanced Analysis Module** (~12 functions) - 📋 Future
   - **Dependency analyzers**: Circular imports, unused dependencies
   - **Security scanners**: SQL injection patterns, XSS vulnerabilities
   - **Performance detectors**: O(n²) loops, memory leaks, anti-patterns
   - **Compliance checkers**: GDPR patterns, accessibility requirements

## Technical Architecture

### Package Structure (Current)

```
coding-open-agent-tools/
├── src/
│   └── coding_open_agent_tools/
│       ├── __init__.py          # Package initialization, version
│       ├── helpers.py            # Tool loading functions (load_all_*)
│       ├── exceptions.py         # Custom exceptions
│       ├── types.py              # Type definitions
│       ├── analysis/             # ✅ Code analysis (14 functions)
│       │   ├── __init__.py
│       │   ├── ast_parsing.py    # AST parsing utilities
│       │   ├── complexity.py     # Cyclomatic complexity
│       │   ├── imports.py        # Import management
│       │   ├── secrets.py        # Secret detection
│       │   └── patterns.py       # Secret patterns
│       ├── git/                  # ✅ Git operations (9 functions)
│       │   ├── __init__.py
│       │   ├── status.py         # Status and diff operations
│       │   ├── history.py        # Log, blame, file history
│       │   └── branches.py       # Branch management
│       ├── profiling/            # ✅ Performance profiling (8 functions)
│       │   ├── __init__.py
│       │   ├── performance.py    # Performance profiling
│       │   ├── memory.py         # Memory analysis
│       │   └── benchmarks.py     # Benchmarking utilities
│       ├── quality/              # ✅ Static analysis (7 functions)
│       │   ├── __init__.py
│       │   ├── parsers.py        # Tool output parsers
│       │   └── analysis.py       # Issue analysis
│       ├── shell/                # 🚧 Shell script generation (planned)
│       └── codegen/              # 🚧 Python code generation (planned)
├── tests/
│   ├── analysis/                 # ✅ 170 tests, 82% coverage
│   ├── git/
│   ├── profiling/
│   └── quality/
├── docs/
│   ├── PRD/                      # Product requirements
│   └── examples/                 # Usage examples (planned)
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

### Integration Pattern (Current)

```python
import coding_open_agent_tools as coat

# Option 1: Load all 38 tools at once
all_tools = coat.load_all_tools()

# Option 2: Load specific modules
analysis_tools = coat.load_all_analysis_tools()  # 14 functions
git_tools = coat.load_all_git_tools()            # 9 functions
profiling_tools = coat.load_all_profiling_tools()  # 8 functions
quality_tools = coat.load_all_quality_tools()    # 7 functions

# Option 3: Use specific functions directly
from coding_open_agent_tools import analysis, git, profiling, quality

complexity = analysis.calculate_complexity("/path/to/file.py")
status = git.get_git_status("/path/to/repo")
profile = profiling.profile_function("/path/to/module.py", "function_name", '{"arg": "value"}')
issues = quality.parse_ruff_json(ruff_output)

# Use with agent frameworks
from google.adk.agents import Agent

agent = Agent(
    tools=all_tools,
    name="CodeAnalyzer",
    instruction="Analyze code quality and performance"
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

### ✅ Milestone 1.1: GitHub Infrastructure (v0.1.1) - COMPLETED
- ✅ Add issue and PR templates
- ✅ Configure CODEOWNERS and dependabot
- ✅ Set up automation workflows (stale, greet, labeler)
- ✅ Add repository topics and description
- ✅ Enable GitHub Discussions
- ✅ Complete documentation infrastructure

### 🚧 Milestone 2: Shell Validation & Security (v0.2.0) - PLANNED
**Priority**: High (Next after v0.1.1)
- Implement shell validation functions (~13)
- Add security scanning and checks
- Full test coverage (80%+)
- Documentation and examples

### 🚧 Milestone 3: Python Validation & Analysis (v0.3.0) - PLANNED
**Priority**: High (Follows v0.2.0)
- Implement Python validation functions (~15)
- Add docstring parsing (Google/NumPy/Sphinx)
- Type hint validation and parsing
- Documentation and examples

### 📋 Milestone 4: Community Release (v1.0.0) - FUTURE
**Priority**: Milestone (Follows completion of all 35 modules)
- Production-ready quality across all modules
- Comprehensive documentation site
- Example projects and tutorials
- Integration guides for popular frameworks (Google ADK, Strands)
- Active community engagement

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

**Document Version**: 3.0
**Last Updated**: 2025-10-14
**Status**: Active - v0.1.1 Released
**Owner**: Project Team

## Version History

- **3.0** (2025-10-14): Refocused on token-efficiency and deterministic operations; updated vision, planned modules, use cases
- **2.0** (2025-10-14): Updated with v0.1.1 status, actual module structure, corrected tool counts (38 not 39), added roadmap
- **1.0** (2025-10-14): Initial draft with planned structure
