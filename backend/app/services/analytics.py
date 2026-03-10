"""Analytics service for dashboard metrics."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.instrumentation import traced
from app.models.appointment import Appointment, AppointmentSource, AppointmentStatus
from app.models.call_log import CallLog, CallOutcome
from app.models.chat_analysis import ChatAnalysis
from app.models.conversation import Conversation
from app.models.patient import Patient
from app.models.pims_sync_log import PIMSSyncLog, SyncJobStatus
from app.schemas.analytics import (
    AppointmentAnalytics,
    CallAnalytics,
    CallLogSummary,
    ChatLogSummary,
    ChatSentimentData,
    DashboardAnalytics,
    EnhancedChatAnalytics,
    PatientAnalytics,
    PIMSSyncAnalytics,
    PIMSSyncDayTrend,
    SentimentData,
)


class AnalyticsService:
    """Service for calculating dashboard analytics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @traced(span_name="analytics.get_call_analytics")
    async def get_call_analytics(
        self, clinic_id: UUID, days: int = 30
    ) -> CallAnalytics:
        """Aggregate call metrics for the past N days."""
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        today_start = datetime.now(UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # Total calls in period
        total_result = await self.db.execute(
            select(func.count())
            .select_from(CallLog)
            .where(
                and_(
                    CallLog.clinic_id == str(clinic_id),
                    CallLog.started_at >= cutoff_date,
                    CallLog.deleted_at.is_(None),
                )
            )
        )
        total_calls = total_result.scalar_one()

        # Calls today
        today_result = await self.db.execute(
            select(func.count())
            .select_from(CallLog)
            .where(
                and_(
                    CallLog.clinic_id == str(clinic_id),
                    CallLog.started_at >= today_start,
                    CallLog.deleted_at.is_(None),
                )
            )
        )
        calls_today = today_result.scalar_one()

        # Direction breakdown
        direction_result = await self.db.execute(
            select(CallLog.direction, func.count())
            .where(
                and_(
                    CallLog.clinic_id == str(clinic_id),
                    CallLog.started_at >= cutoff_date,
                    CallLog.deleted_at.is_(None),
                )
            )
            .group_by(CallLog.direction)
        )
        direction_counts = {k: v for k, v in direction_result.all()}  # noqa: C416
        inbound_calls = direction_counts.get("inbound", 0)
        outbound_calls = direction_counts.get("outbound", 0)

        # AI handled percentage
        ai_handled_result = await self.db.execute(
            select(func.count())
            .select_from(CallLog)
            .where(
                and_(
                    CallLog.clinic_id == str(clinic_id),
                    CallLog.started_at >= cutoff_date,
                    CallLog.deleted_at.is_(None),
                    CallLog.ai_handled.is_(True),
                    CallLog.outcome
                    != CallOutcome.TRANSFERRED_TO_STAFF,  # Fully handled by AI
                )
            )
        )
        ai_handled_count = ai_handled_result.scalar_one()
        ai_handled_percentage = (
            (ai_handled_count / total_calls * 100) if total_calls > 0 else 0.0
        )

        # Average duration
        avg_duration_result = await self.db.execute(
            select(func.avg(CallLog.duration_seconds))
            .select_from(CallLog)
            .where(
                and_(
                    CallLog.clinic_id == str(clinic_id),
                    CallLog.started_at >= cutoff_date,
                    CallLog.deleted_at.is_(None),
                    CallLog.duration_seconds.is_not(None),
                )
            )
        )
        avg_duration = avg_duration_result.scalar_one() or 0.0

        # Emergency transfers
        emergency_result = await self.db.execute(
            select(func.count())
            .select_from(CallLog)
            .where(
                and_(
                    CallLog.clinic_id == str(clinic_id),
                    CallLog.started_at >= cutoff_date,
                    CallLog.deleted_at.is_(None),
                    CallLog.outcome == CallOutcome.EMERGENCY_TRANSFER,
                )
            )
        )
        emergency_transfers = emergency_result.scalar_one()

        # Appointments booked via calls
        appt_booked_result = await self.db.execute(
            select(func.count())
            .select_from(CallLog)
            .where(
                and_(
                    CallLog.clinic_id == str(clinic_id),
                    CallLog.started_at >= cutoff_date,
                    CallLog.deleted_at.is_(None),
                    CallLog.outcome == CallOutcome.APPOINTMENT_BOOKED,
                )
            )
        )
        appointments_booked = appt_booked_result.scalar_one()

        # Average AI confidence
        avg_confidence_result = await self.db.execute(
            select(func.avg(CallLog.ai_confidence_score))
            .select_from(CallLog)
            .where(
                and_(
                    CallLog.clinic_id == str(clinic_id),
                    CallLog.started_at >= cutoff_date,
                    CallLog.deleted_at.is_(None),
                    CallLog.ai_confidence_score.is_not(None),
                )
            )
        )
        avg_confidence = avg_confidence_result.scalar_one() or 0.0

        # Calls by outcome
        outcome_result = await self.db.execute(
            select(CallLog.outcome, func.count())
            .where(
                and_(
                    CallLog.clinic_id == str(clinic_id),
                    CallLog.started_at >= cutoff_date,
                    CallLog.deleted_at.is_(None),
                    CallLog.outcome.is_not(None),
                )
            )
            .group_by(CallLog.outcome)
        )
        calls_by_outcome = {
            str(outcome): count for outcome, count in outcome_result.all()
        }

        # Calls by hour (last 24 hours)
        last_24h = datetime.now(UTC) - timedelta(hours=24)
        hourly_result = await self.db.execute(
            select(
                func.extract("hour", CallLog.started_at).label("hour"),
                func.count().label("count"),
            )
            .where(
                and_(
                    CallLog.clinic_id == str(clinic_id),
                    CallLog.started_at >= last_24h,
                    CallLog.deleted_at.is_(None),
                )
            )
            .group_by(func.extract("hour", CallLog.started_at))
            .order_by(func.extract("hour", CallLog.started_at))
        )
        hourly_data = [
            {"hour": int(hour), "count": count} for hour, count in hourly_result.all()
        ]

        # Fill in missing hours with 0
        calls_by_hour_dict = {item["hour"]: item["count"] for item in hourly_data}
        calls_by_hour = [
            {"hour": h, "count": calls_by_hour_dict.get(h, 0)} for h in range(24)
        ]

        # Get hours when transfers occurred (last 24 hours)
        transfer_hours_result = await self.db.execute(
            select(func.extract("hour", CallLog.started_at).label("hour"))
            .where(
                and_(
                    CallLog.clinic_id == str(clinic_id),
                    CallLog.started_at >= last_24h,
                    CallLog.deleted_at.is_(None),
                    CallLog.outcome.in_(
                        [
                            CallOutcome.TRANSFERRED_TO_STAFF,
                            CallOutcome.EMERGENCY_TRANSFER,
                        ]
                    ),
                )
            )
            .distinct()
        )
        transfer_hours = [int(row[0]) for row in transfer_hours_result.all()]

        return CallAnalytics(
            total_calls=total_calls,
            calls_today=calls_today,
            inbound_calls=inbound_calls,
            outbound_calls=outbound_calls,
            ai_handled_percentage=round(ai_handled_percentage, 2),
            average_duration_seconds=round(avg_duration, 2),
            emergency_transfers=emergency_transfers,
            appointments_booked=appointments_booked,
            average_confidence_score=round(avg_confidence, 2),
            calls_by_outcome=calls_by_outcome,
            calls_by_hour=calls_by_hour,
            transfer_hours=transfer_hours,
        )

    @traced(span_name="analytics.get_appointment_analytics")
    async def get_appointment_analytics(
        self, clinic_id: UUID, days: int = 30
    ) -> AppointmentAnalytics:
        """Aggregate appointment metrics."""
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        week_start = datetime.now(UTC) - timedelta(days=7)

        # Total appointments in period
        total_result = await self.db.execute(
            select(func.count())
            .select_from(Appointment)
            .where(
                and_(
                    Appointment.clinic_id == str(clinic_id),
                    Appointment.start_time >= cutoff_date,
                    Appointment.deleted_at.is_(None),
                )
            )
        )
        total_appointments = total_result.scalar_one()

        # Appointments this week
        week_result = await self.db.execute(
            select(func.count())
            .select_from(Appointment)
            .where(
                and_(
                    Appointment.clinic_id == str(clinic_id),
                    Appointment.start_time >= week_start,
                    Appointment.deleted_at.is_(None),
                )
            )
        )
        appointments_this_week = week_result.scalar_one()

        # Bookings by source
        source_result = await self.db.execute(
            select(Appointment.source, func.count())
            .where(
                and_(
                    Appointment.clinic_id == str(clinic_id),
                    Appointment.start_time >= cutoff_date,
                    Appointment.deleted_at.is_(None),
                )
            )
            .group_by(Appointment.source)
        )
        source_counts = {k: v for k, v in source_result.all()}  # noqa: C416
        bookings_via_ai = source_counts.get(AppointmentSource.VOICE_AI, 0)
        bookings_via_dashboard = source_counts.get(AppointmentSource.DASHBOARD, 0)

        # No-show rate
        status_result = await self.db.execute(
            select(Appointment.status, func.count())
            .where(
                and_(
                    Appointment.clinic_id == str(clinic_id),
                    Appointment.start_time >= cutoff_date,
                    Appointment.deleted_at.is_(None),
                )
            )
            .group_by(Appointment.status)
        )
        status_counts = {k: v for k, v in status_result.all()}  # noqa: C416
        no_shows = status_counts.get(AppointmentStatus.NO_SHOW, 0)
        cancelled = status_counts.get(AppointmentStatus.CANCELLED, 0)
        no_show_rate = (
            (no_shows / total_appointments * 100) if total_appointments > 0 else 0.0
        )
        cancellation_rate = (
            (cancelled / total_appointments * 100) if total_appointments > 0 else 0.0
        )

        # Appointments by type
        type_result = await self.db.execute(
            select(Appointment.appointment_type, func.count())
            .where(
                and_(
                    Appointment.clinic_id == str(clinic_id),
                    Appointment.start_time >= cutoff_date,
                    Appointment.deleted_at.is_(None),
                )
            )
            .group_by(Appointment.appointment_type)
        )
        appointments_by_type = {
            str(appt_type): count for appt_type, count in type_result.all()
        }

        # Appointments by status
        appointments_by_status = {
            str(status): count for status, count in status_counts.items()
        }

        return AppointmentAnalytics(
            total_appointments=total_appointments,
            appointments_this_week=appointments_this_week,
            bookings_via_ai=bookings_via_ai,
            bookings_via_dashboard=bookings_via_dashboard,
            no_show_rate=round(no_show_rate, 2),
            cancellation_rate=round(cancellation_rate, 2),
            appointments_by_type=appointments_by_type,
            appointments_by_status=appointments_by_status,
        )

    @traced(span_name="analytics.get_patient_analytics")
    async def get_patient_analytics(self, clinic_id: UUID) -> PatientAnalytics:
        """Get patient statistics."""
        month_start = datetime.now(UTC).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        # Total active patients
        active_result = await self.db.execute(
            select(func.count())
            .select_from(Patient)
            .where(
                and_(
                    Patient.clinic_id == str(clinic_id),
                    Patient.is_deceased.is_(False),
                    Patient.deleted_at.is_(None),
                )
            )
        )
        total_active_patients = active_result.scalar_one()

        # New patients this month
        new_result = await self.db.execute(
            select(func.count())
            .select_from(Patient)
            .where(
                and_(
                    Patient.clinic_id == str(clinic_id),
                    Patient.created_at >= month_start,
                    Patient.deleted_at.is_(None),
                )
            )
        )
        new_patients_this_month = new_result.scalar_one()

        # Patients by species
        species_result = await self.db.execute(
            select(Patient.species, func.count())
            .where(
                and_(
                    Patient.clinic_id == str(clinic_id),
                    Patient.is_deceased.is_(False),
                    Patient.deleted_at.is_(None),
                )
            )
            .group_by(Patient.species)
        )
        patients_by_species = {
            str(species): count for species, count in species_result.all()
        }

        # Total distinct owners
        owner_result = await self.db.execute(
            select(func.count(func.distinct(Patient.owner_phone)))
            .select_from(Patient)
            .where(
                and_(
                    Patient.clinic_id == str(clinic_id),
                    Patient.deleted_at.is_(None),
                )
            )
        )
        total_owners = owner_result.scalar_one()

        return PatientAnalytics(
            total_active_patients=total_active_patients,
            new_patients_this_month=new_patients_this_month,
            patients_by_species=patients_by_species,
            total_owners=total_owners,
        )

    @traced(span_name="analytics.get_pims_analytics")
    async def get_pims_analytics(self, clinic_id: UUID) -> PIMSSyncAnalytics:
        """Get PIMS sync health."""
        today_start = datetime.now(UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # Get clinic PIMS status
        from app.models.clinic import Clinic

        clinic_result = await self.db.execute(
            select(
                Clinic.pims_connection_status,
                Clinic.pims_last_sync_at,
            ).where(Clinic.id == str(clinic_id))
        )
        clinic_row = clinic_result.one_or_none()

        if not clinic_row:
            # Clinic not found - return default values
            return PIMSSyncAnalytics(
                connection_status="disconnected",
                last_sync_at=None,
                sync_success_rate=0.0,
                total_syncs_today=0,
                failed_syncs_today=0,
            )

        connection_status = str(clinic_row[0]) if clinic_row[0] else "disconnected"
        last_sync_at = clinic_row[1]

        # Sync statistics today
        total_syncs_result = await self.db.execute(
            select(func.count())
            .select_from(PIMSSyncLog)
            .where(
                and_(
                    PIMSSyncLog.clinic_id == str(clinic_id),
                    PIMSSyncLog.started_at >= today_start,
                    PIMSSyncLog.status.in_(
                        [
                            SyncJobStatus.COMPLETED,
                            SyncJobStatus.PARTIAL,
                            SyncJobStatus.FAILED,
                        ]
                    ),
                )
            )
        )
        total_syncs_today = total_syncs_result.scalar_one()

        # Failed syncs today
        failed_syncs_result = await self.db.execute(
            select(func.count())
            .select_from(PIMSSyncLog)
            .where(
                and_(
                    PIMSSyncLog.clinic_id == str(clinic_id),
                    PIMSSyncLog.started_at >= today_start,
                    PIMSSyncLog.status == SyncJobStatus.FAILED,
                )
            )
        )
        failed_syncs_today = failed_syncs_result.scalar_one()

        # Overall sync success rate (last 30 days)
        cutoff_date = datetime.now(UTC) - timedelta(days=30)
        success_rate_result = await self.db.execute(
            select(
                func.count()
                .filter(PIMSSyncLog.status == SyncJobStatus.COMPLETED)
                .label("successful"),
                func.count().label("total"),
            )
            .select_from(PIMSSyncLog)
            .where(
                and_(
                    PIMSSyncLog.clinic_id == str(clinic_id),
                    PIMSSyncLog.started_at >= cutoff_date,
                    PIMSSyncLog.status.in_(
                        [
                            SyncJobStatus.COMPLETED,
                            SyncJobStatus.PARTIAL,
                            SyncJobStatus.FAILED,
                        ]
                    ),
                )
            )
        )
        success_row = success_rate_result.one()
        successful = success_row[0] or 0
        total = success_row[1] or 0
        sync_success_rate = (successful / total * 100) if total > 0 else 100.0

        # Daily sync trend (last 14 days)
        trend_cutoff = datetime.now(UTC) - timedelta(days=14)
        trend_result = await self.db.execute(
            select(
                func.date(PIMSSyncLog.started_at).label("day"),
                func.count()
                .filter(PIMSSyncLog.status == SyncJobStatus.COMPLETED)
                .label("successful"),
                func.count()
                .filter(PIMSSyncLog.status == SyncJobStatus.FAILED)
                .label("failed"),
            )
            .select_from(PIMSSyncLog)
            .where(
                and_(
                    PIMSSyncLog.clinic_id == str(clinic_id),
                    PIMSSyncLog.started_at >= trend_cutoff,
                    PIMSSyncLog.status.in_(
                        [
                            SyncJobStatus.COMPLETED,
                            SyncJobStatus.PARTIAL,
                            SyncJobStatus.FAILED,
                        ]
                    ),
                )
            )
            .group_by(func.date(PIMSSyncLog.started_at))
            .order_by(func.date(PIMSSyncLog.started_at))
        )
        sync_trend = [
            PIMSSyncDayTrend(
                date=str(row.day), successful=row.successful, failed=row.failed
            )
            for row in trend_result.all()
        ]

        return PIMSSyncAnalytics(
            connection_status=connection_status,
            last_sync_at=last_sync_at,
            sync_success_rate=round(sync_success_rate, 2),
            total_syncs_today=total_syncs_today,
            failed_syncs_today=failed_syncs_today,
            sync_trend=sync_trend,
        )

    @traced(span_name="analytics.get_sentiment_analytics")
    async def get_sentiment_analytics(
        self, clinic_id: UUID, days: int = 30
    ) -> SentimentData:
        """Analyze call sentiment from key_points JSONB field."""
        cutoff_date = datetime.now(UTC) - timedelta(days=days)

        # Query calls with sentiment data
        result = await self.db.execute(
            select(CallLog.key_points).where(
                and_(
                    CallLog.clinic_id == str(clinic_id),
                    CallLog.started_at >= cutoff_date,
                    CallLog.deleted_at.is_(None),
                    CallLog.key_points.is_not(None),
                )
            )
        )
        calls = result.scalars().all()

        positive = 0
        neutral = 0
        negative = 0
        sentiment_scores = []

        for key_points in calls:
            if not isinstance(key_points, dict):
                continue

            sentiment = key_points.get("sentiment")
            if sentiment == "positive":
                positive += 1
            elif sentiment == "neutral":
                neutral += 1
            elif sentiment == "negative":
                negative += 1

            # Extract sentiment score if available
            score = key_points.get("sentiment_score")
            if score is not None:
                sentiment_scores.append(float(score))

        avg_sentiment_score = (
            sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        )

        return SentimentData(
            positive_calls=positive,
            neutral_calls=neutral,
            negative_calls=negative,
            average_sentiment_score=round(avg_sentiment_score, 2),
        )

    @traced(span_name="analytics.get_recent_calls")
    async def get_recent_calls(
        self, clinic_id: UUID, limit: int = 10
    ) -> list[CallLogSummary]:
        """Get recent call logs for the dashboard table."""
        result = await self.db.execute(
            select(CallLog)
            .where(
                and_(
                    CallLog.clinic_id == str(clinic_id),
                    CallLog.deleted_at.is_(None),
                )
            )
            .order_by(CallLog.started_at.desc())
            .limit(limit)
        )
        calls = result.scalars().all()

        summaries = []
        for call in calls:
            # Extract sentiment from key_points
            sentiment = None
            if call.key_points and isinstance(call.key_points, dict):
                sentiment = call.key_points.get("sentiment")

            # Determine caller phone based on direction
            caller_phone = (
                call.from_phone
                if call.direction and call.direction.value == "inbound"
                else call.to_phone
            )

            summaries.append(
                CallLogSummary(
                    id=str(call.id),
                    started_at=call.started_at,
                    caller_phone_number=caller_phone,
                    duration_seconds=call.duration_seconds,
                    outcome=str(call.outcome.value) if call.outcome else "unknown",
                    sentiment=sentiment,
                    ai_confidence_score=call.ai_confidence_score,
                    direction=str(call.direction.value)
                    if call.direction
                    else "unknown",
                )
            )

        return summaries

    @traced(span_name="analytics.get_chat_analytics")
    async def get_chat_analytics(
        self, clinic_id: UUID, days: int = 30
    ) -> EnhancedChatAnalytics:
        """Aggregate chat metrics with AI analysis insights."""
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        today_start = datetime.now(UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # Total chats in period (filter by channel="chat")
        total_result = await self.db.execute(
            select(func.count())
            .select_from(Conversation)
            .where(
                and_(
                    Conversation.clinic_id == clinic_id,
                    Conversation.channel == "chat",
                    Conversation.created_at >= cutoff_date,
                )
            )
        )
        total_chats = total_result.scalar_one()

        # Chats today
        today_result = await self.db.execute(
            select(func.count())
            .select_from(Conversation)
            .where(
                and_(
                    Conversation.clinic_id == clinic_id,
                    Conversation.channel == "chat",
                    Conversation.created_at >= today_start,
                )
            )
        )
        chats_today = today_result.scalar_one()

        # Average messages per chat
        avg_messages_result = await self.db.execute(
            select(func.avg(Conversation.total_messages))
            .select_from(Conversation)
            .where(
                and_(
                    Conversation.clinic_id == clinic_id,
                    Conversation.channel == "chat",
                    Conversation.created_at >= cutoff_date,
                )
            )
        )
        avg_messages = avg_messages_result.scalar_one() or 0.0

        # Active sessions
        active_result = await self.db.execute(
            select(func.count())
            .select_from(Conversation)
            .where(
                and_(
                    Conversation.clinic_id == clinic_id,
                    Conversation.channel == "chat",
                    Conversation.session_active.is_(True),
                )
            )
        )
        active_sessions = active_result.scalar_one()

        # Chats by intent
        intent_result = await self.db.execute(
            select(Conversation.intent, func.count())
            .where(
                and_(
                    Conversation.clinic_id == clinic_id,
                    Conversation.channel == "chat",
                    Conversation.created_at >= cutoff_date,
                    Conversation.intent.is_not(None),
                )
            )
            .group_by(Conversation.intent)
        )
        chats_by_intent = {str(intent): count for intent, count in intent_result.all()}

        # Chats by hour (last 24 hours)
        last_24h = datetime.now(UTC) - timedelta(hours=24)
        hourly_result = await self.db.execute(
            select(
                func.extract("hour", Conversation.created_at).label("hour"),
                func.count().label("count"),
            )
            .where(
                and_(
                    Conversation.clinic_id == clinic_id,
                    Conversation.channel == "chat",
                    Conversation.created_at >= last_24h,
                )
            )
            .group_by(func.extract("hour", Conversation.created_at))
            .order_by(func.extract("hour", Conversation.created_at))
        )
        hourly_data = [
            {"hour": int(hour), "count": count} for hour, count in hourly_result.all()
        ]

        # Fill in missing hours with 0
        chats_by_hour_dict = {item["hour"]: item["count"] for item in hourly_data}
        chats_by_hour = [
            {"hour": h, "count": chats_by_hour_dict.get(h, 0)} for h in range(24)
        ]

        # --- AI Analysis Metrics ---
        # Sentiment distribution from completed analyses
        sentiment_result = await self.db.execute(
            select(ChatAnalysis.sentiment, func.count())
            .join(Conversation, ChatAnalysis.conversation_id == Conversation.id)
            .where(
                and_(
                    Conversation.clinic_id == clinic_id,
                    Conversation.channel == "chat",
                    Conversation.created_at >= cutoff_date,
                    ChatAnalysis.status == "completed",
                    ChatAnalysis.sentiment.is_not(None),
                )
            )
            .group_by(ChatAnalysis.sentiment)
        )
        sentiment_counts = {str(s): c for s, c in sentiment_result.all()}

        # Average sentiment score
        avg_score_result = await self.db.execute(
            select(func.avg(ChatAnalysis.sentiment_score))
            .join(Conversation, ChatAnalysis.conversation_id == Conversation.id)
            .where(
                and_(
                    Conversation.clinic_id == clinic_id,
                    Conversation.channel == "chat",
                    Conversation.created_at >= cutoff_date,
                    ChatAnalysis.status == "completed",
                    ChatAnalysis.sentiment_score.is_not(None),
                )
            )
        )
        avg_sentiment_score = avg_score_result.scalar_one() or 0.0

        chat_sentiment = ChatSentimentData(
            positive_chats=sentiment_counts.get("positive", 0),
            neutral_chats=sentiment_counts.get("neutral", 0),
            negative_chats=sentiment_counts.get("negative", 0),
            average_sentiment_score=round(avg_sentiment_score, 2),
        )

        # Resolution rate
        resolved_result = await self.db.execute(
            select(ChatAnalysis.resolution_status, func.count())
            .join(Conversation, ChatAnalysis.conversation_id == Conversation.id)
            .where(
                and_(
                    Conversation.clinic_id == clinic_id,
                    Conversation.channel == "chat",
                    Conversation.created_at >= cutoff_date,
                    ChatAnalysis.status == "completed",
                    ChatAnalysis.resolution_status.is_not(None),
                )
            )
            .group_by(ChatAnalysis.resolution_status)
        )
        resolution_counts = {str(r): c for r, c in resolved_result.all()}
        total_analyzed = sum(resolution_counts.values())
        resolved_count = resolution_counts.get("resolved", 0)
        resolution_rate = (
            round(resolved_count / total_analyzed * 100, 2)
            if total_analyzed > 0
            else None
        )

        # Top topics
        topic_result = await self.db.execute(
            select(ChatAnalysis.primary_topic, func.count().label("count"))
            .join(Conversation, ChatAnalysis.conversation_id == Conversation.id)
            .where(
                and_(
                    Conversation.clinic_id == clinic_id,
                    Conversation.channel == "chat",
                    Conversation.created_at >= cutoff_date,
                    ChatAnalysis.status == "completed",
                    ChatAnalysis.primary_topic.is_not(None),
                )
            )
            .group_by(ChatAnalysis.primary_topic)
            .order_by(func.count().desc())
            .limit(10)
        )
        top_topics = [
            {"topic": str(topic), "count": count} for topic, count in topic_result.all()
        ]

        # Satisfaction distribution
        satisfaction_result = await self.db.execute(
            select(ChatAnalysis.user_satisfaction, func.count())
            .join(Conversation, ChatAnalysis.conversation_id == Conversation.id)
            .where(
                and_(
                    Conversation.clinic_id == clinic_id,
                    Conversation.channel == "chat",
                    Conversation.created_at >= cutoff_date,
                    ChatAnalysis.status == "completed",
                    ChatAnalysis.user_satisfaction.is_not(None),
                )
            )
            .group_by(ChatAnalysis.user_satisfaction)
        )
        satisfaction_dist = {str(s): c for s, c in satisfaction_result.all()}

        return EnhancedChatAnalytics(
            total_chats=total_chats,
            chats_today=chats_today,
            average_messages_per_chat=round(avg_messages, 2),
            active_sessions=active_sessions,
            chats_by_intent=chats_by_intent,
            chats_by_hour=chats_by_hour,
            sentiment=chat_sentiment,
            resolution_rate=resolution_rate,
            top_topics=top_topics if top_topics else None,
            satisfaction_distribution=satisfaction_dist if satisfaction_dist else None,
            analyzed_count=total_analyzed,
        )

    @traced(span_name="analytics.get_recent_chats")
    async def get_recent_chats(
        self, clinic_id: UUID, limit: int = 10
    ) -> list[ChatLogSummary]:
        """Get recent chat conversations with analysis data."""
        from sqlalchemy.orm import joinedload

        result = await self.db.execute(
            select(Conversation)
            .options(joinedload(Conversation.analysis))
            .where(
                and_(
                    Conversation.clinic_id == clinic_id,
                    Conversation.channel == "chat",
                )
            )
            .order_by(Conversation.created_at.desc())
            .limit(limit)
        )
        conversations = result.unique().scalars().all()

        summaries = []
        for conv in conversations:
            analysis = conv.analysis
            summaries.append(
                ChatLogSummary(
                    id=str(conv.id),
                    started_at=conv.created_at,
                    user_identifier=conv.user_identifier,
                    total_messages=conv.total_messages,
                    intent=conv.intent,
                    session_active=conv.session_active,
                    summary=conv.summary,
                    sentiment=analysis.sentiment if analysis else None,
                    resolution_status=analysis.resolution_status if analysis else None,
                    primary_topic=analysis.primary_topic if analysis else None,
                )
            )

        return summaries

    @traced(span_name="analytics.get_dashboard_analytics")
    async def get_dashboard_analytics(
        self, clinic_id: UUID, days: int = 30
    ) -> DashboardAnalytics:
        """Get all dashboard analytics in parallel for better performance."""
        import asyncio

        # Run all analytics queries in parallel (4x faster!)
        results: tuple[
            CallAnalytics,
            AppointmentAnalytics,
            PatientAnalytics,
            PIMSSyncAnalytics,
            SentimentData,
            list[CallLogSummary],
            EnhancedChatAnalytics,
            list[ChatLogSummary],
        ] = await asyncio.gather(  # type: ignore[assignment]
            self.get_call_analytics(clinic_id, days=days),
            self.get_appointment_analytics(clinic_id, days=days),
            self.get_patient_analytics(clinic_id),
            self.get_pims_analytics(clinic_id),
            self.get_sentiment_analytics(clinic_id, days=days),
            self.get_recent_calls(clinic_id),
            self.get_chat_analytics(clinic_id, days=days),
            self.get_recent_chats(clinic_id),
        )

        (
            calls,
            appointments,
            patients,
            pims,
            sentiment,
            recent_calls,
            chats,
            recent_chats,
        ) = results

        return DashboardAnalytics(
            calls=calls,
            appointments=appointments,
            patients=patients,
            pims=pims,
            sentiment=sentiment,
            recent_calls=recent_calls,
            chats=chats,
            recent_chats=recent_chats,
        )
