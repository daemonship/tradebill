"""Invoice API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.invoice import Invoice, InvoiceStatus, TradeType
from app.models.line_item import LineItem, LineItemCategory
from app.models.business_profile import BusinessProfile
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceStatusUpdate,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceTotals,
    LineItemSummary,
)
from app.pdf_generator import pdf_generator
from app.services.storage import r2_storage
from app.services.email import email_service

router = APIRouter(prefix="/invoices", tags=["invoices"])


def calculate_invoice_totals(invoice: Invoice) -> InvoiceTotals:
    """Calculate totals for an invoice."""
    category_totals = {}
    subtotal = 0.0

    for item in invoice.line_items:
        line_total = item.line_total
        subtotal += line_total
        category = item.category.value
        category_totals[category] = category_totals.get(category, 0) + line_total

    tax_amount = subtotal * (float(invoice.tax_rate) / 100)
    total = subtotal + tax_amount

    breakdown = [
        LineItemSummary(category=cat, total=amount)
        for cat, amount in category_totals.items()
    ]

    return InvoiceTotals(
        subtotal=round(subtotal, 2),
        tax_amount=round(tax_amount, 2),
        total=round(total, 2),
        category_breakdown=breakdown,
    )


def get_compliance_notes(trade_type: TradeType) -> str:
    """Get default compliance notes for a trade type."""
    notes = {
        TradeType.PLUMBING: (
            "This plumbing work was performed in accordance with local "
            "plumbing codes and regulations. All fixtures and installations "
            "are guaranteed for 1 year from date of completion. Keep this "
            "invoice for warranty claims and tax records."
        ),
        TradeType.ELECTRICAL: (
            "This electrical work was performed in accordance with the "
            "National Electrical Code and local regulations. All work is "
            "guaranteed for 1 year from date of completion. Electrical "
            "permit information available upon request. Keep this invoice "
            "for warranty claims and tax records."
        ),
        TradeType.HVAC: (
            "This HVAC work was performed in accordance with industry "
            "standards and local regulations. Equipment warranties may "
            "require registration with manufacturer. All labor is guaranteed "
            "for 1 year from date of completion. Keep this invoice for "
            "warranty claims and tax records."
        ),
    }
    return notes.get(trade_type, "")


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new invoice."""
    # Create invoice
    invoice = Invoice(
        user_id=current_user.id,
        client_name=invoice_data.client_name,
        client_email=invoice_data.client_email,
        job_address=invoice_data.job_address,
        trade_type=invoice_data.trade_type,
        tax_rate=invoice_data.tax_rate,
        status=InvoiceStatus.DRAFT,
    )
    db.add(invoice)
    db.flush()  # Get the invoice ID

    # Create line items
    for item_data in invoice_data.line_items:
        line_item = LineItem(
            invoice_id=invoice.id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            category=item_data.category,
        )
        db.add(line_item)

    db.commit()
    db.refresh(invoice)

    # Calculate totals
    invoice_response = InvoiceResponse.model_validate(invoice)

    return invoice_response


