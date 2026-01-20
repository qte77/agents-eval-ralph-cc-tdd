"""Core data models for papers and reviews."""

from pydantic import BaseModel, Field, field_validator


class Paper(BaseModel):
    """Model representing a scientific paper."""

    id: str = Field(..., description="Unique paper identifier")
    title: str
    abstract: str
    authors: list[str]
    venue: str
    year: int | None = None
    keywords: list[str] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate that id is provided."""
        if not v:
            raise ValueError("id field is required")
        return v


class Review(BaseModel):
    """Model representing a paper review."""

    id: str = Field(..., description="Unique review identifier")
    paper_id: str
    rating: int = Field(..., ge=1, le=10)
    confidence: int = Field(..., ge=1, le=5)
    review_text: str

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        """Validate rating is between 1-10."""
        if not 1 <= v <= 10:
            raise ValueError("rating must be between 1 and 10")
        return v

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: int) -> int:
        """Validate confidence is between 1-5."""
        if not 1 <= v <= 5:
            raise ValueError("confidence must be between 1 and 5")
        return v
