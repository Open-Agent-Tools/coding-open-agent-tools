"""Tests for the database module (SQLite operations)."""

import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from coding_open_agent_tools.database import (
    add_column,
    backup_database,
    build_delete_query,
    build_insert_query,
    build_select_query,
    build_update_query,
    create_index,
    create_sqlite_database,
    create_table_from_dict,
    escape_sql_identifier,
    execute_many,
    execute_query,
    export_to_json,
    fetch_all,
    fetch_one,
    import_from_json,
    inspect_schema,
    validate_sql_query,
)


# Fixtures
@pytest.fixture
def temp_db():
    """Create a temporary database file path (file not created yet)."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    # Delete the file immediately so tests can create it
    Path(db_path).unlink()
    yield db_path
    # Clean up after test
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def temp_json():
    """Create a temporary JSON file."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        json_path = f.name
    yield json_path
    Path(json_path).unlink(missing_ok=True)


@pytest.fixture
def sample_db(temp_db):
    """Create a database with sample data."""
    create_sqlite_database(temp_db)
    execute_query(
        temp_db,
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)",
    )
    execute_query(temp_db, "INSERT INTO users (name, age) VALUES (?, ?)", ["Alice", 30])
    execute_query(temp_db, "INSERT INTO users (name, age) VALUES (?, ?)", ["Bob", 25])
    return temp_db


# Test: create_sqlite_database
def test_create_sqlite_database_success(temp_db):
    """Test successful database creation."""
    result = create_sqlite_database(temp_db)
    assert result["status"] == "created"
    assert Path(result["database_path"]).exists()
    assert result["message"].startswith("Database created successfully")


def test_create_sqlite_database_already_exists(temp_db):
    """Test database creation when file already exists."""
    create_sqlite_database(temp_db)
    result = create_sqlite_database(temp_db)
    assert result["status"] == "already_exists"
    assert result["message"].startswith("Database already exists")


