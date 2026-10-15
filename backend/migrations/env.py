"""Alembic migration environment."""
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import get_settings
from app.db.base import Base
from app.db.url import get_async_db_config, normalize_database_url
# Import all models so they are registered with Base.metadata
import app.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    url_override = config.get_main_option("sqlalchemy.url")
    if url_override and url_override != "sqlite+aiosqlite:///./travel_planner.db":
        return url_override
    settings = get_settings()
    return settings.database_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = normalize_database_url(get_url())
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    raw_url = get_url()
    normalized_url, connect_args, _ = get_async_db_config(raw_url)

    # Handle SQLite vs PostgreSQL
    if "sqlite" in normalized_url:
        from sqlalchemy import create_engine
        sync_url = normalized_url.replace("sqlite+aiosqlite", "sqlite")
        connectable = create_engine(sync_url, connect_args=connect_args)
        with connectable.connect() as connection:
            do_run_migrations(connection)
    else:
        configuration = config.get_section(config.config_ini_section, {})
        configuration["sqlalchemy.url"] = normalized_url
        connectable = async_engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            connect_args=connect_args,
        )
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
