"""Tests for traditional performance metrics.

Following TDD approach - these tests should FAIL initially.
Tests validate traditional metrics: execution time, success rate, coordination quality.
"""

import json

import pytest

from agenteval.metrics.traditional import (
    TraditionalMetrics,
    calculate_coordination_quality,
    calculate_execution_time,
    calculate_success_rate,
    evaluate_batch,
)
from agenteval.models.evaluation import Metrics


class TestExecutionTime:
    """Tests for execution time calculation."""

    def test_calculate_execution_time_single_task(self):
        """Test calculating execution time for a single task."""
        start_time = 100.0
        end_time = 145.5
        execution_time = calculate_execution_time(start_time, end_time)
        assert execution_time == 45.5

    def test_calculate_execution_time_zero(self):
        """Test execution time when start and end are the same."""
        start_time = 100.0
        end_time = 100.0
        execution_time = calculate_execution_time(start_time, end_time)
        assert execution_time == 0.0

    def test_calculate_execution_time_raises_on_negative(self):
        """Test that negative execution time raises error."""
        start_time = 100.0
        end_time = 50.0
        with pytest.raises(ValueError, match="End time must be after start time"):
            calculate_execution_time(start_time, end_time)


class TestSuccessRate:
    """Tests for success rate calculation."""

    def test_calculate_success_rate_all_success(self):
        """Test success rate when all tasks succeed."""
        task_results = [True, True, True, True]
        success_rate = calculate_success_rate(task_results)
        assert success_rate == 1.0

    def test_calculate_success_rate_partial_success(self):
        """Test success rate with mixed results."""
        task_results = [True, False, True, False]
        success_rate = calculate_success_rate(task_results)
        assert success_rate == 0.5

    def test_calculate_success_rate_no_success(self):
        """Test success rate when all tasks fail."""
        task_results = [False, False, False]
        success_rate = calculate_success_rate(task_results)
        assert success_rate == 0.0

    def test_calculate_success_rate_empty_raises(self):
        """Test that empty task list raises error."""
        with pytest.raises(ValueError, match="Task results cannot be empty"):
            calculate_success_rate([])


class TestCoordinationQuality:
    """Tests for coordination quality assessment."""

    def test_calculate_coordination_quality_perfect(self):
        """Test coordination quality with perfect coordination."""
        coordination_events = [
            {"agent_id": "agent1", "timestamp": 100.0, "success": True},
            {"agent_id": "agent2", "timestamp": 101.0, "success": True},
            {"agent_id": "agent1", "timestamp": 102.0, "success": True},
        ]
        quality = calculate_coordination_quality(coordination_events)
        assert quality == 1.0

    def test_calculate_coordination_quality_partial(self):
        """Test coordination quality with some failures."""
        coordination_events = [
            {"agent_id": "agent1", "timestamp": 100.0, "success": True},
            {"agent_id": "agent2", "timestamp": 101.0, "success": False},
            {"agent_id": "agent1", "timestamp": 102.0, "success": True},
            {"agent_id": "agent3", "timestamp": 103.0, "success": False},
        ]
        quality = calculate_coordination_quality(coordination_events)
        assert quality == 0.5

    def test_calculate_coordination_quality_no_success(self):
        """Test coordination quality when all coordination fails."""
        coordination_events = [
            {"agent_id": "agent1", "timestamp": 100.0, "success": False},
            {"agent_id": "agent2", "timestamp": 101.0, "success": False},
        ]
        quality = calculate_coordination_quality(coordination_events)
        assert quality == 0.0

    def test_calculate_coordination_quality_empty_raises(self):
        """Test that empty coordination events raises error."""
        with pytest.raises(ValueError, match="Coordination events cannot be empty"):
            calculate_coordination_quality([])


