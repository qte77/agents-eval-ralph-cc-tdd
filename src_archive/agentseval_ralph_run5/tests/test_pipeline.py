"""Tests for evaluation pipeline orchestrator.

Following TDD approach - these tests should FAIL initially.
Tests validate pipeline orchestration: running evaluation modules in sequence,
dependency management, reproducibility controls, and result collection.
"""

import json

import pytest

from agenteval.models.data import Review
from agenteval.models.evaluation import Evaluation, Metrics


class TestPipeline:
    """Tests for pipeline orchestration."""

    def test_pipeline_creation_with_config(self):
        """Test creating pipeline with configuration."""
        from agenteval.pipeline import Pipeline

        pipeline = Pipeline(seed=42)

        assert pipeline is not None
        assert pipeline.seed == 42

    def test_pipeline_creation_default_seed(self):
        """Test creating pipeline with default seed."""
        from agenteval.pipeline import Pipeline

        pipeline = Pipeline()

        assert pipeline is not None
        assert pipeline.seed == 42  # Default seed from config

    def test_pipeline_run_traditional_metrics(self):
        """Test pipeline runs traditional metrics evaluation."""
        from agenteval.pipeline import Pipeline

        pipeline = Pipeline(seed=42)

        # Mock traditional metrics input
        traditional_input = {
            "start_time": 100.0,
            "end_time": 150.0,
            "task_results": [True, True, False, True],
            "coordination_events": [
                {"agent_id": "agent1", "timestamp": 100.0, "success": True},
                {"agent_id": "agent2", "timestamp": 101.0, "success": True},
            ],
        }

        result = pipeline.run_traditional_metrics(traditional_input)

        assert result is not None
        assert isinstance(result, Metrics)
        assert result.execution_time_seconds == 50.0
        assert result.success_rate == 0.75

    def test_pipeline_run_llm_judge(self):
        """Test pipeline runs LLM judge evaluation."""
        from agenteval.pipeline import Pipeline

        pipeline = Pipeline(seed=42)

        # Mock LLM judge input
        agent_review = Review(
            id="agent_review_1",
            paper_id="paper_001",
            rating=8,
            confidence=4,
            review_text="This paper presents a novel approach to machine learning.",
        )
        baseline_review = Review(
            id="baseline_review_1",
            paper_id="paper_001",
            rating=9,
            confidence=5,
            review_text="This work introduces an innovative methodology for ML applications.",
        )

        result = pipeline.run_llm_judge(agent_review, baseline_review)

        assert result is not None
        assert isinstance(result, Evaluation)
        assert result.review_id == "agent_review_1"
        assert result.baseline_review_id == "baseline_review_1"
        assert 0.0 <= result.semantic_score <= 1.0

    def test_pipeline_run_graph_analysis(self):
        """Test pipeline runs graph-based complexity analysis."""
        from agenteval.pipeline import Pipeline

        pipeline = Pipeline(seed=42)

        # Mock graph analysis input
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent2", "target": "agent3", "timestamp": 101.0, "type": "message"},
            {"source": "agent3", "target": "agent1", "timestamp": 102.0, "type": "message"},
        ]

        result = pipeline.run_graph_analysis(interactions)

        assert result is not None
        assert isinstance(result, dict)
        assert "density" in result
        assert "centrality" in result
        assert "clustering_coefficient" in result
        assert "coordination_patterns" in result

    def test_pipeline_run_all_evaluations(self):
        """Test pipeline runs all three evaluation tiers in sequence."""
        from agenteval.pipeline import Pipeline

        pipeline = Pipeline(seed=42)

        # Mock inputs for all three tiers
        traditional_input = {
            "start_time": 100.0,
            "end_time": 150.0,
            "task_results": [True, True, True],
            "coordination_events": [
                {"agent_id": "agent1", "timestamp": 100.0, "success": True}
            ],
        }

        agent_review = Review(
            id="agent_review_1",
            paper_id="paper_001",
            rating=8,
            confidence=4,
            review_text="Good paper.",
        )
        baseline_review = Review(
            id="baseline_review_1",
            paper_id="paper_001",
            rating=9,
            confidence=5,
            review_text="Excellent paper.",
        )

        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
        ]

        result = pipeline.run_all(
            traditional_input=traditional_input,
            agent_review=agent_review,
            baseline_review=baseline_review,
            interactions=interactions,
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "traditional_metrics" in result
        assert "llm_evaluation" in result
        assert "graph_metrics" in result
        assert isinstance(result["traditional_metrics"], Metrics)
        assert isinstance(result["llm_evaluation"], Evaluation)
        assert isinstance(result["graph_metrics"], dict)

    def test_pipeline_handles_dependencies_correctly(self):
        """Test that pipeline respects module dependencies."""
        from agenteval.pipeline import Pipeline

        pipeline = Pipeline(seed=42)

        # Traditional metrics should run first
        # LLM judge and graph analysis depend on Story 3,4,5
        # All should be available in the pipeline

        traditional_input = {
            "start_time": 100.0,
            "end_time": 150.0,
            "task_results": [True],
            "coordination_events": [
                {"agent_id": "agent1", "timestamp": 100.0, "success": True}
            ],
        }

        # Should not raise any dependency errors
        result = pipeline.run_traditional_metrics(traditional_input)
        assert result is not None

    def test_pipeline_reproducibility_with_seed(self):
        """Test that pipeline produces reproducible results with same seed."""
        from agenteval.pipeline import Pipeline

        pipeline1 = Pipeline(seed=123)
        pipeline2 = Pipeline(seed=123)

        traditional_input = {
            "start_time": 100.0,
            "end_time": 150.0,
            "task_results": [True, False, True],
            "coordination_events": [
                {"agent_id": "agent1", "timestamp": 100.0, "success": True}
            ],
        }

        result1 = pipeline1.run_traditional_metrics(traditional_input)
        result2 = pipeline2.run_traditional_metrics(traditional_input)

        # Results should be identical with same seed
        assert result1.execution_time_seconds == result2.execution_time_seconds
        assert result1.success_rate == result2.success_rate
        assert result1.coordination_quality == result2.coordination_quality

    def test_pipeline_collects_all_results(self):
        """Test that pipeline collects results from all modules."""
        from agenteval.pipeline import Pipeline

        pipeline = Pipeline(seed=42)

        traditional_input = {
            "start_time": 100.0,
            "end_time": 150.0,
            "task_results": [True, True],
            "coordination_events": [
                {"agent_id": "agent1", "timestamp": 100.0, "success": True}
            ],
        }

        agent_review = Review(
            id="agent_review_1",
            paper_id="paper_001",
            rating=7,
            confidence=4,
            review_text="Test review.",
        )
        baseline_review = Review(
            id="baseline_review_1",
            paper_id="paper_001",
            rating=8,
            confidence=5,
            review_text="Test baseline.",
        )

        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
        ]

        result = pipeline.run_all(
            traditional_input=traditional_input,
            agent_review=agent_review,
            baseline_review=baseline_review,
            interactions=interactions,
        )

        # Verify all results are collected
        assert "traditional_metrics" in result
        assert "llm_evaluation" in result
        assert "graph_metrics" in result

        # Verify types
        assert isinstance(result["traditional_metrics"], Metrics)
        assert isinstance(result["llm_evaluation"], Evaluation)
        assert isinstance(result["graph_metrics"], dict)

    def test_pipeline_passes_results_to_reporting(self):
        """Test that pipeline returns results in format suitable for reporting module."""
        from agenteval.pipeline import Pipeline

        pipeline = Pipeline(seed=42)

        traditional_input = {
            "start_time": 100.0,
            "end_time": 150.0,
            "task_results": [True],
            "coordination_events": [
                {"agent_id": "agent1", "timestamp": 100.0, "success": True}
            ],
        }

        agent_review = Review(
            id="agent_review_1",
            paper_id="paper_001",
            rating=7,
            confidence=4,
            review_text="Test.",
        )
        baseline_review = Review(
            id="baseline_review_1",
            paper_id="paper_001",
            rating=8,
            confidence=5,
            review_text="Test baseline.",
        )

        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
        ]

        result = pipeline.run_all(
            traditional_input=traditional_input,
            agent_review=agent_review,
            baseline_review=baseline_review,
            interactions=interactions,
        )

        # Result should be JSON serializable for reporting
        json_str = json.dumps(
            {
                "traditional_metrics": result["traditional_metrics"].model_dump(),
                "llm_evaluation": result["llm_evaluation"].model_dump(),
                "graph_metrics": result["graph_metrics"],
            }
        )
        parsed = json.loads(json_str)

        assert "traditional_metrics" in parsed
        assert "llm_evaluation" in parsed
        assert "graph_metrics" in parsed


