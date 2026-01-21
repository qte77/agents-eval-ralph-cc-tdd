"""Tests for traditional performance metrics module.

Tests verify execution time calculation, success rate measurement,
coordination quality assessment, structured JSON output, and batch evaluation.
"""

from datetime import datetime

import pytest
from agenteval.metrics.traditional import (  # type: ignore[import-not-found]
    TraditionalMetrics,
    calculate_metrics,
)
from agenteval.models.evaluation import Metrics


def test_calculate_execution_time_metrics():
    """Test that execution time is calculated correctly from start/end timestamps."""
    start_time = datetime(2024, 1, 1, 10, 0, 0)
    end_time = datetime(2024, 1, 1, 10, 5, 30)

    metrics_calculator = TraditionalMetrics()
    result = metrics_calculator.calculate_execution_time(start_time, end_time)

    # 5 minutes 30 seconds = 330 seconds
    assert result == 330.0
    assert isinstance(result, float)


def test_calculate_task_success_rate():
    """Test that task success rate is calculated across evaluation runs."""
    # Simulate 8 successful out of 10 tasks
    task_results = [True, True, False, True, True, True, False, True, True, True]

    metrics_calculator = TraditionalMetrics()
    success_rate = metrics_calculator.calculate_success_rate(task_results)

    assert success_rate == 0.8  # 8/10
    assert 0.0 <= success_rate <= 1.0


def test_calculate_task_success_rate_all_pass():
    """Test success rate when all tasks pass."""
    task_results = [True, True, True, True, True]

    metrics_calculator = TraditionalMetrics()
    success_rate = metrics_calculator.calculate_success_rate(task_results)

    assert success_rate == 1.0


def test_calculate_task_success_rate_all_fail():
    """Test success rate when all tasks fail."""
    task_results = [False, False, False]

    metrics_calculator = TraditionalMetrics()
    success_rate = metrics_calculator.calculate_success_rate(task_results)

    assert success_rate == 0.0


def test_assess_coordination_quality():
    """Test that coordination quality between agents is assessed."""
    # Mock agent interaction data
    agent_interactions = [
        {"agent_a": "agent1", "agent_b": "agent2", "successful": True},
        {"agent_a": "agent1", "agent_b": "agent3", "successful": True},
        {"agent_a": "agent2", "agent_b": "agent3", "successful": False},
    ]

    metrics_calculator = TraditionalMetrics()
    coordination_quality = metrics_calculator.assess_coordination_quality(agent_interactions)

    # 2 successful out of 3 = 0.667
    assert coordination_quality == pytest.approx(0.667, abs=0.01)
    assert 0.0 <= coordination_quality <= 1.0


def test_assess_coordination_quality_perfect():
    """Test coordination quality when all interactions succeed."""
    agent_interactions = [
        {"agent_a": "agent1", "agent_b": "agent2", "successful": True},
        {"agent_a": "agent2", "agent_b": "agent3", "successful": True},
    ]

    metrics_calculator = TraditionalMetrics()
    coordination_quality = metrics_calculator.assess_coordination_quality(agent_interactions)

    assert coordination_quality == 1.0


def test_output_metrics_in_structured_json_format():
    """Test that metrics are output in structured JSON format using Metrics model."""
    metrics_calculator = TraditionalMetrics()

    # Create metrics from various calculations
    execution_time = 120.5
    success_rate = 0.85
    coordination_quality = 0.75

    metrics = metrics_calculator.create_metrics(
        execution_time=execution_time,
        success_rate=success_rate,
        coordination_quality=coordination_quality,
    )

    assert isinstance(metrics, Metrics)
    assert metrics.execution_time_seconds == 120.5
    assert metrics.task_success_rate == 0.85
    assert metrics.coordination_quality == 0.75


