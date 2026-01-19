# PawPoint - GitHub Copilot Instructions

## Project Overview

PawPoint is a veterinary clinic management application with a Python FastAPI backend and Next.js frontend.

## Tech Stack

### Backend
- **Language**: Python 3.13+
- **Framework**: FastAPI with SQLAlchemy ORM
- **Package Manager**: UV
- **Database**: PostgreSQL (via asyncpg)
- **Testing**: pytest

### Frontend
- **Framework**: Next.js 16.1.3 with App Router
- **Runtime**: Bun
- **Language**: TypeScript
- **UI**: React 19.2.3
- **Styling**: Tailwind CSS 4
- **Compiler**: React Compiler enabled (babel-plugin-react-compiler)

## Build and Test Commands

### Backend
```bash
cd backend
# Install dependencies
uv sync
# Run tests
uv run pytest
# Run linting
uv run ruff check .
# Format code
uv run ruff format .
```

### Frontend
```bash
cd frontend
# Install dependencies
bun install
# Run development server
bun run dev
# Build production
bun run build
# Run linting
bun run lint
# Start production server
bun run start
```

## Code Style and Conventions

### Python (Backend)
- Follow PEP 8 conventions
- Use type hints for all function parameters and return values
- Use snake_case for files, functions, and variables
- Use PascalCase for classes
- Use UPPER_SNAKE_CASE for constants
- Prefer async/await patterns for I/O operations
- Keep business logic in `services/` layer, separate from API endpoints
- Use Pydantic models for request/response validation
- Always use dependency injection for database sessions and external services

### TypeScript/React (Frontend)
- Use TypeScript for all new files
- Prefer functional components with hooks
- Use kebab-case for URLs and routes
- Use camelCase for variables and functions
- Use PascalCase for React components and TypeScript types/interfaces
- Prefer named exports over default exports
- Use React Server Components by default (Next.js App Router)
- Follow Next.js 16 App Router conventions

## Architecture Guidelines

### Backend Structure
- **API Layer** (`app/api/`): HTTP handling, validation, routing only
- **Services** (`app/services/`): Business logic, independent of HTTP
- **Models** (`app/models/`): SQLAlchemy ORM models
- **Schemas** (`app/schemas/`): Pydantic schemas for validation
- **Adapters** (`app/adapters/`): External service integrations
- **Core** (`app/core/`): Configuration, security, shared utilities

### Frontend Structure
- Use Next.js App Router structure (`app/` directory)
- Keep components modular and reusable
- Use Server Components by default, mark Client Components with 'use client'
- Follow Next.js file conventions (page.tsx, layout.tsx, loading.tsx, error.tsx)

## Security Best Practices
- Never commit secrets or API keys to the repository
- Always validate and sanitize user input
- Use environment variables for configuration
- Implement proper authentication and authorization checks
- Follow OWASP security guidelines

## Testing Guidelines
- Write tests for new features and bug fixes
- Backend: Use pytest with fixtures for database setup
- Frontend: Follow existing test patterns if tests are added
- Aim for meaningful test coverage, not just high percentages

## Documentation
- Update README files when making significant changes
- Document API endpoints with clear descriptions
- Add docstrings to Python functions and classes
- Use JSDoc comments for complex TypeScript functions
