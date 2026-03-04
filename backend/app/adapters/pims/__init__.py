"""PIMS adapter package.

Provides a unified interface for integrating with Practice Information
Management Systems (ezyVet, Vetspire, Covetrus, etc.)
"""

from app.adapters.pims.base import IPIMSAdapter
from app.adapters.pims.errors import (
    PIMSAuthError,
    PIMSConnectionError,
    PIMSError,
    PIMSNotFoundError,
    PIMSRateLimitError,
    PIMSWriteError,
)
from app.adapters.pims.factory import get_pims_adapter
from app.adapters.pims.types import (
    PIMSAppointment,
    PIMSPatient,
    PIMSProvider,
    PIMSTimeSlot,
)

__all__ = [
    "IPIMSAdapter",
    "PIMSAppointment",
    "PIMSAuthError",
    "PIMSConnectionError",
    "PIMSError",
    "PIMSNotFoundError",
    "PIMSPatient",
    "PIMSProvider",
    "PIMSRateLimitError",
    "PIMSTimeSlot",
    "PIMSWriteError",
    "get_pims_adapter",
]
