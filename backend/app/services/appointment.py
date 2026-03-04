"""Appointment service for CRUD operations."""

from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.instrumentation import traced
from app.models.appointment import Appointment, AppointmentStatus
from app.models.patient import Patient
from app.models.provider import Provider
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate


class AppointmentService:
    """Service for appointment CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @traced(span_name="appointment.list_appointments")
    async def list_appointments(
        self,
        clinic_id: UUID,
        page: int = 1,
        limit: int = 20,
        start_date: date | None = None,
        end_date: date | None = None,
        status: str | None = None,
        provider_id: UUID | None = None,
    ) -> tuple[list[dict], int]:
        """List appointments with pagination and filters.

        Returns denormalized dicts with patient_name and provider_name.
        """
        query = (
            select(Appointment, Patient.name, Provider.first_name, Provider.last_name)
            .outerjoin(Patient, Appointment.patient_id == Patient.id)
            .outerjoin(Provider, Appointment.provider_id == Provider.id)
            .where(
                and_(
                    Appointment.clinic_id == clinic_id,
                    Appointment.deleted_at.is_(None),
                )
            )
        )

        if start_date:
            query = query.where(
                Appointment.start_time
                >= datetime.combine(start_date, datetime.min.time())
            )
        if end_date:
            query = query.where(
                Appointment.start_time
                <= datetime.combine(end_date, datetime.max.time())
            )
        if status:
            query = query.where(Appointment.status == status)
        if provider_id:
            query = query.where(Appointment.provider_id == provider_id)

        # Count total (using subquery of the filtered appointments)
        count_subq = (
            select(func.count())
            .select_from(Appointment)
            .where(
                and_(
                    Appointment.clinic_id == clinic_id,
                    Appointment.deleted_at.is_(None),
                )
            )
        )
        if start_date:
            count_subq = count_subq.where(
                Appointment.start_time
                >= datetime.combine(start_date, datetime.min.time())
            )
        if end_date:
            count_subq = count_subq.where(
                Appointment.start_time
                <= datetime.combine(end_date, datetime.max.time())
            )
        if status:
            count_subq = count_subq.where(Appointment.status == status)
        if provider_id:
            count_subq = count_subq.where(Appointment.provider_id == provider_id)

        total_result = await self.db.execute(count_subq)
        total = total_result.scalar_one()

        # Apply pagination
        query = query.order_by(Appointment.start_time.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(query)
        rows = result.all()

        items = []
        for row in rows:
            appt = row[0]
            patient_name = row[1]
            provider_first = row[2]
            provider_last = row[3]
            provider_name = (
                f"{provider_first} {provider_last}"
                if provider_first and provider_last
                else None
            )

            item = {
                "id": appt.id,
                "start_time": appt.start_time,
                "end_time": appt.end_time,
                "appointment_type": str(appt.appointment_type),
                "status": str(appt.status),
                "source": str(appt.source),
                "reason": appt.reason,
                "patient_name": patient_name,
                "provider_name": provider_name,
            }
            items.append(item)

        return items, total

    @traced(span_name="appointment.get_appointment")
    async def get_appointment(
        self, clinic_id: UUID, appointment_id: UUID
    ) -> dict | None:
        """Get a single appointment with patient/provider names."""
        result = await self.db.execute(
            select(Appointment, Patient.name, Provider.first_name, Provider.last_name)
            .outerjoin(Patient, Appointment.patient_id == Patient.id)
            .outerjoin(Provider, Appointment.provider_id == Provider.id)
            .where(
                and_(
                    Appointment.id == appointment_id,
                    Appointment.clinic_id == clinic_id,
                    Appointment.deleted_at.is_(None),
                )
            )
        )
        row = result.one_or_none()
        if not row:
            return None

        appt = row[0]
        patient_name = row[1]
        provider_first = row[2]
        provider_last = row[3]
        provider_name = (
            f"{provider_first} {provider_last}"
            if provider_first and provider_last
            else None
        )

        return {
            "id": appt.id,
            "clinic_id": appt.clinic_id,
            "patient_id": appt.patient_id,
            "provider_id": appt.provider_id,
            "call_log_id": appt.call_log_id,
            "start_time": appt.start_time,
            "end_time": appt.end_time,
            "duration_minutes": appt.duration_minutes,
            "appointment_type": str(appt.appointment_type),
            "status": str(appt.status),
            "source": str(appt.source),
            "reason": appt.reason,
            "notes": appt.notes,
            "client_notes": appt.client_notes,
            "cancellation_reason": appt.cancellation_reason,
            "cancelled_at": appt.cancelled_at,
            "patient_name": patient_name,
            "provider_name": provider_name,
            "pims_id": appt.pims_id,
            "sync_status": str(appt.sync_status),
            "created_at": appt.created_at,
            "updated_at": appt.updated_at,
        }

    @traced(span_name="appointment.create_appointment")
    async def create_appointment(
        self,
        clinic_id: UUID,
        data: AppointmentCreate,
        source: str = "dashboard",
    ) -> Appointment:
        """Create a new appointment.

        Validates no provider overlap exists for the requested time slot.
        """
        # Validate no provider overlap if provider is specified
        if data.provider_id:
            overlap = await self._check_provider_overlap(
                clinic_id, data.provider_id, data.start_time, data.end_time
            )
            if overlap:
                from fastapi import HTTPException

                raise HTTPException(
                    status_code=409,
                    detail="Provider has a conflicting appointment at this time",
                )

        duration_minutes = int((data.end_time - data.start_time).total_seconds() / 60)

        appointment = Appointment(
            clinic_id=clinic_id,
            patient_id=data.patient_id,
            provider_id=data.provider_id,
            start_time=data.start_time,
            end_time=data.end_time,
            duration_minutes=duration_minutes,
            appointment_type=data.appointment_type,
            source=source,
            reason=data.reason,
            notes=data.notes,
            client_notes=data.client_notes,
        )
        self.db.add(appointment)
        await self.db.flush()
        await self.db.refresh(appointment)
        return appointment

    @traced(span_name="appointment.update_appointment")
    async def update_appointment(
        self, clinic_id: UUID, appointment_id: UUID, data: AppointmentUpdate
    ) -> Appointment | None:
        """Update an existing appointment."""
        result = await self.db.execute(
            select(Appointment).where(
                and_(
                    Appointment.id == appointment_id,
                    Appointment.clinic_id == clinic_id,
                    Appointment.deleted_at.is_(None),
                )
            )
        )
        appointment = result.scalar_one_or_none()
        if not appointment:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # If times are changing, check for overlap
        start = update_data.get("start_time", appointment.start_time)
        end = update_data.get("end_time", appointment.end_time)
        provider = update_data.get("provider_id", appointment.provider_id)

        if provider and (
            "start_time" in update_data
            or "end_time" in update_data
            or "provider_id" in update_data
        ):
            overlap = await self._check_provider_overlap(
                clinic_id, provider, start, end, exclude_id=appointment_id
            )
            if overlap:
                from fastapi import HTTPException

                raise HTTPException(
                    status_code=409,
                    detail="Provider has a conflicting appointment at this time",
                )

        for field, value in update_data.items():
            setattr(appointment, field, value)

        # Recalculate duration if times changed
        if "start_time" in update_data or "end_time" in update_data:
            appointment.duration_minutes = int(
                (appointment.end_time - appointment.start_time).total_seconds() / 60
            )

        await self.db.flush()
        await self.db.refresh(appointment)
        return appointment

    @traced(span_name="appointment.update_status")
    async def update_status(
        self,
        clinic_id: UUID,
        appointment_id: UUID,
        status: str | AppointmentStatus,
        cancellation_reason: str | None = None,
    ) -> Appointment | None:
        """Update appointment status."""
        result = await self.db.execute(
            select(Appointment).where(
                and_(
                    Appointment.id == appointment_id,
                    Appointment.clinic_id == clinic_id,
                    Appointment.deleted_at.is_(None),
                )
            )
        )
        appointment = result.scalar_one_or_none()
        if not appointment:
            return None

        appointment.status = (
            AppointmentStatus(status) if isinstance(status, str) else status
        )

        if status == AppointmentStatus.CANCELLED:
            appointment.cancelled_at = datetime.now(UTC)
            appointment.cancellation_reason = cancellation_reason

        await self.db.flush()
        await self.db.refresh(appointment)
        return appointment

    @traced(span_name="appointment.get_available_slots")
    async def get_available_slots(
        self,
        clinic_id: UUID,
        provider_id: UUID,
        target_date: date,
        duration_minutes: int = 30,
    ) -> list[dict]:
        """Get available time slots for a provider on a given date.

        Subtracts booked appointments from provider's availability schedule.
        """
        # Get provider's availability
        result = await self.db.execute(
            select(Provider).where(
                and_(
                    Provider.id == provider_id,
                    Provider.clinic_id == clinic_id,
                    Provider.deleted_at.is_(None),
                )
            )
        )
        provider = result.scalar_one_or_none()
        if not provider or not provider.availability:
            return []

        # Get day of week (monday=0)
        day_name = target_date.strftime("%A").lower()
        day_schedule = provider.availability.get(day_name)
        if not day_schedule:
            return []

        # Parse schedule into time ranges
        work_start = datetime.combine(
            target_date,
            datetime.strptime(day_schedule.get("start", "09:00"), "%H:%M").time(),
        )
        work_end = datetime.combine(
            target_date,
            datetime.strptime(day_schedule.get("end", "17:00"), "%H:%M").time(),
        )

        # Get existing appointments for this provider on this date
        day_start = datetime.combine(target_date, datetime.min.time())
        day_end = datetime.combine(target_date, datetime.max.time())

        appt_result = await self.db.execute(
            select(Appointment.start_time, Appointment.end_time)
            .where(
                and_(
                    Appointment.provider_id == provider_id,
                    Appointment.clinic_id == clinic_id,
                    Appointment.start_time >= day_start,
                    Appointment.start_time <= day_end,
                    Appointment.deleted_at.is_(None),
                    Appointment.status.notin_(
                        [AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]
                    ),
                )
            )
            .order_by(Appointment.start_time)
        )
        booked = appt_result.all()

        # Generate available slots
        slots = []
        current = work_start
        slot_duration = timedelta(minutes=duration_minutes)

        while current + slot_duration <= work_end:
            slot_end = current + slot_duration
            # Check if this slot overlaps with any booked appointment
            is_available = True
            for booked_start, booked_end in booked:
                if current < booked_end and slot_end > booked_start:
                    is_available = False
                    # Jump to end of this booked appointment
                    current = booked_end
                    break

            if is_available:
                slots.append({"start_time": current, "end_time": slot_end})
                current = slot_end

        return slots

    @traced(span_name="appointment.get_today_appointments")
    async def get_today_appointments(self, clinic_id: UUID) -> list[dict]:
        """Get today's appointments for the clinic."""
        today = datetime.now(UTC).date()
        items, _ = await self.list_appointments(
            clinic_id=clinic_id,
            page=1,
            limit=100,
            start_date=today,
            end_date=today,
        )
        return items

    async def _check_provider_overlap(
        self,
        clinic_id: UUID,
        provider_id: UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_id: UUID | None = None,
    ) -> bool:
        """Check if provider has overlapping appointments."""
        query = (
            select(func.count())
            .select_from(Appointment)
            .where(
                and_(
                    Appointment.provider_id == provider_id,
                    Appointment.clinic_id == clinic_id,
                    Appointment.deleted_at.is_(None),
                    Appointment.status.notin_(
                        [AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]
                    ),
                    Appointment.start_time < end_time,
                    Appointment.end_time > start_time,
                )
            )
        )

        if exclude_id:
            query = query.where(Appointment.id != exclude_id)

        result = await self.db.execute(query)
        count = result.scalar_one()
        return count > 0
