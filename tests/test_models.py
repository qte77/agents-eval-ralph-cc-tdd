"""Tests for core Pydantic data models.

Following TDD approach - these tests should FAIL initially.
Tests validate shared data models: Paper, Review, Evaluation, Metrics, Report.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from agenteval.models.data import Paper, Review
from agenteval.models.evaluation import Evaluation, Metrics, Report


class TestPaperModel:
    """Tests for Paper model."""

    def test_paper_creation(self):
        """Test creating a Paper with required fields."""
        paper = Paper(
            id="paper_001",
            title="Deep Learning for NLP",
            abstract="This paper discusses deep learning approaches for NLP tasks.",
            authors=["John Doe", "Jane Smith"],
            venue="ICML 2024",
        )
        assert paper.id == "paper_001"
        assert paper.title == "Deep Learning for NLP"
        assert len(paper.authors) == 2

    def test_paper_with_optional_fields(self):
        """Test Paper model with optional fields."""
        paper = Paper(
            id="paper_002",
            title="Test Paper",
            abstract="Abstract text",
            authors=["Author"],
            venue="Test Venue",
            year=2024,
            keywords=["ML", "AI"],
        )
        assert paper.year == 2024
        assert "ML" in paper.keywords

    def test_paper_requires_id(self):
        """Test that Paper requires an id field."""
        with pytest.raises(ValidationError):
            Paper(  # type: ignore[call-arg]
                title="Test",
                abstract="Abstract",
                authors=["Author"],
                venue="Venue",
            )


class TestReviewModel:
    """Tests for Review model."""

    def test_review_creation(self):
        """Test creating a Review with required fields."""
        review = Review(
            id="review_001",
            paper_id="paper_001",
            rating=8,
            confidence=4,
            review_text="This is a well-written paper with strong contributions.",
        )
        assert review.id == "review_001"
        assert review.paper_id == "paper_001"
        assert review.rating == 8
        assert review.confidence == 4

    def test_review_validates_rating_range(self):
        """Test that Review validates rating is between 1-10."""
        with pytest.raises(ValueError):
            Review(
                id="review_002",
                paper_id="paper_001",
                rating=11,
                confidence=3,
                review_text="Test review",
            )

    def test_review_validates_confidence_range(self):
        """Test that Review validates confidence is between 1-5."""
        with pytest.raises(ValueError):
            Review(
                id="review_003",
                paper_id="paper_001",
                rating=7,
                confidence=6,
                review_text="Test review",
            )


class TestMetricsModel:
    """Tests for Metrics model."""

    def test_metrics_creation(self):
        """Test creating Metrics with performance data."""
        metrics = Metrics(
            execution_time_seconds=45.2,
            success_rate=0.95,
            coordination_quality=0.87,
        )
        assert metrics.execution_time_seconds == 45.2
        assert metrics.success_rate == 0.95
        assert metrics.coordination_quality == 0.87

    def test_metrics_validates_percentage_ranges(self):
        """Test that Metrics validates percentage fields are 0-1."""
        with pytest.raises(ValueError):
            Metrics(
                execution_time_seconds=10.0,
                success_rate=1.5,
                coordination_quality=0.8,
            )


class TestEvaluationModel:
    """Tests for Evaluation model."""

    def test_evaluation_creation(self):
        """Test creating an Evaluation with judge results."""
        evaluation = Evaluation(
            review_id="review_001",
            semantic_score=0.85,
            justification="Strong alignment with human review on key points.",
            baseline_review_id="human_review_001",
        )
        assert evaluation.review_id == "review_001"
        assert evaluation.semantic_score == 0.85
        assert "alignment" in evaluation.justification

    def test_evaluation_validates_score_range(self):
        """Test that Evaluation validates semantic_score is 0-1."""
        with pytest.raises(ValueError):
            Evaluation(
                review_id="review_002",
                semantic_score=1.2,
                justification="Test",
                baseline_review_id="baseline_001",
            )


class TestReportModel:
    """Tests for Report model."""

    def test_report_creation(self):
        """Test creating a Report with consolidated results."""
        metrics = Metrics(
            execution_time_seconds=30.0,
            success_rate=0.92,
            coordination_quality=0.88,
        )
        evaluation = Evaluation(
            review_id="review_001",
            semantic_score=0.80,
            justification="Good quality",
            baseline_review_id="baseline_001",
        )
        report = Report(
            run_id="run_001",
            timestamp=datetime.now(),
            metrics=metrics,
            evaluations=[evaluation],
            graph_metrics={"density": 0.75, "centrality": 0.65},
        )
        assert report.run_id == "run_001"
        assert report.metrics.success_rate == 0.92
        assert len(report.evaluations) == 1
        assert report.graph_metrics["density"] == 0.75

    def test_report_requires_run_id(self):
        """Test that Report requires a run_id field."""
        with pytest.raises(ValidationError):
            Report(  # type: ignore[call-arg]
                timestamp=datetime.now(),
                metrics=Metrics(
                    execution_time_seconds=10.0,
                    success_rate=0.9,
                    coordination_quality=0.8,
                ),
                evaluations=[],
                graph_metrics={},
            )
