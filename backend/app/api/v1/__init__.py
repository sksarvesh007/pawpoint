"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai_chat,
    analytics,
    auth,
    calls,
    clinic_ai,
    clinic_ai_streaming,
    clinics,
    demo_chat,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(clinics.router, prefix="/clinics", tags=["clinics"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])

# Legacy endpoint (for backward compatibility)
api_router.include_router(ai_chat.router)  # /ai/chat/message

# Demo endpoint MUST be registered BEFORE wildcard clinic routes
api_router.include_router(demo_chat.router)  # /demo-clinic/chat/stream

# NEW: Clinic-specific AI endpoints (recommended)
api_router.include_router(clinic_ai.router, tags=["Clinic AI"])  # /{clinic-slug}/chat
api_router.include_router(
    clinic_ai_streaming.router, tags=["Clinic AI"]
)  # /{clinic-slug}/chat/stream
