"""Pydantic schemas for Invoice."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from app.models.invoice import TradeType, InvoiceStatus
from app.schemas.line_item import LineItemResponse, LineItemCreate


class InvoiceBase(BaseModel):
    """Base invoice fields."""
    client_name: str = Field(..., min_length=1, max_length=255)
    client_email: str = Field(..., min_length=1, max_length=255)
    job_address: str = Field(..., min_length=1, max_length=500)
    trade_type: TradeType
    tax_rate: float = Field(..., ge=0, le=100, description="Tax rate as percentage (e.g., 8.25)")


class InvoiceCreate(InvoiceBase):
    """Schema for creating an invoice."""
    line_items: List[LineItemCreate] = Field(..., min_length=1)


class InvoiceUpdate(InvoiceBase):
    """Schema for updating an invoice."""
    line_items: List[LineItemCreate] = Field(..., min_length=1)


class InvoiceStatusUpdate(BaseModel):
    """Schema for updating invoice status."""
    status: InvoiceStatus


class LineItemSummary(BaseModel):
    """Summary of line items by category."""
    category: str
    total: float


class InvoiceTotals(BaseModel):
    """Calculated totals for an invoice."""
    subtotal: float
    tax_amount: float
    total: float
    category_breakdown: List[LineItemSummary]


class InvoiceResponse(InvoiceBase):
    """Schema for invoice response."""
    id: int
    user_id: int
    status: InvoiceStatus
    pdf_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    line_items: List[LineItemResponse]
    totals: InvoiceTotals

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    """Schema for invoice list item (without full details)."""
    id: int
    client_name: str
    job_address: str
    trade_type: TradeType
    status: InvoiceStatus
    total: float
    created_at: datetime

    class Config:
        from_attributes = True
