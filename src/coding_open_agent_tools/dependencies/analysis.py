"""Dependency analysis and conflict detection implementation.

This module provides tools for parsing, analyzing, and validating dependencies
across multiple programming languages and package managers.
"""

import json
import re
from typing import Any, Callable

# Conditional import for strands decorator
try:
    from strands_agents import tool as strands_tool
except ImportError:

    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        return func


@strands_tool
def parse_requirements_txt(content: str) -> dict[str, str]:
    """Parse Python requirements.txt file and extract package dependencies.

    Supports standard pip requirements format including:
    - Simple package names: package==1.0.0
    - Version specifiers: >=, <=, >, <, ==, !=
    - Comments (lines starting with #)
    - Extra requirements: package[extra]==1.0.0
    - Git URLs and VCS requirements
    - Line continuation with backslash

    Args:
        content: String contents of requirements.txt file

    Returns:
        Dictionary with:
        - package_count: Number of packages found
        - packages: JSON array of package objects with name, version, specifier
        - has_git_dependencies: "true" if git URLs found
        - has_extras: "true" if extras specified
        - comments: Number of comment lines

    Raises:
        TypeError: If content is not a string
        ValueError: If content is empty

    Example:
        >>> content = "requests==2.28.0\\ndjango>=4.0.0"
        >>> result = parse_requirements_txt(content)
        >>> result["package_count"]
        '2'
    """
    if not isinstance(content, str):
        raise TypeError("content must be a string")
    if not content.strip():
        raise ValueError("content cannot be empty")

    packages = []
    has_git = False
    has_extras = False
    comment_count = 0

    lines = content.split("\n")
    for line in lines:
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Handle comments
        if stripped.startswith("#"):
            comment_count += 1
            continue

        # Remove inline comments
        if "#" in stripped:
            stripped = stripped.split("#")[0].strip()

        # Check for git dependencies
        if any(vcs in stripped.lower() for vcs in ["git+", "hg+", "svn+", "bzr+"]):
            has_git = True
            # Extract package name from git URL if possible
            if "@" in stripped:
                pkg_name = stripped.split("/")[-1].split("@")[0].replace(".git", "")
                packages.append(
                    {"name": pkg_name, "version": "git", "specifier": "git"}
                )
            continue

        # Parse standard requirement
        # Match: package[extras]operator version
        match = re.match(
            r"^([a-zA-Z0-9_-]+)(\[([a-zA-Z0-9_,-]+)\])?(==|>=|<=|>|<|!=|~=)?(.+)?$",
            stripped,
        )

        if match:
            pkg_name = match.group(1)
            extras = match.group(3)
            specifier = match.group(4) or "=="
            version = (match.group(5) or "").strip()

            if extras:
                has_extras = True

            packages.append(
                {
                    "name": pkg_name,
                    "version": version if version else "any",
                    "specifier": specifier,
                    "extras": extras if extras else "",
                }
            )

    return {
        "package_count": str(len(packages)),
        "packages": json.dumps(packages),
        "has_git_dependencies": "true" if has_git else "false",
        "has_extras": "true" if has_extras else "false",
        "comments": str(comment_count),
    }


