"""
Security and authentication utilities.

Provides:
- Secure password hashing and verification using bcrypt
- JSON Web Token (JWT) creation and decoding using PyJWT
- Token extraction from Authorization header, Cookie, or query param (for SSE)
- Request ID generation
"""
from __future__ import annotations

import datetime
import uuid
import bcrypt
import jwt
from typing import Any, Optional
from fastapi import Request

from app.core.config import get_settings


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt and automatic salt."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored bcrypt hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[datetime.timedelta] = None,
) -> str:
    """Create a signed JWT access token."""
    settings = get_settings()
    to_encode = data.copy()

    now = datetime.datetime.now(datetime.timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + datetime.timedelta(minutes=settings.jwt_access_token_expire_minutes)

    to_encode.update({
        "exp": expire,
        "iat": now,
    })

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """Decode and validate a JWT access token. Returns payload or None if invalid/expired."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except (jwt.PyJWTError, Exception):
        return None


def extract_token_from_request(request: Request) -> Optional[str]:
    """
    Extract token from:
    1. Authorization: Bearer <token>
    2. Cookie 'access_token'
    3. Query parameter 'token' (crucial for browser EventSource / SSE)
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()

    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token.strip()

    query_token = request.query_params.get("token")
    if query_token:
        return query_token.strip()

    return None


def get_user_id(request: Request) -> str:
    """
    Extract user ID from request.
    Decodes JWT token if present. Falls back to X-User-ID or 'default-user' only in development.
    """
    token = extract_token_from_request(request)
    if token:
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            return payload["sub"]

    settings = get_settings()
    if settings.is_development:
        user_id = request.headers.get("X-User-ID")
        return user_id or "default-user"

    return "anonymous"


def generate_request_id() -> str:
    """Generate a unique travel request ID."""
    now = datetime.datetime.now(datetime.timezone.utc)
    date_part = now.strftime("%Y%m%d")
    unique_part = uuid.uuid4().hex[:8].upper()
    return f"TRV-{date_part}-{unique_part}"
