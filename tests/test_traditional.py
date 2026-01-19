"""Tests for traditional performance metrics.

Following TDD RED phase - these tests should FAIL until implementation is complete.
"""

import json

import pytest


class TestPerformanceMetrics:
    """Test execution time and success rate metrics."""

    def test_execution_time_metric_basic(self):
        """Test basic execution time metric calculation."""
        from agenteval.metrics.traditional import ExecutionTimeMetric

        metric = ExecutionTimeMetric()
        result = metric.calculate(start_time=0.0, end_time=1.5)

        assert result["execution_time_seconds"] == 1.5
        assert "metric_name" in result
        assert result["metric_name"] == "execution_time"

    def test_success_rate_metric_basic(self):
        """Test basic success rate calculation."""
        from agenteval.metrics.traditional import SuccessRateMetric

        metric = SuccessRateMetric()
        result = metric.calculate(total_tasks=10, successful_tasks=8)

        assert result["success_rate"] == 0.8
        assert result["total_tasks"] == 10
        assert result["successful_tasks"] == 8
        assert result["failed_tasks"] == 2

    def test_success_rate_handles_zero_tasks(self):
        """Test success rate handles edge case of zero tasks."""
        from agenteval.metrics.traditional import SuccessRateMetric

        metric = SuccessRateMetric()
        result = metric.calculate(total_tasks=0, successful_tasks=0)

        assert result["success_rate"] == 0.0

    def test_success_rate_handles_all_failures(self):
        """Test success rate with all failures."""
        from agenteval.metrics.traditional import SuccessRateMetric

        metric = SuccessRateMetric()
        result = metric.calculate(total_tasks=5, successful_tasks=0)

        assert result["success_rate"] == 0.0
        assert result["failed_tasks"] == 5


class TestCoordinationMetrics:
    """Test coordination quality assessment between agents."""

    def test_coordination_metric_text_similarity(self):
        """Test coordination metric using text similarity."""
        from agenteval.metrics.traditional import CoordinationMetric

        metric = CoordinationMetric()
        result = metric.calculate_text_similarity(
            text1="The paper presents a novel approach",
            text2="The paper presents a new approach",
        )

        # Should use Levenshtein or Jaro-Winkler from rapidfuzz
        assert "similarity_score" in result
        assert 0.0 <= result["similarity_score"] <= 1.0
        assert result["similarity_score"] > 0.8  # Very similar texts

    def test_coordination_metric_vector_similarity(self):
        """Test coordination metric using vector cosine similarity."""
        from agenteval.metrics.traditional import CoordinationMetric

        metric = CoordinationMetric()

        # Simple numeric vectors representing agent outputs
        vector1 = [1.0, 2.0, 3.0, 4.0, 5.0]
        vector2 = [1.1, 2.1, 2.9, 4.2, 4.8]

        result = metric.calculate_vector_similarity(vector1=vector1, vector2=vector2)

        # Should use cosine similarity from scikit-learn
        assert "cosine_similarity" in result
        assert 0.0 <= result["cosine_similarity"] <= 1.0
        assert result["cosine_similarity"] > 0.95  # Very similar vectors

    def test_coordination_metric_agreement_score(self):
        """Test coordination agreement across multiple agents."""
        from agenteval.metrics.traditional import CoordinationMetric

        metric = CoordinationMetric()

        # Agent outputs as list of text responses
        agent_outputs = [
            "accept",
            "accept",
            "accept",
            "reject",
        ]

        result = metric.calculate_agreement(outputs=agent_outputs)

        assert "agreement_score" in result
        assert result["agreement_score"] == 0.75  # 3 out of 4 agree
        assert "majority_output" in result
        assert result["majority_output"] == "accept"


