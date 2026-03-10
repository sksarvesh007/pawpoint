"""Report generation service."""

from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import Date, and_, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.instrumentation import traced
from app.schemas.reports import ReportResponse


class ReportsService:
    """Service for generating clinic reports."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @traced(span_name="reports.generate")
    async def generate_report(
        self,
        clinic_id: UUID,
        report_type: str,
        start_date: date,
        end_date: date,
    ) -> ReportResponse:
        """Generate a report for the given type and date range."""
        generators = {
            "call_summary": self._call_summary,
            "appointment_summary": self._appointment_summary,
            "patient_summary": self._patient_summary,
            "ai_performance": self._ai_performance,
        }

        generator = generators.get(report_type)
        if not generator:
            raise ValueError(f"Unknown report type: {report_type}")

        return await generator(clinic_id, start_date, end_date)

    async def _call_summary(
        self, clinic_id: UUID, start_date: date, end_date: date
    ) -> ReportResponse:
        from app.models.call_log import CallLog, CallOutcome

        rows: list[dict] = []
        total_calls = 0
        total_ai = 0
        total_transferred = 0
        total_booked = 0

        current = start_date
        while current <= end_date:
            day_start = datetime.combine(current, datetime.min.time()).replace(
                tzinfo=UTC
            )
            day_end = day_start + timedelta(days=1)
            base = and_(
                CallLog.clinic_id == str(clinic_id),
                CallLog.started_at >= day_start,
                CallLog.started_at < day_end,
                CallLog.deleted_at.is_(None),
            )

            result = await self.db.execute(
                select(
                    func.count().label("total"),
                    func.count()
                    .filter(CallLog.direction == "inbound")
                    .label("inbound"),
                    func.count()
                    .filter(CallLog.direction == "outbound")
                    .label("outbound"),
                    func.coalesce(func.avg(CallLog.duration_seconds), 0).label(
                        "avg_dur"
                    ),
                    func.count()
                    .filter(CallLog.ai_handled.is_(True))
                    .label("ai_handled"),
                    func.count()
                    .filter(CallLog.outcome == CallOutcome.TRANSFERRED_TO_STAFF)
                    .label("transferred"),
                    func.count()
                    .filter(CallLog.outcome == CallOutcome.APPOINTMENT_BOOKED)
                    .label("booked"),
                ).where(base)
            )
            r = result.one()
            row = {
                "date": current.isoformat(),
                "total_calls": r.total,
                "inbound": r.inbound,
                "outbound": r.outbound,
                "avg_duration_seconds": round(float(r.avg_dur), 1),
                "ai_handled": r.ai_handled,
                "transferred": r.transferred,
                "appointments_booked": r.booked,
            }
            rows.append(row)
            total_calls += r.total
            total_ai += r.ai_handled
            total_transferred += r.transferred
            total_booked += r.booked
            current += timedelta(days=1)

        return ReportResponse(
            report_type="call_summary",
            title="Call Summary Report",
            start_date=start_date,
            end_date=end_date,
            generated_at=datetime.now(UTC),
            columns=[
                "Date",
                "Total Calls",
                "Inbound",
                "Outbound",
                "Avg Duration (s)",
                "AI Handled",
                "Transferred",
                "Appointments Booked",
            ],
            rows=rows,
            summary={
                "total_calls": total_calls,
                "total_ai_handled": total_ai,
                "total_transferred": total_transferred,
                "total_appointments_booked": total_booked,
                "ai_resolution_rate": round(
                    total_ai / total_calls * 100 if total_calls else 0, 1
                ),
            },
        )

    async def _appointment_summary(
        self, clinic_id: UUID, start_date: date, end_date: date
    ) -> ReportResponse:
        from app.models.appointment import Appointment, AppointmentStatus

        rows: list[dict] = []
        totals = {
            "total": 0,
            "scheduled": 0,
            "completed": 0,
            "cancelled": 0,
            "no_show": 0,
        }

        current = start_date
        while current <= end_date:
            base = and_(
                Appointment.clinic_id == str(clinic_id),
                cast(Appointment.start_time, Date) == current,
                Appointment.deleted_at.is_(None),
            )

            result = await self.db.execute(
                select(
                    func.count().label("total"),
                    func.count()
                    .filter(Appointment.status == AppointmentStatus.SCHEDULED)
                    .label("scheduled"),
                    func.count()
                    .filter(Appointment.status == AppointmentStatus.COMPLETED)
                    .label("completed"),
                    func.count()
                    .filter(Appointment.status == AppointmentStatus.CANCELLED)
                    .label("cancelled"),
                    func.count()
                    .filter(Appointment.status == AppointmentStatus.NO_SHOW)
                    .label("no_show"),
                ).where(base)
            )
            r = result.one()
            row = {
                "date": current.isoformat(),
                "total": r.total,
                "scheduled": r.scheduled,
                "completed": r.completed,
                "cancelled": r.cancelled,
                "no_show": r.no_show,
            }
            rows.append(row)
            for k in totals:
                totals[k] += getattr(r, k)
            current += timedelta(days=1)

        return ReportResponse(
            report_type="appointment_summary",
            title="Appointment Summary Report",
            start_date=start_date,
            end_date=end_date,
            generated_at=datetime.now(UTC),
            columns=["Date", "Total", "Scheduled", "Completed", "Cancelled", "No Show"],
            rows=rows,
            summary=totals,
        )

    async def _patient_summary(
        self, clinic_id: UUID, start_date: date, end_date: date
    ) -> ReportResponse:
        from app.models.patient import Patient

        # Species breakdown
        result = await self.db.execute(
            select(Patient.species, func.count().label("total"))
            .where(
                and_(
                    Patient.clinic_id == str(clinic_id),
                    Patient.deleted_at.is_(None),
                )
            )
            .group_by(Patient.species)
        )
        species_counts = {str(s): int(c) for s, c in result.all()}

        # New patients in period
        period_start = datetime.combine(start_date, datetime.min.time()).replace(
            tzinfo=UTC
        )
        period_end = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=UTC)

        result = await self.db.execute(
            select(Patient.species, func.count().label("new_count"))
            .where(
                and_(
                    Patient.clinic_id == str(clinic_id),
                    Patient.created_at >= period_start,
                    Patient.created_at <= period_end,
                    Patient.deleted_at.is_(None),
                )
            )
            .group_by(Patient.species)
        )
        new_counts = {str(s): int(c) for s, c in result.all()}

        rows = [
            {
                "species": species,
                "total": count,
                "new_this_period": new_counts.get(species, 0),
            }
            for species, count in sorted(
                species_counts.items(), key=lambda x: x[1], reverse=True
            )
        ]

        return ReportResponse(
            report_type="patient_summary",
            title="Patient Summary Report",
            start_date=start_date,
            end_date=end_date,
            generated_at=datetime.now(UTC),
            columns=["Species", "Total Patients", "New This Period"],
            rows=rows,
            summary={
                "total_patients": sum(species_counts.values()),
                "new_patients": sum(new_counts.values()),
                "species_count": len(species_counts),
            },
        )

    async def _ai_performance(
        self, clinic_id: UUID, start_date: date, end_date: date
    ) -> ReportResponse:
        from app.models.call_log import CallLog, CallOutcome

        rows: list[dict] = []
        total_interactions = 0
        total_transfers = 0

        current = start_date
        while current <= end_date:
            day_start = datetime.combine(current, datetime.min.time()).replace(
                tzinfo=UTC
            )
            day_end = day_start + timedelta(days=1)
            base = and_(
                CallLog.clinic_id == str(clinic_id),
                CallLog.started_at >= day_start,
                CallLog.started_at < day_end,
                CallLog.deleted_at.is_(None),
            )

            result = await self.db.execute(
                select(
                    func.count().label("total"),
                    func.coalesce(func.avg(CallLog.ai_confidence_score), 0).label(
                        "avg_conf"
                    ),
                    func.count()
                    .filter(CallLog.ai_handled.is_(True))
                    .label("ai_handled"),
                    func.count()
                    .filter(CallLog.outcome == CallOutcome.TRANSFERRED_TO_STAFF)
                    .label("xfer"),
                    func.count()
                    .filter(CallLog.outcome == CallOutcome.APPOINTMENT_BOOKED)
                    .label("booked"),
                ).where(base)
            )
            r = result.one()
            xfer_rate = round(r.xfer / r.total * 100 if r.total else 0, 1)
            rows.append(
                {
                    "date": current.isoformat(),
                    "total_interactions": r.total,
                    "avg_confidence": round(float(r.avg_conf), 2),
                    "ai_handled": r.ai_handled,
                    "transferred": r.xfer,
                    "appointments_booked": r.booked,
                    "transfer_rate": xfer_rate,
                }
            )
            total_interactions += r.total
            total_transfers += r.xfer
            current += timedelta(days=1)

        return ReportResponse(
            report_type="ai_performance",
            title="AI Performance Report",
            start_date=start_date,
            end_date=end_date,
            generated_at=datetime.now(UTC),
            columns=[
                "Date",
                "Total Interactions",
                "Avg Confidence",
                "AI Handled",
                "Transferred",
                "Appointments Booked",
                "Transfer Rate %",
            ],
            rows=rows,
            summary={
                "total_interactions": total_interactions,
                "total_transfers": total_transfers,
                "overall_transfer_rate": round(
                    total_transfers / total_interactions * 100
                    if total_interactions
                    else 0,
                    1,
                ),
            },
        )
