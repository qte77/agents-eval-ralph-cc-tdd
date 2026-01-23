"""Evaluation models for metrics, judge results, and reports."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Metrics(BaseModel):
    """Model for traditional performance metrics."""

    execution_time_seconds: float
    task_success_rate: float = Field(..., ge=0.0, le=1.0)
    coordination_quality: float | None = None
    semantic_similarity: float | None = None
    graph_density: float | None = None
    graph_centrality: float | None = None


class Evaluation(BaseModel):
    """Model for evaluation results."""

    evaluation_id: str
    paper_id: str
    agent_review_id: str
    baseline_review_id: str
    llm_judge_score: float
    llm_judge_justification: str
    metrics: dict[str, Any] = Field(default_factory=dict)


class Report(BaseModel):
    """Model for consolidated evaluation report."""

    report_id: str
    run_timestamp: datetime
    config: dict[str, Any] = Field(default_factory=dict)
    evaluations: list[dict[str, Any]] = Field(default_factory=list)
    aggregate_metrics: dict[str, Any] = Field(default_factory=dict)
    summary: str
