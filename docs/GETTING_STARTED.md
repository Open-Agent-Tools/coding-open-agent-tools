# Getting Started with Coding Open Agent Tools

Quick start guide to begin using coding-open-agent-tools in your AI agent projects.

## What is This?

**coding-open-agent-tools** is a Python library providing 286 validators, parsers, and analysis tools specifically designed to save AI agents' tokens by performing deterministic operations that agents waste tokens on.

**Key Philosophy:** Build what agents waste tokens on, avoid what they do well.

## Installation

### Basic Installation

```bash
# Install from PyPI
pip install coding-open-agent-tools

# Or with UV
uv add coding-open-agent-tools
```

### Optional Dependencies

```bash
# Enhanced security scanning (detect-secrets)
pip install coding-open-agent-tools[enhanced-security]

# Enhanced code navigation (tree-sitter)
pip install coding-open-agent-tools[enhanced-navigation]

# All optional features
pip install coding-open-agent-tools[all]
```

### Development Installation

```bash
git clone https://github.com/Open-Agent-Tools/coding-open-agent-tools.git
cd coding-open-agent-tools
pip install -e ".[dev]"
```

## Quick Start Examples

### 1. Validate Python Code (Prevent Retry Loops)

```python
from coding_open_agent_tools.python import validators

# Validate syntax before execution
code = """
def calculate_total(items):
    return sum(items)
"""

result = validators.validate_python_syntax(code)
print(f"Valid: {result['is_valid']}")  # "true"

# Invalid code example
invalid_code = "def broken( print('missing closing paren')"
result = validators.validate_python_syntax(invalid_code)
print(f"Valid: {result['is_valid']}")  # "false"
print(f"Error: {result['error_message']}")
print(f"Line: {result['line_number']}")
```

**Token Savings:** 90-95% (prevents retry loops)

### 2. Navigate Code Without Reading Full Files

```python
from coding_open_agent_tools.python import navigation

# Get overview without reading entire file
source_code = open("my_module.py").read()

# List all functions (quick discovery)
functions = navigation.list_python_functions(source_code)
print(f"Functions: {functions['functions']}")
print(f"Count: {functions['count']}")

# Get specific function signature
sig = navigation.get_python_function_signature(source_code, "calculate_total")
print(f"Signature: {sig['signature']}")

# Get line numbers for targeted reading
lines = navigation.get_python_function_line_numbers(source_code, "calculate_total")
print(f"Lines {lines['start_line']}-{lines['end_line']}")
# Now use Read tool: Read(file_path="my_module.py", offset=start, limit=count)
```

**Token Savings:** 70-95% (targeted extraction vs full file reading)

### 3. Check Git Repository Health

```python
from coding_open_agent_tools.git import health

repo_path = "/path/to/your/repo"

# Get comprehensive health metrics
metrics = health.get_repository_metrics(repo_path)
print(f"Health score: {metrics['health_score']}/100")
print(f"Total commits: {metrics['total_commits']}")
print(f"Repository size: {metrics['repo_size']}")

# Check if garbage collection is needed
gc_check = health.check_gc_needed(repo_path)
if gc_check['gc_needed'] == 'true':
    print(f"Recommendations: {gc_check['recommendations']}")

# Find large files
large_files = health.find_large_files(repo_path, "10")  # > 10MB
print(f"Large files: {large_files['large_files_count']}")
```

**Token Savings:** 70-85% (structured metrics vs parsing git output)

### 4. Scan for Secrets (Security)

```python
from coding_open_agent_tools.analysis import secrets

code_with_secrets = """
API_KEY = "sk_live_1234567890abcdef"
DATABASE_URL = "postgresql://admin:password@localhost/db"
"""

# Scan for exposed secrets
result = secrets.scan_for_secrets(code_with_secrets)
print(f"Secrets found: {result['secret_count']}")

if result['secret_count'] != '0':
    for secret in eval(result['secrets_found']):
        print(f"  Line {secret['line']}: {secret['type']}")

# Scan entire directory
dir_result = secrets.scan_directory_for_secrets("/path/to/project")
print(f"Files with secrets: {dir_result['files_with_secrets']}")
```

