"""Celery tasks for background processing.

Tasks:
- analyze_chat_conversation: LLM analysis of completed chat conversations
- cleanup_stale_sessions: Periodic cleanup of abandoned chat sessions
"""

import asyncio
from datetime import UTC, datetime, timedelta

from loguru import logger

from app.workers.celery_app import app


@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def analyze_chat_conversation(self, conversation_id: str) -> dict:
    """Analyze a completed chat conversation using LLM.

    Creates a ChatAnalysis record with sentiment, topics, resolution,
    and extracted entities from the conversation transcript.

    Args:
        conversation_id: UUID string of the conversation to analyze.

    Returns:
        Dict with analysis status and key results.
    """
    return asyncio.run(_analyze_chat_conversation(self, conversation_id))


async def _analyze_chat_conversation(task, conversation_id: str) -> dict:
    """Async implementation of chat analysis."""
    from uuid import UUID

    from sqlalchemy import select

    from app.db import get_db_session
    from app.models.chat_analysis import ChatAnalysis
    from app.models.conversation import Conversation
    from app.models.message import Message

    logger.info(f"Analyzing conversation {conversation_id}")

    async with get_db_session() as db:
        # Check if analysis already exists and is completed
        existing = await db.execute(
            select(ChatAnalysis).where(
                ChatAnalysis.conversation_id == UUID(conversation_id)
            )
        )
        existing_analysis = existing.scalar_one_or_none()
        if existing_analysis and existing_analysis.status == "completed":
            logger.info(f"Analysis already completed for {conversation_id}")
            return {"status": "already_completed"}

        # Fetch conversation
        conv_result = await db.execute(
            select(Conversation).where(Conversation.id == UUID(conversation_id))
        )
        conversation = conv_result.scalar_one_or_none()
        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found")
            return {"status": "not_found"}

        # Fetch messages
        msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == UUID(conversation_id))
            .order_by(Message.created_at.asc())
        )
        messages = msg_result.scalars().all()

        if not messages:
            logger.info(f"No messages in conversation {conversation_id}")
            return {"status": "no_messages"}

        # Create or update analysis record
        if existing_analysis:
            analysis = existing_analysis
        else:
            analysis = ChatAnalysis(
                conversation_id=UUID(conversation_id),
                status="processing",
            )
            db.add(analysis)
            await db.flush()

        analysis.status = "processing"
        await db.commit()

    # Format transcript
    transcript_lines = []
    for msg in messages:
        role = "USER" if msg.role == "user" else "ASSISTANT"
        content = msg.content or ""
        transcript_lines.append(f"[{role}]: {content}")
    transcript = "\n".join(transcript_lines)

    # Run LLM analysis
    try:
        from app.ai.agents.analytics_agent import create_analytics_agent

        agent = create_analytics_agent()
        result = await agent.run(transcript)
        analysis_result = result.output

        # Store results
        async with get_db_session() as db:
            analysis_record = await db.execute(
                select(ChatAnalysis).where(
                    ChatAnalysis.conversation_id == UUID(conversation_id)
                )
            )
            analysis = analysis_record.scalar_one()
            analysis.status = "completed"
            analysis.analyzed_at = datetime.now(UTC)
            analysis.analysis_model = "deepseek-v3"
            analysis.sentiment = analysis_result.sentiment
            analysis.sentiment_score = analysis_result.sentiment_score
            analysis.resolution_status = analysis_result.resolution_status
            analysis.user_satisfaction = analysis_result.user_satisfaction
            analysis.primary_topic = analysis_result.primary_topic
            analysis.topics = analysis_result.topics
            analysis.entities = analysis_result.entities.model_dump()
            analysis.key_points = analysis_result.key_points
            analysis.suggested_followup = analysis_result.suggested_followup

            # Try to get token usage
            try:
                usage = result.usage()
                analysis.analysis_tokens = (
                    usage.total_tokens if hasattr(usage, "total_tokens") else None
                )
            except (AttributeError, TypeError):
                pass

            await db.commit()

        logger.success(
            f"Analysis completed for {conversation_id}: "
            f"sentiment={analysis_result.sentiment}, "
            f"topic={analysis_result.primary_topic}"
        )
        return {
            "status": "completed",
            "sentiment": analysis_result.sentiment,
            "primary_topic": analysis_result.primary_topic,
        }

    except Exception as exc:
        logger.error(f"Analysis failed for {conversation_id}: {exc}")

        # Mark as failed
        try:
            async with get_db_session() as db:
                analysis_record = await db.execute(
                    select(ChatAnalysis).where(
                        ChatAnalysis.conversation_id == UUID(conversation_id)
                    )
                )
                analysis = analysis_record.scalar_one_or_none()
                if analysis:
                    analysis.status = "failed"
                    analysis.error_message = str(exc)[:500]
                    await db.commit()
        except Exception as db_err:
            logger.error(f"Failed to update analysis status: {db_err}")

        # Retry
        raise task.retry(exc=exc) from exc


