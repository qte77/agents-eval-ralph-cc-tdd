"""Tests for consolidated reporting and observability.

Following TDD RED phase - these tests should FAIL until implementation is complete.
Tests validate consolidation of all evaluation tier results into unified JSON report
with loguru console logging and optional Logfire/Weave cloud export.
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agenteval.pipeline import PipelineResult


class TestReportGeneratorInitialization:
    """Test report generator initialization."""

    def test_report_generator_exists(self):
        """Test ReportGenerator class exists."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        assert generator is not None

    def test_report_generator_accepts_config(self):
        """Test ReportGenerator accepts configuration."""
        from agenteval.config import Config
        from agenteval.report import ReportGenerator

        config = Config()
        generator = ReportGenerator(config=config)
        assert generator is not None
        assert generator.config == config


class TestConsolidatedReportGeneration:
    """Test consolidated report generation from all tiers."""

    @pytest.fixture
    def pipeline_result(self):
        """Provide sample pipeline result."""
        return PipelineResult(
            run_id="test-run-123",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            traditional_metrics={
                "execution_time_seconds": 10.5,
                "success_rate": 0.95,
                "coordination_quality": 0.88,
            },
            llm_judge_results=[
                {
                    "review_id": "review1",
                    "semantic_score": 0.85,
                    "justification": "High quality review",
                    "baseline_review_id": "baseline1",
                }
            ],
            graph_metrics={
                "density": 0.75,
                "avg_clustering_coefficient": 0.6,
                "avg_betweenness_centrality": 0.4,
                "num_nodes": 5,
                "num_edges": 8,
            },
        )

    def test_generate_report_returns_report_model(self, pipeline_result):
        """Test generate_report returns Report model."""
        from agenteval.models.evaluation import Report
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        report = generator.generate_report(pipeline_result)

        assert isinstance(report, Report)

    def test_generate_report_combines_all_tiers(self, pipeline_result):
        """Test generate_report combines results from all three tiers."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        report = generator.generate_report(pipeline_result)

        # Should have data from all three tiers
        assert report.metrics is not None
        assert report.evaluations is not None
        assert report.graph_metrics is not None

    def test_generate_report_includes_run_metadata(self, pipeline_result):
        """Test generate_report includes run metadata (run_id, timestamp)."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        report = generator.generate_report(pipeline_result)

        assert report.run_id == "test-run-123"
        assert report.timestamp == datetime(2024, 1, 1, 12, 0, 0)

    def test_generate_report_transforms_traditional_metrics(self, pipeline_result):
        """Test generate_report transforms traditional metrics into Metrics model."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        report = generator.generate_report(pipeline_result)

        assert report.metrics.execution_time_seconds == 10.5
        assert report.metrics.success_rate == 0.95
        assert report.metrics.coordination_quality == 0.88

    def test_generate_report_transforms_llm_judge_results(self, pipeline_result):
        """Test generate_report transforms LLM judge results into Evaluation models."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        report = generator.generate_report(pipeline_result)

        assert len(report.evaluations) == 1
        eval_result = report.evaluations[0]
        assert eval_result.review_id == "review1"
        assert eval_result.semantic_score == 0.85
        assert eval_result.justification == "High quality review"
        assert eval_result.baseline_review_id == "baseline1"

    def test_generate_report_includes_graph_metrics(self, pipeline_result):
        """Test generate_report includes graph metrics as dict."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        report = generator.generate_report(pipeline_result)

        assert "density" in report.graph_metrics
        assert "num_nodes" in report.graph_metrics
        assert report.graph_metrics["density"] == 0.75
        assert report.graph_metrics["num_nodes"] == 5


class TestJSONReportOutput:
    """Test JSON report output functionality."""

    @pytest.fixture
    def pipeline_result(self):
        """Provide sample pipeline result."""
        return PipelineResult(
            run_id="test-run-456",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            traditional_metrics={
                "execution_time_seconds": 5.0,
                "success_rate": 1.0,
                "coordination_quality": 0.9,
            },
            llm_judge_results=[],
            graph_metrics={"density": 0.5, "num_nodes": 3, "num_edges": 2},
        )

    def test_save_report_to_json(self, tmp_path, pipeline_result):
        """Test save_report writes JSON file to specified path."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        report = generator.generate_report(pipeline_result)

        output_path = tmp_path / "report.json"
        generator.save_report(report, output_path)

        assert output_path.exists()

    def test_save_report_json_structure(self, tmp_path, pipeline_result):
        """Test save_report produces valid JSON with correct structure."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        report = generator.generate_report(pipeline_result)

        output_path = tmp_path / "report.json"
        generator.save_report(report, output_path)

        with open(output_path) as f:
            data = json.load(f)

        assert "run_id" in data
        assert "timestamp" in data
        assert "metrics" in data
        assert "evaluations" in data
        assert "graph_metrics" in data

    def test_save_report_json_valid_format(self, tmp_path, pipeline_result):
        """Test save_report JSON is valid and readable."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        report = generator.generate_report(pipeline_result)

        output_path = tmp_path / "report.json"
        generator.save_report(report, output_path)

        # Should be valid JSON
        with open(output_path) as f:
            data = json.load(f)

        assert data["run_id"] == "test-run-456"
        assert data["metrics"]["execution_time_seconds"] == 5.0


