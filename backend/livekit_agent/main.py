"""
LiveKit Agent Entry Point

Runs the voice AI agent worker that handles real-time voice interactions.

Usage:
    python -m livekit_agent.main dev     # Development mode
    python -m livekit_agent.main start   # Production mode
"""

import json
import logging
import os
from datetime import UTC, datetime

from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import assemblyai, cartesia, openai, silero
from sqlalchemy import select

from livekit_agent.cache import (
    clear_call_state,
    get_clinic_for_phone,
    warm_phone_mapping,
)
from livekit_agent.config import agent_settings
from livekit_agent.db import SessionLocal, warm_connection_pool
from livekit_agent.prompts import get_greeting, get_system_prompt
from livekit_agent.telemetry import record_call_end, record_call_start

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Enable debug logging for livekit components
logging.getLogger("livekit").setLevel(logging.DEBUG)
logging.getLogger("livekit.agents").setLevel(logging.DEBUG)
logging.getLogger("livekit.plugins").setLevel(logging.DEBUG)
logging.getLogger("livekit.plugins.openai").setLevel(logging.DEBUG)
logging.getLogger("openai").setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)

# Flag to track if startup has run
_startup_done = False


async def ensure_startup():
    """Ensure startup tasks run once."""
    global _startup_done
    if _startup_done:
        return

    logger.info("Starting LiveKit agent worker...")
    try:
        await warm_connection_pool()
        await warm_phone_mapping()
        logger.info("Agent worker initialized successfully")
        _startup_done = True
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


