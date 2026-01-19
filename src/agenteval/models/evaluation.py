"""Evaluation models for metrics, judge results, and reports."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Metrics(BaseModel):
    """Model for traditional performance metrics."""

    execution_time_seconds: float
    success_rate: float = Field(..., ge=0.0, le=1.0)
    coordination_quality: float = Field(..., ge=0.0, le=1.0)

    @field_validator("success_rate", "coordination_quality")
    @classmethod
    def validate_percentage(cls, v: float) -> float:
        """Validate percentage fields are between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("percentage fields must be between 0 and 1")
        return v


class Evaluation(BaseModel):
    """Model for LLM judge evaluation results."""

    review_id: str
    semantic_score: float = Field(..., ge=0.0, le=1.0)
    justification: str
    baseline_review_id: str

    @field_validator("semantic_score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        """Validate semantic_score is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("semantic_score must be between 0 and 1")
        return v


class Report(BaseModel):
    """Model for consolidated evaluation report."""

    run_id: str = Field(..., description="Unique run identifier")
    timestamp: datetime
    metrics: Metrics
    evaluations: list[Evaluation]
    graph_metrics: dict[str, Any]

    @field_validator("run_id")
    @classmethod
    def validate_run_id(cls, v: str) -> str:
        """Validate that run_id is provided."""
        if not v:
            raise ValueError("run_id field is required")
        return v
