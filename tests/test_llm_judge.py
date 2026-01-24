"""Tests for LLM-as-a-Judge evaluation module.

Tests verify semantic quality evaluation of agent-generated reviews,
comparison against human baseline reviews, scoring with justification,
configurable evaluation criteria, and use of mock/sample agent outputs.
"""

import pytest
from agenteval.judges.llm_judge import LLMJudge, evaluate_review  # type: ignore[import-not-found]
from agenteval.models.data import Review
from agenteval.models.evaluation import Evaluation


@pytest.fixture
def human_baseline_review() -> Review:
    """Create a mock human baseline review from PeerRead dataset."""
    return Review(
        review_id="human_001",
        paper_id="paper_123",
        rating=7,
        confidence=4,
        summary="This paper presents a novel approach to neural architecture search.",
        strengths=[
            "Well-written and clear presentation",
            "Strong empirical results on standard benchmarks",
            "Novel contribution to the field",
        ],
        weaknesses=[
            "Limited theoretical analysis",
            "Missing ablation studies for key components",
        ],
        detailed_comments="The paper introduces an interesting method for automated neural architecture search. The experimental results are convincing, showing improvements over existing baselines. However, the paper would benefit from deeper theoretical insights and more comprehensive ablation studies.",
        is_agent_generated=False,
    )


@pytest.fixture
def agent_generated_review() -> Review:
    """Create a mock agent-generated review for testing."""
    return Review(
        review_id="agent_001",
        paper_id="paper_123",
        rating=8,
        confidence=3,
        summary="This paper proposes a new method for neural architecture search with promising results.",
        strengths=[
            "Clear writing and good organization",
            "Strong experimental validation",
            "Innovative approach to NAS",
        ],
        weaknesses=[
            "Could use more theoretical foundation",
            "Some ablation studies are missing",
        ],
        detailed_comments="The paper presents a valuable contribution to neural architecture search. The experiments demonstrate clear improvements. Adding more theoretical analysis and comprehensive ablations would strengthen the work further.",
        is_agent_generated=True,
    )


@pytest.fixture
def low_quality_agent_review() -> Review:
    """Create a mock low-quality agent-generated review."""
    return Review(
        review_id="agent_002",
        paper_id="paper_123",
        rating=5,
        confidence=2,
        summary="Paper is okay.",
        strengths=["Some good ideas"],
        weaknesses=["Some problems"],
        detailed_comments="The paper has some interesting aspects but also has issues.",
        is_agent_generated=True,
    )


def test_evaluate_semantic_quality_of_agent_review(
    agent_generated_review: Review, human_baseline_review: Review
):
    """Test that LLM judge evaluates semantic quality of agent-generated review."""
    judge = LLMJudge(model="mock")
    evaluation = judge.evaluate(
        agent_review=agent_generated_review, baseline_review=human_baseline_review
    )

    assert isinstance(evaluation, Evaluation)
    assert evaluation.agent_review_id == agent_generated_review.review_id
    assert evaluation.baseline_review_id == human_baseline_review.review_id
    assert evaluation.paper_id == agent_generated_review.paper_id


def test_llm_judge_provides_score(
    agent_generated_review: Review, human_baseline_review: Review
):
    """Test that LLM judge provides a numerical score."""
    judge = LLMJudge(model="mock")
    evaluation = judge.evaluate(
        agent_review=agent_generated_review, baseline_review=human_baseline_review
    )

    assert isinstance(evaluation.llm_judge_score, float)
    assert 0.0 <= evaluation.llm_judge_score <= 1.0


def test_llm_judge_provides_justification(
    agent_generated_review: Review, human_baseline_review: Review
):
    """Test that LLM judge provides justification for the score."""
    judge = LLMJudge(model="mock")
    evaluation = judge.evaluate(
        agent_review=agent_generated_review, baseline_review=human_baseline_review
    )

    assert isinstance(evaluation.llm_judge_justification, str)
    assert len(evaluation.llm_judge_justification) > 0


def test_high_quality_review_gets_high_score(
    agent_generated_review: Review, human_baseline_review: Review
):
    """Test that high-quality agent review scores highly against baseline."""
    judge = LLMJudge(model="mock")
    evaluation = judge.evaluate(
        agent_review=agent_generated_review, baseline_review=human_baseline_review
    )

    # High quality review should score above 0.7
    assert evaluation.llm_judge_score >= 0.7


def test_low_quality_review_gets_low_score(
    low_quality_agent_review: Review, human_baseline_review: Review
):
    """Test that low-quality agent review scores poorly against baseline."""
    judge = LLMJudge(model="mock")
    evaluation = judge.evaluate(
        agent_review=low_quality_agent_review, baseline_review=human_baseline_review
    )

    # Low quality review should score below 0.5
    assert evaluation.llm_judge_score < 0.5


