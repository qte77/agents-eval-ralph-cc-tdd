"""Tests for LLM-as-a-Judge evaluation implementation.

Following TDD RED phase - these tests should FAIL until implementation is complete.
"""

import json

import pytest


class TestLLMJudgeModels:
    """Test Pydantic models for LLM judge evaluation."""

    def test_review_evaluation_model(self):
        """Test ReviewEvaluation model with score and reasoning."""
        from agenteval.judges.llm_judge import ReviewEvaluation

        evaluation = ReviewEvaluation(
            score=8.5,
            reasoning="The review demonstrates strong technical understanding...",
            criteria_scores={
                "technical_accuracy": 9.0,
                "clarity": 8.0,
                "constructiveness": 8.5,
            },
        )

        assert evaluation.score == 8.5
        assert "technical understanding" in evaluation.reasoning
        assert evaluation.criteria_scores["technical_accuracy"] == 9.0

    def test_agent_review_input_model(self):
        """Test AgentReview input model for review content."""
        from agenteval.judges.llm_judge import AgentReview

        review = AgentReview(
            review_id="review_001",
            paper_id="paper_001",
            content="This paper presents a novel approach...",
            agent_id="agent_reviewer_1",
        )

        assert review.review_id == "review_001"
        assert review.paper_id == "paper_001"
        assert review.agent_id == "agent_reviewer_1"

    def test_human_baseline_model(self):
        """Test HumanBaseline model for reference reviews."""
        from agenteval.judges.llm_judge import HumanBaseline

        baseline = HumanBaseline(
            review_id="human_review_001",
            paper_id="paper_001",
            content="This is a human-written review...",
            score=8.0,
        )

        assert baseline.review_id == "human_review_001"
        assert baseline.content == "This is a human-written review..."
        assert baseline.score == 8.0

    def test_evaluation_criteria_model(self):
        """Test EvaluationCriteria model for configurable criteria."""
        from agenteval.judges.llm_judge import EvaluationCriteria

        criteria = EvaluationCriteria(
            technical_accuracy=True,
            clarity=True,
            constructiveness=True,
            completeness=False,
        )

        assert criteria.technical_accuracy is True
        assert criteria.clarity is True
        assert criteria.completeness is False


class TestLLMJudgeAgent:
    """Test PydanticAI judge agent initialization and configuration."""

    def test_judge_agent_initialization(self):
        """Test LLMJudgeAgent can be initialized."""
        from agenteval.judges.llm_judge import LLMJudgeAgent

        judge = LLMJudgeAgent()
        assert judge is not None

    def test_judge_agent_with_custom_model(self):
        """Test LLMJudgeAgent accepts custom model configuration."""
        from agenteval.judges.llm_judge import LLMJudgeAgent

        judge = LLMJudgeAgent(model="openai:gpt-4")
        assert judge is not None

    def test_judge_agent_with_criteria(self):
        """Test LLMJudgeAgent accepts custom evaluation criteria."""
        from agenteval.judges.llm_judge import EvaluationCriteria, LLMJudgeAgent

        criteria = EvaluationCriteria(
            technical_accuracy=True,
            clarity=True,
            constructiveness=True,
            completeness=True,
        )

        judge = LLMJudgeAgent(criteria=criteria)
        assert judge is not None


