"""Analytics schemas for dashboard metrics."""

from datetime import datetime

from pydantic import BaseModel


class CallAnalytics(BaseModel):
    """Call center analytics metrics."""

    total_calls: int
    calls_today: int
    inbound_calls: int
    outbound_calls: int
    ai_handled_percentage: float  # % handled without transfer
    average_duration_seconds: float
    emergency_transfers: int
    appointments_booked: int
    average_confidence_score: float
    calls_by_outcome: dict[str, int]  # outcome -> count
    calls_by_hour: list[dict[str, int]]  # hourly distribution for chart


class AppointmentAnalytics(BaseModel):
    """Appointment booking analytics."""

    total_appointments: int
    appointments_this_week: int
    bookings_via_ai: int
    bookings_via_dashboard: int
    no_show_rate: float
    cancellation_rate: float
    appointments_by_type: dict[str, int]  # type -> count
    appointments_by_status: dict[str, int]  # status -> count


class PatientAnalytics(BaseModel):
    """Patient statistics."""

    total_active_patients: int
    new_patients_this_month: int
    patients_by_species: dict[str, int]  # species -> count
    total_owners: int  # distinct owners


class PIMSSyncAnalytics(BaseModel):
    """PIMS integration health."""

    connection_status: str
    last_sync_at: datetime | None
    sync_success_rate: float
    total_syncs_today: int
    failed_syncs_today: int


class SentimentData(BaseModel):
    """Call sentiment analysis."""

    positive_calls: int
    neutral_calls: int
    negative_calls: int
    average_sentiment_score: float


class CallLogSummary(BaseModel):
    """Summary of a single call for recent calls table."""

    id: str
    started_at: datetime
    caller_phone_number: str | None
    duration_seconds: int | None
    outcome: str
    sentiment: str | None
    ai_confidence_score: float | None
    direction: str


class DashboardAnalytics(BaseModel):
    """Complete dashboard analytics."""

    calls: CallAnalytics
    appointments: AppointmentAnalytics
    patients: PatientAnalytics
    pims: PIMSSyncAnalytics
    sentiment: SentimentData
    recent_calls: list[CallLogSummary]
