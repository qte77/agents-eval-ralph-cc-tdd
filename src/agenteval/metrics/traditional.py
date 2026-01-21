"""Traditional performance metrics calculation."""

from datetime import datetime


def calculate_execution_time(start_time: datetime, end_time: datetime) -> float:
    """Calculate execution time from start and end timestamps."""
    raise NotImplementedError


def calculate_success_rate(task_results: list[dict]) -> float:
    """Calculate task success rate."""
    raise NotImplementedError


def calculate_coordination_quality(agent_interactions: list[dict]) -> float:
    """Calculate coordination quality between agents."""
    raise NotImplementedError


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
        raise NotImplementedError

    def to_json(self, result: dict) -> str:
        """Output metrics in structured JSON format."""
        raise NotImplementedError

    def batch_evaluate(self, evaluations: list[dict]) -> list[dict]:
        """Support batch evaluation of multiple agent outputs."""
        raise NotImplementedError
