"""Traditional performance metrics calculation."""

import json
from datetime import datetime


def calculate_execution_time(start_time: datetime, end_time: datetime) -> float:
    """Calculate execution time from start and end timestamps."""
    delta = end_time - start_time
    return delta.total_seconds()


def calculate_success_rate(task_results: list[dict]) -> float:
    """Calculate task success rate."""
    if not task_results:
        return 0.0

    successful = sum(1 for task in task_results if task.get("success", False))
    return successful / len(task_results)


def calculate_coordination_quality(agent_interactions: list[dict]) -> float:
    """Calculate coordination quality between agents."""
    if not agent_interactions:
        return 0.0

    total_messages = sum(agent.get("message_count", 0) for agent in agent_interactions)
    if total_messages == 0:
        return 0.0

    total_duplicates = sum(agent.get("duplicate_count", 0) for agent in agent_interactions)
    return 1.0 - (total_duplicates / total_messages)


class TraditionalMetrics:
    """Traditional performance metrics calculator."""

    def calculate_all(
        self,
        start_time: datetime,
        end_time: datetime,
        task_results: list[dict],
        agent_interactions: list[dict],
    ) -> dict:
        """Calculate all metrics together."""
        return {
            "execution_time": calculate_execution_time(start_time, end_time),
            "success_rate": calculate_success_rate(task_results),
            "coordination_quality": calculate_coordination_quality(agent_interactions),
        }

    def to_json(self, result: dict) -> str:
        """Output metrics in structured JSON format."""
        return json.dumps(result)

    def batch_evaluate(self, evaluations: list[dict]) -> list[dict]:
        """Support batch evaluation of multiple agent outputs."""
        results = []
        for evaluation in evaluations:
            metrics = self.calculate_all(
                start_time=evaluation["start_time"],
                end_time=evaluation["end_time"],
                task_results=evaluation["task_results"],
                agent_interactions=evaluation["agent_interactions"],
            )
            results.append({"run_id": evaluation["run_id"], **metrics})
        return results
