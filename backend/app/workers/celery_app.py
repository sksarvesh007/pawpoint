"""Celery application configuration.

Uses Redis as broker and result backend. Configured for JSON serialization
and UTC timezone with task retries.
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# Use Redis URL from settings, fallback to localhost
broker_url = settings.redis_url or "redis://localhost:6379/0"

app = Celery(
    "pawpoint",
    broker=broker_url,
    backend=broker_url,
    include=["app.workers.tasks"],
)

app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Reliability
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    # Default retry policy
    task_default_retry_delay=60,
    task_max_retries=3,
    # Result expiry (24 hours)
    result_expires=86400,
    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-stale-sessions": {
            "task": "app.workers.tasks.cleanup_stale_sessions",
            "schedule": crontab(minute="*/15"),  # Every 15 minutes
        },
        "sync-patients-every-6h": {
            "task": "app.workers.tasks.sync_all_clinics_patients",
            "schedule": crontab(hour="*/6", minute="0"),
        },
        "sync-appointments-every-15m": {
            "task": "app.workers.tasks.sync_all_clinics_appointments",
            "schedule": crontab(minute="*/15"),
        },
    },
)
