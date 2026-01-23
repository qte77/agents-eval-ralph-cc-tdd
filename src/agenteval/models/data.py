"""Core data models for papers and reviews."""

from typing import Any

from pydantic import BaseModel, Field


class Paper(BaseModel):
    """Model representing a scientific paper."""

    paper_id: str
    title: str
    abstract: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Review(BaseModel):
    """Model representing a paper review."""

    review_id: str
    paper_id: str
    rating: int = Field(..., ge=1, le=10)
    confidence: int = Field(..., ge=1, le=5)
    summary: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    detailed_comments: str
    is_agent_generated: bool
