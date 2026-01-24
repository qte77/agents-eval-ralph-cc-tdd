"""Core data models for papers and reviews."""

from pydantic import BaseModel, Field


class Paper(BaseModel):
    """Scientific paper model."""

    id: str
    title: str
    abstract: str
    authors: list[str]
    content: str


class Review(BaseModel):
    """Review model for paper assessment."""

    id: str
    paper_id: str
    reviewer: str
    rating: float = Field(ge=0.0, le=10.0)
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    confidence: int = Field(ge=1, le=5)
