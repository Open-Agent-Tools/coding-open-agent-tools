"""Example: Git repository health checking.

Demonstrates how to check repository health, detect issues,
and get actionable metrics without manual git command execution.

Token Savings: 70-85% (structured metrics vs parsing git output)
"""

from coding_open_agent_tools.git import health
import tempfile
import subprocess

# Create a temporary git repository for demonstration
print("=" * 60)
print("Setting up demo git repository...")
print("=" * 60)

# Create temp directory
repo_path = tempfile.mkdtemp()
print(f"Created temp repo at: {repo_path}\n")

# Initialize git repo
subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
subprocess.run(["git", "config", "user.name", "Demo User"], cwd=repo_path, capture_output=True)
subprocess.run(["git", "config", "user.email", "demo@example.com"], cwd=repo_path, capture_output=True)

# Create some commits
for i in range(5):
    with open(f"{repo_path}/file{i}.txt", "w") as f:
        f.write(f"Content for file {i}\n" * 100)
    subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", f"Commit {i+1}"], cwd=repo_path, capture_output=True)

print("Demo repository created with 5 commits\n")

# Example 1: Get overall repository metrics
print("=" * 60)
print("Example 1: Get repository health metrics")
print("=" * 60)

metrics = health.get_repository_metrics(repo_path)
print(f"Total commits: {metrics['total_commits']}")
print(f"Total branches: {metrics['total_branches']}")
print(f"Repository size: {metrics['repo_size']}")
print(f"Health score: {metrics['health_score']}/100")
print(f"Warnings: {metrics['warnings']}")
print()

# Example 2: Check if garbage collection is needed
print("=" * 60)
print("Example 2: Check if garbage collection is needed")
print("=" * 60)

gc_check = health.check_gc_needed(repo_path)
print(f"GC needed: {gc_check['gc_needed']}")
print(f"Loose objects: {gc_check['loose_objects_count']}")
print(f"Pack files: {gc_check['pack_files_count']}")
print(f"Repository size: {gc_check['repo_size_mb']} MB")
if gc_check['gc_needed'] == "true":
    print(f"Recommendations: {gc_check['recommendations']}")
print()

# Example 3: Find large files
print("=" * 60)
print("Example 3: Find large files (>1KB)")
print("=" * 60)

large_files = health.find_large_files(repo_path, "1")  # Files > 1KB
print(f"Large files found: {large_files['large_files_count']}")
if int(large_files['large_files_count']) > 0:
    print(f"Files: {large_files['files_list']}")
print(f"Total size: {large_files['total_size_kb']} KB")
print()

# Example 4: Get repository statistics
print("=" * 60)
print("Example 4: Get comprehensive repository statistics")
print("=" * 60)

stats = health.get_repository_statistics(repo_path)
print(f"Total commits: {stats['total_commits']}")
print(f"Total branches: {stats['total_branches']}")
print(f"Total tags: {stats['total_tags']}")
print(f"Total contributors: {stats['total_contributors']}")
print(f"Repository size: {stats['repo_size_mb']} MB")
print(f"First commit date: {stats['first_commit_date']}")
print(f"Last commit date: {stats['last_commit_date']}")
print()

# Example 5: Check repository health issues
print("=" * 60)
print("Example 5: Check for specific health issues")
print("=" * 60)

health_check = health.check_repository_health(repo_path)
print(f"Has issues: {health_check['has_issues']}")
print(f"Issue count: {health_check['issue_count']}")
if int(health_check['issue_count']) > 0:
    print(f"Issues: {health_check['issues']}")
print(f"Recommendations: {health_check['recommendations']}")
print()

# Cleanup
subprocess.run(["rm", "-rf", repo_path], capture_output=True)
print(f"Cleaned up temp repo: {repo_path}\n")

# Why this saves tokens:
print("=" * 60)
print("TOKEN SAVINGS BREAKDOWN")
print("=" * 60)
print("""
Without health tools:
1. Agent runs 'git log --oneline' (200 tokens response)
2. Agent runs 'git branch -a' (150 tokens response)
3. Agent runs 'git count-objects -v' (100 tokens response)
4. Agent runs 'du -sh .git' (50 tokens response)
5. Agent parses all output manually (300 tokens reasoning)
6. Agent computes metrics (200 tokens reasoning)
7. Total: ~1000 tokens

With health tools:
1. Call get_repository_metrics() (50 tokens structured response)
2. All metrics pre-computed and structured (150 tokens analysis)
3. Total: ~200 tokens

Token savings: 80% (800 tokens saved)

Additional benefits:
- No parsing errors (prevents retry loops)
- Consistent format across repositories
- Actionable recommendations included
- Health score provides quick assessment
""")
