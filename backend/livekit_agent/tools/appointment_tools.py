"""
Appointment Management Tools

Tools for booking, canceling, and rescheduling appointments.
Uses async writes via Redis queue for responsiveness.
Includes PIMS-aware variants that use external PIMS adapters with local DB fallback.
"""

import json
import logging
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import redis.asyncio as redis
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.pims.base import IPIMSAdapter
from app.adapters.pims.types import PIMSAppointment, PIMSProvider

logger = logging.getLogger(__name__)


async def check_available_appointments(
    db: AsyncSession,
    clinic_id: str,
    date: str,
    provider_id: str | None = None,
) -> str:
    """
    Check available appointment slots for a given date.

    Args:
        db: Database session
        clinic_id: Clinic ID
        date: Date to check (YYYY-MM-DD format)
        provider_id: Optional specific provider ID

    Returns:
        Voice-friendly string with available slots
    """
    # Import here to avoid circular imports
    from app.models.appointment import Appointment, AppointmentStatus

    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return (
            "I didn't quite catch the date. Could you say it again, like January 15th?"
        )

    # Check if date is too far in the future
    max_booking_date = datetime.now().date() + timedelta(days=90)
    if target_date > max_booking_date:
        return f"I can only book appointments up to 3 months in advance. The latest date I can book is {max_booking_date.strftime('%B %d')}."

    # Check if date is in the past
    if target_date < datetime.now().date():
        return "That date is in the past. Would you like to book for a future date instead?"

    try:
        # Get existing appointments for the date
        # Create start and end of day boundaries for the target date
        from sqlalchemy import Date, cast

        existing = await db.execute(
            select(Appointment.start_time).where(
                and_(
                    Appointment.clinic_id == clinic_id,
                    cast(Appointment.start_time, Date) == target_date,
                    Appointment.status.in_(
                        [
                            AppointmentStatus.SCHEDULED,
                            AppointmentStatus.CONFIRMED,
                        ]
                    ),
                    Appointment.deleted_at.is_(None),
                )
            )
        )
        # Extract time strings from start_time datetimes
        booked_times = {row[0].strftime("%H:%M") for row in existing.all()}

        # Generate available slots (9 AM to 5 PM, 30-minute intervals)
        available_slots = []
        for hour in range(9, 17):
            for minute in [0, 30]:
                slot_time = f"{hour:02d}:{minute:02d}"
                if slot_time not in booked_times:
                    # Format for voice: "9 AM", "9:30 AM", "2 PM", etc.
                    formatted = datetime.strptime(slot_time, "%H:%M").strftime(
                        "%-I:%M %p" if minute else "%-I %p"
                    )
                    available_slots.append(formatted)

        if not available_slots:
            return f"I'm sorry, we don't have any available appointments on {target_date.strftime('%B %d')}. Would you like me to check another day?"

        # Limit to first 5 slots for voice readability
        display_slots = available_slots[:5]
        slots_text = ", ".join(display_slots[:-1]) + f", or {display_slots[-1]}"

        if len(available_slots) > 5:
            return f"On {target_date.strftime('%B %d')}, we have openings at {slots_text}, and more. What time works best for you?"
        else:
            return f"On {target_date.strftime('%B %d')}, we have openings at {slots_text}. What time would you prefer?"

    except Exception as e:
        logger.error(f"Error checking appointments: {e}")
        return "I'm having trouble checking our schedule right now. Would you like me to transfer you to someone who can help?"


