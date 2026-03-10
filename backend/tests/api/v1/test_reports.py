"""Tests for reports API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import setup_auth

# Base URL for report endpoints
GENERATE_URL = "/api/v1/reports/generate"
EXPORT_URL = "/api/v1/reports/export"

# Default query params for a valid report request
DEFAULT_PARAMS = {
    "report_type": "call_summary",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
}


# =============================================================================
# Authentication Tests
# =============================================================================


@pytest.mark.asyncio
async def test_generate_report_requires_auth(client: AsyncClient) -> None:
    """Test that generating a report without auth returns 401."""
    response = await client.get(GENERATE_URL, params=DEFAULT_PARAMS)
    assert response.status_code == 401


# =============================================================================
# Generate Report Tests
# =============================================================================


@pytest.mark.asyncio
async def test_generate_report_call_summary(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test generating a call_summary report returns expected structure."""
    await setup_auth(db_session, client)

    response = await client.get(GENERATE_URL, params=DEFAULT_PARAMS)
    assert response.status_code == 200

    data = response.json()
    assert data["report_type"] == "call_summary"
    assert data["title"] == "Call Summary Report"
    assert isinstance(data["columns"], list)
    assert len(data["columns"]) > 0
    assert isinstance(data["rows"], list)
    assert isinstance(data["summary"], dict)
    assert "start_date" in data
    assert "end_date" in data
    assert "generated_at" in data


@pytest.mark.asyncio
async def test_generate_report_appointment_summary(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test generating an appointment_summary report returns expected structure."""
    await setup_auth(db_session, client)

    params = {**DEFAULT_PARAMS, "report_type": "appointment_summary"}
    response = await client.get(GENERATE_URL, params=params)
    assert response.status_code == 200

    data = response.json()
    assert data["report_type"] == "appointment_summary"
    assert data["title"] == "Appointment Summary Report"
    assert isinstance(data["columns"], list)
    assert len(data["columns"]) > 0
    assert isinstance(data["rows"], list)
    assert isinstance(data["summary"], dict)


@pytest.mark.asyncio
async def test_generate_report_patient_summary(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test generating a patient_summary report returns expected structure."""
    await setup_auth(db_session, client)

    params = {**DEFAULT_PARAMS, "report_type": "patient_summary"}
    response = await client.get(GENERATE_URL, params=params)
    assert response.status_code == 200

    data = response.json()
    assert data["report_type"] == "patient_summary"
    assert data["title"] == "Patient Summary Report"
    assert isinstance(data["columns"], list)
    assert len(data["columns"]) > 0
    assert isinstance(data["rows"], list)
    assert isinstance(data["summary"], dict)


@pytest.mark.asyncio
async def test_generate_report_ai_performance(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test generating an ai_performance report returns expected structure."""
    await setup_auth(db_session, client)

    params = {**DEFAULT_PARAMS, "report_type": "ai_performance"}
    response = await client.get(GENERATE_URL, params=params)
    assert response.status_code == 200

    data = response.json()
    assert data["report_type"] == "ai_performance"
    assert data["title"] == "AI Performance Report"
    assert isinstance(data["columns"], list)
    assert len(data["columns"]) > 0
    assert isinstance(data["rows"], list)
    assert isinstance(data["summary"], dict)


@pytest.mark.asyncio
async def test_generate_report_invalid_type(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test that an invalid report_type returns 422 validation error."""
    await setup_auth(db_session, client)

    params = {**DEFAULT_PARAMS, "report_type": "nonexistent_report"}
    response = await client.get(GENERATE_URL, params=params)
    assert response.status_code == 422


# =============================================================================
# Export CSV Tests
# =============================================================================


@pytest.mark.asyncio
async def test_export_csv(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test exporting a report as CSV returns text/csv content type."""
    await setup_auth(db_session, client)

    response = await client.get(EXPORT_URL, params=DEFAULT_PARAMS)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")


@pytest.mark.asyncio
async def test_export_csv_has_content_disposition(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test that CSV export includes Content-Disposition header with filename."""
    await setup_auth(db_session, client)

    response = await client.get(EXPORT_URL, params=DEFAULT_PARAMS)
    assert response.status_code == 200

    content_disposition = response.headers.get("content-disposition", "")
    assert "attachment" in content_disposition
    assert "filename=" in content_disposition
    assert "call_summary" in content_disposition
    assert ".csv" in content_disposition
