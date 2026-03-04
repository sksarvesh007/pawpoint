"""Patient service for CRUD operations."""

from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.instrumentation import traced
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


class PatientService:
    """Service for patient CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @traced(span_name="patient.list_patients")
    async def list_patients(
        self,
        clinic_id: UUID,
        page: int = 1,
        limit: int = 20,
        search: str | None = None,
        species: str | None = None,
    ) -> tuple[list[Patient], int]:
        """List patients with pagination, search, and species filter."""
        query = select(Patient).where(
            and_(
                Patient.clinic_id == clinic_id,
                Patient.deleted_at.is_(None),
            )
        )

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Patient.name.ilike(search_term),
                    Patient.owner_first_name.ilike(search_term),
                    Patient.owner_last_name.ilike(search_term),
                    Patient.owner_phone.ilike(search_term),
                    Patient.owner_email.ilike(search_term),
                )
            )

        if species:
            query = query.where(Patient.species == species)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination
        query = query.order_by(Patient.name.asc())
        query = query.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(query)
        patients = list(result.scalars().all())

        return patients, total

    @traced(span_name="patient.get_patient")
    async def get_patient(self, clinic_id: UUID, patient_id: UUID) -> Patient | None:
        """Get a single patient by ID."""
        result = await self.db.execute(
            select(Patient).where(
                and_(
                    Patient.id == patient_id,
                    Patient.clinic_id == clinic_id,
                    Patient.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    @traced(span_name="patient.create_patient")
    async def create_patient(self, clinic_id: UUID, data: PatientCreate) -> Patient:
        """Create a new patient."""
        patient = Patient(
            clinic_id=clinic_id,
            **data.model_dump(),
        )
        self.db.add(patient)
        await self.db.flush()
        await self.db.refresh(patient)
        return patient

    @traced(span_name="patient.update_patient")
    async def update_patient(
        self, clinic_id: UUID, patient_id: UUID, data: PatientUpdate
    ) -> Patient | None:
        """Update an existing patient."""
        patient = await self.get_patient(clinic_id, patient_id)
        if not patient:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)

        await self.db.flush()
        await self.db.refresh(patient)
        return patient

    @traced(span_name="patient.delete_patient")
    async def delete_patient(self, clinic_id: UUID, patient_id: UUID) -> bool:
        """Soft delete a patient."""
        patient = await self.get_patient(clinic_id, patient_id)
        if not patient:
            return False

        patient.soft_delete()
        await self.db.flush()
        return True

    @traced(span_name="patient.search_patients")
    async def search_patients(
        self, clinic_id: UUID, query: str, limit: int = 10
    ) -> list[Patient]:
        """Search patients by name, owner name, or phone (for AI autocomplete)."""
        search_term = f"%{query}%"
        result = await self.db.execute(
            select(Patient)
            .where(
                and_(
                    Patient.clinic_id == clinic_id,
                    Patient.deleted_at.is_(None),
                    or_(
                        Patient.name.ilike(search_term),
                        Patient.owner_first_name.ilike(search_term),
                        Patient.owner_last_name.ilike(search_term),
                        Patient.owner_phone.ilike(search_term),
                    ),
                )
            )
            .order_by(Patient.name.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
