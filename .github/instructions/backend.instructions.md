---
applyTo: "backend/**/*.py"
---

# Backend Python Instructions

## Python Style
- Always use type hints for function parameters and return values
- Use snake_case for all Python identifiers (variables, functions, files)
- Use PascalCase for class names
- Use UPPER_SNAKE_CASE for constants
- Follow PEP 8 formatting guidelines

## FastAPI Patterns
- Use dependency injection via `Depends()` for database sessions and authentication
- Define route handlers in `app/api/v1/endpoints/`
- Keep route handlers thin - delegate business logic to service layer
- Use Pydantic schemas from `app/schemas/` for request/response validation
- Return proper HTTP status codes (use FastAPI's `status` module)

## Database and ORM
- Define SQLAlchemy models in `app/models/`
- Use async session management with `AsyncSession`
- Prefer async queries (`await session.execute()`)
- Use SQLAlchemy 2.0 style queries (not legacy 1.x style)
- Apply mixins from `app/models/base.py` (UUIDMixin, TimestampMixin, etc.)

## Service Layer
- Place all business logic in `app/services/`
- Services should not depend on FastAPI-specific types (no Request, Response)
- Services should accept database sessions as parameters
- Keep services focused on single responsibilities

## Error Handling
- Use custom exceptions from `app/core/exceptions.py`
- Let FastAPI exception handlers format error responses
- Provide meaningful error messages for debugging

## Testing
- Use pytest for all tests
- Place tests in `tests/` directory mirroring `app/` structure
- Use fixtures from `tests/conftest.py` for database setup
- Test service layer independently from API endpoints
- Mock external service calls (PIMS adapters, Twilio)

## Package Management
- Use UV for all dependency management
- Add dependencies to `pyproject.toml`
- Always check for security vulnerabilities before adding new dependencies
