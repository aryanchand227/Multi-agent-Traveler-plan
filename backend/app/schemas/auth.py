"""Authentication request and response schemas."""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """User registration payload."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    display_name: Optional[str] = Field(None, max_length=100)


class UserLoginRequest(BaseModel):
    """User login payload."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Public user profile data."""
    id: str
    email: str
    display_name: Optional[str] = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Authentication token response with user profile."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
