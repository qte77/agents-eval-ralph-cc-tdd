"""Tests for core Pydantic data models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from agenteval.models.data import Paper, Review
from agenteval.models.evaluation import Evaluation, Metrics, Report


def test_paper_model_creation():
    """Test Paper model can be created with required fields."""
    paper = Paper(
        id="paper-123",
        title="Test Paper",
        abstract="This is a test abstract.",
        authors=["Alice", "Bob"],
        content="Full paper content here."
    )

    assert paper.id == "paper-123"
    assert paper.title == "Test Paper"
    assert len(paper.authors) == 2


def test_paper_model_validation_requires_id():
    """Test Paper model validation fails without required id field."""
    with pytest.raises(ValidationError):
        Paper(
            title="Test Paper",
            abstract="Abstract",
            authors=["Alice"],
            content="Content"
        )  # type: ignore[call-arg]


def test_review_model_creation():
    """Test Review model can be created with required fields."""
    review = Review(
        id="review-456",
        paper_id="paper-123",
        reviewer="Reviewer A",
        rating=8.5,
        summary="Good paper with minor issues.",
        strengths=["Clear methodology", "Novel approach"],
        weaknesses=["Limited scope"],
        confidence=4
    )

    assert review.id == "review-456"
    assert review.paper_id == "paper-123"
    assert review.rating == 8.5
    assert len(review.strengths) == 2


def test_review_model_rating_validation():
    """Test Review model validates rating bounds."""
    with pytest.raises(ValidationError):
        Review(
            id="review-456",
            paper_id="paper-123",
            reviewer="Reviewer A",
            rating=11.0,  # Invalid: should be <= 10
            summary="Summary",
            strengths=["strength"],
            weaknesses=["weakness"],
            confidence=4
        )


def test_metrics_model_creation():
    """Test Metrics model can be created with performance data."""
    metrics = Metrics(
        execution_time=45.2,
        success_rate=0.95,
        coordination_quality=0.87,
        graph_density=0.42,
        graph_centrality={"node1": 0.8, "node2": 0.6}
    )

    assert metrics.execution_time == 45.2
    assert metrics.success_rate == 0.95
    assert "node1" in metrics.graph_centrality


def test_evaluation_model_creation():
    """Test Evaluation model tracks assessment results."""
    evaluation = Evaluation(
        id="eval-789",
        paper_id="paper-123",
        agent_review_id="review-456",
        human_baseline_id="review-111",
        semantic_score=8.2,
        justification="Agent review demonstrates good understanding.",
        evaluated_at=datetime.now()
    )

    assert evaluation.id == "eval-789"
    assert evaluation.semantic_score == 8.2
    assert evaluation.evaluated_at is not None


def test_report_model_creation():
    """Test Report model aggregates all evaluation data."""
    metrics = Metrics(
        execution_time=45.2,
        success_rate=0.95,
        coordination_quality=0.87,
        graph_density=0.42,
        graph_centrality={"node1": 0.8}
    )

    evaluation = Evaluation(
        id="eval-789",
        paper_id="paper-123",
        agent_review_id="review-456",
        human_baseline_id="review-111",
        semantic_score=8.2,
        justification="Good review.",
        evaluated_at=datetime.now()
    )

    report = Report(
        id="report-001",
        run_id="run-2026-01-21",
        created_at=datetime.now(),
        metrics=metrics,
        evaluations=[evaluation],
        summary="Evaluation completed successfully."
    )

    assert report.id == "report-001"
    assert report.metrics.success_rate == 0.95
    assert len(report.evaluations) == 1


def test_report_model_allows_empty_evaluations():
    """Test Report model can be created with no evaluations."""
    metrics = Metrics(
        execution_time=0.0,
        success_rate=0.0,
        coordination_quality=0.0,
        graph_density=0.0,
        graph_centrality={}
    )

    report = Report(
        id="report-002",
        run_id="run-2026-01-21",
        created_at=datetime.now(),
        metrics=metrics,
        evaluations=[],
        summary="No evaluations yet."
    )

    assert report.id == "report-002"
    assert len(report.evaluations) == 0


def test_models_are_json_serializable():
    """Test that all models can be serialized to JSON."""
    paper = Paper(
        id="paper-123",
        title="Test Paper",
        abstract="Abstract",
        authors=["Alice"],
        content="Content"
    )

    review = Review(
        id="review-456",
        paper_id="paper-123",
        reviewer="Reviewer A",
        rating=8.5,
        summary="Summary",
        strengths=["strength"],
        weaknesses=["weakness"],
        confidence=4
    )

    # Test JSON serialization
    paper_json = paper.model_dump_json()
    review_json = review.model_dump_json()

    assert isinstance(paper_json, str)
    assert isinstance(review_json, str)
    assert "paper-123" in paper_json
    assert "review-456" in review_json
