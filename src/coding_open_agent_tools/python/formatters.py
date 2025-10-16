"""Python code formatters for docstrings, imports, and type hints.

This module provides deterministic formatting functions:
- Docstring formatting (Google, NumPy, Sphinx styles)
- Import sorting and grouping
- Type hint normalization
"""

import ast
import re
from typing import Any

from coding_open_agent_tools._decorators import strands_tool
from coding_open_agent_tools.types import STDLIB_MODULES


@strands_tool
def format_docstring(docstring: str, style: str, line_length: str) -> dict[str, str]:
    """Format a docstring to conform to a specific style guide.

    Formats docstrings to match Google, NumPy, or Sphinx conventions.
    This is a deterministic formatting operation that agents often
    spend tokens on.

    Args:
        docstring: The docstring text to format
        style: Docstring style ("google", "numpy", "sphinx")
        line_length: Maximum line length (e.g., "79", "88", "100")

    Returns:
        Dictionary with:
        - formatted_docstring: The formatted docstring text
        - style_used: The style applied
        - line_count: Number of lines in formatted docstring
        - changes_made: Description of changes applied

    Raises:
        TypeError: If parameters are not strings
        ValueError: If docstring is empty or style is invalid
    """
    if not isinstance(docstring, str):
        raise TypeError("docstring must be a string")
    if not isinstance(style, str):
        raise TypeError("style must be a string")
    if not isinstance(line_length, str):
        raise TypeError("line_length must be a string")

    if not docstring.strip():
        raise ValueError("docstring cannot be empty")

    if style not in ("google", "numpy", "sphinx"):
        raise ValueError("style must be one of: google, numpy, sphinx")

    try:
        max_length = int(line_length)
        if max_length < 40:
            raise ValueError("line_length must be at least 40")
    except ValueError as e:
        if "invalid literal" in str(e):
            raise ValueError("line_length must be a valid integer string") from e
        raise

    changes: list[str] = []

    # Normalize line endings and trim excess whitespace
    lines = docstring.strip().split("\n")
    lines = [line.rstrip() for line in lines]

    # Extract summary (first line or paragraph)
    summary_lines: list[str] = []
    body_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            if summary_lines:
                body_start = i + 1
                break
            continue
        summary_lines.append(stripped)
        if stripped.endswith("."):  # End of summary sentence
            body_start = i + 1
            break

    summary = " ".join(summary_lines)

    # Wrap summary to line length
    wrapped_summary = _wrap_text(summary, max_length)
    if len(summary_lines) != len(wrapped_summary):
        changes.append("Wrapped summary text to fit line length")

    # Process remaining content
    body_lines = lines[body_start:]

    # Identify sections
    sections: dict[str, list[str]] = {}
    current_section = None
    current_content: list[str] = []

    section_patterns = {
        "google": r"^(Args?|Arguments?|Parameters?|Returns?|Return|Yields?|Raises?|Examples?|Note|Notes):\s*$",
        "numpy": r"^(Parameters?|Returns?|Yields?|Raises?|See Also|Notes?|References?|Examples?)\s*$",
        "sphinx": r"^:(param|type|returns?|rtype|raises?):",
    }

    pattern = section_patterns.get(style, section_patterns["google"])

    for line in body_lines:
        stripped = line.strip()
        if re.match(pattern, stripped):
            if current_section:
                sections[current_section] = current_content
            current_section = stripped.rstrip(":")
            current_content = []
        else:
            if (
                current_section or stripped
            ):  # Only add non-empty lines if we're in a section
                current_content.append(line)

    if current_section:
        sections[current_section] = current_content

    # Format based on style
    formatted_lines: list[str] = wrapped_summary

    if style == "google":
        # Google style: section headers followed by indented content
        for section, content in sections.items():
            formatted_lines.append("")
            formatted_lines.append(f"{section}:")
            for line in content:
                if line.strip():
                    # Indent content
                    if not line.startswith("    "):
                        formatted_lines.append(f"    {line.strip()}")
                        changes.append(f"Indented content in {section} section")
                    else:
                        formatted_lines.append(line.rstrip())
                else:
                    formatted_lines.append("")

    elif style == "numpy":
        # NumPy style: section headers with underlines
        for section, content in sections.items():
            formatted_lines.append("")
            formatted_lines.append(section)
            formatted_lines.append("-" * len(section))
            for line in content:
                formatted_lines.append(line.rstrip())

    elif style == "sphinx":
        # Sphinx style: field lists
        for _section, content in sections.items():
            formatted_lines.append("")
            for line in content:
                formatted_lines.append(line.rstrip())

    formatted_text = "\n".join(formatted_lines)
    line_count = len(formatted_lines)

    if not changes:
        changes.append("No changes needed - already formatted")

    return {
        "formatted_docstring": formatted_text,
        "style_used": style,
        "line_count": str(line_count),
        "changes_made": "; ".join(changes),
    }


