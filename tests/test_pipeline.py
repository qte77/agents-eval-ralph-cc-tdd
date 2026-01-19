"""Tests for unified evaluation pipeline.

Following TDD RED phase - these tests should FAIL until implementation is complete.
"""

import pytest
from unittest.mock import Mock, patch


class TestEvaluationPipeline:
    """Test unified evaluation pipeline orchestration."""

    def test_pipeline_initialization(self):
        """Test pipeline can be initialized with default config."""
        from agenteval.pipeline import EvaluationPipeline

        pipeline = EvaluationPipeline()

        assert pipeline is not None
        assert hasattr(pipeline, "run")

    def test_pipeline_with_seed_configuration(self):
        """Test pipeline supports seed-based reproducibility."""
        from agenteval.pipeline import EvaluationPipeline

        pipeline = EvaluationPipeline(seed=42)

        assert pipeline.seed == 42

    def test_pipeline_runs_all_three_tiers(self):
        """Test pipeline executes all three evaluation tiers in sequence."""
        from agenteval.pipeline import EvaluationPipeline

        pipeline = EvaluationPipeline(seed=42)

        result = pipeline.run(
            agent_output="Test review",
            baseline="Baseline review",
            interaction_data={"agent1": {"agent2": 1.0}}
        )

        # Verify result contains all three tiers
        assert result is not None
        assert "traditional_metrics" in result
        assert "llm_evaluation" in result
        assert "graph_analysis" in result

    def test_pipeline_returns_consolidated_results(self):
        """Test pipeline returns consolidated results from all tiers."""
        from agenteval.pipeline import EvaluationPipeline

        pipeline = EvaluationPipeline(seed=42)

        result = pipeline.run(
            agent_output="Test review",
            baseline="Baseline review",
            interaction_data={"agent1": {"agent2": 1.0}}
        )

        # Check consolidated result structure
        assert "traditional_metrics" in result
        assert "llm_evaluation" in result
        assert "graph_analysis" in result
        assert "metadata" in result
        assert result["metadata"]["seed"] == 42

    def test_pipeline_with_tracing_enabled(self):
        """Test pipeline enables local console tracing by default."""
        from agenteval.pipeline import EvaluationPipeline

        pipeline = EvaluationPipeline(enable_tracing=True)

        assert pipeline.enable_tracing is True

    def test_pipeline_with_logfire_export(self):
        """Test pipeline supports optional Logfire cloud export."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(enable_logfire=True)
        pipeline = EvaluationPipeline(config=config)

        assert pipeline.config.enable_logfire is True

    def test_pipeline_with_weave_export(self):
        """Test pipeline supports optional Weave W&B export."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        config = PipelineConfig(enable_weave=True)
        pipeline = EvaluationPipeline(config=config)

        assert pipeline.config.enable_weave is True

    def test_pipeline_error_handling(self):
        """Test pipeline handles errors gracefully."""
        from agenteval.pipeline import EvaluationPipeline

        pipeline = EvaluationPipeline()

        # Test with invalid input
        with pytest.raises(ValueError):
            pipeline.run(agent_output="", baseline="", interaction_data={})


class TestPipelineConfig:
    """Test pipeline configuration with pydantic-settings."""

    def test_config_default_values(self):
        """Test config has sensible defaults."""
        from agenteval.pipeline import PipelineConfig

        config = PipelineConfig()

        assert config.enable_logfire is False
        assert config.enable_weave is False
        assert config.log_level == "INFO"

    def test_config_from_environment(self):
        """Test config can be loaded from environment variables."""
        from agenteval.pipeline import PipelineConfig

        with patch.dict("os.environ", {"ENABLE_LOGFIRE": "true", "ENABLE_WEAVE": "true"}):
            config = PipelineConfig()

            assert config.enable_logfire is True
            assert config.enable_weave is True

    def test_config_validation(self):
        """Test config validates input values."""
        from agenteval.pipeline import PipelineConfig

        # Valid log level
        config = PipelineConfig(log_level="DEBUG")
        assert config.log_level == "DEBUG"

        # Invalid log level should raise error
        with pytest.raises(ValueError):
            PipelineConfig(log_level="INVALID")


class TestBatchPipeline:
    """Test batch evaluation pipeline."""

    def test_batch_pipeline_processes_multiple_inputs(self):
        """Test pipeline can process multiple inputs in batch."""
        from agenteval.pipeline import EvaluationPipeline

        pipeline = EvaluationPipeline(seed=42)

        results = pipeline.run_batch([
            {
                "agent_output": "Review 1",
                "baseline": "Baseline 1",
                "interaction_data": {"agent1": {"agent2": 1.0}}
            },
            {
                "agent_output": "Review 2",
                "baseline": "Baseline 2",
                "interaction_data": {"agent3": {"agent4": 0.5}}
            }
        ])

        assert len(results) == 2
        assert all("traditional_metrics" in r for r in results)
        assert all("llm_evaluation" in r for r in results)
        assert all("graph_analysis" in r for r in results)


class TestPipelineIntegration:
    """Test pipeline integration with all three tiers."""

    def test_pipeline_with_peerread_data(self):
        """Test pipeline can process PeerRead dataset."""
        from agenteval.pipeline import EvaluationPipeline
        from agenteval.data.peerread import PeerReadLoader

        loader = PeerReadLoader()
        data = loader.load(split="train", max_samples=1, require_reviews=True)

        pipeline = EvaluationPipeline(seed=42)

        if data:
            pair = data[0]
            result = pipeline.run(
                agent_output=pair.reviews[0].comments,
                baseline=pair.reviews[0].comments,
                interaction_data={"agent1": {"agent2": 1.0}}
            )

            assert result is not None
            assert "traditional_metrics" in result
            assert "llm_evaluation" in result
            assert "graph_analysis" in result

    def test_pipeline_reproducibility_with_seed(self):
        """Test pipeline produces consistent results with same seed."""
        from agenteval.pipeline import EvaluationPipeline

        pipeline1 = EvaluationPipeline(seed=42)
        pipeline2 = EvaluationPipeline(seed=42)

        input_data = {
            "agent_output": "Test review",
            "baseline": "Baseline review",
            "interaction_data": {"agent1": {"agent2": 1.0}}
        }

        result1 = pipeline1.run(**input_data)
        result2 = pipeline2.run(**input_data)

        # Results should be identical with same seed
        assert result1["metadata"]["seed"] == result2["metadata"]["seed"]