class TestMetricOutput:
    """Test structured JSON output format for metrics."""

    def test_metrics_output_as_json(self):
        """Test metrics can be serialized to JSON format."""
        from agenteval.metrics.traditional import MetricsReport

        report = MetricsReport(
            execution_time=1.5,
            success_rate=0.8,
            coordination_score=0.85,
            metadata={"agent_count": 3, "task_type": "review"},
        )

        json_output = report.to_json()

        # Should be valid JSON
        parsed = json.loads(json_output)
        assert parsed["execution_time"] == 1.5
        assert parsed["success_rate"] == 0.8
        assert parsed["coordination_score"] == 0.85
        assert parsed["metadata"]["agent_count"] == 3

    def test_metrics_report_pydantic_model(self):
        """Test MetricsReport is a Pydantic model with validation."""
        from agenteval.metrics.traditional import MetricsReport

        report = MetricsReport(
            execution_time=2.5,
            success_rate=0.9,
            coordination_score=0.75,
            metadata={},
        )

        assert report.execution_time == 2.5
        assert report.success_rate == 0.9
        assert report.coordination_score == 0.75

    def test_metrics_report_validation(self):
        """Test MetricsReport validates numeric ranges."""
        from agenteval.metrics.traditional import MetricsReport
        from pydantic import ValidationError

        # Success rate must be between 0 and 1
        with pytest.raises(ValidationError):
            MetricsReport(
                execution_time=1.0,
                success_rate=1.5,  # Invalid: > 1.0
                coordination_score=0.5,
                metadata={},
            )


class TestBatchEvaluation:
    """Test batch evaluation of multiple agent outputs."""

    def test_batch_evaluator_processes_multiple_outputs(self):
        """Test batch evaluator processes multiple agent outputs."""
        from agenteval.metrics.traditional import BatchEvaluator

        evaluator = BatchEvaluator()

        # Simulated agent outputs with execution data
        outputs = [
            {"task_id": "task1", "success": True, "execution_time": 1.2},
            {"task_id": "task2", "success": True, "execution_time": 1.5},
            {"task_id": "task3", "success": False, "execution_time": 0.8},
        ]

        results = evaluator.evaluate_batch(outputs)

        assert "aggregate_metrics" in results
        assert results["aggregate_metrics"]["total_tasks"] == 3
        assert results["aggregate_metrics"]["successful_tasks"] == 2
        assert results["aggregate_metrics"]["success_rate"] == pytest.approx(0.667, rel=0.01)

    def test_batch_evaluator_calculates_average_execution_time(self):
        """Test batch evaluator calculates average execution time."""
        from agenteval.metrics.traditional import BatchEvaluator

        evaluator = BatchEvaluator()

        outputs = [
            {"task_id": "task1", "success": True, "execution_time": 1.0},
            {"task_id": "task2", "success": True, "execution_time": 2.0},
            {"task_id": "task3", "success": True, "execution_time": 3.0},
        ]

        results = evaluator.evaluate_batch(outputs)

        assert results["aggregate_metrics"]["avg_execution_time"] == 2.0

    def test_batch_evaluator_returns_per_task_metrics(self):
        """Test batch evaluator includes per-task metrics."""
        from agenteval.metrics.traditional import BatchEvaluator

        evaluator = BatchEvaluator()

        outputs = [
            {"task_id": "task1", "success": True, "execution_time": 1.0},
            {"task_id": "task2", "success": False, "execution_time": 0.5},
        ]

        results = evaluator.evaluate_batch(outputs)

        assert "per_task_metrics" in results
        assert len(results["per_task_metrics"]) == 2
        assert results["per_task_metrics"][0]["task_id"] == "task1"
        assert results["per_task_metrics"][0]["success"] is True


class TestMLMetrics:
    """Test ML metrics using scikit-learn."""

    def test_f1_score_calculation(self):
        """Test F1 score calculation for classification tasks."""
        from agenteval.metrics.traditional import MLMetrics

        metrics = MLMetrics()

        # Binary classification: true labels vs predicted labels
        y_true = [1, 1, 0, 1, 0, 0, 1, 1]
        y_pred = [1, 0, 0, 1, 0, 1, 1, 1]

        result = metrics.calculate_f1_score(y_true=y_true, y_pred=y_pred)

        assert "f1_score" in result
        assert 0.0 <= result["f1_score"] <= 1.0

    def test_precision_recall_calculation(self):
        """Test precision and recall calculation."""
        from agenteval.metrics.traditional import MLMetrics

        metrics = MLMetrics()

        y_true = [1, 1, 0, 1, 0]
        y_pred = [1, 1, 0, 0, 0]

        result = metrics.calculate_precision_recall(y_true=y_true, y_pred=y_pred)

        assert "precision" in result
        assert "recall" in result
        assert 0.0 <= result["precision"] <= 1.0
        assert 0.0 <= result["recall"] <= 1.0
