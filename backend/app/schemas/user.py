"""User schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# Auth schemas
class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""

    user_id: Optional[int] = None


# User schemas
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithProfile(UserResponse):
    """Schema for user with business profile."""

    business_profile: Optional["BusinessProfileResponse"] = None

    class Config:
        from_attributes = True
