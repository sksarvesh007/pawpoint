# PawPoint Backend

Backend service for PawPoint, providing APIs for pet profiles, appointments, and user management.

## Tech Stack
- **Framework:** FastAPI
- **Package Manager:** uv
- **Database:** PostgreSQL (planned)

## Getting Started

### Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) installed

### Environment Setup
**Important:** You must create a `.env` file before running the application.

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Update `.env` with your configuration (if needed).

### Running Locally
```bash
# Install dependencies
uv sync

# Run development server
uv run fastapi dev
```

### Running with Docker
```bash
# Start backend service
docker compose up -d backend
```

## Testing
```bash
# Run tests
uv run pytest
```
