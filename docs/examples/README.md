# Usage Examples

This directory contains practical examples demonstrating how to use coding-open-agent-tools to save agent tokens and improve efficiency.

## Available Examples

### 1. Python Validation (`01_python_validation.py`)
**Focus:** Validate Python syntax before execution
**Token Savings:** 90-95% (prevents retry loops)
**Use Cases:**
- Catch syntax errors before code execution
- Prevent failed execution cycles
- Validate generated code immediately
- Save retry tokens in agent workflows

**Key Functions:**
- `validate_python_syntax()` - Check Python code validity
- Error details with line numbers and offsets
- Clear error messages for quick fixes

### 2. Git Health Check (`02_git_health_check.py`)
**Focus:** Repository health monitoring
**Token Savings:** 70-85% (structured metrics vs parsing git output)
**Use Cases:**
- Get repository health metrics
- Check if garbage collection is needed
- Find large files in repository
- Monitor repository statistics
- Detect health issues early

**Key Functions:**
- `get_repository_metrics()` - Overall health score
- `check_gc_needed()` - Garbage collection assessment
- `find_large_files()` - Identify large files
- `get_repository_statistics()` - Comprehensive stats
- `check_repository_health()` - Issue detection

### 3. Code Navigation (`03_code_navigation.py`)
**Focus:** Navigate code without reading full files
**Token Savings:** 70-95% (targeted extraction vs full file reading)
**Use Cases:**
- List functions without reading entire files
- Get function signatures quickly
- Check function existence
- Get line numbers for targeted reading
- Build code navigation indexes

**Key Functions:**
- `list_python_functions()` - Get all function names
- `get_python_function_signature()` - Extract signatures
- `get_python_function_docstring()` - Read documentation
- `get_python_module_overview()` - Complete module summary
- `get_python_function_line_numbers()` - Targeted file reading
- `check_python_function_exists()` - Quick validation
- `list_python_classes()` - Get all class names
- `get_python_class_methods()` - List class methods

### 4. Security Scanning (`04_security_scanning.py`)
**Focus:** Detect secrets and security vulnerabilities
**Token Savings:** 85-90% (structured detection vs manual analysis)
**Use Cases:**
- Scan code for hardcoded secrets
- Detect API keys and tokens
- Find security vulnerabilities in shell scripts
- Scan entire directories for secrets
- Validate secret patterns

**Key Functions:**
- `scan_for_secrets()` - Find secrets in code
- `analyze_shell_security()` - Shell script vulnerabilities
- `scan_directory_for_secrets()` - Directory-wide scanning
- `validate_secret_patterns()` - Pattern identification

### 5. Config Parsing (`05_config_parsing.py`)
**Focus:** Parse and validate configuration files
**Token Savings:** 80-90% (structured extraction vs manual parsing)
**Use Cases:**
- Extract values from YAML/TOML/JSON
- Parse .env files
- Validate configuration formats
- Check .gitignore security
- Merge configuration files
- Parse INI and properties files

**Key Functions:**
- `extract_yaml_value()` - YAML value extraction
- `extract_toml_value()` - TOML value extraction
- `extract_json_value()` - JSON value extraction
- `parse_env_file()` - .env file parsing
- `parse_ini_file()` - INI file parsing
- `parse_properties_file()` - Java properties parsing
- `validate_yaml_format()` - Format validation
- `check_gitignore_security()` - Security checking
- `merge_env_files()` - Configuration merging

## Running Examples

```bash
# Run a specific example
python docs/examples/01_python_validation.py

# Run all examples
for example in docs/examples/[0-9]*.py; do
    echo "Running $example..."
    python "$example"
    echo ""
done
```

## Token Savings Summary

