"""Report schemas for generating clinic reports."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    """Request parameters for generating a report."""

    report_type: str = Field(
        ...,
        description="Type of report: call_summary, appointment_summary, patient_summary, ai_performance",
    )
    start_date: date = Field(..., description="Report start date")
    end_date: date = Field(..., description="Report end date")


class CallSummaryRow(BaseModel):
    """A single row in the call summary report."""

    date: str
    total_calls: int
    inbound: int
    outbound: int
    avg_duration_seconds: float
    ai_handled: int
    transferred: int
    appointments_booked: int


class AppointmentSummaryRow(BaseModel):
    """A single row in the appointment summary report."""

    date: str
    total: int
    scheduled: int
    completed: int
    cancelled: int
    no_show: int


class PatientSummaryRow(BaseModel):
    """A single row in the patient summary report."""

    species: str
    total: int
    new_this_period: int


class AIPerformanceRow(BaseModel):
    """A single row in the AI performance report."""

    date: str
    total_interactions: int
    avg_confidence: float
    positive_sentiment: int
    neutral_sentiment: int
    negative_sentiment: int
    transfer_rate: float


class ReportResponse(BaseModel):
    """Response containing generated report data."""

    report_type: str
    title: str
    start_date: date
    end_date: date
    generated_at: datetime
    columns: list[str]
    rows: list[dict]
    summary: dict
