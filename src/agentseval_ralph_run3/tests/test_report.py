"""Tests for consolidated reporting and observability.

This module tests the consolidation of results from all evaluation tiers
into unified reports with integrated observability.
"""

from datetime import datetime
from pathlib import Path

import pytest
from agenteval.report import ConsolidatedReport, ReportConfig, ReportGenerator

from agenteval.pipeline import PipelineResult


@pytest.fixture
def sample_pipeline_result() -> PipelineResult:
    """Provide sample pipeline result for testing."""
    return PipelineResult(
        run_id="test-run-123",
        timestamp=datetime(2024, 1, 1, 10, 0, 0),
        traditional_metrics={
            "execution_time_seconds": 10.5,
            "success_rate": 0.85,
            "coordination_quality": 0.9,
        },
        llm_judge_results=[
            {
                "review_id": "review-1",
                "semantic_score": 0.8,
                "justification": "Good quality review",
                "baseline_review_id": "baseline-1",
            },
        ],
        graph_metrics={
            "density": 0.6,
            "avg_clustering_coefficient": 0.5,
            "avg_betweenness_centrality": 0.3,
            "avg_closeness_centrality": 0.7,
            "num_nodes": 5,
            "num_edges": 10,
        },
    )


class TestReportConfig:
    """Test report configuration."""

    def test_default_config(self) -> None:
        """Test default report configuration with loguru enabled."""
        config = ReportConfig()
        assert config.loguru_enabled is True
        assert config.logfire_enabled is False
        assert config.weave_enabled is False

    def test_custom_config(self) -> None:
        """Test custom report configuration."""
        config = ReportConfig(
            loguru_enabled=False,
            logfire_enabled=True,
            weave_enabled=True,
        )
        assert config.loguru_enabled is False
        assert config.logfire_enabled is True
        assert config.weave_enabled is True


class TestConsolidatedReport:
    """Test consolidated report data model."""

    def test_report_structure(self, sample_pipeline_result: PipelineResult) -> None:
        """Test consolidated report has correct structure."""
        report = ConsolidatedReport(
            run_id=sample_pipeline_result.run_id,
            timestamp=sample_pipeline_result.timestamp,
            traditional_metrics=sample_pipeline_result.traditional_metrics,
            llm_judge_results=sample_pipeline_result.llm_judge_results,
            graph_metrics=sample_pipeline_result.graph_metrics,
        )

        assert report.run_id == "test-run-123"
        assert report.timestamp == datetime(2024, 1, 1, 10, 0, 0)
        assert report.traditional_metrics["execution_time_seconds"] == 10.5
        assert len(report.llm_judge_results) == 1
        assert report.graph_metrics["num_nodes"] == 5

    def test_report_json_serialization(self, sample_pipeline_result: PipelineResult) -> None:
        """Test report can be serialized to JSON."""
        report = ConsolidatedReport(
            run_id=sample_pipeline_result.run_id,
            timestamp=sample_pipeline_result.timestamp,
            traditional_metrics=sample_pipeline_result.traditional_metrics,
            llm_judge_results=sample_pipeline_result.llm_judge_results,
            graph_metrics=sample_pipeline_result.graph_metrics,
        )

        json_data = report.model_dump_json()
        assert isinstance(json_data, str)
        assert "test-run-123" in json_data
        assert "traditional_metrics" in json_data
        assert "llm_judge_results" in json_data
        assert "graph_metrics" in json_data


class TestReportGenerator:
    """Test report generator."""

    def test_generator_initialization(self) -> None:
        """Test report generator can be initialized."""
        config = ReportConfig()
        generator = ReportGenerator(config)
        assert generator.config == config

    def test_generator_with_loguru_enabled(self) -> None:
        """Test generator initializes with loguru enabled by default."""
        config = ReportConfig(loguru_enabled=True)
        generator = ReportGenerator(config)
        assert generator.config.loguru_enabled is True

    def test_generate_report_from_pipeline_result(
        self, sample_pipeline_result: PipelineResult
    ) -> None:
        """Test generating consolidated report from pipeline result."""
        config = ReportConfig()
        generator = ReportGenerator(config)

        report = generator.generate_report(sample_pipeline_result)

        assert isinstance(report, ConsolidatedReport)
        assert report.run_id == sample_pipeline_result.run_id
        assert report.timestamp == sample_pipeline_result.timestamp
        assert report.traditional_metrics == sample_pipeline_result.traditional_metrics
        assert report.llm_judge_results == sample_pipeline_result.llm_judge_results
        assert report.graph_metrics == sample_pipeline_result.graph_metrics

    def test_save_report_to_json(
        self, sample_pipeline_result: PipelineResult, tmp_path: Path
    ) -> None:
        """Test saving report to JSON file."""
        config = ReportConfig()
        generator = ReportGenerator(config)
        report = generator.generate_report(sample_pipeline_result)

        output_file = tmp_path / "report.json"
        generator.save_report(report, output_file)

        assert output_file.exists()

        # Verify JSON content
        import json

        with open(output_file) as f:
            data = json.load(f)

        assert data["run_id"] == "test-run-123"
        assert "traditional_metrics" in data
        assert "llm_judge_results" in data
        assert "graph_metrics" in data

    def test_generate_and_save_combined(
        self, sample_pipeline_result: PipelineResult, tmp_path: Path
    ) -> None:
        """Test combined generate and save workflow."""
        config = ReportConfig()
        generator = ReportGenerator(config)

        output_file = tmp_path / "combined_report.json"
        report = generator.generate_report(sample_pipeline_result)
        generator.save_report(report, output_file)

        assert output_file.exists()

        # Verify saved content matches input
        import json

        with open(output_file) as f:
            data = json.load(f)

        assert data["run_id"] == sample_pipeline_result.run_id
        assert (
            data["traditional_metrics"]["execution_time_seconds"]
            == sample_pipeline_result.traditional_metrics["execution_time_seconds"]
        )

    def test_observability_logfire_config(self) -> None:
        """Test generator respects logfire configuration."""
        config = ReportConfig(logfire_enabled=True)
        generator = ReportGenerator(config)
        assert generator.config.logfire_enabled is True

    def test_observability_weave_config(self) -> None:
        """Test generator respects weave configuration."""
        config = ReportConfig(weave_enabled=True)
        generator = ReportGenerator(config)
        assert generator.config.weave_enabled is True

    def test_consolidated_report_combines_all_tiers(
        self, sample_pipeline_result: PipelineResult
    ) -> None:
        """Test that consolidated report includes all three evaluation tiers."""
        config = ReportConfig()
        generator = ReportGenerator(config)
        report = generator.generate_report(sample_pipeline_result)

        # Verify all three tiers are present
        assert report.traditional_metrics is not None
        assert len(report.traditional_metrics) > 0

        assert report.llm_judge_results is not None
        assert len(report.llm_judge_results) > 0

        assert report.graph_metrics is not None
        assert len(report.graph_metrics) > 0
