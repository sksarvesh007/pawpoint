"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai_chat,
    analytics,
    appointments,
    auth,
    calls,
    chats,
    clinic_ai,
    clinic_ai_streaming,
    clinics,
    demo_chat,
    outbound_calls,
    patients,
    pims,
    providers,
    recordings,
    voice,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(clinics.router, prefix="/clinics", tags=["clinics"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(
    appointments.router, prefix="/appointments", tags=["appointments"]
)
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
api_router.include_router(pims.router, prefix="/pims", tags=["pims"])

# Legacy endpoint (for backward compatibility)
api_router.include_router(ai_chat.router)  # /ai/chat/message

# Demo endpoint MUST be registered BEFORE wildcard clinic routes
api_router.include_router(demo_chat.router)  # /demo-clinic/chat/stream

# NEW: Clinic-specific AI endpoints (recommended)
api_router.include_router(clinic_ai.router, tags=["Clinic AI"])  # /{clinic-slug}/chat
api_router.include_router(
    clinic_ai_streaming.router, tags=["Clinic AI"]
)  # /{clinic-slug}/chat/stream

api_router.include_router(
    outbound_calls.router, prefix="/outbound-calls", tags=["outbound-calls"]
)
api_router.include_router(recordings.router, prefix="/recordings", tags=["recordings"])

# Voice endpoints (LiveKit integration)
api_router.include_router(voice.router, tags=["Voice"])  # /{clinic-slug}/voice/*
