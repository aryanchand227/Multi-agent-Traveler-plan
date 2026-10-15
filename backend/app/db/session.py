"""
Database session management.

Supports both PostgreSQL (production) and SQLite (development).
Uses async SQLAlchemy throughout. Key settings:
- expire_on_commit=False to prevent MissingGreenlet in async context
- pool_pre_ping=True for connection health checks (PostgreSQL only)
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.db.url import get_async_db_config

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _create_engine(database_url: str) -> AsyncEngine:
    """Create async engine with appropriate settings for the database type."""
    normalized_url, connect_args, kwargs = get_async_db_config(database_url)

    return create_async_engine(
        normalized_url,
        connect_args=connect_args,
        **kwargs,
    )


def get_engine() -> AsyncEngine:
    """Get or create the async database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = _create_engine(settings.database_url)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Initialize database — ensure all registered tables are created."""
    from app.db.base import Base  # noqa: F811
    import app.models  # noqa: F401 - registers all models

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose of the database engine on shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