@strands_tool
def parse_package_json(content: str) -> dict[str, str]:
    """Parse Node.js package.json file and extract dependencies.

    Extracts dependencies, devDependencies, peerDependencies, and optionalDependencies.
    Supports standard npm/yarn semantic versioning and version ranges.

    Args:
        content: String contents of package.json file

    Returns:
        Dictionary with:
        - package_name: Name of the package
        - version: Package version
        - dependency_count: Total number of dependencies
        - dependencies: JSON array of regular dependencies
        - dev_dependency_count: Number of devDependencies
        - dev_dependencies: JSON array of devDependencies
        - peer_dependency_count: Number of peerDependencies
        - has_scripts: "true" if scripts defined
        - has_workspaces: "true" if workspaces defined

    Raises:
        TypeError: If content is not a string
        ValueError: If content is empty or invalid JSON

    Example:
        >>> content = '{"name": "myapp", "dependencies": {"express": "^4.0.0"}}'
        >>> result = parse_package_json(content)
        >>> result["dependency_count"]
        '1'
    """
    if not isinstance(content, str):
        raise TypeError("content must be a string")
    if not content.strip():
        raise ValueError("content cannot be empty")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    # Extract basic package info
    pkg_name = data.get("name", "")
    version = data.get("version", "")

    # Parse dependencies
    dependencies = []
    for name, ver in data.get("dependencies", {}).items():
        dependencies.append({"name": name, "version": ver, "type": "production"})

    # Parse devDependencies
    dev_dependencies = []
    for name, ver in data.get("devDependencies", {}).items():
        dev_dependencies.append({"name": name, "version": ver, "type": "development"})

    # Parse peerDependencies
    peer_count = len(data.get("peerDependencies", {}))

    # Check for scripts and workspaces
    has_scripts = "scripts" in data and len(data["scripts"]) > 0
    has_workspaces = "workspaces" in data

    return {
        "package_name": pkg_name,
        "version": version,
        "dependency_count": str(len(dependencies)),
        "dependencies": json.dumps(dependencies),
        "dev_dependency_count": str(len(dev_dependencies)),
        "dev_dependencies": json.dumps(dev_dependencies),
        "peer_dependency_count": str(peer_count),
        "has_scripts": "true" if has_scripts else "false",
        "has_workspaces": "true" if has_workspaces else "false",
    }


@strands_tool
def parse_poetry_lock(content: str) -> dict[str, str]:
    """Parse Python Poetry lock file and extract locked dependencies.

    Parses TOML-formatted poetry.lock files to extract exact versions,
    hashes, and dependency metadata.

    Args:
        content: String contents of poetry.lock file

    Returns:
        Dictionary with:
        - package_count: Number of locked packages
        - packages: JSON array of package objects
        - has_hashes: "true" if package hashes present
        - python_version: Python version constraint
        - content_hash: Lock file content hash

    Raises:
        TypeError: If content is not a string
        ValueError: If content is empty

    Example:
        >>> content = '[[package]]\\nname = "requests"\\nversion = "2.28.0"'
        >>> result = parse_poetry_lock(content)
        >>> result["package_count"]
        '1'
    """
    if not isinstance(content, str):
        raise TypeError("content must be a string")
    if not content.strip():
        raise ValueError("content cannot be empty")

    packages = []
    has_hashes = False
    python_version = ""
    content_hash = ""

    # Simple TOML parsing for [[package]] sections
    current_package: dict[str, str] = {}
    lines = content.split("\n")

    for line in lines:
        stripped = line.strip()

        # Start of new package
        if stripped == "[[package]]":
            if current_package:
                packages.append(current_package.copy())
            current_package = {}
            continue

        # Extract metadata section
        if "[metadata]" in stripped:
            # Look for content-hash in next lines
            continue

        # Parse key-value pairs
        if "=" in stripped and not stripped.startswith("#"):
            # Remove quotes and parse
            if 'name = "' in stripped:
                name = stripped.split('name = "')[1].split('"')[0]
                current_package["name"] = name
            elif 'version = "' in stripped:
                version = stripped.split('version = "')[1].split('"')[0]
                current_package["version"] = version
            elif 'python-versions = "' in stripped:
                python_version = stripped.split('python-versions = "')[1].split('"')[0]
            elif 'content-hash = "' in stripped:
                content_hash = stripped.split('content-hash = "')[1].split('"')[0]
            elif stripped.startswith("files = ["):
                has_hashes = True

    # Add last package
    if current_package:
        packages.append(current_package)

    return {
        "package_count": str(len(packages)),
        "packages": json.dumps(packages),
        "has_hashes": "true" if has_hashes else "false",
        "python_version": python_version,
        "content_hash": content_hash,
    }