async def book_appointment(
    redis_client: redis.Redis,
    clinic_id: str,
    pet_name: str,
    owner_name: str,
    date: str,
    time: str,
    reason: str,
    phone: str,
    owner_email: str | None = None,
) -> str:
    """
    Book a new appointment.

    Uses async write to Redis queue for responsiveness.
    A background worker processes the queue for actual DB writes.

    Args:
        redis_client: Redis client for queuing
        clinic_id: Clinic ID
        pet_name: Name of the pet
        owner_name: Owner's name
        date: Appointment date (YYYY-MM-DD)
        time: Appointment time (HH:MM)
        reason: Reason for visit
        phone: Callback phone number
        owner_email: Owner's email (optional)

    Returns:
        Voice-friendly confirmation or error message
    """
    # Generate confirmation code
    booking_id = str(uuid4())[:8].upper()

    try:
        # Validate date/time
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        datetime.strptime(time, "%H:%M").time()  # Validate time format

        # Format for confirmation
        formatted_date = target_date.strftime("%B %d")
        formatted_time = datetime.strptime(time, "%H:%M").strftime("%-I:%M %p")

        # Queue for async processing
        booking_data = {
            "id": booking_id,
            "clinic_id": clinic_id,
            "pet_name": pet_name,
            "owner_name": owner_name,
            "date": date,
            "time": time,
            "reason": reason,
            "phone": phone,
            "owner_email": owner_email,
            "source": "voice_ai",
            "created_at": datetime.now(UTC).isoformat(),
        }

        await redis_client.rpush("booking_queue", json.dumps(booking_data))  # type: ignore[misc]

        return (
            f"I've scheduled an appointment for {pet_name} on {formatted_date} at {formatted_time}. "
            f"Your confirmation number is {booking_id}. "
            f"We'll send a confirmation to {phone}. Is there anything else I can help you with?"
        )

    except ValueError as e:
        logger.error(f"Date/time parsing error: {e}")
        return "I had trouble with that date or time. Could you repeat it for me?"
    except Exception as e:
        logger.error(f"Booking error: {e}")
        return "I ran into an issue booking that appointment. Would you like me to transfer you to our staff?"


async def cancel_appointment(
    db: AsyncSession,
    clinic_id: str,
    confirmation_code: str | None = None,
    owner_phone: str | None = None,
) -> str:
    """
    Cancel an existing appointment.

    Args:
        db: Database session
        clinic_id: Clinic ID
        confirmation_code: Booking confirmation code
        owner_phone: Owner's phone number for lookup

    Returns:
        Voice-friendly confirmation or error message
    """
    from app.models.appointment import Appointment, AppointmentStatus

    if not confirmation_code and not owner_phone:
        return "I'll need either your confirmation number or the phone number you used when booking. Which would you like to provide?"

    try:
        # Look up appointment
        query = select(Appointment).where(
            and_(
                Appointment.clinic_id == clinic_id,
                Appointment.status.in_(
                    [
                        AppointmentStatus.SCHEDULED,
                        AppointmentStatus.CONFIRMED,
                    ]
                ),
                Appointment.deleted_at.is_(None),
            )
        )

        # Add filter based on what was provided
        if confirmation_code:
            query = query.where(Appointment.id.startswith(confirmation_code.lower()))

        result = await db.execute(query)
        appointment = result.scalar_one_or_none()

        if not appointment:
            return "I couldn't find an appointment with that information. Could you double-check the confirmation number or phone number?"

        # Cancel the appointment
        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancelled_at = datetime.now(UTC)
        appointment.cancellation_reason = "Cancelled via voice AI"
        await db.commit()

        return f"I've cancelled your appointment for {appointment.start_time.strftime('%B %d')}. Would you like to schedule a new appointment?"

    except Exception as e:
        logger.error(f"Cancellation error: {e}")
        return "I'm having trouble cancelling that appointment. Let me transfer you to someone who can help."


