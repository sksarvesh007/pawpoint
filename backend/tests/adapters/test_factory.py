"""Tests for PIMS adapter factory."""

import uuid

import pytest

from app.adapters.pims.errors import PIMSError
from app.adapters.pims.factory import get_pims_adapter
from app.models.clinic import PIMSType


class FakeClinic:
    """Minimal clinic object for factory tests."""

    def __init__(
        self,
        pims_type: PIMSType = PIMSType.NONE,
        pims_credentials_encrypted: bytes | None = None,
    ) -> None:
        self.id = uuid.uuid4()
        self.pims_type = pims_type
        self.pims_credentials_encrypted = pims_credentials_encrypted


def test_factory_raises_for_none_type() -> None:
    """Should raise PIMSError when pims_type is 'none'."""
    clinic = FakeClinic(pims_type=PIMSType.NONE)

    with pytest.raises(PIMSError, match="No PIMS configured"):
        get_pims_adapter(clinic)  # type: ignore[arg-type]


def test_factory_raises_for_missing_credentials() -> None:
    """Should raise PIMSError when credentials are missing."""
    clinic = FakeClinic(pims_type=PIMSType.EZYVET, pims_credentials_encrypted=None)

    with pytest.raises(PIMSError, match="credentials"):
        get_pims_adapter(clinic)  # type: ignore[arg-type]
