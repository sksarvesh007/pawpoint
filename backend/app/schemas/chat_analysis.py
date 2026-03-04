"""Pydantic schemas for chat analysis.

ChatAnalysisResult is used as structured output for the LLM analytics agent.
ChatAnalysisDetail is the API response schema.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatEntities(BaseModel):
    """Entities extracted from a chat conversation."""

    pet_names: list[str] = Field(default_factory=list)
    pet_species: list[str] = Field(default_factory=list)
    appointment_types: list[str] = Field(default_factory=list)
    owner_names: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)


class ChatAnalysisResult(BaseModel):
    """Pydantic structured output for LLM chat analysis.

    Used as output_type for the analytics agent to ensure
    the LLM returns properly structured data.
    """

    sentiment: Literal["positive", "neutral", "negative"]
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    resolution_status: Literal["resolved", "unresolved", "partial", "escalated"]
    user_satisfaction: Literal["satisfied", "neutral", "dissatisfied"]
    primary_topic: str
    topics: list[str]
    entities: ChatEntities
    key_points: list[str] = Field(min_length=1, max_length=5)
    suggested_followup: str | None = None


class ChatAnalysisDetail(BaseModel):
    """API response schema for chat analysis data."""

    sentiment: str
    sentiment_score: float
    resolution_status: str
    user_satisfaction: str
    primary_topic: str
    topics: list[str]
    entities: dict
    key_points: list[str]
    suggested_followup: str | None
    analyzed_at: datetime | None
    status: str
