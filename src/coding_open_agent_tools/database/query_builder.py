"""Safe SQL query building functions.

This module provides functions for building parameterized SQL queries that prevent
SQL injection attacks. All functions return queries with placeholders (?) and
separate parameter lists.
"""

from __future__ import annotations

import re
from typing import Any

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def escape_sql_identifier(identifier: str) -> str:
    """Escape a SQL identifier (table/column name) for safe use.

    Validates and escapes identifiers to prevent SQL injection in cases where
    parameterized queries can't be used (e.g., table names, column names).

    Only allows alphanumeric characters and underscores. Does NOT add quotes.

    Args:
        identifier: Table name, column name, or other SQL identifier

    Returns:
        Validated identifier string (unchanged if valid)

    Raises:
        TypeError: If identifier is not a string
        ValueError: If identifier is empty or contains invalid characters
    """
    if not isinstance(identifier, str):
        raise TypeError("identifier must be a string")

    if not identifier.strip():
        raise ValueError("identifier cannot be empty")

    # Only allow alphanumeric and underscore
    if not identifier.replace("_", "").isalnum():
        raise ValueError(
            "SQL identifier must contain only alphanumeric characters and underscores"
        )

    # Don't allow starting with a number
    if identifier[0].isdigit():
        raise ValueError("SQL identifier cannot start with a number")

    return identifier


@strands_tool
def validate_sql_query(query: str) -> dict[str, Any]:
    """Validate a SQL query for safety and correctness.

    Performs basic validation to detect common SQL injection patterns
    and syntax issues. NOT a complete SQL parser, but catches obvious problems.

    Args:
        query: SQL query string to validate

    Returns:
        Dictionary with:
        - is_valid: "true" or "false"
        - issues: List of validation issues found (empty if valid)
        - query_type: Detected query type (SELECT, INSERT, UPDATE, DELETE, etc.)

    Raises:
        TypeError: If query is not a string
        ValueError: If query is empty
    """
    if not isinstance(query, str):
        raise TypeError("query must be a string")

    if not query.strip():
        raise ValueError("query cannot be empty")

    issues = []
    query_upper = query.strip().upper()

    # Detect query type
    query_type = "UNKNOWN"
    for qtype in ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"]:
        if query_upper.startswith(qtype):
            query_type = qtype
            break

    # Check for suspicious patterns (basic SQL injection detection)
    suspicious_patterns = [
        (r";\s*DROP\s+TABLE", "Potential DROP TABLE attack"),
        (r";\s*DELETE\s+FROM", "Potential DELETE attack"),
        (r"--", "SQL comment detected (potential injection)"),
        (r"/\*.*\*/", "SQL block comment detected"),
        (r"UNION\s+SELECT", "UNION SELECT detected (potential injection)"),
        (r"OR\s+1\s*=\s*1", "Tautology detected (OR 1=1)"),
        (r"OR\s+'1'\s*=\s*'1'", "Tautology detected (OR '1'='1')"),
    ]

    for pattern, message in suspicious_patterns:
        if re.search(pattern, query_upper):
            issues.append(message)

    # Check for unbalanced quotes
    single_quotes = query.count("'") - query.count("\\'")
    double_quotes = query.count('"') - query.count('\\"')

    if single_quotes % 2 != 0:
        issues.append("Unbalanced single quotes")
    if double_quotes % 2 != 0:
        issues.append("Unbalanced double quotes")

    is_valid = "true" if not issues else "false"

    return {
        "is_valid": is_valid,
        "issues": issues,
        "query_type": query_type,
    }


@strands_tool
def build_select_query(
    table_name: str,
    columns: list[str] | None = None,
    where_conditions: dict[str, Any] | None = None,
    order_by: str = "",
    limit: int = 0,
) -> dict[str, Any]:
    """Build a safe parameterized SELECT query.

    Constructs a SELECT query with optional WHERE, ORDER BY, and LIMIT clauses.
    Returns parameterized query to prevent SQL injection.

    Args:
        table_name: Name of the table to query
        columns: List of column names to select (None = SELECT *)
        where_conditions: Dictionary mapping column names to values for WHERE clause
        order_by: Column name to order by (empty = no ORDER BY)
        limit: Maximum number of rows to return (0 = no limit)

    Returns:
        Dictionary with:
        - query: SQL query string with ? placeholders
        - parameters: List of parameter values
        - column_count: Number of columns selected

    Raises:
        TypeError: If arguments are wrong type
        ValueError: If table_name is empty or invalid
    """
    if not isinstance(table_name, str):
        raise TypeError("table_name must be a string")

    table_name = escape_sql_identifier(table_name)

    # Build column list
    if columns is None or not columns:
        column_str = "*"
        column_count = 0  # Unknown for SELECT *
    else:
        validated_columns = [escape_sql_identifier(col) for col in columns]
        column_str = ", ".join(validated_columns)
        column_count = len(validated_columns)

    query = f"SELECT {column_str} FROM {table_name}"
    parameters: list[Any] = []

    # Add WHERE clause
    if where_conditions:
        where_parts = []
        for col_name, value in where_conditions.items():
            validated_col = escape_sql_identifier(col_name)
            where_parts.append(f"{validated_col} = ?")
            parameters.append(value)
        query += " WHERE " + " AND ".join(where_parts)

    # Add ORDER BY
    if order_by:
        validated_order = escape_sql_identifier(order_by)
        query += f" ORDER BY {validated_order}"

    # Add LIMIT
    if limit > 0:
        query += f" LIMIT {limit}"

    return {
        "query": query,
        "parameters": parameters,
        "column_count": str(column_count),
    }


