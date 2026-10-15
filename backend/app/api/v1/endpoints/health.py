"""Health check endpoint."""
from __future__ import annotations

import datetime

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Liveness probe — indicates whether the process is running."""
    settings = get_settings()
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "database": "sqlite" if settings.is_sqlite else "postgresql",
        "llm_provider": settings.llm_provider,
        "mock_providers": settings.use_mock_providers,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@router.get("/ready")
async def readiness_check() -> dict:
    """Readiness probe — verifies essential services (e.g. database) without consuming LLM quota."""
    from sqlalchemy import text
    from fastapi import HTTPException
    from app.db.session import get_session_factory

    settings = get_settings()
    db_status = "unknown"

    try:
        session_factory = get_session_factory()
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"unhealthy: {type(e).__name__}"
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "database": db_status,
                "environment": settings.app_env,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            },
        )

    return {
        "status": "ready",
        "database": db_status,
        "environment": settings.app_env,
        "llm_configured": bool(settings.llm_api_key or settings.use_mock_providers),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

