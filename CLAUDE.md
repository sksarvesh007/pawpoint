# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PawPoint is an AI-powered veterinary clinic management platform with a Python FastAPI backend and Next.js frontend. Key features include appointments, patient records, PIMS (Practice Information Management System) integration, and AI-powered voice interactions.

## Tech Stack

**Backend**: Python 3.13+, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, UV package manager
**Frontend**: Next.js 16.1.3, React 19.2.3, TypeScript, Tailwind CSS 4, Bun
**Observability**: OpenTelemetry, Prometheus, Grafana
**Background Jobs**: Celery + Redis

## Common Commands

### Backend

```bash
cd backend
uv sync                              # Install dependencies
PYTHONPATH=. uv run fastapi dev app/main.py  # Run dev server (port 8000)
uv run pytest                        # Run all tests
uv run pytest tests/test_api/test_health.py  # Run specific test file
uv run ruff check . --fix            # Lint and auto-fix
uv run ruff format .                 # Format code
uv run ty check                      # Type check
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
docker compose up                    # Start all services
docker compose up backend            # Start backend only
# Grafana: localhost:3001 (admin/admin), Prometheus: localhost:9090
```

## Architecture

### Backend Layers (`backend/app/`)

- **api/v1/endpoints/**: HTTP handlers - keep thin, delegate to services
- **services/**: Business logic (currently being built out)
- **models/**: SQLAlchemy ORM models with mixins (UUID, Timestamp, SoftDelete, PIMSSync)
- **schemas/**: Pydantic request/response validation
- **adapters/pims/**: External PIMS integrations (ezyVet, Vetspire) via adapter pattern
- **core/**: Config, security, logging, telemetry

### Frontend Structure (`frontend/src/`)

- **app/**: Next.js App Router pages and layouts
- **lib/**: Shared utilities (e.g., type-safe env vars in `env.ts`)
now
### Key Design Patterns

- **Dependency Injection**: FastAPI `Depends()` for sessions, auth, services
- **Mixin-based Models**: Inherit `TimestampMixin`, `SoftDeleteMixin`, `PIMSSyncMixin`
- **Async Throughout**: All database and HTTP operations use async/await
- **PIMS Adapter Factory**: Dynamic provider selection via `IPIMSAdapter` interface

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

## API Documentation

When backend is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
