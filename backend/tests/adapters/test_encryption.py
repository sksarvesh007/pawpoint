"""Tests for PIMS credential encryption."""

import pytest

from app.adapters.pims.encryption import decrypt_credentials, encrypt_credentials


@pytest.mark.asyncio
async def test_encrypt_decrypt_roundtrip() -> None:
    """Encrypting then decrypting should return original data."""
    original = {
        "client_id": "abc123",
        "client_secret": "super-secret-value",
        "partner_id": "partner-456",
    }

    encrypted = encrypt_credentials(original)

    # Encrypted should be bytes and different from original
    assert isinstance(encrypted, bytes)
    assert b"super-secret-value" not in encrypted

    decrypted = decrypt_credentials(encrypted)
    assert decrypted == original


@pytest.mark.asyncio
async def test_encrypt_empty_dict() -> None:
    """Should handle empty credentials dict."""
    encrypted = encrypt_credentials({})
    decrypted = decrypt_credentials(encrypted)
    assert decrypted == {}


@pytest.mark.asyncio
async def test_encrypt_special_characters() -> None:
    """Should handle credentials with special characters."""
    original = {
        "api_key": "key-with-special-chars!@#$%^&*()",
        "url": "https://api.example.com/v1?token=abc&lang=en",
    }

    encrypted = encrypt_credentials(original)
    decrypted = decrypt_credentials(encrypted)
    assert decrypted == original


@pytest.mark.asyncio
async def test_different_data_produces_different_encrypted() -> None:
    """Different input should produce different encrypted output."""
    data_a = {"key": "value_a"}
    data_b = {"key": "value_b"}

    encrypted_a = encrypt_credentials(data_a)
    encrypted_b = encrypt_credentials(data_b)

    # Fernet adds randomness, but the data bytes differ
    assert encrypted_a != encrypted_b
