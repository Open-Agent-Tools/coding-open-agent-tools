"""Core SQLite database operations.

This module provides fundamental database operations for creating databases,
executing queries, and fetching results. All operations use parameterized queries
to prevent SQL injection.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def create_sqlite_database(db_path: str) -> dict[str, str]:
    """Create a new SQLite database file.

    Creates a new SQLite database at the specified path. If the database
    already exists, connects to it. Creates parent directories if needed.

    Args:
        db_path: Path where database file should be created

    Returns:
        Dictionary with:
        - database_path: Absolute path to the created database
        - status: "created" or "already_exists"
        - message: Success message

    Raises:
        TypeError: If db_path is not a string
        ValueError: If db_path is empty
        PermissionError: If no permission to create database
    """
    if not isinstance(db_path, str):
        raise TypeError("db_path must be a string")

    if not db_path.strip():
        raise ValueError("db_path cannot be empty")

    # Convert to Path object
    path = Path(db_path).resolve()

    # Check if database already exists
    already_exists = path.exists()

    # Create parent directories if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create/connect to database (this creates the file if it doesn't exist)
    try:
        conn = sqlite3.connect(str(path))
        conn.close()
    except PermissionError as e:
        raise PermissionError(f"No permission to create database at {path}") from e

    status = "already_exists" if already_exists else "created"
    message = (
        f"Database already exists at {path}"
        if already_exists
        else f"Database created successfully at {path}"
    )

    return {
        "database_path": str(path),
        "status": status,
        "message": message,
    }


@strands_tool
def execute_query(
    db_path: str, query: str, parameters: list[Any] | None = None
) -> dict[str, str]:
    """Execute a SQL query (INSERT, UPDATE, DELETE, CREATE, etc.).

    Executes a SQL statement with optional parameters. Automatically commits
    changes. Use parameterized queries to prevent SQL injection.

    Args:
        db_path: Path to the SQLite database file
        query: SQL query to execute
        parameters: Optional list of parameters for parameterized query

    Returns:
        Dictionary with:
        - rows_affected: Number of rows affected by the query
        - last_row_id: ID of last inserted row (0 if not INSERT)
        - status: "success"

    Raises:
        TypeError: If db_path or query are not strings
        ValueError: If db_path or query are empty, or database doesn't exist
        sqlite3.Error: If SQL execution fails
    """
    if not isinstance(db_path, str):
        raise TypeError("db_path must be a string")
    if not isinstance(query, str):
        raise TypeError("query must be a string")

    if not db_path.strip():
        raise ValueError("db_path cannot be empty")
    if not query.strip():
        raise ValueError("query cannot be empty")

    path = Path(db_path)
    if not path.exists():
        raise ValueError(f"Database does not exist: {db_path}")

    params = parameters if parameters is not None else []

    conn = sqlite3.connect(str(path))
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

        return {
            "rows_affected": str(cursor.rowcount),
            "last_row_id": str(cursor.lastrowid),
            "status": "success",
        }
    finally:
        conn.close()


@strands_tool
def execute_many(
    db_path: str, query: str, parameters_list: list[list[Any]]
) -> dict[str, str]:
    """Execute a SQL query multiple times with different parameters.

    Efficiently executes the same query multiple times with different parameter
    sets. Useful for batch inserts. All executions happen in a single transaction.

    Args:
        db_path: Path to the SQLite database file
        query: SQL query to execute (typically INSERT)
        parameters_list: List of parameter lists for each execution

    Returns:
        Dictionary with:
        - total_rows_affected: Total number of rows affected
        - executions_count: Number of times query was executed
        - status: "success"

    Raises:
        TypeError: If arguments are wrong type
        ValueError: If db_path/query empty, database doesn't exist, or parameters_list empty
        sqlite3.Error: If SQL execution fails
    """
    if not isinstance(db_path, str):
        raise TypeError("db_path must be a string")
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    if not isinstance(parameters_list, list):
        raise TypeError("parameters_list must be a list")

    if not db_path.strip():
        raise ValueError("db_path cannot be empty")
    if not query.strip():
        raise ValueError("query cannot be empty")
    if not parameters_list:
        raise ValueError("parameters_list cannot be empty")

    path = Path(db_path)
    if not path.exists():
        raise ValueError(f"Database does not exist: {db_path}")

    conn = sqlite3.connect(str(path))
    try:
        cursor = conn.cursor()
        cursor.executemany(query, parameters_list)
        conn.commit()

        return {
            "total_rows_affected": str(cursor.rowcount),
            "executions_count": str(len(parameters_list)),
            "status": "success",
        }
    finally:
        conn.close()


@strands_tool
def fetch_all(
    db_path: str, query: str, parameters: list[Any] | None = None
) -> dict[str, Any]:
    """Fetch all rows from a SELECT query.

    Executes a SELECT query and returns all matching rows. Returns both
    column names and row data.

    Args:
        db_path: Path to the SQLite database file
        query: SELECT query to execute
        parameters: Optional list of parameters for parameterized query

    Returns:
        Dictionary with:
        - rows: List of row dictionaries (each dict maps column name to value)
        - row_count: Number of rows returned
        - columns: List of column names

    Raises:
        TypeError: If arguments are wrong type
        ValueError: If db_path/query empty or database doesn't exist
        sqlite3.Error: If SQL execution fails
    """
    if not isinstance(db_path, str):
        raise TypeError("db_path must be a string")
    if not isinstance(query, str):
        raise TypeError("query must be a string")

    if not db_path.strip():
        raise ValueError("db_path cannot be empty")
    if not query.strip():
        raise ValueError("query cannot be empty")

    path = Path(db_path)
    if not path.exists():
        raise ValueError(f"Database does not exist: {db_path}")

    params = parameters if parameters is not None else []

    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Convert Row objects to dictionaries
        row_dicts = [dict(row) for row in rows]
        columns = list(rows[0].keys()) if rows else []

        return {
            "rows": row_dicts,
            "row_count": str(len(rows)),
            "columns": columns,
        }
    finally:
        conn.close()


@strands_tool
def fetch_one(
    db_path: str, query: str, parameters: list[Any] | None = None
) -> dict[str, Any]:
    """Fetch a single row from a SELECT query.

    Executes a SELECT query and returns the first matching row. Returns None
    for the row if no matches found.

    Args:
        db_path: Path to the SQLite database file
        query: SELECT query to execute
        parameters: Optional list of parameters for parameterized query

    Returns:
        Dictionary with:
        - row: Dictionary mapping column names to values (None if no match)
        - found: "true" if row found, "false" otherwise
        - columns: List of column names (empty if no row found)

    Raises:
        TypeError: If arguments are wrong type
        ValueError: If db_path/query empty or database doesn't exist
        sqlite3.Error: If SQL execution fails
    """
    if not isinstance(db_path, str):
        raise TypeError("db_path must be a string")
    if not isinstance(query, str):
        raise TypeError("query must be a string")

    if not db_path.strip():
        raise ValueError("db_path cannot be empty")
    if not query.strip():
        raise ValueError("query cannot be empty")

    path = Path(db_path)
    if not path.exists():
        raise ValueError(f"Database does not exist: {db_path}")

    params = parameters if parameters is not None else []

    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()

        if row:
            return {
                "row": dict(row),
                "found": "true",
                "columns": list(row.keys()),
            }
        else:
            return {
                "row": None,
                "found": "false",
                "columns": [],
            }
    finally:
        conn.close()