def test_configurable_evaluation_criteria():
    """Test that evaluation criteria can be configured."""
    criteria = [
        "Clarity and coherence",
        "Depth of analysis",
        "Constructiveness of feedback",
        "Alignment with rating",
    ]

    judge = LLMJudge(model="mock", evaluation_criteria=criteria)

    assert judge.evaluation_criteria == criteria


def test_default_evaluation_criteria():
    """Test that default evaluation criteria are used when none provided."""
    judge = LLMJudge(model="mock")

    assert isinstance(judge.evaluation_criteria, list)
    assert len(judge.evaluation_criteria) > 0


def test_evaluation_id_is_unique():
    """Test that each evaluation gets a unique ID."""
    judge = LLMJudge(model="mock")

    agent_review = Review(
        review_id="agent_001",
        paper_id="paper_123",
        rating=7,
        confidence=3,
        summary="Test summary",
        strengths=["Good"],
        weaknesses=["Bad"],
        detailed_comments="Test comments",
        is_agent_generated=True,
    )

    baseline_review = Review(
        review_id="human_001",
        paper_id="paper_123",
        rating=8,
        confidence=4,
        summary="Test baseline",
        strengths=["Excellent"],
        weaknesses=["Minor issues"],
        detailed_comments="Baseline comments",
        is_agent_generated=False,
    )

    eval1 = judge.evaluate(agent_review=agent_review, baseline_review=baseline_review)
    eval2 = judge.evaluate(agent_review=agent_review, baseline_review=baseline_review)

    assert eval1.evaluation_id != eval2.evaluation_id


def test_batch_evaluation_of_multiple_reviews(human_baseline_review: Review):
    """Test that multiple agent reviews can be evaluated in batch."""
    agent_reviews = [
        Review(
            review_id=f"agent_{i:03d}",
            paper_id="paper_123",
            rating=7 + i % 2,
            confidence=3,
            summary=f"Agent review {i}",
            strengths=["Good work"],
            weaknesses=["Some issues"],
            detailed_comments=f"Detailed comments for review {i}",
            is_agent_generated=True,
        )
        for i in range(3)
    ]

    judge = LLMJudge(model="mock")
    evaluations = judge.evaluate_batch(
        agent_reviews=agent_reviews, baseline_review=human_baseline_review
    )

    assert len(evaluations) == 3
    assert all(isinstance(e, Evaluation) for e in evaluations)
    assert all(e.baseline_review_id == human_baseline_review.review_id for e in evaluations)


def test_empty_batch_returns_empty_list():
    """Test that evaluating empty batch returns empty list."""
    judge = LLMJudge(model="mock")

    baseline_review = Review(
        review_id="human_001",
        paper_id="paper_123",
        rating=8,
        confidence=4,
        summary="Baseline",
        strengths=["Good"],
        weaknesses=["Minor"],
        detailed_comments="Comments",
        is_agent_generated=False,
    )

    evaluations = judge.evaluate_batch(agent_reviews=[], baseline_review=baseline_review)

    assert evaluations == []
    assert isinstance(evaluations, list)


def test_evaluation_includes_paper_id(
    agent_generated_review: Review, human_baseline_review: Review
):
    """Test that evaluation includes the paper ID for tracking."""
    judge = LLMJudge(model="mock")
    evaluation = judge.evaluate(
        agent_review=agent_generated_review, baseline_review=human_baseline_review
    )

    assert evaluation.paper_id == "paper_123"


def test_convenience_function_for_single_evaluation(
    agent_generated_review: Review, human_baseline_review: Review
):
    """Test convenience function for evaluating a single review."""
    evaluation = evaluate_review(
        agent_review=agent_generated_review,
        baseline_review=human_baseline_review,
        model="mock",
    )

    assert isinstance(evaluation, Evaluation)
    assert evaluation.agent_review_id == agent_generated_review.review_id
    assert evaluation.baseline_review_id == human_baseline_review.review_id


def test_mismatched_paper_ids_raises_error():
    """Test that evaluating reviews with mismatched paper IDs raises error."""
    agent_review = Review(
        review_id="agent_001",
        paper_id="paper_123",
        rating=7,
        confidence=3,
        summary="Test",
        strengths=["Good"],
        weaknesses=["Bad"],
        detailed_comments="Comments",
        is_agent_generated=True,
    )

    baseline_review = Review(
        review_id="human_001",
        paper_id="paper_456",  # Different paper ID
        rating=8,
        confidence=4,
        summary="Baseline",
        strengths=["Excellent"],
        weaknesses=["Minor"],
        detailed_comments="Baseline comments",
        is_agent_generated=False,
    )

    judge = LLMJudge(model="mock")

    with pytest.raises(ValueError, match="Paper IDs must match"):
        judge.evaluate(agent_review=agent_review, baseline_review=baseline_review)


def test_custom_model_name():
    """Test that custom model name can be specified."""
    judge = LLMJudge(model="gpt-4")

    assert judge.model == "gpt-4"
