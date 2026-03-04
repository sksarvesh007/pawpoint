"""PIMS service for connection management."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.pims.encryption import encrypt_credentials
from app.adapters.pims.errors import PIMSError
from app.adapters.pims.factory import get_pims_adapter
from app.core.instrumentation import traced
from app.models.clinic import Clinic, PIMSConnectionStatus, PIMSType
from app.models.pims_sync_log import PIMSSyncLog


class PIMSService:
    """Service for managing PIMS connections and credentials."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @traced(span_name="pims.save_credentials")
    async def save_credentials(
        self,
        clinic_id: UUID,
        pims_type: str,
        credentials: dict,
    ) -> dict:
        """Save encrypted PIMS credentials for a clinic."""
        result = await self.db.execute(select(Clinic).where(Clinic.id == clinic_id))
        clinic = result.scalar_one_or_none()
        if not clinic:
            raise ValueError("Clinic not found")

        clinic.pims_type = (
            PIMSType(pims_type) if isinstance(pims_type, str) else pims_type
        )
        clinic.pims_credentials_encrypted = encrypt_credentials(credentials)
        clinic.pims_connection_status = PIMSConnectionStatus.DISCONNECTED

        await self.db.flush()

        return {
            "pims_type": str(clinic.pims_type),
            "connection_status": str(clinic.pims_connection_status),
            "last_sync_at": clinic.pims_last_sync_at,
            "message": "Credentials saved. Test connection to verify.",
        }

    @traced(span_name="pims.test_connection")
    async def test_connection(self, clinic_id: UUID) -> dict:
        """Test PIMS connection for a clinic."""
        result = await self.db.execute(select(Clinic).where(Clinic.id == clinic_id))
        clinic = result.scalar_one_or_none()
        if not clinic:
            raise ValueError("Clinic not found")

        if clinic.pims_type == PIMSType.NONE:
            return {
                "connected": False,
                "message": "No PIMS configured",
            }

        try:
            adapter = get_pims_adapter(clinic)
            test_result = await adapter.test_connection()
            await adapter.close()

            # Update clinic connection status
            if test_result.get("connected"):
                clinic.pims_connection_status = PIMSConnectionStatus.CONNECTED
            else:
                clinic.pims_connection_status = PIMSConnectionStatus.ERROR
            await self.db.flush()

            return test_result
        except PIMSError as e:
            clinic.pims_connection_status = PIMSConnectionStatus.ERROR
            await self.db.flush()
            return {
                "connected": False,
                "message": str(e),
            }

    @traced(span_name="pims.disconnect")
    async def disconnect(self, clinic_id: UUID) -> dict:
        """Disconnect PIMS and clear credentials."""
        result = await self.db.execute(select(Clinic).where(Clinic.id == clinic_id))
        clinic = result.scalar_one_or_none()
        if not clinic:
            raise ValueError("Clinic not found")

        clinic.pims_type = PIMSType.NONE
        clinic.pims_credentials_encrypted = None
        clinic.pims_connection_status = PIMSConnectionStatus.DISCONNECTED
        clinic.pims_settings = None

        await self.db.flush()

        return {
            "pims_type": "none",
            "connection_status": "disconnected",
            "last_sync_at": None,
            "message": "PIMS disconnected and credentials cleared.",
        }

    @traced(span_name="pims.get_connection_status")
    async def get_connection_status(self, clinic_id: UUID) -> dict:
        """Get current PIMS connection status."""
        result = await self.db.execute(select(Clinic).where(Clinic.id == clinic_id))
        clinic = result.scalar_one_or_none()
        if not clinic:
            raise ValueError("Clinic not found")

        return {
            "pims_type": str(clinic.pims_type),
            "connection_status": str(clinic.pims_connection_status),
            "last_sync_at": clinic.pims_last_sync_at,
        }

    @traced(span_name="pims.get_sync_logs")
    async def get_sync_logs(
        self, clinic_id: UUID, limit: int = 20
    ) -> list[PIMSSyncLog]:
        """Get recent sync logs for a clinic."""
        result = await self.db.execute(
            select(PIMSSyncLog)
            .where(PIMSSyncLog.clinic_id == clinic_id)
            .order_by(PIMSSyncLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
