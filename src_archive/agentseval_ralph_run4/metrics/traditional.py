"""Traditional metrics calculator.

Calculate execution time, task success rate, and coordination quality metrics
for agent evaluation with structured JSON output.
"""

from typing import Any

from agenteval.models.evaluation import Metrics


class MetricsCalculator:
    """Calculate traditional performance metrics for agent evaluation."""

    def calculate(self, agent_runs: list[dict[str, Any]]) -> Metrics:
        """Calculate metrics from agent runs.

        Args:
            agent_runs: List of agent run dictionaries containing:
                - agent_id: str
                - start_time: datetime
                - end_time: datetime
                - task_completed: bool
                - coordination_events: list (optional)

        Returns:
            Metrics: Calculated metrics object
        """
        if not agent_runs:
            return Metrics(
                execution_time_seconds=0.0,
                success_rate=0.0,
                coordination_quality=0.0,
            )

        # Calculate average execution time
        total_time = sum(
            (run["end_time"] - run["start_time"]).total_seconds() for run in agent_runs
        )
        avg_execution_time = total_time / len(agent_runs)

        # Calculate success rate
        completed_count = sum(1 for run in agent_runs if run["task_completed"])
        success_rate = completed_count / len(agent_runs)

        # Calculate coordination quality
        total_coordination_events = 0
        successful_coordination_events = 0

        for run in agent_runs:
            coordination_events = run.get("coordination_events", [])
            for event in coordination_events:
                total_coordination_events += 1
                if event.get("success", False):
                    successful_coordination_events += 1

        # If no coordination events, assume perfect coordination
        if total_coordination_events == 0:
            coordination_quality = 1.0
        else:
            coordination_quality = successful_coordination_events / total_coordination_events

        return Metrics(
            execution_time_seconds=avg_execution_time,
            success_rate=success_rate,
            coordination_quality=coordination_quality,
        )
