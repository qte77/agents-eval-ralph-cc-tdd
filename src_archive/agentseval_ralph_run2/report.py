"""Consolidated evaluation report generation.

This module provides functionality to generate consolidated reports
from pipeline evaluation results in various formats.
"""

import json

from agenteval.pipeline import PipelineResult


class ReportGenerator:
    """Generator for consolidated evaluation reports."""

    def generate_json(self, result: PipelineResult) -> dict:
        """Generate JSON report from pipeline results.

        Args:
            result: PipelineResult to convert to JSON

        Returns:
            Dictionary containing structured report data
        """
        return result.model_dump()

    def _add_section(self, lines: list[str], title: str, metrics: dict | None) -> None:
        """Add a metrics section to the report.

        Args:
            lines: List to append lines to
            title: Section title
            metrics: Dictionary of metrics to display
        """
        if not metrics:
            return

        lines.append(f"{title}:")
        lines.append("-" * 40)

        # Format specific metrics
        if "success_rate" in metrics:
            lines.append(f"  Success Rate: {metrics['success_rate']:.2%}")
        if "avg_execution_time" in metrics:
            lines.append(f"  Avg Execution Time: {metrics['avg_execution_time']:.2f}s")
        if "avg_score" in metrics:
            lines.append(f"  Average Score: {metrics['avg_score']:.2f}")
        if "density" in metrics:
            lines.append(f"  Graph Density: {metrics['density']:.3f}")

        lines.append("")

    def generate_summary(self, result: PipelineResult) -> str:
        """Generate human-readable summary report.

        Args:
            result: PipelineResult to summarize

        Returns:
            String containing formatted summary
        """
        lines = [
            "=" * 60,
            "EVALUATION PIPELINE SUMMARY",
            "=" * 60,
            f"Run ID: {result.run_id}",
            f"Timestamp: {result.timestamp}",
            f"Execution Time: {result.execution_time:.2f}s",
            "",
        ]

        self._add_section(lines, "TRADITIONAL METRICS", result.traditional_metrics)
        self._add_section(lines, "LLM JUDGE RESULTS", result.llm_judge_results)
        self._add_section(lines, "GRAPH METRICS", result.graph_metrics)

        lines.append("=" * 60)

        return "\n".join(lines)

    def save_json_report(self, result: PipelineResult, filepath: str) -> None:
        """Save JSON report to file.

        Args:
            result: PipelineResult to save
            filepath: Path to output file
        """
        report = self.generate_json(result)
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2, default=str)

    def save_summary_report(self, result: PipelineResult, filepath: str) -> None:
        """Save summary report to file.

        Args:
            result: PipelineResult to save
            filepath: Path to output file
        """
        summary = self.generate_summary(result)
        with open(filepath, "w") as f:
            f.write(summary)
