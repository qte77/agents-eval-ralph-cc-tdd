"""Tests for traditional performance metrics calculation."""

from datetime import datetime

import pytest

from agenteval.metrics.traditional import (
    TraditionalMetrics,
    calculate_execution_time,
    calculate_success_rate,
    calculate_coordination_quality,
)


def test_calculate_execution_time():
    """Test execution time calculation from start and end timestamps."""
    start_time = datetime(2026, 1, 21, 10, 0, 0)
    end_time = datetime(2026, 1, 21, 10, 0, 45)

    execution_time = calculate_execution_time(start_time, end_time)

    assert execution_time == 45.0


def test_calculate_execution_time_with_milliseconds():
    """Test execution time calculation includes milliseconds."""
    start_time = datetime(2026, 1, 21, 10, 0, 0, 0)
    end_time = datetime(2026, 1, 21, 10, 0, 0, 500000)

    execution_time = calculate_execution_time(start_time, end_time)

    assert execution_time == 0.5


def test_calculate_success_rate_all_successful():
    """Test success rate when all tasks succeed."""
    task_results = [
        {"task_id": "task_1", "success": True},
        {"task_id": "task_2", "success": True},
        {"task_id": "task_3", "success": True},
    ]

    success_rate = calculate_success_rate(task_results)

    assert success_rate == 1.0


def test_calculate_success_rate_partial_success():
    """Test success rate with partial task success."""
    task_results = [
        {"task_id": "task_1", "success": True},
        {"task_id": "task_2", "success": False},
        {"task_id": "task_3", "success": True},
        {"task_id": "task_4", "success": False},
    ]

    success_rate = calculate_success_rate(task_results)

    assert success_rate == 0.5


def test_calculate_success_rate_all_failed():
    """Test success rate when all tasks fail."""
    task_results = [
        {"task_id": "task_1", "success": False},
        {"task_id": "task_2", "success": False},
    ]

    success_rate = calculate_success_rate(task_results)

    assert success_rate == 0.0


def test_calculate_success_rate_empty_results():
    """Test success rate with no task results."""
    task_results = []

    success_rate = calculate_success_rate(task_results)

    assert success_rate == 0.0


def test_calculate_coordination_quality_high():
    """Test coordination quality with low message overhead."""
    agent_interactions = [
        {"agent_id": "agent_1", "message_count": 5, "duplicate_count": 0},
        {"agent_id": "agent_2", "message_count": 6, "duplicate_count": 1},
    ]

    coordination_quality = calculate_coordination_quality(agent_interactions)

    # Quality = 1 - (duplicates / total_messages) = 1 - (1 / 11) ≈ 0.909
    assert 0.9 <= coordination_quality <= 1.0


def test_calculate_coordination_quality_low():
    """Test coordination quality with high message overhead."""
    agent_interactions = [
        {"agent_id": "agent_1", "message_count": 10, "duplicate_count": 5},
        {"agent_id": "agent_2", "message_count": 10, "duplicate_count": 5},
    ]

    coordination_quality = calculate_coordination_quality(agent_interactions)

    # Quality = 1 - (duplicates / total_messages) = 1 - (10 / 20) = 0.5
    assert coordination_quality == 0.5


def test_calculate_coordination_quality_no_duplicates():
    """Test coordination quality with perfect efficiency (no duplicates)."""
    agent_interactions = [
        {"agent_id": "agent_1", "message_count": 5, "duplicate_count": 0},
        {"agent_id": "agent_2", "message_count": 5, "duplicate_count": 0},
    ]

    coordination_quality = calculate_coordination_quality(agent_interactions)

    assert coordination_quality == 1.0


def test_calculate_coordination_quality_empty_interactions():
    """Test coordination quality with no interactions."""
    agent_interactions = []

    coordination_quality = calculate_coordination_quality(agent_interactions)

    assert coordination_quality == 0.0


def test_traditional_metrics_class_initialization():
    """Test TraditionalMetrics class can be initialized."""
    metrics = TraditionalMetrics()

    assert metrics is not None


def test_traditional_metrics_calculate_all():
    """Test calculating all metrics together."""
    metrics = TraditionalMetrics()

    start_time = datetime(2026, 1, 21, 10, 0, 0)
    end_time = datetime(2026, 1, 21, 10, 0, 30)

    task_results = [
        {"task_id": "task_1", "success": True},
        {"task_id": "task_2", "success": True},
        {"task_id": "task_3", "success": False},
    ]

    agent_interactions = [
        {"agent_id": "agent_1", "message_count": 10, "duplicate_count": 2},
        {"agent_id": "agent_2", "message_count": 8, "duplicate_count": 1},
    ]

    result = metrics.calculate_all(
        start_time=start_time,
        end_time=end_time,
        task_results=task_results,
        agent_interactions=agent_interactions,
    )

    assert result["execution_time"] == 30.0
    assert result["success_rate"] == pytest.approx(0.6667, rel=0.01)
    assert result["coordination_quality"] == pytest.approx(0.8333, rel=0.01)


def test_traditional_metrics_to_json():
    """Test metrics can be output in structured JSON format."""
    metrics = TraditionalMetrics()

    start_time = datetime(2026, 1, 21, 10, 0, 0)
    end_time = datetime(2026, 1, 21, 10, 0, 15)

    task_results = [
        {"task_id": "task_1", "success": True},
    ]

    agent_interactions = [
        {"agent_id": "agent_1", "message_count": 5, "duplicate_count": 0},
    ]

    result = metrics.calculate_all(
        start_time=start_time,
        end_time=end_time,
        task_results=task_results,
        agent_interactions=agent_interactions,
    )

    json_output = metrics.to_json(result)

    assert isinstance(json_output, str)
    assert "execution_time" in json_output
    assert "success_rate" in json_output
    assert "coordination_quality" in json_output


def test_traditional_metrics_batch_evaluation():
    """Test batch evaluation of multiple agent outputs."""
    metrics = TraditionalMetrics()

    # Multiple evaluation runs
    evaluations = [
        {
            "run_id": "run_1",
            "start_time": datetime(2026, 1, 21, 10, 0, 0),
            "end_time": datetime(2026, 1, 21, 10, 0, 30),
            "task_results": [{"task_id": "t1", "success": True}],
            "agent_interactions": [{"agent_id": "a1", "message_count": 5, "duplicate_count": 0}],
        },
        {
            "run_id": "run_2",
            "start_time": datetime(2026, 1, 21, 11, 0, 0),
            "end_time": datetime(2026, 1, 21, 11, 0, 45),
            "task_results": [{"task_id": "t2", "success": True}],
            "agent_interactions": [{"agent_id": "a2", "message_count": 8, "duplicate_count": 1}],
        },
    ]

    batch_results = metrics.batch_evaluate(evaluations)

    assert len(batch_results) == 2
    assert batch_results[0]["run_id"] == "run_1"
    assert batch_results[1]["run_id"] == "run_2"
    assert batch_results[0]["execution_time"] == 30.0
    assert batch_results[1]["execution_time"] == 45.0


def test_traditional_metrics_batch_evaluation_empty():
    """Test batch evaluation with no evaluations."""
    metrics = TraditionalMetrics()

    batch_results = metrics.batch_evaluate([])

    assert batch_results == []