@app.task(bind=True)
def cleanup_stale_sessions(self) -> dict:
    """Clean up stale chat sessions and trigger analysis.

    Finds conversations that are still marked active but haven't
    been updated in 30+ minutes, ends them, and enqueues analysis.
    """
    return asyncio.run(_cleanup_stale_sessions())


async def _cleanup_stale_sessions() -> dict:
    """Async implementation of stale session cleanup."""
    from sqlalchemy import and_, select

    from app.db import get_db_session
    from app.models.conversation import Conversation

    stale_cutoff = datetime.now(UTC) - timedelta(minutes=30)
    cleaned = 0

    async with get_db_session() as db:
        result = await db.execute(
            select(Conversation).where(
                and_(
                    Conversation.session_active.is_(True),
                    Conversation.channel == "chat",
                    Conversation.updated_at < stale_cutoff,
                )
            )
        )
        stale_conversations = result.scalars().all()

        for conv in stale_conversations:
            conv.session_active = False
            conv.session_ended_at = datetime.now(UTC)
            cleaned += 1

            # Enqueue analysis
            analyze_chat_conversation.delay(str(conv.id))

        await db.commit()

    # Clean up Redis sessions
    if stale_conversations:
        try:
            from redis.asyncio import Redis as AsyncRedis

            from app.core.config import get_settings

            redis_url = get_settings().redis_url
            if redis_url:
                redis = AsyncRedis.from_url(redis_url, decode_responses=True)
                for conv in stale_conversations:
                    key = f"conversation:session:{conv.id}"
                    await redis.delete(key)
                await redis.aclose()
        except Exception as e:
            logger.warning(f"Failed to clean Redis sessions: {e}")

    logger.info(f"Cleaned up {cleaned} stale sessions")
    return {"cleaned": cleaned}


# =============================================================================
# PIMS Sync Tasks
# =============================================================================


@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=120,
    acks_late=True,
)
def sync_patients_from_pims(self, clinic_id: str) -> dict:
    """Sync patients from PIMS to local database."""
    return asyncio.run(_sync_patients_from_pims(self, clinic_id))


