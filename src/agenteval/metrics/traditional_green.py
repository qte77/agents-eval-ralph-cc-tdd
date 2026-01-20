"""Traditional performance metrics for agent evaluation.

This module provides functionality to measure:
- Execution time metrics
- Task success rate
- Coordination quality between agents
- Batch evaluation capabilities
"""

from typing import Any

from pydantic import BaseModel

from agenteval.models.evaluation import Metrics


def calculate_execution_time(start_time: float, end_time: float) -> float:
    """Calculate execution time between start and end timestamps.

    Args:
        start_time: Start timestamp in seconds
        end_time: End timestamp in seconds

    Returns:
        Execution time in seconds

    Raises:
        ValueError: If end_time is before start_time
    """
    if end_time < start_time:
        raise ValueError("End time must be after start time")
    return end_time - start_time


def calculate_success_rate(task_results: list[bool]) -> float:
    """Calculate success rate from task results.

    Args:
        task_results: List of boolean task results (True = success, False = failure)

    Returns:
        Success rate as a float between 0.0 and 1.0

    Raises:
        ValueError: If task_results is empty
    """
    if not task_results:
        raise ValueError("Task results cannot be empty")
    return sum(task_results) / len(task_results)


def calculate_coordination_quality(coordination_events: list[dict[str, Any]]) -> float:
    """Calculate coordination quality from agent coordination events.

    Args:
        coordination_events: List of coordination events with agent_id, timestamp, and success

    Returns:
        Coordination quality score between 0.0 and 1.0

    Raises:
        ValueError: If coordination_events is empty
    """
    if not coordination_events:
        raise ValueError("Coordination events cannot be empty")
    successful_events = sum(1 for event in coordination_events if event["success"])
    return successful_events / len(coordination_events)


class TraditionalMetrics(BaseModel):
    """Container for traditional performance metrics data.

    This class holds the raw data needed to calculate traditional metrics
    and provides methods to compute and export the metrics.
    """

    start_time: float
    end_time: float
    task_results: list[bool]
    coordination_events: list[dict[str, Any]]

    def calculate(self) -> Metrics:
        """Calculate all traditional metrics and return as Metrics model.

        Returns:
            Metrics model with execution_time_seconds, success_rate, and coordination_quality
        """
        execution_time = calculate_execution_time(self.start_time, self.end_time)
        success_rate = calculate_success_rate(self.task_results)
        coordination_quality = calculate_coordination_quality(self.coordination_events)

        return Metrics(
            execution_time_seconds=execution_time,
            success_rate=success_rate,
            coordination_quality=coordination_quality,
        )


def evaluate_batch(runs: list[dict[str, Any]]) -> list[Metrics]:
    """Evaluate multiple agent runs in batch.

    Args:
        runs: List of run dictionaries containing start_time, end_time,
              task_results, and coordination_events

    Returns:
        List of Metrics models, one for each run

    Raises:
        ValueError: If runs is empty
    """
    if not runs:
        raise ValueError("Batch cannot be empty")

    results = []
    for run in runs:
        metrics = TraditionalMetrics(
            start_time=run["start_time"],
            end_time=run["end_time"],
            task_results=run["task_results"],
            coordination_events=run["coordination_events"],
        )
        results.append(metrics.calculate())

    return results