async def get_clinic_by_id(clinic_id: str) -> dict | None:
    """Load clinic data from database."""
    from app.models.clinic import Clinic

    async with SessionLocal() as db:
        result = await db.execute(
            select(Clinic).where(
                Clinic.id == clinic_id,
                Clinic.deleted_at.is_(None),
            )
        )
        clinic = result.scalar_one_or_none()

        if not clinic:
            return None

        # Build full address from components
        address_parts = [clinic.address_line1]
        if clinic.address_line2:
            address_parts.append(clinic.address_line2)
        address = ", ".join(filter(None, address_parts)) or None

        return {
            "id": str(clinic.id),
            "name": clinic.name,
            "slug": clinic.slug,
            "address": address,
            "city": clinic.city,
            "state": clinic.state,
            "postal_code": clinic.postal_code,
            "phone": clinic.phone,
            "email": clinic.email,
            "business_hours": clinic.business_hours,
            "voice_enabled": clinic.voice_enabled,
            "voice_settings": clinic.voice_settings,
            "twilio_phone_number": clinic.twilio_phone_number,
            "emergency_phone": clinic.emergency_phone,
            "emergency_keywords": clinic.emergency_keywords,
        }


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for handling voice sessions.

    This is called when a new room is created for a voice call.
    """
    # Ensure startup has run
    await ensure_startup()

    logger.info(f"New voice session: room={ctx.room.name}")

    # Connect to the room
    await ctx.connect()
    logger.info("Connected to room, waiting for participant...")

    # Wait for a human participant to join
    participant = await ctx.wait_for_participant()
    logger.info(f"Participant joined: {participant.identity}")

    # Parse room metadata for call context
    room_metadata = json.loads(ctx.room.metadata or "{}")
    channel = room_metadata.get("channel", "web_voice")

    logger.debug(f"Room metadata: {room_metadata}")

    # Determine clinic from channel type
    if channel == "phone":
        # Phone call - look up clinic by dialed number
        dialed_number = room_metadata.get("dialed_number")
        if not dialed_number:
            logger.error("No dialed number in room metadata")
            return

        clinic_id = await get_clinic_for_phone(dialed_number)
        if not clinic_id:
            logger.error(f"No clinic found for phone: {dialed_number}")
            return
    else:
        # Web voice widget - clinic_id provided in metadata
        clinic_id = room_metadata.get("clinic_id")

        # Fallback: parse clinic_id from room name (format: voice-{clinic_id}-{uuid})
        if not clinic_id and ctx.room.name.startswith("voice-"):
            parts = ctx.room.name.split("-")
            if len(parts) >= 6:
                clinic_id = "-".join(parts[1:6])
                logger.info(f"Parsed clinic_id from room name: {clinic_id}")

        if not clinic_id:
            logger.error("No clinic_id in room metadata for web_voice")
            return

    # Load clinic data
    clinic = await get_clinic_by_id(clinic_id)
    if not clinic:
        logger.error(f"Clinic not found: {clinic_id}")
        return

    if not clinic.get("voice_enabled"):
        logger.warning(f"Voice not enabled for clinic: {clinic_id}")
        return

    logger.info(
        f"Loaded clinic: {clinic['name']} (voice_enabled={clinic['voice_enabled']})"
    )

    # Record call start
    record_call_start(clinic_id, channel)
    call_start_time = datetime.now(UTC)

    # Format business hours for prompt
    hours = clinic.get("business_hours", {})
    hours_str = (
        ", ".join(f"{day.capitalize()}: {h}" for day, h in hours.items() if h)
        if hours
        else "Please ask staff for hours"
    )

    # Generate system prompt
    system_prompt = get_system_prompt(
        clinic_name=clinic["name"],
        business_hours=hours_str,
        address=clinic.get("address"),
        emergency_phone=clinic.get("emergency_phone"),
        emergency_keywords=clinic.get("emergency_keywords"),
    )

    # Get greeting
    greeting = get_greeting(
        clinic["name"],
        clinic.get("voice_settings", {}).get("greeting_message"),
    )

    logger.info("Initializing AI providers with explicit API keys...")

    # Initialize providers with explicit API keys
    # Using plugin classes directly for better control
    stt = assemblyai.STT(
        api_key=agent_settings.assemblyai_api_key.get_secret_value(),
    )
    logger.info("  - STT: AssemblyAI initialized")

    logger.info(
        f"  - LLM: Initializing DeepSeek with base_url={agent_settings.deepseek_base_url}"
    )
    llm = openai.LLM(
        model=agent_settings.deepseek_model,
        api_key=agent_settings.deepseek_api_key.get_secret_value(),
        base_url=agent_settings.deepseek_base_url,
    )
    logger.info(
        f"  - LLM: DeepSeek {agent_settings.deepseek_model} initialized successfully"
    )

    tts = cartesia.TTS(
        api_key=agent_settings.cartesia_api_key.get_secret_value(),
        voice=agent_settings.cartesia_voice_id,
    )
    logger.info(
        f"  - TTS: Cartesia initialized (voice: {agent_settings.cartesia_voice_id})"
    )

    vad = silero.VAD.load()
    logger.info("  - VAD: Silero initialized")

    # Create agent with instructions
    agent = Agent(instructions=system_prompt)

    # Create session with AI providers
    session = AgentSession(
        stt=stt,
        llm=llm,
        tts=tts,
        vad=vad,
    )

    logger.info(f"Starting voice session for clinic {clinic['name']}")

    # Register cleanup callback for when session ends
    async def on_shutdown():
        duration = (datetime.now(UTC) - call_start_time).total_seconds()
        record_call_end(clinic_id, channel, duration)
        await clear_call_state(ctx.room.name)
        logger.info(
            f"Voice session ended: clinic={clinic['name']}, duration={duration:.1f}s"
        )

    ctx.add_shutdown_callback(on_shutdown)

    # Start the session
    await session.start(
        agent=agent,
        room=ctx.room,
    )

    logger.info("Session started, speaking greeting...")
    logger.info(f"Greeting text: {greeting}")

    # Speak the greeting directly using TTS (no LLM needed for greeting)
    try:
        logger.info("Calling session.say() for greeting...")
        await session.say(
            greeting,
            allow_interruptions=True,
            add_to_chat_ctx=True,  # Add to context so LLM knows what was said
        )
        logger.info(f"Greeting spoken for clinic {clinic['name']}")
    except Exception as e:
        logger.error(f"session.say() failed: {e}")
        import traceback

        logger.error(traceback.format_exc())


if __name__ == "__main__":
    # Set API keys as environment variables (some plugins may read from env)
    os.environ["ASSEMBLYAI_API_KEY"] = (
        agent_settings.assemblyai_api_key.get_secret_value()
    )
    os.environ["CARTESIA_API_KEY"] = agent_settings.cartesia_api_key.get_secret_value()
    os.environ["OPENAI_API_KEY"] = agent_settings.deepseek_api_key.get_secret_value()

    logger.info("Starting LiveKit agent worker...")
    logger.info(f"  - LiveKit URL: {agent_settings.livekit_url}")
    logger.info(f"  - LiveKit API Key: {agent_settings.livekit_api_key[:8]}...")

    # Run the agent worker using CLI
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=agent_settings.livekit_api_key,
            api_secret=agent_settings.livekit_api_secret.get_secret_value(),
            ws_url=agent_settings.livekit_url,
        )
    )
