"""Model factory for creating LLM instances with provider routing.

This module provides a centralized factory for creating OpenAI and Gemini models
using the OpenAI Python client (Gemini via OpenAI-compatible API).
"""

from enum import Enum
from typing import Literal

from typing import Any

from app.core.config import settings


class ModelProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    GEMINI = "gemini"


class TaskType(str, Enum):
    """Task types for model routing."""

    VOICE = "voice"  # Real-time voice interactions
    APPOINTMENT_BOOKING = "appointment_booking"  # Complex scheduling logic
    PATIENT_RECORD = "patient_record"  # Patient data access/updates
    PIMS_INTEGRATION = "pims_integration"  # PIMS API calls
    FAQ = "faq"  # General clinic information
    COMPLEX_REASONING = "complex_reasoning"  # Multi-step reasoning tasks
    GENERAL = "general"  # Default task type


class ModelFactory:
    """Factory for creating model name strings for pydantic-ai.

    Provides:
    - Model name string generation in pydantic-ai format
    - Intelligent routing based on task type and channel
    - Support for both OpenAI and Gemini models
    """

    @classmethod
    def get_openai_model(cls, model_name: str | None = None) -> str:
        """Get OpenAI model name string.

        Args:
            model_name: Model name (e.g., "gpt-4o", "gpt-4o-mini")
                       Defaults to settings.llm_reasoning_model

        Returns:
            Model name string with openai: prefix

        Raises:
            ValueError: If OpenAI API key is not configured
        """
        if not settings.openai_api_key:
            raise ValueError(
                "OpenAI API key not configured. Set OPENAI_API_KEY in your .env file"
            )

        model_name = model_name or settings.llm_reasoning_model
        return f"openai:{model_name}"

    @classmethod
    def get_gemini_model(cls, model_name: str | None = None) -> str:
        """Get Gemini model name string.

        Args:
            model_name: Model name (e.g., "gemini-1.5-flash", "gemini-1.5-pro")
                       Defaults to settings.llm_voice_model

        Returns:
            Model name string with google-gla: prefix for Generative Language API

        Raises:
            ValueError: If Google API key is not configured
        """
        if not settings.google_api_key:
            raise ValueError(
                "Google API key not configured. Set GOOGLE_API_KEY in your .env file"
            )

        model_name = model_name or settings.llm_voice_model or settings.llm_default_model
        return f"google-gla:{model_name}"

    @classmethod
    def get_model_for_task(
        cls,
        task_type: TaskType | str,
        channel: Literal["voice", "chat", "email"] | None = None,
        prefer_provider: ModelProvider | None = None,
    ) -> str:
        """Route request to appropriate model based on task type and channel.

        Routing strategy (Gemini-only mode):
        - All tasks: Gemini 2.0 Flash (fast, cost-effective)
        - Can be configured to use different Gemini models per task

        Args:
            task_type: Type of task being performed
            channel: Communication channel (voice, chat, email)
            prefer_provider: Override to force specific provider

        Returns:
            OpenAIChatModel instance appropriate for the task

        Raises:
            ValueError: If required API keys are not configured
        """
        # Convert string to enum if needed
        if isinstance(task_type, str):
            try:
                task_type = TaskType(task_type.lower())
            except ValueError:
                task_type = TaskType.GENERAL

        # Force specific provider if requested
        if prefer_provider == ModelProvider.OPENAI and settings.openai_api_key:
            return cls.get_openai_model()
        if prefer_provider == ModelProvider.GEMINI:
            return cls.get_gemini_model()

        # Gemini-only mode: Use Gemini for all tasks
        if settings.llm_use_gemini_only or not settings.openai_api_key:
            # Voice channel uses voice model (fastest)
            if channel == "voice" or task_type == TaskType.VOICE:
                return cls.get_gemini_model(settings.llm_voice_model)

            # Complex reasoning uses reasoning model
            if task_type in [
                TaskType.APPOINTMENT_BOOKING,
                TaskType.COMPLEX_REASONING,
                TaskType.PIMS_INTEGRATION,
            ]:
                return cls.get_gemini_model(settings.llm_reasoning_model)

            # Default model for everything else
            return cls.get_gemini_model(settings.llm_default_model)

        # If OpenAI is configured and not in Gemini-only mode
        # Voice channel always uses Gemini (low latency)
        if channel == "voice" or task_type == TaskType.VOICE:
            return cls.get_gemini_model(settings.llm_voice_model)

        # Complex reasoning tasks can use OpenAI
        if task_type in [
            TaskType.APPOINTMENT_BOOKING,
            TaskType.COMPLEX_REASONING,
            TaskType.PIMS_INTEGRATION,
        ]:
            return cls.get_openai_model(settings.llm_reasoning_model)

        # Default: Use Gemini
        return cls.get_gemini_model(settings.llm_default_model)

