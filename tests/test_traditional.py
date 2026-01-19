"""Tests for traditional performance metrics calculation.

Following TDD RED phase - these tests should FAIL until implementation is complete.
"""

import json
from datetime import datetime


class TestMetricsModels:
    """Test Pydantic models for traditional metrics."""

    def test_agent_task_result_model(self):
        """Test AgentTaskResult model with basic fields."""
        from agenteval.metrics.traditional import AgentTaskResult

        result = AgentTaskResult(
            agent_id="agent_1",
            task_id="task_1",
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 5),
            success=True,
            output="Test output",
        )

        assert result.agent_id == "agent_1"
        assert result.task_id == "task_1"
        assert result.success is True
        assert result.output == "Test output"

    def test_coordination_event_model(self):
        """Test CoordinationEvent model for agent interactions."""
        from agenteval.metrics.traditional import CoordinationEvent

        event = CoordinationEvent(
            from_agent="agent_1",
            to_agent="agent_2",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            event_type="message",
            successful=True,
        )

        assert event.from_agent == "agent_1"
        assert event.to_agent == "agent_2"
        assert event.event_type == "message"
        assert event.successful is True

    def test_traditional_metrics_model(self):
        """Test TraditionalMetrics model with all metric fields."""
        from agenteval.metrics.traditional import TraditionalMetrics

        metrics = TraditionalMetrics(
            avg_execution_time=5.5,
            success_rate=0.85,
            coordination_quality=0.92,
            total_tasks=100,
            successful_tasks=85,
            failed_tasks=15,
            total_coordination_events=50,
            successful_coordination_events=46,
        )

        assert metrics.avg_execution_time == 5.5
        assert metrics.success_rate == 0.85
        assert metrics.coordination_quality == 0.92
        assert metrics.total_tasks == 100
        assert metrics.successful_tasks == 85


class TestExecutionTimeMetrics:
    """Test execution time calculation."""

    def test_calculate_execution_time_single_task(self):
        """Test execution time calculation for a single task."""
        from agenteval.metrics.traditional import (
            AgentTaskResult,
            calculate_execution_time,
        )

        result = AgentTaskResult(
            agent_id="agent_1",
            task_id="task_1",
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 5),
            success=True,
            output="Done",
        )

        execution_time = calculate_execution_time(result)
        assert execution_time == 5.0

    def test_calculate_avg_execution_time_multiple_tasks(self):
        """Test average execution time across multiple tasks."""
        from agenteval.metrics.traditional import (
            AgentTaskResult,
            calculate_avg_execution_time,
        )

        results = [
            AgentTaskResult(
                agent_id="agent_1",
                task_id=f"task_{i}",
                start_time=datetime(2024, 1, 1, 12, 0, 0),
                end_time=datetime(2024, 1, 1, 12, 0, i + 1),
                success=True,
                output="Done",
            )
            for i in range(5)
        ]

        avg_time = calculate_avg_execution_time(results)
        # Average of 1, 2, 3, 4, 5 seconds = 3.0
        assert avg_time == 3.0

    def test_calculate_avg_execution_time_empty_list(self):
        """Test average execution time with empty results list."""
        from agenteval.metrics.traditional import calculate_avg_execution_time

        avg_time = calculate_avg_execution_time([])
        assert avg_time == 0.0


class TestSuccessRateMetrics:
    """Test success rate calculation."""

    def test_calculate_success_rate_all_successful(self):
        """Test success rate when all tasks succeed."""
        from agenteval.metrics.traditional import (
            AgentTaskResult,
            calculate_success_rate,
        )

        results = [
            AgentTaskResult(
                agent_id=f"agent_{i}",
                task_id=f"task_{i}",
                start_time=datetime(2024, 1, 1, 12, 0, 0),
                end_time=datetime(2024, 1, 1, 12, 0, 1),
                success=True,
                output="Done",
            )
            for i in range(10)
        ]

        success_rate = calculate_success_rate(results)
        assert success_rate == 1.0

    def test_calculate_success_rate_partial_success(self):
        """Test success rate with mixed success/failure."""
        from agenteval.metrics.traditional import (
            AgentTaskResult,
            calculate_success_rate,
        )

        results = [
            AgentTaskResult(
                agent_id=f"agent_{i}",
                task_id=f"task_{i}",
                start_time=datetime(2024, 1, 1, 12, 0, 0),
                end_time=datetime(2024, 1, 1, 12, 0, 1),
                success=i < 7,  # 7 successful, 3 failed
                output="Done" if i < 7 else "Failed",
            )
            for i in range(10)
        ]

        success_rate = calculate_success_rate(results)
        assert success_rate == 0.7

    def test_calculate_success_rate_empty_list(self):
        """Test success rate with empty results list."""
        from agenteval.metrics.traditional import calculate_success_rate

        success_rate = calculate_success_rate([])
        assert success_rate == 0.0


