# PawPoint Backend Directory Structure

> Enterprise-grade Python backend structure for FastAPI + SQLAlchemy

```
backend/
│
├── app/                                    # Main application package
│   ├── __init__.py                         # Package init with version
│   ├── main.py                             # FastAPI app entry point, lifespan, middleware
│   │
│   ├── core/                               # Core configuration & utilities
│   │   ├── __init__.py
│   │   ├── config.py                       # Pydantic settings (env vars)
│   │   ├── security.py                     # JWT tokens, password hashing
│   │   └── exceptions.py                   # Custom exception classes

│   │
│   ├── api/                                # API layer (HTTP handling only)
│   │   ├── __init__.py
│   │   ├── deps.py                         # Dependency injection (auth, db, redis)
│   │   └── v1/                             # API version 1
│   │       ├── __init__.py
│   │       ├── router.py                   # Aggregates all endpoint routers
│   │       └── endpoints/                  # Route handlers by domain
│   │           ├── __init__.py
│   │           ├── auth.py                 # Login, register, token refresh
│   │           ├── users.py                # User CRUD
│   │           ├── clinics.py              # Clinic management
│   │           ├── patients.py             # Patient (pet) management
│   │           ├── providers.py            # Veterinarian management
│   │           ├── appointments.py         # Appointment CRUD
│   │           ├── pims.py                 # PIMS connection & sync
│   │           ├── voice.py                # Twilio webhooks, call logs
│   │           └── health.py               # Health checks
│   │
│   ├── models/                             # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py                         # Base model, mixins (UUID, timestamps, soft delete)
│   │   ├── user.py
│   │   ├── clinic.py
│   │   ├── patient.py
│   │   ├── provider.py
│   │   ├── appointment.py
│   │   └── call_log.py
│   │
│   ├── schemas/                            # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── auth.py                         # Token, login schemas
│   │   ├── user.py                         # UserCreate, UserUpdate, UserResponse
│   │   ├── clinic.py
│   │   ├── patient.py
│   │   ├── provider.py
│   │   └── appointment.py
│   │
│   ├── services/                           # Business logic layer
│   │   ├── __init__.py
│   │   ├── user.py                         # User service
│   │   ├── clinic.py
│   │   ├── patient.py
│   │   ├── appointment.py
│   │   └── pims_sync.py                    # PIMS synchronization logic
│   │
│   ├── adapters/                           # External service integrations
│   │   ├── __init__.py
│   │   └── pims/                           # PIMS adapters
│   │       ├── __init__.py
│   │       ├── base.py                     # IPIMSAdapter interface + factory
│   │       ├── ezyvet.py                   # ezyVet adapter (REST, OAuth2)
│   │       └── vetspire.py                 # Vetspire adapter (GraphQL)
│   │
│   ├── workers/                            # Background tasks (Celery/ARQ)
│   │   ├── __init__.py
│   │   └── pims_sync.py                    # Scheduled sync tasks
│   │
│   └── db/                                 # Database configuration
│       ├── __init__.py                     # Engine, session factory
│       └── migrations/                     # Alembic migrations (optional location)
│
├── tests/                                  # Test suite
│   ├── __init__.py
│   ├── conftest.py                         # Pytest fixtures
│   ├── test_api/                           # API endpoint tests
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_health.py
│   │   └── test_appointments.py
│   ├── test_services/                      # Service layer tests
│   │   └── __init__.py
│   └── test_adapters/                      # PIMS adapter tests
│       └── __init__.py
│
├── alembic/                                # Database migrations
│   ├── env.py
│   ├── versions/                           # Migration files
│   └── alembic.ini
│
├── pyproject.toml                          # Dependencies, tool config (ruff, pytest, mypy)
├── Makefile                                # Dev commands (make dev, make test, make lint)
├── .env.example                            # Environment variables template
├── .gitignore
├── README.md
└── Dockerfile                              # Container build (optional)
```

---

## Layer Responsibilities

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **API** | `app/api/` | HTTP handling, validation, routing |
| **Services** | `app/services/` | Business logic, independent of HTTP |
| **Adapters** | `app/adapters/` | External integrations (PIMS, Twilio) |
| **Models** | `app/models/` | Database entities (no business logic) |
| **Schemas** | `app/schemas/` | Request/response validation |
| **Core** | `app/core/` | Config, security, exceptions |

---

## Key Files Explained

### `app/main.py`
- Creates FastAPI app with lifespan handler
- Configures CORS, middleware
- Includes all routers

### `app/core/config.py`
- Uses `pydantic-settings` to load from `.env`
- All secrets and config in one place

### `app/api/deps.py`
- `get_current_user()` - JWT validation
- `get_db()` - Database session
- `get_redis()` - Cache client

### `app/adapters/pims/base.py`
- `IPIMSAdapter` - Abstract interface all PIMS implement
- `PIMSAdapterFactory` - Creates adapter by type

### `app/models/base.py`
- `UUIDMixin` - UUID primary keys
- `TimestampMixin` - created_at, updated_at
- `SoftDeleteMixin` - deleted_at
- `PIMSSyncMixin` - pims_id, sync_status, last_synced_at

---

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | snake_case | `user_service.py` |
| Classes | PascalCase | `UserService` |
| Functions | snake_case | `get_user_by_id()` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Endpoints | kebab-case | `/api/v1/call-logs` |

---

## Dependencies to Add

```toml
# pyproject.toml
[project.dependencies]
fastapi = ">=0.109.0"
uvicorn = {extras = ["standard"], version = ">=0.27.0"}
pydantic = ">=2.5.0"
pydantic-settings = ">=2.1.0"
sqlalchemy = ">=2.0.25"
asyncpg = ">=0.29.0"
alembic = ">=1.13.0"
python-jose = {extras = ["cryptography"], version = ">=3.3.0"}
passlib = {extras = ["bcrypt"], version = ">=1.7.4"}
httpx = ">=0.26.0"
redis = ">=5.0.0"
```