async def reschedule_appointment(
    db: AsyncSession,
    redis_client: redis.Redis,
    clinic_id: str,
    confirmation_code: str,
    new_date: str,
    new_time: str,
) -> str:
    """
    Reschedule an existing appointment.

    Args:
        db: Database session
        redis_client: Redis client for queuing
        clinic_id: Clinic ID
        confirmation_code: Original booking confirmation code
        new_date: New date (YYYY-MM-DD)
        new_time: New time (HH:MM)

    Returns:
        Voice-friendly confirmation or error message
    """
    from app.models.appointment import Appointment, AppointmentStatus

    try:
        # Look up existing appointment
        result = await db.execute(
            select(Appointment).where(
                and_(
                    Appointment.clinic_id == clinic_id,
                    Appointment.id.startswith(confirmation_code.lower()),
                    Appointment.status.in_(
                        [
                            AppointmentStatus.SCHEDULED,
                            AppointmentStatus.CONFIRMED,
                        ]
                    ),
                    Appointment.deleted_at.is_(None),
                )
            )
        )
        appointment = result.scalar_one_or_none()

        if not appointment:
            return "I couldn't find an appointment with that confirmation number. Could you double-check it?"

        # Validate new date/time
        target_date = datetime.strptime(new_date, "%Y-%m-%d").date()
        datetime.strptime(new_time, "%H:%M").time()  # Validate time format

        formatted_date = target_date.strftime("%B %d")
        formatted_time = datetime.strptime(new_time, "%H:%M").strftime("%-I:%M %p")

        # Update appointment
        old_date = appointment.start_time.strftime("%B %d")
        # Combine new date and time into start_time
        new_time_obj = datetime.strptime(new_time, "%H:%M").time()
        appointment.start_time = datetime.combine(target_date, new_time_obj).replace(
            tzinfo=UTC
        )
        # Update end_time (assuming same duration)
        if appointment.duration_minutes:
            appointment.end_time = appointment.start_time + timedelta(
                minutes=appointment.duration_minutes
            )
        await db.commit()

        return (
            f"I've rescheduled your appointment from {old_date} to {formatted_date} at {formatted_time}. "
            f"Is there anything else I can help you with?"
        )

    except ValueError:
        return "I had trouble with that date or time. Could you say it again?"
    except Exception as e:
        logger.error(f"Reschedule error: {e}")
        return "I'm having trouble rescheduling. Would you like me to transfer you to our staff?"


# ---------------------------------------------------------------------------
# PIMS-aware functions
# ---------------------------------------------------------------------------


def _compute_slots_from_appointments(
    target_date: date,
    appointments: list[PIMSAppointment],
) -> list[str]:
    """Compute free 30-min slots from 9am-5pm minus booked appointments.

    Returns voice-formatted time strings like "9 AM", "2:30 PM".
    """
    booked_times: set[str] = set()
    for appt in appointments:
        if appt.start_time:
            booked_times.add(appt.start_time.strftime("%H:%M"))

    available: list[str] = []
    for hour in range(9, 17):
        for minute in [0, 30]:
            slot_time = f"{hour:02d}:{minute:02d}"
            if slot_time not in booked_times:
                formatted = datetime.strptime(slot_time, "%H:%M").strftime(
                    "%-I:%M %p" if minute else "%-I %p"
                )
                available.append(formatted)
    return available


