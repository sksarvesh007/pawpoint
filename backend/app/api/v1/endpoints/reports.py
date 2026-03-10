"""Reports API endpoints."""

import csv
import io
from datetime import date, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_clinic
from app.core.rate_limit import limiter
from app.db import get_db
from app.models.clinic import Clinic
from app.schemas.reports import ReportResponse
from app.services.reports import ReportsService

router = APIRouter()

ReportType = Literal[
    "call_summary", "appointment_summary", "patient_summary", "ai_performance"
]


@router.get("/generate", response_model=ReportResponse)
@limiter.limit("30/minute")
async def generate_report(
    request: Request,
    report_type: ReportType = Query(..., description="Report type"),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> ReportResponse:
    """Generate a report for the specified type and date range."""
    if (end_date - start_date).days > 365:
        end_date = start_date + timedelta(days=365)

    service = ReportsService(db)
    return await service.generate_report(
        clinic_id=current_clinic.id,
        report_type=report_type,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/export")
@limiter.limit("10/minute")
async def export_report_csv(
    request: Request,
    report_type: ReportType = Query(..., description="Report type"),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Export a report as CSV file."""
    if (end_date - start_date).days > 365:
        end_date = start_date + timedelta(days=365)

    service = ReportsService(db)
    report = await service.generate_report(
        clinic_id=current_clinic.id,
        report_type=report_type,
        start_date=start_date,
        end_date=end_date,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(report.columns)
    for row in report.rows:
        writer.writerow(row.values())

    output.seek(0)
    filename = f"{report_type}_{start_date}_{end_date}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
