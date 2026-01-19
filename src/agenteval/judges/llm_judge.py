"""LLM-as-a-Judge evaluation for agent-generated reviews.

Implements semantic quality assessment using PydanticAI.
"""

from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel


class EvaluationCriteria(BaseModel):
    """Configurable evaluation criteria for LLM judge."""

    aspects: list[str]
    description: str


class EvaluationResult(BaseModel):
    """Structured evaluation result with scores and reasoning."""

    overall_score: float = Field(..., ge=0.0, le=10.0)
    aspect_scores: dict[str, float]
    reasoning: str
    justification: str

    @field_validator("overall_score")
    @classmethod
    def validate_overall_score(cls, v: float) -> float:
        """Validate overall score is in valid range."""
        if not 0.0 <= v <= 10.0:
            raise ValueError("Overall score must be between 0 and 10")
        return v


class LLMJudge:
    """LLM-based judge for evaluating semantic quality of agent outputs.

    Uses PydanticAI Agent for structured LLM calls and evaluation.
    """

    def __init__(
        self,
        model: str | TestModel = "test",
        api_key: str | None = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        """Initialize LLM judge.

        Args:
            model: Model identifier for PydanticAI or TestModel instance
            api_key: Optional API key for LLM provider
            max_retries: Maximum number of retries for API calls
            retry_delay: Delay between retries in seconds
        """
        self.model = model
        self.api_key = api_key
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Use TestModel for testing if model is "test"
        if isinstance(model, str) and model == "test":
            # Create TestModel with mock response
            test_model = TestModel()
            self._agent: Agent[None, EvaluationResult] = Agent(
                test_model, output_type=EvaluationResult
            )
        elif isinstance(model, TestModel):
            self._agent = Agent(model, output_type=EvaluationResult)
        else:
            # Use specified model for production
            self._agent = Agent(model, output_type=EvaluationResult)

    @property
    def agent(self) -> Agent[None, EvaluationResult]:
        """Get the underlying PydanticAI agent."""
        return self._agent

    def evaluate(
        self,
        text: str,
        criteria: EvaluationCriteria,
    ) -> EvaluationResult:
        """Evaluate semantic quality of text against criteria.

        Args:
            text: Text to evaluate
            criteria: Evaluation criteria

        Returns:
            EvaluationResult with scores and reasoning
        """
        # Handle empty text
        if not text or text.strip() == "":
            return EvaluationResult(
                overall_score=0.0,
                aspect_scores={aspect: 0.0 for aspect in criteria.aspects},
                reasoning="Empty text provided",
                justification="Cannot evaluate empty text",
            )

        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(text, criteria)

        try:
            # Run agent to get structured evaluation
            result = self._agent.run_sync(prompt)
            return result.output
        except Exception as e:
            # Handle API errors gracefully
            if "API" in str(e) or "key" in str(e).lower():
                raise Exception(f"API error: {e}") from e
            # Return minimal result for other errors
            return EvaluationResult(
                overall_score=0.0,
                aspect_scores={aspect: 0.0 for aspect in criteria.aspects},
                reasoning=f"Error during evaluation: {e}",
                justification="Evaluation failed",
            )

    def compare(
        self,
        text: str,
        baseline: str,
        criteria: EvaluationCriteria,
    ) -> EvaluationResult:
        """Compare text against baseline using criteria.

        Args:
            text: Text to evaluate
            baseline: Baseline text for comparison
            criteria: Evaluation criteria

        Returns:
            EvaluationResult with comparison scores and reasoning
        """
        # Build comparison prompt
        prompt = self._build_comparison_prompt(text, baseline, criteria)

        try:
            # Run agent to get structured evaluation
            result = self._agent.run_sync(prompt)
            return result.output
        except Exception as e:
            # Handle API errors gracefully
            if "API" in str(e) or "key" in str(e).lower():
                raise Exception(f"API error: {e}") from e
            return EvaluationResult(
                overall_score=0.0,
                aspect_scores={aspect: 0.0 for aspect in criteria.aspects},
                reasoning=f"Error during comparison: {e}",
                justification="Comparison failed",
            )

    def batch_evaluate(
        self,
        texts: list[str],
        criteria: EvaluationCriteria,
    ) -> list[EvaluationResult]:
        """Evaluate multiple texts in batch.

        Args:
            texts: List of texts to evaluate
            criteria: Evaluation criteria

        Returns:
            List of EvaluationResult objects
        """
        return [self.evaluate(text=text, criteria=criteria) for text in texts]

    def batch_compare(
        self,
        texts: list[str],
        baselines: list[str],
        criteria: EvaluationCriteria,
    ) -> list[EvaluationResult]:
        """Compare multiple texts against baselines in batch.

        Args:
            texts: List of texts to evaluate
            baselines: List of baseline texts
            criteria: Evaluation criteria

        Returns:
            List of EvaluationResult objects
        """
        if len(texts) != len(baselines):
            raise ValueError("texts and baselines must have same length")

        return [
            self.compare(text=text, baseline=baseline, criteria=criteria)
            for text, baseline in zip(texts, baselines, strict=True)
        ]

    def _build_evaluation_prompt(
        self,
        text: str,
        criteria: EvaluationCriteria,
    ) -> str:
        """Build prompt for evaluating text.

        Args:
            text: Text to evaluate
            criteria: Evaluation criteria

        Returns:
            Formatted prompt string
        """
        aspects_str = ", ".join(criteria.aspects)

        return f"""Evaluate the following text based on these criteria: {criteria.description}

Aspects to evaluate: {aspects_str}

Text to evaluate:
{text}

Provide:
1. An overall score from 0-10
2. Individual scores for each aspect (0-10)
3. Clear reasoning for your evaluation
4. Detailed justification for the scores

Return your evaluation as structured JSON matching the EvaluationResult schema."""

    def _build_comparison_prompt(
        self,
        text: str,
        baseline: str,
        criteria: EvaluationCriteria,
    ) -> str:
        """Build prompt for comparing text against baseline.

        Args:
            text: Text to evaluate
            baseline: Baseline text
            criteria: Evaluation criteria

        Returns:
            Formatted prompt string
        """
        aspects_str = ", ".join(criteria.aspects)

        return f"""Compare the following text against the baseline using these criteria: {criteria.description}

Aspects to compare: {aspects_str}

Text to evaluate:
{text}

Baseline for comparison:
{baseline}

Provide:
1. An overall comparison score from 0-10 (10 = matches or exceeds baseline)
2. Individual scores for each aspect (0-10)
3. Clear reasoning explaining the comparison
4. Detailed justification for the scores

Return your evaluation as structured JSON matching the EvaluationResult schema."""
