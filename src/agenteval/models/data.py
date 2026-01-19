"""Data models for papers and reviews."""

from pydantic import BaseModel, Field


class Paper(BaseModel):
    """Paper model with metadata and content."""

    id: str
    title: str
    abstract: str
    authors: list[str]
    venue: str
    year: int | None = None
    keywords: list[str] = Field(default_factory=list)


class Review(BaseModel):
    """Review model with rating and content."""

    id: str
    paper_id: str
    rating: int = Field(ge=1, le=10)
    confidence: int = Field(ge=1, le=5)
    review_text: str