class TestPipelineBatchProcessing:
    """Tests for batch processing through pipeline."""

    def test_pipeline_run_batch_evaluations(self):
        """Test pipeline handles batch processing of multiple inputs."""
        from agenteval.pipeline import Pipeline

        pipeline = Pipeline(seed=42)

        # Multiple review pairs for batch processing
        review_pairs = [
            {
                "agent_review": Review(
                    id="agent_1",
                    paper_id="paper_1",
                    rating=7,
                    confidence=4,
                    review_text="Good paper.",
                ),
                "baseline_review": Review(
                    id="baseline_1",
                    paper_id="paper_1",
                    rating=8,
                    confidence=5,
                    review_text="Excellent paper.",
                ),
            },
            {
                "agent_review": Review(
                    id="agent_2",
                    paper_id="paper_2",
                    rating=5,
                    confidence=3,
                    review_text="Needs improvement.",
                ),
                "baseline_review": Review(
                    id="baseline_2",
                    paper_id="paper_2",
                    rating=6,
                    confidence=4,
                    review_text="Could be better.",
                ),
            },
        ]

        results = pipeline.run_llm_judge_batch(review_pairs)

        assert len(results) == 2
        assert all(isinstance(r, Evaluation) for r in results)
        assert results[0].review_id == "agent_1"
        assert results[1].review_id == "agent_2"
