"""Tests for LLM-as-a-Judge evaluation.

Following TDD RED phase - these tests should FAIL until implementation is complete.
"""

import pytest


class TestLLMJudgeModels:
    """Test Pydantic models for LLM judge evaluation."""

    def test_evaluation_criteria_model(self):
        """Test EvaluationCriteria model for configurable criteria."""
        from agenteval.judges.llm_judge import EvaluationCriteria

        criteria = EvaluationCriteria(
            aspects=["clarity", "correctness", "helpfulness"],
            description="Evaluate the quality of scientific paper reviews",
        )

        assert len(criteria.aspects) == 3
        assert "clarity" in criteria.aspects
        assert criteria.description == "Evaluate the quality of scientific paper reviews"

    def test_evaluation_result_model(self):
        """Test EvaluationResult model with scores and reasoning."""
        from agenteval.judges.llm_judge import EvaluationResult

        result = EvaluationResult(
            overall_score=8.5,
            aspect_scores={"clarity": 9.0, "correctness": 8.0},
            reasoning="The review is clear and mostly correct.",
            justification="Provides specific feedback with minor issues.",
        )

        assert result.overall_score == 8.5
        assert result.aspect_scores["clarity"] == 9.0
        assert "clear" in result.reasoning
        assert result.justification is not None

    def test_evaluation_result_validates_score_range(self):
        """Test EvaluationResult validates scores are in valid range."""
        from agenteval.judges.llm_judge import EvaluationResult
        from pydantic import ValidationError

        # Score should be between 0 and 10
        with pytest.raises(ValidationError):
            EvaluationResult(
                overall_score=15.0,  # Invalid: > 10
                aspect_scores={},
                reasoning="Test",
                justification="Test",
            )


class TestLLMJudge:
    """Test LLMJudge functionality."""

    def test_llm_judge_initialization(self):
        """Test LLMJudge can be initialized."""
        from agenteval.judges.llm_judge import LLMJudge

        judge = LLMJudge()
        assert judge is not None

    def test_llm_judge_initialization_with_custom_model(self):
        """Test LLMJudge can be initialized with custom model."""
        from agenteval.judges.llm_judge import LLMJudge

        judge = LLMJudge(model="gpt-4")
        assert judge is not None

    def test_llm_judge_evaluates_semantic_quality(self):
        """Test LLMJudge evaluates semantic quality of agent-generated reviews."""
        from agenteval.judges.llm_judge import LLMJudge, EvaluationCriteria

        judge = LLMJudge()
        criteria = EvaluationCriteria(
            aspects=["clarity", "correctness"],
            description="Evaluate review quality",
        )

        agent_review = "This paper presents a novel approach to machine learning."
        result = judge.evaluate(
            text=agent_review,
            criteria=criteria,
        )

        assert result.overall_score >= 0.0
        assert result.overall_score <= 10.0
        assert result.reasoning is not None
        assert len(result.reasoning) > 0

    def test_llm_judge_compares_against_baseline(self):
        """Test LLMJudge compares agent output against human baseline."""
        from agenteval.judges.llm_judge import LLMJudge, EvaluationCriteria

        judge = LLMJudge()
        criteria = EvaluationCriteria(
            aspects=["similarity", "quality"],
            description="Compare against baseline",
        )

        agent_review = "The paper is well-written and presents novel ideas."
        baseline_review = "This is a well-structured paper with innovative concepts."

        result = judge.compare(
            text=agent_review,
            baseline=baseline_review,
            criteria=criteria,
        )

        assert result.overall_score >= 0.0
        assert result.overall_score <= 10.0
        assert result.reasoning is not None
        assert "baseline" in result.reasoning.lower() or "comparison" in result.reasoning.lower()

    def test_llm_judge_provides_justification(self):
        """Test LLMJudge provides detailed justification for scores."""
        from agenteval.judges.llm_judge import LLMJudge, EvaluationCriteria

        judge = LLMJudge()
        criteria = EvaluationCriteria(
            aspects=["clarity"],
            description="Evaluate clarity",
        )

        result = judge.evaluate(
            text="The methodology is unclear and poorly described.",
            criteria=criteria,
        )

        assert result.justification is not None
        assert len(result.justification) > 0

    def test_llm_judge_supports_configurable_criteria(self):
        """Test LLMJudge supports different evaluation criteria."""
        from agenteval.judges.llm_judge import LLMJudge, EvaluationCriteria

        judge = LLMJudge()

        # Test with different criteria
        criteria1 = EvaluationCriteria(
            aspects=["technical_accuracy"],
            description="Evaluate technical accuracy",
        )

        criteria2 = EvaluationCriteria(
            aspects=["readability", "structure"],
            description="Evaluate presentation quality",
        )

        result1 = judge.evaluate(text="Technical content here", criteria=criteria1)
        result2 = judge.evaluate(text="Well-structured text", criteria=criteria2)

        # Both should return valid results
        assert result1.overall_score >= 0.0
        assert result2.overall_score >= 0.0


