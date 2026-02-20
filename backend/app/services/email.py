"""Email sending service using Resend."""
import base64
from typing import Optional
import resend
from resend.exceptions import ResendError

from app.core.config import settings


class EmailService:
    """Email service using Resend."""

    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self._configured = bool(self.api_key)

    def _check_config(self):
        if not self._configured:
            raise ValueError("RESEND_API_KEY not configured")

    def send_invoice_email(
        self,
        to_email: str,
        business_name: str,
        client_name: str,
        invoice_number: int,
        pdf_bytes: bytes,
        pdf_filename: str,
    ) -> str:
        """Send invoice email with PDF attachment.
        
        Returns the Resend email ID for tracking.
        """
        self._check_config()
        resend.api_key = self.api_key
        
        # Encode PDF as base64
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

        params = {
            "from": "Invoice Designer <invoices@invoice-designer.app>",
            "to": [to_email],
            "subject": f"Invoice #{invoice_number} from {business_name}",
            "html": f"""
                <!DOCTYPE html>
                <html>
                <body>
                    <p>Dear {client_name},</p>
                    <p>Please find your invoice attached.</p>
                    <p>This invoice was created and sent using Invoice Designer.</p>
                    <p>If you have any questions, please contact {business_name} directly.</p>
                    <br>
                    <p>Best regards,</p>
                    <p>The Invoice Designer Team</p>
                </body>
                </html>
            """,
            "attachments": [
                {
                    "filename": pdf_filename,
                    "content": pdf_b64,
                }
            ],
        }

        try:
            email = resend.Emails.send(params)
            return email["id"]
        except ResendError as e:
            raise Exception(f"Failed to send email via Resend: {e}")


# Singleton instance
email_service = EmailService()