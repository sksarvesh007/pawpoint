# =============================================================================
# PawPoint Frontend Dockerfile (Next.js + Bun)
# =============================================================================
# Multi-stage build for development and production
# Development: Hot reload with mounted volumes
# Production: Optimized static build
# =============================================================================

FROM oven/bun:1 AS base
WORKDIR /app

# ---------------------------------------------------------------------------
# Dependencies stage
# ---------------------------------------------------------------------------
FROM base AS deps
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# ---------------------------------------------------------------------------
# Development stage (for docker-compose)
# ---------------------------------------------------------------------------
FROM base AS development
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Expose Next.js dev server port
EXPOSE 3000

# Start development server with hot reload
CMD ["bun", "run", "dev"]

# ---------------------------------------------------------------------------
# Production build stage
# ---------------------------------------------------------------------------
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build Next.js app
RUN bun run build

# ---------------------------------------------------------------------------
# Production runtime stage
# ---------------------------------------------------------------------------
FROM base AS production
ENV NODE_ENV=production

# Copy built assets and dependencies
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["bun", "run", "server.js"]
