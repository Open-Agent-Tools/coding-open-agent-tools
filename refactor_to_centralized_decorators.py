#!/usr/bin/env python3
"""Refactor all module files to use centralized decorator imports.

This script:
1. Removes duplicated conditional import blocks
2. Adds single import from _decorators module
3. Preserves type imports if needed elsewhere
"""

import re
from pathlib import Path

# Files to update
MODULE_FILES = [
    "src/coding_open_agent_tools/database/query_builder.py",
    "src/coding_open_agent_tools/database/operations.py",
    "src/coding_open_agent_tools/database/utils.py",
    "src/coding_open_agent_tools/database/schema.py",
    "src/coding_open_agent_tools/analysis/patterns.py",
    "src/coding_open_agent_tools/analysis/complexity.py",
    "src/coding_open_agent_tools/analysis/imports.py",
    "src/coding_open_agent_tools/analysis/secrets.py",
    "src/coding_open_agent_tools/analysis/ast_parsing.py",
    "src/coding_open_agent_tools/quality/analysis.py",
    "src/coding_open_agent_tools/quality/parsers.py",
    "src/coding_open_agent_tools/python/analyzers.py",
    "src/coding_open_agent_tools/python/formatters.py",
    "src/coding_open_agent_tools/python/extractors.py",
    "src/coding_open_agent_tools/python/validators.py",
    "src/coding_open_agent_tools/shell/analyzers.py",
    "src/coding_open_agent_tools/shell/formatters.py",
    "src/coding_open_agent_tools/shell/validators.py",
    "src/coding_open_agent_tools/shell/security.py",
    "src/coding_open_agent_tools/shell/parsers.py",
    "src/coding_open_agent_tools/profiling/memory.py",
    "src/coding_open_agent_tools/profiling/performance.py",
    "src/coding_open_agent_tools/profiling/benchmarks.py",
    "src/coding_open_agent_tools/git/branches.py",
    "src/coding_open_agent_tools/git/status.py",
    "src/coding_open_agent_tools/git/history.py",
]

# Pattern to match the conditional import blocks
DECORATOR_PATTERN = re.compile(
    r"try:\s+from strands import tool as strands_tool\s+"
    r"except ImportError:\s+.*?def strands_tool\(func: Callable\[\.\.\..*?\]\) -> Callable\[\.\.\..*?\]:.*?"
    r"return func\s+"
    r"try:\s+from google\.adk\.tools import tool as adk_tool\s+"
    r"except ImportError:\s+.*?def adk_tool\(func: Callable\[\.\.\..*?\]\) -> Callable\[\.\.\..*?\]:.*?"
    r"return func",
    re.DOTALL | re.MULTILINE,
)


def process_file(file_path: Path) -> bool:
    """Process a single file to replace decorator imports.

    Returns:
        True if file was modified, False otherwise
    """
    content = file_path.read_text()

    # Check if file has the old pattern
    if not DECORATOR_PATTERN.search(content):
        print(f"⏭️  Skipping {file_path.name} - no decorator pattern found")
        return False

    # Remove the conditional import blocks
    new_content = DECORATOR_PATTERN.sub("", content)

    # Check if file uses Callable or Any elsewhere (beyond decorators)
    # Look for uses of Callable/Any in type hints, function signatures, etc.
    uses_typing = False
    for line in new_content.split("\n"):
        # Skip import lines
        if line.strip().startswith("import ") or line.strip().startswith("from "):
            continue
        # Check if Callable or Any used in the code
        if "Callable" in line or "Any" in line:
            uses_typing = True
            break

    # Find where to insert the new import
    # Look for the first import statement or after docstring
    lines = new_content.split("\n")
    insert_index = 0
    in_docstring = False
    docstring_char = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track docstrings
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if not in_docstring:
                in_docstring = True
                docstring_char = '"""' if stripped.startswith('"""') else "'''"
                if stripped.count(docstring_char) >= 2:
                    in_docstring = False
            elif docstring_char in stripped:
                in_docstring = False
                continue

        # Skip if still in docstring
        if in_docstring:
            continue

        # Found first import line
        if stripped.startswith("import ") or stripped.startswith("from "):
            insert_index = i
            break

    # Build new import section
    import_lines = []

    # Add typing import if needed
    if uses_typing:
        import_lines.append("from typing import Any, Callable")
        import_lines.append("")

    # Add centralized decorator import
    import_lines.append(
        "from coding_open_agent_tools._decorators import strands_tool"
    )

    # Insert the new imports
    lines.insert(insert_index, "\n".join(import_lines))
    new_content = "\n".join(lines)

    # Clean up excessive blank lines (more than 2 in a row)
    new_content = re.sub(r"\n\n\n+", "\n\n", new_content)

    # Write the updated content
    file_path.write_text(new_content)
    print(f"✅ Updated {file_path.name}")
    return True


def main() -> None:
    """Process all module files."""
    print("Starting refactoring to centralized decorators...\n")

    updated_count = 0
    for file_path_str in MODULE_FILES:
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        if process_file(file_path):
            updated_count += 1

    print(f"\n✨ Refactoring complete! Updated {updated_count} files.")


if __name__ == "__main__":
    main()
