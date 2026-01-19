"""Consolidated Reporting & Observability.

Combine results from all evaluation tiers into unified reports with
integrated observability for debugging and monitoring.
"""

from datetime import datetime
from pathlib import Path

from loguru import logger
from pydantic import BaseModel

from agenteval.pipeline import PipelineResult


class ReportConfig(BaseModel):
    """Configuration for report generation and observability."""

    loguru_enabled: bool = True
    logfire_enabled: bool = False
    weave_enabled: bool = False


class ConsolidatedReport(BaseModel):
    """Consolidated report combining all evaluation tier results."""

    run_id: str
    timestamp: datetime
    traditional_metrics: dict[str, float]
    llm_judge_results: list[dict]
    graph_metrics: dict[str, float | int]


class ReportGenerator:
    """Generator for consolidated evaluation reports."""

    def __init__(self, config: ReportConfig) -> None:
        """Initialize report generator.

        Args:
            config: Report configuration including observability settings
        """
        self.config = config

        # Configure observability based on settings
        if self.config.loguru_enabled:
            # Loguru is already configured by default, just ensure it's enabled
            logger.enable("agenteval")

        if self.config.logfire_enabled:
            # Optional: Initialize logfire if enabled
            try:
                import logfire  # noqa: F401

                logger.info("Logfire observability enabled")
            except ImportError:
                logger.warning(
                    "Logfire enabled but not installed. Install with: pip install logfire"
                )

        if self.config.weave_enabled:
            # Optional: Initialize weave if enabled
            try:
                import weave  # noqa: F401

                logger.info("Weave observability enabled")
            except ImportError:
                logger.warning("Weave enabled but not installed. Install with: pip install weave")

    def generate_report(self, pipeline_result: PipelineResult) -> ConsolidatedReport:
        """Generate consolidated report from pipeline result.

        Args:
            pipeline_result: Result from evaluation pipeline

        Returns:
            ConsolidatedReport containing all evaluation tier results
        """
        if self.config.loguru_enabled:
            logger.info(f"Generating consolidated report for run: {pipeline_result.run_id}")

        report = ConsolidatedReport(
            run_id=pipeline_result.run_id,
            timestamp=pipeline_result.timestamp,
            traditional_metrics=pipeline_result.traditional_metrics,
            llm_judge_results=pipeline_result.llm_judge_results,
            graph_metrics=pipeline_result.graph_metrics,
        )

        if self.config.loguru_enabled:
            logger.info(f"Report generated with {len(report.llm_judge_results)} LLM judge results")

        return report

    def save_report(self, report: ConsolidatedReport, output_path: Path) -> None:
        """Save consolidated report to JSON file.

        Args:
            report: Consolidated report to save
            output_path: Path to output JSON file
        """
        if self.config.loguru_enabled:
            logger.info(f"Saving report to {output_path}")

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON report
        with open(output_path, "w") as f:
            f.write(report.model_dump_json(indent=2))

        if self.config.loguru_enabled:
            logger.info(f"Report saved successfully to {output_path}")
