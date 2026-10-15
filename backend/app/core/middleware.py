"""
Security and networking middlewares.

Includes:
1. SecurityHeadersMiddleware: injects OWASP recommended security headers.
2. RequestBodyLimitMiddleware: protects against memory exhaustion via oversized payloads.
3. get_client_ip: secure client IP extraction respecting trusted proxy rules.
"""
from __future__ import annotations

import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str:
    """
    Safely extract the client IP address.

    Follows Section 7:
    - Never blindly trusts X-Forwarded-For supplied by arbitrary clients.
    - Only inspects forwarding headers if the immediate peer (request.client.host)
      is in settings.trusted_proxies or if trust_all_proxies is explicitly enabled.
    - Handles IPv4 and IPv6 format.
    """
    settings = get_settings()
    peer_ip = request.client.host if request.client else "127.0.0.1"

    is_trusted_peer = (
        settings.trust_all_proxies or
        peer_ip in settings.trusted_proxies or
        peer_ip == "127.0.0.1" or
        peer_ip == "::1"
    )

    if not is_trusted_peer:
        # Untrusted direct connection: strictly use peer IP
        return peer_ip

    # Peer is trusted proxy (e.g. Render/Cloudflare/Nginx), inspect forwarding headers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For: client, proxy1, proxy2...
        # Take the leftmost public client IP
        ips = [ip.strip() for ip in forwarded_for.split(",") if ip.strip()]
        if ips:
            return ips[0]

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    return peer_ip


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds standard security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        settings = get_settings()

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Enable HSTS only in production (or over HTTPS)
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


class RequestBodyLimitMiddleware(BaseHTTPMiddleware):
    """Enforces maximum request body size to mitigate DoS attacks."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = get_settings()
        content_length = request.headers.get("Content-Length")

        if content_length:
            try:
                length = int(content_length)
                if length > settings.max_request_body_bytes:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "PayloadTooLarge",
                            "message": f"Request body exceeds maximum allowed size of {settings.max_request_body_bytes} bytes.",
                        },
                    )
            except ValueError:
                pass

        return await call_next(request)
