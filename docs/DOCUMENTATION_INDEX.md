# Documentation Index

Complete guide to coding-open-agent-tools documentation.

## Quick Start

- **[README.md](../README.md)** - Project overview, installation, quick start
- **[docs/examples/](examples/)** - Practical usage examples with token savings analysis

## Core Documentation

### Architecture & Design
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - Complete architecture overview
  - Project philosophy: Token efficiency first
  - Design patterns and best practices
  - Module organization
  - Framework compatibility (Strands, Google ADK, LangGraph)
  - Code quality standards
  - Testing strategy
  - Optional dependencies pattern
  - Performance considerations

### Contributing
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Comprehensive contribution guide
  - Development setup
  - Code quality standards
  - Testing guidelines
  - What to contribute (and what not to)
  - Decision framework
  - Pull request process
  - Decorator requirements
  - Google ADK compliance rules

### Security
- **[SECURITY.md](../SECURITY.md)** - Security policy and reporting
- **[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)** - Community guidelines

## Usage Examples

Located in [docs/examples/](examples/):

### 1. Python Validation
**File:** [01_python_validation.py](examples/01_python_validation.py)
**Token Savings:** 90-95%
**Focus:** Validate Python syntax before execution, prevent retry loops

### 2. Git Health Check
**File:** [02_git_health_check.py](examples/02_git_health_check.py)
**Token Savings:** 70-85%
**Focus:** Repository health monitoring, metrics, garbage collection

### 3. Code Navigation
**File:** [03_code_navigation.py](examples/03_code_navigation.py)
**Token Savings:** 70-95%
**Focus:** Navigate code without reading full files, function discovery

### 4. Security Scanning
**File:** [04_security_scanning.py](examples/04_security_scanning.py)
**Token Savings:** 85-90%
**Focus:** Detect secrets and security vulnerabilities

### 5. Config Parsing
**File:** [05_config_parsing.py](examples/05_config_parsing.py)
**Token Savings:** 80-90%
**Focus:** Parse and validate configuration files (YAML, TOML, JSON, .env)

**Examples README:** [docs/examples/README.md](examples/README.md)

## Planning & Roadmap

- **[TODO.md](../TODO.md)** - Current roadmap and planned features
- **[ROADMAP.md](ROADMAP.md)** - Long-term vision (36 modules, 370+ functions)
- **[MODULE_SUMMARY.md](MODULE_SUMMARY.md)** - Complete module plan
- **[CHANGELOG.md](../CHANGELOG.md)** - Release history and updates

## Product Requirements

Located in [docs/PRD/](PRD/):

- **[01-project-overview.md](PRD/01-project-overview.md)** - Project vision and goals
- **[02-shell-module-prd.md](PRD/02-shell-module-prd.md)** - Shell module specification
- **[03-codegen-module-prd.md](PRD/03-codegen-module-prd.md)** - Code generation module (future)

## Module Documentation

### Core Modules (199 functions)

#### Code Analysis
- **Git Module** (79 functions)
  - 14 submodules: branches, commits, config, conflicts, diffs, health, history, hooks, remotes, security, status, submodules, tags, workflows
  - Repository operations and health checks
  - Security scanning and metrics

- **Python Module** (32 functions)
  - 5 submodules: navigation, validators, analyzers, extractors, formatters
  - 17 navigation tools (70-95% token savings)
  - Syntax validation and type checking

- **Analysis Module** (14 functions)
  - AST parsing and complexity calculation
  - Import tracking and management
  - Secret detection

#### Configuration & Data
- **Config Module** (28 functions)
  - .env file operations
  - YAML/TOML/JSON extraction
  - INI/properties/XML parsing
  - Security scanning

- **Database Module** (18 functions)
  - SQLite operations
  - Safe query building
  - Schema inspection

#### Development Tools
- **Shell Module** (13 functions)
  - Shell validation and security
  - Argument escaping

- **Profiling Module** (8 functions)
  - Performance and memory profiling

- **Quality Module** (7 functions)
  - Static analysis parsers

### Language-Specific Modules (87 functions)

7 language modules with 17 functions each:
- C++ navigation
- C# navigation
- Go navigation
- Java navigation
- JavaScript/TypeScript navigation
- Ruby navigation
- Rust navigation

## Key Concepts

### Token Efficiency Philosophy

**We build what agents waste tokens on:**
- ✅ Validators - Catch errors before execution
- ✅ Parsers - Convert unstructured → structured
- ✅ Extractors - Pull specific data
- ✅ Formatters - Apply deterministic rules
- ✅ Scanners - Rule-based detection

**We avoid what agents do well:**
- ❌ Code generators
- ❌ Architecture tools
- ❌ Refactoring tools

### Design Patterns