class TestCoordinationQualityMetrics:
    """Test coordination quality assessment."""

    def test_calculate_coordination_quality_perfect(self):
        """Test coordination quality when all events succeed."""
        from agenteval.metrics.traditional import (
            CoordinationEvent,
            calculate_coordination_quality,
        )

        events = [
            CoordinationEvent(
                from_agent="agent_1",
                to_agent="agent_2",
                timestamp=datetime(2024, 1, 1, 12, 0, i),
                event_type="message",
                successful=True,
            )
            for i in range(20)
        ]

        quality = calculate_coordination_quality(events)
        assert quality == 1.0

    def test_calculate_coordination_quality_partial(self):
        """Test coordination quality with some failures."""
        from agenteval.metrics.traditional import (
            CoordinationEvent,
            calculate_coordination_quality,
        )

        events = [
            CoordinationEvent(
                from_agent="agent_1",
                to_agent="agent_2",
                timestamp=datetime(2024, 1, 1, 12, 0, i),
                event_type="message",
                successful=i < 8,  # 8 successful, 2 failed
            )
            for i in range(10)
        ]

        quality = calculate_coordination_quality(events)
        assert quality == 0.8

    def test_calculate_coordination_quality_empty_list(self):
        """Test coordination quality with empty events list."""
        from agenteval.metrics.traditional import calculate_coordination_quality

        quality = calculate_coordination_quality([])
        assert quality == 0.0


class TestMetricsEvaluator:
    """Test MetricsEvaluator for comprehensive evaluation."""

    def test_evaluator_initialization(self):
        """Test MetricsEvaluator can be initialized."""
        from agenteval.metrics.traditional import MetricsEvaluator

        evaluator = MetricsEvaluator()
        assert evaluator is not None

    def test_evaluate_returns_traditional_metrics(self):
        """Test evaluate() returns TraditionalMetrics object."""
        from agenteval.metrics.traditional import (
            AgentTaskResult,
            CoordinationEvent,
            MetricsEvaluator,
            TraditionalMetrics,
        )

        evaluator = MetricsEvaluator()

        task_results = [
            AgentTaskResult(
                agent_id=f"agent_{i}",
                task_id=f"task_{i}",
                start_time=datetime(2024, 1, 1, 12, 0, 0),
                end_time=datetime(2024, 1, 1, 12, 0, 5),
                success=i < 8,
                output="Done",
            )
            for i in range(10)
        ]

        coordination_events = [
            CoordinationEvent(
                from_agent="agent_1",
                to_agent="agent_2",
                timestamp=datetime(2024, 1, 1, 12, 0, i),
                event_type="message",
                successful=True,
            )
            for i in range(5)
        ]

        metrics = evaluator.evaluate(task_results, coordination_events)

        assert isinstance(metrics, TraditionalMetrics)
        assert metrics.total_tasks == 10
        assert metrics.successful_tasks == 8
        assert metrics.failed_tasks == 2
        assert metrics.success_rate == 0.8

    def test_evaluate_calculates_all_metrics(self):
        """Test evaluate() calculates all required metrics."""
        from agenteval.metrics.traditional import (
            AgentTaskResult,
            CoordinationEvent,
            MetricsEvaluator,
        )

        evaluator = MetricsEvaluator()

        task_results = [
            AgentTaskResult(
                agent_id="agent_1",
                task_id="task_1",
                start_time=datetime(2024, 1, 1, 12, 0, 0),
                end_time=datetime(2024, 1, 1, 12, 0, 10),
                success=True,
                output="Done",
            ),
            AgentTaskResult(
                agent_id="agent_2",
                task_id="task_2",
                start_time=datetime(2024, 1, 1, 12, 0, 0),
                end_time=datetime(2024, 1, 1, 12, 0, 20),
                success=False,
                output="Failed",
            ),
        ]

        coordination_events = [
            CoordinationEvent(
                from_agent="agent_1",
                to_agent="agent_2",
                timestamp=datetime(2024, 1, 1, 12, 0, 5),
                event_type="message",
                successful=True,
            )
        ]

        metrics = evaluator.evaluate(task_results, coordination_events)

        assert metrics.avg_execution_time == 15.0  # (10 + 20) / 2
        assert metrics.success_rate == 0.5  # 1 success out of 2
        assert metrics.coordination_quality == 1.0  # 1 successful event
        assert metrics.total_tasks == 2
        assert metrics.successful_tasks == 1
        assert metrics.failed_tasks == 1
        assert metrics.total_coordination_events == 1
        assert metrics.successful_coordination_events == 1


