"""Tests for LLM Judge Evaluator.

Following TDD RED phase - these tests should FAIL until implementation is complete.
Tests validate semantic quality evaluation of agent-generated reviews against human baselines.
"""

import pytest
from pydantic_ai.models.test import TestModel

from agenteval.judges.llm_judge import (
    AgentReview,
    EvaluationCriteria,
    LLMJudgeEvaluator,
)
from agenteval.models.data import Review
from agenteval.models.evaluation import Evaluation


class TestAgentReview:
    """Test AgentReview Pydantic model."""

    def test_agent_review_model(self):
        """Test AgentReview model has required fields."""
        agent_review = AgentReview(
            review_id="agent_review_001",
            paper_id="paper_001",
            rating=8,
            confidence=4,
            review_text="This paper presents a novel approach to multi-agent coordination.",
        )
        assert agent_review.review_id == "agent_review_001"
        assert agent_review.paper_id == "paper_001"
        assert agent_review.rating == 8
        assert agent_review.confidence == 4
        assert "novel approach" in agent_review.review_text


class TestEvaluationCriteria:
    """Test EvaluationCriteria Pydantic model."""

    def test_evaluation_criteria_defaults(self):
        """Test EvaluationCriteria has sensible defaults."""
        criteria = EvaluationCriteria()
        assert criteria.coherence_weight >= 0.0
        assert criteria.relevance_weight >= 0.0
        assert criteria.completeness_weight >= 0.0
        assert criteria.technical_accuracy_weight >= 0.0

    def test_evaluation_criteria_custom_weights(self):
        """Test EvaluationCriteria accepts custom weights."""
        criteria = EvaluationCriteria(
            coherence_weight=0.3,
            relevance_weight=0.3,
            completeness_weight=0.2,
            technical_accuracy_weight=0.2,
        )
        assert criteria.coherence_weight == 0.3
        assert criteria.relevance_weight == 0.3
        assert criteria.completeness_weight == 0.2
        assert criteria.technical_accuracy_weight == 0.2