async def check_available_appointments_pims(
    adapter: IPIMSAdapter,
    date_str: str,
    cached_providers: list[PIMSProvider] | None = None,
) -> str:
    """Check available appointment slots using PIMS adapter.

    Args:
        adapter: PIMS adapter instance
        date_str: Date to check (YYYY-MM-DD format)
        cached_providers: Pre-cached provider list for slot lookup

    Returns:
        Voice-friendly string with available slots

    Raises:
        PIMSError subclasses on adapter failures (caller handles fallback)
    """
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return (
            "I didn't quite catch the date. Could you say it again, like January 15th?"
        )

    max_booking_date = datetime.now().date() + timedelta(days=90)
    if target_date > max_booking_date:
        return f"I can only book appointments up to 3 months in advance. The latest date I can book is {max_booking_date.strftime('%B %d')}."

    if target_date < datetime.now().date():
        return "That date is in the past. Would you like to book for a future date instead?"

    # If we have cached providers, use get_available_slots per provider
    if cached_providers:
        all_slots: list[str] = []
        seen_times: set[str] = set()
        for provider in cached_providers[:3]:  # Limit to 3 providers for speed
            slots = await adapter.get_available_slots(provider.pims_id, target_date)
            for slot in slots:
                time_key = slot.start_time.strftime("%H:%M")
                if time_key not in seen_times:
                    seen_times.add(time_key)
                    minute = slot.start_time.minute
                    formatted = slot.start_time.strftime(
                        "%-I:%M %p" if minute else "%-I %p"
                    )
                    all_slots.append(formatted)
        available_slots = sorted(
            all_slots,
            key=lambda s: datetime.strptime(s, "%I:%M %p" if ":" in s else "%I %p"),
        )
    else:
        # Fall back to computing gaps from appointments
        appointments = await adapter.get_appointments(
            start_date=target_date,
            end_date=target_date,
        )
        available_slots = _compute_slots_from_appointments(target_date, appointments)

    if not available_slots:
        return f"I'm sorry, we don't have any available appointments on {target_date.strftime('%B %d')}. Would you like me to check another day?"

    display_slots = available_slots[:5]
    slots_text = ", ".join(display_slots[:-1]) + f", or {display_slots[-1]}"

    if len(available_slots) > 5:
        return f"On {target_date.strftime('%B %d')}, we have openings at {slots_text}, and more. What time works best for you?"
    else:
        return f"On {target_date.strftime('%B %d')}, we have openings at {slots_text}. What time would you prefer?"


async def book_appointment_pims(
    adapter: IPIMSAdapter,
    redis_client: redis.Redis,
    clinic_id: str,
    pet_name: str,
    owner_name: str,
    date_str: str,
    time_str: str,
    reason: str,
    phone: str,
) -> str:
    """Book an appointment via PIMS and queue local DB sync.

    Args:
        adapter: PIMS adapter instance
        redis_client: Redis client for local DB sync queue
        clinic_id: Clinic ID
        pet_name: Name of the pet
        owner_name: Owner's name
        date_str: Appointment date (YYYY-MM-DD)
        time_str: Appointment time (HH:MM)
        reason: Reason for visit
        phone: Contact phone number

    Returns:
        Voice-friendly confirmation with PIMS reference number

    Raises:
        PIMSError subclasses on adapter failures (caller handles fallback)
    """
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    target_time = datetime.strptime(time_str, "%H:%M").time()
    start_dt = datetime.combine(target_date, target_time).replace(tzinfo=UTC)
    end_dt = start_dt + timedelta(minutes=30)

    pims_appt = PIMSAppointment(
        pims_id="",  # Will be assigned by PIMS
        start_time=start_dt,
        end_time=end_dt,
        reason=reason,
        notes=f"Pet: {pet_name}, Owner: {owner_name}, Phone: {phone}",
        status="scheduled",
    )

    created = await adapter.create_appointment(pims_appt)

    formatted_date = target_date.strftime("%B %d")
    formatted_time = datetime.strptime(time_str, "%H:%M").strftime("%-I:%M %p")

    # Queue local DB sync
    booking_data = {
        "id": created.pims_id,
        "clinic_id": clinic_id,
        "pet_name": pet_name,
        "owner_name": owner_name,
        "date": date_str,
        "time": time_str,
        "reason": reason,
        "phone": phone,
        "pims_id": created.pims_id,
        "source": "voice_ai_pims",
        "created_at": datetime.now(UTC).isoformat(),
    }
    await redis_client.rpush("booking_queue", json.dumps(booking_data))  # type: ignore[misc]

    return (
        f"I've scheduled an appointment for {pet_name} on {formatted_date} at {formatted_time}. "
        f"Your reference number is {created.pims_id}. "
        f"We'll send a confirmation to {phone}. Is there anything else I can help you with?"
    )


