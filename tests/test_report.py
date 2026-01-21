"""Tests for consolidated reporting and observability."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from agenteval.report import ConsolidatedReporter

from agenteval.models.evaluation import Evaluation


def test_reporter_initialization():
    """Test reporter can be initialized."""
    reporter = ConsolidatedReporter()

    assert reporter is not None


def test_reporter_combines_all_tiers():
    """Test reporter combines results from all three evaluation tiers."""
    reporter = ConsolidatedReporter()

    # Mock data from pipeline output
    pipeline_results = {
        "traditional_metrics": {
            "execution_time": 30.5,
            "success_rate": 0.95,
            "coordination_quality": 0.88,
        },
        "llm_evaluations": [
            Evaluation(
                id="eval_1",
                paper_id="paper_1",
                agent_review_id="agent_review_1",
                human_baseline_id="human_baseline_1",
                semantic_score=0.85,
                justification="Good quality review",
                evaluated_at=datetime(2026, 1, 21, 10, 0, 0),
            )
        ],
        "graph_metrics": {
            "density": 0.75,
            "centrality": {"agent_1": 0.8, "agent_2": 0.6},
            "clustering_coefficient": 0.65,
        },
        "run_metadata": {"seed": 42, "timestamp": datetime(2026, 1, 21, 10, 0, 0)},
    }

    report = reporter.generate_report(pipeline_results)

    # Report should contain all three tiers
    assert "traditional_metrics" in report
    assert "llm_evaluations" in report
    assert "graph_metrics" in report


def test_reporter_generates_consolidated_json():
    """Test reporter generates consolidated JSON report with all metrics."""
    reporter = ConsolidatedReporter()

    pipeline_results = {
        "traditional_metrics": {
            "execution_time": 30.5,
            "success_rate": 0.95,
            "coordination_quality": 0.88,
        },
        "llm_evaluations": [],
        "graph_metrics": {
            "density": 0.75,
            "centrality": {"agent_1": 0.8},
            "clustering_coefficient": 0.65,
        },
        "run_metadata": {"seed": 42, "timestamp": datetime(2026, 1, 21, 10, 0, 0)},
    }

    report = reporter.generate_report(pipeline_results)

    # Report should be JSON-serializable
    json_str = json.dumps(report, default=str)
    assert json_str is not None
    assert len(json_str) > 0


def test_reporter_integrates_loguru_console_logging():
    """Test reporter integrates loguru for local console tracing by default."""
    with patch("agenteval.report.logger") as mock_logger:
        reporter = ConsolidatedReporter()

        pipeline_results = {
            "traditional_metrics": {"execution_time": 30.5},
            "llm_evaluations": [],
            "graph_metrics": {"density": 0.75},
            "run_metadata": {"seed": 42, "timestamp": datetime(2026, 1, 21, 10, 0, 0)},
        }

        reporter.generate_report(pipeline_results)

        # Loguru logger should be used
        assert mock_logger.info.called


def test_reporter_respects_console_logging_config():
    """Test reporter respects console_logging configuration setting."""
    # Test with console logging disabled
    with patch("agenteval.report.load_config") as mock_load_config:
        mock_config = Mock()
        mock_config.observability.console_logging = False
        mock_load_config.return_value = mock_config

        reporter = ConsolidatedReporter()

        pipeline_results = {
            "traditional_metrics": {"execution_time": 30.5},
            "llm_evaluations": [],
            "graph_metrics": {"density": 0.75},
            "run_metadata": {"seed": 42, "timestamp": datetime(2026, 1, 21, 10, 0, 0)},
        }

        # Should not raise even if console logging disabled
        report = reporter.generate_report(pipeline_results)
        assert report is not None


def test_reporter_supports_cloud_export_via_config():
    """Test reporter supports optional Logfire/Weave cloud export via configuration."""
    with patch("agenteval.report.load_config") as mock_load_config:
        mock_config = Mock()
        mock_config.observability.cloud_export = True
        mock_load_config.return_value = mock_config

        reporter = ConsolidatedReporter()

        pipeline_results = {
            "traditional_metrics": {"execution_time": 30.5},
            "llm_evaluations": [],
            "graph_metrics": {"density": 0.75},
            "run_metadata": {"seed": 42, "timestamp": datetime(2026, 1, 21, 10, 0, 0)},
        }

        # Should handle cloud export configuration
        report = reporter.generate_report(pipeline_results)
        assert report is not None


def test_reporter_outputs_structured_format():
    """Test reporter outputs combined results in structured format."""
    reporter = ConsolidatedReporter()

    pipeline_results = {
        "traditional_metrics": {
            "execution_time": 30.5,
            "success_rate": 0.95,
            "coordination_quality": 0.88,
        },
        "llm_evaluations": [
            Evaluation(
                id="eval_1",
                paper_id="paper_1",
                agent_review_id="agent_review_1",
                human_baseline_id="human_baseline_1",
                semantic_score=0.85,
                justification="Good quality review",
                evaluated_at=datetime(2026, 1, 21, 10, 0, 0),
            )
        ],
        "graph_metrics": {
            "density": 0.75,
            "centrality": {"agent_1": 0.8, "agent_2": 0.6},
            "clustering_coefficient": 0.65,
        },
        "run_metadata": {"seed": 42, "timestamp": datetime(2026, 1, 21, 10, 0, 0)},
    }

    report = reporter.generate_report(pipeline_results)

    # Verify structured format
    assert isinstance(report, dict)
    assert "report_id" in report
    assert "run_id" in report
    assert "created_at" in report


def test_reporter_saves_report_to_file():
    """Test reporter can save consolidated report to JSON file."""
    reporter = ConsolidatedReporter()

    pipeline_results = {
        "traditional_metrics": {"execution_time": 30.5},
        "llm_evaluations": [],
        "graph_metrics": {"density": 0.75},
        "run_metadata": {"seed": 42, "timestamp": datetime(2026, 1, 21, 10, 0, 0)},
    }

    with patch("pathlib.Path.open", create=True) as mock_open:
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        output_path = Path("/tmp/test_report.json")
        reporter.save_report(pipeline_results, output_path)

        # Verify file write was attempted
        mock_open.assert_called_once()


def test_reporter_includes_summary_statistics():
    """Test reporter includes summary statistics in output."""
    reporter = ConsolidatedReporter()

    pipeline_results = {
        "traditional_metrics": {
            "execution_time": 30.5,
            "success_rate": 0.95,
            "coordination_quality": 0.88,
        },
        "llm_evaluations": [
            Evaluation(
                id="eval_1",
                paper_id="paper_1",
                agent_review_id="agent_review_1",
                human_baseline_id="human_baseline_1",
                semantic_score=0.85,
                justification="Good quality",
                evaluated_at=datetime(2026, 1, 21, 10, 0, 0),
            ),
            Evaluation(
                id="eval_2",
                paper_id="paper_2",
                agent_review_id="agent_review_2",
                human_baseline_id="human_baseline_2",
                semantic_score=0.75,
                justification="Acceptable quality",
                evaluated_at=datetime(2026, 1, 21, 10, 0, 0),
            ),
        ],
        "graph_metrics": {
            "density": 0.75,
            "centrality": {"agent_1": 0.8},
            "clustering_coefficient": 0.65,
        },
        "run_metadata": {"seed": 42, "timestamp": datetime(2026, 1, 21, 10, 0, 0)},
    }

    report = reporter.generate_report(pipeline_results)

    # Should include summary statistics
    assert "summary" in report
    assert "total_evaluations" in report["summary"]
    assert report["summary"]["total_evaluations"] == 2
