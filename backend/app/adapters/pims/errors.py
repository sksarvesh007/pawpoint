"""PIMS adapter error hierarchy."""


class PIMSError(Exception):
    """Base exception for all PIMS adapter errors."""

    def __init__(self, message: str, pims_type: str = "unknown") -> None:
        self.pims_type = pims_type
        super().__init__(message)


class PIMSAuthError(PIMSError):
    """Authentication failure with PIMS system."""


class PIMSRateLimitError(PIMSError):
    """Rate limit exceeded by PIMS API."""

    def __init__(
        self,
        message: str,
        pims_type: str = "unknown",
        retry_after: int = 60,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, pims_type)


class PIMSNotFoundError(PIMSError):
    """Resource not found in PIMS system."""


class PIMSWriteError(PIMSError):
    """Write operation failed in PIMS system."""


class PIMSConnectionError(PIMSError):
    """Network/connection error communicating with PIMS."""
