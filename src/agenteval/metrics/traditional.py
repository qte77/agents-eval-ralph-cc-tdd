"""Traditional performance metrics for agent evaluation.

Provides functions to calculate execution time, task success rate, and
coordination quality for agent systems.
"""

from __future__ import annotations

from datetime import datetime

from agenteval.models.evaluation import Metrics


class TraditionalMetrics:
    """Calculator for traditional performance metrics."""

    def calculate_execution_time(self, start_time: datetime, end_time: datetime) -> float:
        """Calculate execution time between start and end timestamps.

        Args:
            start_time: Start datetime
            end_time: End datetime

        Returns:
            Execution time in seconds

        Raises:
            ValueError: If end_time is before start_time
        """
        if end_time < start_time:
            raise ValueError("End time must be after start time")
        return (end_time - start_time).total_seconds()

    def calculate_success_rate(self, task_results: list[bool]) -> float:
        """Calculate task success rate.

        Args:
            task_results: List of boolean task results (True = success)

        Returns:
            Success rate as a float between 0.0 and 1.0
        """
        if not task_results:
            return 0.0
        return sum(task_results) / len(task_results)

    def assess_coordination_quality(
        self, agent_interactions: list[dict[str, str | bool]]
    ) -> float | None:
        """Assess coordination quality between agents.

        Args:
            agent_interactions: List of interaction dictionaries with 'successful' field

        Returns:
            Coordination quality score as a float between 0.0 and 1.0, or None if empty
        """
        if not agent_interactions:
            return None

        successful = sum(
            1 for interaction in agent_interactions if interaction.get("successful", False)
        )
        return successful / len(agent_interactions)

    def create_metrics(
        self,
        execution_time: float,
        success_rate: float,
        coordination_quality: float | None,
    ) -> Metrics:
        """Create a Metrics object from calculated values.

        Args:
            execution_time: Execution time in seconds
            success_rate: Task success rate (0-1)
            coordination_quality: Coordination quality score (0-1) or None

        Returns:
            Metrics object
        """
        return Metrics(
            execution_time_seconds=execution_time,
            task_success_rate=success_rate,
            coordination_quality=coordination_quality,
            semantic_similarity=None,
            graph_density=None,
            graph_centrality=None,
        )

    def evaluate_batch(self, evaluation_runs: list[dict]) -> list[Metrics]:  # type: ignore
        """Evaluate a batch of agent outputs and return metrics for each.

        Args:
            evaluation_runs: List of dictionaries containing evaluation data

        Returns:
            List of Metrics objects, one for each evaluation run
        """
        results = []

        for run in evaluation_runs:
            start_time: datetime = run["start_time"]
            end_time: datetime = run["end_time"]
            task_results: list[bool] = run["task_results"]
            agent_interactions: list[dict[str, str | bool]] = run["agent_interactions"]

            execution_time = self.calculate_execution_time(start_time, end_time)
            success_rate = self.calculate_success_rate(task_results)
            coordination_quality = self.assess_coordination_quality(agent_interactions)

            metrics = self.create_metrics(
                execution_time=execution_time,
                success_rate=success_rate,
                coordination_quality=coordination_quality,
            )
            results.append(metrics)

        return results


def calculate_metrics(
    start_time: datetime,
    end_time: datetime,
    task_results: list[bool],
    agent_interactions: list[dict[str, str | bool]],
) -> Metrics:
    """Convenience function for calculating all metrics at once.

    Args:
        start_time: Start datetime
        end_time: End datetime
        task_results: List of boolean task results
        agent_interactions: List of agent interaction dictionaries

    Returns:
        Metrics object with all calculated metrics
    """
    calculator = TraditionalMetrics()
    execution_time = calculator.calculate_execution_time(start_time, end_time)
    success_rate = calculator.calculate_success_rate(task_results)
    coordination_quality = calculator.assess_coordination_quality(agent_interactions)

    return calculator.create_metrics(
        execution_time=execution_time,
        success_rate=success_rate,
        coordination_quality=coordination_quality,
    )
