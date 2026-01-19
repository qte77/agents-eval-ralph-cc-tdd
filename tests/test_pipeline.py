"""Tests for unified evaluation pipeline orchestration.

Following TDD RED phase - these tests should FAIL until implementation is complete.
"""

from datetime import datetime

import pytest


class TestPipelineModels:
    """Test Pydantic models for pipeline configuration and results."""

    def test_pipeline_config_model(self):
        """Test PipelineConfig model with all configuration options."""
        from agenteval.pipeline import PipelineConfig

        config = PipelineConfig(
            seed=42,
            enable_traditional_metrics=True,
            enable_llm_judge=True,
            enable_graph_metrics=True,
            llm_model="test",
        )

        assert config.seed == 42
        assert config.enable_traditional_metrics is True
        assert config.enable_llm_judge is True
        assert config.enable_graph_metrics is True
        assert config.llm_model == "test"

    def test_pipeline_config_defaults(self):
        """Test PipelineConfig with default values."""
        from agenteval.pipeline import PipelineConfig

        config = PipelineConfig()

        assert config.seed is not None
        assert config.enable_traditional_metrics is True
        assert config.enable_llm_judge is True
        assert config.enable_graph_metrics is True

    def test_pipeline_result_model(self):
        """Test PipelineResult model with all tier results."""
        from agenteval.pipeline import PipelineResult

        result = PipelineResult(
            run_id="test_run_1",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            config={"seed": 42},
            traditional_metrics={"success_rate": 0.95},
            llm_judge_results={"avg_score": 8.5},
            graph_metrics={"density": 0.75},
            execution_time=123.45,
        )

        assert result.run_id == "test_run_1"
        assert result.traditional_metrics["success_rate"] == 0.95
        assert result.llm_judge_results["avg_score"] == 8.5
        assert result.graph_metrics["density"] == 0.75
        assert result.execution_time == 123.45


