"""Health endpoint tests."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Test health endpoint returns healthy status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data
    assert "database" in data
    assert "llm_provider" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_check_contains_mock_info(client: AsyncClient) -> None:
    """Test health endpoint reports mock provider status."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert "mock_providers" in data
