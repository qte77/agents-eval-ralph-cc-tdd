"""Tests for traditional metrics calculator.

Following TDD RED phase - these tests should FAIL until implementation is complete.
Tests validate calculation of execution time, task success rate, and coordination quality metrics.
"""

from datetime import datetime, timedelta

import pytest

from agenteval.models.evaluation import Metrics


class TestMetricsCalculator:
    """Test MetricsCalculator functionality for computing traditional metrics."""

    def test_calculator_initialization(self):
        """Test MetricsCalculator can be initialized."""
        from agenteval.metrics.traditional import MetricsCalculator

        calculator = MetricsCalculator()
        assert calculator is not None

    def test_calculator_computes_execution_time_metrics(self):
        """Test calculator computes execution time for agent task completion."""
        from agenteval.metrics.traditional import MetricsCalculator

        calculator = MetricsCalculator()

        # Single agent task with start and end timestamps
        agent_run = {
            "agent_id": "agent1",
            "start_time": datetime(2024, 1, 1, 10, 0, 0),
            "end_time": datetime(2024, 1, 1, 10, 5, 30),
            "task_completed": True,
        }

        metrics = calculator.calculate([agent_run])

        assert isinstance(metrics, Metrics)
        assert metrics.execution_time_seconds == 330.0  # 5 minutes 30 seconds

    def test_calculator_measures_task_success_rate(self):
        """Test calculator measures task success rate across evaluation runs."""
        from agenteval.metrics.traditional import MetricsCalculator

        calculator = MetricsCalculator()

        agent_runs = [
            {
                "agent_id": "agent1",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, 5, 0),
                "task_completed": True,
            },
            {
                "agent_id": "agent2",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, 3, 0),
                "task_completed": True,
            },
            {
                "agent_id": "agent3",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, 2, 0),
                "task_completed": False,
            },
        ]

        metrics = calculator.calculate(agent_runs)

        assert metrics.success_rate == pytest.approx(2 / 3, abs=0.01)  # 2 out of 3 succeeded

    def test_calculator_assesses_coordination_quality(self):
        """Test calculator assesses coordination quality between agents."""
        from agenteval.metrics.traditional import MetricsCalculator

        calculator = MetricsCalculator()

        # Agent runs with coordination events
        agent_runs = [
            {
                "agent_id": "agent1",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, 5, 0),
                "task_completed": True,
                "coordination_events": [
                    {"type": "message_sent", "to": "agent2", "success": True},
                    {"type": "message_sent", "to": "agent3", "success": True},
                ],
            },
            {
                "agent_id": "agent2",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, 3, 0),
                "task_completed": True,
                "coordination_events": [
                    {"type": "message_sent", "to": "agent1", "success": True},
                    {"type": "message_sent", "to": "agent3", "success": False},
                ],
            },
        ]

        metrics = calculator.calculate(agent_runs)

        # 3 successful out of 4 total coordination events
        assert metrics.coordination_quality == pytest.approx(0.75, abs=0.01)

    def test_calculator_outputs_structured_json_format(self):
        """Test calculator outputs metrics in structured JSON format."""
        from agenteval.metrics.traditional import MetricsCalculator

        calculator = MetricsCalculator()

        agent_runs = [
            {
                "agent_id": "agent1",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, 5, 0),
                "task_completed": True,
                "coordination_events": [{"type": "message_sent", "to": "agent2", "success": True}],
            }
        ]

        metrics = calculator.calculate(agent_runs)

        # Should be able to convert to JSON (via Pydantic model)
        json_output = metrics.model_dump_json()
        assert isinstance(json_output, str)
        assert "execution_time_seconds" in json_output
        assert "success_rate" in json_output
        assert "coordination_quality" in json_output

    def test_calculator_supports_batch_evaluation(self):
        """Test calculator supports batch evaluation of multiple agent outputs."""
        from agenteval.metrics.traditional import MetricsCalculator

        calculator = MetricsCalculator()

        # Multiple agent runs in a batch
        agent_runs = [
            {
                "agent_id": f"agent{i}",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, i + 1, 0),
                "task_completed": i % 2 == 0,
                "coordination_events": [],
            }
            for i in range(10)
        ]

        metrics = calculator.calculate(agent_runs)

        assert isinstance(metrics, Metrics)
        assert 0.0 <= metrics.success_rate <= 1.0
        assert metrics.execution_time_seconds > 0

    def test_calculator_handles_empty_agent_runs(self):
        """Test calculator handles empty agent runs list."""
        from agenteval.metrics.traditional import MetricsCalculator

        calculator = MetricsCalculator()

        metrics = calculator.calculate([])

        assert isinstance(metrics, Metrics)
        assert metrics.execution_time_seconds == 0.0
        assert metrics.success_rate == 0.0
        assert metrics.coordination_quality == 0.0

    def test_calculator_handles_no_coordination_events(self):
        """Test calculator handles agent runs with no coordination events."""
        from agenteval.metrics.traditional import MetricsCalculator

        calculator = MetricsCalculator()

        agent_runs = [
            {
                "agent_id": "agent1",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, 5, 0),
                "task_completed": True,
            }
        ]

        metrics = calculator.calculate(agent_runs)

        # No coordination events means perfect coordination (1.0) or neutral (depending on design)
        assert metrics.coordination_quality == 1.0

    def test_calculator_computes_average_execution_time(self):
        """Test calculator computes average execution time across multiple runs."""
        from agenteval.metrics.traditional import MetricsCalculator

        calculator = MetricsCalculator()

        agent_runs = [
            {
                "agent_id": "agent1",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, 2, 0),  # 120 seconds
                "task_completed": True,
            },
            {
                "agent_id": "agent2",
                "start_time": datetime(2024, 1, 1, 10, 0, 0),
                "end_time": datetime(2024, 1, 1, 10, 4, 0),  # 240 seconds
                "task_completed": True,
            },
        ]

        metrics = calculator.calculate(agent_runs)

        # Average execution time: (120 + 240) / 2 = 180
        assert metrics.execution_time_seconds == 180.0


class TestMetricsValidation:
    """Test metrics model validation."""

    def test_metrics_validates_success_rate_range(self):
        """Test Metrics model validates success_rate is between 0 and 1."""
        with pytest.raises(Exception):  # ValidationError
            Metrics(execution_time_seconds=100.0, success_rate=1.5, coordination_quality=0.8)

        with pytest.raises(Exception):  # ValidationError
            Metrics(execution_time_seconds=100.0, success_rate=-0.1, coordination_quality=0.8)

    def test_metrics_validates_coordination_quality_range(self):
        """Test Metrics model validates coordination_quality is between 0 and 1."""
        with pytest.raises(Exception):  # ValidationError
            Metrics(execution_time_seconds=100.0, success_rate=0.8, coordination_quality=1.5)

        with pytest.raises(Exception):  # ValidationError
            Metrics(execution_time_seconds=100.0, success_rate=0.8, coordination_quality=-0.1)

    def test_metrics_accepts_valid_values(self):
        """Test Metrics model accepts valid values."""
        metrics = Metrics(execution_time_seconds=100.0, success_rate=0.75, coordination_quality=0.9)

        assert metrics.execution_time_seconds == 100.0
        assert metrics.success_rate == 0.75
        assert metrics.coordination_quality == 0.9
