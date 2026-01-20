"""Tests for LLM-as-a-Judge evaluation.

Following TDD approach - these tests should FAIL initially.
Tests validate LLM judge evaluation: semantic quality scoring, justification, and comparison.
"""

import json

import pytest

from agenteval.judges.llm_judge import (
    LLMJudge,
    evaluate_review,
    evaluate_review_batch,
)
from agenteval.models.data import Review
from agenteval.models.evaluation import Evaluation


class TestEvaluateReview:
    """Tests for single review evaluation."""

    def test_evaluate_review_basic(self):
        """Test basic LLM judge evaluation of a review against baseline."""
        agent_review = Review(
            id="agent_review_1",
            paper_id="paper_001",
            rating=8,
            confidence=4,
            review_text="This paper presents a novel approach to machine learning.",
        )
        baseline_review = Review(
            id="baseline_review_1",
            paper_id="paper_001",
            rating=9,
            confidence=5,
            review_text="This work introduces an innovative methodology for ML applications.",
        )

        evaluation = evaluate_review(
            agent_review=agent_review,
            baseline_review=baseline_review,
            criteria=["relevance", "clarity", "depth"],
        )

        assert isinstance(evaluation, Evaluation)
        assert evaluation.review_id == "agent_review_1"
        assert evaluation.baseline_review_id == "baseline_review_1"
        assert 0.0 <= evaluation.semantic_score <= 1.0
        assert len(evaluation.justification) > 0

    def test_evaluate_review_high_quality_match(self):
        """Test evaluation of high-quality review that closely matches baseline."""
        agent_review = Review(
            id="agent_review_2",
            paper_id="paper_002",
            rating=7,
            confidence=4,
            review_text="Excellent methodology with clear experimental design and strong results.",
        )
        baseline_review = Review(
            id="baseline_review_2",
            paper_id="paper_002",
            rating=7,
            confidence=4,
            review_text="Strong methodology, well-designed experiments, compelling results.",
        )

        evaluation = evaluate_review(
            agent_review=agent_review, baseline_review=baseline_review
        )

        # High semantic similarity should yield high score
        assert evaluation.semantic_score >= 0.6
        assert "similar" in evaluation.justification.lower() or "match" in evaluation.justification.lower()

    def test_evaluate_review_low_quality_mismatch(self):
        """Test evaluation of low-quality review that differs from baseline."""
        agent_review = Review(
            id="agent_review_3",
            paper_id="paper_003",
            rating=5,
            confidence=2,
            review_text="The paper is okay.",
        )
        baseline_review = Review(
            id="baseline_review_3",
            paper_id="paper_003",
            rating=8,
            confidence=5,
            review_text="This paper demonstrates exceptional theoretical contributions with rigorous proofs and comprehensive evaluation across multiple benchmarks.",
        )

        evaluation = evaluate_review(
            agent_review=agent_review, baseline_review=baseline_review
        )

        # Low semantic similarity should yield low score
        assert evaluation.semantic_score <= 0.5
        assert len(evaluation.justification) > 20  # Should have detailed justification

    def test_evaluate_review_custom_criteria(self):
        """Test evaluation with custom criteria."""
        agent_review = Review(
            id="agent_review_4",
            paper_id="paper_004",
            rating=6,
            confidence=3,
            review_text="Good work on data analysis.",
        )
        baseline_review = Review(
            id="baseline_review_4",
            paper_id="paper_004",
            rating=7,
            confidence=4,
            review_text="Thorough data analysis with strong statistical support.",
        )

        custom_criteria = ["technical_accuracy", "completeness", "constructiveness"]
        evaluation = evaluate_review(
            agent_review=agent_review,
            baseline_review=baseline_review,
            criteria=custom_criteria,
        )

        assert isinstance(evaluation, Evaluation)
        assert evaluation.semantic_score >= 0.0