async def _sync_patients_from_pims(task, clinic_id: str) -> dict:
    """Async implementation of patient sync."""
    from uuid import UUID

    from sqlalchemy import and_, select

    from app.adapters.pims.conflict import ConflictStrategy, resolve_patient_conflict
    from app.adapters.pims.errors import PIMSError
    from app.adapters.pims.factory import get_pims_adapter
    from app.db import get_db_session
    from app.models.clinic import Clinic
    from app.models.patient import Patient
    from app.models.pims_sync_log import PIMSSyncLog, SyncEntityType, SyncType

    logger.info(f"Starting patient sync for clinic {clinic_id}")

    async with get_db_session() as db:
        # Load clinic
        result = await db.execute(select(Clinic).where(Clinic.id == UUID(clinic_id)))
        clinic = result.scalar_one_or_none()
        if not clinic:
            return {"status": "error", "message": "Clinic not found"}

        # Create sync log
        sync_log = PIMSSyncLog(
            clinic_id=UUID(clinic_id),
            sync_type=SyncType.PULL,
            entity_type=SyncEntityType.PATIENTS,
            triggered_by="scheduler",
        )
        sync_log.start()
        db.add(sync_log)
        await db.flush()

        try:
            adapter = get_pims_adapter(clinic)
            await adapter.authenticate()

            offset = 0
            limit = 100
            created = 0
            updated = 0
            processed = 0

            while True:
                patients = await adapter.get_patients(
                    since=clinic.pims_last_sync_at, limit=limit, offset=offset
                )
                if not patients:
                    break

                for pims_patient in patients:
                    processed += 1
                    # Check if patient exists locally
                    existing = await db.execute(
                        select(Patient).where(
                            and_(
                                Patient.clinic_id == UUID(clinic_id),
                                Patient.pims_id == pims_patient.pims_id,
                                Patient.deleted_at.is_(None),
                            )
                        )
                    )
                    local_patient = existing.scalar_one_or_none()

                    if local_patient:
                        # Update existing
                        pims_data = {
                            "name": pims_patient.name,
                            "species": pims_patient.species,
                            "breed": pims_patient.breed,
                            "owner_first_name": pims_patient.owner_first_name,
                            "owner_last_name": pims_patient.owner_last_name,
                            "owner_phone": pims_patient.owner_phone,
                            "owner_email": pims_patient.owner_email,
                        }
                        updates = resolve_patient_conflict(
                            local_patient.to_dict(),
                            pims_data,
                            ConflictStrategy.PIMS_WINS,
                        )
                        for field, value in updates.items():
                            if hasattr(local_patient, field):
                                setattr(local_patient, field, value)
                        local_patient.mark_synced(pims_patient.pims_id)
                        updated += 1
                    else:
                        # Create new
                        new_patient = Patient(
                            clinic_id=UUID(clinic_id),
                            name=pims_patient.name,
                            species=pims_patient.species or "other",
                            breed=pims_patient.breed,
                            color=pims_patient.color,
                            sex=pims_patient.sex or "unknown",
                            date_of_birth=pims_patient.date_of_birth,
                            weight_kg=pims_patient.weight_kg,
                            microchip_id=pims_patient.microchip_id,
                            is_deceased=pims_patient.is_deceased,
                            owner_first_name=pims_patient.owner_first_name or "Unknown",
                            owner_last_name=pims_patient.owner_last_name or "Unknown",
                            owner_phone=pims_patient.owner_phone or "",
                            owner_email=pims_patient.owner_email,
                            owner_address=pims_patient.owner_address,
                            allergies=pims_patient.allergies,
                            medical_notes=pims_patient.medical_notes,
                            pims_metadata=pims_patient.raw_data,
                        )
                        new_patient.mark_synced(pims_patient.pims_id)
                        db.add(new_patient)
                        created += 1

                offset += limit
                if len(patients) < limit:
                    break

            await adapter.close()

            # Update sync log
            sync_log.records_processed = processed
            sync_log.records_created = created
            sync_log.records_updated = updated
            sync_log.complete()

            # Update clinic last sync
            clinic.pims_last_sync_at = datetime.now(UTC)
            await db.commit()

            logger.success(
                f"Patient sync complete for {clinic_id}: "
                f"{created} created, {updated} updated, {processed} processed"
            )
            return {
                "status": "completed",
                "created": created,
                "updated": updated,
                "processed": processed,
            }

        except PIMSError as exc:
            sync_log.fail(str(exc))
            await db.commit()
            logger.error(f"Patient sync failed for {clinic_id}: {exc}")
            raise task.retry(exc=exc) from exc

        except Exception as exc:
            sync_log.fail(str(exc))
            await db.commit()
            logger.error(f"Patient sync failed for {clinic_id}: {exc}")
            raise task.retry(exc=exc) from exc