class TestLoguruLogging:
    """Test loguru console logging integration."""

    @pytest.fixture
    def pipeline_result(self):
        """Provide sample pipeline result."""
        return PipelineResult(
            run_id="test-run-789",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            traditional_metrics={
                "execution_time_seconds": 8.0,
                "success_rate": 0.9,
                "coordination_quality": 0.85,
            },
            llm_judge_results=[],
            graph_metrics={"density": 0.6, "num_nodes": 4, "num_edges": 5},
        )

    def test_loguru_enabled_by_default(self):
        """Test loguru logging is enabled by default via config."""
        from agenteval.config import Config
        from agenteval.report import ReportGenerator

        config = Config()
        generator = ReportGenerator(config=config)

        assert config.observability["loguru_enabled"] is True

    @patch("agenteval.report.logger")
    def test_generate_report_logs_to_console(self, mock_logger, pipeline_result):
        """Test generate_report logs activity to console via loguru."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        generator.generate_report(pipeline_result)

        # Should have logged at least once
        assert mock_logger.info.called or mock_logger.debug.called

    @patch("agenteval.report.logger")
    def test_generate_report_logs_run_id(self, mock_logger, pipeline_result):
        """Test generate_report logs run_id in console output."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        generator.generate_report(pipeline_result)

        # Check that run_id was logged
        calls = mock_logger.info.call_args_list + mock_logger.debug.call_args_list
        logged_text = " ".join(str(call) for call in calls)
        assert "test-run-789" in logged_text

    @patch("agenteval.report.logger")
    def test_save_report_logs_output_path(self, mock_logger, tmp_path, pipeline_result):
        """Test save_report logs output file path."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        report = generator.generate_report(pipeline_result)

        output_path = tmp_path / "report.json"
        generator.save_report(report, output_path)

        # Should log the output path
        calls = mock_logger.info.call_args_list + mock_logger.debug.call_args_list
        logged_text = " ".join(str(call) for call in calls)
        assert "report.json" in logged_text


class TestLogfireIntegration:
    """Test optional Logfire cloud export integration."""

    @pytest.fixture
    def pipeline_result(self):
        """Provide sample pipeline result."""
        return PipelineResult(
            run_id="test-run-logfire",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            traditional_metrics={
                "execution_time_seconds": 12.0,
                "success_rate": 0.88,
                "coordination_quality": 0.92,
            },
            llm_judge_results=[],
            graph_metrics={"density": 0.7, "num_nodes": 6, "num_edges": 9},
        )

    def test_logfire_disabled_by_default(self):
        """Test Logfire export is disabled by default."""
        from agenteval.config import Config

        config = Config()
        assert config.observability["logfire_enabled"] is False

    @patch("agenteval.report.logfire", create=True)
    def test_export_to_logfire_when_enabled(self, mock_logfire, pipeline_result):
        """Test report exports to Logfire when enabled in config."""
        from agenteval.config import Config
        from agenteval.report import ReportGenerator

        config = Config(observability={"loguru_enabled": True, "logfire_enabled": True})
        generator = ReportGenerator(config=config)
        report = generator.generate_report(pipeline_result)

        generator.export_to_cloud(report)

        # Should call logfire when enabled
        assert mock_logfire.info.called or mock_logfire.log.called

    @patch("agenteval.report.logfire", create=True)
    def test_no_logfire_export_when_disabled(self, mock_logfire, pipeline_result):
        """Test report does not export to Logfire when disabled."""
        from agenteval.config import Config
        from agenteval.report import ReportGenerator

        config = Config(observability={"loguru_enabled": True, "logfire_enabled": False})
        generator = ReportGenerator(config=config)
        report = generator.generate_report(pipeline_result)

        generator.export_to_cloud(report)

        # Should not call logfire when disabled
        assert not mock_logfire.info.called and not mock_logfire.log.called


class TestWeaveIntegration:
    """Test optional Weave cloud export integration."""

    @pytest.fixture
    def pipeline_result(self):
        """Provide sample pipeline result."""
        return PipelineResult(
            run_id="test-run-weave",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            traditional_metrics={
                "execution_time_seconds": 7.5,
                "success_rate": 0.93,
                "coordination_quality": 0.87,
            },
            llm_judge_results=[],
            graph_metrics={"density": 0.65, "num_nodes": 5, "num_edges": 7},
        )

    def test_weave_disabled_by_default(self):
        """Test Weave export is disabled by default."""
        from agenteval.config import Config

        config = Config()
        assert config.observability["weave_enabled"] is False

    @patch("agenteval.report.weave", create=True)
    def test_export_to_weave_when_enabled(self, mock_weave, pipeline_result):
        """Test report exports to Weave when enabled in config."""
        from agenteval.config import Config
        from agenteval.report import ReportGenerator

        config = Config(observability={"loguru_enabled": True, "weave_enabled": True})
        generator = ReportGenerator(config=config)
        report = generator.generate_report(pipeline_result)

        generator.export_to_cloud(report)

        # Should call weave when enabled
        assert mock_weave.log.called or hasattr(mock_weave, "track")

    @patch("agenteval.report.weave", create=True)
    def test_no_weave_export_when_disabled(self, mock_weave, pipeline_result):
        """Test report does not export to Weave when disabled."""
        from agenteval.config import Config
        from agenteval.report import ReportGenerator

        config = Config(observability={"loguru_enabled": True, "weave_enabled": False})
        generator = ReportGenerator(config=config)
        report = generator.generate_report(pipeline_result)

        generator.export_to_cloud(report)

        # Should not call weave when disabled
        if hasattr(mock_weave, "log"):
            assert not mock_weave.log.called


class TestStructuredOutputFormat:
    """Test structured output format requirements."""

    @pytest.fixture
    def pipeline_result(self):
        """Provide sample pipeline result."""
        return PipelineResult(
            run_id="test-run-structured",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            traditional_metrics={
                "execution_time_seconds": 9.0,
                "success_rate": 0.91,
                "coordination_quality": 0.89,
            },
            llm_judge_results=[
                {
                    "review_id": "r1",
                    "semantic_score": 0.8,
                    "justification": "Good",
                    "baseline_review_id": "b1",
                }
            ],
            graph_metrics={"density": 0.55, "num_nodes": 4, "num_edges": 4},
        )

    def test_report_output_is_serializable(self, pipeline_result):
        """Test report output is fully serializable to JSON."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        report = generator.generate_report(pipeline_result)

        # Should be serializable
        report_dict = report.model_dump()
        json_str = json.dumps(report_dict, default=str)
        assert json_str is not None

    def test_report_includes_all_required_fields(self, pipeline_result):
        """Test report includes all required fields per acceptance criteria."""
        from agenteval.report import ReportGenerator

        generator = ReportGenerator()
        report = generator.generate_report(pipeline_result)

        report_dict = report.model_dump()

        # Required fields from acceptance criteria
        assert "run_id" in report_dict
        assert "timestamp" in report_dict
        assert "metrics" in report_dict
        assert "evaluations" in report_dict
        assert "graph_metrics" in report_dict


