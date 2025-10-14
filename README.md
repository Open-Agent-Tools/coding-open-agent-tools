# Coding Open Agent Tools

**Advanced code generation and shell scripting toolkit for AI agents**

This project provides specialized code generation, script creation, and development automation capabilities designed specifically for AI agents. It complements [basic-open-agent-tools](https://github.com/yourusername/basic-open-agent-tools) by building higher-level coding abstractions on top of its foundational utilities.

## Project Status

✅ **v0.1.0-beta Released** - First beta with 39 migrated developer-focused tools from basic-open-agent-tools.

**What's Available Now:**
- ✅ Analysis Module (14 functions) - AST parsing, complexity analysis, imports, secrets
- ✅ Git Module (9 functions) - Read-only git operations
- ✅ Profiling Module (8 functions) - Performance and memory profiling
- ✅ Quality Module (7 functions) - Static analysis parsers

**Coming Next:**
- 🚧 Shell script generation module (planned for v0.2.0)
- 🚧 Python code generation module (planned for v0.3.0)

See [docs/PRD](./docs/PRD/) for detailed requirements and specifications.

## Relationship to Basic Open Agent Tools

### Division of Responsibilities

**[basic-open-agent-tools](https://github.com/Open-Agent-Tools/basic-open-agent-tools)** (Foundation Layer):
- Core file system operations
- Text and data processing
- Document format handling (PDF, Word, Excel, PowerPoint, etc.)
- System utilities and network operations
- General-purpose, low-level operations
- 200+ foundational agent tools

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

## Planned Modules (v0.1.0)

### 1. Shell Script Generation Module (~15 functions)
Generate, validate, and analyze shell scripts for deployment, CI/CD, and system administration:

- **Generation**: Bash scripts, systemd services, cron jobs, Docker entrypoints, CI pipelines
- **Validation**: Syntax checking, dependency analysis, security scanning
- **Utilities**: Argument escaping, permission handling, documentation generation

**Example**:
```python
import coding_open_agent_tools as coat

script = coat.generate_bash_script(
    commands=["cd /app", "git pull", "npm install", "npm run build"],
    variables={"NODE_ENV": "production"},
    add_error_handling=True,
    add_logging=True,
    set_flags=["u", "o pipefail"]
)

# Validate before using
validation = coat.validate_shell_syntax(script, "bash")
security = coat.analyze_shell_security(script)
```

### 2. Python Code Generation Module (~18 functions)
Generate high-quality Python code with type hints, docstrings, and tests:

- **Functions**: Sync/async functions, lambdas with full type annotations
- **Classes**: Regular classes, dataclasses, Pydantic models, exceptions
- **Documentation**: Google/NumPy/Sphinx docstrings, module headers
- **Tests**: Pytest skeletons, fixtures, test classes
- **Projects**: Complete project scaffolding, pyproject.toml, README, .gitignore

**Example**:
```python
import coding_open_agent_tools as coat

func = coat.generate_python_function(
    name="process_data",
    parameters=[
        {"name": "data", "type": "list[dict[str, str]]", "description": "Input data"},
        {"name": "operation", "type": "str", "description": "Operation type"}
    ],
    return_type="dict[str, str]",
    description="Process data with specified operation",
    docstring_style="google",
    add_type_checking=True,
    add_error_handling=True,
    raises=[
        {"type": "TypeError", "description": "If parameters are wrong type"},
        {"type": "ValueError", "description": "If operation is not supported"}
    ]
)
```

## Design Philosophy

### Same Principles as Basic Tools

1. **Minimal Dependencies**: Prefer stdlib, add dependencies only when substantial value added
2. **Google ADK Compliance**: All functions use JSON-serializable types, no default parameters
3. **Local Operations**: No HTTP/API calls, focus on local development tasks
4. **Type Safety**: Full mypy compliance with comprehensive type hints
5. **High Quality**: 100% ruff compliance, comprehensive testing (80%+ coverage)
6. **Agent-First Design**: Functions designed for LLM comprehension and use

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

## Documentation

- **[Product Requirements Documents](./docs/PRD/)**: Detailed specifications
  - [Project Overview](./docs/PRD/01-project-overview.md)
  - [Shell Module PRD](./docs/PRD/02-shell-module-prd.md)
  - [Codegen Module PRD](./docs/PRD/03-codegen-module-prd.md)

## Installation

```bash
# Install latest beta from source
git clone https://github.com/Open-Agent-Tools/coding-open-agent-tools.git
cd coding-open-agent-tools
pip install -e ".[dev]"

# Or install specific version (when published to PyPI)
pip install coding-open-agent-tools==0.1.0-beta

# This will automatically install basic-open-agent-tools as a dependency
```

## Quick Start

```python
import coding_open_agent_tools as coat

# Load all 39 functions
all_tools = coat.load_all_tools()

# Or load by category
analysis_tools = coat.load_all_analysis_tools()  # 14 functions
git_tools = coat.load_all_git_tools()            # 9 functions
profiling_tools = coat.load_all_profiling_tools()  # 8 functions
quality_tools = coat.load_all_quality_tools()    # 7 functions

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

**Current Phase**: Planning and Requirements
**Next Steps**:
1. Initialize repository structure
2. Set up development environment
3. Implement Shell Script Generation Module (v0.1.0)
4. Implement Python Code Generation Module (v0.2.0)

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

**Status**: 🚧 Planning Phase
**Version**: 0.0.0 (not yet released)
**Last Updated**: 2025-10-14
