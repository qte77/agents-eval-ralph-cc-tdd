"""Traditional performance metrics calculator for agent evaluation.

Calculates execution time, success rate, and coordination quality metrics
for agent task completion.
"""

from datetime import datetime

from pydantic import BaseModel, Field, computed_field, field_validator

from agenteval.models.evaluation import Metrics


class AgentTaskResult(BaseModel):
    """Model for individual agent task execution result."""

    task_id: str
    agent_id: str
    start_time: datetime
    end_time: datetime
    success: bool
    coordination_score: float = Field(..., ge=0.0, le=1.0)

    @field_validator("coordination_score")
    @classmethod
    def validate_coordination_score(cls, v: float) -> float:
        """Validate coordination_score is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("coordination_score must be between 0 and 1")
        return v

    @computed_field  # type: ignore[prop-decorator]
    @property
    def execution_time_seconds(self) -> float:
        """Calculate execution time from start and end times."""
        return (self.end_time - self.start_time).total_seconds()


class TraditionalMetricsCalculator:
    """Calculator for traditional performance metrics."""

    def _validate_results(self, results: list[AgentTaskResult]) -> None:
        """Validate that results list is not empty.

        Args:
            results: List of agent task results

        Raises:
            ValueError: If results list is empty
        """
        if not results:
            raise ValueError("Cannot calculate metrics for empty results")

    def calculate_execution_time(self, results: list[AgentTaskResult]) -> float:
        """Calculate average execution time across tasks.

        Args:
            results: List of agent task results

        Returns:
            Average execution time in seconds
        """
        self._validate_results(results)
        return sum(r.execution_time_seconds for r in results) / len(results)

    def calculate_success_rate(self, results: list[AgentTaskResult]) -> float:
        """Calculate task success rate.

        Args:
            results: List of agent task results

        Returns:
            Success rate as a float between 0.0 and 1.0
        """
        self._validate_results(results)
        successful_tasks = sum(1 for r in results if r.success)
        return successful_tasks / len(results)

    def calculate_coordination_quality(self, results: list[AgentTaskResult]) -> float:
        """Calculate average coordination quality across tasks.

        Args:
            results: List of agent task results

        Returns:
            Average coordination quality score between 0.0 and 1.0
        """
        self._validate_results(results)
        return sum(r.coordination_score for r in results) / len(results)

    def calculate_metrics(self, results: list[AgentTaskResult]) -> Metrics:
        """Calculate all traditional metrics from task results.

        Args:
            results: List of agent task results

        Returns:
            Metrics model with execution time, success rate, and coordination quality

        Raises:
            ValueError: If results list is empty
        """
        self._validate_results(results)

        return Metrics(
            execution_time_seconds=self.calculate_execution_time(results),
            success_rate=self.calculate_success_rate(results),
            coordination_quality=self.calculate_coordination_quality(results),
        )
