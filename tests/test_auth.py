"""
Test authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_user():
    """Test user registration"""
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 201
    assert "username" in response.json()
    assert response.json()["username"] == "testuser"


def test_register_duplicate_user():
    """Test registering duplicate username"""
    # First registration
    client.post(
        "/auth/register",
        json={
            "username": "duplicate",
            "password": "password123"
        }
    )

    # Second registration with same username
    response = client.post(
        "/auth/register",
        json={
            "username": "duplicate",
            "password": "password456"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login():
    """Test user login"""
    # Register user first
    client.post(
        "/auth/register",
        json={
            "username": "logintest",
            "password": "password123"
        }
    )

    # Login
    response = client.post(
        "/auth/token",
        data={
            "username": "logintest",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/token",
        data={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
