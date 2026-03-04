"""Model factory for creating LLM instances with provider routing.

This module provides a centralized factory for creating DeepSeek models
using the OpenAI-compatible API.
"""

from enum import StrEnum
from typing import Any, Literal

from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

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
    """Factory for creating configured model instances for pydantic-ai.

    Provides:
    - Properly configured OpenAIChatModel instances with API keys and base URLs
    - Intelligent routing based on task type and channel
    - Support for DeepSeek models via OpenAI-compatible API
    """

    @classmethod
    def get_deepseek_model(cls, model_name: str | None = None) -> OpenAIChatModel:
        """Get a configured DeepSeek model instance.

        Creates an OpenAIChatModel with the DeepSeek API key and base URL
        properly configured, so pydantic-ai doesn't fall back to OPENAI_API_KEY.

        Args:
            model_name: Model name (e.g., "deepseek-v3-0324")
                       Defaults to settings.deepseek_model

        Returns:
            Configured OpenAIChatModel instance

        Raises:
            ValueError: If DeepSeek API key is not configured
        """
        if not settings.deepseek_api_key:
            raise ValueError(
                "DeepSeek API key not configured. Set DEEPSEEK_API_KEY in your .env file"
            )

        model_name = model_name or settings.deepseek_model

        client = AsyncOpenAI(
            api_key=settings.deepseek_api_key.get_secret_value(),
            base_url=settings.deepseek_base_url,
        )
        provider = OpenAIProvider(openai_client=client)
        return OpenAIChatModel(model_name, provider=provider)

    @classmethod
    def get_openai_model(cls, model_name: str | None = None) -> OpenAIChatModel:
        """Get a configured OpenAI model instance (for potential future use).

        Args:
            model_name: Model name (e.g., "gpt-4o", "gpt-4o-mini")
                       Defaults to settings.llm_reasoning_model

        Returns:
            Configured OpenAIChatModel instance

        Raises:
            ValueError: If OpenAI API key is not configured
        """
        if not settings.openai_api_key:
            raise ValueError(
                "OpenAI API key not configured. Set OPENAI_API_KEY in your .env file"
            )

        model_name = model_name or settings.llm_reasoning_model

        client = AsyncOpenAI(
            api_key=settings.openai_api_key.get_secret_value(),
        )
        provider = OpenAIProvider(openai_client=client)
        return OpenAIChatModel(model_name, provider=provider)

    @classmethod
    def get_model_for_task(
        cls,
        task_type: TaskType | str,
        channel: Literal["voice", "chat", "email"] | None = None,
        prefer_provider: ModelProvider | None = None,
    ) -> Any:
        """Route request to appropriate model based on task type and channel.

        Currently uses DeepSeek for all tasks as the primary LLM provider.

        Args:
            task_type: Type of task being performed
            channel: Communication channel (voice, chat, email)
            prefer_provider: Override to force specific provider

        Returns:
            Configured model instance appropriate for the task

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