class TestLLMJudge:
    """Tests for LLMJudge class."""

    def test_llm_judge_creation_default(self):
        """Test creating LLMJudge with default criteria."""
        judge = LLMJudge()

        assert judge.criteria is not None
        assert len(judge.criteria) > 0
        assert "relevance" in judge.criteria or "clarity" in judge.criteria

    def test_llm_judge_creation_custom_criteria(self):
        """Test creating LLMJudge with custom criteria."""
        custom_criteria = ["accuracy", "depth", "novelty"]
        judge = LLMJudge(criteria=custom_criteria)

        assert judge.criteria == custom_criteria
        assert "accuracy" in judge.criteria
        assert "depth" in judge.criteria
        assert "novelty" in judge.criteria

    def test_llm_judge_evaluate(self):
        """Test that LLMJudge.evaluate() returns valid Evaluation."""
        judge = LLMJudge()

        agent_review = Review(
            id="agent_review_5",
            paper_id="paper_005",
            rating=7,
            confidence=4,
            review_text="Well-written paper with solid contributions.",
        )
        baseline_review = Review(
            id="baseline_review_5",
            paper_id="paper_005",
            rating=8,
            confidence=5,
            review_text="Excellent paper with significant contributions to the field.",
        )

        evaluation = judge.evaluate(
            agent_review=agent_review, baseline_review=baseline_review
        )

        assert isinstance(evaluation, Evaluation)
        assert evaluation.review_id == "agent_review_5"
        assert evaluation.baseline_review_id == "baseline_review_5"
        assert 0.0 <= evaluation.semantic_score <= 1.0
        assert len(evaluation.justification) > 0

    def test_llm_judge_evaluate_preserves_ids(self):
        """Test that evaluation preserves correct review IDs."""
        judge = LLMJudge()

        agent_review = Review(
            id="test_agent_id",
            paper_id="paper_x",
            rating=5,
            confidence=3,
            review_text="Test review content.",
        )
        baseline_review = Review(
            id="test_baseline_id",
            paper_id="paper_x",
            rating=6,
            confidence=4,
            review_text="Test baseline content.",
        )

        evaluation = judge.evaluate(
            agent_review=agent_review, baseline_review=baseline_review
        )

        assert evaluation.review_id == "test_agent_id"
        assert evaluation.baseline_review_id == "test_baseline_id"


class TestEvaluateReviewBatch:
    """Tests for batch evaluation of multiple reviews."""

    def test_evaluate_review_batch_single_pair(self):
        """Test batch evaluation with a single review pair."""
        pairs = [
            {
                "agent_review": Review(
                    id="agent_1",
                    paper_id="paper_1",
                    rating=7,
                    confidence=4,
                    review_text="Good paper.",
                ),
                "baseline_review": Review(
                    id="baseline_1",
                    paper_id="paper_1",
                    rating=8,
                    confidence=5,
                    review_text="Excellent paper.",
                ),
            }
        ]

        results = evaluate_review_batch(pairs)

        assert len(results) == 1
        assert isinstance(results[0], Evaluation)
        assert results[0].review_id == "agent_1"
        assert results[0].baseline_review_id == "baseline_1"

    def test_evaluate_review_batch_multiple_pairs(self):
        """Test batch evaluation with multiple review pairs."""
        pairs = [
            {
                "agent_review": Review(
                    id="agent_1",
                    paper_id="paper_1",
                    rating=7,
                    confidence=4,
                    review_text="Strong methodology.",
                ),
                "baseline_review": Review(
                    id="baseline_1",
                    paper_id="paper_1",
                    rating=8,
                    confidence=5,
                    review_text="Excellent methodology.",
                ),
            },
            {
                "agent_review": Review(
                    id="agent_2",
                    paper_id="paper_2",
                    rating=5,
                    confidence=3,
                    review_text="Needs improvement.",
                ),
                "baseline_review": Review(
                    id="baseline_2",
                    paper_id="paper_2",
                    rating=9,
                    confidence=5,
                    review_text="Outstanding work with significant contributions.",
                ),
            },
        ]

        results = evaluate_review_batch(pairs)

        assert len(results) == 2
        assert all(isinstance(r, Evaluation) for r in results)
        assert results[0].review_id == "agent_1"
        assert results[1].review_id == "agent_2"

    def test_evaluate_review_batch_empty_raises(self):
        """Test that empty batch raises error."""
        with pytest.raises(ValueError, match="Batch cannot be empty"):
            evaluate_review_batch([])

    def test_evaluate_review_batch_with_criteria(self):
        """Test batch evaluation with custom criteria."""
        pairs = [
            {
                "agent_review": Review(
                    id="agent_x",
                    paper_id="paper_x",
                    rating=6,
                    confidence=3,
                    review_text="Decent work.",
                ),
                "baseline_review": Review(
                    id="baseline_x",
                    paper_id="paper_x",
                    rating=7,
                    confidence=4,
                    review_text="Good work.",
                ),
            }
        ]

        criteria = ["accuracy", "completeness"]
        results = evaluate_review_batch(pairs, criteria=criteria)

        assert len(results) == 1
        assert isinstance(results[0], Evaluation)

    def test_evaluate_review_batch_to_json(self):
        """Test that batch results can be converted to JSON."""
        pairs = [
            {
                "agent_review": Review(
                    id="agent_json",
                    paper_id="paper_json",
                    rating=7,
                    confidence=4,
                    review_text="Test review.",
                ),
                "baseline_review": Review(
                    id="baseline_json",
                    paper_id="paper_json",
                    rating=8,
                    confidence=5,
                    review_text="Test baseline.",
                ),
            }
        ]

        results = evaluate_review_batch(pairs)

        # Verify we can serialize to JSON
        json_results = [result.model_dump() for result in results]
        json_str = json.dumps(json_results)
        parsed = json.loads(json_str)

        assert len(parsed) == 1
        assert "review_id" in parsed[0]
        assert "semantic_score" in parsed[0]
        assert "justification" in parsed[0]
        assert "baseline_review_id" in parsed[0]
        assert parsed[0]["review_id"] == "agent_json"
