"""Evaluation Pipeline Orchestrator.

Orchestrates the execution of all evaluation modules in sequence with
dependency management and reproducibility controls.
"""

import random
import uuid
from datetime import datetime

from agenteval.judges.llm_judge import AgentReview, LLMJudgeEvaluator
from agenteval.metrics.graph import AgentInteraction, GraphComplexityAnalyzer
from agenteval.metrics.traditional import AgentTaskResult, TraditionalMetricsCalculator
from pydantic import BaseModel, Field

from agenteval.models.data import Review


class PipelineConfig(BaseModel):
    """Configuration for evaluation pipeline."""

    seed: int | None = Field(default_factory=lambda: random.randint(0, 999999))


class PipelineResult(BaseModel):
    """Result from running the evaluation pipeline."""

    run_id: str
    timestamp: datetime
    traditional_metrics: dict[str, float]
    llm_judge_results: list[dict]
    graph_metrics: dict[str, float | int]


class EvaluationPipeline:
    """Unified evaluation pipeline combining all three tiers."""

    def __init__(self, config: PipelineConfig) -> None:
        """Initialize the evaluation pipeline.

        Args:
            config: Pipeline configuration
        """
        self.config = config

        # Set random seed for reproducibility
        if config.seed is not None:
            random.seed(config.seed)

        # Initialize evaluators
        self.traditional_calculator = TraditionalMetricsCalculator()
        self.llm_evaluator = LLMJudgeEvaluator(model="test")
        self.graph_analyzer = GraphComplexityAnalyzer()

    async def run(
        self,
        task_results: list[AgentTaskResult],
        interactions: list[AgentInteraction],
        agent_reviews: list[AgentReview],
        baseline_reviews: list[Review],
    ) -> PipelineResult:
        """Run the unified evaluation pipeline.

        Args:
            task_results: List of agent task results for traditional metrics
            interactions: List of agent interactions for graph metrics
            agent_reviews: List of agent reviews for LLM judge evaluation
            baseline_reviews: List of human baseline reviews for comparison

        Returns:
            PipelineResult with consolidated results from all enabled tiers

        Raises:
            ValueError: If agent_reviews and baseline_reviews have different lengths
        """
        run_id = str(uuid.uuid4())
        timestamp = datetime.now()

        # Run traditional metrics tier
        if task_results:
            metrics = self.traditional_calculator.calculate_metrics(task_results)
            traditional_metrics = {
                "execution_time_seconds": metrics.execution_time_seconds,
                "success_rate": metrics.success_rate,
                "coordination_quality": metrics.coordination_quality,
            }
        else:
            traditional_metrics = {
                "execution_time_seconds": 0.0,
                "success_rate": 0.0,
                "coordination_quality": 0.0,
            }

        # Run LLM judge tier
        if agent_reviews and baseline_reviews:
            evaluations = await self.llm_evaluator.batch_evaluate(agent_reviews, baseline_reviews)
            llm_judge_results = [
                {
                    "review_id": e.review_id,
                    "semantic_score": e.semantic_score,
                    "justification": e.justification,
                    "baseline_review_id": e.baseline_review_id,
                }
                for e in evaluations
            ]
        elif not agent_reviews and not baseline_reviews:
            llm_judge_results = []
        else:
            raise ValueError(
                f"Mismatched lengths: {len(agent_reviews)} agent reviews vs "
                f"{len(baseline_reviews)} baseline reviews"
            )

        # Run graph metrics tier
        if interactions:
            graph_metrics_obj = self.graph_analyzer.calculate_metrics(interactions)
            graph_metrics = {
                "density": graph_metrics_obj.density,
                "avg_clustering_coefficient": graph_metrics_obj.avg_clustering_coefficient,
                "avg_betweenness_centrality": graph_metrics_obj.avg_betweenness_centrality,
                "avg_closeness_centrality": graph_metrics_obj.avg_closeness_centrality,
                "num_nodes": graph_metrics_obj.num_nodes,
                "num_edges": graph_metrics_obj.num_edges,
            }
        else:
            graph_metrics = {
                "density": 0.0,
                "avg_clustering_coefficient": 0.0,
                "avg_betweenness_centrality": 0.0,
                "avg_closeness_centrality": 0.0,
                "num_nodes": 0,
                "num_edges": 0,
            }

        return PipelineResult(
            run_id=run_id,
            timestamp=timestamp,
            traditional_metrics=traditional_metrics,
            llm_judge_results=llm_judge_results,
            graph_metrics=graph_metrics,
        )
