"""Tests for evaluation pipeline orchestrator.

Following TDD RED phase - these tests should FAIL until implementation is complete.
Tests validate orchestration of all three evaluation tiers with dependency management
and reproducibility controls.
"""

import random
from datetime import datetime

import pytest

from agenteval.judges.llm_judge import AgentReview
from agenteval.metrics.graph import AgentInteraction
from agenteval.models.data import Review


class TestPipelineConfigurationModels:
    """Test pipeline configuration models."""

    def test_pipeline_config_exists(self):
        """Test PipelineConfig model exists and has seed field."""
        from agenteval.pipeline import PipelineConfig

        config = PipelineConfig()
        assert hasattr(config, "seed")

    def test_pipeline_config_default_seed(self):
        """Test PipelineConfig generates default random seed."""
        from agenteval.pipeline import PipelineConfig

        config = PipelineConfig()
        assert config.seed is not None
        assert isinstance(config.seed, int)
        assert config.seed >= 0

    def test_pipeline_config_custom_seed(self):
        """Test PipelineConfig accepts custom seed."""
        from agenteval.pipeline import PipelineConfig

        config = PipelineConfig(seed=42)
        assert config.seed == 42

    def test_pipeline_config_seed_for_reproducibility(self):
        """Test that same seed produces reproducible random behavior."""
        from agenteval.pipeline import PipelineConfig

        config1 = PipelineConfig(seed=42)
        random.seed(config1.seed)
        val1 = random.random()

        config2 = PipelineConfig(seed=42)
        random.seed(config2.seed)
        val2 = random.random()

        assert val1 == val2


class TestPipelineResultModel:
    """Test pipeline result model."""

    def test_pipeline_result_exists(self):
        """Test PipelineResult model exists with required fields."""
        from agenteval.pipeline import PipelineResult

        result = PipelineResult(
            run_id="test-run-123",
            timestamp=datetime.now(),
            traditional_metrics={"execution_time_seconds": 10.0},
            llm_judge_results=[],
            graph_metrics={"density": 0.5},
        )
        assert result.run_id == "test-run-123"
        assert result.traditional_metrics is not None
        assert result.llm_judge_results is not None
        assert result.graph_metrics is not None


