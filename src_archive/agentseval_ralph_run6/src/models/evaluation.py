"""Evaluation models for metrics and reports."""

from datetime import datetime

from pydantic import BaseModel


class Metrics(BaseModel):
    """Performance metrics model."""

    execution_time: float
    success_rate: float
    coordination_quality: float
    graph_density: float
    graph_centrality: dict[str, float]


class Evaluation(BaseModel):
    """LLM-as-a-Judge evaluation result."""

    id: str
    paper_id: str
    agent_review_id: str
    human_baseline_id: str
    semantic_score: float
    justification: str
    evaluated_at: datetime


class Report(BaseModel):
    """Consolidated evaluation report."""

    id: str
    run_id: str
    created_at: datetime
    metrics: Metrics
    evaluations: list[Evaluation]
    summary: str
