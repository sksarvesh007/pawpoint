#!/usr/bin/env python3
"""
Test script to verify each voice AI provider works correctly.

Usage:
    cd backend
    PYTHONPATH=. uv run python scripts/test_voice_providers.py
"""

import asyncio
import os
import sys

import aiohttp

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from livekit_agent.config import agent_settings


def print_header(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def print_success(msg: str):
    print(f"✅ {msg}")


def print_error(msg: str):
    print(f"❌ {msg}")


def print_info(msg: str):
    print(f"ℹ️  {msg}")


async def test_config():
    """Test that configuration loads correctly."""
    print_header("1. Testing Configuration")

    try:
        print_info(f"LiveKit URL: {agent_settings.livekit_url}")
        print_info(f"LiveKit API Key: {agent_settings.livekit_api_key[:10]}...")
        print_info(f"Database URL: {agent_settings.database_url[:50]}...")
        print_info(f"Cartesia Voice ID: {agent_settings.cartesia_voice_id}")

        # Check API keys are set
        assemblyai_key = agent_settings.assemblyai_api_key.get_secret_value()
        google_key = agent_settings.google_api_key.get_secret_value()
        cartesia_key = agent_settings.cartesia_api_key.get_secret_value()

        print_info(f"AssemblyAI API Key: {assemblyai_key[:10]}...")
        print_info(f"Google API Key: {google_key[:10]}...")
        print_info(f"Cartesia API Key: {cartesia_key[:10]}...")

        print_success("Configuration loaded successfully")
        return True
    except Exception as e:
        print_error(f"Configuration error: {e}")
        return False


async def test_silero_vad():
    """Test Silero VAD loads correctly."""
    print_header("2. Testing Silero VAD")

    try:
        from livekit.plugins import silero

        print_info("Loading Silero VAD model...")
        vad = silero.VAD.load()
        print_success(f"Silero VAD loaded: {type(vad)}")
        return True
    except Exception as e:
        print_error(f"Silero VAD error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_assemblyai_stt():
    """Test AssemblyAI STT initialization."""
    print_header("3. Testing AssemblyAI STT")

    try:
        from livekit.plugins import assemblyai

        api_key = agent_settings.assemblyai_api_key.get_secret_value()
        print_info(f"Initializing with API key: {api_key[:10]}...")

        stt = assemblyai.STT(api_key=api_key)
        print_success(f"AssemblyAI STT initialized: {type(stt)}")

        # Try to get capabilities
        if hasattr(stt, "capabilities"):
            print_info(f"Capabilities: {stt.capabilities}")

        return True
    except Exception as e:
        print_error(f"AssemblyAI STT error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_deepseek_llm():
    """Test DeepSeek LLM using direct API call."""
    print_header("4. Testing DeepSeek LLM")

    try:
        api_key = agent_settings.deepseek_api_key.get_secret_value()
        base_url = agent_settings.deepseek_base_url
        model = agent_settings.deepseek_model

        print_info(f"Testing with API key: {api_key[:10]}...")
        print_info(f"Base URL: {base_url}")
        print_info(f"Model: {model}")

        # Test DeepSeek API (OpenAI-compatible)
        url = f"{base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Say hello in one word."}],
            "max_tokens": 50,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    text = (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )
                    print_success(f"DeepSeek API response: {text.strip()[:100]}")
                    return True
                else:
                    error_text = await resp.text()
                    print_error(f"DeepSeek API error {resp.status}: {error_text[:200]}")
                    return False
    except Exception as e:
        print_error(f"DeepSeek LLM error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_cartesia_tts():
    """Test Cartesia TTS using direct API call."""
    print_header("5. Testing Cartesia TTS")

    try:
        api_key = agent_settings.cartesia_api_key.get_secret_value()
        voice_id = agent_settings.cartesia_voice_id

        print_info(f"Testing with API key: {api_key[:10]}...")
        print_info(f"Voice ID: {voice_id}")

        # Test Cartesia API directly since LiveKit plugin needs job context
        url = "https://api.cartesia.ai/tts/bytes"

        headers = {
            "X-API-Key": api_key,
            "Cartesia-Version": "2024-06-10",
            "Content-Type": "application/json",
        }

        payload = {
            "model_id": "sonic-2",
            "transcript": "Hello, this is a test.",
            "voice": {
                "mode": "id",
                "id": voice_id,
            },
            "output_format": {
                "container": "raw",
                "encoding": "pcm_s16le",
                "sample_rate": 24000,
            },
        }

        print_info("Testing speech synthesis...")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    audio_data = await resp.read()
                    print_success(
                        f"Cartesia TTS synthesized {len(audio_data)} bytes of audio"
                    )
                    return True
                else:
                    error_text = await resp.text()
                    print_error(f"Cartesia API error {resp.status}: {error_text[:200]}")
                    return False
    except Exception as e:
        print_error(f"Cartesia TTS error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_livekit_connection():
    """Test LiveKit server connection."""
    print_header("6. Testing LiveKit Connection")

    try:
        from livekit import api

        livekit_api = api.LiveKitAPI(
            url=agent_settings.livekit_url.replace("ws://", "http://").replace(
                "wss://", "https://"
            ),
            api_key=agent_settings.livekit_api_key,
            api_secret=agent_settings.livekit_api_secret.get_secret_value(),
        )

        print_info("Listing rooms...")
        rooms = await livekit_api.room.list_rooms(api.ListRoomsRequest())
        print_success(f"Connected to LiveKit. Found {len(rooms.rooms)} active rooms.")

        for room in rooms.rooms:
            print_info(f"  - Room: {room.name} ({room.num_participants} participants)")

        await livekit_api.aclose()
        return True
    except Exception as e:
        print_error(f"LiveKit connection error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    print("\n" + "=" * 60)
    print("  VOICE AI PROVIDER TEST SUITE")
    print("=" * 60)

    results = {}

    # Run all tests
    results["config"] = await test_config()
    results["silero_vad"] = await test_silero_vad()
    results["assemblyai_stt"] = await test_assemblyai_stt()
    results["deepseek_llm"] = await test_deepseek_llm()
    results["cartesia_tts"] = await test_cartesia_tts()
    results["livekit"] = await test_livekit_connection()

    # Summary
    print_header("TEST SUMMARY")

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print_success("All tests passed! Voice AI providers are working correctly.")
    else:
        print_error("Some tests failed. Check the errors above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