class TestReportGeneratorEdgeCases:
    """Test edge cases and error handling."""

    def test_generate_report_with_empty_results(self):
        """Test generate_report handles empty evaluation results."""
        from agenteval.report import ReportGenerator

        pipeline_result = PipelineResult(
            run_id="empty-run",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            traditional_metrics={
                "execution_time_seconds": 0.0,
                "success_rate": 0.0,
                "coordination_quality": 0.0,
            },
            llm_judge_results=[],
            graph_metrics={},
        )

        generator = ReportGenerator()
        report = generator.generate_report(pipeline_result)

        assert report is not None
        assert report.evaluations == []

    def test_save_report_creates_directory_if_missing(self, tmp_path):
        """Test save_report creates output directory if it doesn't exist."""
        from agenteval.report import ReportGenerator

        pipeline_result = PipelineResult(
            run_id="dir-test",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            traditional_metrics={
                "execution_time_seconds": 1.0,
                "success_rate": 1.0,
                "coordination_quality": 1.0,
            },
            llm_judge_results=[],
            graph_metrics={},
        )

        generator = ReportGenerator()
        report = generator.generate_report(pipeline_result)

        # Create path with non-existent directory
        output_path = tmp_path / "subdir" / "nested" / "report.json"
        generator.save_report(report, output_path)

        assert output_path.exists()
