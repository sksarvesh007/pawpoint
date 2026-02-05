#!/bin/bash
# =============================================================================
# Production Entrypoint Script
# Runs database migrations before starting the server
# =============================================================================

set -e

echo "Running database migrations..."
uv run --no-sync alembic upgrade head

echo "Enabling voice for all clinics..."
uv run --no-sync python -c "
import asyncio
from sqlalchemy import update
from app.db import async_session_factory
from app.models.clinic import Clinic

async def enable_voice():
    async with async_session_factory() as db:
        result = await db.execute(update(Clinic).values(voice_enabled=True))
        await db.commit()
        print(f'Voice enabled for {result.rowcount} clinic(s)')

asyncio.run(enable_voice())
"

echo "Starting FastAPI server..."
exec uv run --no-sync fastapi run --host 0.0.0.0 --port "${PORT:-8000}"
