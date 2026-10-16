"""Shared FastAPI dependencies for authentication, database, and rate limiting."""
from __future__ import annotations

from typing import Optional
import jwt
from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.repositories.user import UserRepository
from app.models.user import User
from app.core.config import get_settings
from app.core.security import extract_token_from_request, decode_access_token


async def get_database(session: AsyncSession = Depends(get_db)) -> AsyncSession:
    """Get database session dependency."""
    return session


async def get_current_user_optional(
    request: Request,
    session: AsyncSession = Depends(get_database),
) -> Optional[User]:
    """Extract authenticated user if valid token is provided; returns None otherwise."""
    token = extract_token_from_request(request)
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(payload["sub"])
    if user and user.is_active:
        return user
    return None


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_database),
) -> User:
    """
    Enforces authentication.
    Returns User if valid JWT is provided.
    Raises specific 401 exceptions if token is expired or invalid.
    In development mode only, allows fallback to development user if no token is sent.
    """
    token = extract_token_from_request(request)
    if token:
        settings = get_settings()
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            if "sub" in payload:
                user_repo = UserRepository(session)
                user = await user_repo.get_by_id(payload["sub"])
                if user and user.is_active:
                    return user
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account not found or inactive. Please log in again.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please log in again.",
                headers={"WWW-Authenticate": 'Bearer error="invalid_token", error_description="The token has expired"'},
            )
        except (jwt.InvalidTokenError, jwt.PyJWTError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token. Please log in again.",
                headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
            )

    settings = get_settings()

    # In development mode, allow header-based or default user fallback
    if settings.is_development:
        user_id = request.headers.get("X-User-ID") or "default-user"
        user_repo = UserRepository(session)
        dev_user = await user_repo.get_by_id(user_id)
        if not dev_user:
            # Auto-provision development user
            dev_user = await user_repo.create(
                email=f"{user_id}@example.com",
                hashed_password="",
                display_name=user_id.replace("-", " ").title(),
                user_id=user_id,
            )
        return dev_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Please provide a valid Bearer token.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user_id(
    user: User = Depends(get_current_user),
) -> str:
    """Extract current authenticated user ID."""
    return user.id
