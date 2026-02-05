"""Model factory for creating LLM instances with provider routing.

This module provides a centralized factory for creating DeepSeek models
using the OpenAI-compatible API.
"""

from enum import StrEnum
from typing import Literal

from app.core.config import settings


class ModelProvider(StrEnum):
    """Supported LLM providers."""

    DEEPSEEK = "deepseek"
    OPENAI = "openai"  # Kept for potential future use


class TaskType(StrEnum):
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
    - Support for DeepSeek models via OpenAI-compatible API
    """

    @classmethod
    def get_deepseek_model(cls, model_name: str | None = None) -> str:
        """Get DeepSeek model name string for pydantic-ai.

        DeepSeek uses OpenAI-compatible API, so we use the openai: prefix
        with custom base_url configured in the agent.

        Args:
            model_name: Model name (e.g., "deepseek-v3-0324")
                       Defaults to settings.deepseek_model

        Returns:
            Model name string with openai: prefix (DeepSeek uses OpenAI-compatible API)

        Raises:
            ValueError: If DeepSeek API key is not configured
        """
        if not settings.deepseek_api_key:
            raise ValueError(
                "DeepSeek API key not configured. Set DEEPSEEK_API_KEY in your .env file"
            )

        model_name = model_name or settings.deepseek_model
        # DeepSeek uses OpenAI-compatible API, so we use openai: prefix
        # The base_url is configured separately when creating the agent
        return f"openai:{model_name}"

    @classmethod
    def get_openai_model(cls, model_name: str | None = None) -> str:
        """Get OpenAI model name string (for potential future use).

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
    def get_model_for_task(
        cls,
        task_type: TaskType | str,
        channel: Literal["voice", "chat", "email"] | None = None,
        prefer_provider: ModelProvider | None = None,
    ) -> str:
        """Route request to appropriate model based on task type and channel.

        Currently uses DeepSeek for all tasks as the primary LLM provider.

        Args:
            task_type: Type of task being performed
            channel: Communication channel (voice, chat, email)
            prefer_provider: Override to force specific provider

        Returns:
            Model name string appropriate for the task

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

        # Default: Use DeepSeek for all tasks
        return cls.get_deepseek_model(settings.deepseek_model)
