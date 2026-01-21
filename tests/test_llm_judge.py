"""Tests for LLM-as-a-Judge evaluation."""

from datetime import datetime

import pytest
from agenteval.judges.llm_judge import LLMJudge

from agenteval.models.data import Review
from agenteval.models.evaluation import Evaluation


@pytest.fixture
def human_baseline_review():
    """Create a sample human baseline review from PeerRead."""
    return Review(
        id="human_review_1",
        paper_id="paper_123",
        reviewer="human_reviewer",
        rating=8.5,
        summary=(
            "This paper presents a novel approach to natural language processing "
            "with strong empirical results."
        ),
        strengths=[
            "Clear methodology and reproducible experiments",
            "Strong empirical results across multiple datasets",
            "Well-written and easy to follow",
        ],
        weaknesses=[
            "Limited comparison with recent baselines",
            "Some hyperparameters not fully justified",
        ],
        confidence=4,
    )


@pytest.fixture
def agent_generated_review():
    """Create a sample agent-generated review to evaluate."""
    return Review(
        id="agent_review_1",
        paper_id="paper_123",
        reviewer="agent_system",
        rating=8.0,
        summary="The paper introduces an innovative NLP method with promising results.",
        strengths=[
            "Solid experimental design",
            "Good performance on benchmarks",
        ],
        weaknesses=[
            "Missing comparisons with state-of-the-art methods",
            "Hyperparameter choices lack explanation",
        ],
        confidence=3,
    )


@pytest.fixture
def llm_judge():
    """Create LLMJudge instance."""
    return LLMJudge(model="claude-sonnet-4-5")


def test_llm_judge_initialization(llm_judge):
    """Test LLMJudge can be initialized with a model."""
    assert llm_judge is not None
    assert llm_judge.model == "claude-sonnet-4-5"


def test_evaluate_semantic_quality(llm_judge, agent_generated_review, human_baseline_review):
    """Test semantic quality evaluation of agent review against human baseline."""
    evaluation = llm_judge.evaluate(
        agent_review=agent_generated_review,
        human_baseline=human_baseline_review,
    )

    assert isinstance(evaluation, Evaluation)
    assert evaluation.paper_id == "paper_123"
    assert evaluation.agent_review_id == "agent_review_1"
    assert evaluation.human_baseline_id == "human_review_1"
    assert 0.0 <= evaluation.semantic_score <= 10.0
    assert len(evaluation.justification) > 0
    assert isinstance(evaluation.evaluated_at, datetime)


def test_evaluate_returns_scoring_with_justification(
    llm_judge, agent_generated_review, human_baseline_review
):
    """Test evaluation provides both score and justification."""
    evaluation = llm_judge.evaluate(
        agent_review=agent_generated_review,
        human_baseline=human_baseline_review,
    )

    # Score should be reasonable for similar reviews
    assert 5.0 <= evaluation.semantic_score <= 10.0

    # Justification should explain the scoring
    justification_lower = evaluation.justification.lower()
    assert any(
        keyword in justification_lower
        for keyword in ["similar", "strengths", "weaknesses", "quality", "comparison"]
    )


def test_evaluate_configurable_criteria(llm_judge, agent_generated_review, human_baseline_review):
    """Test evaluation supports configurable criteria."""
    custom_criteria = [
        "Clarity of review",
        "Depth of analysis",
        "Constructiveness of feedback",
    ]

    evaluation = llm_judge.evaluate(
        agent_review=agent_generated_review,
        human_baseline=human_baseline_review,
        criteria=custom_criteria,
    )

    assert isinstance(evaluation, Evaluation)
    # Justification should reference custom criteria
    justification_lower = evaluation.justification.lower()
    assert any(
        criterion.lower() in justification_lower
        for criterion in ["clarity", "depth", "constructive"]
    )


def test_evaluate_poor_quality_agent_review(llm_judge, human_baseline_review):
    """Test evaluation of low-quality agent review."""
    poor_agent_review = Review(
        id="agent_review_poor",
        paper_id="paper_123",
        reviewer="agent_system",
        rating=5.0,
        summary="This paper is okay.",
        strengths=["It exists"],
        weaknesses=["Not great"],
        confidence=1,
    )

    evaluation = llm_judge.evaluate(
        agent_review=poor_agent_review,
        human_baseline=human_baseline_review,
    )

    # Poor quality review should score lower
    assert evaluation.semantic_score < 5.0
    assert "low" in evaluation.justification.lower() or "poor" in evaluation.justification.lower()


def test_evaluate_excellent_agent_review(llm_judge, human_baseline_review):
    """Test evaluation of high-quality agent review."""
    excellent_agent_review = Review(
        id="agent_review_excellent",
        paper_id="paper_123",
        reviewer="agent_system",
        rating=8.5,
        summary=(
            "This paper presents a novel approach to natural language processing "
            "with strong empirical results and clear methodology."
        ),
        strengths=[
            "Clear methodology and reproducible experiments",
            "Strong empirical results across multiple datasets",
            "Well-written and easy to follow",
            "Thorough literature review",
        ],
        weaknesses=[
            "Limited comparison with recent baselines",
            "Some hyperparameters not fully justified",
            "Could benefit from additional ablation studies",
        ],
        confidence=4,
    )

    evaluation = llm_judge.evaluate(
        agent_review=excellent_agent_review,
        human_baseline=human_baseline_review,
    )

    # Excellent review should score higher
    assert evaluation.semantic_score >= 7.0


def test_batch_evaluate_multiple_reviews(llm_judge):
    """Test batch evaluation of multiple agent reviews."""
    human_baselines = [
        Review(
            id=f"human_review_{i}",
            paper_id=f"paper_{i}",
            reviewer="human",
            rating=8.0,
            summary=f"Review {i} summary",
            strengths=["Good work"],
            weaknesses=["Could improve"],
            confidence=4,
        )
        for i in range(3)
    ]

    agent_reviews = [
        Review(
            id=f"agent_review_{i}",
            paper_id=f"paper_{i}",
            reviewer="agent",
            rating=7.5,
            summary=f"Agent review {i} summary",
            strengths=["Solid work"],
            weaknesses=["Needs improvement"],
            confidence=3,
        )
        for i in range(3)
    ]

    evaluations = llm_judge.batch_evaluate(
        agent_reviews=agent_reviews,
        human_baselines=human_baselines,
    )

    assert len(evaluations) == 3
    assert all(isinstance(eval, Evaluation) for eval in evaluations)
    assert all(0.0 <= eval.semantic_score <= 10.0 for eval in evaluations)


def test_batch_evaluate_empty_lists(llm_judge):
    """Test batch evaluation with empty input lists."""
    evaluations = llm_judge.batch_evaluate(
        agent_reviews=[],
        human_baselines=[],
    )

    assert evaluations == []


def test_evaluate_mismatched_paper_ids(llm_judge, agent_generated_review):
    """Test evaluation with mismatched paper IDs raises error."""
    mismatched_baseline = Review(
        id="human_review_different",
        paper_id="paper_999",  # Different paper ID
        reviewer="human",
        rating=8.0,
        summary="Different paper review",
        strengths=["Good"],
        weaknesses=["Bad"],
        confidence=4,
    )

    with pytest.raises(ValueError, match="paper_id"):
        llm_judge.evaluate(
            agent_review=agent_generated_review,
            human_baseline=mismatched_baseline,
        )


def test_llm_judge_default_criteria(llm_judge):
    """Test LLMJudge has default evaluation criteria."""
    assert hasattr(llm_judge, "default_criteria")
    assert isinstance(llm_judge.default_criteria, list)
    assert len(llm_judge.default_criteria) > 0
