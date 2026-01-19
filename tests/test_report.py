"""Tests for consolidated evaluation report generation.

Following TDD RED phase - these tests should FAIL until implementation is complete.
"""

import json
import pytest
from pathlib import Path


class TestEvaluationReport:
    """Test consolidated evaluation report generation."""

    def test_report_initialization(self):
        """Test report can be initialized with evaluation results."""
        from agenteval.report import EvaluationReport

        report = EvaluationReport(
            traditional_metrics={"execution_time": 1.5, "success_rate": 0.8},
            llm_evaluation={"overall_score": 7.5, "reasoning": "Good"},
            graph_analysis={"density": 0.6},
            metadata={"seed": 42, "timestamp": "2024-01-01T00:00:00"}
        )

        assert report is not None
        assert report.traditional_metrics is not None
        assert report.llm_evaluation is not None
        assert report.graph_analysis is not None
        assert report.metadata is not None

    def test_report_to_json(self):
        """Test report can be serialized to JSON format."""
        from agenteval.report import EvaluationReport

        report = EvaluationReport(
            traditional_metrics={"execution_time": 1.5, "success_rate": 0.8},
            llm_evaluation={"overall_score": 7.5, "reasoning": "Good"},
            graph_analysis={"density": 0.6},
            metadata={"seed": 42, "timestamp": "2024-01-01T00:00:00"}
        )

        json_output = report.to_json()

        # Should be valid JSON
        parsed = json.loads(json_output)
        assert "traditional_metrics" in parsed
        assert "llm_evaluation" in parsed
        assert "graph_analysis" in parsed
        assert "metadata" in parsed

    def test_report_to_dict(self):
        """Test report can be converted to dictionary."""
        from agenteval.report import EvaluationReport

        report = EvaluationReport(
            traditional_metrics={"execution_time": 1.5, "success_rate": 0.8},
            llm_evaluation={"overall_score": 7.5, "reasoning": "Good"},
            graph_analysis={"density": 0.6},
            metadata={"seed": 42, "timestamp": "2024-01-01T00:00:00"}
        )

        result_dict = report.to_dict()

        assert isinstance(result_dict, dict)
        assert "traditional_metrics" in result_dict
        assert result_dict["traditional_metrics"]["success_rate"] == 0.8

    def test_report_save_to_file(self):
        """Test report can be saved to JSON file."""
        from agenteval.report import EvaluationReport
        import tempfile

        report = EvaluationReport(
            traditional_metrics={"execution_time": 1.5, "success_rate": 0.8},
            llm_evaluation={"overall_score": 7.5, "reasoning": "Good"},
            graph_analysis={"density": 0.6},
            metadata={"seed": 42, "timestamp": "2024-01-01T00:00:00"}
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            filepath = Path(f.name)

        try:
            report.save(filepath)

            # Verify file was created and contains valid JSON
            assert filepath.exists()
            with open(filepath) as f:
                data = json.load(f)
                assert "traditional_metrics" in data
        finally:
            filepath.unlink(missing_ok=True)

    def test_report_load_from_file(self):
        """Test report can be loaded from JSON file."""
        from agenteval.report import EvaluationReport
        import tempfile

        report = EvaluationReport(
            traditional_metrics={"execution_time": 1.5, "success_rate": 0.8},
            llm_evaluation={"overall_score": 7.5, "reasoning": "Good"},
            graph_analysis={"density": 0.6},
            metadata={"seed": 42, "timestamp": "2024-01-01T00:00:00"}
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            filepath = Path(f.name)

        try:
            report.save(filepath)
            loaded_report = EvaluationReport.load(filepath)

            assert loaded_report.traditional_metrics == report.traditional_metrics
            assert loaded_report.llm_evaluation == report.llm_evaluation
            assert loaded_report.graph_analysis == report.graph_analysis
        finally:
            filepath.unlink(missing_ok=True)


class TestBatchReport:
    """Test batch report generation."""

    def test_batch_report_initialization(self):
        """Test batch report can combine multiple individual reports."""
        from agenteval.report import BatchReport, EvaluationReport

        reports = [
            EvaluationReport(
                traditional_metrics={"execution_time": 1.5, "success_rate": 0.8},
                llm_evaluation={"overall_score": 7.5, "reasoning": "Good"},
                graph_analysis={"density": 0.6},
                metadata={"seed": 42, "timestamp": "2024-01-01T00:00:00"}
            ),
            EvaluationReport(
                traditional_metrics={"execution_time": 2.0, "success_rate": 0.9},
                llm_evaluation={"overall_score": 8.0, "reasoning": "Excellent"},
                graph_analysis={"density": 0.7},
                metadata={"seed": 43, "timestamp": "2024-01-01T00:01:00"}
            )
        ]

        batch_report = BatchReport(reports=reports)

        assert batch_report is not None
        assert len(batch_report.reports) == 2

    def test_batch_report_aggregate_metrics(self):
        """Test batch report calculates aggregate metrics."""
        from agenteval.report import BatchReport, EvaluationReport

        reports = [
            EvaluationReport(
                traditional_metrics={"execution_time": 1.5, "success_rate": 0.8},
                llm_evaluation={"overall_score": 7.5, "reasoning": "Good"},
                graph_analysis={"density": 0.6},
                metadata={"seed": 42, "timestamp": "2024-01-01T00:00:00"}
            ),
            EvaluationReport(
                traditional_metrics={"execution_time": 2.0, "success_rate": 0.9},
                llm_evaluation={"overall_score": 8.0, "reasoning": "Excellent"},
                graph_analysis={"density": 0.7},
                metadata={"seed": 43, "timestamp": "2024-01-01T00:01:00"}
            )
        ]

        batch_report = BatchReport(reports=reports)
        aggregates = batch_report.aggregate_metrics()

        assert "avg_execution_time" in aggregates
        assert "avg_success_rate" in aggregates
        assert "avg_llm_score" in aggregates
        assert aggregates["total_evaluations"] == 2

    def test_batch_report_to_json(self):
        """Test batch report can be serialized to JSON."""
        from agenteval.report import BatchReport, EvaluationReport

        reports = [
            EvaluationReport(
                traditional_metrics={"execution_time": 1.5, "success_rate": 0.8},
                llm_evaluation={"overall_score": 7.5, "reasoning": "Good"},
                graph_analysis={"density": 0.6},
                metadata={"seed": 42, "timestamp": "2024-01-01T00:00:00"}
            )
        ]

        batch_report = BatchReport(reports=reports)
        json_output = batch_report.to_json()

        parsed = json.loads(json_output)
        assert "reports" in parsed
        assert "aggregate_metrics" in parsed


class TestReportFormatting:
    """Test report formatting and display options."""

    def test_report_summary(self):
        """Test report can generate summary text."""
        from agenteval.report import EvaluationReport

        report = EvaluationReport(
            traditional_metrics={"execution_time": 1.5, "success_rate": 0.8},
            llm_evaluation={"overall_score": 7.5, "reasoning": "Good"},
            graph_analysis={"density": 0.6},
            metadata={"seed": 42, "timestamp": "2024-01-01T00:00:00"}
        )

        summary = report.summary()

        assert isinstance(summary, str)
        assert "success_rate" in summary.lower() or "0.8" in summary
        assert "7.5" in summary or "overall_score" in summary.lower()

    def test_report_pretty_print(self):
        """Test report can be pretty printed."""
        from agenteval.report import EvaluationReport

        report = EvaluationReport(
            traditional_metrics={"execution_time": 1.5, "success_rate": 0.8},
            llm_evaluation={"overall_score": 7.5, "reasoning": "Good"},
            graph_analysis={"density": 0.6},
            metadata={"seed": 42, "timestamp": "2024-01-01T00:00:00"}
        )

        pretty = report.pretty_print()

        assert isinstance(pretty, str)
        assert len(pretty) > 0


class TestReportValidation:
    """Test report data validation."""

    def test_report_validates_metrics_structure(self):
        """Test report validates required fields in metrics."""
        from agenteval.report import EvaluationReport

        # Should raise error if required fields missing
        with pytest.raises((ValueError, TypeError)):
            EvaluationReport(
                traditional_metrics=None,
                llm_evaluation={"overall_score": 7.5},
                graph_analysis={"density": 0.6},
                metadata={"seed": 42}
            )

    def test_report_validates_metadata(self):
        """Test report ensures metadata contains required fields."""
        from agenteval.report import EvaluationReport

        report = EvaluationReport(
            traditional_metrics={"execution_time": 1.5},
            llm_evaluation={"overall_score": 7.5},
            graph_analysis={"density": 0.6},
            metadata={"seed": 42, "timestamp": "2024-01-01T00:00:00"}
        )

        assert "seed" in report.metadata
        assert "timestamp" in report.metadata