1. **Decorator Pattern** - Centralized `@strands_tool` decorator
2. **Shared Utilities** - Common validation functions
3. **JSON-Serializable Returns** - Google ADK compliance
4. **Input Validation** - Clear error messages
5. **Smart Confirmation** - Three-mode system (bypass/interactive/agent)

### Framework Compatibility

| Framework | Support | Notes |
|-----------|---------|-------|
| **Strands** | ✅ Full | All tools use `@strands_tool` decorator |
| **Google ADK** | ✅ Full | JSON-serializable returns, no defaults |
| **LangGraph** | ✅ Full | Works with standard callables |

## Testing & Quality

### Quality Standards
- 100% ruff compliance
- 100% mypy compliance
- 83% test coverage (571 tests passing)
- Google ADK compliance

### Test Categories
1. Type validation tests
2. Value validation tests
3. Path validation tests
4. Happy path tests
5. Edge case tests
6. Mocked subprocess tests

### Running Tests
```bash
# All tests
pytest tests/

# With coverage
pytest tests/ --cov=src --cov-report=term

# Specific module
pytest tests/git/test_health.py -v
```

## Helper Functions

11 helper functions for tool management:

### Tool Loading
- `load_all_tools()` - Load all 286 functions
- `load_all_analysis_tools()` - 14 functions
- `load_all_config_tools()` - 28 functions
- `load_all_git_tools()` - 79 functions
- `load_all_profiling_tools()` - 8 functions
- `load_all_quality_tools()` - 7 functions
- `load_all_shell_tools()` - 13 functions
- `load_all_python_tools()` - 32 functions
- `load_all_database_tools()` - 18 functions

### Tool Management
- `merge_tool_lists()` - Combine tool lists
- `get_tool_info()` - Inspect tool details
- `list_all_available_tools()` - Get organized catalog

## Installation

### Basic Installation
```bash
pip install coding-open-agent-tools
```

### Optional Dependencies
```bash
# Enhanced security scanning
pip install coding-open-agent-tools[enhanced-security]

# Enhanced navigation
pip install coding-open-agent-tools[enhanced-navigation]

# All optional features
pip install coding-open-agent-tools[all]

# Development installation
pip install -e ".[dev]"
```

## Quick Reference

### Token Savings by Use Case

| Use Case | Without Tools | With Tools | Savings |
|----------|--------------|------------|---------|
| Python validation | 1700 tokens | 950 tokens | 44% |
| Git health check | 1000 tokens | 200 tokens | 80% |
| Code navigation | 1700 tokens | 180 tokens | 89% |
| Security scanning | 8500 tokens | 600 tokens | 93% |
| Config parsing | 1000 tokens | 80 tokens | 92% |

**Average: 80-90% token savings**

### Common Workflows

#### 1. Validate Generated Code
```python
from coding_open_agent_tools.python import validators

result = validators.validate_python_syntax(generated_code)
if result['is_valid'] == 'true':
    # Code is valid, proceed
    pass
```

#### 2. Navigate Codebase
```python
from coding_open_agent_tools.python import navigation

# Get overview
overview = navigation.get_python_module_overview(source_code)

# Get line numbers for specific function
lines = navigation.get_python_function_line_numbers(source_code, "my_function")
# Use with Read tool for targeted reading
```

#### 3. Check Repository Health
```python
from coding_open_agent_tools.git import health

metrics = health.get_repository_metrics(repo_path)
print(f"Health score: {metrics['health_score']}/100")
```

#### 4. Scan for Secrets
```python
from coding_open_agent_tools.analysis import secrets

result = secrets.scan_for_secrets(code_content)
if result['secret_count'] != '0':
    # Handle found secrets
    pass
```

#### 5. Parse Configuration
```python
from coding_open_agent_tools.config import extractors

db_host = extractors.extract_yaml_value(config_content, "database.host")
print(f"Database host: {db_host['value']}")
```

## Additional Resources

### External Links
- [GitHub Repository](https://github.com/Open-Agent-Tools/coding-open-agent-tools)
- [PyPI Package](https://pypi.org/project/coding-open-agent-tools/)
- [basic-open-agent-tools](https://github.com/Open-Agent-Tools/basic-open-agent-tools) - Foundation layer
- [Open Agent Tools Organization](https://github.com/Open-Agent-Tools)

### Community
- GitHub Issues - Bug reports and feature requests
- GitHub Discussions - Questions and ideas
- Pull Requests - Contributions welcome

## Version Information

**Current Version:** v0.9.1
**Status:** Active Development
**Python Support:** 3.9+
**License:** MIT

## Maintainers

- @jwesleye
- @unseriousai

---

**Last Updated:** 2025-11-24

For questions or contributions, see [CONTRIBUTING.md](../CONTRIBUTING.md).