@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def sync_appointments_from_pims(self, clinic_id: str, days_ahead: int = 14) -> dict:
    """Sync appointments from PIMS for the next N days."""
    return asyncio.run(_sync_appointments_from_pims(self, clinic_id, days_ahead))


async def _sync_appointments_from_pims(task, clinic_id: str, days_ahead: int) -> dict:
    """Async implementation of appointment sync."""
    from uuid import UUID

    from sqlalchemy import and_, select

    from app.adapters.pims.errors import PIMSError
    from app.adapters.pims.factory import get_pims_adapter
    from app.db import get_db_session
    from app.models.appointment import Appointment
    from app.models.clinic import Clinic
    from app.models.patient import Patient
    from app.models.pims_sync_log import PIMSSyncLog, SyncEntityType, SyncType
    from app.models.provider import Provider

    logger.info(f"Starting appointment sync for clinic {clinic_id}")

    async with get_db_session() as db:
        result = await db.execute(select(Clinic).where(Clinic.id == UUID(clinic_id)))
        clinic = result.scalar_one_or_none()
        if not clinic:
            return {"status": "error", "message": "Clinic not found"}

        sync_log = PIMSSyncLog(
            clinic_id=UUID(clinic_id),
            sync_type=SyncType.PULL,
            entity_type=SyncEntityType.APPOINTMENTS,
            triggered_by="scheduler",
        )
        sync_log.start()
        db.add(sync_log)
        await db.flush()

        try:
            adapter = get_pims_adapter(clinic)
            await adapter.authenticate()

            today = datetime.now(UTC).date()
            end_date = today + timedelta(days=days_ahead)

            pims_appointments = await adapter.get_appointments(
                start_date=today, end_date=end_date
            )
            await adapter.close()

            created = 0
            updated = 0

            for pims_appt in pims_appointments:
                # Lookup patient/provider by pims_id
                patient_id = None
                if pims_appt.patient_pims_id:
                    p_result = await db.execute(
                        select(Patient.id).where(
                            and_(
                                Patient.clinic_id == UUID(clinic_id),
                                Patient.pims_id == pims_appt.patient_pims_id,
                            )
                        )
                    )
                    row = p_result.one_or_none()
                    if row:
                        patient_id = row[0]

                provider_id = None
                if pims_appt.provider_pims_id:
                    prov_result = await db.execute(
                        select(Provider.id).where(
                            and_(
                                Provider.clinic_id == UUID(clinic_id),
                                Provider.pims_id == pims_appt.provider_pims_id,
                            )
                        )
                    )
                    row = prov_result.one_or_none()
                    if row:
                        provider_id = row[0]

                # Check if appointment exists
                existing = await db.execute(
                    select(Appointment).where(
                        and_(
                            Appointment.clinic_id == UUID(clinic_id),
                            Appointment.pims_id == pims_appt.pims_id,
                            Appointment.deleted_at.is_(None),
                        )
                    )
                )
                local_appt = existing.scalar_one_or_none()

                if local_appt:
                    if pims_appt.start_time:
                        local_appt.start_time = pims_appt.start_time
                    if pims_appt.end_time:
                        local_appt.end_time = pims_appt.end_time
                    if pims_appt.status:
                        local_appt.status = pims_appt.status
                    local_appt.patient_id = patient_id
                    local_appt.provider_id = provider_id
                    local_appt.mark_synced(pims_appt.pims_id)
                    updated += 1
                else:
                    if not pims_appt.start_time or not pims_appt.end_time:
                        continue

                    duration = int(
                        (pims_appt.end_time - pims_appt.start_time).total_seconds() / 60
                    )
                    new_appt = Appointment(
                        clinic_id=UUID(clinic_id),
                        patient_id=patient_id,
                        provider_id=provider_id,
                        start_time=pims_appt.start_time,
                        end_time=pims_appt.end_time,
                        duration_minutes=duration,
                        appointment_type=pims_appt.appointment_type or "checkup",
                        status=pims_appt.status or "scheduled",
                        source="pims",
                        reason=pims_appt.reason,
                        pims_metadata=pims_appt.raw_data,
                    )
                    new_appt.mark_synced(pims_appt.pims_id)
                    db.add(new_appt)
                    created += 1

            sync_log.records_processed = len(pims_appointments)
            sync_log.records_created = created
            sync_log.records_updated = updated
            sync_log.complete()

            clinic.pims_last_sync_at = datetime.now(UTC)
            await db.commit()

            logger.success(
                f"Appointment sync complete for {clinic_id}: "
                f"{created} created, {updated} updated"
            )
            return {"status": "completed", "created": created, "updated": updated}

        except PIMSError as exc:
            sync_log.fail(str(exc))
            await db.commit()
            raise task.retry(exc=exc) from exc

        except Exception as exc:
            sync_log.fail(str(exc))
            await db.commit()
            raise task.retry(exc=exc) from exc