def test_create_sqlite_database_with_parent_dirs():
    """Test database creation with parent directory creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "subdir" / "test.db"
        result = create_sqlite_database(str(db_path))
        assert result["status"] == "created"
        assert db_path.exists()


def test_create_sqlite_database_empty_path():
    """Test database creation with empty path."""
    with pytest.raises(ValueError, match="db_path cannot be empty"):
        create_sqlite_database("")


def test_create_sqlite_database_invalid_type():
    """Test database creation with invalid type."""
    with pytest.raises(TypeError, match="db_path must be a string"):
        create_sqlite_database(123)  # type: ignore[arg-type]


# Test: execute_query
def test_execute_query_insert(sample_db):
    """Test INSERT query execution."""
    result = execute_query(
        sample_db, "INSERT INTO users (name, age) VALUES (?, ?)", ["Charlie", 35]
    )
    assert result["status"] == "success"
    assert int(result["rows_affected"]) == 1
    assert int(result["last_row_id"]) > 0


def test_execute_query_update(sample_db):
    """Test UPDATE query execution."""
    result = execute_query(
        sample_db, "UPDATE users SET age = ? WHERE name = ?", [31, "Alice"]
    )
    assert result["status"] == "success"
    assert int(result["rows_affected"]) == 1


def test_execute_query_delete(sample_db):
    """Test DELETE query execution."""
    result = execute_query(sample_db, "DELETE FROM users WHERE name = ?", ["Bob"])
    assert result["status"] == "success"
    assert int(result["rows_affected"]) == 1


def test_execute_query_create_table(temp_db):
    """Test CREATE TABLE execution."""
    create_sqlite_database(temp_db)
    result = execute_query(temp_db, "CREATE TABLE test (id INTEGER, name TEXT)")
    assert result["status"] == "success"


def test_execute_query_empty_query(sample_db):
    """Test query execution with empty query."""
    with pytest.raises(ValueError, match="query cannot be empty"):
        execute_query(sample_db, "")


def test_execute_query_invalid_db(temp_db):
    """Test query execution on non-existent database."""
    with pytest.raises(ValueError, match="Database does not exist"):
        execute_query(temp_db, "SELECT 1")


def test_execute_query_invalid_types():
    """Test query execution with invalid types."""
    with pytest.raises(TypeError, match="db_path must be a string"):
        execute_query(123, "SELECT 1")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="query must be a string"):
        execute_query("test.db", 123)  # type: ignore[arg-type]


# Test: execute_many
def test_execute_many_success(sample_db):
    """Test batch execution."""
    result = execute_many(
        sample_db,
        "INSERT INTO users (name, age) VALUES (?, ?)",
        [["David", 40], ["Eve", 28], ["Frank", 33]],
    )
    assert result["status"] == "success"
    assert result["executions_count"] == "3"
    assert int(result["total_rows_affected"]) == 3


def test_execute_many_empty_list(sample_db):
    """Test batch execution with empty parameter list."""
    with pytest.raises(ValueError, match="parameters_list cannot be empty"):
        execute_many(sample_db, "INSERT INTO users (name, age) VALUES (?, ?)", [])


def test_execute_many_invalid_types():
    """Test batch execution with invalid types."""
    with pytest.raises(TypeError, match="parameters_list must be a list"):
        execute_many("test.db", "SELECT 1", "invalid")  # type: ignore[arg-type]


# Test: fetch_all
def test_fetch_all_success(sample_db):
    """Test fetching all rows."""
    result = fetch_all(sample_db, "SELECT * FROM users")
    assert int(result["row_count"]) == 2
    assert len(result["rows"]) == 2
    assert result["columns"] == ["id", "name", "age"]
    assert result["rows"][0]["name"] == "Alice"


def test_fetch_all_with_parameters(sample_db):
    """Test fetch_all with parameters."""
    result = fetch_all(sample_db, "SELECT * FROM users WHERE age > ?", [26])
    assert int(result["row_count"]) == 1
    assert result["rows"][0]["name"] == "Alice"


def test_fetch_all_empty_result(sample_db):
    """Test fetch_all with no matching rows."""
    result = fetch_all(sample_db, "SELECT * FROM users WHERE age > 100")
    assert result["row_count"] == "0"
    assert result["rows"] == []
    assert result["columns"] == []


def test_fetch_all_invalid_query(sample_db):
    """Test fetch_all with invalid SQL."""
    with pytest.raises(sqlite3.OperationalError):
        fetch_all(sample_db, "SELECT * FROM nonexistent")


# Test: fetch_one
def test_fetch_one_success(sample_db):
    """Test fetching single row."""
    result = fetch_one(sample_db, "SELECT * FROM users WHERE name = ?", ["Alice"])
    assert result["found"] == "true"
    assert result["row"]["name"] == "Alice"  # type: ignore[index]
    assert result["columns"] == ["id", "name", "age"]


def test_fetch_one_not_found(sample_db):
    """Test fetch_one with no matching row."""
    result = fetch_one(sample_db, "SELECT * FROM users WHERE name = ?", ["Zoe"])
    assert result["found"] == "false"
    assert result["row"] is None
    assert result["columns"] == []


def test_fetch_one_multiple_matches(sample_db):
    """Test fetch_one returns only first match."""
    result = fetch_one(sample_db, "SELECT * FROM users")
    assert result["found"] == "true"
    assert result["row"] is not None


# Test: inspect_schema
def test_inspect_schema_success(sample_db):
    """Test schema inspection."""
    result = inspect_schema(sample_db)
    assert int(result["total_tables"]) == 1
    assert len(result["tables"]) == 1
    table = result["tables"][0]
    assert table["name"] == "users"
    assert len(table["columns"]) == 3
    assert table["columns"][0]["name"] == "id"
    assert table["columns"][1]["name"] == "name"
    assert int(table["row_count"]) == 2


def test_inspect_schema_with_indexes(sample_db):
    """Test schema inspection with indexes."""
    execute_query(sample_db, "CREATE INDEX idx_name ON users(name)")
    result = inspect_schema(sample_db)
    table = result["tables"][0]
    assert "idx_name" in table["indexes"]


def test_inspect_schema_empty_database(temp_db):
    """Test schema inspection on empty database."""
    create_sqlite_database(temp_db)
    result = inspect_schema(temp_db)
    assert result["total_tables"] == "0"
    assert result["tables"] == []


def test_inspect_schema_invalid_db():
    """Test schema inspection on non-existent database."""
    with pytest.raises(ValueError, match="Database does not exist"):
        inspect_schema("/nonexistent/path.db")


# Test: create_table_from_dict
def test_create_table_from_dict_success(temp_db):
    """Test table creation from dictionary."""
    create_sqlite_database(temp_db)
    result = create_table_from_dict(
        temp_db,
        "products",
        {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "price": "REAL"},
    )
    assert result["status"] == "success"
    assert result["table_name"] == "products"
    assert result["columns_created"] == "3"


def test_create_table_from_dict_invalid_table_name(temp_db):
    """Test table creation with invalid table name."""
    create_sqlite_database(temp_db)
    with pytest.raises(
        ValueError, match="must contain only alphanumeric characters and underscores"
    ):
        create_table_from_dict(temp_db, "invalid-name", {"id": "INTEGER"})


def test_create_table_from_dict_invalid_column_name(temp_db):
    """Test table creation with invalid column name."""
    create_sqlite_database(temp_db)
    with pytest.raises(
        ValueError, match="must contain only alphanumeric characters and underscores"
    ):
        create_table_from_dict(temp_db, "test", {"invalid-col": "TEXT"})


def test_create_table_from_dict_empty_columns(temp_db):
    """Test table creation with empty columns."""
    create_sqlite_database(temp_db)
    with pytest.raises(ValueError, match="columns cannot be empty"):
        create_table_from_dict(temp_db, "test", {})


# Test: add_column
def test_add_column_success(sample_db):
    """Test adding column to table."""
    result = add_column(sample_db, "users", "email", "TEXT")
    assert result["status"] == "success"
    assert result["table_name"] == "users"
    assert result["column_name"] == "email"


def test_add_column_with_default(sample_db):
    """Test adding column with default value."""
    result = add_column(sample_db, "users", "active", "INTEGER DEFAULT 1")
    assert result["status"] == "success"


def test_add_column_invalid_table(sample_db):
    """Test adding column to non-existent table."""
    with pytest.raises(sqlite3.OperationalError):
        add_column(sample_db, "nonexistent", "col", "TEXT")


def test_add_column_invalid_names(sample_db):
    """Test adding column with invalid names."""
    with pytest.raises(
        ValueError, match="must contain only alphanumeric characters and underscores"
    ):
        add_column(sample_db, "invalid-table", "col", "TEXT")
    with pytest.raises(
        ValueError, match="must contain only alphanumeric characters and underscores"
    ):
        add_column(sample_db, "users", "invalid-col", "TEXT")


# Test: create_index
def test_create_index_success(sample_db):
    """Test index creation."""
    result = create_index(sample_db, "users", ["name"], "idx_users_name")
    assert result["status"] == "success"
    assert result["index_name"] == "idx_users_name"
    assert result["table_name"] == "users"
    assert result["columns"] == "name"


def test_create_index_auto_name(sample_db):
    """Test index creation with auto-generated name."""
    result = create_index(sample_db, "users", ["name", "age"], "")
    assert result["status"] == "success"
    assert result["index_name"] == "idx_users_name_age"
    assert result["columns"] == "name, age"


def test_create_index_invalid_column(sample_db):
    """Test index creation with invalid column name."""
    with pytest.raises(
        ValueError, match="must contain only alphanumeric characters and underscores"
    ):
        create_index(sample_db, "users", ["invalid-col"], "")


def test_create_index_empty_columns(sample_db):
    """Test index creation with empty column list."""
    with pytest.raises(ValueError, match="column_names cannot be empty"):
        create_index(sample_db, "users", [], "")


# Test: escape_sql_identifier
def test_escape_sql_identifier_valid():
    """Test escaping valid identifiers."""
    assert escape_sql_identifier("valid_name") == "valid_name"
    assert escape_sql_identifier("table123") == "table123"
    assert escape_sql_identifier("_underscore") == "_underscore"


def test_escape_sql_identifier_invalid():
    """Test escaping invalid identifiers."""
    with pytest.raises(
        ValueError, match="must contain only alphanumeric characters and underscores"
    ):
        escape_sql_identifier("invalid-name")
    with pytest.raises(
        ValueError, match="must contain only alphanumeric characters and underscores"
    ):
        escape_sql_identifier("table.name")
    with pytest.raises(ValueError, match="cannot start with a number"):
        escape_sql_identifier("123table")


def test_escape_sql_identifier_empty():
    """Test escaping empty identifier."""
    with pytest.raises(ValueError, match="identifier cannot be empty"):
        escape_sql_identifier("")
    with pytest.raises(ValueError, match="identifier cannot be empty"):
        escape_sql_identifier("   ")


def test_escape_sql_identifier_invalid_type():
    """Test escaping with invalid type."""
    with pytest.raises(TypeError, match="identifier must be a string"):
        escape_sql_identifier(123)  # type: ignore[arg-type]


# Test: validate_sql_query
def test_validate_sql_query_valid():
    """Test validation of valid queries."""
    result = validate_sql_query("SELECT * FROM users WHERE id = ?")
    assert result["is_valid"] == "true"
    assert result["query_type"] == "SELECT"
    assert result["issues"] == []


def test_validate_sql_query_injection_patterns():
    """Test detection of SQL injection patterns."""
    result = validate_sql_query("SELECT * FROM users; DROP TABLE users")
    assert result["is_valid"] == "false"
    assert any("DROP TABLE" in issue for issue in result["issues"])

    result = validate_sql_query("SELECT * FROM users WHERE name='x' OR 1=1")
    assert result["is_valid"] == "false"
    assert any("Tautology" in issue for issue in result["issues"])

    result = validate_sql_query("SELECT * FROM users -- comment")
    assert result["is_valid"] == "false"
    assert any("comment" in issue for issue in result["issues"])


def test_validate_sql_query_unbalanced_quotes():
    """Test detection of unbalanced quotes."""
    result = validate_sql_query("SELECT * FROM users WHERE name = 'unclosed")
    assert result["is_valid"] == "false"
    assert "Unbalanced single quotes" in result["issues"]


def test_validate_sql_query_empty():
    """Test validation with empty query."""
    with pytest.raises(ValueError, match="query cannot be empty"):
        validate_sql_query("")


def test_validate_sql_query_types():
    """Test validation detects different query types."""
    assert validate_sql_query("INSERT INTO users VALUES (1)")["query_type"] == "INSERT"
    assert validate_sql_query("UPDATE users SET name = 'x'")["query_type"] == "UPDATE"
    assert validate_sql_query("DELETE FROM users")["query_type"] == "DELETE"
    assert validate_sql_query("CREATE TABLE test (id INT)")["query_type"] == "CREATE"


# Test: build_select_query
def test_build_select_query_basic():
    """Test building basic SELECT query."""
    result = build_select_query("users")
    assert result["query"] == "SELECT * FROM users"
    assert result["parameters"] == []
    assert result["column_count"] == "0"


def test_build_select_query_with_columns():
    """Test SELECT query with specific columns."""
    result = build_select_query("users", ["id", "name"])
    assert result["query"] == "SELECT id, name FROM users"
    assert result["column_count"] == "2"


def test_build_select_query_with_where():
    """Test SELECT query with WHERE clause."""
    result = build_select_query("users", None, {"name": "Alice", "age": 30})
    assert "WHERE" in result["query"]
    assert "name = ?" in result["query"]
    assert "age = ?" in result["query"]
    assert result["parameters"] == ["Alice", 30]


def test_build_select_query_with_order_by():
    """Test SELECT query with ORDER BY."""
    result = build_select_query("users", None, None, "name")
    assert result["query"] == "SELECT * FROM users ORDER BY name"


def test_build_select_query_with_limit():
    """Test SELECT query with LIMIT."""
    result = build_select_query("users", None, None, "", 10)
    assert result["query"] == "SELECT * FROM users LIMIT 10"


def test_build_select_query_full():
    """Test SELECT query with all options."""
    result = build_select_query("users", ["name", "age"], {"active": 1}, "name", 5)
    assert "SELECT name, age FROM users" in result["query"]
    assert "WHERE active = ?" in result["query"]
    assert "ORDER BY name" in result["query"]
    assert "LIMIT 5" in result["query"]
    assert result["parameters"] == [1]


def test_build_select_query_invalid_identifier():
    """Test SELECT with invalid identifier."""
    with pytest.raises(
        ValueError, match="must contain only alphanumeric characters and underscores"
    ):
        build_select_query("invalid-table")


# Test: build_insert_query
def test_build_insert_query_success():
    """Test building INSERT query."""
    result = build_insert_query("users", ["name", "age"], ["Alice", 30])
    assert result["query"] == "INSERT INTO users (name, age) VALUES (?, ?)"
    assert result["parameters"] == ["Alice", 30]
    assert result["column_count"] == "2"


def test_build_insert_query_mismatched_length():
    """Test INSERT with mismatched columns/values."""
    with pytest.raises(ValueError, match="must have same length"):
        build_insert_query("users", ["name", "age"], ["Alice"])


def test_build_insert_query_empty():
    """Test INSERT with empty columns/values."""
    with pytest.raises(ValueError, match="columns cannot be empty"):
        build_insert_query("users", [], [])


def test_build_insert_query_invalid_types():
    """Test INSERT with invalid types."""
    with pytest.raises(TypeError, match="columns must be a list"):
        build_insert_query("users", "name", ["Alice"])  # type: ignore[arg-type]


# Test: build_update_query
def test_build_update_query_success():
    """Test building UPDATE query."""
    result = build_update_query("users", {"name": "Alice"}, {"id": 1})
    assert result["query"] == "UPDATE users SET name = ? WHERE id = ?"
    assert result["parameters"] == ["Alice", 1]
    assert result["columns_updated"] == "1"


def test_build_update_query_multiple_fields():
    """Test UPDATE with multiple fields."""
    result = build_update_query("users", {"name": "Alice", "age": 30}, {"id": 1})
    assert "SET" in result["query"]
    assert "name = ?" in result["query"]
    assert "age = ?" in result["query"]
    assert result["parameters"] == ["Alice", 30, 1]


def test_build_update_query_no_where():
    """Test UPDATE without WHERE clause."""
    with pytest.raises(ValueError, match="WHERE conditions required"):
        build_update_query("users", {"name": "Alice"}, None)


def test_build_update_query_empty_updates():
    """Test UPDATE with empty updates."""
    with pytest.raises(ValueError, match="updates cannot be empty"):
        build_update_query("users", {}, {"id": 1})


# Test: build_delete_query
def test_build_delete_query_success():
    """Test building DELETE query."""
    result = build_delete_query("users", {"id": 1})
    assert result["query"] == "DELETE FROM users WHERE id = ?"
    assert result["parameters"] == [1]
    assert result["has_where_clause"] == "true"


def test_build_delete_query_multiple_conditions():
    """Test DELETE with multiple conditions."""
    result = build_delete_query("users", {"name": "Alice", "age": 30})
    assert "WHERE" in result["query"]
    assert "name = ?" in result["query"]
    assert "age = ?" in result["query"]
    assert result["parameters"] == ["Alice", 30]


def test_build_delete_query_no_where():
    """Test DELETE without WHERE clause."""
    with pytest.raises(ValueError, match="WHERE conditions required"):
        build_delete_query("users", None)


def test_build_delete_query_explicit_empty_dict():
    """Test DELETE with explicit empty dict."""
    with pytest.raises(ValueError, match="WHERE conditions required"):
        build_delete_query("users", {})


# Test: export_to_json
def test_export_to_json_success(sample_db, temp_json):
    """Test exporting table to JSON."""
    result = export_to_json(sample_db, "users", temp_json)
    assert result["status"] == "success"
    assert result["table_name"] == "users"
    assert result["rows_exported"] == "2"
    assert Path(result["export_file"]).exists()

    # Verify JSON content
    with open(temp_json, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 2
    assert data[0]["name"] == "Alice"


def test_export_to_json_empty_table(sample_db, temp_json):
    """Test exporting empty table."""
    execute_query(sample_db, "DELETE FROM users")
    result = export_to_json(sample_db, "users", temp_json)
    assert result["rows_exported"] == "0"

    with open(temp_json, encoding="utf-8") as f:
        data = json.load(f)
    assert data == []


def test_export_to_json_creates_parent_dirs(sample_db):
    """Test export creates parent directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "subdir" / "export.json"
        result = export_to_json(sample_db, "users", str(json_path))
        assert json_path.exists()
        assert result["status"] == "success"


