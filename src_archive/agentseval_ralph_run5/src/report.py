"""Consolidated reporting and observability.

Combines results from all evaluation tiers into unified reports with
integrated observability for debugging and monitoring.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from agenteval.config.config import Config
from agenteval.models.evaluation import Evaluation, Metrics, Report


def generate_report(
    run_id: str,
    traditional_metrics: Metrics,
    llm_evaluations: list[Evaluation],
    graph_metrics: dict[str, Any],
) -> Report:
    """Generate consolidated report from all evaluation tiers.

    Args:
        run_id: Unique identifier for this evaluation run
        traditional_metrics: Results from traditional performance metrics
        llm_evaluations: List of LLM judge evaluation results
        graph_metrics: Results from graph-based complexity analysis

    Returns:
        Report: Consolidated report containing all evaluation results
    """
    logger.info(f"Generating report for run_id={run_id}")

    report = Report(
        run_id=run_id,
        timestamp=datetime.now(),
        metrics=traditional_metrics,
        evaluations=llm_evaluations,
        graph_metrics=graph_metrics,
    )

    logger.info(f"Report generated successfully: {len(llm_evaluations)} evaluations")

    return report


def generate_report_with_config(
    run_id: str,
    traditional_metrics: Metrics,
    llm_evaluations: list[Evaluation],
    graph_metrics: dict[str, Any],
    config: Config,
) -> Report:
    """Generate report with observability configuration.

    Args:
        run_id: Unique identifier for this evaluation run
        traditional_metrics: Results from traditional performance metrics
        llm_evaluations: List of LLM judge evaluation results
        graph_metrics: Results from graph-based complexity analysis
        config: Configuration including observability settings

    Returns:
        Report: Consolidated report containing all evaluation results
    """
    logger.info(f"Generating report with config for run_id={run_id}")

    report = generate_report(
        run_id=run_id,
        traditional_metrics=traditional_metrics,
        llm_evaluations=llm_evaluations,
        graph_metrics=graph_metrics,
    )

    # Export to cloud observability platforms if enabled
    if config.observability.get("logfire_enabled", False):
        export_to_logfire(report)

    if config.observability.get("weave_enabled", False):
        export_to_weave(report)

    return report


def save_report(report: Report, output_path: Path) -> None:
    """Save report to JSON file.

    Args:
        report: Report to save
        output_path: Path where JSON file will be written
    """
    logger.info(f"Saving report to {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(report.model_dump(mode="json"), f, indent=2, default=str)

    logger.info("Report saved successfully")


def load_report(input_path: Path) -> Report:
    """Load report from JSON file.

    Args:
        input_path: Path to JSON file to load

    Returns:
        Report: Loaded report object
    """
    logger.info(f"Loading report from {input_path}")

    with open(input_path) as f:
        data = json.load(f)

    report = Report(**data)

    logger.info("Report loaded successfully")

    return report


def export_to_logfire(report: Report) -> None:
    """Export report to Logfire cloud observability platform.

    Args:
        report: Report to export
    """
    logger.info(f"Exporting report {report.run_id} to Logfire")
    # Actual Logfire integration would go here
    # For now, this is a placeholder for optional cloud export


def export_to_weave(report: Report) -> None:
    """Export report to Weave cloud observability platform.

    Args:
        report: Report to export
    """
    logger.info(f"Exporting report {report.run_id} to Weave")
    # Actual Weave integration would go here
    # For now, this is a placeholder for optional cloud export
