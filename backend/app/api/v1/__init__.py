"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import analytics, auth, calls, clinics

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(clinics.router, prefix="/clinics", tags=["clinics"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
