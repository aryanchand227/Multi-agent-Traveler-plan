"""FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import TravelPlannerError
from app.core.middleware import SecurityHeadersMiddleware, RequestBodyLimitMiddleware
from app.db.session import init_db, close_db
from app.api.v1.router import api_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — startup and shutdown."""
    settings = get_settings()
    setup_logging(
        log_level="DEBUG" if settings.debug else "INFO",
        json_format=settings.is_production,
    )
    logger.info("Starting AI Travel Planner", env=settings.app_env)

    # Check production validation
    prod_issues = settings.validate_production_settings()
    for issue in prod_issues:
        logger.warning("Production security notice", issue=issue)

    # Fail fast if production is configured with SQLite
    if settings.is_production and settings.is_sqlite:
        error_msg = (
            "FATAL: Production environment detected (APP_ENV=production) with SQLite DATABASE_URL. "
            "Hosted platforms (such as Render) run on ephemeral containers where SQLite files are lost on restart/redeploy. "
            "A persistent PostgreSQL database (such as Supabase Free Tier) is required in production. "
            "Set DATABASE_URL to a valid PostgreSQL connection string or set APP_ENV=development for local testing."
        )
        logger.error("Production SQLite rejected", error=error_msg)
        raise RuntimeError(error_msg)

    await init_db()
    logger.info("Database initialized")
    yield
    await close_db()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Multi-Agent AI Travel Planning Platform",
        lifespan=lifespan,
    )

    # Security Headers and Body Size Limit
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestBodyLimitMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(TravelPlannerError)
    async def travel_planner_error_handler(request: Request, exc: TravelPlannerError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        headers = dict(exc.headers) if exc.headers else None
        detail = exc.detail
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTPException",
                "message": detail if isinstance(detail, str) else str(detail),
                "detail": detail,
            },
            headers=headers,
        )

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled exception", error=str(exc), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred.",
            },
        )


    # Routes
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
