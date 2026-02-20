"""Tests for invoice endpoints."""
import pytest
from fastapi import status
from app.models.invoice import TradeType, InvoiceStatus
from app.models.line_item import LineItemCategory


class TestInvoiceCreation:
    """Tests for invoice creation."""

    def test_create_invoice_success(self, client, auth_headers):
        """Test successful invoice creation."""
        response = client.post(
            "/invoices",
            json={
                "client_name": "John Doe",
                "client_email": "john@example.com",
                "job_address": "123 Main St, Anytown, TX 75001",
                "trade_type": "plumbing",
                "tax_rate": 8.25,
                "line_items": [
                    {
                        "description": "Water heater installation",
                        "quantity": 1,
                        "unit_price": 1500.00,
                        "category": "labor",
                    },
                    {
                        "description": "Water heater (40 gallon)",
                        "quantity": 1,
                        "unit_price": 800.00,
                        "category": "parts",
                    },
                    {
                        "description": "Copper pipe (1/2 inch)",
                        "quantity": 10,
                        "unit_price": 12.50,
                        "category": "parts",
                    },
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["client_name"] == "John Doe"
        assert data["client_email"] == "john@example.com"
        assert data["trade_type"] == "plumbing"
        assert data["status"] == "draft"
        assert len(data["line_items"]) == 3

        # Check totals calculation
        assert data["totals"]["subtotal"] == 2425.00  # 1500 + 800 + 125
        assert data["totals"]["tax_amount"] == 200.06  # 2425 * 0.0825
        assert data["totals"]["total"] == 2625.06

        # Check category breakdown
        categories = {item["category"]: item["total"] for item in data["totals"]["category_breakdown"]}
        assert categories["labor"] == 1500.00
        assert categories["parts"] == 925.00  # 800 + 125

    def test_create_invoice_no_auth(self, client):
        """Test invoice creation without authentication."""
        response = client.post(
            "/invoices",
            json={
                "client_name": "John Doe",
                "client_email": "john@example.com",
                "job_address": "123 Main St",
                "trade_type": "electrical",
                "tax_rate": 0,
                "line_items": [
                    {
                        "description": "Service call",
                        "quantity": 1,
                        "unit_price": 75.00,
                        "category": "labor",
                    }
                ],
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_invoice_validation_error(self, client, auth_headers):
        """Test invoice creation with invalid data."""
        response = client.post(
            "/invoices",
            json={
                "client_name": "",  # Empty name
                "client_email": "invalid-email",  # Invalid email format
                "job_address": "123 Main St",
                "trade_type": "plumbing",
                "tax_rate": 150,  # Invalid tax rate (> 100)
                "line_items": [],  # No line items
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestInvoiceList:
    """Tests for invoice listing."""

    def test_list_invoices_empty(self, client, auth_headers):
        """Test listing invoices when none exist."""
        response = client.get(
            "/invoices",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_invoices(self, client, auth_headers):
        """Test listing invoices."""
        # Create two invoices
        client.post(
            "/invoices",
            json={
                "client_name": "Client One",
                "client_email": "client1@example.com",
                "job_address": "123 Main St",
                "trade_type": "plumbing",
                "tax_rate": 8.25,
                "line_items": [
                    {
                        "description": "Service",
                        "quantity": 1,
                        "unit_price": 100.00,
                        "category": "labor",
                    }
                ],
            },
            headers=auth_headers,
        )

        client.post(
            "/invoices",
            json={
                "client_name": "Client Two",
                "client_email": "client2@example.com",
                "job_address": "456 Oak Ave",
                "trade_type": "electrical",
                "tax_rate": 0,
                "line_items": [
                    {
                        "description": "Repair",
                        "quantity": 2,
                        "unit_price": 50.00,
                        "category": "labor",
                    }
                ],
            },
            headers=auth_headers,
        )

        response = client.get(
            "/invoices",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        invoices = response.json()
        assert len(invoices) == 2
        # Should be ordered by created_at descending
        assert invoices[0]["client_name"] == "Client Two"
        assert invoices[1]["client_name"] == "Client One"


class TestInvoiceDetail:
    """Tests for getting invoice details."""

    def test_get_invoice(self, client, auth_headers):
        """Test getting a specific invoice."""
        # Create an invoice
        create_response = client.post(
            "/invoices",
            json={
                "client_name": "Jane Smith",
                "client_email": "jane@example.com",
                "job_address": "789 Pine Rd",
                "trade_type": "hvac",
                "tax_rate": 6.5,
                "line_items": [
                    {
                        "description": "AC repair",
                        "quantity": 1,
                        "unit_price": 200.00,
                        "category": "labor",
                    },
                ],
            },
            headers=auth_headers,
        )

        invoice_id = create_response.json()["id"]

        # Get the invoice
        response = client.get(
            f"/invoices/{invoice_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == invoice_id
        assert data["client_name"] == "Jane Smith"
        assert data["trade_type"] == "hvac"

    def test_get_invoice_not_found(self, client, auth_headers):
        """Test getting a non-existent invoice."""
        response = client.get(
            "/invoices/99999",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestInvoiceUpdate:
    """Tests for invoice updates."""

    def test_update_invoice(self, client, auth_headers):
        """Test updating an invoice."""
        # Create an invoice
        create_response = client.post(
            "/invoices",
            json={
                "client_name": "Original Client",
                "client_email": "original@example.com",
                "job_address": "123 Main St",
                "trade_type": "plumbing",
                "tax_rate": 8.25,
                "line_items": [
                    {
                        "description": "Original item",
                        "quantity": 1,
                        "unit_price": 100.00,
                        "category": "labor",
                    }
                ],
            },
            headers=auth_headers,
        )

        invoice_id = create_response.json()["id"]

        # Update the invoice
        response = client.put(
            f"/invoices/{invoice_id}",
            json={
                "client_name": "Updated Client",
                "client_email": "updated@example.com",
                "job_address": "456 New Address",
                "trade_type": "electrical",
                "tax_rate": 7.0,
                "line_items": [
                    {
                        "description": "Updated item",
                        "quantity": 2,
                        "unit_price": 150.00,
                        "category": "labor",
                    }
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["client_name"] == "Updated Client"
        assert data["client_email"] == "updated@example.com"
        assert data["trade_type"] == "electrical"
        assert len(data["line_items"]) == 1
        assert data["line_items"][0]["description"] == "Updated item"
        assert data["totals"]["subtotal"] == 300.00

    def test_update_invoice_not_found(self, client, auth_headers):
        """Test updating a non-existent invoice."""
        response = client.put(
            "/invoices/99999",
            json={
                "client_name": "Test",
                "client_email": "test@example.com",
                "job_address": "123 Main St",
                "trade_type": "plumbing",
                "tax_rate": 0,
                "line_items": [
                    {
                        "description": "Item",
                        "quantity": 1,
                        "unit_price": 100.00,
                        "category": "labor",
                    }
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestInvoiceStatusUpdate:
    """Tests for invoice status updates."""

    def test_update_status_to_sent(self, client, auth_headers):
        """Test updating invoice status to sent."""
        # Create an invoice
        create_response = client.post(
            "/invoices",
            json={
                "client_name": "Test Client",
                "client_email": "test@example.com",
                "job_address": "123 Main St",
                "trade_type": "plumbing",
                "tax_rate": 0,
                "line_items": [
                    {
                        "description": "Service",
                        "quantity": 1,
                        "unit_price": 100.00,
                        "category": "labor",
                    }
                ],
            },
            headers=auth_headers,
        )

        invoice_id = create_response.json()["id"]
        assert create_response.json()["status"] == "draft"

        # Update status to sent
        response = client.patch(
            f"/invoices/{invoice_id}/status",
            json={"status": "sent"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "sent"

    def test_update_status_to_paid(self, client, auth_headers):
        """Test updating invoice status to paid."""
        # Create and mark as sent
        create_response = client.post(
            "/invoices",
            json={
                "client_name": "Test Client",
                "client_email": "test@example.com",
                "job_address": "123 Main St",
                "trade_type": "electrical",
                "tax_rate": 0,
                "line_items": [
                    {
                        "description": "Service",
                        "quantity": 1,
                        "unit_price": 100.00,
                        "category": "labor",
                    }
                ],
            },
            headers=auth_headers,
        )

        invoice_id = create_response.json()["id"]

        # Update status to paid
        response = client.patch(
            f"/invoices/{invoice_id}/status",
            json={"status": "paid"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "paid"


class TestComplianceNotes:
    """Tests for compliance notes templates."""

    def test_get_plumbing_compliance_notes(self, client):
        """Test getting plumbing compliance notes."""
        response = client.get("/invoices/templates/compliance-notes?trade_type=plumbing")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["trade_type"] == "plumbing"
        assert "plumbing codes" in data["compliance_notes"].lower()
        assert "warranty" in data["compliance_notes"].lower()

    def test_get_electrical_compliance_notes(self, client):
        """Test getting electrical compliance notes."""
        response = client.get("/invoices/templates/compliance-notes?trade_type=electrical")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["trade_type"] == "electrical"
        assert "national electrical code" in data["compliance_notes"].lower()
        assert "permit" in data["compliance_notes"].lower()

    def test_get_hvac_compliance_notes(self, client):
        """Test getting HVAC compliance notes."""
        response = client.get("/invoices/templates/compliance-notes?trade_type=hvac")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["trade_type"] == "hvac"
        assert "hvac" in data["compliance_notes"].lower()
        assert "manufacturer" in data["compliance_notes"].lower()
