#!/usr/bin/env python3
"""Refactor all module files to use centralized decorator imports (v2).

This script:
1. Removes duplicated conditional import blocks
2. Adds single import from _decorators module
3. Cleans up duplicate imports properly
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


def process_file(file_path: Path) -> bool:
    """Process a single file to replace decorator imports.

    Returns:
        True if file was modified, False otherwise
    """
    content = file_path.read_text()

    # Remove the decorators import if already added by v1
    content = re.sub(
        r"from coding_open_agent_tools\._decorators import adk_tool, strands_tool\n",
        "",
        content,
    )

    # Remove conditional import blocks for strands
    content = re.sub(
        r"try:\s+from strands import tool as strands_tool\s+"
        r"except ImportError:\s+.*?def strands_tool\(func: Callable\[\.\.\..*?\]\) -> Callable\[\.\.\..*?\]:.*?"
        r"return func\s+",
        "",
        content,
        flags=re.DOTALL,
    )

    # Remove conditional import blocks for adk_tool
    content = re.sub(
        r"try:\s+from google\.adk\.tools import tool as adk_tool\s+"
        r"except ImportError:\s+.*?def adk_tool\(func: Callable\[\.\.\..*?\]\) -> Callable\[\.\.\..*?\]:.*?"
        r"return func\s+",
        "",
        content,
        flags=re.DOTALL,
    )

    # Remove duplicate "from typing import Any, Callable" lines
    lines = content.split("\n")
    seen_typing_import = False
    cleaned_lines = []
    decorator_import_added = False

    for i, line in enumerate(lines):
        # Skip duplicate typing imports
        if line.strip() == "from typing import Any, Callable":
            if seen_typing_import:
                continue  # Skip duplicate
            seen_typing_import = True

        # Add decorator import right after first typing import
        if seen_typing_import and not decorator_import_added and line.strip():
            # Check if this is still an import line or if we've moved past imports
            if not (
                line.strip().startswith("import ") or line.strip().startswith("from ")
            ):
                # We're past imports, insert decorator import before this line
                cleaned_lines.append("")
                cleaned_lines.append(
                    "from coding_open_agent_tools._decorators import strands_tool"
                )
                decorator_import_added = True

        cleaned_lines.append(line)

    # If we never added decorator import (no non-import line found), add it at end of imports
    if not decorator_import_added:
        # Find the last import line
        for i in range(len(cleaned_lines) - 1, -1, -1):
            if cleaned_lines[i].strip().startswith(("import ", "from ")):
                cleaned_lines.insert(i + 1, "")
                cleaned_lines.insert(
                    i + 2,
                    "from coding_open_agent_tools._decorators import strands_tool",
                )
                break

    content = "\n".join(cleaned_lines)

    # Clean up excessive blank lines (more than 2 in a row)
    content = re.sub(r"\n\n\n+", "\n\n", content)

    # Write the updated content
    file_path.write_text(content)
    print(f"✅ Cleaned up {file_path.name}")
    return True


def main() -> None:
    """Process all module files."""
    print("Starting cleanup refactoring...\n")

    updated_count = 0
    for file_path_str in MODULE_FILES:
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        if process_file(file_path):
            updated_count += 1

    print(f"\n✨ Cleanup complete! Updated {updated_count} files.")


if __name__ == "__main__":
    main()