@app.task(bind=True, max_retries=3, default_retry_delay=30, acks_late=True)
def push_appointment_to_pims(self, appointment_id: str) -> dict:
    """Push a locally created appointment to PIMS."""
    return asyncio.run(_push_appointment_to_pims(self, appointment_id))


async def _push_appointment_to_pims(task, appointment_id: str) -> dict:
    """Async implementation of appointment push."""
    from uuid import UUID

    from sqlalchemy import select

    from app.adapters.pims.errors import PIMSError
    from app.adapters.pims.factory import get_pims_adapter
    from app.adapters.pims.types import PIMSAppointment
    from app.db import get_db_session
    from app.models.appointment import Appointment
    from app.models.clinic import Clinic

    async with get_db_session() as db:
        result = await db.execute(
            select(Appointment).where(Appointment.id == UUID(appointment_id))
        )
        appointment = result.scalar_one_or_none()
        if not appointment:
            return {"status": "error", "message": "Appointment not found"}

        clinic_result = await db.execute(
            select(Clinic).where(Clinic.id == appointment.clinic_id)
        )
        clinic = clinic_result.scalar_one_or_none()
        if not clinic:
            return {"status": "error", "message": "Clinic not found"}

        try:
            adapter = get_pims_adapter(clinic)
            await adapter.authenticate()

            pims_data = PIMSAppointment(
                pims_id="",
                start_time=appointment.start_time,
                end_time=appointment.end_time,
                appointment_type=str(appointment.appointment_type),
                reason=appointment.reason,
            )

            created = await adapter.create_appointment(pims_data)
            await adapter.close()

            appointment.mark_synced(created.pims_id)
            await db.commit()

            logger.success(
                f"Appointment {appointment_id} pushed to PIMS as {created.pims_id}"
            )
            return {"status": "completed", "pims_id": created.pims_id}

        except PIMSError as exc:
            appointment.mark_sync_error()
            await db.commit()
            raise task.retry(exc=exc) from exc

        except Exception as exc:
            appointment.mark_sync_error()
            await db.commit()
            raise task.retry(exc=exc) from exc


@app.task(bind=True, max_retries=3, default_retry_delay=30, acks_late=True)
def sync_providers_from_pims(self, clinic_id: str) -> dict:
    """Sync providers from PIMS."""
    return asyncio.run(_sync_providers_from_pims(self, clinic_id))


