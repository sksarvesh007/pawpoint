"""One-time script to enable voice for all existing clinics."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import update
from app.db import SessionLocal
from app.models.clinic import Clinic


async def enable_voice_for_all():
    """Enable voice for all existing clinics."""
    async with SessionLocal() as db:
        result = await db.execute(
            update(Clinic).values(voice_enabled=True)
        )
        await db.commit()
        print(f"Updated {result.rowcount} clinics - voice_enabled=True")


if __name__ == "__main__":
    asyncio.run(enable_voice_for_all())
