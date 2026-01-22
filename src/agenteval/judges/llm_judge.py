"""LLM-as-a-Judge evaluation module.

Evaluates semantic quality of agent-generated reviews using LLM-based
assessment against human baseline reviews from PeerRead dataset.
"""

from __future__ import annotations

import uuid

from agenteval.models.data import Review
from agenteval.models.evaluation import Evaluation


class LLMJudge:
    """LLM-based judge for evaluating agent-generated reviews."""

    def __init__(
        self,
        model: str,
        evaluation_criteria: list[str] | None = None,
    ):
        """Initialize LLM judge.

        Args:
            model: Model name to use for evaluation
            evaluation_criteria: Optional list of criteria for evaluation
        """
        self.model = model
        self.evaluation_criteria = evaluation_criteria or [
            "Clarity and coherence",
            "Depth of analysis",
            "Constructiveness of feedback",
            "Alignment with rating",
        ]

    def evaluate(
        self,
        agent_review: Review,
        baseline_review: Review,
    ) -> Evaluation:
        """Evaluate an agent-generated review against baseline.

        Args:
            agent_review: Agent-generated review to evaluate
            baseline_review: Human baseline review for comparison

        Returns:
            Evaluation object with score and justification

        Raises:
            ValueError: If paper IDs don't match
        """
        if agent_review.paper_id != baseline_review.paper_id:
            raise ValueError("Paper IDs must match between agent and baseline reviews")

        # Mock evaluation for testing - in production this would call LLM
        score = self._calculate_mock_score(agent_review, baseline_review)
        justification = self._generate_mock_justification(agent_review, baseline_review, score)

        return Evaluation(
            evaluation_id=str(uuid.uuid4()),
            paper_id=agent_review.paper_id,
            agent_review_id=agent_review.review_id,
            baseline_review_id=baseline_review.review_id,
            llm_judge_score=score,
            llm_judge_justification=justification,
        )

    def evaluate_batch(
        self,
        agent_reviews: list[Review],
        baseline_review: Review,
    ) -> list[Evaluation]:
        """Evaluate multiple agent reviews against a baseline.

        Args:
            agent_reviews: List of agent-generated reviews to evaluate
            baseline_review: Human baseline review for comparison

        Returns:
            List of Evaluation objects
        """
        if not agent_reviews:
            return []

        return [
            self.evaluate(agent_review=review, baseline_review=baseline_review)
            for review in agent_reviews
        ]

    def _calculate_mock_score(self, agent_review: Review, baseline_review: Review) -> float:
        """Calculate mock score based on review quality indicators.

        This is a simplified mock implementation for testing.
        In production, this would use actual LLM evaluation.
        """
        # Simple heuristics for mock scoring
        score = 0.5  # Start at middle

        # Check summary quality
        if len(agent_review.summary) > 20:
            score += 0.1

        # Check strengths and weaknesses
        if len(agent_review.strengths) >= 2:
            score += 0.1
        if len(agent_review.weaknesses) >= 1:
            score += 0.1

        # Check detailed comments
        if len(agent_review.detailed_comments) > 50:
            score += 0.1

        # Penalize very low quality
        if (
            len(agent_review.summary) < 15
            or len(agent_review.strengths) < 1
            or len(agent_review.detailed_comments) < 30
        ):
            score -= 0.3

        # Ensure score is in valid range
        return max(0.0, min(1.0, score))

    def _generate_mock_justification(
        self, agent_review: Review, baseline_review: Review, score: float
    ) -> str:
        """Generate mock justification for the score.

        This is a simplified mock implementation for testing.
        In production, this would use actual LLM-generated justification.
        """
        if score >= 0.7:
            return (
                f"The agent-generated review demonstrates strong quality with a comprehensive "
                f"summary, well-articulated strengths ({len(agent_review.strengths)} points), "
                f"and constructive weaknesses ({len(agent_review.weaknesses)} points). "
                f"The detailed comments provide substantive feedback comparable to the "
                f"baseline review."
            )
        elif score >= 0.5:
            return (
                "The agent-generated review shows moderate quality with adequate coverage "
                "of key points. However, it could benefit from more detailed analysis "
                "or more specific feedback compared to the baseline review."
            )
        else:
            return (
                f"The agent-generated review lacks sufficient detail and depth. "
                f"The summary is too brief ({len(agent_review.summary)} chars), "
                f"and the detailed comments need substantial improvement to match "
                f"the baseline review quality."
            )


def evaluate_review(
    agent_review: Review,
    baseline_review: Review,
    model: str = "mock",
    evaluation_criteria: list[str] | None = None,
) -> Evaluation:
    """Convenience function to evaluate a single review.

    Args:
        agent_review: Agent-generated review to evaluate
        baseline_review: Human baseline review for comparison
        model: Model name to use for evaluation
        evaluation_criteria: Optional list of criteria for evaluation

    Returns:
        Evaluation object with score and justification
    """
    judge = LLMJudge(model=model, evaluation_criteria=evaluation_criteria)
    return judge.evaluate(agent_review=agent_review, baseline_review=baseline_review)
