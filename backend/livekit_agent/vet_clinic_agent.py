"""
Veterinary Clinic Voice Agent

The main agent class that handles voice interactions with callers.
"""

import logging
from datetime import UTC, datetime

from livekit.agents import Agent, RunContext, function_tool
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.pims.base import IPIMSAdapter
from app.adapters.pims.errors import PIMSError
from app.adapters.pims.types import PIMSProvider
from livekit_agent.cache import get_redis, save_call_state
from livekit_agent.db import SessionLocal
from livekit_agent.prompts import FALLBACK_RESPONSES, get_system_prompt
from livekit_agent.telemetry import LatencyTimer, record_error, record_tool_execution_ms
from livekit_agent.tools.appointment_tools import (
    book_appointment,
    book_appointment_pims,
    cancel_appointment,
    cancel_appointment_pims,
    check_available_appointments,
    check_available_appointments_pims,
    reschedule_appointment,
    reschedule_appointment_pims,
)
from livekit_agent.tools.clinic_tools import (
    get_clinic_hours,
    get_clinic_location,
    get_clinic_services,
)
from livekit_agent.tools.patient_tools import search_patient_local, search_patient_pims
from livekit_agent.tools.transfer_tools import (
    check_emergency_keywords,
    take_message,
    transfer_call,
)

logger = logging.getLogger(__name__)


