#!/bin/bash
# =============================================================================
# Production Entrypoint Script
# Runs database migrations before starting the server
# =============================================================================

set -e

echo "Running database migrations..."
uv run alembic upgrade head

echo "Starting FastAPI server..."
exec uv run fastapi run --host 0.0.0.0 --port "${PORT:-8000}"
