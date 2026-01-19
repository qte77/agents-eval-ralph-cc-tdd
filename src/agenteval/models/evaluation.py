"""Evaluation models for metrics and reports."""

from datetime import datetime

from pydantic import BaseModel, Field


class Metrics(BaseModel):
    """Traditional performance metrics."""

    execution_time_seconds: float
    success_rate: float = Field(ge=0.0, le=1.0)
    coordination_quality: float = Field(ge=0.0, le=1.0)


class Evaluation(BaseModel):
    """LLM judge evaluation result."""

    review_id: str
    semantic_score: float = Field(ge=0.0, le=1.0)
    justification: str
    baseline_review_id: str


class Report(BaseModel):
    """Consolidated evaluation report."""

    run_id: str
    timestamp: datetime
    metrics: Metrics
    evaluations: list[Evaluation]
    graph_metrics: dict[str, float]
