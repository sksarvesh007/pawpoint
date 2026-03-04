"""Provider service for CRUD operations."""

from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.instrumentation import traced
from app.models.provider import Provider
from app.schemas.provider import ProviderCreate, ProviderUpdate


class ProviderService:
    """Service for provider CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @traced(span_name="provider.list_providers")
    async def list_providers(
        self, clinic_id: UUID, active_only: bool = True
    ) -> list[Provider]:
        """List providers for a clinic."""
        query = select(Provider).where(
            and_(
                Provider.clinic_id == clinic_id,
                Provider.deleted_at.is_(None),
            )
        )

        if active_only:
            query = query.where(Provider.is_active.is_(True))

        query = query.order_by(Provider.display_order.asc(), Provider.last_name.asc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    @traced(span_name="provider.get_provider")
    async def get_provider(self, clinic_id: UUID, provider_id: UUID) -> Provider | None:
        """Get a single provider by ID."""
        result = await self.db.execute(
            select(Provider).where(
                and_(
                    Provider.id == provider_id,
                    Provider.clinic_id == clinic_id,
                    Provider.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    @traced(span_name="provider.create_provider")
    async def create_provider(self, clinic_id: UUID, data: ProviderCreate) -> Provider:
        """Create a new provider."""
        provider = Provider(
            clinic_id=clinic_id,
            **data.model_dump(),
        )
        self.db.add(provider)
        await self.db.flush()
        await self.db.refresh(provider)
        return provider

    @traced(span_name="provider.update_provider")
    async def update_provider(
        self, clinic_id: UUID, provider_id: UUID, data: ProviderUpdate
    ) -> Provider | None:
        """Update an existing provider."""
        provider = await self.get_provider(clinic_id, provider_id)
        if not provider:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(provider, field, value)

        await self.db.flush()
        await self.db.refresh(provider)
        return provider

    @traced(span_name="provider.delete_provider")
    async def delete_provider(self, clinic_id: UUID, provider_id: UUID) -> bool:
        """Soft delete a provider."""
        provider = await self.get_provider(clinic_id, provider_id)
        if not provider:
            return False

        provider.soft_delete()
        await self.db.flush()
        return True
