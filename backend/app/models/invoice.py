"""Invoice database model."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class TradeType(str, enum.Enum):
    """Trade types for invoices."""
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    HVAC = "hvac"


class InvoiceStatus(str, enum.Enum):
    """Status of an invoice."""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"


class Invoice(Base):
    """Invoice for a job."""

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    client_name = Column(String(255), nullable=False)
    client_email = Column(String(255), nullable=False)
    job_address = Column(String(500), nullable=False)
    trade_type = Column(SQLEnum(TradeType), nullable=False)
    tax_rate = Column(Numeric(5, 2), nullable=False, default=0)  # e.g., 8.25 for 8.25%
    status = Column(SQLEnum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT)
    pdf_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    line_items = relationship("LineItem", back_populates="invoice", cascade="all, delete-orphan")

    # Relationship to user
    user = relationship("User", backref="invoices")

    @property
    def totals(self):
        """Calculate and return invoice totals."""
        from app.api.invoices import calculate_invoice_totals
        return calculate_invoice_totals(self)