@strands_tool
def parse_cargo_toml(content: str) -> dict[str, str]:
    """Parse Rust Cargo.toml file and extract dependencies.

    Parses TOML-formatted Cargo.toml to extract package dependencies,
    build dependencies, and dev dependencies.

    Args:
        content: String contents of Cargo.toml file

    Returns:
        Dictionary with:
        - package_name: Name of the Rust package
        - version: Package version
        - dependency_count: Number of regular dependencies
        - dependencies: JSON array of dependencies
        - dev_dependency_count: Number of dev dependencies
        - build_dependency_count: Number of build dependencies
        - has_features: "true" if features defined

    Raises:
        TypeError: If content is not a string
        ValueError: If content is empty

    Example:
        >>> content = '[package]\\nname = "myapp"\\n[dependencies]\\nserde = "1.0"'
        >>> result = parse_cargo_toml(content)
        >>> result["dependency_count"]
        '1'
    """
    if not isinstance(content, str):
        raise TypeError("content must be a string")
    if not content.strip():
        raise ValueError("content cannot be empty")

    pkg_name = ""
    version = ""
    dependencies = []
    dev_dependencies = []
    build_dependencies = []
    has_features = False

    current_section = None
    lines = content.split("\n")

    for line in lines:
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            continue

        # Detect sections
        if stripped.startswith("["):
            if stripped == "[package]":
                current_section = "package"
            elif stripped == "[dependencies]":
                current_section = "dependencies"
            elif stripped == "[dev-dependencies]":
                current_section = "dev-dependencies"
            elif stripped == "[build-dependencies]":
                current_section = "build-dependencies"
            elif stripped.startswith("[features"):
                has_features = True
                current_section = "features"
            else:
                current_section = "other"
            continue

        # Parse based on current section
        if current_section == "package":
            if 'name = "' in stripped:
                pkg_name = stripped.split('name = "')[1].split('"')[0]
            elif 'version = "' in stripped:
                version = stripped.split('version = "')[1].split('"')[0]

        elif current_section == "dependencies":
            if "=" in stripped:
                dep_name = stripped.split("=")[0].strip()
                # Extract version (simple string or table format)
                if '"' in stripped:
                    dep_version = stripped.split('"')[1] if '"' in stripped else "any"
                else:
                    dep_version = "any"
                dependencies.append({"name": dep_name, "version": dep_version})

        elif current_section == "dev-dependencies":
            if "=" in stripped:
                dep_name = stripped.split("=")[0].strip()
                dev_dependencies.append({"name": dep_name, "version": "dev"})

        elif current_section == "build-dependencies":
            if "=" in stripped:
                dep_name = stripped.split("=")[0].strip()
                build_dependencies.append({"name": dep_name, "version": "build"})

    return {
        "package_name": pkg_name,
        "version": version,
        "dependency_count": str(len(dependencies)),
        "dependencies": json.dumps(dependencies),
        "dev_dependency_count": str(len(dev_dependencies)),
        "build_dependency_count": str(len(build_dependencies)),
        "has_features": "true" if has_features else "false",
    }