class VetClinicAgent(Agent):
    """
    Voice AI agent for veterinary clinic phone interactions.

    Handles:
    - Appointment booking, cancellation, and rescheduling
    - Providing clinic information
    - Taking messages for staff
    - Emergency transfers
    - Patient record lookups (when PIMS is connected)
    """

    def __init__(
        self,
        clinic: dict,
        channel: str = "phone",
        room_name: str | None = None,
        pims_adapter: IPIMSAdapter | None = None,
    ) -> None:
        """
        Initialize the agent with clinic context.

        Args:
            clinic: Clinic data dictionary
            channel: Call channel ("phone" or "web_voice")
            room_name: LiveKit room name
            pims_adapter: Optional PIMS adapter for external system integration
        """
        self.clinic = clinic
        self.clinic_id = clinic["id"]
        self.channel = channel
        self.room_name = room_name
        self.pims_adapter = pims_adapter

        # Cached data (populated in warm_cache)
        self.cached_hours: dict | None = None
        self.cached_providers: list | None = None
        self.cached_pims_providers: list[PIMSProvider] | None = None
        self.cached_appointment_types: list | None = None

        # Emergency keywords
        self.emergency_keywords = clinic.get(
            "emergency_keywords",
            [
                "emergency",
                "dying",
                "bleeding",
                "not breathing",
                "seizure",
                "poisoned",
                "hit by car",
                "choking",
            ],
        )

        # Session state
        self.call_start_time = datetime.now(UTC)
        self.actions_taken: list[dict] = []

        # Generate system prompt
        self.system_prompt = get_system_prompt(
            clinic_name=clinic["name"],
            business_hours=self._format_hours(clinic.get("business_hours")),
            address=clinic.get("address"),
            emergency_phone=clinic.get("emergency_phone"),
            emergency_keywords=self.emergency_keywords,
            custom_instructions=clinic.get("voice_settings", {}).get(
                "custom_instructions"
            ),
            pims_enabled=bool(self.pims_adapter),
        )

        super().__init__(
            instructions=self.system_prompt,
        )

    def _format_hours(self, hours: dict | None) -> str:
        """Format business hours for the prompt."""
        if not hours:
            return "Please ask staff for hours"

        parts = []
        for day in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]:
            if day in hours:
                parts.append(f"{day.capitalize()}: {hours[day]}")
        return ", ".join(parts)

    async def warm_cache(self, db: AsyncSession) -> None:
        """
        Pre-cache clinic data at session start for low-latency responses.

        Args:
            db: Database session
        """
        from app.models.provider import Provider

        try:
            # Cache business hours
            self.cached_hours = self.clinic.get("business_hours", {})

            # Cache providers from local DB
            from sqlalchemy import select

            result = await db.execute(
                select(Provider).where(
                    Provider.clinic_id == self.clinic_id,
                    Provider.is_active.is_(True),
                    Provider.deleted_at.is_(None),
                )
            )
            self.cached_providers = [
                {"id": str(p.id), "name": p.full_name, "specialties": p.specialties}
                for p in result.scalars().all()
            ]

            # Also fetch PIMS providers if adapter available
            if self.pims_adapter:
                try:
                    self.cached_pims_providers = await self.pims_adapter.get_providers()
                    logger.info(
                        f"Cached {len(self.cached_pims_providers)} PIMS providers"
                    )
                except PIMSError as e:
                    logger.warning(f"Failed to fetch PIMS providers: {e}")
                    self.cached_pims_providers = None

            logger.info(f"Warmed cache for clinic {self.clinic_id}")
        except Exception as e:
            logger.error(f"Cache warm error: {e}")

    async def on_state_change(self, state: dict) -> None:
        """
        Persist call state to Redis for recovery.

        Called periodically to save conversation context.
        """
        if self.room_name:
            await save_call_state(
                self.room_name,
                {
                    "clinic_id": self.clinic_id,
                    "channel": self.channel,
                    "actions_taken": self.actions_taken,
                    "conversation_context": state,
                },
            )

    async def on_error(self, error: Exception, source: str) -> str:
        """
        Handle errors gracefully with appropriate fallback responses.

        Args:
            error: The exception that occurred
            source: Where the error originated (stt, llm, tool, etc.)

        Returns:
            Fallback response to speak to the caller
        """
        logger.error(f"Agent error from {source}: {error}")
        record_error(type(error).__name__, source)

        if source == "stt":
            return FALLBACK_RESPONSES["stt_failure"]
        elif source == "llm":
            return FALLBACK_RESPONSES["llm_timeout"]
        elif source == "tool":
            return FALLBACK_RESPONSES["tool_error"]
        else:
            return FALLBACK_RESPONSES["general_error"]

    def _record_action(self, action: str, details: dict) -> None:
        """Record an action taken during the call."""
        self.actions_taken.append(
            {
                "action": action,
                "details": details,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

    # -------------------------------------------------------------------------
    # Function Tools - Available to the LLM
    # -------------------------------------------------------------------------

    @function_tool()
    async def get_clinic_hours_tool(self, ctx: RunContext) -> str:
        """Get the clinic's business hours."""
        timer = LatencyTimer()
        timer.start()
        try:
            result = get_clinic_hours(self.cached_hours)
            self._record_action("get_hours", {})
            return result
        finally:
            record_tool_execution_ms("get_clinic_hours", timer.stop(), True)

    @function_tool()
    async def get_clinic_location_tool(self, ctx: RunContext) -> str:
        """Get the clinic's address and location information."""
        timer = LatencyTimer()
        timer.start()
        try:
            result = get_clinic_location(self.clinic)
            self._record_action("get_location", {})
            return result
        finally:
            record_tool_execution_ms("get_clinic_location", timer.stop(), True)

    @function_tool()
    async def get_clinic_services_tool(self, ctx: RunContext) -> str:
        """Get the list of services offered by the clinic."""
        timer = LatencyTimer()
        timer.start()
        try:
            result = get_clinic_services(self.clinic)
            self._record_action("get_services", {})
            return result
        finally:
            record_tool_execution_ms("get_clinic_services", timer.stop(), True)

    @function_tool()
    async def check_appointments_tool(
        self,
        ctx: RunContext,
        date: str,
    ) -> str:
        """
        Check available appointment slots for a specific date.

        Args:
            date: The date to check in YYYY-MM-DD format
        """
        timer = LatencyTimer()
        timer.start()
        try:
            if self.pims_adapter:
                try:
                    result = await check_available_appointments_pims(
                        adapter=self.pims_adapter,
                        date_str=date,
                        cached_providers=self.cached_pims_providers,
                    )
                    self._record_action(
                        "check_appointments", {"date": date, "source": "pims"}
                    )
                    return result
                except PIMSError as e:
                    logger.warning(
                        f"PIMS check_appointments failed, falling back to local DB: {e}"
                    )

            # Fallback to local DB
            async with SessionLocal() as db:
                result = await check_available_appointments(
                    db=db,
                    clinic_id=self.clinic_id,
                    date=date,
                )
            self._record_action("check_appointments", {"date": date, "source": "local"})
            return result
        except Exception as e:
            logger.error(f"Check appointments error: {e}")
            record_tool_execution_ms("check_appointments", timer.stop(), False)
            return "I'm having trouble checking our schedule. Would you like me to transfer you?"
        finally:
            record_tool_execution_ms("check_appointments", timer.stop(), True)

    @function_tool()
    async def book_appointment_tool(
        self,
        ctx: RunContext,
        pet_name: str,
        owner_name: str,
        date: str,
        time: str,
        reason: str,
        phone: str,
    ) -> str:
        """
        Book a new appointment at the clinic.

        Args:
            pet_name: Name of the pet
            owner_name: Name of the pet owner
            date: Appointment date in YYYY-MM-DD format
            time: Appointment time in HH:MM format (24-hour)
            reason: Reason for the visit
            phone: Contact phone number
        """
        timer = LatencyTimer()
        timer.start()
        try:
            redis_client = await get_redis()

            if self.pims_adapter:
                try:
                    result = await book_appointment_pims(
                        adapter=self.pims_adapter,
                        redis_client=redis_client,
                        clinic_id=self.clinic_id,
                        pet_name=pet_name,
                        owner_name=owner_name,
                        date_str=date,
                        time_str=time,
                        reason=reason,
                        phone=phone,
                    )
                    self._record_action(
                        "book_appointment",
                        {
                            "pet_name": pet_name,
                            "owner_name": owner_name,
                            "date": date,
                            "time": time,
                            "reason": reason,
                            "source": "pims",
                        },
                    )
                    return result
                except PIMSError as e:
                    logger.warning(
                        f"PIMS book_appointment failed, falling back to local: {e}"
                    )

            # Fallback to local Redis queue
            result = await book_appointment(
                redis_client=redis_client,
                clinic_id=self.clinic_id,
                pet_name=pet_name,
                owner_name=owner_name,
                date=date,
                time=time,
                reason=reason,
                phone=phone,
            )
            self._record_action(
                "book_appointment",
                {
                    "pet_name": pet_name,
                    "owner_name": owner_name,
                    "date": date,
                    "time": time,
                    "reason": reason,
                    "source": "local",
                },
            )
            return result
        except Exception as e:
            logger.error(f"Book appointment error: {e}")
            record_tool_execution_ms("book_appointment", timer.stop(), False)
            return "I ran into an issue booking that appointment. Would you like me to transfer you?"
        finally:
            record_tool_execution_ms("book_appointment", timer.stop(), True)

    @function_tool()
    async def cancel_appointment_tool(
        self,
        ctx: RunContext,
        confirmation_code: str,
    ) -> str:
        """
        Cancel an existing appointment.

        Args:
            confirmation_code: The appointment confirmation code
        """
        timer = LatencyTimer()
        timer.start()
        try:
            if self.pims_adapter:
                try:
                    async with SessionLocal() as db:
                        result = await cancel_appointment_pims(
                            adapter=self.pims_adapter,
                            db=db,
                            clinic_id=self.clinic_id,
                            confirmation_code=confirmation_code,
                        )
                    self._record_action(
                        "cancel_appointment",
                        {
                            "confirmation_code": confirmation_code,
                            "source": "pims",
                        },
                    )
                    return result
                except PIMSError as e:
                    logger.warning(f"PIMS cancel failed, falling back to local DB: {e}")

            # Fallback to local DB
            async with SessionLocal() as db:
                result = await cancel_appointment(
                    db=db,
                    clinic_id=self.clinic_id,
                    confirmation_code=confirmation_code,
                )
            self._record_action(
                "cancel_appointment",
                {
                    "confirmation_code": confirmation_code,
                    "source": "local",
                },
            )
            return result
        except Exception as e:
            logger.error(f"Cancel appointment error: {e}")
            record_tool_execution_ms("cancel_appointment", timer.stop(), False)
            return "I'm having trouble with the cancellation. Let me transfer you."
        finally:
            record_tool_execution_ms("cancel_appointment", timer.stop(), True)

    @function_tool()
    async def reschedule_appointment_tool(
        self,
        ctx: RunContext,
        confirmation_code: str,
        new_date: str,
        new_time: str,
    ) -> str:
        """
        Reschedule an existing appointment to a new date and time.

        Args:
            confirmation_code: The appointment confirmation code
            new_date: New date in YYYY-MM-DD format
            new_time: New time in HH:MM format (24-hour)
        """
        timer = LatencyTimer()
        timer.start()
        try:
            redis_client = await get_redis()

            if self.pims_adapter:
                try:
                    async with SessionLocal() as db:
                        result = await reschedule_appointment_pims(
                            adapter=self.pims_adapter,
                            db=db,
                            redis_client=redis_client,
                            clinic_id=self.clinic_id,
                            confirmation_code=confirmation_code,
                            new_date=new_date,
                            new_time=new_time,
                        )
                    self._record_action(
                        "reschedule_appointment",
                        {
                            "confirmation_code": confirmation_code,
                            "new_date": new_date,
                            "new_time": new_time,
                            "source": "pims",
                        },
                    )
                    return result
                except PIMSError as e:
                    logger.warning(
                        f"PIMS reschedule failed, falling back to local DB: {e}"
                    )

            # Fallback to local DB
            async with SessionLocal() as db:
                result = await reschedule_appointment(
                    db=db,
                    redis_client=redis_client,
                    clinic_id=self.clinic_id,
                    confirmation_code=confirmation_code,
                    new_date=new_date,
                    new_time=new_time,
                )
            self._record_action(
                "reschedule_appointment",
                {
                    "confirmation_code": confirmation_code,
                    "new_date": new_date,
                    "new_time": new_time,
                    "source": "local",
                },
            )
            return result
        except Exception as e:
            logger.error(f"Reschedule error: {e}")
            record_tool_execution_ms("reschedule_appointment", timer.stop(), False)
            return "I'm having trouble rescheduling. Would you like me to transfer you?"
        finally:
            record_tool_execution_ms("reschedule_appointment", timer.stop(), True)

    @function_tool()
    async def search_patient_tool(
        self,
        ctx: RunContext,
        query: str,
    ) -> str:
        """
        Search for a patient by pet name, owner name, or phone number.

        Args:
            query: Search term - pet name, owner name, or phone number
        """
        timer = LatencyTimer()
        timer.start()
        try:
            if self.pims_adapter:
                try:
                    result = await search_patient_pims(
                        adapter=self.pims_adapter,
                        query=query,
                    )
                    self._record_action(
                        "search_patient", {"query": query, "source": "pims"}
                    )
                    return result
                except PIMSError as e:
                    logger.warning(
                        f"PIMS patient search failed, falling back to local DB: {e}"
                    )

            # Fallback to local DB
            async with SessionLocal() as db:
                result = await search_patient_local(
                    db=db,
                    clinic_id=self.clinic_id,
                    query=query,
                )
            self._record_action("search_patient", {"query": query, "source": "local"})
            return result
        except Exception as e:
            logger.error(f"Patient search error: {e}")
            record_tool_execution_ms("search_patient", timer.stop(), False)
            return "I'm having trouble looking up patient records. Would you like me to transfer you?"
        finally:
            record_tool_execution_ms("search_patient", timer.stop(), True)

    @function_tool()
    async def get_providers_tool(self, ctx: RunContext) -> str:
        """Get the list of available veterinarians at the clinic."""
        timer = LatencyTimer()
        timer.start()
        try:
            # Prefer PIMS providers if available
            if self.cached_pims_providers:
                names = [
                    f"Dr. {p.first_name} {p.last_name}"
                    + (f" ({', '.join(p.specialties)})" if p.specialties else "")
                    for p in self.cached_pims_providers
                    if p.is_active
                ]
            elif self.cached_providers:
                names = [
                    p["name"]
                    + (
                        f" ({', '.join(p['specialties'])})"
                        if p.get("specialties")
                        else ""
                    )
                    for p in self.cached_providers
                ]
            else:
                self._record_action("get_providers", {})
                return "I don't have the provider list available right now. Would you like me to transfer you to find out?"

            self._record_action("get_providers", {"count": len(names)})
            if len(names) == 1:
                return f"We have {names[0]} available."
            listing = ", ".join(names[:-1]) + f", and {names[-1]}"
            return f"Our veterinarians include {listing}."
        finally:
            record_tool_execution_ms("get_providers", timer.stop(), True)

    @function_tool()
    async def transfer_to_staff_tool(
        self,
        ctx: RunContext,
        reason: str,
    ) -> str:
        """
        Transfer the call to a staff member.

        Use this when:
        - The caller requests to speak with a human
        - The situation is too complex for AI to handle
        - There's an emergency

        Args:
            reason: Why the call is being transferred
        """
        timer = LatencyTimer()
        timer.start()
        try:
            redis_client = await get_redis()
            result = await transfer_call(
                redis_client=redis_client,
                room_name=self.room_name or "unknown",
                clinic_id=self.clinic_id,
                reason=reason,
            )
            self._record_action("transfer_call", {"reason": reason})
            return result
        except Exception as e:
            logger.error(f"Transfer error: {e}")
            record_tool_execution_ms("transfer_call", timer.stop(), False)
            return "I'm connecting you now, please hold."
        finally:
            record_tool_execution_ms("transfer_call", timer.stop(), True)

    @function_tool()
    async def take_message_tool(
        self,
        ctx: RunContext,
        caller_name: str,
        message: str,
        callback_number: str,
        is_urgent: bool = False,
    ) -> str:
        """
        Take a message for the clinic staff.

        Args:
            caller_name: Name of the caller
            message: The message content
            callback_number: Phone number to call back
            is_urgent: Whether this is an urgent message
        """
        timer = LatencyTimer()
        timer.start()
        try:
            redis_client = await get_redis()
            result = await take_message(
                redis_client=redis_client,
                clinic_id=self.clinic_id,
                caller_name=caller_name,
                message=message,
                callback_number=callback_number,
                urgency="urgent" if is_urgent else "normal",
            )
            self._record_action(
                "take_message",
                {
                    "caller_name": caller_name,
                    "urgent": is_urgent,
                },
            )
            return result
        except Exception as e:
            logger.error(f"Take message error: {e}")
            record_tool_execution_ms("take_message", timer.stop(), False)
            return "I had trouble saving your message. Could you repeat that?"
        finally:
            record_tool_execution_ms("take_message", timer.stop(), True)

    async def check_for_emergency(self, text: str) -> bool:
        """
        Check if the caller's message indicates an emergency.

        Args:
            text: The caller's message

        Returns:
            True if emergency keywords detected
        """
        return check_emergency_keywords(text, self.emergency_keywords)
