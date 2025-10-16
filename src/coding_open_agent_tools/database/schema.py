"""SQLite schema management operations.

This module provides functions for inspecting and modifying database schemas,
including table inspection, column addition, and index creation.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from coding_open_agent_tools._decorators import strands_tool


@strands_tool
def inspect_schema(db_path: str) -> dict[str, Any]:
    """Inspect database schema and return structured information.

    Analyzes the database and returns information about all tables,
    their columns, data types, and indexes.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        Dictionary with:
        - tables: List of table dictionaries, each containing:
            - name: Table name
            - columns: List of column dictionaries with name, type, nullable, default
            - indexes: List of index names
            - row_count: Approximate number of rows
        - total_tables: Number of tables in database
        - database_size_bytes: Size of database file in bytes

    Raises:
        TypeError: If db_path is not a string
        ValueError: If db_path is empty or database doesn't exist
    """
    if not isinstance(db_path, str):
        raise TypeError("db_path must be a string")

    if not db_path.strip():
        raise ValueError("db_path cannot be empty")

    path = Path(db_path)
    if not path.exists():
        raise ValueError(f"Database does not exist: {db_path}")

    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()

        # Get all tables (excluding sqlite internal tables)
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        )
        table_names = [row["name"] for row in cursor.fetchall()]

        tables = []
        for table_name in table_names:
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")  # noqa: S608
            columns = []
            for col in cursor.fetchall():
                columns.append(
                    {
                        "name": col["name"],
                        "type": col["type"],
                        "nullable": "false" if col["notnull"] else "true",
                        "default": str(col["dflt_value"])
                        if col["dflt_value"] is not None
                        else "NULL",
                        "primary_key": "true" if col["pk"] else "false",
                    }
                )

            # Get indexes for this table
            cursor.execute(f"PRAGMA index_list({table_name})")  # noqa: S608
            indexes = [row["name"] for row in cursor.fetchall()]

            # Get approximate row count
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")  # noqa: S608
            row_count = cursor.fetchone()["count"]

            tables.append(
                {
                    "name": table_name,
                    "columns": columns,
                    "indexes": indexes,
                    "row_count": str(row_count),
                }
            )

        # Get database file size
        db_size = path.stat().st_size

        return {
            "tables": tables,
            "total_tables": str(len(tables)),
            "database_size_bytes": str(db_size),
        }
    finally:
        conn.close()


@strands_tool
def create_table_from_dict(
    db_path: str, table_name: str, columns: dict[str, str]
) -> dict[str, str]:
    """Create a table from a dictionary of column definitions.

    Creates a new table with columns specified in the dictionary.
    Column dictionary maps column names to SQL types (e.g., "INTEGER", "TEXT").

    Args:
        db_path: Path to the SQLite database file
        table_name: Name for the new table
        columns: Dictionary mapping column names to SQL types

    Returns:
        Dictionary with:
        - table_name: Name of created table
        - columns_created: Number of columns created
        - status: "success"

    Raises:
        TypeError: If arguments are wrong type
        ValueError: If arguments are empty or invalid
        sqlite3.Error: If table creation fails
    """
    if not isinstance(db_path, str):
        raise TypeError("db_path must be a string")
    if not isinstance(table_name, str):
        raise TypeError("table_name must be a string")
    if not isinstance(columns, dict):
        raise TypeError("columns must be a dictionary")

    if not db_path.strip():
        raise ValueError("db_path cannot be empty")
    if not table_name.strip():
        raise ValueError("table_name cannot be empty")
    if not columns:
        raise ValueError("columns cannot be empty")

    # Validate table name (alphanumeric and underscore only)
    if not table_name.replace("_", "").isalnum():
        raise ValueError(
            "table_name must contain only alphanumeric characters and underscores"
        )

    path = Path(db_path)
    if not path.exists():
        raise ValueError(f"Database does not exist: {db_path}")

    # Build CREATE TABLE statement
    column_defs = []
    for col_name, col_type in columns.items():
        # Validate column name
        if not col_name.replace("_", "").isalnum():
            raise ValueError(
                f"Column name '{col_name}' must contain only alphanumeric characters and underscores"
            )
        column_defs.append(f"{col_name} {col_type}")

    create_sql = f"CREATE TABLE {table_name} ({', '.join(column_defs)})"

    conn = sqlite3.connect(str(path))
    try:
        cursor = conn.cursor()
        cursor.execute(create_sql)
        conn.commit()

        return {
            "table_name": table_name,
            "columns_created": str(len(columns)),
            "status": "success",
        }
    finally:
        conn.close()


@strands_tool
def add_column(
    db_path: str, table_name: str, column_name: str, column_type: str
) -> dict[str, str]:
    """Add a new column to an existing table.

    Adds a new column with the specified type to an existing table.
    Note: SQLite limitations mean the new column cannot have a NOT NULL
    constraint unless a default value is provided.

    Args:
        db_path: Path to the SQLite database file
        table_name: Name of the existing table
        column_name: Name for the new column
        column_type: SQL type for the column (e.g., "TEXT", "INTEGER DEFAULT 0")

    Returns:
        Dictionary with:
        - table_name: Name of the modified table
        - column_name: Name of the added column
        - column_type: Type of the added column
        - status: "success"

    Raises:
        TypeError: If arguments are wrong type
        ValueError: If arguments are empty or invalid
        sqlite3.Error: If column addition fails
    """
    if not isinstance(db_path, str):
        raise TypeError("db_path must be a string")
    if not isinstance(table_name, str):
        raise TypeError("table_name must be a string")
    if not isinstance(column_name, str):
        raise TypeError("column_name must be a string")
    if not isinstance(column_type, str):
        raise TypeError("column_type must be a string")

    if not db_path.strip():
        raise ValueError("db_path cannot be empty")
    if not table_name.strip():
        raise ValueError("table_name cannot be empty")
    if not column_name.strip():
        raise ValueError("column_name cannot be empty")
    if not column_type.strip():
        raise ValueError("column_type cannot be empty")

    # Validate names
    if not table_name.replace("_", "").isalnum():
        raise ValueError(
            "table_name must contain only alphanumeric characters and underscores"
        )
    if not column_name.replace("_", "").isalnum():
        raise ValueError(
            "column_name must contain only alphanumeric characters and underscores"
        )

    path = Path(db_path)
    if not path.exists():
        raise ValueError(f"Database does not exist: {db_path}")

    alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"

    conn = sqlite3.connect(str(path))
    try:
        cursor = conn.cursor()
        cursor.execute(alter_sql)
        conn.commit()

        return {
            "table_name": table_name,
            "column_name": column_name,
            "column_type": column_type,
            "status": "success",
        }
    finally:
        conn.close()


@strands_tool
def create_index(
    db_path: str, table_name: str, column_names: list[str], index_name: str = ""
) -> dict[str, str]:
    """Create an index on one or more columns.

    Creates an index to speed up queries on the specified columns.
    If index_name is not provided, generates one automatically.

    Args:
        db_path: Path to the SQLite database file
        table_name: Name of the table to index
        column_names: List of column names to include in index
        index_name: Optional name for the index (auto-generated if empty)

    Returns:
        Dictionary with:
        - index_name: Name of the created index
        - table_name: Table the index was created on
        - columns: Comma-separated list of indexed columns
        - status: "success"

    Raises:
        TypeError: If arguments are wrong type
        ValueError: If arguments are empty or invalid
        sqlite3.Error: If index creation fails
    """
    if not isinstance(db_path, str):
        raise TypeError("db_path must be a string")
    if not isinstance(table_name, str):
        raise TypeError("table_name must be a string")
    if not isinstance(column_names, list):
        raise TypeError("column_names must be a list")
    if not isinstance(index_name, str):
        raise TypeError("index_name must be a string")

    if not db_path.strip():
        raise ValueError("db_path cannot be empty")
    if not table_name.strip():
        raise ValueError("table_name cannot be empty")
    if not column_names:
        raise ValueError("column_names cannot be empty")

    # Validate table name
    if not table_name.replace("_", "").isalnum():
        raise ValueError(
            "table_name must contain only alphanumeric characters and underscores"
        )

    # Validate column names
    for col_name in column_names:
        if not isinstance(col_name, str) or not col_name.strip():
            raise ValueError("All column names must be non-empty strings")
        if not col_name.replace("_", "").isalnum():
            raise ValueError(
                f"Column name '{col_name}' must contain only alphanumeric characters and underscores"
            )

    path = Path(db_path)
    if not path.exists():
        raise ValueError(f"Database does not exist: {db_path}")

    # Generate index name if not provided
    if not index_name.strip():
        index_name = f"idx_{table_name}_{'_'.join(column_names)}"

    # Validate index name
    if not index_name.replace("_", "").isalnum():
        raise ValueError(
            "index_name must contain only alphanumeric characters and underscores"
        )

    columns_str = ", ".join(column_names)
    create_index_sql = f"CREATE INDEX {index_name} ON {table_name} ({columns_str})"

    conn = sqlite3.connect(str(path))
    try:
        cursor = conn.cursor()
        cursor.execute(create_index_sql)
        conn.commit()

        return {
            "index_name": index_name,
            "table_name": table_name,
            "columns": columns_str,
            "status": "success",
        }
    finally:
        conn.close()
