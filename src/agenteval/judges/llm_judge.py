"""LLM-as-a-Judge evaluation implementation using PydanticAI.

This module provides semantic quality assessment for agent-generated reviews
using LLM-based evaluation with structured outputs.
"""

from pydantic import BaseModel
from pydantic_ai import Agent


class ReviewEvaluation(BaseModel):
    """Structured evaluation result from LLM judge."""

    score: float
    reasoning: str
    criteria_scores: dict[str, float]


class AgentReview(BaseModel):
    """Agent-generated review to be evaluated."""

    review_id: str
    paper_id: str
    content: str
    agent_id: str


class HumanBaseline(BaseModel):
    """Human baseline review for comparison."""

    review_id: str
    paper_id: str
    content: str
    score: float


class EvaluationCriteria(BaseModel):
    """Configurable criteria for evaluation."""

    technical_accuracy: bool = True
    clarity: bool = True
    constructiveness: bool = True
    completeness: bool = False


class LLMJudgeAgent:
    """PydanticAI-based LLM judge for semantic quality assessment."""

    def __init__(
        self,
        model: str = "test",
        criteria: EvaluationCriteria | None = None,
    ) -> None:
        """Initialize LLM judge agent.

        Args:
            model: Model identifier for PydanticAI
            criteria: Evaluation criteria configuration
        """
        self.model = model
        self.criteria = criteria or EvaluationCriteria()
        self._agent = Agent(
            self.model,
            output_type=ReviewEvaluation,
            system_prompt=self._build_system_prompt(),
        )

    def _build_system_prompt(self) -> str:
        """Build system prompt based on evaluation criteria."""
        criteria_list = []
        if self.criteria.technical_accuracy:
            criteria_list.append("technical_accuracy")
        if self.criteria.clarity:
            criteria_list.append("clarity")
        if self.criteria.constructiveness:
            criteria_list.append("constructiveness")
        if self.criteria.completeness:
            criteria_list.append("completeness")

        return f"""You are an expert judge evaluating the quality of scientific paper reviews.

Evaluate reviews based on these criteria: {", ".join(criteria_list)}

For each review, provide:
1. An overall score (0.0-10.0)
2. Detailed reasoning for the score
3. Individual scores for each criterion

Be strict but fair in your evaluation."""

    async def evaluate_review(self, review: AgentReview) -> ReviewEvaluation:
        """Evaluate a single agent-generated review.

        Args:
            review: AgentReview to evaluate

        Returns:
            ReviewEvaluation with score, reasoning, and criteria scores
        """
        prompt = f"""Evaluate this review:

Review ID: {review.review_id}
Paper ID: {review.paper_id}
Agent ID: {review.agent_id}

Review Content:
{review.content}

Provide evaluation scores for the enabled criteria."""

        result = await self._agent.run(prompt)
        return result.output

    async def evaluate_with_baseline(
        self, agent_review: AgentReview, baseline: HumanBaseline
    ) -> ReviewEvaluation:
        """Evaluate agent review compared to human baseline.

        Args:
            agent_review: AgentReview to evaluate
            baseline: HumanBaseline for comparison

        Returns:
            ReviewEvaluation with comparison to baseline
        """
        prompt = f"""Evaluate this agent-generated review by comparing it to a human baseline.

Agent Review:
{agent_review.content}

Human Baseline Review (score: {baseline.score}):
{baseline.content}

Evaluate the agent review's quality relative to the baseline. Consider how well it
matches the depth, insight, and quality of the human review."""

        result = await self._agent.run(prompt)
        return result.output

    async def evaluate_batch(self, reviews: list[AgentReview]) -> list[ReviewEvaluation]:
        """Evaluate multiple reviews in batch.

        Args:
            reviews: List of AgentReview objects

        Returns:
            List of ReviewEvaluation objects
        """
        evaluations = []
        for review in reviews:
            evaluation = await self.evaluate_review(review)
            evaluations.append(evaluation)
        return evaluations

    async def evaluate_batch_with_baselines(
        self, agent_reviews: list[AgentReview], baselines: list[HumanBaseline]
    ) -> list[ReviewEvaluation]:
        """Evaluate multiple reviews with corresponding baselines.

        Args:
            agent_reviews: List of AgentReview objects
            baselines: List of HumanBaseline objects (same length)

        Returns:
            List of ReviewEvaluation objects
        """
        evaluations = []
        for agent_review, baseline in zip(agent_reviews, baselines):
            evaluation = await self.evaluate_with_baseline(agent_review, baseline)
            evaluations.append(evaluation)
        return evaluations
