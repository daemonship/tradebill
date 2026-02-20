"""Tests for business profile API."""
import pytest
from fastapi.testclient import TestClient


def test_create_profile(client: TestClient, test_user, auth_token):
    """Test creating a business profile."""
    response = client.post(
        "/profile",
        json={
            "business_name": "Test Plumbing Co",
            "phone": "555-123-4567",
            "email": "business@test.com",
            "license_number": "TPC-12345",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["business_name"] == "Test Plumbing Co"
    assert data["phone"] == "555-123-4567"
    assert data["email"] == "business@test.com"
    assert data["license_number"] == "TPC-12345"
    assert "id" in data
    assert data["user_id"] == test_user.id


def test_get_profile(client: TestClient, test_user, business_profile, auth_token):
    """Test getting a business profile."""
    response = client.get(
        "/profile",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["business_name"] == "Test Plumbing Co"
    assert data["license_number"] == "TPC-12345"


def test_get_profile_not_found(client: TestClient, test_user, auth_token):
    """Test getting a profile that doesn't exist."""
    response = client.get(
        "/profile",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404
    assert "Business profile not found" in response.json()["detail"]


def test_update_profile(client: TestClient, test_user, business_profile, auth_token):
    """Test updating a business profile."""
    response = client.put(
        "/profile",
        json={
            "business_name": "Updated Plumbing Co",
            "license_number": "UPDATED-999",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["business_name"] == "Updated Plumbing Co"
    assert data["license_number"] == "UPDATED-999"
    # Other fields should remain unchanged
    assert data["phone"] == "555-123-4567"


def test_update_profile_partial(client: TestClient, test_user, business_profile, auth_token):
    """Test partially updating a business profile."""
    response = client.put(
        "/profile",
        json={"phone": "555-999-9999"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "555-999-9999"
    # Other fields should remain unchanged
    assert data["business_name"] == "Test Plumbing Co"


def test_create_duplicate_profile(client: TestClient, test_user, business_profile, auth_token):
    """Test that creating a duplicate profile fails."""
    response = client.post(
        "/profile",
        json={"business_name": "Another Business"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_unauthorized_profile_access(client: TestClient):
    """Test accessing profile without authentication."""
    response = client.get("/profile")
    assert response.status_code == 401
