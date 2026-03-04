"""PIMS adapter factory.

Dynamically instantiates the correct adapter based on clinic's PIMS type.
"""

from app.adapters.pims.base import IPIMSAdapter
from app.adapters.pims.encryption import decrypt_credentials
from app.adapters.pims.errors import PIMSError
from app.models.clinic import Clinic, PIMSType


def get_pims_adapter(clinic: Clinic) -> IPIMSAdapter:
    """Create the appropriate PIMS adapter for a clinic.

    Args:
        clinic: Clinic model with pims_type and encrypted credentials.

    Returns:
        Configured PIMS adapter instance.

    Raises:
        PIMSError: If PIMS type is NONE or credentials are missing.
    """
    if clinic.pims_type == PIMSType.NONE:
        raise PIMSError("No PIMS configured for this clinic", pims_type="none")

    if not clinic.pims_credentials_encrypted:
        raise PIMSError(
            "No PIMS credentials configured for this clinic",
            pims_type=str(clinic.pims_type),
        )

    credentials = decrypt_credentials(clinic.pims_credentials_encrypted)

    if clinic.pims_type == PIMSType.EZYVET:
        from app.adapters.pims.ezyvet import EzyVetAdapter

        return EzyVetAdapter(
            clinic_id=clinic.id,
            credentials=credentials,
            settings=clinic.pims_settings,
        )

    if clinic.pims_type == PIMSType.VETSPIRE:
        from app.adapters.pims.vetspire import VetspireAdapter

        return VetspireAdapter(
            clinic_id=clinic.id,
            credentials=credentials,
            settings=clinic.pims_settings,
        )

    if clinic.pims_type in (
        PIMSType.AVIMARK,
        PIMSType.CORNERSTONE,
        PIMSType.PULSE,
        PIMSType.IMPROMED,
    ):
        from app.adapters.pims.covetrus import CovetrusAdapter

        return CovetrusAdapter(
            clinic_id=clinic.id,
            credentials=credentials,
            settings=clinic.pims_settings,
        )

    raise PIMSError(
        f"Unsupported PIMS type: {clinic.pims_type}",
        pims_type=str(clinic.pims_type),
    )
