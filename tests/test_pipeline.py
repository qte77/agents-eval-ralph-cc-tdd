"""Tests for evaluation pipeline orchestrator.

This module tests the orchestration of all evaluation modules with
dependency management and reproducibility controls.
"""

import random
from datetime import datetime

import pytest
from agenteval.pipeline import EvaluationPipeline, PipelineConfig, PipelineResult

from agenteval.judges.llm_judge import AgentReview
from agenteval.metrics.graph import AgentInteraction
from agenteval.metrics.traditional import AgentTaskResult
from agenteval.models.data import Review


@pytest.fixture
def sample_task_results() -> list[AgentTaskResult]:
    """Provide sample agent task results for testing."""
    return [
        AgentTaskResult(
            task_id="task-1",
            agent_id="agent-1",
            start_time=datetime(2024, 1, 1, 10, 0, 0),
            end_time=datetime(2024, 1, 1, 10, 0, 5),
            success=True,
            coordination_score=0.8,
        ),
        AgentTaskResult(
            task_id="task-2",
            agent_id="agent-2",
            start_time=datetime(2024, 1, 1, 10, 0, 10),
            end_time=datetime(2024, 1, 1, 10, 0, 18),
            success=True,
            coordination_score=0.9,
        ),
    ]


@pytest.fixture
def sample_interactions() -> list[AgentInteraction]:
    """Provide sample agent interactions for testing."""
    return [
        AgentInteraction(
            from_agent="agent-1",
            to_agent="agent-2",
            interaction_type="message",
            timestamp="2024-01-01T10:00:00Z",
        ),
        AgentInteraction(
            from_agent="agent-2",
            to_agent="agent-1",
            interaction_type="response",
            timestamp="2024-01-01T10:00:05Z",
        ),
    ]


@pytest.fixture
def sample_agent_reviews() -> list[AgentReview]:
    """Provide sample agent reviews for testing."""
    return [
        AgentReview(
            review_id="review-1",
            paper_id="paper-1",
            rating=8,
            confidence=4,
            review_text="This paper presents a novel approach to the problem.",
        ),
    ]


@pytest.fixture
def sample_baseline_reviews() -> list[Review]:
    """Provide sample baseline reviews for testing."""
    return [
        Review(
            id="baseline-1",
            paper_id="paper-1",
            rating=7,
            confidence=4,
            review_text="The paper introduces an interesting method.",
        ),
    ]


class TestPipelineConfig:
    """Test pipeline configuration."""

    def test_default_config(self) -> None:
        """Test default pipeline configuration."""
        config = PipelineConfig()
        assert config.seed is not None
        assert isinstance(config.seed, int)
        assert config.seed >= 0

    def test_custom_seed(self) -> None:
        """Test custom seed configuration."""
        config = PipelineConfig(seed=42)
        assert config.seed == 42

    def test_reproducible_seed(self) -> None:
        """Test that same seed produces same random behavior."""
        config1 = PipelineConfig(seed=42)
        random.seed(config1.seed)
        val1 = random.random()

        config2 = PipelineConfig(seed=42)
        random.seed(config2.seed)
        val2 = random.random()

        assert val1 == val2


