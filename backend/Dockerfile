# =============================================================================
# PawPoint Backend Dockerfile
# Multi-stage build for development and production
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Base image with uv package manager
# -----------------------------------------------------------------------------
FROM python:3.13-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# -----------------------------------------------------------------------------
# Stage 2: Development image
# Includes dev dependencies, hot reload, and debugging tools
# -----------------------------------------------------------------------------
FROM base AS development

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install all dependencies (including dev)
RUN uv sync --frozen

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Development command with hot reload
CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0", "--port", "8000"]

# -----------------------------------------------------------------------------
# Stage 3: Production build
# Only production dependencies, optimized for size and security
# -----------------------------------------------------------------------------
FROM base AS production

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install only production dependencies (no dev group)
RUN uv sync --frozen --no-dev

# Copy application code
COPY --chown=appuser:appgroup . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Production entrypoint (runs migrations then starts server)
CMD ["./entrypoint.sh"]