async def cancel_appointment_pims(
    adapter: IPIMSAdapter,
    db: AsyncSession,
    clinic_id: str,
    confirmation_code: str,
) -> str:
    """Cancel an appointment in PIMS and update local DB.

    Args:
        adapter: PIMS adapter instance
        db: Database session for local lookup
        clinic_id: Clinic ID
        confirmation_code: Booking confirmation code

    Returns:
        Voice-friendly confirmation

    Raises:
        PIMSError subclasses on adapter failures (caller handles fallback)
    """
    from app.models.appointment import Appointment, AppointmentStatus

    # Find appointment locally to get pims_id
    result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.clinic_id == clinic_id,
                Appointment.id.startswith(confirmation_code.lower()),
                Appointment.status.in_(
                    [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]
                ),
                Appointment.deleted_at.is_(None),
            )
        )
    )
    appointment = result.scalar_one_or_none()

    if not appointment:
        return "I couldn't find an appointment with that confirmation number. Could you double-check it?"

    pims_id = appointment.pims_id
    if not pims_id:
        return "I couldn't find a PIMS record for that appointment. Let me transfer you to our staff."

    # Cancel in PIMS
    await adapter.cancel_appointment(pims_id, reason="Cancelled via voice AI")

    # Update local DB
    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancelled_at = datetime.now(UTC)
    appointment.cancellation_reason = "Cancelled via voice AI (PIMS)"
    await db.commit()

    return f"I've cancelled your appointment for {appointment.start_time.strftime('%B %d')}. Would you like to schedule a new appointment?"


async def reschedule_appointment_pims(
    adapter: IPIMSAdapter,
    db: AsyncSession,
    redis_client: redis.Redis,
    clinic_id: str,
    confirmation_code: str,
    new_date: str,
    new_time: str,
) -> str:
    """Reschedule an appointment via PIMS and update local DB.

    Args:
        adapter: PIMS adapter instance
        db: Database session for local lookup
        redis_client: Redis client (reserved for future sync)
        clinic_id: Clinic ID
        confirmation_code: Original confirmation code
        new_date: New date (YYYY-MM-DD)
        new_time: New time (HH:MM)

    Returns:
        Voice-friendly confirmation

    Raises:
        PIMSError subclasses on adapter failures (caller handles fallback)
    """
    from app.models.appointment import Appointment, AppointmentStatus

    # Find appointment locally
    result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.clinic_id == clinic_id,
                Appointment.id.startswith(confirmation_code.lower()),
                Appointment.status.in_(
                    [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]
                ),
                Appointment.deleted_at.is_(None),
            )
        )
    )
    appointment = result.scalar_one_or_none()

    if not appointment:
        return "I couldn't find an appointment with that confirmation number. Could you double-check it?"

    pims_id = appointment.pims_id
    if not pims_id:
        return "I couldn't find a PIMS record for that appointment. Let me transfer you to our staff."

    target_date = datetime.strptime(new_date, "%Y-%m-%d").date()
    new_time_obj = datetime.strptime(new_time, "%H:%M").time()
    new_start = datetime.combine(target_date, new_time_obj).replace(tzinfo=UTC)
    new_end = new_start + timedelta(minutes=appointment.duration_minutes or 30)

    updated_appt = PIMSAppointment(
        pims_id=pims_id,
        start_time=new_start,
        end_time=new_end,
        reason=appointment.reason,
        status="scheduled",
    )

    await adapter.update_appointment(pims_id, updated_appt)

    # Update local DB
    old_date = appointment.start_time.strftime("%B %d")
    appointment.start_time = new_start
    appointment.end_time = new_end
    await db.commit()

    formatted_date = target_date.strftime("%B %d")
    formatted_time = datetime.strptime(new_time, "%H:%M").strftime("%-I:%M %p")

    return (
        f"I've rescheduled your appointment from {old_date} to {formatted_date} at {formatted_time}. "
        f"Is there anything else I can help you with?"
    )
