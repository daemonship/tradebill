"""Pytest fixtures for testing."""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from app.core.database import Base, get_db
from app.main import app
from app.models import User, BusinessProfile
from app.core.auth import get_password_hash, create_access_token


# Test database settings
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """Create a test database."""
    # Use in-memory SQLite for testing
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    # Override the get_db dependency
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear the override
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    h = get_password_hash("securepassword123")
    user = User(
        email="test@example.com",
        hashed_password=h,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_db):
    """Create a test user and return auth headers."""
    # Create user in the test database
    h = get_password_hash("securepassword123")
    user = User(
        email="test@example.com",
        hashed_password=h,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Generate token for the user
    token = create_access_token(data={"sub": user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_token(test_user):
    """Create an auth token for the test user."""
    return create_access_token(data={"sub": test_user.id})


@pytest.fixture
def business_profile(test_db, test_user):
    """Create a test business profile."""
    profile = BusinessProfile(
        user_id=test_user.id,
        business_name="Test Plumbing Co",
        phone="555-123-4567",
        email="business@test.com",
        license_number="TPC-12345",
    )
    test_db.add(profile)
    test_db.commit()
    test_db.refresh(profile)
    return profile
