"""Tests for consolidated reporting and observability.

Following TDD approach - these tests should FAIL initially.
Tests validate report generation: combining all evaluation tier results,
generating consolidated JSON reports, integrating observability (loguru),
and supporting optional cloud export (Logfire/Weave).
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from agenteval.models.evaluation import Evaluation, Metrics, Report


class TestReportGeneration:
    """Tests for generating consolidated reports."""

    def test_generate_report_combines_all_tiers(self):
        """Test report combines results from all three evaluation tiers."""
        from agenteval.report import generate_report

        # Mock results from all three tiers
        traditional_metrics = Metrics(
            execution_time_seconds=50.0,
            success_rate=0.75,
            coordination_quality=0.8,
        )

        llm_evaluation = Evaluation(
            review_id="agent_review_1",
            semantic_score=0.85,
            justification="High quality review with good coverage",
            baseline_review_id="baseline_review_1",
        )

        graph_metrics = {
            "density": 0.5,
            "centrality": {"agent1": 0.8, "agent2": 0.5},
            "clustering_coefficient": 0.3,
            "coordination_patterns": ["sequential", "parallel"],
        }

        report = generate_report(
            run_id="test_run_001",
            traditional_metrics=traditional_metrics,
            llm_evaluations=[llm_evaluation],
            graph_metrics=graph_metrics,
        )

        assert report is not None
        assert isinstance(report, Report)
        assert report.run_id == "test_run_001"
        assert report.metrics == traditional_metrics
        assert len(report.evaluations) == 1
        assert report.evaluations[0] == llm_evaluation
        assert report.graph_metrics == graph_metrics

    def test_generate_report_creates_timestamp(self):
        """Test report includes timestamp of generation."""
        from agenteval.report import generate_report

        traditional_metrics = Metrics(
            execution_time_seconds=50.0,
            success_rate=0.75,
            coordination_quality=0.8,
        )

        report = generate_report(
            run_id="test_run_002",
            traditional_metrics=traditional_metrics,
            llm_evaluations=[],
            graph_metrics={},
        )

        assert report.timestamp is not None
        assert isinstance(report.timestamp, datetime)

    def test_generate_report_with_multiple_evaluations(self):
        """Test report handles multiple LLM evaluations."""
        from agenteval.report import generate_report

        traditional_metrics = Metrics(
            execution_time_seconds=50.0,
            success_rate=0.75,
            coordination_quality=0.8,
        )

        llm_evaluations = [
            Evaluation(
                review_id="agent_review_1",
                semantic_score=0.85,
                justification="Good quality",
                baseline_review_id="baseline_review_1",
            ),
            Evaluation(
                review_id="agent_review_2",
                semantic_score=0.75,
                justification="Decent quality",
                baseline_review_id="baseline_review_2",
            ),
        ]

        graph_metrics = {"density": 0.5}

        report = generate_report(
            run_id="test_run_003",
            traditional_metrics=traditional_metrics,
            llm_evaluations=llm_evaluations,
            graph_metrics=graph_metrics,
        )

        assert len(report.evaluations) == 2
        assert report.evaluations[0].review_id == "agent_review_1"
        assert report.evaluations[1].review_id == "agent_review_2"


class TestReportSerialization:
    """Tests for report serialization to JSON."""

    def test_save_report_to_json(self):
        """Test saving report to JSON file."""
        from agenteval.report import save_report

        traditional_metrics = Metrics(
            execution_time_seconds=50.0,
            success_rate=0.75,
            coordination_quality=0.8,
        )

        llm_evaluation = Evaluation(
            review_id="agent_review_1",
            semantic_score=0.85,
            justification="Good quality",
            baseline_review_id="baseline_review_1",
        )

        report = Report(
            run_id="test_run_004",
            timestamp=datetime.now(),
            metrics=traditional_metrics,
            evaluations=[llm_evaluation],
            graph_metrics={"density": 0.5},
        )

        output_path = Path("/tmp/test_report.json")

        save_report(report, output_path)

        assert output_path.exists()

        # Verify JSON content
        import json
        with open(output_path) as f:
            data = json.load(f)

        assert data["run_id"] == "test_run_004"
        assert "metrics" in data
        assert "evaluations" in data
        assert "graph_metrics" in data

    def test_load_report_from_json(self):
        """Test loading report from JSON file."""
        from agenteval.report import load_report, save_report

        traditional_metrics = Metrics(
            execution_time_seconds=50.0,
            success_rate=0.75,
            coordination_quality=0.8,
        )

        original_report = Report(
            run_id="test_run_005",
            timestamp=datetime.now(),
            metrics=traditional_metrics,
            evaluations=[],
            graph_metrics={},
        )

        output_path = Path("/tmp/test_report_load.json")
        save_report(original_report, output_path)

        loaded_report = load_report(output_path)

        assert loaded_report.run_id == original_report.run_id
        assert loaded_report.metrics == original_report.metrics


class TestObservabilityIntegration:
    """Tests for observability integration."""

    @patch("agenteval.report.logger")
    def test_loguru_logging_enabled_by_default(self, mock_logger):
        """Test loguru logging is integrated and enabled by default."""
        from agenteval.report import generate_report

        traditional_metrics = Metrics(
            execution_time_seconds=50.0,
            success_rate=0.75,
            coordination_quality=0.8,
        )

        generate_report(
            run_id="test_run_006",
            traditional_metrics=traditional_metrics,
            llm_evaluations=[],
            graph_metrics={},
        )

        # Verify logger was called
        mock_logger.info.assert_called()

    def test_observability_config_integration(self):
        """Test observability respects configuration settings."""
        from agenteval.config.config import Config
        from agenteval.report import generate_report_with_config

        config = Config(
            observability={
                "loguru_enabled": True,
                "logfire_enabled": False,
                "weave_enabled": False,
            }
        )

        traditional_metrics = Metrics(
            execution_time_seconds=50.0,
            success_rate=0.75,
            coordination_quality=0.8,
        )

        report = generate_report_with_config(
            run_id="test_run_007",
            traditional_metrics=traditional_metrics,
            llm_evaluations=[],
            graph_metrics={},
            config=config,
        )

        assert report is not None

    @patch("agenteval.report.logger")
    def test_loguru_traces_report_generation(self, mock_logger):
        """Test loguru traces report generation steps."""
        from agenteval.report import generate_report

        traditional_metrics = Metrics(
            execution_time_seconds=50.0,
            success_rate=0.75,
            coordination_quality=0.8,
        )

        generate_report(
            run_id="test_run_008",
            traditional_metrics=traditional_metrics,
            llm_evaluations=[],
            graph_metrics={},
        )

        # Verify key steps are logged
        assert mock_logger.info.call_count >= 1

    def test_cloud_export_disabled_by_default(self):
        """Test Logfire/Weave export disabled by default."""
        from agenteval.config.config import Config

        config = Config()

        assert config.observability["loguru_enabled"] is True
        assert config.observability["logfire_enabled"] is False
        assert config.observability["weave_enabled"] is False

    @patch("agenteval.report.export_to_logfire")
    def test_optional_logfire_export(self, mock_export):
        """Test optional Logfire cloud export when enabled."""
        from agenteval.config.config import Config
        from agenteval.report import generate_report_with_config

        config = Config(
            observability={
                "loguru_enabled": True,
                "logfire_enabled": True,
                "weave_enabled": False,
            }
        )

        traditional_metrics = Metrics(
            execution_time_seconds=50.0,
            success_rate=0.75,
            coordination_quality=0.8,
        )

        generate_report_with_config(
            run_id="test_run_009",
            traditional_metrics=traditional_metrics,
            llm_evaluations=[],
            graph_metrics={},
            config=config,
        )

        # Verify Logfire export was called when enabled
        mock_export.assert_called_once()

    @patch("agenteval.report.export_to_weave")
    def test_optional_weave_export(self, mock_export):
        """Test optional Weave cloud export when enabled."""
        from agenteval.config.config import Config
        from agenteval.report import generate_report_with_config

        config = Config(
            observability={
                "loguru_enabled": True,
                "logfire_enabled": False,
                "weave_enabled": True,
            }
        )

        traditional_metrics = Metrics(
            execution_time_seconds=50.0,
            success_rate=0.75,
            coordination_quality=0.8,
        )

        generate_report_with_config(
            run_id="test_run_010",
            traditional_metrics=traditional_metrics,
            llm_evaluations=[],
            graph_metrics={},
            config=config,
        )

        # Verify Weave export was called when enabled
        mock_export.assert_called_once()


class TestReportFormatting:
    """Tests for report output formatting."""

    def test_report_json_structure(self):
        """Test report exports to valid JSON with expected structure."""
        from agenteval.report import generate_report

        traditional_metrics = Metrics(
            execution_time_seconds=50.0,
            success_rate=0.75,
            coordination_quality=0.8,
        )

        llm_evaluation = Evaluation(
            review_id="agent_review_1",
            semantic_score=0.85,
            justification="Good",
            baseline_review_id="baseline_review_1",
        )

        graph_metrics = {"density": 0.5}

        report = generate_report(
            run_id="test_run_011",
            traditional_metrics=traditional_metrics,
            llm_evaluations=[llm_evaluation],
            graph_metrics=graph_metrics,
        )

        # Convert to JSON
        json_data = report.model_dump()

        assert "run_id" in json_data
        assert "timestamp" in json_data
        assert "metrics" in json_data
        assert "evaluations" in json_data
        assert "graph_metrics" in json_data

        # Verify nested structure
        assert "execution_time_seconds" in json_data["metrics"]
        assert "success_rate" in json_data["metrics"]
        assert "coordination_quality" in json_data["metrics"]

    def test_report_serialization_preserves_data(self):
        """Test report serialization preserves all data accurately."""
        from agenteval.report import generate_report

        traditional_metrics = Metrics(
            execution_time_seconds=123.45,
            success_rate=0.876,
            coordination_quality=0.654,
        )

        report = generate_report(
            run_id="test_run_012",
            traditional_metrics=traditional_metrics,
            llm_evaluations=[],
            graph_metrics={"custom_metric": 0.999},
        )

        json_data = report.model_dump()

        assert json_data["metrics"]["execution_time_seconds"] == 123.45
        assert json_data["metrics"]["success_rate"] == 0.876
        assert json_data["graph_metrics"]["custom_metric"] == 0.999