**Token Savings:** 85-90% (structured detection vs manual analysis)

### 5. Parse Configuration Files

```python
from coding_open_agent_tools.config import extractors, parsers

# Extract from YAML using dot notation
yaml_content = """
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
"""

db_host = extractors.extract_yaml_value(yaml_content, "database.host")
print(f"Database host: {db_host['value']}")

db_user = extractors.extract_yaml_value(yaml_content, "database.credentials.username")
print(f"Username: {db_user['value']}")

# Parse .env file
env_content = """
DATABASE_URL=postgresql://localhost:5432/mydb
API_KEY=secret
"""

env_result = parsers.parse_env_file(env_content)
print(f"Variables: {env_result['variable_count']}")
```

**Token Savings:** 80-90% (structured extraction vs manual parsing)

## Loading Tools for Agent Frameworks

### Load All Tools (286 Functions)

```python
import coding_open_agent_tools as coat

# Load everything
all_tools = coat.load_all_tools()
```

### Load by Category

```python
# Load specific modules
analysis_tools = coat.load_all_analysis_tools()      # 14 functions
config_tools = coat.load_all_config_tools()          # 28 functions
git_tools = coat.load_all_git_tools()                # 79 functions
python_tools = coat.load_all_python_tools()          # 32 functions
shell_tools = coat.load_all_shell_tools()            # 13 functions
database_tools = coat.load_all_database_tools()      # 18 functions
profiling_tools = coat.load_all_profiling_tools()    # 8 functions
quality_tools = coat.load_all_quality_tools()        # 7 functions
```

### Merge Custom Tools

```python
# Combine built-in and custom tools
def my_custom_tool(x: str) -> dict[str, str]:
    return {"result": x}

combined_tools = coat.merge_tool_lists(
    coat.load_all_analysis_tools(),
    coat.load_all_git_tools(),
    my_custom_tool
)
```

## Framework Integration

### Strands Framework

```python
from strands import Agent
import coding_open_agent_tools as coat

agent = Agent(
    name="CodeAnalyzer",
    tools=coat.load_all_tools(),
    instruction="Analyze code quality and security"
)
```

### Google ADK

```python
from google.adk.agents import Agent
import coding_open_agent_tools as coat

agent = Agent(
    tools=coat.load_all_python_tools() + coat.load_all_git_tools(),
    name="DevAssistant",
)
```

### LangGraph

```python
from langgraph.prebuilt import ToolNode
import coding_open_agent_tools as coat

tool_node = ToolNode(tools=coat.load_all_tools())
```

## Common Patterns

### Pattern 1: Validate Before Execute

Always validate generated code before execution:

```python
from coding_open_agent_tools.python import validators

# Agent generates code
generated_code = agent_generate_function()

# Validate before executing
result = validators.validate_python_syntax(generated_code)

if result['is_valid'] == 'true':
    # Safe to execute
    exec(generated_code)
else:
    # Fix based on error
    print(f"Error at line {result['line_number']}: {result['error_message']}")
```

### Pattern 2: Navigate Before Reading

Use navigation to find relevant code before reading full files:

```python
from coding_open_agent_tools.python import navigation

# 1. Get overview (small token cost)
overview = navigation.get_python_module_overview(source_code)

# 2. Identify target function
if "process_data" in overview['function_names']:
    # 3. Get line numbers
    lines = navigation.get_python_function_line_numbers(source_code, "process_data")

    # 4. Read only that section (targeted, efficient)
    # Use Read tool with offset/limit based on lines
```

### Pattern 3: Security First

Scan for secrets before committing:

```python
from coding_open_agent_tools.analysis import secrets

# Before git commit
new_files = get_staged_files()

for file_path in new_files:
    content = open(file_path).read()
    result = secrets.scan_for_secrets(content)

    if result['secret_count'] != '0':
        print(f"⚠️  Secrets found in {file_path}")
        # Handle secrets before committing
```

