"""Consolidated Reporting & Observability.

Combines results from all evaluation tiers into unified JSON report with
loguru console logging and optional Logfire/Weave cloud export.
"""

import json
from pathlib import Path

from loguru import logger

from agenteval.config import Config
from agenteval.models.evaluation import Evaluation, Metrics, Report
from agenteval.pipeline import PipelineResult

# Optional cloud observability imports (fail gracefully if not installed)
try:
    import logfire  # type: ignore
except ImportError:
    logfire = None  # type: ignore

try:
    import weave  # type: ignore
except ImportError:
    weave = None  # type: ignore


class ReportGenerator:
    """Generate consolidated evaluation reports with observability."""

    def __init__(self, config: Config | None = None) -> None:
        """Initialize report generator.

        Args:
            config: Optional configuration for observability settings
        """
        self.config = config if config is not None else Config()

    def generate_report(self, pipeline_result: PipelineResult) -> Report:
        """Generate consolidated report from pipeline results.

        Args:
            pipeline_result: Results from evaluation pipeline

        Returns:
            Report: Consolidated report model
        """
        # Log report generation
        if self.config.observability.get("loguru_enabled", True):
            logger.info(f"Generating consolidated report for run_id: {pipeline_result.run_id}")

        # Transform traditional metrics into Metrics model
        metrics = Metrics(
            execution_time_seconds=pipeline_result.traditional_metrics["execution_time_seconds"],
            success_rate=pipeline_result.traditional_metrics["success_rate"],
            coordination_quality=pipeline_result.traditional_metrics["coordination_quality"],
        )

        # Transform LLM judge results into Evaluation models
        evaluations = [
            Evaluation(
                review_id=result["review_id"],
                semantic_score=result["semantic_score"],
                justification=result["justification"],
                baseline_review_id=result["baseline_review_id"],
            )
            for result in pipeline_result.llm_judge_results
        ]

        # Create consolidated report
        report = Report(
            run_id=pipeline_result.run_id,
            timestamp=pipeline_result.timestamp,
            metrics=metrics,
            evaluations=evaluations,
            graph_metrics=pipeline_result.graph_metrics,
        )

        logger.debug(
            f"Report generated: {len(evaluations)} evaluations, "
            f"{len(pipeline_result.graph_metrics)} graph metrics"
        )

        return report

    def save_report(self, report: Report, output_path: Path) -> None:
        """Save report to JSON file.

        Args:
            report: Report model to save
            output_path: Path to output JSON file
        """
        # Create directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert report to dict and save as JSON
        report_dict = report.model_dump(mode="json")

        with open(output_path, "w") as f:
            json.dump(report_dict, f, indent=2, default=str)

        if self.config.observability.get("loguru_enabled", True):
            logger.info(f"Report saved to: {output_path}")

    def export_to_cloud(self, report: Report) -> None:
        """Export report to cloud observability platforms.

        Args:
            report: Report model to export
        """
        # Export to Logfire if enabled
        if self.config.observability.get("logfire_enabled", False):
            if logfire is not None:
                report_dict = report.model_dump(mode="json")
                logfire.info("evaluation_report", **report_dict)
                logger.debug("Report exported to Logfire")
            else:
                logger.warning("Logfire export enabled but logfire package not installed")

        # Export to Weave if enabled
        if self.config.observability.get("weave_enabled", False):
            if weave is not None:
                report_dict = report.model_dump(mode="json")
                weave.log(report_dict)
                logger.debug("Report exported to Weave")
            else:
                logger.warning("Weave export enabled but weave package not installed")
