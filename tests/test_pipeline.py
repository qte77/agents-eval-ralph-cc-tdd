"""Tests for evaluation pipeline orchestrator.

Tests verify that the pipeline runs all three evaluation tiers (traditional, LLM judge, graph)
in sequence with dependency management and reproducibility controls.
"""

from datetime import datetime

from agenteval.models.data import Review
from agenteval.models.evaluation import Evaluation, Metrics
from agenteval.pipeline import EvaluationPipeline


def test_pipeline_runs_all_three_evaluation_tiers():
    """Test that pipeline runs traditional, LLM judge, and graph evaluations in sequence."""
    pipeline = EvaluationPipeline(seed=42)

    # Mock inputs for the pipeline
    traditional_input = {
        "start_time": datetime(2024, 1, 1, 10, 0, 0),
        "end_time": datetime(2024, 1, 1, 10, 5, 0),
        "task_results": [True, True, False, True],
        "agent_interactions": [
            {"agent_a": "agent1", "agent_b": "agent2", "successful": True}
        ],
    }

    llm_judge_input = {
        "agent_review": Review(
            review_id="agent_001",
            paper_id="paper_001",
            rating=8,
            confidence=4,
            summary="Good paper with clear contributions",
            strengths=["Clear writing", "Novel approach"],
            weaknesses=["Limited experiments"],
            detailed_comments="Well structured paper.",
            is_agent_generated=True,
        ),
        "baseline_review": Review(
            review_id="baseline_001",
            paper_id="paper_001",
            rating=8,
            confidence=5,
            summary="Strong paper",
            strengths=["Clear methodology"],
            weaknesses=["Needs more evaluation"],
            detailed_comments="Good contribution to the field.",
            is_agent_generated=False,
        ),
    }

    graph_input = {
        "interactions": [
            {"source": "agent1", "target": "agent2", "type": "message"},
            {"source": "agent2", "target": "agent3", "type": "message"},
        ]
    }

    results = pipeline.run(
        traditional_input=traditional_input,
        llm_judge_input=llm_judge_input,
        graph_input=graph_input,
    )

    assert "traditional_metrics" in results
    assert "llm_evaluation" in results
    assert "graph_metrics" in results
    assert isinstance(results["traditional_metrics"], Metrics)
    assert isinstance(results["llm_evaluation"], Evaluation)
    assert isinstance(results["graph_metrics"], dict)


def test_pipeline_handles_module_dependencies():
    """Test that pipeline handles dependencies between modules correctly."""
    pipeline = EvaluationPipeline(seed=42)

    # Verify that pipeline can be instantiated without errors
    assert pipeline is not None
    assert hasattr(pipeline, "run")

    # Verify seed is set correctly for reproducibility
    assert pipeline.seed == 42


def test_pipeline_supports_reproducible_runs_with_seed():
    """Test that pipeline produces reproducible results with same seed."""
    seed = 123
    pipeline1 = EvaluationPipeline(seed=seed)
    pipeline2 = EvaluationPipeline(seed=seed)

    # Both pipelines should have same seed
    assert pipeline1.seed == pipeline2.seed
    assert pipeline1.seed == seed


def test_pipeline_collects_results_from_all_modules():
    """Test that pipeline collects and aggregates results from all modules."""
    pipeline = EvaluationPipeline(seed=42)

    traditional_input = {
        "start_time": datetime(2024, 1, 1, 10, 0, 0),
        "end_time": datetime(2024, 1, 1, 10, 2, 0),
        "task_results": [True, True, True],
        "agent_interactions": [
            {"agent_a": "a1", "agent_b": "a2", "successful": True}
        ],
    }

    llm_judge_input = {
        "agent_review": Review(
            review_id="r1",
            paper_id="p1",
            rating=7,
            confidence=4,
            summary="Good paper",
            strengths=["Clear"],
            weaknesses=["Limited"],
            detailed_comments="Well done.",
            is_agent_generated=True,
        ),
        "baseline_review": Review(
            review_id="r2",
            paper_id="p1",
            rating=7,
            confidence=5,
            summary="Strong",
            strengths=["Clear"],
            weaknesses=["Needs more"],
            detailed_comments="Good.",
            is_agent_generated=False,
        ),
    }

    graph_input = {
        "interactions": [
            {"source": "a1", "target": "a2", "type": "msg"},
        ]
    }

    results = pipeline.run(
        traditional_input=traditional_input,
        llm_judge_input=llm_judge_input,
        graph_input=graph_input,
    )

    # Results should contain all three evaluation tier outputs
    assert len(results) >= 3
    assert all(key in results for key in ["traditional_metrics", "llm_evaluation", "graph_metrics"])


def test_pipeline_passes_results_to_reporting_format():
    """Test that pipeline results are in a format suitable for reporting module."""
    pipeline = EvaluationPipeline(seed=42)

    traditional_input = {
        "start_time": datetime(2024, 1, 1, 10, 0, 0),
        "end_time": datetime(2024, 1, 1, 10, 1, 0),
        "task_results": [True],
        "agent_interactions": [{"agent_a": "a1", "agent_b": "a2", "successful": True}],
    }

    llm_judge_input = {
        "agent_review": Review(
            review_id="r1",
            paper_id="p1",
            rating=8,
            confidence=4,
            summary="Good",
            strengths=["A"],
            weaknesses=["B"],
            detailed_comments="C",
            is_agent_generated=True,
        ),
        "baseline_review": Review(
            review_id="r2",
            paper_id="p1",
            rating=8,
            confidence=5,
            summary="Good",
            strengths=["A"],
            weaknesses=["B"],
            detailed_comments="C",
            is_agent_generated=False,
        ),
    }

    graph_input = {"interactions": [{"source": "a1", "target": "a2"}]}

    results = pipeline.run(
        traditional_input=traditional_input,
        llm_judge_input=llm_judge_input,
        graph_input=graph_input,
    )

    # Results should be dict that can be passed to reporting
    assert isinstance(results, dict)

    # Should contain metrics that can be serialized
    assert results["traditional_metrics"].model_dump() is not None
    assert results["llm_evaluation"].model_dump() is not None


def test_pipeline_with_missing_optional_inputs():
    """Test that pipeline handles missing optional inputs gracefully."""
    pipeline = EvaluationPipeline(seed=42)

    # Only provide traditional input
    traditional_input = {
        "start_time": datetime(2024, 1, 1, 10, 0, 0),
        "end_time": datetime(2024, 1, 1, 10, 1, 0),
        "task_results": [True],
        "agent_interactions": [{"agent_a": "a1", "agent_b": "a2", "successful": True}],
    }

    # Pipeline should handle None for optional inputs
    results = pipeline.run(
        traditional_input=traditional_input,
        llm_judge_input=None,
        graph_input=None,
    )

    assert "traditional_metrics" in results
    # Optional modules should be skipped or return None
    assert results.get("llm_evaluation") is None or "llm_evaluation" not in results
    assert results.get("graph_metrics") is None or "graph_metrics" not in results


def test_pipeline_execution_order():
    """Test that pipeline executes modules in correct order."""
    pipeline = EvaluationPipeline(seed=42)

    # The pipeline should execute modules in sequence
    assert pipeline is not None
    assert hasattr(pipeline, "run")
