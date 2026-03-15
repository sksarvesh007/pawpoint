"""Tests for recording API endpoints."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.recordings import _get_storage
from app.main import app
from app.models.call_log import CallLog, CallStatus
from tests.helpers import create_call_log, create_test_clinic, setup_auth


def _mock_storage() -> MagicMock:
    """Create a mock StorageService with async methods."""
    mock = MagicMock()
    mock.upload_recording = AsyncMock(
        return_value="http://localhost:9000/pawpoint-recordings/recordings/test.wav"
    )
    mock.get_presigned_url = AsyncMock(
        return_value="http://localhost:9000/pawpoint-recordings/recordings/test.wav?X-Amz-Signature=abc"
    )
    mock.delete_recording = AsyncMock()
    mock.ensure_bucket = AsyncMock()
    return mock


@pytest.mark.asyncio
async def test_upload_requires_auth(client: AsyncClient) -> None:
    """Upload endpoint requires authentication."""
    response = await client.post(
        f"/api/v1/recordings/upload/{uuid.uuid4()}",
        files={"file": ("test.wav", b"fake-audio", "audio/wav")},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_recording_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Upload recording stores in S3 and updates CallLog.recording_url."""
    clinic = await setup_auth(db_session, client)
    call = await create_call_log(db_session, clinic.id)

    mock = _mock_storage()
    app.dependency_overrides[_get_storage] = lambda: mock
    try:
        response = await client.post(
            f"/api/v1/recordings/upload/{call.id}",
            files={"file": ("test.wav", b"fake-audio-data", "audio/wav")},
        )
    finally:
        app.dependency_overrides.pop(_get_storage, None)

    assert response.status_code == 201
    data = response.json()
    assert data["call_id"] == str(call.id)
    assert "recording_url" in data
    assert data["size_bytes"] == len(b"fake-audio-data")

    mock.upload_recording.assert_awaited_once()

    # Verify DB was updated
    await db_session.refresh(call)
    assert call.recording_url is not None


@pytest.mark.asyncio
async def test_get_recording_url(client: AsyncClient, db_session: AsyncSession) -> None:
    """Returns a presigned URL for an existing recording."""
    clinic = await setup_auth(db_session, client)
    call = await create_call_log(
        db_session,
        clinic.id,
        recording_url="http://localhost:9000/pawpoint-recordings/recordings/test.wav",
    )

    mock = _mock_storage()
    app.dependency_overrides[_get_storage] = lambda: mock
    try:
        response = await client.get(f"/api/v1/recordings/{call.id}")
    finally:
        app.dependency_overrides.pop(_get_storage, None)

    assert response.status_code == 200
    data = response.json()
    assert data["call_id"] == str(call.id)
    assert "presigned_url" in data
    assert data["expires_in"] == 3600

    mock.get_presigned_url.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_recording_not_found(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Returns 404 when call has no recording."""
    clinic = await setup_auth(db_session, client)
    call = await create_call_log(db_session, clinic.id, recording_url=None)

    mock = _mock_storage()
    app.dependency_overrides[_get_storage] = lambda: mock
    try:
        response = await client.get(f"/api/v1/recordings/{call.id}")
    finally:
        app.dependency_overrides.pop(_get_storage, None)

    assert response.status_code == 404
    assert "No recording" in response.json()["detail"]


@pytest.mark.asyncio
async def test_twilio_recording_callback(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Twilio webhook fetches .wav from Twilio, stores in S3, updates CallLog."""
    clinic = await create_test_clinic(db_session)
    call = CallLog(
        clinic_id=clinic.id,
        direction="inbound",
        status=CallStatus.COMPLETED,
        from_phone="+15551234567",
        to_phone="+15559876543",
        started_at=datetime.now(UTC),
        duration_seconds=60,
        ai_handled=True,
        ai_confidence_score=0.9,
        twilio_call_sid="CA1234567890abcdef",
    )
    db_session.add(call)
    await db_session.flush()

    mock_storage = _mock_storage()
    app.dependency_overrides[_get_storage] = lambda: mock_storage

    try:
        with (
            patch(
                "app.api.v1.endpoints.recordings._validate_twilio_signature",
                return_value=True,
            ),
            patch("app.api.v1.endpoints.recordings.httpx") as mock_httpx,
        ):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.content = b"wav-audio-bytes"

            mock_http_client = AsyncMock()
            mock_http_client.get = AsyncMock(return_value=mock_resp)
            mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
            mock_http_client.__aexit__ = AsyncMock(return_value=False)
            mock_httpx.AsyncClient.return_value = mock_http_client

            response = await client.post(
                "/api/v1/recordings/webhooks/twilio",
                data={
                    "RecordingSid": "RE9876543210",
                    "RecordingUrl": "https://api.twilio.com/2010-04-01/Accounts/AC123/Recordings/RE9876543210",
                    "CallSid": "CA1234567890abcdef",
                    "RecordingDuration": "45",
                },
            )
    finally:
        app.dependency_overrides.pop(_get_storage, None)

    assert response.status_code == 204

    mock_storage.upload_recording.assert_awaited_once()

    # Verify DB was updated
    await db_session.refresh(call)
    assert call.recording_url is not None
    assert call.recording_duration_seconds == 45


@pytest.mark.asyncio
async def test_upload_recording_unsupported_format(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Upload endpoint rejects non-audio file formats with 400."""
    clinic = await setup_auth(db_session, client)
    call = await create_call_log(db_session, clinic.id)

    mock = _mock_storage()
    app.dependency_overrides[_get_storage] = lambda: mock
    try:
        response = await client.post(
            f"/api/v1/recordings/upload/{call.id}",
            files={"file": ("notes.txt", b"some text content", "text/plain")},
        )
    finally:
        app.dependency_overrides.pop(_get_storage, None)

    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]
    mock.upload_recording.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_recording_requires_auth(client: AsyncClient) -> None:
    """GET recording URL endpoint requires authentication."""
    response = await client.get(f"/api/v1/recordings/{uuid.uuid4()}")
    assert response.status_code == 401