class TestEvaluationPipelineInitialization:
    """Test evaluation pipeline initialization."""

    def test_pipeline_initialization(self):
        """Test EvaluationPipeline can be initialized with config."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)
        assert pipeline is not None
        assert pipeline.config == config

    def test_pipeline_initializes_evaluators(self):
        """Test pipeline initializes all three evaluation tier modules."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        # Should have evaluators for all three tiers
        assert hasattr(pipeline, "traditional_calculator")
        assert hasattr(pipeline, "llm_evaluator")
        assert hasattr(pipeline, "graph_analyzer")

    def test_pipeline_sets_random_seed(self):
        """Test pipeline sets random seed for reproducibility."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(seed=42)
        EvaluationPipeline(config)

        # After initialization, random should be seeded
        val1 = random.random()

        config2 = PipelineConfig(seed=42)
        EvaluationPipeline(config2)
        val2 = random.random()

        assert val1 == val2


class TestPipelineOrchestration:
    """Test pipeline orchestration of all three tiers."""

    @pytest.fixture
    def sample_agent_runs(self):
        """Provide sample agent run data."""
        return [
            {
                "agent_id": "agent1",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, 5, 0),
                "task_completed": True,
                "coordination_events": [{"type": "message", "success": True}],
            },
            {
                "agent_id": "agent2",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, 3, 0),
                "task_completed": True,
                "coordination_events": [{"type": "message", "success": True}],
            },
        ]

    @pytest.fixture
    def sample_interactions(self):
        """Provide sample agent interactions."""
        return [
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent2",
                interaction_type="message",
                timestamp="2024-01-01T10:00:00Z",
            ),
            AgentInteraction(
                from_agent="agent2",
                to_agent="agent1",
                interaction_type="response",
                timestamp="2024-01-01T10:00:05Z",
            ),
        ]

    @pytest.fixture
    def sample_agent_reviews(self):
        """Provide sample agent-generated reviews."""
        return [
            AgentReview(
                review_id="agent_review_001",
                paper_id="paper_001",
                rating=8,
                confidence=4,
                review_text="This paper presents a novel approach.",
            ),
        ]

    @pytest.fixture
    def sample_baseline_reviews(self):
        """Provide sample human baseline reviews."""
        return [
            Review(
                id="baseline_review_001",
                paper_id="paper_001",
                rating=7,
                confidence=4,
                review_text="The paper introduces an interesting method.",
            ),
        ]

    @pytest.mark.anyio
    async def test_pipeline_runs_all_three_tiers(
        self,
        sample_agent_runs,
        sample_interactions,
        sample_agent_reviews,
        sample_baseline_reviews,
    ):
        """Test pipeline executes all three evaluation tiers in sequence."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        result = await pipeline.run(
            agent_runs=sample_agent_runs,
            interactions=sample_interactions,
            agent_reviews=sample_agent_reviews,
            baseline_reviews=sample_baseline_reviews,
        )

        # Should have results from all three tiers
        assert result.traditional_metrics is not None
        assert result.llm_judge_results is not None
        assert result.graph_metrics is not None

    @pytest.mark.anyio
    async def test_pipeline_traditional_metrics_tier(self, sample_agent_runs):
        """Test pipeline executes traditional metrics tier."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        result = await pipeline.run(
            agent_runs=sample_agent_runs,
            interactions=[],
            agent_reviews=[],
            baseline_reviews=[],
        )

        # Traditional metrics should be calculated
        assert "execution_time_seconds" in result.traditional_metrics
        assert "success_rate" in result.traditional_metrics
        assert "coordination_quality" in result.traditional_metrics
        assert result.traditional_metrics["success_rate"] > 0

    @pytest.mark.anyio
    async def test_pipeline_llm_judge_tier(
        self, sample_agent_reviews, sample_baseline_reviews
    ):
        """Test pipeline executes LLM judge tier."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        result = await pipeline.run(
            agent_runs=[],
            interactions=[],
            agent_reviews=sample_agent_reviews,
            baseline_reviews=sample_baseline_reviews,
        )

        # LLM judge results should be present
        assert isinstance(result.llm_judge_results, list)
        assert len(result.llm_judge_results) == len(sample_agent_reviews)
        if result.llm_judge_results:
            assert "review_id" in result.llm_judge_results[0]
            assert "semantic_score" in result.llm_judge_results[0]
            assert "justification" in result.llm_judge_results[0]

    @pytest.mark.anyio
    async def test_pipeline_graph_metrics_tier(self, sample_interactions):
        """Test pipeline executes graph metrics tier."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        result = await pipeline.run(
            agent_runs=[],
            interactions=sample_interactions,
            agent_reviews=[],
            baseline_reviews=[],
        )

        # Graph metrics should be calculated
        assert "density" in result.graph_metrics
        assert "num_nodes" in result.graph_metrics
        assert "num_edges" in result.graph_metrics
        assert result.graph_metrics["num_nodes"] > 0


class TestPipelineDependencyManagement:
    """Test pipeline handles module dependencies correctly."""

    @pytest.mark.anyio
    async def test_pipeline_handles_dependencies(self):
        """Test pipeline handles module dependencies without errors."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        agent_runs = [
            {
                "agent_id": "agent1",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, 5, 0),
                "task_completed": True,
            }
        ]

        interactions = [
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent2",
                interaction_type="message",
                timestamp="2024-01-01T10:00:00Z",
            ),
        ]

        agent_reviews = [
            AgentReview(
                review_id="review1",
                paper_id="paper1",
                rating=8,
                confidence=4,
                review_text="Good paper.",
            ),
        ]

        baseline_reviews = [
            Review(
                id="baseline1",
                paper_id="paper1",
                rating=7,
                confidence=4,
                review_text="Good work.",
            ),
        ]

        # Should complete without errors despite dependencies
        result = await pipeline.run(
            agent_runs=agent_runs,
            interactions=interactions,
            agent_reviews=agent_reviews,
            baseline_reviews=baseline_reviews,
        )

        assert result is not None
        assert result.traditional_metrics is not None
        assert result.llm_judge_results is not None
        assert result.graph_metrics is not None


