"""SQLite utility functions for data migration and backup.

This module provides helper functions for importing/exporting data to JSON
and creating database backups.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from coding_open_agent_tools._decorators import strands_tool

from .operations import execute_many, fetch_all


@strands_tool
def export_to_json(db_path: str, table_name: str, output_file: str) -> dict[str, str]:
    """Export table data to a JSON file.

    Exports all rows from the specified table to a JSON file. Each row is
    exported as a dictionary mapping column names to values.

    Args:
        db_path: Path to the SQLite database file
        table_name: Name of the table to export
        output_file: Path where JSON file should be written

    Returns:
        Dictionary with:
        - export_file: Absolute path to the created JSON file
        - rows_exported: Number of rows exported
        - table_name: Name of the exported table
        - status: "success"

    Raises:
        TypeError: If arguments are wrong type
        ValueError: If arguments are empty or database doesn't exist
        sqlite3.Error: If query execution fails
        OSError: If file writing fails
    """
    if not isinstance(db_path, str):
        raise TypeError("db_path must be a string")
    if not isinstance(table_name, str):
        raise TypeError("table_name must be a string")
    if not isinstance(output_file, str):
        raise TypeError("output_file must be a string")

    if not db_path.strip():
        raise ValueError("db_path cannot be empty")
    if not table_name.strip():
        raise ValueError("table_name cannot be empty")
    if not output_file.strip():
        raise ValueError("output_file cannot be empty")

    # Validate table name (alphanumeric and underscore only)
    if not table_name.replace("_", "").isalnum():
        raise ValueError(
            "table_name must contain only alphanumeric characters and underscores"
        )

    db = Path(db_path)
    if not db.exists():
        raise ValueError(f"Database does not exist: {db_path}")

    # Fetch all rows from table
    query = f"SELECT * FROM {table_name}"  # noqa: S608
    result = fetch_all(db_path, query)
    rows = result["rows"]

    # Write to JSON file
    output_path = Path(output_file).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    return {
        "export_file": str(output_path),
        "rows_exported": str(len(rows)),
        "table_name": table_name,
        "status": "success",
    }


@strands_tool
def import_from_json(
    db_path: str, table_name: str, json_file: str, clear_table: str = "false"
) -> dict[str, str]:
    """Import data from a JSON file into a table.

    Imports rows from a JSON file into the specified table. The JSON file
    should contain a list of dictionaries, where each dictionary maps
    column names to values.

    Args:
        db_path: Path to the SQLite database file
        table_name: Name of the table to import into
        json_file: Path to the JSON file to import
        clear_table: "true" to delete existing rows first, "false" to append

    Returns:
        Dictionary with:
        - rows_imported: Number of rows imported
        - table_name: Name of the table
        - cleared: "true" if table was cleared first, "false" otherwise
        - status: "success"

    Raises:
        TypeError: If arguments are wrong type
        ValueError: If arguments are empty, files don't exist, or JSON invalid
        sqlite3.Error: If query execution fails
    """
    if not isinstance(db_path, str):
        raise TypeError("db_path must be a string")
    if not isinstance(table_name, str):
        raise TypeError("table_name must be a string")
    if not isinstance(json_file, str):
        raise TypeError("json_file must be a string")
    if not isinstance(clear_table, str):
        raise TypeError("clear_table must be a string")

    if not db_path.strip():
        raise ValueError("db_path cannot be empty")
    if not table_name.strip():
        raise ValueError("table_name cannot be empty")
    if not json_file.strip():
        raise ValueError("json_file cannot be empty")
    if clear_table not in ("true", "false"):
        raise ValueError("clear_table must be 'true' or 'false'")

    # Validate table name
    if not table_name.replace("_", "").isalnum():
        raise ValueError(
            "table_name must contain only alphanumeric characters and underscores"
        )

    db = Path(db_path)
    if not db.exists():
        raise ValueError(f"Database does not exist: {db_path}")

    json_path = Path(json_file)
    if not json_path.exists():
        raise ValueError(f"JSON file does not exist: {json_file}")

    # Read JSON file
    with json_path.open("r", encoding="utf-8") as f:
        rows = json.load(f)

    if not isinstance(rows, list):
        raise ValueError("JSON file must contain a list of objects")

    if not rows:
        return {
            "rows_imported": "0",
            "table_name": table_name,
            "cleared": clear_table,
            "status": "success",
        }

    # Validate all rows are dictionaries
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError("All items in JSON list must be objects")

    # Clear table if requested
    if clear_table == "true":
        # Import here to avoid circular dependency
        from .operations import execute_query

        execute_query(db_path, f"DELETE FROM {table_name}")  # noqa: S608

    # Get column names from first row
    columns = list(rows[0].keys())

    # Validate column names
    for col in columns:
        if not col.replace("_", "").isalnum():
            raise ValueError(
                f"Column name '{col}' must contain only alphanumeric characters and underscores"
            )

    # Build INSERT query
    placeholders = ", ".join(["?"] * len(columns))
    column_str = ", ".join(columns)
    query = f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders})"  # noqa: S608

    # Convert rows to parameter lists
    parameters_list = [[row.get(col) for col in columns] for row in rows]

    # Execute batch insert
    execute_many(db_path, query, parameters_list)

    return {
        "rows_imported": str(len(rows)),
        "table_name": table_name,
        "cleared": clear_table,
        "status": "success",
    }


@strands_tool
def backup_database(db_path: str, backup_path: str) -> dict[str, str]:
    """Create a backup copy of the database.

    Creates a complete copy of the database file at the specified backup path.
    Preserves file metadata (timestamps, permissions).

    Args:
        db_path: Path to the SQLite database file
        backup_path: Path where backup file should be created

    Returns:
        Dictionary with:
        - backup_path: Absolute path to the backup file
        - original_size_bytes: Size of original database in bytes
        - backup_size_bytes: Size of backup file in bytes
        - status: "success"

    Raises:
        TypeError: If arguments are wrong type
        ValueError: If arguments are empty or database doesn't exist
        OSError: If backup creation fails
    """
    if not isinstance(db_path, str):
        raise TypeError("db_path must be a string")
    if not isinstance(backup_path, str):
        raise TypeError("backup_path must be a string")

    if not db_path.strip():
        raise ValueError("db_path cannot be empty")
    if not backup_path.strip():
        raise ValueError("backup_path cannot be empty")

    source = Path(db_path).resolve()
    if not source.exists():
        raise ValueError(f"Database does not exist: {db_path}")

    destination = Path(backup_path).resolve()

    # Create parent directories if needed
    destination.parent.mkdir(parents=True, exist_ok=True)

    # Get original size
    original_size = source.stat().st_size

    # Copy database file (preserves metadata)
    shutil.copy2(source, destination)

    # Get backup size
    backup_size = destination.stat().st_size

    return {
        "backup_path": str(destination),
        "original_size_bytes": str(original_size),
        "backup_size_bytes": str(backup_size),
        "status": "success",
    }
