# Coding Open Agent Tools

**Deterministic code validation and analysis toolkit for AI agents - Save tokens, prevent errors**

This project provides **parsing, validation, and analysis tools** that save agent tokens by handling deterministic operations agents struggle with or waste excessive tokens on. It complements [basic-open-agent-tools](https://github.com/Open-Agent-Tools/basic-open-agent-tools) by providing higher-level code analysis capabilities.

## 🎯 Core Philosophy: Token Efficiency

**We focus on what agents waste tokens on:**
- ✅ **Validators** - Catch syntax/type errors before execution (prevents retry loops)
- ✅ **Parsers** - Convert unstructured → structured (AST, tool output, logs)
- ✅ **Extractors** - Pull specific data from complex sources (tedious for agents)
- ✅ **Formatters** - Apply deterministic rules (escaping, quoting, import sorting)
- ✅ **Scanners** - Rule-based pattern detection (secrets, anti-patterns, security)

**We avoid duplicating what agents do well:**
- ❌ Full code generation (agents excel at creative logic)
- ❌ Architecture decisions (requires judgment and context)
- ❌ Code refactoring (agents reason through transformations)
- ❌ Project scaffolding (agents use examples effectively)

## 🆕 What's New in v0.10.0

🎉 **Phase 12 Completion: Quality & Documentation** - Major improvements across the board:
- **Test Coverage**: 26% → 84% (added 513 new tests for git modules)
- **Code Quality**: Reduced duplication from 15-20% → <5% (navigation/shared.py)
- **Decorator Consistency**: 100% of 51 modules using centralized pattern
- **Documentation**: ~5,000 lines of comprehensive docs with runnable examples
- **Production Ready**: 1,775 tests passing, all quality gates passing

### Previous Updates

**v0.9.0** - Configuration Module Expansion (+19 new functions, 42 total)
- .env file support, config extraction, security best practices

**v0.5.0** - Python Navigation Complete: Added 7 advanced navigation functions (70-90% token reduction)

**v0.4.4** - Python Navigation Tools: Added 10 token-saving navigation functions for line numbers, overviews, and signatures

**v0.4.3** - Helper Function Documentation: Added comprehensive documentation for all 11 helper functions with usage examples and `__all__` export

**v0.4.2** - Enhanced diff preview from 20 to 50 lines for better context

**v0.4.0** - Added database module with SQLite operations and safe query building

**v0.3.0** - Python module for syntax validation, type checking, and import analysis

**v0.2.0** - Shell module with validation, security scanning, and escaping utilities

**v0.1.0-beta** - Initial release with 39 migrated developer-focused tools from basic-open-agent-tools

## Available Tools

**9 core modules** with **213 functions** + **8 language-specific modules** with **184 functions** = **461 total functions** — all with `@strands_tool` decorator and Google ADK compatible signatures.

### 📊 Core Module Breakdown

| Module | Functions | Description |
|--------|-----------|-------------|
| **Code Analysis** | | |
| `git` | 79 | Repository operations, history, commits, branches, tags, hooks, workflows |
| `config` | 42 | **.env/INI/properties/XML parsing**, YAML/TOML/JSON validation, security scanning |
| `python` | 32 | **Navigation (23 tools!)**, syntax validation, type checking, import analysis, AST parsing |
| `database` | 18 | SQLite operations, safe query building, schema inspection |
| `analysis` | 14 | Code complexity, AST parsing, import tracking, secret detection |
| `dependencies` | 12 | **Multi-language parsers, version conflicts, circular dependencies, security advisories** |
| **Development Tools** | | |
| `shell` | 13 | Shell validation, security scanning, argument escaping |
| `profiling` | 8 | Performance profiling, memory analysis, execution timing |
| `quality` | 7 | Static analysis parsers, linting tool integration |
| **CORE TOTAL** | **225** | |

**Language-Specific Modules**: Python (23), JavaScript/TypeScript (35), Java (23), Go (23), Rust (23), C++ (23), C# (23), Ruby (23) = **196 functions**

**GRAND TOTAL**: **485 functions** across **18 modules**

See [docs/ROADMAP.md](./docs/ROADMAP.md) and [docs/PRD](./docs/PRD/) for detailed plans.

## Relationship to Basic Open Agent Tools

### Division of Responsibilities

**[basic-open-agent-tools](https://github.com/Open-Agent-Tools/basic-open-agent-tools)** (Foundation Layer):
- Core file system operations
- Text and data processing
- Document format handling (PDF, Word, Excel, PowerPoint, etc.)
- System utilities and network operations
- General-purpose, low-level operations
- 326 foundational agent tools across 21 modules

**coding-open-agent-tools** (Development Layer):
- Code generation and scaffolding
- Shell script creation and validation
- Project structure generation
- Development workflow automation
- Language-specific tooling
- Security analysis for generated code

### Dependency Model

```
coding-open-agent-tools (this project)
    └─> basic-open-agent-tools (dependency)
         └─> Python stdlib (minimal external dependencies)
```

This project will **depend on** `basic-open-agent-tools` for file operations, text processing, and other foundational capabilities, while providing specialized code generation features.

## Key Features

### Shell Module (13 functions)
Validate and analyze shell scripts for security and correctness:

- **Validation**: Syntax checking, shell type detection (bash/zsh/sh)
- **Security**: Security scanning for dangerous patterns, command injection risks
- **Utilities**: Argument escaping, quote handling, path validation

**Example**:
```python
import coding_open_agent_tools as coat

# Validate shell syntax
validation = coat.shell.validate_shell_syntax("#!/bin/bash\necho 'Hello'", "bash")
print(f"Valid: {validation['is_valid']}")

# Security analysis
security = coat.shell.analyze_shell_security(script_content)
print(f"Issues found: {len(security['issues'])}")
```

### Python Module (15 functions)
Validate Python code and analyze imports:

- **Validation**: Syntax checking, AST parsing, type hint extraction
- **Analysis**: Import tracking, dependency analysis, function/class detection
- **Type Checking**: Extract and validate type annotations

**Example**:
```python
import coding_open_agent_tools as coat

# Validate Python syntax
result = coat.python.validate_python_syntax("def hello(): return 'world'")
print(f"Valid: {result['is_valid']}")

# Analyze imports
imports = coat.python.extract_imports(code_content)
print(f"Found {len(imports)} import statements")
```

## Design Philosophy

### Same Principles as Basic Tools

1. **Minimal Dependencies**: Prefer stdlib, add dependencies only when substantial value added
2. **Google ADK Compliance**: All functions use JSON-serializable types, no default parameters
3. **Local Operations**: No HTTP/API calls, focus on local development tasks
4. **Type Safety**: Full mypy compliance with comprehensive type hints
5. **High Quality**: 100% ruff compliance, comprehensive testing (80%+ coverage)
6. **Agent-First Design**: Functions designed for LLM comprehension and use
7. **Smart Confirmation**: 3-mode confirmation system (bypass/interactive/agent) for write/delete operations

### Additional Focus Areas

1. **Code Quality**: Generate code that follows best practices (PEP 8, type hints)
2. **Security**: Built-in security analysis and validation for generated scripts
3. **Template-Driven**: Extensive template library for common patterns
4. **Validation**: Syntax checking and error detection before execution
5. **Self-Documenting**: All generated code includes comprehensive documentation

## Target Use Cases

### For AI Agents
- **Project Scaffolding**: Create new projects with proper structure
- **Boilerplate Reduction**: Generate repetitive code structures
- **Script Automation**: Create deployment and maintenance scripts
- **Test Generation**: Scaffold comprehensive test coverage
- **Documentation**: Generate consistent docstrings and README files

### For Developers
- **Agent Development**: Build agents that generate code
- **Automation Engineering**: Create development workflow automation
- **DevOps**: Generate deployment scripts and service configurations
- **Framework Building**: Integrate code generation into frameworks

## Integration Example

```python
import coding_open_agent_tools as coat
from basic_open_agent_tools import file_system

# Generate code using coding tools
code = coat.generate_python_function(...)

# Validate the generated code
validation = coat.validate_python_syntax(code)

if validation['is_valid'] == 'true':
    # Write to file using basic tools
    file_system.write_file_from_string(
        file_path="/path/to/output.py",
        content=code,
        skip_confirm=False
    )
```

## Safety Features

### Smart Confirmation System (3 Modes)

The confirmation module provides intelligent confirmation handling for future write/delete operations:

**🔄 Bypass Mode** - `skip_confirm=True` or `BYPASS_TOOL_CONSENT=true` env var
- Proceeds immediately without prompts
- Perfect for CI/CD and automation

**💬 Interactive Mode** - Terminal with `skip_confirm=False`
- Prompts user with `y/n` confirmation
- Shows preview info (file sizes, etc.)

**🤖 Agent Mode** - Non-TTY with `skip_confirm=False`
- Raises `CONFIRMATION_REQUIRED` error with instructions
- LLM agents can ask user and retry with `skip_confirm=True`

```python
from coding_open_agent_tools.confirmation import check_user_confirmation

# Safe by default - adapts to context
confirmed = check_user_confirmation(
    operation="overwrite file",
    target="/path/to/file.py",
    skip_confirm=False,  # Interactive prompt OR agent error
    preview_info="1024 bytes"
)

# Automation mode
import os
os.environ['BYPASS_TOOL_CONSENT'] = 'true'
# All confirmations bypassed for CI/CD
```

**Note**: Current modules (analysis, git, profiling, quality) are read-only and don't require confirmations. The confirmation system is ready for future write/delete operations in planned modules (shell generation, code generation, etc.).

## Documentation

- **[Product Requirements Documents](./docs/PRD/)**: Detailed specifications
  - [Project Overview](./docs/PRD/01-project-overview.md)
  - [Shell Module PRD](./docs/PRD/02-shell-module-prd.md)
  - [Codegen Module PRD](./docs/PRD/03-codegen-module-prd.md)

## Installation

```bash
# Install from PyPI
pip install coding-open-agent-tools

# Or with UV
uv add coding-open-agent-tools

# Install from source for development
git clone https://github.com/Open-Agent-Tools/coding-open-agent-tools.git
cd coding-open-agent-tools
pip install -e ".[dev]"

# This will automatically install basic-open-agent-tools as a dependency
```

## Helper Functions

The package provides **29 helper functions** for tool management, loading, and introspection:

### 📦 Core Module Loaders

| Function | Count | Description |
|----------|-------|-------------|
| `load_all_tools()` | 461 | Load **all** functions from all modules (recommended) |
| `load_all_analysis_tools()` | 14 | AST parsing, complexity, imports, secret detection |
| `load_all_config_tools()` | 42 | YAML/TOML/JSON, .env, security scanning, validation |
| `load_all_git_tools()` | 79 | Repository operations, commits, branches, tags, hooks |
| `load_all_profiling_tools()` | 8 | Performance profiling, memory analysis, benchmarking |
| `load_all_quality_tools()` | 7 | ruff/mypy/pytest parsers, static analysis |
| `load_all_shell_tools()` | 13 | Shell validation, security scanning, escaping |
| `load_all_python_tools()` | 32 | Python validation, navigation, import analysis |
| `load_all_database_tools()` | 18 | SQLite operations, query building, schema inspection |

### 🌍 Language-Specific Loaders (Navigation Tools)

| Function | Count | Description |
|----------|-------|-------------|
| `load_all_javascript_tools()` | 35 | JavaScript/TypeScript navigation & validation (70-85% token savings) |
| `load_all_java_tools()` | 23 | Java code navigation and structure analysis |
| `load_all_go_tools()` | 23 | Go code navigation for microservices/cloud |
| `load_all_rust_tools()` | 23 | Rust code navigation with memory safety focus |
| `load_all_cpp_tools()` | 23 | C++ code navigation for systems programming |
| `load_all_csharp_tools()` | 23 | C# code navigation for .NET/Unity projects |
| `load_all_ruby_tools()` | 23 | Ruby code navigation for Rails applications |

### 🎯 Language-Specific Loadouts (Pre-Configured Sets)

Curated tool combinations optimized for specific languages:

| Function | Count | Included Modules | Best For |
|----------|-------|------------------|----------|
| `load_python_loadout()` | 171 | Python, Analysis, Quality, Git, Shell, Database, Profiling | Python/Django/FastAPI projects |
| `load_javascript_loadout()` | 161 | JavaScript, Analysis, Git, Shell, Database, Profiling | Node.js/React/Vue.js projects |
| `load_typescript_loadout()` | 161 | Same as JavaScript (TypeScript is a superset) | TypeScript/Angular projects |
| `load_java_loadout()` | 149 | Java, Analysis, Git, Shell, Database, Profiling | Spring Boot/enterprise Java |
| `load_cpp_loadout()` | 149 | C++, Analysis, Git, Shell, Database, Profiling | Systems/performance-critical apps |
| `load_csharp_loadout()` | 149 | C#, Analysis, Git, Shell, Database, Profiling | .NET/Unity/Xamarin projects |
| `load_go_loadout()` | 149 | Go, Analysis, Git, Shell, Database, Profiling | Microservices/cloud services |
| `load_rust_loadout()` | 149 | Rust, Analysis, Git, Shell, Database, Profiling | Memory-safe systems programming |
| `load_ruby_loadout()` | 149 | Ruby, Analysis, Git, Shell, Database, Profiling | Ruby on Rails web apps |
| `load_swift_loadout()` | 132 | Analysis, Git, Shell, Database, Profiling | iOS/macOS development |
| `load_kotlin_loadout()` | 132 | Analysis, Git, Shell, Database, Profiling | Android/JVM applications |

### 🛠️ Utility Functions

| Function | Description |
|----------|-------------|
| `merge_tool_lists(*args)` | Merge multiple tool lists and individual functions with automatic deduplication |
| `get_tool_info(tool)` | Inspect a tool's name, docstring, signature, and parameters |
| `list_all_available_tools()` | Get all tools organized by category with metadata |

## Quick Start

```python
import coding_open_agent_tools as coat

# Option 1: Load all 461 functions (recommended for general-purpose agents)
all_tools = coat.load_all_tools()

# Option 2: Load language-specific loadouts (recommended for focused agents)
python_tools = coat.load_python_loadout()        # 171 functions - Python development
javascript_tools = coat.load_javascript_loadout()  # 161 functions - JS/TS development
java_tools = coat.load_java_loadout()            # 149 functions - Java development
go_tools = coat.load_go_loadout()                # 149 functions - Go development
rust_tools = coat.load_rust_loadout()            # 149 functions - Rust development

# Option 3: Load individual modules
analysis_tools = coat.load_all_analysis_tools()  # 14 functions
config_tools = coat.load_all_config_tools()      # 42 functions
git_tools = coat.load_all_git_tools()            # 79 functions
python_tools = coat.load_all_python_tools()      # 32 functions

# Merge custom tools with built-in tools
def my_custom_tool(x: str) -> dict[str, str]:
    return {"result": x}

combined_tools = coat.merge_tool_lists(
    coat.load_python_loadout(),  # 171 Python-focused tools
    my_custom_tool  # Add individual functions
)

# Inspect tool information
tool_info = coat.get_tool_info(my_custom_tool)
print(f"Tool: {tool_info['name']}, Params: {tool_info['parameters']}")

# Use with any agent framework
from google.adk.agents import Agent

# General-purpose code agent
general_agent = Agent(
    tools=coat.load_all_tools(),
    name="CodeAnalyzer",
    instruction="Analyze code quality and performance"
)

# Python-focused agent (more efficient token usage)
python_agent = Agent(
    tools=coat.load_python_loadout(),
    name="PythonDeveloper",
    instruction="Develop and analyze Python code with quality checks"
)

# Example: Analyze code complexity
from coding_open_agent_tools import analysis

complexity = analysis.calculate_complexity("/path/to/code.py")
print(f"Cyclomatic complexity: {complexity['total_complexity']}")

# Example: Check git status
from coding_open_agent_tools import git

status = git.get_git_status("/path/to/repo")
print(f"Modified files: {len(status['modified'])}")

# Example: Use navigation tools to save tokens (NEW in v0.4.4)
from coding_open_agent_tools import python

# Get overview without reading entire file (85-90% token savings)
overview = python.get_python_module_overview(source_code)
print(f"Functions: {overview['function_names']}")

# Get line numbers for targeted reading (90-95% token savings)
lines = python.get_python_function_line_numbers(source_code, "process_data")
# Then use: Read(file_path="module.py", offset=int(lines['start_line']), limit=int(lines['end_line'])-int(lines['start_line']))

# Example: Config file operations (NEW in v0.9.0)
from coding_open_agent_tools import config

# Parse and validate .env files
env_result = config.parse_env_file(".env content here")
print(f"Variables: {env_result['variable_count']}")

# Extract specific values from YAML using dot notation
yaml_value = config.extract_yaml_value(yaml_content, "database.host")
print(f"Database host: {yaml_value['value']}")

# Security: Check gitignore for missing patterns
security = config.check_gitignore_security(gitignore_content)
print(f"Security status: {security['is_secure']}")
```

## Development Status

**Current Version**: v0.10.0
**Status**: Active Development
**Focus**: Token-efficient code analysis and navigation for AI agents (461 functions across 17 modules)

## Quality Standards

- **Code Quality**: 100% ruff compliance (linting + formatting)
- **Type Safety**: 100% mypy compliance
- **Test Coverage**: Minimum 80% for all modules
- **Google ADK Compliance**: All function signatures compatible with agent frameworks
- **Security**: All generated code scanned for vulnerabilities

## Contributing (Future)

Contributions will be welcome once the initial implementation is complete. We will provide:
- Contribution guidelines
- Code of conduct
- Development setup instructions
- Testing requirements

## License

MIT License (same as basic-open-agent-tools)

## Related Projects

- **[basic-open-agent-tools](https://github.com/Open-Agent-Tools/basic-open-agent-tools)** - Foundational toolkit for AI agents
- **[Google ADK](https://github.com/google/agent-development-kit)** - Agent Development Kit
- **[Strands Agents](https://github.com/strands-ai/strands)** - Agent framework

---

**Version**: v0.10.0
**Last Updated**: 2025-11-24
