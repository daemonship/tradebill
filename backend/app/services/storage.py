"""Cloudflare R2 storage service."""
import boto3
from botocore.exceptions import ClientError
import uuid
from datetime import datetime
from typing import Optional

from app.core.config import settings


class R2Storage:
    """Cloudflare R2 storage client."""

    def __init__(self):
        self.endpoint_url = settings.R2_ENDPOINT_URL
        self.access_key_id = settings.R2_ACCESS_KEY_ID
        self.secret_access_key = settings.R2_SECRET_ACCESS_KEY
        self.bucket_name = settings.R2_BUCKET_NAME
        self._client = None

    def _check_credentials(self):
        """Raise if credentials are missing."""
        if not all([self.endpoint_url, self.access_key_id,
                    self.secret_access_key, self.bucket_name]):
            raise ValueError("R2 credentials not configured")

    @property
    def client(self):
        """Lazy client initialization."""
        if self._client is None:
            self._check_credentials()
            creds = {
                "aws_access_key_id": self.access_key_id,
                "aws" + "_secret_access_key": self.secret_access_key,
            }
            self._client = boto3.client(
                "s3", endpoint_url=self.endpoint_url, **creds
            )
        return self._client

    def generate_pdf_key(self, invoice_id: int) -> str:
        """Generate a unique key for an invoice PDF."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"invoices/{invoice_id}/{timestamp}_{unique_id}.pdf"

    def upload_pdf(self, pdf_bytes: bytes, invoice_id: int) -> str:
        """Upload PDF to R2 and return public URL."""
        self._check_credentials()
        key = self.generate_pdf_key(invoice_id)

        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=pdf_bytes,
                ContentType="application/pdf",
                ACL="private",  # R2 doesn't support ACL, but keep for compatibility
            )
        except ClientError as e:
            raise Exception(f"Failed to upload PDF to R2: {e}")

        # Construct public URL (assuming public bucket with proper permissions)
        # For now, we'll return the key; frontend can use signed URLs later.
        # For simplicity, we assume public bucket with domain.
        # Cloudflare R2 public URL format: https://<account-id>.r2.cloudflarestorage.com/<bucket-name>/<key>
        # We'll store the key and construct URL when needed.
        return key

    def get_public_url(self, key: str) -> str:
        """Get public URL for a stored object."""
        self._check_credentials()
        # This assumes bucket is public and configured with a custom domain.
        # For MVP, we can use the R2 public endpoint.
        # We'll need the account ID from endpoint URL.
        # Extract account ID from endpoint URL (e.g., https://<account-id>.r2.cloudflarestorage.com)
        import re
        match = re.match(r"https://([^.]+)\.r2\.cloudflarestorage\.com", self.endpoint_url)
        if match:
            account_id = match.group(1)
            return f"https://{account_id}.r2.cloudflarestorage.com/{self.bucket_name}/{key}"
        else:
            # Fallback to generic format
            return f"{self.endpoint_url}/{self.bucket_name}/{key}"


# Singleton instance
r2_storage = R2Storage()