class TestEvaluationPipeline:
    """Test evaluation pipeline orchestrator."""

    def test_pipeline_initialization(self) -> None:
        """Test pipeline can be initialized with config."""
        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)
        assert pipeline.config == config
        assert hasattr(pipeline, "traditional_calculator")
        assert hasattr(pipeline, "llm_evaluator")
        assert hasattr(pipeline, "graph_analyzer")

    @pytest.mark.anyio
    async def test_run_all_tiers(
        self,
        sample_task_results: list[AgentTaskResult],
        sample_interactions: list[AgentInteraction],
        sample_agent_reviews: list[AgentReview],
        sample_baseline_reviews: list[Review],
    ) -> None:
        """Test pipeline runs all three evaluation tiers."""
        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        result = await pipeline.run(
            task_results=sample_task_results,
            interactions=sample_interactions,
            agent_reviews=sample_agent_reviews,
            baseline_reviews=sample_baseline_reviews,
        )

        assert isinstance(result, PipelineResult)
        assert result.run_id is not None
        assert result.timestamp is not None
        assert result.traditional_metrics is not None
        assert result.llm_judge_results is not None
        assert result.graph_metrics is not None

    @pytest.mark.anyio
    async def test_pipeline_result_structure(
        self,
        sample_task_results: list[AgentTaskResult],
        sample_interactions: list[AgentInteraction],
        sample_agent_reviews: list[AgentReview],
        sample_baseline_reviews: list[Review],
    ) -> None:
        """Test pipeline result has correct structure."""
        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        result = await pipeline.run(
            task_results=sample_task_results,
            interactions=sample_interactions,
            agent_reviews=sample_agent_reviews,
            baseline_reviews=sample_baseline_reviews,
        )

        # Check traditional metrics
        assert "execution_time_seconds" in result.traditional_metrics
        assert "success_rate" in result.traditional_metrics
        assert "coordination_quality" in result.traditional_metrics

        # Check LLM judge results
        assert isinstance(result.llm_judge_results, list)
        assert len(result.llm_judge_results) == len(sample_agent_reviews)

        # Check graph metrics
        assert "density" in result.graph_metrics
        assert "num_nodes" in result.graph_metrics
        assert "num_edges" in result.graph_metrics

    @pytest.mark.anyio
    async def test_reproducible_runs(
        self,
        sample_task_results: list[AgentTaskResult],
        sample_interactions: list[AgentInteraction],
        sample_agent_reviews: list[AgentReview],
        sample_baseline_reviews: list[Review],
    ) -> None:
        """Test that same seed produces reproducible results."""
        config1 = PipelineConfig(seed=42)
        pipeline1 = EvaluationPipeline(config1)
        result1 = await pipeline1.run(
            task_results=sample_task_results,
            interactions=sample_interactions,
            agent_reviews=sample_agent_reviews,
            baseline_reviews=sample_baseline_reviews,
        )

        config2 = PipelineConfig(seed=42)
        pipeline2 = EvaluationPipeline(config2)
        result2 = await pipeline2.run(
            task_results=sample_task_results,
            interactions=sample_interactions,
            agent_reviews=sample_agent_reviews,
            baseline_reviews=sample_baseline_reviews,
        )

        # Same seed should produce same metrics
        assert result1.traditional_metrics == result2.traditional_metrics
        assert result1.graph_metrics == result2.graph_metrics

    @pytest.mark.anyio
    async def test_dependency_handling(
        self,
        sample_task_results: list[AgentTaskResult],
        sample_interactions: list[AgentInteraction],
        sample_agent_reviews: list[AgentReview],
        sample_baseline_reviews: list[Review],
    ) -> None:
        """Test pipeline handles module dependencies correctly."""
        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        # Should not raise any errors even with dependencies between modules
        result = await pipeline.run(
            task_results=sample_task_results,
            interactions=sample_interactions,
            agent_reviews=sample_agent_reviews,
            baseline_reviews=sample_baseline_reviews,
        )

        assert result is not None
        # All modules should have completed
        assert result.traditional_metrics is not None
        assert result.llm_judge_results is not None
        assert result.graph_metrics is not None

    @pytest.mark.anyio
    async def test_empty_inputs(self) -> None:
        """Test pipeline handles empty inputs gracefully."""
        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        # Should handle empty lists without crashing
        result = await pipeline.run(
            task_results=[],
            interactions=[],
            agent_reviews=[],
            baseline_reviews=[],
        )

        assert isinstance(result, PipelineResult)
        # Empty inputs should produce empty/default results
        assert result.llm_judge_results == []

    @pytest.mark.anyio
    async def test_mismatched_review_lengths(
        self,
        sample_task_results: list[AgentTaskResult],
        sample_interactions: list[AgentInteraction],
        sample_agent_reviews: list[AgentReview],
    ) -> None:
        """Test pipeline handles mismatched review list lengths."""
        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        # Mismatched lengths should raise an error
        with pytest.raises(ValueError, match="Mismatched lengths"):
            await pipeline.run(
                task_results=sample_task_results,
                interactions=sample_interactions,
                agent_reviews=sample_agent_reviews,
                baseline_reviews=[],  # Empty baseline
            )