class TestEvaluationPipeline:
    """Test unified evaluation pipeline orchestration."""

    @pytest.mark.anyio
    async def test_pipeline_runs_all_tiers(self):
        """Test that pipeline runs all three evaluation tiers in sequence."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        from agenteval.metrics.graph import AgentInteraction
        from agenteval.metrics.traditional import AgentTaskResult, CoordinationEvent

        config = PipelineConfig(seed=42, llm_model="test")
        pipeline = EvaluationPipeline(config)

        # Create minimal test data
        task_results = [
            AgentTaskResult(
                agent_id="agent_1",
                task_id="task_1",
                start_time=datetime(2024, 1, 1, 12, 0, 0),
                end_time=datetime(2024, 1, 1, 12, 0, 5),
                success=True,
                output="Test output",
            )
        ]

        coordination_events = [
            CoordinationEvent(
                from_agent="agent_1",
                to_agent="agent_2",
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
                event_type="message",
                successful=True,
            )
        ]

        interactions = [
            AgentInteraction(
                from_agent="agent_1",
                to_agent="agent_2",
                interaction_type="message",
                timestamp=1704110400.0,
                metadata={},
            )
        ]

        result = await pipeline.run(
            task_results=task_results,
            coordination_events=coordination_events,
            interactions=interactions,
        )

        # Verify all tiers ran
        assert result.traditional_metrics is not None
        assert result.llm_judge_results is not None
        assert result.graph_metrics is not None
        assert result.run_id is not None
        assert result.execution_time > 0

    @pytest.mark.anyio
    async def test_pipeline_reproducible_with_seed(self):
        """Test that pipeline produces reproducible results with same seed."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        from agenteval.metrics.graph import AgentInteraction
        from agenteval.metrics.traditional import AgentTaskResult, CoordinationEvent

        # Run pipeline twice with same seed
        config1 = PipelineConfig(seed=42, llm_model="test")
        config2 = PipelineConfig(seed=42, llm_model="test")

        pipeline1 = EvaluationPipeline(config1)
        pipeline2 = EvaluationPipeline(config2)

        task_results = [
            AgentTaskResult(
                agent_id="agent_1",
                task_id="task_1",
                start_time=datetime(2024, 1, 1, 12, 0, 0),
                end_time=datetime(2024, 1, 1, 12, 0, 5),
                success=True,
                output="Test output",
            )
        ]

        coordination_events = [
            CoordinationEvent(
                from_agent="agent_1",
                to_agent="agent_2",
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
                event_type="message",
                successful=True,
            )
        ]

        interactions = [
            AgentInteraction(
                from_agent="agent_1",
                to_agent="agent_2",
                interaction_type="message",
                timestamp=1704110400.0,
                metadata={},
            )
        ]

        result1 = await pipeline1.run(
            task_results=task_results,
            coordination_events=coordination_events,
            interactions=interactions,
        )

        result2 = await pipeline2.run(
            task_results=task_results,
            coordination_events=coordination_events,
            interactions=interactions,
        )

        # Verify both pipelines used the same seed
        assert result1.config["seed"] == result2.config["seed"] == 42

    @pytest.mark.anyio
    async def test_pipeline_selective_tiers(self):
        """Test that pipeline can run with selective tiers enabled."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        from agenteval.metrics.graph import AgentInteraction
        from agenteval.metrics.traditional import AgentTaskResult, CoordinationEvent

        # Only enable traditional metrics
        config = PipelineConfig(
            seed=42,
            enable_traditional_metrics=True,
            enable_llm_judge=False,
            enable_graph_metrics=False,
        )
        pipeline = EvaluationPipeline(config)

        task_results = [
            AgentTaskResult(
                agent_id="agent_1",
                task_id="task_1",
                start_time=datetime(2024, 1, 1, 12, 0, 0),
                end_time=datetime(2024, 1, 1, 12, 0, 5),
                success=True,
                output="Test output",
            )
        ]

        coordination_events = [
            CoordinationEvent(
                from_agent="agent_1",
                to_agent="agent_2",
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
                event_type="message",
                successful=True,
            )
        ]

        interactions = [
            AgentInteraction(
                from_agent="agent_1",
                to_agent="agent_2",
                interaction_type="message",
                timestamp=1704110400.0,
                metadata={},
            )
        ]

        result = await pipeline.run(
            task_results=task_results,
            coordination_events=coordination_events,
            interactions=interactions,
        )

        # Verify only traditional metrics ran
        assert result.traditional_metrics is not None
        assert result.llm_judge_results is None
        assert result.graph_metrics is None


class TestConsolidatedReport:
    """Test consolidated evaluation report generation."""

    def test_report_generator_model(self):
        """Test ReportGenerator can create consolidated reports."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        assert generator is not None

    def test_generate_json_report(self):
        """Test generating JSON report from pipeline results."""
        from agenteval.pipeline import PipelineResult
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()

        result = PipelineResult(
            run_id="test_run_1",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            config={"seed": 42},
            traditional_metrics={"success_rate": 0.95},
            llm_judge_results={"avg_score": 8.5},
            graph_metrics={"density": 0.75},
            execution_time=123.45,
        )

        report_json = generator.generate_json(result)

        # Verify JSON structure
        assert "run_id" in report_json
        assert "timestamp" in report_json
        assert "traditional_metrics" in report_json
        assert "llm_judge_results" in report_json
        assert "graph_metrics" in report_json
        assert "execution_time" in report_json

    def test_generate_summary_report(self):
        """Test generating human-readable summary report."""
        from agenteval.pipeline import PipelineResult
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()

        result = PipelineResult(
            run_id="test_run_1",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            config={"seed": 42},
            traditional_metrics={"success_rate": 0.95, "avg_execution_time": 5.0},
            llm_judge_results={"avg_score": 8.5},
            graph_metrics={"density": 0.75},
            execution_time=123.45,
        )

        summary = generator.generate_summary(result)

        # Verify summary contains key information
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "test_run_1" in summary


class TestObservability:
    """Test observability features with loguru tracing."""

    @pytest.mark.anyio
    async def test_pipeline_with_loguru_tracing(self):
        """Test that pipeline uses loguru for local console tracing."""
        from agenteval.pipeline import EvaluationPipeline, PipelineConfig

        from agenteval.metrics.graph import AgentInteraction
        from agenteval.metrics.traditional import AgentTaskResult, CoordinationEvent

        config = PipelineConfig(seed=42, llm_model="test")
        pipeline = EvaluationPipeline(config)

        # Verify pipeline has logger attribute
        assert hasattr(pipeline, "logger")

        task_results = [
            AgentTaskResult(
                agent_id="agent_1",
                task_id="task_1",
                start_time=datetime(2024, 1, 1, 12, 0, 0),
                end_time=datetime(2024, 1, 1, 12, 0, 5),
                success=True,
                output="Test output",
            )
        ]

        coordination_events = [
            CoordinationEvent(
                from_agent="agent_1",
                to_agent="agent_2",
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
                event_type="message",
                successful=True,
            )
        ]

        interactions = [
            AgentInteraction(
                from_agent="agent_1",
                to_agent="agent_2",
                interaction_type="message",
                timestamp=1704110400.0,
                metadata={},
            )
        ]

        # Should run without errors with logging
        result = await pipeline.run(
            task_results=task_results,
            coordination_events=coordination_events,
            interactions=interactions,
        )

        assert result is not None
