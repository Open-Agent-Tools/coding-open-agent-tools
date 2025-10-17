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

## 🆕 What's New in v0.4.3

📚 **Helper Function Documentation**: Added comprehensive documentation for all 11 helper functions with usage examples and `__all__` export

### Recent Updates

**v0.4.2** - Enhanced diff preview from 20 to 50 lines for better context

**v0.4.0** - Added database module with SQLite operations and safe query building

**v0.3.0** - Python module for syntax validation, type checking, and import analysis

**v0.2.0** - Shell module with validation, security scanning, and escaping utilities

**v0.1.0-beta** - Initial release with 39 migrated developer-focused tools from basic-open-agent-tools

## Available Tools

**7 modules** with **154 total functions** — all with `@strands_tool` decorator and Google ADK compatible signatures.

### 📊 Complete Module Breakdown

| Module | Functions | Description |
|--------|-----------|-------------|
| **Code Analysis** | | |
| `git` | 79 | Repository operations, history, commits, branches, tags, hooks, workflows |
| `python` | 15 | Syntax validation, type checking, import analysis, AST parsing |
| `analysis` | 14 | Code complexity, AST parsing, import tracking, secret detection |
| **Data & Storage** | | |
| `database` | 18 | SQLite operations, safe query building, schema inspection |
| **Development Tools** | | |
| `shell` | 13 | Shell validation, security scanning, argument escaping |
| `profiling` | 8 | Performance profiling, memory analysis, execution timing |
| `quality` | 7 | Static analysis parsers, linting tool integration |
| **TOTAL** | **154** | |

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

The package provides 11 helper functions for tool management and introspection:

### Tool Loading Functions

- **`load_all_tools()`** - Load all 154 functions from all modules
- **`load_all_analysis_tools()`** - Load 14 code analysis functions
- **`load_all_git_tools()`** - Load 79 git operation functions
- **`load_all_profiling_tools()`** - Load 8 profiling functions
- **`load_all_quality_tools()`** - Load 7 static analysis functions
- **`load_all_shell_tools()`** - Load 13 shell validation functions
- **`load_all_python_tools()`** - Load 15 Python validation functions
- **`load_all_database_tools()`** - Load 18 SQLite operation functions

### Tool Management Functions

- **`merge_tool_lists(*args)`** - Merge multiple tool lists and individual functions with automatic deduplication
- **`get_tool_info(tool)`** - Inspect a tool's name, docstring, signature, and parameters
- **`list_all_available_tools()`** - Get all tools organized by category with metadata

## Quick Start

```python
import coding_open_agent_tools as coat

# Load all 154 functions
all_tools = coat.load_all_tools()

# Or load by category
analysis_tools = coat.load_all_analysis_tools()  # 14 functions
git_tools = coat.load_all_git_tools()            # 79 functions
profiling_tools = coat.load_all_profiling_tools()  # 8 functions
quality_tools = coat.load_all_quality_tools()    # 7 functions
shell_tools = coat.load_all_shell_tools()        # 13 functions
python_tools = coat.load_all_python_tools()      # 15 functions
database_tools = coat.load_all_database_tools()  # 18 functions

# Merge custom tools with built-in tools
def my_custom_tool(x: str) -> dict[str, str]:
    return {"result": x}

combined_tools = coat.merge_tool_lists(
    coat.load_all_analysis_tools(),
    coat.load_all_git_tools(),
    my_custom_tool  # Add individual functions
)

# Inspect tool information
tool_info = coat.get_tool_info(my_custom_tool)
print(f"Tool: {tool_info['name']}, Params: {tool_info['parameters']}")

# List all available tools by category
all_available = coat.list_all_available_tools()
print(f"Categories: {list(all_available.keys())}")

# Use with any agent framework
from google.adk.agents import Agent

agent = Agent(
    tools=all_tools,
    name="CodeAnalyzer",
    instruction="Analyze code quality and performance"
)

# Example: Analyze code complexity
from coding_open_agent_tools import analysis

complexity = analysis.calculate_complexity("/path/to/code.py")
print(f"Cyclomatic complexity: {complexity['total_complexity']}")

# Example: Check git status
from coding_open_agent_tools import git

status = git.get_git_status("/path/to/repo")
print(f"Modified files: {len(status['modified'])}")
```

## Development Status

**Current Version**: v0.4.3
**Status**: Active Development
**Focus**: Code validation and analysis tools for AI agents

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

**Version**: v0.4.3
**Last Updated**: 2025-10-17