class TestSemanticQualityEvaluation:
    """Test semantic quality assessment of agent-generated reviews."""

    @pytest.mark.anyio
    async def test_evaluate_single_review(self):
        """Test evaluating a single agent-generated review."""
        from agenteval.judges.llm_judge import AgentReview, LLMJudgeAgent

        judge = LLMJudgeAgent()

        review = AgentReview(
            review_id="review_001",
            paper_id="paper_001",
            content="This paper presents a novel neural architecture with strong experimental results.",
            agent_id="agent_1",
        )

        evaluation = await judge.evaluate_review(review)

        assert evaluation.score >= 0.0
        assert evaluation.score <= 10.0
        assert len(evaluation.reasoning) > 0
        assert isinstance(evaluation.criteria_scores, dict)

    @pytest.mark.anyio
    async def test_evaluate_with_baseline_comparison(self):
        """Test evaluating agent review against human baseline."""
        from agenteval.judges.llm_judge import (
            AgentReview,
            HumanBaseline,
            LLMJudgeAgent,
        )

        judge = LLMJudgeAgent()

        agent_review = AgentReview(
            review_id="review_001",
            paper_id="paper_001",
            content="This paper presents a novel approach with good experimental validation.",
            agent_id="agent_1",
        )

        baseline = HumanBaseline(
            review_id="human_001",
            paper_id="paper_001",
            content="The paper introduces an innovative method supported by comprehensive experiments.",
            score=8.5,
        )

        evaluation = await judge.evaluate_with_baseline(agent_review, baseline)

        assert evaluation.score >= 0.0
        assert evaluation.score <= 10.0
        assert "baseline" in evaluation.reasoning.lower() or "comparison" in evaluation.reasoning.lower()

    @pytest.mark.anyio
    async def test_evaluate_low_quality_review(self):
        """Test that low-quality reviews receive lower scores."""
        from agenteval.judges.llm_judge import AgentReview, LLMJudgeAgent

        judge = LLMJudgeAgent()

        poor_review = AgentReview(
            review_id="review_002",
            paper_id="paper_002",
            content="This paper is bad.",
            agent_id="agent_2",
        )

        evaluation = await judge.evaluate_review(poor_review)

        assert evaluation.score < 5.0  # Expect low score for poor review
        assert len(evaluation.reasoning) > 0


class TestConfigurableCriteria:
    """Test support for configurable evaluation criteria."""

    @pytest.mark.anyio
    async def test_evaluate_with_custom_criteria(self):
        """Test evaluation with custom criteria configuration."""
        from agenteval.judges.llm_judge import (
            AgentReview,
            EvaluationCriteria,
            LLMJudgeAgent,
        )

        criteria = EvaluationCriteria(
            technical_accuracy=True,
            clarity=True,
            constructiveness=False,
            completeness=False,
        )

        judge = LLMJudgeAgent(criteria=criteria)

        review = AgentReview(
            review_id="review_003",
            paper_id="paper_003",
            content="The methodology is technically sound and clearly explained.",
            agent_id="agent_3",
        )

        evaluation = await judge.evaluate_review(review)

        # Should only evaluate enabled criteria
        assert "technical_accuracy" in evaluation.criteria_scores
        assert "clarity" in evaluation.criteria_scores
        # Disabled criteria should not be included
        assert "constructiveness" not in evaluation.criteria_scores or evaluation.criteria_scores.get("constructiveness") is None

    @pytest.mark.anyio
    async def test_criteria_affects_scoring(self):
        """Test that different criteria configurations affect evaluation."""
        from agenteval.judges.llm_judge import (
            AgentReview,
            EvaluationCriteria,
            LLMJudgeAgent,
        )

        review = AgentReview(
            review_id="review_004",
            paper_id="paper_004",
            content="Technical analysis with clear explanations.",
            agent_id="agent_4",
        )

        # Evaluate with minimal criteria
        minimal_criteria = EvaluationCriteria(
            technical_accuracy=True,
            clarity=False,
            constructiveness=False,
            completeness=False,
        )
        judge_minimal = LLMJudgeAgent(criteria=minimal_criteria)
        eval_minimal = await judge_minimal.evaluate_review(review)

        # Evaluate with all criteria
        full_criteria = EvaluationCriteria(
            technical_accuracy=True,
            clarity=True,
            constructiveness=True,
            completeness=True,
        )
        judge_full = LLMJudgeAgent(criteria=full_criteria)
        eval_full = await judge_full.evaluate_review(review)

        # Both should produce valid evaluations
        assert eval_minimal.score >= 0.0
        assert eval_full.score >= 0.0
        assert len(eval_minimal.criteria_scores) < len(eval_full.criteria_scores)


