"""Analytics agent for extracting structured insights from chat transcripts.

Uses Pydantic AI with structured output to analyze veterinary clinic
chat conversations and extract sentiment, topics, entities, and resolution.
"""

from openai import AsyncOpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.core.config import settings
from app.schemas.chat_analysis import ChatAnalysisResult

ANALYTICS_SYSTEM_PROMPT = """\
You are an expert analyst for a veterinary clinic chat system.
Analyze the following chat transcript between a pet owner and the clinic's AI assistant.

Extract the following structured information:

1. **Sentiment**: Overall sentiment of the user (positive/neutral/negative) and a score from -1.0 to 1.0.
2. **Resolution**: Whether the user's issue was resolved (resolved/unresolved/partial/escalated).
3. **Satisfaction**: Inferred user satisfaction (satisfied/neutral/dissatisfied).
4. **Topics**: The primary topic and all topics discussed (e.g., appointment_booking, vaccination, billing, emergency, general_inquiry, medication, surgery, dental, grooming, nutrition, behavioral).
5. **Entities**: Extract pet names, species, appointment types, owner names, and medications mentioned.
6. **Key Points**: 3-5 bullet point summary of the conversation.
7. **Follow-up**: Suggest a follow-up action if appropriate (e.g., "Schedule follow-up appointment", "Send vaccination reminder"), or null if none needed.

Be accurate and concise. Base your analysis only on what is in the transcript."""


def create_analytics_agent() -> Agent:
    """Create an analytics agent configured with DeepSeek.

    Returns a fresh agent instance. Called from Celery tasks
    where there is no FastAPI context.
    """
    deepseek_client = AsyncOpenAI(
        api_key=settings.deepseek_api_key.get_secret_value()
        if settings.deepseek_api_key
        else "",
        base_url=settings.deepseek_base_url,
    )
    deepseek_provider = OpenAIProvider(openai_client=deepseek_client)
    deepseek_model = OpenAIChatModel(
        settings.deepseek_model,
        provider=deepseek_provider,
    )

    return Agent(
        model=deepseek_model,
        system_prompt=ANALYTICS_SYSTEM_PROMPT,
        output_type=ChatAnalysisResult,
        name="chat_analytics_agent",
    )
