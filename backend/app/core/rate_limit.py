"""
Rate limiting and abuse prevention layer.

Implements:
- Sliding-window rate limiter for IP and user accounts
- Safe client IP resolution through trusted proxies
- Workflow concurrency semaphore for LangGraph pipelines
- HTTP 429 Too Many Requests response with Retry-After header
"""
from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from typing import Callable, Optional
from fastapi import Request, HTTPException, status

from app.core.config import get_settings
from app.core.middleware import get_client_ip


class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding window rate limiter."""

    def __init__(self) -> None:
        self._history: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 60,
    ) -> tuple[bool, int]:
        """
        Check if request is allowed.
        Returns: (is_allowed, retry_after_seconds)
        """
        now = time.time()
        window_start = now - window_seconds

        async with self._lock:
            # Filter timestamps outside the window
            timestamps = [ts for ts in self._history[key] if ts > window_start]

            if len(timestamps) >= max_requests:
                earliest = timestamps[0]
                retry_after = max(1, int(earliest + window_seconds - now))
                self._history[key] = timestamps
                return False, retry_after

            # Record this request
            timestamps.append(now)
            self._history[key] = timestamps
            return True, 0

    async def cleanup_stale_entries(self, max_age_seconds: int = 300) -> None:
        """Periodic cleanup of old keys to prevent memory leaks."""
        now = time.time()
        async with self._lock:
            stale_keys = [
                k for k, timestamps in self._history.items()
                if not timestamps or timestamps[-1] < (now - max_age_seconds)
            ]
            for k in stale_keys:
                del self._history[k]


    def reset(self) -> None:
        """Clear all rate limit history (useful for test isolation)."""
        self._history.clear()


# Global limiter instance
_rate_limiter = SlidingWindowRateLimiter()


def reset_rate_limiter() -> None:
    """Reset all active rate limits."""
    _rate_limiter.reset()

# Concurrency semaphore for active LangGraph workflows
_workflow_semaphore: Optional[asyncio.Semaphore] = None


def get_workflow_semaphore() -> asyncio.Semaphore:
    """Get or initialize the global workflow concurrency semaphore."""
    global _workflow_semaphore
    if _workflow_semaphore is None:
        settings = get_settings()
        _workflow_semaphore = asyncio.Semaphore(settings.max_concurrent_plans_total)
    return _workflow_semaphore


async def rate_limit_auth(request: Request) -> None:
    """Strict rate limiter for sensitive authentication endpoints (login/register)."""
    settings = get_settings()
    if not settings.rate_limit_enabled:
        return

    ip = get_client_ip(request)
    key = f"auth:{ip}"
    allowed, retry_after = await _rate_limiter.check_rate_limit(
        key=key,
        max_requests=settings.rate_limit_auth_per_minute,
        window_seconds=60,
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )


async def rate_limit_planning(request: Request, user_id: str) -> None:
    """
    Rate limiter for expensive travel planning workflows.
    Enforces per-IP and per-account limits.
    """
    settings = get_settings()
    if not settings.rate_limit_enabled:
        return

    ip = get_client_ip(request)

    # 1. IP-level check
    ip_key = f"plan_ip:{ip}"
    ip_allowed, ip_retry = await _rate_limiter.check_rate_limit(
        key=ip_key,
        max_requests=settings.rate_limit_anonymous_per_minute,
        window_seconds=60,
    )
    if not ip_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many planning requests from this IP address. Please slow down.",
            headers={"Retry-After": str(ip_retry)},
        )

    # 2. User-level check (if authenticated)
    if user_id and user_id != "anonymous":
        user_key = f"plan_user:{user_id}"
        user_allowed, user_retry = await _rate_limiter.check_rate_limit(
            key=user_key,
            max_requests=settings.rate_limit_user_per_minute,
            window_seconds=60,
        )
        if not user_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Account planning rate limit reached. Please wait before creating another plan.",
                headers={"Retry-After": str(user_retry)},
            )
