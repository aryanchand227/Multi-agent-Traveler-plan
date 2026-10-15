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
    assert engine_kwargs.get("prepared_statement_cache_size") == 0
    assert connect_args.get("ssl") == "require"


def test_supabase_direct_port_5432_config():
    raw = "postgresql://postgres:secret@db.myref.supabase.co:5432/postgres"
    normalized, connect_args, engine_kwargs = get_async_db_config(raw)

    assert normalized.startswith("postgresql+asyncpg://")
    assert connect_args.get("ssl") == "require"
    # Port 5432 is a direct PostgreSQL connection, statement cache not forcibly disabled
    assert "statement_cache_size" not in connect_args
    assert engine_kwargs.get("pool_pre_ping") is True


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
