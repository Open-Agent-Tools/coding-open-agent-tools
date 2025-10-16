"""Read-only git repository information and analysis tools.

This module provides functions to query git repository information using
read-only operations. No write operations (commit, push, merge) are included
for safety.
"""

from coding_open_agent_tools.git.branches import (
    get_branch_info,
    list_branches,
)
from coding_open_agent_tools.git.commits import (
    analyze_commit_quality,
    check_breaking_changes,
    extract_commit_type,
    parse_commit_message,
    validate_commit_length,
    validate_commit_scope,
    validate_commit_signature,
    validate_conventional_commit,
)
from coding_open_agent_tools.git.config import (
    analyze_config_security,
    get_config_value,
    parse_git_config,
    parse_gitignore,
    validate_gitattributes,
    validate_gitignore_patterns,
)
from coding_open_agent_tools.git.conflicts import (
    analyze_conflict_complexity,
    detect_merge_conflicts,
    get_conflict_context,
    parse_conflict_markers,
    predict_merge_conflicts,
    suggest_conflict_resolution,
)
from coding_open_agent_tools.git.diffs import (
    analyze_diff_stats,
    calculate_code_churn,
    find_largest_changes,
    get_file_diff,
)
from coding_open_agent_tools.git.health import (
    analyze_branch_staleness,
    analyze_repository_activity,
    check_gc_needed,
    check_repository_size,
    check_worktree_clean,
    detect_corrupted_objects,
    find_large_files,
    get_repository_metrics,
)
from coding_open_agent_tools.git.history import (
    get_file_at_commit,
    get_file_history,
    get_git_blame,
    get_git_log,
)
from coding_open_agent_tools.git.hooks import (
    analyze_hook_script,
    check_hook_executable,
    get_hook_dependencies,
    list_installed_hooks,
    parse_hook_output,
    test_hook_execution,
    validate_hook_permissions,
    validate_hook_security,
    validate_hook_syntax,
)
from coding_open_agent_tools.git.remotes import (
    analyze_remote_branches,
    check_remote_connectivity,
    check_remote_sync_status,
    list_remotes,
    validate_remote_url_security,
)
from coding_open_agent_tools.git.security import (
    analyze_file_permissions,
    audit_commit_authors,
    check_force_push_protection,
    check_sensitive_files,
    check_signed_tags,
    detect_security_issues,
    scan_history_for_secrets,
    validate_gpg_signatures,
)
from coding_open_agent_tools.git.status import (
    get_current_branch,
    get_git_diff,
    get_git_status,
)
from coding_open_agent_tools.git.submodules import (
    analyze_submodule_updates,
    check_submodule_sync,
    list_submodules,
    validate_submodule_commits,
    validate_submodule_urls,
)
from coding_open_agent_tools.git.tags import (
    analyze_tag_history,
    compare_versions,
    find_commits_between_tags,
    list_tags,
    validate_semver_tag,
)
from coding_open_agent_tools.git.workflows import (
    analyze_merge_strategy,
    check_protected_branches,
    validate_branch_naming,
    validate_commit_frequency,
    validate_gitflow_workflow,
    validate_trunk_based_workflow,
)

__all__ = [
    # Status and diff operations
    "get_git_status",
    "get_current_branch",
    "get_git_diff",
    # Log and blame operations
    "get_git_log",
    "get_git_blame",
    "get_file_history",
    "get_file_at_commit",
    # Branch information
    "list_branches",
    "get_branch_info",
    # Commit validation and analysis
    "validate_conventional_commit",
    "validate_commit_signature",
    "analyze_commit_quality",
    "parse_commit_message",
    "validate_commit_length",
    "extract_commit_type",
    "validate_commit_scope",
    "check_breaking_changes",
    # Hook management
    "list_installed_hooks",
    "validate_hook_syntax",
    "validate_hook_security",
    "check_hook_executable",
    "analyze_hook_script",
    "test_hook_execution",
    "parse_hook_output",
    "validate_hook_permissions",
    "get_hook_dependencies",
    # Configuration
    "parse_git_config",
    "validate_gitignore_patterns",
    "parse_gitignore",
    "validate_gitattributes",
    "analyze_config_security",
    "get_config_value",
    # Repository health
    "find_large_files",
    "check_repository_size",
    "analyze_branch_staleness",
    "check_gc_needed",
    "detect_corrupted_objects",
    "analyze_repository_activity",
    "check_worktree_clean",
    "get_repository_metrics",
    # Merge conflicts
    "detect_merge_conflicts",
    "parse_conflict_markers",
    "predict_merge_conflicts",
    "analyze_conflict_complexity",
    "get_conflict_context",
    "suggest_conflict_resolution",
    # Security auditing
    "scan_history_for_secrets",
    "check_sensitive_files",
    "validate_gpg_signatures",
    "check_force_push_protection",
    "analyze_file_permissions",
    "check_signed_tags",
    "detect_security_issues",
    "audit_commit_authors",
    # Submodule management
    "list_submodules",
    "validate_submodule_urls",
    "check_submodule_sync",
    "analyze_submodule_updates",
    "validate_submodule_commits",
    # Workflow validation
    "validate_gitflow_workflow",
    "validate_trunk_based_workflow",
    "validate_branch_naming",
    "check_protected_branches",
    "analyze_merge_strategy",
    "validate_commit_frequency",
    # Remote analysis
    "list_remotes",
    "check_remote_connectivity",
    "analyze_remote_branches",
    "check_remote_sync_status",
    "validate_remote_url_security",
    # Tag and version management
    "list_tags",
    "validate_semver_tag",
    "compare_versions",
    "analyze_tag_history",
    "find_commits_between_tags",
    # Diff analysis
    "analyze_diff_stats",
    "calculate_code_churn",
    "get_file_diff",
    "find_largest_changes",
]
