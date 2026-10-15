"""
Unit and offline tests for database URL normalization, Supabase configuration,
production SQLite rejection, and fresh database migration schema initialization.
"""

import os
import tempfile
import sqlite3
import pytest
from unittest.mock import patch

from app.db.url import normalize_database_url, get_async_db_config
from app.core.config import Settings
from app.main import lifespan, create_app
from alembic.config import Config
from alembic import command


# --- 1. URL Normalization Tests ---

def test_sqlite_url_normalization_preserved():
    urls = [
        "sqlite+aiosqlite:///./travel_planner.db",
        "sqlite+aiosqlite:///:memory:",
        "sqlite:///./travel_planner.db",
    ]
    for url in urls:
        assert normalize_database_url(url) == url
        normalized, connect_args, kwargs = get_async_db_config(url)
        assert normalized == url
        assert connect_args.get("check_same_thread") is False


def test_postgres_to_asyncpg_conversion():
    raw = "postgres://postgres:secret@db.projectref.supabase.co:5432/postgres"
    expected = "postgresql+asyncpg://postgres:secret@db.projectref.supabase.co:5432/postgres"
    assert normalize_database_url(raw) == expected


def test_postgresql_to_asyncpg_conversion():
    raw = "postgresql://postgres:secret@db.projectref.supabase.co:5432/postgres"
    expected = "postgresql+asyncpg://postgres:secret@db.projectref.supabase.co:5432/postgres"
    assert normalize_database_url(raw) == expected


def test_sslmode_query_param_stripping_and_handling():
    raw = "postgresql://postgres.ref:secret@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
    normalized, connect_args, kwargs = get_async_db_config(raw)

    # sslmode must be stripped from the URL query string for asyncpg
    assert "sslmode" not in normalized
    # But ssl must be set in connect_args
    assert connect_args.get("ssl") == "require"


def test_supabase_pooler_port_6543_statement_cache_disabled():
    raw = "postgresql://postgres.ref:secret@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    normalized, connect_args, engine_kwargs = get_async_db_config(raw)

    assert normalized.startswith("postgresql+asyncpg://")
    assert connect_args.get("statement_cache_size") == 0
    # Must NOT include prepared_statement_cache_size in engine_kwargs (it causes TypeError in create_engine)
    assert "prepared_statement_cache_size" not in engine_kwargs
    assert connect_args.get("ssl") == "require"


def test_supabase_pooler_engine_creation_succeeds_without_type_error():
    """Regression test: create_async_engine must not raise TypeError with prepared_statement_cache_size."""
    from app.db.session import _create_engine
    raw = "postgresql://postgres.ref:secret@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    # Must create engine successfully without raising:
    # TypeError: Invalid argument(s) 'prepared_statement_cache_size' sent to create_engine()
    engine = _create_engine(raw)
    assert engine is not None


def test_create_async_engine_receives_exact_valid_arguments_for_pooler():
    """Assert the exact arguments and connect_args passed to create_async_engine."""
    from app.db.session import _create_engine
    raw = "postgresql://postgres.ref:secret@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    with patch("app.db.session.create_async_engine") as mock_create_engine:
        _create_engine(raw)
        mock_create_engine.assert_called_once()
        args, kwargs = mock_create_engine.call_args

        # URL should be normalized to postgresql+asyncpg
        assert args[0] == "postgresql+asyncpg://postgres.ref:secret@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

        # connect_args must have asyncpg-specific statement_cache_size=0 and ssl='require'
        assert kwargs["connect_args"] == {
            "ssl": "require",
            "statement_cache_size": 0,
        }

        # SQLAlchemy engine kwargs must NOT contain prepared_statement_cache_size
        assert "prepared_statement_cache_size" not in kwargs
        assert kwargs["echo"] is False
        assert kwargs["pool_size"] == 20
        assert kwargs["max_overflow"] == 10
        assert kwargs["pool_pre_ping"] is True
        assert kwargs["pool_recycle"] == 3600


def test_supabase_direct_port_5432_config():
    from app.db.session import _create_engine
    raw = "postgresql://postgres:secret@db.myref.supabase.co:5432/postgres"
    normalized, connect_args, engine_kwargs = get_async_db_config(raw)

    assert normalized.startswith("postgresql+asyncpg://")
    assert connect_args.get("ssl") == "require"
    # Port 5432 is a direct PostgreSQL connection, statement cache not forcibly disabled
    assert "statement_cache_size" not in connect_args
    assert "prepared_statement_cache_size" not in engine_kwargs
    assert engine_kwargs.get("pool_pre_ping") is True

    # Engine creation succeeds without error
    engine = _create_engine(raw)
    assert engine is not None