def test_output_metrics_can_be_serialized_to_json():
    """Test that Metrics model can be serialized to JSON."""
    metrics = Metrics(
        execution_time_seconds=100.0, task_success_rate=0.9, coordination_quality=0.8
    )

    json_data = metrics.model_dump()

    assert isinstance(json_data, dict)
    assert json_data["execution_time_seconds"] == 100.0
    assert json_data["task_success_rate"] == 0.9
    assert json_data["coordination_quality"] == 0.8


def test_batch_evaluation_of_multiple_agent_outputs():
    """Test that metrics can be calculated for multiple agent outputs in batch."""
    # Mock multiple evaluation runs
    evaluation_runs = [
        {
            "start_time": datetime(2024, 1, 1, 10, 0, 0),
            "end_time": datetime(2024, 1, 1, 10, 2, 0),
            "task_results": [True, True, True],
            "agent_interactions": [
                {"agent_a": "a1", "agent_b": "a2", "successful": True}
            ],
        },
        {
            "start_time": datetime(2024, 1, 1, 11, 0, 0),
            "end_time": datetime(2024, 1, 1, 11, 3, 30),
            "task_results": [True, False, True],
            "agent_interactions": [
                {"agent_a": "a1", "agent_b": "a2", "successful": True},
                {"agent_a": "a1", "agent_b": "a3", "successful": False},
            ],
        },
    ]

    metrics_calculator = TraditionalMetrics()
    batch_results = metrics_calculator.evaluate_batch(evaluation_runs)

    assert len(batch_results) == 2
    assert all(isinstance(m, Metrics) for m in batch_results)

    # First run: 120 seconds, 100% success, 100% coordination
    assert batch_results[0].execution_time_seconds == 120.0
    assert batch_results[0].task_success_rate == 1.0
    assert batch_results[0].coordination_quality == 1.0

    # Second run: 210 seconds, 66.7% success, 50% coordination
    assert batch_results[1].execution_time_seconds == 210.0
    assert batch_results[1].task_success_rate == pytest.approx(0.667, abs=0.01)
    assert batch_results[1].coordination_quality == 0.5


def test_calculate_metrics_convenience_function():
    """Test convenience function for calculating all metrics at once."""
    start_time = datetime(2024, 1, 1, 10, 0, 0)
    end_time = datetime(2024, 1, 1, 10, 5, 0)
    task_results = [True, True, False, True]
    agent_interactions = [
        {"agent_a": "a1", "agent_b": "a2", "successful": True},
        {"agent_a": "a2", "agent_b": "a3", "successful": True},
    ]

    metrics = calculate_metrics(
        start_time=start_time,
        end_time=end_time,
        task_results=task_results,
        agent_interactions=agent_interactions,
    )

    assert isinstance(metrics, Metrics)
    assert metrics.execution_time_seconds == 300.0  # 5 minutes
    assert metrics.task_success_rate == 0.75  # 3/4
    assert metrics.coordination_quality == 1.0  # 2/2


def test_empty_task_results_returns_zero_success_rate():
    """Test that empty task results list returns 0.0 success rate."""
    metrics_calculator = TraditionalMetrics()
    success_rate = metrics_calculator.calculate_success_rate([])

    assert success_rate == 0.0


def test_empty_agent_interactions_returns_none_coordination():
    """Test that empty agent interactions returns None for coordination quality."""
    metrics_calculator = TraditionalMetrics()
    coordination_quality = metrics_calculator.assess_coordination_quality([])

    assert coordination_quality is None


def test_negative_execution_time_raises_error():
    """Test that negative execution time raises ValueError."""
    start_time = datetime(2024, 1, 1, 10, 5, 0)
    end_time = datetime(2024, 1, 1, 10, 0, 0)  # End before start

    metrics_calculator = TraditionalMetrics()

    with pytest.raises(ValueError, match="End time must be after start time"):
        metrics_calculator.calculate_execution_time(start_time, end_time)


def test_batch_evaluation_with_empty_list():
    """Test batch evaluation with empty list returns empty results."""
    metrics_calculator = TraditionalMetrics()
    batch_results = metrics_calculator.evaluate_batch([])

    assert batch_results == []
    assert isinstance(batch_results, list)
