"""Tests for consolidated reporting and observability.

Tests verify that the reporting module combines results from all three evaluation tiers
(traditional, LLM judge, graph) into unified reports with integrated observability.
"""

from unittest.mock import patch

from agenteval.report import ReportGenerator

from agenteval.models.evaluation import Evaluation, Metrics


def test_combine_results_from_all_three_evaluation_tiers():
    """Test that report combines traditional, LLM judge, and graph metrics."""
    report_gen = ReportGenerator()

    # Mock pipeline results
    pipeline_results = {
        "traditional_metrics": Metrics(
            execution_time_seconds=120.5,
            task_success_rate=0.85,
            coordination_quality=0.92,
            semantic_similarity=None,
            graph_density=None,
            graph_centrality=None,
        ),
        "llm_evaluation": Evaluation(
            evaluation_id="eval_001",
            paper_id="paper_001",
            agent_review_id="agent_001",
            baseline_review_id="baseline_001",
            llm_judge_score=0.88,
            llm_judge_justification="High quality review with good coverage",
            metrics={},
        ),
        "graph_metrics": {
            "density": 0.75,
            "avg_centrality": 0.65,
            "clustering_coefficient": 0.82,
        },
    }

    report = report_gen.generate_report(pipeline_results)

    # Report should contain all three tier results
    assert "traditional_metrics" in report
    assert "llm_evaluation" in report
    assert "graph_metrics" in report


def test_generate_consolidated_json_report_with_all_metrics():
    """Test that report generates JSON with all metrics in structured format."""
    report_gen = ReportGenerator()

    pipeline_results = {
        "traditional_metrics": Metrics(
            execution_time_seconds=60.0,
            task_success_rate=1.0,
            coordination_quality=0.95,
            semantic_similarity=None,
            graph_density=None,
            graph_centrality=None,
        ),
        "llm_evaluation": Evaluation(
            evaluation_id="eval_002",
            paper_id="paper_002",
            agent_review_id="agent_002",
            baseline_review_id="baseline_002",
            llm_judge_score=0.92,
            llm_judge_justification="Excellent alignment with baseline",
            metrics={"semantic_similarity": 0.91},
        ),
        "graph_metrics": {
            "density": 0.80,
            "avg_centrality": 0.70,
        },
    }

    report = report_gen.generate_report(pipeline_results)

    # Report should be JSON-serializable
    json_report = report_gen.to_json(report)
    assert json_report is not None
    assert isinstance(json_report, str)
    assert "execution_time_seconds" in json_report
    assert "llm_judge_score" in json_report
    assert "density" in json_report


def test_integrate_loguru_for_local_console_tracing():
    """Test that loguru is integrated for local console tracing by default."""
    # Verify loguru is configured and ready to use
    with patch("agenteval.report.logger") as mock_logger:
        report_gen = ReportGenerator()
        report_gen.log_event("test_event", {"key": "value"})

        # Loguru logger should be called
        mock_logger.info.assert_called()


def test_support_optional_logfire_cloud_export_via_config():
    """Test that Logfire cloud export can be enabled via configuration."""
    # Test with Logfire enabled in config
    config = {"observability": {"backend": "logfire", "log_level": "INFO"}}

    with patch("agenteval.report.configure_logfire") as mock_logfire:
        report_gen = ReportGenerator(config=config)

        # Logfire should be configured when backend is set to logfire
        if config["observability"]["backend"] == "logfire":
            assert mock_logfire.called or hasattr(report_gen, "logfire_enabled")


def test_support_optional_weave_cloud_export_via_config():
    """Test that Weave cloud export can be enabled via configuration."""
    # Test with Weave enabled in config
    config = {"observability": {"backend": "weave", "log_level": "INFO"}}

    with patch("agenteval.report.configure_weave") as mock_weave:
        report_gen = ReportGenerator(config=config)

        # Weave should be configured when backend is set to weave
        if config["observability"]["backend"] == "weave":
            assert mock_weave.called or hasattr(report_gen, "weave_enabled")


def test_output_combined_results_in_structured_format():
    """Test that report outputs results in a structured, machine-readable format."""
    report_gen = ReportGenerator()

    pipeline_results = {
        "traditional_metrics": Metrics(
            execution_time_seconds=45.5,
            task_success_rate=0.90,
            coordination_quality=0.88,
            semantic_similarity=None,
            graph_density=None,
            graph_centrality=None,
        ),
        "llm_evaluation": Evaluation(
            evaluation_id="eval_003",
            paper_id="paper_003",
            agent_review_id="agent_003",
            baseline_review_id="baseline_003",
            llm_judge_score=0.85,
            llm_judge_justification="Good quality review",
            metrics={},
        ),
        "graph_metrics": {
            "density": 0.70,
            "avg_centrality": 0.60,
            "clustering_coefficient": 0.75,
        },
    }

    report = report_gen.generate_report(pipeline_results)

    # Report should have structured format
    assert isinstance(report, dict)
    assert "metadata" in report
    assert "results" in report
    assert report["metadata"]["timestamp"] is not None
    assert report["metadata"]["report_id"] is not None


def test_report_includes_aggregate_statistics():
    """Test that report includes aggregate statistics across all tiers."""
    report_gen = ReportGenerator()

    pipeline_results = {
        "traditional_metrics": Metrics(
            execution_time_seconds=100.0,
            task_success_rate=0.80,
            coordination_quality=0.85,
            semantic_similarity=None,
            graph_density=None,
            graph_centrality=None,
        ),
        "llm_evaluation": Evaluation(
            evaluation_id="eval_004",
            paper_id="paper_004",
            agent_review_id="agent_004",
            baseline_review_id="baseline_004",
            llm_judge_score=0.78,
            llm_judge_justification="Acceptable quality",
            metrics={"semantic_similarity": 0.80},
        ),
        "graph_metrics": {
            "density": 0.65,
            "avg_centrality": 0.55,
        },
    }

    report = report_gen.generate_report(pipeline_results)

    # Should include aggregate metrics
    assert "aggregate_metrics" in report
    aggregate = report["aggregate_metrics"]
    assert "overall_quality_score" in aggregate or len(aggregate) > 0


def test_report_handles_missing_optional_tiers():
    """Test that report handles cases where some evaluation tiers are missing."""
    report_gen = ReportGenerator()

    # Only traditional metrics provided
    pipeline_results = {
        "traditional_metrics": Metrics(
            execution_time_seconds=30.0,
            task_success_rate=0.95,
            coordination_quality=0.90,
            semantic_similarity=None,
            graph_density=None,
            graph_centrality=None,
        ),
    }

    report = report_gen.generate_report(pipeline_results)

    # Report should still be generated with available data
    assert report is not None
    assert "traditional_metrics" in report
    # Should gracefully handle missing tiers
    assert report.get("llm_evaluation") is None or "llm_evaluation" not in report
    assert report.get("graph_metrics") is None or "graph_metrics" not in report


def test_report_handles_empty_pipeline_results():
    """Test that report handles completely empty pipeline results gracefully."""
    report_gen = ReportGenerator()

    # Empty pipeline results
    pipeline_results = {}

    report = report_gen.generate_report(pipeline_results)

    # Report should still be generated with minimal structure
    assert report is not None
    assert "metadata" in report
    assert "results" in report
    assert "aggregate_metrics" in report
    assert report["metadata"]["timestamp"] is not None
    assert report["metadata"]["report_id"] is not None
