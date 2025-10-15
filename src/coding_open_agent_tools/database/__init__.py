"""SQLite database operations module.

This module provides comprehensive SQLite database operations for agent memory,
structured data storage, and safe query building. All operations use pure stdlib
(sqlite3) with zero external dependencies.

Key features:
- Database operations (create, execute, fetch)
- Schema management and inspection
- Safe parameterized query building (prevents SQL injection)
- JSON import/export for data migration
- Database backup operations
"""

from .operations import (
    create_sqlite_database,
    execute_many,
    execute_query,
    fetch_all,
    fetch_one,
)
from .query_builder import (
    build_delete_query,
    build_insert_query,
    build_select_query,
    build_update_query,
    escape_sql_identifier,
    validate_sql_query,
)
from .schema import add_column, create_index, create_table_from_dict, inspect_schema
from .utils import backup_database, export_to_json, import_from_json

__all__ = [
    # Database operations
    "create_sqlite_database",
    "execute_query",
    "execute_many",
    "fetch_all",
    "fetch_one",
    # Schema management
    "inspect_schema",
    "create_table_from_dict",
    "add_column",
    "create_index",
    # Safe query building
    "build_select_query",
    "build_insert_query",
    "build_update_query",
    "build_delete_query",
    "escape_sql_identifier",
    "validate_sql_query",
    # Migration helpers
    "export_to_json",
    "import_from_json",
    "backup_database",
]
