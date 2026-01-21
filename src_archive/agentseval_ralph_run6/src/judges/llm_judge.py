"""LLM-as-a-Judge evaluation using PydanticAI."""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from agenteval.models.data import Review
from agenteval.models.evaluation import Evaluation

# Default evaluation criteria
DEFAULT_CRITERIA = [
    "Accuracy and relevance of assessment",
    "Clarity and specificity of feedback",
    "Depth and thoroughness of analysis",
    "Balance of strengths and weaknesses",
    "Constructiveness of suggestions",
]


class EvaluationResult(BaseModel):
    """Structured output from LLM judge."""

    semantic_score: float
    justification: str


class LLMJudge:
    """LLM-based judge for evaluating review quality using PydanticAI."""

    def __init__(self, model: str = "claude-sonnet-4-5", use_test_model: bool = False):
        """Initialize LLMJudge with a specific model.

        Args:
            model: LLM model identifier (e.g., "claude-sonnet-4-5")
            use_test_model: If True, use TestModel for testing (no API calls)
        """
        self.model = model
        self.default_criteria = DEFAULT_CRITERIA

        # Use TestModel for testing to avoid API calls
        if use_test_model:
            # TestModel auto-generates valid structured data based on output_type
            self._model = TestModel()
        else:
            self._model = model

        self._agent = Agent(
            self._model,
            output_type=EvaluationResult,
            system_prompt=(
                "You are an expert evaluator of scientific paper reviews. "
                "Your task is to assess the quality of agent-generated reviews by comparing them "
                "to human baseline reviews from the PeerRead dataset. "
                "Provide a semantic quality score from 0 to 10 and a detailed justification."
            ),
        )

    def evaluate(
        self,
        agent_review: Review,
        human_baseline: Review,
        criteria: list[str] | None = None,
    ) -> Evaluation:
        """Evaluate agent review quality against human baseline.

        Args:
            agent_review: The agent-generated review to evaluate
            human_baseline: The human baseline review from PeerRead
            criteria: Optional custom evaluation criteria

        Returns:
            Evaluation object with score, justification, and metadata

        Raises:
            ValueError: If paper_id mismatch between reviews
        """
        if agent_review.paper_id != human_baseline.paper_id:
            raise ValueError(
                f"paper_id mismatch: agent review has {agent_review.paper_id}, "
                f"baseline has {human_baseline.paper_id}"
            )

        evaluation_criteria = criteria if criteria is not None else self.default_criteria

        prompt = self._build_evaluation_prompt(agent_review, human_baseline, evaluation_criteria)

        result = self._agent.run_sync(prompt)

        return Evaluation(
            id=str(uuid.uuid4()),
            paper_id=agent_review.paper_id,
            agent_review_id=agent_review.id,
            human_baseline_id=human_baseline.id,
            semantic_score=result.output.semantic_score,
            justification=result.output.justification,
            evaluated_at=datetime.now(UTC),
        )

    def batch_evaluate(
        self,
        agent_reviews: list[Review],
        human_baselines: list[Review],
        criteria: list[str] | None = None,
    ) -> list[Evaluation]:
        """Evaluate multiple agent reviews in batch.

        Args:
            agent_reviews: List of agent-generated reviews
            human_baselines: List of corresponding human baseline reviews
            criteria: Optional custom evaluation criteria

        Returns:
            List of Evaluation objects
        """
        if len(agent_reviews) != len(human_baselines):
            raise ValueError(
                f"Mismatched list lengths: {len(agent_reviews)} agent reviews vs "
                f"{len(human_baselines)} baselines"
            )

        if not agent_reviews:
            return []

        evaluations = []
        for agent_review, baseline in zip(agent_reviews, human_baselines, strict=True):
            evaluation = self.evaluate(
                agent_review=agent_review,
                human_baseline=baseline,
                criteria=criteria,
            )
            evaluations.append(evaluation)

        return evaluations

    def _build_evaluation_prompt(
        self,
        agent_review: Review,
        human_baseline: Review,
        criteria: list[str],
    ) -> str:
        """Build evaluation prompt for the LLM judge.

        Args:
            agent_review: Agent-generated review
            human_baseline: Human baseline review
            criteria: Evaluation criteria

        Returns:
            Formatted prompt string
        """
        criteria_text = "\n".join(f"- {criterion}" for criterion in criteria)

        return f"""Evaluate the quality of the following agent-generated review by \
comparing it to a human baseline review.

**Evaluation Criteria:**
{criteria_text}

**Human Baseline Review (from PeerRead dataset):**
- Rating: {human_baseline.rating}/10
- Summary: {human_baseline.summary}
- Strengths: {", ".join(human_baseline.strengths)}
- Weaknesses: {", ".join(human_baseline.weaknesses)}
- Confidence: {human_baseline.confidence}/5

**Agent-Generated Review:**
- Rating: {agent_review.rating}/10
- Summary: {agent_review.summary}
- Strengths: {", ".join(agent_review.strengths)}
- Weaknesses: {", ".join(agent_review.weaknesses)}
- Confidence: {agent_review.confidence}/5

Provide a semantic quality score from 0 to 10, where:
- 0-3: Poor quality (major issues, lacks depth, misses key points)
- 4-6: Moderate quality (acceptable but with notable gaps)
- 7-8: Good quality (solid review with minor issues)
- 9-10: Excellent quality (comprehensive, insightful, well-balanced)

Include a detailed justification explaining the score based on the criteria above."""
