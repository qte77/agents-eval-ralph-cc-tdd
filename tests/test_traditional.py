"""Tests for traditional performance metrics.

Tests calculation of execution time, task success rate, coordination quality,
and batch evaluation of multiple agent outputs.
"""

import pytest

from agenteval.metrics.traditional import (
    calculate_execution_time,
    calculate_task_success_rate,
    assess_coordination_quality,
    evaluate_batch,
)
from agenteval.models.evaluation import Metrics


def test_calculate_execution_time():
    """Test execution time calculation."""
    start_time = 1000.0
    end_time = 1010.5

    execution_time = calculate_execution_time(start_time, end_time)

    assert execution_time == 10.5
    assert isinstance(execution_time, float)


def test_calculate_execution_time_zero():
    """Test execution time when start and end are the same."""
    start_time = 1000.0
    end_time = 1000.0

    execution_time = calculate_execution_time(start_time, end_time)

    assert execution_time == 0.0


def test_calculate_task_success_rate():
    """Test task success rate calculation."""
    completed_tasks = 8
    total_tasks = 10

    success_rate = calculate_task_success_rate(completed_tasks, total_tasks)

    assert success_rate == 0.8
    assert isinstance(success_rate, float)
    assert 0.0 <= success_rate <= 1.0


def test_calculate_task_success_rate_all_success():
    """Test success rate when all tasks succeed."""
    success_rate = calculate_task_success_rate(10, 10)

    assert success_rate == 1.0


def test_calculate_task_success_rate_all_fail():
    """Test success rate when all tasks fail."""
    success_rate = calculate_task_success_rate(0, 10)

    assert success_rate == 0.0


def test_calculate_task_success_rate_zero_total():
    """Test success rate with zero total tasks."""
    success_rate = calculate_task_success_rate(0, 0)

    assert success_rate == 0.0


def test_assess_coordination_quality():
    """Test coordination quality assessment."""
    agent_interactions = [
        {"agent_a": "reviewer", "agent_b": "summarizer", "success": True},
        {"agent_a": "summarizer", "agent_b": "validator", "success": True},
        {"agent_a": "reviewer", "agent_b": "validator", "success": False},
    ]

    quality = assess_coordination_quality(agent_interactions)

    assert isinstance(quality, float)
    assert 0.0 <= quality <= 1.0
    assert quality == pytest.approx(2.0 / 3.0, abs=0.01)


def test_assess_coordination_quality_perfect():
    """Test coordination quality with all successful interactions."""
    agent_interactions = [
        {"agent_a": "agent1", "agent_b": "agent2", "success": True},
        {"agent_a": "agent2", "agent_b": "agent3", "success": True},
    ]

    quality = assess_coordination_quality(agent_interactions)

    assert quality == 1.0


def test_assess_coordination_quality_empty():
    """Test coordination quality with no interactions."""
    quality = assess_coordination_quality([])

    assert quality == 0.0


def test_evaluate_batch():
    """Test batch evaluation of multiple agent outputs."""
    agent_outputs = [
        {
            "start_time": 1000.0,
            "end_time": 1010.0,
            "completed_tasks": 5,
            "total_tasks": 5,
            "interactions": [
                {"agent_a": "a1", "agent_b": "a2", "success": True},
            ],
        },
        {
            "start_time": 2000.0,
            "end_time": 2015.0,
            "completed_tasks": 8,
            "total_tasks": 10,
            "interactions": [
                {"agent_a": "a1", "agent_b": "a2", "success": True},
                {"agent_a": "a2", "agent_b": "a3", "success": False},
            ],
        },
    ]

    results = evaluate_batch(agent_outputs)

    assert isinstance(results, list)
    assert len(results) == 2

    # First result
    assert isinstance(results[0], Metrics)
    assert results[0].execution_time_seconds == 10.0
    assert results[0].task_success_rate == 1.0
    assert results[0].coordination_quality == 1.0

    # Second result
    assert isinstance(results[1], Metrics)
    assert results[1].execution_time_seconds == 15.0
    assert results[1].task_success_rate == 0.8
    assert results[1].coordination_quality == 0.5


def test_evaluate_batch_empty():
    """Test batch evaluation with empty input."""
    results = evaluate_batch([])

    assert isinstance(results, list)
    assert len(results) == 0


def test_metrics_output_json_format():
    """Test that metrics can be output in JSON format."""
    metrics = Metrics(
        execution_time_seconds=10.5,
        task_success_rate=0.9,
        coordination_quality=0.85,
        semantic_similarity=None,
        graph_density=None,
        graph_centrality=None,
    )

    json_data = metrics.model_dump()

    assert isinstance(json_data, dict)
    assert json_data["execution_time_seconds"] == 10.5
    assert json_data["task_success_rate"] == 0.9
    assert json_data["coordination_quality"] == 0.85