# --- 2. Production SQLite Rejection & Development Compatibility ---

@pytest.mark.asyncio
async def test_production_sqlite_rejected():
    """In production, using SQLite must fail fast with RuntimeError."""
    prod_settings = Settings(
        app_env="production",
        database_url="sqlite+aiosqlite:///./ephemeral.db",
        jwt_secret_key="super-secret-production-key-must-be-32-chars-long",
        debug=False,
    )

    app = create_app()
    with patch("app.main.get_settings", return_value=prod_settings):
        with pytest.raises(RuntimeError) as exc_info:
            async with lifespan(app):
                pass
        assert "FATAL: Production environment detected" in str(exc_info.value)
        assert "SQLite DATABASE_URL" in str(exc_info.value)


@pytest.mark.asyncio
async def test_development_sqlite_allowed():
    """In development, SQLite must start cleanly without error."""
    dev_settings = Settings(
        app_env="development",
        database_url="sqlite+aiosqlite:///:memory:",
        debug=True,
    )

    app = create_app()
    with patch("app.main.get_settings", return_value=dev_settings):
        async with lifespan(app):
            # If we reach here, lifespan startup succeeded
            assert True


# --- 3. Fresh Database Migration Initialization Test ---

def test_fresh_database_schema_all_13_tables_created():
    """Tests that alembic upgrade head on a brand new empty database creates all 13 core tables."""
    temp_dir = tempfile.gettempdir()
    test_db_path = os.path.join(temp_dir, f"test_alembic_fresh_{os.getpid()}.db")
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{test_db_path}")

    try:
        # Run upgrade head on clean database
        command.upgrade(alembic_cfg, "head")

        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        created_tables = {row[0] for row in cursor.fetchall()}
        conn.close()

        expected_tables = {
            "users",
            "user_preferences",
            "travel_requests",
            "travel_runs",
            "transport_options",
            "accommodation_options",
            "activities",
            "itineraries",
            "itinerary_days",
            "itinerary_items",
            "memory_entries",
            "agent_events",
            "llm_usage_records",
            "alembic_version",
        }

        assert expected_tables.issubset(created_tables), f"Missing tables: {expected_tables - created_tables}"

    finally:
        if os.path.exists(test_db_path):
            try:
                os.remove(test_db_path)
            except Exception:
                pass


# --- 4. PostgreSQL & SQLite Boolean Defaults Compatibility Tests ---

def test_fresh_postgresql_schema_boolean_defaults_portable():
    """Verify that the initial schema migration generates valid PostgreSQL DDL with BOOLEAN DEFAULT true/false.

    Ensures that integer defaults ('1', '0') are not generated for Boolean columns on PostgreSQL,
    which would otherwise trigger PostgreSQL error:
    'column ... is of type boolean but default expression is of type integer'
    """
    import io
    import importlib.util
    import sqlalchemy as sa
    from sqlalchemy.dialects import postgresql
    from alembic.operations import Operations
    from alembic.runtime.migration import MigrationContext

    output_buffer = io.StringIO()

    def dump_sql(sql, *multiparams, **params):
        str_sql = str(sql.compile(dialect=postgresql.dialect())) if hasattr(sql, "compile") else str(sql)
        output_buffer.write(str_sql + ";\n")

    mock_engine = sa.create_mock_engine("postgresql://", dump_sql)
    ctx = MigrationContext.configure(mock_engine)

    # Load initial schema migration
    migration_path = os.path.join(
        os.path.dirname(__file__), "..", "migrations", "versions", "134b62b01968_initial_schema.py"
    )
    spec = importlib.util.spec_from_file_location("initial_schema_migration", migration_path)
    migration_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration_mod)

    with Operations.context(ctx):
        migration_mod.upgrade()

    generated_sql = output_buffer.getvalue()

    # Verify no integer defaults on Boolean columns
    assert "BOOLEAN DEFAULT 1" not in generated_sql, "PostgreSQL schema must not contain BOOLEAN DEFAULT 1"
    assert "BOOLEAN DEFAULT 0" not in generated_sql, "PostgreSQL schema must not contain BOOLEAN DEFAULT 0"
    assert "BOOLEAN DEFAULT '1'" not in generated_sql, "PostgreSQL schema must not contain BOOLEAN DEFAULT '1'"
    assert "BOOLEAN DEFAULT '0'" not in generated_sql, "PostgreSQL schema must not contain BOOLEAN DEFAULT '0'"

    # Verify expected boolean defaults are present
    assert "is_active BOOLEAN DEFAULT true" in generated_sql, "users.is_active must have DEFAULT true"
    assert "is_selected BOOLEAN DEFAULT false" in generated_sql, "is_selected must have DEFAULT false"
    assert "weather_dependency BOOLEAN DEFAULT false" in generated_sql, "activities.weather_dependency must have DEFAULT false"


