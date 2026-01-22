"""Consolidated reporting and observability.

Combines results from all evaluation tiers into unified reports with integrated
observability for debugging and monitoring.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from loguru import logger

from agenteval.models.evaluation import Evaluation, Metrics


def configure_logfire() -> None:
    """Configure Logfire for cloud export.

    This function is a placeholder for Logfire integration.
    Actual implementation would initialize Logfire SDK.
    """
    pass


def configure_weave() -> None:
    """Configure Weave for cloud export.

    This function is a placeholder for Weave integration.
    Actual implementation would initialize Weave SDK.
    """
    pass


class ReportGenerator:
    """Generates consolidated reports from evaluation pipeline results."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the report generator.

        Args:
            config: Optional configuration dictionary with observability settings
        """
        self.config = config or {}
        self.logfire_enabled = False
        self.weave_enabled = False

        # Configure observability backend
        if self.config.get("observability", {}).get("backend") == "logfire":
            configure_logfire()
            self.logfire_enabled = True
        elif self.config.get("observability", {}).get("backend") == "weave":
            configure_weave()
            self.weave_enabled = True

    def generate_report(self, pipeline_results: dict[str, Any]) -> dict[str, Any]:
        """Generate consolidated report from pipeline results.

        Args:
            pipeline_results: Dictionary containing results from all evaluation tiers

        Returns:
            Dictionary with structured report including metadata, results, and aggregates
        """
        report = {
            "metadata": {
                "report_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
            },
            "results": {},
            "aggregate_metrics": {},
        }

        # Include traditional metrics if present
        if "traditional_metrics" in pipeline_results:
            traditional = pipeline_results["traditional_metrics"]
            if isinstance(traditional, Metrics):
                report["traditional_metrics"] = traditional.model_dump()
                report["results"]["traditional_metrics"] = traditional.model_dump()
            else:
                report["traditional_metrics"] = traditional
                report["results"]["traditional_metrics"] = traditional

        # Include LLM evaluation if present
        if "llm_evaluation" in pipeline_results:
            llm_eval = pipeline_results["llm_evaluation"]
            if isinstance(llm_eval, Evaluation):
                report["llm_evaluation"] = llm_eval.model_dump()
                report["results"]["llm_evaluation"] = llm_eval.model_dump()
            else:
                report["llm_evaluation"] = llm_eval
                report["results"]["llm_evaluation"] = llm_eval

        # Include graph metrics if present
        if "graph_metrics" in pipeline_results:
            graph = pipeline_results["graph_metrics"]
            report["graph_metrics"] = graph
            report["results"]["graph_metrics"] = graph

        # Calculate aggregate metrics
        report["aggregate_metrics"] = self._calculate_aggregate_metrics(pipeline_results)

        return report

    def _calculate_aggregate_metrics(self, pipeline_results: dict[str, Any]) -> dict[str, float]:
        """Calculate aggregate metrics across all evaluation tiers.

        Args:
            pipeline_results: Dictionary containing results from all evaluation tiers

        Returns:
            Dictionary with aggregate metrics
        """
        aggregate = {}
        scores = []

        # Collect scores from traditional metrics
        if "traditional_metrics" in pipeline_results:
            traditional = pipeline_results["traditional_metrics"]
            if isinstance(traditional, Metrics):
                if traditional.task_success_rate is not None:
                    scores.append(traditional.task_success_rate)
                if traditional.coordination_quality is not None:
                    scores.append(traditional.coordination_quality)

        # Collect scores from LLM evaluation
        if "llm_evaluation" in pipeline_results:
            llm_eval = pipeline_results["llm_evaluation"]
            if isinstance(llm_eval, Evaluation):
                scores.append(llm_eval.llm_judge_score)

        # Calculate overall quality score as average of all scores
        if scores:
            aggregate["overall_quality_score"] = sum(scores) / len(scores)

        return aggregate

    def to_json(self, report: dict[str, Any]) -> str:
        """Convert report to JSON string.

        Args:
            report: Report dictionary

        Returns:
            JSON string representation of the report
        """
        return json.dumps(report, indent=2)

    def log_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Log an event using the configured observability backend.

        Args:
            event_name: Name of the event to log
            data: Event data to log
        """
        logger.info(f"{event_name}: {data}")
