"""Tests for Traditional Metrics Calculator.

Following TDD RED phase - these tests should FAIL until implementation is complete.
Tests validate calculation of execution time, success rate, and coordination quality metrics.
"""

from datetime import datetime

import pytest
from agenteval.metrics.traditional import (
    AgentTaskResult,
    TraditionalMetricsCalculator,
)

from agenteval.models.evaluation import Metrics


class TestAgentTaskResult:
    """Test AgentTaskResult Pydantic model."""

    def test_agent_task_result_model(self):
        """Test AgentTaskResult model has required fields."""
        result = AgentTaskResult(
            task_id="task_001",
            agent_id="agent_001",
            start_time=datetime(2026, 1, 19, 10, 0, 0),
            end_time=datetime(2026, 1, 19, 10, 1, 30),
            success=True,
            coordination_score=0.85,
        )
        assert result.task_id == "task_001"
        assert result.agent_id == "agent_001"
        assert result.success is True
        assert result.coordination_score == 0.85

    def test_execution_time_property(self):
        """Test AgentTaskResult computes execution time from start/end times."""
        result = AgentTaskResult(
            task_id="task_001",
            agent_id="agent_001",
            start_time=datetime(2026, 1, 19, 10, 0, 0),
            end_time=datetime(2026, 1, 19, 10, 2, 30),
            success=True,
            coordination_score=0.8,
        )
        # 2 minutes 30 seconds = 150 seconds
        assert result.execution_time_seconds == 150.0

    def test_coordination_score_validation(self):
        """Test coordination_score is validated to be between 0 and 1."""
        with pytest.raises(ValueError):
            AgentTaskResult(
                task_id="task_001",
                agent_id="agent_001",
                start_time=datetime(2026, 1, 19, 10, 0, 0),
                end_time=datetime(2026, 1, 19, 10, 1, 0),
                success=True,
                coordination_score=1.5,  # Invalid: > 1.0
            )


