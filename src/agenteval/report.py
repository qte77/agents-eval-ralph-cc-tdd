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

    def generate_summary(self, result: PipelineResult) -> str:
        """Generate human-readable summary report.

        Args:
            result: PipelineResult to summarize

        Returns:
            String containing formatted summary
        """
        lines = []
        lines.append("=" * 60)
        lines.append("EVALUATION PIPELINE SUMMARY")
        lines.append("=" * 60)
        lines.append(f"Run ID: {result.run_id}")
        lines.append(f"Timestamp: {result.timestamp}")
        lines.append(f"Execution Time: {result.execution_time:.2f}s")
        lines.append("")

        # Traditional metrics section
        if result.traditional_metrics:
            lines.append("TRADITIONAL METRICS:")
            lines.append("-" * 40)
            if "success_rate" in result.traditional_metrics:
                lines.append(f"  Success Rate: {result.traditional_metrics['success_rate']:.2%}")
            if "avg_execution_time" in result.traditional_metrics:
                lines.append(
                    f"  Avg Execution Time: {result.traditional_metrics['avg_execution_time']:.2f}s"
                )
            lines.append("")

        # LLM judge section
        if result.llm_judge_results:
            lines.append("LLM JUDGE RESULTS:")
            lines.append("-" * 40)
            if "avg_score" in result.llm_judge_results:
                lines.append(f"  Average Score: {result.llm_judge_results['avg_score']:.2f}")
            lines.append("")

        # Graph metrics section
        if result.graph_metrics:
            lines.append("GRAPH METRICS:")
            lines.append("-" * 40)
            if "density" in result.graph_metrics:
                lines.append(f"  Graph Density: {result.graph_metrics['density']:.3f}")
            lines.append("")

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