class TestTraditionalMetrics:
    """Tests for TraditionalMetrics class that combines all metrics."""

    def test_traditional_metrics_creation(self):
        """Test creating TraditionalMetrics with all required data."""
        metrics = TraditionalMetrics(
            start_time=100.0,
            end_time=150.0,
            task_results=[True, True, False, True],
            coordination_events=[
                {"agent_id": "agent1", "timestamp": 100.0, "success": True},
                {"agent_id": "agent2", "timestamp": 101.0, "success": True},
            ],
        )
        assert metrics.start_time == 100.0
        assert metrics.end_time == 150.0
        assert len(metrics.task_results) == 4
        assert len(metrics.coordination_events) == 2

    def test_traditional_metrics_calculate(self):
        """Test that calculate() returns a Metrics model with correct values."""
        metrics = TraditionalMetrics(
            start_time=100.0,
            end_time=150.0,
            task_results=[True, True, False, True],
            coordination_events=[
                {"agent_id": "agent1", "timestamp": 100.0, "success": True},
                {"agent_id": "agent2", "timestamp": 101.0, "success": True},
                {"agent_id": "agent3", "timestamp": 102.0, "success": False},
            ],
        )
        result = metrics.calculate()

        assert isinstance(result, Metrics)
        assert result.execution_time_seconds == 50.0
        assert result.success_rate == 0.75
        assert abs(result.coordination_quality - 0.6667) < 0.001

    def test_traditional_metrics_to_json(self):
        """Test that to_json() returns valid JSON string."""
        metrics = TraditionalMetrics(
            start_time=100.0,
            end_time=125.0,
            task_results=[True, True],
            coordination_events=[
                {"agent_id": "agent1", "timestamp": 100.0, "success": True}
            ],
        )
        result = metrics.calculate()
        json_str = result.model_dump_json()

        # Verify it's valid JSON and contains expected fields
        parsed = json.loads(json_str)
        assert "execution_time_seconds" in parsed
        assert "success_rate" in parsed
        assert "coordination_quality" in parsed
        assert parsed["execution_time_seconds"] == 25.0
        assert parsed["success_rate"] == 1.0


class TestBatchEvaluation:
    """Tests for batch evaluation of multiple agent outputs."""

    def test_evaluate_batch_single_run(self):
        """Test batch evaluation with a single run."""
        runs = [
            {
                "start_time": 100.0,
                "end_time": 150.0,
                "task_results": [True, True, True],
                "coordination_events": [
                    {"agent_id": "agent1", "timestamp": 100.0, "success": True}
                ],
            }
        ]
        results = evaluate_batch(runs)

        assert len(results) == 1
        assert isinstance(results[0], Metrics)
        assert results[0].execution_time_seconds == 50.0
        assert results[0].success_rate == 1.0

    def test_evaluate_batch_multiple_runs(self):
        """Test batch evaluation with multiple runs."""
        runs = [
            {
                "start_time": 100.0,
                "end_time": 150.0,
                "task_results": [True, True],
                "coordination_events": [
                    {"agent_id": "agent1", "timestamp": 100.0, "success": True}
                ],
            },
            {
                "start_time": 200.0,
                "end_time": 230.0,
                "task_results": [True, False, True],
                "coordination_events": [
                    {"agent_id": "agent1", "timestamp": 200.0, "success": True},
                    {"agent_id": "agent2", "timestamp": 201.0, "success": False},
                ],
            },
        ]
        results = evaluate_batch(runs)

        assert len(results) == 2
        assert results[0].execution_time_seconds == 50.0
        assert results[0].success_rate == 1.0
        assert results[1].execution_time_seconds == 30.0
        assert abs(results[1].success_rate - 0.6667) < 0.001

    def test_evaluate_batch_empty_raises(self):
        """Test that empty batch raises error."""
        with pytest.raises(ValueError, match="Batch cannot be empty"):
            evaluate_batch([])

    def test_evaluate_batch_to_json_format(self):
        """Test that batch results can be converted to JSON."""
        runs = [
            {
                "start_time": 100.0,
                "end_time": 120.0,
                "task_results": [True],
                "coordination_events": [
                    {"agent_id": "agent1", "timestamp": 100.0, "success": True}
                ],
            }
        ]
        results = evaluate_batch(runs)

        # Verify we can serialize to JSON
        json_results = [result.model_dump() for result in results]
        json_str = json.dumps(json_results)
        parsed = json.loads(json_str)

        assert len(parsed) == 1
        assert parsed[0]["execution_time_seconds"] == 20.0
        assert parsed[0]["success_rate"] == 1.0
        assert parsed[0]["coordination_quality"] == 1.0