class TestStructuredOutput:
    """Test structured evaluation output with scores and reasoning."""

    @pytest.mark.anyio
    async def test_evaluation_to_json(self):
        """Test ReviewEvaluation can be serialized to JSON."""
        from agenteval.judges.llm_judge import AgentReview, LLMJudgeAgent

        judge = LLMJudgeAgent()

        review = AgentReview(
            review_id="review_005",
            paper_id="paper_005",
            content="Solid technical contribution with clear presentation.",
            agent_id="agent_5",
        )

        evaluation = await judge.evaluate_review(review)
        json_str = evaluation.model_dump_json()
        data = json.loads(json_str)

        assert "score" in data
        assert "reasoning" in data
        assert "criteria_scores" in data
        assert isinstance(data["score"], (int, float))
        assert isinstance(data["reasoning"], str)
        assert isinstance(data["criteria_scores"], dict)

    @pytest.mark.anyio
    async def test_evaluation_to_dict(self):
        """Test ReviewEvaluation can be converted to dict."""
        from agenteval.judges.llm_judge import AgentReview, LLMJudgeAgent

        judge = LLMJudgeAgent()

        review = AgentReview(
            review_id="review_006",
            paper_id="paper_006",
            content="Well-structured review with actionable feedback.",
            agent_id="agent_6",
        )

        evaluation = await judge.evaluate_review(review)
        eval_dict = evaluation.model_dump()

        assert isinstance(eval_dict, dict)
        assert "score" in eval_dict
        assert "reasoning" in eval_dict
        assert "criteria_scores" in eval_dict


class TestBatchEvaluation:
    """Test batch evaluation of multiple agent reviews."""

    @pytest.mark.anyio
    async def test_evaluate_multiple_reviews(self):
        """Test evaluating multiple reviews in batch."""
        from agenteval.judges.llm_judge import AgentReview, LLMJudgeAgent

        judge = LLMJudgeAgent()

        reviews = [
            AgentReview(
                review_id=f"review_{i}",
                paper_id=f"paper_{i}",
                content=f"Review content {i} with technical analysis.",
                agent_id=f"agent_{i}",
            )
            for i in range(3)
        ]

        evaluations = await judge.evaluate_batch(reviews)

        assert len(evaluations) == 3
        for evaluation in evaluations:
            assert evaluation.score >= 0.0
            assert evaluation.score <= 10.0
            assert len(evaluation.reasoning) > 0

    @pytest.mark.anyio
    async def test_batch_with_baselines(self):
        """Test batch evaluation with corresponding human baselines."""
        from agenteval.judges.llm_judge import (
            AgentReview,
            HumanBaseline,
            LLMJudgeAgent,
        )

        judge = LLMJudgeAgent()

        agent_reviews = [
            AgentReview(
                review_id=f"review_{i}",
                paper_id=f"paper_{i}",
                content=f"Agent review {i} content.",
                agent_id=f"agent_{i}",
            )
            for i in range(2)
        ]

        baselines = [
            HumanBaseline(
                review_id=f"human_{i}",
                paper_id=f"paper_{i}",
                content=f"Human review {i} content.",
                score=8.0,
            )
            for i in range(2)
        ]

        evaluations = await judge.evaluate_batch_with_baselines(agent_reviews, baselines)

        assert len(evaluations) == 2
        for evaluation in evaluations:
            assert evaluation.score >= 0.0
            assert evaluation.score <= 10.0


class TestJudgeWithPydanticAI:
    """Test PydanticAI integration for LLM judge."""

    @pytest.mark.anyio
    async def test_pydanticai_agent_returns_structured_output(self):
        """Test that PydanticAI agent returns structured ReviewEvaluation."""
        from agenteval.judges.llm_judge import AgentReview, LLMJudgeAgent

        judge = LLMJudgeAgent()

        review = AgentReview(
            review_id="review_007",
            paper_id="paper_007",
            content="Comprehensive analysis with clear methodology review.",
            agent_id="agent_7",
        )

        evaluation = await judge.evaluate_review(review)

        # PydanticAI should enforce structured output
        from agenteval.judges.llm_judge import ReviewEvaluation

        assert isinstance(evaluation, ReviewEvaluation)
        assert hasattr(evaluation, "score")
        assert hasattr(evaluation, "reasoning")
        assert hasattr(evaluation, "criteria_scores")

    @pytest.mark.anyio
    async def test_judge_provides_justification(self):
        """Test that judge provides meaningful justification."""
        from agenteval.judges.llm_judge import AgentReview, LLMJudgeAgent

        judge = LLMJudgeAgent()

        review = AgentReview(
            review_id="review_008",
            paper_id="paper_008",
            content="The experimental design is robust and the results are convincing.",
            agent_id="agent_8",
        )

        evaluation = await judge.evaluate_review(review)

        # Reasoning should be substantive
        assert len(evaluation.reasoning) > 20
        assert any(
            word in evaluation.reasoning.lower()
            for word in ["review", "analysis", "quality", "evaluation"]
        )
