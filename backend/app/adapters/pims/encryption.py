"""Credential encryption for PIMS API keys and secrets.

Uses Fernet symmetric encryption with a key derived from the
application's secret_key via SHA-256 hashing.
"""

import hashlib
import json

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


def _get_fernet() -> Fernet:
    """Derive a Fernet key from the application secret key."""
    secret = settings.secret_key.get_secret_value().encode()
    # SHA-256 produces 32 bytes, base64 encode for Fernet (which needs 32 url-safe base64 bytes)
    import base64

    key = base64.urlsafe_b64encode(hashlib.sha256(secret).digest())
    return Fernet(key)


def encrypt_credentials(credentials: dict) -> bytes:
    """Encrypt a credentials dictionary.

    Args:
        credentials: Dictionary of credential key-value pairs.

    Returns:
        Encrypted bytes suitable for database storage.
    """
    fernet = _get_fernet()
    plaintext = json.dumps(credentials).encode("utf-8")
    return fernet.encrypt(plaintext)


def decrypt_credentials(encrypted: bytes) -> dict:
    """Decrypt credentials back to a dictionary.

    Args:
        encrypted: Encrypted bytes from the database.

    Returns:
        Original credentials dictionary.

    Raises:
        ValueError: If decryption fails (wrong key or corrupted data).
    """
    fernet = _get_fernet()
    try:
        plaintext = fernet.decrypt(encrypted)
        return json.loads(plaintext.decode("utf-8"))
    except InvalidToken as e:
        raise ValueError(
            "Failed to decrypt PIMS credentials: invalid key or corrupted data"
        ) from e
