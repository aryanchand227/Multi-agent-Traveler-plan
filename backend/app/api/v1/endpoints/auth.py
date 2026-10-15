"""User Authentication API Endpoints (Register, Login, Me, Logout)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_database, get_current_user
from app.db.repositories.user import UserRepository
from app.models.user import User
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import get_settings
from app.core.rate_limit import rate_limit_auth

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_auth)],
)
async def register(
    data: UserRegisterRequest,
    response: Response,
    session: AsyncSession = Depends(get_database),
) -> TokenResponse:
    """Register a new user account."""
    user_repo = UserRepository(session)
    existing = await user_repo.get_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    pwd_hash = hash_password(data.password)
    user = await user_repo.create(
        email=data.email,
        hashed_password=pwd_hash,
        display_name=data.display_name,
    )

    token = create_access_token(data={"sub": user.id, "email": user.email})
    settings = get_settings()

    # Set secure HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.jwt_access_token_expire_minutes * 60,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit_auth)],
)
async def login(
    data: UserLoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_database),
) -> TokenResponse:
    """Authenticate with email and password."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_email(data.email)

    # Generic error message to prevent account enumeration
    invalid_credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user or not user.hashed_password:
        raise invalid_credentials_exc

    if not verify_password(data.password, user.hashed_password):
        raise invalid_credentials_exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    token = create_access_token(data={"sub": user.id, "email": user.email})
    settings = get_settings()

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.jwt_access_token_expire_minutes * 60,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Retrieve profile of currently authenticated user."""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    """Log out by clearing authentication cookies."""
    response.delete_cookie(key="access_token", httponly=True, samesite="lax")
    return {"message": "Logged out successfully."}