### Pattern 4: Configuration Management

Extract config values without parsing full files:

```python
from coding_open_agent_tools.config import extractors

# Direct value extraction (very efficient)
db_host = extractors.extract_yaml_value(config, "database.host")
api_key = extractors.extract_yaml_value(config, "api.credentials.key")

# No need to parse entire YAML structure
```

### Pattern 5: Repository Monitoring

Regular health checks for git repositories:

```python
from coding_open_agent_tools.git import health

# Periodic health check
metrics = health.get_repository_metrics(repo_path)

if int(metrics['health_score']) < 70:
    print("⚠️  Repository health issues detected")
    # Run garbage collection
    # Clean up large files
    # Fix detected issues
```

## Module Overview

### Core Modules (199 functions)

| Module | Functions | Primary Use Cases |
|--------|-----------|-------------------|
| `git` | 79 | Repository health, security, metrics |
| `python` | 32 | Navigation, validation, analysis |
| `config` | 28 | Config parsing, extraction, validation |
| `database` | 18 | SQLite operations, query building |
| `analysis` | 14 | AST parsing, complexity, secrets |
| `shell` | 13 | Shell validation, security |
| `profiling` | 8 | Performance analysis |
| `quality` | 7 | Code quality metrics |

### Language Navigation (87 functions)

7 languages with 17 navigation functions each:
- C++, C#, Go, Java, JavaScript/TypeScript, Ruby, Rust

## Token Savings Summary

| Operation | Without Tools | With Tools | Savings |
|-----------|--------------|------------|---------|
| Syntax validation | 1700 tokens | 950 tokens | 44% |
| Code navigation | 1700 tokens | 180 tokens | 89% |
| Git health check | 1000 tokens | 200 tokens | 80% |
| Security scanning | 8500 tokens | 600 tokens | 93% |
| Config parsing | 1000 tokens | 80 tokens | 92% |

**Average: 80-90% token savings across common workflows**

## Next Steps

1. **Try the Examples**
   - Run [example scripts](examples/) to see tools in action
   - Each example includes token savings analysis

2. **Read the Documentation**
   - [Architecture](../ARCHITECTURE.md) - Design patterns and philosophy
   - [Contributing](../CONTRIBUTING.md) - Add your own tools
   - [API Reference](DOCUMENTATION_INDEX.md) - Complete function reference

3. **Integrate with Your Agent**
   - Choose your framework (Strands, Google ADK, LangGraph)
   - Load relevant tool categories
   - Start saving tokens!

4. **Join the Community**
   - GitHub Issues - Report bugs or request features
   - GitHub Discussions - Ask questions, share ideas
   - Pull Requests - Contribute improvements

## Troubleshooting

### Import Errors

```python
# If strands not installed, decorator is no-op
# Package works without strands!
from coding_open_agent_tools.python import validators
```

### Type Errors with mypy

All functions return `dict[str, str]` for Google ADK compatibility:
```python
result = some_function()
count = int(result['count'])  # Convert string to int
is_valid = result['is_valid'] == 'true'  # Compare string
```

### File Not Found

Always use absolute paths:
```python
import os
file_path = os.path.abspath("my_file.py")
result = some_function(file_path)
```

## Support

- **Documentation:** [docs/DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- **Examples:** [docs/examples/](examples/)
- **Issues:** [GitHub Issues](https://github.com/Open-Agent-Tools/coding-open-agent-tools/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Open-Agent-Tools/coding-open-agent-tools/discussions)

## Resources

- [GitHub Repository](https://github.com/Open-Agent-Tools/coding-open-agent-tools)
- [PyPI Package](https://pypi.org/project/coding-open-agent-tools/)
- [basic-open-agent-tools](https://github.com/Open-Agent-Tools/basic-open-agent-tools) - Foundation layer
- [CHANGELOG](../CHANGELOG.md) - Release history

---

**Ready to save tokens?** Start with the [examples](examples/) and integrate with your agent framework!
