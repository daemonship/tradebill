"""Business profile database model."""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class BusinessProfile(Base):
    """Business profile for a user."""

    __tablename__ = "business_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String(255), nullable=False)
    phone = Column(String(50))
    email = Column(String(255))
    license_number = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to user
    user = relationship("User", back_populates="business_profile")