class TestTraditionalMetricsCalculator:
    """Test Traditional Metrics Calculator functionality."""

    def test_calculator_initialization(self):
        """Test TraditionalMetricsCalculator can be initialized."""
        calculator = TraditionalMetricsCalculator()
        assert isinstance(calculator, TraditionalMetricsCalculator)

    def test_calculate_execution_time_single_task(self):
        """Test calculating execution time for a single task."""
        calculator = TraditionalMetricsCalculator()

        result = AgentTaskResult(
            task_id="task_001",
            agent_id="agent_001",
            start_time=datetime(2026, 1, 19, 10, 0, 0),
            end_time=datetime(2026, 1, 19, 10, 3, 0),
            success=True,
            coordination_score=0.9,
        )

        exec_time = calculator.calculate_execution_time([result])
        # 3 minutes = 180 seconds
        assert exec_time == 180.0

    def test_calculate_execution_time_multiple_tasks(self):
        """Test calculating average execution time across multiple tasks."""
        calculator = TraditionalMetricsCalculator()

        results = [
            AgentTaskResult(
                task_id=f"task_{i:03d}",
                agent_id="agent_001",
                start_time=datetime(2026, 1, 19, 10, 0, 0),
                end_time=datetime(2026, 1, 19, 10, i + 1, 0),
                success=True,
                coordination_score=0.8,
            )
            for i in range(3)
        ]

        exec_time = calculator.calculate_execution_time(results)
        # (60 + 120 + 180) / 3 = 120 seconds
        assert exec_time == 120.0

    def test_calculate_success_rate_all_successful(self):
        """Test success rate calculation when all tasks succeed."""
        calculator = TraditionalMetricsCalculator()

        results = [
            AgentTaskResult(
                task_id=f"task_{i:03d}",
                agent_id="agent_001",
                start_time=datetime(2026, 1, 19, 10, 0, 0),
                end_time=datetime(2026, 1, 19, 10, 1, 0),
                success=True,
                coordination_score=0.8,
            )
            for i in range(5)
        ]

        success_rate = calculator.calculate_success_rate(results)
        assert success_rate == 1.0

    def test_calculate_success_rate_partial_success(self):
        """Test success rate calculation with some failures."""
        calculator = TraditionalMetricsCalculator()

        results = [
            AgentTaskResult(
                task_id=f"task_{i:03d}",
                agent_id="agent_001",
                start_time=datetime(2026, 1, 19, 10, 0, 0),
                end_time=datetime(2026, 1, 19, 10, 1, 0),
                success=(i < 3),  # First 3 succeed, last 2 fail
                coordination_score=0.8,
            )
            for i in range(5)
        ]

        success_rate = calculator.calculate_success_rate(results)
        assert success_rate == 0.6  # 3/5 = 0.6

    def test_calculate_success_rate_all_failed(self):
        """Test success rate calculation when all tasks fail."""
        calculator = TraditionalMetricsCalculator()

        results = [
            AgentTaskResult(
                task_id=f"task_{i:03d}",
                agent_id="agent_001",
                start_time=datetime(2026, 1, 19, 10, 0, 0),
                end_time=datetime(2026, 1, 19, 10, 1, 0),
                success=False,
                coordination_score=0.5,
            )
            for i in range(3)
        ]

        success_rate = calculator.calculate_success_rate(results)
        assert success_rate == 0.0

    def test_calculate_coordination_quality_single_task(self):
        """Test coordination quality calculation for single task."""
        calculator = TraditionalMetricsCalculator()

        result = AgentTaskResult(
            task_id="task_001",
            agent_id="agent_001",
            start_time=datetime(2026, 1, 19, 10, 0, 0),
            end_time=datetime(2026, 1, 19, 10, 1, 0),
            success=True,
            coordination_score=0.85,
        )

        coord_quality = calculator.calculate_coordination_quality([result])
        assert coord_quality == 0.85

    def test_calculate_coordination_quality_multiple_tasks(self):
        """Test coordination quality calculation across multiple tasks."""
        calculator = TraditionalMetricsCalculator()

        results = [
            AgentTaskResult(
                task_id=f"task_{i:03d}",
                agent_id=f"agent_{i % 2:03d}",
                start_time=datetime(2026, 1, 19, 10, 0, 0),
                end_time=datetime(2026, 1, 19, 10, 1, 0),
                success=True,
                coordination_score=0.7 + (i * 0.05),
            )
            for i in range(4)
        ]

        coord_quality = calculator.calculate_coordination_quality(results)
        # (0.7 + 0.75 + 0.8 + 0.85) / 4 = 0.775
        assert coord_quality == 0.775

    def test_calculate_metrics_returns_metrics_model(self):
        """Test calculate_metrics returns Metrics Pydantic model."""
        calculator = TraditionalMetricsCalculator()

        results = [
            AgentTaskResult(
                task_id="task_001",
                agent_id="agent_001",
                start_time=datetime(2026, 1, 19, 10, 0, 0),
                end_time=datetime(2026, 1, 19, 10, 2, 0),
                success=True,
                coordination_score=0.8,
            )
        ]

        metrics = calculator.calculate_metrics(results)

        assert isinstance(metrics, Metrics)
        assert metrics.execution_time_seconds == 120.0
        assert metrics.success_rate == 1.0
        assert metrics.coordination_quality == 0.8

    def test_batch_evaluation_multiple_agent_outputs(self):
        """Test batch evaluation of multiple agent task results."""
        calculator = TraditionalMetricsCalculator()

        # Simulate multiple agent tasks from different agents
        results = [
            AgentTaskResult(
                task_id=f"task_{i:03d}",
                agent_id=f"agent_{i % 3:03d}",
                start_time=datetime(2026, 1, 19, 10, 0, 0),
                end_time=datetime(2026, 1, 19, 10, i + 1, 0),
                success=(i % 2 == 0),  # Every other task succeeds
                coordination_score=0.6 + (i * 0.05),
            )
            for i in range(6)
        ]

        metrics = calculator.calculate_metrics(results)

        assert isinstance(metrics, Metrics)
        assert metrics.execution_time_seconds > 0
        assert 0.0 <= metrics.success_rate <= 1.0
        assert 0.0 <= metrics.coordination_quality <= 1.0

    def test_calculate_metrics_to_json(self):
        """Test metrics output can be serialized to JSON format."""
        calculator = TraditionalMetricsCalculator()

        results = [
            AgentTaskResult(
                task_id="task_001",
                agent_id="agent_001",
                start_time=datetime(2026, 1, 19, 10, 0, 0),
                end_time=datetime(2026, 1, 19, 10, 1, 30),
                success=True,
                coordination_score=0.9,
            )
        ]

        metrics = calculator.calculate_metrics(results)
        json_output = metrics.model_dump_json()

        assert isinstance(json_output, str)
        assert "execution_time_seconds" in json_output
        assert "success_rate" in json_output
        assert "coordination_quality" in json_output

    def test_handles_empty_results_gracefully(self):
        """Test calculator handles empty results list gracefully."""
        calculator = TraditionalMetricsCalculator()

        with pytest.raises(ValueError):
            calculator.calculate_metrics([])

    def test_execution_time_for_concurrent_tasks(self):
        """Test execution time calculation for concurrent overlapping tasks."""
        calculator = TraditionalMetricsCalculator()

        # Two tasks running concurrently
        results = [
            AgentTaskResult(
                task_id="task_001",
                agent_id="agent_001",
                start_time=datetime(2026, 1, 19, 10, 0, 0),
                end_time=datetime(2026, 1, 19, 10, 3, 0),
                success=True,
                coordination_score=0.8,
            ),
            AgentTaskResult(
                task_id="task_002",
                agent_id="agent_002",
                start_time=datetime(2026, 1, 19, 10, 1, 0),
                end_time=datetime(2026, 1, 19, 10, 4, 0),
                success=True,
                coordination_score=0.9,
            ),
        ]

        exec_time = calculator.calculate_execution_time(results)
        # Average: (180 + 180) / 2 = 180 seconds
        assert exec_time == 180.0

    def test_coordination_quality_validation(self):
        """Test that calculated coordination_quality is validated by Metrics model."""
        calculator = TraditionalMetricsCalculator()

        results = [
            AgentTaskResult(
                task_id="task_001",
                agent_id="agent_001",
                start_time=datetime(2026, 1, 19, 10, 0, 0),
                end_time=datetime(2026, 1, 19, 10, 1, 0),
                success=True,
                coordination_score=0.75,
            )
        ]

        metrics = calculator.calculate_metrics(results)

        # Should be validated by Metrics model (0.0 <= value <= 1.0)
        assert 0.0 <= metrics.coordination_quality <= 1.0

    def test_calculate_metrics_with_mixed_agents(self):
        """Test metrics calculation with results from multiple different agents."""
        calculator = TraditionalMetricsCalculator()

        results = [
            AgentTaskResult(
                task_id=f"task_{i:03d}",
                agent_id=f"agent_{chr(65 + i)}",  # agent_A, agent_B, etc.
                start_time=datetime(2026, 1, 19, 10, 0, 0),
                end_time=datetime(2026, 1, 19, 10, 2, 0),
                success=(i % 3 != 0),  # 2/3 succeed
                coordination_score=0.65 + (i * 0.1),
            )
            for i in range(3)
        ]

        metrics = calculator.calculate_metrics(results)

        assert isinstance(metrics, Metrics)
        # 2 out of 3 succeed
        assert abs(metrics.success_rate - (2 / 3)) < 0.01
