"""Evaluation models for metrics and reports.

Defines Pydantic models for Evaluation, Metrics, and Report entities.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Metrics(BaseModel):
    """Performance metrics model."""

    execution_time_seconds: float = Field(..., description="Execution time in seconds")
    task_success_rate: float = Field(..., description="Task success rate (0-1)")
    coordination_quality: float | None = Field(None, description="Coordination quality score (0-1)")
    semantic_similarity: float | None = Field(None, description="Semantic similarity score (0-1)")
    graph_density: float | None = Field(None, description="Graph density metric (0-1)")
    graph_centrality: float | None = Field(None, description="Graph centrality metric (0-1)")


class Evaluation(BaseModel):
    """Evaluation result model."""

    evaluation_id: str = Field(..., description="Unique evaluation identifier")
    paper_id: str = Field(..., description="ID of evaluated paper")
    agent_review_id: str = Field(..., description="ID of agent-generated review")
    baseline_review_id: str = Field(..., description="ID of baseline human review")
    llm_judge_score: float = Field(..., description="LLM judge score")
    llm_judge_justification: str = Field(..., description="LLM judge justification")
    metrics: dict[str, float] = Field(default_factory=dict, description="Additional metrics")


class Report(BaseModel):
    """Evaluation report model."""

    report_id: str = Field(..., description="Unique report identifier")
    run_timestamp: datetime = Field(..., description="Timestamp of evaluation run")
    config: dict[str, int | str] = Field(
        default_factory=dict, description="Configuration used for evaluation"
    )
    evaluations: list[dict[str, str | float]] = Field(
        default_factory=list, description="List of evaluation results"
    )
    aggregate_metrics: dict[str, float] = Field(
        default_factory=dict, description="Aggregated metrics across evaluations"
    )
    summary: str = Field(..., description="Summary of evaluation results")