def test_models_ddl_compilation_boolean_defaults():
    """Verify ORM models compile to correct Boolean expressions under both PostgreSQL and SQLite."""
    import sqlalchemy as sa
    from sqlalchemy.dialects import postgresql, sqlite
    from sqlalchemy.schema import CreateTable
    from app.models.user import User
    from app.models.travel_option import TransportOption
    from app.models.accommodation import AccommodationOption
    from app.models.activity import Activity

    models_and_columns = [
        (User, "is_active", "DEFAULT true", "DEFAULT 1"),
        (TransportOption, "is_selected", "DEFAULT false", "DEFAULT 0"),
        (AccommodationOption, "is_selected", "DEFAULT false", "DEFAULT 0"),
        (Activity, "weather_dependency", "DEFAULT false", "DEFAULT 0"),
    ]

    for model_cls, col_name, expected_pg, expected_sqlite in models_and_columns:
        table = model_cls.__table__
        pg_ddl = str(CreateTable(table).compile(dialect=postgresql.dialect()))
        sqlite_ddl = str(CreateTable(table).compile(dialect=sqlite.dialect()))

        # PostgreSQL assertions
        assert expected_pg in pg_ddl, f"{model_cls.__name__}.{col_name} should have {expected_pg} in PostgreSQL DDL"
        assert "DEFAULT 1" not in pg_ddl if expected_pg == "DEFAULT true" else True
        assert "DEFAULT 0" not in pg_ddl if expected_pg == "DEFAULT false" else True

        # SQLite assertions
        assert expected_sqlite in sqlite_ddl, f"{model_cls.__name__}.{col_name} should have {expected_sqlite} in SQLite DDL"


def test_fresh_sqlite_schema_boolean_defaults_applied():
    """Verify that on SQLite, inserting rows without Boolean values respects default values."""
    temp_dir = tempfile.gettempdir()
    test_db_path = os.path.join(temp_dir, f"test_bool_defaults_{os.getpid()}.db")
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{test_db_path}")

    try:
        command.upgrade(alembic_cfg, "head")

        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()

        # Insert user without is_active
        cursor.execute(
            "INSERT INTO users (id, email) VALUES (?, ?)",
            ("user-test-bool-1", "booltest@example.com"),
        )
        cursor.execute("SELECT is_active FROM users WHERE id = ?", ("user-test-bool-1",))
        is_active_val = cursor.fetchone()[0]
        assert is_active_val == 1, f"Expected is_active default to be 1 in SQLite, got {is_active_val}"

        # Insert travel_request & travel_run to satisfy FK
        cursor.execute(
            "INSERT INTO travel_requests (id, user_id, raw_request) VALUES (?, ?, ?)",
            ("req-1", "user-test-bool-1", "Trip to Paris"),
        )
        cursor.execute(
            "INSERT INTO travel_runs (id, request_id) VALUES (?, ?)",
            ("run-1", "req-1"),
        )

        # Insert transport_option without is_selected
        cursor.execute(
            "INSERT INTO transport_options (id, run_id, mode, provider, provider_type, origin, destination, price_per_person, total_price, source, source_type, retrieved_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("opt-1", "run-1", "flight", "AirFrance", "commercial", "NYC", "CDG", 500.0, 500.0, "mock", "api", "2026-10-15 12:00:00"),
        )
        cursor.execute("SELECT is_selected FROM transport_options WHERE id = ?", ("opt-1",))
        is_selected_val = cursor.fetchone()[0]
        assert is_selected_val == 0, f"Expected is_selected default to be 0 in SQLite, got {is_selected_val}"

        conn.close()
    finally:
        if os.path.exists(test_db_path):
            try:
                os.remove(test_db_path)
            except Exception:
                pass


def test_real_postgresql_integration_if_configured():
    """Run real migration and schema check if a live PostgreSQL database is supplied via environment variable."""
    pg_url = os.getenv("TEST_POSTGRESQL_URL")
    if not pg_url:
        pytest.skip("TEST_POSTGRESQL_URL not set; skipping live PostgreSQL integration test")

    import sqlalchemy as sa
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", pg_url)
    command.upgrade(alembic_cfg, "head")

    engine = sa.create_engine(pg_url)
    with engine.connect() as conn:
        result = conn.execute(sa.text("SELECT column_name, data_type, column_default FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'is_active'"))
        row = result.fetchone()
        assert row is not None
        assert row[1] == "boolean"
        assert "true" in str(row[2]).lower()
