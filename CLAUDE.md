# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PawPoint is an AI-powered veterinary clinic management platform with a Python FastAPI backend and Next.js frontend. Key features include appointments, patient records, PIMS (Practice Information Management System) integration, and AI-powered voice interactions.

## Tech Stack

**Backend**: Python 3.13+, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, UV package manager
**Frontend**: Next.js 16.1.3, React 19.2.3, TypeScript, Tailwind CSS 4, Bun
**AI**: pydantic-ai with DeepSeek (primary), Google Gemini (fallback), OpenAI-compatible API
**Voice**: LiveKit (WebRTC + SIP), AssemblyAI (STT), Cartesia (TTS), Silero (VAD)
**Observability**: OpenTelemetry → Alloy → Tempo/Prometheus/Loki → Grafana
**Background Jobs**: Celery + Redis

## Common Commands

### Backend

```bash
cd backend
uv sync                              # Install dependencies
PYTHONPATH=. uv run fastapi dev app/main.py  # Run dev server (port 8000)
uv run pytest                        # Run all tests
uv run pytest tests/test_api/test_health.py  # Run specific test file
uv run pytest -k "test_name"         # Run tests matching pattern
uv run ruff check . --fix            # Lint and auto-fix
uv run ruff format .                 # Format code
uv run ty check                      # Type check

# Database migrations (Alembic)
uv run alembic revision --autogenerate -m "description"  # Generate migration
uv run alembic upgrade head          # Apply all migrations
uv run alembic downgrade -1          # Rollback last migration

# Seed data (requires db running and DATABASE_URL in dev.env)
PYTHONPATH=. uv run python scripts/seed_data.py           # Seed database
PYTHONPATH=. uv run python scripts/seed_data.py --clear   # Clear and re-seed
PYTHONPATH=. uv run python scripts/seed_data.py --minimal # Minimal data set
```

### Frontend

```bash
cd frontend
bun install                          # Install dependencies
bun dev                              # Run dev server (port 3000)
bun build                            # Production build
bun run lint                         # ESLint
```

### Docker & Observability

```bash
# Start services
docker compose up                    # Start all services (db, backend, frontend, observability)
docker compose up backend frontend   # Start backend + frontend (app services only)
docker compose up backend            # Start backend + db only
docker compose up db                 # Start PostgreSQL only

# View logs with Lazydocker (recommended)
lazydocker                           # Interactive TUI for all services
# Install: brew install lazydocker

# Service URLs
# Backend API: http://localhost:8000
# Frontend: http://localhost:3000
# PostgreSQL: localhost:5434 (non-standard to avoid local conflicts)
# MinIO: http://localhost:9000 (API), http://localhost:9001 (Console)
# Grafana: http://localhost:3001 (admin/admin)
# Prometheus: http://localhost:9090
```

## Architecture

### Backend Layers (`backend/app/`)

