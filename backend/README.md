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
| **PostgreSQL** | 16+ | Database (planned) |
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

### 4. Run Development Server

```bash
PYTHONPATH=. uv run fastapi dev app/main.py
```

API available at [http://localhost:8000](http://localhost:8000)

Interactive docs at [http://localhost:8000/docs](http://localhost:8000/docs)

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
│       └── migrations/                     # Alembic migrations
│
├── tests/                                  # Test suite
│   ├── conftest.py                         # Pytest fixtures
│   ├── test_api/                           # API endpoint tests
│   ├── test_services/                      # Service layer tests
│   └── test_adapters/                      # PIMS adapter tests
│
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
| `DATABASE_URL` | PostgreSQL connection string | Optional |
| `REDIS_URL` | Redis connection string | Optional |

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
- [uv Documentation](https://docs.astral.sh/uv/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pydantic Documentation](https://docs.pydantic.dev)
