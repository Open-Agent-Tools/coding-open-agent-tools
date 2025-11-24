"""Example: Configuration file parsing and validation.

Demonstrates parsing and extracting values from various configuration
formats (YAML, TOML, JSON, .env, INI, properties, XML).

Token Savings: 80-90% (structured extraction vs manual parsing)
"""

from coding_open_agent_tools.config import (
    env_parser,
    extractors,
    parsers,
    security,
    validators,
)

# Example 1: Parse and extract from YAML
print("=" * 60)
print("Example 1: Extract values from YAML using dot notation")
print("=" * 60)

yaml_content = """
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret123

api:
  endpoint: https://api.example.com
  timeout: 30
  retries: 3

features:
  - authentication
  - logging
  - caching
"""

# Extract nested values using dot notation
db_host = extractors.extract_yaml_value(yaml_content, "database.host")
print(f"Database host: {db_host['value']}")
print(f"Found: {db_host['found']}")

db_user = extractors.extract_yaml_value(yaml_content, "database.credentials.username")
print(f"Database username: {db_user['value']}")

api_endpoint = extractors.extract_yaml_value(yaml_content, "api.endpoint")
print(f"API endpoint: {api_endpoint['value']}")
print()

# Example 2: Parse .env file
print("=" * 60)
print("Example 2: Parse .env file")
print("=" * 60)

env_content = """
# Database configuration
DATABASE_URL=postgresql://localhost:5432/mydb
DATABASE_USER=admin
DATABASE_PASSWORD=secret

# API configuration
API_KEY=sk_live_1234567890
API_ENDPOINT=https://api.example.com
API_TIMEOUT=30

# Feature flags
FEATURE_LOGGING=true
FEATURE_CACHING=false
DEBUG=true
"""

env_result = env_parser.parse_env_file(env_content)
print(f"Variables found: {env_result['variable_count']}")
print(f"Has errors: {env_result['has_errors']}")
print("\nVariables:")
for var in eval(env_result["variables"])[:5]:  # Show first 5
    print(f"  {var['key']} = {var['value']}")
print()

# Example 3: Extract from TOML
print("=" * 60)
print("Example 3: Extract values from TOML")
print("=" * 60)

toml_content = """
[database]
host = "localhost"
port = 5432

[database.pool]
min_connections = 5
max_connections = 20

[api]
endpoint = "https://api.example.com"
timeout = 30
"""

toml_host = extractors.extract_toml_value(toml_content, "database.host")
print(f"Database host: {toml_host['value']}")

toml_pool = extractors.extract_toml_value(toml_content, "database.pool.max_connections")
print(f"Max connections: {toml_pool['value']}")
print()

# Example 4: Parse INI file
print("=" * 60)
print("Example 4: Parse INI configuration file")
print("=" * 60)

ini_content = """
[database]
host = localhost
port = 5432
user = admin

[logging]
level = INFO
format = json
output = /var/log/app.log

[cache]
enabled = true
ttl = 3600
"""

ini_result = parsers.parse_ini_file(ini_content)
print(f"Sections found: {ini_result['section_count']}")
print(f"Total settings: {ini_result['total_settings']}")
print("\nSections:")
for section in eval(ini_result["sections"])[:2]:
    print(f"  [{section['section']}]")
    for key, value in eval(section["settings"]).items():
        print(f"    {key} = {value}")
print()

# Example 5: Parse Java properties file
print("=" * 60)
print("Example 5: Parse Java properties file")
print("=" * 60)

properties_content = """
# Application configuration
app.name=MyApplication
app.version=1.0.0
app.debug=true

# Database settings
db.url=jdbc:postgresql://localhost:5432/mydb
db.driver=org.postgresql.Driver
db.pool.size=10
"""

props_result = parsers.parse_properties_file(properties_content)
print(f"Properties found: {props_result['property_count']}")
print("\nProperties:")
for prop in eval(props_result["properties"])[:5]:
    print(f"  {prop['key']} = {prop['value']}")
print()

# Example 6: Validate configuration formats
print("=" * 60)
print("Example 6: Validate configuration file formats")
print("=" * 60)

# Valid YAML
valid_yaml = validators.validate_yaml_format(yaml_content)
print(f"YAML valid: {valid_yaml['is_valid']}")

# Invalid YAML
invalid_yaml_content = """
database:
  host: localhost
    port: 5432  # Wrong indentation
"""
invalid_yaml = validators.validate_yaml_format(invalid_yaml_content)
print(f"Invalid YAML: {invalid_yaml['is_valid']}")
print(f"Error: {invalid_yaml['error_message'][:50]}...")
print()

# Example 7: Check .gitignore security
print("=" * 60)
print("Example 7: Scan .gitignore for security issues")
print("=" * 60)

gitignore_content = """
# Python
__pycache__/
*.py[cod]
*.so

# Virtual environments
venv/
.venv/

# IDE
.vscode/
.idea/

# Note: Missing critical security patterns!
# Should include: .env, secrets.json, credentials.yml, etc.
"""

security_check = security.check_gitignore_security(gitignore_content)
print(f"Is secure: {security_check['is_secure']}")
print(f"Missing patterns: {security_check['missing_pattern_count']}")
print("\nMissing critical patterns:")
for pattern in eval(security_check["missing_patterns"])[:5]:
    print(f"  {pattern['pattern']} - {pattern['reason']}")
print()

# Example 8: Merge .env files
print("=" * 60)
print("Example 8: Merge multiple .env files")
print("=" * 60)

base_env = """
DATABASE_URL=postgresql://localhost:5432/mydb
API_KEY=base_key
DEBUG=false
"""

override_env = """
API_KEY=override_key
NEW_SETTING=value
"""

merged = env_parser.merge_env_files(base_env, override_env)
print(f"Merged variables: {merged['merged_count']}")
print(f"Conflicts: {merged['conflict_count']}")
print("\nMerged content preview:")
print(merged["merged_content"][:200])
print()

# Why this saves tokens:
print("=" * 60)
print("TOKEN SAVINGS BREAKDOWN")
print("=" * 60)
print("""
Without config parsing tools:
1. Agent reads config file (200 tokens)
2. Agent manually parses format (300 tokens reasoning)
3. Agent extracts specific values (200 tokens)
4. Agent validates format (100 tokens)
5. Agent checks for security issues (200 tokens)
6. Total: ~1000 tokens

With config parsing tools:
1. extract_yaml_value() for specific value (30 tokens)
2. check_gitignore_security() for validation (50 tokens)
3. Total: ~80 tokens

Token savings: 92% (920 tokens saved)

Real-world benefits:
- Extract values without full file parsing
- Validate formats before deployment
- Detect security misconfigurations
- Handle multiple config formats consistently
- Merge configurations safely
- Environment variable substitution

For a typical application with 10 config files:
- Without: 10,000 tokens to parse and validate
- With: 800 tokens for structured extraction
- Savings: ~9,200 tokens (92%)

Security benefits:
- Detect exposed secrets in configs
- Validate .gitignore completeness
- Check for dangerous permissions
- Identify missing security patterns
""")
