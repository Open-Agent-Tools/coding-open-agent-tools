"""Example: Security scanning for secrets and vulnerabilities.

Demonstrates how to detect secrets, security issues, and dangerous
patterns in code before they reach production.

Token Savings: 85-90% (structured detection vs manual analysis)
"""

from coding_open_agent_tools.analysis import secrets
from coding_open_agent_tools.shell import security
from coding_open_agent_tools.git import security as git_security
import tempfile
import os

# Example 1: Scan code for secrets
print("=" * 60)
print("Example 1: Scan Python code for exposed secrets")
print("=" * 60)

python_code_with_secrets = """
import requests

# Bad practice: Hardcoded credentials
API_KEY = "sk_live_1234567890abcdef"
DATABASE_URL = "postgresql://admin:SecretPassword123@localhost:5432/mydb"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

def connect_to_api():
    # Another bad practice: API key in URL
    response = requests.get(
        "https://api.example.com/data?api_key=abc123def456"
    )
    return response.json()

def process_data():
    # GitHub token
    token = "ghp_1234567890abcdefghijklmnopqrstuv"
    return token
"""

result = secrets.scan_for_secrets(python_code_with_secrets)
print(f"Secrets found: {result['secrets_found']}")
print(f"Secret count: {result['secret_count']}")
print(f"Secret types detected:")
for secret in eval(result['secrets_found']):
    print(f"  - Line {secret['line']}: {secret['type']}")
print()

# Example 2: Scan shell script for security issues
print("=" * 60)
print("Example 2: Scan shell script for security vulnerabilities")
print("=" * 60)

dangerous_shell_script = """#!/bin/bash
# Dangerous shell script with multiple security issues

# Issue 1: Command injection risk (unquoted variable)
USER_INPUT=$1
eval "ls $USER_INPUT"

# Issue 2: Using dangerous commands
rm -rf /tmp/*

# Issue 3: Downloading and executing without verification
curl http://example.com/script.sh | bash

# Issue 4: Using eval with user input
eval "echo $USER_INPUT"

# Issue 5: Hardcoded credentials
PASSWORD="SuperSecret123"
mysql -u root -p$PASSWORD -e "SELECT * FROM users"

# Issue 6: No input validation
echo "User provided: $1"
mkdir $1
"""

security_result = security.analyze_shell_security(dangerous_shell_script)
print(f"Issues found: {security_result['issue_count']}")
print(f"Critical issues: {security_result['critical_count']}")
print(f"High issues: {security_result['high_count']}")
print(f"Medium issues: {security_result['medium_count']}")
print(f"\nIssues detected:")
for issue in eval(security_result['issues']):
    print(f"  [{issue['severity']}] Line {issue['line']}: {issue['type']}")
    print(f"    {issue['description']}")
print()

# Example 3: Scan directory for secrets
print("=" * 60)
print("Example 3: Scan entire directory for secrets")
print("=" * 60)

# Create temporary directory with test files
temp_dir = tempfile.mkdtemp()
print(f"Created temp directory: {temp_dir}")

# Create file with secrets
test_file1 = os.path.join(temp_dir, "config.py")
with open(test_file1, "w") as f:
    f.write("""
API_KEY = "EXAMPLE_API_KEY_abc123xyz789_NOT_REAL"
STRIPE_KEY = "EXAMPLE_STRIPE_KEY_pk_test_123456789_FAKE"
""")

# Create file without secrets
test_file2 = os.path.join(temp_dir, "utils.py")
with open(test_file2, "w") as f:
    f.write("""
def process_data(data):
    return data.upper()
""")

# Scan directory
dir_result = secrets.scan_directory_for_secrets(temp_dir)
print(f"Total files scanned: {dir_result['total_files']}")
print(f"Files with secrets: {dir_result['files_with_secrets']}")
print(f"Total secrets found: {dir_result['total_secrets']}")
print(f"\nFiles containing secrets:")
for file_info in eval(dir_result['results']):
    print(f"  {file_info['file']}: {file_info['secret_count']} secrets")

# Cleanup
os.remove(test_file1)
os.remove(test_file2)
os.rmdir(temp_dir)
print(f"\nCleaned up: {temp_dir}")
print()

# Example 4: Validate secret patterns
print("=" * 60)
print("Example 4: Validate and identify secret patterns")
print("=" * 60)

test_patterns = [
    "sk_live_1234567890abcdef",  # Stripe key
    "ghp_1234567890abcdefghijklmnopqrstuv",  # GitHub token
    "AKIA1234567890ABCDEF",  # AWS access key
    "just_a_normal_string",  # Not a secret
    "password123",  # Weak password
]

for pattern in test_patterns:
    validation = secrets.validate_secret_patterns(pattern)
    print(f"Pattern: {pattern[:30]}...")
    print(f"  Is potential secret: {validation['is_potential_secret']}")
    if validation['is_potential_secret'] == "true":
        print(f"  Pattern types: {validation['pattern_types']}")
    print()

# Example 5: Git repository security scan
print("=" * 60)
print("Example 5: Security scan for git repository (demo)")
print("=" * 60)

print("""
Note: This would scan a real git repository for:
- Exposed secrets in commit history
- Sensitive files that should be .gitignored
- Credentials in config files
- API keys in environment files
- Private keys in the repository

Example output:
  Secrets in history: 3
  Exposed files: 2 (.env, secrets.json)
  Recommendations:
    - Add .env to .gitignore
    - Use git-filter-repo to remove secrets.json from history
    - Rotate compromised API keys immediately
    - Use environment variables for configuration
""")
print()

# Why this saves tokens:
print("=" * 60)
print("TOKEN SAVINGS BREAKDOWN")
print("=" * 60)
print("""
Without security scanning tools:
1. Agent reads 50 files to understand codebase (5000 tokens)
2. Agent analyzes each file for patterns (2000 tokens reasoning)
3. Agent manually identifies potential issues (1000 tokens)
4. Agent writes up findings (500 tokens)
5. Total: ~8500 tokens

With security scanning tools:
1. scan_directory_for_secrets() on 50 files (100 tokens structured response)
2. Agent reviews specific issues only (300 tokens)
3. Agent provides recommendations (200 tokens)
4. Total: ~600 tokens

Token savings: 93% (7900 tokens saved)

Additional benefits:
- Comprehensive pattern detection (30+ secret types)
- Line-number precision for quick fixes
- Severity classification (Critical/High/Medium/Low)
- Actionable recommendations included
- Prevents accidental secret exposure
- Catches issues before git commit

Real-world impact:
- Prevents data breaches
- Maintains compliance (GDPR, PCI-DSS)
- Protects API quotas and costs
- Avoids credential rotation overhead
- Saves security review time
""")
