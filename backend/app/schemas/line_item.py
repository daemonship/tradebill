"""Pydantic schemas for LineItem."""
from pydantic import BaseModel, Field

from app.models.line_item import LineItemCategory


class LineItemBase(BaseModel):
    """Base line item fields."""
    description: str = Field(..., min_length=1, max_length=500)
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    category: LineItemCategory


class LineItemCreate(LineItemBase):
    """Schema for creating a line item."""
    pass


class LineItemResponse(LineItemBase):
    """Schema for line item response."""
    id: int
    line_total: float

    class Config:
        from_attributes = True
