"""Business profile schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class BusinessProfileBase(BaseModel):
    """Base business profile schema."""

    business_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    license_number: Optional[str] = Field(None, max_length=100)


class BusinessProfileCreate(BusinessProfileBase):
    """Schema for creating a business profile."""

    pass


class BusinessProfileUpdate(BaseModel):
    """Schema for updating a business profile."""

    business_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    license_number: Optional[str] = Field(None, max_length=100)


class BusinessProfileResponse(BusinessProfileBase):
    """Schema for business profile response."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
