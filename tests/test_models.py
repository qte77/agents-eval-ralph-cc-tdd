"""Tests for core data models."""

from datetime import datetime

import pytest
from agenteval.models.data import Paper, Review
from agenteval.models.evaluation import Evaluation, Metrics, Report


def test_paper_model_creation():
    """Test that Paper model can be created with required fields."""
    paper = Paper(
        paper_id="paper_001",
        title="Test Paper",
        abstract="This is a test abstract",
        content="Full paper content here",
        metadata={"venue": "Test Conference", "year": 2024},
    )

    assert paper.paper_id == "paper_001"
    assert paper.title == "Test Paper"
    assert paper.abstract == "This is a test abstract"
    assert paper.content == "Full paper content here"
    assert paper.metadata["venue"] == "Test Conference"


def test_review_model_creation():
    """Test that Review model can be created with required fields."""
    review = Review(
        review_id="review_001",
        paper_id="paper_001",
        rating=8,
        confidence=4,
        summary="Good paper with solid contributions",
        strengths=["Novel approach", "Strong empirical results"],
        weaknesses=["Limited theoretical analysis"],
        detailed_comments="The paper presents...",
        is_agent_generated=False,
    )

    assert review.review_id == "review_001"
    assert review.paper_id == "paper_001"
    assert review.rating == 8
    assert review.confidence == 4
    assert review.is_agent_generated is False


def test_metrics_model_creation():
    """Test that Metrics model can be created with performance metrics."""
    metrics = Metrics(
        execution_time_seconds=12.5,
        task_success_rate=0.85,
        coordination_quality=0.75,
        semantic_similarity=0.80,
        graph_density=0.45,
        graph_centrality=0.60,
    )

    assert metrics.execution_time_seconds == 12.5
    assert metrics.task_success_rate == 0.85
    assert metrics.coordination_quality == 0.75
    assert metrics.semantic_similarity == 0.80
    assert metrics.graph_density == 0.45
    assert metrics.graph_centrality == 0.60


def test_evaluation_model_creation():
    """Test that Evaluation model can be created with evaluation results."""
    evaluation = Evaluation(
        evaluation_id="eval_001",
        paper_id="paper_001",
        agent_review_id="review_agent_001",
        baseline_review_id="review_human_001",
        llm_judge_score=7.5,
        llm_judge_justification="The agent review captures key points...",
        metrics={
            "execution_time_seconds": 12.5,
            "task_success_rate": 0.85,
            "coordination_quality": 0.75,
        },
    )

    assert evaluation.evaluation_id == "eval_001"
    assert evaluation.paper_id == "paper_001"
    assert evaluation.llm_judge_score == 7.5
    assert evaluation.metrics["task_success_rate"] == 0.85


def test_report_model_creation():
    """Test that Report model can be created with aggregated results."""
    report = Report(
        report_id="report_001",
        run_timestamp=datetime.now(),
        config={
            "seed": 42,
            "batch_size": 10,
        },
        evaluations=[
            {
                "evaluation_id": "eval_001",
                "paper_id": "paper_001",
                "llm_judge_score": 7.5,
            }
        ],
        aggregate_metrics={
            "mean_execution_time": 12.3,
            "mean_task_success_rate": 0.84,
            "mean_llm_judge_score": 7.2,
        },
        summary="Overall performance is good with strong task completion rates.",
    )

    assert report.report_id == "report_001"
    assert report.config["seed"] == 42
    assert len(report.evaluations) == 1
    assert report.aggregate_metrics["mean_llm_judge_score"] == 7.2


def test_paper_model_validates_required_fields():
    """Test that Paper model validates required fields."""
    with pytest.raises(Exception):  # Pydantic ValidationError
        Paper()  # type: ignore[call-arg]


def test_review_model_validates_required_fields():
    """Test that Review model validates required fields."""
    with pytest.raises(Exception):  # Pydantic ValidationError
        Review()  # type: ignore[call-arg]


def test_metrics_model_has_optional_fields():
    """Test that Metrics model allows optional fields."""
    # Create with minimal required fields
    metrics = Metrics(  # type: ignore[call-arg]
        execution_time_seconds=10.0,
        task_success_rate=0.9,
    )

    assert metrics.execution_time_seconds == 10.0
    assert metrics.task_success_rate == 0.9
    # Optional fields should be None or have defaults
    assert hasattr(metrics, "coordination_quality")


def test_models_are_json_serializable():
    """Test that all models can be serialized to JSON."""
    paper = Paper(
        paper_id="paper_001",
        title="Test",
        abstract="Abstract",
        content="Content",
        metadata={},
    )

    review = Review(
        review_id="review_001",
        paper_id="paper_001",
        rating=8,
        confidence=4,
        summary="Good",
        strengths=["A"],
        weaknesses=["B"],
        detailed_comments="Details",
        is_agent_generated=False,
    )

    # Pydantic models have .model_dump_json()
    paper_json = paper.model_dump_json()
    review_json = review.model_dump_json()

    assert "paper_001" in paper_json
    assert "review_001" in review_json