class TestLLMJudgeEvaluator:
    """Test LLM Judge Evaluator functionality."""

    def test_evaluator_initialization_default_criteria(self):
        """Test LLMJudgeEvaluator can be initialized with default criteria."""
        test_model = TestModel()
        evaluator = LLMJudgeEvaluator(model=test_model)
        assert isinstance(evaluator, LLMJudgeEvaluator)

    def test_evaluator_initialization_custom_criteria(self):
        """Test LLMJudgeEvaluator can be initialized with custom criteria."""
        criteria = EvaluationCriteria(
            coherence_weight=0.4,
            relevance_weight=0.3,
            completeness_weight=0.2,
            technical_accuracy_weight=0.1,
        )
        test_model = TestModel()
        evaluator = LLMJudgeEvaluator(criteria=criteria, model=test_model)
        assert isinstance(evaluator, LLMJudgeEvaluator)
        assert evaluator.criteria == criteria

    @pytest.mark.anyio
    async def test_evaluate_single_review(self):
        """Test evaluating a single agent review against baseline."""
        test_model = TestModel(
            custom_output_args={
                "semantic_score": 0.85,
                "justification": "Reviews are semantically similar",
            }
        )
        evaluator = LLMJudgeEvaluator(model=test_model)

        agent_review = AgentReview(
            review_id="agent_review_001",
            paper_id="paper_001",
            rating=8,
            confidence=4,
            review_text="This paper presents a novel approach to reinforcement learning.",
        )

        baseline_review = Review(
            id="baseline_review_001",
            paper_id="paper_001",
            rating=8,
            confidence=4,
            review_text="The paper introduces an innovative method for reinforcement learning.",
        )

        evaluation = await evaluator.evaluate(agent_review, baseline_review)

        assert isinstance(evaluation, Evaluation)
        assert evaluation.review_id == "agent_review_001"
        assert evaluation.baseline_review_id == "baseline_review_001"
        assert 0.0 <= evaluation.semantic_score <= 1.0
        assert len(evaluation.justification) > 0

    @pytest.mark.anyio
    async def test_evaluate_high_quality_match(self):
        """Test evaluation of high-quality agent review matching baseline."""
        test_model = TestModel(
            custom_output_args={
                "semantic_score": 0.92,
                "justification": "Highly similar semantic content",
            }
        )
        evaluator = LLMJudgeEvaluator(model=test_model)

        agent_review = AgentReview(
            review_id="agent_review_002",
            paper_id="paper_002",
            rating=9,
            confidence=5,
            review_text="Excellent work with rigorous methodology and clear presentation.",
        )

        baseline_review = Review(
            id="baseline_review_002",
            paper_id="paper_002",
            rating=9,
            confidence=5,
            review_text="Outstanding research with strong methodology and clear writing.",
        )

        evaluation = await evaluator.evaluate(agent_review, baseline_review)

        # High semantic similarity expected
        assert evaluation.semantic_score >= 0.7
        assert (
            "similar" in evaluation.justification.lower()
            or "match" in evaluation.justification.lower()
        )

    @pytest.mark.anyio
    async def test_evaluate_low_quality_mismatch(self):
        """Test evaluation of poor agent review not matching baseline."""
        test_model = TestModel(
            custom_output_args={
                "semantic_score": 0.35,
                "justification": "Significant semantic differences",
            }
        )
        evaluator = LLMJudgeEvaluator(model=test_model)

        agent_review = AgentReview(
            review_id="agent_review_003",
            paper_id="paper_003",
            rating=3,
            confidence=2,
            review_text="The paper is okay.",
        )

        baseline_review = Review(
            id="baseline_review_003",
            paper_id="paper_003",
            rating=8,
            confidence=5,
            review_text=(
                "This work demonstrates significant innovation with "
                "comprehensive experimental validation."
            ),
        )

        evaluation = await evaluator.evaluate(agent_review, baseline_review)

        # Low semantic similarity expected due to mismatch
        assert evaluation.semantic_score < 0.7
        assert len(evaluation.justification) > 0

    @pytest.mark.anyio
    async def test_evaluate_provides_justification(self):
        """Test that evaluation includes detailed justification."""
        test_model = TestModel(
            custom_output_args={
                "semantic_score": 0.78,
                "justification": (
                    "Both reviews highlight similar concerns about the experimental methodology"
                ),
            }
        )
        evaluator = LLMJudgeEvaluator(model=test_model)

        agent_review = AgentReview(
            review_id="agent_review_004",
            paper_id="paper_004",
            rating=7,
            confidence=4,
            review_text="Good analysis but missing details on experimental setup.",
        )

        baseline_review = Review(
            id="baseline_review_004",
            paper_id="paper_004",
            rating=7,
            confidence=4,
            review_text="Strong analysis though experimental section needs improvement.",
        )

        evaluation = await evaluator.evaluate(agent_review, baseline_review)

        # Justification should be substantive
        assert len(evaluation.justification) > 20
        assert isinstance(evaluation.justification, str)

    @pytest.mark.anyio
    async def test_batch_evaluate_multiple_reviews(self):
        """Test batch evaluation of multiple agent reviews."""
        test_model = TestModel(
            custom_output_args={
                "semantic_score": 0.75,
                "justification": "Batch evaluation result",
            }
        )
        evaluator = LLMJudgeEvaluator(model=test_model)

        agent_reviews = [
            AgentReview(
                review_id=f"agent_review_{i:03d}",
                paper_id=f"paper_{i:03d}",
                rating=7 + i,
                confidence=4,
                review_text=f"Review content for paper {i}.",
            )
            for i in range(3)
        ]

        baseline_reviews = [
            Review(
                id=f"baseline_review_{i:03d}",
                paper_id=f"paper_{i:03d}",
                rating=7 + i,
                confidence=4,
                review_text=f"Baseline review for paper {i}.",
            )
            for i in range(3)
        ]

        evaluations = await evaluator.batch_evaluate(agent_reviews, baseline_reviews)

        assert len(evaluations) == 3
        for evaluation in evaluations:
            assert isinstance(evaluation, Evaluation)
            assert 0.0 <= evaluation.semantic_score <= 1.0
            assert len(evaluation.justification) > 0

    @pytest.mark.anyio
    async def test_evaluate_respects_custom_criteria(self):
        """Test that evaluation respects custom criteria weights."""
        criteria = EvaluationCriteria(
            coherence_weight=0.5,
            relevance_weight=0.3,
            completeness_weight=0.1,
            technical_accuracy_weight=0.1,
        )
        test_model = TestModel(
            custom_output_args={
                "semantic_score": 0.65,
                "justification": "Evaluated with custom criteria",
            }
        )
        evaluator = LLMJudgeEvaluator(criteria=criteria, model=test_model)

        agent_review = AgentReview(
            review_id="agent_review_005",
            paper_id="paper_005",
            rating=6,
            confidence=3,
            review_text="Decent paper with some issues.",
        )

        baseline_review = Review(
            id="baseline_review_005",
            paper_id="paper_005",
            rating=6,
            confidence=3,
            review_text="Acceptable work with minor problems.",
        )

        evaluation = await evaluator.evaluate(agent_review, baseline_review)

        # Should complete successfully with custom criteria
        assert isinstance(evaluation, Evaluation)
        assert 0.0 <= evaluation.semantic_score <= 1.0

    @pytest.mark.anyio
    async def test_batch_evaluate_mismatched_lengths_raises_error(self):
        """Test batch evaluation raises error for mismatched input lengths."""
        test_model = TestModel()
        evaluator = LLMJudgeEvaluator(model=test_model)

        agent_reviews = [
            AgentReview(
                review_id="agent_review_001",
                paper_id="paper_001",
                rating=7,
                confidence=4,
                review_text="Review 1",
            )
        ]

        baseline_reviews = [
            Review(
                id="baseline_review_001",
                paper_id="paper_001",
                rating=7,
                confidence=4,
                review_text="Baseline 1",
            ),
            Review(
                id="baseline_review_002",
                paper_id="paper_002",
                rating=8,
                confidence=4,
                review_text="Baseline 2",
            ),
        ]

        with pytest.raises(ValueError):
            await evaluator.batch_evaluate(agent_reviews, baseline_reviews)

    @pytest.mark.anyio
    async def test_evaluate_with_empty_review_text(self):
        """Test evaluation handles edge case of empty review text."""
        test_model = TestModel(
            custom_output_args={
                "semantic_score": 0.15,
                "justification": "Empty review provides no semantic content",
            }
        )
        evaluator = LLMJudgeEvaluator(model=test_model)

        agent_review = AgentReview(
            review_id="agent_review_006",
            paper_id="paper_006",
            rating=5,
            confidence=3,
            review_text="",
        )

        baseline_review = Review(
            id="baseline_review_006",
            paper_id="paper_006",
            rating=7,
            confidence=4,
            review_text="This is a comprehensive baseline review.",
        )

        # Should handle gracefully, likely with low score
        evaluation = await evaluator.evaluate(agent_review, baseline_review)
        assert isinstance(evaluation, Evaluation)
        assert 0.0 <= evaluation.semantic_score <= 1.0

    @pytest.mark.anyio
    async def test_batch_evaluate_empty_list(self):
        """Test batch evaluation with empty lists."""
        test_model = TestModel()
        evaluator = LLMJudgeEvaluator(model=test_model)

        evaluations = await evaluator.batch_evaluate([], [])

        assert evaluations == []
