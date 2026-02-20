"""PDF generation for invoices."""
import os
from typing import Dict, List, Any
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration

from app.core.config import settings


class InvoicePDFGenerator:
    """Generate PDF invoices from templates."""

    def __init__(self):
        self.template_dir = os.path.join(
            os.path.dirname(__file__), "templates"
        )
        self.font_config = FontConfiguration()

    def _load_template(self, trade_type: str) -> str:
        """Load HTML template for a trade type."""
        template_path = os.path.join(
            self.template_dir, f"invoice_{trade_type}.html"
        )
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()

    def _format_currency(self, amount: float) -> str:
        """Format currency with two decimal places."""
        return f"${amount:.2f}"

    def _generate_item_rows(self, items: List[Dict]) -> str:
        """Generate HTML rows for line items."""
        rows = []
        for item in items:
            row = f"""
            <tr>
                <td>{item['description']}</td>
                <td class="text-right">{item['quantity']}</td>
                <td class="text-right">{self._format_currency(item['unit_price'])}</td>
                <td class="text-right">{self._format_currency(item['line_total'])}</td>
            </tr>
            """
            rows.append(row)
        return "\n".join(rows)

    def _group_line_items(self, line_items: List[Dict]) -> Dict[str, List[Dict]]:
        """Group line items by category (parts/labor)."""
        grouped = {"parts": [], "labor": []}
        for item in line_items:
            category = item["category"].value  # LineItemCategory enum
            if category in grouped:
                grouped[category].append(item)
        return grouped

    def _calculate_category_totals(self, grouped_items: Dict[str, List[Dict]]) -> Dict[str, float]:
        """Calculate subtotals for each category."""
        totals = {}
        for category, items in grouped_items.items():
            total = sum(item["line_total"] for item in items)
            totals[category] = round(total, 2)
        return totals

    def generate_pdf(
        self,
        invoice: Dict,
        business_profile: Dict,
        line_items: List[Dict],
        compliance_notes: str,
    ) -> bytes:
        """Generate PDF bytes for an invoice."""
        # Group line items by category
        grouped = self._group_line_items(line_items)
        category_totals = self._calculate_category_totals(grouped)

        # Generate HTML rows for each category
        parts_rows = self._generate_item_rows(grouped.get("parts", []))
        labor_rows = self._generate_item_rows(grouped.get("labor", []))

        # Prepare template context
        context = {
            "business_name": business_profile.get("business_name", ""),
            "business_phone": business_profile.get("phone", ""),
            "business_email": business_profile.get("email", ""),
            "business_license": business_profile.get("license_number", ""),
            "client_name": invoice["client_name"],
            "client_email": invoice["client_email"],
            "job_address": invoice["job_address"],
            "invoice_number": invoice["id"],
            "invoice_date": invoice["created_at"].strftime("%B %d, %Y"),
            "trade_type": invoice["trade_type"].value.title(),
            "parts_rows": parts_rows,
            "labor_rows": labor_rows,
            "subtotal_parts": self._format_currency(category_totals.get("parts", 0)),
            "subtotal_labor": self._format_currency(category_totals.get("labor", 0)),
            "subtotal": self._format_currency(invoice["totals"]["subtotal"]),
            "tax_rate": invoice["tax_rate"],
            "tax_amount": self._format_currency(invoice["totals"]["tax_amount"]),
            "total": self._format_currency(invoice["totals"]["total"]),
            "compliance_notes": compliance_notes,
        }

        # Load and render template
        template = self._load_template(invoice["trade_type"].value)
        html_content = template.format(**context)

        # Generate PDF
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf(font_config=self.font_config)
        return pdf_bytes


# Singleton instance
pdf_generator = InvoicePDFGenerator()