async def _sync_providers_from_pims(task, clinic_id: str) -> dict:
    """Async implementation of provider sync."""
    from uuid import UUID

    from sqlalchemy import and_, select

    from app.adapters.pims.errors import PIMSError
    from app.adapters.pims.factory import get_pims_adapter
    from app.db import get_db_session
    from app.models.clinic import Clinic
    from app.models.pims_sync_log import PIMSSyncLog, SyncEntityType, SyncType
    from app.models.provider import Provider

    async with get_db_session() as db:
        result = await db.execute(select(Clinic).where(Clinic.id == UUID(clinic_id)))
        clinic = result.scalar_one_or_none()
        if not clinic:
            return {"status": "error", "message": "Clinic not found"}

        sync_log = PIMSSyncLog(
            clinic_id=UUID(clinic_id),
            sync_type=SyncType.PULL,
            entity_type=SyncEntityType.PROVIDERS,
            triggered_by="scheduler",
        )
        sync_log.start()
        db.add(sync_log)
        await db.flush()

        try:
            adapter = get_pims_adapter(clinic)
            await adapter.authenticate()
            pims_providers = await adapter.get_providers()
            await adapter.close()

            created = 0
            updated = 0

            for pims_prov in pims_providers:
                existing = await db.execute(
                    select(Provider).where(
                        and_(
                            Provider.clinic_id == UUID(clinic_id),
                            Provider.pims_id == pims_prov.pims_id,
                            Provider.deleted_at.is_(None),
                        )
                    )
                )
                local_prov = existing.scalar_one_or_none()

                if local_prov:
                    local_prov.first_name = pims_prov.first_name
                    local_prov.last_name = pims_prov.last_name
                    local_prov.title = pims_prov.title
                    local_prov.email = pims_prov.email
                    local_prov.phone = pims_prov.phone
                    local_prov.is_active = pims_prov.is_active
                    local_prov.mark_synced(pims_prov.pims_id)
                    updated += 1
                else:
                    new_prov = Provider(
                        clinic_id=UUID(clinic_id),
                        first_name=pims_prov.first_name,
                        last_name=pims_prov.last_name,
                        title=pims_prov.title,
                        provider_type=pims_prov.provider_type or "veterinarian",
                        specialties=pims_prov.specialties,
                        email=pims_prov.email,
                        phone=pims_prov.phone,
                        is_active=pims_prov.is_active,
                        pims_metadata=pims_prov.raw_data,
                    )
                    new_prov.mark_synced(pims_prov.pims_id)
                    db.add(new_prov)
                    created += 1

            sync_log.records_processed = len(pims_providers)
            sync_log.records_created = created
            sync_log.records_updated = updated
            sync_log.complete()

            await db.commit()

            return {"status": "completed", "created": created, "updated": updated}

        except PIMSError as exc:
            sync_log.fail(str(exc))
            await db.commit()
            raise task.retry(exc=exc) from exc

        except Exception as exc:
            sync_log.fail(str(exc))
            await db.commit()
            raise task.retry(exc=exc) from exc


@app.task
def sync_all_clinics_patients() -> dict:
    """Enqueue patient sync for all PIMS-connected clinics."""
    return asyncio.run(_sync_all_clinics("patients"))


@app.task
def sync_all_clinics_appointments() -> dict:
    """Enqueue appointment sync for all PIMS-connected clinics."""
    return asyncio.run(_sync_all_clinics("appointments"))


async def _sync_all_clinics(entity: str) -> dict:
    """Enqueue sync tasks for all PIMS-connected clinics."""
    from sqlalchemy import select

    from app.db import get_db_session
    from app.models.clinic import Clinic, PIMSType

    async with get_db_session() as db:
        result = await db.execute(
            select(Clinic.id).where(
                Clinic.pims_type != PIMSType.NONE,
                Clinic.pims_credentials_encrypted.is_not(None),
                Clinic.is_active.is_(True),
                Clinic.deleted_at.is_(None),
            )
        )
        clinic_ids = [str(row[0]) for row in result.all()]

    enqueued = 0
    for cid in clinic_ids:
        if entity == "patients":
            sync_patients_from_pims.delay(cid)
        else:
            sync_appointments_from_pims.delay(cid)
        enqueued += 1

    logger.info(f"Enqueued {entity} sync for {enqueued} clinics")
    return {"enqueued": enqueued, "entity": entity}