def test_export_to_json_invalid_table(sample_db, temp_json):
    """Test export with non-existent table."""
    with pytest.raises(sqlite3.OperationalError):
        export_to_json(sample_db, "nonexistent", temp_json)


# Test: import_from_json
def test_import_from_json_success(sample_db, temp_json):
    """Test importing from JSON."""
    # Create JSON file
    data = [{"name": "Charlie", "age": 35}, {"name": "Diana", "age": 28}]
    with open(temp_json, "w", encoding="utf-8") as f:
        json.dump(data, f)

    result = import_from_json(sample_db, "users", temp_json, "false")
    assert result["status"] == "success"
    assert result["rows_imported"] == "2"
    assert result["cleared"] == "false"

    # Verify data
    rows = fetch_all(sample_db, "SELECT * FROM users")
    assert int(rows["row_count"]) == 4  # 2 original + 2 new


def test_import_from_json_with_clear(sample_db, temp_json):
    """Test importing with table clearing."""
    data = [{"name": "Charlie", "age": 35}]
    with open(temp_json, "w", encoding="utf-8") as f:
        json.dump(data, f)

    result = import_from_json(sample_db, "users", temp_json, "true")
    assert result["cleared"] == "true"

    rows = fetch_all(sample_db, "SELECT * FROM users")
    assert int(rows["row_count"]) == 1
    assert rows["rows"][0]["name"] == "Charlie"


