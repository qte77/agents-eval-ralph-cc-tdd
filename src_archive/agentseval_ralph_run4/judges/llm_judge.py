"""LLM Judge Evaluator for semantic quality assessment of agent reviews.

Evaluates agent-generated reviews against human baseline reviews from PeerRead
using LLM-based semantic comparison with configurable criteria.
"""

from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from agenteval.models.data import Review
from agenteval.models.evaluation import Evaluation


class AgentReview(BaseModel):
    """Model for agent-generated review to be evaluated."""

    review_id: str
    paper_id: str
    rating: int = Field(..., ge=1, le=10)
    confidence: int = Field(..., ge=1, le=5)
    review_text: str


class EvaluationCriteria(BaseModel):
    """Configurable criteria for LLM-based evaluation."""

    coherence_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    relevance_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    completeness_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    technical_accuracy_weight: float = Field(default=0.25, ge=0.0, le=1.0)


class EvaluationResult(BaseModel):
    """Structured result from LLM judge evaluation."""

    semantic_score: float = Field(..., ge=0.0, le=1.0)
    justification: str


class LLMJudgeEvaluator:
    """LLM-based evaluator for semantic quality of agent reviews."""

    def __init__(self, criteria: EvaluationCriteria | None = None, model: Any | None = None):
        """Initialize evaluator with optional custom criteria and model.

        Args:
            criteria: Custom evaluation criteria weights, defaults to equal weights
            model: Optional model to use (defaults to openai:gpt-4o-mini if None)
        """
        self.criteria = criteria or EvaluationCriteria()
        model_name = model if model is not None else "openai:gpt-4o-mini"
        self._agent = Agent(
            model_name,
            output_type=EvaluationResult,
            system_prompt=self._build_system_prompt(),
        )

    def _build_system_prompt(self) -> str:
        """Build system prompt for LLM judge based on criteria.

        Returns:
            System prompt string with evaluation instructions
        """
        return f"""You are an expert evaluator assessing the semantic quality of \
AI-generated paper reviews.

Compare an agent-generated review against a human baseline review and evaluate \
semantic similarity.

Evaluation Criteria (weights):
- Coherence: {self.criteria.coherence_weight} - Logical flow and clarity
- Relevance: {self.criteria.relevance_weight} - Addressing key paper aspects
- Completeness: {self.criteria.completeness_weight} - Coverage of important points
- Technical Accuracy: {self.criteria.technical_accuracy_weight} - Correctness of details

Provide:
1. A semantic_score between 0.0 and 1.0 (0 = completely different, 1 = equivalent)
2. A brief justification explaining the score

Consider semantic meaning, not exact wording. Reviews with similar intent and coverage \
should score highly even if phrased differently."""

    async def evaluate(self, agent_review: AgentReview, baseline_review: Review) -> Evaluation:
        """Evaluate a single agent review against a baseline.

        Args:
            agent_review: Agent-generated review to evaluate
            baseline_review: Human baseline review for comparison

        Returns:
            Evaluation with semantic score and justification
        """
        prompt = f"""Agent Review:
Rating: {agent_review.rating}/10, Confidence: {agent_review.confidence}/5
Text: {agent_review.review_text}

Baseline Review:
Rating: {baseline_review.rating}/10, Confidence: {baseline_review.confidence}/5
Text: {baseline_review.review_text}

Evaluate the semantic similarity and provide a score with justification."""

        result = await self._agent.run(prompt)
        eval_result = result.output

        return Evaluation(
            review_id=agent_review.review_id,
            semantic_score=eval_result.semantic_score,
            justification=eval_result.justification,
            baseline_review_id=baseline_review.id,
        )

    async def batch_evaluate(
        self,
        agent_reviews: list[AgentReview],
        baseline_reviews: list[Review],
    ) -> list[Evaluation]:
        """Evaluate multiple agent reviews against baseline reviews.

        Args:
            agent_reviews: List of agent-generated reviews
            baseline_reviews: List of human baseline reviews

        Returns:
            List of evaluations for each review pair

        Raises:
            ValueError: If input lists have different lengths
        """
        if len(agent_reviews) != len(baseline_reviews):
            raise ValueError(
                f"Mismatched lengths: {len(agent_reviews)} agent reviews vs "
                f"{len(baseline_reviews)} baseline reviews"
            )

        if not agent_reviews:
            return []

        evaluations = []
        for agent_review, baseline_review in zip(agent_reviews, baseline_reviews):
            evaluation = await self.evaluate(agent_review, baseline_review)
            evaluations.append(evaluation)

        return evaluations