@strands_tool
def build_insert_query(
    table_name: str, columns: list[str], values: list[Any]
) -> dict[str, Any]:
    """Build a safe parameterized INSERT query.

    Constructs an INSERT query with parameterized values to prevent SQL injection.

    Args:
        table_name: Name of the table to insert into
        columns: List of column names
        values: List of values corresponding to columns

    Returns:
        Dictionary with:
        - query: SQL query string with ? placeholders
        - parameters: List of parameter values
        - column_count: Number of columns in INSERT

    Raises:
        TypeError: If arguments are wrong type
        ValueError: If table_name is empty, or columns/values length mismatch
    """
    if not isinstance(table_name, str):
        raise TypeError("table_name must be a string")
    if not isinstance(columns, list):
        raise TypeError("columns must be a list")
    if not isinstance(values, list):
        raise TypeError("values must be a list")

    if not columns:
        raise ValueError("columns cannot be empty")
    if not values:
        raise ValueError("values cannot be empty")
    if len(columns) != len(values):
        raise ValueError(
            f"columns and values must have same length (got {len(columns)} vs {len(values)})"
        )

    table_name = escape_sql_identifier(table_name)
    validated_columns = [escape_sql_identifier(col) for col in columns]

    columns_str = ", ".join(validated_columns)
    placeholders = ", ".join(["?"] * len(values))

    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

    return {
        "query": query,
        "parameters": values,
        "column_count": str(len(columns)),
    }


@strands_tool
def build_update_query(
    table_name: str,
    updates: dict[str, Any],
    where_conditions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a safe parameterized UPDATE query.

    Constructs an UPDATE query with parameterized values to prevent SQL injection.
    Requires WHERE clause to prevent accidental full-table updates.

    Args:
        table_name: Name of the table to update
        updates: Dictionary mapping column names to new values
        where_conditions: Dictionary mapping column names to values for WHERE clause

    Returns:
        Dictionary with:
        - query: SQL query string with ? placeholders
        - parameters: List of parameter values
        - columns_updated: Number of columns being updated

    Raises:
        TypeError: If arguments are wrong type
        ValueError: If table_name is empty, updates is empty, or no WHERE clause
    """
    if not isinstance(table_name, str):
        raise TypeError("table_name must be a string")
    if not isinstance(updates, dict):
        raise TypeError("updates must be a dictionary")

    if not updates:
        raise ValueError("updates cannot be empty")
    if not where_conditions:
        raise ValueError(
            "WHERE conditions required for UPDATE to prevent accidental full-table updates"
        )

    table_name = escape_sql_identifier(table_name)

    # Build SET clause
    set_parts = []
    parameters: list[Any] = []
    for col_name, value in updates.items():
        validated_col = escape_sql_identifier(col_name)
        set_parts.append(f"{validated_col} = ?")
        parameters.append(value)

    query = f"UPDATE {table_name} SET {', '.join(set_parts)}"

    # Add WHERE clause
    if where_conditions:  # Will always be true due to check above, but keep for clarity
        where_parts = []
        for col_name, value in where_conditions.items():
            validated_col = escape_sql_identifier(col_name)
            where_parts.append(f"{validated_col} = ?")
            parameters.append(value)
        query += " WHERE " + " AND ".join(where_parts)

    return {
        "query": query,
        "parameters": parameters,
        "columns_updated": str(len(updates)),
    }


@strands_tool
def build_delete_query(
    table_name: str, where_conditions: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Build a safe parameterized DELETE query.

    Constructs a DELETE query with parameterized values to prevent SQL injection.
    Requires WHERE clause to prevent accidental full-table deletion.

    Args:
        table_name: Name of the table to delete from
        where_conditions: Dictionary mapping column names to values for WHERE clause

    Returns:
        Dictionary with:
        - query: SQL query string with ? placeholders
        - parameters: List of parameter values
        - has_where_clause: "true" if WHERE clause present

    Raises:
        TypeError: If arguments are wrong type
        ValueError: If table_name is empty or no WHERE clause provided
    """
    if not isinstance(table_name, str):
        raise TypeError("table_name must be a string")

    if not where_conditions:
        raise ValueError(
            "WHERE conditions required for DELETE to prevent accidental full-table deletion"
        )

    table_name = escape_sql_identifier(table_name)

    query = f"DELETE FROM {table_name}"
    parameters: list[Any] = []

    # Add WHERE clause
    if where_conditions:
        where_parts = []
        for col_name, value in where_conditions.items():
            validated_col = escape_sql_identifier(col_name)
            where_parts.append(f"{validated_col} = ?")
            parameters.append(value)
        query += " WHERE " + " AND ".join(where_parts)

    return {
        "query": query,
        "parameters": parameters,
        "has_where_clause": "true" if where_conditions else "false",
    }
