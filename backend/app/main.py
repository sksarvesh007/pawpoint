"""PawPoint Backend - Main Application Entry Point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="PawPoint API",
    description="AI-powered veterinary engagement platform",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - health check."""
    return {"status": "healthy", "service": "pawpoint-api"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for deployment platforms."""
    return {"status": "ok"}