def test_import_from_json_empty_file(sample_db, temp_json):
    """Test importing from empty JSON."""
    with open(temp_json, "w", encoding="utf-8") as f:
        json.dump([], f)

    result = import_from_json(sample_db, "users", temp_json, "false")
    assert result["rows_imported"] == "0"


def test_import_from_json_invalid_json(sample_db, temp_json):
    """Test importing invalid JSON."""
    with open(temp_json, "w", encoding="utf-8") as f:
        f.write("not valid json")

    with pytest.raises(json.JSONDecodeError):
        import_from_json(sample_db, "users", temp_json, "false")


def test_import_from_json_not_list(sample_db, temp_json):
    """Test importing non-list JSON."""
    with open(temp_json, "w", encoding="utf-8") as f:
        json.dump({"not": "a list"}, f)

    with pytest.raises(ValueError, match="must contain a list"):
        import_from_json(sample_db, "users", temp_json, "false")


def test_import_from_json_nonexistent_file(sample_db):
    """Test importing from non-existent file."""
    with pytest.raises(ValueError, match="JSON file does not exist"):
        import_from_json(sample_db, "users", "/nonexistent/file.json", "false")


# Test: backup_database
def test_backup_database_success(sample_db):
    """Test database backup."""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_path = Path(tmpdir) / "backup.db"
        result = backup_database(sample_db, str(backup_path))
        assert result["status"] == "success"
        assert backup_path.exists()
        assert result["original_size_bytes"] == result["backup_size_bytes"]


def test_backup_database_creates_parent_dirs(sample_db):
    """Test backup creates parent directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_path = Path(tmpdir) / "subdir" / "backup.db"
        result = backup_database(sample_db, str(backup_path))
        assert backup_path.exists()
        assert result["status"] == "success"


def test_backup_database_preserves_data(sample_db):
    """Test backup preserves data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_path = Path(tmpdir) / "backup.db"
        backup_database(sample_db, str(backup_path))

        # Verify backup has same data
        result = fetch_all(str(backup_path), "SELECT * FROM users")
        assert int(result["row_count"]) == 2


def test_backup_database_invalid_source():
    """Test backup with non-existent source."""
    with pytest.raises(ValueError, match="Database does not exist"):
        backup_database("/nonexistent/db.db", "/backup.db")


def test_backup_database_empty_path():
    """Test backup with empty path."""
    with pytest.raises(ValueError, match="backup_path cannot be empty"):
        backup_database("test.db", "")
