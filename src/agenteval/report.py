"""Consolidated evaluation report generation.

Provides structured report format for evaluation results from all three tiers.
"""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class EvaluationReport(BaseModel):
    """Consolidated evaluation report combining all three tiers."""

    traditional_metrics: dict[str, Any]
    llm_evaluation: dict[str, Any]
    graph_analysis: dict[str, Any]
    metadata: dict[str, Any]

    def to_json(self) -> str:
        """Serialize report to JSON format.

        Returns:
            JSON string representation
        """
        return self.model_dump_json(indent=2)

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary.

        Returns:
            Dictionary representation
        """
        return self.model_dump()

    def save(self, filepath: Path) -> None:
        """Save report to JSON file.

        Args:
            filepath: Path to save JSON file
        """
        filepath.write_text(self.to_json())

    @classmethod
    def load(cls, filepath: Path) -> "EvaluationReport":
        """Load report from JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            EvaluationReport instance
        """
        data = json.loads(filepath.read_text())
        return cls(**data)

    def summary(self) -> str:
        """Generate summary text of report.

        Returns:
            Summary string
        """
        lines = ["Evaluation Report Summary", "=" * 50]

        # Traditional metrics
        if "success_rate" in self.traditional_metrics:
            lines.append(f"Success Rate: {self.traditional_metrics['success_rate']:.2%}")
        if "execution_time" in self.traditional_metrics:
            lines.append(
                f"Execution Time: {self.traditional_metrics['execution_time']:.2f}s"
            )

        # LLM evaluation
        if "overall_score" in self.llm_evaluation:
            lines.append(f"LLM Overall Score: {self.llm_evaluation['overall_score']:.1f}/10")

        # Graph analysis
        if "density" in self.graph_analysis:
            lines.append(f"Graph Density: {self.graph_analysis['density']:.2f}")

        # Metadata
        if "seed" in self.metadata:
            lines.append(f"Seed: {self.metadata['seed']}")

        return "\n".join(lines)

    def pretty_print(self) -> str:
        """Pretty print report.

        Returns:
            Formatted string
        """
        return json.dumps(self.to_dict(), indent=2)


class BatchReport(BaseModel):
    """Batch report combining multiple individual reports."""

    reports: list[EvaluationReport]

    def aggregate_metrics(self) -> dict[str, Any]:
        """Calculate aggregate metrics across all reports.

        Returns:
            Dictionary with aggregate metrics
        """
        total = len(self.reports)

        # Aggregate traditional metrics
        avg_execution_time = sum(
            r.traditional_metrics.get("execution_time", 0.0) for r in self.reports
        ) / total

        avg_success_rate = sum(
            r.traditional_metrics.get("success_rate", 0.0) for r in self.reports
        ) / total

        # Aggregate LLM scores
        avg_llm_score = sum(
            r.llm_evaluation.get("overall_score", 0.0) for r in self.reports
        ) / total

        # Aggregate graph metrics
        avg_density = sum(
            r.graph_analysis.get("density", 0.0) for r in self.reports
        ) / total

        return {
            "total_evaluations": total,
            "avg_execution_time": avg_execution_time,
            "avg_success_rate": avg_success_rate,
            "avg_llm_score": avg_llm_score,
            "avg_graph_density": avg_density,
        }

    def to_json(self) -> str:
        """Serialize batch report to JSON.

        Returns:
            JSON string
        """
        data = {
            "reports": [r.to_dict() for r in self.reports],
            "aggregate_metrics": self.aggregate_metrics(),
        }
        return json.dumps(data, indent=2)