@strands_tool
def sort_imports(source_code: str) -> dict[str, Any]:
    """Sort and group imports according to PEP 8 conventions.

    Organizes imports into three groups:
    1. Standard library imports
    2. Third-party imports
    3. Local imports

    Within each group, imports are sorted alphabetically.

    Args:
        source_code: Python source code with imports to sort

    Returns:
        Dictionary with:
        - sorted_code: Source code with sorted imports
        - changes_made: Description of sorting changes
        - stdlib_count: Number of stdlib imports
        - third_party_count: Number of third-party imports
        - local_count: Number of local imports
        - total_imports: Total number of imports

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Cannot parse source code: {e}") from e

    lines = source_code.split("\n")

    # Find import block (consecutive import statements at the top)
    import_lines: list[
        tuple[int, str, str]
    ] = []  # (line_num, import_text, import_type)
    first_import_line = None
    last_import_line = None

    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            line_num = node.lineno - 1  # Convert to 0-indexed
            import_text = lines[line_num]

            # Classify import
            if isinstance(node, ast.Import):
                module_name = node.names[0].name
            else:
                module_name = node.module or ""

            import_type = _classify_import(module_name)
            import_lines.append((line_num, import_text, import_type))

            if first_import_line is None:
                first_import_line = line_num
            last_import_line = line_num
        elif import_lines:
            # Stop at first non-import statement after imports started
            break

    if not import_lines:
        return {
            "sorted_code": source_code,
            "changes_made": "No imports found",
            "stdlib_count": "0",
            "third_party_count": "0",
            "local_count": "0",
            "total_imports": "0",
        }

    # Group imports by type
    stdlib_imports: list[str] = []
    third_party_imports: list[str] = []
    local_imports: list[str] = []

    for _, import_text, import_type in import_lines:
        if import_type == "stdlib":
            stdlib_imports.append(import_text)
        elif import_type == "third_party":
            third_party_imports.append(import_text)
        else:
            local_imports.append(import_text)

    # Sort each group alphabetically
    stdlib_imports.sort()
    third_party_imports.sort()
    local_imports.sort()

    # Build sorted import block
    sorted_imports: list[str] = []

    if stdlib_imports:
        sorted_imports.extend(stdlib_imports)
        if third_party_imports or local_imports:
            sorted_imports.append("")  # Blank line between groups

    if third_party_imports:
        sorted_imports.extend(third_party_imports)
        if local_imports:
            sorted_imports.append("")

    if local_imports:
        sorted_imports.extend(local_imports)

    # Replace import block in source code
    before_imports = lines[:first_import_line] if first_import_line else []
    after_imports = (
        lines[last_import_line + 1 :] if last_import_line is not None else lines
    )

    # Remove any trailing blank lines from before_imports
    while before_imports and not before_imports[-1].strip():
        before_imports.pop()

    # Remove any leading blank lines from after_imports
    while after_imports and not after_imports[0].strip():
        after_imports.pop(0)

    # Construct new source
    new_lines = before_imports + sorted_imports + [""] + after_imports
    sorted_code = "\n".join(new_lines)

    # Determine changes
    original_import_text = "\n".join(line for _, line, _ in import_lines)
    new_import_text = "\n".join(sorted_imports)

    if original_import_text == new_import_text:
        changes = "No changes needed - imports already sorted"
    else:
        changes = "Sorted and grouped imports by PEP 8 standards"

    return {
        "sorted_code": sorted_code,
        "changes_made": changes,
        "stdlib_count": str(len(stdlib_imports)),
        "third_party_count": str(len(third_party_imports)),
        "local_count": str(len(local_imports)),
        "total_imports": str(len(import_lines)),
    }


@strands_tool
def normalize_type_hints(source_code: str) -> dict[str, Any]:
    """Normalize type hints to use modern syntax (PEP 585, PEP 604).

    Converts deprecated typing module types to built-in equivalents:
    - typing.List → list
    - typing.Dict → dict
    - typing.Tuple → tuple
    - typing.Set → set
    - Union[X, Y] → X | Y (Python 3.10+)
    - Optional[X] → X | None (Python 3.10+)

    Args:
        source_code: Python source code to normalize

    Returns:
        Dictionary with:
        - normalized_code: Source code with normalized type hints
        - changes_made: List of normalization changes
        - total_changes: String count of changes made
        - deprecated_typing_removed: "true" or "false"

    Raises:
        TypeError: If source_code is not a string
        ValueError: If source_code is empty
    """
    if not isinstance(source_code, str):
        raise TypeError("source_code must be a string")
    if not source_code.strip():
        raise ValueError("source_code cannot be empty")

    changes: list[str] = []
    normalized = source_code

    # Replace deprecated typing constructs
    replacements = [
        (r"\bList\[", "list[", "Replaced typing.List with built-in list"),
        (r"\bDict\[", "dict[", "Replaced typing.Dict with built-in dict"),
        (r"\bTuple\[", "tuple[", "Replaced typing.Tuple with built-in tuple"),
        (r"\bSet\[", "set[", "Replaced typing.Set with built-in set"),
        (
            r"\bFrozenSet\[",
            "frozenset[",
            "Replaced typing.FrozenSet with built-in frozenset",
        ),
    ]

    for pattern, replacement, description in replacements:
        if re.search(pattern, normalized):
            normalized = re.sub(pattern, replacement, normalized)
            if description not in changes:
                changes.append(description)

    # Replace Union[X, Y] with X | Y (more complex, need to handle nested brackets)
    union_pattern = r"Union\[([^\]]+)\]"
    union_matches = list(re.finditer(union_pattern, normalized))

    if union_matches:
        # Process from end to start to preserve positions
        for match in reversed(union_matches):
            union_content = match.group(1)
            # Split by comma, but respect nested brackets
            types = _split_union_types(union_content)
            pipe_syntax = " | ".join(t.strip() for t in types)
            normalized = (
                normalized[: match.start()] + pipe_syntax + normalized[match.end() :]
            )
            changes.append("Replaced Union[...] with | syntax (PEP 604)")

    # Replace Optional[X] with X | None
    optional_pattern = r"Optional\[([^\]]+)\]"
    optional_matches = list(re.finditer(optional_pattern, normalized))

    if optional_matches:
        for match in reversed(optional_matches):
            optional_content = match.group(1)
            pipe_syntax = f"{optional_content} | None"
            normalized = (
                normalized[: match.start()] + pipe_syntax + normalized[match.end() :]
            )
            changes.append("Replaced Optional[...] with | None syntax (PEP 604)")

    # Check if typing imports can be removed or simplified
    deprecated_typing_removed = "false"

    # If we made changes, check if typing imports are still needed
    if changes:
        typing_constructs = [
            "List",
            "Dict",
            "Tuple",
            "Set",
            "Union",
            "Optional",
            "FrozenSet",
        ]
        still_needed = any(
            re.search(rf"\b{construct}\b", normalized)
            for construct in typing_constructs
        )

        if not still_needed:
            # Try to remove typing imports that are no longer needed
            import_pattern = r"from typing import ([^\n]+)"
            import_match = re.search(import_pattern, normalized)

            if import_match:
                imports = [imp.strip() for imp in import_match.group(1).split(",")]
                remaining_imports = [
                    imp for imp in imports if imp not in typing_constructs
                ]

                if not remaining_imports:
                    # Remove the entire import line
                    normalized = re.sub(r"from typing import [^\n]+\n", "", normalized)
                    changes.append("Removed unnecessary typing import")
                    deprecated_typing_removed = "true"
                elif len(remaining_imports) < len(imports):
                    # Update import to only include remaining
                    new_import = f"from typing import {', '.join(remaining_imports)}"
                    normalized = re.sub(import_pattern, new_import, normalized)
                    changes.append("Simplified typing import")
                    deprecated_typing_removed = "true"

    if not changes:
        changes.append("No deprecated type hints found")

    return {
        "normalized_code": normalized,
        "changes_made": changes,
        "total_changes": str(len(changes)),
        "deprecated_typing_removed": deprecated_typing_removed,
    }


def _wrap_text(text: str, max_length: int) -> list[str]:
    """Wrap text to specified line length, preserving word boundaries.

    Args:
        text: Text to wrap
        max_length: Maximum line length

    Returns:
        List of wrapped lines
    """
    if len(text) <= max_length:
        return [text]

    words = text.split()
    lines: list[str] = []
    current_line: list[str] = []
    current_length = 0

    for word in words:
        word_length = len(word)
        # +1 for space
        if current_length + word_length + (1 if current_line else 0) <= max_length:
            current_line.append(word)
            current_length += word_length + (1 if len(current_line) > 1 else 0)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = word_length

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def _classify_import(import_name: str) -> str:
    """Classify an import as stdlib, third-party, or local.

    Args:
        import_name: Name of the import

    Returns:
        One of: "stdlib", "third_party", "local"
    """
    base_module = import_name.split(".")[0]

    if base_module in STDLIB_MODULES:
        return "stdlib"
    elif base_module.startswith("_"):
        return "local"
    else:
        if "." in import_name and not any(
            import_name.startswith(pkg)
            for pkg in ["google", "microsoft", "amazon", "aws"]
        ):
            return "local"
        return "third_party"


def _split_union_types(union_content: str) -> list[str]:
    """Split Union type content by commas, respecting nested brackets.

    Args:
        union_content: Content inside Union[...] brackets

    Returns:
        List of type strings
    """
    types: list[str] = []
    current: list[str] = []
    bracket_depth = 0

    for char in union_content:
        if char == "[":
            bracket_depth += 1
            current.append(char)
        elif char == "]":
            bracket_depth -= 1
            current.append(char)
        elif char == "," and bracket_depth == 0:
            types.append("".join(current))
            current = []
        else:
            current.append(char)

    if current:
        types.append("".join(current))

    return types
