"""
Structured logging configuration.

Uses structlog for JSON-structured logs. Every log includes contextual fields
(request_id, agent_name, operation) but NEVER secrets or API keys.
"""

from __future__ import annotations

import logging
import sys

import structlog


def setup_logging(log_level: str = "INFO", json_format: bool = False) -> None:
    """Configure structured logging for the application."""

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_format:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Suppress noisy third-party loggers
    for logger_name in ["uvicorn.access", "httpx", "httpcore", "sqlalchemy.engine"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str | None = None, **initial_context: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger with optional initial context."""
    logger = structlog.get_logger(name)
    if initial_context:
        logger = logger.bind(**initial_context)
    return logger
