"""Traditional performance metrics calculation for agent evaluation.

Implements standard metrics including execution time, success rate,
and coordination quality for multi-agent systems.
"""

from datetime import datetime

from pydantic import BaseModel


class AgentTaskResult(BaseModel):
    """Represents the result of an agent task execution."""

    agent_id: str
    task_id: str
    start_time: datetime
    end_time: datetime
    success: bool
    output: str


class CoordinationEvent(BaseModel):
    """Represents a coordination event between agents."""

    from_agent: str
    to_agent: str
    timestamp: datetime
    event_type: str
    successful: bool


class TraditionalMetrics(BaseModel):
    """Traditional performance metrics for agent evaluation."""

    avg_execution_time: float
    success_rate: float
    coordination_quality: float
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    total_coordination_events: int
    successful_coordination_events: int


def calculate_execution_time(result: AgentTaskResult) -> float:
    """Calculate execution time for a single task in seconds.

    Args:
        result: AgentTaskResult containing start and end times

    Returns:
        Execution time in seconds
    """
    delta = result.end_time - result.start_time
    return delta.total_seconds()


def calculate_avg_execution_time(results: list[AgentTaskResult]) -> float:
    """Calculate average execution time across multiple tasks.

    Args:
        results: List of AgentTaskResult objects

    Returns:
        Average execution time in seconds, or 0.0 if results is empty
    """
    if not results:
        return 0.0

    total_time = sum(calculate_execution_time(result) for result in results)
    return total_time / len(results)


def calculate_success_rate(results: list[AgentTaskResult]) -> float:
    """Calculate task success rate.

    Args:
        results: List of AgentTaskResult objects

    Returns:
        Success rate as a float between 0.0 and 1.0, or 0.0 if results is empty
    """
    if not results:
        return 0.0

    successful = sum(1 for result in results if result.success)
    return successful / len(results)


def calculate_coordination_quality(events: list[CoordinationEvent]) -> float:
    """Calculate coordination quality based on event success rate.

    Args:
        events: List of CoordinationEvent objects

    Returns:
        Coordination quality as a float between 0.0 and 1.0, or 0.0 if events is empty
    """
    if not events:
        return 0.0

    successful = sum(1 for event in events if event.successful)
    return successful / len(events)


class MetricsEvaluator:
    """Evaluator for calculating comprehensive traditional metrics."""

    def evaluate(
        self,
        task_results: list[AgentTaskResult],
        coordination_events: list[CoordinationEvent],
    ) -> TraditionalMetrics:
        """Evaluate task results and coordination events to produce metrics.

        Args:
            task_results: List of AgentTaskResult objects
            coordination_events: List of CoordinationEvent objects

        Returns:
            TraditionalMetrics object with calculated metrics
        """
        # Calculate task metrics
        avg_execution_time = calculate_avg_execution_time(task_results)
        success_rate = calculate_success_rate(task_results)
        total_tasks = len(task_results)
        successful_tasks = sum(1 for result in task_results if result.success)
        failed_tasks = total_tasks - successful_tasks

        # Calculate coordination metrics
        coordination_quality = calculate_coordination_quality(coordination_events)
        total_coordination_events = len(coordination_events)
        successful_coordination_events = sum(1 for event in coordination_events if event.successful)

        return TraditionalMetrics(
            avg_execution_time=avg_execution_time,
            success_rate=success_rate,
            coordination_quality=coordination_quality,
            total_tasks=total_tasks,
            successful_tasks=successful_tasks,
            failed_tasks=failed_tasks,
            total_coordination_events=total_coordination_events,
            successful_coordination_events=successful_coordination_events,
        )
