"""Business profile API endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, BusinessProfile
from app.schemas import (
    UserResponse,
    BusinessProfileCreate,
    BusinessProfileUpdate,
    BusinessProfileResponse,
)
from app.api.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=BusinessProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BusinessProfile:
    """Get the current user's business profile."""
    profile = db.query(BusinessProfile).filter(
        BusinessProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found",
        )
    
    return profile


@router.put("", response_model=BusinessProfileResponse)
def update_profile(
    profile_data: BusinessProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BusinessProfile:
    """Update the current user's business profile."""
    profile = db.query(BusinessProfile).filter(
        BusinessProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        # Create profile if it doesn't exist
        profile = BusinessProfile(user_id=current_user.id)
        db.add(profile)
    
    # Update fields if provided
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile


@router.post("", response_model=BusinessProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile_data: BusinessProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BusinessProfile:
    """Create a business profile for the current user."""
    # Check if profile already exists
    existing_profile = db.query(BusinessProfile).filter(
        BusinessProfile.user_id == current_user.id
    ).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business profile already exists. Use PUT to update.",
        )
    
    # Create new profile
    new_profile = BusinessProfile(
        user_id=current_user.id,
        **profile_data.model_dump(),
    )
    
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    
    return new_profile