class TestPipelineReproducibility:
    """Test pipeline reproducibility controls."""

    @pytest.mark.anyio
    async def test_pipeline_reproducible_runs_with_same_seed(self):
        """Test that same seed produces reproducible results."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        agent_runs = [
            {
                "agent_id": "agent1",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, 5, 0),
                "task_completed": True,
            }
        ]

        interactions = [
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent2",
                interaction_type="message",
                timestamp="2024-01-01T10:00:00Z",
            ),
        ]

        # Run 1
        config1 = PipelineConfig(seed=42)
        pipeline1 = EvaluationPipeline(config1)
        result1 = await pipeline1.run(
            agent_runs=agent_runs,
            interactions=interactions,
            agent_reviews=[],
            baseline_reviews=[],
        )

        # Run 2 with same seed
        config2 = PipelineConfig(seed=42)
        pipeline2 = EvaluationPipeline(config2)
        result2 = await pipeline2.run(
            agent_runs=agent_runs,
            interactions=interactions,
            agent_reviews=[],
            baseline_reviews=[],
        )

        # Results should be identical
        assert result1.traditional_metrics == result2.traditional_metrics
        assert result1.graph_metrics == result2.graph_metrics


class TestPipelineResultCollection:
    """Test pipeline collects results from all modules."""

    @pytest.mark.anyio
    async def test_pipeline_result_has_run_id(self):
        """Test pipeline result includes unique run ID."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        result = await pipeline.run(
            agent_runs=[], interactions=[], agent_reviews=[], baseline_reviews=[]
        )

        assert result.run_id is not None
        assert isinstance(result.run_id, str)
        assert len(result.run_id) > 0

    @pytest.mark.anyio
    async def test_pipeline_result_has_timestamp(self):
        """Test pipeline result includes execution timestamp."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        before = datetime.now()
        result = await pipeline.run(
            agent_runs=[], interactions=[], agent_reviews=[], baseline_reviews=[]
        )
        after = datetime.now()

        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)
        assert before <= result.timestamp <= after

    @pytest.mark.anyio
    async def test_pipeline_passes_results_to_reporting(self):
        """Test pipeline result can be passed to reporting module."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        result = await pipeline.run(
            agent_runs=[], interactions=[], agent_reviews=[], baseline_reviews=[]
        )

        # Result should be serializable (for reporting module)
        result_dict = result.model_dump()
        assert "run_id" in result_dict
        assert "timestamp" in result_dict
        assert "traditional_metrics" in result_dict
        assert "llm_judge_results" in result_dict
        assert "graph_metrics" in result_dict


class TestPipelineEdgeCases:
    """Test pipeline handles edge cases gracefully."""

    @pytest.mark.anyio
    async def test_pipeline_handles_empty_inputs(self):
        """Test pipeline handles all empty inputs gracefully."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        result = await pipeline.run(
            agent_runs=[], interactions=[], agent_reviews=[], baseline_reviews=[]
        )

        assert result is not None
        assert result.traditional_metrics is not None
        assert result.llm_judge_results == []
        assert result.graph_metrics is not None

    @pytest.mark.anyio
    async def test_pipeline_handles_mismatched_review_lengths(self):
        """Test pipeline raises error for mismatched review list lengths."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        agent_reviews = [
            AgentReview(
                review_id="review1",
                paper_id="paper1",
                rating=8,
                confidence=4,
                review_text="Good paper.",
            ),
        ]

        # Empty baseline reviews (mismatch)
        baseline_reviews = []

        with pytest.raises(ValueError, match="Mismatched lengths"):
            await pipeline.run(
                agent_runs=[],
                interactions=[],
                agent_reviews=agent_reviews,
                baseline_reviews=baseline_reviews,
            )

    @pytest.mark.anyio
    async def test_pipeline_handles_partial_data(self):
        """Test pipeline handles partial data (only some tiers have data)."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(seed=42)
        pipeline = EvaluationPipeline(config)

        # Only traditional metrics data
        agent_runs = [
            {
                "agent_id": "agent1",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, 5, 0),
                "task_completed": True,
            }
        ]

        result = await pipeline.run(
            agent_runs=agent_runs,
            interactions=[],  # No graph data
            agent_reviews=[],  # No LLM judge data
            baseline_reviews=[],
        )

        # Should handle gracefully with defaults for missing tiers
        assert result.traditional_metrics["success_rate"] > 0
        assert result.llm_judge_results == []
        assert result.graph_metrics["num_nodes"] == 0