class TestJSONOutput:
    """Test structured JSON output."""

    def test_metrics_to_json(self):
        """Test TraditionalMetrics can be serialized to JSON."""
        from agenteval.metrics.traditional import TraditionalMetrics

        metrics = TraditionalMetrics(
            avg_execution_time=5.5,
            success_rate=0.85,
            coordination_quality=0.92,
            total_tasks=100,
            successful_tasks=85,
            failed_tasks=15,
            total_coordination_events=50,
            successful_coordination_events=46,
        )

        json_str = metrics.model_dump_json()
        data = json.loads(json_str)

        assert data["avg_execution_time"] == 5.5
        assert data["success_rate"] == 0.85
        assert data["coordination_quality"] == 0.92
        assert data["total_tasks"] == 100

    def test_evaluator_to_dict_output(self):
        """Test MetricsEvaluator can output results as dict."""
        from agenteval.metrics.traditional import (
            AgentTaskResult,
            MetricsEvaluator,
        )

        evaluator = MetricsEvaluator()

        task_results = [
            AgentTaskResult(
                agent_id="agent_1",
                task_id="task_1",
                start_time=datetime(2024, 1, 1, 12, 0, 0),
                end_time=datetime(2024, 1, 1, 12, 0, 5),
                success=True,
                output="Done",
            )
        ]

        metrics = evaluator.evaluate(task_results, [])
        metrics_dict = metrics.model_dump()

        assert isinstance(metrics_dict, dict)
        assert "avg_execution_time" in metrics_dict
        assert "success_rate" in metrics_dict
        assert "coordination_quality" in metrics_dict


class TestBatchEvaluation:
    """Test batch evaluation of multiple agent outputs."""

    def test_evaluate_batch(self):
        """Test evaluating multiple batches of results."""
        from agenteval.metrics.traditional import (
            AgentTaskResult,
            MetricsEvaluator,
        )

        evaluator = MetricsEvaluator()

        # Batch 1
        batch1 = [
            AgentTaskResult(
                agent_id="agent_1",
                task_id="task_1",
                start_time=datetime(2024, 1, 1, 12, 0, 0),
                end_time=datetime(2024, 1, 1, 12, 0, 5),
                success=True,
                output="Done",
            )
        ]

        # Batch 2
        batch2 = [
            AgentTaskResult(
                agent_id="agent_2",
                task_id="task_2",
                start_time=datetime(2024, 1, 1, 12, 0, 0),
                end_time=datetime(2024, 1, 1, 12, 0, 10),
                success=True,
                output="Done",
            )
        ]

        metrics1 = evaluator.evaluate(batch1, [])
        metrics2 = evaluator.evaluate(batch2, [])

        assert metrics1.total_tasks == 1
        assert metrics2.total_tasks == 1
        assert metrics1.avg_execution_time == 5.0
        assert metrics2.avg_execution_time == 10.0

    def test_evaluate_batch_multiple_results(self):
        """Test batch evaluation supports multiple results per batch."""
        from agenteval.metrics.traditional import (
            AgentTaskResult,
            MetricsEvaluator,
        )

        evaluator = MetricsEvaluator()

        batches = [
            [
                AgentTaskResult(
                    agent_id=f"agent_{j}",
                    task_id=f"task_{i}_{j}",
                    start_time=datetime(2024, 1, 1, 12, 0, 0),
                    end_time=datetime(2024, 1, 1, 12, 0, j + 1),
                    success=True,
                    output="Done",
                )
                for j in range(3)
            ]
            for i in range(2)
        ]

        all_metrics = [evaluator.evaluate(batch, []) for batch in batches]

        assert len(all_metrics) == 2
        assert all(m.total_tasks == 3 for m in all_metrics)
        assert all(m.success_rate == 1.0 for m in all_metrics)