@strands_tool
def detect_version_conflicts(dependencies_json: str) -> dict[str, str]:
    """Detect version conflicts in dependency specifications.

    Analyzes a list of dependencies to find packages with conflicting
    version requirements (e.g., package A requires lib==1.0, package B requires lib==2.0).

    Args:
        dependencies_json: JSON string of dependencies array with name, version, specifier

    Returns:
        Dictionary with:
        - has_conflicts: "true" if conflicts detected
        - conflict_count: Number of conflicting packages
        - conflicts: JSON array of conflict details
        - suggestions: Recommended resolution steps

    Raises:
        TypeError: If dependencies_json is not a string
        ValueError: If dependencies_json is empty or invalid JSON

    Example:
        >>> deps = '[{"name": "pkg", "version": "1.0", "specifier": "=="}]'
        >>> result = detect_version_conflicts(deps)
        >>> result["has_conflicts"]
        'false'
    """
    if not isinstance(dependencies_json, str):
        raise TypeError("dependencies_json must be a string")
    if not dependencies_json.strip():
        raise ValueError("dependencies_json cannot be empty")

    try:
        dependencies = json.loads(dependencies_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    # Group dependencies by package name
    package_versions: dict[str, list[dict[str, str]]] = {}
    for dep in dependencies:
        name = dep.get("name", "")
        if name:
            if name not in package_versions:
                package_versions[name] = []
            package_versions[name].append(dep)

    # Detect conflicts
    conflicts = []
    for pkg_name, versions in package_versions.items():
        if len(versions) > 1:
            # Check for incompatible version requirements
            version_specs = [
                f"{v.get('specifier', '==')}{v.get('version', '')}" for v in versions
            ]

            # Simplified conflict detection: exact versions that differ
            exact_versions = [
                v.get("version")
                for v in versions
                if v.get("specifier") == "==" and v.get("version")
            ]

            if len(set(exact_versions)) > 1:
                conflicts.append(
                    {
                        "package": pkg_name,
                        "conflicting_versions": version_specs,
                        "severity": "high",
                    }
                )

    suggestions = []
    if conflicts:
        suggestions.append("Review conflicting version requirements")
        suggestions.append("Consider using version ranges instead of exact pins")
        suggestions.append("Check if packages can be upgraded to compatible versions")

    return {
        "has_conflicts": "true" if conflicts else "false",
        "conflict_count": str(len(conflicts)),
        "conflicts": json.dumps(conflicts),
        "suggestions": json.dumps(suggestions),
    }


@strands_tool
def validate_semver(version: str) -> dict[str, str]:
    """Validate semantic versioning format.

    Checks if a version string follows semantic versioning (semver) specification:
    MAJOR.MINOR.PATCH with optional pre-release and build metadata.

    Args:
        version: Version string to validate

    Returns:
        Dictionary with:
        - is_valid: "true" if valid semver
        - major: Major version number
        - minor: Minor version number
        - patch: Patch version number
        - prerelease: Pre-release identifier (if present)
        - build_metadata: Build metadata (if present)
        - error_message: Error description if invalid

    Raises:
        TypeError: If version is not a string
        ValueError: If version is empty

    Example:
        >>> result = validate_semver("1.2.3-alpha+build.123")
        >>> result["is_valid"]
        'true'
    """
    if not isinstance(version, str):
        raise TypeError("version must be a string")
    if not version.strip():
        raise ValueError("version cannot be empty")

    # Semver regex pattern
    semver_pattern = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"

    match = re.match(semver_pattern, version.strip())

    if match:
        return {
            "is_valid": "true",
            "major": match.group(1),
            "minor": match.group(2),
            "patch": match.group(3),
            "prerelease": match.group(4) if match.group(4) else "",
            "build_metadata": match.group(5) if match.group(5) else "",
            "error_message": "",
        }
    else:
        return {
            "is_valid": "false",
            "major": "0",
            "minor": "0",
            "patch": "0",
            "prerelease": "",
            "build_metadata": "",
            "error_message": f"Invalid semver format: {version}",
        }


@strands_tool
def check_license_conflicts(packages_json: str) -> dict[str, str]:
    """Check for license incompatibilities between dependencies.

    Analyzes package licenses to detect potential conflicts (e.g., GPL with proprietary).
    Identifies copyleft, permissive, and proprietary licenses.

    Args:
        packages_json: JSON string of packages with name and license fields

    Returns:
        Dictionary with:
        - has_conflicts: "true" if license conflicts detected
        - conflict_count: Number of license conflicts
        - conflicts: JSON array of conflict descriptions
        - copyleft_count: Number of copyleft licenses (GPL, AGPL)
        - permissive_count: Number of permissive licenses (MIT, Apache, BSD)
        - proprietary_count: Number of proprietary/unknown licenses
        - warnings: License compatibility warnings

    Raises:
        TypeError: If packages_json is not a string
        ValueError: If packages_json is empty or invalid JSON

    Example:
        >>> pkgs = '[{"name": "pkg1", "license": "MIT"}]'
        >>> result = check_license_conflicts(pkgs)
        >>> result["permissive_count"]
        '1'
    """
    if not isinstance(packages_json, str):
        raise TypeError("packages_json must be a string")
    if not packages_json.strip():
        raise ValueError("packages_json cannot be empty")

    try:
        packages = json.loads(packages_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    # License categories (uppercase for matching)
    copyleft_licenses = ["GPL", "AGPL", "LGPL", "MPL", "EPL", "EUPL"]
    permissive_licenses = ["MIT", "APACHE", "BSD", "ISC", "UNLICENSE", "WTFPL"]

    copyleft_packages = []
    permissive_packages = []
    proprietary_packages = []
    conflicts = []
    warnings = []

    for pkg in packages:
        name = pkg.get("name", "")
        license_str = pkg.get("license", "").upper()

        if any(cl in license_str for cl in copyleft_licenses):
            copyleft_packages.append({"name": name, "license": license_str})
        elif any(pl in license_str for pl in permissive_licenses):
            permissive_packages.append({"name": name, "license": license_str})
        else:
            proprietary_packages.append({"name": name, "license": license_str})

    # Detect conflicts
    if copyleft_packages and proprietary_packages:
        conflicts.append(
            {
                "type": "copyleft-proprietary",
                "copyleft": [p["name"] for p in copyleft_packages[:3]],
                "proprietary": [p["name"] for p in proprietary_packages[:3]],
            }
        )
        warnings.append(
            "Mixing copyleft and proprietary licenses may have legal implications"
        )

    if any("GPL" in p["license"] for p in copyleft_packages):
        warnings.append("GPL licenses require derivative works to also be GPL-licensed")

    return {
        "has_conflicts": "true" if conflicts else "false",
        "conflict_count": str(len(conflicts)),
        "conflicts": json.dumps(conflicts),
        "copyleft_count": str(len(copyleft_packages)),
        "permissive_count": str(len(permissive_packages)),
        "proprietary_count": str(len(proprietary_packages)),
        "warnings": json.dumps(warnings),
    }


@strands_tool
def calculate_dependency_tree(dependencies_json: str) -> dict[str, str]:
    """Calculate dependency tree structure and depth.

    Builds a dependency tree from a list of package dependencies and
    calculates metrics like depth, breadth, and total node count.

    Args:
        dependencies_json: JSON string with packages and their dependencies

    Returns:
        Dictionary with:
        - max_depth: Maximum depth of dependency tree
        - total_packages: Total number of unique packages
        - leaf_packages: Number of packages with no dependencies
        - root_packages: Number of top-level packages
        - tree_structure: JSON representation of tree
        - average_dependencies: Average dependencies per package

    Raises:
        TypeError: If dependencies_json is not a string
        ValueError: If dependencies_json is empty or invalid JSON

    Example:
        >>> deps = '[{"name": "app", "requires": ["lib1", "lib2"]}]'
        >>> result = calculate_dependency_tree(deps)
        >>> result["root_packages"]
        '1'
    """
    if not isinstance(dependencies_json, str):
        raise TypeError("dependencies_json must be a string")
    if not dependencies_json.strip():
        raise ValueError("dependencies_json cannot be empty")

    try:
        dependencies = json.loads(dependencies_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    # Build adjacency list
    dep_graph: dict[str, list[str]] = {}
    all_packages = set()

    for dep in dependencies:
        name = dep.get("name", "")
        requires = dep.get("requires", [])

        if name:
            all_packages.add(name)
            dep_graph[name] = requires if isinstance(requires, list) else []

            for req in dep_graph[name]:
                all_packages.add(req)

    # Calculate depth using BFS
    def calculate_max_depth() -> int:
        if not dep_graph:
            return 0

        # Find root nodes (packages not required by others)
        required_by_others = set()
        for deps in dep_graph.values():
            required_by_others.update(deps)

        roots = [pkg for pkg in dep_graph if pkg not in required_by_others]

        if not roots:
            # All packages are interdependent (circular), use first package
            roots = [list(dep_graph.keys())[0]]

        max_d = 0
        for root in roots:
            visited = set()
            queue = [(root, 0)]

            while queue:
                node, depth = queue.pop(0)
                if node in visited:
                    continue

                visited.add(node)
                max_d = max(max_d, depth)

                for child in dep_graph.get(node, []):
                    if child not in visited:
                        queue.append((child, depth + 1))

        return max_d

    max_depth = calculate_max_depth()

    # Find leaf packages (no dependencies)
    leaf_count = sum(1 for deps in dep_graph.values() if not deps)

    # Find root packages
    required_by_others = set()
    for deps in dep_graph.values():
        required_by_others.update(deps)
    root_count = len([pkg for pkg in dep_graph if pkg not in required_by_others])

    # Calculate average dependencies
    total_deps = sum(len(deps) for deps in dep_graph.values())
    avg_deps = total_deps / len(dep_graph) if dep_graph else 0

    return {
        "max_depth": str(max_depth),
        "total_packages": str(len(all_packages)),
        "leaf_packages": str(leaf_count),
        "root_packages": str(root_count),
        "tree_structure": json.dumps(dep_graph),
        "average_dependencies": f"{avg_deps:.2f}",
    }


@strands_tool
def find_unused_dependencies(
    dependencies_json: str, imports_json: str
) -> dict[str, str]:
    """Find dependencies that are declared but not imported/used.

    Compares declared dependencies against actual imports to identify
    potentially unused packages.

    Args:
        dependencies_json: JSON string of declared dependencies
        imports_json: JSON string of actual imports found in code

    Returns:
        Dictionary with:
        - has_unused: "true" if unused dependencies found
        - unused_count: Number of unused dependencies
        - unused_packages: JSON array of unused package names
        - usage_percentage: Percentage of dependencies actually used
        - suggestions: Recommendations for cleanup

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty or invalid JSON

    Example:
        >>> deps = '["requests", "django", "unused-lib"]'
        >>> imports = '["requests", "django"]'
        >>> result = find_unused_dependencies(deps, imports)
        >>> result["unused_count"]
        '1'
    """
    if not isinstance(dependencies_json, str):
        raise TypeError("dependencies_json must be a string")
    if not isinstance(imports_json, str):
        raise TypeError("imports_json must be a string")
    if not dependencies_json.strip():
        raise ValueError("dependencies_json cannot be empty")
    if not imports_json.strip():
        raise ValueError("imports_json cannot be empty")

    try:
        dependencies = json.loads(dependencies_json)
        imports = json.loads(imports_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    # Normalize package names (handle common transformations)
    def normalize_name(name: str) -> str:
        return name.lower().replace("-", "_").replace(".", "_")

    import_names = {normalize_name(i) for i in imports}

    # Find unused dependencies
    unused = [d for d in dependencies if normalize_name(d) not in import_names]

    usage_pct = (
        ((len(dependencies) - len(unused)) / len(dependencies) * 100)
        if dependencies
        else 100
    )

    suggestions = []
    if unused:
        suggestions.append("Consider removing unused dependencies to reduce bloat")
        suggestions.append("Verify if packages are used dynamically or in tests")
        suggestions.append("Check if imports use different names than package names")

    return {
        "has_unused": "true" if unused else "false",
        "unused_count": str(len(unused)),
        "unused_packages": json.dumps(unused),
        "usage_percentage": f"{usage_pct:.1f}",
        "suggestions": json.dumps(suggestions),
    }


@strands_tool
def identify_circular_dependency_chains(dependency_graph_json: str) -> dict[str, str]:
    """Identify circular dependency chains in package graph.

    Uses depth-first search to detect cycles in the dependency graph.
    Reports all circular chains found and affected packages.

    Args:
        dependency_graph_json: JSON string of dependency graph (package: [dependencies])

    Returns:
        Dictionary with:
        - has_circular: "true" if circular dependencies found
        - cycle_count: Number of circular dependency chains
        - cycles: JSON array of circular chains
        - affected_packages: JSON array of packages in cycles
        - severity: "high", "medium", or "low" based on cycle complexity

    Raises:
        TypeError: If dependency_graph_json is not a string
        ValueError: If dependency_graph_json is empty or invalid JSON

    Example:
        >>> graph = '{"A": ["B"], "B": ["C"], "C": ["A"]}'
        >>> result = identify_circular_dependency_chains(graph)
        >>> result["has_circular"]
        'true'
    """
    if not isinstance(dependency_graph_json, str):
        raise TypeError("dependency_graph_json must be a string")
    if not dependency_graph_json.strip():
        raise ValueError("dependency_graph_json cannot be empty")

    try:
        graph = json.loads(dependency_graph_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    # DFS to detect cycles
    def find_cycles() -> list[list[str]]:
        cycles = []
        visited = set()
        rec_stack = set()
        path: list[str] = []

        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles

    cycles = find_cycles()

    # Remove duplicate cycles
    unique_cycles = []
    seen_cycles = set()
    for cycle in cycles:
        # Normalize cycle for comparison
        min_idx = cycle.index(min(cycle))
        normalized = tuple(cycle[min_idx:] + cycle[:min_idx])
        if normalized not in seen_cycles:
            seen_cycles.add(normalized)
            unique_cycles.append(cycle)

    # Get affected packages
    affected = list({pkg for cycle in unique_cycles for pkg in cycle})

    # Determine severity
    if not unique_cycles:
        severity = "none"
    elif len(unique_cycles) > 5 or any(len(c) > 5 for c in unique_cycles):
        severity = "high"
    elif len(unique_cycles) > 2:
        severity = "medium"
    else:
        severity = "low"

    return {
        "has_circular": "true" if unique_cycles else "false",
        "cycle_count": str(len(unique_cycles)),
        "cycles": json.dumps(unique_cycles),
        "affected_packages": json.dumps(affected),
        "severity": severity,
    }


@strands_tool
def check_outdated_dependencies(
    packages_json: str, current_versions_json: str
) -> dict[str, str]:
    """Check for outdated dependencies with known security issues.

    Compares installed package versions against current/latest versions
    to identify outdated packages that may have security vulnerabilities.

    Args:
        packages_json: JSON string of installed packages with versions
        current_versions_json: JSON string of current/latest versions

    Returns:
        Dictionary with:
        - has_outdated: "true" if outdated packages found
        - outdated_count: Number of outdated packages
        - outdated_packages: JSON array of outdated package details
        - security_risk_count: Number with known vulnerabilities
        - update_priority: "high", "medium", or "low"
        - suggestions: Update recommendations

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty or invalid JSON

    Example:
        >>> installed = '[{"name": "lib", "version": "1.0.0"}]'
        >>> current = '[{"name": "lib", "version": "2.0.0"}]'
        >>> result = check_outdated_dependencies(installed, current)
        >>> result["has_outdated"]
        'true'
    """
    if not isinstance(packages_json, str):
        raise TypeError("packages_json must be a string")
    if not isinstance(current_versions_json, str):
        raise TypeError("current_versions_json must be a string")
    if not packages_json.strip():
        raise ValueError("packages_json cannot be empty")
    if not current_versions_json.strip():
        raise ValueError("current_versions_json cannot be empty")

    try:
        packages = json.loads(packages_json)
        current_versions = json.loads(current_versions_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    # Build current versions map
    current_map = {pkg["name"]: pkg["version"] for pkg in current_versions}

    # Find outdated packages
    outdated = []
    security_risk = 0

    for pkg in packages:
        name = pkg.get("name", "")
        installed_version = pkg.get("version", "")
        current_version = current_map.get(name, "")

        if current_version and installed_version != current_version:
            # Simple version comparison (assumes semver)
            outdated.append(
                {
                    "name": name,
                    "installed": installed_version,
                    "current": current_version,
                }
            )

            # Heuristic: major version behind = potential security risk
            try:
                installed_major = int(installed_version.split(".")[0])
                current_major = int(current_version.split(".")[0])
                if current_major > installed_major:
                    security_risk += 1
            except (ValueError, IndexError):
                pass

    # Determine update priority
    if security_risk > 5:
        priority = "high"
    elif security_risk > 2 or len(outdated) > 10:
        priority = "medium"
    else:
        priority = "low"

    suggestions = []
    if outdated:
        suggestions.append("Update outdated packages to latest versions")
        if security_risk > 0:
            suggestions.append(
                f"{security_risk} package(s) may have security vulnerabilities"
            )
        suggestions.append("Review changelogs before updating")

    return {
        "has_outdated": "true" if outdated else "false",
        "outdated_count": str(len(outdated)),
        "outdated_packages": json.dumps(outdated),
        "security_risk_count": str(security_risk),
        "update_priority": priority,
        "suggestions": json.dumps(suggestions),
    }


@strands_tool
def analyze_security_advisories(
    packages_json: str, advisories_json: str
) -> dict[str, str]:
    """Analyze packages against known security advisories.

    Cross-references installed packages with security advisory databases
    to identify known vulnerabilities (CVEs).

    Args:
        packages_json: JSON string of installed packages
        advisories_json: JSON string of security advisories with package/version/CVE

    Returns:
        Dictionary with:
        - has_vulnerabilities: "true" if vulnerabilities found
        - vulnerability_count: Number of vulnerabilities
        - critical_count: Number of critical severity issues
        - high_count: Number of high severity issues
        - affected_packages: JSON array of affected packages with CVE details
        - remediation_steps: JSON array of recommended fixes

    Raises:
        TypeError: If arguments are not strings
        ValueError: If arguments are empty or invalid JSON

    Example:
        >>> pkgs = '[{"name": "lib", "version": "1.0.0"}]'
        >>> advisories = '[{"package": "lib", "version": "1.0.0", "cve": "CVE-2023-1234"}]'
        >>> result = analyze_security_advisories(pkgs, advisories)
        >>> result["has_vulnerabilities"]
        'true'
    """
    if not isinstance(packages_json, str):
        raise TypeError("packages_json must be a string")
    if not isinstance(advisories_json, str):
        raise TypeError("advisories_json must be a string")
    if not packages_json.strip():
        raise ValueError("packages_json cannot be empty")
    if not advisories_json.strip():
        raise ValueError("advisories_json cannot be empty")

    try:
        packages = json.loads(packages_json)
        advisories = json.loads(advisories_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    # Build package version map
    installed = {pkg["name"]: pkg.get("version", "") for pkg in packages}

    # Find matching vulnerabilities
    vulnerabilities = []
    critical_count = 0
    high_count = 0

    for advisory in advisories:
        pkg_name = advisory.get("package", "")
        affected_version = advisory.get("version", "")
        cve = advisory.get("cve", "")
        severity = advisory.get("severity", "").lower()

        if pkg_name in installed:
            if affected_version == installed[pkg_name] or affected_version == "*":
                vulnerabilities.append(
                    {
                        "package": pkg_name,
                        "version": installed[pkg_name],
                        "cve": cve,
                        "severity": severity,
                    }
                )

                if severity == "critical":
                    critical_count += 1
                elif severity == "high":
                    high_count += 1

    # Generate remediation steps
    remediation = []
    if vulnerabilities:
        remediation.append("Update vulnerable packages to patched versions")
        if critical_count > 0:
            remediation.append(
                f"URGENT: {critical_count} critical vulnerabilities require immediate attention"
            )
        remediation.append("Review security advisories for affected packages")
        remediation.append("Consider using automated dependency scanning tools")

    return {
        "has_vulnerabilities": "true" if vulnerabilities else "false",
        "vulnerability_count": str(len(vulnerabilities)),
        "critical_count": str(critical_count),
        "high_count": str(high_count),
        "affected_packages": json.dumps(vulnerabilities),
        "remediation_steps": json.dumps(remediation),
    }