class TestLLMJudgeErrorHandling:
    """Test LLMJudge handles errors gracefully."""

    def test_llm_judge_handles_api_errors(self):
        """Test LLMJudge handles API errors gracefully."""
        from agenteval.judges.llm_judge import LLMJudge, EvaluationCriteria

        # Use invalid API key to trigger error
        judge = LLMJudge(api_key="invalid_key_for_testing")
        criteria = EvaluationCriteria(
            aspects=["clarity"],
            description="Test",
        )

        # Should either raise specific exception or return error result
        try:
            result = judge.evaluate(text="Test text", criteria=criteria)
            # If it doesn't raise, should have error indicator
            assert hasattr(result, "error") or result.overall_score == 0.0
        except Exception as e:
            # Should raise a specific, helpful exception
            assert "API" in str(e) or "key" in str(e).lower()

    def test_llm_judge_handles_rate_limits(self):
        """Test LLMJudge handles rate limit errors gracefully."""
        from agenteval.judges.llm_judge import LLMJudge

        judge = LLMJudge()

        # Should have rate limiting configuration or handling
        assert hasattr(judge, "max_retries") or hasattr(judge, "retry_delay")

    def test_llm_judge_handles_empty_text(self):
        """Test LLMJudge handles empty text input."""
        from agenteval.judges.llm_judge import LLMJudge, EvaluationCriteria

        judge = LLMJudge()
        criteria = EvaluationCriteria(
            aspects=["clarity"],
            description="Test",
        )

        # Should handle empty text gracefully
        result = judge.evaluate(text="", criteria=criteria)
        assert result is not None
        assert result.overall_score >= 0.0


class TestLLMJudgePydanticAI:
    """Test LLMJudge uses PydanticAI for structured outputs."""

    def test_llm_judge_uses_pydantic_ai_agent(self):
        """Test LLMJudge uses PydanticAI Agent for LLM calls."""
        from agenteval.judges.llm_judge import LLMJudge

        judge = LLMJudge()

        # Should use PydanticAI Agent internally
        assert hasattr(judge, "_agent") or hasattr(judge, "agent")

    def test_llm_judge_returns_structured_output(self):
        """Test LLMJudge returns structured Pydantic output."""
        from agenteval.judges.llm_judge import LLMJudge, EvaluationCriteria, EvaluationResult

        judge = LLMJudge()
        criteria = EvaluationCriteria(
            aspects=["clarity"],
            description="Test",
        )

        result = judge.evaluate(text="Test review text", criteria=criteria)

        # Result should be a Pydantic model
        assert isinstance(result, EvaluationResult)
        assert hasattr(result, "model_dump")
        assert hasattr(result, "model_dump_json")


class TestLLMJudgeBatchEvaluation:
    """Test batch evaluation capabilities."""

    def test_llm_judge_batch_evaluate(self):
        """Test LLMJudge can evaluate multiple texts in batch."""
        from agenteval.judges.llm_judge import LLMJudge, EvaluationCriteria

        judge = LLMJudge()
        criteria = EvaluationCriteria(
            aspects=["quality"],
            description="Evaluate quality",
        )

        texts = [
            "First review text",
            "Second review text",
            "Third review text",
        ]

        results = judge.batch_evaluate(texts=texts, criteria=criteria)

        assert len(results) == 3
        assert all(hasattr(r, "overall_score") for r in results)

    def test_llm_judge_batch_compare(self):
        """Test LLMJudge can compare multiple texts against baselines in batch."""
        from agenteval.judges.llm_judge import LLMJudge, EvaluationCriteria

        judge = LLMJudge()
        criteria = EvaluationCriteria(
            aspects=["similarity"],
            description="Compare quality",
        )

        texts = ["Review 1", "Review 2"]
        baselines = ["Baseline 1", "Baseline 2"]

        results = judge.batch_compare(texts=texts, baselines=baselines, criteria=criteria)

        assert len(results) == 2
        assert all(hasattr(r, "overall_score") for r in results)
