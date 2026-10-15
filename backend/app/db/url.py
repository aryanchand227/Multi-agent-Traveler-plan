"""
Database URL normalization and connection configuration utility.

Handles conversion of standard PostgreSQL and Supabase URLs to asyncpg-compatible
schemes, configures SSL parameters, and tunes connection arguments for transaction
poolers (PgBouncer port 6543) and local development SQLite.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def normalize_database_url(url: str) -> str:
    """Normalize database connection string for async SQLAlchemy.

    - Converts `postgres://` or `postgresql://` to `postgresql+asyncpg://`
    - Removes `sslmode` query parameter from the URL string because asyncpg
      handles SSL via connect_args rather than URL query parameters.
    - Preserves `sqlite+aiosqlite://` and standard SQLite URLs untouched.
    """
    if not url:
        return ""

    trimmed = url.strip()

    # SQLite URLs: preserve as-is
    if "sqlite" in trimmed:
        return trimmed

    # Convert scheme to postgresql+asyncpg
    if trimmed.startswith("postgres://"):
        trimmed = "postgresql+asyncpg://" + trimmed[len("postgres://"):]
    elif trimmed.startswith("postgresql://"):
        trimmed = "postgresql+asyncpg://" + trimmed[len("postgresql://"):]
    elif trimmed.startswith("postgresql+psycopg2://"):
        trimmed = "postgresql+asyncpg://" + trimmed[len("postgresql+psycopg2://"):]

    # Parse and strip unsupported asyncpg query parameters (like sslmode)
    parsed = urlparse(trimmed)
    if parsed.query:
        query_params = parse_qsl(parsed.query, keep_blank_values=True)
        # Filter out sslmode which asyncpg rejects as an unrecognized argument
        filtered_params = [(k, v) for k, v in query_params if k.lower() != "sslmode"]
        new_query = urlencode(filtered_params)
        trimmed = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        ))

    return trimmed


def get_async_db_config(raw_url: str) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Generate normalized database URL, connect_args, and engine kwargs.

    Returns:
        (normalized_url, connect_args, engine_kwargs)
    """
    normalized_url = normalize_database_url(raw_url)
    is_sqlite = "sqlite" in normalized_url

    connect_args: dict[str, Any] = {}
    engine_kwargs: dict[str, Any] = {
        "echo": False,
    }

    if is_sqlite:
        connect_args["check_same_thread"] = False
    else:
        # PostgreSQL connection pool settings
        engine_kwargs.update({
            "pool_size": 20,
            "max_overflow": 10,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        })

        parsed = urlparse(raw_url)
        hostname = (parsed.hostname or "").lower()
        port = parsed.port

        # Determine SSL requirement:
        # Remote databases (Supabase, Neon, Render, AWS) or explicit sslmode=require
        is_remote = hostname and hostname not in ("localhost", "127.0.0.1", "::1", "postgres")
        has_sslmode_require = "sslmode=require" in raw_url.lower()

        if is_remote or has_sslmode_require or "supabase" in hostname:
            connect_args["ssl"] = "require"

        # Supabase transaction pooler runs on port 6543 (PgBouncer in transaction mode).
        # Transaction mode does not support prepared statements; statement cache must be disabled.
        if port == 6543 or "pooler" in hostname:
            connect_args["statement_cache_size"] = 0
            engine_kwargs["prepared_statement_cache_size"] = 0

    return normalized_url, connect_args, engine_kwargs
