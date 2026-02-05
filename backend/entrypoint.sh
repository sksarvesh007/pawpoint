#!/bin/bash
# =============================================================================
# Production Entrypoint Script
# Runs database migrations before starting the server
# =============================================================================

set -e

echo "Running database migrations..."
uv run --no-sync alembic upgrade head

echo "Starting FastAPI server..."
exec uv run --no-sync fastapi run --host 0.0.0.0 --port "${PORT:-8000}"
