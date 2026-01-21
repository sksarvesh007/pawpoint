# PawPoint Backend

Backend service for PawPoint - an AI-powered veterinary engagement platform providing APIs for pet profiles, appointments, PIMS integration, and user management.

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | ≥0.115.11 | High-performance async web framework |
| **Python** | 3.13+ | Runtime |
| **uv** | Latest | Fast Python package manager |
| **Ruff** | ≥0.14.13 | Linting & formatting |
| **ty** | ≥0.0.12 | Type checking |
| **PostgreSQL** | 16+ | Database |
| **Alembic** | ≥1.13.0 | Database migrations |
| **Docker** | Latest | Containerization |

### Key Features
- ⚡ **Async/await** support throughout
- 🔒 **JWT authentication** with secure password hashing
- 🏥 **PIMS integration** (ezyVet, Vetspire)
- 📊 **Pydantic v2** for request/response validation
- 🧪 **Pytest** for testing
- 🐳 **Docker** ready with multi-stage builds

---

## Prerequisites

- **Python** 3.13+
- **[uv](https://docs.astral.sh/uv/)** installed globally
- **Docker** (optional, for containerized development)

---

## Getting Started

### 1. Navigate to Backend

```bash
cd backend
```

### 2. Environment Setup

The application loads from `dev.env` or `prod.env` based on `APP_ENV`:

```bash
# Development (default)
# Uses dev.env automatically

# Production
export APP_ENV=production
# Uses prod.env
```

Configure your settings in `dev.env`:

```env
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secure-secret-key
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Database Setup

Start PostgreSQL via Docker:

```bash
# From project root
docker compose up -d db
```

Run database migrations:

```bash
uv run alembic upgrade head
```

### 5. Run Development Server

```bash
PYTHONPATH=. uv run fastapi dev app/main.py
```

API available at [http://localhost:8000](http://localhost:8000)

Interactive docs at [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Database Migrations (Alembic)

Alembic manages database schema changes. Migration files are in `alembic/versions/`.

### Common Commands

| Command | Description |
|---------|-------------|
| `uv run alembic upgrade head` | Apply all pending migrations |
| `uv run alembic downgrade -1` | Rollback last migration |
| `uv run alembic revision --autogenerate -m "message"` | Generate new migration |
| `uv run alembic history` | Show migration history |
| `uv run alembic current` | Show current revision |

### Creating a New Migration

After modifying models in `app/models/`:

```bash
# Generate migration (auto-detects changes)
uv run alembic revision --autogenerate -m "add_new_field_to_patients"

# Review the generated file in alembic/versions/
# Then apply it
uv run alembic upgrade head
```

### Migration Best Practices

- Always review auto-generated migrations before applying
- Use descriptive migration messages (e.g., "add_email_verified_to_users")
- Test migrations on a copy of production data before deploying
- Never edit migrations that have been applied to production

---

## Available Commands

| Command | Description |
|---------|-------------|
| `uv sync` | Install/sync dependencies |
| `uv run fastapi dev` | Start development server (hot reload) |
| `uv run fastapi run` | Start production server |
| `uv run pytest` | Run test suite |
| `uv run ruff check .` | Run linter |
| `uv run ruff format .` | Format code |
| `uv run ty check` | Run type checker |
| `uv run alembic upgrade head` | Apply database migrations |
| `uv run alembic revision --autogenerate -m "msg"` | Generate migration |

---

## Docker

### Using Docker Compose (Recommended)

```bash
# From project root
docker compose up backend

# Rebuild after changes
docker compose up --build backend

# Stop services
docker compose down
```

### Standalone Docker

```bash
# Build image
docker build -t pawpoint-backend .

# Run container
docker run -p 8000:8000 --env-file .env pawpoint-backend
```

---

## Directory Structure

```
backend/
│
├── app/                                    # Main application package
│   ├── main.py                             # FastAPI entry point, lifespan, middleware
│   │
│   ├── core/                               # Core configuration & utilities
│   │   ├── config.py                       # Pydantic settings (env vars)
│   │   ├── security.py                     # JWT tokens, password hashing
│   │   └── exceptions.py                   # Custom exception classes
│   │
│   ├── api/                                # API layer (HTTP handling only)
│   │   ├── deps.py                         # Dependency injection (auth, db, redis)
│   │   └── v1/                             # API version 1
│   │       ├── router.py                   # Aggregates all endpoint routers
│   │       └── endpoints/                  # Route handlers by domain
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
│   │   ├── base.py                         # Base model, mixins (UUID, timestamps)
│   │   ├── user.py
│   │   ├── clinic.py
│   │   ├── patient.py
│   │   ├── provider.py
│   │   ├── appointment.py
│   │   └── call_log.py
│   │
│   ├── schemas/                            # Pydantic schemas (request/response)
│   │   ├── auth.py                         # Token, login schemas
│   │   ├── user.py                         # UserCreate, UserUpdate, UserResponse
│   │   ├── clinic.py
│   │   ├── patient.py
│   │   ├── provider.py
│   │   └── appointment.py
│   │
│   ├── services/                           # Business logic layer
│   │   ├── user.py                         # User service
│   │   ├── clinic.py
│   │   ├── patient.py
│   │   ├── appointment.py
│   │   └── pims_sync.py                    # PIMS synchronization logic
│   │
│   ├── adapters/                           # External service integrations
│   │   └── pims/                           # PIMS adapters
│   │       ├── base.py                     # IPIMSAdapter interface + factory
│   │       ├── ezyvet.py                   # ezyVet adapter (REST, OAuth2)
│   │       └── vetspire.py                 # Vetspire adapter (GraphQL)
│   │
│   ├── workers/                            # Background tasks (Celery/ARQ)
│   │   └── pims_sync.py                    # Scheduled sync tasks
│   │
│   └── db/                                 # Database configuration
│       └── __init__.py                     # Async engine, session factory
│
├── alembic/                                # Database migrations
│   ├── env.py                              # Migration environment config
│   ├── script.py.mako                      # Migration template
│   └── versions/                           # Migration files
│       └── 20260121_initial_schema.py      # Initial migration
│
├── tests/                                  # Test suite
│   ├── conftest.py                         # Pytest fixtures
│   ├── test_api/                           # API endpoint tests
│   ├── test_services/                      # Service layer tests
│   └── test_adapters/                      # PIMS adapter tests
│
├── alembic.ini                             # Alembic configuration
├── pyproject.toml                          # Dependencies, tool config
├── Dockerfile                              # Multi-stage container build
├── .env.example                            # Environment template
└── README.md                               # This file
```

---

## Architecture

### Layer Responsibilities

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **API** | `app/api/` | HTTP handling, validation, routing |
| **Services** | `app/services/` | Business logic, independent of HTTP |
| **Adapters** | `app/adapters/` | External integrations (PIMS, Twilio) |
| **Models** | `app/models/` | Database entities (no business logic) |
| **Schemas** | `app/schemas/` | Request/response validation |
| **Core** | `app/core/` | Config, security, exceptions |

### Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app with lifespan, CORS, routers |
| `app/core/config.py` | Pydantic settings from `.env` |
| `app/api/deps.py` | Dependency injection (auth, db sessions) |
| `app/adapters/pims/base.py` | PIMS adapter interface + factory |
| `app/models/base.py` | SQLAlchemy mixins (UUID, timestamps) |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENV` | Environment (development/production) | `development` |
| `DEBUG` | Enable debug mode | `true` |
| `SECRET_KEY` | JWT signing key | Required |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `ALLOWED_ORIGINS` | CORS origins (comma-separated) | `http://localhost:3000` |
| `DATABASE_URL` | PostgreSQL async connection string | Required |
| `REDIS_URL` | Redis connection string | Optional |

### Database URL Format

```bash
# Inside Docker (backend connects to db service)
DATABASE_URL=postgresql+asyncpg://pawpoint:localdevonly@db:5432/pawpoint

# Outside Docker (connect to docker db on mapped port)
DATABASE_URL=postgresql+asyncpg://pawpoint:localdevonly@localhost:5434/pawpoint
```

### Recreating the Database

If you need to start fresh (reset all data) or if database credentials changed:

```bash
# From project root - this removes all data!
docker compose down -v              # Stop containers and DELETE database volume
docker compose up -d db             # Start fresh database
sleep 5                             # Wait for database to initialize
cd backend
uv run alembic upgrade head         # Re-apply all migrations
```

**What each command does:**
- `docker compose down -v` - Stops all containers and removes volumes (deletes all database data)
- `docker compose up -d db` - Starts only the PostgreSQL container in background
- `alembic upgrade head` - Creates all tables by running migrations

---

## Code Quality

### Linting with Ruff

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix

# Format code
uv run ruff format .
```

### Type Checking with ty

```bash
uv run ty check
```

### Pre-commit Hooks

```bash
# Install hooks
uv run pre-commit install

# Run manually
uv run pre-commit run --all-files
```

---

## Testing

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=app

# Specific test file
uv run pytest tests/test_api/test_health.py
```

---

## API Documentation

When running locally, access interactive API docs:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Troubleshooting

### Port 8000 already in use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Virtual environment issues

```bash
# Recreate venv
rm -rf .venv
uv sync
```

### Module not found errors

```bash
# Ensure you're running via uv
uv run python -c "import app"
```

---

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Alembic Documentation](https://alembic.sqlalchemy.org)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pydantic Documentation](https://docs.pydantic.dev)