- **api/v1/endpoints/**: HTTP handlers — keep thin, delegate to services. ~17 modules covering auth, clinic, appointments, patients, providers, AI chat (streaming + non-streaming), voice, calls, recordings, PIMS, analytics.
- **services/**: Business logic — auth, appointment, analytics, patient, provider, clinic, outbound_call, storage (MinIO), pims, voice
- **models/**: SQLAlchemy ORM models with mixins (UUID, Timestamp, SoftDelete, PIMSSync)
- **schemas/**: Pydantic request/response validation
- **adapters/pims/**: External PIMS integrations via adapter pattern
- **core/**: Config, security, logging, telemetry, instrumentation
- **ai/**: Pydantic AI agents, model factory, conversation state, tools
- **workers/**: Celery tasks and beat scheduler
- **middleware/**: Request logging, security headers, metrics, rate limiting

### Multi-Tenant Routing

All clinic operations are scoped to a clinic resolved from the URL slug:

```python
ClinicDep = Annotated[Clinic, Depends(get_clinic_by_slug)]

@router.get("/{clinic_slug}/appointments")
async def get_appointments(clinic: ClinicDep, db: DbSession):
    ...
```

The `get_current_user()` dependency accepts JWT from either httpOnly cookie or `Authorization: Bearer` header. The JWT payload carries `user_id` (as `sub`) and `clinic_id`.

### Backend Key Design Patterns

- **Dependency Injection**: `get_db()` for async sessions, `get_current_user()` for JWT auth, `get_clinic_by_slug()` for multi-tenant scoping
- **Mixin-based Models**: All models inherit `Base` (UUID PK, auto table name) + optional `TimestampMixin`, `SoftDeleteMixin`, `PIMSSyncMixin`
- **Soft Deletes**: `SoftDeleteMixin` adds `deleted_at`; queries must explicitly filter `Model.deleted_at == None`
- **PIMS Adapter Factory**: `get_pims_adapter(clinic)` returns the correct `IPIMSAdapter` implementation based on `clinic.pims_type`
- **Async Throughout**: All DB and HTTP operations use async/await; Celery tasks use `get_db_session()` context manager (not the FastAPI dependency) to avoid event loop conflicts

### PIMSSyncMixin

Models that sync with external PIMS systems use `PIMSSyncMixin`, which adds:
- `pims_id`, `sync_status` (pending/synced/conflict/error/local_only)
- `last_synced_at`, `pims_version` for conflict detection
- `mark_synced()`, `mark_sync_error()`, `mark_sync_conflict()` helpers

### PIMS Adapters (`backend/app/adapters/pims/`)

Supported systems: ezyVet, Vetspire, Avimark, Cornerstone, Pulse, Impromed/Covetrus. The base adapter provides:
- Abstract interface all adapters must implement
- Shared `_request()` with retry + exponential backoff, rate-limit handling (Retry-After), 401 re-auth
- Error hierarchy: `PIMSError`, `PIMSAuthError`, `PIMSRateLimitError`, `PIMSConnectionError`

Credentials are encrypted via `encrypt_credentials()` / `decrypt_credentials()` and stored as `pims_credentials_encrypted` on the Clinic model.

### AI Agents (`backend/app/ai/`)

Five specialized pydantic-ai agents: `AppointmentAgent`, `AnalyticsAgent`, `ClinicAgent`, `FAQAgent`, `BaseAgent`.

- Tools are registered with `@agent.tool` and receive `RunContext[AgentDependencies]` for access to `db_session`, `redis_client`, `clinic_id`, etc.
- `ModelFactory.get_model_for_task(task_type, channel)` selects the right model (DeepSeek, Gemini, OpenAI) per task (appointment_booking, reasoning, chat, voice)
- Conversation state: active sessions in Redis (30 min TTL, extendable), full history persisted to PostgreSQL

### Voice / LiveKit Integration

- `VoiceService` generates LiveKit access tokens and pre-creates rooms with metadata (clinic_id, channel, user_id)
- Webhooks use HMAC-SHA256 signature verification
- `CallLog` records track status, duration, transcript, summary, actions_taken, outcome
- SIP integration via `livekit-sip` service for phone calls
- `LIVEKIT_AGENT_EMBEDDED=true` runs the LiveKit agent inside FastAPI (useful for limited deployments); otherwise it runs as a separate worker

### Background Jobs (`backend/app/workers/`)

- `analyze_chat_conversation`: LLM analysis of completed chats → creates `ChatAnalysis` records
- `cleanup_stale_sessions`: Periodic cleanup of abandoned Redis sessions
- Beat scheduler runs inside the `celery-worker` container (`--beat` flag)

### Environment Configuration

Environment files: `backend/dev.env`, `backend/prod.env`, `backend/test.env`.

**To switch environments**: change the `ENVIRONMENT` constant at the top of `backend/app/core/config.py`. Pydantic Settings reads the corresponding `.env` file.

The `Settings` class exposes `is_development`, `is_production`, `is_testing` properties. Swagger/ReDoc UI is disabled in production unless `settings.debug` is True. The `/metrics` endpoint uses HTTP Basic auth (`METRICS_USERNAME`, `METRICS_PASSWORD`).

### Observability

- `@traced()` decorator creates OpenTelemetry spans automatically
- Metrics: `api_requests_total`, `api_request_duration_seconds`, `db_queries_total`, `llm_requests_total`, etc.
- URL path normalization is applied for cardinality control (e.g. `/items/123` → `/items/{id}`)
- Sampling: 100% in development, 10% in production

### Frontend Structure (`frontend/src/`)

- **app/**: Next.js App Router pages — `dashboard/`, `login/`, `signup/`, `onboarding/`, `demo/`, `[slug]/` (dynamic clinic routes), plus `/api/*` server-side routes
- **lib/api/**: Typed API client modules per domain (`appointments.ts`, `patients.ts`, `voice.ts`, `pims.ts`, etc.)
- **lib/env.ts**: Type-safe env vars; `getApiUrl()` switches between `NEXT_PUBLIC_API_URL` (client-side) and `SERVER_API_URL` (server-side inside Docker)
- **components/**: Shared UI — `Chatbot.tsx`, `ErrorBoundary.tsx`, dashboard-specific components

### Testing

```bash
cd backend
uv run pytest tests/adapters/       # PIMS adapter tests
uv run pytest tests/api/v1/         # Endpoint tests
uv run pytest tests/services/       # Service tests
uv run pytest -x -v                 # Stop on first failure, verbose
```

Key patterns in `tests/conftest.py`:
- Each test runs in a transaction that's rolled back on teardown (true isolation)
- `AsyncClient` is set up with `get_db` dependency override pointing to the test session
- Rate limiting is disabled via a context manager fixture

## Code Style

### Python

- Type hints required on all functions
- snake_case for files/functions/variables, PascalCase for classes
- Ruff linting (88 char lines, double quotes)
- SQLAlchemy 2.0 style (not legacy 1.x)

### TypeScript/React

- Strict TypeScript, avoid `any` (use `unknown`)
- Server Components by default, `'use client'` only when needed
- Functional components with hooks
- Tailwind CSS utilities for styling

## Pre-commit Hooks

Pre-commit runs Ruff (lint + format) and ty (type check) automatically. Install with:

```bash
cd backend
uv run pre-commit install
```

Always run before committing to fix linting errors:

```bash
uv run pre-commit run --all-files
```

## API Documentation

When backend is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
