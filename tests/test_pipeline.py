"""Tests for evaluation pipeline orchestrator."""

from datetime import datetime
from unittest.mock import Mock, patch

from agenteval.pipeline import EvaluationPipeline


def test_pipeline_initialization():
    """Test pipeline can be initialized."""
    pipeline = EvaluationPipeline()

    assert pipeline is not None


def test_pipeline_initialization_with_seed():
    """Test pipeline initialization with custom seed for reproducibility."""
    pipeline = EvaluationPipeline(seed=42)

    assert pipeline.seed == 42


def test_pipeline_run_all_tiers():
    """Test pipeline runs all three evaluation tiers in sequence."""
    pipeline = EvaluationPipeline(seed=42)

    # Mock data for pipeline execution
    mock_task_data = {
        "start_time": datetime(2026, 1, 21, 10, 0, 0),
        "end_time": datetime(2026, 1, 21, 10, 0, 30),
        "task_results": [{"task_id": "task_1", "success": True}],
        "agent_interactions": [
            {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"}
        ],
        "agent_reviews": [],
        "human_baselines": [],
    }

    result = pipeline.run(mock_task_data)

    # Verify all three tiers executed
    assert "traditional_metrics" in result
    assert "llm_evaluations" in result
    assert "graph_metrics" in result


def test_pipeline_handles_dependencies():
    """Test pipeline handles module dependencies correctly."""
    pipeline = EvaluationPipeline(seed=42)

    mock_task_data = {
        "start_time": datetime(2026, 1, 21, 10, 0, 0),
        "end_time": datetime(2026, 1, 21, 10, 0, 30),
        "task_results": [{"task_id": "task_1", "success": True}],
        "agent_interactions": [
            {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"}
        ],
        "agent_reviews": [],
        "human_baselines": [],
    }

    # Should complete without errors even with complex dependencies
    result = pipeline.run(mock_task_data)

    assert result is not None
    assert isinstance(result, dict)


def test_pipeline_reproducible_runs():
    """Test pipeline produces reproducible results with same seed."""
    mock_task_data = {
        "start_time": datetime(2026, 1, 21, 10, 0, 0),
        "end_time": datetime(2026, 1, 21, 10, 0, 30),
        "task_results": [{"task_id": "task_1", "success": True}],
        "agent_interactions": [
            {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"}
        ],
        "agent_reviews": [],
        "human_baselines": [],
    }

    pipeline1 = EvaluationPipeline(seed=42)
    result1 = pipeline1.run(mock_task_data)

    pipeline2 = EvaluationPipeline(seed=42)
    result2 = pipeline2.run(mock_task_data)

    # Traditional and graph metrics should be identical
    assert result1["traditional_metrics"] == result2["traditional_metrics"]
    assert result1["graph_metrics"] == result2["graph_metrics"]


def test_pipeline_collects_all_results():
    """Test pipeline collects results from all modules."""
    pipeline = EvaluationPipeline(seed=42)

    mock_task_data = {
        "start_time": datetime(2026, 1, 21, 10, 0, 0),
        "end_time": datetime(2026, 1, 21, 10, 0, 30),
        "task_results": [{"task_id": "task_1", "success": True}],
        "agent_interactions": [
            {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"}
        ],
        "agent_reviews": [],
        "human_baselines": [],
    }

    result = pipeline.run(mock_task_data)

    # Traditional metrics should be collected
    assert "execution_time" in result["traditional_metrics"]
    assert "success_rate" in result["traditional_metrics"]
    assert "coordination_quality" in result["traditional_metrics"]

    # Graph metrics should be collected
    assert "density" in result["graph_metrics"]
    assert "centrality" in result["graph_metrics"]
    assert "clustering_coefficient" in result["graph_metrics"]

    # LLM evaluations should be collected (even if empty list)
    assert isinstance(result["llm_evaluations"], list)


def test_pipeline_returns_formatted_for_reporting():
    """Test pipeline returns results in format ready for reporting module."""
    pipeline = EvaluationPipeline(seed=42)

    mock_task_data = {
        "start_time": datetime(2026, 1, 21, 10, 0, 0),
        "end_time": datetime(2026, 1, 21, 10, 0, 30),
        "task_results": [{"task_id": "task_1", "success": True}],
        "agent_interactions": [
            {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"}
        ],
        "agent_reviews": [],
        "human_baselines": [],
    }

    result = pipeline.run(mock_task_data)

    # Result should have all required keys for reporting
    assert "traditional_metrics" in result
    assert "llm_evaluations" in result
    assert "graph_metrics" in result
    assert "run_metadata" in result

    # Metadata should include reproducibility info
    assert "seed" in result["run_metadata"]
    assert result["run_metadata"]["seed"] == 42


def test_pipeline_with_empty_interactions():
    """Test pipeline handles empty agent interactions gracefully."""
    pipeline = EvaluationPipeline(seed=42)

    mock_task_data = {
        "start_time": datetime(2026, 1, 21, 10, 0, 0),
        "end_time": datetime(2026, 1, 21, 10, 0, 30),
        "task_results": [{"task_id": "task_1", "success": True}],
        "agent_interactions": [],
        "agent_reviews": [],
        "human_baselines": [],
    }

    result = pipeline.run(mock_task_data)

    # Should still return valid results even with empty interactions
    assert result is not None
    assert "graph_metrics" in result


def test_pipeline_default_seed_from_config():
    """Test pipeline uses seed from config when not specified."""
    # Mock config loading
    with patch("agenteval.pipeline.load_config") as mock_load_config:
        mock_config = Mock()
        mock_config.evaluation.seed = 123
        mock_load_config.return_value = mock_config

        pipeline = EvaluationPipeline()

        assert pipeline.seed == 123


def test_pipeline_explicit_seed_overrides_config():
    """Test explicit seed parameter overrides config."""
    # Mock config loading
    with patch("agenteval.pipeline.load_config") as mock_load_config:
        mock_config = Mock()
        mock_config.evaluation.seed = 123
        mock_load_config.return_value = mock_config

        pipeline = EvaluationPipeline(seed=999)

        assert pipeline.seed == 999
