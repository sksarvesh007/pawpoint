"""Authentication API endpoint tests."""

import uuid
from typing import Any

import pytest
from httpx import AsyncClient

# =============================================================================
# Helper Functions
# =============================================================================


def make_unique_email(prefix: str = "test") -> str:
    """Generate a unique email for test isolation."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


def make_registration_payload(
    clinic_name: str | None = None,
    email: str | None = None,
    password: str = "SecurePassword123!",
) -> dict[str, str]:
    """Create a registration payload with optional overrides."""
    return {
        "clinic_name": clinic_name or f"Clinic {uuid.uuid4().hex[:8]}",
        "email": email or make_unique_email(),
        "password": password,
        "admin_first_name": "Test",
        "admin_last_name": "User",
    }


async def register_user(
    client: AsyncClient, payload: dict[str, str] | None = None
) -> dict[str, Any]:
    """
    Register a user and return the response data.

    Raises AssertionError if registration fails.
    """
    if payload is None:
        payload = make_registration_payload()

    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, (
        f"Registration failed with status {response.status_code}: {response.json()}"
    )
    return response.json()


# =============================================================================
# Registration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    """Test successful clinic registration with full response validation."""
    email = make_unique_email("register")
    clinic_name = f"Test Clinic {uuid.uuid4().hex[:8]}"

    payload = make_registration_payload(clinic_name=clinic_name, email=email)
    response = await client.post("/api/v1/auth/register", json=payload)

    # Validate status code
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    # Validate response structure
    data = response.json()
    assert "access_token" in data, "Response missing access_token"
    assert data["token_type"] == "bearer", f"Expected bearer, got {data['token_type']}"
    assert "expires_in" in data, "Response missing expires_in"

    # Validate clinic data
    assert data["clinic"]["name"] == clinic_name
    assert "id" in data["clinic"], "Clinic missing id"
    assert "slug" in data["clinic"], "Clinic missing slug"

    # Validate user data
    assert data["user"]["email"] == email
    assert data["user"]["role"] == "admin", (
        f"Expected role 'admin', got '{data['user']['role']}'"
    )
    assert "id" in data["user"], "User missing id"
    assert data["user"]["first_name"] == "Test"
    assert data["user"]["last_name"] == "User"

    # Verify httpOnly cookie is set
    assert "access_token" in response.cookies, "Expected access_token cookie to be set"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    """Test that registration with an existing email fails with proper error."""
    email = make_unique_email("duplicate")

    # First registration should succeed
    payload1 = make_registration_payload(clinic_name="Clinic A", email=email)
    response1 = await client.post("/api/v1/auth/register", json=payload1)
    assert response1.status_code == 201, "First registration should succeed"

    # Second registration with same email should fail
    payload2 = make_registration_payload(clinic_name="Clinic B", email=email)
    response2 = await client.post("/api/v1/auth/register", json=payload2)

    assert response2.status_code == 400, (
        f"Expected 400 for duplicate email, got {response2.status_code}"
    )

    error_detail = response2.json().get("detail", "")
    assert "Registration failed" in error_detail, (
        f"Expected 'Registration failed' in error, got: {error_detail}"
    )


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient) -> None:
    """Test that registration with a weak password fails."""
    payload = make_registration_payload(password="weak")
    response = await client.post("/api/v1/auth/register", json=payload)

    # Should fail validation (either 400 or 422 depending on implementation)
    assert response.status_code in (400, 422), (
        f"Expected 400 or 422 for weak password, got {response.status_code}"
    )


@pytest.mark.asyncio
async def test_register_invalid_email_format(client: AsyncClient) -> None:
    """Test that registration with invalid email format fails."""
    payload = make_registration_payload(email="not-an-email")
    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code in (400, 422), (
        f"Expected 400 or 422 for invalid email, got {response.status_code}"
    )


# =============================================================================
# Login Tests
# =============================================================================


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    """Test successful login with full response validation."""
    email = make_unique_email("login")
    password = "SecurePassword123!"

    # Register first and validate success
    register_payload = make_registration_payload(email=email, password=password)
    await register_user(client, register_payload)

    # Login
    login_payload = {"email": email, "password": password}
    response = await client.post("/api/v1/auth/login", json=login_payload)

    # Validate status code
    assert response.status_code == 200, (
        f"Login failed with status {response.status_code}: {response.json()}"
    )

    # Validate response structure
    data = response.json()
    assert "access_token" in data, "Response missing access_token"
    assert data["token_type"] == "bearer"
    assert "expires_in" in data
    assert data["user"]["email"] == email

    # Verify cookie is set
    assert "access_token" in response.cookies, "Expected access_token cookie"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient) -> None:
    """Test login with incorrect password fails with 401."""
    email = make_unique_email("wrongpass")
    correct_password = "CorrectPassword123!"
    wrong_password = "WrongPassword123!"

    # Register first
    register_payload = make_registration_payload(email=email, password=correct_password)
    await register_user(client, register_payload)

    # Login with wrong password
    login_payload = {"email": email, "password": wrong_password}
    response = await client.post("/api/v1/auth/login", json=login_payload)

    assert response.status_code == 401, (
        f"Expected 401 for wrong password, got {response.status_code}"
    )

    # Validate WWW-Authenticate header for 401 responses
    assert "www-authenticate" in response.headers, (
        "Expected WWW-Authenticate header for 401 response"
    )


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    """Test login with non-existent email fails with 401."""
    login_payload = {
        "email": f"nonexistent_{uuid.uuid4().hex[:8]}@example.com",
        "password": "AnyPassword123!",
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)

    assert response.status_code == 401, (
        f"Expected 401 for non-existent user, got {response.status_code}"
    )


@pytest.mark.asyncio
async def test_login_invalid_email_format(client: AsyncClient) -> None:
    """Test login with invalid email format fails."""
    login_payload = {"email": "not-an-email", "password": "Password123!"}
    response = await client.post("/api/v1/auth/login", json=login_payload)

    assert response.status_code in (400, 422), (
        f"Expected 400 or 422 for invalid email, got {response.status_code}"
    )


# =============================================================================
# Logout Tests
# =============================================================================


@pytest.mark.asyncio
async def test_logout_clears_cookie(client: AsyncClient) -> None:
    """Test that logout properly clears the access_token cookie."""
    email = make_unique_email("logout")

    # Register to get a valid session
    register_payload = make_registration_payload(email=email)
    await register_user(client, register_payload)

    # Logout
    response = await client.post("/api/v1/auth/logout")

    assert response.status_code == 204, (
        f"Expected 204 for logout, got {response.status_code}"
    )

    # Verify cookie is properly cleared
    set_cookie_header = response.headers.get("set-cookie", "")
    assert "access_token" in set_cookie_header, (
        "Expected access_token in Set-Cookie header"
    )

    # Cookie should be cleared via empty value or Max-Age=0
    cookie_is_cleared = (
        'access_token=""' in set_cookie_header
        or "access_token=;" in set_cookie_header
        or "Max-Age=0" in set_cookie_header
    )
    assert cookie_is_cleared, (
        f"Cookie not properly cleared. Set-Cookie header: {set_cookie_header}"
    )


@pytest.mark.asyncio
async def test_logout_without_session(client: AsyncClient) -> None:
    """Test that logout works even without an active session."""
    response = await client.post("/api/v1/auth/logout")

    # Should still return 204 (idempotent operation)
    assert response.status_code == 204, (
        f"Expected 204 for logout without session, got {response.status_code}"
    )
