"""Traditional performance metrics for agent system evaluation.

Implements execution time, success rate, coordination quality, and ML metrics.
"""

from collections import Counter
from typing import Any

import numpy as np
from pydantic import BaseModel, field_validator
from rapidfuzz import fuzz
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.metrics.pairwise import cosine_similarity


class ExecutionTimeMetric:
    """Calculate execution time metrics for agent task completion."""

    def calculate(self, start_time: float, end_time: float) -> dict[str, Any]:
        """Calculate execution time.

        Args:
            start_time: Task start time in seconds
            end_time: Task end time in seconds

        Returns:
            Dictionary with execution time metric
        """
        return {
            "metric_name": "execution_time",
            "execution_time_seconds": end_time - start_time,
        }


class SuccessRateMetric:
    """Measure task success rate across evaluation runs."""

    def calculate(self, total_tasks: int, successful_tasks: int) -> dict[str, Any]:
        """Calculate success rate.

        Args:
            total_tasks: Total number of tasks
            successful_tasks: Number of successful tasks

        Returns:
            Dictionary with success rate metrics
        """
        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0.0
        failed_tasks = total_tasks - successful_tasks

        return {
            "success_rate": success_rate,
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
        }


class CoordinationMetric:
    """Assess coordination quality between agents."""

    def calculate_text_similarity(self, text1: str, text2: str) -> dict[str, Any]:
        """Calculate text similarity using Jaro-Winkler.

        Args:
            text1: First text string
            text2: Second text string

        Returns:
            Dictionary with similarity score
        """
        # Use Jaro-Winkler similarity from rapidfuzz
        similarity = fuzz.ratio(text1, text2) / 100.0

        return {
            "similarity_score": similarity,
        }

    def calculate_vector_similarity(
        self, vector1: list[float], vector2: list[float]
    ) -> dict[str, Any]:
        """Calculate cosine similarity between vectors.

        Args:
            vector1: First vector
            vector2: Second vector

        Returns:
            Dictionary with cosine similarity
        """
        # Reshape for sklearn
        v1 = np.array(vector1).reshape(1, -1)
        v2 = np.array(vector2).reshape(1, -1)

        similarity = cosine_similarity(v1, v2)[0][0]

        return {
            "cosine_similarity": float(similarity),
        }

    def calculate_agreement(self, outputs: list[str]) -> dict[str, Any]:
        """Calculate agreement score across agent outputs.

        Args:
            outputs: List of agent output strings

        Returns:
            Dictionary with agreement score and majority output
        """
        if not outputs:
            return {"agreement_score": 0.0, "majority_output": None}

        # Count occurrences
        counter = Counter(outputs)
        majority_output, majority_count = counter.most_common(1)[0]

        agreement_score = majority_count / len(outputs)

        return {
            "agreement_score": agreement_score,
            "majority_output": majority_output,
        }


class MetricsReport(BaseModel):
    """Structured metrics report with JSON serialization."""

    execution_time: float
    success_rate: float
    coordination_score: float
    metadata: dict[str, Any]

    @field_validator("success_rate", "coordination_score")
    @classmethod
    def validate_rate(cls, v: float) -> float:
        """Validate rate is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Rate must be between 0 and 1")
        return v

    def to_json(self) -> str:
        """Serialize to JSON format.

        Returns:
            JSON string representation
        """
        return self.model_dump_json()


class BatchEvaluator:
    """Support batch evaluation of multiple agent outputs."""

    def evaluate_batch(self, outputs: list[dict[str, Any]]) -> dict[str, Any]:
        """Evaluate batch of agent outputs.

        Args:
            outputs: List of output dictionaries with task_id, success, execution_time

        Returns:
            Dictionary with aggregate and per-task metrics
        """
        total_tasks = len(outputs)
        successful_tasks = sum(1 for o in outputs if o.get("success", False))
        total_execution_time = sum(o.get("execution_time", 0.0) for o in outputs)

        avg_execution_time = total_execution_time / total_tasks if total_tasks > 0 else 0.0
        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0.0

        return {
            "aggregate_metrics": {
                "total_tasks": total_tasks,
                "successful_tasks": successful_tasks,
                "success_rate": success_rate,
                "avg_execution_time": avg_execution_time,
            },
            "per_task_metrics": [
                {
                    "task_id": o["task_id"],
                    "success": o["success"],
                    "execution_time": o["execution_time"],
                }
                for o in outputs
            ],
        }


class MLMetrics:
    """ML metrics using scikit-learn."""

    def calculate_f1_score(
        self, y_true: list[int], y_pred: list[int]
    ) -> dict[str, float]:
        """Calculate F1 score.

        Args:
            y_true: True labels
            y_pred: Predicted labels

        Returns:
            Dictionary with F1 score
        """
        score = f1_score(y_true, y_pred, average="binary", zero_division=0.0)

        return {
            "f1_score": float(score),
        }

    def calculate_precision_recall(
        self, y_true: list[int], y_pred: list[int]
    ) -> dict[str, float]:
        """Calculate precision and recall.

        Args:
            y_true: True labels
            y_pred: Predicted labels

        Returns:
            Dictionary with precision and recall
        """
        precision = precision_score(y_true, y_pred, average="binary", zero_division=0.0)
        recall = recall_score(y_true, y_pred, average="binary", zero_division=0.0)

        return {
            "precision": float(precision),
            "recall": float(recall),
        }
