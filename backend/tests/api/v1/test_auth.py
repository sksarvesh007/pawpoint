
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Test successful clinic registration."""
    payload = {
        "clinic_name": "Test Clinic",
        "email": "admin@testclinic.com",
        "password": "SecurePassword123!",
        "admin_first_name": "Admin",
        "admin_last_name": "User"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    if response.status_code != 201:
        print(response.json())
        
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["clinic"]["name"] == "Test Clinic"
    assert data["user"]["email"] == "admin@testclinic.com"
    assert data["user"]["role"] == "admin"
    
    # Verify cookie
    assert "access_token" in response.cookies


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with existing email fails."""
    # First registration
    payload = {
        "clinic_name": "Clinic A",
        "email": "duplicate@example.com",
        "password": "Password123!",
        "admin_first_name": "Test",
        "admin_last_name": "User"
    }
    response1 = await client.post("/api/v1/auth/register", json=payload)
    assert response1.status_code == 201

    # Second registration with same email
    payload["clinic_name"] = "Clinic B"
    response2 = await client.post("/api/v1/auth/register", json=payload)
    assert response2.status_code == 400
    assert "Registration failed" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login."""
    # Register first
    register_payload = {
        "clinic_name": "Login Clinic",
        "email": "login@example.com",
        "password": "Password123!",
        "admin_first_name": "Login",
        "admin_last_name": "User"
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    # Login
    login_payload = {
        "email": "login@example.com",
        "password": "Password123!"
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "access_token" in response.cookies


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with wrong password."""
    # Register
    register_payload = {
        "clinic_name": "Wrong Pass Clinic",
        "email": "wrongpass@example.com",
        "password": "Password123!",
        "admin_first_name": "Test",
        "admin_last_name": "User"
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    # Login with wrong password
    login_payload = {
        "email": "wrongpass@example.com",
        "password": "WrongPassword!"
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test logout clears cookies."""
    # Register/Login to set cookie
    payload = {
        "clinic_name": "Logout Clinic",
        "email": "logout@example.com",
        "password": "Password123!",
        "admin_first_name": "Logout",
        "admin_last_name": "User"
    }
    await client.post("/api/v1/auth/register", json=payload)
    
    # Logout
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 204
    
    # Check cookie is cleared (max-age=0 or empty value depending on implementation)
    # httpx cookie handling can be subtle, but we can check if it's "deleted"
    # Typically headers will contain 'Set-Cookie: access_token=""; ...'
    assert "access_token" in response.headers["set-cookie"]
    assert 'access_token=""' in response.headers["set-cookie"] or 'Max-Age=0' in response.headers["set-cookie"]
