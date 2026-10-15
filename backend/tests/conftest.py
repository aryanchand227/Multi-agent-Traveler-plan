"""Test fixtures and configuration."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from app.main import app as fast_app
import app.models  # noqa: F401 — register all models


# Test database — in-memory SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_database():
    """Create tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a test database session."""
    async with TestSessionFactory() as session:
        yield session


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Get a test HTTP client."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestSessionFactory() as session:
            yield session

    fast_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=fast_app),
        base_url="http://test",
    ) as client:
        yield client

    fast_app.dependency_overrides.clear()
