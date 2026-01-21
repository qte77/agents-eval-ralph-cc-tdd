"""Consolidated reporting and observability."""

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from loguru import logger

from agenteval.config.config import load_config


class ConsolidatedReporter:
    """Combine results from all evaluation tiers into unified reports."""

    def __init__(self):
        """Initialize reporter with configuration."""
        self.config = load_config()

        # Configure loguru console logging based on config
        if not self.config.observability.console_logging:
            logger.remove()  # Disable console logging if configured

    def generate_report(self, pipeline_results: dict) -> dict:
        """Generate consolidated report from pipeline results.

        Args:
            pipeline_results: Dict containing:
                - traditional_metrics: dict
                - llm_evaluations: list[Evaluation]
                - graph_metrics: dict
                - run_metadata: dict

        Returns:
            Dict with consolidated report including all metrics and metadata.
        """
        # Log report generation if console logging enabled
        if self.config.observability.console_logging:
            logger.info("Generating consolidated evaluation report")

        # Extract results from all three tiers
        traditional_metrics = pipeline_results["traditional_metrics"]
        llm_evaluations = pipeline_results["llm_evaluations"]
        graph_metrics = pipeline_results["graph_metrics"]
        run_metadata = pipeline_results["run_metadata"]

        # Generate unique report ID
        report_id = str(uuid.uuid4())
        run_id = str(uuid.uuid4())
        created_at = datetime.now(UTC)

        # Calculate summary statistics
        total_evaluations = len(llm_evaluations)
        avg_semantic_score = (
            sum(eval.semantic_score for eval in llm_evaluations) / total_evaluations
            if total_evaluations > 0
            else 0.0
        )

        summary = {
            "total_evaluations": total_evaluations,
            "avg_semantic_score": avg_semantic_score,
        }

        # Combine all results into structured report
        report = {
            "report_id": report_id,
            "run_id": run_id,
            "created_at": created_at,
            "traditional_metrics": traditional_metrics,
            "llm_evaluations": [eval.model_dump() for eval in llm_evaluations],
            "graph_metrics": graph_metrics,
            "run_metadata": run_metadata,
            "summary": summary,
        }

        # Log completion if console logging enabled
        if self.config.observability.console_logging:
            logger.info(
                f"Report generated: {total_evaluations} evaluations, "
                f"avg score: {avg_semantic_score:.2f}"
            )

        # Handle optional cloud export if configured
        if self.config.observability.cloud_export:
            self._export_to_cloud(report)

        return report

    def save_report(self, pipeline_results: dict, output_path: Path) -> None:
        """Save consolidated report to JSON file.

        Args:
            pipeline_results: Pipeline results to include in report.
            output_path: Path where JSON report should be saved.
        """
        report = self.generate_report(pipeline_results)

        # Convert datetime objects to ISO format strings for JSON serialization
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        with output_path.open("w") as f:
            json.dump(report, f, indent=2, default=json_serializer)

        if self.config.observability.console_logging:
            logger.info(f"Report saved to {output_path}")

    def _export_to_cloud(self, report: dict) -> None:
        """Export report to cloud observability platform.

        Args:
            report: Consolidated report to export.

        Note:
            This is a placeholder for cloud export functionality.
            Actual implementation would integrate with Logfire/Weave.
        """
        # Placeholder for cloud export
        # In production, would send to Logfire/Weave
        if self.config.observability.console_logging:
            logger.debug("Cloud export configured (placeholder)")