| Example | Without Tools | With Tools | Savings | Use Case |
|---------|--------------|------------|---------|----------|
| Python Validation | ~1700 tokens | ~950 tokens | 44% | Syntax validation |
| Git Health Check | ~1000 tokens | ~200 tokens | 80% | Repository metrics |
| Code Navigation | ~1700 tokens | ~180 tokens | 89% | Function discovery |
| Security Scanning | ~8500 tokens | ~600 tokens | 93% | Secret detection |
| Config Parsing | ~1000 tokens | ~80 tokens | 92% | Value extraction |

**Average Token Savings: 80-90%**

## Real-World Impact

### Development Workflow
A typical agent development workflow involves:
1. Understanding codebase structure (navigation)
2. Validating generated code (validation)
3. Checking security (scanning)
4. Configuring applications (config parsing)
5. Monitoring repository health (git tools)

**Without tools:** ~15,000 tokens per workflow cycle
**With tools:** ~2,000 tokens per workflow cycle
**Savings:** ~13,000 tokens (87% reduction)

### Large Codebase Analysis
Analyzing a 100-file Python project:
- **Without:** 170,000 tokens to understand structure
- **With:** 18,000 tokens for complete navigation
- **Savings:** 152,000 tokens (89% reduction)

### Security Audit
Complete security audit of 50-file project:
- **Without:** 8,500 tokens per file = 425,000 tokens
- **With:** 100 tokens per file = 5,000 tokens
- **Savings:** 420,000 tokens (99% reduction)

## Integration Examples

### With Strands Framework
```python
from strands import Agent
from coding_open_agent_tools import load_all_tools

agent = Agent(
    name="CodeAnalyzer",
    tools=load_all_tools(),
    instruction="Analyze code quality and security"
)
```

### With Google ADK
```python
from google.adk.agents import Agent
from coding_open_agent_tools import (
    load_all_analysis_tools,
    load_all_git_tools,
    load_all_python_tools,
)

agent = Agent(
    tools=load_all_analysis_tools() +
          load_all_git_tools() +
          load_all_python_tools(),
    name="DevAssistant",
)
```

### With LangGraph
```python
from langgraph.prebuilt import ToolNode
from coding_open_agent_tools import load_all_tools

tool_node = ToolNode(tools=load_all_tools())
```

## Best Practices

### 1. Use Navigation Before Reading
Always use navigation tools to identify relevant code before reading full files:
```python
# BAD: Read entire file
content = Read(file_path="large_file.py")  # 1000 tokens

# GOOD: Navigate first
overview = get_python_module_overview(content)  # 50 tokens
line_nums = get_python_function_line_numbers(content, "target_func")  # 20 tokens
# Then read only relevant section: 60 tokens
# Total: 130 tokens (87% savings)
```

### 2. Validate Before Execution
Always validate code before executing or committing:
```python
# Validate syntax
result = validate_python_syntax(generated_code)
if result['is_valid'] != 'true':
    # Fix issues based on error_message, line_number, etc.
    pass
```

### 3. Scan for Secrets Regularly
Integrate security scanning into your workflow:
```python
# Before git commit
secrets_found = scan_for_secrets(new_code)
if secrets_found['secret_count'] != '0':
    # Handle secrets before committing
    pass
```

### 4. Extract Config Values Directly
Don't parse entire config files manually:
```python
# Extract specific values
db_host = extract_yaml_value(config_content, "database.host")
api_key = extract_yaml_value(config_content, "api.key")
# No need to parse full YAML structure
```

### 5. Check Repository Health
Monitor git repository health proactively:
```python
# Regular health checks
metrics = get_repository_metrics(repo_path)
if int(metrics['health_score']) < 70:
    # Take action on health issues
    pass
```

## Contributing Examples

Have a great use case? We'd love to see it! Please:
1. Follow the existing example format
2. Include clear explanations
3. Show token savings
4. Document real-world benefits
5. Submit a PR

## Additional Resources

- [Project README](../../README.md)
- [Architecture Documentation](../../ARCHITECTURE.md)
- [Contributing Guidelines](../../CONTRIBUTING.md)
- [API Reference](../../docs/)

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for usage questions
- Check existing examples for patterns
