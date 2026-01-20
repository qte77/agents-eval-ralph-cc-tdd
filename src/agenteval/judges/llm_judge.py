"""LLM-as-a-Judge evaluation module.

Evaluates semantic quality of agent-generated reviews by comparing them
against human baseline reviews using LLM-based assessment.
"""

from agenteval.models.data import Review
from agenteval.models.evaluation import Evaluation


def evaluate_review(
    agent_review: Review,
    baseline_review: Review,
    criteria: list[str] | None = None,
) -> Evaluation:
    """Evaluate a single agent review against a baseline human review.

    Args:
        agent_review: The agent-generated review to evaluate
        baseline_review: The human baseline review to compare against
        criteria: Optional list of evaluation criteria

    Returns:
        Evaluation: Evaluation result with semantic score and justification
    """
    if criteria is None:
        criteria = ["relevance", "clarity", "depth"]

    # Calculate semantic similarity (mock implementation)
    # In production, this would use an actual LLM to judge quality
    score = _calculate_semantic_score(agent_review, baseline_review)
    justification = _generate_justification(agent_review, baseline_review, score)

    return Evaluation(
        review_id=agent_review.id,
        baseline_review_id=baseline_review.id,
        semantic_score=score,
        justification=justification,
    )


def _calculate_semantic_score(agent_review: Review, baseline_review: Review) -> float:
    """Calculate semantic similarity score between reviews.

    This is a simplified mock implementation. In production, this would use
    an LLM to judge semantic quality.

    Args:
        agent_review: The agent-generated review
        baseline_review: The baseline human review

    Returns:
        float: Semantic score between 0 and 1
    """
    # Simple heuristic based on review text length similarity and rating
    agent_text_len = len(agent_review.review_text)
    baseline_text_len = len(baseline_review.review_text)

    # Text length similarity (0-1)
    length_ratio = min(agent_text_len, baseline_text_len) / max(agent_text_len, baseline_text_len)

    # Rating similarity (0-1)
    rating_diff = abs(agent_review.rating - baseline_review.rating)
    rating_similarity = 1.0 - (rating_diff / 9.0)  # Max diff is 9 (10-1)

    # Combined score with weights (balance rating and text quality)
    score = (length_ratio * 0.4) + (rating_similarity * 0.6)

    return round(score, 2)


def _generate_justification(agent_review: Review, baseline_review: Review, score: float) -> str:
    """Generate justification for the evaluation score.

    Args:
        agent_review: The agent-generated review
        baseline_review: The baseline human review
        score: The calculated semantic score

    Returns:
        str: Justification text explaining the score
    """
    agent_len = len(agent_review.review_text)
    baseline_len = len(baseline_review.review_text)
    rating_diff = abs(agent_review.rating - baseline_review.rating)

    if score >= 0.7:
        if agent_len < baseline_len * 0.5:
            return (
                f"Agent review closely matches baseline rating "
                f"(diff: {rating_diff}) but more concise. Score: {score:.2f}"
            )
        return f"Strong semantic similarity with comparable ratings and detail. Score: {score:.2f}"
    elif score >= 0.5:
        return (
            f"Moderate alignment with baseline. Rating diff: {rating_diff}, "
            f"some variation in detail. Score: {score:.2f}"
        )
    else:
        return (
            f"Significant differences in rating (diff: {rating_diff}) "
            f"and detail level. Score: {score:.2f}"
        )


def evaluate_review_batch(
    pairs: list[dict],
    criteria: list[str] | None = None,
) -> list[Evaluation]:
    """Evaluate multiple agent reviews in batch.

    Args:
        pairs: List of dicts with 'agent_review' and 'baseline_review' keys
        criteria: Optional list of evaluation criteria

    Returns:
        list[Evaluation]: List of evaluation results

    Raises:
        ValueError: If batch is empty
    """
    if not pairs:
        raise ValueError("Batch cannot be empty")

    results = []
    for pair in pairs:
        evaluation = evaluate_review(
            agent_review=pair["agent_review"],
            baseline_review=pair["baseline_review"],
            criteria=criteria,
        )
        results.append(evaluation)

    return results


class LLMJudge:
    """LLM-based judge for evaluating review quality.

    Uses LLM to assess semantic quality of agent-generated reviews
    by comparing them against human baseline reviews.
    """

    def __init__(self, criteria: list[str] | None = None):
        """Initialize LLMJudge with evaluation criteria.

        Args:
            criteria: List of evaluation criteria (default: relevance, clarity, depth)
        """
        if criteria is None:
            criteria = ["relevance", "clarity", "depth"]
        self.criteria = criteria

    def evaluate(
        self,
        agent_review: Review,
        baseline_review: Review,
    ) -> Evaluation:
        """Evaluate an agent review against a baseline.

        Args:
            agent_review: The agent-generated review to evaluate
            baseline_review: The human baseline review to compare against

        Returns:
            Evaluation: Evaluation result with semantic score and justification
        """
        return evaluate_review(
            agent_review=agent_review,
            baseline_review=baseline_review,
            criteria=self.criteria,
        )