@router.get("", response_model=List[InvoiceListResponse])
async def list_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all invoices for the current user, ordered by date descending."""
    invoices = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id)
        .order_by(desc(Invoice.created_at), desc(Invoice.id))
        .all()
    )

    result = []
    for invoice in invoices:
        totals = calculate_invoice_totals(invoice)
        result.append(
            InvoiceListResponse(
                id=invoice.id,
                client_name=invoice.client_name,
                job_address=invoice.job_address,
                trade_type=invoice.trade_type,
                status=invoice.status,
                total=totals.total,
                created_at=invoice.created_at,
            )
        )

    return result


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific invoice by ID."""
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    totals = calculate_invoice_totals(invoice)
    invoice_response = InvoiceResponse.model_validate(invoice)
    invoice_response.totals = totals

    return invoice_response


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an invoice."""
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    # Update invoice fields
    invoice.client_name = invoice_data.client_name
    invoice.client_email = invoice_data.client_email
    invoice.job_address = invoice_data.job_address
    invoice.trade_type = invoice_data.trade_type
    invoice.tax_rate = invoice_data.tax_rate

    # Delete existing line items
    db.query(LineItem).filter(LineItem.invoice_id == invoice.id).delete()

    # Create new line items
    for item_data in invoice_data.line_items:
        line_item = LineItem(
            invoice_id=invoice.id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            category=item_data.category,
        )
        db.add(line_item)

    db.commit()
    db.refresh(invoice)

    totals = calculate_invoice_totals(invoice)
    invoice_response = InvoiceResponse.model_validate(invoice)
    invoice_response.totals = totals

    return invoice_response


@router.patch("/{invoice_id}/status", response_model=InvoiceResponse)
async def update_invoice_status(
    invoice_id: int,
    status_update: InvoiceStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the status of an invoice."""
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    invoice.status = status_update.status
    db.commit()
    db.refresh(invoice)

    totals = calculate_invoice_totals(invoice)
    invoice_response = InvoiceResponse.model_validate(invoice)
    invoice_response.totals = totals

    return invoice_response


@router.post("/{invoice_id}/send", response_model=InvoiceResponse)
async def send_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send an invoice: generate PDF, upload to R2, email to client."""
    # Fetch invoice with line items
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        .first()
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    # Prevent re-sending if already sent
    if invoice.status == InvoiceStatus.SENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice has already been sent",
        )

    # Fetch business profile
    business_profile = (
        db.query(BusinessProfile)
        .filter(BusinessProfile.user_id == current_user.id)
        .first()
    )
    if not business_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business profile not set up. Please complete your business profile first.",
        )

    # Get compliance notes for trade
    compliance_notes = get_compliance_notes(invoice.trade_type)

    # Prepare data for PDF generation
    invoice_dict = {
        "id": invoice.id,
        "client_name": invoice.client_name,
        "client_email": invoice.client_email,
        "job_address": invoice.job_address,
        "trade_type": invoice.trade_type,
        "tax_rate": float(invoice.tax_rate),
        "created_at": invoice.created_at,
        "totals": calculate_invoice_totals(invoice).model_dump(),
    }

    business_profile_dict = {
        "business_name": business_profile.business_name,
        "phone": business_profile.phone,
        "email": business_profile.email,
        "license_number": business_profile.license_number,
    }

    line_items = []
    for item in invoice.line_items:
        line_items.append({
            "description": item.description,
            "quantity": float(item.quantity),
            "unit_price": float(item.unit_price),
            "category": item.category,
            "line_total": item.line_total,
        })

    try:
        # Generate PDF
        pdf_bytes = pdf_generator.generate_pdf(
            invoice=invoice_dict,
            business_profile=business_profile_dict,
            line_items=line_items,
            compliance_notes=compliance_notes,
        )

        # Upload to R2
        pdf_key = r2_storage.upload_pdf(pdf_bytes, invoice.id)
        pdf_url = r2_storage.get_public_url(pdf_key)

        # Send email with PDF attachment
        pdf_filename = f"invoice_{invoice.id}_{business_profile.business_name.replace(' ', '_')}.pdf"
        email_service.send_invoice_email(
            to_email=invoice.client_email,
            business_name=business_profile.business_name,
            client_name=invoice.client_name,
            invoice_number=invoice.id,
            pdf_bytes=pdf_bytes,
            pdf_filename=pdf_filename,
        )

        # Update invoice
        invoice.status = InvoiceStatus.SENT
        invoice.pdf_url = pdf_url
        db.commit()
        db.refresh(invoice)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send invoice: {str(e)}",
        )

    totals = calculate_invoice_totals(invoice)
    invoice_response = InvoiceResponse.model_validate(invoice)
    invoice_response.totals = totals

    return invoice_response


@router.get("/templates/compliance-notes")
async def get_compliance_notes_template(trade_type: TradeType):
    """Get compliance notes template for a trade type."""
    return {"trade_type": trade_type, "compliance_notes": get_compliance_notes(trade_type)}
