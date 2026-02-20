"""LineItem database model."""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class LineItemCategory(str, enum.Enum):
    """Categories for line items."""
    PARTS = "parts"
    LABOR = "labor"


class LineItem(Base):
    """Line item for an invoice."""

    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    category = Column(SQLEnum(LineItemCategory), nullable=False)

    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")

    @property
    def line_total(self) -> float:
        """Calculate total for this line item."""
        return float(self.quantity * self.unit_price)
